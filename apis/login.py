from dbconnect import dbPayroll
from flask import Flask, jsonify, request, json, Response
#from flask_mysqldb import MySQL
#from flask_cors import CORS
from flask_restplus import Api, Resource, Namespace
from datetime import datetime, timedelta
import jwt
app = Flask(__name__)

api = Namespace('LOGIN-PayrollDatabase V.1', description='เข้าสู่ระบบ Payroll')

#ns_login = api.namespace('api/v1/', description='Login')
### เข้าสู่ระบบ ###
@api.route('/login', methods=['POST'])
class HRDLogin(Resource):
    def post(self):
        try:
            data_json = request.json
            idcard = data_json["auth"]["idcard"]
            JWT_TOKEN_EXPIRE = 12
            EXP = datetime.utcnow() + timedelta(hours=JWT_TOKEN_EXPIRE)
            iat = datetime.utcnow()
            # passpwd = data_json["auth"]["password"]
            cur = dbPayroll()
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
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            encode = jwt.encode(
                {
                    'data': [json_data[0]],
                    'iat': iat,
                    'exp': EXP
                },
                'secret',
                algorithm='HS256')
            encode_data = encode.decode('utf-8')
            # print(encode_data)
            return jsonify({'token': encode_data})
        except Exception as err:
            json_data.append({"msg": err})
            return jsonify(json_data)