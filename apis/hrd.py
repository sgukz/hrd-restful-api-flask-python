from dbconnect import dbPayroll
from flask import Flask, jsonify, request, json, Response
from flask_restplus import Api, Resource, Namespace
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
api = Namespace('ระบบขออนุมัติไปราชการ รพ.ร้อยเอ็ด',
                description='จัดการข้อมูลระบบขออนุมัติไปราชการ')


### ข้อมูลบุคลากรจากการเงิน ###
@api.route('/rehuser', methods=['GET'])
class Employee(Resource):
    def get(self):
        cur = dbPayroll()
        try:
            cur.execute(
                """SELECT *, idcard, CONCAT(pname,fname,' ',lname) as fullname FROM payroll_employee 
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
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


### ข้อมูลตำแหน่งทั้งหมด ###
@api.route('/positions', methods=['GET'])
class Positions(Resource):
    def get(self):
        cur = dbPayroll()
        try:
            cur.execute(
                """SELECT position_name FROM officerdata_db.reh_employee_tb 
                    GROUP BY position_name
                    ORDER BY position_name""")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


@api.route('/positions/create', methods=['POST'])
class createPositions(Resource):
    def post(self):
        curs = dbPayroll()
        try:
            data_json = request.json
            cid = str(data_json["position"]["cid"])
            fix_name = str(data_json["position"]["fix_name"])
            first_name = str(data_json["position"]["first_name"])
            last_name = str(data_json["position"]["last_name"])
            position_name = data_json["position"]["position_name"]
            degree = data_json["position"]["degree"]

            sql = """INSERT INTO officerdata_db.reh_employee_tb(cid, fix_name, first_name, last_name, position_name, degree)
                    VALUES('%s', '%s', '%s', '%s', '%s', '%s')""" % (
                cid, fix_name, first_name, last_name, position_name, degree)
            curs.execute(sql)
            curs.connection.commit()
            curs.connection.close()
            return jsonify({
                "code": 200,
                "msg": "บันทึกข้อมูลบุคลากร",
                "text": "เรียบร้อยแล้ว",
                "type": "success"
            })
        except Exception as err:
            return jsonify({
                "code": 400,
                "msg": str(err),
                "text": "เกิดข้อผิดพลาด",
                "type": "error"
            })


@api.route('/positions/update', methods=['POST'])
class updatePositions(Resource):
    def post(self):
        curs = dbPayroll()
        data_json = request.json
        try:
            cid = data_json["position"]["cid"]
            position_name = data_json["position"]["position_name"]
            degree = data_json["position"]["degree"]            

            sql = """UPDATE officerdata_db.reh_employee_tb SET position_name = '%s', degree = '%s'
                    WHERE cid = '%s'""" % (position_name, degree, cid)
            # print(sql)
            curs.execute(sql)
            curs.connection.commit()
            curs.connection.close()
            return jsonify({
                "code": 200,
                "msg": "แก้ไขข้อมูลบุคลากร",
                "text": "เรียบร้อยแล้ว",
                "type": "success"
            })
        except Exception as err:
            # print(data_json["position"])
            return jsonify({
                "code": 400,
                "msg": str(err),
                "text": "เกิดข้อผิดพลาด",
                "type": "error"
            })


### ข้อมูลบุคลากร ###
@api.route('/reh-employee', methods=['GET'])
class RehEmployee(Resource):
    def get(self):
        cur = dbPayroll()
        try:
            cur.execute(
                """SELECT DISTINCT pr.idcard AS cid, pr.pname, pr.fname, pr.lname, re.position_name,
                    CASE
                        WHEN re.degree = 'ทรงคุณวุฒิ' THEN re.degree
                        WHEN re.degree = 'ชำนาญการพิเศษ' THEN re.degree
                        WHEN re.degree = 'ชำนาญการ' THEN re.degree
                        WHEN re.degree = 'ปฏิบัติการ' THEN re.degree
                        WHEN re.degree = 'ปฏิบัติงาน' THEN re.degree
                        WHEN re.degree = 'เชี่ยวชาญ' THEN re.degree
                        WHEN re.degree = 'ชำนาญงาน' THEN re.degree
                        ELSE ''
                    END as pos_degree,
                    CASE
                        WHEN re.is_active IS NULL THEN 0
                        ELSE re.is_active
                    END active
                FROM
                    payroll.payroll_employee pr
                    LEFT JOIN officerdata_db.reh_employee_tb re
                    ON pr.idcard = re.cid
                WHERE
                    pr.is_expire != 'Y' AND pr.idcard <> '' 
                ORDER BY pr.fname""")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            cur.close()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


###########################################################################


### ดึงข้อมูลหน่วยงานทั้งหมด ###
@api.route('/department', methods=['GET'])
class HRDDepart(Resource):
    def get(self):
        try:
            cur = dbPayroll()
            cur.execute("SELECT * FROM hrd.department ORDER BY dep_code_name")
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))

            sql = """SELECT dep_name 
                    FROM payroll_employee 
                    GROUP BY dep_name 
                    HAVING dep_name IS NOT NULL 
                    ORDER BY dep_name"""
            cur.execute(sql)
            row_headers2 = [x[0] for x in cur.description]
            rv2 = cur.fetchall()
            json_data2 = []
            for result in rv2:
                json_data2.append(dict(zip(row_headers2, result)))
            dep_name = ''
            for key in json_data2:
                for k, v in key.items():
                    if k == 'dep_name':
                        dep_name = str(v)
                        checkDep = getDepartment(dep_name)
                        if len(checkDep) == 0:
                            query = """INSERT INTO hrd.department(dep_code_name)
                                        VALUES('%s')
                                    """ % (dep_name)
                            cur.execute(query)
            return jsonify(json_data)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


###########################################################################


### จัดการข้อมูลหน่วยงาน ###
@api.route('/dep/create', methods=['POST'])
@api.route('/dep/delete/<depid>', methods=['DELETE'])
@api.route('/dep/view/<depid>', methods=['GET'])
@api.route('/dep/update', methods=['PUT'])
class HRDDepartManage(Resource):
    def get(self, depid):
        try:
            cur = dbPayroll()
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
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})

    def post(self):
        try:
            data_json = request.json
            data = []
            depart = data_json['department']
            #print(depart)
            cur = dbPayroll()
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
            cur = dbPayroll()
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
            cur = dbPayroll()
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


###########################################################################


### ค้นหาหน่วยงาน ###
@api.route('/dep/search', methods=['post'])
class HRDSearchDepart(Resource):
    def post(self):
        try:
            cur = dbPayroll()
            data_json = request.json['keyword']
            #print(data_json['keyword'])
            like_dep_name = "%" + data_json['keyword'] + "%"
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
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


###########################################################################


### ดึงข้อมูลหน่วยงานตามข้อมูลขอไปราชการ ###
@api.route('/depmeeting/<idcard>/<re_id>', methods=['GET'])
class HRDDepartMeeting(Resource):
    def get(self, idcard, re_id):
        try:
            curs = dbPayroll()
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
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


###########################################################################


### ข้อมูลขอไปราชการรายบุคคลและแก้ไขข้อมูลไปราชการ ###
@api.route('/<idcard>', methods=['GET'])
@api.route('/update', methods=['POST'])
class HRDMeetingUpdate(Resource):
    def get(self, idcard):
        try:
            curs = dbPayroll()
            sql = """SELECT mr.re_id,CONCAT(mr.date_time_save,',') created_at ,mr.code_master, mt.meeting_type_name,mr.meeting_story,CONCAT(mr.start_date,',', mr.end_date) datemeeting, mr.cid_account as cid_your,mrp.cid_account as cid_partner, "true" as isActive
                    FROM hrd.meeting_register mr 
                    LEFT JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id 
                    LEFT JOIN hrd.meeting_type mt ON mr.meeting_type = mt.meeting_type_code
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
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})

    def post(self):
        try:
            curs = dbPayroll()  ### Connect to database HRD ###
            fields = ""
            fields_partner = ""
            values_partner = ""
            data = []
            code_master = ""
            data_json = request.json
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
            valStr = ""
            #print(data_json["hrdplan"])
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
                                ) + int(data_json["register"]
                                        ["expense_owncar"]) + int(
                                            data_json["register"]
                                            ["expense_residence"]) + int(
                                                data_json["register"]
                                                ["expense_register_meeting"])
                                +int(
                                    data_json["register"]["expense_allowance"]
                                ) + int(data_json["register"]["expense_other"])
                                fields += str(key) + " = '" + str(
                                    expense_total) + "'"
                            else:
                                if data_json["register"][key] == True:
                                    valStr = 1
                                elif data_json["register"][key] == False:
                                    valStr = 0
                                else:
                                    valStr = data_json["register"][key]
                                fields += str(key) + " = '" + str(
                                    valStr) + "',"
            re_id = str(data_json["register"]["re_id"])
            cid_account = str(data_json["register"]["cid_account"])
            sql = """UPDATE hrd.meeting_register SET %s
                    WHERE re_id = '%s'
                    """ % (fields, re_id)
            try:
                #print(sql)
                ### execute meeting_register ###
                curs.execute(sql)
                curs.connection.commit()
                ### UPDATE HRDPLAN ###
                meeting_is = str(data_json["register"]["meeting_is"])
                if meeting_is != "3":
                    updateMeetingHRDPlan = """
                        UPDATE hrd.meeting_register SET hrdplan_id = 0 WHERE re_id = '%s'
                    """ % (re_id)
                    #print(updateMeetingHRDPlan)
                    curs.execute(updateMeetingHRDPlan)
                    idPlan = str(data_json["hrdplan"])
                    #print('ID Plan: ' + idPlan)
                    if idPlan != "0":
                        updateHRDPlan1 = """
                            UPDATE hrdplandb.devolopplan SET id_meeting = NULL WHERE id = %s
                        """ % (idPlan)
                        #print(updateHRDPlan1)
                        curs.execute(updateHRDPlan1)
                        deleteFollowPlan = """
                            DELETE FROM hrdplandb.follow_plan WHERE id_plan = %s
                        """ % (idPlan)
                        #print(deleteFollowPlan)
                        curs.execute(deleteFollowPlan)
                        curs.connection.commit()
                else:
                    hrdplan_id = data_json["register"]["hrdplan_id"]
                    if hrdplan_id != "0":
                        startdate = data_json["register"]["start_date"]
                        enddate = data_json["register"]["end_date"]
                        unitDate = formatTimestamp(startdate, enddate)
                        updateHRDPlan = """
                            UPDATE hrdplandb.devolopplan SET id_meeting = '%s' WHERE `id` = %s
                        """ % (re_id, hrdplan_id)
                        #print(updateHRDPlan)
                        curs.execute(updateHRDPlan)
                        addFollowPlan = """
                            INSERT INTO hrdplandb.follow_plan(id_plan, startdate, enddate, unit_date, status_plan, create_date)
                            VALUES(%s, '%s', '%s', %s, 1, NOW())
                        """ % (hrdplan_id, startdate, enddate, unitDate)
                        #print(addFollowPlan)_
                        curs.execute(addFollowPlan)
                ######################

                #### Update meeting_partner ###
                trav_type = data_json['travel_chagne']
                # print(data_json['travel_chagne'])
                if (trav_type != ""):
                    sqlTravel = """UPDATE hrd.meeting_register_partner
                                SET travel_type = %s
                                WHERE cid_account = '%s' AND re_id = '%s'""" % (
                        trav_type, cid_account, re_id)
                    #print(sqlTravel)
                    curs.execute(sqlTravel)
                #### End Update meeting_partner ###
                queue_number = ""
                # #### insert meeting_partner ###
                # fields_partner = "re_id, re_date, fullname , cid_account, cid_account_recoder, employee_type, department, department_money, travel_type"
                fields_partner = "re_id, re_date, fullname , cid_account, cid_account_recoder, employee_type, department, department_money, travel_type , queue, created_at"
                old = ""
                for key_partner in data_json["register_partner"]:
                    for k, v in key_partner.items():
                        if k == "fullname":
                            fullname = str(v)
                        elif k == "employee_type":
                            employee_type = str(v)
                        elif k == "cid_account":
                            idcard = str(v)
                        elif k == "cid_account_recoder":
                            recoder = str(v)
                        elif k == "re_date":
                            re_date = str(v)
                        elif k == "department":
                            department = str(v)
                            depart_data = getDepartment(department)
                            for key_depart in depart_data:
                                for k_depart, v_depart in key_depart.items():
                                    if k_depart == "dep_code_id":
                                        dep_code_id = str(v_depart)
                        elif k == "travel_type":
                            travel_type = str(v)
                        elif k == "queue":
                            queue_number = str(v)
                        elif k == "old":
                            old = str(v)
                    if old == "0":
                        val_part = re_id + ", '" + re_date + "', '" + fullname + "','" + idcard + "','" + recoder + "','" + employee_type + "','" + dep_code_id + "', '" + dep_code_id + "'," + str(
                            travel_type) + " ," + queue_number + " ,NOW()"
                        sql_partner = """INSERT INTO hrd.meeting_register_partner(%s) VALUES(%s)""" % (
                            fields_partner, val_part)
                        ### execute meeting_register_partner ###
                        #print(sql_partner)
                        curs.execute(sql_partner)
                # #queue_number
                curs.connection.commit()
                curs.connection.close()
                ### END insert meeting_partner ###
                data.append({"status": 200, "msg": "OK"})
                return jsonify(data)
            except Exception as e:
                data.append({"status": 400, "msg": str(e)})
                return jsonify(data)
                #return str(e)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


