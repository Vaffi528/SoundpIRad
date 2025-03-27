import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QGroupBox, QButtonGroup, QListWidget, QTextEdit, QLineEdit, QInputDialog, QComboBox, QMenu, QMenuBar, QAction, QDialog, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import multiprocessing
import json

import sounddevice as sd
import soundfile as sf

import playsound_

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.data={"sounds":[]}
        self.setStyleSheet("QWidget{background-color: #6f9bcb;}")

        self.button = QPushButton("Play")
        self.button.setFont(QtGui.QFont("Times New Roman", 12))
        self.button2 = QPushButton("Add sound")
        self.button2.setFont(QtGui.QFont("Times New Roman", 12))
        self.button4 = QPushButton("Stop")
        self.button4.setFont(QtGui.QFont("Times New Roman", 12))
        self.box = QComboBox()
        sounds = self.loadsounds()
        try:
            self.box.addItems(sounds['sounds'])
        except:
            self.box.addItems([])
            
        self.button.setStyleSheet("""
        QPushButton{
            font-style: oblique;
            font-weight: bold;
            border: 1px solid #1DA1F2;
            border-radius: 15px;
            color: #1DA1F2;
            background-color: #fff;
        }
        """)

        self.button2.setStyleSheet("""
        QPushButton{
            font-style: oblique;
            font-weight: bold;
            border: 1px solid #1DA1F2;
            border-radius: 15px;
            color: #1DA1F2;
            background-color: #fff;
        }
        """)
        self.button4.setStyleSheet("""
        QPushButton{
            font-style: oblique;
            font-weight: bold;
            border: 1px solid #1DA1F2;
            border-radius: 15px;
            color: #1DA1F2;
            background-color: #fff;
        }
        """)
        self.button.setFixedSize(100, 40)
        self.button2.setFixedSize(100, 40)
        self.button4.setFixedSize(100, 40)
        self.box.setFixedSize(120, 20)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.box, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.button4, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.button2, alignment=Qt.AlignHCenter)

    def updatebox(self):
        try:
            self.box.clear()
            self.box.addItems(self.data['sounds'])
        except:
            self.box.addItems([])

    def loadsounds(self):
        with open('data/data.json', "r", encoding='utf-8') as file:
            return json.load(file)
    
    def dumpsounds(self):
        with open('data/data.json', "w", encoding='utf-8') as file:
            json.dump(self.data, file)

    def add_sound(self):
        def close():
            filename = self.edit.text()
            data = self.loadsounds()
            try:
                self.data['sounds'] = data['sounds']
            except:
                None
            finally:
                self.data['sounds'].append(filename)
            self.dumpsounds()
            self.updatebox()
            self.mydile.close()

        self.edit = QLineEdit()
        self.edit.setFont(QtGui.QFont("Times New Roman", 14))
        self.edit.setPlaceholderText("type the path of a sound")
        self.edit.setFixedHeight(40)
        self.edit.setStyleSheet("""
        QLineEdit{
            border: 1px solid #CCD6DD;
        }
        """)
        self.mydile = QDialog()
        self.mydile.resize(300,200)
        self.layout1 = QVBoxLayout()
        self.mydile.setWindowTitle('new sound')
        self.button3 = QPushButton("Add sound")
        self.button3.setFont(QtGui.QFont("Times New Roman", 12))

        self.button3.clicked.connect(close)

        self.layout1.addWidget(self.edit, alignment=Qt.AlignHCenter)
        self.layout1.addWidget(self.button3, alignment=Qt.AlignHCenter)
        self.mydile.setLayout(self.layout1)
        self.mydile.exec_()

    def play(self):
        # terminating all previous processes
        try: self.terminate()
        except AttributeError: None

        filename = f'music/{self.box.currentText()}'

        # extracting data and sampling frequency from the file
        data, fs = sf.read(filename, dtype='float64')  

        # receiving all useful data of the sound devices
        devices = sd.query_devices(kind='output')
        devicesall = list(sd.query_devices())
        hostapis = sd.query_hostapis()

        # setting the idexes of devices with needed api
        for element in hostapis:
            if element['name'] == 'MME': #or Windows DirectSound, or Windows WASAPI, or Windows WDM-KS
                deviceindexes = element['devices']
                break
        
        # finding the index of needed device
        index = None
        for element in devicesall:
            if element['name'].startswith('CABLE Input') and 'VB-Audio' in element['name'] and element['index'] in deviceindexes:
                index = int(element['index'])
                break
        
        #defining and starting the processes
        self.process1 = multiprocessing.Process(target=playsound_.playmusic, args=(dict(devices)['index'], data, fs))
        self.process2 = multiprocessing.Process(target=playsound_.playmusic, args=(index, data, fs))
        self.process2.start()
        self.process1.start()
        
    def terminate(self):
        self.process1.terminate()
        self.process2.terminate()

    def run(self):
        self.button4.clicked.connect(self.terminate)
        self.button2.clicked.connect(self.add_sound)
        self.button.clicked.connect(self.play)
        self.setLayout(self.layout)
        self.show()
        app.exec_()

    def closeEvent(self, event):
        self.terminate()
        event.accept()
        
if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    main.run()