
from flask import Flask
import pymysql
import os

app = Flask(__name__)

def get_connection():
    return pymysql.connect(
        unix_socket="/run/mysqld/mysqld.sock",
        user="week4writer",
        password=os.environ["DB_PASSWORD"],
        database="week4db",
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def index():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE visitors SET count = count + 1 WHERE id = 1"
            )
            connection.commit()

            cursor.execute("SELECT count FROM visitors WHERE id = 1")
            result = cursor.fetchone()
            count = result["count"] if result else 0
    finally:
        connection.close()

    return f"""
    <!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <title>Week 4 - Server A</title>
    </head>
    <body>
        <h1>Week 4 - Server A</h1>
        <h2>Kävijälaskuri: {count}</h2>
        <p>Server A kasvattaa laskuria.</p>
        <p>Arvo replikoidaan Server B:n tietokantaan.</p>
        <p><a href="https://github.com/Perttu13/linux">GitHub-projekti</a></p>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
