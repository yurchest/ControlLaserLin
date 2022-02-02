#!/usr/bin/python3
import socket
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap, QColor
from socket import *

from form1 import *
import functions


class App(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.w2 = QtWidgets.QMainWindow()
        self.w_root = Ui_MainWindow()
        self.w_root.setupUi(self.w2)
        # self.w_root = uic.loadUi('form1.ui')
        self.w2.setWindowTitle('ControlLaser')
        self.w2.setWindowIcon(QtGui.QIcon(':/newPrefix/icon.ico'))

        self.ip = self.w_root.lineEdit.text()
        self.port = int(self.w_root.lineEdit_2.text())
        self.myIp = functions.extract_ip()

        self.SendRepeat = SendRepeat(self.myIp)
        self.SendRepeat.start()



        self.startSets()

        self.w_root.pushButton.clicked.connect(self.laserOn)
        self.w_root.pushButton_2.clicked.connect(self.laserOff)
        self.w_root.pushButton_3.clicked.connect(self.buttStatus)
        self.w_root.pushButton_4.clicked.connect(self.buttStatusUstr)
        self.w_root.pushButton_5.clicked.connect(self.clearTextEdit)
        self.w_root.pushButton_6.clicked.connect(self.clearTextEdit)
        self.w_root.pushButton_7.clicked.connect(self.service)
        self.w_root.pushButton_9.clicked.connect(self.chngMoxaIpPort)
        self.w_root.pushButton_8.clicked.connect(self.setMu)
        self.w_root.pushButton_10.clicked.connect(self.setCu)

        self.w_root.tabWidget.currentChanged.connect(self.changeTextEdit)

        self.SendRepeat.out_signal.connect(self.recieve_data)
        self.SendRepeat.checkCon.connect(self.checkCon)

        self.w2.show()


    def startSets(self):
        self.ICON_RED_LED = ":/newPrefix/png/led-red-on.png"
        self.ICON_GREEN_LED = ":/newPrefix/png/green-led-on.png"
        self.ICON_BLUE_LED = ":/newPrefix/png/blue-led-on.png"
        self.NET_ON = ':/newPrefix/png/online.png'
        self.NET_OFF = ':/newPrefix/png/offline.png'
        self.merr = ('!! Not delivered answer !!')
        self.redText = QColor(255, 0, 0)
        self.greenText = QColor(111, 189, 100)
        self.yellowText = QColor(255, 100, 0)
        self.blackText = QColor(0, 0, 0)
        self.clck_ContS = 0

        self.requestModules = True
        self.showDataOnTextEdit = False

        self.SendRepeat.ip = self.ip
        self.SendRepeat.port = self.port

        self.w_root.label_3.setFixedSize(121, 41)
        self.w_root.label_3.setPixmap(QPixmap(self.NET_OFF))
        self.w_root.tabWidget.setCurrentIndex(0)

        self.changeTextEdit()

    def recieve_data(self, data):
        if data[2] == 0:
            if self.checkControlSum(data[0]):
                self.dataBin = functions.strToBin(data)
                self.w_root.label_63.setText('Control Sum')
                self.w_root.label_63.setStyleSheet('background-color: rgb(0, 255, 0, 150);border-radius: 20')

                if self.showDataOnTextEdit:
                    self.w_root.textEdit.append(str(self.dataBin))

                if data[1] == 'stMOD':
                    self.requestModules = True
                    self.w_root.textEdit.setTextColor(self.greenText)
                    self.w_root.textEdit.append('Успешное выполнение команды " Статус Модулей " ')
                    self.w_root.textEdit.setTextColor(self.blackText)
                    self.w_root.textEdit.append(
                        '----------------------------------------------------------------------')

                elif data[1] == 'stMOD_Repeat':
                    self.requestModules = True

                elif data[1] == 'stUSTR':
                    self.requestModules = False
                    self.w_root.textEdit.setTextColor(self.greenText)
                    self.w_root.textEdit.append('Успешное выполнение команды " Статус Устройств " ')
                    self.w_root.textEdit.setTextColor(self.blackText)
                    self.w_root.textEdit.append(
                        '----------------------------------------------------------------------')
                self.setLeds()

            elif not self.checkControlSum(data[0]):
                self.setDefaults()
                self.w_root.label_63.setText('Control Sum')
                self.w_root.label_63.setStyleSheet('background-color: rgb(255, 0, 0, 150);border-radius: 20')

        elif data[2] == 1:
            if data[1] == 'laserON':
                command = 'Работа'
            elif data[1] == 'laserOFF':
                command = 'Готов'
            elif data[1] == 'setMU':
                command = 'Переход в МУ'
            elif data[1] == 'setCU':
                command = 'Переход в ЦУ'

            self.checkMERR(data[0])

            self.w_root.textEdit.append('Результат выполнения команды "{0}" :'.format(command))
            self.w_root.textEdit.append(self.merr)
            self.w_root.textEdit.setTextColor(self.blackText)
            self.w_root.textEdit.append('----------------------------------------------------------------------')

    def checkMERR(self, data):
        self.w_root.textEdit.setTextColor(self.redText)
        if data.decode('raw_unicode_escape') == 'OK':
            self.w_root.textEdit.setTextColor(self.greenText)
            self.merr = 'OK'
        elif data.decode('raw_unicode_escape') == 'E0':
            self.merr = 'Error E0 : Ошибка контрольной суммы'  # Ошибка контрольной суммы
        elif data.decode('raw_unicode_escape') == 'E1':
            self.merr = 'Error E1 : Ошибка формата команды или сообщения'  # Ошибка формата команды или сообщения
        elif data.decode('raw_unicode_escape') == 'E2':
            self.merr = 'Error E2 : Неизвестная команда или сообщение'  # Неизвестная команда или сообщение
        elif data.decode('raw_unicode_escape') == 'E3':
            self.merr = 'Error E3 : Недопустимое значение параметра'  # Недопустимое значение параметра
        elif data.decode('raw_unicode_escape') == 'E4':
            self.merr = 'Error E4 : Команда не может бьыть выполнена, так как еще не закончено выполнение ранее пришедшей команды'  # Команда не может бьыть выполнена, так как еще не закончено выполнение ранее пришедшей команды
        elif data.decode("raw_unicode_escape") == 'E5':
            self.merr = 'Error E5 : НВПЛП-М находится в режиме местного управления'  # ВПЛП-М находится в режиме местного управления

    def checkControlSum(self, data):
        x = 0
        for byte_str in data[:6]:
            x += byte_str
        if int(bin(x)[-8:].zfill(8), 2) == data[6]:
            return True
        else:
            return False

    def changeTextEdit(self):
        if str(self.w_root.tabWidget.currentIndex()) == '0':
            self.w_root.textEdit = self.w_root.textEdit_1
        elif str(self.w_root.tabWidget.currentIndex()) == '1':
            self.w_root.textEdit = self.w_root.textEdit_2

    def laserOn(self):
        self.SendRepeat.tx = ['#', '\x03', 'P', '\x00']
        self.SendRepeat.wait_for_send = True


    def laserOff(self):
        self.SendRepeat.tx = ['#', '\x03', 'O', '\x00']
        self.SendRepeat.wait_for_send = True

    def buttStatusUstr(self):
        self.SendRepeat.tx = ['#', '\x03', 'E', '\x01']
        self.SendRepeat.wait_for_send = True

    def buttStatus(self):
        self.SendRepeat.tx = ['#', '\x03', 'E', '\x00']
        self.SendRepeat.wait_for_send = True

    def clearTextEdit(self):
        self.w_root.textEdit_1.clear()
        self.w_root.textEdit_2.clear()

    def service(self):
        self.showDataOnTextEdit = not self.showDataOnTextEdit

    def chngMoxaIpPort(self):
        self.SendRepeat.stop()
        self.SendRepeat.wait()
        self.ip = self.w_root.lineEdit.text()
        self.port = int(self.w_root.lineEdit_2.text())
        self.SendRepeat.ip = self.ip
        self.SendRepeat.port = self.port
        self.SendRepeat.start()
        self.w_root.textEdit.setTextColor(self.yellowText)
        self.w_root.textEdit.append('MOXA IP изменен на {}'.format(self.ip))
        self.w_root.textEdit.append('MOXA PORT изменен на {}'.format(self.port))
        self.w_root.textEdit.setTextColor(self.blackText)
        self.w_root.textEdit.append('----------------------------------------------------------------------')

    def setCu(self):
        self.SendRepeat.tx = ['#', '\x03', 'U', '\x00']
        self.SendRepeat.wait_for_send = True

    def setMu(self):
        self.SendRepeat.tx = ['#', '\x03', 'N', '\x00']
        self.SendRepeat.wait_for_send = True


    def setDefaults(self):
        self.w_root.label_8.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_9.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_10.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_11.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_12.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_13.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_26.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_27.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_25.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_47.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_48.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_46.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_44.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_45.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_41.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_60.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_61.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_62.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_66.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_80.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_81.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_82.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_84.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_71.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_72.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_73.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_74.setPixmap(QPixmap(self.ICON_BLUE_LED))
        self.w_root.label_37.setText('  ??')
        self.w_root.label_54.setText('??')
        self.w_root.label_58.setText('??')
        self.w_root.label_59.setText('??')
        self.w_root.label_34.setText('??')
        self.w_root.label_36.setText('??')
        self.w_root.label_63.setText('Control Sum')
        self.w_root.label_63.setStyleSheet('background-color: rgba(135, 212, 157, 220); border-radius: 20')
        self.w_root.label_58.setStyleSheet('background-color: rgba(135, 212, 157, 220); border-radius: 20')
        self.w_root.label_59.setStyleSheet('background-color: rgba(135, 212, 157, 220); border-radius: 20')
        self.w_root.label_54.setStyleSheet('background-color: rgba(135, 212, 157, 220); border-radius: 20')

    def checkCon(self, data):
        if data:
            self.w_root.label_3.setFixedSize(41, 41)
            self.w_root.label_3.setPixmap(QPixmap(self.NET_ON))
        else:
            self.w_root.label_3.setFixedSize(121, 41)
            self.w_root.label_3.setPixmap(QPixmap(self.NET_OFF))
            self.setDefaults()
            self.w_root.label_63.setText('NO RX DATA')
            self.w_root.label_63.setStyleSheet('background-color: rgba(255, 0, 0,150);border-radius: 20')

    def setLeds(self):
        # -------------------------------------------------------------------#
        #                       Байт состояния ВПЛП-М                        #
        # -------------------------------------------------------------------#

        if self.dataBin[3][7] == '0':  # Местное управление
            self.w_root.label_44.setPixmap(QPixmap(self.ICON_GREEN_LED))
            self.w_root.label_45.setPixmap(QPixmap(self.ICON_RED_LED))

        elif self.dataBin[3][7] == '1':  # Центральное управление
            self.w_root.label_45.setPixmap(QPixmap(self.ICON_GREEN_LED))
            self.w_root.label_44.setPixmap(QPixmap(self.ICON_RED_LED))

        if self.dataBin[3][6] == '0':  # Внутрення синхронизация
            self.w_root.label_37.setText('Внутр')
            self.w_root.label.setText(" ")
        elif self.dataBin[3][6] == '1':  # Внешняя синхронизация
            self.w_root.label_37.setText('Внешн')
            if self.dataBin[3][1] == '0':  # Внешние синхроимпульсы в норме
                self.w_root.label.setStyleSheet('color: rgb(111, 189, 100)')
                self.w_root.label.setText("Внешние синхроимпульсы в норме")
            elif self.dataBin[3][1] == '1':  # Ошибка поступления внешних синхроимпульсов
                self.w_root.label.setText("Ошибка поступления внешних синхроимпульсов")
                self.w_root.label.setStyleSheet('color: rgb(255, 0, 0)')

        if self.dataBin[3][4:6] == '00':  # Ожидание готовности
            self.w_root.label_55.setText('Ожидание готовности')
            self.w_root.label_55.setStyleSheet('background-color: rgb(211, 255, 183,100); border-radius: 20')
        elif self.dataBin[3][4:6] == '01':  # Готов
            self.w_root.label_55.setText('Готов')
            self.w_root.label_55.setStyleSheet('background-color: rgb(255, 255, 0,100); border-radius: 20')
        elif self.dataBin[3][4:6] == '10':  # Работа
            self.w_root.label_55.setText('Работа')
            self.w_root.label_55.setStyleSheet('background-color: rgb(0, 255, 0,100); border-radius: 20')
        else:
            self.w_root.label_55.setText('? Неизвестно ?')
            self.w_root.label_55.setStyleSheet('background-color: rgb(255, 0, 0,100); border-radius: 20')

        if self.dataBin[3][3] == '0':  # В системе присутсвуют ошибки
            self.w_root.label_54.setText('Да')
            self.w_root.label_54.setStyleSheet('border-radius: 14;background-color: rgb(255, 0, 0,120);')
        elif self.dataBin[3][3] == '1':  # Ошибок нет
            self.w_root.label_54.setText('Нет')
            self.w_root.label_54.setStyleSheet('border-radius: 14;background-color: rgb(25, 255, 0, 100);')

        if self.dataBin[3][2] == '0':  # Система охлаждения не готова
            self.w_root.label_41.setPixmap(QPixmap(self.ICON_RED_LED))
        elif self.dataBin[3][2] == '1':  # Система охлаждения готова
            self.w_root.label_41.setPixmap(QPixmap(self.ICON_GREEN_LED))

        if self.dataBin[3][0] == '1':  # Выходная энергия выходит за границы допустимого диапазона (не ошибка)
            pass

        if self.requestModules:
            # -------------------------------------------------------------------#
            #                   Старший байт состояния модулей                   #
            # -------------------------------------------------------------------#
            if self.dataBin[4][7] == '0':  # Модуль задающего генератора не готов
                self.w_root.label_47.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[4][7] == '1':  # Модуль задающего генератора готов
                self.w_root.label_47.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[4][6] == '1':  # Ошибка модуля задающего генератора
                self.w_root.label_46.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_46.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[4][5] == '0':  # Модуль задающего генератора не работет
                self.w_root.label_48.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[4][5] == '1':  # Модуль задающего генератора работает
                self.w_root.label_48.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[4][4] == '0':  # Модуль регенеративного усилителя не готов
                self.w_root.label_26.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[4][4] == '1':  # Модуль регенеративного усилителя готов
                self.w_root.label_26.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[4][3] == '1':  # Ошибка модуля регенеративного усилителя
                self.w_root.label_25.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_25.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[4][2] == '0':  # Модуль регенеративного усилителя не работает или 1064 не в норме
                self.w_root.label_58.setText('Не в норме')
                self.w_root.label_58.setStyleSheet('border-radius: 14;background-color: rgb(255, 0, 0,120);')
                self.isEn1064 = False
            elif self.dataBin[4][2] == '1':  # Модуль регенеративного усилителя работает 1064 в норме
                self.w_root.label_58.setText('В норме')
                self.w_root.label_58.setStyleSheet('border-radius: 14;background-color: rgb(25, 255, 0, 100);')
                self.isEn1064 = True

            if self.dataBin[4][1] == '0':  # Модуль регенеративного усилителя не работает или 532  не в норме
                self.w_root.label_59.setText('Не в норме')
                self.w_root.label_59.setStyleSheet('border-radius: 14;background-color: rgb(255, 0, 0,120);')
                self.isEn532 = False
            elif self.dataBin[4][1] == '1':  # Модуль регенеративного усилителя работает 532 в норме
                self.w_root.label_59.setText('В норме')
                self.w_root.label_59.setStyleSheet('border-radius: 14;background-color: rgb(25, 255, 0, 100);')
                self.isEn532 = True

            if self.isEn532 and self.isEn1064:
                self.w_root.label_27.setPixmap(QPixmap(self.ICON_GREEN_LED))
            else:
                self.w_root.label_27.setPixmap(QPixmap(self.ICON_RED_LED))

            if self.dataBin[4][0] == '0':  # Пустой бит (Всегда 0)
                pass
            elif self.dataBin[4][0] == '1':
                pass

            # -------------------------------------------------------------------#
            #                   Младший байт состояния модулей                   #
            # -------------------------------------------------------------------#

            if self.dataBin[5][7] == '0':  # Модуль накачки 1 не готов
                self.w_root.label_8.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][7] == '1':  # Модуль накачки 1 готов
                self.w_root.label_8.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][6] == '1':  # Ошибка модуля накачки 1
                self.w_root.label_10.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_10.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[5][5] == '0':  # Модуль накачки 1 не работает
                self.w_root.label_9.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][5] == '1':  # Модуль накачки 1 работает
                self.w_root.label_9.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][4] == '0':  # Модуль накачки 2 не готов
                self.w_root.label_12.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][4] == '1':  # Модуль накачки 2 готов
                self.w_root.label_12.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][3] == '1':  # Ошибка модуля накачки 2
                self.w_root.label_11.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_11.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[5][2] == '0':  # Модуль накачки 2 не работает
                self.w_root.label_13.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][2] == '1':  # Модуль накачки 2 работает
                self.w_root.label_13.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][1] == '0':  # Перключатель синхронизации в положении ВНУТР
                self.w_root.label_34.setText('ВНУТР')
            elif self.dataBin[5][1] == '1':  # Перключатель синхронизации в положении ВНЕШН
                self.w_root.label_34.setText('ВНЕШН')

            if self.dataBin[5][0] == '0':  # Переключатель МУ/ЦУ находится в положении МУ
                self.w_root.label_36.setText('МУ')
            elif self.dataBin[5][7] == '1':  # Переключатель МУ/ЦУ находится в положении ЦУ
                self.w_root.label_36.setText('ЦУ')

        elif self.requestModules == False:

            # -------------------------------------------------------------------#
            #                   Старший байт состояния устройств                 #
            # -------------------------------------------------------------------#

            if self.dataBin[4][7] == '0':  # Термоконтроллер АЭ не готов
                self.w_root.label_71.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[4][7] == '1':  # Термоконтроллер АЭ готов
                self.w_root.label_71.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[4][6] == '1':  # Ошибка термоконтроллера АЭ
                self.w_root.label_72.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_72.setPixmap(QPixmap(self.ICON_BLUE_LED))

            # Добавил Егоров Петр

            if self.dataBin[4][5] == '0':  # Термоконтроллер ГВГ не готов
                self.w_root.label_73.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[4][5] == '1':  # Термоконтроллер ГВГ готов
                self.w_root.label_73.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[4][4] == '1':  # Ошибка термоконтроллера ГВГ
                self.w_root.label_74.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_74.setPixmap(QPixmap(self.ICON_BLUE_LED))

            # -------------------------------------------------------------------#
            #                   Младший байт состояния устройств                 #
            # -------------------------------------------------------------------#

            if self.dataBin[5][7] == '0':  # Термоконтроллер LD1 не готов
                self.w_root.label_60.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][7] == '1':  # Термоконтроллер LD1 готов
                self.w_root.label_60.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][6] == '1':  # Ошибка Термоконтроллера LD1
                self.w_root.label_61.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_61.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[5][5] == '0':  # Выходная мощность LD1 не в норме
                self.w_root.label_62.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][5] == '1':  # Выходная мощность LD1 в норме
                self.w_root.label_62.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][4] == '1':  # Ошибка драйвера тока LD1
                self.w_root.label_66.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_66.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[5][3] == '0':  # Термоконтроллер LD2 не готов
                self.w_root.label_80.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][3] == '1':  # Термоконтроллер LD2 готов
                self.w_root.label_80.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][2] == '1':  # Ошибка Термоконтроллера LD2
                self.w_root.label_81.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_81.setPixmap(QPixmap(self.ICON_BLUE_LED))

            if self.dataBin[5][1] == '0':  # Выходная мощность LD2 не в норме
                self.w_root.label_82.setPixmap(QPixmap(self.ICON_RED_LED))
            elif self.dataBin[5][1] == '1':  # Выходная мощность LD2 в норме
                self.w_root.label_82.setPixmap(QPixmap(self.ICON_GREEN_LED))

            if self.dataBin[5][0] == '1':  # Ошибка драйвера тока LD2
                self.w_root.label_84.setPixmap(QPixmap(self.ICON_RED_LED))
            else:
                self.w_root.label_84.setPixmap(QPixmap(self.ICON_BLUE_LED))



