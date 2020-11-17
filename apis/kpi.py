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


@api.route('/getIndicators/<userId>', methods=['GET'])
@api.route('/addIndicators', methods=['POST'])
@api.route('/deleteIndicators/<id>', methods=['DELETE'])
class KPIIndicators(Resource):
    ### Endpoint /addIndicators
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
                            if key != "dataTable":
                                if key != "status":
                                    if key != "redirect":
                                        if data_json["strategic"][
                                                key] is not None:
                                            values += "'" + str(
                                                data_json["strategic"]
                                                [key]) + "',"
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
                cur.connection.close()
                data.append({
                    "code": 200,
                    "msg": "บันทึกตัวชี้วัดเรียบร้อยแล้ว"
                })
                return jsonify(data)
            except Exception as e:
                return jsonify([{"code": 400, "msg": str(e)}])
        except Exception as err:
            return jsonify([{"code": 400, "msg": str(err)}])

    ### Endpoint /getIndicators
    def get(selt, userId):
        try:
            cur = dbKPI()
            if userId != "":
                sql = """
                        SELECT ip.*, st.NAME_STRATE, CONCAT(ip.CREATED_AT,'') CREATEDAT, si.*,p.ID_PURPOSE,p.NAME_PURPOSE
                        FROM kpi_indicators_person ip
                        LEFT JOIN kpi_score_indicators si ON ip.ID_INDICATORS_PERSON = si.ID_INDICATORS_PERSON
                        LEFT JOIN kpi_strategic st ON ip.ID_STRATE = st.ID_STRATE
                        LEFT JOIN kpi_purpose p ON p.ID_STRATE = st.ID_STRATE
                        ORDER BY ip.CREATED_AT DESC
                    """
            else:
                sql = """
                        SELECT ip.*, st.NAME_STRATE, CONCAT(ip.CREATED_AT,'') CREATEDAT, si.* , p.ID_PURPOSE,p.NAME_PURPOSE  
                        FROM kpi_indicators_person ip
                        LEFT JOIN kpi_score_indicators si ON ip.ID_INDICATORS_PERSON = si.ID_INDICATORS_PERSON
                        LEFT JOIN kpi_strategic st ON ip.ID_STRATE = st.ID_STRATE
                        LEFT JOIN kpi_purpose p ON p.ID_STRATE = st.ID_STRATE
                        WHERE ip.IDCARD_USER = '%s'
                        ORDER BY ip.CREATED_AT DESC
                    """ % (userId)
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

    ### Endpoint /deleteIndicators
    def delete(selt, id):
        try:
            cur = dbKPI()
            idIndicator = id
            data = []
            deleteIndicators = """
                                DELETE kpi_indicators_person, kpi_score_indicators
                                FROM kpi_indicators_person
                                INNER JOIN kpi_score_indicators
                                ON kpi_indicators_person.ID_INDICATORS_PERSON = kpi_score_indicators.ID_INDICATORS_PERSON
                                WHERE kpi_indicators_person.ID_INDICATORS_PERSON = %s
                            """ % (idIndicator)
            cur.execute(deleteIndicators, )
            cur.connection.commit()
            cur.connection.close()
            data.append({"code": 200, "msg": "ลบข้อมูลตัวชี้วัดเรียบร้อยแล้ว"})
            return jsonify(data)
        except Exception as err:
            return jsonify({"code": 400, "msg": str(err)})


