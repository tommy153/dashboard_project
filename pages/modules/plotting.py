import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

def viz_rate_week(
    df_year1, df_year2, 
    selected_panel, 
    pos, neg, 
    df_diff_count, df_diff_rate, 
    year1, year2, 
    true_range):
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

    # 신뢰도가 낮은 구간 배경색 추가
    if selected_panel in true_range:
        range_weeks = abs(true_range[selected_panel])  # 음수를 양수로 변환

        # 데이터의 마지막 주차들 구하기
        max_week = df_year2['주차'].max() if not df_year2.empty else df_year1['주차'].max()
        min_week = df_year2['주차'].min() if not df_year2.empty else df_year1['주차'].min()

        # 신뢰도 낮은 구간 계산 (마지막 N주)
        if range_weeks > 0:
            cutoff_week = max_week - range_weeks + 1  # +1은 경계 포함을 위해
            if cutoff_week <= max_week:
                fig.add_vrect(
                    x0=max(cutoff_week, min_week), x1=max_week + 0.5,
                    fillcolor="red", opacity=0.1,
                    layer="below", line_width=0,
                    annotation_text=f"신뢰도 낮음 ({range_weeks}주)",
                    annotation_position="top left",
                    row=1, col=1
                )

    # 첫 번째 서브플롯: 이탈률 라인 차트
    # 지난년도 데이터
    fig.add_trace(
        go.Scatter(
            x=df_year1['주차'],
            y=df_year1[selected_panel],
            mode='lines+markers',
            name=str(year1),
            line=dict(color='gray', dash='dash', width=3),
            marker=dict(size=8),
            customdata=df_year1[['시작일', '종료일', '신규 활성 수업 수']].values,
            hovertemplate=
                f"<b>{year1}년 %{{x}}주차</b><br>" +
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
            x=df_year2['주차'],
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
                f"<b>{year2}년 %{{x}}주차</b><br>" +
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
            x=pos['주차'],
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
                f"<b>{year2}년 %{{x}}주차</b><br>" +
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
            x=neg['주차'],
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
                f"<b>{year2}년 %{{x}}주차</b><br>" +
                "기간: %{customdata[0]} ~ %{customdata[1]}<br>" +
                f"{selected_panel}: %{{y:.2f}}%<br>" +
                "신규 활성 수업 수: %{customdata[2]}<br>" +
                f"<span style='color:green'>{year1} 대비: %{{customdata[3]:+}}p.p.</span>" +
                "<extra></extra>"
        ),
        row=1, col=1
    )
    
        # 신뢰도가 낮은 구간 배경색 추가
    if selected_panel in true_range:
        range_weeks = abs(true_range[selected_panel])  # -2 → 2로 변환

        # 이번년도 데이터 기준 마지막 주차
        max_week = df_year2['주차'].max() if not df_year2.empty else df_year1['주차'].max()

        # 마지막 N주 구간 (예: -2 → 마지막 2주)
        cutoff_week = max_week - range_weeks + 0.5  # 경계 포함

        fig.add_vrect(
            x0=cutoff_week, 
            x1=max_week + 0.5,   # 마지막 구간 살짝 오른쪽까지
            fillcolor="red", 
            opacity=0.1,
            layer="below", 
            line_width=0,
            annotation_text=f"신뢰도 낮음 ({range_weeks}주)", 
            annotation_position="top left",
            row=1, col=1
        )


    # 두 번째 서브플롯: 신규 활성 수업 수 바 차트
    # 지난년도 바
    # 지난년도 막대 (겹침)
    fig.add_trace(
        go.Bar(
            x=df_diff_count['주차'],
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
                "<b>%{x}주차 비교</b><br>" +
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
            x=df_diff_count['주차'],
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
                "<b>%{x}주차 비교</b><br>" +
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
    fig.update_xaxes(title_text="주차", row=2, col=1)

    # 바 차트를 그룹으로 설정
    fig.update_layout(barmode='overlay')

    return fig

def viz_rate_month(
    df_year1, df_year2, 
    selected_panel, 
    pos, neg, 
    df_diff_count, df_diff_rate, 
    year1, year2, 
    true_range):
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
        # 신뢰도가 낮은 구간 배경색 추가 (월 기준)
    if selected_panel in true_range:
        range_months = abs(true_range[selected_panel])  # 음수를 양수로 변환

        # 데이터의 마지막/최소 월 구하기
        max_month = df_year2['월'].max() if not df_year2.empty else df_year1['월'].max()
        min_month = df_year2['월'].min() if not df_year2.empty else df_year1['월'].min()

        # 신뢰도 낮은 구간 계산 (마지막 N개월)
        if range_months > 0:
            cutoff_month = max_month - range_months + 0.5  # +1은 경계 포함을 위해
            if cutoff_month <= max_month:
                fig.add_vrect(
                    x0=max(cutoff_month, min_month), 
                    x1=max_month + 0.5,
                    fillcolor="red", opacity=0.1,
                    layer="below", line_width=0,
                    annotation_text=f"신뢰도 낮음 ({range_months}개월)",
                    annotation_position="top left",
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

def style_comparison_table(
    df_year1_reset, df_year2_reset, 
    df_diff_rate_reset, 
    year1, year2, 
    selected_panel, week=True):
    """
    연도별 데이터 비교 테이블을 만들고 스타일 적용한 DataFrame 반환
    
    Parameters
    ----------
    df_year1_reset : pd.DataFrame
        지난년도 데이터프레임 (reset_index 된 상태)
    df_year2_reset : pd.DataFrame
        이번년도 데이터프레임 (reset_index 된 상태)
    df_diff_rate_reset : pd.DataFrame
        diff_pp 포함된 데이터프레임
    year1 : int
        비교 기준 년도
    year2 : int
        비교 대상 년도
    selected_panel : str
        비교할 지표명
    
    Returns
    -------
    styled_df : pd.io.formats.style.Styler
        스타일이 적용된 DataFrame Styler 객체
    """

    comparison_df = pd.DataFrame()

    if week:
        # 공통 컬럼
        comparison_df[f'{year1}_연도-주차'] = df_year1_reset['연도'].astype(str) + '-' + df_year1_reset['주차'].astype(str)
        comparison_df[f'{year1}_시작일-종료일'] = df_year1_reset['시작일'] + '~' + df_year1_reset['종료일']

        # 이번년도 공통 컬럼
        comparison_df[f'{year2}_연도-주차'] = df_year2_reset['연도'].astype(str) + '-' + df_year2_reset['주차'].astype(str)
        comparison_df[f'{year2}_시작일-종료일'] = df_year2_reset['시작일'] + '~' + df_year2_reset['종료일']

    else:
        # 공통 컬럼들
        comparison_df[f'{year1}_연도-월'] = df_year1_reset['연도'].astype(str) + '-' + df_year1_reset['월'].astype(str)
        comparison_df[f'{year1}_시작일-종료일'] = df_year1_reset['시작일'] + '~' + df_year1_reset['종료일']
        
        # 이번년도 공통 컬럼들
        comparison_df[f'{year2}_연도-월'] = df_year2_reset['연도'].astype(str) + '-' + df_year2_reset['월'].astype(str)
        comparison_df[f'{year2}_시작일-종료일'] = df_year2_reset['시작일'] + '~' + df_year2_reset['종료일']

    # 지난년도 데이터
    comparison_df[f'{year1}_신규활성수업수'] = df_year1_reset['신규 활성 수업 수']
    comparison_df[f'{year1}_{selected_panel}'] = df_year1_reset[selected_panel]

    # 이번년도 데이터
    comparison_df[f'{year2}_신규활성수업수'] = df_year2_reset['신규 활성 수업 수']
    comparison_df[f'{year2}_{selected_panel}'] = df_year2_reset[selected_panel]

    # 차이 계산
    comparison_df['차이(p.p.)'] = df_diff_rate_reset['diff_pp']

    # 스타일 함수 정의
    def color_diff_column(val):
        if pd.isna(val):
            return ''
        elif val > 0:
            return 'color: #d32f2f'  # 빨간색 (악화)
        elif val < 0:
            return 'color: #2e7d32'  # 초록색 (개선)
        else:
            return ''

    # 숫자 컬럼 포맷 정의
    format_dict = {}
    for col in comparison_df.columns:
        if comparison_df[col].dtype in ['float64', 'int64'] and '수업수' not in col:
            format_dict[col] = '{:.2f}'

    # 스타일 적용
    styled_df = comparison_df.style.map(
        color_diff_column,
        subset=['차이(p.p.)']
    ).format(format_dict)

    return styled_df
