#!/usr/bin/env python3
# _*_ coding: utf-8 _*_


"""
auth: sunhaobo
version:
function: MySQL操作类, Use PyMySQL
usage:
note: 读取配置文件的配置，创建游标对象操作数据库（保证了数据的原子性），
      写了3个数据库处理函数 insertmany(),exec(),find()，剩下的处理函数没有写完后续可以补充。
      使用了with...as...上下文管理器机制处理报错，使代码简洁了许多。
date:2022-11-15
"""

import time
import pymysql
import traceback
from comm.getconfig import get_config


class SQL(object):
    config = get_config()   # 从 配置文件 中读取配置

    # config = {
    #     "name": "config file",
    #     "version": "1.0.0",
    #     "modify": "2019.12.26",
    #     "author": "wangzhangzheng",
    #     "database": {
    #         "godv": {
    #             "hostname": "mysql11146w.zll.yun.qianxin-inc.cn",
    #             "username": "godv",
    #             "password": "7dde2636c4939967",
    #             "database": "godv",
    #             "port": 11146
    #         }
    #     }
    # }

    def __init__(self):  # 读取过来的配置编入自己的属性变量
        self.config = self.config['database']['godv']
        self.hostname = self.config['hostname']
        self.username = self.config['username']
        self.password = self.config['password']
        self.database = self.config['database']
        self.port = int(self.config['port'])
        self.charset = 'utf8'  # 防止乱码，定义死符号
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 上文管理器 with 返回的结果 会被赋给 as 关键字之后的变量  # 上下文管理器 语法：with...as.. 参考：https://www.cnblogs.com/lipijin/p/4460487.html
        # :return: cursor                              # 当 with 开始时候触发__enter__执行，当with结束后触发__exit__执行

    def __enter__(self):
        try:
            self.conn = pymysql.connect(  # 创建mysql数据库链接
                host=self.hostname,
                user=self.username,
                password=self.password,
                db=self.database,
                port=self.port,
                charset=self.charset,
            )

            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)  # 创建游标对象  通过游标对数据库进行操作
            # self.conn.cursor() 创建普通的游标对象
            # pymysql.cursors.DictCursor 以字典的形式返回结果
            return self.cursor
        except Exception as error:
            print(self.time, 'comm.mysql.SQL.__enter__ have error: %s' % error)
            traceback.print_exc()
            # raise error
            """
            # 连接数据库
            db = pymysql.connect("localhost", "root", "LBLB1212@@", "dbforpymysql")
            # 使用cursor()方法创建一个游标对象
            cursor = db.cursor()
            # 使用execute()方法执行SQL语句
            cursor.execute("SELECT * FROM userinfo")
            # 使用fetall()获取全部数据
            data = cursor.fetchall()
            # 打印获取到的数据
            print(data)
            # 关闭游标和数据库的连接
            cursor.close()
            db.close()
            """

        # 下文管理器 选择性地处理包装代码块中出现的异常   # 如果抛出出异常，则
        # :param exc_type: 获取异常类型 默认为 None,发生异常,参数被填充
        # :param exc_val: 获取异常实例 默认为 None,发生异常,参数被填充
        # :param exc_tb: 获取异常回溯 默认为 None,发生异常,参数被填充,获取异常位置
        # :return:

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:  # 如果报错异常
                self.conn.rollback()  # 数据回滚，保证数据的源子性，多条sql语句要么都执行要么都不执行
                return False
            else:
                self.conn.commit()  # 提交操作（不报错就提交执行sql语句）
        except Exception as error:
            print(self.time, 'comm.mysql.SQL.__exit__ have error: %s' % error)
            # raise error
        finally:
            self.cursor.close()  # 关闭游标对象
            self.conn.close()  # 关闭数据库链接


# Mysql类
class MySQL:
    def __init__(self, sql):  # 自带一个sql语句属性
        self.sql = sql
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 自带时间属性

    def add(self):  # 这些其实都可以补充，只是这里用不到这个处理函数
        return

    def delete(self):  # 这些其实都可以补充，只是这里用不到这个处理函数
        return

    def insert(self):  # 这些其实都可以补充，只是这里用不到这个处理函数
        return

    def insertmany(self, data):  # 同时写入多个语句
        # data 需要是 list 或 set
        with SQL() as cursor:  # 上下文管理器的使用，SQL()返回的结果被赋值给cursor，类型不变，且关闭了SQL()的句柄（不用专门关闭，代码简洁）
            try:  # 在这里利用with...as..上文管理器巧妙的关闭了数据库游标对象，还不用写出来 cursor.close()，因为在SQL()中已经封装关闭了
                cursor.executemany(self.sql, data)  # 使用as之后的cursor执行的语句
                return {
                    'state': 1,
                    'msg': 'insert many data successfully'
                }
            except Exception as error:
                print(self.time, 'comm.mysql.MySQL.insertmany have error: %s' % error)
                return {
                    'state': 0,
                    'msg': 'insert many data failed, error: %s' % error
                }

    def find(self):  # 查找数据
        with SQL() as cursor:  # 上下文管理器的使用，SQL()返回的结果被赋值给cursor，类型不变，且关闭了SQL()的句柄（不用专门关闭，代码简洁）
            try:
                cursor.execute(sql)
                res = cursor.fetchall()  # 全部读取数据
                if res:
                    return {
                        'state': 1,
                        'data': res,  # 读取的数据放入字典中
                        'msg': 'sql exec successfully'
                    }
                else:
                    return {
                        'state': 1,
                        'data': None,
                        'msg': 'no data found'
                    }
            except pymysql.err.ProgrammingError as error:
                print(self.time, 'comm.mysql.MySQL.find have error: %s' % error)
                return {
                    'state': 0,
                    'data': None,
                    'msg': error.args
                }

    def exec(self):  # 执行sql语句函数
        with SQL() as cursor:
            try:
                cursor.execute(self.sql)
                res = cursor.fetchall()
                if res:
                    state = 1
                    data = res
                    msg = 'sql exec successfully'
                else:  # data 为空
                    state = 1
                    data = []
                    msg = 'no data found'
            except pymysql.err.ProgrammingError as error:
                print(self.time, 'comm.mysql.MySQL.exec have error: %s' % error)
                state = 0
                data = []
                msg = error.args
            except Exception as error:
                print(self.time, 'comm.mysql.MySQL.exec have error: %s' % error)
                state = 0
                data = []
                msg = error

        return {'state': state, 'data': data, 'msg': msg}


if __name__ == '__main__':
    sql = "SELECT domain FROM asset_dns_records WHERE updateTime < DATE_SUB(NOW(), INTERVAL 3 DAY)"
    res = MySQL(sql=sql).exec()  # 可用 20241223
    print(res)
