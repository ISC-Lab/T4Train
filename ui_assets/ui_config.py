#temporary, delete later
import sys

#System
import pyaudio
import configparser

#Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor, QPalette, QFont, QValidator, QColor

#================================================================
# read in configuration
config=configparser.ConfigParser()
config.read('config.ini')

LABELS         =      config['GLOBAL']['LABELS'         ][1:-1].split(', ')
INSTANCES      =  int(config['GLOBAL']['INSTANCES'      ])
CHANNELS       =  int(config['GLOBAL']['CHANNELS'       ])
ALGOS          =      config['GLOBAL']['ALGOS'          ][1:-1].split(', ')
CURR_ALGO_INDEX=  int(config['GLOBAL']['CURR_ALGO_INDEX'])
ALGO_SUGGESTION=  int(config['GLOBAL']['ALGO_SUGGESTION'])
FRAME_LENGTH   =  int(config['GLOBAL']['FRAME_LENGTH'   ])
OPEN_SPLASH    =  int(config['GLOBAL']['OPEN_SPLASH'   ])

DS_HANDLERS    =      config['DS'    ]['DS_HANDLERS'    ][1:-1].split(', ')
DS_FILENAMES   =      config['DS'    ]['DS_FILENAMES'   ][1:-1].split(', ')
DS_FILE_NUM    =  int(config['DS'    ]['DS_FILE_NUM'    ])

T_RECORD    =  int(config['DS_arduino'    ]['T_RECORD'    ])
T_OVERLAP    = float(config['DS_arduino'    ]['T_OVERLAP'    ])

SAMPLE_RATE = int(config['DS']['SAMPLE_RATE'])
NUM_BINS = int(config['ML']['NUM_BINS'])

# Get data collection .py filename
ds_filename = DS_FILENAMES[DS_FILE_NUM]
ds_handler = DS_HANDLERS[DS_FILE_NUM]
#================================================================

