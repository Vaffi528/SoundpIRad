import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QGroupBox, QButtonGroup, QListWidget, QTextEdit, QLineEdit, QInputDialog, QComboBox, QMenu, QMenuBar, QAction, QDialog, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import subprocess
import multiprocessing
import json
import sounddevice as sd

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
        filename = self.box.currentText()
        self.process = multiprocessing.Process(target=playsound, args=(filename,))
        self.process.start()
        
    def terminate(self):
        self.process.terminate()

    def run(self):
        self.button4.clicked.connect(self.terminate)
        self.button2.clicked.connect(self.add_sound)
        self.button.clicked.connect(self.play)
        self.setLayout(self.layout)
        self.show()
        app.exec_()

def playsound(filename):
    subprocess.run("./venv/Scripts/python.exe VBAplaysound.py", input=(f'music/{filename}').encode('utf-8'))

if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    main.run()