"""Registration, login and logout routes."""

import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import UserMixin, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import login_manager
from app.database import get_db

auth = Blueprint("auth", __name__)


class User(UserMixin):
    """User model backed by the SQLite users table."""

    def __init__(self, user_id, username, email, password_hash):
        self.id = str(user_id)
        self.username = username
        self.email = email
        self.password_hash = password_hash


@login_manager.user_loader
def load_user(user_id):
    """Load a logged-in user from the database."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, username, email, password_hash "
            "FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return User(row["id"], row["username"], row["email"], row["password_hash"])


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) "
                "VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("That username or email is already registered.", "error")
            return render_template("register.html")
        finally:
            conn.close()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, username, email, password_hash "
                "FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        finally:
            conn.close()

        if row and check_password_hash(row["password_hash"], password):
            user = User(row["id"], row["username"], row["email"], row["password_hash"])
            login_user(user)
            return redirect(url_for("main.home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
