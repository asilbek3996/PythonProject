from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")

# DATABASE_URL = "postgresql://postgres:Asilxan1968.@db.gzmrwexzjcgniadmvzfz.supabase.co:5432/postgres"
DATABASE_URL = "postgresql://postgres.gzmrwexzjcgniadmvzfz:Asilxan1968.@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"


def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Eski jadvallarni yangilash uchun tozalab boshtatan yaratamiz
        cursor.execute("DROP TABLE IF EXISTS students CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS groups CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS courses CASCADE;")

        cursor.execute("""
            CREATE TABLE students (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                birth_date TEXT,
                address TEXT NOT NULL,
                group_name TEXT,
                phone TEXT NOT NULL,
                home_phone TEXT,
                graduation TEXT,
                performance TEXT,
                status TEXT DEFAULT 'active'
            );
        """)

        cursor.execute("""
            CREATE TABLE groups (
                id SERIAL PRIMARY KEY,
                group_name TEXT NOT NULL,
                course_name TEXT NOT NULL,
                teacher_name TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE courses (
                id SERIAL PRIMARY KEY,
                course_name TEXT NOT NULL,
                price TEXT NOT NULL,
                duration TEXT NOT NULL
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Supabase bazasi muvaffaqiyatli yangilandi va jadvallar yaratildi!")
    except Exception as e:
        print("Bazaga ulanishda xatolik:", e)


init_db()


class Student(BaseModel):
    full_name: str
    birth_date: str = ""
    address: str
    group_name: str = ""
    phone: str
    home_phone: str = ""
    graduation: str = ""
    performance: str = ""
    status: str = "active"


class Group(BaseModel):
    group_name: str
    course_name: str
    teacher_name: str


class Course(BaseModel):
    course_name: str
    price: str
    duration: str


@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "index.html topilmadi!"


@app.get("/api/students")
def get_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.post("/api/students")
def add_student(student: Student):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (full_name, birth_date, address, group_name, phone, home_phone, graduation, performance, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            student.full_name, student.birth_date, student.address, student.group_name,
            student.phone, student.home_phone, student.graduation, student.performance, student.status
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print("O'quvchi qo'shishda xatolik:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "deleted"}


@app.get("/api/groups")
def get_groups():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.post("/api/groups")
def add_group(group: Group):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO groups (group_name, course_name, teacher_name) VALUES (%s, %s, %s)",
        (group.group_name, group.course_name, group.teacher_name)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success"}


@app.delete("/api/groups/{group_id}")
def delete_group(group_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM groups WHERE id = %s", (group_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "deleted"}


@app.get("/api/courses")
def get_courses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.post("/api/courses")
def add_course(course: Course):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (course_name, price, duration) VALUES (%s, %s, %s)",
        (course.course_name, course.price, course.duration)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success"}


@app.delete("/api/courses/{course_id}")
def delete_course(course_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "deleted"}