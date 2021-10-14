import pymysql


db = pymysql.connect(host="adimsdb.mysteel.local", user="adims", password="Yj69%M,6=4ub", database="adims")
cursor = db.cursor()   # 使用cursor()方法获取操作游标
sql="truncate adims.t_event_new_history"
cursor.execute(sql)
db.commit()