from flask_restplus import Api
from .login import api as ns_login
from .kpi import api as ns_kpi
from .hrd import api as ns_hrd

api = Api(
    title='HRD Api',
    version='2.0',
    description='HRD Api  Roi Et Hospital',
)

api.add_namespace(ns_login, path='/api/v1')
api.add_namespace(ns_kpi, path='/api/v1/kpi')
api.add_namespace(ns_hrd, path='/api/v1/hrd')