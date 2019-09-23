from dbconnect import dbPayroll, dbKPI
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
            cur = dbKPI()
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
            response = {'code': 200, 'data': json_data, 'msg': 'success'}
            return jsonify(response)
        except Exception as err:
            return jsonify({"code": 400, "msg": err})


@api.route('/addIndicators', methods=['POST'])
@api.route('/getIndicators', methods=['GET'])
class KPIIndicators(Resource):
    def post(self):
        try:
            cur = dbKPI()
            fields = ""
            values = ""
            score = ""
            data = []
            data_json = request.json
            for key in data_json["strategic"]:
                if key != "userLogin":
                    if key != "items":
                        if key != "shareholders":
                            if data_json["strategic"][key] is not None:
                                values += "'" + str(
                                    data_json["strategic"][key]) + "',"
                            else:
                                values += """'',"""
                else:
                    if data_json["strategic"][key] is not None:
                        values += "'" + str(data_json["strategic"][key]) + "'"
                    else:
                        values += """''"""
            fields = "NAME_INDICATORS_PERSON, ID_STRATE, IDCARD_USER,CREATED_AT"
            sql = """INSERT INTO kpi_indicators_person(%s)
                    VALUES(%s, NOW())
                    """ % (fields, values)
            #print(sql)
            try:
                cur.execute(sql, )
                for key_score in data_json["strategic"]["shareholders"]:
                    score += "'" + key_score['name'] + "',"
                lastID = cur.lastrowid
                #print(lastID)
                sql_score = """INSERT into kpi_score_indicators(ID_INDICATORS_PERSON, SCORE_1,SCORE_2,SCORE_3,SCORE_4,SCORE_5,CREATED_AT)
                                VALUES(%s,%s NOW())
                            """ % (lastID, score)
                #print(sql_score)
                cur.execute(sql_score, )
                cur.connection.commit()
                #cur.connection.close()
                data.append({
                    "code": 200,
                    "msg": "บันทึกตัวชี้วัดเรียบร้อยแล้ว"
                })
                return jsonify(data)
            except Exception as e:
                return jsonify([{"code": 400, "msg": str(e)}])
        except Exception as err:
            return jsonify([{"code": 400, "msg": str(err)}])

    def get(selt):
        try:
            cur = dbKPI()
            data_json = request.json
            userId = ""
            sql = """
                    SELECT @s:=@s+1 as `order`,ip.*, CONCAT(ip.CREATED_AT,'') CREATEDAT, si.*   
                    FROM kpi_indicators_person ip
                    LEFT JOIN kpi_score_indicators si ON ip.ID_INDICATORS_PERSON = si.ID_INDICATORS_PERSON,
                    (SELECT @s:= 0) AS s
                    ORDER BY ip.CREATED_AT DESC
                """
            # if userId == "":
            # else:
            #     sql = """
            #             SELECT * FROM kpi_indicators_person ip
            #             LEFT JOIN kpi_score_indicators si ON ip.ID_INDICATORS_PERSON = si.ID_INDICATORS_PERSON
            #             WHERE ip.IDCARD_USER = '%s'
            #             ORDER BY ip.CREATED_AT DESC
            #         """ % (userId)
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
