from __future__ import division
import MySQLdb as mdb
import matplotlib.pyplot as plt

import numpy as np
import collections
from calendar import monthrange, calendar


def calc_num_all_dept(verbose=False, dbhostip="127.0.0.1"):
    '''
    Calculates the number of members in each dept 
    '''
    db = mdb.connect(charset='utf8', host=dbhostip, user="root", passwd="root", db="lwc_members")
    cur = db.cursor()
    cur.execute("SELECT * FROM members_list WHERE membership_status='Active'")
    CL_count = 0
    BF_count = 0
    JS_count = 0
    YM_count = 0
    YF_count = 0
    CM_count = 0
    CF_count = 0
    SSM_count = 0
    SSF_count = 0
    MWM_count = 0
    MWF_count = 0
    GL_count = 0
    OS_count = 0
    
    data = cur.fetchall()
    for row in data:
#         print row
    #     print row[0], row[1].encode('utf8'), row[2]
        if row[4]=='CL':
            CL_count+=1
        if row[4]=='BF':
            BF_count+=1
        if row[4]=='JS':
            JS_count+=1
        if row[4]=='YM':
            YM_count+=1
        if row[4]=='YF':
            YF_count+=1
        if row[4]=='CM':
            CM_count+=1
        if row[4]=='CF':
            CF_count+=1
        if row[4]=='SSM':
            SSM_count+=1
        if row[4]=="SSF":
            SSF_count+=1
        if row[4]=='MWM':
            MWM_count+=1
        if row[4]=='MWF':
            MWF_count+=1    
        if row[4]=='GL':
            GL_count+=1
        if row[4]=='OS':
            OS_count+=1   
    if verbose:        
        print "CL:", CL_count
        print "BF:", BF_count
        print "JS:", JS_count
        print "YM:", YM_count
        print "YF:", YF_count
        print "CM:", CM_count
        print "CF:", CF_count
        print "SSM:", SSM_count
        print "SSF:", SSF_count
        print "MWM:", MWM_count
        print "MWF:", MWF_count
        print "GL:", GL_count
        print "OS:", OS_count
        print "Total members:", CL_count+BF_count+JS_count+YM_count+YF_count+CM_count+CF_count+SSM_count+SSF_count+MWM_count+MWF_count+GL_count+OS_count
    
    d = collections.OrderedDict()
    d['CL'] = CL_count
    d['BF'] = BF_count
    d['JS'] = JS_count
    d['YM'] = YM_count
    d['YF'] = YF_count
    d['CM'] = CM_count
    d['CF'] = CF_count
    d['SSM'] = SSM_count
    d['SSF'] = SSF_count
    d['MWM'] = MWM_count
    d['MWF'] = MWF_count
    d['GL'] = GL_count
    d['OS'] = OS_count    
    
    db.close()
    return d

def plot_dept_stats():
    '''
    Plots a bar chart of the number of members in each dept
    '''
    members_count = calc_num_all_dept(verbose=True)
#     plt.figure(figsize=(15,10))
    plt.grid(True)
    plt.title("LWC Members Distribution")
    plt.xlabel("Department")
    plt.ylabel("Number of members")
    plt.bar(range(len(members_count)), members_count.values(), align='center')
    plt.xticks(range(len(members_count)), members_count.keys())
#     plt.show()



def calc_att_by_category(month, year, event_type, dbhostip="127.0.0.1"):
    '''
    Plots the attendance statistics for entire church given event and month
    '''
    db = mdb.connect(charset='utf8', host=dbhostip, user="root", passwd="root", db="lwc_members")
    cur = db.cursor()
    cur.execute("SELECT * FROM member_attendance_summary WHERE event_type='%s' AND month(event_date)=%d AND year(event_date)=%d " % (event_type, month, year) )
    data = cur.fetchall()
    
    # if there is no data just return all as absent
    if data == ():
        cur.execute("SELECT COUNT(*) FROM event_test WHERE event_type='%s' " % event_type)
        num_events = cur.fetchall()[0]
        cur.execute("SELECT COUNT(*) FROM members_list WHERE membership_status='Active'")
        num_members = cur.fetchall()[0]
        
        total_days_counted = (num_members[0]*num_events[0])
        
        present_count = 0
        broadcast_count = 0
        absent_count = total_days_counted - (present_count + broadcast_count)
        import calendar
        print "### Overall church Attendance (%s) ###" % event_type
        print "There are %d members in our church and %d events of %s in the month of %s, %d" % (num_members[0], num_events[0], event_type, calendar.month_name[month], year )
        print "Total days counted for the above criteria is %d" % (total_days_counted)
        print "Present:", present_count
        print "Broadcast:", broadcast_count
        print "Absent:", absent_count
    
