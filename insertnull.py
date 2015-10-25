
import MySQLdb as mdb

db = mdb.connect(charset='utf8', host="127.0.0.1", user="root", passwd="root", db="lwc_members")
cur = db.cursor()

rfid = None
cur.execute("UPDATE members_list SET rfid_num=NULL WHERE id=69")
db.commit()

# cur.execute("UPDATE members_list SET rfid_num='%s', chi_name='%s', eng_name='%s', dept='%s', gender='%s', membership_status='%s', dob='%s', passing_date='%s', contact_num='%s' WHERE id=%d " 
#             % (rfid_num,chi_name,eng_name,dept,gender,status,dob,passing_date,contact_num,idnum))