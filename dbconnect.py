import MySQLdb



def dbHRDPlan():
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="root",
                           passwd="",
                           db="db_hrdplan",
                           charset='utf8',
                           use_unicode=True)
    cur = conn.cursor()
    return cur
