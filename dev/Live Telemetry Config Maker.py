from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, sys


# storing the class instances
tabInstances = []

#car name. Should be "CAN" on a car and "ITEMS" on paddock
#name leftover from when all cars where in one file
globalCarName = ""

#stores the index of the current file in use
currentIndex = 0

def saveAsButton(fileName,whatToSave,howToSave):
    # reusable saving function

    file = open(fileName, howToSave)
            
    file.write(whatToSave)

    file.close()

def loadFile(fileName):
    # same as saveAsButton but loads instead and returns what is loaded
    file = open(fileName, "r")
            
    returnData = file.read()

    file.close()

    return returnData

#LE = Logan Edition
class TextEditLE(QTextEdit):
    # Allows for pressing Enter/Return to take you to the next option

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(27)
        self.setTabChangesFocus(True)

    def keyPressEvent(self, event):
        #Makes it so pressing 'Enter' takes you to the next child just like tabbing
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.focusNextChild()

            event.ignore()
        else: 
            super().keyPressEvent(event)

class PushButtonLE(QPushButton):
    # Quick fix for TextEditLE not liking the default Focus Policy
    
    def __init__(self, text, clicked=None, parent=None):
        super().__init__(text, parent)
        
        self.setFocusPolicy(Qt.StrongFocus)

        if clicked:
            self.clicked.connect(clicked)

