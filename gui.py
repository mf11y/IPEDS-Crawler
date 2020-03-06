import json

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setGeometry(500, 500, 250, 0)

        layout = QVBoxLayout()

        self.b = QPushButton("Retrieve Links")
        self.b.pressed.connect(self.crawl)

        self.c = QLineEdit()
        self.c.setText("Start Year")
        self.d = QLineEdit()
        self.d.setText("End Year")
        self.f = QComboBox()


        layout.addWidget(self.b)
        layout.addWidget(self.c)
        layout.addWidget(self.d)
        layout.addWidget(self.f)

        self.c.setEnabled(False)
        self.d.setEnabled(False)
        self.f.setEnabled(False)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

    def crawl(self):
        self.b.setText("Please Wait")
        self.b.setEnabled(False)
        command = 'scrapy'
        args = ['runspider', 'Crawler.py']
        process = QProcess(self)
        process.finished.connect(self.onFinished)
        process.start(command, args)

    def onFinished(self, exitCode, exitStatus):
        self.b.setText("Links retrieved")
        self.c.setEnabled(True)
        self.d.setEnabled(True)
        self.f.setEnabled(True)
        with open('ipeds.json', 'r') as fp:
            jsondata = json.loads(fp.read())

        for item in jsondata:
            self.f.addItem(item)

        print(jsondata)


app = QApplication([])
window = MainWindow()
app.exec_()
