import threading
from collections import namedtuple

class gpio_mn():
    def __init__(self):
        self.SensorData = namedtuple('SensorData', ['temp', 'co2', 'light'])
        self.data = self.SensorData(temp=0, co2=0, light=0)
        self.delay = 0.5

    def __get_gpio__(self):
        return None

    def loop_gpio(self, frequent = 2):
        '''
        用于循环读取gpio数据，在单独线程中执行
        :param frequent: gpio读取频率 hz 最高200
        :type frequent: int
        :return: None
        '''

        if frequent > 200:
            frequent = 200
        elif frequent < 1:
            frequent = 1
        self.delay = 1 / frequent
        th = threading.Thread(target=self.__get_gpio__)

        return None

    def read(self, types="all"):
        '''
        获取gpio数据
        :param types: 获取数据类型, 可选"all" "temp" "co2" "light"
        :type types: str
        :return: float | dict
        '''
        match types:
            case "temp":
                return self.data.temp
            case "co2":
                return self.data.co2
            case "light":
                return self.data.light
            case _:
                return self.data

        return None
