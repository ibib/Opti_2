#!/usr/bin/env python3

import os, sys, time, datetime
import subprocess
import pyzdde.zdde as pyz
import configparser
from distutils.dir_util import copy_tree
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QListWidgetItem, QInputDialog
from PyQt5 import uic
import glob
import psutil
import platform

import pandas as pd

Ui_MainWindow, QtBaseClass = uic.loadUiType("gui.ui")

class MyApp(QMainWindow):

    def __init__(self):
        super(MyApp, self).__init__()
        
        '''Registrierung der Buttons'''
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.OpenZemaxButton.clicked.connect(self.OpenZemax)
        self.ui.SettingsMenu.clicked.connect(self.openSettings)
        self.ui.createSubfolders.clicked.connect(self.createSubfolders)
        self.ui.save_n_transfer.clicked.connect(self.save_n_transfer)
        self.ui.ListDir.clicked.connect(self.ListDir)
        self.ui.LoadSystemFrom.clicked.connect(self.LoadSystemFrom)
        self.ui.LoadSC.clicked.connect(self.LoadSC)
        self.ui.LoadNSC.clicked.connect(self.LoadNSC)
        self.ui.EditComment.clicked.connect(self.EditComment)
        self.ui.SaveModel.clicked.connect(self.Archive)
        self.ui.ConvertCad.clicked.connect(self.ConvertCad)
        self.ui.Help.clicked.connect(self.Help)
        #self.ui.Merit.clicked.connect(self.ManualOptimize)
        self.ui.Merit_auto.clicked.connect(self.AutoOptimize)
        self.ui.trace.clicked.connect(self.ray_trace)
        self.ui.save_detect.clicked.connect(self.save_detector_file)
        self.ui.delete_2.clicked.connect(self.delete_entries)
        self.getZemaxExec()
        self.showWorkingDir()  
        
        self.ListDir()
        
    def delete_entries(self):
        print('deletion started')
        selected_system = self.ui.listWidget.currentItem().text()
        splitted = str.split(selected_system)
        chosenArchive = splitted[0]
        print('Archive: ' + chosenArchive)
        
        #Empty live folder
        files = glob.glob(self.configDir + '/archiv/' + chosenArchive + '/*')
        for f in files:
            os.remove(f)
        print('Files removed')
        
        #Remove Archiv folder
        os.rmdir(self.configDir + '/archiv/' + chosenArchive)
        print('Folder removed')
        
        df = pd.read_csv(self.configDir + '/archiv/comments.csv', sep=';')
        
        print(df)
        df = df[df['a'] != int(chosenArchive)]
        
        
        '''Save to csv an refresh view'''
        df.to_csv(self.configDir + '/archiv/comments.csv', sep=';', index=False)
        self.ListDir()

    
    def ray_trace(self):
        print('start ray tracing')
        subprocess.call(["AHK\AutoHotkeyA32.exe",
                 "ray_trace.ahk"])
        
    
    def read_detector_power(self):
        
        #Read total Power from detector file
        
        file = open(self.configDir + '/live/' + 'detectorViewerFile.txt','r')
        dirty_string = file.read(1500)
        clean_list = dirty_string.replace('\x00', '').split('\n')
        total_power_string = clean_list[22]
        print(total_power_string)
        total_power_string_splitted = total_power_string.split(' ')
        watt_string = total_power_string_splitted[7]
        self.watt = float(watt_string.replace(',','.'))
        print('Power: ' + str(self.watt))        
        #Push power to gui
        
        self.ui.power_last_run.setText('Power last run: ' + str(self.watt))

    def save_detector_file(self):
        print('save detector file')
        #This function is a bit broken. It throws an error but still does it's job
        try:
            self.link = pyz.createLink()
            self.link.zGetDetectorViewer()
            self.link.close()
        except:
            self.link.close()
        time.sleep(4)
        print('Saving detectorFile finished')
        
        self.read_detector_power()
        
        
        
        
    
    #Warining! Function should only be called one time per replacement_name.
    # =>Double replacement    
    def set_ray_file(self, ray_file_name, replacement_name):
        self.link = pyz.createLink()
        
        #Check if in SC-Mode
        if not self.link._zGetMode()[0] == 1:
            self.link.close()
            QMessageBox.about(self, "Title", "Function is only available in NSC-Mode.")
            return None
        
        for i in range(20):
            comment = self.link.zGetNSCProperty(1,i,1,1)
            print(comment)
            if comment == replacement_name:
                print('replacement position found')
                z_position = self.link.zGetNSCPosition(1,i)[2]
                self.link.zSetNSCProperty(1,i,1,0, value='NSC_SFIL')
                print('type replaced')
                print('ray_file_name: ' + str(type(ray_file_name)))
                self.link.zSetNSCProperty(1,i,1,1, value=str(ray_file_name))
                self.link.zSetNSCPosition(1,i,3,z_position)
                self.link.zPushLens()
                break
        self.link.close()

        
    def set_ray_files(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        checkbox_one = self.config.get('RAYFIELD', 'one_checked', fallback='')
        field_one = self.config.get('RAYFIELD', 'one', fallback='')
        if checkbox_one == 'True':
            self.set_ray_file(ray_file_name=field_one, replacement_name='Field 1')
        
        checkbox_two = self.config.get('RAYFIELD', 'two_checked', fallback='')
        field_two = self.config.get('RAYFIELD', 'two', fallback='')
        if checkbox_two == 'True':
            self.set_ray_file(ray_file_name=field_two, replacement_name='Field 2')
            
        checkbox_three = self.config.get('RAYFIELD', 'three_checked', fallback='')
        field_three = self.config.get('RAYFIELD', 'three', fallback='')
        if checkbox_three == 'True':
            self.set_ray_file(ray_file_name=field_three, replacement_name='Field 3')
            
        checkbox_four = self.config.get('RAYFIELD', 'four_checked', fallback='')
        field_four = self.config.get('RAYFIELD', 'four', fallback='')
        if checkbox_four == 'True':
            self.set_ray_file(ray_file_name=field_four, replacement_name='Field 4')
    
    
    def AutoOptimize(self):
        print('Auto optimize started')
        self.read_detector_power()
        self.ManualOptimize(auto_value = self.watt)
        
    
    def ManualOptimize(self, auto_value = 'False'):
        
        '''Zemax Verbindung aufbauen'''
        self.link = pyz.createLink()

        #Check if in SC-Mode
        if not self.link._zGetMode()[0] == 0:
            self.link.close()
            QMessageBox.about(self, "Title", "Function is not available in NSC-Mode.")
            return None
        
        self.link.close()
        
        self.delete_old_merit()
        print('deleteMFO ended')
        
        self.link = pyz.createLink()
        
        '''Check Merit Function for Signal'''
        optimizer_row = ''
        for i in range(1,300):
            comment = self.link.zGetOperand(row=i, column=2)
            print(comment)
            if comment == 'OPTIMIZER':
                print('OPTIMIZER FOUND')
                print('row: ' + str(i))
                optimizer_row = i
                break

        optimizer_row_end = ''
        for j in range(1,300):
            comment = self.link.zGetOperand(row=j, column=2)
            if comment == 'ENDOPTIMIZER':
                print('ENDOPTIMIZER FOUND')
                print('row_end: ' + str(j))
                optimizer_row_end = j
                break          
        
        if (optimizer_row == '') or (optimizer_row_end == ''):
            print('OPTIMIZER row not found')
            QMessageBox.about(self, "Error", "'OPTIMIZER' row not found.")
            return
        
        #Anzahl der Meritfunctions die betrachtet werden
        merits = 1
        for i in range(merits):
            self.link.zInsertMFO(optimizer_row+1)
        
        
        self.link.zSetOperand(row=(optimizer_row+1), column=1, value='ZPLM')
        
        prog = 17 #Macro has the name 'ZPL17.ZPL'
        self.link.zSetOperand(row=(optimizer_row+1), column=2, value=prog)
        
        data = 0 #Valueposition 0 is read from the macro
        self.link.zSetOperand(row=(optimizer_row+1), column=3, value=data)
        
        
        weight = str(self.ui.SpinBox_Weight.value())
        self.link.zSetOperand(row=(optimizer_row+1), column=9, value=weight)
        
        Target = str(self.ui.SpinBox_Target.value())
        self.link.zSetOperand(row=(optimizer_row+1), column=8, value=Target)
        
        print(str(type(auto_value)))
#        if auto_target == False:
#            print('auto_target empty')
#            Target = str(self.ui.SpinBox_Value.value())
#            self.link.zSetOperand(row=(optimizer_row+1), column=4, value=Target)
        if str(type(auto_value)) == "<class 'float'>" :
            print('auto_target: ' + str(auto_value))
            Value = str(1/auto_value)
            self.link.zSetOperand(row=(optimizer_row+1), column=4, value=Value)
        
        self.link.zPushLens()
        self.link.close()
        
        subprocess.call(["AHK\AutoHotkeyA32.exe",
                     "optimize.ahk"])
    
        time.sleep (5)
        
        
        
    def delete_old_merit(self):
        '''Zemax Verbindung aufbauen'''
        self.link = pyz.createLink()
        
        print('called deleteMFO')
        optimizer_row = ''
        for i in range(1,300):
            comment = self.link.zGetOperand(row=i, column=2)
            if comment == 'OPTIMIZER':
                print('OPTIMIZER FOUND')
                print('row: ' + str(i))
                optimizer_row = i
                break

        optimizer_row_end = ''
        for j in range(1,300):
            comment = self.link.zGetOperand(row=j, column=2)
            if comment == 'ENDOPTIMIZER':
                print('ENDOPTIMIZER FOUND')
                print('row_end: ' + str(j))
                optimizer_row_end = j
                break
        self.link.close()
           
        if (optimizer_row == '') or (optimizer_row_end == ''):
            print('OPTIMIZER row not found')
            QMessageBox.about(self, "Error", "'OPTIMIZER' row not found.")
            return
        elif (optimizer_row_end - optimizer_row) >= 2:
            self.link = pyz.createLink()
            self.link.zDeleteMFO(optimizer_row +1 )
            self.link.zPushLens()
            self.link.close()
            self.delete_old_merit()
            
        print('deleteMFO end')
        return

    def ConvertCad(self):
        
        '''Zemax Verbindung aufbauen'''
        self.link = pyz.createLink()

        #Check if in SC-Mode
        if not self.link._zGetMode()[0] == 1:
            self.link.close()
            QMessageBox.about(self, "Title", "Function is only available in NSC-Mode.")
            return None
        
        '''Save current NSC-Model'''
        time.sleep(0.5)
        success = self.link.zSaveFile(self.configDir + '/live' + '/lens-NSC.zmx')
        time.sleep(0.5)
        self.link.close()
        
        if success == 0:
            print('SUCCES-File saved')
        else:
            print('ERROR-File not saved')
        
        '''Execute userfunction. Saves Step-file in Live folder'''
        '''Win 7 and Win 10 have a different Save Dialoge. One more Tab is needed'''
        if platform.release() == '7':
            subprocess.call(["AHK\AutoHotkeyA32.exe",
                     "Export_to_CAD_7.ahk",
                     self.configDir + '/live/', 'lens-STEP.stp'])
        elif platform.release() == '10':
            subprocess.call(["AHK\AutoHotkeyA32.exe",
                     "Export_to_CAD_10.ahk",
                     self.configDir + '/live/', 'lens-STEP.stp'])
        else:
            QMessageBox.about(self, "Error", "OS not supported.")
    
        self.getInventorExec()
        subprocess.Popen([self.InventorPath, self.configDir + '/live' + '/lens-STEP.stp'])

        
    def EditComment(self):
        print('Comment edit')
        text, ok = QInputDialog.getText(self, 'Edit comment dialog', 'Enter comment:')
        
        if ok:            
            self.saveComment(text=text, position='selection')

    def AddComment(self):
        print('Add comment')
        text, ok = QInputDialog.getText(self, 'Add comment dialog', 'Enter comment:')
        
        if ok:            
            self.saveComment(text=text, position='end')
         
    def saveComment(self, text, position):
        
        '''Feststellen an welcher Stelle Kommentar geschrieben werden soll'''
        if position == 'selection':
            choosen_line = self.ui.listWidget.currentItem().text()
            def extract_num(string):
                splitted = str.split(string)
                return int(splitted[0])        
            choosen_system = extract_num(choosen_line)
        if position == 'end':
            choosen_system = self.getArchiveNumber()            
        
        
        df = pd.read_csv(self.configDir + '/archiv/comments.csv', sep=';')
        #Wenn df nummer nicht enthält => Append
        if choosen_system not in df['a']:
            print('Comment nicht vorhanden')
            df = df.append(pd.Series([choosen_system, text], index=['a', 'b']), ignore_index=True)
        #Wenn df nummer enthält => change
        df.loc[df['a'] == choosen_system, ['b']] = text
        
        '''Save to csv an refresh view'''
        df.to_csv(self.configDir + '/archiv/comments.csv', sep=';', index=False)
        self.ListDir()
    
    def LoadSC(self):
        #Check if Zemax is running
        if self.isZemaxRunning():
            QMessageBox.about(self, "Title", "Function is not available while ZEMAX is running.")
            return None
        subprocess.Popen([self.ZemaxPath, self.configDir + '/live' + '/lensfile.zmx'])
        
    def LoadNSC(self):
        #Check if Zemax is running
        if self.isZemaxRunning():
            QMessageBox.about(self, "Title", "Function is not available while ZEMAX is running.")
            return None
        subprocess.Popen([self.ZemaxPath, 
                          self.configDir + '/live' + '/lens-NSC.zmx'])

    def LoadSystemFrom(self):
        #Check if Zemax is running
        if self.isZemaxRunning():
            QMessageBox.about(self, "Title", "Function is not available while ZEMAX is running.")
            return None
        current_system = self.ui.listWidget.currentItem().text()
        splitted = str.split(current_system)
        chosenArchive = splitted[0]
        #Archive system in live folder
        self.Archive()
        
        #Empty live folder
        files = glob.glob(self.configDir + '/live' + '/*')
        for f in files:
            os.remove(f)
            
        #Copy from archive folder
        destDirectory = self.configDir + '/live'
        fromDirectory = self.configDir + '/archiv/' + str(chosenArchive)
        copy_tree(fromDirectory, destDirectory)
        
        self.ListDir()

    '''Lists all folders with mtime in the archive folder'''
    def ListDir(self):
        if os.path.isdir(self.configDir) == False:
            return
        if os.path.exists(self.configDir + '/archiv') == False:
            return
        '''Load comment file'''
        df = pd.read_csv(self.configDir + '/archiv/comments.csv', sep=';')
        
        self.ui.listWidget.clear()
        for i in os.listdir(os.path.join(self.configDir + '/archiv')):
            #If Objekt in archive folde is not an folder => skip (see comments.csv)
            if os.path.isdir(self.configDir + '/archiv/' + str(i)) == False:
                continue
            
            '''Filter comments from csv file'''
            comment_line = df.loc[df['a'] == int(i), 'b']
            if comment_line.size == 0:
                comment = ''
            else:
                comment = comment_line.iloc[0]
                print(comment)
            
            #Extrahierung und Formatierung der mtime
            stat = os.stat(os.path.join(self.configDir + '/archiv/' + str(i)))
            date = datetime.datetime.fromtimestamp(stat.st_mtime)
            dt = '{0:%Y-%m-%d %H:%M:%S}'.format(date)
            
            '''Ein wenig hübscher formatiert'''
            if int(i) < 10:
                self.ui.listWidget.addItem(ListWidgetItem(' {:12}{:25}{}'.format(i, str(dt), str(comment))))
            else:
                self.ui.listWidget.addItem(ListWidgetItem('{:12}{:25}{}'.format(i, str(dt), str(comment))))
        self.showWorkingDir()

    def getArchiveNumber(self):
        ''''Scans for int foldernames and returns highest number'''
        folders = filter(lambda x: os.path.isdir(os.path.join((self.configDir + '/archiv'), x)),
                         os.listdir((self.configDir + '/archiv')))
        number = 0
        for i in folders:
            if i.isdigit():
                if int(i) > number:
                    number = int(i)
        return number

    def save_n_transfer(self):
        #Save File
        '''Zemax Verbindung aufbauen'''
        self.link = pyz.createLink()

        #Check if in SC-Mode
        if not self.link._zGetMode()[0] == 0:
            self.link.close()
            QMessageBox.about(self, "Title", "Function is not available in NSC-Mode.")
            return None

        time.sleep(1)
        print('saving started')
        success = self.link.zSaveFile(self.configDir + '/live' + '/lensfile.zmx')
        print('saving finished')
        time.sleep(1)
        
        self.link.close()
        if success == 0:
            print('SUCCES-File saved')
        else:
            print('ERROR-File not saved')
        self.Archive()
        #Transfer System to NSC-Group
        '''It is not supported by pyzdde to Convert from SC to NSC by Python-API'''
        '''The solution is to replace the user by a script.'''
        subprocess.call(["AHK\AutoHotkeyA32.exe",
                         "Convert_to_NSGroup.ahk",
                         self.configDir + '/live'+ '/lens-NSC.zmx'])
        time.sleep(10)
        
        self.set_ray_files()
        

    def Archive(self):
        #Copy to archiv
        #Create new archiv folder
        archiv_number = 1 + self.getArchiveNumber()
        os.mkdir(self.configDir + '/archiv/' + str(archiv_number))

        #Copy to archive folder
        fromDirectory = self.configDir + '/live'
        destDirectory = self.configDir + '/archiv/' + str(archiv_number)
        copy_tree(fromDirectory, destDirectory)
        
        self.AddComment()



    def createSubfolders(self):
        print('Subfolder creation started')
        self.showWorkingDir()
        live = os.path.isdir(self.configDir + '/live')
        archiv = os.path.isdir(self.configDir + '/archiv')
        comments = os.path.isfile(self.configDir + '/archiv/comments.csv')
        if not live:
            print('no "live"')
            os.mkdir(self.configDir + '/live')
        if not archiv:
            print('no "archiv"')
            os.mkdir(self.configDir + '/archiv')
        if not comments:
            print('no comments file')
            df = pd.DataFrame({'a':[], 'b':[]})
            df.to_csv(self.configDir + '/archiv/comments.csv', sep=';', index=False)

    def OpenZemax(self):
        print(self.ZemaxPath)
        subprocess.Popen([self.ZemaxPath])

    def showWorkingDir(self):
        self.ui.label.setText('Working Dir not set or invalid')
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        print(self.config.sections())
        self.configDir = self.config.get('DEFAULT', 'WorkingDir', fallback='Working Dir not set')
        if os.path.isdir(self.configDir) == False:
            self.ui.label.setText('Working Dir not set or invalid')
            return        
        self.ui.label.setText(self.configDir)

    def isZemaxRunning(self):
        isRunning = "OpticStudio.exe" in (p.name() for p in psutil.process_iter())
        return isRunning
    
    def getZemaxExec(self):
        self.ZemaxPath = configparser.ConfigParser()
        self.ZemaxPath.read("config.ini")
        self.ZemaxPath = self.ZemaxPath.get('ZEMAX', 'zemaxexec', fallback='C:/')
        
    def getInventorExec(self):
        self.InventorPath = configparser.ConfigParser()
        self.InventorPath.read("config.ini")
        self.InventorPath = self.InventorPath.get('INVENTOR', 'inventorexec', fallback='C:/')
        
    def openSettings(self):
        print('Settings are being opened')
        dialog = Settings(self)
        dialog.show()
        
    def Help(self):
        print('Help is being opened')
        dialog = Help(self)
        dialog.show()

#Function override to sort entries in the GUI
class ListWidgetItem(QListWidgetItem):
    def __lt__(self, other):
        
        def extract_num(string):
            splitted = str.split(string)
            return splitted[0]
            
        if (int(extract_num(self.text())) < int(extract_num(other.text()))):
            return True
        else:
            return False

#Settings dialoge
class Help(QMainWindow):
    def __init__(self, parent=None):
        super(Help, self).__init__(parent)
        Help_Window, QtBaseClass = uic.loadUiType("help.ui")
        self.ui = Help_Window()
        self.ui.setupUi(self)
        


#Settings dialoge
class Settings(QMainWindow):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        Settings_Window, QtBaseClass = uic.loadUiType("settings.ui")
        self.ui = Settings_Window()
        self.ui.setupUi(self)
        
        self.ui.ChooseWorkingDir.clicked.connect(self.ChooseWorkingDir)
        self.ui.ChooseZemaxPath.clicked.connect(self.ChooseZemaxPath)
        self.ui.ChooseInventorPath.clicked.connect(self.ChooseInventorPath)
        
        self.ui.RayFieldCheck1.stateChanged.connect(self.Box_1)
        self.ui.RayFieldCheck2.stateChanged.connect(self.Box_2)
        self.ui.RayFieldCheck3.stateChanged.connect(self.Box_3)
        self.ui.RayFieldCheck4.stateChanged.connect(self.Box_4)
        
        self.ui.SaveRayFiles.clicked.connect(self.SaveRayFiles)
        
        self.showWorkingLabels()
        
        self.read_checkboxes()
        self.Box_1()
        self.Box_2()
        self.Box_3()
        self.Box_4()
        
    def read_checkboxes(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        checkbox_one = self.config.get('RAYFIELD', 'one_checked', fallback='')
        print('state checkbox_one' + checkbox_one)
        
        if checkbox_one == 'True':
            print('meepmeep')
            self.ui.RayFieldCheck1.setChecked(True)
        
        checkbox_two = self.config.get('RAYFIELD', 'two_checked', fallback='')
        if checkbox_two == 'True':
            self.ui.RayFieldCheck2.setChecked(True)
            
        checkbox_three = self.config.get('RAYFIELD', 'three_checked', fallback='')
        if checkbox_three == 'True':
            self.ui.RayFieldCheck3.setChecked(True)
        
        checkbox_four = self.config.get('RAYFIELD', 'four_checked', fallback='')
        if checkbox_four == 'True':
            self.ui.RayFieldCheck4.setChecked(True)
        
    def SaveRayFiles(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.config['RAYFIELD'] = {'one' : self.ui.RayField1.text(),
                                   'one_checked' : self.ui.RayFieldCheck1.isChecked(),
                                   'two' : self.ui.RayField2.text(),
                                   'two_checked' : self.ui.RayFieldCheck2.isChecked(),
                                   'three': self.ui.RayField3.text(),
                                   'three_checked' : self.ui.RayFieldCheck3.isChecked(),
                                   'four': self.ui.RayField4.text(),
                                   'four_checked' : self.ui.RayFieldCheck4.isChecked(),}
        
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        self.showWorkingLabels()
        
    
    def Box_1(self):
        if self.ui.RayFieldCheck1.isChecked():
            print('RayFieldCheck1 checked')
            self.ui.RayField1.setEnabled(True)
            
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')
            print(self.config.sections())
            self.Field1 = self.config.get('RAYFIELD', 'one', fallback='')
            self.ui.RayField1.setText(self.Field1)
            
        else:
            print('RayFieldCheck1 unchecked')
            self.ui.RayField1.setEnabled(False)
            
    def Box_2(self):
        if self.ui.RayFieldCheck2.isChecked():
            print('RayFieldCheck2 checked')
            self.ui.RayField2.setEnabled(True)
            
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')
            print(self.config.sections())
            self.Field2 = self.config.get('RAYFIELD', 'two', fallback='')
            self.ui.RayField2.setText(self.Field2)
            
        else:
            print('RayFieldCheck2 unchecked')
            self.ui.RayField2.setEnabled(False)
            
    def Box_3(self):
        if self.ui.RayFieldCheck3.isChecked():
            print('RayFieldCheck3 checked')
            self.ui.RayField3.setEnabled(True)
            
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')
            print(self.config.sections())
            self.Field3 = self.config.get('RAYFIELD', 'three', fallback='')
            self.ui.RayField3.setText(self.Field3)
            
        else:
            print('RayFieldCheck3 unchecked')
            self.ui.RayField3.setEnabled(False)
            
    def Box_4(self):
        if self.ui.RayFieldCheck4.isChecked():
            print('RayFieldCheck4 checked')
            self.ui.RayField4.setEnabled(True)
            
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')
            print(self.config.sections())
            self.Field4 = self.config.get('RAYFIELD', 'four', fallback='')
            self.ui.RayField4.setText(self.Field4)
            
        else:
            print('RayFieldCheck3 unchecked')
            self.ui.RayField3.setEnabled(False)
        
    def showWorkingLabels(self):
        self.ui.label.setText('Working Dir not set or invalid')
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        print(self.config.sections())
        self.configDir = self.config.get('DEFAULT', 'WorkingDir', fallback='Working Dir not set')
        self.ui.label.setText(self.configDir)
        
        self.ZemaxPath = self.config.get('ZEMAX', 'zemaxexec', fallback='ZEMAX Path not set')
        self.ui.ZemaxPath.setText(self.ZemaxPath)
        
        self.InventorPath = self.config.get('INVENTOR', 'inventorexec', fallback='Inventor Path not set')
        self.ui.InventorPath.setText(self.InventorPath)
    
    def ChooseZemaxPath(self):
        path = QFileDialog.getOpenFileName(self,"Zemax Path", "","All Files (*);;Executable (*.exe)")[0]
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.config['ZEMAX'] = {'zemaxexec' : path}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        self.showWorkingLabels()
        
    def ChooseInventorPath(self):
        path = QFileDialog.getOpenFileName(self,"Inventor Path", "","All Files (*);;Executable (*.exe)")[0]
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.config['INVENTOR'] = {'inventorexec' : path}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        self.showWorkingLabels()
        print(path)
        
    def ChooseWorkingDir(self):
        file = QFileDialog.getExistingDirectory(None,
                                                'Open working directory',
                                                None,
                                                QFileDialog.ShowDirsOnly)
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.config['DEFAULT'] = {'WorkingDir' : file}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        self.showWorkingLabels()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
