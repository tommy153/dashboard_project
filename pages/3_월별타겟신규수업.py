import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# Google Sheets 연동 함수
@st.cache_data(ttl=300)  # 5분 캐시
def load_google_sheets_data():
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
    worksheet = spreadsheet.worksheet("대시보드용_월별타겟신규수업")

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

    # 월별 정보 추출
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month

    # 패널 컬럼
    panel_cos = list(df.columns[3:-3])

    # 최종 컬럼 선택
    df = df[['연도', '날짜', '월', '시작일', '종료일', '신규 활성 수업 수'] + panel_cos]

    # 오늘 이전 데이터만 사용
    today = datetime.now()
    current_week_data = df[df['날짜'] < today]

    st.success(f"✅ Google Sheets 데이터 로드 성공! ({len(df)}행)")

    return current_week_data, panel_cos


def cleansing_df(df, year1, year2):
    df_year1 = df[df['연도'] == year1]
    df_year2 = df[df['연도'] == year2]

    common_months = set(df_year1['월']) & set(df_year2['월'])
    if common_months:
        max_common_month = max(common_months)
        df_year1_common = df_year1[df_year1['월'] <= max_common_month]
        df_year2_common = df_year2[df_year2['월'] <= max_common_month]
    else:
        df_year1_common = df_year1
        df_year2_common = df_year2

    return df_year1_common, df_year2_common

def cal_rate(df_year1, df_year2, pannel_column, year1, year2):
    # 두 데이터프레임의 길이를 맞춰주기
    min_length = min(len(df_year1), len(df_year2))

    df_year1_trimmed = df_year1.head(min_length).reset_index(drop=True)
    df_year2_trimmed = df_year2.head(min_length).reset_index(drop=True)

    df_diff_rate = df_year2_trimmed.copy()
    df_diff_rate[f'{year1}_{pannel_column}_이탈율'] = df_year1_trimmed[f'{pannel_column}'].values
    df_diff_rate[f'{year2}_{pannel_column}_이탈율'] = df_year2_trimmed[f'{pannel_column}'].values
    df_diff_rate['diff_pp'] = df_diff_rate[f'{year2}_{pannel_column}_이탈율'] - df_diff_rate[f'{year1}_{pannel_column}_이탈율']  # p.p. 차이
    return df_diff_rate

def cal_count(df_year1, df_year2, year1, year2):
    # 두 데이터프레임의 길이를 맞춰주기
    min_length = min(len(df_year1), len(df_year2))

    df_year1_trimmed = df_year1.head(min_length).reset_index(drop=True)
    df_year2_trimmed = df_year2.head(min_length).reset_index(drop=True)

    df_diff_count = df_year2_trimmed.copy()
    df_diff_count[f'{year1}_count'] = df_year1_trimmed['신규 활성 수업 수'].values
    df_diff_count[f'{year2}_count'] = df_year2_trimmed['신규 활성 수업 수'].values
    df_diff_count['diff_count'] = df_diff_count[f'{year2}_count'] - df_diff_count[f'{year1}_count']
    return df_diff_count

