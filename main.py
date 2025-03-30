from soundplayer import Main
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    main.run(app)