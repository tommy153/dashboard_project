import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 페이지 설정
st.set_page_config(
    page_title="이탈률 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 이탈률 분석 대시보드")

# Google Sheets 연동 함수
@st.cache_data(ttl=300)  # 5분 캐시
def load_google_sheets_data():
    """Google Sheets에서 데이터 로드"""
    try:
        # Streamlit secrets 또는 로컬 파일에서 인증 정보 가져오기
        if "google_credentials" in st.secrets:
            # Streamlit Cloud에서 실행 시
            credentials_info = dict(st.secrets["google_credentials"])
        else:
            # 로컬에서 실행 시 - credentials.json 파일 사용
            import json
            with open('credentials.json', 'r') as f:
                credentials_info = json.load(f)
        
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
        client = gspread.authorize(creds)
        
        # 스프레드시트 열기
        spreadsheet = client.open("경험그룹_KPI (수업 기준)")
        worksheet = spreadsheet.worksheet("주간 전체신규결제수업의 구간별 이탈")
        
        # 데이터 가져오기
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        # 컬럼명 정리
        for i in df.columns[3:]:
            df[f'{i}'] = df[f'{i}'].str.replace('%', '').astype(float)

        df['날짜'] = pd.to_datetime(df['시작일'])
        df['시작일'] = pd.to_datetime(df['시작일']).dt.strftime('%m-%d')
        df['종료일'] = pd.to_datetime(df['종료일']).dt.strftime('%m-%d')
        df['주차'] = df['날짜'].dt.strftime("%W").astype(int)
        df['연도'] = df['날짜'].dt.year    

        panel_cos = list(df.columns[3:-3])
        # 구간
        df = df[['연도', '주차', '시작일', '종료일', '신규 활성 수업 수'] + panel_cos]
        st.success(f"✅ Google Sheets 데이터 로드 성공! ({len(df)}행)")
        return df, panel_cos
        
    except Exception as e:
        st.error(f"❌ Google Sheets 데이터 로드 실패: {e}")
        # 새로고침 버튼
        if st.button("🔄 데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()
        return pd.DataFrame(), []
    
def cleansing_df(df):
    df_2024 = df[df['연도'] == 2024]
    df_2025 = df[df['연도'] == 2025]

    common_weeks = set(df_2024['주차']) & set(df_2025['주차'])
    max_common_week = max(common_weeks)

    df_2024_common = df_2024[df_2024['주차'] < max_common_week]
    df_2025_common = df_2025[df_2025['주차'] < max_common_week]

    return df_2024_common, df_2025_common

def cal_rate(df_2024_common, df_2025_common, pannel_column):
    df_diff_rate = df_2025_common.copy()
    df_diff_rate[f'2024_{pannel_column}_이탈율'] = df_2024_common[f'{pannel_column}'].values
    df_diff_rate[f'2025_{pannel_column}_이탈율'] = df_2025_common[f'{pannel_column}'].values
    df_diff_rate['diff_pp'] = df_diff_rate[f'2025_{pannel_column}_이탈율'] - df_diff_rate[f'2024_{pannel_column}_이탈율']  # p.p. 차이
    return df_diff_rate

def cal_count(df_2024_common, df_2025_common):
    df_diff_count = df_2025_common.copy()
    df_diff_count['2024_count'] = df_2024_common['신규 활성 수업 수'].values
    df_diff_count['2025_count'] = df_2025_common['신규 활성 수업 수'].values
    df_diff_count['diff_count'] = df_diff_count['2025_count'] - df_diff_count['2024_count']
    return df_diff_count

def viz_rate(df_2024_common, df_2025_common, selected_panel, pos, neg, df_diff_count):
    # 서브플롯 생성 (2행 1열, 높이 비율 3:1)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"{selected_panel} (2024 vs 2025)", "신규 활성 수업 수"),
        vertical_spacing=0.05
    )

    fig.update_layout(template="seaborn")

    # 첫 번째 서브플롯: 이탈률 라인 차트
    # 2024년 데이터
    fig.add_trace(
        go.Scatter(
            x=df_2024_common['주차'],
            y=df_2024_common[selected_panel],
            mode='lines+markers',
            name='2024',
            line=dict(color='gray', dash='dash', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )

    # 2025년 데이터
    fig.add_trace(
        go.Scatter(
            x=df_2025_common['주차'],
            y=df_2025_common[selected_panel],
            mode='lines+markers',
            name='2025',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )

    # 평균선 추가
    avg_2024 = df_2024_common[selected_panel].mean()
    avg_2025 = df_2025_common[selected_panel].mean()

    # 2024 평균 라벨 (오른쪽 위 상단)
    fig.add_annotation(
        x=1, y=1.03,  # 오른쪽 위, y>1로 해서 플롯 위로 조금 띄움
        xref="paper", yref="paper",
        text=f"2024 평균: {avg_2024:.2f}%",
        showarrow=False,
        font=dict(size=12, color="gray", family="Arial", weight="bold"),
        align="right"
    )

    # 2025 평균 라벨 (그 옆에 배치, 살짝 왼쪽으로)
    fig.add_annotation(
        x=0.85, y=1.03,  # 살짝 왼쪽에 붙여줌
        xref="paper", yref="paper",
        text=f"2025 평균: {avg_2025:.2f}%",
        showarrow=False,
        font=dict(size=12, color="blue", family="Arial", weight="bold"),
        align="right"
    )


    # 2025 (양수인 경우 - 초록색 표시)
    fig.add_trace(
        go.Scatter(
            x=pos['주차'],
            y=pos[selected_panel],
            mode='markers',
            marker=dict(size=10, color="blue"),
            name="2025 (양수)",
            customdata=round(pos["diff_pp"],3),
            hovertemplate=
                "<b>%{x}주차</b><br>" +
                "2025: %{y:.2f}%<br>" +
                "<span style='color:red'>2024 대비: %{customdata:+.2f}p.p.</span>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )

    # 2025 (음수인 경우 - 빨간색 표시)
    fig.add_trace(
        go.Scatter(
            x=neg['주차'],
            y=neg[selected_panel],
            mode='markers',
            marker=dict(size=10, color="blue"),
            name="2025 (음수)",
            customdata=round(neg["diff_pp"],3),
            hovertemplate=
                "<b>%{x}주차</b><br>" +
                "2025: %{y:.2f}%<br>" + 
                "<span style='color:green'>2024 대비: %{customdata:+.2f}p.p.</span>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )


    # 두 번째 서브플롯: 신규 활성 수업 수 바 차트
    # 2024년 바
    # 2024 막대 (겹침)
    fig.add_trace(
        go.Bar(
            x=df_diff_count['주차'],
            y=df_diff_count['2024_count'],
            name='2024 신규 활성 수업',
            marker_color='gray',
            opacity=0.6,
            customdata=np.stack([df_diff_count['2025_count'], df_diff_count['diff_count']], axis=-1),
            hovertemplate=
                "<b>%{x}주차</b><br>" +
                "2025년 수업 수: %{customdata[0]}<br>" +
                "2024년 수업 수: %{y}<br>" +
                "차이: %{customdata[1]:+d}<br>" +
                "<extra></extra>"
        ),
        row=2, col=1
    )

    # 2025년 바
    fig.add_trace(
        go.Bar(
            x=df_diff_count['주차'],
            y=df_diff_count['2025_count'],
            name='2025 신규 활성 수업',
            marker_color='blue',
            opacity=0.6,
            customdata=np.stack([df_diff_count['2024_count'], df_diff_count['diff_count']], axis=-1),
            hovertemplate=
                "<b>%{x}주차</b><br>" +
                "2025년 수업 수: %{y}<br>" +
                "2024년 수업 수: %{customdata[0]}<br>" +
                "차이: %{customdata[1]:+d}<br>" +
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

    # Y축 설정
    fig.update_yaxes(title_text="이탈률 (%)", row=1, col=1, range=[1.5, 11])
    fig.update_yaxes(title_text="신규 활성 수업 수", row=2, col=1)

    # X축 설정
    fig.update_xaxes(title_text="주차", row=2, col=1)

    # 바 차트를 그룹으로 설정
    fig.update_layout(barmode='overlay')

    return fig

# 데이터 로드
df, panel_cos = load_google_sheets_data()

# 데이터가 있으면 표시
if not df.empty and panel_cos:
    # panel_cos 선택 UI
    st.subheader("🎯 분석할 구간 선택")
    selected_panel = st.selectbox(
        "분석하고 싶은 구간을 선택하세요:",
        options=panel_cos,
        index=0,
        help="하나의 구간을 선택할 수 있습니다"
    )
    
    df_2024_common, df_2025_common = cleansing_df(df)
    df_diff_rate = cal_rate(df_2024_common, df_2025_common, selected_panel)
    df_diff_count = cal_count(df_2024_common, df_2025_common)
    
    # 양수/음수 나누기
    pos = df_diff_rate[df_diff_rate["diff_pp"] >= 0]
    neg = df_diff_rate[df_diff_rate["diff_pp"] < 0]

    # 시각화 생성
    st.subheader(f"📈 {selected_panel} 이탈률 분석")
    fig = viz_rate(df_2024_common, df_2025_common, selected_panel, pos, neg, df_diff_count)
    st.plotly_chart(fig, use_container_width=True)
    # 테이블 (2024 vs 2025 비교)
    st.subheader("📊 데이터 테이블 (2024 vs 2025 비교)")
    
    # 2024/2025 비교 데이터 생성
    # 인덱스 리셋
    df_2024_reset = df_2024_common.reset_index(drop=True)
    df_2025_reset = df_2025_common.reset_index(drop=True)
    df_diff_rate_reset = df_diff_rate.reset_index(drop=True)
    
    comparison_df = pd.DataFrame()
    
    # 공통 컬럼들
    comparison_df['2024_연도-주차'] = df_2024_reset['연도'].astype(str) + '-' + df_2024_reset['주차'].astype(str)
    comparison_df['2024_시작일-종료일'] = df_2024_reset['시작일'] + '~' + df_2024_reset['종료일']
    
    # 2024년 데이터
    comparison_df['2024_신규활성수업수'] = df_2024_reset['신규 활성 수업 수']
    comparison_df[f'2024_{selected_panel}'] = df_2024_reset[selected_panel]
    
    # 2025년 공통 컬럼들
    comparison_df['2025_연도-주차'] = df_2025_reset['연도'].astype(str) + '-' + df_2025_reset['주차'].astype(str)
    comparison_df['2025_시작일-종료일'] = df_2025_reset['시작일'] + '~' + df_2025_reset['종료일']
    
    # 2025년 데이터  
    comparison_df['2025_신규활성수업수'] = df_2025_reset['신규 활성 수업 수']
    comparison_df[f'2025_{selected_panel}'] = df_2025_reset[selected_panel]
    
    # 차이 계산
    comparison_df['차이(p.p.)'] = df_diff_rate_reset['diff_pp']
    
    st.dataframe(comparison_df, width='stretch')
    

else:
    selected_panel = None
    df_diff_rate = pd.DataFrame()
    df_diff_count = pd.DataFrame()


# 새로고침 버튼
if st.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()
       