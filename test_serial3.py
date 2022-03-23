__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

from inspect import Attribute
import sys, serial, serial.tools.list_ports, warnings, glob, os
from tabnanny import check
from PyQt5.QtCore import  Qt,QSize, QRect, QObject, pyqtSignal, QThread, pyqtSignal, pyqtSlot
import time
from PyQt5.QtWidgets import QMenu,QFileDialog, QInputDialog, QToolBar,QCheckBox, QApplication, QFileDialog, QAction, QColorDialog, QComboBox, QDialog, QMainWindow, QWidget, QLabel, QTextEdit, QListWidget, \
    QListView,QTableWidgetItem, QLineEdit, QLayout, QPushButton, QTabWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QSlider, QSizePolicy
from PyQt5.uic import loadUi
import pickle
import math
from PyQt5.QtGui import QColor, QIcon,QPixmap, QFont, QPalette, QPageLayout, QTextLayout
from PyQt5.Qt import Qt
from pynput import keyboard
import calendar
from time import sleep




liste_modifier = ["Alt", "Ctrl", "Shift", "Win"]
liste_titles = ["Touches", "Mode", "Media", "Mods", "Envoi", "Ecran"]
liste_media = ["Up", "Down", "Mute", "Pause", "Play"]
liste_led_modes = ["Static", "On/Off", "On-Click", "Snake", "Diagonal"]
liste_modes = ["Modif.", "Media.", "Suite"]
        

class button():

    def __init__(self):
 
        self.sending = ''
        self.screen = ''
        self.mode = 0
        self.media = 0
        self.modifiers = [False, False,False,False]
       

class sheet():

    def __init__(self):

        self.r = 255
        self.g = 255
        self.b = 255
        self.led_mode = 0
        self.intensite = 0
        self.name = ''   
        self.buttons = [button(),button(),button(),
                        button(),button(),button(),button(),button(),button(),button(),button()]

class config():

    def __init__(self):

        self.sheets = []

class WorkerComm(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        """Long-running task."""
        for i in range(5):
            sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()

class WorkerDetect(QObject):
    finished = pyqtSignal()
    numberConnection = pyqtSignal(list)
    

    def run(self):

        nbPorts = 0
        while(True):
            ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'USB' or 'ACM' in p.description
            ]

            portsN = [
                p.description
                for p in serial.tools.list_ports.comports()
                if 'USB' or 'ACM' in p.description
                ]
            
            if len(ports) is not nbPorts:
                nbPorts = len(ports)
                self.numberConnection.emit(ports)

            sleep(2)
        #self.finished.emit()




