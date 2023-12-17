from datetime import date, datetime
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tododb'
mysql = MySQL(app)
today_date = date.today().strftime("%Y_%m_%d")
name = "ARJUN2226"
now = datetime.now()
time = now.strftime('%H:%M:%S')
with app.app_context():
    cur = mysql.connection.cursor()
    cur = mysql.connection.cursor()

    check = f"SELECT * FROM TODO WHERE CONTENT='{name}'"
    # check_query = f"SELECT {today_date} from todo where content='{name}'"
    cur.execute(check)

    # Fetch the result
    result = cur.fetchone()
    print("Result: ", result)
    if result is None:
        student_insert = f"INSERT INTO TODO(CONTENT, {today_date}) VALUES('{name}', '{time}')"
        cur.execute(student_insert)
        mysql.connection.commit()
    elif result[-1] == 'absent':
        mark_present_query = f"UPDATE todo SET {today_date}='{time}' WHERE content='{name}'"
        cur.execute(mark_present_query)
        mysql.connection.commit()

    cur.close()
