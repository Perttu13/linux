
from flask import Flask
import pymysql
import os

app = Flask(__name__)

def get_visitor_count():
    connection = pymysql.connect(
        host="localhost",
        user="week4reader",
        password=os.environ["DB_PASSWORD"],
        database="week4db",
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count FROM visitors WHERE id = 1")
            result = cursor.fetchone()
            return result["count"] if result else 0
    finally:
        connection.close()


@app.route("/")
def index():
    count = get_visitor_count()

    return f"""
    <!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Week 4 | Server B</title>
    </head>
    <body>
        <h1>Week 4 – Server B</h1>
        <h2>Replikoitu laskuri: {count}</h2>
        <p>Server B näyttää Server A:lta replikoidun arvon.</p>
        <p>Server B ei kasvata laskuria.</p>
        <p><a href="https://github.com/Perttu13/linux">GitHub-projekti</a></p>
        <p><a href="https://github.com/Perttu13/linux#readme">Dokumentaatio</a></p>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
