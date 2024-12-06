from ast import List
from optparse import Option
from typing import Optional, Union
from PyQt5 import QtCore, QtGui, QtWidgets 
import numpy as np
import cv2
class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.current_contour_item = None
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fit_in_view(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewport = self.viewport()
                if viewport is not None:
                    viewrect = viewport.rect()
                else:
                    viewrect = QtCore.QRect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0
    
    
    def setPhoto(self, pixmap=None, contour_item=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            self._photo.setTransformationMode(QtCore.Qt.TransformationMode.SmoothTransformation)
            if contour_item is not None:
                if self.current_contour_item is not None:
                    self._scene.removeItem(self.current_contour_item)
                self.current_contour_item = contour_item
                self._scene.addItem(contour_item)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def add_item(self, item: QtWidgets.QGraphicsItem):
        self._scene.addItem(item)
    
    def remove_item(self, item: QtWidgets.QGraphicsItem):
        self._scene.removeItem(item)
      
    def wheelEvent(self, event):
        if event is None:
            return
        modifiers = event.modifiers()
        if self.hasPhoto():
            if modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:
                if event.angleDelta().y() > 0:
                    factor = 1.25
                    self._zoom += 1
                else:
                    factor = 0.75
                    self._zoom -= 1
                if self._zoom > 0:
                    self.scale(factor, factor)
                elif self._zoom == 0:
                    self.fit_in_view()
                else:
                    self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    # def mousePressEvent(self, event):
    #     if self._photo.isUnderMouse():
    #         if event is None:
    #             return
    #         point = self.mapToScene(event.pos().toPoint())
    #         if point is None:
    #             return
    #         self.photoClicked.emit(point.toPoint())
    #     super(PhotoViewer, self).mousePressEvent(event)

class PlayerView(QtWidgets.QWidget):
    def __init__(self):
        super(PlayerView, self).__init__()
        self.images = None
        self.num_of_images = 0
        self.contour_images = None
        self.initWidget()
        
    def initWidget(self):
        label_font = QtGui.QFont()
        label_font.setFamily('Verdana')
        label_font.setPointSize(12)
        label_font.setBold(True)  
        
        # PhotoViewer
        self.viewer = PhotoViewer(self)
        self.viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # Scroll bar
        self.scrollBar = QtWidgets.QScrollBar(QtCore.Qt.Orientation.Horizontal)
        self.scrollBar.setMinimum(0)
        self.scrollBar.setMaximum(0)  # 初始設置為0，因為還沒有圖片加載
        self.scrollBar.valueChanged.connect(self.show)

        # Text
        self.sliceText = QtWidgets.QLineEdit('0')
        self.sliceText.setFont(label_font)
        self.sliceText.setFixedSize(QtCore.QSize(50, 30))  # 可視需求移除這行
        self.sliceText.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.maxSliceText = QtWidgets.QLabel('/')
        self.maxSliceText.setFont(label_font)
        self.maxSliceText.setFixedSize(QtCore.QSize(50, 30))  # 可視需求移除這行
        self.maxSliceText.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        # layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.addWidget(self.scrollBar, 10)
        HBlayout.addWidget(self.sliceText, 1)
        HBlayout.addWidget(self.maxSliceText, 1)
        
        VBlayout.addWidget(self.viewer)
        VBlayout.addLayout(HBlayout)
        
        # 自動適應螢幕大小
        self.setLayout(VBlayout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    
    def _numpytoPixmap(self, image):
        image =  cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_GRAY2RGB)
        h,w,ch = image.shape
        image = QtGui.QImage(image, w, h, w*ch, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap(image)
        return pix
    
    def _generate_contour_item(self, contour_image):
        height, width = contour_image.shape
        contour_image = np.array(contour_image, dtype=np.uint8)

            
        contour_pixmap = QtGui.QPixmap(width, height)
        transparent_color = QtGui.QColor(0, 0, 0, 0)
        contour_pixmap.fill(transparent_color)
        painter = QtGui.QPainter(contour_pixmap)
        
        if np.max(contour_image) == 0:
            painter.end()
            return QtWidgets.QGraphicsPixmapItem(contour_pixmap)
        
        y_index, x_index = np.where(contour_image == 255)
        for y, x in zip(y_index, x_index):
            painter.setPen(QtGui.QColor(255, 0, 0, int((contour_image[y, x]))))  # Red color for edges
            painter.drawPoint(x, y)
        painter.end()
        contour_item = QtWidgets.QGraphicsPixmapItem(contour_pixmap)
        
        return contour_item
        
    def load_image(self, images):
        self.images = images
        if self.images is None:
            return
        self.image_index = 0
        self.num_of_images = self.images.shape[2]
        self.scrollBar.setMaximum(self.images.shape[2]-1)
        self.show_image()
    
    def show_image(self, image_index=0):
        # init
        if self.contour_images is not None:
            contour_item = self._generate_contour_item(self.contour_images[:,:,image_index])
        else:
            contour_item = None
        if self.images is not None: 
            self.viewer.setPhoto(self._numpytoPixmap(self.images[:,:,image_index]), contour_item)
            # self.viewer.fit_in_view()
        self.image_index = image_index
    
    
    def show(self, image_index:int=0):
        self.sliceText.setText(str(image_index))
        self.show_image(image_index)
    
    def set_current_scrollbar_index(self, value:int):
        self.scrollBar.setValue(value)
    
    def reset_rects(self):
        # init
        for rect in self.rects:
            self.viewer.remove_item(rect)

        del self.rects
        # init bbox annotation
        self.rects = []
    
    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers == QtCore.Qt.NoModifier:
            if event.angleDelta().y() > 0:
                action = 'next'
            else:
                action = 'previous'

            self.scroll_image(action)
            
    def scroll_image(self, type):
        if type == 'previous':
            if self.image_index > 0:
                currrent_image_index = self.image_index
                self.scrollBar.setValue(currrent_image_index-1)
        elif type == 'next':
            if self.image_index < self.num_of_images-1:
                currrent_image_index = self.image_index
                self.scrollBar.setValue(currrent_image_index+1) 

        
class LoadImageButton(QtWidgets.QPushButton):
    load_image_clicked = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(LoadImageButton, self).__init__(parent)
        self.setText('Load image')
        self.clicked.connect(self.load_image)
    
    def load_image(self):
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", "./")
        if filename != '':
            self.load_image_clicked.emit(filename)
        