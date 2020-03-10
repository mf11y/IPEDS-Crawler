import json

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(500, 500, 250, 0)
        self.layout = QVBoxLayout()

        self.jsondata = {}

        self.retrievebutton = QPushButton()

        self.surveylabel = QLabel()
        self.surveys = QComboBox()

        self.startyear = QComboBox()
        self.startlabel = QLabel()

        self.endyear = QComboBox()
        self.endlabel = QLabel()

        self.titlelabel = QLabel()
        self.title = QComboBox()

        self.download = QPushButton()

        self.initUI()

        w = QWidget()
        w.setLayout(self.layout)

        self.setCentralWidget(w)

        self.show()

    def selectedsurvey(self, selected):
        print(self.surveys.currentText())
        self.initStartYear()

    def initStartYear(self):
        self.startyear.clear()
        self.endyear.clear()

        for item in self.jsondata[self.surveys.currentText()]:
            self.startyear.addItem(item)

    def selectedstartyear(self, selected):
        self.endyear.clear()
        for item in self.jsondata[self.surveys.currentText()]:
            if int(item) >= int(self.startyear.currentText()):
                self.endyear.addItem(item)

    def selectedendyear(self):

        years = []

        for i in range(0, self.endyear.count()):
            if self.endyear.itemText(i) <= self.endyear.currentText():
                years.append(str(self.endyear.itemText(i)))

        print (years)
        for x in years:
            print(self.jsondata[self.surveys.currentText()][x])

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
            self.jsondata = json.loads(fp.read())

        self.setWidgets()

    def setWidgets(self):
        self.retrievebutton.setText("Links retrieved")
        self.startyear.setEnabled(True)
        self.endyear.setEnabled(True)
        self.surveys.setEnabled(True)
        for item in self.jsondata:
            self.surveys.addItem(item)

    def initUI(self):

        self.retrievebutton.setText("Retrieve Links")
        self.retrievebutton.pressed.connect(self.crawl)

        self.surveylabel.setText('Survey')
        self.surveys.activated.connect(self.selectedsurvey)

        self.startlabel.setText('Start year')
        self.startyear.activated.connect(self.selectedstartyear)

        self.endlabel.setText('End year')
        self.endyear.activated.connect(self.selectedendyear)

        self.titlelabel.setText('Title')

        self.download.setText('Download Files')

        self.startyear.setEnabled(False)
        self.endyear.setEnabled(False)
        self.surveys.setEnabled(False)
        self.title.setEnabled(False)
        self.download.setEnabled(False)

        self.layout.addWidget(self.retrievebutton)
        self.layout.addWidget(self.surveylabel)
        self.layout.addWidget(self.surveys)
        self.layout.addWidget(self.startlabel)
        self.layout.addWidget(self.startyear)
        self.layout.addWidget(self.endlabel)
        self.layout.addWidget(self.endyear)
        self.layout.addWidget(self.titlelabel)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.download)


app = QApplication([])
window = MainWindow()
app.exec_()
