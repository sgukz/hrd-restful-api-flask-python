from flask import Flask, jsonify, request, json, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_restplus import Api, Resource, fields
import MySQLdb
import datetime

app = Flask(__name__)
api = Api(app)

### Connect Database First
# app.config['MYSQL_USER'] = 'sgdev'
# app.config['MYSQL_PASSWORD'] = '$Guk4210'
# app.config['MYSQL_DB'] = 'payroll'
# app.config['MYSQL_HOST'] = '192.168.0.251'
# app.config['MYSQL_CHARSET'] = 'tis620'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'payroll'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_CHARSET'] = 'utf8'

mysql = MySQL(app)
CORS(app)
now = datetime.datetime.now()

ns = api.namespace('api', description='Data Payroll Employee REH')
ns_login = api.namespace('login', description='เข้าสู่ระบบ HRD')
ns_member = api.namespace('users', description='ข้อมูลบุคลากรจากการเงิน')
ns_hrd = api.namespace('hrd', description='จัดการข้อมูลขออนุมัติไปราชการ')
ns_department = api.namespace('department', description='จัดการข้อมูลหน่วยงาน')


### เข้าสู่ระบบ ###
@ns_login.route('/v1', methods=['POST'])
class HRDLogin(Resource):
    def post(self):
        try:
            data_json = request.json
            idcard = data_json["auth"]["idcard"]
            # passpwd = data_json["auth"]["password"]
            cur = mysql.connection.cursor()
            sql = """SELECT emp.*, p.* , 
                reh.position_name posname, reh.degree,
                CASE
                	WHEN reh.degree = "ทรงคุณวุฒิ" THEN CONCAT(reh.position_name,'',reh.degree)
                	WHEN reh.degree = "ชำนาญการพิเศษ" THEN CONCAT(reh.position_name,'',reh.degree)
                	WHEN reh.degree = "ชำนาญการ" THEN CONCAT(reh.position_name,'',reh.degree)
                	WHEN reh.degree = "ปฏิบัติการ" THEN CONCAT(reh.position_name,'',reh.degree)
                	WHEN reh.degree = "ปฏิบัติงาน" THEN CONCAT(reh.position_name,'',reh.degree)
                	WHEN reh.degree = "เชี่ยวชาญ" THEN CONCAT(reh.position_name,'',reh.degree)
                	ELSE reh.position_name
                END as positionname
                ,emp.idcard, CONCAT(emp.fname,' ',emp.lname) as fullname , COUNT(emp.idcard) chkLog
                FROM payroll.payroll_employee emp 
                LEFT JOIN hrd.personal p ON emp.idcard = p.pid
                LEFT JOIN officerdata_db.reh_employee_tb reh ON emp.idcard = reh.cid
                WHERE emp.idcard = '%s' AND emp.is_expire <> 'Y'""" % (idcard)
            cur.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            # print(sql)
            # print(json_data)
            return jsonify(json_data)
        except Exception as err:
            json_data.append({"msg": err})
            return jsonify(json_data)


### ข้อมูลบุคลากรจากการเงิน ###
@ns_member.route('/rehuser', methods=['GET'])
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


### ดึงข้อมูลหน่วยงานทั้งหมด ###
@ns_hrd.route('/department', methods=['GET'])
class HRDDepart(Resource):
    def get(self):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM hrd.department ORDER BY dep_code_name")
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


### จัดการข้อมูลหน่วยงาน ###
@ns_department.route('/create', methods=['POST'])
@ns_department.route('/delete/<depid>', methods=['DELETE'])
@ns_department.route('/view/<depid>', methods=['GET'])
@ns_department.route('/update', methods=['PUT'])
class HRDDepartManage(Resource):
    def get(self, depid):
        try:
            cur = mysql.connection.cursor()
            sql = """SELECT * FROM hrd.department 
                    WHERE dep_code_id = '%s' 
                    ORDER BY dep_code_name""" % (depid)
            cur.execute(sql)
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

    def post(self):
        try:
            data_json = request.json
            data = []
            depart = data_json['department']
            #print(depart)
            cur = mysql.connection.cursor()
            getMaxId = cur.execute(
                "SELECT MAX(dep_code_id)+1 max_id FROM hrd.department")
            rv = cur.fetchall()
            sql = """INSERT INTO hrd.department(dep_code_id,dep_code_name) VALUES('%s','%s')""" % (
                int(rv[0][0]), depart)
            cur.execute(sql)
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as e:
            data.append({"status": 400, "msg": str(e)})
            return jsonify(data)

    def delete(self, depid):
        try:
            cur = mysql.connection.cursor()
            data = []
            delete = """DELETE FROM hrd.department
                                WHERE dep_code_id = '%s'
                                """ % (depid)
            cur.execute(delete)
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)

    def put(self):
        try:
            cur = mysql.connection.cursor()
            data = []
            data_json = request.json
            depId = data_json['depId']
            depName = data_json['depName'].strip()
            update = """UPDATE hrd.department
                                SET dep_code_name = '%s'
                                WHERE dep_code_id = '%s'
                                """ % (depName, depId)
            #print(update)
            cur.execute(update)
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


