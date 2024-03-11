#!/usr/bin/env python3
import sys, signal, math, argparse
# try:
#     from PyQt import QtWidgets, QtGui, QtCore
# except ImportError:
#     from PyQt5 import QtWidgets, QtGui, QtCore

from PyQt5.QtWidgets import QTextEdit, QApplication, QMainWindow
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import QTimer
# from PyQt5.QtGui import QFontDatabase
# from PyQt5.QtWidgets import QGraphicsOpacityEffect
# from PyQt5.QtCore import QPropertyAnimation

# aliases
ceil = math.ceil
floor = math.floor

# Create an argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--timeout', '-t', type=int, default=0, help='Set timeout value')
parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
parser.add_argument('--floating', '-f', action='store_true', default=False, help='Floating window')
parser.add_argument('--opacity', '-o', type=float, default=0.8, help='Set window opacity')
parser.add_argument('--font', '-F', type=str, default="menlo", help='Set font')
parser.add_argument('--size', '-s', type=int, default=24, help='Set font size')
parser.add_argument('text', nargs='?', type=str, help="Text to display, or '-' to read from STDIN")
args = parser.parse_args()

# parameters and defaults
max_screen_width_ratio = 0.8
max_screen_height_ratio = 0.8
text_margin = 20
app_name = "shout"
fade_in_duration = 1000  # TODO
fade_out_duration = 1000  # TODO

import inspect

def debug(debug_item):
    if args.debug:
        print(f"DEBUG: {debug_item}")

class ShoutText(QTextEdit):
    def __init__(self, parent=None):
        super(ShoutText, self).__init__(parent)

        self.window = parent

        self.font = QFont(
            args.font, args.size
        )
        self.setFont(self.font)
        self.document().setDocumentMargin(text_margin)
        self.setReadOnly(True)

        window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus)
        window.setAttribute(Qt.WA_ShowWithoutActivating)  # Show the window without activating it

        if args.floating:
            # Set the window to stay on top of all others
            window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)

        if args.timeout > 0:
            debug(f"setting auto close duration to {args.timeout} ms")
            QTimer.singleShot(args.timeout * 1000, window.close)
        else:
            debug("auto close duration is set to 0, not closing automatically")

    def setText(self, text):
        the_text = text.rstrip()
        debug(f"ShoutText.setText: {the_text}")
        super(ShoutText, self).setText(the_text)
        # QApplication.processEvents()  # Process all pending events - needed as layout updated asynchronously
        # self.resize_window()
        QTimer.singleShot(0, self.resize_window)  # Delay the resizing

    def resize_window(self):
        debug("ShoutText.resize_window")

        doc = self.document()
        win = self.window

        # Calculate the width of the longest line
        lines = self.toPlainText().split('\n')
        debug(f"ShoutText.resize_window: len(lines) is {len(lines)}")
        font_metrics = QFontMetrics(self.font)
        max_width = max(font_metrics.horizontalAdvance(line) for line in lines)

        screen_width_max = (max_screen_width_ratio * app.desktop().screenGeometry().width())  # Get the screen width
        screen_height_max = (max_screen_height_ratio * app.desktop().screenGeometry().height())  # Get the screen height

        max_height = doc.size().height()
        # debug(f"self.font.pixelSize() is {self.font.pixelSize()}")
        # doc_height = len(lines) * self.font.pixelSize()  # Calculate the height of the document
        # doc_height = doc().size().height()
        debug(f"ShoutText.resize_window: doc_height is {max_height}")

        # Add the document margin to the width
        margin = doc.documentMargin()
        max_width += (2 * margin)  # Add the margin to both sides
        max_height += (2 * margin)  # Add the margin to both sides

        self.window.setFixedHeight(int(min(ceil(max_height), screen_height_max)))
        self.window.setFixedWidth(int(min(ceil(max_width), screen_width_max)))

        debug(f"ShoutText.resize_window: window size is {win.size().width()} x {win.size().height()}")

        # Center the window on the screen
        screen_geometry = app.desktop().screenGeometry()
        window_geometry = win.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        win.move(window_geometry.topLeft())


# Try to change the argv[0] value
try:
    sys.argv[0] = app_name
    debug(sys.srgv)
except Exception:
    debug("setting argv[0] failed")
    pass  # Ignore any exceptions

# Create a QApplication instance
app = QApplication(sys.argv)
app.setApplicationDisplayName(app_name)
signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C to close the application

# Create a QMainWindow instance
window = QMainWindow()
window.setWindowOpacity(
    args.opacity
)  # Set the opacity to 0.8 (1.0 is fully opaque, 0.0 is fully transparent)

# Make the window borderless
window.setWindowFlags(Qt.FramelessWindowHint)

# Create a QTextEdit widget to display the text
text_widget = ShoutText(window)


debug("args.text is " + str(args.text))
debug("args.timeout is " + str(args.timeout))

if args.text is None:
    print(parser.format_help())
    sys.exit(1)
elif args.text == '-':
    stdin_text = sys.stdin.read()
    text_widget.setText(stdin_text)
else:
    text_widget.setText(args.text)

window.setCentralWidget(text_widget)

# resize_window()


# Show the QMainWindow
window.show()

# Start the QApplication event loop
sys.exit(app.exec_())