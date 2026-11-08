import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "student_information.db"


@contextmanager
def get_connection():
    """Open a SQLite connection and always close it after use."""
    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                middle_name TEXT,
                last_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                address TEXT NOT NULL,
                department TEXT NOT NULL,
                course TEXT NOT NULL,
                year_level TEXT NOT NULL,
                section TEXT NOT NULL,
                enrollment_date TEXT NOT NULL,
                student_status TEXT NOT NULL
            )
        """)

        count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            sample_students = [
                ("2026-0001", "Juan", "Santos", "Dela Cruz", "Male", "2005-01-15", "juan@example.com", "09171234501", "Angeles City", "Information Technology", "BSIT", "2nd Year", "A", "2026-06-01", "Active"),
                ("2026-0002", "Maria", "Reyes", "Garcia", "Female", "2005-03-20", "maria@example.com", "09171234502", "Mabalacat City", "Computer Science", "BSCS", "2nd Year", "A", "2026-06-01", "Active"),
                ("2026-0003", "Pedro", "Lopez", "Ramos", "Male", "2004-07-10", "pedro@example.com", "09171234503", "San Fernando City", "Information Systems", "BSIS", "3rd Year", "B", "2026-06-01", "Active"),
                ("2026-0004", "Ana", "Mendoza", "Flores", "Female", "2006-02-25", "ana@example.com", "09171234504", "Porac", "Computer Engineering", "BSCpE", "1st Year", "A", "2026-06-01", "Active"),
                ("2026-0005", "Mark", "Villanueva", "Perez", "Male", "2005-11-08", "mark@example.com", "09171234505", "Magalang", "Information Technology", "BSIT", "2nd Year", "B", "2026-06-01", "Active")
            ]
            conn.executemany("""
                INSERT INTO students (
                    student_id, first_name, middle_name, last_name, gender,
                    date_of_birth, email, contact_number, address, department,
                    course, year_level, section, enrollment_date, student_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_students)


def get_all_students(search=""):
    term = f"%{search}%"
    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ?
               OR first_name LIKE ?
               OR middle_name LIKE ?
               OR last_name LIKE ?
               OR email LIKE ?
               OR department LIKE ?
               OR course LIKE ?
            ORDER BY id DESC
        """, (term, term, term, term, term, term, term)).fetchall()


def get_student(student_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()


def add_student(data):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO students (
                student_id, first_name, middle_name, last_name, gender,
                date_of_birth, email, contact_number, address, department,
                course, year_level, section, enrollment_date, student_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        return cursor.lastrowid


def update_student(student_id, data):
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE students SET
                student_id = ?, first_name = ?, middle_name = ?, last_name = ?,
                gender = ?, date_of_birth = ?, email = ?, contact_number = ?,
                address = ?, department = ?, course = ?, year_level = ?,
                section = ?, enrollment_date = ?, student_status = ?
            WHERE id = ?
        """, (*data, student_id))
        return cursor.rowcount > 0


def delete_student(student_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        return cursor.rowcount > 0


def student_id_exists(student_id, exclude_id=None):
    with get_connection() as conn:
        if exclude_id is None:
            row = conn.execute(
                "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM students WHERE student_id = ? AND id != ?",
                (student_id, exclude_id)
            ).fetchone()
        return row is not None


def get_dashboard_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        male = conn.execute(
            "SELECT COUNT(*) FROM students WHERE gender = 'Male'"
        ).fetchone()[0]
        female = conn.execute(
            "SELECT COUNT(*) FROM students WHERE gender = 'Female'"
        ).fetchone()[0]
        departments = conn.execute(
            "SELECT COUNT(DISTINCT department) FROM students"
        ).fetchone()[0]
        recent = conn.execute(
            "SELECT * FROM students ORDER BY id DESC LIMIT 5"
        ).fetchall()
        return {
            "total": total,
            "male": male,
            "female": female,
            "departments": departments,
            "recent": recent
        }
