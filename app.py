from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-key"

BOOKS_FILE = "books.json"

# simple auth: one user
VALID_USER = {"username": "user", "password": "pass123"}


def load_books():
    with open(BOOKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get("logged_in"):
            return f(*args, **kwargs)
        return redirect(url_for("login", next=request.path))
    return wrapped


@app.route("/")
def home():
    # frontend will call Open Library directly for trending.
    return render_template("index.html")


@app.route("/library")
@login_required
def library():
    books = load_books()
    return render_template("library.html", books=books)


@app.route("/notes")
def notes():
    # page will ask class and open filtered view in client JS or new tab.
    return render_template("notes.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Minimal behavior: print to console. In production, send email.
        data = request.form.to_dict()
        print("Contact form submitted:", data)
        return render_template("contact.html", sent=True)
    return render_template("contact.html", sent=False)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # simplified if-else login check
        if username == VALID_USER["username"]:
            if password == VALID_USER["password"]:
                session["logged_in"] = True
                session["username"] = username
                nxt = request.args.get("next") or url_for("library")
                return redirect(nxt)
            else:
                error = "Incorrect password."
                return render_template("login.html", error=error)
        else:
            error = "User not found."
            return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/api/books")
def api_books():
    return jsonify(load_books())


if __name__ == "__main__":
    app.run(debug=True)