### ค้นหาหน่วยงาน ###
@ns_department.route('/search', methods=['post'])
class HRDSearchDepart(Resource):
    def post(self):
        try:
            data_json = request.json['keyword']
            #print(data_json['keyword'])
            like_dep_name = "%" + data_json['keyword'] + "%"
            cur = mysql.connection.cursor()
            if data_json['keyword'] != "":
                sql = """SELECT * FROM hrd.department
                    WHERE dep_code_name LIKE '%s'""" % (like_dep_name)
            else:
                sql = """SELECT * FROM hrd.department ORDER BY dep_code_name"""
            cur.execute(sql)
            #แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return str(e)


### ดึงข้อมูลหน่วยงานตามข้อมูลขอไปราชการ ###
@ns_hrd.route('/depmeeting/<idcard>/<re_id>', methods=['GET'])
class HRDDepartMeeting(Resource):
    def get(self, idcard, re_id):
        try:
            curs = mysql.connection.cursor()
            sql = """SELECT dep_code_name FROM hrd.meeting_register mr
	                JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id
	                JOIN hrd.department d ON mrp.department = d.dep_code_id
	                WHERE mrp.cid_account = '%s' AND mrp.re_id = '%s'""" % (
                idcard, re_id)
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


### ข้อมูลขอไปราชการรายบุคคลและแก้ไขข้อมูลไปราชการ ###
@ns_hrd.route('/<idcard>', methods=['GET'])
@ns_hrd.route('/update', methods=['POST'])
class HRDMeetingUpdate(Resource):
    def get(self, idcard):
        try:
            curs = mysql.connection.cursor()
            sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your,mrp.cid_account as cid_partner, "true" as isActive
                    FROM hrd.meeting_register mr 
                    JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id 
                    JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
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

    def post(self):
        try:
            fields = ""
            fields_partner = ""
            values_partner = ""
            data = []
            code_master = ""
            data_json = request.json
            curs = mysql.connection.cursor()  ### Connect to database HRD ###
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
            regID = ""
            #print(data_json["register"])
            for key in data_json["register"]:
                if key != "re_id":
                    if key != "cid_account":
                        if key != "re_date":
                            if key == "expense_total":
                                expense_total = int(
                                    data_json["register"]["expense_bus"]
                                ) + int(
                                    data_json["register"]["expense_fuel"]
                                ) + int(
                                    data_json["register"]["expense_airplane"]
                                ) + int(
                                    data_json["register"]["expense_owncar"]
                                ) + int(
                                    data_json["register"]["expense_residence"]
                                ) + int(data_json["register"]
                                        ["expense_register_meeting"]) + int(
                                            data_json["register"]
                                            ["expense_allowance"]) + int(
                                                data_json["register"]
                                                ["expense_other"])
                                fields += str(key) + " = '" + str(
                                    expense_total) + "'"
                            else:
                                fields += str(key) + " = '" + str(
                                    data_json["register"][key]) + "',"
            re_id = str(data_json["register"]["re_id"])
            cid_account = str(data_json["register"]["cid_account"])
            sql = """UPDATE hrd.meeting_register SET %s
                    WHERE re_id = '%s'
                    """ % (fields, re_id)
            #print(data_json["register"])
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
                if (trav_type != ""):
                    sqlTravel = """UPDATE hrd.meeting_register_partner
                                SET travel_type = %s
                                WHERE cid_account = '%s' AND re_id = '%s'""" % (
                        trav_type, cid_account, re_id)
                    #print(sqlTravel)
                    curs.execute(sqlTravel)
                #### End Update meeting_partner ###
                queue_number = 0
                #### insert meeting_partner ###
                fields_partner = "re_id, re_date, fullname , cid_account, cid_account_recoder, employee_type, department, department_money, travel_type, queue"
                for key_partner in data_json["register_partner"]:
                    for k, v in key_partner.items():
                        if k == "re_id":
                            regID = str(v)
                        elif k == "fullname":
                            name = str(v)
                            payroll_data = getIdcard(name)
                            for key_payroll in payroll_data:
                                for k_pay, v_pay in key_payroll.items():
                                    if k_pay == "idcard":
                                        idcard = v_pay
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
                        sqlQueue = """SELECT MAX(queue) q_max 
                                     FROM hrd.meeting_register_partner 
                                     WHERE re_id = '%s'""" %(regID)
                        getQueue = curs.execute(sqlQueue)
                        rv = curs.fetchall()
                        maxQueue = rv[0][0]
                        if maxQueue is None:
                            queue_number = queue_number + 1
                        else:
                            queue_number = queue_number + maxQueue
                        #print(sqlQueue)
                        val_part = regID + ", '" + re_date + "', '" + fullname + "','" + idcard + "','" + recoder + "','" + employee_type + "','" + dep_code_id + "', '" + dep_code_id + "'," + str(
                            travel_type) + "," + str(queue_number+1)
                        sql_partner = """INSERT INTO hrd.meeting_register_partner(%s) VALUES(%s)""" % (
                            fields_partner, val_part)
                        # print(sql_partner)
                        # print(maxQueue)
                        # print(queue_number)
                        curs.execute(
                            sql_partner
                        )  ### execute meeting_register_partner ###
                        #queue_number
                    ### END insert meeting_partner ###
                data.append({"status": 200, "msg": "OK"})
                return jsonify(data)
            except Exception as e:
                data.append({"status": 400, "msg": str(e)})
                return jsonify(data)
                #return str(e)
        except Exception as err:
            return str(err)
