from flask import Flask, jsonify, request, json, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_restplus import Api, Resource, fields
import MySQLdb
import datetime

app = Flask(__name__)
api = Api(app)

### Connect Database First
app.config['MYSQL_USER'] = 'sgdev'
app.config['MYSQL_PASSWORD'] = '$Guk4210'
app.config['MYSQL_DB'] = 'payroll'
app.config['MYSQL_HOST'] = '192.168.0.251'
#app.config['MYSQL_USE_UNICODE'] = 'utf8'
app.config['MYSQL_CHARSET'] = 'tis620'
#app.config['MYSQL_PORT'] = '3306'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
CORS(app)
now = datetime.datetime.now()

### Connect Database Second
# dbhrd = MySQLdb.connect(
#     host="localhost",
#     user="root",
#     passwd="",
#     db="hrd",
#     charset='utf8',
#     use_unicode=True)
dbhrd = MySQLdb.connect(
    host="192.168.0.251",
    user="sgdev",
    passwd="$Guk4210",
    db="hrd",
    charset='utf8',
    use_unicode=True)

ns = api.namespace('api', description='Data Payroll Employee REH')

def getIdcard(fullname):
    strName = fullname.split()
    cur = mysql.connection.cursor()
    sql = """SELECT *, CONCAT(pname,fname,' ',lname) as fullname FROM payroll_employee
            WHERE fname = '%s' AND lname = '%s'
            HAVING is_expire <> 'Y'""" % (strName[0], strName[1])
    cur.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    cur.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

def getDepartment(dep):
    strDep = "%"+dep+"%"
    curs = dbhrd.cursor()
    sql = """SELECT * FROM department WHERE dep_code_name LIKE '%s'""" % (strDep)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

def getTravel(travel):
    strTravel = "%"+travel+"%"
    curs = dbhrd.cursor()
    sql = """SELECT * FROM meeting_travel WHERE travel_name LIKE '%s'""" % (strTravel)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


def getPosition(idcard):
    curs = dbhrd.cursor()
    sql = """SELECT pos_no FROM personal WHERE pid = '%s'""" % (idcard)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


@ns.route('/rehuser')
class Employee(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                """SELECT *, idcard, CONCAT(fname,' ',lname) as fullname FROM payroll_employee 
                    HAVING is_expire <> 'Y' AND idcard <> "" 
                    ORDER BY fname""")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return str(e)

@ns.route('/position')
class HRDPositions(Resource):
    def get(self):
        try:
            curs = dbhrd.cursor()
            curs.execute("SELECT * FROM position ORDER BY pos_name")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            curs.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return str(e)

@ns.route('/department')
class HRDDepart(Resource):
    def get(self):
        try:
            curs = dbhrd.cursor()
            curs.execute("SELECT * FROM department ORDER BY dep_code_name")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            curs.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return str(e)

@ns.route('/login')
class HRDLogin(Resource):
    def post(self):
        try:
            data_json = request.json
            idcard = data_json["auth"]["idcard"]
            # passpwd = data_json["auth"]["password"]
            cur = mysql.connection.cursor()
            sql = """SELECT emp.*, p.* ,emp.idcard, CONCAT(emp.fname,' ',emp.lname) as fullname , COUNT(emp.idcard) chkLog
                    FROM payroll.payroll_employee emp 
                    LEFT JOIN hrd.personal p ON emp.idcard = p.pid
                    WHERE emp.idcard = '%s'
                    HAVING emp.is_expire <> 'Y'""" % (idcard)
            cur.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)

        except Exception as err:
            return err


@ns.route('/profile/<idcard>')
class HRDUpdateProfile(Resource):
    def get(self, idcard):
        try:
            curs = dbhrd.cursor()
            sql = """SELECT * FROM personal per
                    JOIN position pos ON per.pos_no = pos.pos_no
                    WHERE per.pid = '%s'""" % (idcard)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            curs.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return str(e)


