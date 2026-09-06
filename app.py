"""Todo Manager web application and JSON API."""

import os
from datetime import datetime, timezone

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///todo_manager.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

PRIORITIES = {"HIGH", "MEDIUM", "LOW"}
TAGS = {"WORK", "PERSONAL"}


@app.context_processor
def inject_datetime():
    return {"datetime": datetime}


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(10), nullable=False, default="MEDIUM")
    tag = db.Column(db.String(10), nullable=False, default="PERSONAL")
    print_flag = db.Column(db.Boolean, nullable=False, default=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Task {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.name,
            "name": self.name,
            "description": self.description,
            "creation_date": self.creation_date.isoformat(),
            "due_date": self.due_date.date().isoformat(),
            "priority": self.priority,
            "tag": self.tag,
            "print_flag": self.print_flag,
            "completed": self.completed,
        }

    def to_print_dict(self):
        data = self.to_dict()
        data["creation_date"] = self.creation_date
        data["due_date"] = self.due_date
        return data


def parse_boolean(value, field):
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    raise ValueError(f"{field} must be a boolean")


def parse_task_data(data, partial=False):
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")

    values = {}
    if "name" in data or not partial:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("name is required")
        if len(name) > 200:
            raise ValueError("name must be at most 200 characters")
        values["name"] = name

    if "description" in data:
        values["description"] = str(data["description"]).strip()

    if "due_date" in data or not partial:
        due_date = data.get("due_date")
        if not due_date:
            raise ValueError("due_date is required")
        try:
            values["due_date"] = datetime.strptime(str(due_date), "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("due_date must use YYYY-MM-DD format") from exc

    if "priority" in data or not partial:
        priority = str(data.get("priority", "MEDIUM")).upper()
        if priority not in PRIORITIES:
            raise ValueError("priority must be HIGH, MEDIUM, or LOW")
        values["priority"] = priority

    if "tag" in data or not partial:
        tag = str(data.get("tag", "PERSONAL")).upper()
        if tag not in TAGS:
            raise ValueError("tag must be WORK or PERSONAL")
        values["tag"] = tag

    for field in ("print_flag", "completed"):
        if field in data:
            values[field] = parse_boolean(data[field], field)

    return values


def print_task_card(task):
    from task_card_generator import create_task_image, print_to_thermal_printer

    image_path = create_task_image(task.to_print_dict())
    if not image_path:
        raise RuntimeError("Could not create task image")
    print_to_thermal_printer(image_path)


def filtered_tasks(args, active_by_default=True):
    query = Task.query
    tag = args.get("tag", "").upper()
    if tag:
        if tag not in TAGS:
            raise ValueError("tag must be WORK or PERSONAL")
        query = query.filter_by(tag=tag)

    completed = args.get("completed")
    if completed is not None:
        query = query.filter_by(completed=parse_boolean(completed, "completed"))
    elif active_by_default:
        query = query.filter_by(completed=False)

    return query.order_by(Task.due_date.asc())


def api_error(message, status=400):
    return jsonify({"error": message}), status


@app.route("/")
def index():
    try:
        tasks = filtered_tasks(request.args).all()
    except ValueError:
        tasks = Task.query.filter_by(completed=False).order_by(Task.due_date.asc()).all()
    selected_tag = request.args.get("tag", "").upper()
    return render_template("index.html", tasks=tasks, selected_tag=selected_tag)


@app.route("/add_task", methods=["POST"])
def add_task():
    try:
        values = parse_task_data(
            {
                "name": request.form.get("name", ""),
                "description": request.form.get("description", ""),
                "due_date": request.form.get("due_date", ""),
                "priority": request.form.get("priority", "MEDIUM"),
                "tag": request.form.get("tag", "PERSONAL"),
                "print_flag": "print_flag" in request.form,
            }
        )
        task = Task(**values)
        db.session.add(task)
        db.session.commit()
        if task.print_flag:
            try:
                print_task_card(task)
                flash(f'Task "{task.name}" added and sent to printer!', "success")
            except Exception:
                flash(f'Task "{task.name}" added but printing failed.', "warning")
        else:
            flash(f'Task "{task.name}" added successfully!', "success")
    except ValueError:
        flash("Invalid task data.", "error")
    except Exception:
        db.session.rollback()
        flash("Error adding task.", "error")
    return redirect(url_for("index"))


@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    task = db.get_or_404(Task, task_id)
    task.completed = True
    db.session.commit()
    flash(f'Task "{task.name}" marked as completed!', "success")
    return redirect(url_for("index"))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    task = db.get_or_404(Task, task_id)
    task_name = task.name
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{task_name}" deleted!', "success")
    return redirect(url_for("index"))


@app.route("/clear_all", methods=["POST"])
def clear_all():
    tasks = Task.query.filter_by(completed=False).all()
    for task in tasks:
        task.completed = True
    db.session.commit()
    flash(f"{len(tasks)} tasks marked as completed!", "success")
    return redirect(url_for("index"))


@app.route("/print_task/<int:task_id>", methods=["POST"])
def print_task(task_id):
    task = db.get_or_404(Task, task_id)
    try:
        print_task_card(task)
        flash(f'Task "{task.name}" sent to printer!', "success")
    except Exception:
        flash("Printing failed.", "error")
    return redirect(url_for("index"))


@app.route("/api/tasks", methods=["GET"])
def api_list_tasks():
    try:
        return jsonify([task.to_dict() for task in filtered_tasks(request.args).all()])
    except ValueError:
        return api_error("Invalid filter")


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    try:
        values = parse_task_data(request.get_json(silent=True))
        task = Task(**values)
        db.session.add(task)
        db.session.commit()
        response = {"task": task.to_dict()}
        if task.print_flag:
            try:
                print_task_card(task)
                response["printed"] = True
            except Exception:
                response["printed"] = False
                response["print_error"] = "Printing failed"
        return jsonify(response), 201
    except ValueError:
        return api_error("Invalid task data")
    except Exception:
        db.session.rollback()
        return api_error("Unable to create task", 500)


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return api_error("Task not found", 404)
    return jsonify(task.to_dict())


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def api_update_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return api_error("Task not found", 404)
    try:
        values = parse_task_data(request.get_json(silent=True), partial=True)
        if not values:
            raise ValueError("At least one task field is required")
        for field, value in values.items():
            setattr(task, field, value)
        db.session.commit()
        return jsonify(task.to_dict())
    except ValueError:
        return api_error("Invalid task data")
    except Exception:
        db.session.rollback()
        return api_error("Unable to update task", 500)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return api_error("Task not found", 404)
    db.session.delete(task)
    db.session.commit()
    return "", 204


@app.route("/api/tasks/<int:task_id>/complete", methods=["POST"])
def api_complete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return api_error("Task not found", 404)
    task.completed = True
    db.session.commit()
    return jsonify(task.to_dict())


@app.route("/api/tasks/<int:task_id>/print", methods=["POST"])
def api_print_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return api_error("Task not found", 404)
    try:
        print_task_card(task)
        return jsonify({"printed": True, "task": task.to_dict()})
    except Exception:
        return api_error("Printing failed", 502)


@app.route("/api/tasks/complete-all", methods=["POST"])
def api_complete_all_tasks():
    try:
        tasks = filtered_tasks(request.args).all()
    except ValueError:
        return api_error("Invalid filter")
    for task in tasks:
        task.completed = True
    db.session.commit()
    return jsonify({"completed_count": len(tasks)})


def initialize_database():
    db.create_all()
    columns = {column["name"] for column in inspect(db.engine).get_columns("task")}
    if "tag" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE task ADD COLUMN tag VARCHAR(10) "
                "NOT NULL DEFAULT 'PERSONAL'"
            )
        )
        db.session.commit()


with app.app_context():
    initialize_database()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(debug=os.getenv("FLASK_DEBUG") == "1", host="0.0.0.0", port=port)