#         print present_count, broadcast_count, absent_count
        return present_count, broadcast_count, absent_count 
    
    # if there is data
    present_count = 0
    broadcast_count = 0
    for row in data:
#         print row[4]
        if row[4]=='P':
            present_count+=1
        if row[4]=='B':
            broadcast_count+=1
    
    cur.execute("SELECT COUNT(*) FROM event_test WHERE event_type='%s' AND MONTH(event_date)='%s' AND YEAR(event_date)='%s' " % (event_type, month, year) )
    num_events = cur.fetchall()[0]
    cur.execute("SELECT COUNT(*) FROM members_list WHERE membership_status='Active'")
    num_members = cur.fetchall()[0]
    
    # total days counted is num of members * num of events
    total_days_counted = (num_members[0]*num_events[0])
    # count total absentees by subtracting P and B from the total number of events for all members
    absent_count = total_days_counted - (present_count + broadcast_count)
    import calendar
    print "### Overall church Attendance (%s) ###" % event_type
    print "There are %d members in our church and %d events of %s in the month of %s, %d" % (num_members[0], num_events[0], event_type, calendar.month_name[month], year )
    print "Total days counted for the above criteria is %d" % (total_days_counted)
    print "Present:", present_count
    print "Broadcast:", broadcast_count
    print "Absent:", absent_count
    
#     print present_count, broadcast_count, absent_count
#     print present_count, broadcast_count, absent_count
    db.close()
    return present_count, broadcast_count, absent_count
    
     
#     plt.pie([present_count, broadcast_count, absent_count], labels=["Present", "Broadcast", "Absent"],autopct='%1.1f%%',
#             colors = ['green', 'yellow', 'red'])
#     plt.title("Attendance Statistics for %s for month %d, %d"  % (event_type, month, year))
    
    
#     plt.tight_layout(pad=0.5)
#     plt.axis('equal')
#     plt.show()

def calc_att_by_category_alldept(month, year, event_type, dbhostip="127.0.0.1"):
    '''
    Plots the attendance statistics for entire church given event and month for each department
    '''
    db = mdb.connect(charset='utf8', host=dbhostip, user="root", passwd="root", db="lwc_members")
    cur = db.cursor()
    dept_list = ["CL", "BF", "JS", "YM", "YF", "CM", "CF", "SSM", "SSF", "MWM", "MWF", "GL", "OS" ]
    d_present = collections.OrderedDict()
    d_broadcast = collections.OrderedDict()
    d_absent = collections.OrderedDict()
    
    for dept in dept_list:
        
        cur.execute("SELECT * FROM member_attendance_summary WHERE event_type='%s' AND month(event_date)=%d AND year(event_date)=%d AND dept='%s' "  % (event_type, month, year, dept) )
        data = cur.fetchall()
        
        # if there is no present member at all
        if data == ():
            cur.execute("SELECT COUNT(*) FROM event_test WHERE event_type='%s' " % event_type)
            num_events = cur.fetchall()[0]
            cur.execute("SELECT COUNT(*) FROM members_list WHERE dept='%s' AND membership_status='Active'" % dept)
            num_members = cur.fetchall()[0]
            total_days_counted = (num_members[0]*num_events[0])
            present_count=0
            broadcast_count=0
            absent_count = total_days_counted - (present_count + broadcast_count)
#             print "Total days counted for %s dept in month %d is %d " % (dept, month, total_days_counted)
            present_pcnt = present_count/total_days_counted * 100.00
#             print "Present %s: %d, %4.2f %%" % (dept, present_count, present_pcnt)
            broadcast_pcnt = broadcast_count/total_days_counted * 100.00
#             print "Broadcast %s: %d, %4.2f %%" % (dept, broadcast_count, broadcast_pcnt)
            absent_pcnt = absent_count/total_days_counted * 100.00