### เปลี่ยนคนไปราชการแทน ###
@ns_hrd.route('/change/<re_id>/<idcard>', methods=['get'])
class HRDChangePerson(Resource):
    def get(self, re_id, idcard):
        try:
            cur = mysql.connection.cursor()
            data = []
            employee_type = ""
            department = ""
            fullname = ""
            dep_code_id = ""
            sqlUpdate = """UPDATE hrd.meeting_register
                    SET cid_account = '%s',cid_account_recoder = '%s'
                    WHERE re_id = %s
                    """ % (idcard, idcard, re_id)
            cur.execute(sqlUpdate)
            payroll_data = getDataEmployee(idcard)
            for key_payroll in payroll_data:
                for k_pay, v_pay in key_payroll.items():
                    if k_pay == "type_name":
                        employee_type = v_pay
                    elif k_pay == "fullname":
                        fullname = str(v_pay)
                    elif k_pay == "dep_name":
                        department = str(v_pay)
                        depart_data = getDepartment(department)
                        for key_depart in depart_data:
                            for k_depart, v_depart in key_depart.items():
                                if k_depart == "dep_code_id":
                                    dep_code_id = str(v_depart)
            sqlPartner = """UPDATE hrd.meeting_register_partner
                    SET fullname = '%s', cid_account = '%s',cid_account_recoder = '%s',
                    employee_type = '%s', department = '%s'
                    WHERE re_id = %s AND queue = 1
                    """ % (fullname, idcard, idcard, employee_type, dep_code_id, re_id)
            cur.execute(sqlPartner)
            #print(sqlPartner)
            sqlPartnerAll = """UPDATE hrd.meeting_register_partner
                    SET cid_account_recoder = '%s'
                    WHERE re_id = %s
                    """ % (idcard, re_id)
            cur.execute(sqlPartnerAll)
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as e:
            #return e
            data.append({"status": 400, "msg": str(e)})
            return jsonify(data)

### ค้นหาข้อมูลขอไปราชการ ###
@ns_hrd.route('/search', methods=['post'])
class HRDSearchMeeting(Resource):
    def post(self):
        try:
            cur = mysql.connection.cursor()
            data_json = request.json
            keyword = data_json['keyword']
            idcard = data_json['idcard']
            like_meeting_story = "%" + keyword + "%"
            if idcard is None:
                if keyword != "":
                    sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your, "true" as isActive
                        FROM hrd.meeting_register mr
                        JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
                        WHERE mr.cid_account <> "" AND mr.meeting_story LIKE '%s'
                        ORDER BY mr.date_time_save DESC""" % (
                        like_meeting_story)
                else:
                    sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your, "true" as isActive
                        FROM hrd.meeting_register mr
                        JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
                        WHERE mr.cid_account <> "" 
                        ORDER BY mr.date_time_save DESC"""
            else:
                if keyword != "":
                    sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your,mrp.cid_account as cid_partner, "true" as isActive
                            FROM hrd.meeting_register mr
                            JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id
                            JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
                            WHERE mr.meeting_story LIKE '%s' AND mrp.cid_account = '%s'
                            ORDER BY mr.date_time_save DESC""" % (
                        like_meeting_story, idcard)
                else:
                    sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your,mrp.cid_account as cid_partner, "true" as isActive
                        FROM hrd.meeting_register mr
                        JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id
                        JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
                        WHERE mrp.cid_account = '%s'
                        ORDER BY mr.date_time_save DESC""" % (idcard)
            #print(sql)
            cur.execute(sql)
            #แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as e:
            return str(e)


