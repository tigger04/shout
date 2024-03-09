#!/usr/bin/env python3
import sys, signal, math
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation

# aliases
ceil = math.ceil
floor = math.floor

# parameters and defaults
max_screen_width_ratio = 0.8
max_screen_height_ratio = 0.8
text_margin = 20
floating_window = True
app_name = "shout!"
fade_in_duration = 1000  # TODO
fade_out_duration = 1000  # TODO
auto_close_duration = 5000  # TODO
window_opacity = 0.8

class ShoutText(QTextEdit):
    def __init__(self, parent=None):
        super(ShoutText, self).__init__(parent)

        self.window = parent

        # self.font = QFontDatabase.systemFont(
        #     QFontDatabase.FixedFont
        # )  # Set the font to system's monospaced font
        # self.setFontPointSize(24)  # Set the font size to 18 points

        self.font = QFont(
            "Sudoers", 24
        )  # Set the font to a generic monospaced font and size to 24 points
        self.setFont(self.font)
        self.document().setDocumentMargin(text_margin)
        self.setReadOnly(True)

        if floating_window:
            # Set the window to stay on top of all others
            window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        if auto_close_duration > 0:
            print("setting auto close duration to", auto_close_duration, "ms")
            QTimer.singleShot(auto_close_duration, window.close)

    def setText(self, text):
        super(ShoutText, self).setText(text.rstrip('\n'))
        # QApplication.processEvents()  # Process all pending events - needed as layout updated asynchronously
        # self.resize_window()
        QTimer.singleShot(0, self.resize_window)  # Delay the resizing

    def resize_window(self):
        print("ShoutText.resize_window")

        doc = self.document
        win = self.window

        # Calculate the width of the longest line
        # text = self.toPlainText().rstrip('\n') # Remove trailing newlines
        lines = self.toPlainText().split('\n')
        font_metrics = QFontMetrics(self.font)
        max_width = max(font_metrics.horizontalAdvance(line) for line in lines)

        # Add the document margin to the width
        margin = doc().documentMargin()
        max_width += (2 * margin)  # Add the margin to both sides

        screen_width_max = (max_screen_width_ratio * app.desktop().screenGeometry().width())  # Get the screen width
        screen_height_max = (max_screen_height_ratio * app.desktop().screenGeometry().height())  # Get the screen height

        doc_height = doc().size().height()

        self.window.setFixedHeight(int(min(ceil(doc_height), screen_height_max)))
        self.window.setFixedWidth(int(min(ceil(max_width), screen_width_max)))

        # Center the window on the screen
        screen_geometry = app.desktop().screenGeometry()
        window_geometry = win.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        win.move(window_geometry.topLeft())


# Try to change the argv[0] value
try:
    sys.argv[0] = app_name
except Exception:
    print("setting argv[0] failed")
    pass  # Ignore any exceptions

# Create a QApplication instance
app = QApplication(sys.argv)
app.setApplicationDisplayName(app_name)
signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C to close the application

# Create a QMainWindow instance
window = QMainWindow()
window.setWindowOpacity(
    window_opacity
)  # Set the opacity to 0.8 (1.0 is fully opaque, 0.0 is fully transparent)

# Make the window borderless
window.setWindowFlags(Qt.FramelessWindowHint)

# Create a QTextEdit widget to display the text
text_widget = ShoutText(window)

# def resize_window():
#     print("Resizing window")
#     doc_height = text_widget.document().size().height()
#     window.setFixedHeight(min(int(doc_height), screen_height_max))
#     window.setFixedWidth(min(max_width, screen_width_max))

# Connect the QTextEdit.document().sizeChanged signal to a slot that resizes the window
# text_widget.document().documentLayout().documentSizeChanged.connect(resize_window)

# Read from STDIN and set the text of the QTextEdit widget
stdin_text = sys.stdin.read()
text_widget.setText(stdin_text)

# # Calculate the width of the longest line
# lines = stdin_text.split('\n')
# font_metrics = QFontMetrics(font)
# max_width = max(font_metrics.width(line) for line in lines)

# Set the QTextEdit widget as the central widget of the QMainWindow
window.setCentralWidget(text_widget)

# resize_window()


# Show the QMainWindow
window.show()

# Start the QApplication event loop
sys.exit(app.exec_())