def viz_rate(df_year1, df_year2, selected_panel, pos, neg, df_diff_count, df_diff_rate, year1, year2):
    # 모든 데이터프레임의 길이를 맞춰주기
    min_length = min(len(df_year1), len(df_year2), len(df_diff_count), len(df_diff_rate))

    df_year1 = df_year1.head(min_length).reset_index(drop=True)
    df_year2 = df_year2.head(min_length).reset_index(drop=True)
    df_diff_count = df_diff_count.head(min_length).reset_index(drop=True)
    df_diff_rate = df_diff_rate.head(min_length).reset_index(drop=True)
    # 서브플롯 생성 (2행 1열, 높이 비율 3:1)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"{selected_panel} ({year1} vs {year2})", "신규 활성 수업 수"),
        vertical_spacing=0.05
    )

    fig.update_layout(template="seaborn")

    # 첫 번째 서브플롯: 이탈률 라인 차트
    # 지난년도 데이터
    fig.add_trace(
        go.Scatter(
            x=df_year1['월'],
            y=df_year1[selected_panel],
            mode='lines+markers',
            name=str(year1),
            line=dict(color='gray', dash='dash', width=3),
            marker=dict(size=8),
            customdata=df_year1[['시작일', '종료일', '신규 활성 수업 수']].values,
            hovertemplate=
                f"<b>{year1}년 %{{x}}월</b><br>" +
                "기간: %{customdata[0]} ~ %{customdata[1]}<br>" +
                f"{selected_panel}: %{{y:.2f}}%<br>" +
                "신규 활성 수업 수: %{customdata[2]}<br>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )

    # 이번년도 데이터
    fig.add_trace(
        go.Scatter(
            x=df_year2['월'],
            y=df_year2[selected_panel],
            mode='lines+markers',
            name=str(year2),
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            customdata=np.column_stack([
                df_year2['시작일'].values, df_year2['종료일'].values,
                df_diff_rate['diff_pp'].values
            ]),
            hovertemplate=
                f"<b>{year2}년 %{{x}}월</b><br>" +
                "기간: %{customdata[0]} ~ %{customdata[1]}<br>" +
                f"{selected_panel}: %{{y:.2f}}%<br>" +
                f"{year1}년 대비: %{{customdata[2]:+.2f}}p.p.<br>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )

    # 평균선 추가
    avg_year1 = df_year1[selected_panel].mean()
    avg_year2 = df_year2[selected_panel].mean()

    # 지난년도 평균 라벨 (오른쪽 위 상단)
    fig.add_annotation(
        x=1, y=1.03,  # 오른쪽 위, y>1로 해서 플롯 위로 조금 띄움
        xref="paper", yref="paper",
        text=f"{year1} 평균: {avg_year1:.2f}%",
        showarrow=False,
        font=dict(size=12, color="gray", family="Arial", weight="bold"),
        align="right"
    )

    # 이번년도 평균 라벨 (그 옆에 배치, 살짝 왼쪽으로)
    fig.add_annotation(
        x=0.85, y=1.03,  # 살짝 왼쪽에 붙여줌
        xref="paper", yref="paper",
        text=f"{year2} 평균: {avg_year2:.2f}%",
        showarrow=False,
        font=dict(size=12, color="blue", family="Arial", weight="bold"),
        align="right"
    )

    # 이번년도 (양수인 경우 - 초록색 표시)
    fig.add_trace(
        go.Scatter(
            x=pos['월'],
            y=pos[selected_panel],
            mode='markers',
            marker=dict(size=10, color="blue"),
            name=f"{year2} (양수)",
            customdata=np.column_stack([
                pos['시작일'].values,
                pos['종료일'].values,
                pos['신규 활성 수업 수'].values,
                np.round(pos["diff_pp"].values, 2)
            ]),
            hovertemplate=
                f"<b>{year2}년 %{{x}}월</b><br>" +
                "기간: %{customdata[0]} ~ %{customdata[1]}<br>" +
                f"{selected_panel}: %{{y:.2f}}%<br>" +
                "신규 활성 수업 수: %{customdata[2]}<br>" +
                f"<span style='color:red'>{year1} 대비: %{{customdata[3]:+}}p.p.</span>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )

    # 이번년도 (음수인 경우 - 빨간색 표시)
    fig.add_trace(
        go.Scatter(
            x=neg['월'],
            y=neg[selected_panel],
            mode='markers',
            marker=dict(size=10, color="blue"),
            name=f"{year2} (음수)",
            customdata=np.column_stack([
                neg['시작일'].values,
                neg['종료일'].values,
                neg['신규 활성 수업 수'].values,
                np.round(neg["diff_pp"].values, 2)
            ]),
            hovertemplate=
                f"<b>{year2}년 %{{x}}월</b><br>" +
                "기간: %{customdata[0]} ~ %{customdata[1]}<br>" +
                f"{selected_panel}: %{{y:.2f}}%<br>" +
                "신규 활성 수업 수: %{customdata[2]}<br>" +
                f"<span style='color:green'>{year1} 대비: %{{customdata[3]:+}}p.p.</span>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )

    # 두 번째 서브플롯: 신규 활성 수업 수 바 차트
    # 지난년도 바
    # 지난년도 막대 (겹침)
    fig.add_trace(
        go.Bar(
            x=df_diff_count['월'],
            y=df_diff_count[f'{year1}_count'],
            name=f'{year1} 신규 활성 수업',
            marker_color='gray',
            opacity=0.6,
            customdata=np.column_stack([
                df_year1['시작일'].values,
                df_year1['종료일'].values,
                df_year2['시작일'].values,
                df_year2['종료일'].values,
                df_diff_count[f'{year2}_count'].values,
                df_diff_count['diff_count'].values
            ]),
            hovertemplate=
                "<b>%{x}월 비교</b><br>" +
                f"{year2}년 (%{{customdata[2]}}~%{{customdata[3]}}): %{{customdata[4]}}개<br>" +
                f"{year1}년 (%{{customdata[0]}}~%{{customdata[1]}}): %{{y}}개<br>" +
                "차이: %{customdata[5]:+d}개<br>" +
                "<extra></extra>"
        ),
        row=2, col=1
    )

    # 이번년도 바
    fig.add_trace(
        go.Bar(
            x=df_diff_count['월'],
            y=df_diff_count[f'{year2}_count'],
            name=f'{year2} 신규 활성 수업',
            marker_color='blue',
            opacity=0.6,
            customdata=np.column_stack([
                df_year2['시작일'].values,
                df_year2['종료일'].values,
                df_year1['시작일'].values,
                df_year1['종료일'].values,
                df_diff_count[f'{year1}_count'].values,
                df_diff_count['diff_count'].values
            ]),
            hovertemplate=
                "<b>%{x}월 비교</b><br>" +
                f"{year2}년 (%{{customdata[0]}}~%{{customdata[1]}}): %{{y}}개<br>" +
                f"{year1}년 (%{{customdata[2]}}~%{{customdata[3]}}): %{{customdata[4]}}개<br>" +
                "차이: %{customdata[5]:+d}개<br>" +
                "<extra></extra>"
        ),
        row=2, col=1
    )

    # 레이아웃 설정
    fig.update_layout(
        title_text=f"{selected_panel} 이탈률 분석",
        showlegend=True,
        height=800,
        width=1400
    )

    fig.update_traces(
        hoverlabel=dict(
            bgcolor="white",   # 배경 흰색
            font=dict(size=13) # 글자 크기 키우기
        )
    )

    # --- y축 범위 자동 계산 ---
    # 두 데이터프레임에서 최소/최대 구하기
    ymin = min(df_year1[selected_panel].min(), df_year2[selected_panel].min())
    ymax = max(df_year1[selected_panel].max(), df_year2[selected_panel].max())

    # 보기 좋게 여유(10% 정도) 추가
    y_margin = (ymax - ymin) * 0.1 if ymax > ymin else 1
    ymin_fixed = ymin - y_margin
    ymax_fixed = ymax + y_margin

    # Y축 설정 (자동 고정값 사용)
    fig.update_yaxes(title_text="이탈률 (%)", row=1, col=1, range=[ymin_fixed, ymax_fixed])
    fig.update_yaxes(title_text="신규 활성 수업 수", row=2, col=1)

    # X축 설정
    fig.update_xaxes(title_text="월", row=2, col=1)

    # 바 차트를 그룹으로 설정
    fig.update_layout(barmode='overlay')

    return fig

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

df, panel_cos = load_google_sheets_data()

# 데이터가 제대로 로드되었는지 확인
if df.empty or '연도' not in df.columns:
    st.error("데이터를 로드할 수 없습니다. 새로고침을 시도해보세요.")
    st.stop()

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
df_year1, df_year2 = cleansing_df(df, year1, year2)
df_diff_rate = cal_rate(df_year1, df_year2, selected_panel, year1, year2)
df_diff_count = cal_count(df_year1, df_year2, year1, year2)

# 양수/음수 나누기
pos = df_diff_rate[df_diff_rate["diff_pp"] >= 0]
neg = df_diff_rate[df_diff_rate["diff_pp"] < 0]

 # 시각화 생성
st.subheader(f"📈 {selected_panel} 월별 이탈률 분석")
fig = viz_rate(df_year1, df_year2, selected_panel, pos, neg, df_diff_count, df_diff_rate, year1, year2)
st.plotly_chart(fig)

# 테이블 (지난연도 vs 이번연도 비교)
st.subheader(f"📊 데이터 테이블 ({year1} vs {year2} 비교)")
df_year1_reset = df_year1.reset_index(drop=True)
df_year2_reset = df_year2.reset_index(drop=True)
df_diff_rate_reset = df_diff_rate.reset_index(drop=True)

comparison_df = pd.DataFrame()

# 공통 컬럼들
comparison_df[f'{year1}_연도-월'] = df_year1_reset['연도'].astype(str) + '-' + df_year1_reset['월'].astype(str)
comparison_df[f'{year1}_시작일-종료일'] = df_year1_reset['시작일'] + '~' + df_year1_reset['종료일']

# 지난년도 데이터
comparison_df[f'{year1}_신규활성수업수'] = df_year1_reset['신규 활성 수업 수']
comparison_df[f'{year1}_{selected_panel}'] = df_year1_reset[selected_panel]

# 이번년도 공통 컬럼들
comparison_df[f'{year2}_연도-월'] = df_year2_reset['연도'].astype(str) + '-' + df_year2_reset['월'].astype(str)
comparison_df[f'{year2}_시작일-종료일'] = df_year2_reset['시작일'] + '~' + df_year2_reset['종료일']

# 이번년도 데이터
comparison_df[f'{year2}_신규활성수업수'] = df_year2_reset['신규 활성 수업 수']
comparison_df[f'{year2}_{selected_panel}'] = df_year2_reset[selected_panel]

# 차이 계산
comparison_df['차이(p.p.)'] = df_diff_rate_reset['diff_pp']

# 스타일 함수 정의
def color_diff_column(val):
    """차이(p.p.) 컬럼에 조건부 색상 적용"""
    if pd.isna(val):
        return ''
    elif val > 0:
        return 'color: #d32f2f'  # 빨간색 (악화)
    elif val < 0:
        return 'color: #2e7d32'  # 초록색 (개선)
    else:
        return ''

# 모든 숫자 컬럼에 포맷 적용
format_dict = {}
for col in comparison_df.columns:
    if comparison_df[col].dtype in ['float64', 'int64'] and '수업수' not in col:
        format_dict[col] = '{:.2f}'

# 스타일이 적용된 데이터프레임 표시
styled_df = comparison_df.style.map(
    color_diff_column,
    subset=['차이(p.p.)']
).format(format_dict)

st.dataframe(styled_df)


