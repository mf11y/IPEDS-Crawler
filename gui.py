import json
import os
import urllib.request

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

IPEDSURL = "https://nces.ed.gov/datacenter/"

'''
class Worker(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit
'''


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(500, 500, 600, 500)
        self.layout = QVBoxLayout()

        self.cwd = os.getcwd()
        print(self.cwd)

        self.jsondata = {}

        self.retrievebutton = QPushButton()

        self.surveylabel = QLabel()
        self.surveys = QComboBox()

        self.titlelabel = QLabel()
        self.title = QListWidget()

        self.download = QPushButton()

        self.initUI()

        w = QWidget()
        w.setLayout(self.layout)

        self.setCentralWidget(w)

        self.show()

    def selectedSurvey(self):
        self.populateTitle()

    def populateTitle(self):
        self.title.clear()
        print('hello')

        currentdict = self.jsondata[self.surveys.currentText()]
        yearlist = []
        orderlist = []

        for item in currentdict:
            yearlist.clear()
            print(item)

            for y in currentdict[item]:
                yearlist.append(y)

            orderlist.append(item + '      [ ' + min(yearlist) + ' - ' + max(yearlist) +' ] ')

        orderlist.sort()

        for item in orderlist:
            self.title.addItem(item)

    def selectedTitle(self):
        self.activatedownload()


    def activatedownload(self):
        self.download.setEnabled(True)

    def createDirs(self):
        if not os.path.exists(self.surveys.currentText()):
            os.makedirs(self.surveys.currentText() + '\\' + self.surveys.currentText() + ' Extracted Stata Data Files' +
                        '\\' + self.surveys.currentText() + ' Original Zipped Stata Data')
            os.makedirs(
                self.surveys.currentText() + '\\' + self.surveys.currentText() + ' Extracted Stata Program Files'
                + '\\' + self.surveys.currentText() + ' Original Zipped Stata Program Files')
            os.makedirs(self.surveys.currentText() + '\\' + self.surveys.currentText() +
                        ' Extracted Dictionary Data Files' + '\\' + self.surveys.currentText()
                        + ' Original Zipped Dictionary Data Files')

    def crawl(self):
        self.retrievebutton.setText("Please Wait")
        self.retrievebutton.setEnabled(False)
        command = 'scrapy'
        args = ['runspider', 'Crawler.py']
        process = QProcess(self)
        process.finished.connect(self.retrieveJSON)
        process.start(command, args)

    def retrieveJSON(self, exitCode, exitStatus):
        with open('ipeds.json', 'r') as fp:
            self.jsondata = json.load(fp)

        self.setWidgets()

    def setWidgets(self):
        self.retrievebutton.setText("Links retrieved")
        self.surveys.setEnabled(True)
        self.title.setEnabled(True)
        for item in self.jsondata:
            self.surveys.addItem(item)

    def initUI(self):

        self.retrievebutton.setText("Retrieve Links")
        self.retrievebutton.pressed.connect(self.crawl)

        self.surveylabel.setText('Survey')
        self.surveys.activated.connect(self.selectedSurvey)

        self.titlelabel.setText('Title')
        self.title.activated.connect(self.selectedTitle)

        self.download.setText('Download Files')
        self.download.pressed.connect(self.createDirs)

        self.surveys.setEnabled(False)
        self.title.setEnabled(False)
        self.download.setEnabled(False)

        self.layout.addWidget(self.retrievebutton)
        self.layout.addWidget(self.surveylabel)
        self.layout.addWidget(self.surveys)
        self.layout.addWidget(self.titlelabel)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.download)


app = QApplication([])
window = MainWindow()
app.exec_()