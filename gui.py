import json
import os
import urllib.request

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

IPEDSURL = "https://nces.ed.gov/datacenter/"


class Worker(QObject):

    filesToDL = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filesToDL.connect(self.download_files)

    @pyqtSlot(dict)
    def download_files(self, files):
        import time
        time.sleep(5)
        print(files)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        screen = app.primaryScreen()
        size = screen.size()
        self.setGeometry(30, 30, size.width()/2, size.height() - 100)

        self.layout = QVBoxLayout()

        self.jsondata = {}
        self.filesToDL = []

        self.surveylabel = QLabel()
        self.surveys = QComboBox()

        self.filterlabel = QLabel()
        self.filterEdit = QLineEdit()

        self.filterbutton = QPushButton()

        self.titlelabel = QLabel()
        self.title = QListWidget()

        self.download = QPushButton()

        self.worker = Worker()
        thread = QThread(self)
        thread.start()

        self.worker.moveToThread(thread)

        self.dirNameLabel = QLabel()
        self.dirName = QLineEdit()

        self.initUI()

        w = QWidget()
        w.setLayout(self.layout)

        self.setCentralWidget(w)

        self.show()

    def activateDirName(self):
        self.dirName.setEnabled(True)

    def activateDLButton(self):
        self.download.setEnabled(True)

    def filter(self):
        self.title.clear()

        if not str(self.filterEdit.text()).isdigit():
            self.filterEdit.setText('1980')

        currentdict = self.jsondata[self.surveys.currentText()]
        orderlist = []

        for item in currentdict:
            for y in currentdict[item]:
                if y >= self.filterEdit.text():
                    orderlist.append(item + ' | ' + y)

        orderlist.sort()

        for item in orderlist:
            self.title.addItem(item)


    def readyFiles(self):

        if not os.path.exists(self.surveys.currentText()):
            dirName = self.dirName.text()
            surveyName = self.surveys.currentText()

            os.makedirs(surveyName + '\\' + dirName + ' Extracted Stata Data Files' + '\\' + dirName +
                        ' Original Zipped Stata Data')
            os.makedirs(surveyName + '\\' + dirName + ' Extracted Stata Program Files'+ '\\' + dirName +
                        ' Original Zipped Stata Program Files')
            os.makedirs(surveyName + '\\' + dirName + ' Extracted Dictionary Data Files' + '\\' + dirName +
                        ' Original Zipped Dictionary Data Files')

        self.filesToDL.clear()
        survey = self.surveys.currentText()



        for x in range(len(self.title.selectedItems())):
            title = self.title.selectedItems()[x].text().split('|')[0].strip()
            year = self.title.selectedItems()[x].text().split('|')[1].strip()
            self.filesToDL = self.filesToDL + [self.jsondata[survey][title][year]]

        self.worker.filesToDL.emit(self.filesToDL)


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
        self.filterEdit.setEnabled(True)
        self.filterbutton.setEnabled(True)
        for item in self.jsondata:
            self.surveys.addItem(item)

    def initUI(self):

        self.retrievebutton = QPushButton()
        self.retrievebutton.setText("Retrieve Links")
        self.retrievebutton.pressed.connect(self.crawl)

        self.surveylabel.setText('Survey')

        self.filterlabel.setText('Filter (Show only entries >= date)')

        self.filterEdit.setText('1980')
        self.filterEdit.returnPressed.connect(self.filter)

        self.filterbutton.setText('Filter')
        self.filterbutton.pressed.connect(self.filter)

        self.titlelabel.setText('Title')
        self.title.setFont(QFont('Arial', 10))
        self.title.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.title.itemClicked.connect(self.activateDirName)

        self.dirNameLabel.setText('Directory Names')
        self.dirName.setText('DirName')
        self.dirName.textEdited.connect(self.activateDLButton)

        self.download.setText('Download Files')
        self.download.clicked.connect(self.readyFiles)

        self.surveys.setEnabled(False)
        self.title.setEnabled(False)
        self.download.setEnabled(False)
        self.filterEdit.setEnabled(False)
        self.filterbutton.setEnabled(False)
        self.dirName.setEnabled(False)

        self.layout.addWidget(self.retrievebutton)
        self.layout.addWidget(self.surveylabel)
        self.layout.addWidget(self.surveys)
        self.layout.addWidget(self.filterlabel)
        self.layout.addWidget(self.filterEdit)
        self.layout.addWidget(self.filterbutton)
        self.layout.addWidget(self.titlelabel)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.dirNameLabel)
        self.layout.addWidget(self.dirName)
        self.layout.addWidget(self.download)


app = QApplication([])
window = MainWindow()
app.exec_()
