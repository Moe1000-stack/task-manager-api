from flask import Flask, jsonify, request
from datetime import datetime
import json
import os

app = Flask(__name__)
DATA_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_tasks(tasks):
    with open(DATA_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Task Manager API",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "GET /tasks/<id>": "Get one task",
            "POST /tasks": "Create a task",
            "PUT /tasks/<id>": "Update a task",
            "DELETE /tasks/<id>": "Delete a task"
        }
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks()), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Task title is required"}), 400

    tasks = load_tasks()

    new_task = {
        "id": get_next_id(tasks),
        "title": data["title"],
        "description": data.get("description", ""),
        "completed": False,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    tasks = load_tasks()

    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if "title" in data:
        if not data["title"]:
            return jsonify({"error": "Title cannot be empty"}), 400
        task["title"] = data["title"]

    if "description" in data:
        task["description"] = data["description"]

    if "completed" in data:
        if not isinstance(data["completed"], bool):
            return jsonify({"error": "Completed must be true or false"}), 400
        task["completed"] = data["completed"]

    save_tasks(tasks)
    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()

    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)

    return jsonify({"message": "Task deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)