@ns.route('/profile')
class HRDProfile(Resource):
    def post(self):
        try:
            fields = ""
            idcard = ""
            data_json = request.json
            data = []
            for key in data_json["profile"]:
                if key != "dep_name":
                    if key == "idcard":
                        idcard = str(data_json["profile"][key])
                    else:
                        if key == "pos_no":
                            fields += str(key) + " = '" + str(data_json["profile"][key]) + "'"
                        else:
                            fields += str(key) + " = '" + str(data_json["profile"][key]) + "',"
                else:
                    fields += ""
            sql = """UPDATE personal SET %s
                WHERE pid= '%s'
                """ % (fields, idcard)
            curs = dbhrd.cursor()
            curs.execute(sql)

            data.append({"status": 200,"msg" :"OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


@ns.route('/register/add')
class HRDMeetingAdd(Resource):
    def post(self):
        try:
            fields = ""
            values = ""
            fields_partner = ""
            values_partner = ""
            data = []
            data_json = request.json
            year = int(now.strftime("%Y"))
            yearTH = str(year + 543)
            shortYear = yearTH[2:]
            curs = dbhrd.cursor()
            curs.execute(
                "SELECT MAX(code_num) code_num FROM meeting_register WHERE code_y = '"
                + shortYear + "'")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))

            code_number = 0
            for key in json_data:
                for k, v in key.items():
                    code_number += v + 1

            code_map = '%04d' % code_number
            code_master = shortYear + str(code_map)
            addField = "code_y, code_num, code_master, "
            fields += addField
            fields_partner += addField + "re_date, fullname , cid_account, cid_account_recoder, employee_type, emp_position, department, department_money, travel_type"
            values += str(shortYear)+ "," + str(code_number) +","+str(code_master)+","
            values_partner += str(shortYear)+ "," + str(code_number) +","+str(code_master)+","

            addFieldPartner = ""
            re_date = ""
            fullname = ""
            cid_account = ""
            employee_type = ""
            emp_position = ""
            dep_code_id = ""
            travel_type = ""
            idcard = ""
            employee_type = ""
            department = ""
            travel = ""
            pos_no = ""
            recoder = ""

            for key in data_json["register"]:
                if key != "cid_account_recoder":
                    if key == "expense_total":
                        if data_json["register"][key] is not None:
                            fields += str(key) + ","
                            expense_total = int(data_json["register"]["expense_bus"])+int(data_json["register"]["expense_fuel"])+int(data_json["register"]["expense_airplane"])+int(data_json["register"]["expense_owncar"])+int(data_json["register"]["expense_residence"])+int(data_json["register"]["expense_register_meeting"])+int(data_json["register"]["expense_allowance"])+int(data_json["register"]["expense_other"])
                            values += str(expense_total)+","
                        else:
                            values += """'',"""
                    else:
                        fields += str(key) + ","
                        if data_json["register"][key] is not None:
                            if data_json["register"][key] == True:
                                data_json["register"][key] = 1
                            elif data_json["register"][key] == False:
                                data_json["register"][key] = 0
                            values += "'" + str(data_json["register"][key]) + "',"
                        else:
                            values += """'',"""
                else:
                    fields += key
                    if data_json["register"][key] is not None:
                        if data_json["register"][key] == "True":
                            data_json["register"][key] = 1
                        elif data_json["register"][key] == "False":
                            data_json["register"][key] = 0
                        values += "'" + str(data_json["register"][key])+"'"
                    else:
                        values += """''"""

            fields += ", date_time_save"
            values += ",'" + now.strftime("%Y-%m-%d %H:%M:%S") + "'"
            sql = """INSERT INTO meeting_register(%s)
                    VALUES(%s)
                    """ % (fields, values)
            try:
                print(sql)
                curs.execute(sql)
                # ### insert meeting_partner ###
                for key_partner in data_json["register_partner"]:
                    for k, v in key_partner.items():
                        if k == "fullname":
                            name = str(v)
                            payroll_data = getIdcard(name)
                            for key_payroll in payroll_data:
                                for k_pay, v_pay in key_payroll.items():
                                    if k_pay == "idcard":
                                        idcard = v_pay
                                        position_data = getPosition(idcard)
                                        for key_position in position_data:
                                            for k_pos, v_pos in key_position.items():
                                                pos_no = str(v_pos)
                                    elif k_pay == "type_name":
                                        employee_type = v_pay
                                    elif k_pay == "fullname":
                                        fullname = str(v_pay)
                        elif k == "re_date":
                            re_date = str(v)
                        elif k == "dep":
                            department = str(v)
                            depart_data = getDepartment(department)
                            for key_depart in depart_data:
                                for k_depart, v_depart in key_depart.items():
                                    if k_depart == "dep_code_id":
                                        dep_code_id = str(v_depart)
                        elif k == "travel":
                            travel = str(v)
                            travel_data = getTravel(travel)
                            for key_travel in travel_data:
                                for k_tarvel, v_travel in key_travel.items():
                                    if k_tarvel == "travel_id":
                                        travel_type = v_travel
                        elif k == "recoder":
                            recoder = str(v)
                    val_part = values_partner + "'" + re_date + "', '" + fullname + "','" + idcard +"','"+recoder+ "','" + employee_type + "','" + str(pos_no) +"','" + dep_code_id + "', '" + dep_code_id + "'," +str(travel_type)
                    sql_partner = """INSERT INTO meeting_register_partner(%s) VALUES(%s)""" % (fields_partner, val_part)
                    print(sql_partner)
                    curs.execute(sql_partner)
                ### END insert meeting_partner ###

                data.append({"status": 200,"msg" :"OK"})
                return jsonify(data)
            except Exception as e:
                data.append({"status": 400, "msg": str(e)})
                return jsonify(data)
        except Exception as err:
            print(err)

