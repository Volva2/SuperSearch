import sys
import os
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QObject, QEvent, QThread, Signal, Slot, QSize
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QListWidget, QListWidgetItem, QLabel, QPushButton, QSizePolicy, QMessageBox
from PySide6.QtGui import QFont, QIcon, QCursor, QKeyEvent, QPixmap
from search_content import search_content
from search_everything import search_everything

class Worker(QObject):
    finished = Signal(str, list)

    @Slot(str)
    def get_file_matches(self, text: str):
        if text.casefold().startswith("in:") and "||" in text:
            everything_matches = search_everything(text.split("||")[0].strip()[3:])
            content_matches = []
            
            for i in everything_matches:
                content_matches.append(search_content(text.split("||")[1].strip(), i.split("\n")[1]))

            matches = [everything_matches, content_matches]
            print(matches)
            self.finished.emit('content', matches)
        elif text.startswith("in:") or text.startswith("IN:"):
            matches = search_everything(text[3:])
            self.finished.emit('everything', matches)
        # else:
        #     ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        #     subprocess.run(f"{ps_path} -Command {text} -ErrorAction SilentlyContinue", shell=True)


class CustomFileWidget(QWidget):
    def __init__(self, text="No text", content="", content_path="", parent=None):
        super().__init__(parent)

        font_family = "Victor Mono"
        font_size = 15
        font = QFont(font_family, font_size)

        content_layout = QVBoxLayout()
        container_layout = QHBoxLayout(self)

        filename = QLabel(text[0]) if content == "" else QLabel(content_path.split("\\")[-1])
        filepath = QLabel(text[1]) if content == "" else QLabel(content_path)
        search_content = QLabel(content)
        
        filename.setStyleSheet("padding: 0%; margin: 0%; background: transparent")
        filepath.setStyleSheet("padding: 0%; margin: 0%; background: transparent")
        search_content.setStyleSheet("""
            padding: 15%;
            background: transparent;
            color: beige;
        """)

        file_icon = QPixmap('.\icons\document.png') if os.path.isfile(filepath.text()) else QPixmap('.\icons\\folder.png')

        filename.setFont(font)
        filepath.setFont(font)
        search_content.setFont(font)

        filename.setWordWrap(True)
        filepath.setWordWrap(True)
        search_content.setWordWrap(True)
        
        filename.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        filepath.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.addWidget(filename)
        content_layout.addWidget(filepath)
        if content != "":
            content_layout.addWidget(search_content)

        icon = QLabel()
        icon.setPixmap(file_icon.scaled(50, 50))
        icon.resize(50, 50)
        icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        icon.setContentsMargins(15,5,15,5)
        icon.setStyleSheet("background: transparent")

        if text != "No text":
            container_layout.addWidget(icon)
            container_layout.addLayout(content_layout)
        else:
            container_layout.addWidget(QLabel("No such content was found"))
        
        # Store the file path for opening
        self.file_path = text[1]

    def get_file_icon(filepath, large_icon=True):
        pass

class SupperSearchLauncher(QWidget):

    input_change_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperSearch")
        self.setWindowIconText("SuperSearch 0.0.0")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.worker = Worker()
        self.text_thread = QThread()
        self.worker.moveToThread(self.text_thread)

        self.input_change_signal.connect(self.worker.get_file_matches)
        self.worker.finished.connect(self.on_everything_searched)

        self.text_thread.start()

        self.setMaximumWidth(2000)
        self.setMinimumWidth(2000)
        self.layoutMargins = 100
        self.x = 0
        self.y = 0
        self.xDiv = self.width()/238
        self.yDiv = self.height()/50
        self.centerXY()

        # self.setStyleSheet("background:rgba(130, 153, 255, 0);")
        self.setStyleSheet("background:rgba(34, 34, 34, 0.75);")
        self.setGeometry(self.x/self.xDiv, self.y/self.yDiv, self.x/1.5, self.y/1.5)

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
        mainLayout.addWidget(self.input)
        mainLayout.addWidget(self.exit)
        mainLayout.setContentsMargins(self.layoutMargins, self.layoutMargins, self.layoutMargins, self.layoutMargins-50)
        containerLayout.addLayout(mainLayout)

        resultsLayout = QVBoxLayout(self)
        resultsLayout.addWidget(self.results)
        resultsLayout.setContentsMargins(self.layoutMargins, 0, self.layoutMargins, self.layoutMargins)
        containerLayout.addLayout(resultsLayout)
        
        input_margin = self.input.width()/20
        self.input.setPlaceholderText("Start your search here...")
        self.input.setFont(self.font)
        self.input.setTextMargins(input_margin, input_margin*2, input_margin, input_margin*2)
        self.input.setMaximumWidth(self.width()/1.5)
        self.input.returnPressed.connect(self.on_search)

        self.results.setFont(self.font)
        self.results.itemActivated.connect(self.open_item)
        self.results.setVisible(False)
        self.results.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.results.setMaximumWidth(self.width())
        
        # Enable focus for the results list
        self.results.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.exit.setFont(self.font)
        self.exit.setText('Exit')
        self.exit.setStyleSheet("QPushButton {padding: 1em; max-width: 50%;}")
        self.exit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.exit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.exit.clicked.connect(QApplication.instance().quit)

    def keyPressEvent(self, event: QKeyEvent):
        if not self.results.isVisible() or self.results.count() == 0:
            super().keyPressEvent(event)
            return

        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.results.currentItem()
            if current_item:
                self.open_item(current_item)
            event.accept()
            
        elif event.key() == Qt.Key.Key_Escape:
            self.input.clear()
            self.results.setVisible(False)
            self.input.setFocus()
            event.accept()
    
    def on_search(self):
        text = self.input.text().strip()

        if not text:
            self.results.clear()
            self.results.setVisible(False)
            return

        self.results.clear()
        self.results.addItem("Searching, please wait...")
        self.results.setVisible(True)

        self.input_change_signal.emit(text)
    
    def on_everything_searched(self, type: str, matches: list):
        self.results.clear()

        if type == 'everything':
            for m in matches[:100]:
                m = m.split('\n')
                item = QListWidgetItem(self.results)
                customWidget = CustomFileWidget(m)
                item.setSizeHint(customWidget.sizeHint())
                self.results.setItemWidget(item, customWidget)

            if self.results.count() > 0:
                # Select the first item by default
                self.results.setCurrentRow(0)
        else:
            index = 0
            content = ""

            for match in matches[1][index][:50]:
                file = matches[0][index].split('\n')
                content+=f"Line {match["line"]}: {match["text"]}\n"
                content_path = match["file"]

                item = QListWidgetItem(self.results)
                customWidget = CustomFileWidget(file, content, content_path)
                item.setSizeHint(customWidget.sizeHint())
                self.results.setItemWidget(item, customWidget)
                index+=1

            if self.results.count() > 0:
                # Select the first item by default
                self.results.setCurrentRow(0)

    def open_item(self, item: QWidget):
        custom_widget = self.results.itemWidget(item)
        
        if custom_widget and hasattr(custom_widget, 'file_path'):
            file_path = custom_widget.file_path
        else:
            item_text = item.text()
            if ':' in item_text:
                file_path = item_text.split(':')[0]
            else:
                file_path = item_text.split('\n')[1] if '\n' in item_text else item_text
        
        try:
            print(file_path)
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {file_path}\nError: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("C:\\Usersvolva\\OneDrive\\Desktop\\Programming\\SuperSearch\\SuperSearch.png"))
    win = SupperSearchLauncher()
    win.show()
    sys.exit(app.exec())