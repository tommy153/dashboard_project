import pandas as pd

def cleansing_df_week(df, year1, year2):
    df_year1 = df[df['연도'] == year1]
    df_year2 = df[df['연도'] == year2]

    common_weeks = set(df_year1['주차']) & set(df_year2['주차'])
    if common_weeks:
        max_common_week = max(common_weeks)
        df_year1_common = df_year1[df_year1['주차'] <= max_common_week]
        df_year2_common = df_year2[df_year2['주차'] <= max_common_week]
    else:
        df_year1_common = df_year1
        df_year2_common = df_year2

    return df_year1_common, df_year2_common

def cleansing_df_month(df, year1, year2):
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
