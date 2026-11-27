import sqlite3, os
from datetime import datetime
DB_PATH=os.environ.get("ZAARA_DB_PATH","zaara_world.db")
def connect():
    con=sqlite3.connect(DB_PATH,check_same_thread=False)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con
def init_db():
    schema="""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'Employee',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY AUTOINCREMENT,employee_code TEXT,full_name TEXT NOT NULL,email TEXT,phone TEXT,department TEXT,designation TEXT,joining_date TEXT,employment_status TEXT DEFAULT 'Active');
    CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,manager TEXT,description TEXT);
    CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT,employee_name TEXT,attendance_date TEXT,check_in TEXT,check_out TEXT,status TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS leaves(id INTEGER PRIMARY KEY AUTOINCREMENT,employee_name TEXT,leave_type TEXT,start_date TEXT,end_date TEXT,reason TEXT,status TEXT DEFAULT 'Pending');
    CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,client TEXT,manager TEXT,start_date TEXT,due_date TEXT,status TEXT,progress TEXT);
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,project TEXT,assigned_to TEXT,due_date TEXT,priority TEXT,status TEXT,description TEXT);
    CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY AUTOINCREMENT,company_name TEXT,contact_person TEXT,email TEXT,phone TEXT,address TEXT);
    CREATE TABLE IF NOT EXISTS payroll(id INTEGER PRIMARY KEY AUTOINCREMENT,employee_name TEXT,pay_month TEXT,basic_salary REAL DEFAULT 0,allowances REAL DEFAULT 0,deductions REAL DEFAULT 0,payment_status TEXT);
    CREATE TABLE IF NOT EXISTS invoices(id INTEGER PRIMARY KEY AUTOINCREMENT,invoice_number TEXT,client TEXT,issue_date TEXT,due_date TEXT,amount REAL DEFAULT 0,status TEXT);
    CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT,description TEXT,expense_date TEXT,amount REAL DEFAULT 0,paid_to TEXT);
    CREATE TABLE IF NOT EXISTS meetings(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,meeting_date TEXT,meeting_time TEXT,participants TEXT,location TEXT,agenda TEXT);
    CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,action TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    """
    with connect() as con:
        con.executescript(schema)
        if con.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
            from auth import hash_password
            import os
            email=os.environ.get("ZAARA_ADMIN_EMAIL","admin@zaaraworld.com")
            password=os.environ.get("ZAARA_ADMIN_PASSWORD","ChangeMe123!")
            con.execute("INSERT INTO users(full_name,email,password_hash,role) VALUES(?,?,?,'Super Admin')",("Zaara World Admin",email,hash_password(password)))
def query(sql,params=()):
    with connect() as con: return con.execute(sql,params).fetchall()
def execute(sql,params=()):
    with connect() as con:
        cur=con.execute(sql,params); con.commit(); return cur.lastrowid
def scalar(sql,params=()):
    row=query(sql,params)
    return row[0][0] if row else 0
def log_action(uid,action):
    execute("INSERT INTO activity_logs(user_id,action) VALUES(?,?)",(uid,action))
