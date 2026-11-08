# Student Information System (Fixed Version)

## Requirements
- Python 3.10 or newer
- Flask
- Flask-WTF

## Setup on Windows

1. Extract this ZIP file.
2. Open Command Prompt inside the extracted `student-information-system` folder.
3. (Recommended) Create a fresh virtual environment:

   ```bat
   py -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   py -m pip install -r requirements.txt
   ```

5. Start the application:

   ```bat
   py app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## CRUD fixes included
- Add Student now has a complete POST form, CSRF hidden field, and Save Student button.
- Edit Student submits a valid CSRF hidden field.
- Delete Student uses a valid CSRF hidden field and requires a POST confirmation.
- SQLite connections are committed/rolled back and always closed.
- Search checks student ID, first/middle/last name, email, department, and course.
- Duplicate student IDs are checked before insert/update.
- Existing SQLite database and student records are preserved.

## Important
- Do not copy the old `venv` folder into this project. Create a fresh virtual environment using the steps above.
- Back up `student_information.db` before making major changes.
- For deployment, set a strong `SECRET_KEY` environment variable. Do not use the development fallback key on a public server.
- Debug mode is off by default. Set `FLASK_DEBUG=1` only for local development.