@api.route('/updateIndicators', methods=['POST'])
class KPIUpdateIndicator(Resource):
    def post(selt):
        try:
            cur = dbKPI()
            data_json = request.json
            data = []
            value1 = ""
            value2 = ""
            idIndication = ""
            idScore = ""
            for key in data_json['dataEdit']:
                if key != "status":
                    if key != "items":
                        if key == "indicators":
                            value1 += "NAME_INDICATORS_PERSON = '" + str(
                                data_json["dataEdit"][key]) + "', "
                        if key == "id":
                            idIndication += str(data_json["dataEdit"][key])
                        if key == "strategic":
                            value1 += "ID_STRATE = " + str(
                                data_json["dataEdit"][key]['value'])
                        if key == "idScore":
                            idScore += str(data_json["dataEdit"][key])
                        if key == "score1":
                            value2 += "SCORE_1 = '" + str(
                                data_json["dataEdit"][key]) + "', "
                        if key == "score2":
                            value2 += "SCORE_2 = '" + str(
                                data_json["dataEdit"][key]) + "', "
                        if key == "score3":
                            value2 += "SCORE_3 = '" + str(
                                data_json["dataEdit"][key]) + "', "
                        if key == "score4":
                            value2 += "SCORE_4 = '" + str(
                                data_json["dataEdit"][key]) + "', "
                        if key == "score5":
                            value2 += "SCORE_5 = '" + str(
                                data_json["dataEdit"][key]) + "'"

            # updateIndicators = """
            #         UPDATE kpi_indicators_person SET %s
            #         WHERE ID_INDICATORS_PERSON = %s;
            #         UPDATE kpi_score_indicators SET %s
            #         WHERE ID_SCORE_INDICATOR = %s;
            #         """ % (value1, idIndication, value2, idScore)
            updateIndicators = """
                    UPDATE kpi_indicators_person SET %s 
                    WHERE ID_INDICATORS_PERSON = %s;
                    """ % (value1, idIndication)
            updateScore = """
                    UPDATE kpi_score_indicators SET %s
                    WHERE ID_SCORE_INDICATOR = %s;
            """ % (value2, idScore)
            #print(updateIndicators)
            cur.execute(updateIndicators,)
            cur.execute(updateScore,)
            cur.connection.commit()
            cur.connection.close()
            data.append({
                "code": 200,
                "msg": "แก้ไขข้อมูลตัวชี้วัดเรียบร้อยแล้ว"
            })
            return jsonify(data)
        except Exception as err:
            return jsonify([{"code": 400, "msg": str(err)}])


@api.route('/viewIndicator/<idIndicator>', methods=['GET'])
class KPIViewIndicator(Resource):
    def get(selt, idIndicator):
        try:
            cur = dbKPI()
            data = []
            sql = """
                SELECT ip.ID_INDICATORS_PERSON ID_INDIC,
                    si.ID_SCORE_INDICATOR ID_SCORE,
                    ip.NAME_INDICATORS_PERSON,
                    ip.ID_STRATE,
                    CONCAT(st.ID_STRATE,'. ',st.NAME_STRATE) NAME_STRATE,
                    si.SCORE_1,
                    si.SCORE_2,
                    si.SCORE_3,
                    si.SCORE_4,
                    si.SCORE_5
                FROM kpi_indicators_person ip
                LEFT JOIN kpi_score_indicators si ON ip.ID_INDICATORS_PERSON = si.ID_INDICATORS_PERSON
                LEFT JOIN kpi_strategic st ON ip.ID_STRATE = st.ID_STRATE
                WHERE ip.ID_INDICATORS_PERSON = '%s'
                ORDER BY ip.CREATED_AT DESC
                """ % (idIndicator)
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


@api.route('/getPurposeGoal/<idPurpose>', methods=['GET'])
class KPIPurposeGoal(Resource):
    def get(selt, idPurpose):
        try:
            cur = dbKPI()
            sql = """
                SELECT * FROM kpi_goal WHERE ID_PURPOSE = %s
                """ % (idPurpose)
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


@api.route('/getObjective/<idGoal>', methods=['GET'])
class KPIObjective(Resource):
    def get(selt, idGoal):
        try:
            cur = dbKPI()
            sql = """
                SELECT * FROM kpi_objective WHERE ID_GOAL = %s
                """ % (idGoal)
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


@api.route('/getIndicatorHospital/<idObjective>', methods=['GET'])
class KPIIndicatorHospital(Resource):
    def get(selt, idObjective):
        try:
            cur = dbKPI()
            sql = """
                SELECT * FROM kpi_indicators WHERE ID_OBJ = %s
                """ % (idObjective)
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
