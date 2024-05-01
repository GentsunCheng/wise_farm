import time
import pymysql
import datetime
import threading
from collections import namedtuple

import random

class gpio_mn():
    def __init__(self):
        self.SensorData = namedtuple('SensorData', ['temp', 'co2', 'light'])
        self.data = self.SensorData(temp=0, co2=0, light=0)
        self.datas = []
        self.delay = 0.5
        self.run = False
        self.th = threading.Thread(target=self.__get_gpio__)
        self.td = threading.Thread(target=self.__write_db__)
        self.event = threading.Event()
        self.cursor = pymysql.connect(
            host="localhost",
            user="farmer",
            password="12358",
            database="wise_farm"
        ).cursor()

    def __get_gpio__(self):
        old_time = datetime.datetime.now()
        old_minute = old_time.minute
        self.td.start()
        while self.run:
            print("server is running")
            self.data.temp = random.randint(0,30)
            self.data.co2 = random.randint(0,500)
            self.data.light = random.randint(0,100)
            self.datas.append(self.data)
            current_time = datetime.datetime.now()
            current_minute = current_time.minute
            if old_time > 56:
                current_minute = current_minute + 60
            if current_minute - old_minute >= 3:
                old_minute = current_minute
                if self.td.is_alive():
                    self.event.set()
            time.sleep(self.delay)
        self.td.join()
        return None

    def __write_db__(self):
        while self.run:
            self.event.wait()
            sql = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
            data = ("value1", "value2")
            try:
                cursor.execute(sql, data)
                conn.commit()
                print("数据插入成功")
            except Exception as e:
                conn.rollback()
                print("数据插入失败:", e)
            finally:
                cursor.close()
                conn.close()
            self.datas.clear()
            self.event.clear()

    def gpio_server(self,cmd="start", frequent = 2):
        '''
        用于循环读取gpio数据，在单独线程中执行
        :param frequent: gpio读取频率 hz 最高200
        :type frequent: int
        :return: None
        '''

        if cmd == "start":
            if self.th.is_alive():
                print("server is already running!!")
            else:
                if frequent > 200:
                    frequent = 200
                elif frequent < 1:
                    frequent = 1
                self.delay = 1 / frequent

                self.run = True
                self.th.start()

        elif cmd == "stop":
            if self.th.is_alive():
                self.run = False
                self.th.join()
            else:
                print("server is not running!!")


        return None

    def read(self, types="all"):
        '''
        获取gpio数据
        :param types: 获取数据类型, 可选"all" "temp" "co2" "light"
        :type types: str
        :return: float | dict
        '''
        if self.th.is_alive():
            match types:
                case "temp":
                    return self.data.temp
                case "co2":
                    return self.data.co2
                case "light":
                    return self.data.light
                case _:
                    return self.data

        else:
            return None

