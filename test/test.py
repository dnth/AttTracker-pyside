import sys 
from PyQt4.QtCore import *
from PyQt4.QtGui import * 

class MoviePlayer(QWidget): 
    def __init__(self, gif, parent=None): 
        super(MoviePlayer, self).__init__(parent)

        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle("QMovie to show animated gif")

        self.movie_screen = QLabel()
        self.movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        
        self.movie_screen.setAlignment(Qt.AlignCenter) 

        btn_start = QPushButton("Start Animation")
        btn_start.clicked.connect(self.start) 

        btn_stop = QPushButton("Stop Animation")
        btn_stop.clicked.connect(self.stop) 

        main_layout = QVBoxLayout() 
        main_layout.addWidget(self.movie_screen)
        main_layout.addWidget(btn_start) 
        main_layout.addWidget(btn_stop)
        self.setLayout(main_layout) 

        self.movie = QMovie(gif, QByteArray(), self) 
        self.movie.setCacheMode(QMovie.CacheAll) 
        self.movie.setSpeed(100) 
        self.movie_screen.setMovie(self.movie) 


    def start(self):
        """
        Start animation
        """
        self.movie.start()

    def stop(self):
        """
        Stop the animation
        """
        self.movie.stop()


app = QApplication(sys.argv) 
player = MoviePlayer("/home/camaro/Desktop/giphy.gif") 
player.show() 
sys.exit(app.exec_())