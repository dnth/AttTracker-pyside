from PySide import QtCore, QtGui, QtWebKit

class TransWindow(QtGui.QDialog):
    """
    Example of a partially transparent browser window
    Base on screenshot: http://goo.gl/UiULPU
    """
    
    HOME = "http://www.kde.org"

    def __init__(self):
        super(TransWindow, self).__init__()
        self.resize(800,600)

        style = QtGui.qApp.style()

        self.backButton = QtGui.QToolButton(self)
        self.backButton.setIcon(style.standardIcon(style.SP_ArrowLeft))

        self.forwardButton = QtGui.QToolButton(self)
        self.forwardButton.setIcon(style.standardIcon(style.SP_ArrowRight))

        self.reloadButton = QtGui.QToolButton(self)
        self.reloadButton.setIcon(style.standardIcon(style.SP_BrowserReload))

        self.location = QtGui.QLineEdit(self)

        self.webView = QtWebKit.QWebView(self)
        self.webView.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                   QtGui.QSizePolicy.Expanding)

        toolLayout = QtGui.QHBoxLayout()
        toolLayout.setSpacing(0)
        toolLayout.addWidget(self.backButton)
        toolLayout.addWidget(self.forwardButton)
        toolLayout.addSpacing(6)
        toolLayout.addWidget(self.reloadButton)
        toolLayout.addSpacing(6)
        toolLayout.addWidget(self.location)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setSpacing(16)
        self.layout.addLayout(toolLayout)
        self.layout.addWidget(self.webView)

#         self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
#         self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
#         self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
#         self.setStyleSheet("background:transparent;")
#         self.setStyleSheet("""
#             QDialog {
#                 background-color: rgba(50,50,50,35%);
#                 border-radius: 5px;
#             }
#             """)

        self.backButton.clicked.connect(self.webView.back)
        self.forwardButton.clicked.connect(self.webView.forward)
        self.reloadButton.clicked.connect(self.webView.reload)
        self.location.returnPressed.connect(self._updateLocation)
        self.webView.urlChanged.connect(self._locationChanged)

    def showEvent(self, event):
        super(TransWindow, self).showEvent(event)
        self.webView.load(QtCore.QUrl(self.HOME))

    def _updateLocation(self):
        text = self.location.text().strip()
        if not text:
            return          

        # Being really basic here, for the demo
        url = QtCore.QUrl(text)
        if not url.scheme():
            url.setScheme("http")
        self.webView.load(url)

    def _locationChanged(self, url):
        self.location.setText(url.toString())


if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TransWindow()
    win.show()
    win.raise_()
    app.exec_()