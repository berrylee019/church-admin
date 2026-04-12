import streamlit as st
import pandas as pd
from datetime import datetime


# 1. 가상의 사용자 데이터베이스 (아이디: [비밀번호, 직분])
USER_DB = {
    "admin": ["0191", "관리자"],
    "staff": ["0191", "교직원"],
    "leader": ["0191", "구역장"]
}

def login_sidebar():
    st.sidebar.title("🔐 직분자 로그인")
    
    # 세션 상태 초기화
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    if not st.session_state.logged_in:
        input_id = st.sidebar.text_input("아이디")
        input_pw = st.sidebar.text_input("비밀번호", type="password")
        
        if st.sidebar.button("로그인"):
            if input_id in USER_DB and USER_DB[input_id][0] == input_pw:
                st.session_state.logged_in = True
                st.session_state.user_role = USER_DB[input_id][1]
                st.session_state.user_id = input_id
                st.sidebar.success(f"{st.session_state.user_role}님 환영합니다!")
                st.rerun() # 화면 즉시 갱신
            else:
                st.sidebar.error("아이디 또는 비밀번호가 틀렸습니다.")
        return False
    else:
        st.sidebar.write(f"✅ **{st.session_state.user_id}** ({st.session_state.user_role}) 접속 중")
        if st.sidebar.button("로그아웃"):
            st.session_state.logged_in = False
            st.rerun()
        return True

# --- 메인 로직 시작 ---
is_authenticated = login_sidebar()

if is_authenticated:
    role = st.session_state.user_role
    
    # 권한별 메뉴 구성
    menu_options = ["공지사항"] # 공통 메뉴
    
    if role == "관리자":
        menu_options += ["교적부 관리", "재정 관리", "출석 통계"]
    elif role == "교직원":
        menu_options += ["교적부 관리", "출석 체크"]
    elif role == "구역장":
        menu_options += ["출석 체크"]

    choice = st.sidebar.radio("행정 메뉴", menu_options)
    
    st.title(f"⛪ {choice}")
    st.write(f"{role} 권한으로 접속하셨습니다.")
    
    # 여기에 선택된 메뉴별 기능(if choice == "...") 코드를 넣으시면 됩니다.

else:
    st.title("⛪ 교회 행정 시스템")
    st.warning("왼쪽 사이드바에서 로그인 후 이용해 주세요.")

# 페이지 설정
st.set_page_config(page_title="Church Admin System", layout="wide")

# 1. 가상의 데이터 (추후 DB 또는 Google Sheets 연동)
if 'members' not in st.session_state:
    st.session_state.members = pd.DataFrame([
        {"성명": "김철수", "직분": "집사", "연락처": "010-1234-5678", "교구": "1교구"},
        {"성명": "이영희", "직분": "권사", "연락처": "010-9876-5432", "교구": "2교구"}
    ])

st.title("⛪ 스마트 교회 행정 관리 시스템")

# --- 사이드바 메뉴 ---
menu = st.sidebar.radio("메뉴 선택", ["교적부 관리", "재정/헌금 관리", "출석 체크", "공지사항"])

# --- 모듈 1: 교적부 관리 ---
if menu == "교적부 관리":
    st.header("👥 성도 명부 및 검색")
    search_name = st.text_input("이름으로 검색")
    
    if search_name:
        filtered_df = st.session_state.members[st.session_state.members['성명'].str.contains(search_name)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(st.session_state.members, use_container_width=True)
    
    with st.expander("신규 성도 등록"):
        with st.form("new_member_form"):
            name = st.text_input("성명")
            position = st.selectbox("직분", ["성도", "집사", "권사", "장로", "목회자"])
            phone = st.text_input("연락처")
            district = st.text_input("교구/구역")
            if st.form_submit_button("등록하기"):
                st.success(f"{name} {position}님 정보를 등록했습니다.")

# --- 모듈 2: 재정/헌금 관리 ---
elif menu == "재정/헌금 관리":
    st.header("💰 재정 및 헌금 통계")
    col1, col2, col3 = st.columns(3)
    col1.metric("이번 주 십일조", "₩1,250,000", "+5%")
    col2.metric("감사헌금", "₩450,000", "-2%")
    col3.metric("선교헌금", "₩300,000", "0%")
    
    st.subheader("📊 월간 재정 흐름")
    chart_data = pd.DataFrame({
        '월': ['1월', '2월', '3월', '4월'],
        '수입': [500, 600, 450, 700],
        '지출': [400, 450, 420, 500]
    })
    st.line_chart(chart_data.set_index('월'))

# --- 모듈 3: 출석 체크 ---
elif menu == "출석 체크":
    st.header("📍 예배 출석 체크")
    date = st.date_input("예배 날짜", datetime.now())
    st.write(f"**{date}** 주일예배 출석 명단")
    
    for i, row in st.session_state.members.iterrows():
        st.checkbox(f"{row['성명']} ({row['직분']})", key=f"attendance_{i}")
        
    if st.button("출석 저장"):
        st.info("출석 데이터가 저장되었습니다.")
