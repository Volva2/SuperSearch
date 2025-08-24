import sys
import os
import time
import threading
from search_content import search_content
from search_everything import search_everything
from PySide6.QtConcurrent import run
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QSplitter, QWidget, QLineEdit, QListWidget, QPushButton, QSizePolicy
from PySide6.QtGui import QFont, QIcon, QCursor

class SupperSearchLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperSearch")
        self.setWindowIconText("SuperSearch 0.0.0")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.setMaximumWidth(2000)
        self.setMinimumWidth(2000)
        self.layoutMargins = 100
        self.x = 0
        self.y = 0
        self.xDiv = self.width()/238
        self.yDiv = self.height()/50
        self.centerXY()

        self.setStyleSheet("background:rgba(130, 153, 255, 0);")
        self.setGeometry(self.x/self.xDiv, self.y/self.yDiv, 1000, 200)

        self.icon = QIcon("C:\\Usersvolva\\OneDrive\\Desktop\\Programming\\SuperSearch\\SuperSearch.png")
        self.setWindowIcon(self.icon)
        
        self.font = QFont("Victor Mono", 14)
        self.textMargin = 10

        self.overlay = None
        self.init_ui()

    def centerXY(self):
        screen = QApplication.primaryScreen().size()

        self.x = screen.width()
        self.y = screen.height()

    def init_ui(self):
        self.input = QLineEdit(self)
        self.results = QListWidget(self)
        self.exit = QPushButton(self)

        containerLayout = QVBoxLayout(self)
        
        mainLayout = QHBoxLayout(self)
        mainLayout.addWidget(self.exit)
        mainLayout.addWidget(self.input)
        mainLayout.setContentsMargins(self.layoutMargins, self.layoutMargins, self.layoutMargins, self.layoutMargins-50)
        containerLayout.addLayout(mainLayout)

        resultsLayout = QVBoxLayout(self)
        resultsLayout.addWidget(self.results)
        resultsLayout.setContentsMargins(self.layoutMargins, 0, self.layoutMargins, self.layoutMargins)
        containerLayout.addLayout(resultsLayout)

        self.setLayout(containerLayout)

        self.input.setPlaceholderText("Start your search here...")
        self.input.setFont(self.font)
        self.input.setTextMargins(self.textMargin, self.textMargin, self.textMargin, self.textMargin)
        self.input.setMaximumWidth(self.width()/1.5)
        self.input.textChanged.connect(lambda: run(self.on_search))

        self.results.setFont(self.font)
        self.results.itemActivated.connect(self.open_item)
        self.results.setVisible(False)
        self.results.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.results.setMaximumWidth(self.width())

        self.exit.setFont(self.font)
        self.exit.setText('Exit')
        self.exit.setStyleSheet("QPushButton {padding: 1em; max-width: 50%;}")
        self.exit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.exit.clicked.connect(QApplication.instance().quit)

    def on_search(self, text):
        self.results.setVisible(True)
        self.results.clear()
        
        if not text:
            return
        # Decide if it's a content search
        if text.startswith("in:"):
            matches = (search_everything(text.split(':')[1]))
            for m in matches[:20]:
                self.results.addItem(m)
        else:
            matches = search_content(text[3:])
            for m in matches[:20]:
                self.results.addItem(f"{m['file']}:{m['line']}  {m['text']}")

    def open_item(self, item):
        path = item.text().split()[0]
        os.startfile(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("C:\\Usersvolva\\OneDrive\\Desktop\\Programming\\SuperSearch\\SuperSearch.png"))
    win = SupperSearchLauncher()
    win.show()
    sys.exit(app.exec())