from PySide6.QtWidgets import QSlider, QApplication, QMainWindow, QFileDialog, QLabel, QDockWidget, QLineEdit, QVBoxLayout
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtCore import Qt
import cv2
from collections import namedtuple
import procesamientos as proc

const = {
    'MINWIDTH': 150,
}

posicion = {
    'DER': Qt.RightDockWidgetArea,
    'IZQ': Qt.LeftDockWidgetArea,
}

Thresh = namedtuple('Thresh', 'x y')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("QStudio")
        self.setGeometry(200, 100, 800, 500)
        label = QLabel("Ingrese una imagen \nArchivo > Abrir")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

        # MENU
        open_button = QAction("&Abrir", self)
        open_button.triggered.connect(self.open_file)
        self.filename_edit = QLineEdit()

        save_button = QAction("Guardar", self)
        # save_button.triggered.connect(self.buttonClick)

        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("&Archivo")
        file_menu.addAction(open_button)
        file_menu.addAction(save_button)

        # DOCK
        label = QLabel()
        label.setStyleSheet('background-color: lightgray')

        self.text_x = QLineEdit(label)
        self.text_x.setAlignment(Qt.AlignCenter)
        self.text_x.setGeometry(2, 10, 30, 20)
        self.text_x.setMaxLength(3)
        self.text_x.setText('0')
        self.text_x.returnPressed.connect(self.text_changed)

        self.slider_x = QSlider(Qt.Orientation.Horizontal, label)
        self.slider_x.setGeometry(40, 10, 100, 20)
        self.slider_x.setMinimum(-20)
        self.slider_x.setMaximum(200)
        self.slider_x.setSingleStep(20)
        self.slider_x.setTickPosition(QSlider.TicksBelow)
        self.slider_x.setTickInterval(20)
        self.slider_x.valueChanged.connect(self.value_changed)

        self.text_y = QLineEdit(label)
        self.text_y.setAlignment(Qt.AlignCenter)
        self.text_y.setGeometry(2, 40, 30, 20)
        self.text_y.setMaxLength(3)
        self.text_y.setText('0')
        self.text_y.returnPressed.connect(self.text_changed)

        self.slider_y = QSlider(Qt.Orientation.Horizontal, label)
        self.slider_y.setGeometry(40, 40, 100, 20)
        self.slider_y.setMinimum(-20)
        self.slider_y.setMaximum(200)
        self.slider_y.setSingleStep(20)
        self.slider_y.setTickPosition(QSlider.TicksBelow)
        self.slider_y.setTickInterval(20)
        self.slider_y.valueChanged.connect(self.value_changed)

        self.build_dock("Controles", label, posicion['DER'])

    def value_changed(self, value):
        x = self.slider_x.value()
        y = self.slider_y.value()

        self.text_x.setText(str(x))
        self.text_y.setText(str(y))

        thresh = Thresh(x, y)
        img = proc.cannyThreshold(self.img_copy,thresh)
        print(img.shape)
        self.set_img(img)
        

    def text_changed(self):
        self.slider_x.setValue(int(self.text_x.text()))
        self.slider_y.setValue(int(self.text_y.text()))

    def build_dock(self, title, widget, position):
        dock = QDockWidget()
        dock.setWindowTitle(title)
        dock.setWidget(widget)
        dock.setMinimumWidth(const['MINWIDTH'])
        self.addDockWidget(position, dock)

    def open_file(self):
        path = self.search_file()
        img_original = cv2.imread(path)
        self.img_copy = img_original.copy()
        img = cv2.cvtColor(self.img_copy, cv2.COLOR_BGR2RGB)
        self.set_img(img)

    def search_file(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            "D:\\icons\\avatar\\",
            "Images (*.png *.jpg)"
        )
        return filename
    
    def set_img(self,img):
        h, w, *ch  = img.shape
        if not ch:
            ch = 1
        else:
            ch = ch[0]
        
        img = QImage(img.data, w, h, ch * w, QImage.Format_RGB888)
        scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
        self.centralWidget().setPixmap(QPixmap.fromImage(scaled_img))

app = QApplication()

window = MainWindow()
window.show()

app.exec()
