from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from ai import generate_learning_path
from ai_chat import tutor_reply

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        goal TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists."

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/")

        return "Invalid Username or Password"

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- GENERATE ----------------

@app.route("/generate", methods=["POST"])
def generate():

    if "user" not in session:
        return redirect("/login")

    goal = request.form["goal"]

    result = generate_learning_path(goal)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO history(username,goal,result) VALUES(?,?,?)",
        (session["user"], goal, result)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        goal=goal,
        result=result
    )


# ---------------- HISTORY ----------------

@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "SELECT goal,result FROM history WHERE username=? ORDER BY id DESC",
        (session["user"],)
    )

    data = c.fetchall()

    conn.close()

    return render_template("history.html", data=data)


# ---------------- API ----------------

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json()

    goal = data.get("goal", "")

    result = generate_learning_path(goal)

    return jsonify({
        "goal": goal,
        "roadmap": result
    })


# ---------------- CHAT ----------------

@app.route("/chat")
def chat_page():
    if "user" not in session:
        return redirect("/login")

    return render_template("chat.html")


@app.route("/chat/api", methods=["POST"])
def chat_api():
    data = request.get_json()

    message = data["message"]

    reply = tutor_reply(
        message,
        "Backend Developer",
        ""
    )

    return jsonify({
        "reply": reply
    })


# ---------------- RUN ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)