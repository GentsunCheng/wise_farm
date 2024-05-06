import time
import pymysql
import datetime
import threading
import sorfcom
import periphery

import random


class gpio_mn():
    class __SensorData__:
        def __init__(self, temp=0, co2=0, light=0):
            self.temp = temp
            self.co2 = co2
            self.light = light

    class __LED__:
        def __init__(self, r, g, b):
            self.r = r
            self.g = g
            self.b = b

    class __sgp30__:
        def __init__(self):
            self.addr = 0x58
            self.i2c = periphery.I2C("/dev/i2c-0")
            self.stat = False

            th = threading.Thread(target=self.__wait_init__)

            msgs = [self.i2c.Message([0x20, 0x03])]
            self.i2c.transfer(self.addr, msgs)
            th.start()

        def __wait_init__(self):
            print("please wait 15s for sgp30 init")
            time.sleep(15)
            self.stat = True

        def read(self):
            '''
            获取sgp30数据, 初始化至少15秒使用
            返回co2, tvoc
            :return: int, int
            '''
            while not self.stat:
                time.sleep(1)
            msgs = [self.i2c.Message([0x20, 0x08])]
            self.i2c.transfer(self.addr, msgs)
            time.sleep(0.1)
            msgs = [self.i2c.Message([0x00, 0x00, 0x00, 0x00], read=True)]
            self.i2c.transfer(self.addr, msgs)
            return int(msgs[0].data[0]) << 4 | int(msgs[0].data[1]), int(msgs[0].data[2]) << 4 | int(msgs[0].data[3])


    def __init__(self):
        self.data = self.__SensorData__(temp=0, co2=0, light=0)
        self.datas = []
        self.delay = 0.5
        self.runing = False
        self.record_time = datetime.datetime.now()
        self.th = threading.Thread(target=self.__get_gpio__)
        self.td = threading.Thread(target=self.__write_db__)
        self.wait_write = True
        self.read_history_lock = False
        self.conn = None
        self.cursor = None
        self.__conn_db__()

        # self.ad7705 = periphery.SPI("/dev/spidev0.0", 0, 4915200, "msb", 16, 0)
        # self.sgp30 = periphery.I2C("/dev/i2c-0")
        # self.gpio = self.__LED__(r=periphery.GPIO("/dev/gpiochip0", 42, "out"), g=periphery.GPIO("/dev/gpiochip0", 43, "out"), b=periphery.GPIO("/dev/gpiochip0", 47, "out"))

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        self.runing = False

    def __conn_db__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="farmer",
            password="12358",
            database="wise_farm"
        )
        self.cursor = self.conn.cursor()

    def __clos_db__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __get_gpio__(self):
        old_time = datetime.datetime.now()
        self.record_time = old_time
        print("gpio server started!")
        self.td.start()
        while self.runing:
            self.data.temp = random.randint(0,30)
            self.data.co2 = random.randint(0,500)
            self.data.light = random.randint(0,100)
            self.datas.append([self.data.temp, self.data.co2, self.data.light])
            current_time = datetime.datetime.now()
            current_minute = current_time.minute
            if old_time.minute > 56:
                current_minute = current_minute + 60
            if current_minute - old_time.minute >= 3:
                self.record_time = old_time
                old_time = current_time
                if self.td.is_alive():
                    self.wait_write = False
            time.sleep(self.delay)
        print("gpio server stopped!")
        self.td.join()
        return None

    def __write_db__(self):
        self.__conn_db__()
        table_name = self.record_time.strftime('data%Y%m%d')
        self.cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        if self.cursor.fetchone():
            print(f"表 '{table_name}' 存在")
        else:
            sql = "create table " + table_name + "(time DATETIME, temp FLOAT, co2 FLOAT, light FLOAT)"
            try:
                self.cursor.execute(sql)
                self.conn.commit()
                print("创建成功")
            except Exception as e:
                self.conn.rollback()
                print("创建失败失败:", e)
        print("data server started!")
        while self.runing:
            while self.wait_write or self.read_history_lock:
                time.sleep(1)
            tmp_list = []
            tmp_list.append(self.record_time.strftime('%Y-%m-%d %H:%M'))
            for i in range(3):
                tmp = 0
                for j in self.datas:
                    tmp = tmp + j[i]
                tmp = tmp /len(self.datas)
                tmp_list.append(tmp)
            sql = "INSERT INTO " + table_name + "(time, temp, co2, light) VALUES (%s, %s, %s, %s)"
            data = tuple(tmp_list)
            tmp_list.clear()
            try:
                self.cursor.execute(sql, data)
                self.conn.commit()
                print("数据插入成功")
            except Exception as e:
                self.conn.rollback()
                print("数据插入失败:", e)
            self.datas.clear()
            self.wait_write = True
        self.__clos_db__()
        print("data server stopped!")

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

                self.runing = True
                self.th.start()

        elif cmd == "stop":
            if self.th.is_alive():
                self.runing = False
                self.th.join()
            else:
                print("server is not running!!")
        return None

    def history(self, type="general", table=None):
        '''
        获取历史数据
        :param type: 获取数据类型, 可选"general" "detail"
        :type type: str
        :param table: 数据表名
        :type table: str
        :return: list
        '''

        while not self.wait_write:
            time.sleep(1)
        if type == "detail" and table is None:
            return None

        self.read_history_lock = True
        self.__conn_db__()
        if type == "general":
            sql = "show tables"
        elif type == "detail":
            sql = "select * from " + table
        else:
            return None

        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
        except Exception as e:
            print(e)
            return None

        self.__clos_db__()
        self.read_history_lock = False
        return data

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

    def write(self, *args):
        pass
