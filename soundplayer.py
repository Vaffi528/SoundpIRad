from PyQt5.QtWidgets import QSlider, QDialogButtonBox, QTabWidget, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox, QListWidget, QTextEdit, QLineEdit, QInputDialog, QComboBox, QMenu, QMenuBar, QAction, QDialog, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

import multiprocessing
import json
import copy
from pathlib import Path 

import sounddevice as sd
import soundfile as sf

import playsound_

class Main(QWidget):
    def __init__(self):
        super().__init__()
        #set data
        self.data = self.load()
        if 'auto' not in self.data:
            self.data['auto'] = True
            self.dumps()
        self.volume = 0.5
        #this value need only when user play suond for the 1 time after starting the programm. It is nesessary to check indexes of devises cuz they can be changed
        self.check_device = not self.data['auto']

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
        self.button5 = QPushButton("")
        self.picture = QPushButton("")

        #create combobox
        self.box = QComboBox()
        self.box.setContextMenuPolicy(Qt.CustomContextMenu)
        self.box.setFont(QtGui.QFont("monospace", 12))
        self.box.customContextMenuRequested.connect(self.showMenu)

        #load sounds to combobox
        try:
            self.box.addItems(self.data['sounds'])
        except:
            self.box.addItems([])

        #set style
        self.setStyleSheet(Path('style/main.css').read_text())
        self.picture.setStyleSheet(Path('style/picture.css').read_text())
        self.button.setStyleSheet(Path('style/playbutton.css').read_text())
        self.button2.setStyleSheet(Path('style/addbutton.css').read_text())
        self.button4.setStyleSheet(Path('style/pausebutton.css').read_text())
        self.button5.setStyleSheet(Path('style/settingbutton.css').read_text())
        self.box.setStyleSheet(Path('style/box.css').read_text())
        self.slider.setStyleSheet(Path('style/slider.css').read_text())

        #set size of all elements
        self.picture.setFixedSize(40, 40)
        self.button.setFixedSize(72, 63)
        self.button2.setFixedSize(63, 63)
        self.button4.setFixedSize(72, 63)
        self.button5.setFixedSize(63, 63)
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
        self.layoutH.addWidget(self.button5)

    def add_sound(self):
        #getting music from user
        files = QFileDialog()
        files.setFileMode(QFileDialog.ExistingFiles)
        sounds = files.getOpenFileNames(self, "Open files", filter='Audio (*.mp3 *.wav *.ogg)')[0]
        sounds = list(map(lambda x: x.split('/')[-1], sounds))

        #check if user didnt choose anything
        if sounds == []:
            return
        
        #extracting all new files form the choosen music
        box_items = [self.box.itemText(i) for i in range(self.box.count())]
        sounds_ = list()
        for sound in sounds:
            if sound not in box_items:
                sounds_.append(sound)
        
        #concatenating new and old files and updating the combobox and data
        self.data['sounds'] = box_items + sounds_
        self.dumps()
        self.updatebox()

    def settings(self):
        #terminating all the processes and calling settings window
        self.terminate()
        SettingsWindow(self)

    def showMenu(self,pos):
        menu = QMenu()
        clear_action = menu.addAction("Clear Selection")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == clear_action:
            self.remove()
    
    def remove(self):
        self.box.removeItem(self.box.currentIndex())
        self.data['sounds'] = [self.box.itemText(i) for i in range(self.box.count())]
        self.dumps()

    def updatebox(self):
        try:
            self.box.clear()
            self.box.addItems(self.data['sounds'])
        except:
            self.box.addItems([])

    def load(self):
        with open('data/data.json', "r", encoding='utf-8') as file:
            return json.load(file)
    
    def dumps(self):
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
        
        if "devices" in self.data and len(self.data["devices"]) == 2 and self.check_device:
            device0 = self.data["devices"][0]
            device1 = self.data["devices"][1]
        else:
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
            
            # check if the device found
            if index == None:
                return

            device0 = dict(devices)['index']
            device1 = index
            self.data["devices"] = [device0, device1]
            self.dumps()
            self.check_device = True
            
        #defining and starting the processes
        self.process1 = multiprocessing.Process(target=playsound_.playmusic, args=(device0, data, fs, self.volume))
        self.process2 = multiprocessing.Process(target=playsound_.playmusic, args=(device1, data, fs, self.volume))
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
        self.button5.clicked.connect(self.settings)
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

