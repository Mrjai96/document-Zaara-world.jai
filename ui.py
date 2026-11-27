import streamlit as st
def sidebar(user):
    st.sidebar.markdown("# 🌐 Zaara World")
    st.sidebar.caption("Company Management System")
    st.sidebar.markdown(f"**{user['full_name']}**")
    st.sidebar.caption(user["role"])
    pages=["Dashboard","Employees","Departments","Attendance","Leave Management","Projects","Tasks","Clients","Payroll","Finance","Meetings","Reports","Notifications","User Management","Settings"]
    for p in pages:
        if st.sidebar.button(p,use_container_width=True,type="primary" if st.session_state.get("page","Dashboard")==p else "secondary",key="nav_"+p):
            st.session_state["page"]=p; st.rerun()
def page_header(title,subtitle=""):
    st.title(title)
    if subtitle: st.caption(subtitle)
def metric(col,label,value):
    with col: st.metric(label,value)
