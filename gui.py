import json
import os
import requests
import zipfile

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

IPEDSURL = "https://nces.ed.gov/ipeds/datacenter/"


class Worker(QObject):

    downloadSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloadSignal.connect(self.download_files)

    @pyqtSlot(dict)
    def download_files(self, files):
        import time

        for x in files:
            for y in files[x]:
                r = requests.get(IPEDSURL + y, stream=True)
                print(IPEDSURL + y)
                print(x + '\\' + y.split('/')[1])
                filepath = x + '\\' + y.split('/')[1]
                with open(filepath, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)

                updir = filepath.split('\\')[0] + '\\'+ filepath.split('\\')[1] + '\\'
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(updir)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        screen = app.primaryScreen()
        size = screen.size()
        self.setGeometry(30, 30, size.width()/2, size.height() - 100)
        self.initUI()
        self.jsondata = {}


    def activateDirName(self):
        self.dirName.setEnabled(True)

    def activateDLButton(self):
        self.download.setEnabled(True)

    def filterandSort(self):
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

    def downloadFiles(self):

        pathsCreated = self.createDirsForIncomingFiles()

        linksToDL = self.collectLinksForSelected()

        dirPathandLinksdict = self.linkPathsandLinks(pathsCreated, linksToDL)

        print(dirPathandLinksdict)

        self.worker.downloadSignal.emit(dirPathandLinksdict)


    def createDirsForIncomingFiles(self):

        dirName = self.dirName.text()
        mainDir = self.surveys.currentText()

        stata_dataDirs = mainDir + '\\' + dirName + ' Extracted Stata Data Files' + '\\' + dirName + \
                         ' Original Zipped Stata Data'
        stata_programDirs = mainDir + '\\' + dirName + ' Extracted Stata Program Files' + '\\' + dirName + \
                            ' Original Zipped Stata Program Files'
        dictDirs = mainDir + '\\' + dirName + ' Extracted Dictionary Data Files' + '\\' + dirName + \
                   ' Original Zipped Dictionary Data Files'

        if not os.path.exists(mainDir):
            os.makedirs(stata_dataDirs)
            os.makedirs(stata_programDirs)
            os.makedirs(dictDirs)

        return {'Stata_DataDir': stata_dataDirs, 'Stata_ProgramDir': stata_programDirs, 'DictionaryDir': dictDirs}

    def collectLinksForSelected(self):

        surveyName = self.surveys.currentText()
        filesToDL = {}

        for x in range(len(self.title.selectedItems())):
            title = self.title.selectedItems()[x].text().split('|')[0].strip()
            year = self.title.selectedItems()[x].text().split('|')[1].strip()

            for y in self.jsondata[surveyName][title][year]:
                if y in filesToDL:
                    filesToDL[y] = filesToDL[y] + [self.jsondata[surveyName][title][year][y]]
                else:
                    filesToDL[y] = [self.jsondata[surveyName][title][year][y]]


        return filesToDL

    def linkPathsandLinks(self, pathsCreated, linksToDL):
        dirPathandLinksdict = {}

        dirPathandLinksdict[pathsCreated['Stata_DataDir']] = linksToDL['stata_link']
        dirPathandLinksdict[pathsCreated['Stata_ProgramDir']] = linksToDL['stata_program_link']
        dirPathandLinksdict[pathsCreated['DictionaryDir']] = linksToDL['dictionary']

        return dirPathandLinksdict

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
        self.layout = QVBoxLayout()

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

        w = QWidget()
        w.setLayout(self.layout)

        self.setCentralWidget(w)

        self.show()

        self.retrievebutton = QPushButton()
        self.retrievebutton.setText("Retrieve Links")
        self.retrievebutton.pressed.connect(self.crawl)

        self.surveylabel.setText('Survey')

        self.filterlabel.setText('Filter (Show only entries >= date)')

        self.filterEdit.setText('1980')
        self.filterEdit.returnPressed.connect(self.filterandSort)

        self.filterbutton.setText('Filter')
        self.filterbutton.pressed.connect(self.filterandSort)

        self.titlelabel.setText('Title')
        self.title.setFont(QFont('Arial', 10))
        self.title.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.title.itemClicked.connect(self.activateDirName)

        self.dirNameLabel.setText('Directory Names')
        self.dirName.setText('DirName')
        self.dirName.textEdited.connect(self.activateDLButton)

        self.download.setText('Download Files')
        self.download.clicked.connect(self.downloadFiles)

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
