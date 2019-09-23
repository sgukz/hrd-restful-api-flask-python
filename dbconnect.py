import MySQLdb


def dbPayroll():
    conn = MySQLdb.connect(host="192.168.0.251",
                           user="sgdev",
                           passwd="$Guk4210",
                           db="payroll",
                           charset='tis620',
                           use_unicode=True)
    cur = conn.cursor()
    return cur


def dbKPI():
    conn = MySQLdb.connect(host="192.168.0.251",
                           user="sgdev",
                           passwd="$Guk4210",
                           db="db_kpi",
                           charset='tis620',
                           use_unicode=True)
    cur = conn.cursor()
    return cur
