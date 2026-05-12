import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 고령인구 분석", layout="wide")

st.title("📊 서울시 고령인구 분석 대시보드")
st.markdown("---")

# 2. 데이터베이스 연결 및 확인
db_path = 'seoul_elderly.db'

if not os.path.exists(db_path):
    st.error(f"❌ 데이터베이스 파일('{db_path}')을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

# --- 차트 1. 서울시 연도별 고령인구 추이 ---
st.subheader("1. 서울시 연도별 고령인구 추이 (2022~2034)")
col1, col2 = st.columns([2, 1])

with col1:
    sql1 = "SELECT 연도, SUM(고령인구수) as 총인구 FROM 고령인구 GROUP BY 연도 ORDER BY 연도"
    df1 = run_query(sql1)
    
    # 실제 데이터(2022-2025)와 추계 데이터(2026-2034) 분리
    df_real = df1[df1['연도'] <= 2025]
    df_proj = df1[df1['연도'] >= 2025] # 연결을 위해 2025 포함
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_real['연도'], y=df_real['총인구'], name='실제 인구', line=dict(color='blue', width=4)))
    fig1.add_trace(go.Scatter(x=df_proj['연도'], y=df_proj['총인구'], name='추계 인구', line=dict(color='red', width=4, dash='dash')))
    fig1.update_layout(xaxis_title="연도", yaxis_title="총 고령인구 수 (명)", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.code(sql1, language='sql')
    st.info("""
    **데이터 인사이트**
    * 2025년을 기점으로 서울시 고령인구 증가세가 더욱 가팔라지는 양상을 보입니다.
    * 2030년 이후에는 2022년 대비 약 1.5배 이상의 고령인구가 거주할 것으로 예측됩니다.
    * 향후 10년간 폭발적으로 증가하는 노인 인구를 대비한 장기적인 복지 예산 편성이 시급합니다.
    """)

# --- 차트 2. 2024년 자치구별 고령인구 ---
st.subheader("2. 2024년 서울시 자치구별 노인 인구")
col1, col2 = st.columns([2, 1])

with col1:
    sql2 = "SELECT 자치구, 고령인구수 FROM 고령인구 WHERE 연도 = 2024 ORDER BY 고령인구수 DESC"
    df2 = run_query(sql2)
    fig2 = px.bar(df2, x='자치구', y='고령인구수', color='고령인구수', color_continuous_scale='Viridis')
    fig2.update_layout(xaxis_title="자치구 명칭", yaxis_title="고령인구 수 (명)")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.code(sql2, language='sql')
    st.info("""
    **데이터 인사이트**
    * 송파구와 강서구가 서울시 내에서 고령인구가 가장 많은 자치구로 확인됩니다.
    * 인구 규모가 큰 자치구일수록 고령인구의 절대 수치도 높게 나타나는 경향이 있습니다.
    * 하위권 구와 비교했을 때 최대 3배 이상의 인구 차이가 발생하여 자치구별 맞춤 전략이 필요합니다.
    """)

# --- 차트 3. 2024년 자치구별 독거노인 비율 ---
st.subheader("3. 2024년 자치구별 고령인구 대비 독거노인 비율")
col1, col2 = st.columns([2, 1])

with col1:
    # 독거노인 테이블은 행정동 단위이므로 자치구 단위로 합산 필요
    sql3 = """
    SELECT k.자치구, 
           (CAST(SUM(d.독거노인수) AS FLOAT) / k.고령인구수) * 100 as 독거노인비율
    FROM 고령인구 k
    JOIN 독거노인 d ON k.자치구_id = d.자치구_id
    WHERE k.연도 = 2024
    GROUP BY k.자치구
    ORDER BY 독거노인비율 DESC
    """
    df3 = run_query(sql3)
    fig3 = px.bar(df3, x='자치구', y='독거노인비율', color='독거노인비율', color_continuous_scale='Reds')
    fig3.update_layout(xaxis_title="자치구 명칭", yaxis_title="독거노인 비율 (%)")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.code(sql3, language='sql')
    st.info("""
    **데이터 인사이트**
    * 강북구와 중구 지역이 전체 고령인구 중 홀로 거주하는 노인의 비율이 가장 높습니다.
    * 인구수가 많았던 송파구보다 오히려 도심권이나 전통적인 주거 밀집 지역의 독거 비율이 높게 나타납니다.
    * 비율이 높은 지역은 고독사 예방 등 밀착형 돌봄 서비스의 우선 순위가 높아야 함을 의미합니다.
    """)

# --- 차트 4. 복지시설 수 vs 독거노인 수 비교 ---
st.subheader("4. 자치구별 복지시설 수 vs 독거노인 수 비교")
col1, col2 = st.columns([2, 1])

with col1:
    sql4 = """
    SELECT w.자치구, w.시설합계, SUM(d.독거노인수) as 총독거노인수
    FROM 복지시설 w
    JOIN 독거노인 d ON w.자치구_id = d.자치구_id
    GROUP BY w.자치구
    """
    df4 = run_query(sql4)
    
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=df4['자치구'], y=df4['총독거노인수'], name='독거노인 수', marker_color='orange'))
    fig4.add_trace(go.Scatter(x=df4['자치구'], y=df4['시설합계'], name='복지시설 수', yaxis='y2', line=dict(color='blue', width=3)))
    
    fig4.update_layout(
        xaxis_title="자치구 명칭",
        yaxis=dict(title="독거노인 수 (명)"),
        yaxis2=dict(title="복지시설 수 (개)", overlaying='y', side='right'),
        legend=dict(x=1.1, y=1)
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.code(sql4, language='sql')
    st.info("""
    **데이터 인사이트**
    * 독거노인 수가 많은 구라고 해서 반드시 복지시설 수가 많은 것은 아님이 확인됩니다.
    * 특정 자치구는 돌봄 수요(독거노인)에 비해 인프라(시설)가 부족한 '복지 불균형' 상태를 보입니다.
    * 시설 확충 시 단순히 인구수가 아닌, 독거노인 밀집도를 고려한 자원 배분이 시급합니다.
    """)

st.write("---")
st.caption("데이터 출처: 서울 열린데이터 광장 (본 데이터는 교육용으로 가공되었습니다.)")
