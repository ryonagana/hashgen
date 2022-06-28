import sys
import os
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QThreadPool
import cbhash.hash_worker

class Application(QApplication):

    filepath = ""

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(sys.argv)

        self.loader = QUiLoader()

        self.window = self.loader.load("res//main.ui")
        self.progress_widget = self.loader.load("res//progress.ui")
        
        self.isDone = False
        self.thread_pool  = QThreadPool()

        self.connect()

    def connect(self):
        self.window.acLoadFile.triggered.connect(self.actionLoadFile)
        self.window.btnLoadFile.setDefaultAction(self.window.acLoadFile)

    def actionLoadFile(self):
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