@ns.route('/register/update')
class HRDMeetingUpdate(Resource):
    def post(self):
        try:
            fields = ""
            fields_partner = ""
            values_partner = ""
            data = []
            code_master = ""
            data_json = request.json
            curs = dbhrd.cursor() ### Connect to database HRD ###
            addFieldPartner = ""
            code_y = ""
            code_num = ""
            codemaster = ""
            re_date = ""
            fullname = ""
            cid_account = ""
            employee_type = ""
            emp_position = ""
            dep_code_id = ""
            travel_type = ""
            idcard = ""
            employee_type = ""
            department = ""
            travel = ""
            pos_no = ""
            recoder = ""
            cid = ""

            for key in data_json["register"]:
                if key != "code_master":
                    if key != "cid_account":
                        if key != "re_date":
                            if key == "expense_total":
                                expense_total = int(data_json["register"]["expense_bus"])+int(data_json["register"]["expense_fuel"])+int(data_json["register"]["expense_airplane"])+int(data_json["register"]["expense_owncar"])+int(data_json["register"]["expense_residence"])+int(data_json["register"]["expense_register_meeting"])+int(data_json["register"]["expense_allowance"])+int(data_json["register"]["expense_other"])
                                fields += str(key) + " = '" + str(expense_total) + "'"
                            else:
                                fields += str(key) + " = '" + str(data_json["register"][key]) + "',"
            code_master = str(data_json["register"]["code_master"])
            cid_account = str(data_json["register"]["cid_account"])
            sql = """UPDATE meeting_register SET %s
                    WHERE code_master = '%s'
                    """ % (fields, code_master)
            # print(sql)
            # print(data_json["register"])
            try:
                #print(sql)
                curs.execute(sql)  ### execute meeting_register ###
                #### Update meeting_partner ###
                trav_type = ""
                for travel_change in data_json['travel_chagne']:
                    for key_t, val_t in travel_change.items():
                        if key_t != "":
                            trav_data = getTravel(str(val_t))
                            for key_trav in trav_data:
                                for k_trav, v_trav in key_trav.items():
                                    if k_trav == "travel_id":
                                        trav_type = str(v_trav)
                sqlTravel = """UPDATE meeting_register_partner
                                SET travel_type = %s
                                WHERE cid_account = '%s' AND code_master = '%s'""" % (trav_type, cid_account, code_master)
                curs.execute(sqlTravel)
                #### End Update meeting_partner ###

                #### insert meeting_partner ###
                fields_partner = "code_y, code_num, code_master, re_date, fullname , cid_account, cid_account_recoder, employee_type, emp_position, department, department_money, travel_type"
                for key_partner in data_json["register_partner"]:
                    for k, v in key_partner.items():
                        if k == "code_y":
                            code_y = str(v)
                        elif k == "code_num":
                            code_num = str(v)
                        elif k == "code_master":
                            codemaster = str(v)
                        elif k == "fullname":
                            name = str(v)
                            payroll_data = getIdcard(name)
                            for key_payroll in payroll_data:
                                for k_pay, v_pay in key_payroll.items():
                                    if k_pay == "idcard":
                                        idcard = v_pay
                                        position_data = getPosition(idcard)
                                        for key_position in position_data:
                                            for k_pos, v_pos in key_position.items():
                                                pos_no = str(v_pos)
                                    elif k_pay == "type_name":
                                        employee_type = v_pay
                                    elif k_pay == "fullname":
                                        fullname = str(v_pay)
                        elif k == "re_date":
                            re_date = str(v)
                        elif k == "dep":
                            department = str(v)
                            depart_data = getDepartment(department)
                            for key_depart in depart_data:
                                for k_depart, v_depart in key_depart.items():
                                    if k_depart == "dep_code_id":
                                        dep_code_id = str(v_depart)
                        elif k == "travel":
                            travel = str(v)
                            travel_data = getTravel(travel)
                            for key_travel in travel_data:
                                for k_tarvel, v_travel in key_travel.items():
                                    if k_tarvel == "travel_id":
                                        travel_type = v_travel
                        elif k == "recoder":
                            recoder = str(v)
                        elif k == "cid":
                            cid = str(v)
                    if cid == '':
                        val_part = code_y+", "+code_num+", "+codemaster+", '"+ re_date + "', '" + fullname + "','" + idcard + "','" + recoder + "','" + employee_type + "','" + str(pos_no) + "','" + dep_code_id + "', '" + dep_code_id + "'," + str(travel_type)
                        sql_partner = """INSERT INTO meeting_register_partner(%s) VALUES(%s)""" % (fields_partner, val_part)
                        #print(sql_partner)
                        curs.execute(sql_partner) ### execute meeting_register_partner ###
                    ### END insert meeting_partner ###
                data.append({"status": 200,"msg" :"OK"})
                return jsonify(data)
            except Exception as e:
                #return str(r)
                data.append({"status": 400, "msg": str(e)})
                return jsonify(data)
        except Exception as err:
            return str(err)


