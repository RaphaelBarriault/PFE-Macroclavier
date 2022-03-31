

import sys, serial, serial.tools.list_ports,  os
from time import sleep
import pickle
from PyQt5.QtCore import  Qt, QObject, pyqtSignal, QThread, pyqtSignal
from PyQt5.QtWidgets import QMenu,QSpacerItem,QFileDialog,QMessageBox, QInputDialog, QToolBar,QCheckBox, QApplication, QFileDialog, QAction, QColorDialog, QComboBox, QDialog, QMainWindow, QWidget, QLabel, QTextEdit, QListWidget, \
     QLineEdit, QPushButton, QTabWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QSlider, QSizePolicy
from PyQt5.QtGui import  QIcon,QPixmap
from PyQt5.Qt import Qt




# liste de tous les modificateurs disponible
liste_modifier = ["Alt", "Ctrl", "Shift", "Win", "Gui"]

# listes des titres des diff/rentes section de configuration des touches
liste_titles = ["Touches", "Mode", "Media", "Mods", "Envoi", "Ecran"]

# liste des touches multimedia disponible
liste_media = ["Up", "Down", "Mute", "Play"]

# liste des modes pour les leds
liste_led_modes = ["Static", "On/Off", "On-Click", "Snake", "Diagonal"]

# liste des modes pour les touches
liste_modes = ["Modif.", "Media.", "Suite", "Page Up", "Page Down", "Go to"]
        

# classe representant une touche
class button():

    def __init__(self):
        
        # keybind envoyer a l'application
        self.sending = ''

        # l'affichage a l'ecran
        self.screen = ''

        # le mode de la touche (voir liste_modes)
        self.mode = 0

        # touche de media (lorsque le mode est <<Media>>)
        self.media = 0

        # liste des modifiers a envoye
        self.modifiers = [False, False,False,False, False]
       
# class representant un sous-dossier
class sheet():

    def __init__(self):

        # la couleur choisi en fonctions de ses parametre r, g et b
        self.r = 255
        self.g = 255
        self.b = 255

        # mode des leds
        self.led_mode = 0

        # intensite des leds
        self.intensite = 0

        # mode contraste 
        self.black = 0

        # nom du sous-dossier pour l'affichage dans l'application
        self.name = ''

        # liste contenant 11 boutons (8 touches, encodeur gauche, droit et centre)
        self.buttons = [button(),button(),button(),
                        button(),button(),button(),button(),button(),button(),button(),button()]

# represente la configuration complete du macro-clavier.
#  C'est cet objet qui est sauvegarde lors d'une sauvegarde de la congi
class config():

    def __init__(self):

        # liste contenant tous les sous-dossiers
        self.sheets = []

# class worker qui sert a faire rouler un thread en parallele de l'application principale
# celui-ci nous permet de detecter les ports series
class WorkerDetect(QObject):

    # connection des signaux
    finished = pyqtSignal()
    numberConnection = pyqtSignal(list)
    

    def run(self):

        # detection des differents ports
        nbPorts = 0
        while(True):
            ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'USB' or 'ACM' in p.description
            ]

            # lorsque le nombre de ports change, on envoi la liste des ports au thread principal
            if len(ports) != nbPorts:
                nbPorts = len(ports)
                self.numberConnection.emit(ports)

            sleep(2)


