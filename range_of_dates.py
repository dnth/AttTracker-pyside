import datetime
import calendar
from datetime import date, timedelta as td
# from read_graph_tables import plot_service_daily
import matplotlib.pyplot as plt
from calendar import monthrange
import MySQLdb as mdb
import matplotlib.ticker as plticker


# 
# for i in range(delta.days + 1):
#     print d1 + td(days=i)




        
def plot_service_daily(month, year, event_type, dbhostip="127.0.0.1"):
    db = mdb.connect(charset='utf8', host=dbhostip, user="root", passwd="root", db="lwc_members")
    cur = db.cursor()
    days = range(1,monthrange(year, month)[1]+1) 
#     print days

    d1 = date(year, month, 1)
    d2 = date(year, month, calendar.monthrange(year, month)[1])# get last day of the month
    delta = d2 - d1
    date_list = [d1+td(days=i) for i in range(delta.days+1)]
    print date_list
    
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
    return present_list, broadcast_list, days, date_list

daily_present_list, daily_broadcast_list, days, date_list = plot_service_daily(month=11, year=2015, event_type="Dawn Service")

daily_present_rects = plt.bar(date_list, daily_present_list, align='center', color="g", label="Present", width=1 )
plt.show()