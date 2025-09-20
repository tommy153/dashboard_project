from google import genai
import streamlit as st

# 전체 데이터로 보고서 생성
def full_data_report(df):
    """전체 데이터프레임을 Gemini에게 전달해서 종합 보고서 생성"""

    # 전체 데이터를 텍스트로 변환
    data_text = df.to_string()

    # 데이터에서 연도 범위 동적으로 추출
    min_year = df['연도'].min()
    max_year = df['연도'].max()
    min_date = df['날짜'].min().strftime('%Y년 %m월')
    max_date = df['날짜'].max().strftime('%Y년 %m월')

    prompt = f"""
    다음은 교육 서비스의 주별 타겟 신규 수업 이탈률 분석 데이터입니다 ({min_date}부터 {max_date}까지).
    - 데이터 범위: 주단위로 집계된 타겟 신규 수업의 이탈률 데이터
    - 분석 대상: 신규로 시작한 수업의 주차별 이탈 패턴
    - 데이터 기간: {min_year}년~{max_year}년 ({len(df)}주 데이터)

    **데이터 컬럼 설명:**
    - DM (Done_Month): 수업을 지속한 개월 수 (1달=DM1, 2달=DM2, 3달=DM3, 4달=DM4)
    - "결제": 결제 단계에서의 이탈률
    - "과외신청서": 과외신청서 작성 단계에서의 이탈률
    - "1. 결제 직후 매칭 전": 결제 완료 후 선생님 매칭 전까지의 이탈률
    - "2. 매칭 직후 첫 수업 전": 매칭 완료 후 첫 수업 시작 전까지의 이탈률
    - "3. 첫 수업 후 2회차 수업 전": 첫 수업 완료 후 두 번째 수업 전까지의 이탈률
    - "4. 2회차 수업 후 DM 1.0 이하": 두 번째 수업 후 1개월 완주 전까지의 이탈률
    - "5. DM 1 총 이탈": 1개월 완주 전 총 이탈률
    - "DM 3 총 이탈": 3개월 완주 전 총 이탈률
    - "DM 4 총 이탈 (4미만)": 4개월 완주 전 총 이탈률
    - "단골 전환 4개월 이상": 4개월 이상 지속한 단골 고객 비율

    **중요한 데이터 특성:**
    - 이탈률은 후행 지표로, 수업 시작 후 일정 기간이 지나야 정확한 측정이 가능합니다
    - {max_year}년 최근 데이터 (특히 7-9월)는 아직 이탈률 집계가 완료되지 않았을 수 있습니다
    - "단골 전환 4개월 이상" 등 장기 지표는 최근 데이터에서 0.00으로 표시되는 것은 정상입니다 (아직 4개월이 지나지 않음)

    전체 데이터:
    {data_text}

    보고서에 포함할 내용:
    1. {min_year}년 데이터 기준 주요 트렌드 분석 (완전한 집계 데이터)
    2. {max_year}년 상반기 데이터와 2024년 동기간 비교
    3. 가장 문제가 되는 이탈 구간 분석 (어느 단계에서 이탈이 많은지)
    4. 개선된 부분과 악화된 부분 식별
    5. 최근 데이터의 한계점을 고려한 해석
    6. 구체적인 개선 방안 제시 (각 이탈 구간별로)

    **분석 시 주의사항:**
    - 최근 3-4개월 데이터는 아직 완전하지 않을 수 있음을 고려
    - 장기 이탈률 지표는 시간이 충분히 지난 데이터만 신뢰할 것
    - {max_year}년 데이터 해석 시 데이터 집계 완성도를 감안할 것

    한국어로 500-700단어 정도의 상세한 보고서를 작성해주세요.
    """
    
    try:
        if "genai" in st.secrets:
            APIKEY = st.secrets["genai"]["APIKEY"]
            client = genai.Client(api_key=APIKEY)

            # 모델 이름과 함께 generate_content 직접 호출
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )

            return response.text  # 또는 적절한 필드
    except Exception as e:
        return f"오류: {e}"