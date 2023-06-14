from django.db import connection


# 数据库操作类
class mysql(object):

    # 连接数据库
    def __init__(self):
        # 连接database
        self.conn = connection

    # 关闭连接
    def closeConn(self):
        self.conn.close()

    # 查询
    def select(self, sql):
        # 执行sql语句 查询
        cursor = self.conn.cursor()
        cursor.execute(sql)
        field = cursor.description
        # 获取所有
        rows = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        # print(field)
        # print(rows)
        resuleRows = []
        for row in rows:
            rowDict = {}
            for index, fieldData in enumerate(row):
                rowDict[field[index][0]] = fieldData
            resuleRows.append(rowDict)
        return resuleRows

    # 新增
    def insert(self, tabelName, keys, values):
        cursor = self.conn.cursor()
        keyStr = ""
        for key in keys:
            keyStr += (key + ",")
        valueStr = ""
        if len(values) > 0:
            for i in values:
                valueStr += ("%s,")

            sql = "INSERT INTO " + tabelName + " (" + keyStr[:-1] + ") " + " VALUES (" + valueStr[:-1] + ");"
            cursor.execute(sql, values)
            self.conn.commit()
            rowcount = cursor.rowcount
            lastrowid = cursor.lastrowid
            cursor.close()
            return rowcount, lastrowid
        else:
            return 0

    # 修改
    def update(self, table_name, updateData, whereLabel):
        cursor = self.conn.cursor()
        for data in updateData:
            whereColumn = ""
            setColumn = ""
            for k, v in data.items():
                if k == whereLabel:
                    if type(v) == str:
                        whereColumn = "'" + v + "'"
                    elif type(v) == int:
                        whereColumn = str(v)
                else:
                    if type(v) == str:
                        setColumn += (" " + k + " = '" + v + "' ,")
                    elif type(v) == int:
                        setColumn += (" " + k + " = " + str(v) + " ,")
                    elif type(v) == bytes:
                        setColumn += (" " + k + " = (X'" + v.hex() + "') ,")

            sql = "Update " + table_name + " Set " + setColumn[:-1] + " Where " + whereLabel + " = " + whereColumn + ";"
            # print("执行sql===>", sql)
            try:
                cursor.execute(sql)
            except Exception as e:
                print("数据===>", data)
                print("错误===》", e)
        returnValue = self.conn.commit()
        cursor.close()
        return returnValue

    def delete(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
