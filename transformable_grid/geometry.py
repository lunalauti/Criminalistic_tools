from PySide6 import QtCore, QtGui, QtWidgets
from drawer import GridDisplay
from phantom import geometry
import cv2 
import numpy as np

class Cycle(list):

    def __getitem__(self, index):
        i = index % len(self)
        return super().__getitem__(i)

class TransformableGrid(GridDisplay):

    pointsChanged = QtCore.Signal()

    finished = QtCore.Signal()
    """Emited when the user has finished editing the points."""

    def __init__(self, parent: QtWidgets.QWidget = None, pixmap: QtGui.QPixmap = None):
        """
        Initializes the PixmapPreview class.
        """
        super().__init__(parent, pixmap)
        self.setMinimumHeight(600)
        self.setMinimumWidth(400)
        self._path = 'D:/Backup/Facultad/PPS/queiloscopy/ipa.jpg'
        imagen = QtGui.QPixmap(self._path)
        self._imgcopy = imagen.copy()
        self.setPixmap(self._imgcopy)
        self.setMouseTracking(True)
        self._pointsImageSpace = []  # type: list[QtCore.QPoint]
        self._rectPoints = []  # type: list[QtCore.QPoint]
        self._gridControlPoints = []
        self._controlPoints = []
        self._gridLines = []
        self._steps = 10

        self._curvePoints = []
        self._curves = []

        self._cursorPoint = None  # type: QtCore.QPoint
        self._hasFinished = False
        self._hightlightedPointIndex = -1  # type: int
        self._selectedControlPointIndex = -1
        self._draggedPointIndex = -1  # type: int
        self._draggedControlPointIndex = -1  # type: int
        self._pointHitAreaRadius = 15  # type: int
        self._requiredPoints = 4  # type: int

        self._drag = False

        # Visual settings
        self._pointsPen = QtGui.QPen(QtGui.QColor("#9B59B6"), 6)
        self._pointsPen = QtGui.QPen(QtGui.QColor("#1ABC9C"), 4)
        self._highlightedPointPen = QtGui.QPen(QtGui.QColor("#EFD547"), 10)
        self._controlPointPen = QtGui.QPen(QtGui.QColor("#2980B9"), 10)
        self._gridLinesPen = QtGui.QPen(QtGui.QColor("#CCC"), 2)
        self._editingLinePen = QtGui.QPen(QtGui.QColor("#CCC"), 2)
        self._finishedlinePen = QtGui.QPen(QtGui.QColor("#FFF"), 2)

        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

    def addRectPoint(self, point: QtCore.QPoint):
        """
        Adds a point to the preview. The point must be in the image's coordinate system.
        """
        point = self._clampToImage(point)
        self._pointsImageSpace.append(point)
        self._rectPoints.append(self.imageToWidgetTransform().map(point))
        self.pointsChanged.emit()
        self.update()

    def addControlPoint(self, point: QtCore.QPoint):
        point = self._clampToImage(point)
        self._controlPoints.append(point)
        self.pointsChanged.emit()
        self.update()

    def setRectPoint(self, index: int, point: QtCore.QPoint):
        """
        Sets a point. The point must be in the image's coordinate system.
        """
        if index < 0 or index >= len(self._pointsImageSpace):
            return
        point = self._clampToImage(point)
        self._pointsImageSpace[index] = point
        self._rectPoints[index] = self.imageToWidgetTransform().map(point)
        self.pointsChanged.emit()
        self.update()

    def setControlPoint(self, index: int, point: QtCore.QPoint):
        if index < 0 or index >= len(self._controlPoints):
            return
        point = self._clampToImage(point)
        self._controlPoints[index] = point
        self.pointsChanged.emit()
        self.update()

    def removePoint(self, index: int):
        """
        Removes a point.
        """
        if index < 0 or index >= len(self._pointsImageSpace):
            return
        self._pointsImageSpace.pop(index)
        self._rectPoints.pop(index)
        self.pointsChanged.emit()
        self.update()

    def clearPoints(self) -> None:
        """
        Clears the points.
        """
        self._pointsImageSpace.clear()
        self._rectPoints.clear()
        self._hasFinished = False
        self.pointsChanged.emit()

    def paintEvent(self, event: QtGui.QPaintEvent):
        """
        Paints the widget.
        """
        painter = QtGui.QPainter(self)

        rectPoints = self._rectPoints
        controlPoints = self._controlPoints
        grid = self._gridLines
        
        curvePoints = points = []
        for line in self._curvePoints:
            for point in line:
                curvePoints.append(point)

        [points.append(x) for x in curvePoints if x not in points]

        if self._hasFinished:
            grid.append(self._curvePoints[0])
            grid.append(self._curvePoints[2])

            self._drawPoints(painter,curvePoints,self._pointsPen)
            self._drawGrid(painter, grid)
            self._drawCurves(painter,curvePoints)
       
        elif len(rectPoints) > 0:
            self._drawUnfinishedBorders(painter,rectPoints)

        self._drawPoints(painter,rectPoints,self._pointsPen)
        self._drawPoints(painter,controlPoints,self._controlPointPen)
         
        color = Cycle(["#5499C7", "#1ABC9C", "#F1C40F", "#E67E22", "#ECF0F1", "#34495E","#641E16"])

        for i, point in enumerate(self._gridControlPoints):
            painter.setPen(QtGui.QPen(QtGui.QColor(color[i]), 12))
            painter.drawPoint(point)

    def _drawCurves(self, painter,curvePoints):
        painter.setCompositionMode(
            QtGui.QPainter.CompositionMode.RasterOp_SourceXorDestination)
        painter.setPen(self._finishedlinePen)
        painter.drawPolygon(curvePoints)
    
    def _drawUnfinishedBorders(self, painter, line):
        painter.setCompositionMode(
            QtGui.QPainter.CompositionMode.RasterOp_SourceXorDestination)
        painter.setPen(self._editingLinePen)
        painter.drawPolyline(line)
        painter.drawLine(line[-1], self._cursorPoint)

    def _drawPoints(self, painter, points, style):
        painter.setCompositionMode(
            QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
        for i, point in enumerate(points):
            if i == self._hightlightedPointIndex:
                painter.setPen(self._highlightedPointPen)
            else:
                painter.setPen(style)
            painter.drawPoint(point)

    def _drawGrid(self, painter, gridLines):
        painter.setCompositionMode(
            QtGui.QPainter.CompositionMode.RasterOp_SourceXorDestination)
        painter.setPen(self._gridLinesPen)

        for line in gridLines[:-2]:
            painter.drawPolyline(line)

        p = []
        p.append(transformToPoint(gridLines[-2]))
        
        for line in gridLines[:self._steps -1]:
            p.append(transformToPoint(line))
        p.append(transformToPoint(gridLines[-1]))
        print(p)
        grid = geometry.grid_from_lines(p,self._steps)
        img = cv2.imread(self._path)
        grid._draw_points(img,255,2)
        cv2.imshow('color',img)

    def _widgetToImage(self, point: QtCore.QPoint) -> QtCore.QPoint:
        """
        Converts a point from widget space to image space and clamps it to the image's bounds.
        """
        point = self.widgetToImageTransform().map(point)
        point = self._clampToImage(point)
        return point

    def _clampToImage(self, point: QtCore.QPoint) -> QtCore.QPoint:
        """
        Clamps a point to the image's bounds.
        """
        pixmapSize = self.pixmap().size()
        x = max(0, min(point.x(), pixmapSize.width()))
        y = max(0, min(point.y(), pixmapSize.height()))
        return QtCore.QPoint(x, y)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """
        Handles mouse press events.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self._hasFinished and self._hightlightedPointIndex >= 0:
                # Start dragging a point
                self._draggedPointIndex = self._hightlightedPointIndex
            elif self._hasFinished and self._selectedControlPointIndex >= 0:
                self._draggedControlPointIndex = self._selectedControlPointIndex

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            if not self._hasFinished:
                # Remove the last point
                if len(self._pointsImageSpace) > 0:
                    self._pointsImageSpace.pop()
                    self._rectPoints.pop()
                    self.pointsChanged.emit()
                    self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """
        Handles mouse move events.
        """
        self._cursorPoint = event.pos()
        cursorPosInImageSpace = self._widgetToImage(event.pos())

        if self._draggedPointIndex >= 0:
            # Drag a point
            self.setRectPoint(self._draggedPointIndex, cursorPosInImageSpace)
            #TODO Agregar que se modifique la curva nuevamente
            """
            for i, line in enumerate(self._curves):
                if line == self._rectPoints[self._draggedPointIndex]:
                    print(f'coincide {i} = {line}')
                    self.updateCurve(i)
            self.getGrid()"""
            

        elif self._draggedControlPointIndex >= 0:
            #Drag a control point
            index = self._draggedControlPointIndex
            self.setControlPoint(index, event.pos())
            self.updateCurve(index)
            """
            self._curvePoints[self._draggedControlPointIndex] = []
            for x, y in getCurve(self._steps + 1, lines, control):
                self._curvePoints[self._draggedControlPointIndex].append(QtCore.QPoint(x, y))
            self.getGrid()"""

        elif self._hasFinished:
            # Check if the cursor is over a point
            self._hightlightedPointIndex = -1
            self._selectedControlPointIndex = -1
            minDist = self._pointHitAreaRadius
            for i, point in enumerate(self._rectPoints):
                distance = (point - event.pos()).manhattanLength()
                if distance < minDist:
                    self._hightlightedPointIndex = i
                    minDist = distance
            if self._hightlightedPointIndex == -1:
                for i, point in enumerate(self._controlPoints):
                    distance = (point - event.pos()).manhattanLength()
                    if distance < minDist:
                        self._selectedControlPointIndex = i
                        minDist = distance

        self._updateCursor()
        self.update()

    def updateCurve(self, index):        
        lines = self._curves[index]
        control = self._controlPoints[index].toTuple()    
        self._curvePoints[index] = []
        for x, y in getCurve(self._steps + 1, lines, control):
            self._curvePoints[index].append(QtCore.QPoint(x, y))
        self.getGrid()

    def _updateCursor(self):
        if self._draggedPointIndex >= 0 or self._draggedPointIndex >= 0:
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        elif self._hightlightedPointIndex >= 0:
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        elif self._selectedControlPointIndex >= 0:
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        else:
            self.unsetCursor()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        """
        Handles mouse release events.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:

            if self._draggedPointIndex >= 0:
                # Stop dragging a point
                self._draggedPointIndex = -1
                self.createControlPoints(self._rectPoints)

            elif self._draggedControlPointIndex >= 0:
                self._draggedControlPointIndex = -1
            elif not self._hasFinished:
                # Add a point
                point = self._widgetToImage(event.pos())
                self.addRectPoint(point)
                if len(self._pointsImageSpace) == self._requiredPoints:
                    self._hasFinished = True
                    self.createControlPoints(self._rectPoints)
                    self.getGrid()
                    self.finished.emit()

            self._updateCursor()
            self.update()

    def createControlPoints(self, points):
        tuplePoints = []
        for p in points:
            tuplePoints.append(p.toTuple())

        line_pairs = zip(tuplePoints, tuplePoints[1:] + tuplePoints[:1])

        self._controlPoints.clear()
        self._curvePoints.clear()
        for i, line in enumerate(line_pairs):
            division = segmentLine(line, self._steps)
            self._curvePoints.insert(i, transformToQPoint(division))
            
            new_line = segmentLine(line)
            self._curves.insert(i, line)
            self.addControlPoint(QtCore.QPoint(new_line[1][0], new_line[1][1]))

    def getGrid(self):
        " Obtiene las lineas verticales y horizontales de acuerdo a las curvas de bezier"
        vGuides = [transformToPoint(self._curvePoints[-1][::-1]),
                   transformToPoint(self._curvePoints[1])]
        hGuides = [transformToPoint(self._curvePoints[-2][::-1]),
                   transformToPoint(self._curvePoints[0])]
        controlPoints = transformToPoint(self._controlPoints)

        hGridLines, controlh = getGridLines(
            (controlPoints[0], controlPoints[2]), vGuides, self._steps)
        vGridLines, controlv = getGridLines(
            (controlPoints[3], controlPoints[1]), hGuides, self._steps, True)

        self._gridControlPoints = transformToQPoint(controlh+controlv)

        """
        gridLines = []
        gridLines.append(transformToQPoint(linea) for linea in hGridLines)
        gridLines.append(transformToQPoint(linea) for linea in vGridLines)"""
        gridLines = list(transformToQPoint(linea) for linea in (hGridLines+vGridLines))
        self._gridLines = gridLines

def segmentLine(line, n=2):
    "Divide las lineas en n segmentos (default n=2)"
    start = line[0][:]
    end = line[1][:]
    dif = np.subtract(end,start)
    new_line = []
    for x in list(float(start[0] + dif[0]/n * step) for step in range(n+1)):
        y = float(start[1] + (x - start[0]) / dif[0] * dif[1])
        new_line.append((x,y))
    return new_line

def transformToPoint(qpoints: list[QtCore.QPoint]) -> list[tuple]:
    "Transforma QPoints en tuplas (x,y)"
    points = []
    for point in qpoints:
        points.append((point.x(), point.y()))
    return points


def transformToQPoint(points) -> list[QtCore.QPoint]:
    "Transforma tuplas (x,y) en QPoints"
    qpoints = []
    for point in points:
        qpoints.append(QtCore.QPoint(point[0], point[1]))
    return qpoints


def getGridLines(controlPoints, xtremePoints, steps, vertical = False):
    "Obtiene las curvas de bezier para formar las grilla en una direccion"
    gridLines = []
    gridPoints = []
    # Obtenemos todos los puntos de control interpolados entre las 2 rectas
    for i, controlPoint in enumerate(linealInterpolation(controlPoints[0], controlPoints[1], steps, vertical), 1):
        gridPoints.append(controlPoint)
        P = xtremePoints[0][i]
        Q = xtremePoints[1][i]
        # Calculamos los puntos de las curvas de bezier intermedias
        gridLines.append([])
        for point in getCurve(steps+1, line=(P, Q), controlPoint=controlPoint):
            gridLines[-1].append((point[0], point[1]))
    return gridLines, gridPoints


def linealInterpolation(control1, control2,  n, vertical):
    "Calcula los puntos de control para las rectas de la grilla entre 2 curvas de bezier "
    dif = np.subtract(control2, control1)
    if vertical:
        for y in list(float(control1[1] + dif[1]/n * step) for step in range(1, n+1)):
            x = float(control1[0] + (y - control1[1]) / dif[1] * dif[0])
            yield (x, y)
    else:
        for x in list(float(control1[0] + dif[0]/n * step) for step in range(1, n+1)):
            y = float(control1[1] + (x - control1[0]) / dif[0] * dif[1])
            yield (x, y)


def getCurve(n, line, controlPoint):
    "Devuelve los puntos de la curva de bezier"
    for i in range(n):
        t = i / float(n - 1)
        yield bezierCurve(line[0], line[1], controlPoint, t)


def bezierCurve(startPoint, endPoint, controlPoint, t):
    "Hace el calculo de cada punto de la curva de bezier"
    x = startPoint[0] * ((1-t)**2) + 2 * controlPoint[0] * \
        t * (1-t) + endPoint[0] * (t**2)
    y = startPoint[1] * ((1-t)**2) + 2 * controlPoint[1] * \
        t * (1-t) + endPoint[1] * (t**2)
    return x, y


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.pixmap = TransformableGrid()

        w = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout()
        w.setLayout(l)
        l.addWidget(self.pixmap)

        """palette = QtWidgets.QHBoxLayout()
        self.add_palette_buttons(palette)
        l.addLayout(palette)"""

        self.setCentralWidget(w)


app = QtWidgets.QApplication()
window = MainWindow()
window.show()
app.exec()
