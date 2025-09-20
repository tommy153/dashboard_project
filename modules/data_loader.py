import streamlit as st
import numpy as np
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json

@st.cache_data(ttl=300)
def load_google_sheets_data(worksheet:str, week:bool):
    """Google Sheets에서 데이터 로드"""
    
    # Streamlit secrets에서 인증 정보 가져오기
    if "gcp_service_account" in st.secrets:
        credentials_info = dict(st.secrets["gcp_service_account"])
    else:
        # 로컬에서 실행 시 - pj_appscript.json 파일 사용
        with open('./pj_appscript.json', 'r') as f:
            credentials_info = json.load(f)

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(creds)

    # 스프레드시트 열기
    spreadsheet = client.open("🔥🔥🔥 경험그룹_KPI (수업 기준!!!!!) 🔥🔥🔥")
    worksheet = spreadsheet.worksheet(worksheet)

    # 데이터 가져오기
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # 퍼센트 문자열 → float
    for i in df.columns[3:]:
        df[f'{i}'] = df[f'{i}'].str.replace('%', '').astype(float)

    # 날짜 처리
    df['날짜'] = pd.to_datetime(df['시작일'])
    df['시작일'] = pd.to_datetime(df['시작일']).dt.strftime('%m-%d')
    df['종료일'] = pd.to_datetime(df['종료일']).dt.strftime('%m-%d')
    if week:
        # ISO 주차/연도 (월요일 시작, 연말 자동 조정)
        iso_calendar = df['날짜'].dt.isocalendar()
        df['연도'] = iso_calendar.year
        df['주차'] = iso_calendar.week

        # 패널 컬럼
        panel_cos = list(df.columns[3:-3])

        # 최종 컬럼 선택
        df = df[['연도', '날짜', '주차', '시작일', '종료일', '신규 활성 수업 수'] + panel_cos]

        # 오늘 이전 데이터만 사용
        today = datetime.now()
        df = df[df['날짜'] < today]
    else:
        # 월별 정보 추출
        df['연도'] = df['날짜'].dt.year
        df['월'] = df['날짜'].dt.month
        # 오늘 이전 데이터만 사용
        today = datetime.now()
        df = df[df['날짜'] < today]

        # 패널 컬럼
        panel_cos = list(df.columns[3:-3])

    st.success(f"✅ Google Sheets 데이터 로드 성공! ({len(df)}행)")

    return df, panel_cos