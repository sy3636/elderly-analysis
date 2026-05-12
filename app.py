import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 1. 페이지 설정 및 DB 연결 확인
st.set_page_config(page_title="서울시 고령인구 분석 대시보드", layout="wide")

DB_PATH = "seoul_elderly.db"

if not os.path.exists(DB_PATH):
    st.error(f"❌ 데이터베이스 파일('{DB_PATH}')을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    """SQL 쿼리를 실행하여 판다스 데이터프레임으로 반환하는 함수"""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn)

# 헤더 부분
st.title("👵 서울시 고령인구 및 복지시설 분석")
st.markdown("본 대시보드는 서울시 공공데이터를 기반으로 고령화 현황을 시각화합니다.")
st.divider()

# --- [차트 1: 서울시 연도별 고령인구 추이] ---
st.subheader("① 서울시 연도별 고령인구 추이 (2022~2034)")
col1, col2 = st.columns([1.5, 1])

sql1 = """
SELECT 연도, SUM(고령인구수) as 총인구 
FROM 고령인구 
GROUP BY 연도 
ORDER BY 연도
"""
df1 = run_query(sql1)

with col1:
    # 데이터 분리 (연결을 위해 2025년을 양쪽에 포함)
    actual = df1[df1['연도'] <= 2025]
    projected = df1[df1['연도'] >= 2025]

    fig1 = go.Figure()
    # 실선 (실제)
    fig1.add_trace(go.Scatter(x=actual['연도'], y=actual['총인구'], name='실제 데이터',
                             line=dict(color='royalblue', width=3)))
    # 점선 (추계)
    fig1.add_trace(go.Scatter(x=projected['연도'], y=projected['총인구'], name='추계 데이터 (예측)',
                             line=dict(color='royalblue', width=3, dash='dot')))
    
    fig1.update_layout(hovermode='x unified', template='plotly_white')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(sql1, language='sql')
    st.markdown("##### 💡 인사이트")
    st.info("2025년을 기점으로 서울시 고령인구가 가파르게 상승하여 2030년 이후에는 초고령 사회의 특징이 더욱 두드러질 것으로 예측됩니다.")

st.divider()

# --- [차트 2: 2024년 자치구별 고령인구] ---
st.subheader("② 2024년 자치구별 고령인구 순위")
col1, col2 = st.columns([1.5, 1])

sql2 = """
SELECT 자치구, 고령인구수 
FROM 고령인구 
WHERE 연도 = 2024 
ORDER BY 고령인구수 ASC
"""
df2 = run_query(sql2)

with col1:
    fig2 = px.bar(df2, x='고령인구수', y='자치구', orientation='h',
                 color='고령인구수', color_continuous_scale='Blues')
    fig2.update_layout(showlegend=False, template='plotly_white')
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(sql2, language='sql')
    st.markdown("##### 💡 인사이트")
    st.info("특정 자치구(예: 송파구, 강서구 등)의 고령인구 절대 수치가 높게 나타나며, 해당 지역의 복지 수요가 높을 것으로 판단됩니다.")

st.divider()

# --- [차트 3: 2024년 자치구별 독거노인 비율] ---
st.subheader("③ 2024년 고령인구 대비 독거노인 비율")
col1, col2 = st.columns([1.5, 1])

sql3 = """
SELECT a.자치구, 
       (SUM(b.독거노인수) * 100.0 / a.고령인구수) as 독거비율
FROM 고령인구 a
JOIN 독거노인 b ON a.자치구_id = b.자치구_id
WHERE a.연도 = 2024
GROUP BY a.자치구
ORDER BY 독거비율 ASC
"""
df3 = run_query(sql3)

with col1:
    fig3 = px.bar(df3, x='독거비율', y='자치구', orientation='h',
                 labels={'독거비율': '독거노인 비율 (%)'})
    fig3.update_traces(marker_color='indianred')
    fig3.update_layout(template='plotly_white')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(sql3, language='sql')
    st.markdown("##### 💡 인사이트")
    st.info("단순 인구수뿐만 아니라 독거노인 비율을 통해 고립 위험이 높은 지역을 식별할 수 있습니다. 일부 외곽 지역에서 비율이 높게 나타납니다.")

st.divider()

# --- [차트 4: 복지시설 vs 독거노인 수 비교] ---
st.subheader
