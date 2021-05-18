from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from bact.applib.elogwrapper import elogwrapper

class Commit_Control(QMainWindow):
    
    def __init__(self, *args, mode='manual', attachments=[], **kwargs):
        super(Commit_Control, self).__init__(*args, **kwargs)
        self.mode = mode
        self.attachments = attachments
        
        self.main = QtWidgets.QWidget()
        self.main.resize(400, 600)
        self.setCentralWidget(self.main)
        
        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.main.setLayout(self.layout)
        
        btn_font = QtGui.QFont()
        btn_font.setPointSize(12)
        
        label_font = QtGui.QFont()
        label_font.setPointSize(15)
        
        self.scan_name = QtWidgets.QLabel(self)
        self.layout.addWidget(self.scan_name, 0, 0, 1, 3)
        self.scan_name.setFont(label_font)
        self.scan_name.setAlignment(QtCore.Qt.AlignCenter)
        self.scan_name.setObjectName("scanName")
        
        self.name_input = QtWidgets.QLineEdit()
        self.layout.addWidget(self.name_input, 1, 0, 1, 3)
        self.name_input.setObjectName('nameInput')
        
        self.author_name = QtWidgets.QLabel(self)
        self.layout.addWidget(self.author_name, 2, 0, 1, 3)
        self.scan_name.setFont(label_font)
        self.scan_name.setAlignment(QtCore.Qt.AlignCenter)
        self.scan_name.setObjectName("authorName")
        
        self.author_input = QtWidgets.QLineEdit()
        self.layout.addWidget(self.author_input, 3, 0, 1, 3)
        self.author_input.setObjectName('authorInput')
        
        self.descr_name = QtWidgets.QLabel(self)
        self.layout.addWidget(self.descr_name, 4, 0, 1, 3)
        self.scan_name.setFont(label_font)
        self.scan_name.setAlignment(QtCore.Qt.AlignCenter)
        self.scan_name.setObjectName("descriptionName")
        
        self.description = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.description, 5, 0, 1, 3)
        self.description.setObjectName("descriptionBox")
        
        self.attachment_name = QtWidgets.QLabel(self)
        self.layout.addWidget(self.attachment_name, 6, 0, 1, 3)
        self.scan_name.setFont(label_font)
        self.scan_name.setAlignment(QtCore.Qt.AlignCenter)
        self.scan_name.setObjectName("attachmentName")
        
        self.attachment_list = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.attachment_list, 7, 0, 2, 1)
        self.attachment_list.setObjectName('attachmentList')
        self.attachment_list.clicked.connect(self.preview)
        
        
        self.preview = QtGui.QPixmap()        
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setPixmap(self.preview)
        self.preview_label.resize(self.preview.width(), self.preview.height())
        
        self.preview_box = QtWidgets.QScrollArea(self)
        self.preview_box.setFixedHeight(400)
        self.preview_box.setFixedWidth(400)
        self.preview_box.setWidgetResizable(True)
        self.preview_box.setWidget(self.preview_label)
        
        self.layout.addWidget(self.preview_box, 8, 1, 1, 2)
        self.preview_box.setObjectName('attachmentPreview')
        
        self.add_btn = QtWidgets.QPushButton(self)
        self.add_btn.setFixedHeight(50)
        self.layout.addWidget(self.add_btn, 7, 1)
        self.add_btn.setFont(btn_font)
        self.add_btn.setObjectName("addButton")
        self.add_btn.clicked.connect(self.add_attachment)
        
        self.remove_btn = QtWidgets.QPushButton(self)
        self.remove_btn.setFixedHeight(50)
        self.layout.addWidget(self.remove_btn, 7, 2)
        self.remove_btn.setFont(btn_font)
        self.remove_btn.setObjectName("removeButton")
        self.remove_btn.clicked.connect(self.remove_attachment)
        
        self.commit_btn = QtWidgets.QPushButton(self)
        self.commit_btn.setFixedHeight(80)
        self.layout.addWidget(self.commit_btn, 9, 1)
        self.commit_btn.setFont(btn_font)
        self.commit_btn.setObjectName("commitButton")
        self.commit_btn.clicked.connect(self.commit)
        
        self.retranslateUi()
        
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", 'Commit Control'))
        self.scan_name.setText('Scan Name:')
        self.author_name.setText('Author Name:')
        self.descr_name.setText('Description:')
        self.attachment_name.setText('Attachments:')
        self.add_btn.setText('Add')
        self.remove_btn.setText('Remove')
        self.commit_btn.setText('Commit')
        
    def add_attachment(self):
        image_paths, ftypes = QFileDialog.getOpenFileNames(self, "Select Image File to append", "", "Image File (*.png)")
        
        for image in image_paths:
            self.attachment_list.addItem(image)
        
    def remove_attachment(self):
        select = self.attachment_list.currentRow()
        self.attachment_list.takeItem(select)
        self.preview_label.setPixmap(self.preview)
        self.preview_label.resize(self.preview.width(), self.preview.height())
        
    def preview(self):
        preview = QtGui.QPixmap(self.attachment_list.currentItem().text())
        self.preview_label.setPixmap(preview)
        self.preview_label.resize(self.preview.width(), self.preview.height())
        
    def commit_old(self):
        image_paths, ftypes = QFileDialog.getOpenFileNames(self, "Select Image File to append", "", "Image File (*.png)")

        plotfiles = image_paths
        
        name = self.plan_name.text()

        m_date = date.today().strftime("%b-%d-%Y")
        
        data = "Date: {}\n Measurement: {}\n".format(m_date, name)

        elogwrapper.elog_BESSYII_automeas_section_create(name, name, data, plotfiles)
        
    def commit(self):
        author = self.author_input.text()
        name = self.name_input.text()
        description = self.description.toPlainText()
        
        attachments = []
        for x in range(self.attachment_list.count()):
            attachments.append(self.attachment_list.item(x).text())
            
        print('Scan Name: {}\nAuthor: {}\nDescription: {}\nAttachments: {}'.format(name, author, description, attachments))
        
        elogwrapper.elog_BESSYII_automeas_section_create(name, author, description, attachments)
       
        
        
if __name__ == '__main__':
    app = 0
    app = QApplication([])

    window = Commit_Control()
    window.show()
    # Start the event loop.
    app.exec_()