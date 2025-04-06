from soundplayer import Main
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

if __name__ == "__main__":
    app = QApplication([])
    app.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
    main = Main()
    main.run(app)