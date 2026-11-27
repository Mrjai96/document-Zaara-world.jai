import streamlit as st, hashlib, hmac, os
from database import query
def hash_password(password):
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,260000)
    return salt.hex()+":"+digest.hex()
def verify_password(password,stored):
    try:
        salt_hex,digest_hex=stored.split(":")
        test=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),260000)
        return hmac.compare_digest(test.hex(),digest_hex)
    except Exception: return False
def login_screen():
    st.markdown("<h1 style='text-align:center;color:#8b5cf6'>🌐 Zaara World</h1><p style='text-align:center'>Company Management Portal</p>",unsafe_allow_html=True)
    _,col,_=st.columns([1,1.2,1])
    with col:
        with st.container(border=True):
            st.subheader("Sign in")
            with st.form("login"):
                email=st.text_input("Email",placeholder="admin@zaaraworld.com")
                password=st.text_input("Password",type="password")
                submitted=st.form_submit_button("Sign in",type="primary",use_container_width=True)
            if submitted:
                rows=query("SELECT * FROM users WHERE email=?",(email.lower().strip(),))
                if rows and verify_password(password,rows[0]["password_hash"]):
                    st.session_state["user"]=dict(rows[0]); st.rerun()
                else: st.error("Invalid email or password.")
        st.caption("Default first-run credentials are documented in README.md. Change them before deployment.")
def require_login():
    if not st.session_state.get("user"): st.stop()
def logout_button():
    with st.sidebar:
        if st.button("Log out",use_container_width=True):
            st.session_state.pop("user",None); st.rerun()
