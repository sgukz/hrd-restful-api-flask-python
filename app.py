from flask_restplus import Namespace, Api, Resource
from flask import Flask, jsonify, request, current_app
from flask_mysqldb import MySQL
from flask_cors import CORS
from apis import api

app = Flask(__name__)
api.init_app(app)
CORS(app)
if __name__ == '__main__':
    #app.run(debug=True)
    app.debug = True
    app.run(host='0.0.0.0', port=8000)