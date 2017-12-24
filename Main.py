
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import shutil


class AddMapDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add new map")
        self.resize(600, 100)

        rootLayouot = QGridLayout()
        self.setLayout(rootLayouot)

        # name
        nameLable = QLabel("Name")
        rootLayouot.addWidget(nameLable, 0, 0)
        self.nameLine = QLineEdit()
        rootLayouot.addWidget(self.nameLine, 0, 1)

        # source
        sourceLable = QLabel("Source")
        rootLayouot.addWidget(sourceLable, 1, 0)
        self.sourceLine = QLineEdit()
        rootLayouot.addWidget(self.sourceLine,1,1)
        sourcePathButton = QPushButton("selecte folder")
        def sourcePathButtonCallBack() :
            path = QFileDialog.getExistingDirectory()
            if path:
                path = path.replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                self.sourceLine.setText(path)
        sourcePathButton.clicked.connect(sourcePathButtonCallBack)
        rootLayouot.addWidget(sourcePathButton, 1, 2)
        sourceFilesButton = QPushButton("selecte files")
        def sourceFilesButtonCallBack():
            files = QFileDialog.getOpenFileNames()[0]
            if files:
                filesStr = ""
                for file in files:
                    file = file.replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                    filesStr += file
                    filesStr += ","
                filesStr = filesStr[:-1]
                self.sourceLine.setText(filesStr)
        sourceFilesButton.clicked.connect(sourceFilesButtonCallBack)
        rootLayouot.addWidget(sourceFilesButton, 1, 3)

        # target
        targetLable = QLabel("Target")
        rootLayouot.addWidget(targetLable, 2, 0)
        self.targetLine = QLineEdit()
        rootLayouot.addWidget(self.targetLine, 2, 1)
        targetPathButton = QPushButton("selecte folder")
        def  targetPathButtonCallBack():
            path = QFileDialog.getExistingDirectory()
            if path:
                path = path.replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                self.targetLine.setText(path)
        targetPathButton.clicked.connect( targetPathButtonCallBack)
        rootLayouot.addWidget( targetPathButton, 2, 2)

        userWidget = QWidget()
        userLayout = QHBoxLayout()
        userWidget.setLayout(userLayout)
        rootLayouot.addWidget(userWidget, 3, 0, 1, 4)

        confirmButton = QPushButton("Confirm")
        def confirmButtonCallBack():
            if not self.sourceLine.text() or not self.targetLine.text():
                messageBox = QErrorMessage(self)
                messageBox.setWindowTitle("Error")
                messageBox.showMessage("Source or target not set")
            else:
                self.accept()
        confirmButton.clicked.connect(confirmButtonCallBack)
        userLayout.addWidget(confirmButton)

        cancelButton = QPushButton("Cancel")
        def concelButtonCallBack():
            self.reject()
        cancelButton.clicked.connect(concelButtonCallBack)
        userLayout.addWidget(cancelButton)

    def getName(self):
        return self.nameLine.text()
    def getSource(self):
        return self.sourceLine.text()
    def getTarget(self):
        return self.targetLine.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 450)

        root = QWidget()
        self.setCentralWidget(root)

        rootLayouot = QGridLayout()
        root.setLayout(rootLayouot)

        gBox = QGroupBox("Maps")
        rootLayouot.addWidget(gBox,0,0)

        gBoxLayout = QGridLayout()
        gBox.setLayout(gBoxLayout)

        view = QTreeView()
        view.setAlternatingRowColors(True)
        view.setSortingEnabled(True)
        gBoxLayout.addWidget(view,0,0,1,2)
        model = QStandardItemModel(0, 3)
        model.setHeaderData(0, Qt.Horizontal, "Name")
        model.setHeaderData(1, Qt.Horizontal, "Source")
        model.setHeaderData(2, Qt.Horizontal, "Target")
        view.setModel(model)
        view.setColumnWidth(1,350)

        addButton = QPushButton("Add")
        def addButtonCallBack():
            addMapDialog = AddMapDialog()
            if addMapDialog.exec_() == QDialog.Accepted:
                model.insertRow(0)
                model.setData(model.index(0, 0), addMapDialog.getName())
                model.setData(model.index(0, 1), addMapDialog.getSource())
                model.setData(model.index(0, 2), addMapDialog.getTarget())
        addButton.clicked.connect(addButtonCallBack)
        gBoxLayout.addWidget(addButton, 1, 0)

        removeButton = QPushButton("Remove")
        def removeButtonCallBack():
            self.removeDialog = QMessageBox()
            ret = self.removeDialog.question(self, "Confirm", "Remove selected maps?",self.removeDialog.Ok | self.removeDialog.Cancel)
            if not ret == self.removeDialog.Ok:
                return

            rows = set(index.row() for index in view.selectionModel().selectedIndexes())
            for row in rows:
                model.removeRow(row)
        removeButton.clicked.connect(removeButtonCallBack)
        gBoxLayout.addWidget(removeButton,1,1)

        openButton = QPushButton("Open")
        def openButtonCallBack():
            openFileRet = QFileDialog.getOpenFileNames()
            openFileName = ""
            if len(openFileRet) > 0 and len(openFileRet[0]) > 0:
                openFileName = openFileRet[0][0]
            else:
                return
            if openFileName:
                model.removeRows(0, model.rowCount())
                lines = open(openFileName).read().split('\n')
                for line in lines:
                    maps = line.split(';')
                    if len(maps) == 3:
                        maps[1] = maps[1].replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                        maps[2] = maps[2].replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                        row = model.rowCount()
                        model.insertRow(row)
                        model.setData(model.index(row, 0), maps[0])
                        model.setData(model.index(row, 1), maps[1])
                        model.setData(model.index(row, 2), maps[2])
        openButton.clicked.connect(openButtonCallBack)
        gBoxLayout.addWidget(openButton, 2, 0)

        saveButton = QPushButton("Save")
        def saveButtonCallBack():
            saveFileName = QFileDialog.getSaveFileName(self,'Save', filter='*.txt')[0]
            if saveFileName:
                writeFile = open(saveFileName , 'w')
                for index in range(model.rowCount()):
                    writeFile.write(model.data(model.index(index, 0)))
                    writeFile.write(";")
                    writeFile.write(model.data(model.index(index, 1)))
                    writeFile.write(";")
                    writeFile.write(model.data(model.index(index, 2)))
                    writeFile.write("\n")
        saveButton.clicked.connect(saveButtonCallBack)
        gBoxLayout.addWidget(saveButton, 2, 1)

        backUpButton = QPushButton("Back up")
        def backUpButtonCallBack():
            self.backUpDialog = QMessageBox()
            ret = self.backUpDialog.question(self, "Confirm", "Back up all maps?",self.backUpDialog.Ok | self.backUpDialog.Cancel)
            if not ret == self.backUpDialog.Ok:
                return

            for index in range(model.rowCount()):
                sourceLine = model.data(model.index(index, 1))
                sourceLine = os.path.expandvars(sourceLine)
                sourceLine = sourceLine. replace('\\', '/')
                targetLine = model.data(model.index(index, 2))
                targetLine = os.path.expandvars(targetLine)
                targetLine = targetLine.replace('\\', '/')

                for source in sourceLine.split(","):
                    command = "robocopy /DCOPY:T "
                    if os.path.isdir(source):
                        command += '/e "'+source+'" "'+targetLine+"/"+source.split("/")[-1]+'"'
                    else:
                        command += '"'+os.path.dirname(source) + '" "' + targetLine + '" "' + os.path.basename(source) +'"'
                    os.system(command)
        backUpButton.clicked.connect(backUpButtonCallBack)
        gBoxLayout.addWidget(backUpButton, 3, 0)

        restoreButton = QPushButton("Restore")
        def restoreButtonCallBack():
            self.restoreDialog = QMessageBox()
            ret = self.restoreDialog.question(self, "Confirm", "Restore all maps?",self.restoreDialog.Ok | self.restoreDialog.Cancel)
            if not ret == self.restoreDialog.Ok:
                return

            for index in range(model.rowCount()):
                sourceLine = model.data(model.index(index, 1))
                sourceLine = os.path.expandvars(sourceLine)
                sourceLine = sourceLine.replace('\\', '/')
                targetLine = model.data(model.index(index, 2))
                targetLine = os.path.expandvars(targetLine)
                targetLine = targetLine.replace('\\', '/')

                for source in sourceLine.split(","):
                    command = "robocopy /DCOPY:T "
                    if os.path.isdir(source):
                        command += '/e "'+targetLine+"/"+source.split("/")[-1]+'" "'+source +'"'
                    else:
                        command += '"'+targetLine + '" "' +os.path.dirname(source) + '" "' +  os.path.basename(source)+'"'
                    os.system(command)
        restoreButton.clicked.connect(restoreButtonCallBack)
        gBoxLayout.addWidget(restoreButton, 3, 1)

        testButton = QPushButton("test")
        def testButtonCallBack():
            writeFile= open('maps.txt', 'w')
            for index in range(model.rowCount()):
                writeFile.write( model.data(model.index(index, 0)))
                writeFile.write(";")
                writeFile.write(model.data(model.index(index, 1)))
                writeFile.write("\n")
        testButton.clicked.connect(testButtonCallBack)
        #gBoxLayout.addWidget(testButton, 3, 0)


if __name__ == '__main__':

    import sys

    App = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.setWindowTitle("back up assistant")
    MainWindow.show()
    sys.exit(App.exec_())