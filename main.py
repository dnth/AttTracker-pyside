import sys
import os
from PySide import QtGui, QtCore
import tabbed_design

from importserial import load_serial_ports
import serial


from read_graph_tables import calc_att_by_category, calc_att_by_category_alldept, calc_num_all_dept, plot_service_daily
from mpldatacursor import datacursor
import calendar

import MySQLdb as mdb

import datetime
from datetime import date, time
from time import strftime

class Login(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.textName = QtGui.QLineEdit(self)
        self.textPass = QtGui.QLineEdit(self)
        self.buttonLogin = QtGui.QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        if (self.textName.text() == 'foo' and
            self.textPass.text() == 'bar'):
            self.accept()
        else:
            QtGui.QMessageBox.warning(
                self, 'Error', 'Bad user or password')
            

class AttTracker(QtGui.QMainWindow, tabbed_design.Ui_LWCAttendanceTaker):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        self.setWindowIcon(QtGui.QIcon('icon/python.jpg'))

        self.actionQuit.triggered.connect(self.close_application)
         
        self.actionQuit.setStatusTip("Leave the application")
        self.actionQuit.setShortcut("Ctrl+Shift+Q")
         
        self.actionConnect.triggered.connect(self.connect_serial_port)
        self.actionConnect.setStatusTip("Connect to serial port")
        self.actionConnect.setShortcut("Ctrl+Shift+C")
        
        self.home()
        
        
    def home(self):
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        self.statusbar.showMessage("No database connected. Enter the IP address of the database server")
        
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
        
        # attendance marking stuff
        self.pushButton_submit.clicked.connect(self.submit_attendance)
        self.pushButton_delete.clicked.connect(self.delete_attendance)
#         self.pushButton_reload_attlist.clicked.connect(self.load_admin_name_status_combobox)
        
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
        

         
    def close_application(self):
        print "Thanks for using me!"
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
            
            
    def add_new_member(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        
        cur.execute("INSERT INTO members_list (chi_name, eng_name, dept, gender, membership_status, dob, passing_date, contact_num) VALUES ('%s', '%s', '%s', '%s', 'Active', '%s', '%s', '%s') " 
                    % (self.nameLineEdit.text(), self.englishNameLineEdit.text(), self.comboBox_addmemberdept.currentText(), self.comboBox_addmembergender.currentText(), self.calendarWidget_newmember_dob.selectedDate().toString("yyyy-MM-dd"), self.calendarWidget_newmember_passing.selectedDate().toString("yyyy-MM-dd"), self.contactNum_lineEdit.text() ))
        db.commit()
        
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
        self.statusbar.showMessage("New member added!")


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
            
        

####################################################################################################################################################    
    def loadMembersTableView(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()   
        
        self.statusbar.showMessage("Loaded database")
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        
        if self.comboBox_viewtabledept.currentText() == "ALL DEPT":
            cur.execute("SELECT * FROM members_list ORDER BY dept")
        else: 
            cur.execute("SELECT * FROM members_list WHERE dept='%s' ORDER BY dept" % self.comboBox_viewtabledept.currentText())
        
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
        

        # load combobox values
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
                
            
            cur.execute("UPDATE members_list SET chi_name='%s', eng_name='%s', dept='%s', gender='%s', membership_status='%s', contact_num='%s' WHERE id=%d " 
            % (chi_name,eng_name,dept,gender,membership_status,contact_num,idnum))

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
            self.comboBox_admintab_event.addItems(event)
        db.close()
            
    def load_admin_name_status_combobox(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        self.comboBox_admintab_name.clear()
        self.comboBox_admintab_status.clear()
        
        cur.execute("SELECT chi_name FROM members_list WHERE dept='%s' AND membership_status='Active'" % self.comboBox_admintab_dept.currentText())
        namelist = cur.fetchall()
        for name in namelist:
            self.comboBox_admintab_name.addItems(name)
        self.comboBox_admintab_status.addItems(["P", "B"])
        
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
        
        print member_data
        
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
                self.lineEdit_profiledob.setText(member_data[0][7])
            self.lineEdit_profiledob.setDisabled(True)
            
            if member_data[0][8] is None:
                self.lineEdit_profilepassing.setText("Null")
            else:
                self.lineEdit_profilepassing.setText(member_data[0][8])
            self.lineEdit_profilepassing.setDisabled(True)
            
            if member_data[0][9] is None:
                self.lineEdit_profileconnum.setText("Null")
            else:
                self.lineEdit_profileconnum.setText(member_data[0][9])
            self.lineEdit_profileconnum.setDisabled(True)
            
                  
            if os.path.exists("pics/%s.jpg" % self.comboBox_profilename.currentText()):
                        self.label_personalpic.setPixmap(QtGui.QPixmap("pics/%s.jpg" % self.comboBox_profilename.currentText()).scaledToHeight(200) )
            else:
                self.label_personalpic.setPixmap(QtGui.QPixmap("unknown_profile.png" ).scaledToHeight(160))
        
        
####################################################################################################################################################    

        
    def submit_attendance(self):
#         self.label_admintab_dynamic_remarks.setStyleSheet("color: none")
        self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT id from members_list WHERE chi_name='%s' " % self.comboBox_admintab_name.currentText() )
        member_id = cur.fetchall()
        cur.execute("SELECT event_id FROM event_test WHERE event_type='%s' AND event_date='%s'  " % (self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))
        event_id = cur.fetchall()
        print event_id
        
        if event_id == ():
#             self.label_admintab_dynamic_remarks.setText("No such event! Check event type")
#             self.label_admintab_dynamic_remarks.setStyleSheet("color: red")
            self.statusbar.showMessage("No such event! Check event type")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        
        duplicate = cur.execute("SELECT * FROM new_attendance_table WHERE member_id=%d AND event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
        if duplicate == 0:
#             self.label_admintab_dynamic_remarks.setText( "Submitted query for member_id=%d, event_id=%d, status=%s" % (int(member_id[0][0]), int(event_id[0][0]), self.comboBox_admintab_status.currentText()))
#             self.label_admintab_dynamic_remarks.setStyleSheet("color: green")
            self.statusbar.showMessage("Submitted query for member_id=%d, event_id=%d, status=%s" % (int(member_id[0][0]), int(event_id[0][0]), self.comboBox_admintab_status.currentText()))
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            cur.execute("INSERT INTO new_attendance_table (member_id, event_id, status) VALUES ('%d', '%d', '%s') " % (int(member_id[0][0]), int(event_id[0][0]), self.comboBox_admintab_status.currentText()))
            db.commit()
        else:
            self.statusbar.showMessage("Duplicate entry")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
#             self.label_admintab_dynamic_remarks.setText("Duplicate entry")
#             self.label_admintab_dynamic_remarks.setStyleSheet("color: red")
        
    def delete_attendance(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT id from members_list WHERE chi_name='%s' " % self.comboBox_admintab_name.currentText() )
        member_id = cur.fetchall()
        cur.execute("SELECT event_id FROM event_test WHERE event_type='%s' AND event_date='%s'  " % (self.comboBox_admintab_event.currentText(), self.calendarWidget.selectedDate().toString("yyyy-MM-dd")))
        event_id = cur.fetchall()
        
        if event_id == ():
#             self.label_admintab_dynamic_remarks.setText("No such event! Check event type")
            self.statusbar.showMessage("No such event! Check event type")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
            
        cur.execute("SELECT * FROM new_attendance_table WHERE member_id=%d AND event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
        found = cur.fetchall()
        
        if found == ():
#             self.label_admintab_dynamic_remarks.setText("No record found!")
            self.statusbar.showMessage("No record found!")
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        else:
            cur.execute("DELETE FROM new_attendance_table WHERE member_id=%d AND event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
#             self.label_admintab_dynamic_remarks.setText( "Deleted for member_id=%d, event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
            self.statusbar.showMessage("Deleted for member_id=%d, event_id=%d" % (int(member_id[0][0]), int(event_id[0][0])))
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
            db.commit()
####################################################################################################################################################        
   
    def Time(self):
        self.lcdNumber_time.display(strftime("%H"+":"+"%M"+":"+"%S"))
    def Date(self):
        self.label_dynamic_date.setText(strftime("%Y"+" "+"%B"+" "+"%d"+", "+"%A"))
        
    def updateEventStatus(self):
        db = mdb.connect(charset='utf8', host=str(self.databaseHostLineEdit.text()), user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        self.event_id=None
        self.current_date = datetime.datetime.date(datetime.datetime.now())
        self.current_time = datetime.datetime.time(datetime.datetime.now())
#         self.current_date = date(2015,10,4)
#         self.current_time = time(9,0,0)
        if self.current_date.strftime("%A") == "Sunday" and self.current_time >= time(7,0,0) and self.current_time <= time(18,00,0):
            self.event_type = "Sunday Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Sunday Service")
            self.label_welcome.setText("Welcome, swipe id for Sunday Service Attendance!")
        elif self.current_date.strftime("%A") == "Wednesday" and self.current_time >= time(18,0,0) and self.current_time <= time(21,30,0):
            self.event_type = "Wednesday Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Wednesday Service")
            self.label_welcome.setText("Welcome, swipe id for Wednesday Service Attendance!")
        elif self.current_date.strftime("%A") == "Friday" and self.current_time >= time(18,0,0) and self.current_time <= time(21,30,0):
            self.event_type = "Friday Prayer Meeting"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Friday Prayer Meeting")
            self.label_welcome.setText("Welcome, swipe id for Friday Prayer Attendance!")
                        
        elif self.current_date.strftime("%A") == "Sunday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Monday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Tuesday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Wednesday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Thursday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Friday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        elif self.current_date.strftime("%A") == "Saturday" and self.current_time >= time(0,0,0) and self.current_time <= time(5,30,0):
            self.event_type = "Dawn Service"
            self.event_date = self.current_date
            cur.execute("SELECT * FROM event_test WHERE event_type='%s' AND event_date='%s' " % (self.event_type, self.event_date) )
            self.event_id = str(cur.fetchall()[0][0])
            self.label_dynamic_event.setText("Dawn Service")
            self.label_welcome.setText("Welcome, swipe id for Dawn Service Attendance!")
        
        else:
            self.label_dynamic_event.setText("No event now =(")
            self.label_welcome.setText("Welcome! There's no event now")
            self.label_dynamic_event.setStyleSheet("font-size:11pt")
            
        if self.event_id is not None:
            self.label_dynamic_event.setStyleSheet("color: red")
            
    
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
        
        datacursor(present_rects, hover=True,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=True,formatter='{width}%'.format)
        datacursor(absent_rects, hover=True,formatter='{width}%'.format)
        
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
        daily_present_list, daily_broadcast_list, days = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Sunday Service", dbhostip=self.databaseHostLineEdit.text())
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
        
        datacursor(daily_present_rects, hover=True,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=True,formatter='{height}'.format)
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
        
        datacursor(present_rects, hover=True,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=True,formatter='{width}%'.format)
        datacursor(absent_rects, hover=True,formatter='{width}%'.format)
        
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
        daily_present_list, daily_broadcast_list, days = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Wednesday Service", dbhostip=self.databaseHostLineEdit.text())
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
        
        datacursor(daily_present_rects, hover=True,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=True,formatter='{height}'.format)
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
        
        datacursor(present_rects, hover=True,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=True,formatter='{width}%'.format)
        datacursor(absent_rects, hover=True,formatter='{width}%'.format)

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
        daily_present_list, daily_broadcast_list, days = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Friday Prayer Meeting", dbhostip=self.databaseHostLineEdit.text())
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
        
        datacursor(daily_present_rects, hover=True,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=True,formatter='{height}'.format)
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
        
        datacursor(present_rects, hover=True,formatter='{width}%'.format)
        datacursor(broadcast_rects, hover=True,formatter='{width}%'.format)
        datacursor(absent_rects, hover=True,formatter='{width}%'.format)
            
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
        daily_present_list, daily_broadcast_list, days = plot_service_daily(month=int(self.comboBox_monthselector.currentText()), year=int(self.comboBox_yearselector.currentText()), event_type="Dawn Service", dbhostip=self.databaseHostLineEdit.text())
        daily_present_rects = self.mpl_dawnservice_daily.canvas.ax.bar(days, daily_present_list, align='center', color="g", label="Present", width=1 )
        daily_braodcast_rects = self.mpl_dawnservice_daily.canvas.ax.bar(days, daily_broadcast_list, align='center', color="yellow", bottom=daily_present_list, label="Broadcast", width=1)
        self.mpl_dawnservice_daily.canvas.ax.grid(True)
        
        self.mpl_dawnservice_daily.canvas.ax.set_ylabel("No of members")
        self.mpl_dawnservice_daily.canvas.ax.set_xlabel("Day")
        self.mpl_dawnservice_daily.canvas.ax.set_xlim([0,days[-1]+1])
        self.mpl_dawnservice_daily.canvas.ax.legend(loc='lower right')
#         self.mpl_dawnservice_daily.canvas.ax.set_title("Daily Dawn Service Attendance, [Month:%s Year:%s]" % (int(self.comboBox_monthselector.currentText()), int(self.comboBox_yearselector.currentText())))
        self.mpl_dawnservice_daily.canvas.ax.set_title("Attendance Distribution %s, %d" % (calendar.month_abbr[int(self.comboBox_monthselector.currentText())], int(self.comboBox_yearselector.currentText())), y=1.05)
        import matplotlib.ticker as plticker

        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        self.mpl_dawnservice_daily.canvas.ax.xaxis.set_major_locator(loc)
        
        datacursor(daily_present_rects, hover=True,formatter='{height}'.format)
        datacursor(daily_braodcast_rects, hover=True,formatter='{height}'.format)
        self.mpl_dawnservice_daily.canvas.draw()
        
    def plot_dept_stats(self):
        '''
        Plots a bar chart of the number of members in each dept
        '''
        members_count = calc_num_all_dept(verbose=False, dbhostip=self.databaseHostLineEdit.text())
        
        self.mpl_memberscount.canvas.ax.clear()
        rects = self.mpl_memberscount.canvas.ax.bar(range(len(members_count)), members_count.values(), align='center')
        self.mpl_memberscount.canvas.ax.set_xticks(range(len(members_count)))
        self.mpl_memberscount.canvas.ax.set_xticklabels(members_count.keys())
        self.mpl_memberscount.canvas.ax.set_xlabel("Department")
        self.mpl_memberscount.canvas.ax.set_ylabel("Number of members")
        self.mpl_memberscount.canvas.ax.set_title("LWC Active Members Distribution")
        self.mpl_memberscount.canvas.ax.grid(True)
        # label values on graph
        for rect in rects:
            height = rect.get_height()
            self.mpl_memberscount.canvas.ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom', color='blue', fontweight='bold')
            
        # hover mouse
        datacursor(rects, hover=True,formatter='{height}'.format)
        
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
            print read_id

            member_data = self.search_database_for_member_id(read_id)
            if member_data:
                print "Success"
                self.clear_members_dynamic_fields()
                member_id = member_data[0][0] 

                print "Name: %s" % member_data[0][2]
                
                self.label_dynamic_name.setText(member_data[0][2])
                
                if member_data[0][1] is not None:
                    self.label_dynamic_rfid.setText(member_data[0][1])
                if member_data[0][3] is not None:
                    self.label_dynamic_engname.setText(member_data[0][3])

                self.label_dynamic_dept.setText(member_data[0][4])
                
                
                
                if os.path.exists("pics/%s.jpg" % member_data[0][2]):
                    self.label_picture.setPixmap(QtGui.QPixmap("pics/%s.jpg" % member_data[0][2]).scaledToHeight(200) )

                else:
                    self.label_picture.setPixmap(QtGui.QPixmap("unknown_profile.png" ).scaledToHeight(160))
                 
                self.updateEventStatus()
                print "Event ID", self.event_id
                self.label_dynamic_status.setStyleSheet("color: black")
                
                if self.event_id is not None:
                    cur.execute("SELECT * FROM new_attendance_table WHERE member_id='%d' AND event_id='%d' " % ( int(member_id), int(self.event_id) ) )
                    if cur.fetchall() == ():
                        cur.execute("INSERT INTO new_attendance_table VALUES (NULL, '%d', '%d', 'P', '%s' )" % ( int(member_id), int(self.event_id), datetime.datetime.now()))
                        db.commit()
                        print "Recorded!"
                        print "Member:", member_data[0][2]
                        print "Event:", self.event_type, self.event_date 
                        self.label_dynamic_status.setText("Done! Congratulations for attending %s!" % self.event_type)
                        self.label_dynamic_status.setStyleSheet("color: green")
    
                    else:
                        print "Record exists for:"
                        print "Member:", member_data[0][2]
                        print "Event:", self.event_type, self.event_date
                        self.label_dynamic_status.setText("Duplicate entry. Your attendance was taken earlier.")
                        self.label_dynamic_status.setStyleSheet("color: red")
                else:
                    self.label_dynamic_status.setText("There's no event at the moment. Good job for coming to church!")
                    self.label_dynamic_status.setStyleSheet("color: black")

            else:
                print "Sorry no match in database!"
                self.label_dynamic_status.setText("Sorry no match in database! Please get help from LWC admin")
                self.label_dynamic_status.setStyleSheet("color: blue")
                self.label_picture.clear()
                self.label_dynamic_name.clear()
                self.label_dynamic_dept.clear()
                self.label_dynamic_rfid.clear()
                self.label_dynamic_engname.clear()
                
        
def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    
    form = AttTracker()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()    
