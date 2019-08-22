from dbconnect import dbPayroll
from flask import Flask, jsonify, request, json, Response
from flask_restplus import Api, Resource, Namespace
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
api = Namespace('ระบบประเมินผลสัมฤทธิ์บุคลากร รพ.ร้อยเอ็ด',
                description='จัดการข้อมูลระบบประเมินผลสัมฤทธิ์')

@api.route('/getStrategic', methods=['GET'])
class KPIStrategic(Resource):
    def get(self):
        try:
            cur = dbPayroll()
            sql = """
                SELECT * FROM db_kpi.kpi_strategic
                """
            cur.execute(sql)
            # แยกส่วนหัวของแถว
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            response = {
                'code': 200,
                'data': json_data,
                'msg' : 'success'
            }
            return jsonify(response)
        except Exception as err:
            return jsonify({"code": 400, "msg": err})