#             print "Absent %s: %d, %4.2f %%" % (dept, absent_count, absent_pcnt)
#             overall_dept_att.append((present_count, broadcast_count, absent_count))
            d_present['%s'%dept] = present_count
            d_broadcast['%s'%dept] = broadcast_count
            d_absent['%s'%dept] = absent_count

        
        present_count = 0
        broadcast_count = 0
        for row in data:
    #         print row[4]
            if row[4]=='P':
                present_count+=1
            if row[4]=='B':
                broadcast_count+=1
        
        cur.execute("SELECT COUNT(*) FROM event_test WHERE event_type='%s' AND MONTH(event_date)='%s' AND YEAR(event_date)='%s' " % (event_type, month, year) )
        num_events = cur.fetchall()[0]
        cur.execute("SELECT COUNT(*) FROM members_list WHERE dept='%s' AND membership_status='Active'" % dept)
        num_members = cur.fetchall()[0]
        
        # total days counted is num of members * num of events
        total_days_counted = (num_members[0]*num_events[0])
        # count total absentees by subtracting P and B from the total number of events for all members
        absent_count = total_days_counted - (present_count + broadcast_count)
        
#         print "Total days counted for %s dept in month %d is %d " % (dept, month, total_days_counted)
        present_pcnt = round(present_count/total_days_counted * 100.0 ,2)
#         print "Present %s: %d, %4.2f %%" % (dept, present_count, present_pcnt)
        broadcast_pcnt = round(broadcast_count/total_days_counted * 100.0 ,2)
#         print "Broadcast %s: %d, %4.2f %%" % (dept, broadcast_count, broadcast_pcnt)
        absent_pcnt = round(absent_count/total_days_counted * 100.0 ,2)
#         print "Absent %s: %d, %4.2f %%" % (dept, absent_count, absent_pcnt)

        d_present['%s'%dept] = present_pcnt
        d_broadcast['%s'%dept] = broadcast_pcnt
        d_absent['%s'%dept] = absent_pcnt
        
#         print d_present
#         print d_broadcast
#         print d_absent
    db.close()
    return d_present, d_broadcast, d_absent
    



# def plot_predawn_daily_attendance(year, month):
#     '''
#     Plot a line graph showing attendance for each day for each week
#     '''
#     db = mdb.connect(charset='utf8', host="127.0.0.1", user="root", passwd="root", db="lwc_members")
#     cur = db.cursor()
#     days = monthrange(year, month)
#     
#     fig = plt.Figure()
#     cur.execute("SELECT event_date, COUNT(*) as broadcast FROM `member_attendance_summary` WHERE status='B' GROUP BY event_date")
#     data = cur.fetchall()
#     data = list(data)
# #     print type(data)
#     
#     points = []
#     for point in data:
# #         print point
#         points.append(point[1])
#     plt.plot(range(1,days[1]),points, label="Broadcast")
#     
#     
#     cur.execute("SELECT event_date, COUNT(*) as present FROM `member_attendance_summary` WHERE status='P' GROUP BY event_date")
#     data = cur.fetchall()
#     data = list(data)
# #     print type(data)
#     
#     points = []
#     for point in data:
# #         print point
#         points.append(point[1])
#     plt.plot(range(1,days[1]),points, label="Present")
#     
#     plt.grid(True)
#     plt.legend(loc=4)
#     plt.show()
    

    
def plot_service_daily(month, year, event_type, dbhostip="127.0.0.1"):
    db = mdb.connect(charset='utf8', host=dbhostip, user="root", passwd="root", db="lwc_members")
    cur = db.cursor()
    days = range(1,monthrange(year, month)[1]+1) 
#     print days
    
    present_list = []
    for day in days:
        cur.execute("SELECT count(*) FROM member_attendance_summary WHERE DAY(event_date)=%d AND MONTH(event_date)=%d AND YEAR(event_date)=%d \
        AND event_type='%s' AND status='P' " % (day,month,year, event_type))
        count = cur.fetchall()[0][0] 
        present_list.append(count) 
        
    broadcast_list = []
    for day in days:
        cur.execute("SELECT count(*) FROM member_attendance_summary WHERE DAY(event_date)=%d AND MONTH(event_date)=%d AND YEAR(event_date)=%d \
        AND event_type='%s' AND status='B' " % (day,month,year,event_type))
        count = cur.fetchall()[0][0] 
        broadcast_list.append(count) 
    
#     print present_list
#     print broadcast_list
    db.close()
    return present_list, broadcast_list, days
    
# plot_dawn_service_daily(month=10, year=2015)
# print calc_att_by_category(year=2015, month=10, event_type="Sunday Service")

# print calc_att_by_category_alldept(month=10, year=2015, event_type="Sunday Service")

# calc_num_all_dept(True)




