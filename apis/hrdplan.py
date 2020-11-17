from dbconnect import dbPayroll
from flask import Flask, jsonify, request, json, Response
from flask_restplus import Api, Resource, Namespace
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
api = Namespace('ระบบแผนพัฒนาบุคลากร รพ.ร้อยเอ็ด',
                description='จัดการข้อมูลระบบขออนุมัติไปราชการ')