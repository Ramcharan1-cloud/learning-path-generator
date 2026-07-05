from flask import Flask, render_template, request, redirect, session
import sqlite3
from ai import generate_learning_path

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        goal TEXT,
        result TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        print("Users in DB:", c.fetchall())

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        )
        user = c.fetchone()
        conn.close()

        print("Login result:", user)

        if user:
            session["user"] = u
            return redirect("/")

        return "Login failed"

    return render_template("register.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- HOME ----------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

# ---------------- GENERATE ----------------
@app.route("/generate", methods=["POST"])
def generate():
    goal = request.form["goal"]
    result = generate_learning_path(goal)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (username, goal, result) VALUES (?, ?, ?)",
              (session["user"], goal, result))
    conn.commit()
    conn.close()

    return render_template("result.html", goal=goal, result=result)

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE username=? ORDER BY id DESC",
              (session["user"],))
    data = c.fetchall()
    conn.close()

    return render_template("history.html", data=data)

# ---------------- RUN ----------------
@app.route("/api/generate", methods=["POST"])
def api_generate():
    from flask import jsonify

    data = request.get_json()
    goal = data.get("goal")

    result = generate_learning_path(goal)

    return jsonify({
        "goal": goal,
        "roadmap": result
    })


import os

if __name__ == "__main__":
    print("🚀 Flask server starting...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)