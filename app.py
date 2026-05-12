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
st.title("👵 서울시 고령인구 분석")
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
    actual = df1[df1['연도'] <= 2025]
    projected = df1[df1['연도'] >= 2025]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=actual['연도'], y=actual['총인구'], name='실제 데이터',
                             line=dict(color='royalblue', width=3)))
    fig1.add_trace(go.Scatter(x=projected['연도'], y=projected['총인구'], name='추계 데이터 (예측)',
                             line=dict(color='royalblue', width=3, dash='dot')))
    fig1.update_layout(hovermode='x unified', template='plotly_white')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(sql1, language='sql')
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 2025년을 기점으로 서울시 고령인구 증가세가 더욱 가팔라지는 양상을 보입니다.
    * 2030년 이후에는 2022년 대비 약 1.5배 이상의 고령인구가 거주할 것으로 예측됩니다.
    * 향후 10년간 폭발적으로 증가하는 노인 인구를 대비한 장기적인 복지 예산 편성이 시급합니다.
    """)

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
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 송파구와 강서구가 서울시 내에서 고령인구가 가장 많은 자치구로 확인됩니다.
    * 인구 규모가 큰 자치구일수록 고령인구의 절대 수치도 높게 나타나는 경향이 있습니다.
    * 하위권 구와 비교했을 때 최대 3배 이상의 인구 차이가 발생하여 자치구별 맞춤 전략이 필요합니다.
    """)

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
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 강북구와 중구 지역이 전체 고령인구 중 홀로 거주하는 노인의 비율이 가장 높습니다.
    * 인구수가 많았던 송파구보다 오히려 도심권이나 전통적인 주거 밀집 지역의 독거 비율이 높게 나타납니다.
    * 비율이 높은 지역은 고독사 예방 등 밀착형 돌봄 서비스의 우선 순위가 높아야 함을 의미합니다.
    """)

st.divider()

# --- [차트 4: 복지시설 vs 독거노인 수 비교] ---
st.subheader("④ 자치구별 복지시설 수 vs 독거노인 수 비교")
col1, col2 = st.columns([1.5, 1])

sql4 = """
SELECT 
    W.자치구, 
    W.시설합계 AS 복지시설수, 
    SUM(S.독거노인수) AS 총_독거노인수
FROM 복지시설 W
JOIN 독거노인 S ON W.자치구_id = S.자치구_id
GROUP BY W.자치구_id, W.자치구, W.시설합계
ORDER BY 총_독거노인수 DESC
"""
df4 = run_query(sql4)

with col1:
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(go.Bar(x=df4['자치구'], y=df4['총_독거노인수'],
                         name="독거노인 수 (명)", marker_color='lightblue'),
                  secondary_y=False)
    fig4.add_trace(go.Scatter(x=df4['자치구'], y=df4['복지시설수'],
                             name="복지시설 수 (개)", mode='lines+markers',
                             marker_color='red'),
                  secondary_y=True)
    fig4.update_layout(template='plotly_white', hovermode='x unified')
    fig4.update_yaxes(title_text="독거노인 수 (명)", secondary_y=False)
    fig4.update_yaxes(title_text="복지시설 수 (개)", secondary_y=True)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(sql4, language='sql')
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 독거노인 수가 많은 구라고 해서 반드시 복지시설 수가 많은 것은 아님이 확인됩니다.
    * 특정 자치구는 돌봄 수요(독거노인)에 비해 인프라(시설)가 부족한 '복지 불균형' 상태를 보입니다.
    * 시설 확충 시 단순히 인구수가 아닌, 독거노인 밀집도를 고려한 자원 배분이 시급합니다.
    """)

st.divider()
st.caption("데이터 출처: 서울 열린데이터 광장 ")
