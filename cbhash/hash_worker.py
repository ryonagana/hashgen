from asyncio import subprocess
from asyncio.subprocess import STDOUT
from asyncio.windows_utils import pipe
import sys
import os
import platform
from subprocess import Popen
from PySide2.QtCore import QThread, Signal, Slot
from PySide2.QtCore import QObject, QRunnable

class WorkerSignals(QObject):
    progress = Signal(int) 
    hashlists  = Signal(dict)




class HashWorker(QRunnable):


    signals = WorkerSignals()

    def whichOS(self):
        if platform.system() == "Windows":
            return "win32"
        if platform.system() == "Darwin":
            return "macos"
        if platform.system() == "Linux":
            return "linux"
        


    def __init__(self, *args, **kwargs):
        super(HashWorker,self).__init__(self)
        
        if "filename" in kwargs:
            self.filepath = kwargs['filename']

    def fix_str_communicate(self, result):
        r =  result.decode('utf-8','backslashreplace')
        r = r.split('\r')[1].replace('\n','').replace(' ','')
        return r

    def run_hashes_windows(self):
  
        hash_list = ["MD5", "SHA256", "SHA512"]



        result = {}

        percent = 0.0

        for c,h in  enumerate(hash_list,start=1):
            
            percent = (c  / len(hash_list)) * 100

            proc = Popen(['certUtil','-hashfile', self.filepath, h], stdout=subprocess.PIPE)
                
            result[h] = proc.communicate()[0]
            result[h] = self.fix_str_communicate(result[h])
            self.signals.progress.emit(percent)
                  
        self.signals.hashlists.emit(result)

    @Slot()
    def run(self):


        if self.whichOS() == "win32":
            self.run_hashes_windows()
        pass