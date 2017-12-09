
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

        self.source = ""
        self.target = ""

        rootLayouot = QGridLayout()
        self.setLayout(rootLayouot)

        # source
        sourceLable = QLabel("Source")
        rootLayouot.addWidget(sourceLable, 0, 0)

        sourceLine = QLineEdit()
        def sourceLineEdit():
            self.source = sourceLine.text()
        sourceLine.textEdited.connect(sourceLineEdit)
        rootLayouot.addWidget(sourceLine,0,1)

        sourcePathButton = QPushButton("selecte folder")
        def sourcePathButtonCallBack() :
            path = QFileDialog.getExistingDirectory()
            if path:
                path = path.replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                self.source = path
                sourceLine.setText(path)
        sourcePathButton.clicked.connect(sourcePathButtonCallBack)
        rootLayouot.addWidget(sourcePathButton, 0, 2)

        sourceFilesButton = QPushButton("selecte files")
        def sourceFilesButtonCallBack():
            files = QFileDialog.getOpenFileNames()[0]
            if files:
                print(files)
                filesStr = ""
                for file in files:
                    file = file.replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                    filesStr += file
                    filesStr += ","
                filesStr = filesStr[:-1]
                self.source = filesStr
                sourceLine.setText(filesStr)
        sourceFilesButton.clicked.connect(sourceFilesButtonCallBack)
        rootLayouot.addWidget(sourceFilesButton, 0, 3)

        # target
        targetLable = QLabel("Target")
        rootLayouot.addWidget(targetLable, 1, 0)

        targetLine = QLineEdit()
        def targetLineEdit():
            self.target = targetLine.text()
        targetLine.textEdited.connect(targetLineEdit)
        rootLayouot.addWidget(targetLine, 1, 1)
        targetPathButton = QPushButton("selecte folder")
        def  targetPathButtonCallBack():
            path = QFileDialog.getExistingDirectory()
            if path:
                path = path.replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                self.target = path
                targetLine.setText(path)
        targetPathButton.clicked.connect( targetPathButtonCallBack)
        rootLayouot.addWidget( targetPathButton, 1, 2)

        userWidget = QWidget()
        userLayout = QHBoxLayout()
        userWidget.setLayout(userLayout)
        rootLayouot.addWidget(userWidget, 2, 0, 1, 4)

        confirmButton = QPushButton("Confirm")
        def confirmButtonCallBack():
            if not self.source or not self.target:
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

    def getSource(self):
        return self.source
    def getTarget(self):
        return self.target


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 450)

        root = QWidget()
        self.setCentralWidget(root)

        rootLayouot = QGridLayout()
        root.setLayout(rootLayouot)

        gBox = QGroupBox("maps")
        rootLayouot.addWidget(gBox,0,0)

        gBoxLayout = QGridLayout()
        gBox.setLayout(gBoxLayout)

        view = QTreeView()
        view.setAlternatingRowColors(True)
        gBoxLayout.addWidget(view,0,0,1,2)
        model = QStandardItemModel(0, 2)
        model.setHeaderData(0, Qt.Horizontal, "Source")
        model.setHeaderData(1, Qt.Horizontal, "Target")
        view.setModel(model)
        view.setColumnWidth(0,350)

        addButton = QPushButton("Add")
        def addButtonCallBack():
            addMapDialog = AddMapDialog()
            if addMapDialog.exec_() == QDialog.Accepted:
                model.insertRow(0)
                model.setData(model.index(0, 0), addMapDialog.getSource())
                model.setData(model.index(0, 1), addMapDialog.getTarget())
        addButton.clicked.connect(addButtonCallBack)
        gBoxLayout.addWidget(addButton, 1, 0)

        removeButton = QPushButton("Remove")
        def removeButtonCallBack():
            rows = set(index.row() for index in view.selectionModel().selectedIndexes())
            for row in rows:
                model.removeRow(row)
        removeButton.clicked.connect(removeButtonCallBack)
        gBoxLayout.addWidget(removeButton,1,1)

        openButton = QPushButton("Open")
        def openButtonCallBack():
            openFileName = QFileDialog.getOpenFileNames()[0][0]
            if openFileName:
                model.removeRows(0, model.rowCount())
                lines = open(openFileName).read().split('\n')
                for line in lines:
                    maps = line.split(';')
                    if len(maps) == 2:
                        maps[0] = maps[0].replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                        maps[1] = maps[1].replace(os.environ['USERPROFILE'].replace('\\', '/'), "$USERPROFILE")
                        row = model.rowCount()
                        model.insertRow(row)
                        model.setData(model.index(row, 0), maps[0])
                        model.setData(model.index(row, 1), maps[1])
        openButton.clicked.connect(openButtonCallBack)
        gBoxLayout.addWidget(openButton, 2, 0)

        saveButton = QPushButton("Save")
        def saveButtonCallBack():
            saveFileName = QFileDialog.getSaveFileName()[0]
            if saveFileName:
                writeFile = open(saveFileName , 'w')
                for index in range(model.rowCount()):
                    writeFile.write(model.data(model.index(index, 0)))
                    writeFile.write(";")
                    writeFile.write(model.data(model.index(index, 1)))
                    writeFile.write("\n")
        saveButton.clicked.connect(saveButtonCallBack)
        gBoxLayout.addWidget(saveButton, 2, 1)

        backUpButton = QPushButton("Back up")
        def backUpButtonCallBack():
            for index in range(model.rowCount()):
                source = model.data(model.index(index, 0))
                source = os.path.expandvars(source)
                source = source. replace('\\', '/')
                target = model.data(model.index(index, 1))
                target = os.path.expandvars(target)
                target = target.replace('\\', '/')

                if os.path.isdir(source):
                    command = "robocopy /e /DCOPY:T  "
                    command += source
                    command += " "
                    command += target
                    command += "/"
                    sourceArray = source.split("/")
                    command += sourceArray[len(sourceArray)-1]
                    os.system(command)
                else:
                    sourceArray = source.split("/")
                    source = source.replace(sourceArray[len(sourceArray) - 1],"")

                    command = "robocopy "
                    command += source
                    command += " "
                    command += target
                    command += " "
                    command += sourceArray[len(sourceArray) - 1]
                    os.system(command)
        backUpButton.clicked.connect(backUpButtonCallBack)
        gBoxLayout.addWidget(backUpButton, 3, 0)

        restoreButton = QPushButton("Restore")
        def restoreButtonCallBack():
            for index in range(model.rowCount()):
                source = model.data(model.index(index, 1))
                source = os.path.expandvars(source)
                source = source.replace('\\', '/')
                target = model.data(model.index(index, 0))
                target = os.path.expandvars(target)
                target = target.replace('\\', '/')

                if os.path.isdir(source):
                    command = "robocopy /e /DCOPY:T  "
                    command += source
                    command += " "
                    command += target
                    command += "/"
                    sourceArray = source.split("/")
                    command += sourceArray[len(sourceArray) - 1]
                    os.system(command)
                else:
                    sourceArray = source.split("/")
                    source = source.replace(sourceArray[len(sourceArray) - 1], "")

                    command = "robocopy "
                    command += source
                    command += " "
                    command += target
                    command += " "
                    command += sourceArray[len(sourceArray) - 1]
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