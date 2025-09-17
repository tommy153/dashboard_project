import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="이탈률 분석 대시보드 홈",
    page_icon="🏠",
    layout="wide"
)

# 메인 헤더
st.title("🏠 이탈률 분석 대시보드")
st.markdown("---")


st.header("📊 대시보드 개요")
st.markdown("""
**이탈률 분석 대시보드**에 오신 것을 환영합니다!

이 대시보드는 신규 활성 수업의 구간별 이탈률을 분석하여 
교육 서비스의 품질 향상과 학습자 만족도 개선을 위한 
데이터 기반 인사이트를 제공합니다.

### 🎯 주요 기능
- **실시간 데이터 연동**: Google Sheets와 연동하여 최신 데이터 자동 업데이트
- **연도별 비교 분석**: 2024년과 2025년 데이터 비교를 통한 트렌드 파악
- **구간별 세부 분석**: 다양한 학습 구간별 이탈률 상세 분석
- **시각화**: 직관적인 차트와 그래프를 통한 데이터 시각화
""")

# 분석 유형 섹션
st.markdown("---")
st.header("📊 분석 유형")

analysis_col1, analysis_col2 = st.columns(2)

with analysis_col1:
    st.markdown("""
    ### 📅 주간 분석
    **Weekly Analysis**
    
    주간 단위로 이탈률 데이터를 분석합니다.
    - 주차별 트렌드 분석
    - 2024-2025년 비교
    - 구간별 세부 분석
    - 신규 활성 수업 수 추적
    """)

with analysis_col2:
    st.markdown("""
    ### 📆 월간 분석
    **Monthly Analysis**
    
    월간 단위로 이탈률 데이터를 분석합니다.
    - 월별 트렌드 분석  
    - 장기적 패턴 파악
    - 계절성 분석
    - 종합적 성과 평가
    """)

# 사용 가이드 섹션
st.markdown("---")
st.markdown("""
### 📋 사용 가이드

1. **사이드바**에서 원하는 분석 페이지(주간/월간)를 선택하세요
2. **구간 선택**에서 분석하고 싶은 구간을 선택하세요
3. **차트**를 통해 2024년과 2025년 데이터를 비교 분석하세요
4. **호버 정보**를 통해 상세한 데이터를 확인하세요
5. **테이블**에서 정확한 수치를 확인하세요
6. 🔄 **새로고침 버튼**으로 최신 데이터를 불러오세요 -> 데이터 연동 개발중..
7. 구간 선택시 그래프가 이상하게 나온다면
https://files.slack.com/files-pri/TCFPKPH17-F09F6TB4UP9/image.png

### 💡 분석 Tips
- 📊 **차트 인터랙션**: 차트의 점에 마우스를 올리면 상세 정보를 볼 수 있습니다
- 🎯 **범례 활용**: 범례를 클릭하여 특정 데이터를 숨기거나 표시할 수 있습니다
- 🔄 **데이터 업데이트**: 데이터는 5분마다 캐시가 업데이트됩니다 -> 데이터 연동 개발중..
- 📈 **트렌드 분석**: 2024년과 2025년 데이터를 비교하여 개선/악화 트렌드를 파악하세요
- 🎨 **색상 구분**: 빨간색(이탈률 증가), 초록색(이탈률 감소)으로 구분됩니다
""")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 10px;'>
        <p>📊 이탈률 분석 대시보드 | Made with Streamlit</p>
        <p>데이터 출처: Google Sheets - 경험그룹_KPI (수업 기준)</p>
    </div>
    """,
    unsafe_allow_html=True
)