class qt(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        self.setWindowTitle("Macro Clavier 1.0")

        # initialisation d'une config vide
        self.config = config()

        # path de la config ouverte
        self.path = None    

        # thread qui nous servira a detecter les ports
        self.thread = None
        self.workerDetect = None

        # parametres du port serie connecte
        self.ser = None

        # liste des ports series
        self.ports = []

        # le port serie presentement connecte
        self.connectedBoard = None

        # creations de la main page, de la barre de menu, des actions et de la toolbar
        self.createHelpSection()
        self.createActions()
        self.createMenu()
        self.createToolBar()
        self.createMainPage()

        # creation du thread de detection des ports
        self.detectBoard()


    #---------------------------------------------------------------------------------------------
    #                     Section creations des menus et des actions
    #---------------------------------------------------------------------------------------------


     # creation de la main page de l'application
    def createMainPage(self):
        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.acceuil = QVBoxLayout(self.main_widget)
        
        # affichage de l'ecran d'accueuil
        textAcceuil = QLabel()
        pixmap = QPixmap("accueuil.png")
        smaller_pixmap = pixmap.scaled(1000,300, Qt.KeepAspectRatio, Qt.FastTransformation)
        textAcceuil.setPixmap(smaller_pixmap)             
        self.acceuil.addWidget(textAcceuil, alignment=Qt.AlignCenter)


    # creation Menu file
    def createMenu(self):

        # creation de la barre de menu
        menuBar = self.menuBar()

        # creation des sous-menus
        fileMenu = QMenu("&File", self)
        editMenu = QMenu("&Edit",self)
        connectMenu = QMenu("&Connect", self)
        helpMenu = QMenu("&Help",self)
        
        # ajout des menus a la barre
        menuBar.addMenu(fileMenu)    
        menuBar.addMenu(editMenu)
        menuBar.addMenu(connectMenu)
        menuBar.addMenu(helpMenu)

        # ajout des actions au file menu 
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.exitAction)

        # ajout des actions au edit menu
        editMenu.addAction(self.addTabAction)
        editMenu.addAction(self.deleteTabAction)

        # ajout des actions au connect menu
        connectMenu.addAction(self.sendConfigAction)

        # ajout des actions au help menu
        helpMenu.addAction(self.helpAction)
        

    # creation de la toolBar
    def createToolBar(self):

        # creation et ajout de la toolbar
        self.toolBar = QToolBar("Main toolbar")
        self.addToolBar(self.toolBar)

        # ajout des actions a la toolbar
        self.toolBar.addAction(self.newAction)
        self.toolBar.addAction(self.openAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.addTabAction)
        self.toolBar.addAction(self.deleteTabAction)
        self.toolBar.addSeparator()

        # ajoute le comboBox du ports
        self.portsChoice = QComboBox()
        self.portsChoice.currentIndexChanged.connect(self.connectBoard)
        self.toolBar.addWidget(self.portsChoice)

        # ajout des autres actions
        self.toolBar.addAction(self.sendConfigAction)
        self.toolBar.addSeparator()

        # creation des differentes icone afficher lors du transfert de la configuration
        self.imageSuccess = QLabel('')
        pixmapBegin = QPixmap("./connectionIcons/empty.jpg")
        pixmapSuccess = QPixmap("./connectionIcons/success.png")
        pixmapFailed = QPixmap("./connectionIcons/failed.png")

        self.smallerPixmapBegin = pixmapBegin.scaled(20,20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.smallerPixmapSuccess = pixmapSuccess.scaled(20,20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.smallerPixmapFailed = pixmapFailed.scaled(20,20, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.imageSuccess.setPixmap(self.smallerPixmapBegin)
        self.toolBar.addWidget(self.imageSuccess)
        self.toolBar.addSeparator()

        # ajout de l'action d'aide
        self.toolBar.addAction(self.helpAction)


    # creation des actions
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

        # creation action menu help
        self.helpAction = QAction("&Help")

        # actions pour les tabs
        self.copyTabAction = QAction("Copy tab")
        self.pasteTabAfterAction = QAction("Paste tab after current tab")
        self.pasteTabBeforeAction = QAction("Paste tab before current tab")

        # ajout des icons
        self.newAction.setIcon(QIcon("./toolBarIcons/newAction.jpeg"))
        self.sendConfigAction.setIcon(QIcon("./toolBarIcons/sendAction.png"))
        self.saveAction.setIcon(QIcon("./toolBarIcons/saveAction.png"))
        self.openAction.setIcon(QIcon("./toolBarIcons/openAction.png"))
        self.addTabAction.setIcon(QIcon("./toolBarIcons/addTab.jpg"))
        self.deleteTabAction.setIcon(QIcon("./toolBarIcons/deleteTab1.png"))
        self.helpAction.setIcon(QIcon("./toolBarIcons/?.jpg"))

        # connection des actions
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.saveAsAction.triggered.connect(self.saveAsFile)
        self.addTabAction.triggered.connect(lambda: self.addTab(False))
        self.deleteTabAction.triggered.connect(self.deleteTab)
        self.sendConfigAction.triggered.connect(self.sendConfig)
        self.helpAction.triggered.connect(self.msgBox.exec)
        self.copyTabAction.triggered.connect(self.copyTab)
        self.pasteTabAfterAction.triggered.connect(lambda: self.pasteTab(1))
        self.pasteTabBeforeAction.triggered.connect(lambda: self.pasteTab(0))


    # fonction servant a creer la section d'aide
    def createHelpSection(self):
        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Question)
        self.msgBox.setText("Help section in building.....")
        self.msgBox.setWindowTitle("Help Section")
        self.msgBox.setStandardButtons(QMessageBox.Close)

    
    # on initalise toutes les listes contenant les layouts de l'application
    def initLayouts(self):

        # initialisation des onglets
        self.tabs = []

        # initialisation des listes de layouts
        self.centralLayout = []
        self.optionLayout = []
        self.btnLayout = []
        self.modeLayout = []
        self.modsLayout = []
        self.mediaLayout = []
        self.envoiLayout = []
        self.ecranLayout = []

        # initialisations des listes contenant les widgets pour les touches
        self.labelBtn = []
        self.boxMode = []
        self.boxMedia = []
        self.btnMods = []
        self.lineEnvoi = []
        self.lineEcran = []
        self.menuModifier = []
        self.menuActions = []

        # initialisation des listes contenant les widgets pour les leds
        self.btnColor = []
        self.boxColorMode = []
        self.sliderIntensite = []
        self.checkBlack = []




    #---------------------------------------------------------------------------------------------
    #                       Section methode pour les fichiers
    #---------------------------------------------------------------------------------------------


     # creation d'une nouvelle config
    def newFile(self):

        self.main_widget.deleteLater()   

        # on cree les tabs
        self.createTabs()

        # creation d'une config vide
        self.config = config()

        # on ajoute une table
        self.addTab(False)

        # on update le titre
        self.update_title()


    # sauvegarde la configuration
    def saveFile(self):

        # si aucun path on utilise la fonction save as
        if self.path == None:

            return self.saveAsFile()
 
        # on fait la sauvegarde
        self._save_to_path(self.path)


    # on chosi un path et on sauvegarde la configuration 
    def saveAsFile(self):

        # on ouvre un dialog qui permet de specifier le path ou on sauvegarde la configuration
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                             "Text documents (*.txt);All files (*.*)")
 
        if not path:
            return

        # on fait la sauvegarde
        self._save_to_path(path)


     # sauvegarde l'objet config au path
    def _save_to_path(self, path):

        # on ouvre le path et on dump l;objet config
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.config, f)

        except Exception as e:
            print(str(e))

        # on update le path et le titre
        else:
            self.path = path
            self.update_title()


     # fonction d'ouverture d'une config
    def openFile(self):
 
        # ouverture du dialogue permettant d'aller chercher le path d;un fichier
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                             "Text documents (*.txt);All files (*.*)")

        if path:
            try:
                with open(path, 'rb') as f:
                    
                    # lecture du fichier .obj qu'on insere dans la config
                    self.config = pickle.load(f)
 
            except Exception as e:
                self.dialog_critical(str(e))

            # mise a jour du path et du titre, update de la config
            else:
                self.path = path
                self.setNewConfig()
                self.update_title()
   

    # fonction pour update le titre
    def update_title(self):
        self.setWindowTitle("%s - Macro clavier 1.0" %(os.path.basename(self.path)
                                                  if self.path else "Untitled"))


    #---------------------------------------------------------------------------------------------
    #                              Section gestion tabs
    #---------------------------------------------------------------------------------------------


    # fonction de creation des tabs
    def createTabs(self):

        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
        # on ajoute les actions au contexte menu
        self.main_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.main_widget.addAction(self.copyTabAction)
        self.main_widget.addAction(self.pasteTabAfterAction)
        self.main_widget.addAction(self.pasteTabBeforeAction)

        # on cree le main window
        self.l = QHBoxLayout(self.main_widget)

        # on cree le widget des tabs
        self.tabsWidget = QTabWidget()

        # initialisation des layouts de chaque tab    
        self.initLayouts()
        self.l.addWidget(self.tabsWidget)

        # on connect le tabs widget pour le changement de nom
        self.tabsWidget.tabBarDoubleClicked.connect(self.askTab)


    # permet de copier la tab active 
    def copyTab(self):

        # on va chercher la tab active
        currentTab = self.tabsWidget.currentIndex()

        # on copie la tab dans un buffer
        self.copiedTab = self.config.sheets[currentTab]


    # permet de coller la tab coller dans copiedTab. Le parametre place dit si la tab doit etre 
    # coller avant ou apres la tab active
    def pasteTab(self, place):

        # on va chercher la tab active
        currentTab = self.tabsWidget.currentIndex()

        # on ajoute dans la config la tab presente dans le buffer 
        self.config.sheets.insert(currentTab+place,self.copiedTab)

        # on met a jour la nouvelle config
        self.setNewConfig()


    # efface la tab active
    def deleteTab(self):

        # on essaye d'aller chercher l'index de la tab active (ne fonctionnera pas si aucune tab)
        try:
            currentTab = self.tabsWidget.currentIndex()
            if len(self.tabs) != 0:

                # on enleve la sheet de la config
                self.config.sheets.pop(currentTab)

                # on met a jour la  nouvelle config
                self.setNewConfig()
                
        except AttributeError as e:
            print(str(e))


    # fonction de creation d'un nouvel onglet (mais pas de l'afficher dans l'application)
    def newTab(self):

        # nombre d'onglets present
        lenghtTabs = len(self.tabs)

        # on ajoute les layouts necessaire a la liste chaque layouts
        self.centralLayout.append(QHBoxLayout())
        self.optionLayout.append(QVBoxLayout())
        self.btnLayout.append(QVBoxLayout())
        self.modeLayout.append(QVBoxLayout())
        self.modsLayout.append(QVBoxLayout())
        self.mediaLayout.append(QVBoxLayout())
        self.envoiLayout.append(QVBoxLayout())
        self.ecranLayout.append(QVBoxLayout())

        # buffer pour les titres de section
        titleTemp = []

        # on cree les titres des sections a partir de liste_titles
        for i in range (0, len(liste_titles)):
            titleTemp.append(QLabel(liste_titles[i]))
            titleTemp[i].setAlignment(Qt.AlignCenter)
            titleTemp[i].setStyleSheet("font-weight: bold; font-size: 13pt; color: #1A49B3")
        
        # on ajoute les titres a leur layouts respectifs
        self.btnLayout[lenghtTabs].addWidget(titleTemp[0])
        self.modeLayout[lenghtTabs].addWidget(titleTemp[1])
        self.mediaLayout[lenghtTabs].addWidget(titleTemp[2])
        self.modsLayout[lenghtTabs].addWidget(titleTemp[3])
        self.envoiLayout[lenghtTabs].addWidget(titleTemp[4])
        self.ecranLayout[lenghtTabs].addWidget(titleTemp[5])

        # on cree les listes de de widgets temporaires
        labelBtnTemp = []
        boxModeTemp = []
        boxMediaTemp = []
        btnModsTemp = []
        lineEnvoiTemp = []
        lineEcranTemp = []
        menuModifierTemp = []
        menuActionsTemp = []

        # pour chaque touche
        for i in range(0,11):
            
            # on va chercher l'icone correspondant a la touche
            if i == 8:
                labelBtnTemp.append(QLabel("Enc. G."))
                pixmap = QPixmap("./buttonsIcons/encoder left.png")
            elif i == 9:
                labelBtnTemp.append(QLabel("Enc. D."))
                pixmap = QPixmap("./buttonsIcons/encoder right.png")
            elif i == 10:
                labelBtnTemp.append(QLabel("Enc. B."))
                pixmap = QPixmap("./buttonsIcons/encoder.png")
            else:    
                labelBtnTemp.append(QLabel(str(i+1))) 
                pixmap = QPixmap("./buttonsIcons/button {}.png".format(i+1))
                
            # on scale l'icone et on ajoute l'icone a la liste
            smaller_pixmap = pixmap.scaled(40,25, Qt.KeepAspectRatio, Qt.FastTransformation)
            labelBtnTemp[i].setAlignment(Qt.AlignCenter)
            labelBtnTemp[i].setPixmap(smaller_pixmap)

            # on ajoute le tooltip qui permet de voir le layout du streamdeck lorsqu'on passe sur la touche
            labelBtnTemp[i].setToolTip('<img src="layout clavier.png" width="200" height="200">')

            # on ajoute le comboBox du Mode
            combo = QComboBox()
            combo.addItems(liste_modes)
            boxModeTemp.append(combo)

             # on ajoute le comboBox du media
            combo = QComboBox()
            combo.addItems(liste_media)
            boxMediaTemp.append(combo)

            # on cree le menu des modif.
            menu = QMenu()
            menuModifierTemp.append(menu)
            listeActions = []

            # pour tous les modificateurs
            for k in range(0, len(liste_modifier)):

                # on cree les actions du menu
                action = QAction(liste_modifier[k])

                # on active le checkable 
                action.setCheckable(True) 

                # attribution d'un numero pour les reconnaitre                   
                action.setData(k)

                # ajout de l'action au menu
                listeActions.append(action)
                menuModifierTemp[i].addAction(action)
            
            # on ajoute le menu des modif.
            menuActionsTemp.append(listeActions)

             # on ajoute le bouton qui ouvre le menu des modifs.
            btn = QPushButton("")
            btnModsTemp.append(btn)

            # on ajoute le lineEdit de l'envoi
            line = QLineEdit()
            line.setMaxLength(128)
            lineEnvoiTemp.append(line)

            # on ajoute le lineEdit de l'ecran
            line = QLineEdit()

            # pour les touches le nombre max de caracteres est de 10
            if i < 8:
                line.setMaxLength(10)

            # pour l'encodeur le nombre de caracteres est de 2
            else:
                line.setMaxLength(2)

            lineEcranTemp.append(line)
           
        # on ajoute les listes temporaire de widgets a la vraie liste
        # (qui deviendra une liste 2D, sauf pour medu modifiers qui en sera une 3D)
        self.menuActions.append(menuActionsTemp)
        self.labelBtn.append(labelBtnTemp)
        self.boxMode.append(boxModeTemp)
        self.boxMedia.append(boxMediaTemp)
        self.btnMods.append(btnModsTemp)
        self.lineEnvoi.append(lineEnvoiTemp)
        self.lineEcran.append(lineEcranTemp)
        self.menuModifier.append(menuModifierTemp)

        # on fait l'ajout des widgets des boutons aux layouts correspondant
        for i in range(0,11):

            # on ajoute tous les widgets
            self.btnLayout[lenghtTabs].addWidget(self.labelBtn[lenghtTabs][i])
            self.modeLayout[lenghtTabs].addWidget(self.boxMode[lenghtTabs][i])
            self.mediaLayout[lenghtTabs].addWidget(self.boxMedia[lenghtTabs][i])
            self.modsLayout[lenghtTabs].addWidget(self.btnMods[lenghtTabs][i])
            self.btnMods[lenghtTabs][i].setMenu(self.menuModifier[lenghtTabs][i])
            self.envoiLayout[lenghtTabs].addWidget(self.lineEnvoi[lenghtTabs][i])
            self.ecranLayout[lenghtTabs].addWidget(self.lineEcran[lenghtTabs][i])

            # on connecte tous les signaux a leurs fonctions respectives
            self.boxMode[lenghtTabs][i].currentIndexChanged.connect(lambda state,ii=i, jj=lenghtTabs: self.buttonMode(jj,ii,self.boxMode[jj][ii].currentIndex()))
            self.boxMedia[lenghtTabs][i].currentIndexChanged.connect(lambda state,ii=i, jj=lenghtTabs: self.buttonMedia(jj,ii,self.boxMedia[jj][ii].currentIndex()))
            self.lineEnvoi[lenghtTabs][i].textChanged.connect(lambda text,ii=i: self.envoiLine(lenghtTabs,ii,text))
            self.lineEcran[lenghtTabs][i].textChanged.connect(lambda text,ii=i: self.ecranLine(lenghtTabs,ii,text))
            self.menuModifier[lenghtTabs][i].triggered.connect((lambda action,ii=i,jj=lenghtTabs: self.modifierCheck(jj,ii, action)))
            
            # on met le mode par defaut (Modif.)
            self.setModeButton(lenghtTabs,i,0)

        # creation du titre du menus des leds
        label = QLabel("Mode Leds")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 13pt; color: #1A49B3")
        label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        label.setMaximumHeight(15)

        # ajout au layout des options
        self.optionLayout[lenghtTabs].addWidget(label)

        # ajout d'un spacer pour eviter que les widgets d'options s'eparpille
        spacer = QSpacerItem(100, 185, QSizePolicy.Fixed, QSizePolicy.Fixed)


        # creation du menu deroulant du mode des leds
        self.boxColorMode.append(QComboBox())
        self.boxColorMode[lenghtTabs].addItems(liste_led_modes)

        # connection de la fonction
        self.boxColorMode[lenghtTabs].currentIndexChanged.connect(lambda state, jj=lenghtTabs: self.ledMode(jj,self.boxColorMode[jj].currentIndex()))

        # ajout du widget au layout 
        self.optionLayout[lenghtTabs].addWidget(self.boxColorMode[lenghtTabs])
        self.boxColorMode[lenghtTabs].setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.boxColorMode[lenghtTabs].setMinimumWidth(100)

        # creation du bouton de choix de couleurs
        self.btnColor.append(QPushButton("Couleur"))

        # connection de la fonction
        self.btnColor[lenghtTabs].clicked.connect(lambda: self.colorButton(lenghtTabs,self.btnColor[lenghtTabs]))

        # ajout du widget au layout 
        self.optionLayout[lenghtTabs].addWidget(self.btnColor[lenghtTabs])
        self.btnColor[lenghtTabs].setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnColor[lenghtTabs].setMinimumWidth(100)
        self.btnColor[lenghtTabs].setMinimumHeight(50)

        # creation slider intensite
        self.sliderIntensite.append(QSlider(Qt.Horizontal))

        # connection de la fonction
        self.sliderIntensite[lenghtTabs].valueChanged.connect(lambda state,jj=lenghtTabs:self.intensiteLumiere(jj, self.sliderIntensite[jj].value()))

        # ajout du widget au layout
        self.optionLayout[lenghtTabs].addWidget(self.sliderIntensite[lenghtTabs])

        # creation checkbox pour mode contraste
        self.checkBlack.append(QCheckBox("Contraste"))

        # connection de la fonction
        self.checkBlack[lenghtTabs].stateChanged.connect(lambda : self.checkBlackMode(lenghtTabs,self.checkBlack[lenghtTabs]))

        # ajout du widget au layout
        self.optionLayout[lenghtTabs].addWidget(self.checkBlack[lenghtTabs])

        # ajout du spacer au layout
        self.optionLayout[lenghtTabs].addItem(spacer)

        # on ajoute tous les layouts au central layout
        self.centralLayout[lenghtTabs].addLayout(self.btnLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.modeLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.mediaLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.modsLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.envoiLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.ecranLayout[lenghtTabs])
        self.centralLayout[lenghtTabs].addLayout(self.optionLayout[lenghtTabs])


    # ajout d'un onglet 
    def addTab(self,open_flag):

        # catch an error si quelqu'un essaye d'ajouter un tab sans avoir de projet d'ouvert
        try:
            tab = QWidget()
            lenghtTabs = len(self.tabs)

            # nombre max de tabs est de 9
            if lenghtTabs < 9:
                
                # flag si c'est une ouverture de fichier
                if not open_flag:
                    self.config.sheets.append(sheet())

                # on cree une tab
                self.newTab()

                # on ajoute la nouvelle tabs au layout
                tab.setLayout(self.centralLayout[lenghtTabs])
                self.tabs.append(tab)
                self.tabsWidget.addTab(self.tabs[lenghtTabs], self.config.sheets[lenghtTabs].name)

                # on ajoute le nom du tabs (ou l'icone bleu s'il n'a pas de nom)
                if self.config.sheets[lenghtTabs].name == '':
                    self.tabsWidget.setTabIcon(lenghtTabs, QIcon("./TabIcons/{} bleu.png".format(lenghtTabs+1)))

                print(len(self.tabs))
                print(len(self.config.sheets))

        except AttributeError as e:
            print(str(e))


    # ouvre un dialog pour demander le nom du tab
    def askTab(self,index):

        # ouverture de la fenetre de dialogue
        text, ok = QInputDialog().getText(self, "Enter tab name",
                                        "Tab Name:", QLineEdit.Normal)

        # si le text est ok, on met a jour le nom
        if ok:
            self.config.sheets[index].name = text
            self.tabsWidget.setTabText(index,text)

        # si le texte est vide, on ajoute l'icone avec le numero correspondant
        if text == '':
            self.tabsWidget.setTabIcon(index, QIcon("./TabIcons/{} bleu.png".format(index+1)))
  
        else:
            self.tabsWidget.setTabIcon(index, QIcon(None))



    #---------------------------------------------------------------------------------------------
    #                            Section update de la config
    #---------------------------------------------------------------------------------------------


     # fonction pour setter le black mode dans la config lors du trigger du checkbox
    def checkBlackMode(self,sheet,check):
        self.config.sheets[sheet].black = not self.config.sheets[sheet].black
        print("sheet: ",sheet)
        print("state: ",self.config.sheets[sheet].black)


    # met a jour la config par rapport a ce qui est ecrit dans le widget ecran
    def ecranLine(self, sheet, button, text):

        self.config.sheets[sheet].buttons[button].screen = text
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].screen)


    # met a jour la config par rapport a ce qui est ecrit dans le widget envoi
    def envoiLine(self, sheet, button, text):

        self.config.sheets[sheet].buttons[button].sending = text
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].sending)


    # on active les widgets e la ligne dependnat du mode choisi pour la touche
    def setModeButton(self, sheet, button, index):

        # pour le mode modif, on enable le menu de modif, on active la ligne d'envoi
        # on descative le combobox de media et on met la ligne d'envoie a un caracter max
        if index == 0:         
            self.menuModifier[sheet][button].setEnabled(True)
            self.lineEnvoi[sheet][button].setEnabled(True)
            self.boxMedia[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setMaxLength(1)

        # pour le mode media on active le combobox media et on desactive le menu
        # de modifiers et la ligne d'envoi
        elif index == 1:
            self.boxMedia[sheet][button].setEnabled(True)
            self.menuModifier[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setEnabled(False)
        
        # pour le mode de suite on desactive le combobox media et le menu de modifiers,
        # on active la ligne d'envoi et on met le nombre de caractere max a 128
        elif index == 2:
            self.menuModifier[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setEnabled(True)
            self.lineEnvoi[sheet][button].setMaxLength(128)
            self.boxMedia[sheet][button].setEnabled(False)

        # pour les modes page up et page down on desactive le combobox media, le menu
        # modifiers et la ligne d'envoi
        elif index == 3 or index == 4:
            self.boxMedia[sheet][button].setEnabled(False)
            self.menuModifier[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setEnabled(False)
        
        # pour le mode go to on desactive le combobox media et le menu modifier
        # on active la ligne d'envoi et on la bloque a 1 caractere
        elif index == 5:
            self.menuModifier[sheet][button].setEnabled(False)
            self.lineEnvoi[sheet][button].setEnabled(True)
            self.lineEnvoi[sheet][button].setMaxLength(1)
            self.boxMedia[sheet][button].setEnabled(False)


    # met a jour la config par rapport a ce qui est dans le combobox mode et update les
    # widgets on consequence
    def buttonMode(self,sheet, button, index):

        self.config.sheets[sheet].buttons[button].mode = index
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].mode)

        self.setModeButton(sheet,button,index)


    # met a jour la config par rapport a ce qui est ecrit dans le combobox media
    def buttonMedia(self,sheet, button, index):
        self.config.sheets[sheet].buttons[button].media = index
        print("sheet: ", sheet)
        print("button: ", button)
        print(self.config.sheets[sheet].buttons[button].media)


    # met a jour la config par rapport a ce qui est ecrit dans menu modifiers
    def modifierCheck(self, index, button, action):
        self.config.sheets[index].buttons[button].modifiers[action.data()] = action.isChecked()
        print("sheet: ",index)
        print("button:",button)
        print(self.config.sheets[index].buttons[button].modifiers[0])
        print(self.config.sheets[index].buttons[button].modifiers[1])
        print(self.config.sheets[index].buttons[button].modifiers[2])
        print(self.config.sheets[index].buttons[button].modifiers[3])
        print(self.config.sheets[index].buttons[button].modifiers[4])


    # met a jour la config par rapport a ce qui est dans le combobox mode led
    def ledMode(self,sheet,index):
        self.config.sheets[sheet].led_mode = index
        print("sheet: ",sheet)
        print(self.config.sheets[sheet].led_mode)


    # fonction pour choisir la couleur des leds
    def colorButton(self,sheet,button):

        # ouvre la fenetre de du color dialog
        color = QColorDialog.getColor()

        # met le bouton de la couleur choisi
        button.setStyleSheet("background-color:%s" % color.name())

        # met a jour la config avec le rgb de la couleur choisi
        self.config.sheets[sheet].r = color.red()
        self.config.sheets[sheet].g = color.green()
        self.config.sheets[sheet].b = color.blue()


     # met a jour la config par rapport a ce qui est dans le slider d'intensite
    def intensiteLumiere(self, sheet, intensite):
        self.config.sheets[sheet].intensite = intensite
        print("sheet: ", sheet)
        print(self.config.sheets[sheet].intensite)


    # on update les layouts et l'app avec la config actuelle
    def setNewConfig(self):

        # on supprime la fenetre principale
        self.main_widget.deleteLater()   

        # on cree les tabs
        self.createTabs()
        for i in range(0, len(self.config.sheets)):
            self.addTab(True)

        # on met les options des leds par rapport a ce qui a dans la config
        for i in range(0,len(self.tabs)):
            self.btnColor[i].setStyleSheet("background-color:rgb({},{},{})".format(self.config.sheets[i].r,self.config.sheets[i].g,self.config.sheets[i].b))
            self.boxColorMode[i].setCurrentIndex(self.config.sheets[i].led_mode)
            self.sliderIntensite[i].setValue(self.config.sheets[i].intensite)
            self.checkBlack[i].setChecked(self.config.sheets[i].black)

            # on met les options de chaque touche par rapport a ce qu'il y a dans la config
            for j in range(0,len(self.config.sheets[i].buttons)):

                self.boxMedia[i][j].setCurrentIndex(self.config.sheets[i].buttons[j].media)
                self.boxMode[i][j].setCurrentIndex(self.config.sheets[i].buttons[j].mode)
                self.lineEcran[i][j].insert(self.config.sheets[i].buttons[j].screen)
                self.lineEnvoi[i][j].insert(self.config.sheets[i].buttons[j].sending)

                # on coche les modificateurs dans chaque menu
                for k in range(0,len(liste_modifier)):
                    self.menuActions[i][j][k].setChecked(self.config.sheets[i].buttons[j].modifiers[k])

    #---------------------------------------------------------------------------------------------
    #                         Section communication macro-clavier
    #---------------------------------------------------------------------------------------------


    # fonction de creation du thread de detection
    def detectBoard(self):

        # creation du thread et du worker object
        self.thread = QThread()
        self.workerDetect = WorkerDetect()
        self.workerDetect.moveToThread(self.thread)

        # connection des siganux aux methodes
        self.thread.started.connect(self.workerDetect.run)
        self.workerDetect.finished.connect(self.thread.quit)
        self.workerDetect.finished.connect(self.workerDetect.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.workerDetect.numberConnection.connect(self.updateConnection)

        # debut du thread
        self.thread.start()


    # fonction qui update les connections de ports serie dans la comboBox avec ce 
    # qu'il recoit du thread de detection
    def updateConnection(self,n):

        tempPorts = []
        self.ports = n

        # si on a au moins un port, on active le bouton d'envoi de la config
        if len(self.ports) > 0:
           self.sendConfigAction.setEnabled(True)

        else:
            self.sendConfigAction.setEnabled(False)

        # on garde en memoire le port courant
        text = self.portsChoice.currentText()

        # on clear la liste de ports
        self.portsChoice.clear()

        # on update la liste de ports. si le port qui etait choisi est 
        # encore dans la liste, on le met en premier dans la nouvelle 
        # liste pour qu'il reste celui connecte
        if text in self.ports:

            self.portsChoice.addItem(text)
            n.remove(text)
            tempPorts.append(text)

        for p in n:
            self.portsChoice.addItem(p)
            tempPorts.append(p)

        self.ports = tempPorts   

        # on se connecte au premier board de la liste  
        self.connectBoard(0)


    # fonction servant a connecter un board
    def connectBoard(self,index):

        if (len(self.ports) > 0):
            if self.connectedBoard != self.ports[index]:
                self.ser = serial.Serial(self.ports[index],9600, timeout=1)
                print("connected: ", self.ports[index])
                self.connectedBoard = self.ports[index]

            else: 
                print("port already connected")
        
        else:
            self.ser = None
            print("no port connected")


    # envoi de la congi au microcontroleur
    def sendConfig(self):

        #TODO parse la config

        # on envoie pour chaque bouton de chaque sheets un bloc de donnee 
        # selon ce format 
        for sheet in range(0,len(self.config.sheets)):
            for button in range(0,len(self.config.sheets[sheet].buttons)):

                mode = self.config.sheets[sheet].buttons[button].mode

                if mode == 0:

                    keybind = ''
                    for k in range(0,5):
                        if(self.config.sheets[sheet].buttons[button].modifiers[k]):

                            keybind = keybind + chr(14+k)

                    keybind = keybind + self.config.sheets[sheet].buttons[button].sending
                
                elif mode == 1:
                    keybind = '{}'.format(chr(65 + self.config.sheets[sheet].buttons[button].media))

                elif mode == 2:
                    keybind = self.config.sheets[sheet].buttons[button].sending

                elif mode == 3:
                    mode = 3
                    keybind = 'U'
                    
                elif mode == 4:
                    mode = 3
                    keybind = 'D'

                elif mode == 5:
                    mode = 3
                    keybind = self.config.sheets[sheet].buttons[button].sending
                    
                
                label = self.config.sheets[sheet].buttons[button].screen

                block =  '{},{},{},{},{},{},{}'.format(hex(1),sheet,button,hex(mode),keybind,hex(2),label)
                self.ser.write(block.encode())
                sleep(0.5)
                print(block)

            # apres la reception des blocs, le microcontroleur envoie une reponse
            # on update l'icone de reussite de transfert en consequence
            data = self.ser.readline()

            # si le transfert du bloc est un succes
            if(data == b'S'):
                print("Successful")
                self.imageSuccess.setToolTip('Success')
                self.imageSuccess.setPixmap(self.smallerPixmapSuccess)

            # si c'est un echec
            elif(data == b'F'):
                print("Failed")
                self.imageSuccess.setToolTip('The data didnt transmit correctly')
                self.imageSuccess.setPixmap(self.smallerPixmapFailed)

            # si on ne recoit aucune reponse du microcontroleur avant le timeout  
            elif(data == b'N'):
                print("No answer from the streamdeck")
                self.imageSuccess.setToolTip('No answer from the streamdeck')
                self.imageSuccess.setPixmap(self.smallerPixmapFailed)

            # on recoit une reponse inattendu du microcontrleur
            else:
                self.imageSuccess.setToolTip('Unknown error happened')
                print("An unknown problem occured")
                self.imageSuccess.setPixmap(self.smallerPixmapFailed)
        


def run():
    app = QApplication(sys.argv)
    widget = qt()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()