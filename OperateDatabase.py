class OperateDatabase:
    def __init__(self):
        self.conn = None

    def set_connection(self, conn):
        self.conn = conn

    def delete_database(self, condition, table):
        """
        从数据库中删除条件为 condition 的记录，使用示例
        self.delete_database("A='{a_content}'", table_name)
        :param condition: 条件，即 WHERE 后的内容
        :param table: 表名
        :return: 数据库本次操作 cursor
        """
        c = self.conn.cursor()
        sql = f"DELETE FROM '{table}' WHERE {condition}"
        # print(sql)
        c.execute(sql)
        self.conn.commit()
        return c

    def update_database(self, t, update_content, update_condition):
        """
        更新数据库数据，例如更新单词 set 的发音，将做如下操作
            UPDATE `pronounce`
            SET pronounce_bre = 'set_bre', pronounce_ame = 'set_ame'
            WHERE
            word = 'set'
        要实现上述语句，执行该函数的样例如下
            self.update_database("pronounce", f"pronounce_bre='{set_bre}',pronounce_ame='{set_ame}'", f"word='{word}'")
        :param t: 表名
        :param update_content: 语句中 SET 后的内容，具体样例：f"pronounce_bre='{set_bre}',pronounce_ame='{set_ame}'"
        :param update_condition: 语句中 WHERE 后的内容，具体样例：f"word='{word}'"
        :return: None
        """
        c = self.conn.cursor()
        update_sql = f"""UPDATE `{t}`
           SET {update_content}
           WHERE {update_condition}
           """
        print(update_sql)
        c.execute(update_sql)
        self.conn.commit()
        return c

    def insert_values_to_database(self, a, t):
        """
        向数据库插入数值
        :param a: 插入的数值字符串，格式为 A, B, C..., 其中，A、B、C都是要按照顺序插入的数值
        :param t: 表名
        :return: None
        """
        insert_sql = f"INSERT INTO `{t}` VALUES ({a})"
        c = self.conn.cursor()
        c.execute(insert_sql)
        self.conn.commit()

    def query_database_without_limits(self, t):
        """
        返回数据库中对应table的所有内容
        :param t: 表名
        :return: 查询table的全部内容
        """
        sql = f"SELECT * FROM `{t}`"
        return self.conn.cursor().execute(sql)

    def query_database(self, a, b, t):
        """
        :param a: 列名
        :param b: 对应值
        :param t: 表名
        :return: 查询结果
        """

        sql = f'SELECT * FROM {t} WHERE {a} = "{b}"'
        return self.conn.cursor().execute(sql)

    def close_database(self):
        """
        提交并断开数据库连接
        :return:
        """
        self.conn.commit()
        self.conn.close()