class qt(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        self.setWindowTitle("Macro Clavier 1.0")
        self.config = config()
        self.path = None
        
        self.thread = None
        self.workerComm = None
        self.workerDetect = None
        self.ser = None
        self.ports = []
        self.connectedBoard = None

        self.createActions()
        self.createMenuFile()
        self.createToolBar()
        self.createMainPage()
        self.detectBoard()


    def detectBoard(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.workerDetect = WorkerDetect()
        # Step 4: Move worker to the thread
        self.workerDetect.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.workerDetect.run)
        self.workerDetect.finished.connect(self.thread.quit)
        self.workerDetect.finished.connect(self.workerDetect.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.workerDetect.numberConnection.connect(self.updateConnection)
        # Step 6: Start the thread
        self.thread.start()

    def updateConnection(self,n):

        tempPorts = []
        self.ports = n

        if len(self.ports) is not 0:
           self.sendConfigAction.setEnabled(True)

        else:
            self.sendConfigAction.setEnabled(False)


        text = self.portsChoice.currentText()
        self.portsChoice.clear()

        if text in self.ports:

            self.portsChoice.addItem(text)
            n.remove(text)
            tempPorts.append(text)

        for p in n:
            self.portsChoice.addItem(p)
            tempPorts.append(p)

        self.ports = tempPorts     
        self.connectBoard(0)

    def connectBoard(self,index):

        if (len(self.ports) > 0):
            if self.connectedBoard is not self.ports[index]:
                self.ser = serial.Serial(self.ports[index],9600)
                print("connected: ", self.ports[index])
                self.connectedBoard = self.ports[index]

            else: 
                print("port already connected")
        
        else:
            self.ser = None
            print("no port connected")


        
    def sendConfig(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.workerComm = WorkerComm()
        # Step 4: Move worker to the thread
        self.workerComm.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.workerComm.run)
        self.workerComm.finished.connect(self.thread.quit)
        self.workerComm.finished.connect(self.workerComm.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        #self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.sendConfigAction.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.sendConfigAction.setEnabled(True)
        )
        #self.thread.finished.connect(
            #lambda: self.stepLabel.setText("Long-Running Step: 0")
       # )
   
    def createMainPage(self):
        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.acceuil = QVBoxLayout(self.main_widget)
        
        textAcceuil = QLabel()
        pixmap = QPixmap("accueuil.png")
        smaller_pixmap = pixmap.scaled(1000,300, Qt.KeepAspectRatio, Qt.FastTransformation)
        textAcceuil.setPixmap(smaller_pixmap)             
        self.acceuil.addWidget(textAcceuil, alignment=Qt.AlignCenter)


    def newFile(self):

        self.main_widget.deleteLater()   
        self.createTabs()
        self.config = config()
        self.addTab(False)
        self.update_title()


    def createTabs(self):

        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # on cree le main window
        self.l = QHBoxLayout(self.main_widget)

        # on cree le widget des tabs
        self.tabsWidget = QTabWidget()

        # initialisation des layouts de chaque tab    
        self.initLayouts()
        self.l.addWidget(self.tabsWidget)

        # on connect le tabs widget pour le changement de nom
        self.tabsWidget.tabBarDoubleClicked.connect(self.askTab)

    

    def createMenuFile(self):

        menuBar = self.menuBar()

        # creation menu
        fileMenu = QMenu("&File", self)
        editMenu = QMenu("&Edit",self)
        connectMenu = QMenu("&Connect", self)
        helpMenu = QMenu("&Help",self)
        
        # ajout des menus
        menuBar.addMenu(fileMenu)    
        menuBar.addMenu(editMenu)
        menuBar.addMenu(connectMenu)
        menuBar.addMenu(helpMenu)

        # ajout des actions a chaque menu  
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.exitAction)

        editMenu.addAction(self.addTabAction)
        editMenu.addAction(self.deleteTabAction)

        connectMenu.addAction(self.sendConfigAction)
        


    def createToolBar(self):

        toolBar = QToolBar("Main toolbar")
        self.addToolBar(toolBar)
        toolBar.addAction(self.newAction)
        toolBar.addAction(self.openAction)
        toolBar.addAction(self.saveAction)
        #toolBar.addAction(self.saveAsAction)
        toolBar.addSeparator()
        toolBar.addAction(self.addTabAction)
        toolBar.addAction(self.deleteTabAction)
        toolBar.addSeparator()

        # ajoute le comboBox du ports
        self.portsChoice = QComboBox()


        self.portsChoice.currentIndexChanged.connect(self.connectBoard)
        toolBar.addWidget(self.portsChoice)

        toolBar.addAction(self.sendConfigAction)


    def createActions(self):

        # creations des actions pour menuFile
        self.newAction = QAction("&New", self)
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.saveAsAction = QAction("&Save as", self)
        self.exitAction = QAction("&Exit", self)

        # creation des actions pour menuEdit
        self.addTabAction = QAction("&Add Tab")
        self.deleteTabAction = QAction("&Delete Tab")

        # creation des options pour le menu connection
        self.sendConfigAction = QAction("&Send") 
        self.sendConfigAction.setEnabled(False)

        # ajout des icons
        self.newAction.setIcon(QIcon("./toolBarIcons/newAction.jpeg"))
        self.sendConfigAction.setIcon(QIcon("./toolBarIcons/sendAction.png"))
        self.saveAction.setIcon(QIcon("./toolBarIcons/saveAction.png"))
        self.openAction.setIcon(QIcon("./toolBarIcons/openAction.png"))
        self.addTabAction.setIcon(QIcon("./toolBarIcons/addTab.jpg"))
        self.deleteTabAction.setIcon(QIcon("./toolBarIcons/deleteTab1.png"))

        # connection des actions
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.saveAsAction.triggered.connect(self.saveAsFile)
        self.addTabAction.triggered.connect(lambda: self.addTab(False))
        self.deleteTabAction.triggered.connect(self.deleteTab)
        self.sendConfigAction.triggered.connect(self.sendConfig)


    def deleteTab(self):

        try:
            currentTab = self.tabsWidget.currentIndex()
            if len(self.tabs) is not 0:

                # on enleve la sheet de la config
                self.config.sheets.pop(currentTab)
                # on refait la config complete... pas tres efficace et nom de fonction a changer
                self.setNewConfig()
        except AttributeError as e:
            print(str(e))


    def saveFile(self):

        # if there is no save path
        if self.path is None:
 
            # call save as method
            return self.saveAsFile()
 
        # else call save to path method
        self._save_to_path(self.path)

    def saveAsFile(self):
        # opening path
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                             "Text documents (*.txt);All files (*.*)")
 
        # if dialog is cancelled i.e no path is selected
        if not path:
            # return this method
            # i.e no action performed
            return
 
        # else call save to path method
        self._save_to_path(path)

     # save to path method
    def _save_to_path(self, path):

        # try catch block
        try:
 
            # opening file to write
            with open(path, 'wb') as f:
 
                # write text in the file
                pickle.dump(self.config, f)
        except Exception as e:
 
            print(str(e))
            # show error using critical
            #self.dialog_critical(str(e))
 
        # else do this
        else:
            # change path
            self.path = path
            # update the title
            #self.update_title()


    def printTest(self):
        print("test")
        

    def initLayouts(self):

        self.tabs = []

        # on initialise les differents layouts
        self.centralLayout = []
        self.optionLayout = []
        self.btnLayout = []
        self.modeLayout = []
        self.modsLayout = []
        self.mediaLayout = []
        self.envoiLayout = []
        self.ecranLayout = []

        # on initialise les differents menus qui ont plusieurs boutons
        self.labelBtn = []
        self.boxMode = []
        self.boxMedia = []
        self.btnMods = []
        self.lineEnvoi = []
        self.lineEcran = []
        self.menuModifier = []
        self.menuActions = []

        # on initialise les menus qui ont un bouton par tab
        self.btnColor = []
        self.boxColorMode = []
        self.sliderIntensite = []
        self.checkEnable = []

        # on les clear tous
        self.tabs.clear()
        self.centralLayout.clear()
        self.optionLayout.clear()
        self.btnLayout.clear()
        self.modeLayout.clear()
        self.modsLayout.clear()
        self.mediaLayout.clear()
        self.envoiLayout.clear()
        self.ecranLayout.clear()
        self.labelBtn.clear()
        self.boxMode.clear()
        self.boxMedia.clear()
        self.btnMods.clear()
        self.lineEnvoi.clear()
        self.lineEcran.clear()
        self.menuModifier.clear()
        self.btnColor.clear()
        self.boxColorMode.clear()
        self.sliderIntensite.clear()
        self.checkEnable.clear()


    def newTab(self):

        lenghtTabs = len(self.tabs)

        # on cree les layouts pour la nouvelle tab
        self.centralLayout.append(QHBoxLayout())
        self.optionLayout.append(QVBoxLayout())
        self.btnLayout.append(QVBoxLayout())
        self.modeLayout.append(QVBoxLayout())
        self.modsLayout.append(QVBoxLayout())
        self.mediaLayout.append(QVBoxLayout())
        self.envoiLayout.append(QVBoxLayout())
        self.ecranLayout.append(QVBoxLayout())

        titleTemp = []

        # on met les titres des sections
        for i in range (0, len(liste_titles)):
            titleTemp.append(QLabel(liste_titles[i]))
            titleTemp[i].setAlignment(Qt.AlignCenter)
            titleTemp[i].setStyleSheet("font-weight: bold; font-size: 13pt; color: #1A49B3")
           # titleTemp[i].setFont(QFont("Serif"))
            
        self.btnLayout[lenghtTabs].addWidget(titleTemp[0])
        self.modeLayout[lenghtTabs].addWidget(titleTemp[1])
        self.mediaLayout[lenghtTabs].addWidget(titleTemp[2])
        self.modsLayout[lenghtTabs].addWidget(titleTemp[3])
        self.envoiLayout[lenghtTabs].addWidget(titleTemp[4])
        self.ecranLayout[lenghtTabs].addWidget(titleTemp[5])

        # on cree les listes de fonctions temporaires
        labelBtnTemp = []
        boxModeTemp = []
        boxMediaTemp = []
        btnModsTemp = []
        lineEnvoiTemp = []
        lineEcranTemp = []
        menuModifierTemp = []
        menuActionsTemp = []

        for i in range(0,11):
            
            # on met les numero/noms des touches
            if i is 8:
                labelBtnTemp.append(QLabel("Enc. G."))
                pixmap = QPixmap("./buttonsIcons/encoder.jpg")
            elif i is 9:
                labelBtnTemp.append(QLabel("Enc. D."))
                pixmap = QPixmap("./buttonsIcons/encoder.jpg")
            elif i is 10:
                labelBtnTemp.append(QLabel("Enc. B."))
                pixmap = QPixmap("./buttonsIcons/encoder.jpg")
            else:    
                labelBtnTemp.append(QLabel(str(i+1))) 
                pixmap = QPixmap("./buttonsIcons/touche.jpg")
                

            smaller_pixmap = pixmap.scaled(40,25, Qt.KeepAspectRatio, Qt.FastTransformation)
            labelBtnTemp[i].setAlignment(Qt.AlignCenter)
            labelBtnTemp[i].setPixmap(smaller_pixmap)
            labelBtnTemp[i].setToolTip('<img src="settings.png" width="200" height="200">')

            # on ajoute le comboBox du Mode
            combo = QComboBox()
            combo.addItems(liste_modes)
            boxModeTemp.append(combo)

             # on ajoute le comboBox du media
            combo = QComboBox()
            combo.addItems(liste_media)
            boxMediaTemp.append(combo)

            # on cree les menu des modif.
            menu = QMenu()
            menuModifierTemp.append(menu)
            listeActions = []
            for k in range(0, len(liste_modifier)):
                action = QAction(liste_modifier[k])
                action.setCheckable(True)                    
                action.setData(k)
                listeActions.append(action)
                menuModifierTemp[i].addAction(action)
                

            menuActionsTemp.append(listeActions)

             # on ajoute le bouton qui ouvre le menu des modifs.
            btn = QPushButton("")
            btnModsTemp.append(btn)

            # on ajoute le lineEdit de l'envoi
            line = QLineEdit()
            lineEnvoiTemp.append(line)

            # on ajoute le lineEdit de l'ecran
            line = QLineEdit()
            line.setMaxLength(10)
            lineEcranTemp.append(line)
           
        # on ajoute la liste temporaire a notre liste de liste
        self.menuActions.append(menuActionsTemp)
        self.labelBtn.append(labelBtnTemp)
        self.boxMode.append(boxModeTemp)
        self.boxMedia.append(boxMediaTemp)
        self.btnMods.append(btnModsTemp)
        self.lineEnvoi.append(lineEnvoiTemp)
        self.lineEcran.append(lineEcranTemp)
        self.menuModifier.append(menuModifierTemp)

        # on fait l'ajout des widgets a la vrai liste
        for i in range(0,11):

            # on ajoute tous les widgets
            self.btnLayout[lenghtTabs].addWidget(self.labelBtn[lenghtTabs][i])
            self.modeLayout[lenghtTabs].addWidget(self.boxMode[lenghtTabs][i])
            self.mediaLayout[lenghtTabs].addWidget(self.boxMedia[lenghtTabs][i])
            self.modsLayout[lenghtTabs].addWidget(self.btnMods[lenghtTabs][i])
            self.btnMods[lenghtTabs][i].setMenu(self.menuModifier[lenghtTabs][i])
            self.envoiLayout[lenghtTabs].addWidget(self.lineEnvoi[lenghtTabs][i])
            self.ecranLayout[lenghtTabs].addWidget(self.lineEcran[lenghtTabs][i])

            # on connecte tous les signaux
            self.boxMode[lenghtTabs][i].currentIndexChanged.connect(lambda state,ii=i, jj=lenghtTabs: self.buttonMode(jj,ii,self.boxMode[jj][ii].currentIndex()))
            self.boxMedia[lenghtTabs][i].currentIndexChanged.connect(lambda state,ii=i, jj=lenghtTabs: self.buttonMedia(jj,ii,self.boxMedia[jj][ii].currentIndex()))
            self.lineEnvoi[lenghtTabs][i].textChanged.connect(lambda text,ii=i: self.envoiLine(lenghtTabs,ii,text))
            self.lineEcran[lenghtTabs][i].textChanged.connect(lambda text,ii=i: self.ecranLine(lenghtTabs,ii,text))
            self.menuModifier[lenghtTabs][i].triggered.connect((lambda action,ii=i,jj=lenghtTabs: self.modifierCheck(jj,ii, action)))
            
            # on met le mode par defaut (Modif.)
            self.setModeButton(lenghtTabs,i,0)

        # creation du bouton de couleur
        self.btnColor.append(QPushButton("Couleur"))
        self.btnColor[lenghtTabs].clicked.connect(lambda: self.colorButton(lenghtTabs,self.btnColor[lenghtTabs]))
        self.optionLayout[lenghtTabs].addWidget(self.btnColor[lenghtTabs])
        self.btnColor[lenghtTabs].setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnColor[lenghtTabs].setMinimumWidth(200)
        self.btnColor[lenghtTabs].setMinimumHeight(50)

        # mode des leds
        self.boxColorMode.append(QComboBox())
        self.boxColorMode[lenghtTabs].addItems(liste_led_modes)
        self.boxColorMode[lenghtTabs].currentIndexChanged.connect(lambda state, jj=lenghtTabs: self.ledMode(jj,self.boxColorMode[jj].currentIndex()))
        self.optionLayout[lenghtTabs].addWidget(self.boxColorMode[lenghtTabs])
        self.boxColorMode[lenghtTabs].setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.boxColorMode[lenghtTabs].setMinimumWidth(200)

        #slider intensite
        self.sliderIntensite.append(QSlider(Qt.Horizontal))
        self.sliderIntensite[lenghtTabs].valueChanged.connect(lambda state,jj=lenghtTabs:self.intensiteLumiere(jj, self.sliderIntensite[jj].value()))
        self.optionLayout[lenghtTabs].addWidget(self.sliderIntensite[lenghtTabs])

        # on ajoute tous les layouts au central layout
        self.centralLayout[lenghtTabs].addLayout(self.btnLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.modeLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.mediaLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.modsLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.envoiLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.ecranLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.optionLayout[lenghtTabs])

    def addTab(self,open_flag):

        # catch an error si quelqu'un essaye d'ajouter un tab sans avoir de projet d'ouvert
        try:
            tab = QWidget()
            lenghtTabs = len(self.tabs)

            # Max number of tabs
            if lenghtTabs is not 9:
                
                # flag si c'est une ouverture de fichier
                if not open_flag:
                    self.config.sheets.append(sheet())

                self.newTab()

                tab.setLayout(self.centralLayout[lenghtTabs])
                self.tabs.append(tab)

                self.tabsWidget.addTab(self.tabs[lenghtTabs], self.config.sheets[lenghtTabs].name)
                #self.tabsWidget.setFont(QFont('Arial', 20))
                #self.tabs[lenghtTabs].setFont(QFont('Arial', 20))

                if self.config.sheets[lenghtTabs].name is '':
                    self.tabsWidget.setTabIcon(lenghtTabs, QIcon("./TabIcons/{} bleu.png".format(lenghtTabs+1)))

                print(len(self.tabs))
                print(len(self.config.sheets))

        except AttributeError as e:
            print(str(e))


    def askTab(self,index):

        text, ok = QInputDialog().getText(self, "Enter tab name",
                                        "Tab Name:", QLineEdit.Normal)

        if ok:
            self.config.sheets[index].name = text
            self.tabsWidget.setTabText(index,text)

        if text is '':
            self.tabsWidget.setTabIcon(index, QIcon("./TabIcons/{} bleu.png".format(index+1)))
        
        else:
            self.tabsWidget.setTabIcon(index, QIcon(None))


    def ecranLine(self, sheet, button, text):

        self.config.sheets[sheet].buttons[button].screen = text
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].screen)


    def envoiLine(self, sheet, button, text):

        self.config.sheets[sheet].buttons[button].sending = text
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].sending)


    def setModeButton(self, sheet, button, index):

        if index is 0:
            
            self.menuModifier[sheet][button].setEnabled(True)
            self.lineEnvoi[sheet][button].setEnabled(True)
            self.boxMedia[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setMaxLength(1)

        elif index is 1:

            self.boxMedia[sheet][button].setEnabled(True)
            self.menuModifier[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setEnabled(False)
            
        elif index is 2:

            self.menuModifier[sheet][button].setEnabled(True)
            self.lineEnvoi[sheet][button].setEnabled(True)
            self.lineEnvoi[sheet][button].setMaxLength(128)
            self.boxMedia[sheet][button].setEnabled(False)


    def buttonMode(self,sheet, button, index):

        self.config.sheets[sheet].buttons[button].mode = index
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].mode)

        self.setModeButton(sheet,button,index)

        
    def buttonMedia(self,sheet, button, index):
        self.config.sheets[sheet].buttons[button].media = index
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].media)


    def modifierCheck(self, index, button, action):
        self.config.sheets[index].buttons[button].modifiers[action.data()] = action.isChecked()
        print("sheet: ",index)
        print("button:",button)
        print(self.config.sheets[index].buttons[button].modifiers[0])
        print(self.config.sheets[index].buttons[button].modifiers[1])
        print(self.config.sheets[index].buttons[button].modifiers[2])
        print(self.config.sheets[index].buttons[button].modifiers[3])


    def sheetChange(self,index):
        self.config.sheetChanger = index
        print(self.config.sheetChanger)
  

    def ledMode(self,sheet,index):
        self.config.sheets[sheet].led_mode = index
        print("sheet: ",sheet)
        print(self.config.sheets[sheet].led_mode)


    def colorButton(self,sheet,button):
        color = QColorDialog.getColor()
        button.setStyleSheet("background-color:%s" % color.name())
        self.config.sheets[sheet].r = color.red()
        self.config.sheets[sheet].g = color.green()
        self.config.sheets[sheet].b = color.blue()


    def intensiteLumiere(self, sheet, intensite):
        self.config.sheets[sheet].intensite = intensite
        print("sheet: ", sheet)
        print(self.config.sheets[sheet].intensite)


    def loop_finished(self):
        print('Loop Finished')


    def enabledToggle(self, sheet):     
        self.config.sheets[sheet].enabled = not self.config.sheets[sheet].enabled
        print(self.config.sheets[sheet].enabled)


    def openFile(self):
 
        # getting path and bool value
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                             "Text documents (*.txt);All files (*.*)")
 
        # if path is true
        if path:
            # try opening path
            try:
                with open(path, 'rb') as f:
                    # read the file
                    self.config = pickle.load(f)
 
            # if some error occured
            except Exception as e:
 
                # show error using critical method
                self.dialog_critical(str(e))
            # else
            else:
                # update path value
                self.path = path
 
                # update the text
                self.setNewConfig()
                
                # update the title
                self.update_title()

    def setNewConfig(self):

        self.main_widget.deleteLater()   
        self.createTabs()
        for i in range(0, len(self.config.sheets)):
            self.addTab(True)

        # on met les options de sheet
        for i in range(0,len(self.tabs)):
            self.btnColor[i].setStyleSheet("background-color:rgb({},{},{})".format(self.config.sheets[i].r,self.config.sheets[i].g,self.config.sheets[i].b))
            self.boxColorMode[i].setCurrentIndex(self.config.sheets[i].led_mode)
            self.sliderIntensite[i].setValue(self.config.sheets[i].intensite)

            # on met les options de chaque bouton
            for j in range(0,len(self.config.sheets[i].buttons)):

                self.boxMedia[i][j].setCurrentIndex(self.config.sheets[i].buttons[j].media)
                self.boxMode[i][j].setCurrentIndex(self.config.sheets[i].buttons[j].mode)
                self.lineEcran[i][j].insert(self.config.sheets[i].buttons[j].screen)
                self.lineEnvoi[i][j].insert(self.config.sheets[i].buttons[j].sending)

                for k in range(0,len(liste_modifier)):
                    self.menuActions[i][j][k].setChecked(self.config.sheets[i].buttons[j].modifiers[k])




    def update_title(self):
 
        # setting window title with prefix as file name
        # suffix as PyQt5 Notepad
        self.setWindowTitle("%s - Macro clavier 1.0" %(os.path.basename(self.path)
                                                  if self.path else "Untitled"))



def run():
    app = QApplication(sys.argv)
    widget = qt()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()