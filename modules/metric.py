import pandas as pd

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
