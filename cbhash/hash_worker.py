from asyncio import subprocess
from asyncio.subprocess import STDOUT
from asyncio.windows_utils import pipe
import sys
import os
import platform
from subprocess import Popen
from PySide2.QtCore import QThread, Signal, Slot
from PySide2.QtCore import QObject, QRunnable
from PySide2.QtWidgets import QMessageBox

from enum import Enum


class HashType(Enum):
    MD5 = 0,
    SHA256 = 1,
    SHA512 = 2,
    
    HASH_TOTAL = 3

class WorkerSignals(QObject):
    progress = Signal(int)
    increase_progress = Signal(int)
    hash_str = Signal(str, HashType)




class HashWorker(QRunnable):

    signals = WorkerSignals()
    hash_type:HashType = HashType.MD5
    

    def whichOS(self):
        if platform.system() == "Windows":
            return "win32"
        if platform.system() == "Darwin":
            return "macos"
        if platform.system() == "Linux":
            return "linux"
        
    def __init__(self, hash_type:HashType = HashType.MD5, *args, **kwargs):
        super(HashWorker, self).__init__(self)
        
        self.hash_type = hash_type
        
        if "filename" in kwargs:
            self.filepath = kwargs['filename']

    def fix_str_communicate(self, result):
        r = result.decode('utf-8','backslashreplace')
        r = r.split('\r')[1].replace('\n','').replace(' ','')
        return r
    
    
    def run_process_window(self, hash_type:HashType =  None):
        hash_str = "MD5"
        
        if hash_type == HashType.MD5 or not type:
            hash_str = "MD5"
        
        if hash_type == HashType.SHA256:
            hash_str = "SHA256"
            
        if hash_type == HashType.SHA512:
            hash_str = "SHA512"

        command_line = ['certUtil', '-hashfile', self.filepath, hash_str]
        process = Popen(command_line, stdout=subprocess.PIPE)
        res = process.communicate()[0]
        
        return res
    
    @Slot()
    def run(self):


        if self.whichOS() == "win32":
            result = self.run_process_window(self.hash_type)
            self.signals.hash_str.emit(self.fix_str_communicate(result), self.hash_type)
            self.signals.increase_progress.emit(1);
            
        else:
            QMessageBox.critical(self, "Error:", "Unknown OS\nSorry!")
        return