class QDialogSplash(QDialog):
    def __init__(self, *args, **kwargs):
        super(QDialogSplash, self).__init__(*args, **kwargs)
        self.remember_splash = OPEN_SPLASH
        self.setWindowTitle("Edit Config")
        self.setFixedHeight(650)
        self.setFixedWidth(1000)
        #self.showMaximized()

        scroll_layout = QGridLayout()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_layout)
        scroll_box = QScrollArea()
        scroll_box.setWidgetResizable(True)
        scroll_box.setWidget(scroll_widget)

        self.labels_list = QListWidget()
        self.labels_list.setStyleSheet("QListWidget {background: white; font-family: Verdana; font-style: normal; font-size: 11pt}")
        self.labels_desc = QLabel("Labels:\nAdd and remove labels for input data to be categorized.")
        self.labels_desc.setWordWrap(True)
        self.current_labels = []
        for label in LABELS:
            self.labels_list.addItem(label)
            self.current_labels.append(label)

        self.onlyInt = QtGui.QIntValidator()
        self.onlyDouble = QtGui.QDoubleValidator()

        scroll_layout.addWidget(self.labels_desc, 0, 0, 1, 2)
        scroll_layout.addWidget(self.labels_list, 1, 0, 1, 2)
        self.labels_box = self.instances_box = QLineEdit()
        self.labels_box.setStyleSheet("color: white;  background-color: black")

        self.labels_add = QPushButton("Add", default=False, autoDefault=False)
        self.labels_remove = QPushButton("Remove", default=False, autoDefault=False)
        self.labels_remove.clicked.connect(lambda: self.remove_label())
        self.labels_add.clicked.connect(lambda: self.add_label())
        scroll_layout.addWidget(self.labels_box, 2, 1, 1, 1)
        scroll_layout.addWidget(self.labels_add, 2, 0, 1, 1)
        scroll_layout.addWidget(self.labels_remove, 3, 0, 1, 2)
        scroll_layout.addWidget(QHLine(), 4, 0, 1, 2)

        self.instances_desc = QLabel("Instances:\nSpecify the amount of instances to be collected at once.")
        self.instances_desc.setWordWrap(True)
        self.instances_box = QLineEdit(placeholderText=str(INSTANCES))
        self.instances_box.setValidator(self.onlyInt)
        self.instances_box.setStyleSheet("color: white;  background-color: black")
        self.instances_label = QLabel("Instances:")
        scroll_layout.addWidget(self.instances_desc, 5, 0, 1, 2)
        scroll_layout.addWidget(self.instances_label, 6, 0)
        scroll_layout.addWidget(self.instances_box, 6, 1)
        scroll_layout.addWidget(QHLine(), 7, 0, 1, 2)

        self.channels_box = QLineEdit(placeholderText=str(CHANNELS))
        self.channels_box.setValidator(self.onlyInt)
        self.channels_box.setStyleSheet("color: white;  background-color: black")
        self.channels_label = QLabel("Channels:")
        self.channels_desc = QLabel("Channels:\nSelect amount of waves to be plotted. Mic only supports 2.")
        scroll_layout.addWidget(self.channels_box, 9, 1)
        scroll_layout.addWidget(self.channels_desc, 8, 0, 1, 2)
        scroll_layout.addWidget(self.channels_label, 9, 0)
        scroll_layout.addWidget(QHLine(), 10, 0, 1, 2)

        self.frame_box = QLineEdit(placeholderText=str(FRAME_LENGTH))
        self.frame_box.setValidator(self.onlyInt)
        self.frame_box.setStyleSheet("color: white;  background-color: black")
        self.frame_label = QLabel("Frame Length:")
        self.frame_desc = QLabel("Frame Length:\nNumber of frames collected per instances.")
        scroll_layout.addWidget(self.frame_desc, 11, 0, 1, 2)
        scroll_layout.addWidget(self.frame_box, 12, 1)
        scroll_layout.addWidget(self.frame_label, 12, 0)
        scroll_layout.addWidget(QHLine(), 13, 0, 1, 2)

        self.combo_box_font = QFont("Verdana", 11)

        self.ds = QComboBox()
        self.ds_mic = QComboBox()
        mic_to_add = list(self.audio_query())
        mic_to_add.sort()
        mic_to_add = [str(x) for x in mic_to_add]
        mic_to_add.append("User Specified")
        self.ds_mic.addItems(mic_to_add)
        self.ds_mic_label = QLabel("Mic Sample Rate:")
        self.ds_mic.setStyleSheet("QListWidget {background: white; font-family: Verdana; font-style: normal; font-size: 11pt}")

        if str(SAMPLE_RATE) in mic_to_add:
            self.ds_mic.setCurrentText(str(SAMPLE_RATE))

        self.ds_mic.setFont(self.combo_box_font)
        scroll_layout.addWidget(self.ds_mic_label, 17, 0)
        scroll_layout.addWidget(self.ds_mic, 17, 1)
        self.ds_mic.currentTextChanged.connect(self.handle_mic_combo)
        self.ds.currentTextChanged.connect(self.handle_mic_combo)

        self.record_box = QLineEdit(placeholderText=str(T_RECORD))
        self.record_box.setValidator(self.onlyDouble)
        self.record_box.setStyleSheet("color: white;  background-color: black")
        self.record_label = QLabel("Record Time:")
        self.overlap_box = QLineEdit(placeholderText=str(T_OVERLAP))
        self.overlap_box.setValidator(self.onlyDouble)
        self.overlap_box.setStyleSheet("color: white;  background-color: black")
        self.overlap_label = QLabel("Overlap Time:")
        scroll_layout.addWidget(self.record_label, 18, 0)
        scroll_layout.addWidget(self.record_box, 18, 1)
        scroll_layout.addWidget(self.overlap_label, 19, 0)
        scroll_layout.addWidget(self.overlap_box, 19, 1)

        self.ds_mic.hide()
        self.ds_mic_label.hide()
        self.record_label.hide()
        self.record_box.hide()
        self.overlap_label.hide()
        self.overlap_box.hide()
        self.ds.currentTextChanged.connect(self.handle_ds_combo)


        self.ds_desc = QLabel("DS Handler:")
        self.sr_label = QLabel("Sample Rate:")
        self.ds_label = QLabel("DS Handler:\nSelect the data handler and its sample rate.")
        self.sr_box = QLineEdit(placeholderText=str(SAMPLE_RATE))
        self.sr_box.setValidator(self.onlyInt)
        self.sr_box.setStyleSheet("color: white;  background-color: black")
        self.ds.addItems(DS_HANDLERS)
        self.ds.setStyleSheet("QListWidget {background: white; font-family: Verdana; font-style: normal; font-size: 11pt}")
        self.ds.setFont(self.combo_box_font)
        self.ds.setCurrentText(DS_HANDLERS[DS_FILE_NUM])
        self.handle_ds_combo()
        self.handle_mic_combo()
        scroll_layout.addWidget(self.ds_label,14,0, 1, 2)
        scroll_layout.addWidget(self.ds_desc,15,0)
        scroll_layout.addWidget(self.ds,15,1)
        scroll_layout.addWidget(self.sr_label,16,0)
        scroll_layout.addWidget(self.sr_box,16,1)
        scroll_layout.addWidget(QHLine(), 20, 0, 1, 2)

        self.algo = QComboBox()
        self.algo_desc = QLabel("ML ALgorithm:\nSelect the ML algorithm. This can be changed later.")
        self.algo_label = QLabel("ML Algorithm:")
        self.algo.addItems(ALGOS)
        self.algo.setStyleSheet("QListWidget {background: white; font-family: Verdana; font-style: normal; font-size: 11pt}")
        self.algo.setFont(self.combo_box_font)
        self.algo.setCurrentText(ALGOS[CURR_ALGO_INDEX])
        self.bins_box = QLineEdit(placeholderText=str(NUM_BINS))
        self.bins_box.setValidator(self.onlyInt)
        self.bins_box.setStyleSheet("color: white;  background-color: black")
        self.bins_label = QLabel("Number Bins:")
        scroll_layout.addWidget(self.algo_desc,21,0,1 ,2)
        scroll_layout.addWidget(self.algo_label,22,0)
        scroll_layout.addWidget(self.algo,22,1)
        scroll_layout.addWidget(self.bins_box,23,1)
        scroll_layout.addWidget(self.bins_label,23,0)

        self.finish_button = QPushButton("Continue", default=False, autoDefault=False)
        self.finish_button.clicked.connect(lambda: self.splash_closed())
        #self.finish_button.setStyleSheet('QPushButton {color: white; background-color: #1C1C1E; border: 1px solid; border-color: white}')
        self.checkbox = QCheckBox("Never open config window again")
        self.checkbox.setChecked(False)
        #self.checkbox.setStyleSheet("QCheckBox { color: #FFFFFF }");
        self.checkbox.stateChanged.connect(lambda:self.change_splash())

        self.layout = QGridLayout()
        self.layout.addWidget(self.checkbox, 1, 0, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.finish_button, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(scroll_box, 0, 0, 1, 2)
        self.setLayout(self.layout)
        self.set_theme()


    def handle_ds_combo(self):
        if self.ds.currentText() == "Microphone":
            self.ds_mic.show()
            self.ds_mic_label.show()
            self.record_label.hide()
            self.record_box.hide()
            self.overlap_label.hide()
            self.overlap_box.hide()
        elif self.ds.currentText() == "Arduino":
            self.ds_mic.hide()
            self.ds_mic_label.hide()
            self.record_label.show()
            self.record_box.show()
            self.overlap_label.show()
            self.overlap_box.show()
        else:
            self.record_label.hide()
            self.record_box.hide()
            self.overlap_label.hide()
            self.overlap_box.hide()
            self.ds_mic.hide()
            self.ds_mic_label.hide()

    def handle_mic_combo(self):
        if (self.ds_mic.currentText() != "User Specified") and (self.ds.currentText() == "Microphone"):
            self.sr_label.hide()
            self.sr_box.hide()
        else:
            self.sr_label.show()
            self.sr_box.show()


    def audio_query(self):
        audio_rates = set()
        p = pyaudio.PyAudio()
        #if "defaultSampleRate" in p.get_device_info_by_index(1):
        #    sr = p.get_device_info_by_index(1)["defaultSampleRate"]
        #    self.sr_box.setText(str(int(sr)))
        #else:
        #    print("audio input not found")
        for i in range(p.get_device_count()):
            if "defaultSampleRate" in p.get_device_info_by_index(i):
                sr = p.get_device_info_by_index(i)["defaultSampleRate"]
                audio_rates.add(int(sr))
        return audio_rates



    def splash_closed(self):
        print("Closing the dialog box")

        config.set("GLOBAL", "OPEN_SPLASH", str(int(self.remember_splash)))
        labels_list_config = []
        for x in range (self.labels_list.count()):
            labels_list_config.append(self.labels_list.item(x).text())
        if len(labels_list_config) > 0:
            config.set("GLOBAL", "LABELS", str(labels_list_config).replace("\'",""))

        if self.instances_box.text():
            config.set("GLOBAL", "INSTANCES", str(self.instances_box.text()))

        if self.channels_box.text():
            config.set("GLOBAL", "CHANNELS", str(self.channels_box.text()))

        if self.frame_box.text():
            config.set("GLOBAL", "FRAME_LENGTH", str(self.frame_box.text()))

        config.set("GLOBAL", "CURR_ALGO_INDEX", str(ALGOS.index(self.algo.currentText())))

        config.set("DS", "DS_FILE_NUM", str(DS_HANDLERS.index(self.ds.currentText())))

        if self.sr_box.text():
            config.set("DS", "SAMPLE_RATE", str(self.sr_box.text()))

        if self.ds.currentText() == "Arduino":
            if self.record_box.text():
                config.set("DS_arduino", "T_RECORD", str(self.record_box.text()))
            if self.overlap_box.text():
                config.set("DS_arduino", "T_OVERLAP", str(self.overlap_box.text()))

        if self.ds.currentText() == "Microphone":
            if self.ds_mic.currentText() == "User Specified":
                if self.sr_box.text():
                    config.set("DS", "SAMPLE_RATE", str(self.sr_box.text()))
            else:
                config.set("DS", "SAMPLE_RATE", str(self.ds_mic.currentText()))
        else:
            if self.sr_box.text():
                config.set("DS", "SAMPLE_RATE", str(self.sr_box.text()))

        if self.bins_box.text():
            config.set("ML", "NUM_BINS", str(self.bins_box.text()))


        with open("config.ini", "w") as cf:
            config.write(cf)
            cf.close()
        #sys.exit(0)
        self.close()


    def change_splash(self):
        self.remember_splash = not self.remember_splash
        print(self.remember_splash)

    def add_label(self):
        add_text = self.labels_box.text().strip()

        if (len(add_text) == 0) or (add_text in self.current_labels):
            return
        self.labels_list.addItem(add_text)
        self.current_labels.append(add_text)

    def remove_label(self):
        to_remove = self.labels_list.selectedItems()
        if not to_remove:
            return
        for tr in to_remove:
            self.labels_list.takeItem(self.labels_list.row(tr))

    def set_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(10, 10, 10))
        palette.setColor(QPalette.Base, Qt.black)
        palette.setColor(QPalette.Background, QColor(28, 28, 30))
        palette.setColor(QPalette.WindowText, QColor(254, 254, 254))
        self.setPalette(palette)
        palette.setColor(QPalette.Base, QColor(28, 28, 30))
        board_stylesheet = 'background-color: rgb(44, 44, 46); border-radius: 8px'

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)




#Some way to pull the splash screen back up from the main window
#Some way to undo the “don’t ask me again toggle”
#ML Algo Recommender (as a pop up)
#   Low # Classes, Low Instances → SVM Linear Kernel
#   Low # Classes, High Instances → SVM RBF Kernel
#   High # Classes, Low Amount of Instances → RF
#   High # Classes, High Data → MLP
