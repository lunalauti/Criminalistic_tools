from PySide6 import QtCore, QtGui, QtWidgets
import math

class GridDisplay(QtWidgets.QWidget):

    imageRectChanged = QtCore.Signal(QtCore.QRect)
    """Signal emmited when the image rectangle changes."""

    _pixmap: QtGui.QPixmap = None

    _resizedPixmap: QtGui.QPixmap = None

    _imageRect: QtCore.QRect = None

    _aspectRatioMode = QtCore.Qt.AspectRatioMode.KeepAspectRatio

    _transformationMode = QtCore.Qt.TransformationMode.SmoothTransformation

    _imageToWidgetTransform = QtGui.QTransform()

    _widgetToImageTransform = QtGui.QTransform()

    #_isDirty = True

    """
    Widget for displaying a QPixmap. The image is scaled proportionally to fit the widget.
    This class can also be used as a base class for editors that display an image.
    """
    def __init__(self, parent: QtWidgets.QWidget = None, pixmap: QtGui.QPixmap = None):
        """
        Initializes the PixmapDisplay class.

        Args:
            pixmap (QPixmap): The pixmap to display. Defaults to None.
        """
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        pixmap is not None and self.setPixmap(pixmap)

    def setPixmap(self, pixmap: QtGui.QPixmap) -> None:
        """
        Sets the pixmap to display.

        Args:
            pixmap (QPixmap): The pixmap to display.
        """
        self._pixmap = pixmap
        self._isDirty = True
        self.update()


    def imageRectChangedEvent(self, imageRect: QtCore.QRect) -> None:
        """
        Called when the image rectangle changes. This method can be overriden
        in derived classes to perform custom actions when the image rectangle changes.
        The rectangle can be null if there is no image.
        """
        self.imageRectChanged.emit(imageRect)

    def _processDirty(self) -> None:
        if not self._isDirty:
            return

        oldRect = self._imageRect
        self._isDirty = False
        if self._pixmap is not None:
            widgetW, widgetH = self.width(), self.height()
            imageW, imageH = self._pixmap.width(), self._pixmap.height()
            self._resizedPixmap = self._pixmap.scaled(widgetW, widgetH, self._aspectRatioMode, self._transformationMode)

            w, h = self._resizedPixmap.width(), self._resizedPixmap.height()
            x, y = (widgetW - w) / 2, (widgetH - h) / 2
            self._imageRect = QtCore.QRect(x, y, w, h)

            # Now we cache the 2d transformation matrix for convenience
            self._imageToWidgetTransform = QtGui.QTransform()
            self._imageToWidgetTransform.translate(x, y)
            self._imageToWidgetTransform.scale(w / imageW, h / imageH)

            self._widgetToImageTransform = QtGui.QTransform()
            self._widgetToImageTransform.scale(imageW / w, imageH / h)
            self._widgetToImageTransform.translate(-x, -y)
        else:
            self._resizedPixmap = None
            self._imageRect = None
            self._imageToWidgetTransform = QtGui.QTransform()
            self._widgetToImageTransform = QtGui.QTransform()

        if oldRect != self._imageRect:
            self.imageRectChangedEvent(self._imageRect)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._isDirty = True

    def widgetToImageTransform(self) -> QtGui.QTransform:
        """
        Gets the transform that converts points from the widget's coordinate system to the image's coordinate system.
        """
        self._processDirty()
        return self._widgetToImageTransform

    def imageToWidgetTransform(self) -> QtGui.QTransform:
        """
        Gets the transform that converts points from the image's coordinate system to the widget's coordinate system.
        """
        self._processDirty()
        return self._imageToWidgetTransform

    def imageRect(self) -> QtCore.QRect:
        """
        Gets the rectangle that the image is drawn into.
        """
        self._processDirty()
        return self._imageRect
