
import os
import re
import sqlite3
from datetime import date

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort
)
from flask_wtf.csrf import CSRFProtect

import database


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "sis-development-key-change-before-deployment"
)

csrf = CSRFProtect(app)

database.init_db()


FIELDS = [
    "student_id", "first_name", "middle_name", "last_name",
    "gender", "date_of_birth", "email", "contact_number",
    "address", "department", "course", "year_level",
    "section", "enrollment_date", "student_status"
]

DEPARTMENTS = [
    "Information Technology",
    "Computer Science",
    "Information Systems",
    "Computer Engineering"
]

COURSES = ["BSIT", "BSCS", "BSIS", "BSCpE"]

YEAR_LEVELS = [
    "1st Year", "2nd Year", "3rd Year", "4th Year"
]

STATUSES = ["Active", "Inactive", "Graduated", "Transferred"]


def validate_student(form, student_id=None):
    data = {field: form.get(field, "").strip() for field in FIELDS}
    errors = []

    required = [
        "student_id", "first_name", "last_name", "gender",
        "date_of_birth", "email", "contact_number",
        "address", "department", "course", "year_level",
        "section", "enrollment_date", "student_status"
    ]

    for field in required:
        if not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    if data["gender"] not in ["Male", "Female"]:
        errors.append("Please select a valid gender.")

    if data["department"] not in DEPARTMENTS:
        errors.append("Please select a valid department.")

    if data["course"] not in COURSES:
        errors.append("Please select a valid course.")

    if data["year_level"] not in YEAR_LEVELS:
        errors.append("Please select a valid year level.")

    if data["student_status"] not in STATUSES:
        errors.append("Please select a valid student status.")

    if data["student_id"] and len(data["student_id"]) > 30:
        errors.append("Student ID must not exceed 30 characters.")

    for field in ["first_name", "middle_name", "last_name"]:
        if len(data[field]) > 100:
            errors.append("Names must not exceed 100 characters.")

    if data["email"] and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]
    ):
        errors.append("Enter a valid email address.")

    if data["email"] and len(data["email"]) > 254:
        errors.append("Email is too long.")

    if data["contact_number"] and not re.fullmatch(
        r"[0-9+\-\s()]{7,20}", data["contact_number"]
    ):
        errors.append("Enter a valid contact number.")

    if data["date_of_birth"]:
        try:
            dob = date.fromisoformat(data["date_of_birth"])
            if dob > date.today():
                errors.append("Date of birth cannot be in the future.")
        except ValueError:
            errors.append("Invalid date of birth.")

    if data["enrollment_date"]:
        try:
            date.fromisoformat(data["enrollment_date"])
        except ValueError:
            errors.append("Invalid enrollment date.")

    if data["student_id"] and database.student_id_exists(
        data["student_id"], student_id
    ):
        errors.append("Student ID already exists.")

    return data, errors


def student_values(data):
    return tuple(data[field] for field in FIELDS)


@app.route("/")
def dashboard():
    stats = database.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


@app.route("/students")
def students():
    search = request.args.get("search", "").strip()
    records = database.get_all_students(search)
    return render_template(
        "students.html", students=records, search=search
    )


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        data, errors = validate_student(request.form)

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "add_student.html",
                departments=DEPARTMENTS,
                courses=COURSES,
                years=YEAR_LEVELS,
                statuses=STATUSES,
                form_data=data
            )

        try:
            database.add_student(student_values(data))
            flash("Student registered successfully!", "success")
            return redirect(url_for("students"))

        except sqlite3.IntegrityError:
            flash("Student ID already exists.", "error")

        except sqlite3.Error:
            app.logger.exception("Database error while adding student.")
            flash("Unable to save student. Please try again.", "error")

        return render_template(
            "add_student.html",
            departments=DEPARTMENTS,
            courses=COURSES,
            years=YEAR_LEVELS,
            statuses=STATUSES,
            form_data=data
        )

    return render_template(
        "add_student.html",
        departments=DEPARTMENTS,
        courses=COURSES,
        years=YEAR_LEVELS,
        statuses=STATUSES,
        form_data={}
    )


@app.route("/view_student/<int:id>")
def view_student(id):
    student = database.get_student(id)

    if student is None:
        abort(404)

    return render_template("view_student.html", student=student)


@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    student = database.get_student(id)

    if student is None:
        abort(404)

    if request.method == "POST":
        data, errors = validate_student(request.form, id)

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "edit_student.html",
                student=data,
                departments=DEPARTMENTS,
                courses=COURSES,
                years=YEAR_LEVELS,
                statuses=STATUSES
            )

        try:
            database.update_student(id, student_values(data))
            flash("Student information updated successfully!", "success")
            return redirect(url_for("students"))

        except sqlite3.IntegrityError:
            flash("Student ID already exists.", "error")

        except sqlite3.Error:
            app.logger.exception("Database error while updating student.")
            flash("Unable to update student. Please try again.", "error")

        return render_template(
            "edit_student.html",
            student=data,
            departments=DEPARTMENTS,
            courses=COURSES,
            years=YEAR_LEVELS,
            statuses=STATUSES
        )

    return render_template(
        "edit_student.html",
        student=student,
        departments=DEPARTMENTS,
        courses=COURSES,
        years=YEAR_LEVELS,
        statuses=STATUSES
    )


@app.route("/delete_student/<int:id>", methods=["GET", "POST"])
def delete_student(id):
    student = database.get_student(id)

    if student is None:
        abort(404)

    if request.method == "POST":
        try:
            database.delete_student(id)
            flash("Student deleted successfully.", "success")
            return redirect(url_for("students"))

        except sqlite3.Error:
            app.logger.exception("Database error while deleting student.")
            flash("Unable to delete student.", "error")
            return redirect(url_for("students"))

    return render_template("delete_student.html", student=student)


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Page or student not found."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template(
        "error.html",
        message="An unexpected error occurred."
    ), 500


if __name__ == "__main__":
    # Set FLASK_DEBUG=1 only during local development.
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1"
    )