@ns.route('/register/<idcard>')
class getRegisterAll(Resource):
    def get(self, idcard):
        try:
            curs = dbhrd.cursor()
            sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your,mrp.cid_account as cid_partner, "true" as isActive
                    FROM meeting_register mr 
                    JOIN meeting_register_partner mrp ON mr.code_master = mrp.code_master 
                    JOIN meeting_type mt ON mr.meeting_type = mt.meeting_type_code
                    WHERE mrp.cid_account = '%s'
                    ORDER BY mr.date_time_save DESC""" % (idcard)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            curs.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return e

@ns.route('/register/delete/<re_id>')
class deleteMeeting(Resource):
    def get(self, re_id):
        try:
            curs = dbhrd.cursor()
            sql = """SELECT code_master FROM meeting_register WHERE re_id = '%s' LIMIT 1""" % (re_id)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            code_master = json_data[0]['code_master']

            try:
                delete_meeting = """DELETE FROM meeting_register
                                    WHERE re_id = '%s'
                                    """ % (re_id)
                curs.execute(delete_meeting)
                delete_meeting_part = """DELETE FROM meeting_register_partner
                                        WHERE code_master = '%s'
                                        """ % (code_master)
                curs.execute(delete_meeting_part)
                data.append({
                    "status":
                    200,
                    "msg": "OK"
                })
                return jsonify(data)
            except Exception as err:
                data.append({"status": 400, "msg": str(err)})
                return jsonify(data)
        except Exception as e:
            return e

@ns.route('/register/edit/<cid_account>/<code_master>')
class editMeeting(Resource):
    def get(self,cid_account, code_master):
        try:
            curs = dbhrd.cursor()
            sql = """SELECT * FROM meeting_register mr
                    JOIN meeting_register_partner mrp ON mr.code_master = mrp.code_master
                    JOIN meeting_travel mt ON mrp.travel_type = mt.travel_id
                    WHERE mrp.cid_account = '%s' AND mr.code_master = '%s' LIMIT 1""" % (cid_account, code_master)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)

        except Exception as e:
            return str(e)

@ns.route('/register/partner/<cid_account>/<code_master>')
class partnerMeeting(Resource):
    def get(self, cid_account, code_master):
        try:
            curs = dbhrd.cursor()
            sql = """SELECT * FROM meeting_register_partner mrp
                        JOIN department d ON mrp.department = d.dep_code_id
                        JOIN meeting_travel mt ON mrp.travel_type = mt.travel_id
                    WHERE mrp.code_master = '%s'
                        HAVING mrp.cid_account <> '%s'
                    """ % (code_master,cid_account)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)

        except Exception as e:
            return str(e)


@ns.route('/register/deletepartner/<cid_account>/<code_master>')
class deletePartnerMeeting(Resource):
    def get(self,cid_account, code_master):
        try:
            curs = dbhrd.cursor()
            sql = """DELETE FROM meeting_register_partner
                    WHERE cid_account = '%s' AND code_master = '%s'
                    """ % (cid_account, code_master)
            curs.execute(sql)
            data = []
            # แยกส่วนหัวของแถว
            data.append({
                "status": 200,
                "msg": "OK"
            })
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


def getPersonal(idcard):
    curs = dbhrd.cursor()
    sql = """SELECT COUNT(pid) as cnt FROM personal WHERE pid = '%s'""" % (idcard)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

def getPrefix(pname):
    curs = dbhrd.cursor()
    sql = """SELECT pcode FROM prefix WHERE longprefix = '%s'""" % (pname)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

@ns.route('/personal')
class updatePersonal(Resource):
    def get(self):
        try:
            cur = mysql.connection.cursor()
            sql = """SELECT * FROM payroll_employee
                    WHERE idcard IS NOT NULL 
                    HAVING is_expire <> 'Y'"""
            cur.execute(sql)
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            cid = ""
            pname = ""
            pcode = ""
            fname = ""
            lname = ""
            fields = "pid, pcode, fname, lname"
            num_rows = 0
            for key in json_data:
                for k, v in key.items():
                    if k == "idcard":
                        cid = str(v)
                    elif k == "pname":
                        pname = str(v)
                        data_prefix = getPrefix(pname)
                        for key_code in data_prefix:
                            for k_code, v_code in key_code.items():
                                pcode = str(v_code)
                    elif k == "fname":
                        fname = str(v)
                    elif k == "lname":
                        lname = str(v)

                checkCID = getPersonal(cid)
                for key_cnt in checkCID:
                    for k_c, v_c in key_cnt.items():
                        if v_c == 0:
                            result = "'"+cid + "' ,'" + pcode + "' ,'"+fname+"' ,'"+lname+"'"
                            query = """INSERT INTO personal(%s) VALUES(%s)""" % (fields, result)
                            print(query)
                            curs = dbhrd.cursor()
                            curs.execute(query)
            # return jsonify(json_data)
            # for key in json_data:
            #     for k, v in key.items():
            #         code_number += v + 1
            # # แยกส่วนหัวของแถว
            data.append({
                "status": 200,
                "msg": "OK"
            })
            return jsonify(data)
        except Exception as err:
            return err
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)

if __name__ == '__main__':
    #app.run(debug=True)
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
