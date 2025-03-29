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
        self.setStyleSheet("QWidget{background-color: #fff;}")

        self.resize(350, 400)
        self.setWindowTitle('SoundpIRad')

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMaximum(100)
        self.slider.setPageStep(1)
        self.slider.setProperty("value", 50)
        self.slider.setSliderPosition(50)

        self.button = QPushButton("")
        self.button2 = QPushButton("")
        self.button4 = QPushButton("")
        self.picture = QPushButton("")

        self.box = QComboBox()
        self.box.setContextMenuPolicy(Qt.CustomContextMenu)
        self.box.setFont(QtGui.QFont("monospace", 12))
        self.box.customContextMenuRequested.connect(self.showMenu)

        sounds = self.loadsounds()
        self.data['sounds'] = sounds['sounds']
        try:
            self.box.addItems(sounds['sounds'])
        except:
            self.box.addItems([])

        self.picture.setStyleSheet("""
            border-radius: 0px;
            background-image: url("img/sound.png");
        """)
        self.button.setStyleSheet("""
        QPushButton{
            border-radius: 6px;
            background-image: url("img/play.png");
        }
        """)
        self.button2.setStyleSheet("""
        QPushButton{
            border-radius: 6px;
            background-image: url("img/add.png");
        }
        """)
        self.button4.setStyleSheet("""
        QPushButton{
            border-radius: 6px;
            background-image: url("img/pause.png");

        }
        """)
        
        self.box.setStyleSheet("""
        QComboBox {
        color: rgb(80,80,80);
        background: #f1f1f1;
        border-width: 1px;
        border-style: solid;
        border-color: #f1f1f1;  
        border-radius: 4px;   
    }

    QComboBox:hover {
        border-color: #d7d7d7;   
    }
    
    QComboBox:on {
        border-bottom-width: 3px;
        border-bottom-color: #f1f1f1;
        border-bottom-right-radius: 0px;
        border-bottom-left-radius: 0px;
    }

    QComboBox::drop-down:on {
        border-bottom-right-radius: 0px;
    }

    QComboBox QAbstractItemView {
        color: rgb(80,80,80);
        background: #f1f1f1;
        border-width: 1px;
        border-style: solid;
        border-color: #d7d7d7;
        selection-background-color: rgb(200, 200, 200);
        selection-color: rgb(25, 25, 25);
        }

    QComboBox::drop-down {
        background: #f1f1f1;
    }

    QComboBox::down-arrow {
        background: #f1f1f1;
        width: 13px;
        height: 13px;
    }

    QComboBox::down-arrow:on {
        background-color: #f1f1f1;
        width: 13px;
        height: 13px;
    } 
    """)
        self.slider.setStyleSheet("""
        QSlider::groove:horizontal {
    height: 40px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    border-radius: 4px;   
    background-color: #f1f1f1;
    margin: 2px 0;
}

QSlider::handle:horizontal {
    width: 20px;
    background: #d9d9d9;
    border-radius: 4px;
    margin: 0; /* expand outside the groove */
}

QSlider::add-page:horizontal {
    background: #f1f1f1;
    border-radius: 4px;
    margin: 2px 0;
}

QSlider::sub-page:horizontal {
    background: #d9d9d9;
    border-radius: 4px;
    margin: 2px 0;
}

        """)
        self.picture.setFixedSize(40, 40)
        self.button.setFixedSize(72, 63)
        self.button2.setFixedSize(63, 63)
        self.button4.setFixedSize(72, 63)
        self.box.setFixedHeight(40)
        self.slider.setFixedHeight(40)
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
        '''self.layout.addWidget(self.slider, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.box, alignment=Qt.AlignHCenter)
        self.layoutH.addWidget(self.button)
        self.layoutH.addWidget(self.button4)
        self.layoutH.addWidget(self.button2)
        self.layout.addLayout(self.layoutH)'''

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
        except: None
        finally: event.accept()

if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    main.run()