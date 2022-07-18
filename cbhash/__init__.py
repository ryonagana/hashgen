import sys
import os
import logging
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QFileDialog, QMessageBox
from PySide2.QtCore import QThreadPool, QTimer, QFile, QTextStream
import cbhash.hash_worker

from cbhash.hash_worker import HashWorker, HashType

import cbhash.resources


class Application(QApplication):
    
    
    WORKER_COUNT: int = 3
    
    filepath = ""
    styles = {'dark':
                [':/dark/window.qss',]
              }
    
    style_default = "dark"
    
    complete: int = 0

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(sys.argv)

        self.loader = QUiLoader()

        self.window = self.loader.load(":/main.ui")
        self.progress_widget = self.loader.load(":/progress.ui")
        
        self.isDone = False
        self.thread_pool  = QThreadPool()

        self.init()
        self.connect()

        style = self.loadStylesheet(self.style_default)
        self.setStyleSheet(style)

    def init(self):
        self.window.labelStatus.setText("")
        self.window.txtFile.setText("No File Loaded!")
    
    def actionMenuSaveAs(self):
        name = ""
        save = QFileDialog()
        save.setAcceptMode(QFileDialog.AcceptSave)
        #save.setFileMode(QFileDialog.)
        save.setViewMode(QFileDialog.Detail)
        
        if save.exec_():
            name = save.selectedFiles()

        data = self.window.fieldMD5.toPlainText()
        print(data)
        print(name)

        
        


    def loadStylesheet(self, type):
        
        stylesheet = ""
        
        try:
            for s in self.styles[type]:
                f = QFile(s)
                
                if not f.exists():
                    return
                
                f.open(QFile.ReadOnly | QFile.Text)
                stream = QTextStream(f)
                stylesheet += stream.readAll()
                f.close()
                return stylesheet
        except IndexError:
            logging.critical(f"Stylesheet Load Error, {type} Not Found!")
            return None
        except Exception as e:
            logging.critical(f"Exception Trying load Style {type} - {e}")
            return None
        
            
    
    def connect(self):
        self.window.acLoadFile.triggered.connect(self.actionLoadFile)
        self.window.btnLoadFile.setDefaultAction(self.window.acLoadFile)
        self.window.acClipMD5.triggered.connect(self.copyToClipboardMD5)
        self.window.btnCopyMD5.setDefaultAction(self.window.acClipMD5)

        self.window.acClipSHA256.triggered.connect(self.copyToClipboardSHA256)
        self.window.btnCopySHA256.setDefaultAction(self.window.acClipSHA256)

        self.window.acClipSHA512.triggered.connect(self.copyToClipboardSHA512)
        self.window.btnCopySHA512.setDefaultAction(self.window.acClipSHA512)

        self.window.acQuit.triggered.connect(self.quitApp)

        self.window.acAboutQt.triggered.connect(self.MenuAboutQt)
        self.window.acSaveAs.triggered.connect(self.actionMenuSaveAs)
    
    def MenuAboutQt(self):
        self.aboutQt()
        return

    def quitApp(self):
        self.quit()

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
        fnames:str = None
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_() :
            fnames = dialog.selectedFiles()

        if not fnames:
            return

        self.filepath = fnames[0]
        self.window.txtFile.setText(os.path.basename(fnames[0]))

        
        workers = [HashWorker(filename=self.filepath, hash_type=HashType.MD5),
                   HashWorker(filename=self.filepath, hash_type=HashType.SHA256),
                   HashWorker(filename=self.filepath, hash_type=HashType.SHA512)]
        
        for i, w in enumerate(workers):
            
            #w.signals.progress.emit((i / len(workers)) * 100)
            w.signals.progress.connect(self.show_progress)
            w.signals.hash_str.connect(self.get_hashes)
            w.signals.increase_progress.connect(self.update_progress)
            self.thread_pool.start(w)

        
        
        
        
        self.isDone = True
        
        self.progress_widget.exec_()
        
        if self.isDone:
            self.window.btnLoadFile.setText("Regenerate Hashes")
       
        
        
       
        """
        worker.signals.progress.connect(self.show_progress)
        worker.signals.hashlists.connect(self.get_hashes)
        self.thread_pool.start(worker)
        self.progress_widget.exec_()
        self.isDone = True
        """
    def update_progress(self, progress:int):
        self.complete += progress
        
        pc = (self.complete / self.WORKER_COUNT) * 100
        self.progress_widget.progressBar.setValue(pc)
        if pc >= 100:
            self.progress_widget.close()
        

    def get_hashes(self, value, hash_type):
        
        if hash_type == HashType.MD5:
            self.window.fieldMD5.setPlainText(value)
        
        if hash_type == HashType.SHA256:
            self.window.fieldSHA256.setPlainText(value)

        if hash_type == HashType.SHA512:
            self.window.fieldSHA512.setPlainText(value)
            
        
        return

    def show_progress(self, pc):
        print(f"AUI AUI {pc}")

        self.progress_widget.progressBar.setValue(pc)

        if pc >= 100:
            self.progress_widget.close()
        

    def run(self):
        self.window.showNormal()
        sys.exit(self.exec_())


def run():
    app = Application()
    app.run()
