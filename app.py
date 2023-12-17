from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tododb'
mysql = MySQL(app)


@app.route('/', methods=['POST', 'GET'])
def index():

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        content = request.form['content']
        cur.execute("INSERT INTO TODO(content) VALUES (%s)", [content])

        mysql.connection.commit()
        cur.close()
        return redirect('/')
    else:
        cur.execute("SELECT * FROM TODO")
        tasks = cur.fetchall()
        return render_template('index.html', tasks=tasks)


if __name__ == "__main__":
    app.run(debug=True)
