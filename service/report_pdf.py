from datetime import datetime


class Utils:

    @staticmethod
    def getTimeInSeconds():
        return int((datetime.now() - datetime(1970, 1, 1)).total_seconds())

    @staticmethod
    def getTimeInMillis():
        return int((datetime.now() - datetime(1970, 1, 1)).total_seconds() * 1000)

    @staticmethod
    def getCurrentMonth():
        return int(datetime.now().strftime("%Y%m"))