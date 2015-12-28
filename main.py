#!/home/camaro/anaconda/bin/python
import sys
import os
from PySide import QtGui, QtCore
import tabbed_design
import login_window

from importserial import load_serial_ports
import serial


from read_graph_tables import calc_att_by_category, calc_att_by_category_alldept, calc_num_all_dept, plot_service_daily
from mpldatacursor import datacursor
import calendar

import MySQLdb as mdb

import datetime
from datetime import date, time
from time import strftime
import time as t

print "Start Time:",datetime.datetime.now()

isAdmin = False

class Login(QtGui.QDialog, login_window.Ui_Dialog):
    def __init__(self):
#         QtGui.QDialog.__init__(self)
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.pushButton_login.clicked.connect(self.handleLogin)
        
        self.lineEdit_username.setText("lwcadmin")
        self.lineEdit_password.setText("lwcadmin")
        
        self.setWindowIcon(QtGui.QIcon("icon/disp_icon.png"))
        self.loginlogo.setPixmap(QtGui.QPixmap("icon/disp_icon.png" ).scaledToHeight(100))
        
#         self.label_picture.setPixmap(QtGui.QPixmap("icon/unknown_profile.png" ).scaledToHeight(160))
        
        self.count = 11
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.countdown)
        self.timer.start(1000)
         
    def handleLogin(self):
        if (self.lineEdit_username.text() == 'lwcadmin' and self.lineEdit_password.text() == 'lwcadmin'):
            self.accept()
            global isAdmin
            isAdmin = True
            
        elif (self.lineEdit_username.text() == 'lwcuser' and self.lineEdit_password.text() == 'lwcuser'):
            self.accept()
            
        else:
            QtGui.QMessageBox.warning(
                self, 'Error', 'Bad user or password')
        
    def countdown(self):
        self.count-=1 
#         print self.count
        self.loginlabel.setText("Login as lwcuser in "+str(self.count)+" seconds")
        if self.count <= 0:
            self.pushButton_login.click()

class AttTracker(QtGui.QMainWindow, tabbed_design.Ui_LWCAttendanceTaker):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        self.setWindowIcon(QtGui.QIcon('icon/disp_icon.png'))
        self.label_picture.setPixmap(QtGui.QPixmap("icon/unknown_profile.png" ).scaledToHeight(160))

        self.actionQuit.triggered.connect(self.close_application)
        self.actionQuit.setStatusTip("Leave the application")
        self.actionQuit.setShortcut("Ctrl+Shift+Q")
         
        self.actionConnect.triggered.connect(self.connect_serial_port)
        self.actionConnect.setStatusTip("Connect to serial port")
        self.actionConnect.setShortcut("Ctrl+Shift+C")
        
        self.actionConnect_to_home.triggered.connect(self.connecttohome)
        self.actionConnect_to_home.setStatusTip("Connect to home server")
        self.actionConnect_to_home.setShortcut("Ctrl+Shift+X")
        
        # set max date for attendnace marking
        self.calendarWidget.setMaximumDate(datetime.datetime.now())
        self.home()
        
        # show maximized
#         self.showMaximized()
        self.showFullScreen()

        if not isAdmin:
            print "Logged in as lwcuser"
            self.tab_widget_overall.setTabEnabled(0, False)
            self.tab_widget_overall.setTabEnabled(2, False)
            self.tab_widget_overall.setTabEnabled(3, False)
        
        
    def home(self):                        
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        self.statusbar.showMessage("Connect to the RFID reader and database to start")
        
#         self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        self.pushButton_quit.clicked.connect(self.close_application)
        self.pushButton_connect.clicked.connect(self.connect_serial_port)
        self.pushButton_refresh.clicked.connect(self.load_serial_port_2)
        self.pushButton_disconnect.clicked.connect(self.disconnect_serial_port)
        self.pushButton_disconnect.setEnabled(False)
        
        # plotting stuff
        self.pushButton_plot.clicked.connect(self.plot_dept_stats)
        self.pushButton_plot.clicked.connect(self.plot_all_service)
        
        # serial port stuff
        self.load_serial_port_2()
        
        # attendance marking and view stuff
        self.pushButton_submit.clicked.connect(self.submit_attendance)
        self.pushButton_delete.clicked.connect(self.delete_attendance)
        self.pushButton_viewatt.clicked.connect(self.viewAttendance)
        self.comboBox_admintab_name.currentIndexChanged.connect(self.load_att_marking_pic)
        
        
        self.comboBox_admintab_dept.currentIndexChanged.connect(self.load_admin_name_status_combobox)
        
        # table view stuffs
        self.pushButton_loadmemberdetails.clicked.connect(self.loadMembersTableView)
        
        self.pushButton_next_graph_ss.clicked.connect(lambda: self.gotonextpage(self.stackedWidget_ss))
        self.pushButton_previous_graph_ss.clicked.connect(lambda: self.gotoprevpage(self.stackedWidget_ss))
        
        self.pushButton_next_graph_ws.clicked.connect(lambda: self.gotonextpage(self.stackedWidget_ws))
        self.pushButton_previous_graph_ws.clicked.connect(lambda: self.gotoprevpage(self.stackedWidget_ws))
        
        self.pushButton_next_graph_fpm.clicked.connect(lambda: self.gotonextpage(self.stackedWidget_fpm))
        self.pushButton_previous_graph_fpm.clicked.connect(lambda: self.gotoprevpage(self.stackedWidget_fpm))
        
        self.pushButton_next_graph_ds.clicked.connect(lambda: self.gotonextpage(self.stackedWidget_ds))
        self.pushButton_previous_graph_ds.clicked.connect(lambda: self.gotoprevpage(self.stackedWidget_ds))
        
#         self.tableWidget.itemChanged.connect(self.printChanged)
        self.pushButton_commitchange.clicked.connect(self.commit_member_details)
        
        # connect db stuffs
        self.pushButton_dbconnect.clicked.connect(self.connectDB)
        self.pushButton_connecttohome.clicked.connect(self.connecttohome)
        self.databaseHostLineEdit.returnPressed.connect(self.connectDB)
        
        # add new members stuff
        self.pushButton_addmember.clicked.connect(self.add_new_member)
        
        # personal profile stuff
        self.comboBox_profiledept.currentIndexChanged.connect(self.load_profile_namecombobox)
        self.comboBox_profilename.currentIndexChanged.connect(self.load_profile)
        
        # view events
        self.pushButton_viewnewevent.clicked.connect(self.viewEvents)
#         self.comboBox_viewevent.addItem("All Events")

        # add events
        self.comboBox_addnewevent.addItem("Others")
        self.pushButton_addnewevent.clicked.connect(self.addevents)
        
        # Enable this line for reader pc. This line simulates a user click on these buttons
        self.pushButton_connect.click()
        self.pushButton_connecttohome.click()
        
        # default check for attendance radio button
        self.radioButton_present.setChecked(True)
        
        self.backgroundpic.lower()

         
    def close_application(self):
        print "Thanks for using me!"
        print "End Time:",datetime.datetime.now()
        sys.exit()
    
    def load_serial_port_2(self):
        self.comboBox_serialPort.clear()
        self.comboBox_serialPort.addItems(load_serial_ports())
    
    def disconnect_serial_port(self):
        self.arduino.close()
        print "Disconnected"
        self.home()
        
    def connect_serial_port(self):
        self.arduino = serial.Serial(str(self.comboBox_serialPort.currentText()), 9600, timeout=0, writeTimeout=0)
        
        # Check If there is connection
        if self.arduino.isOpen():
            print "Connected to", str(self.comboBox_serialPort.currentText())
