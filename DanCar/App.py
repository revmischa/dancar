from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
db = SQLAlchemy(app)
#from flask_sockets import Sockets
#sockets = Sockets(app)

# Throw this error from within DanCar instead of calling abort() directly.
# Doing so allows for error recovery or extra logging.
class DanError (Exception) :
    def __init__ (self,code=500,message="Server Error",headers={}) :
        super(DanError,self).__init__(message)
        self.code = code
        self.headers = headers

# Catch DanError and return back a flask response
@app.errorhandler(DanError)
def catchDan(self) :
    return self.message , self.code , self.headers

# called from __main__.py when "python DanCar" is run from the root.
def run():
    app.run(host='0.0.0.0') # can host be pulled from the config?
