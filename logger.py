class Logger:
    _TAG = "VectraTvOnlinePlugin"
    _DEBUG = 'Debug'
    _INFO = 'Info'
    _WARNING = 'Warning'
    _ERROR = 'Error'

    def __init__(self, prefix):
        self.prefix = prefix.replace('_', '') + '.py'

    def i(self, message):
        self.__log__(message, self._INFO)

    def d(self, message):
        self.__log__(message, self._DEBUG)

    def e(self, message):
        self.__log__(message, self._ERROR)

    def w(self, message):
        self.__log__(message, self._WARNING)

    def __log__(self, message, level):
        print '%s:%s (%s): %s' % (self._TAG, level, self.prefix, message)