class SettingsWindow(QDialog):
    def __init__(self, main):
        super().__init__()

        self.main = main
        self.data = copy.deepcopy(self.main.data)

        self.resize(500,250)
        self.setWindowTitle('Settings')

        tabs = QTabWidget()
        tabs.addTab(FirstTab(self.main), "devices")
        tabs.addTab(SecondTab(), "shortcuts")
        tabs.addTab(ThirdTab(), "info")
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        buttons.setFont(QtGui.QFont("monospace", 12))
        tabs.setStyleSheet(Path('style/tab.css').read_text())
        buttons.setStyleSheet(Path('style/dialogbutton.css').read_text())

        V = QVBoxLayout()
        V.addWidget(tabs)
        V.addWidget(buttons)
        
        self.setLayout(V)
        self.exec_()

    def accept(self):
        #script of OK button
        self.main.dumps()
        self.main.check_device = not self.main.data['auto']
        return super().accept()
    
    def reject(self):
        #script of Cancel button
        self.main.data = self.data
        return super().reject()

class FirstTab(QWidget):
    def __init__(self, main):
        super().__init__()

        self.devicesall = list(sd.query_devices())
        hostapis = sd.query_hostapis()

        # setting the idexes of devices with needed api
        for element in hostapis:
            if element['name'] == 'MME': #or Windows DirectSound, or Windows WASAPI, or Windows WDM-KS
                self.deviceindexes = element['devices']
                break
        
        devices = list()
        for element in self.devicesall:
            if element['max_input_channels'] == 0 and element['index'] in self.deviceindexes:
                devices.append(element['name'])
        
        for element in self.devicesall:
            if element['index'] == main.data["devices"][0] and element['index'] in self.deviceindexes:
                device0 = element['name']
                break
        for element in self.devicesall:
            if element['index'] == main.data["devices"][1] and element['index'] in self.deviceindexes:
                device1 = element['name']
                break

        self.flagbutton = QCheckBox("auto")
        self.flagbutton.setChecked(main.data['auto'])
        self.box1 = QComboBox()
        self.box1.addItems(devices)
        self.box1.setCurrentText(device0)
        self.label1 = QLabel('Device')

        self.box2 = QComboBox()
        self.box2.addItems(devices)
        self.box2.setCurrentText(device1)
        self.label2 = QLabel('Virtual cable')

        self.box1.setStyleSheet(Path('style/devicebox.css').read_text())
        self.box2.setStyleSheet(Path('style/devicebox.css').read_text())
        self.flagbutton.setStyleSheet(Path('style/checkbox.css').read_text())
        self.label1.setFont(QtGui.QFont("monospace", 10))
        self.label2.setFont(QtGui.QFont("monospace", 10))
        self.flagbutton.setFont(QtGui.QFont("monospace", 10))

        self.box1.setFixedHeight(25)
        self.box2.setFixedHeight(25)

        if main.data['auto'] == True:
            self.box1.setEnabled(0)
            self.box2.setEnabled(0)
        
        self.box1.currentTextChanged.connect(lambda: self.onChanged(main))
        self.box2.currentTextChanged.connect(lambda: self.onChanged(main))
        self.flagbutton.toggled.connect(lambda: self.onClicked(main))

        H = QHBoxLayout()
        H1 = QHBoxLayout()
        V1 = QVBoxLayout()
        V2 = QVBoxLayout()
        #H1.addWidget(self.flagbutton, alignment=Qt.AlignTop)
        V1.addWidget(self.label1, alignment=Qt.AlignTop)
        V1.addWidget(self.box1, alignment=Qt.AlignTop)
        V1.addStretch(1)
        V1.addWidget(self.flagbutton)
        V2.addWidget(self.label2, alignment=Qt.AlignTop)
        V2.addWidget(self.box2, alignment=Qt.AlignTop)
        V2.addStretch(1)
        H.addLayout(V1)
        H.addLayout(V2)

        self.setLayout(H)

    def onClicked(self, main):
        main.data['auto'] = self.flagbutton.isChecked()
        self.box1.setEnabled(not main.data['auto'])
        self.box2.setEnabled(not main.data['auto'])

    def onChanged(self, main):
        for element in self.devicesall:
            if element['name'] == self.box1.currentText() and element['index'] in self.deviceindexes:
                device1=element['index']
                break
        for element in self.devicesall:
            if element['name'] == self.box2.currentText() and element['index'] in self.deviceindexes:
                device2=element['index']
                break
        main.data["devices"] = [device1, device2]

class SecondTab(QWidget):
    def __init__(self):
        super().__init__()
        
class ThirdTab(QWidget):
    def __init__(self):
        super().__init__()
        