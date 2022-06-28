import sys
import os
import PySide2
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QFileDialog, QMessageBox
from PySide2.QtCore import QThreadPool, QTimer
import cbhash.hash_worker

import cbhash.resources

class Application(QApplication):

    filepath = ""

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(sys.argv)

        self.loader = QUiLoader()

        self.window = self.loader.load(":/main.ui")
        self.progress_widget = self.loader.load(":/progress.ui")
        
        self.isDone = False
        self.thread_pool  = QThreadPool()

        self.init()
        self.connect()

    def init(self):
        self.window.labelStatus.setText("")

    def connect(self):
        self.window.acLoadFile.triggered.connect(self.actionLoadFile)
        self.window.btnLoadFile.setDefaultAction(self.window.acLoadFile)
        self.window.acClipMD5.triggered.connect(self.copyToClipboardMD5)
        self.window.btnCopyMD5.setDefaultAction(self.window.acClipMD5)

        self.window.acClipSHA256.triggered.connect(self.copyToClipboardSHA256)
        self.window.btnCopySHA256.setDefaultAction(self.window.acClipSHA256)

        self.window.acClipSHA512.triggered.connect(self.copyToClipboardSHA512)
        self.window.btnCopySHA512.setDefaultAction(self.window.acClipSHA512)
        
    
    def copyToClipboardMD5(self):
        self.checkHasDone()

        clipboard = QApplication.clipboard()
        md5 = self.window.fieldMD5.toPlainText()
        clipboard.setText(md5)
        self.window.labelStatus.setText("Hash MD5 Copied to Clipboard!")
        QTimer.singleShot(10000, self.cleanStatusLabelInterval)
        
    def copyToClipboardSHA256(self):
        self.checkHasDone()

        clip = QApplication.clipboard()
        sha = self.window.fieldSHA256.toPlainText()
        clip.setText(sha)
        self.window.labelStatus.setText("Hash SHA256 Copied to Clipboard!")
        QTimer.singleShot(10000, self.cleanStatusLabelInterval)
        

    def copyToClipboardSHA512(self):
        self.checkHasDone()
        clip = QApplication.clipboard()
        sha = self.window.fieldSHA512.toPlainText()
        clip.setText(sha)
        self.window.labelStatus.setText("Hash SHA512 Copied to Clipboard!")
        QTimer.singleShot(10000, self.cleanStatusLabelInterval)
    
    def checkHasDone(self):
        if not self.isDone:
            QMessageBox.warning(self.window, "Warning", "No File Loaded")

    def cleanStatusLabelInterval(self):
        self.window.labelStatus.setText("")

    def actionLoadFile(self):
        fnames = None 
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if(dialog.exec_()):
            fnames = dialog.selectedFiles()

        if not fnames:
            return

        self.filepath = fnames[0]
        self.window.txtFile.setPlainText(os.path.basename(fnames[0]))

        worker = cbhash.hash_worker.HashWorker(filename=self.filepath)

        worker.signals.progress.connect(self.show_progress)
        worker.signals.hashlists.connect(self.get_hashes)
        self.thread_pool.start(worker)
        self.progress_widget.exec_()
        self.isDone = True
            
        
    def get_hashes(self, value):
        self.window.fieldMD5.setPlainText(value['MD5'])
        self.window.fieldSHA256.setPlainText(value['SHA256'])
        self.window.fieldSHA512.setPlainText(value['SHA512'])
        pass

    def show_progress(self, pc):
        print(f"{pc}")

        self.progress_widget.progressBar.setValue(pc)

        if pc >= 100:
            self.progress_widget.close()
        

    def run(self):
        self.window.showNormal()
        sys.exit(self.exec_())


def run():
    app = Application()
    app.run()


if __name__ == "__main__":
    app = Application()
    app.run()