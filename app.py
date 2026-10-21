
import os
import sqlite3
from functools import wraps
from pathlib import Path
from flask_wtf.csrf import CSRFProtect

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"

app = Flask(__name__)

secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError("Set the SECRET_KEY environment variable first.")

app.config.update(
    SECRET_KEY=secret_key,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Local HTTP development only
)

csrf = CSRFProtect(app)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    db.commit()
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/")
def home():
    if session.get("user_id") is not None:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.")
            return render_template("register.html"), 400

        if len(username) > 50 or len(password) < 12:
            flash("Username must be at most 50 characters and password at least 12.")
            return render_template("register.html"), 400

        password_hash = generate_password_hash(password)

        try:
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("That username is already taken.")
            return render_template("register.html"), 409

        flash("Account created. You can now log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT id, username, password_hash, role "
            "FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user is None or not check_password_hash(
            user["password_hash"], password
        ):
            flash("Invalid username or password.")
            return render_template("login.html"), 401

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        username=session["username"],
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
