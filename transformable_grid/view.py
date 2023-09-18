from PySide6 import QtWidgets, QtCore, QtGui
import geometry as gty

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTools")
        self.setGeometry(200, 100, 500, 300)
        label = QtWidgets.QLabel()
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridSize = 10
        self.subventanas = []
        # MENU
        open_button = QtGui.QAction("&Open", self)
        open_button.triggered.connect(self.open_file)
        self.filename_edit = QtWidgets.QLineEdit()

        save_button = QtGui.QAction("&Save", self)
        # save_button.triggered.connect(self.buttonClick)
        
        transform_button = QtGui.QAction("&Transform", self)
        transform_button.triggered.connect(self.createDestGrid)

        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("&File")
        file_menu.addAction(open_button)
        file_menu.addAction(save_button)

        action_menu = self.menu.addMenu("&Actions")
        action_menu.addAction(transform_button)
 
    def open_file(self):
        path = self.search_file()
        if path is None:
            return
        grid = gty.TransformableGrid(self.gridSize,path)
        ventana = Subventana('Origin.py',grid)
        ventana.show()
        self.subventanas.append(ventana)
        
    def createDestGrid(self):
        path = 'PPS/Criminalistic_tools/transformable_grid/resources/aspect_ratio.png'
        grid = gty.TransformableGrid(self.gridSize,path)
        ventana = Subventana('Destination.py',grid)
        ventana.show()
        self.subventanas.append(ventana)

    def search_file(self):
        filename, ok = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select a File",
            "D:\\icons\\avatar\\",
            "Images (*.png *.jpg)"
        )
        return filename   
    
class Subventana(QtWidgets.QWidget):
    def __init__(self, name, widget: QtWidgets):
        super().__init__()
        #self.setGeometry(200, 100, widget.height(),  widget.width())
        self.setWindowTitle(name)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)


app = QtWidgets.QApplication()
window = MainWindow()
window.show()
app.exec()