###########################################################################


### เปลี่ยนคนไปราชการแทน ###
@api.route('/change/<re_id>/<idcard>', methods=['get'])
class HRDChangePerson(Resource):
    def get(self, re_id, idcard):
        try:
            cur = dbPayroll()
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
                    """ % (fullname, idcard, idcard, employee_type,
                           dep_code_id, re_id)
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


######################################################################################################


### ค้นหาข้อมูลขอไปราชการ ###
@api.route('/search', methods=['post'])
class HRDSearchMeeting(Resource):
    def post(self):
        try:
            cur = dbPayroll()
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


######################################################################################################


### ข้อมูลการขอไปราชการทั้งหมดและลบข้อมูล ###
@api.route('/registerall', methods=['GET'])
@api.route('/create', methods=['POST'])
@api.route('/delete/<re_id>', methods=['DELETE'])
class getAll(Resource):
    def post(self):
        try:
            curs = dbPayroll()
            fields = ""
            values = ""
            fields_partner = ""
            values_partner = ""
            data = []
            data_json = request.json

            fields_partner += "re_id, re_date, fullname , cid_account, cid_account_recoder, employee_type, department, department_money, travel_type , queue, created_at"
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
            queue = ""
            #print(data_json["register"])
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
            values += ", NOW()"
            sql = """INSERT INTO hrd.meeting_register(%s)
                    VALUES(%s)
                    """ % (fields, values)
            try:
                #print(sql)
                curs.execute(sql)
                re_id = curs.lastrowid
                ### UPDATE HRD PLAN ###
                hrdplan_id = data_json["register"]["hrdplan_id"]
                startdate = data_json["register"]["start_date"]
                enddate = data_json["register"]["end_date"]
                unitDate = formatTimestamp(startdate, enddate)
                updateHRDPlan = """
                    UPDATE hrdplandb.devolopplan SET id_meeting = '%s' WHERE `id` = %s
                """ % (re_id, hrdplan_id)
                #print(updateHRDPlan)
                curs.execute(updateHRDPlan)
                addFollowPlan = """
                    INSERT INTO hrdplandb.follow_plan(id_plan, startdate, enddate, unit_date, status_plan, create_date)
                    VALUES(%s, '%s', '%s', %s, 1, NOW())
                """ % (hrdplan_id, startdate, enddate, unitDate)
                curs.execute(addFollowPlan)
                #print(addFollowPlan)
                #######################
                values_partner += str(re_id) + ", "
                # ### insert meeting_partner ###
                # print(data_json["register_partner"])
                for key_partner in data_json["register_partner"]:
                    for k, v in key_partner.items():
                        if k == "fullname":
                            fullname = str(v)
                        elif k == "employee_type":
                            employee_type = str(v)
                        elif k == "cid_account":
                            idcard = str(v)
                        elif k == "cid_account_recoder":
                            recoder = str(v)
                        elif k == "re_date":
                            re_date = str(v)
                        elif k == "department":
                            department = str(v)
                            depart_data = getDepartment(department)
                            for key_depart in depart_data:
                                for k_depart, v_depart in key_depart.items():
                                    if k_depart == "dep_code_id":
                                        dep_code_id = str(v_depart)
                        elif k == "travel_type":
                            travel_type = str(v)
                        elif k == "queue":
                            queue = str(v)
                    val_part = values_partner + "'" + re_date + "', '" + fullname + "','" + idcard + "','" + recoder + "','" + employee_type + "','" + dep_code_id + "', '" + dep_code_id + "'," + str(
                        travel_type) + ",'" + queue + "',NOW()"
                    sql_partner = """INSERT INTO hrd.meeting_register_partner(%s) VALUES(%s)""" % (
                        fields_partner, val_part)
                    #print(sql_partner)
                    curs.execute(sql_partner)
                # queue_number += 1
                ### END insert meeting_partner ###
                curs.connection.commit()
                curs.connection.close()
                data.append({"status": 200, "msg": "OK"})
                return jsonify(data)
            except Exception as e:
                data.append({"status": 400, "msg": str(e)})
                return str(e)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})

    def get(self):
        try:
            curs = dbPayroll()
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
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})

    def delete(self, re_id):
        try:
            curs = dbPayroll()
            data = []
            id_plan = ''
            delete_meeting = """DELETE FROM hrd.meeting_register
                                WHERE re_id = '%s'
                                """ % (re_id)
            curs.execute(delete_meeting)
            delete_meeting_part = """DELETE FROM hrd.meeting_register_partner
                                    WHERE re_id = '%s'
                                    """ % (re_id)
            curs.execute(delete_meeting_part)
            data_plan = getIDPlan(re_id)
            for key_plan in data_plan:
                for k, v in key_plan.items():
                    if k == "id":
                        id_plan = str(v)
            if id_plan != "":
                updateHRDPlan = """
                    UPDATE hrdplandb.devolopplan SET id_meeting = NULL
                    WHERE `id` = '%s'
                """ % (id_plan)
                curs.execute(updateHRDPlan)
                deleteFollowPlan = """
                    DELETE FROM hrdplandb.follow_plan WHERE id_plan = '%s'
                """ % (id_plan)
                curs.execute(deleteFollowPlan)
            curs.connection.commit()
            curs.connection.close()
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


######################################################################################################


### ดึงข้อมูลขอไปราชการแสดงเพื่อแก้ไขข้อมูล ###
@api.route('/view/<cid_account>/<re_id>')
class EditMeeting(Resource):
    def get(self, cid_account, re_id):
        try:
            curs = dbPayroll()
            sql = """
                    SELECT mr.*, mr.expense_allowance expenseAllowance , mrp.*, mt.*, d.*, dev.*
                    FROM hrd.meeting_register mr
                        LEFT JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id
                        LEFT JOIN hrd.meeting_travel mt ON mrp.travel_type = mt.travel_id
                        LEFT JOIN hrd.department d ON mrp.department = d.dep_code_id
                        LEFT JOIN hrdplandb.devolopplan dev ON mr.re_id = dev.id_meeting
                    WHERE mrp.cid_account = '%s' AND mr.re_id = '%s'
            """ % (cid_account, re_id)
            curs.execute(sql)
            curs.connection.commit()
            curs.connection.close()
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


################################################################


### ดึงข้อมูลผู้ร่วมไปราชการและลบผู้เข้าร่วมไปราชการ ###
@api.route('/partner/<re_id>', methods=['GET'])
@api.route('/deletepartner/<cid_account>/<re_id>', methods=['DELETE'])
class partnerMeeting(Resource):
    def get(self, re_id):
        try:
            curs = dbPayroll()
            sql = """SELECT * FROM hrd.meeting_register_partner mrp
                        JOIN hrd.department d ON mrp.department = d.dep_code_id
                        JOIN hrd.meeting_travel mt ON mrp.travel_type = mt.travel_id
                    WHERE mrp.re_id = '%s'
                    ORDER BY queue""" % (re_id)
            # print(sql)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)

        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})

    def delete(self, cid_account, re_id):
        try:
            curs = dbPayroll()
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


################################################################


### ข้อมูลบุคลากรในระบบ HRD Update ###
@api.route('/personal', methods=['GET'])
class updatePersonal(Resource):
    def get(self):
        try:
            cur = dbPayroll()
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
                            #print(query)
                            cur.execute(query)
            # # แยกส่วนหัวของแถว
            data.append({"status": 200, "msg": "OK"})
            return jsonify(data)
        except Exception as err:
            data.append({"status": 400, "msg": str(err)})
            return jsonify(data)


################################################################


## ข้อมูลแผนพัฒนาบุคลากร ###
@api.route('/hrdplan', methods=['POST'])
class HRDPlan(Resource):
    def post(self):
        try:
            cur = dbPayroll()
            data_json = request.json
            year = data_json['year']
            depName = data_json['dep']
            depart_data = getDepartment(depName)
            for key_depart in depart_data:
                for k_depart, v_depart in key_depart.items():
                    if k_depart == "dep_code_id":
                        dep_code_id = str(v_depart)

            depID = ""
            sql = """
                SELECT `id`, other_course FROM hrdplandb.devolopplan WHERE dep_id = '%s' AND year_plan = '%s' AND id_meeting IS NULL
                ORDER BY create_date DESC
                """ % (dep_code_id, year)
            cur.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            response = {'code': 200, 'data': json_data, 'msg': 'success'}
            return jsonify(response)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


################################################################
#########################################
#                                       #
#      ข้อมูลวัตถุประสงค์เพื่อพัฒนา            #
#                                       #
#########################################


@api.route('/getMeetingPlan', methods=['GET'])
class HRDMeetingPlan(Resource):
    def get(self):
        try:
            curs = dbPayroll()
            sql = """SELECT * FROM hrd.meeting_plan 
                    WHERE is_active = 1 
                    ORDER BY meeting_plan_id"""
            # print(sql)
            curs.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in curs.description]
            rv = curs.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            response = {'code': 200, 'data': json_data, 'msg': 'success'}
            return jsonify(response)

        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


################################################################

#########################################
#                                       #
#      Report รายงานการขอไปราชการ        #
#                                       #
#########################################


### Report รายงานการอบรม / ประชุม / สัมนารายบุคคล ###
@api.route('/report/person', methods=["post"])
class ReportPerson(Resource):
    def post(self):
        try:
            cur = dbPayroll()
            data_json = request.json
            idcard = data_json["idcard"]
            place = data_json["place"]
            if place == 0 or place == "":
                sql = """
                    SELECT
                        @s:=@s+1 AS `order`,tmp_data.* 
                    FROM
                        (
                        SELECT
                            mr.re_id,
                            mr.meeting_story,
                            CONCAT( mr.start_date, '' ) start_date,
                            CONCAT( mr.end_date, '' ) end_date,
                            mr.meeting_host,
                            mr.meeting_place,
                            mr.expense_total 
                        FROM
                            hrd.meeting_register mr
                            LEFT JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id 
                        WHERE
                            mrp.cid_account = '%s'
                        ORDER BY
                        mr.re_date DESC 
                        ) AS tmp_data 
                        , (SELECT @s:= 0) AS s;
                """ % (idcard)
            else:
                sql = """
                    SELECT
                        @s := @s + 1 AS `order`,tmp_data.* 
                    FROM
                        (
                        SELECT
                            mr.re_id,
                            mr.meeting_story,
                            CONCAT( mr.start_date, '' ) start_date,
                            CONCAT( mr.end_date, '' ) end_date,
                            mr.meeting_host,
                            mr.meeting_place,
                            mr.expense_total 
                        FROM
                            hrd.meeting_register mr
                            LEFT JOIN hrd.meeting_register_partner mrp ON mr.re_id = mrp.re_id 
                        WHERE
                            mrp.cid_account = '%s' 
                            AND mr.meeting_place_type = %s 
                        ORDER BY
                        mr.re_date DESC 
                        ) AS tmp_data 
                        , (SELECT @s:= 0) AS s;
                """ % (idcard, place)
            #print(sql)
            cur.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            response = {'code': 200, 'data': json_data, 'msg': 'success'}
            return jsonify(response)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


########################################################

# ### Report รายงานการอบรม / ประชุม / สัมนารายบุคคล ###
# @api.route('/reportPerson', methods=["post"])
# class HRDReportPerson(Resource):
#     def post(self):
#         try:
#             cur = dbPayroll()
#             data_json = request.json
#             idcard = data_json["data"]["idcard"]
#             meeting_place = data_json["data"]["place"]
#             sql = """
#                 SELECT
#                     mr.re_id,
#                     mr.meeting_story,
#                     CONCAT( mr.start_date, '' ) start_date,
#                     CONCAT( mr.end_date, '' ) end_date,
#                     mr.meeting_host,
#                     mr.meeting_place,
#                     mr.expense_total
#                 FROM
#                     meeting_register mr
#                     LEFT JOIN meeting_register_partner mrp ON mr.re_id = mrp.re_id
#                 WHERE
#                     mrp.cid_account = '%s'
#                     AND mr.meeting_place_type = '%s'
#                 ORDER BY
#                     mr.re_date DESC;
#             """ % (idcard, meeting_place)
#             cur.execute(sql)
#             # แยกส่วนหัวของแถว
#             row_headers = [x[0] for x in cur.description]
#             rv = cur.fetchall()
#             json_data = []
#             for result in rv:
#                 json_data.append(dict(zip(row_headers, result)))
#             response = {'code': 200, 'data': json_data, 'msg': 'success'}
#             return jsonify(response)
#         except Exception as err:
#             return jsonify({"code": 400, "msg": err})
# ##################################################


