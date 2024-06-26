import time
import pymysql
import datetime
import threading
import periphery

import random


class gpio_mn:
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
            """
            获取sgp30数据, 初始化至少15秒使用
            返回co2, tvoc
            :return: int, int
            """
            while not self.stat:
                time.sleep(1)
            msgs = [self.i2c.Message([0x20, 0x08])]
            self.i2c.transfer(self.addr, msgs)
            time.sleep(0.1)
            msgs = [self.i2c.Message([0x00, 0x00, 0x00, 0x00], read=True)]
            self.i2c.transfer(self.addr, msgs)
            return int(msgs[0].data[0]) << 8 | int(msgs[0].data[1]), int(msgs[0].data[2]) << 8 | int(msgs[0].data[3])

    class __ads1115__:
        def __init__(self):
            self.addr = 0x48
            self.i2c = periphery.I2C("/dev/i2c-0")
            self.temp_ch = [0x84, 0x83]
            self.light_ch = [0xc4, 0x83]

        def read(self, config):
            # 写入配置寄存器，启动单次转换
            msgs = [self.i2c.Message([0x00] + config)]
            self.i2c.transfer(self.addr, msgs)
            time.sleep(0.01)
            msgs = [self.i2c.Message([0x00]), self.i2c.Message([0x00, 0x00], read=True)]
            self.i2c.transfer(self.addr, msgs)
            result = (msgs[1].data[0] << 8) | msgs[1].data[1]
            if config == self.temp_ch:
                result = result * 30 / 32768
            elif config == self.light_ch:
                result = result * 100 / 32768
            return int(result)

    def __init__(self):
        self.data = self.__SensorData__(temp=0, co2=0, light=0)
        self.datas = []
        self.delay = 0.5
        self.running = False
        self.record_time = datetime.datetime.now()
        self.th = threading.Thread(target=self.__get_gpio__)
        self.td = threading.Thread(target=self.__write_db__)
        self.wait_write = True
        self.read_history_lock = False
        self.conn = None
        self.cursor = None
        self.sgp30 = self.__sgp30__()
        self.ads1115 = self.__ads1115__()
        self.__conn_db__()

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        self.running = False

    def __conn_db__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="farmer",
            password="12358",
            database="wise_farm"
        )
        self.cursor = self.conn.cursor()
        print("database connected!")

    def __clos_db__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("database closed!")

    def __get_gpio__(self):
        old_time = datetime.datetime.now()
        self.record_time = old_time
        print("gpio server started!")
        self.td.start()
        while self.running:
            self.data.temp = self.ads1115.read(self.ads1115.temp_ch)
            if self.sgp30.stat:
                self.data.co2, _ = self.sgp30.read()
            self.data.light = self.ads1115.read(self.ads1115.light_ch)
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
        self.__clos_db__()
        while self.running:
            while self.wait_write or self.read_history_lock:
                time.sleep(1)
            tmp_list = [self.record_time.strftime('%Y-%m-%d %H:%M')]
            for i in range(3):
                tmp = 0
                for j in self.datas:
                    tmp = tmp + j[i]
                tmp = tmp / len(self.datas)
                tmp_list.append(tmp)
            sql = "INSERT INTO " + table_name + "(time, temp, co2, light) VALUES (%s, %s, %s, %s)"
            data = tuple(tmp_list)
            tmp_list.clear()
            self.__conn_db__()
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

    def gpio_server(self, cmd="start", frequent=2):
        """
        用于循环读取gpio数据，在单独线程中执行
        :param cmd: 控制命令, 可选"start" "stop"
        :param frequent: gpio读取频率 hz 最高200
        :type frequent: int
        :return: None
        """

        if cmd == "start":
            if self.th.is_alive():
                print("server is already running!!")
            else:
                if frequent > 200:
                    frequent = 200
                elif frequent < 1:
                    frequent = 1
                self.delay = 1 / frequent

                self.running = True
                self.th.start()

        elif cmd == "stop":
            if self.th.is_alive():
                self.running = False
                self.th.join()
            else:
                print("server is not running!!")
        return None

    def history(self, dat_type="general", table=None):
        """
        获取历史数据
        :param dat_type: 获取数据类型, 可选"general" "detail"
        :type dat_type: str
        :param table: 数据表名
        :type table: str
        :return: list
        """

        while not self.wait_write:
            time.sleep(1)
        if dat_type == "detail" and table is None:
            return None

        self.read_history_lock = True
        self.__conn_db__()
        if dat_type == "general":
            sql = "show tables"
        elif dat_type == "detail":
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
        print(f"before return: {data}")
        return data

    def read(self, types="all"):
        """
        获取gpio数据
        :param types: 获取数据类型, 可选"all" "temp" "co2" "light"
        :type types: str
        :return: float | dict
        """
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
