
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "tasks.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Initialize database
def initialize_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        """)


# Home page
@app.route("/")
def home():
    with get_db() as conn:
        tasks = conn.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    completed = sum(
        1 for task in tasks
        if task["status"] == "Completed"
    )

    pending = len(tasks) - completed

    return render_template(
        "index.html",
        tasks=tasks,
        completed=completed,
        pending=pending
    )


# Add task
@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,)
            )

    return redirect(url_for("home"))


# Update task status
@app.route("/update/<int:task_id>")
def update_task(task_id):
    with get_db() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET status = CASE
                WHEN status = 'Pending'
                THEN 'Completed'
                ELSE 'Pending'
            END
            WHERE id = ?
            """,
            (task_id,)
        )

    return redirect(url_for("home"))


# Delete task
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

    return redirect(url_for("home"))


# Health check endpoint
@app.route("/health")
def health():
    return {"status": "healthy"}, 200


# Initialize database automatically
initialize_db()


# Start application
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
