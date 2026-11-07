from flask import Flask, render_template
import sqlite3

app = Flask(__name__, static_url_path="/viikko2/static")

DATABASE = "/opt/viikko2/visits.db"


def get_visits():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY,
            count INTEGER NOT NULL
        )
    """)

    cursor.execute("SELECT count FROM visits WHERE id = 1")
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO visits (id, count) VALUES (1, 1)")
        count = 1
    else:
        count = result[0] + 1
        cursor.execute("UPDATE visits SET count = ? WHERE id = 1", (count,))

    connection.commit()
    connection.close()

    return count


@app.route("/")
@app.route("/viikko2/")
def index():
    visits = get_visits()
    return render_template("index.html", visits=visits)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
