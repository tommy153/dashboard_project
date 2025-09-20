# 표준 라이브러리
import streamlit as st
import json
from datetime import datetime

# 로컬 모듈
from modules.data_loader import load_google_sheets_data
from modules.preprocessing import cleansing_df_month
from modules.metric import cal_rate, cal_count
from modules.plotting import viz_rate_month, style_comparison_table

# Google Sheets 연동 함수
df, panel_cos = load_google_sheets_data(worksheet="대시보드용_월별타겟신규수업",week=False)

with open("./true_range_month.json", "r", encoding="utf-8") as f:
    true_range = json.load(f)
    
# 페이지 설정
st.set_page_config(
    page_title="월별 이탈률 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

with st.sidebar:
    st.subheader("메뉴")

    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        
st.title("📊 월별 타겟 신규수업 이탈률 분석")

# 연도 선택 radio 버튼
available_years = sorted(df['연도'].unique())
current_year = datetime.now().year
previous_years = [year for year in available_years if year < current_year]

st.subheader("🎯 비교분석할 연도 선택")
col1, col2 = st.columns(2)

with col1:
    year1 = st.radio("지난년도", previous_years, key="year1")
with col2:
    st.write("**이번년도**")
    year2 = current_year
    st.write(f"{year2}년 (고정)")

st.subheader("🎯 분석할 구간 선택")
selected_panel = st.selectbox(
    "분석하고 싶은 구간을 선택하세요:",
    options=panel_cos,
    index=0,
    help="하나의 구간을 선택할 수 있습니다"
)

# 선택된 연도로 데이터 필터링
df_year1, df_year2 = cleansing_df_month(df, year1, year2)
df_diff_rate = cal_rate(df_year1, df_year2, selected_panel, year1, year2)
df_diff_count = cal_count(df_year1, df_year2, year1, year2)

# 양수/음수 나누기
pos = df_diff_rate[df_diff_rate["diff_pp"] >= 0]
neg = df_diff_rate[df_diff_rate["diff_pp"] < 0]

 # 시각화 생성
st.subheader(f"📈 {selected_panel} 월별 이탈률 분석")
fig = viz_rate_month(df_year1, df_year2, selected_panel, pos, neg, df_diff_count, df_diff_rate, year1, year2, true_range)
st.plotly_chart(fig)

# 테이블 (지난연도 vs 이번연도 비교)
st.subheader(f"📊 데이터 테이블 ({year1} vs {year2} 비교)")
df_year1_reset = df_year1.reset_index(drop=True)
df_year2_reset = df_year2.reset_index(drop=True)
df_diff_rate_reset = df_diff_rate.reset_index(drop=True)

styled_df = style_comparison_table(df_year1_reset, df_year2_reset, df_diff_rate_reset, year1, year2, selected_panel, week=False)
st.dataframe(styled_df)