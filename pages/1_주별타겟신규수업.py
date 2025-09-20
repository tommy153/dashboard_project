import streamlit as st
from datetime import datetime
import json

from modules.data_loader import load_google_sheets_data
from modules.preprocessing import cleansing_df_week
from modules.metric import cal_rate, cal_count
from modules.plotting import viz_rate_week, style_comparison_table
from modules.genai import full_data_report

# Google Sheets 연동 함수
if "data_week_target" not in st.session_state:
    df, panel_cos = load_google_sheets_data(
        worksheet="대시보드용_주별타겟신규수업", week=True
    )
    st.session_state["data_week_target"] = (df, panel_cos)
else:
    df, panel_cos = st.session_state["data_week_target"]

with open("./true_range.json", "r", encoding="utf-8") as f:
    true_range = json.load(f)

# 페이지 설정
st.set_page_config(
    page_title="주간 이탈률 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

with st.sidebar:
    st.subheader("메뉴")

    if st.button("🔄 데이터 새로고침"):
        load_google_sheets_data.clear()  # 특정 함수 캐시만 초기화
        st.rerun()

        
st.title("📊 주별 타겟 신규수업 이탈률 분석")

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
df_year1, df_year2 = cleansing_df_week(df, year1, year2)
df_diff_rate = cal_rate(df_year1, df_year2, selected_panel, year1, year2)
df_diff_count = cal_count(df_year1, df_year2, year1, year2)

# 양수/음수 나누기
pos = df_diff_rate[df_diff_rate["diff_pp"] >= 0]
neg = df_diff_rate[df_diff_rate["diff_pp"] < 0]

 # 시각화 생성
st.subheader(f"📈 {selected_panel} 이탈률 분석")
fig = viz_rate_week(
    df_year1, df_year2, 
    selected_panel, 
    pos, neg, 
    df_diff_count, df_diff_rate, 
    year1, year2, 
    true_range
    )
st.plotly_chart(fig)

# 테이블 (지난연도 vs 이번연도 비교)
st.subheader(f"📊 데이터 테이블 ({year1} vs {year2} 비교)")
df_year1_reset = df_year1.reset_index(drop=True)
df_year2_reset = df_year2.reset_index(drop=True)
df_diff_rate_reset = df_diff_rate.reset_index(drop=True)

styled_df = style_comparison_table(df_year1_reset, df_year2_reset, df_diff_rate_reset, year1, year2, selected_panel)
st.dataframe(styled_df)

# 보고서 생성 섹션
st.markdown("---")
st.header("🤖 AI 보고서 생성")

with st.sidebar:
    if st.button("📑 보고서 출력", type="primary"):
        st.session_state.generate_report = True
        st.session_state.report_content = None  # 새로 생성할 때 기존 내용 초기화

# 보고서 생성
if hasattr(st.session_state, 'generate_report') and st.session_state.generate_report:
    if not hasattr(st.session_state, 'report_content') or st.session_state.report_content is None:
        with st.spinner("AI가 보고서를 생성하고 있습니다..."):
            try:
                full_report = full_data_report(df)
                st.session_state.report_content = full_report  # 보고서 내용 저장
                st.success("보고서 생성 완료!")
            except Exception as e:
                st.error(f"보고서 생성 중 오류가 발생했습니다: {e}")
                st.session_state.generate_report = False

# 보고서 표시 (생성된 내용이 있으면 계속 표시)
if hasattr(st.session_state, 'report_content') and st.session_state.report_content:
    st.subheader("📄 전체 데이터 종합 보고서")
    st.markdown(st.session_state.report_content)

    # 다운로드 버튼
    st.download_button(
        label="📥 보고서 다운로드 (.md)",
        data=st.session_state.report_content,
        file_name=f"이탈률_분석_보고서_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"

    )