#             self.timer = core.QTimer(self)
#             self.timer.timeout.connect(self.v2_scan_id)
#             self.timer.start(300)
            self.pushButton_connect.setStyleSheet("background-color: lightgreen")
            self.pushButton_connect.setText("Connected!")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            self.statusBar().showMessage("Connected to %s" % str(self.comboBox_serialPort.currentText()))
            self.pushButton_disconnect.setEnabled(True)
            
#             self.connectDB()


####################################################################################################################################################    
    def addevents(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        # search for duplicate, if no duplicate, add events, else prompt user
        # currently only support 1 extra event per day due to restriction in the mysql table
        cur.execute("SELECT * FROM event_test WHERE event_name='%s' AND event_date='%s' AND event_type='%s' " % (str(self.lineEdit_addnewevent.text()), self.calendarWidget_addevent.selectedDate().toString("yyyy-MM-dd"), self.comboBox_addnewevent.currentText()))
        duplicate = cur.fetchall()
        
        if duplicate == (): 
            cur.execute("INSERT INTO event_test VALUES (NULL, '%s', '%s', '%s')" % (str(self.lineEdit_addnewevent.text()), self.calendarWidget_addevent.selectedDate().toString("yyyy-MM-dd"), self.comboBox_addnewevent.currentText()))
            db.commit()
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("Event added! Details: %s, @ %s, %s" %(str(self.lineEdit_addnewevent.text()), self.calendarWidget_addevent.selectedDate().toString("yyyy-MM-dd"), self.comboBox_addnewevent.currentText()))
        
        else:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("Duplicate found! Create different event")
        
        db.close()
    
    def viewEvents(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        cur.execute("SELECT * FROM event_test WHERE event_date='%s' " % (self.calendarWidget_viewnewevent.selectedDate().toString("yyyy-MM-dd")))
        events = cur.fetchall()
        if events == ():
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("No such event. Check event details!")
        else:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("Event loaded!")

            
            self.tableWidget_viewevent.horizontalHeader().setStretchLastSection(True)
            self.tableWidget_viewevent.setRowCount(len(events))
            self.tableWidget_viewevent.setColumnCount(3)
            self.tableWidget_attendee.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            self.tableWidget_viewevent.setHorizontalHeaderLabels(["Type", "Date", "Name" ])
            
            for rownumber, rowvalue in enumerate(events):
                self.tableWidget_viewevent.setItem(rownumber,2,QtGui.QTableWidgetItem("%s" %rowvalue[1]))
                self.tableWidget_viewevent.setItem(rownumber,1,QtGui.QTableWidgetItem("%s" %rowvalue[2]))
                self.tableWidget_viewevent.setItem(rownumber,0,QtGui.QTableWidgetItem("%s" %rowvalue[3]))
        
        

        db.close()
            
####################################################################################################################################################    

    def add_new_member(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        if self.nameLineEdit.text(): 
            cur.execute("INSERT INTO members_list (chi_name, eng_name, dept, gender, membership_status, dob, passing_date, contact_num) VALUES ('%s', '%s', '%s', '%s', 'Active', '%s', '%s', '%s') " 
                        % (self.nameLineEdit.text(), self.englishNameLineEdit.text(), self.comboBox_addmemberdept.currentText(), self.comboBox_addmembergender.currentText(), self.calendarWidget_newmember_dob.selectedDate().toString("yyyy-MM-dd"), self.calendarWidget_newmember_passing.selectedDate().toString("yyyy-MM-dd"), self.contactNum_lineEdit.text() ))
            db.commit()
             
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("New member added!")
        else:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("Name cant be empty!")


####################################################################################################################################################    

    def connecttohome(self):
        self.databaseHostLineEdit.setText("127.0.0.1")
        self.pushButton_connecttohome.setDisabled(True)
        self.connectDB()
        
    
    def connectDB(self):
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        
        # start the clock once the connect db has triggered
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Time)
        self.timer.timeout.connect(self.Date)
        self.timer.timeout.connect(self.updateEventStatus)
        self.timer.start(1000)
        self.lcdNumber_time.setDigitCount(8)
        self.lcdNumber_time.display(strftime("%H"+":"+"%M"+":"+"%S"))
        self.label_dynamic_date.setText(strftime("%Y"+" "+"%B"+" "+"%d"+", "+"%A"))
        
        try:
            db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
            
            if db.open:
                self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
                self.statusbar.showMessage("System online!")
                self.pushButton_dbconnect.setText("Connected to database at %s" % str(self.databaseHostLineEdit.text()))
                self.pushButton_dbconnect.setStyleSheet("background-color: lightgreen")
                self.databaseHostLineEdit.setDisabled(True)
            
                self.load_all_deptcombobox()
                self.load_admin_eventcombobox()
                self.load_admin_name_status_combobox()
                self.load_profile_deptcombobox()
                self.load_profile_namecombobox()
                 
                self.comboBox_monthselector.clear()
                self.comboBox_yearselector.clear()
                self.comboBox_monthselector.addItems([str(i) for i in range(1,13)])
                self.comboBox_yearselector.addItems([str(i) for i in range(2015,2024)])
                 
                # set default value of the month combo box to the current month 
                index_month = self.comboBox_monthselector.findText(datetime.datetime.date(datetime.datetime.now()).strftime("%m"), QtCore.Qt.MatchFixedString)
                self.comboBox_monthselector.setCurrentIndex(index_month)
                  
                index_year = self.comboBox_yearselector.findText(datetime.datetime.date(datetime.datetime.now()).strftime("%Y"), QtCore.Qt.MatchFixedString)
                self.comboBox_yearselector.setCurrentIndex(index_year)
                
#                 self.plot_all_service()
                self.plot_dept_stats()
                
                self.timer = QtCore.QTimer(self)
                self.timer.timeout.connect(self.v2_scan_id)
                self.timer.start(300)
            
        except:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("Database cannot be reached, please re-enter")
            self.pushButton_dbconnect.setText("Connection error")
            self.pushButton_dbconnect.setStyleSheet("background-color: red")
            
        

####################################################################################################################################################    
    def loadMembersTableView(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()   
        
        self.statusbar.showMessage("Loaded database")
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        
        if self.checkBox_inactivememebrs.isChecked():
            if self.comboBox_viewtabledept.currentText() == "ALL DEPT":
                cur.execute("SELECT * FROM members_list ORDER BY dept")
            else: 
                cur.execute("SELECT * FROM members_list WHERE dept='%s' ORDER BY dept" % self.comboBox_viewtabledept.currentText())
        else:
            if self.comboBox_viewtabledept.currentText() == "ALL DEPT":
                cur.execute("SELECT * FROM members_list WHERE membership_status='Active' ORDER BY dept")
            else: 
                cur.execute("SELECT * FROM members_list WHERE dept='%s' AND membership_status='Active' ORDER BY dept" % self.comboBox_viewtabledept.currentText())
        
        memberlist = cur.fetchall()
        self.tableWidget.setRowCount(len(memberlist))
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(["id", "RFID", "Chinese Name", "English Name", "Dept", "Gender", "Member Status", "DOB", "Passing Date", "Contact Num"])
        
        # load column 0 - id
        for rownumber, rowvalue in enumerate(memberlist):
            self.tableWidget.setItem(rownumber,0,QtGui.QTableWidgetItem("%d" %rowvalue[0]))
        
        # load column 1 - rfid
        for rownumber, rowvalue in enumerate(memberlist):
            if rowvalue[1] is None:
                self.tableWidget.setItem(rownumber,1,QtGui.QTableWidgetItem(""))
            else:
                self.tableWidget.setItem(rownumber,1,QtGui.QTableWidgetItem(rowvalue[1]))
        
        # load column 2 - name
        for rownumber, rowvalue in enumerate(memberlist):
            self.tableWidget.setItem(rownumber,2,QtGui.QTableWidgetItem(rowvalue[2]))
          
        # load column 3 - english name
        for rownumber, rowvalue in enumerate(memberlist):
            if rowvalue[3] is None:
                self.tableWidget.setItem(rownumber,3,QtGui.QTableWidgetItem(""))
            else:
                self.tableWidget.setItem(rownumber,3,QtGui.QTableWidgetItem(rowvalue[3]))
          
        # load column 4 - dept    
        for rownumber, rowvalue in enumerate(memberlist):
            self.tableWidget.setItem(rownumber,4,QtGui.QTableWidgetItem(rowvalue[4]))
          
        # load column 5 - gender
        for rownumber, rowvalue in enumerate(memberlist):
            self.tableWidget.setItem(rownumber,5,QtGui.QTableWidgetItem(rowvalue[5]))
              
        # load column 6 - status
        for rownumber, rowvalue in enumerate(memberlist):
            self.tableWidget.setItem(rownumber,6,QtGui.QTableWidgetItem(rowvalue[6]))
            
        # load column 7 - dob
        for rownumber, rowvalue in enumerate(memberlist):
            if rowvalue[7] is None:
                self.tableWidget.setItem(rownumber,7,QtGui.QTableWidgetItem(""))
            else:    
                self.tableWidget.setItem(rownumber,7,QtGui.QTableWidgetItem(rowvalue[7].strftime("%Y-%m-%d")))
             
        # load column 8 - passing
        for rownumber, rowvalue in enumerate(memberlist):
            if rowvalue[8] is None:
                self.tableWidget.setItem(rownumber,8,QtGui.QTableWidgetItem(""))
            else:
                self.tableWidget.setItem(rownumber,8,QtGui.QTableWidgetItem(rowvalue[8].strftime("%Y-%m-%d")))
                                         
        # load column 9 - contact
        for rownumber, rowvalue in enumerate(memberlist):
            if rowvalue[9] is None:
                self.tableWidget.setItem(rownumber,9,QtGui.QTableWidgetItem(""))
            else:    
                self.tableWidget.setItem(rownumber,9,QtGui.QTableWidgetItem(rowvalue[9]))
        
        # color the table cell according to dept
        for rownumber, rowvalue in enumerate(memberlist):
            if rowvalue[4] == "CL":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(255,178,102))
            if rowvalue[4] == "BF":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(255,255,102))
            if rowvalue[4] == "JS":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(178,255,102))
            if rowvalue[4] == "YM":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(153,255,153))
            if rowvalue[4] == "YF":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(153,255,204))
            if rowvalue[4] == "CM":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(102,255,255))
            if rowvalue[4] == "CF":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(102,178,255))
            if rowvalue[4] == "SSM":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(153,153,255))
            if rowvalue[4] == "SSF":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(178,102,255))
            if rowvalue[4] == "MWM":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(255,102,255))
            if rowvalue[4] == "MWF":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(255,102,178))
            if rowvalue[4] == "GL":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(255,204,204))
            if rowvalue[4] == "OS":
                self.tableWidget.item(rownumber,2).setBackground(QtGui.QColor(255,102,102))

        # load combobox values in the table cell
        dept_list = ["CL","BF", "JS", "YM", "YF", "CM", "CF", "SSM", "SSF", "MWM", "MWF", "GL", "OS"]
        gender_list = ["M","F"]
        status_list = ["Active", "Inactive"]
         
        for row in (range(self.tableWidget.rowCount())):
            self.table_combobox_dept = QtGui.QComboBox()
            self.table_combobox_gender = QtGui.QComboBox()
            self.table_combobox_status = QtGui.QComboBox()
            
            self.table_combobox_dept.addItems(dept_list)
            self.table_combobox_gender.addItems(gender_list)
            self.table_combobox_status.addItems(status_list)
            
            self.table_combobox_dept.setCurrentIndex(dept_list.index(self.tableWidget.item(row, 4).text())) 
            self.tableWidget.setCellWidget(row, 4, self.table_combobox_dept)
            self.table_combobox_gender.setCurrentIndex(gender_list.index(self.tableWidget.item(row, 5).text())) 
            self.tableWidget.setCellWidget(row, 5, self.table_combobox_gender)
            self.table_combobox_status.setCurrentIndex(status_list.index(self.tableWidget.item(row, 6).text())) 
            self.tableWidget.setCellWidget(row, 6, self.table_combobox_status)
        
        db.close()
        
    def commit_member_details(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT * FROM members_list GROUP by id")
        all_rows = self.tableWidget.rowCount()
        
        # select the current text in combo box for commit
        for row in range(all_rows):
            self.tableWidget.setItem(row,4,QtGui.QTableWidgetItem(self.tableWidget.cellWidget(row, 4).currentText()))
            self.tableWidget.setItem(row,5,QtGui.QTableWidgetItem(self.tableWidget.cellWidget(row, 5).currentText()))
            self.tableWidget.setItem(row,6,QtGui.QTableWidgetItem(self.tableWidget.cellWidget(row, 6).currentText()))
            
        for row in range(all_rows):
            
            rfid_num = self.tableWidget.item(row, 1).text()
            chi_name = self.tableWidget.item(row, 2).text()
            eng_name = self.tableWidget.item(row, 3).text()
            dept = self.tableWidget.item(row, 4).text()
            gender = self.tableWidget.item(row, 5).text()
            membership_status = self.tableWidget.item(row, 6).text()
            dob = self.tableWidget.item(row, 7).text()
            passing_date = self.tableWidget.item(row, 8).text()
            contact_num = self.tableWidget.item(row, 9).text()
            idnum = int(self.tableWidget.item(row, 0).text())
            

            if rfid_num == "":
                cur.execute("UPDATE members_list SET rfid_num=NULL WHERE id=%d" % (idnum))
            else:
                cur.execute("UPDATE members_list SET rfid_num=NULL WHERE id=%d" % (idnum))
                db.commit()
                cur.execute("UPDATE members_list SET rfid_num='%s' WHERE id=%d" % (rfid_num, idnum))
                
            
            cur.execute("UPDATE members_list SET chi_name='%s', eng_name='%s', dept='%s', gender='%s', membership_status='%s', contact_num='%s', dob='%s',passing_date='%s' WHERE id=%d " 
            % (chi_name,eng_name,dept,gender,membership_status,contact_num,dob,passing_date,idnum))

            db.commit()
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            self.statusbar.showMessage("Changes committed!")
            
            


        
####################################################################################################################################################    
    

    def load_all_deptcombobox(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()   
        cur.execute("SELECT dept FROM members_list GROUP by dept")
        deptlist = cur.fetchall()
        for dept in deptlist:
            self.comboBox_admintab_dept.addItems(dept)
            
        # load combobox in the viewtable tab as well 
        for dept in deptlist:
            self.comboBox_viewtabledept.addItems(dept)
        self.comboBox_viewtabledept.addItems(["ALL DEPT"])
        
        # load combobox in the add new members tab and personal profile as well 
        self.comboBox_addmemberdept.clear()
        for dept in deptlist:
            self.comboBox_addmemberdept.addItems(dept)
        
        self.comboBox_addmembergender.addItems(["F", "M"])
        db.close()
        
    def load_admin_eventcombobox(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT event_type FROM event_test GROUP BY event_type")
        eventlist = cur.fetchall()
        for event in eventlist:
#             print event
            self.comboBox_admintab_event.addItems(event)
            self.comboBox_eventviewatt.addItems(event)
#             self.comboBox_viewevent.addItems(event)
            self.comboBox_addnewevent.addItems(event)
        db.close()
            
    def load_admin_name_status_combobox(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        self.comboBox_admintab_name.clear()
#         self.comboBox_admintab_status.clear()
        
        cur.execute("SELECT chi_name FROM members_list WHERE dept='%s' AND membership_status='Active'" % self.comboBox_admintab_dept.currentText())
        namelist = cur.fetchall()

        for name in namelist: 
            self.comboBox_admintab_name.addItems(name)
#         self.comboBox_admintab_status.addItems(["B", "P"])
        
        db.close()
         
        
# PERSONAL PROFILE STUFF #
####################################################################################################################################################    
    def load_profile_deptcombobox(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()        
              
        self.comboBox_profiledept.clear()
        cur.execute("SELECT dept FROM members_list GROUP by dept")
        deptlist = cur.fetchall()
        for dept in deptlist:
            self.comboBox_profiledept.addItems(dept)
            
        db.close()
        
    def load_profile_namecombobox(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()        
        self.comboBox_profilename.clear()
        cur.execute("SELECT chi_name FROM members_list WHERE dept='%s' AND membership_status='Active'" % self.comboBox_profiledept.currentText())
        namelist = cur.fetchall()
        for name in namelist:
            self.comboBox_profilename.addItems(name)
        db.close()
        
        self.load_profile()
        
    def load_profile(self):  
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        cur.execute("SELECT * FROM members_list WHERE chi_name='%s' " % (self.comboBox_profilename.currentText()))
        member_data = cur.fetchall()
        
#         print member_data
        
        if member_data is not ():
            
            if member_data[0][3] is None:
                self.lineEdit_profileenglishname.setText("Null")
            else:    
                self.lineEdit_profileenglishname.setText(member_data[0][3])
            self.lineEdit_profileenglishname.setDisabled(True)
            
            
            self.lineEdit_profilegender.setText(member_data[0][5])
            self.lineEdit_profilegender.setDisabled(True)
            
            if member_data[0][7] is None:
                self.lineEdit_profiledob.setText("Null")
            else: 
                self.lineEdit_profiledob.setText(str(member_data[0][7]))
            self.lineEdit_profiledob.setDisabled(True)
            
            if member_data[0][8] is None:
                self.lineEdit_profilepassing.setText("Null")
            else:
                self.lineEdit_profilepassing.setText(str(member_data[0][8]))
            self.lineEdit_profilepassing.setDisabled(True)
            
            if member_data[0][9] is None:
                self.lineEdit_profileconnum.setText("Null")
            else:
                self.lineEdit_profileconnum.setText(member_data[0][9])
            self.lineEdit_profileconnum.setDisabled(True)
            
                  
            if os.path.exists("pics/%s.jpg" % self.comboBox_profilename.currentText()):
                        self.label_personalpic.setPixmap(QtGui.QPixmap("pics/%s.jpg" % self.comboBox_profilename.currentText()).scaledToHeight(200) )
            else:
                self.label_personalpic.setPixmap(QtGui.QPixmap("icon/unknown_profile.png" ).scaledToHeight(160))
    
        
####################################################################################################################################################    
    def load_att_marking_pic(self):
        if os.path.exists("pics/%s.jpg" % self.comboBox_admintab_name.currentText()):
                        self.label_attmarkingpic.setPixmap(QtGui.QPixmap("pics/%s.jpg" % self.comboBox_admintab_name.currentText()).scaledToHeight(160) )
        else:
            self.label_attmarkingpic.setPixmap(QtGui.QPixmap("icon/unknown_profile.png" ).scaledToHeight(160))

    def submit_attendance(self):
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT id from members_list WHERE chi_name='%s' " % self.comboBox_admintab_name.currentText() )
        member_id = cur.fetchall()
        
        cur.execute("SELECT event_id FROM event_test WHERE event_type='%s' AND event_date='%s'  " % (self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))
        event_id = cur.fetchall()
        
        
        if event_id == ():
            self.statusbar.showMessage("No such event! Check event type")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        
        duplicate = cur.execute("SELECT * FROM new_attendance_table WHERE member_id=%d AND event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
        
        if duplicate == 0:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            
            if self.radioButton_present.isChecked():
                cur.execute("INSERT INTO new_attendance_table (member_id, event_id, status, timestamp) VALUES ('%d', '%d', 'P', '%s') " % (int(member_id[0][0]), int(event_id[0][0]), datetime.datetime.now()))
                db.commit()
                self.statusbar.showMessage("Submitted attendance for %s for %s on %s. Attendance=P" % (self.comboBox_admintab_name.currentText(), self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))
            
            elif self.radioButton_broadcast.isChecked():
                cur.execute("INSERT INTO new_attendance_table (member_id, event_id, status, timestamp) VALUES ('%d', '%d', 'B', '%s') " % (int(member_id[0][0]), int(event_id[0][0]), datetime.datetime.now()))
                db.commit()
                self.statusbar.showMessage("Submitted attendance for %s for %s on %s. Attendance=B" % (self.comboBox_admintab_name.currentText(), self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))
        
        
        else:
            self.statusbar.showMessage("Duplicate entry")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")

    def delete_attendance(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT id from members_list WHERE chi_name='%s' " % self.comboBox_admintab_name.currentText() )
        member_id = cur.fetchall()
        cur.execute("SELECT event_id FROM event_test WHERE event_type='%s' AND event_date='%s'" % (self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))
        event_id = cur.fetchall()
        
        if event_id == ():
            self.statusbar.showMessage("No such event! Check event type")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            
        cur.execute("SELECT * FROM new_attendance_table WHERE member_id=%d AND event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
        found = cur.fetchall()
        
        if found == ():
            self.statusbar.showMessage("No record found!")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        else:
            cur.execute("DELETE FROM new_attendance_table WHERE member_id=%d AND event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            db.commit()
            self.statusbar.showMessage("Deleted attendance for %s for %s on %s" % (self.comboBox_admintab_name.currentText(), self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))

    def viewAttendance(self):
        
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        
        cur.execute("SELECT event_id FROM event_test WHERE event_type='%s' AND event_date='%s'" % (self.comboBox_eventviewatt.currentText(), self.calendarWidget_attview.selectedDate().toString("yyyy-MM-dd")))
        event_id = cur.fetchall()
        
        # check if event exists
        if event_id == ():
            self.statusbar.showMessage("No such event! Check event type")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            
        else:
            cur.execute("SELECT chi_name, dept, status, timestamp FROM member_attendance_summary WHERE event_type='%s' AND event_date='%s' " %(self.comboBox_eventviewatt.currentText(), self.calendarWidget_attview.selectedDate().toString("yyyy-MM-dd")))
            attendees = cur.fetchall()
            
            self.tableWidget_attendee.horizontalHeader().setStretchLastSection(True)
            self.tableWidget_attendee.setRowCount(len(attendees))
            self.tableWidget_attendee.setColumnCount(4)
            self.tableWidget_attendee.setHorizontalHeaderLabels(["Name", "Dept", "Status", "Time In" ])
            
            
            broadcast_count = 0
            present_count = 0
                
            for rownumber, rowvalue in enumerate(attendees):
                self.tableWidget_attendee.setItem(rownumber,0,QtGui.QTableWidgetItem("%s" %rowvalue[0]))
                self.tableWidget_attendee.setItem(rownumber,1,QtGui.QTableWidgetItem("%s" %rowvalue[1]))
                self.tableWidget_attendee.setItem(rownumber,2,QtGui.QTableWidgetItem("%s" %rowvalue[2]))
                self.tableWidget_attendee.setItem(rownumber,3,QtGui.QTableWidgetItem("%s" %rowvalue[3]))
                
                
                # highlight broadcast members for easier view
                if rowvalue[2]=='B':
                    broadcast_count+=1
                    self.tableWidget_attendee.item(rownumber,0).setBackground(QtGui.QColor(153,204,255))
                    self.tableWidget_attendee.item(rownumber,1).setBackground(QtGui.QColor(153,204,255))
                    self.tableWidget_attendee.item(rownumber,2).setBackground(QtGui.QColor(153,204,255))
                    self.tableWidget_attendee.item(rownumber,3).setBackground(QtGui.QColor(153,204,255))
                else:
                    present_count+=1
                    self.tableWidget_attendee.item(rownumber,0).setBackground(QtGui.QColor(153,255,153))
                    self.tableWidget_attendee.item(rownumber,1).setBackground(QtGui.QColor(153,255,153))
                    self.tableWidget_attendee.item(rownumber,2).setBackground(QtGui.QColor(153,255,153))
                    self.tableWidget_attendee.item(rownumber,3).setBackground(QtGui.QColor(153,255,153))
            
            # show summary in label
            self.label_totalbroadcast.setText(str(broadcast_count))
            self.label_totalpresent.setText(str(present_count))
            self.statusbar.showMessage("Attendees loaded")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            
            self.tableWidget_attendee.resizeColumnsToContents()
            self.tableWidget_attendee.horizontalHeader().setStretchLastSection(True)
        
        
####################################################################################################################################################        
   
    def Time(self):
        self.lcdNumber_time.display(strftime("%H"+":"+"%M"+":"+"%S"))
    def Date(self):
        self.label_dynamic_date.setText(strftime("%Y"+" "+"%B"+" "+"%d"+", "+"%A"))
        
    def updateEventStatus(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        self.event_id = None
        self.current_date = datetime.datetime.date(datetime.datetime.now())
        self.current_time = datetime.datetime.time(datetime.datetime.now())
#         self.current_date = date(2015,10,7)
#         self.current_time = time(19,0,0)
        if self.current_date.strftime("%A") == "Sunday" and self.current_time >= time(7,0,0) and self.current_time <= time(13,00,0):
            self.event_type = "Sunday Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Sunday Service")
            self.label_welcome.setText("Welcome! wipe ID for Sunday Service Attendance!")
        elif self.current_date.strftime("%A") == "Wednesday" and self.current_time >= time(18,0,0) and self.current_time <= time(22,30,0):
            self.event_type = "Wednesday Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Wednesday Service")
            self.label_welcome.setText("Welcome! Swipe ID for Wednesday Service Attendance!")
        elif self.current_date.strftime("%A") == "Friday" and self.current_time >= time(18,0,0) and self.current_time <= time(22,30,0):
            self.event_type = "Friday Prayer Meeting"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Friday Prayer Meeting")
            self.label_welcome.setText("Welcome! Swipe ID for Friday Prayer Attendance!")
                        
        elif self.current_date.strftime("%A") == "Sunday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome! Swipe ID for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Monday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, Swipe ID for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Tuesday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome! Swipe ID for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Wednesday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome! Swipe ID for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Thursday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome! Swipe ID for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Friday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome! Swipe ID for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Saturday" and self.current_time >= time(0,0,0) and self.current_time <= time(6,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome! Swipe ID for Dawn Service Attendance!")
        
        else:
            self.label_dynamic_event.setText("No event now =(")
            self.label_welcome.setText("Welcome! There's no event now")
            self.label_dynamic_event.setStyleSheet("font-size:11pt;background-color: rgba(255, 255, 255, 0)")
            
            
        if self.event_id is not None:
            self.label_dynamic_event.setStyleSheet("color: red; background-color: rgba(255, 255, 255, 0)")
        
            
    
####################################################################################################################################################            
    def gotonextpage(self, widget):
        current_index = widget.currentIndex()
        current_index+=1
        widget.setCurrentIndex(current_index)
        
    def gotoprevpage(self, widget):
        current_index = widget.currentIndex()
        current_index-=1
        widget.setCurrentIndex(current_index)
    
    def plot_all_service(self):
        self.plot_sunday_service()
        self.plot_wednesday_service()
        self.plot_friday_prayer()
        self.plot_dawn_service()
        
    def plot_sunday_service(self):
        # Sunday service
        present, broadcast, absent = calc_att_by_category(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Sunday Service", dbhostip=self.databaseHostLineEdit.text())
        self.mpl_sundayservicestats.canvas.ax.clear()
        self.mpl_sundayservicestats.canvas.ax.pie([present, broadcast, absent], labels=["Present", "Broadcast", "Absent"],autopct='%1.1f%%',
             colors = ['green', 'yellow', 'red'], startangle=180)    
        self.mpl_sundayservicestats.canvas.ax.axis('equal')
        self.mpl_sundayservicestats.canvas.ax.legend(loc='upper right')
#         self.mpl_sundayservicestats.canvas.ax.set_title("Attendance Distribution [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_sundayservicestats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_sundayservicestats.canvas.draw()
    
        # function returns dict of present, broadcast and absent according to dept
        d_present, d_broadcast, d_absent = calc_att_by_category_alldept(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Sunday Service", dbhostip=self.databaseHostLineEdit.text())
        self.mpl_sundayservicedeptstats.canvas.ax.clear()
        present_rects = self.mpl_sundayservicedeptstats.canvas.ax.barh(range(len(d_present)), d_present.values(), align='center', color="g", label="Present")
        broadcast_rects = self.mpl_sundayservicedeptstats.canvas.ax.barh(range(len(d_broadcast)), d_broadcast.values(), align='center', color="yellow", left=d_present.values(), label="Broadcast")
        absent_rects = self.mpl_sundayservicedeptstats.canvas.ax.barh(range(len(d_absent)), d_absent.values(), align='center', color="r", left=[i+j for i,j in zip(d_present.values(),d_broadcast.values())], label="Absent")
        
        datacursor(present_rects, hover=False,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=False,formatter='{width}%'.format)
        datacursor(absent_rects, hover=False,formatter='{width}%'.format)
        
        self.mpl_sundayservicedeptstats.canvas.ax.set_yticks(range(len(d_present)))
        self.mpl_sundayservicedeptstats.canvas.ax.set_yticklabels(d_present.keys())
        self.mpl_sundayservicedeptstats.canvas.ax.set_ylabel("Dept")
        self.mpl_sundayservicedeptstats.canvas.ax.set_xlabel("Percentage (%)")
        self.mpl_sundayservicedeptstats.canvas.ax.set_xlim([0.0, 100.0])
        self.mpl_sundayservicedeptstats.canvas.ax.grid(True)
        self.mpl_sundayservicedeptstats.canvas.ax.legend(loc='upper right')
#         self.mpl_sundayservicedeptstats.canvas.ax.set_title("Dept Attendance Distribution [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_sundayservicedeptstats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_sundayservicedeptstats.canvas.draw()
        
        self.mpl_sundayservice_daily.canvas.ax.clear()
        daily_present_list, daily_broadcast_list, days, date_list = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Sunday Service", dbhostip=self.databaseHostLineEdit.text())
        daily_present_rects = self.mpl_sundayservice_daily.canvas.ax.bar(days, daily_present_list, align='center', color="g", label="Present", width=1 )
        daily_braodcast_rects = self.mpl_sundayservice_daily.canvas.ax.bar(days, daily_broadcast_list, align='center', color="yellow", bottom=daily_present_list, label="Broadcast", width=1)
        self.mpl_sundayservice_daily.canvas.ax.grid(True)
        
        self.mpl_sundayservice_daily.canvas.ax.set_ylabel("No of members")
        self.mpl_sundayservice_daily.canvas.ax.set_xlabel("Day")
        self.mpl_sundayservice_daily.canvas.ax.set_xlim([0,days[-1]+1])
        self.mpl_sundayservice_daily.canvas.ax.legend(loc='lower right')
#         self.mpl_sundayservice_daily.canvas.ax.set_title("Daily Sunday Service Attendance, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())))
        self.mpl_sundayservice_daily.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        import matplotlib.ticker as plticker

        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        self.mpl_sundayservice_daily.canvas.ax.xaxis.set_major_locator(loc)
        
        datacursor(daily_present_rects, hover=False,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=False,formatter='{height}'.format)
        self.mpl_sundayservice_daily.canvas.draw()
             
    def plot_wednesday_service(self): 
        present, broadcast, absent = calc_att_by_category(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Wednesday Service", dbhostip=self.databaseHostLineEdit.text())

        self.mpl_weddayservicestats.canvas.ax.clear()
        self.mpl_weddayservicestats.canvas.ax.pie([present, broadcast, absent], labels=["Present", "Broadcast", "Absent"],autopct='%1.1f%%',
             colors = ['green', 'yellow', 'red'], startangle=180)
        self.mpl_weddayservicestats.canvas.ax.axis('equal')
        self.mpl_weddayservicestats.canvas.ax.legend(loc='upper right')
#         self.mpl_weddayservicestats.canvas.ax.set_title("Attendance Distribution [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_weddayservicestats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_weddayservicestats.canvas.draw()
    
        d_present, d_broadcast, d_absent = calc_att_by_category_alldept(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Wednesday Service", dbhostip=self.databaseHostLineEdit.text())
        self.mpl_weddayservicedeptstats.canvas.ax.clear()
        present_rects = self.mpl_weddayservicedeptstats.canvas.ax.barh(range(len(d_present)), d_present.values(), align='center', color="g", label="Present")
        broadcast_rects = self.mpl_weddayservicedeptstats.canvas.ax.barh(range(len(d_broadcast)), d_broadcast.values(), align='center', color="yellow", left=d_present.values(), label="Broadcast")
        absent_rects = self.mpl_weddayservicedeptstats.canvas.ax.barh(range(len(d_absent)), d_absent.values(), align='center', color="r", left=[i+j for i,j in zip(d_present.values(),d_broadcast.values())], label="Absent")
        
        datacursor(present_rects, hover=False,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=False,formatter='{width}%'.format)
        datacursor(absent_rects, hover=False,formatter='{width}%'.format)
        
        self.mpl_weddayservicedeptstats.canvas.ax.set_yticks(range(len(d_present)))
        self.mpl_weddayservicedeptstats.canvas.ax.set_yticklabels(d_present.keys())
        self.mpl_weddayservicedeptstats.canvas.ax.set_ylabel("Dept")
        self.mpl_weddayservicedeptstats.canvas.ax.set_xlabel("Percentage (%)")
        self.mpl_weddayservicedeptstats.canvas.ax.set_xlim([0.0, 100.0])
        self.mpl_weddayservicedeptstats.canvas.ax.grid(True)
        self.mpl_weddayservicedeptstats.canvas.ax.legend(loc='upper right')
#         self.mpl_weddayservicedeptstats.canvas.ax.set_title("Dept Attendance Distribution [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_weddayservicedeptstats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_weddayservicedeptstats.canvas.draw() 
        
        self.mpl_wednesdayservice_daily.canvas.ax.clear()
        daily_present_list, daily_broadcast_list, days, date_list = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Wednesday Service", dbhostip=self.databaseHostLineEdit.text())
        daily_present_rects = self.mpl_wednesdayservice_daily.canvas.ax.bar(days, daily_present_list, align='center', color="g", label="Present", width=1 )
        daily_braodcast_rects = self.mpl_wednesdayservice_daily.canvas.ax.bar(days, daily_broadcast_list, align='center', color="yellow", bottom=daily_present_list, label="Broadcast", width=1)
        self.mpl_wednesdayservice_daily.canvas.ax.grid(True)
        
        self.mpl_wednesdayservice_daily.canvas.ax.set_ylabel("No of members")
        self.mpl_wednesdayservice_daily.canvas.ax.set_xlabel("Day")
        self.mpl_wednesdayservice_daily.canvas.ax.set_xlim([0,days[-1]+1])
        self.mpl_wednesdayservice_daily.canvas.ax.legend(loc='lower right')
#         self.mpl_wednesdayservice_daily.canvas.ax.set_title("Daily Wednesday Service Attendance, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())))
        self.mpl_wednesdayservice_daily.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        import matplotlib.ticker as plticker

        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        self.mpl_wednesdayservice_daily.canvas.ax.xaxis.set_major_locator(loc)
        
        datacursor(daily_present_rects, hover=False,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=False,formatter='{height}'.format)
        self.mpl_wednesdayservice_daily.canvas.draw()
    
    def plot_friday_prayer(self):
        present, broadcast, absent = calc_att_by_category(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Friday Prayer Meeting", dbhostip=self.databaseHostLineEdit.text())
        
        self.mpl_fridayservicestats.canvas.ax.clear()
        self.mpl_fridayservicestats.canvas.ax.pie([present, broadcast, absent], labels=["Present", "Broadcast", "Absent"],autopct='%1.1f%%',
             colors = ['green', 'yellow', 'red'], startangle=180)
        self.mpl_fridayservicestats.canvas.ax.axis('equal')
        self.mpl_fridayservicestats.canvas.ax.legend(loc='upper right')
#         self.mpl_fridayservicestats.canvas.ax.set_title("Attendance Distribution [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_fridayservicestats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_fridayservicestats.canvas.draw()
    
        d_present, d_broadcast, d_absent = calc_att_by_category_alldept(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Friday Prayer Meeting", dbhostip=self.databaseHostLineEdit.text())
        self.mpl_fridayservicedeptstats.canvas.ax.clear()
        present_rects = self.mpl_fridayservicedeptstats.canvas.ax.barh(range(len(d_present)), d_present.values(), align='center', color="g", label="Present")
        broadcast_rects = self.mpl_fridayservicedeptstats.canvas.ax.barh(range(len(d_broadcast)), d_broadcast.values(), align='center', color="yellow", left=d_present.values(), label="Broadcast")
        absent_rects = self.mpl_fridayservicedeptstats.canvas.ax.barh(range(len(d_absent)), d_absent.values(), align='center', color="r", left=[i+j for i,j in zip(d_present.values(),d_broadcast.values())], label="Absent")
        
        datacursor(present_rects, hover=False,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=False,formatter='{width}%'.format)
        datacursor(absent_rects, hover=False,formatter='{width}%'.format)

        self.mpl_fridayservicedeptstats.canvas.ax.set_yticks(range(len(d_present)))
        self.mpl_fridayservicedeptstats.canvas.ax.set_yticklabels(d_present.keys())
        self.mpl_fridayservicedeptstats.canvas.ax.set_ylabel("Dept")
        self.mpl_fridayservicedeptstats.canvas.ax.set_xlabel("Percentage (%)")
        self.mpl_fridayservicedeptstats.canvas.ax.set_xlim([0.0, 100.0])
        self.mpl_fridayservicedeptstats.canvas.ax.grid(True)
        self.mpl_fridayservicedeptstats.canvas.ax.legend(loc='upper right')
#         self.mpl_fridayservicedeptstats.canvas.ax.set_title("Dept Attendance Distribution [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_fridayservicedeptstats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_fridayservicedeptstats.canvas.draw()
        
        self.mpl_fridayprayer_daily.canvas.ax.clear()
        daily_present_list, daily_broadcast_list, days, date_list = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Friday Prayer Meeting", dbhostip=self.databaseHostLineEdit.text())
        daily_present_rects = self.mpl_fridayprayer_daily.canvas.ax.bar(days, daily_present_list, align='center', color="g", label="Present", width=1 )
        daily_braodcast_rects = self.mpl_fridayprayer_daily.canvas.ax.bar(days, daily_broadcast_list, align='center', color="yellow", bottom=daily_present_list, label="Broadcast", width=1)
        self.mpl_fridayprayer_daily.canvas.ax.grid(True)
        
        self.mpl_fridayprayer_daily.canvas.ax.set_ylabel("No of members")
        self.mpl_fridayprayer_daily.canvas.ax.set_xlabel("Day")
        self.mpl_fridayprayer_daily.canvas.ax.set_xlim([0,days[-1]+1])
        self.mpl_fridayprayer_daily.canvas.ax.legend(loc='lower right')
#         self.mpl_fridayprayer_daily.canvas.ax.set_title("Daily Friday Prayer Attendance, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())))
        self.mpl_fridayprayer_daily.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        import matplotlib.ticker as plticker

        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        self.mpl_fridayprayer_daily.canvas.ax.xaxis.set_major_locator(loc)
        
        datacursor(daily_present_rects, hover=False,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=False,formatter='{height}'.format)
        self.mpl_fridayprayer_daily.canvas.draw()
    
    def plot_dawn_service(self):   
        present, broadcast, absent = calc_att_by_category(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Dawn Service", dbhostip=self.databaseHostLineEdit.text())
        
        self.mpl_dawnservicestats.canvas.ax.clear()
        self.mpl_dawnservicestats.canvas.ax.pie([present, broadcast, absent], labels=["Present", "Broadcast", "Absent"],autopct='%1.1f%%',
             colors = ['green', 'yellow', 'red'], startangle=180)
        self.mpl_dawnservicestats.canvas.ax.axis('equal')
        self.mpl_dawnservicestats.canvas.ax.legend(loc='upper right')
#         self.mpl_dawnservicestats.canvas.ax.set_title("Attendance Distribution, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_dawnservicestats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_dawnservicestats.canvas.draw()
        
        d_present, d_broadcast, d_absent = calc_att_by_category_alldept(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Dawn Service", dbhostip=self.databaseHostLineEdit.text())
        self.mpl_dawnservicedeptstats.canvas.ax.clear()
        present_rects = self.mpl_dawnservicedeptstats.canvas.ax.barh(range(len(d_present)), d_present.values(), align='center', color="g", label="Present")
        broadcast_rects = self.mpl_dawnservicedeptstats.canvas.ax.barh(range(len(d_broadcast)), d_broadcast.values(), align='center', color="yellow", left=d_present.values(), label="Broadcast")
        absent_rects = self.mpl_dawnservicedeptstats.canvas.ax.barh(range(len(d_absent)), d_absent.values(), align='center', color="r", left=[i+j for i,j in zip(d_present.values(),d_broadcast.values())], label="Absent")
        
        datacursor(present_rects, hover=False,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=False,formatter='{width}%'.format)
        datacursor(absent_rects, hover=False,formatter='{width}%'.format)
            
        self.mpl_dawnservicedeptstats.canvas.ax.set_yticks(range(len(d_present)))
        self.mpl_dawnservicedeptstats.canvas.ax.set_yticklabels(d_present.keys())
        self.mpl_dawnservicedeptstats.canvas.ax.set_xlim([0.0, 100.0])
        self.mpl_dawnservicedeptstats.canvas.ax.grid(True)
        self.mpl_dawnservicedeptstats.canvas.ax.set_ylabel("Dept")
        self.mpl_dawnservicedeptstats.canvas.ax.set_xlabel("Percentage (%)")
        self.mpl_dawnservicedeptstats.canvas.ax.legend(loc='upper right')
#         self.mpl_dawnservicedeptstats.canvas.ax.set_title("Dept Attendance Distribution, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())) , y=1.05)
        self.mpl_dawnservicedeptstats.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        self.mpl_dawnservicedeptstats.canvas.draw()
        
        
        self.mpl_dawnservice_daily.canvas.ax.clear()
        daily_present_list, daily_broadcast_list, days, date_list = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Dawn Service", dbhostip=self.databaseHostLineEdit.text())
        daily_present_rects = self.mpl_dawnservice_daily.canvas.ax.bar(days, daily_present_list, align='center', color="g", label="Present", width=1 )
        daily_braodcast_rects = self.mpl_dawnservice_daily.canvas.ax.bar(days, daily_broadcast_list, align='center', color="yellow", bottom=daily_present_list, label="Broadcast", width=1)
        self.mpl_dawnservice_daily.canvas.ax.grid(True)
#         self.mpl_dawnservice_daily.canvas.ax.set_xticklabels(date_list, rotation=45)
        
        self.mpl_dawnservice_daily.canvas.ax.set_ylabel("No of members")
        self.mpl_dawnservice_daily.canvas.ax.set_xlabel("Day")
        self.mpl_dawnservice_daily.canvas.ax.set_xlim([0,days[-1]+1])
        self.mpl_dawnservice_daily.canvas.ax.legend(loc='upper right')
#         self.mpl_dawnservice_daily.canvas.ax.set_title("Daily Dawn Service Attendance, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())))
        self.mpl_dawnservice_daily.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        import matplotlib.ticker as plticker

        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        self.mpl_dawnservice_daily.canvas.ax.xaxis.set_major_locator(loc)
        
        datacursor(daily_present_rects, hover=False,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=False,formatter='{height}'.format)
        self.mpl_dawnservice_daily.canvas.draw()
        
        
        # annnotate the daily bar chart with values
        
#         members_count = calc_num_all_dept(verbose=False, dbhostip=self.databaseHostLineEdit.text())
#         total_active_members = (sum(members_count.values()))
#         print total_active_members
            
#         for rect in daily_present_rects:   
#             height = rect.get_height()
#             self.mpl_dawnservice_daily.canvas.ax.text(rect.get_x()+rect.get_width()/2. , 0.5*height, '%.2f%%' % float(float(height)/float(total_active_members)*100),
#                     ha='center', va='bottom', color='greenyellow', fontweight='bold', rotation=90)
            
#         for rect in daily_braodcast_rects:   
#             height = rect.get_height()
#             print height
#             
#             self.mpl_dawnservice_daily.canvas.ax.text(rect.get_x()+rect.get_width()/2. , 1.05*height, '%.2f%%' % float(float(height)/float(total_active_members)*100),
#                     ha='center', va='bottom', color='greenyellow', fontweight='bold', rotation=90)
        
    def plot_dept_stats(self):
        '''
        Plots a bar chart of the number of members in each dept
        '''
        members_count = calc_num_all_dept(verbose=False, dbhostip=self.databaseHostLineEdit.text())
        
        # define a global variable for total active members to avoid redudant call of calc_num_all_dept
        global total_active_members
        total_active_members = (sum(members_count.values()))
        
        self.mpl_memberscount.canvas.ax.clear()
        rects = self.mpl_memberscount.canvas.ax.bar(range(len(members_count)), members_count.values(), align='center')
        self.mpl_memberscount.canvas.ax.set_xticks(range(len(members_count)))
        self.mpl_memberscount.canvas.ax.set_xticklabels(members_count.keys())
        self.mpl_memberscount.canvas.ax.set_xlabel("Department")
        self.mpl_memberscount.canvas.ax.set_ylabel("Number of members")
        self.mpl_memberscount.canvas.ax.set_ylim([0,40])
        self.mpl_memberscount.canvas.ax.set_title("LWC Active Members Distribution, Total Active Members:%d" % total_active_members)
        self.mpl_memberscount.canvas.ax.grid(True)
        # label values on graph
        for rect in rects:
            height = rect.get_height()
            self.mpl_memberscount.canvas.ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom', color='blue', fontweight='bold')
            
        # hover mouse
        datacursor(rects, hover=False,formatter='{height}'.format)
        
        self.mpl_memberscount.canvas.draw()
        
####################################################################################################################################################    

    def search_database_for_member_id(self, rfid):
        '''
        Search databse for member identity and print
        param: id reader
        return: member_id 
        '''
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT * FROM members_list WHERE rfid_num='%s' AND membership_status='Active' " % rfid)
        mysql_data = cur.fetchall()
        return mysql_data
    
    def clear_members_dynamic_fields(self):
        self.label_dynamic_name.setText("")
        self.label_dynamic_rfid.setText("")
        self.label_dynamic_engname.setText("")
        self.label_dynamic_dept.setText("")
        self.label_dynamic_status.setText("")
    
    def v2_scan_id(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        try:
            self.data = self.arduino.read(self.arduino.inWaiting())
        except:
            print("Error reading from %s " % str(self.comboBox_serialPort.currentText()) )
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            self.statusBar().showMessage("Error reading from %s, plug in the reader and restart application! " % str(self.comboBox_serialPort.currentText()))
            self.pushButton_connect.setStyleSheet("background-color: red")
            self.pushButton_connect.setText("Connect")
        
        if len(self.data) > 11:
            print "ID detected"
            read_id = self.data[:12]
            print "Detected ID:",read_id
            print "Time:", datetime.datetime.now()

            member_data = self.search_database_for_member_id(read_id)
            
            if member_data:
#                 print "Success"
                self.clear_members_dynamic_fields()
                member_id = member_data[0][0] 
                
                print "Name: %s" % member_data[0][2].encode('utf-8')
#                 print "Event ID", self.event_id
                
                self.label_dynamic_name.setText(member_data[0][2])
                
                if member_data[0][1] is not None:
                    self.label_dynamic_rfid.setText(member_data[0][1])
                if member_data[0][3] is not None:
                    self.label_dynamic_engname.setText(member_data[0][3])

                self.label_dynamic_dept.setText(member_data[0][4])
                
                if os.path.exists("pics/%s.jpg" % member_data[0][2].encode('utf-8')):
                    self.label_picture.setPixmap(QtGui.QPixmap("pics/%s.jpg" % member_data[0][2]).scaledToHeight(200) )

                else:
                    self.label_picture.setPixmap(QtGui.QPixmap("icon/unknown_profile.png" ).scaledToHeight(160))
                 
                self.updateEventStatus()
                
                self.label_dynamic_status.setStyleSheet("color: black; background-color: rgba(255, 255, 255, 0)")
                
                if self.event_id is not None:
                    cur.execute("SELECT * FROM new_attendance_table WHERE member_id='%d' AND event_id='%d' " % ( int(member_id), int(self.event_id) ) )
                    if cur.fetchall() == ():
                        cur.execute("INSERT INTO new_attendance_table VALUES (NULL, '%d', '%d', 'P', '%s' )" % ( int(member_id), int(self.event_id), datetime.datetime.now()))
                        db.commit()
                        print "*****Recorded!*****"
                        print "Member:", member_data[0][2].encode('utf-8')
                        print "Event:", self.event_type, self.event_date 
                        self.label_dynamic_status.setText("Done! Congratulations for attending %s!" % self.event_type)
                        self.label_dynamic_status.setStyleSheet("color: green; background-color: rgba(255, 255, 255, 0);font-weight:bold;")
                        self.statusbar.clearMessage()
                        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
    
                    else:
                        print "Record exists for:"
                        print "Member:", member_data[0][2].encode('utf-8')
                        print "Event:", self.event_type, self.event_date
                        self.label_dynamic_status.setText("Duplicate entry. Your attendance was taken earlier.")
                        self.label_dynamic_status.setStyleSheet("color: red; background-color: rgba(255, 255, 255, 0);font-weight:bold;")
                        self.statusbar.clearMessage()
                        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
                else:
                    self.label_dynamic_status.setText("There's no event at the moment. Good job for coming to church!")
                    self.label_dynamic_status.setStyleSheet("color: black; background-color: rgba(255, 255, 255, 0)")
                    self.statusbar.clearMessage()
                    self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")

            else:
                print "Sorry no match in database!"
                self.label_dynamic_status.setText("Sorry no match in database! Please get help from LWC admin")
                self.label_dynamic_status.setStyleSheet("color: blue; background-color: rgba(255, 255, 255, 0)")
                self.label_picture.clear()
                self.label_dynamic_name.clear()
                self.label_dynamic_dept.clear()
                self.label_dynamic_rfid.clear()
                self.label_dynamic_engname.clear()
                self.statusbar.clearMessage()
                self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
                
        
def main():

    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
#     form = AttTracker() 
#     form.show()                         # Show the form
#     app.exec_()                         

    if Login().exec_() == QtGui.QDialog.Accepted:
        form = AttTracker() 
        form.show()                         # Show the form
        app.exec_()                         # and execute the app


        

    
if __name__ == '__main__':              # if we're running file directly and not importing it
    main()    
