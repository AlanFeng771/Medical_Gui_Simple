from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence
import widgets
import logging
import os
import numpy as np
logger = logging.getLogger(__name__)
class Controller(QtWidgets.QWidget):
    def __init__(self):
        super(Controller, self).__init__()
        self.initWidget()
        
    def initWidget(self):
        # widgets
        self.player_left = widgets.PlayerView()
        self.player_right = widgets.PlayerView()
        self.load_image_left_button = widgets.LoadImageButton()
        self.load_image_right_button = widgets.LoadImageButton()

        # main layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout_players = QtWidgets.QHBoxLayout()
        HBlayout_players.addWidget(self.player_left)
        HBlayout_players.addWidget(self.player_right)
        
        HBlayout_buttons = QtWidgets.QHBoxLayout()
        HBlayout_buttons.addWidget(self.load_image_left_button)
        HBlayout_buttons.addWidget(self.load_image_right_button)
        
        VBlayout.addLayout(HBlayout_players)
        VBlayout.addLayout(HBlayout_buttons)
        
        # func 
        self.load_image_left_button.load_image_clicked.connect(lambda file_name: self.load_image(file_name, self.player_left))
        self.load_image_right_button.load_image_clicked.connect(lambda file_name: self.load_image(file_name, self.player_right))
    
    def load_image(self, file_name, player):
        image = np.load(file_name)
        player.load_image(image)
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.setGeometry(500, 300, 1200, 600)
    controller.showMaximized()
    sys.exit(app.exec_())