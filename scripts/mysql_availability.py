import pymysql

def check_mysql_up():
    try:
        conn = pymysql.connect(
        host='localhost',
        user='taskuser',
        password='taskpass',
        database='tasks',
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
        )   
        if conn.open:
            print("MySQL is UP")
            conn.close()
            return True
    except pymysql.MySQLError as e:
        print(f"MySQL Down: {e}")
        return False
    return False

if __name__ == "__main__":
    check_mysql_up()