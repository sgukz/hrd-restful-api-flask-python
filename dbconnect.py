import MySQLdb

def dbPayroll():
    conn = MySQLdb.connect(
        host="192.168.0.251",
        user="sgdev",
        passwd="$Guk4210",
        db="payroll",
        charset='tis620',
        use_unicode=True
    )
    cur = conn.cursor()
    return cur


# def dbbackoffice():
#     conn = MySQLdb.connect(
#         host="localhost",
#         user="root",
#         passwd="root",
#         db="backoffice_db",
#         charset='utf8',
#         use_unicode=True)
#     c = conn.cursor()

#     return c