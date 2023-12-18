from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tododb'
mysql = MySQL(app)


def get_column_names():
    cur = mysql.connection.cursor()
    cur.execute("SHOW COLUMNS FROM ATTENDANCE")
    # Fetch all columns and exclude the first one (ID)
    columns = cur.fetchall()[1:]
    column_names = [column[0] for column in columns]
    cur.close()
    return column_names


@app.route('/', methods=['POST', 'GET'])
def index():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        NAME = request.form['NAME']
        cur.execute("INSERT INTO ATTENDANCE(NAME) VALUES (%s)", [NAME])
        mysql.connection.commit()
        cur.close()
        return redirect('/')
    else:
        cur.execute("SELECT * FROM ATTENDANCE")
        tasks = cur.fetchall()
        column_names = get_column_names()
        print(tasks)
        return render_template('index.html', tasks=tasks, column_names=column_names)


if __name__ == "__main__":
    app.run(debug=True)
