# Throw this error from within the app instead of calling abort() directly.
# Doing so allows for error recovery or extra logging.
class error (Exception):
    def __init__ (self,code=500, message="Server Error", headers={}) :
        super(error, self).__init__(message)
        self.code = code
        self.headers = headers