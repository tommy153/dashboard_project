import streamlit as st

def login():
    # secrets.toml에서 가져오기
    correct_username = st.secrets["credentials"]["username"]
    correct_password = st.secrets["credentials"]["password"]

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.subheader("로그인")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if username == correct_username and password == correct_password:
                st.session_state.authenticated = True
                st.success("로그인 성공")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")
    return st.session_state.authenticated

def logout():
    if st.button("로그아웃"):
        st.session_state.authenticated = False
        st.rerun()