### ข้อมูลการขอไปราชการทั้งหมดและลบข้อมูล ###
@ns_hrd.route('/registerall', methods=['GET'])
@ns_hrd.route('/create', methods=['POST'])
@ns_hrd.route('/delete/<re_id>', methods=['DELETE'])
class getAll(Resource):
    def post(self):
        try:
            fields = ""
            values = ""
            fields_partner = ""
            values_partner = ""
            data = []
            data_json = request.json
            curs = mysql.connection.cursor()

            fields_partner += "re_id, re_date, fullname , cid_account, cid_account_recoder, employee_type, department, department_money, travel_type ,queue"
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
                            expense_total = int(
                                data_json["register"]["expense_bus"]) + int(
                                    data_json["register"]["expense_fuel"]
                                ) + int(
                                    data_json["register"]["expense_airplane"]
                                ) + int(
                                    data_json["register"]["expense_owncar"]
                                ) + int(
                                    data_json["register"]["expense_residence"]
                                ) + int(data_json["register"]
                                        ["expense_register_meeting"]) + int(
                                            data_json["register"]
                                            ["expense_allowance"]) + int(
                                                data_json["register"]
                                                ["expense_other"])
                            values += str(expense_total) + ","
                        else:
                            values += """'',"""
                    else:
                        fields += str(key) + ","
                        if data_json["register"][key] is not None:
                            if data_json["register"][key] == True:
                                data_json["register"][key] = 1
                            elif data_json["register"][key] == False:
                                data_json["register"][key] = 0
                            values += "'" + str(
                                data_json["register"][key]) + "',"
                        else:
                            values += """'',"""
                else:
                    fields += key
                    if data_json["register"][key] is not None:
                        if data_json["register"][key] == "True":
                            data_json["register"][key] = 1
                        elif data_json["register"][key] == "False":
                            data_json["register"][key] = 0
                        values += "'" + str(data_json["register"][key]) + "'"
                    else:
                        values += """''"""

            fields += ", date_time_save"
            values += ",'" + now.strftime("%Y-%m-%d %H:%M:%S") + "'"
            sql = """INSERT INTO hrd.meeting_register(%s)
                    VALUES(%s)
                    """ % (fields, values)
            try:
                #print(sql)
                curs.execute(sql)
                queue_number = 1
                re_id = curs.lastrowid
                values_partner += str(re_id) + ", "
                # ### insert meeting_partner ###
                #print(data_json["register_partner"])
                for key_partner in data_json["register_partner"]:
                    for k, v in key_partner.items():
                        if k == "fullname":
                            name = str(v)
                            payroll_data = getIdcard(name)
                            for key_payroll in payroll_data:
                                for k_pay, v_pay in key_payroll.items():
                                    if k_pay == "idcard":
                                        idcard = v_pay
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
                    val_part = values_partner + "'" + re_date + "', '" + fullname + "','" + idcard + "','" + recoder + "','" + employee_type + "','" + dep_code_id + "', '" + dep_code_id + "'," + str(
                        travel_type) + "," + str(queue_number)
                    sql_partner = """INSERT INTO hrd.meeting_register_partner(%s) VALUES(%s)""" % (
                        fields_partner, val_part)
                    #print(sql_partner)
                    curs.execute(sql_partner)
                    queue_number += 1
                ### END insert meeting_partner ###

                data.append({"status": 200, "msg": "OK"})
                return jsonify(data)
            except Exception as e:
                data.append({"status": 400, "msg": str(e)})
                return jsonify(data)
        except Exception as err:
            return str(err)

    def get(self):
        try:
            curs = mysql.connection.cursor()
            sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your, "true" as isActive
                    FROM hrd.meeting_register mr
	                JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
                    WHERE mr.cid_account <> ""
	                ORDER BY mr.date_time_save DESC"""
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

    def delete(self, re_id):
        try:
            curs = mysql.connection.cursor()
            data = []
            delete_meeting = """DELETE FROM hrd.meeting_register
                                WHERE re_id = '%s'
                                """ % (re_id)
            curs.execute(delete_meeting)
            delete_meeting_part = """DELETE FROM hrd.meeting_register_partner
                                    WHERE re_id = '%s'
                                    """ % (re_id)
            curs.execute(delete_meeting_part)
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


### ดึงข้อมูลขอไปราชการแสดงเพื่อแก้ไขข้อมูล ###
@ns_hrd.route('/view/<cid_account>/<re_id>')
class editMeeting(Resource):
    def get(self, cid_account, re_id):
        try:
            curs = mysql.connection.cursor()
            sql = """SELECT * FROM hrd.meeting_register mr
                    JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id
                    JOIN hrd.meeting_travel mt ON mrp.travel_type = mt.travel_id
                    JOIN hrd.department d ON mrp.department = d.dep_code_id
                    WHERE mrp.cid_account = '%s' AND mr.re_id = '%s' LIMIT 1""" % (
                cid_account, re_id)
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


### ดึงข้อมูลผู้ร่วมไปราชการและลบผู้เข้าร่วมไปราชการ ###
@ns_hrd.route('/partner/<cid_account>/<re_id>', methods=['GET'])
@ns_hrd.route('/deletepartner/<cid_account>/<re_id>', methods=['DELETE'])
class partnerMeeting(Resource):
    def get(self, cid_account, re_id):
        try:
            curs = mysql.connection.cursor()
            sql = """SELECT * FROM hrd.meeting_register_partner mrp
                        JOIN hrd.department d ON mrp.department = d.dep_code_id
                        JOIN hrd.meeting_travel mt ON mrp.travel_type = mt.travel_id
                    WHERE mrp.re_id = '%s'
                        HAVING mrp.cid_account <> '%s'
                    """ % (re_id, cid_account)
            # print(sql)
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

    def delete(self, cid_account, re_id):
        try:
            curs = mysql.connection.cursor()
            sql = """DELETE FROM hrd.meeting_register_partner
                    WHERE cid_account = '%s' AND re_id = '%s'
                    """ % (cid_account, re_id)
            # print(sql)
            curs.execute(sql)
            data = []
            # แยกส่วนหัวของแถว
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


### ข้อมูลบุคลากรในระบบ HRD Update ###
@ns_hrd.route('/personal', methods=['GET'])
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
                            result = "'" + cid + "' ,'" + pcode + "' ,'" + fname + "' ,'" + lname + "'"
                            query = """INSERT INTO hrd.personal(%s) VALUES(%s)""" % (
                                fields, result)
                            print(query)
                            cur.execute(query)
            # # แยกส่วนหัวของแถว
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            return err
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


### Function get department ###
def getDepartment(dep):
    strDep = "%" + dep + "%"
    curs = mysql.connection.cursor()
    sql = """SELECT * FROM hrd.department WHERE dep_code_name LIKE '%s'""" % (
        strDep)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


### Function get meeting_travel ###
def getTravel(travel):
    strTravel = "%" + travel + "%"
    curs = mysql.connection.cursor()
    sql = """SELECT * FROM hrd.meeting_travel WHERE travel_name LIKE '%s'""" % (
        strTravel)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


### Function get position ###
def getPosition(idcard):
    curs = mysql.connection.cursor()
    sql = """SELECT pos_no FROM hrd.personal WHERE pid = '%s'""" % (idcard)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


### Function get CID###
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


### Function get information employee ###
def getPersonal(idcard):
    curs = mysql.connection.cursor()
    sql = """SELECT COUNT(pid) as cnt FROM hrd.personal WHERE pid = '%s'""" % (
        idcard)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


### Function get prefix name ###
def getPrefix(pname):
    curs = mysql.connection.cursor()
    sql = """SELECT pcode FROM hrd.prefix WHERE longprefix = '%s'""" % (pname)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

def getDataEmployee(idcard):
    curs = mysql.connection.cursor()
    sql = """SELECT *, CONCAT(pname,fname,' ',lname) as fullname FROM payroll_employee
            WHERE idcard = '%s' AND is_expire <> 'Y'
            """ % (idcard)
    curs.execute(sql)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

if __name__ == '__main__':
    #app.run(debug=True)
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
