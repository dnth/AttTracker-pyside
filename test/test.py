import MySQLdb as mdb
import sys



def search_database_for_member_id(rfid):
        '''
        Search databse for member identity and print
        param: id reader
        return: member_id 
        '''
        db = mdb.connect(charset='utf8', host='127.0.0.1', user="root", passwd="root", db="lwc_members")
        cur = db.cursor()
        cur.execute("SELECT * FROM members_list WHERE rfid_num='%s' AND membership_status='Active' " % rfid)
        mysql_data = cur.fetchall()
        return mysql_data
    

print sys.getdefaultencoding()
print sys.getfilesystemencoding() 
member_data = search_database_for_member_id("07001BAC1AAA")

print member_data[0][2].encode('utf-8')