### TEST Functions ####
@api.route('/testFunctions', methods=["get"])
class TestFunctions(Resource):
    def get(self):
        startdate = '2019-10-29'
        enddate = '2019-10-30'
        obj = formatTimestamp(startdate, enddate)
        print(obj)


### Function get department ###
def getDepartment(dep):
    #strDep = "%" + dep + "%"
    curs = dbPayroll()
    sql = """
            SELECT CONCAT(dep_code_id,'') dep_code_id, dep_code_name 
            FROM hrd.department WHERE dep_code_name = '%s'
            """ % (dep)
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
    curs = dbPayroll()
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
    curs = dbPayroll()
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
    lenStr = len(fullname.split())
    if lenStr > 2:
        strName = fullname.split()
        fname = strName[0]
        lname = strName[1] + "  " + strName[2]
    else:
        strName = fullname.split()
        fname = strName[0]
        lname = strName[1]
    cur = dbPayroll()
    sql = """SELECT *, CONCAT(pname,fname,' ',lname) as fullname FROM payroll_employee
            WHERE fname = '%s' AND lname = '%s'
            HAVING is_expire <> 'Y'""" % (fname, lname)
    # print(sql)
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
    curs = dbPayroll()
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
    curs = dbPayroll()
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


def getIDPlan(idMeeting):
    curs = dbPayroll()
    getIDPlan = """
        SELECT `id` FROM hrdplandb.devolopplan WHERE id_meeting = '%s'
    """ % (idMeeting)
    curs.execute(getIDPlan)
    # แยกส่วนหัวของแถว
    row_headers = [x[0] for x in curs.description]
    rv = curs.fetchall()
    curs.close()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


def getDataEmployee(idcard):
    curs = dbPayroll()
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


def formatTimestamp(startdate, enddate):
    stDate = startdate.split('-')
    enDate = enddate.split('-')
    startDate = datetime(int(stDate[0]), int(stDate[1]), int(stDate[2]), 0, 0,
                         0, 0)
    endDate = datetime(int(enDate[0]), int(enDate[1]), int(enDate[2]), 0, 0, 0,
                       0)
    deffDate = endDate.timestamp() - startDate.timestamp()
    resultDate = int(deffDate / (60 * 60 * 24))
    return resultDate + 1
