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
            passpwd = data_json["auth"]["password"]
            JWT_TOKEN_EXPIRE = 12
            EXP = datetime.utcnow() + timedelta(hours=JWT_TOKEN_EXPIRE)
            iat = datetime.utcnow()
            if passpwd == "":
                conditions = "emp.idcard = '" + idcard + "'"
            else:
                conditions = "emp.idcard = '" + idcard + "' AND emp.pwd_web = '" + passpwd + "'"
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
                WHERE  %s AND emp.is_expire <> 'Y'""" % (conditions)
            #print(sql)
            cur.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))

            for key_data in json_data:
                for k, v in key_data.items():
                    if k == "chkLog":
                        if v == 0:
                            resp = {
                                'code': 400,
                                'msg': "Username or Password is wrong!!!"
                            }
                            encode = jwt.encode(
                                {
                                    'data': [resp],
                                    'iat': iat,
                                    'exp': EXP
                                },
                                'secret',
                                algorithm='HS256')
                            encode_data = encode.decode('utf-8')
                            return jsonify({
                                'token': encode_data,
                                'code': 200,
                                'msg': "Login success"
                            })
                        else:
                            encode = jwt.encode(
                                {
                                    'data': [json_data[0]],
                                    'iat': iat,
                                    'exp': EXP
                                },
                                'secret',
                                algorithm='HS256')
                            encode_data = encode.decode('utf-8')
                            return jsonify({
                                'token': encode_data,
                                'code': 200,
                                'msg': "Login success"
                            })
        except Exception as err:
            json_data.append({"msg": err})
            return jsonify(json_data)