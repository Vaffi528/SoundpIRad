from PyQt5.QtWidgets import QSlider, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QGroupBox, QButtonGroup, QListWidget, QTextEdit, QLineEdit, QInputDialog, QComboBox, QMenu, QMenuBar, QAction, QDialog, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import multiprocessing
import json

from pathlib import Path 

import sounddevice as sd
import soundfile as sf

import playsound_

class Main(QWidget):
    def __init__(self):
        super().__init__()
        #set data
        self.data={"sounds":[]}
        self.volume = 0.5

        #set window parametrs
        self.resize(350, 400)
        self.setWindowTitle('SoundpIRad')

        #create slider
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMaximum(100)
        self.slider.setPageStep(1)
        self.slider.setProperty("value", 50)
        self.slider.setSliderPosition(50)

        #create buttons
        self.button = QPushButton("")
        self.button2 = QPushButton("")
        self.button4 = QPushButton("")
        self.picture = QPushButton("")

        #create combobox
        self.box = QComboBox()
        self.box.setContextMenuPolicy(Qt.CustomContextMenu)
        self.box.setFont(QtGui.QFont("monospace", 12))
        self.box.customContextMenuRequested.connect(self.showMenu)

        #load sounds to combobox
        sounds = self.loadsounds()
        self.data['sounds'] = sounds['sounds']
        try:
            self.box.addItems(sounds['sounds'])
        except:
            self.box.addItems([])

        #set style
        self.setStyleSheet(Path('style/main.css').read_text())
        self.picture.setStyleSheet(Path('style/picture.css').read_text())
        self.button.setStyleSheet(Path('style/playbutton.css').read_text())
        self.button2.setStyleSheet(Path('style/addbutton.css').read_text())
        self.button4.setStyleSheet(Path('style/pausebutton.css').read_text())
        self.box.setStyleSheet(Path('style/box.css').read_text())
        self.slider.setStyleSheet(Path('style/slider.css').read_text())

        #set size of all elements
        self.picture.setFixedSize(40, 40)
        self.button.setFixedSize(72, 63)
        self.button2.setFixedSize(63, 63)
        self.button4.setFixedSize(72, 63)
        self.box.setFixedHeight(40)
        self.slider.setFixedHeight(40)

        #set all elements on the main screen
        self.layout = QVBoxLayout()
        self.layoutH = QHBoxLayout()
        self.layouth = QHBoxLayout()
        self.layouth.addWidget(self.picture)
        self.layouth.addWidget(self.slider)
        self.layout.addLayout(self.layouth)
        self.layout.addWidget(self.box)
        self.layout.addStretch(1)
        self.layout.addLayout(self.layoutH)
        self.layoutH.addWidget(self.button, alignment=Qt.AlignLeft)
        self.layoutH.addWidget(self.button4, alignment=Qt.AlignLeft)
        self.layoutH.addStretch(1)
        self.layoutH.addWidget(self.button2, alignment=Qt.AlignRight)

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
        self.terminate()

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
        try:
            self.process1.terminate()
            self.process2.terminate()
        except AttributeError: None

    def set_volume(self):
        self.volume = self.slider.value()/100

    def run(self, app):
        self.slider.valueChanged.connect(self.set_volume)
        self.button4.clicked.connect(self.terminate)
        self.button2.clicked.connect(self.add_sound)
        self.button.clicked.connect(self.play)
        self.setLayout(self.layout)
        self.show()
        app.exec_()

    def closeEvent(self, event):
        try: self.terminate()
        except: None
        finally: event.accept()