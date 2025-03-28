import sys
from PyQt5.QtWidgets import QApplication, QSlider, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QGroupBox, QButtonGroup, QListWidget, QTextEdit, QLineEdit, QInputDialog, QComboBox, QMenu, QMenuBar, QAction, QDialog, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent
import multiprocessing
import json

import sounddevice as sd
import soundfile as sf

import playsound_

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.data={"sounds":[]}
        self.volume = 0.5
        self.setStyleSheet("QWidget{background-color: #6f9bcb;}")

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMaximum(100)
        self.slider.setPageStep(1)
        self.slider.setProperty("value", 50)
        self.slider.setSliderPosition(50)
        
        self.button = QPushButton("Play")
        self.button.setFont(QtGui.QFont("Times New Roman", 12))
        self.button2 = QPushButton("Add sound")
        self.button2.setFont(QtGui.QFont("Times New Roman", 12))
        self.button4 = QPushButton("Stop")
        self.button4.setFont(QtGui.QFont("Times New Roman", 12))
        self.box = QComboBox()
        self.box.setContextMenuPolicy(Qt.CustomContextMenu)
        self.box.customContextMenuRequested.connect(self.showMenu)
        sounds = self.loadsounds()
        self.data['sounds'] = sounds['sounds']
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
        self.layout.addWidget(self.slider, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.box, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.button4, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.button2, alignment=Qt.AlignHCenter)

    def add_sound(self):
        files = QFileDialog()
        files.setFileMode(QFileDialog.ExistingFiles)
        sounds = files.getOpenFileNames(self, "Open files", filter='Audio (*.mp3 *.wav *.ogg)')[0]
        sounds = list(map(lambda x: x.split('/')[-1], sounds))
        if sounds == []:
            return
        
        box_items = [self.box.itemText(i) for i in range(self.box.count())]
        sounds_ = list()
        for sound in sounds:
            if sound not in box_items:
                sounds_.append(sound)
        
        self.data['sounds'] = box_items + sounds_
        self.dumpsounds()
        self.updatebox()

    def showMenu(self,pos):
        menu = QMenu()
        clear_action = menu.addAction("Clear Selection")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == clear_action:
            self.remove()
    
    def remove(self):
        self.box.removeItem(self.box.currentIndex())
        self.data['sounds'] = [self.box.itemText(i) for i in range(self.box.count())]
        self.dumpsounds()

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

    def play(self):
        # terminating all previous processes
        try: self.terminate()
        except AttributeError: None

        #receiving data about choosen sound
        boxindex = self.box.currentIndex()
        filename = f'music/{self.box.currentText()}'

        # extracting data and sampling frequency from the file
        try: 
            data, fs = sf.read(filename, dtype='float64')  
        except: 
            self.box.removeItem(boxindex)
            return
            
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
        self.process1 = multiprocessing.Process(target=playsound_.playmusic, args=(dict(devices)['index'], data, fs, self.volume))
        self.process2 = multiprocessing.Process(target=playsound_.playmusic, args=(index, data, fs, self.volume))
        self.process2.start()
        self.process1.start()
        
    def terminate(self):
        self.process1.terminate()
        self.process2.terminate()

    def set_volume(self):
        self.volume = self.slider.value()/100

    def run(self):
        self.slider.valueChanged.connect(self.set_volume)
        self.button4.clicked.connect(self.terminate)
        self.button2.clicked.connect(self.add_sound)
        self.button.clicked.connect(self.play)
        self.setLayout(self.layout)
        self.show()
        app.exec_()

    def closeEvent(self, event):
        try: self.terminate()
        except AttributeError: None
        finally: event.accept()

if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    main.run()