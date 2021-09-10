# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Plan.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import ntpath

import threading
import os
import multiprocessing as mp
import random
import time
import sys
from contextlib import redirect_stdout
import logging
import bluesky as bs
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import configparser
from datetime import datetime

from multiprocess_executer import RunProcess
from commit_control import Commit_Control

_EXPECTED_SECTIONS = ['GENERAL', 'PYTHON', 'LAYOUT']   

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)       
        self.config = self.read_config()
        
        bs.callbacks.mpl_plotting.initialize_qt_teleporter()
        
        width = int(self.config['LAYOUT']['window_width'])
        height = int(self.config['LAYOUT']['window_height'])
        self.resize(width, height)
        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        
        self.plan_name = QtWidgets.QLabel(self)
        self.layout.addWidget(self.plan_name, 0, 1)
        font = QtGui.QFont()
        font_size = int(self.config['LAYOUT']['font_title'])
        font.setPointSize(font_size)
        self.plan_name.setFont(font)
        self.plan_name.setAlignment(QtCore.Qt.AlignCenter)
        self.plan_name.setObjectName("planName")
        
        self.plan_select = QtWidgets.QPushButton(self)
        self.layout.addWidget(self.plan_select, 0, 2)
        font = QtGui.QFont()
        font_size = int(self.config['LAYOUT']['font_button'])
        font.setPointSize(font_size)
        self.plan_select.setFont(font)
        self.plan_select.setObjectName("planSelect")
        self.plan_select.clicked.connect(self.select_plan)
        
        self.figure, self.axes = plt.subplots(2, 1, figsize=[12,8], sharex=True)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.canvas, 1, 0, 1, 3)
        self.layout.addWidget(self.toolbar, 2, 0, 1, 3)
        
        self.output = QtWidgets.QTextEdit(self)
        self.output.setFixedHeight(200)
        self.layout.addWidget(self.output, 3, 0, 1, 3)
        self.output.setObjectName("outputBox")
        
        self.run_btn = QtWidgets.QPushButton(self)
        self.run_btn.setFixedHeight(80)
        self.layout.addWidget(self.run_btn, 4, 0)
        self.run_btn.setFont(font)
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self.run_plan)
        
        self.stop_btn = QtWidgets.QPushButton(self)
        self.stop_btn.setFixedHeight(80)
        self.layout.addWidget(self.stop_btn, 4, 1)
        self.stop_btn.setFont(font)
        self.stop_btn.setObjectName("stopButton")
        
        self.commit_btn = QtWidgets.QPushButton(self)
        self.commit_btn.setFixedHeight(80)
        self.layout.addWidget(self.commit_btn, 4, 2)
        self.commit_btn.setFont(font)
        self.commit_btn.setObjectName("comitButton")
        self.commit_btn.clicked.connect(self.commit)
        
        self.plan_path = ''
        self.threadpool = QThreadPool()
        
        self.commit_control = None

        self.retranslateUi()
        self.select_plan(bluesky_path=self.config['GENERAL']['path'])
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", self.config['GENERAL']['title']))
        self.plan_name.setText(_translate("Form", "Plan Name"))
        self.plan_select.setText(_translate("Form", "Select Plan"))
        self.run_btn.setText(_translate("Form", "Start Plan"))
        self.stop_btn.setText(_translate("Form", "Abort Plan"))
        self.commit_btn.setText(_translate("Form", "Commit"))
        
    def read_config(self):
        config = configparser.ConfigParser()
        config_name = os.path.join(os.getcwd(), 'etc', 'simpleGUI.ini')
        with open(config_name) as file:
            try:
                config.read_file(file)
            except FileNotFoundError as f:
                print(f)
                sys.exit()
        if all(elem in config.sections() for elem in _EXPECTED_SECTIONS):
            return config
        else:
            print('Expected {} as sections but got {} from config file.'.format(_EXPECTED_SECTIONS, config.sections()))
            sys.exit()
        
    def select_plan(self, bluesky_path=''):
        if not bluesky_path or bluesky_path == '':
            bluesky_path, ftype = QFileDialog.getOpenFileName(self, 'Select Device File', '',"Bluesky Plan (*.py)")
            if not ftype:
                return
        try:
            self.plan_path = bluesky_path
        except NameError as n:
            print(n)
            sys.exit()
        
        try:
            self.worker.set_plan(self.plan_path, self.plan_name.text())
        except AttributeError as e:
            pass
        
    def run_plan(self):
        if self.plan_path == '':
            self.append_text('No Plan selected')
        else:
            self.worker = RunProcess(path=self.plan_path,plan_name=self.plan_name.text(), axes=self.axes)
            self.worker.signals.signal.connect(self.update)
            self.worker.signals.signal.connect(self.append_text)
            self.stop_btn.clicked.connect(self.worker.close_worker)
            self.stop_btn.clicked.connect(self.stop_worker)
            self.threadpool.start(self.worker)
            
    def stop_worker(self):
        self.threadpool.cancel(self.worker)
        
    def append_text(self,text):
        self.output.moveCursor(QTextCursor.End)
        try:
            self.output.insertPlainText( text + '\n' )
        except TypeError:
            print(text)
    
    def update(self, value):
        pass
        
    def commit(self):
        self.attachments = []
        
        if self.commit_control is None:
            self.commit_control = Commit_Control(self, mode='auto')
            scan = self.plan_name.text()
            author = self.config['GENERAL']['author']
            
            now = datetime.now()
            
            scan_date = now.strftime("%B %d, %Y, %H:%M:%S")
            
            description = scan_date + '\n' + scan
            
            self.commit_control.quick_fill(scan_name=scan, author_name=author, description=description)
            
        self.commit_control.show()
        self.commit_control.activateWindow()
        
        
     
    def closeEvent(self, event):
        # do stuff
        try:
            self.worker.close_worker()
        except AttributeError:
            pass
        event.accept()
        
    
if __name__ == '__main__':
    app = 0
    app = QApplication([])

    window = MainWindow()
    window.show()
    # Start the event loop.
    app.exec_()