class SendRepeat(QThread):
    out_signal = pyqtSignal(tuple)
    checkCon = pyqtSignal(bool)

    def __init__(self, myIp):
        QThread.__init__(self)
        self.tx = ''
        self.ip = '__init__'
        self.port = ''
        self.my_ip = myIp

        self.wait_for_send = False


    def run(self):
        self.running = True
        adr = (self.ip, self.port)
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind((self.my_ip, self.port))
        udp_socket.settimeout(0.2)
        clck = 0

        while self.running:
            self.msleep(1)

            if self.wait_for_send == True:
                if self.tx == ['#', '\x03', 'E', '\x00']:
                    tx_data_type = 'stMOD'
                    data_or_merr = 0

                elif self.tx == ['#', '\x03', 'E', '\x01']:
                    tx_data_type = 'stUSTR'
                    data_or_merr = 0

                elif self.tx == ['#', '\x03', 'O', '\x00']:
                    tx_data_type = 'laserOFF'
                    data_or_merr = 1

                elif self.tx == ['#', '\x03', 'P', '\x00']:
                    tx_data_type = 'laserON'
                    data_or_merr = 1

                elif self.tx == ['#', '\x03', 'N', '\x00']:
                    tx_data_type = 'setMU'
                    data_or_merr = 1

                elif self.tx == ['#', '\x03', 'U', '\x00']:
                    tx_data_type = 'setCU'
                    data_or_merr = 1

                tx = self.tx
                self.wait_for_send = False

            else:
                self.msleep(50)
                tx = ['#', '\x03', 'E', '\x00']
                tx_data_type = 'stMOD_Repeat'
                data_or_merr = 0


            try:
                functions.SendMess(tx, udp_socket, adr)
                print('Sent : ', tx)
                data = functions.ReadMess(udp_socket)[0]
                print('RX Repeat : ', data)
                self.out_signal.emit((data, tx_data_type, data_or_merr))
                clck = 0
                self.checkCon.emit(True)

            except:
                print('Querry exception')
                clck += 1
                if clck > 3:
                    clck = 4
                    tx = ''
                    self.checkCon.emit(False)

        udp_socket.close()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exec()
