import os
import json
from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta

app = Flask(__name__)

# --- MySQL Database Configuration ---
# Your actual database details are now directly in the file.
# Remember that for production deployments, using environment variables
# (as in the previous version) is generally more secure.
DB_CONFIG = {
    'host': 'mysql6013.site4now.net',
    'port': 3306, # Assuming default MySQL port as not explicitly provided in new image
    'database': 'db_abc901_omarelh',
    'user': 'abc901_omarelh',
    'password': 'omarreda123'
}

# --- Database Connection Helper ---
def create_db_connection():
    """Establishes a connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"Successfully connected to MySQL database: {DB_CONFIG['database']}")
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return connection

# --- Database Initialization (Create Tables) ---
def initialize_database():
    """
    Creates necessary tables if they don't exist.
    This function should be called once when the application starts or for setup.
    In a Vercel serverless function, this will run on each invocation,
    but `CREATE TABLE IF NOT EXISTS` ensures idempotency (it won't re-create).
    """
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Users table (basic for now, can be expanded with hashing for passwords)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE
                )
            """)
            # Medical Student Hub
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_plans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    day_of_week VARCHAR(10),
                    time_slot VARCHAR(50),
                    topic VARCHAR(255),
                    resource_type VARCHAR(50),
                    is_completed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    subject_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    total_lectures INT DEFAULT 0,
                    completed_lectures INT DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS read_watch_queue (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    title VARCHAR(255) NOT NULL,
                    type VARCHAR(50),
                    url TEXT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress_charts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    week_start_date DATE,
                    hours_studied DECIMAL(5,2),
                    topics_covered TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # Fitness & Gym Tracker
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    workout_date DATE NOT NULL,
                    split_type VARCHAR(50),
                    exercise_name VARCHAR(255),
                    sets INT,
                    reps INT,
                    weight DECIMAL(7,2),
                    muscle_soreness INT,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS body_progress (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    record_date DATE NOT NULL,
                    weight DECIMAL(5,2),
                    photo_url TEXT,
                    measurements TEXT, -- JSON string
                    goal TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nutrition (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    meal_date DATE NOT NULL,
                    meal_type VARCHAR(50),
                    meal_description TEXT,
                    calories INT,
                    protein_intake DECIMAL(7,2),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shopping_list (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    item_name VARCHAR(255) NOT NULL,
                    quantity VARCHAR(50),
                    is_purchased BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # Basketball & Analysis Lab
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_clips (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    clip_title VARCHAR(255) NOT NULL,
                    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    video_url TEXT,
                    annotations TEXT, -- JSON string
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scouting_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    template_name VARCHAR(255) NOT NULL,
                    opponent_name VARCHAR(255),
                    report_content TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_resources (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    resource_title VARCHAR(255) NOT NULL,
                    platform VARCHAR(100),
                    url TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # Self-Development & Courses
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    course_name VARCHAR(255) NOT NULL,
                    status VARCHAR(50),
                    start_date DATE,
                    completion_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skill_goals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    skill_name VARCHAR(255) NOT NULL,
                    target_date DATE,
                    is_achieved BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # Daily Schedule & Routine
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_schedule (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    schedule_date DATE NOT NULL,
                    morning_routine_completed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_blocking (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    schedule_date DATE NOT NULL,
                    time_slot VARCHAR(50),
                    activity VARCHAR(255),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consistency_score (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    record_date DATE NOT NULL,
                    sleep_score INT,
                    gym_score INT,
                    study_score INT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # Dashboard Home Page
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_tracker (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    record_date DATE NOT NULL,
                    mood_level INT,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sleep_tracker (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    sleep_date DATE NOT NULL,
                    hours_slept DECIMAL(4,2),
                    quality_score INT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    achievement_date DATE NOT NULL,
                    description TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # New table for Pomodoro sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    session_date DATE NOT NULL,
                    duration_minutes INT NOT NULL,
                    is_work_session BOOLEAN NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # New table for Lecture Completion Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lecture_completion_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    subject_id INT,
                    completion_date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            """)

            connection.commit()
            print("All tables checked/created successfully.")

            # Add Omar Elhaq as a default user if not exists
            cursor.execute("SELECT id FROM users WHERE username = 'Omar Elhaq'")
            user_exists = cursor.fetchone()
            if not user_exists:
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                               ("Omar Elhaq", "password123", "omar.elhaq@example.com")) # Use a strong password in production
                connection.commit()
                print("Default user 'Omar Elhaq' added.")

        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            cursor.close()
            connection.close()

# Call database initialization on startup
initialize_database()

# --- Helper to get Omar's user ID (for demonstration) ---
def get_omar_user_id():
    connection = create_db_connection()
    user_id = None
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM users WHERE username = 'Omar Elhaq'")
            user = cursor.fetchone()
            if user:
                user_id = user['id']
        except Error as e:
            print(f"Error fetching user ID: {e}")
        finally:
            cursor.close()
            connection.close()
    return user_id

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main dashboard HTML page."""
    return render_template('index.html')

# --- API Endpoints ---

# Medical Student Hub - Study Plans
@app.route('/api/study_plans', methods=['GET', 'POST'])
def handle_study_plans():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM study_plans WHERE user_id = %s ORDER BY day_of_week, time_slot", (user_id,))
            plans = cursor.fetchall()
            return jsonify(plans)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['day_of_week', 'time_slot', 'topic', 'resource_type']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO study_plans (user_id, day_of_week, time_slot, topic, resource_type, is_completed) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, data['day_of_week'], data['time_slot'], data['topic'], data['resource_type'], data.get('is_completed', False))
            )
            connection.commit()
            return jsonify({"message": "Study plan added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

@app.route('/api/study_plans/<int:plan_id>', methods=['PUT', 'DELETE'])
def manage_study_plan(plan_id):
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'PUT':
        data = request.get_json()
        # Allow updating specific fields, including is_completed
        update_fields = []
        update_values = []
        if 'day_of_week' in data:
            update_fields.append("day_of_week = %s")
            update_values.append(data['day_of_week'])
        if 'time_slot' in data:
            update_fields.append("time_slot = %s")
            update_values.append(data['time_slot'])
        if 'topic' in data:
            update_fields.append("topic = %s")
            update_values.append(data['topic'])
        if 'resource_type' in data:
            update_fields.append("resource_type = %s")
            update_values.append(data['resource_type'])
        if 'is_completed' in data:
            update_fields.append("is_completed = %s")
            update_values.append(data['is_completed'])
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400

        query = f"UPDATE study_plans SET {', '.join(update_fields)} WHERE id=%s AND user_id=%s"
        update_values.extend([plan_id, user_id])

        try:
            cursor.execute(query, tuple(update_values))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({"message": "Study plan not found or not authorized"}), 404
            return jsonify({"message": "Study plan updated successfully"})
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'DELETE':
        try:
            cursor.execute("DELETE FROM study_plans WHERE id=%s AND user_id=%s", (plan_id, user_id))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({"message": "Study plan not found or not authorized"}), 404
            return jsonify({"message": "Study plan deleted successfully"})
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Medical Student Hub - Subjects
@app.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM subjects WHERE user_id = %s", (user_id,))
            subjects = cursor.fetchall()
            return jsonify(subjects)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        if 'subject_name' not in data:
            return jsonify({"error": "Missing subject_name"}), 400
        try:
            cursor.execute(
                "INSERT INTO subjects (user_id, subject_name, description, total_lectures, completed_lectures) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data['subject_name'], data.get('description'), data.get('total_lectures', 0), data.get('completed_lectures', 0))
            )
            connection.commit()
            return jsonify({"message": "Subject added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

@app.route('/api/subjects/<int:subject_id>/complete_lecture', methods=['PUT'])
def complete_lecture(subject_id):
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT completed_lectures, total_lectures, subject_name FROM subjects WHERE id = %s AND user_id = %s", (subject_id, user_id))
        subject = cursor.fetchone()

        if not subject:
            return jsonify({"message": "Subject not found or not authorized"}), 404

        new_completed_lectures = subject['completed_lectures'] + 1
        
        # Update subject's completed lectures
        cursor.execute("UPDATE subjects SET completed_lectures = %s WHERE id = %s AND user_id = %s",
                       (new_completed_lectures, subject_id, user_id))
        
        # Log lecture completion
        cursor.execute("INSERT INTO lecture_completion_log (user_id, subject_id, completion_date) VALUES (%s, %s, %s)",
                       (user_id, subject_id, date.today()))
        
        connection.commit()

        achievement_unlocked = False
        achievement_description = ""

        # Check for achievement (e.g., "Completed 10 lectures in Anatomy")
        if subject['subject_name'] == 'Anatomy' and new_completed_lectures == 10:
            achievement_description = "Completed 10 Anatomy Lectures!"
            cursor.execute("INSERT INTO achievements (user_id, achievement_date, description) VALUES (%s, %s, %s)",
                           (user_id, date.today(), achievement_description))
            connection.commit()
            achievement_unlocked = True

        return jsonify({
            "message": "Lecture marked as complete!",
            "achievement_unlocked": achievement_unlocked,
            "achievement_description": achievement_description
        })
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/subjects/<int:subject_id>/add_lecture', methods=['PUT'])
def add_lecture(subject_id):
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT total_lectures FROM subjects WHERE id = %s AND user_id = %s", (subject_id, user_id))
        subject = cursor.fetchone()

        if not subject:
            return jsonify({"message": "Subject not found or not authorized"}), 404

        new_total_lectures = subject['total_lectures'] + 1
        cursor.execute("UPDATE subjects SET total_lectures = %s WHERE id = %s AND user_id = %s",
                       (new_total_lectures, subject_id, user_id))
        connection.commit()
        return jsonify({"message": "New lecture added to subject!"})
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Medical Student Hub - Read/Watch Queue
@app.route('/api/read_watch_queue', methods=['GET', 'POST'])
def handle_read_watch_queue():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM read_watch_queue WHERE user_id = %s", (user_id,))
            queue_items = cursor.fetchall()
            return jsonify(queue_items)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['title', 'type', 'url']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO read_watch_queue (user_id, title, type, url, is_completed) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data['title'], data['type'], data['url'], data.get('is_completed', False))
            )
            connection.commit()
            return jsonify({"message": "Item added to queue successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Medical Student Hub - Progress Charts (Manual Study Hours)
@app.route('/api/progress_charts', methods=['GET', 'POST'])
def handle_progress_charts():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM progress_charts WHERE user_id = %s ORDER BY week_start_date", (user_id,))
            charts_data = cursor.fetchall()
            # Convert date objects to string for JSON serialization
            for row in charts_data:
                if isinstance(row['week_start_date'], date):
                    row['week_start_date'] = row['week_start_date'].isoformat()
            return jsonify(charts_data)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['week_start_date', 'hours_studied', 'topics_covered']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO progress_charts (user_id, week_start_date, hours_studied, topics_covered) VALUES (%s, %s, %s, %s)",
                (user_id, data['week_start_date'], data['hours_studied'], data['topics_covered'])
            )
            connection.commit()
            return jsonify({"message": "Progress data added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Fitness & Gym Tracker
@app.route('/api/workouts', methods=['GET', 'POST'])
def handle_workouts():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM workouts WHERE user_id = %s ORDER BY workout_date DESC", (user_id,))
            workouts = cursor.fetchall()
            for row in workouts:
                if isinstance(row['workout_date'], date):
                    row['workout_date'] = row['workout_date'].isoformat()
            return jsonify(workouts)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['workout_date', 'split_type', 'exercise_name', 'sets', 'reps', 'weight']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO workouts (user_id, workout_date, split_type, exercise_name, sets, reps, weight, muscle_soreness, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, data['workout_date'], data['split_type'], data['exercise_name'], data['sets'], data['reps'], data['weight'], data.get('muscle_soreness'), data.get('notes'))
            )
            connection.commit()
            return jsonify({"message": "Workout added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Body Progress
@app.route('/api/body_progress', methods=['GET', 'POST'])
def handle_body_progress():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM body_progress WHERE user_id = %s ORDER BY record_date DESC", (user_id,))
            progress_data = cursor.fetchall()
            for row in progress_data:
                if isinstance(row['record_date'], date):
                    row['record_date'] = row['record_date'].isoformat()
                # Parse JSON string back to object
                if row['measurements']:
                    row['measurements'] = json.loads(row['measurements'])
            return jsonify(progress_data)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['record_date', 'weight']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        measurements_json = json.dumps(data.get('measurements')) if 'measurements' in data else None
        
        try:
            cursor.execute(
                "INSERT INTO body_progress (user_id, record_date, weight, photo_url, measurements, goal) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, data['record_date'], data['weight'], data.get('photo_url'), measurements_json, data.get('goal'))
            )
            connection.commit()
            return jsonify({"message": "Body progress added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Nutrition
@app.route('/api/nutrition', methods=['GET', 'POST'])
def handle_nutrition():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM nutrition WHERE user_id = %s ORDER BY meal_date DESC", (user_id,))
            nutrition_data = cursor.fetchall()
            for row in nutrition_data:
                if isinstance(row['meal_date'], date):
                    row['meal_date'] = row['meal_date'].isoformat()
            return jsonify(nutrition_data)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['meal_date', 'meal_type', 'meal_description', 'calories', 'protein_intake']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO nutrition (user_id, meal_date, meal_type, meal_description, calories, protein_intake) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, data['meal_date'], data['meal_type'], data['meal_description'], data['calories'], data['protein_intake'])
            )
            connection.commit()
            return jsonify({"message": "Nutrition entry added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Shopping List
@app.route('/api/shopping_list', methods=['GET', 'POST'])
def handle_shopping_list():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM shopping_list WHERE user_id = %s ORDER BY item_name", (user_id,))
            shopping_items = cursor.fetchall()
            return jsonify(shopping_items)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        if 'item_name' not in data:
            return jsonify({"error": "Missing item_name"}), 400
        try:
            cursor.execute(
                "INSERT INTO shopping_list (user_id, item_name, quantity, is_purchased) VALUES (%s, %s, %s, %s)",
                (user_id, data['item_name'], data.get('quantity'), data.get('is_purchased', False))
            )
            connection.commit()
            return jsonify({"message": "Item added to shopping list successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Basketball & Analysis Lab
@app.route('/api/game_clips', methods=['GET', 'POST'])
def handle_game_clips():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM game_clips WHERE user_id = %s ORDER BY upload_date DESC", (user_id,))
            clips = cursor.fetchall()
            for row in clips:
                if isinstance(row['upload_date'], datetime):
                    row['upload_date'] = row['upload_date'].isoformat()
                if row['annotations']:
                    row['annotations'] = json.loads(row['annotations'])
            return jsonify(clips)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['clip_title', 'video_url']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        annotations_json = json.dumps(data.get('annotations')) if 'annotations' in data else None

        try:
            cursor.execute(
                "INSERT INTO game_clips (user_id, clip_title, video_url, annotations) VALUES (%s, %s, %s, %s)",
                (user_id, data['clip_title'], data['video_url'], annotations_json)
            )
            connection.commit()
            return jsonify({"message": "Game clip added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Scouting Templates
@app.route('/api/scouting_templates', methods=['GET', 'POST'])
def handle_scouting_templates():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM scouting_templates WHERE user_id = %s ORDER BY template_name", (user_id,))
            templates = cursor.fetchall()
            return jsonify(templates)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        if 'template_name' not in data:
            return jsonify({"error": "Missing template_name"}), 400
        try:
            cursor.execute(
                "INSERT INTO scouting_templates (user_id, template_name, opponent_name, report_content) VALUES (%s, %s, %s, %s)",
                (user_id, data['template_name'], data.get('opponent_name'), data.get('report_content'))
            )
            connection.commit()
            return jsonify({"message": "Scouting template added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Learning Resources
@app.route('/api/learning_resources', methods=['GET', 'POST'])
def handle_learning_resources():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM learning_resources WHERE user_id = %s ORDER BY resource_title", (user_id,))
            resources = cursor.fetchall()
            return jsonify(resources)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['resource_title', 'url']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO learning_resources (user_id, resource_title, platform, url) VALUES (%s, %s, %s, %s)",
                (user_id, data['resource_title'], data.get('platform'), data['url'])
            )
            connection.commit()
            return jsonify({"message": "Learning resource added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Self-Development & Courses
@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM courses WHERE user_id = %s ORDER BY course_name", (user_id,))
            courses = cursor.fetchall()
            for row in courses:
                if isinstance(row['start_date'], date):
                    row['start_date'] = row['start_date'].isoformat()
                if isinstance(row['completion_date'], date):
                    row['completion_date'] = row['completion_date'].isoformat()
            return jsonify(courses)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['course_name', 'status']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO courses (user_id, course_name, status, start_date, completion_date) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data['course_name'], data['status'], data.get('start_date'), data.get('completion_date'))
            )
            connection.commit()
            return jsonify({"message": "Course added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Skill Goals
@app.route('/api/skill_goals', methods=['GET', 'POST'])
def handle_skill_goals():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM skill_goals WHERE user_id = %s ORDER BY skill_name", (user_id,))
            goals = cursor.fetchall()
            for row in goals:
                if isinstance(row['target_date'], date):
                    row['target_date'] = row['target_date'].isoformat()
            return jsonify(goals)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['skill_name']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO skill_goals (user_id, skill_name, target_date, is_achieved) VALUES (%s, %s, %s, %s)",
                (user_id, data['skill_name'], data.get('target_date'), data.get('is_achieved', False))
            )
            connection.commit()
            return jsonify({"message": "Skill goal added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Daily Schedule & Routine
@app.route('/api/daily_schedule', methods=['GET', 'POST'])
def handle_daily_schedule():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM daily_schedule WHERE user_id = %s ORDER BY schedule_date DESC", (user_id,))
            schedule = cursor.fetchall()
            for row in schedule:
                if isinstance(row['schedule_date'], date):
                    row['schedule_date'] = row['schedule_date'].isoformat()
            return jsonify(schedule)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        if 'schedule_date' not in data:
            return jsonify({"error": "Missing schedule_date"}), 400
        try:
            cursor.execute(
                "INSERT INTO daily_schedule (user_id, schedule_date, morning_routine_completed) VALUES (%s, %s, %s)",
                (user_id, data['schedule_date'], data.get('morning_routine_completed', False))
            )
            connection.commit()
            return jsonify({"message": "Daily schedule entry added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Time Blocking
@app.route('/api/time_blocking', methods=['GET', 'POST'])
def handle_time_blocking():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM time_blocking WHERE user_id = %s ORDER BY schedule_date, time_slot", (user_id,))
            blocks = cursor.fetchall()
            for row in blocks:
                if isinstance(row['schedule_date'], date):
                    row['schedule_date'] = row['schedule_date'].isoformat()
            return jsonify(blocks)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['schedule_date', 'time_slot', 'activity']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO time_blocking (user_id, schedule_date, time_slot, activity) VALUES (%s, %s, %s, %s)",
                (user_id, data['schedule_date'], data['time_slot'], data['activity'])
            )
            connection.commit()
            return jsonify({"message": "Time block added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Consistency Score
@app.route('/api/consistency_score', methods=['GET', 'POST'])
def handle_consistency_score():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM consistency_score WHERE user_id = %s ORDER BY record_date DESC", (user_id,))
            scores = cursor.fetchall()
            for row in scores:
                if isinstance(row['record_date'], date):
                    row['record_date'] = row['record_date'].isoformat()
            return jsonify(scores)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['record_date', 'sleep_score', 'gym_score', 'study_score']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO consistency_score (user_id, record_date, sleep_score, gym_score, study_score) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data['record_date'], data['sleep_score'], data['gym_score'], data['study_score'])
            )
            connection.commit()
            return jsonify({"message": "Consistency score added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# Dashboard Home Page - Mood Tracker
@app.route('/api/mood_tracker', methods=['GET', 'POST'])
def handle_mood_tracker():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM mood_tracker WHERE user_id = %s ORDER BY record_date DESC", (user_id,))
            moods = cursor.fetchall()
            for row in moods:
                if isinstance(row['record_date'], date):
                    row['record_date'] = row['record_date'].isoformat()
            return jsonify(moods)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['record_date', 'mood_level']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO mood_tracker (user_id, record_date, mood_level, notes) VALUES (%s, %s, %s, %s)",
                (user_id, data['record_date'], data['mood_level'], data.get('notes'))
            )
            connection.commit()
            return jsonify({"message": "Mood entry added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

@app.route('/api/sleep_tracker', methods=['GET', 'POST'])
def handle_sleep_tracker():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM sleep_tracker WHERE user_id = %s ORDER BY sleep_date DESC", (user_id,))
            sleep_data = cursor.fetchall()
            for row in sleep_data:
                if isinstance(row['sleep_date'], date):
                    row['sleep_date'] = row['sleep_date'].isoformat()
            return jsonify(sleep_data)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['sleep_date', 'hours_slept', 'quality_score']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO sleep_tracker (user_id, sleep_date, hours_slept, quality_score) VALUES (%s, %s, %s, %s)",
                (user_id, data['sleep_date'], data['hours_slept'], data['quality_score'])
            )
            connection.commit()
            return jsonify({"message": "Sleep entry added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

@app.route('/api/achievements', methods=['GET', 'POST'])
def handle_achievements():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM achievements WHERE user_id = %s ORDER BY achievement_date DESC", (user_id,))
            achievements = cursor.fetchall()
            for row in achievements:
                if isinstance(row['achievement_date'], date):
                    row['achievement_date'] = row['achievement_date'].isoformat()
            return jsonify(achievements)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ['achievement_date', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            cursor.execute(
                "INSERT INTO achievements (user_id, achievement_date, description) VALUES (%s, %s, %s)",
                (user_id, data['achievement_date'], data['description'])
            )
            connection.commit()
            return jsonify({"message": "Achievement added successfully", "id": cursor.lastrowid}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

# New API endpoint for Pomodoro sessions
@app.route('/api/pomodoro_sessions', methods=['POST'])
def add_pomodoro_session():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor()

    data = request.get_json()
    required_fields = ['session_date', 'duration_minutes', 'is_work_session']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        cursor.execute(
            "INSERT INTO pomodoro_sessions (user_id, session_date, duration_minutes, is_work_session) VALUES (%s, %s, %s, %s)",
            (user_id, data['session_date'], data['duration_minutes'], data['is_work_session'])
        )
        connection.commit()
        return jsonify({"message": "Pomodoro session recorded successfully", "id": cursor.lastrowid}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# New API endpoint for aggregated dashboard summary data for charts
@app.route('/api/dashboard_summary_data', methods=['GET'])
def dashboard_summary_data():
    user_id = get_omar_user_id()
    if not user_id: return jsonify({"error": "User not found"}), 404

    connection = create_db_connection()
    if not connection: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    try:
        # Define the date range (e.g., last 8 weeks)
        today = date.today()
        # Find the start of the current week (Monday)
        current_week_start = today - timedelta(days=today.weekday())
        
        # Generate labels for the last 8 weeks
        labels = []
        week_starts = []
        for i in range(8): # For last 8 weeks
            week_start = current_week_start - timedelta(weeks=7 - i)
            labels.append(week_start.strftime('%Y-%m-%d'))
            week_starts.append(week_start)

        pomodoro_hours = [0] * 8
        lectures_completed_weekly = [0] * 8
        manual_study_hours = [0] * 8

        # Fetch Pomodoro data
        cursor.execute("""
            SELECT session_date, duration_minutes FROM pomodoro_sessions
            WHERE user_id = %s AND is_work_session = TRUE AND session_date >= %s
            ORDER BY session_date
        """, (user_id, week_starts[0]))
        pomodoro_data = cursor.fetchall()

        for session in pomodoro_data:
            session_date = session['session_date']
            for i, ws in enumerate(week_starts):
                if ws <= session_date < ws + timedelta(weeks=1):
                    pomodoro_hours[i] += session['duration_minutes'] / 60.0 # Convert minutes to hours
                    break
        
        # Fetch Lecture Completion Log data
        cursor.execute("""
            SELECT completion_date FROM lecture_completion_log
            WHERE user_id = %s AND completion_date >= %s
            ORDER BY completion_date
        """, (user_id, week_starts[0]))
        lecture_log_data = cursor.fetchall()

        for log_entry in lecture_log_data:
            completion_date = log_entry['completion_date']
            for i, ws in enumerate(week_starts):
                if ws <= completion_date < ws + timedelta(weeks=1):
                    lectures_completed_weekly[i] += 1
                    break

        # Fetch Manual Study Hours data (from progress_charts)
        cursor.execute("""
            SELECT week_start_date, hours_studied FROM progress_charts
            WHERE user_id = %s AND week_start_date >= %s
            ORDER BY week_start_date
        """, (user_id, week_starts[0]))
        manual_study_data = cursor.fetchall()

        for study_entry in manual_study_data:
            study_week_start = study_entry['week_start_date']
            for i, ws in enumerate(week_starts):
                if ws == study_week_start: # Match exact week start date
                    manual_study_hours[i] = study_entry['hours_studied']
                    break

        return jsonify({
            "dates": labels,
            "pomodoro_hours": pomodoro_hours,
            "lectures_completed": lectures_completed_weekly,
            "manual_study_hours": manual_study_hours
        })

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# This is for Vercel deployment. Vercel expects a 'wsgi.py' or 'app.py' at the root
# and will automatically detect the 'app' variable.
# The local `app.run` is removed as Vercel handles the server.