class GroupBoxLE(QGroupBox):
    # allows GroupBox to be clicked like a buttton
    
    clicked = pyqtSignal()

    def __init__(self, text, clicked=None, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class OutputWindow(QWidget):
    # Despite the name this is actually the Main Window. Early on the functionality of OutputWindow and MainWindow were reversed from what they are here.
    # This class' main purpose is to draw the main window and its associated functionality
    
    
    def __init__(self):
        # general initilization. Draws what the program looks like before you create or load a file
        
        super().__init__()        

        self.setWindowTitle('Live Telemetry Config Maker')

        self.setWindowIcon(QIcon("TempIco.png"))
        
        self.layout = QGridLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()

        # Creates the New and Load file buttons
        newFileButton = PushButtonLE('New File')
        newFileButton.clicked.connect(self.newFileButton)


        loadFileButton = PushButtonLE('Load File')
        loadFileButton.clicked.connect(self.loadFileButton)

        
        self.layout.addWidget(newFileButton,0,0)

        self.layout.addWidget(loadFileButton,0,1)


    def reloadText(self):
        # Redraws the OutputWindow to include all the data from the loaded file.
        # This also runs when a new file is created it just doesn't fill in the data that is missing.
        
        global tabInstances

        self.setUpdatesEnabled(True)
        

        # Removes any tabs created prior to the running of function.
        # This prevents duplicate tabs from appearing upon refresh.

        while self.tabs.count():
            self.tabs.removeTab(0)

        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        

        # Begins creation of the UI. Starting with the buttons seen in __init__()
        newFileButton = PushButtonLE('New File')
        newFileButton.clicked.connect(self.newFileButton)


        loadFileButton = PushButtonLE('Load File')
        loadFileButton.clicked.connect(self.loadFileButton)

        makePaddock = PushButtonLE('Create Paddock', clicked=lambda _, tabs=tabInstances: self.createPaddock(tabs))

        doneButton = PushButtonLE('Save', clicked=lambda: self.formatThenSave(self.tabs.currentIndex()))
        

        # Adds the three buttons above to the layout
        self.layout.addWidget(newFileButton,0,0)

        self.layout.addWidget(loadFileButton,0,1)

        self.layout.addWidget(makePaddock,0,2)
        
        self.layout.addWidget(doneButton,0,3)
        


        for i in tabInstances:

            # begins the process of making tabs and adding the groupboxes to said tabs
            tabMaker = QScrollArea()
            tabMaker.setWidgetResizable(True)

            # "scrollWidget" its a QWidget made explicitly to be scrollable
            scrollWidget = QWidget()
            scrollWidget.setObjectName("scrollWidget")
            scrollWidget.setLayout(i.returnBoxes())


            layoutCombined = QVBoxLayout()

            
            # Everything from here to the end of the function is just combining layouts and widgets to create the app's appearence
            settingsWidget = QWidget()
            settingsWidget.setObjectName("scrollWidget")
            settingsWidget.setLayout(i.returnSettings())
            
            
            layoutCombined.addWidget(settingsWidget)
            
            
            layoutCombined.addWidget(scrollWidget)

            combinedWidget = QWidget()
            combinedWidget.setObjectName("combinedWidget")
            combinedWidget.setLayout(layoutCombined)



            tabMaker.setWidget(combinedWidget)


            self.tabs.addTab(tabMaker, str(tabInstances.index(i)+1))
            self.tabs.setObjectName("tabs")

            self.tabs.tabBarClicked.connect(self.tabIndex)

            self.layout.addWidget(self.tabs,1,0,1,4)

            self.loadHeaderData(i.typeRadioButtons, i.createdTextEdits, i.busSpeedRadioButtons, tabInstances.index(i))


    def createPaddock(self, tabInstances):
        # takes all the needed information from all the loaded files and outputs them in the paddock format
        options = QFileDialog.Options()
        
        directory = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if directory:
        
            paddock = {
                "TYPE": 0,
                "CARS": []
            }

            for i in tabInstances:
                dictionaryCopy = i.userEnterData.copy()

                unneededItems = ["F","L","BO","BL","ID"]
                
                for j in i.userEnterData["CAN"]:
                    for k in unneededItems:
                        dictionaryCopy["CAN"][i.userEnterData["CAN"].index(j)].pop(k)
                
                carIndex = {
                    "CN": dictionaryCopy["CN"],
                    "ITEMS": []
                }

                for j in dictionaryCopy["CAN"]:
                    carIndex["ITEMS"].append(j)
                
                paddock["CARS"].append(carIndex)

            dumpedFile = json.dumps(paddock)

            dumpedFile = dumpedFile.replace(': [{', ':[\n    {')
            dumpedFile = dumpedFile.replace('}], ', '}\n],\n')
            dumpedFile = dumpedFile.replace('}, {', '},\n    {')
            dumpedFile = dumpedFile.replace('}]}]}', '}]}\n]}')
            
            saveAsButton(directory[0],dumpedFile,"w")


    def tabIndex(self, index):

        global currentIndex

        print(index)
        if index != -1:
            currentIndex = index
            print(currentIndex)

    
    def saveHeaderData(self, typesRadio, listOfTextEdits, busRadio, index):
        # As is the title of the function this saves the header data
        
        global tabInstances, currentIndex

        try:
            if typesRadio.checkedButton().sendOrRecieve == None:
                print("Type Radio None")

            # index 0 and 3 go unused
            print(f"{listOfTextEdits[1].toPlainText()}")
            if listOfTextEdits[1].toPlainText() == None:
                print("Text Edit 0 None or empty")

            if listOfTextEdits[2].toPlainText() == None:
                print("Text Edit 1 None or empty")

            if busRadio == None:
                print("Bus Radio None")

            tabInstances[index].userEnterData["TYPE"] = int(typesRadio.checkedButton().sendOrRecieve)

            tabInstances[index].userEnterData["CN"] = int(listOfTextEdits[1].toPlainText())

            tabInstances[index].userEnterData["GID"] = int(listOfTextEdits[2].toPlainText(),16)

            tabInstances[index].userEnterData["BS"] = int(busRadio.checkedButton().speed)

        except Exception as err:
            print(err)
            msg = QMessageBox()
            msg.setText(f"Could not save file.\n{err}")
            msg.setWindowTitle("Error")
            msg.exec()
        

    def loadHeaderData(self, typesRadioButtons, listOfTextEdits, busRadioButtons, index):
        # loads the header data. Is called at the end of reload text so when a file is loaded you always have its data

        global tabInstances, currentIndex

        try:
            #print(tabInstances[currentIndex].userEnterData)
            
            listOfTextEdits[1].setPlainText(str(tabInstances[index].userEnterData["CN"])) 

            listOfTextEdits[2].setPlainText(hex(tabInstances[index].userEnterData["GID"]))

            for i in typesRadioButtons:
                if i.sendOrRecieve == int(tabInstances[index].userEnterData["TYPE"]):
                    i.setChecked(True)

            for i in busRadioButtons:
                if i.speed == int(tabInstances[index].userEnterData["BS"]):
                    i.setChecked(True)

        except Exception as err:
            print(err)
            msg = QMessageBox()
            msg.setText(f"Could not save file.\n{err}")
            msg.setWindowTitle("Error")
            msg.exec()


    def newFileButton(self):
        # Creates the base of the file
        
        global tabInstances, currentIndex

        tabInstances.append(TabSystem())

        options = QFileDialog.Options()
        
        directory = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if directory:
            tabInstances[len(tabInstances)-1].userDirectory = directory[0]

            #Reciever or Sender
            # 0 for Paddock, 1 for Car
            tabInstances[len(tabInstances)-1].userEnterData["TYPE"] = 1

            #Car Number
            # INT
            tabInstances[len(tabInstances)-1].userEnterData["CN"] = 0

            #Global CAN ID
            # INT
            tabInstances[len(tabInstances)-1].userEnterData["GID"] = 0 # Entered as a hexadecimal but needs to be INT in the file

            #CAN Bus Speed
            # INT
            tabInstances[len(tabInstances)-1].userEnterData["BS"] = 1000000

            # If you're on the racing team you should know of CAN
            # This is the array of configs
            tabInstances[len(tabInstances)-1].userEnterData["CAN"] = []


            self.reloadText()


    def loadFileButton(self):
        # loads the file and ensures the data is somewhat valid
        
        global tabInstances

        options = QFileDialog.Options()

        msg = QMessageBox()

        tabInstances.append(TabSystem())
        
        directory = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if directory:
            tabInstances[len(tabInstances)-1].userDirectory = directory[0]
            #userDirectory = directory[0]

            try:
                loadedFile = loadFile(tabInstances[len(tabInstances)-1].userDirectory)

                tabInstances[len(tabInstances)-1].userEnterData = json.loads(loadedFile)
                #userEnterData = json.loads(loadedFile)
                

                msg.setText("Successfully loaded configuration!")
                msg.setWindowTitle("Success")
                msg.exec()

            except:
                msg.setText("Could not load Json file.")
                msg.setWindowTitle("Error")
                msg.exec()

            else:
                self.reloadText()


    def formatThenSave(self, index):
        # formats the data then writes it the the txt
        
        global tabInstances, currentIndex

        dumpedFile = ""

        msg = QMessageBox()

        try:

            self.saveHeaderData(tabInstances[index].typeButtonGroup, tabInstances[index].createdTextEdits, tabInstances[index].busSpeedButtonGroup, index)

            dumpedFile = json.dumps(tabInstances[index].userEnterData)

            dumpedFile = dumpedFile.replace(': [{', ':[\n    {')
            dumpedFile = dumpedFile.replace('}], ', '}\n],\n')
            dumpedFile = dumpedFile.replace('}, {', '},\n    {')


            saveAsButton(tabInstances[index].userDirectory,dumpedFile,"w")

            msg.setText("File saved successfully!")
            msg.setWindowTitle("Success")

        except Exception as err:
            msg.setText(f"Error. Something went wrong.\n{err}")
            msg.setWindowTitle("Error")
            

        finally:
            msg.exec()


class TabSystem(QWidget):

    # storage for the loaded file
    userDirectory = ""
    userEnterData = {}

    SecondWindow = None
    
    def __init__(self):
        super().__init__()



    def returnBoxes(self):
        # Creates a copy of the data loaded. This was more necessary earlier in development to removed header data for easier editing.
        # Now that header data has been removed and what replaced it can be edited.
        reloadEnteredData = self.userEnterData.copy()

        
        # In earlier verions of the program this was dynamically changed when all Cars were stored in the same file.
        # Rather than removing and hard coding "CAN" the variable is just changed here.
        key = 'CAN'

        tabLayout = QVBoxLayout()

        
        # This counter tracks which box is created. 
        # With this stored it can be passed to MainWindow where the information displayed in the selected box can be autofilled in for convenience
        entryCounter = 0



        addEntry = PushButtonLE('Add Config')
        
        addEntry.setObjectName("addEntryButton")
        
        # I struggled to figure out why it wasn't passing the proper values
        # It now works but I don't want to change it just in case
        explicitKey = str(key)

        addEntry.clicked.connect(lambda _, carName=explicitKey: self.sendData(carName, "add"))

        tabLayout.addWidget(addEntry)



        for value in reloadEnteredData[key]:
            # This loop creates the boxes that visualize the configurations
            # reloadEnteredData[key] is a list that's values are grabbed here

            groupBoxLayout = QVBoxLayout()

            groupBox = GroupBoxLE(str(value['N']))

            for lowestKey in value:
                # Here it grabs the "lowest key" as in the dictionary keys inside of the list

                itemsToDisplay = [["Name","N"], ["Frequency","F"], ["Lora","L"], ["Bit Offset","BO"], ["Bit Lenght","BL"], ["Can ID (HEX)","ID"]]
                for i in itemsToDisplay:
                    if lowestKey == i[1]:
                        # Checks if the key matches the list of items that need to be displayed
                        
                        formattedData = None

                        if lowestKey == "L":
                            # Edge case where the value of isLora is written out rather than just displaying the value
                            formattedData = QLabel(f"{i[0]}: {bool(value[lowestKey])}")
                        elif lowestKey == "ID":
                            formattedData = QLabel(f"{i[0]}: {hex(value[lowestKey])}")
                        else:
                            formattedData = QLabel(f"{i[0]}: {value[lowestKey]}")
                        groupBoxLayout.addWidget(formattedData)

            
            # sets the groupbox name to key, 
            # makes name equal to the object name, 
            # then passes it into the clicked action of the groupbox
            groupBox.setObjectName(str(key))

            name = groupBox.objectName()

            groupBox.clicked.connect(lambda index=entryCounter, groupName=str(name): self.sendData(groupName,"edit",index))


            groupBox.setLayout(groupBoxLayout)

            tabLayout.addWidget(groupBox)
            
            entryCounter += 1


        return tabLayout


    def returnSettings(self):
            settingsLayout = QGridLayout()

            # The below blocked out function dynamically creates radio buttons 
            # -------------------------------------------------------
            self.typeButtonGroup = QButtonGroup()

            lableNameCounter = 0

            # This function defines how many buttons are created. Index #,0 defines what gets written to the file
            # Index #,1 defines what gets displayed on the screen
            types = [[0,"Paddock"],[1,"Car"]]

            self.typeRadioButtons = []
            radioLayout1 = QHBoxLayout()

            typeCounter = 0
            while len(self.typeRadioButtons) < len(types):
                #creates the actual button and adds it to an array
                typeRadioButton = QRadioButton(f"{types[typeCounter][1]}")
                typeRadioButton.sendOrRecieve = types[typeCounter][0]
                self.typeButtonGroup.addButton(typeRadioButton)
                self.typeRadioButtons.append(typeRadioButton)

                typeCounter += 1
            
            
            # this adds the buttons created above to the layout
            # Just a lazy way of disabling the choice when making a car
            # Mainly done in case the change was rejected
            '''
            for j in self.typeRadioButtons:
                
                radioLayout1.addWidget(j)
            '''
            radioWidget1 = QWidget()
            radioWidget1.setLayout(radioLayout1)

            settingsLayout.addWidget(radioWidget1,lableNameCounter,1)
            # -------------------------------------------------------

            
            # Below dynamically creates lables based off the below list. It also creates TextEditLE for the two text inputs
            #namesForLables = [["TYPE","TYPE"], ["CN","Car Number"], ["GID","Global Time ID"], ["BS", "Bus Speed"]]
            namesForLables = [["CN","Car Number"], ["GID","Global Time ID"], ["BS", "Bus Speed"]]

            self.createdTextEdits = []
            
            # Index 0 and 3 are unused. Modifying them is useless
            while len(self.createdTextEdits) < len(namesForLables):
                bunchOfTextEdits = TextEditLE()
                
                self.createdTextEdits.append(bunchOfTextEdits)

            
            while lableNameCounter < len(namesForLables):
                # Dyanmically Create Lables based on the lenght and contents of namesForLables
                settingsLayout.addWidget(QLabel(namesForLables[lableNameCounter][1] + ": "),lableNameCounter,0)

                
                if lableNameCounter < len(self.createdTextEdits):
                    if lableNameCounter != 0 and lableNameCounter != 3:
                        settingsLayout.addWidget(self.createdTextEdits[lableNameCounter],lableNameCounter-1,1,1,3)

                lableNameCounter = lableNameCounter + 1
            
            

            # The below blocked out function dynamically creates radio buttons
            # Almost identical to the blocked out portion at line 248
            # -------------------------------------------------------
            self.busSpeedButtonGroup = QButtonGroup()

            busSpeeds = [1000000,500000,250000,100000,50000]

            self.busSpeedRadioButtons = []
            radioLayout2 = QHBoxLayout()

            busCounter = 0
            while len(self.busSpeedRadioButtons) < len(busSpeeds):
                #creates the actual button and adds it to an array
                busSpeedRadioButton = QRadioButton(f"{busSpeeds[busCounter]}")
                busSpeedRadioButton.speed = busSpeeds[busCounter]
                self.busSpeedButtonGroup.addButton(busSpeedRadioButton)
                self.busSpeedRadioButtons.append(busSpeedRadioButton)

                busCounter += 1

            for k in self.busSpeedRadioButtons:   
                radioLayout2.addWidget(k)

            radioWidget2 = QWidget()
            radioWidget2.setObjectName("BusSpeedRadioButtons")
            radioWidget2.setLayout(radioLayout2)

            settingsLayout.addWidget(radioWidget2,lableNameCounter-1,1)
            # -------------------------------------------------------

            return settingsLayout


    def sendData(self, carName, mode, index=0):
        # Sends the data from OutputWindow to MainWindow
        
        global globalCarName
        
        print(carName)
        
        globalCarName = carName

        self.showWindow(MainWindow, "main", mode)

        self.SecondWindow.carLoopIndex = index

        if mode == "edit":
            self.SecondWindow.setPlaceholderData(self.userEnterData)

        self.SecondWindow = None


    def showWindow(self, windowClass, windowSelect, mode=None):
        # Shows the window, also has some leftover functionality from a class that no longer exists
        
        if self.SecondWindow is None:
            
            if windowSelect == "main":
                MainWindow.windowMode = mode
            
            self.SecondWindow = windowClass()
        
        self.SecondWindow.show()


class MainWindow(QWidget):
    # Creates the secondary window used to add or edit. 
    # As explained in OutputWindow early on the functionality of OutputWindow and MainWindow were reversed from what they are here 
    
    # Defines the mode which is used later to pick if a config should be added or edited
    windowMode = "add"

    carLoopIndex = 0
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Live Telemetry Config Maker')

        self.setWindowIcon(QIcon("TempIco.png"))

        layout = QGridLayout()

        self.freqButtonGroup = QButtonGroup()
        self.typeButtonGroup = QButtonGroup()
        self.precisionButtonGroup = QButtonGroup()


        # below are three functions to dynamically create radio buttons
        # You can find more details on how these work in OutputWindow().reloadText()
        precision = [1,10,100]

        self.precisionRadioButtons = []

        precisionCounter = 0
        while len(self.precisionRadioButtons) < len(precision):
            precisionRadioButton = QRadioButton(f"{precision[precisionCounter]}")
            precisionRadioButton.precision = precision[precisionCounter]
            self.precisionButtonGroup.addButton(precisionRadioButton)
            self.precisionRadioButtons.append(precisionRadioButton)

            layout.addWidget(self.precisionRadioButtons[precisionCounter],4,precisionCounter+1)

            precisionCounter += 1
        
        
        freqs = [1,10,100]

        self.freqRadioButtons = []

        freqCounter = 0
        while len(self.freqRadioButtons) < len(freqs):
            freqRadioButton = QRadioButton(f"{freqs[freqCounter]}")
            freqRadioButton.frequencey = freqs[freqCounter]
            self.freqButtonGroup.addButton(freqRadioButton)
            self.freqRadioButtons.append(freqRadioButton)

            layout.addWidget(self.freqRadioButtons[freqCounter],5,freqCounter+1)

            freqCounter += 1


        dataTypes = [["Unsigned",117],["Float",102],["Integer",105]]

        self.typesRadioButtons = []

        typesCounter = 0
        while len(self.typesRadioButtons) < len(dataTypes):
            typesRadioButton = QRadioButton(f"{dataTypes[typesCounter][0]}")
            typesRadioButton.dataType = dataTypes[typesCounter][1]
            self.typeButtonGroup.addButton(typesRadioButton)
            self.typesRadioButtons.append(typesRadioButton)

            layout.addWidget(self.typesRadioButtons[typesCounter],6,typesCounter+1)

            typesCounter += 1


        self.isLoraCheckbox = QCheckBox()

        
        namesForLables = ["Name", "Conversion", "Units", "Precision", "Frequency", "Type", "Is Lora", "Bit Offset", "Bit Length", "CAN ID (Hex)"]

        self.createdTextEdits = []
        
        # Three of these go unused because I was too lazy to figure out the skipping beyond what is seen below
        # Index 3, 4, and 5 are unused. Modifying them is useless
        while len(self.createdTextEdits) < len(namesForLables):
            bunchOfTextEdits = TextEditLE()
            
            self.createdTextEdits.append(bunchOfTextEdits)
        
        lableNameCounter = 0
        while lableNameCounter < len(namesForLables):
            # Dyanmically Create Lables based on the lenght and contents of namesForLables
            layout.addWidget(QLabel(namesForLables[lableNameCounter] + ": "),lableNameCounter+1,0)

            
            if lableNameCounter < len(self.createdTextEdits):
                if lableNameCounter != 3 and lableNameCounter != 4 and lableNameCounter != 5 and lableNameCounter != 6:
                    layout.addWidget(self.createdTextEdits[lableNameCounter],lableNameCounter+1,1,1,3)

                else:
                    # quick fix for tabbing since the actual way to correct tab order wasn't working
                    layout.addWidget(self.isLoraCheckbox,7,1)

            lableNameCounter = lableNameCounter + 1

        #type should be a select box of string, int, float
        addButton = PushButtonLE('Save Entry', 
                                 clicked=lambda: self.addConfiguration(self.createdTextEdits, 
                                                                       self.freqButtonGroup, 
                                                                       self.typeButtonGroup, 
                                                                       self.isLoraCheckbox.isChecked(),
                                                                       self.precisionButtonGroup))


        editEntryButton = PushButtonLE('Save Entry', 
                                 clicked=lambda: self.editEntry(self.createdTextEdits, 
                                                                       self.freqButtonGroup, 
                                                                       self.typeButtonGroup, 
                                                                       self.isLoraCheckbox.isChecked(),
                                                                       self.precisionButtonGroup))
        
        deleteEntryButton = PushButtonLE('Delete', 
                                 clicked=lambda: self.deleteEntry(self.createdTextEdits, 
                                                                       self.freqButtonGroup, 
                                                                       self.typeButtonGroup, 
                                                                       self.isLoraCheckbox.isChecked(),
                                                                       self.precisionButtonGroup))
        
        addAndDoneButton = PushButtonLE('Done', 
                                 clicked=lambda: self.doneWithEntry(self.createdTextEdits, 
                                                                       self.freqButtonGroup, 
                                                                       self.typeButtonGroup, 
                                                                       self.isLoraCheckbox.isChecked(),
                                                                       self.precisionButtonGroup,
                                                                       "add"))
        
        editAndDoneButton = PushButtonLE('Done', 
                                 clicked=lambda: self.doneWithEntry(self.createdTextEdits, 
                                                                       self.freqButtonGroup, 
                                                                       self.typeButtonGroup, 
                                                                       self.isLoraCheckbox.isChecked(),
                                                                       self.precisionButtonGroup,
                                                                       "edit"))


        if MainWindow.windowMode == "add":
            layout.addWidget(addButton,lableNameCounter+1,0,1,2)
            self.setWindowTitle('Live Telemetry Config Maker - Add')

            layout.addWidget(addAndDoneButton, lableNameCounter+2,0,1,2)
        else:
            layout.addWidget(editEntryButton,lableNameCounter+1,0,1,2)
            self.setWindowTitle('Live Telemetry Config Maker - Edit')

            layout.addWidget(editAndDoneButton, lableNameCounter+2,0,1,4)

        layout.addWidget(deleteEntryButton,lableNameCounter+1,2,1,2)


        self.setLayout(layout)

  
    def addConfiguration(self, textEdits, freqList, typeList, isLora, percisionList):
        # Error checks and if all data is valid add it to the dictionary

        global tabInstances, currentIndex

        msg = QMessageBox()

        errorReason = "Non-numeric data entered into numeric fields."

        try:
            dataType = str(typeList.checkedButton().dataType)

            jsonDictionary = {
                "N": textEdits[0].toPlainText(),
                "C": float(textEdits[1].toPlainText()),
                "P": int(percisionList.checkedButton().precision),
                "U": textEdits[2].toPlainText(), #7 characters max
                "F": int(freqList.checkedButton().frequencey),
                "T": int(dataType), #Technically a char but python don't got those 
                "L": int(isLora),
                "BO": int(textEdits[7].toPlainText()),
                "BL": int(textEdits[8].toPlainText()),
                "ID": int(textEdits[9].toPlainText(), 16) #CAN ID, convert from HEX to decimal
            }

            keys = ['TYPE','CN','GID','BS','CAN']
            for i in keys:
                if i not in tabInstances[currentIndex].userEnterData:
                    errorReason = "No file is loaded. Please make a new file or load one."
                    raise Exception

            if globalCarName == None:
                errorReason = "No car is currently being edited. Please add or edit one."
                raise Exception
            
            if len(textEdits[0].toPlainText()) > 32:
                errorReason = "Character limit exceeded for 'Name'."
                raise Exception

            if len(textEdits[2].toPlainText()) > 7:
                errorReason = "Character limit exceeded for 'Unit'."
                raise Exception

            if jsonDictionary["BO"] < 0 or jsonDictionary["BO"] > 64:
                errorReason = "Bit Offset outside of 0-64 range."
                raise Exception
            
            if jsonDictionary["BL"] < 1 or jsonDictionary["BL"] > 64:
                errorReason = "Bit Length outside of 1-64 range."
                raise Exception

            
            for i in tabInstances[currentIndex].userEnterData[globalCarName]:

                    if i.get("N") == jsonDictionary.get("N"):
                        errorReason = "This entry already exists, please check spelling or edit the entry."
                        raise Exception
            

            tabInstances[currentIndex].userEnterData[globalCarName].append(jsonDictionary)

            print(tabInstances)

            msg.setText("Successfully added configuration!")
            msg.setWindowTitle("Success")

            window.reloadText()
            window.update()
        
        except:
            msg.setText(errorReason)
            msg.setWindowTitle("Error")
 
        finally:
            msg.exec()


    def editEntry(self, textEdits, freqList, typeList, isLora, percisionList):
        # Performs the same error checks as add but replaces the selected option rather than adding a new one

        global tabInstances, currentIndex

        msg = QMessageBox()

        loopIndex = -1

        errorReason = "Non-numeric data entered into numeric fields."

        try:
            dataType = str(typeList.checkedButton().dataType)

            jsonDictionary = {
                "N": textEdits[0].toPlainText(),
                "C": float(textEdits[1].toPlainText()),
                "P": int(percisionList.checkedButton().precision),
                "U": textEdits[2].toPlainText(), #7 characters max
                "F": int(freqList.checkedButton().frequencey),
                "T": int(dataType), #Technically a char but python don't got those 
                "L": int(isLora),
                "BO": int(textEdits[7].toPlainText()),
                "BL": int(textEdits[8].toPlainText()),
                "ID": int(textEdits[9].toPlainText(), 16) #CAN ID, convert from HEX to decimal
            }

        
            keys = ['TYPE','CN','GID','BS','CAN']
            for i in keys:
                if i not in tabInstances[currentIndex].userEnterData:
                    errorReason = "No file is loaded. Please make a new file or load one."
                    raise Exception

            if globalCarName == None:
                errorReason = "No car is currently being edited. Please add or edit one."
                raise Exception
            
            if len(textEdits[0].toPlainText()) > 32:
                errorReason = "Character limit exceeded for 'Name'."
                raise Exception

            if len(textEdits[2].toPlainText()) > 7:
                errorReason = "Character limit exceeded for 'Unit'."
                raise Exception

            if jsonDictionary["BO"] < 0 or jsonDictionary["BO"] > 64:
                errorReason = "Bit Offset outside of 0-64 range."
                raise Exception
            
            if jsonDictionary["BL"] < 1 or jsonDictionary["BL"] > 64:
                errorReason = "Bit Length outside of 1-64 range."
                raise Exception

            # The loop to replace the items in the dictionary with the new inputs
            if globalCarName in tabInstances[currentIndex].userEnterData:
                for i in tabInstances[currentIndex].userEnterData[globalCarName]:

                    if tabInstances[currentIndex].userEnterData[globalCarName].index(i) == self.carLoopIndex:
                        
                        for j in tabInstances[currentIndex].userEnterData[globalCarName][self.carLoopIndex]:
                            #print(tabInstances[currentIndex].userEnterData[globalCarName][self.carLoopIndex][j])
                            tabInstances[currentIndex].userEnterData[globalCarName][self.carLoopIndex][j] = jsonDictionary[j]
                    

                msg.setText("Entry successfully edited!")
                msg.setWindowTitle("Success")

                window.reloadText()
                window.update()

            else:
                
                msg.setText(f"Entry not present, please check spelling or add the entry.\n{globalCarName}")
                msg.setWindowTitle("Error")
        
        except:
            msg.setText(errorReason)
            msg.setWindowTitle("Error")

        finally:
            msg.exec()

    def doneWithEntry(self, textEdits, freqList, typeList, isLora, percisionList, mode):

        if mode == "add":
            self.addConfiguration(textEdits, freqList, typeList, isLora, percisionList)
        else:
            self.editEntry(textEdits, freqList, typeList, isLora, percisionList)

        self.close()

    def deleteEntry(self, textEdits, freqList, typeList, isLora, percisionList):
        # Performs the same error checks as add but replaces the selected option rather than adding a new one

        global tabInstances, currentIndex

        msg = QMessageBox()

        errorReason = "Non-numeric data entered into numeric fields."

        try:
            dataType = str(typeList.checkedButton().dataType)

            jsonDictionary = {
                "N": textEdits[0].toPlainText(),
                "C": float(textEdits[1].toPlainText()),
                "P": int(percisionList.checkedButton().precision),
                "U": textEdits[2].toPlainText(), #7 characters max
                "F": int(freqList.checkedButton().frequencey),
                "T": int(dataType), #Technically a char but python don't got those 
                "L": int(isLora),
                "BO": int(textEdits[7].toPlainText()),
                "BL": int(textEdits[8].toPlainText()),
                "ID": int(textEdits[9].toPlainText(), 16) #CAN ID, convert from HEX to decimal
            }

        
            keys = ['TYPE','CN','GID','BS','CAN']
            for i in keys:
                if i not in tabInstances[currentIndex].userEnterData:
                    errorReason = "No file is loaded. Please make a new file or load one."
                    raise Exception

            if globalCarName == None:
                errorReason = "No car is currently being edited. Please add or edit one."
                raise Exception

            
            areYouSureButtons = QMessageBox(self)
            areYouSureButtons.setWindowTitle("Delete Entry?")
            areYouSureButtons.setText("Are you sure you want to delete this entry?")
            areYouSureButtons.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            areYouSureButtons.setIcon(QMessageBox.Question)

            verification = areYouSureButtons.exec()

            if verification == QMessageBox.Yes:
                # Entire loop works exactly as edit but replaces the reassignment with popping
                if globalCarName in tabInstances[currentIndex].userEnterData:
                    for i in tabInstances[currentIndex].userEnterData[globalCarName]:

                        if tabInstances[currentIndex].userEnterData[globalCarName].index(i) == self.carLoopIndex:
                            tabInstances[currentIndex].userEnterData[globalCarName].pop(self.carLoopIndex)
                        

                    msg.setText("Entry successfully deleted!")
                    msg.setWindowTitle("Success")

                    window.reloadText()
                    window.update()

                    self.close()

                else:
                    
                    msg.setText(f"Entry not present, please check spelling or add the entry.\n{globalCarName}")
                    msg.setWindowTitle("Error")

                msg.exec()
        
        except:
            msg.setText(errorReason)
            msg.setWindowTitle("Error")
            msg.exec()


    def setPlaceholderData(self,userData):
        # Takes the data set in OutputWindow and sets into the MainWindow
        
        global globalCarName

        print(userData)
        
        print(len(self.createdTextEdits))
        
        self.createdTextEdits[0].setPlainText(userData[globalCarName][self.carLoopIndex]["N"])

        self.createdTextEdits[1].setPlainText(str(userData[globalCarName][self.carLoopIndex]["C"]))

        self.createdTextEdits[2].setPlainText(userData[globalCarName][self.carLoopIndex]["U"])

        for i in self.precisionRadioButtons:
            if i.precision == userData[globalCarName][self.carLoopIndex]["P"]:
                i.setChecked(True)

        for i in self.freqRadioButtons:
            if i.frequencey == userData[globalCarName][self.carLoopIndex]["F"]:
                i.setChecked(True)

        for i in self.typesRadioButtons:
            if i.dataType == userData[globalCarName][self.carLoopIndex]["T"]:
                i.setChecked(True)

        for i in userData[globalCarName]:
            if i["L"] == 1:
                self.isLoraCheckbox.setChecked(True)


        self.createdTextEdits[7].setPlainText(str(userData[globalCarName][self.carLoopIndex]["BO"]))

        self.createdTextEdits[8].setPlainText(str(userData[globalCarName][self.carLoopIndex]["BL"]))

        self.createdTextEdits[9].setPlainText(hex(userData[globalCarName][self.carLoopIndex]["ID"]))



if __name__ == "__main__":
    # Executes the app and configures a few small settings

    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print('running in a PyInstaller bundle')
        stylesheet = loadFile(sys._MEIPASS + "/styles.qss")
    else:
        print('running in a normal Python process')
        stylesheet = loadFile("./dev/styles.qss")

    app.setStyleSheet(stylesheet)
    
    window = OutputWindow()
    
    window.show()

    sys.exit(app.exec())