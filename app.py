import streamlit as st
from database import init_db, query, execute, scalar, log_action
from auth import login_screen, require_login, logout_button, hash_password
from ui import sidebar, page_header, metric
from datetime import date, datetime
import pandas as pd

st.set_page_config(page_title="Zaara World | Company Management", page_icon="🌐", layout="wide")
init_db()
if not st.session_state.get("user"):
    login_screen()
    st.stop()
user=st.session_state["user"]
sidebar(user)
logout_button()
page=st.session_state.get("page","Dashboard")
page_header(page, f"Welcome, {user['full_name']}")

def df_table(sql, params=()):
    rows=query(sql, params)
    return pd.DataFrame([dict(r) for r in rows])

def add_form(title, fields, table, columns=None):
    with st.expander(f"➕ Add {title}", expanded=False):
        with st.form(f"add_{table}"):
            vals={}
            for key,label,kind in fields:
                if kind=="date": vals[key]=st.date_input(label, value=date.today()).isoformat()
                elif kind=="number": vals[key]=st.number_input(label, min_value=0.0, step=100.0)
                elif kind=="long": vals[key]=st.text_area(label)
                else: vals[key]=st.text_input(label)
            ok=st.form_submit_button(f"Save {title}", type="primary")
        if ok:
            cols=columns or [x[0] for x in fields]
            execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", tuple(vals[c] for c in cols))
            log_action(user["id"], f"Created {title}")
            st.success(f"{title} added.")
            st.rerun()

def show_table(title, sql, params=()):
    st.subheader(title)
    data=df_table(sql,params)
    if data.empty: st.info("No records yet. Use the Add section to create your first record.")
    else: st.dataframe(data, use_container_width=True, hide_index=True)

if page=="Dashboard":
    c1,c2,c3,c4=st.columns(4)
    metric(c1,"Employees",scalar("SELECT COUNT(*) FROM employees"))
    metric(c2,"Departments",scalar("SELECT COUNT(*) FROM departments"))
    metric(c3,"Active Projects",scalar("SELECT COUNT(*) FROM projects WHERE status='In Progress'"))
    metric(c4,"Open Tasks",scalar("SELECT COUNT(*) FROM tasks WHERE status!='Completed'"))
    c5,c6,c7=st.columns(3)
    metric(c5,"Pending Leave Requests",scalar("SELECT COUNT(*) FROM leaves WHERE status='Pending'"))
    metric(c6,"Clients",scalar("SELECT COUNT(*) FROM clients"))
    metric(c7,"Unpaid Invoices",scalar("SELECT COUNT(*) FROM invoices WHERE status!='Paid'"))
    left,right=st.columns(2)
    with left:
        st.subheader("Recent tasks")
        show_table(" ", "SELECT title, assigned_to, due_date, status, priority FROM tasks ORDER BY id DESC LIMIT 8")
    with right:
        st.subheader("Recent activity")
        show_table(" ", "SELECT action, created_at FROM activity_logs ORDER BY id DESC LIMIT 8")
    st.caption("Dashboard figures update from the records entered in each module.")

elif page=="Employees":
    add_form("Employee",[("employee_code","Employee ID","text"),("full_name","Full name","text"),("email","Email","text"),("phone","Phone","text"),("department","Department","text"),("designation","Designation","text"),("joining_date","Joining date","date"),("employment_status","Status","text")],"employees")
    show_table("Employee directory","SELECT * FROM employees ORDER BY id DESC")
elif page=="Departments":
    add_form("Department",[("name","Department name","text"),("manager","Department manager","text"),("description","Description","long")],"departments")
    show_table("Departments","SELECT * FROM departments ORDER BY name")
elif page=="Attendance":
    add_form("Attendance record",[("employee_name","Employee name / ID","text"),("attendance_date","Date","date"),("check_in","Check-in time (e.g. 09:00)","text"),("check_out","Check-out time (e.g. 18:00)","text"),("status","Status (Present / Absent / Half Day / Late)","text"),("notes","Notes","long")],"attendance")
    show_table("Attendance records","SELECT * FROM attendance ORDER BY attendance_date DESC")
elif page=="Leave Management":
    add_form("Leave request",[("employee_name","Employee name / ID","text"),("leave_type","Leave type","text"),("start_date","Start date","date"),("end_date","End date","date"),("reason","Reason","long")],"leaves")
    st.subheader("Review requests")
    data=df_table("SELECT * FROM leaves ORDER BY id DESC")
    if not data.empty:
        st.dataframe(data,use_container_width=True,hide_index=True)
        pending=query("SELECT id, employee_name, leave_type FROM leaves WHERE status='Pending'")
        if pending:
            opts={f"#{r['id']} — {r['employee_name']} ({r['leave_type']})":r['id'] for r in pending}
            with st.form("leave_review"):
                choice=st.selectbox("Request",list(opts))
                decision=st.selectbox("Decision",["Approved","Rejected"])
                if st.form_submit_button("Update decision"):
                    execute("UPDATE leaves SET status=? WHERE id=?",(decision,opts[choice]))
                    log_action(user["id"],f"{decision} leave request #{opts[choice]}")
                    st.rerun()
    else: st.info("No leave requests yet.")
elif page=="Projects":
    add_form("Project",[("name","Project name","text"),("client","Client","text"),("manager","Project manager","text"),("start_date","Start date","date"),("due_date","Due date","date"),("status","Status (Not Started / In Progress / On Hold / Completed)","text"),("progress","Progress description","long")],"projects")
    show_table("Projects","SELECT * FROM projects ORDER BY id DESC")
