import MySQLdb as mdb
import datetime
from datetime import timedelta, date

db = mdb.connect(charset='utf8', host="127.0.0.1", user="root", passwd="root", db="lwc_members")
cur = db.cursor()

cur.execute("SELECT * FROM event_test" )
data = cur.fetchall()


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)
        
start_date = date(2015, 1, 1)
end_date = date(2023, 12, 31)
for single_date in daterange(start_date, end_date):
    print single_date.strftime("%Y-%m-%d, %A")
    cur.execute("INSERT INTO event_test VALUES(Null, 'Dawn Service:%s', '%s', 'Dawn Service')" % (single_date, single_date) )
    if single_date.strftime('%A') == 'Sunday':
        cur.execute("INSERT INTO event_test VALUES(Null, 'Sunday Service:%s', '%s', 'Sunday Service')" % (single_date, single_date) )
    if single_date.strftime('%A') == 'Wednesday':
        cur.execute("INSERT INTO event_test VALUES(Null, 'Wednesday Service:%s', '%s', 'Wednesday Service')" % (single_date, single_date) )
    if single_date.strftime('%A') == 'Friday':
        cur.execute("INSERT INTO event_test VALUES(Null, 'Wednesday Service:%s', '%s', 'Friday Prayer Meeting')" % (single_date, single_date) )
db.commit()
db.close()


    