elif page=="Tasks":
    add_form("Task",[("title","Task title","text"),("project","Project","text"),("assigned_to","Assigned to","text"),("due_date","Due date","date"),("priority","Priority (Low / Medium / High)","text"),("status","Status (To Do / In Progress / Completed)","text"),("description","Description","long")],"tasks")
    show_table("Tasks","SELECT * FROM tasks ORDER BY id DESC")
elif page=="Clients":
    add_form("Client",[("company_name","Company / client name","text"),("contact_person","Contact person","text"),("email","Email","text"),("phone","Phone","text"),("address","Address","long")],"clients")
    show_table("Clients","SELECT * FROM clients ORDER BY id DESC")
elif page=="Payroll":
    add_form("Payroll record",[("employee_name","Employee name / ID","text"),("pay_month","Pay month (e.g. Nov 2026)","text"),("basic_salary","Basic salary","number"),("allowances","Allowances","number"),("deductions","Deductions","number"),("payment_status","Payment status","text")],"payroll")
    data=df_table("SELECT *, (basic_salary + allowances - deductions) AS net_salary FROM payroll ORDER BY id DESC")
    st.subheader("Payroll register")
    if data.empty: st.info("No payroll records yet.")
    else: st.dataframe(data,use_container_width=True,hide_index=True)
    st.caption("Configure statutory deductions and verify payroll calculations with your accountant before production use.")
elif page=="Finance":
    add_form("Invoice",[("invoice_number","Invoice number","text"),("client","Client","text"),("issue_date","Issue date","date"),("due_date","Due date","date"),("amount","Amount (₹)","number"),("status","Status (Unpaid / Paid / Overdue)","text")],"invoices")
    add_form("Expense",[("category","Expense category","text"),("description","Description","long"),("expense_date","Expense date","date"),("amount","Amount (₹)","number"),("paid_to","Paid to","text")],"expenses")
    show_table("Invoices","SELECT * FROM invoices ORDER BY id DESC")
    show_table("Expenses","SELECT * FROM expenses ORDER BY id DESC")
elif page=="Meetings":
    add_form("Meeting",[("title","Meeting title","text"),("meeting_date","Meeting date","date"),("meeting_time","Meeting time","text"),("participants","Participants","text"),("location","Location / meeting link","text"),("agenda","Agenda","long")],"meetings")
    show_table("Meetings","SELECT * FROM meetings ORDER BY meeting_date DESC")
elif page=="Reports":
    st.subheader("Company reports")
    tabs=st.tabs(["Headcount","Attendance","Projects","Finance"])
    with tabs[0]: show_table("Employees by department","SELECT department, COUNT(*) AS employee_count FROM employees GROUP BY department")
    with tabs[1]: show_table("Attendance by status","SELECT status, COUNT(*) AS records FROM attendance GROUP BY status")
    with tabs[2]: show_table("Projects by status","SELECT status, COUNT(*) AS projects FROM projects GROUP BY status")
    with tabs[3]:
        income=scalar("SELECT COALESCE(SUM(amount),0) FROM invoices WHERE status='Paid'")
        expenses=scalar("SELECT COALESCE(SUM(amount),0) FROM expenses")
        a,b,c=st.columns(3); metric(a,"Paid invoices",f"₹{income:,.2f}"); metric(b,"Recorded expenses",f"₹{expenses:,.2f}"); metric(c,"Difference",f"₹{income-expenses:,.2f}")
        show_table("Invoice register","SELECT * FROM invoices")
elif page=="Notifications":
    show_table("Recent activity / notifications","SELECT action, created_at FROM activity_logs ORDER BY id DESC")
elif page=="User Management":
    if user["role"] not in ("Super Admin","Admin"):
        st.error("Only an administrator can manage user accounts.")
    else:
        with st.expander("Create user account"):
            with st.form("new_user"):
                name=st.text_input("Full name"); email=st.text_input("Email"); password=st.text_input("Temporary password",type="password")
                role=st.selectbox("Role",["Admin","HR Manager","Manager","Team Leader","Employee","Accountant"])
                if st.form_submit_button("Create account"):
                    if name and email and len(password)>=8:
                        execute("INSERT INTO users(full_name,email,password_hash,role) VALUES(?,?,?,?)",(name,email.lower(),hash_password(password),role))
                        st.success("User created.")
                    else: st.error("Enter name, email and a password of at least 8 characters.")
        show_table("User accounts","SELECT id,full_name,email,role,created_at FROM users")
elif page=="Settings":
    st.subheader("Company settings")
    st.write("Company name: **Zaara World**")
    st.write("Application data is stored in a local SQLite database (`zaara_world.db`).")
    st.warning("Before public deployment, configure secrets, HTTPS, database backups, access policies and persistent storage. Streamlit Community Cloud local files may not be durable.")
    st.subheader("Change your password")
    with st.form("change_password"):
        old=st.text_input("Current password",type="password"); new=st.text_input("New password (minimum 8 characters)",type="password")
        if st.form_submit_button("Update password"):
            from auth import verify_password
            row=query("SELECT password_hash FROM users WHERE id=?",(user["id"],))
            if row and verify_password(old,row[0]["password_hash"]) and len(new)>=8:
                execute("UPDATE users SET password_hash=? WHERE id=?",(hash_password(new),user["id"]))
                st.success("Password updated. Please log in again.")
            else: st.error("Current password is incorrect or new password is too short.")

st.divider()
st.caption("Zaara World • Company Management System • Internal business use")
