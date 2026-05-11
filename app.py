import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="서울시 고령인구 및 복지시설 분석", layout="wide")
st.title("📊 서울시 고령인구 및 돌봄 인프라 대시보드")
st.markdown("데이터베이스(SQLite)를 활용하여 서울시의 고령화 추이와 복지 시설의 불균형을 분석합니다.")

# --- 2. 데이터베이스 연결 및 에러 처리 ---
DB_FILENAME = 'seoul_elderly.db'

# DB 파일이 같은 폴더에 있는지 확인합니다. (없으면 친절한 에러 메시지 출력!)
if not os.path.exists(DB_FILENAME):
    st.error(f"🚨 앗! '{DB_FILENAME}' 파일이 같은 폴더에 없습니다. 데이터를 먼저 준비해주세요!")
    st.stop() # 여기서 코드 실행을 멈춥니다.

# DB에 쿼리를 날려서 데이터를 가져오는 함수 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data(query):
    conn = sqlite3.connect(DB_FILENAME)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.divider()

# --- 차트 1: 서울시 연도별 고령인구 추이 ---
st.subheader("1. 서울시 연도별 고령인구 추이 (2022~2034)")
sql1 = """
SELECT 연도, SUM(고령인구수) AS 총_고령인구수 
FROM 고령인구 
WHERE 연도 BETWEEN 2022 AND 2034 
GROUP BY 연도 
ORDER BY 연도;
"""
df1 = load_data(sql1)

col1, col2 = st.columns([1, 1])
with col1:
    # ① 시각화 (라인 차트)
    fig1 = px.line(df1, x='연도', y='총_고령인구수', markers=True, title="연도별 총 고령인구수 추이")
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    # ② 사용한 SQL
    st.markdown("**사용된 SQL 쿼리:**")
    st.code(sql1, language="sql")
    # ③ 인사이트
    st.info("💡 **인사이트:**\n"
            "그래프의 기울기를 통해 서울시의 고령화가 얼마나 가파르게 진행되는지 확인할 수 있습니다.\n"
            "향후 10년간 폭발적으로 증가하는 노인 인구를 대비한 장기적인 복지 예산 편성이 시급합니다.")

st.divider()

# --- 차트 2: 2024년 자치구별 노인 인구 ---
st.subheader("2. 2024년 서울시 자치구별 고령인구")
sql2 = """
SELECT 자치구, SUM(고령인구수) AS 총_고령인구수 
FROM 고령인구 
WHERE 연도 = 2024 
GROUP BY 자치구 
ORDER BY 총_고령인구수 DESC;
"""
df2 = load_data(sql2)

col1, col2 = st.columns([1, 1])
with col1:
    fig2 = px.bar(df2, x='자치구', y='총_고령인구수', color='총_고령인구수', title="2024년 자치구별 고령인구수")
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.markdown("**사용된 SQL 쿼리:**")
    st.code(sql2, language="sql")
    st.info("💡 **인사이트:**\n"
            "단순한 인구수 기준으로 어떤 자치구에 고령 인구가 가장 많이 밀집해 있는지 한눈에 파악됩니다.\n"
            "이 데이터는 노인 관련 일반 시설(경로당, 보건소 등)의 지역별 우선순위를 정하는 데 활용할 수 있습니다.")

st.divider()

# --- 차트 3: 2024년 자치구별 고령인구 대비 독거노인 비율 ---
st.subheader("3. 2024년 자치구별 고령인구 대비 독거노인 비율 (%)")
# SQLite에서는 정수끼리 나누면 0이 되므로 CAST를 써서 소수점(FLOAT)으로 바꿔줍니다.
sql3 = """
SELECT 
    A.자치구, 
    B.총_독거노인수, 
    A.총_고령인구수,
    ROUND(CAST(B.총_독거노인수 AS FLOAT) / A.총_고령인구수 * 100, 2) AS 독거노인_비율
FROM (
    SELECT 자치구_id, 자치구, SUM(고령인구수) AS 총_고령인구수 
    FROM 고령인구 
    WHERE 연도 = 2024 
    GROUP BY 자치구_id, 자치구
) A
JOIN (
    SELECT 자치구_id, SUM(독거노인수) AS 총_독거노인수 
    FROM 독거노인 
    GROUP BY 자치구_id
) B ON A.자치구_id = B.자치구_id
ORDER BY 독거노인_비율 DESC;
"""
df3 = load_data(sql3)

col1, col2 = st.columns([1, 1])
with col1:
    fig3 = px.bar(df3, x='자치구', y='독거노인_비율', text_auto=True, title="고령인구 대비 독거노인 비율", color='독거노인_비율', color_continuous_scale='Reds')
    st.plotly_chart(fig3, use_container_width=True)
with col2:
    st.markdown("**사용된 SQL 쿼리:**")
    st.code(sql3, language="sql")
    st.info("💡 **인사이트:**\n"
            "전체 노인 수는 적더라도, '독거노인 비율'이 높은 구역은 각별한 주의가 필요합니다.\n"
            "고독사 예방 프로그램이나 1:1 방문 돌봄 서비스는 이 비율이 높은 지역에 집중적으로 투입해야 합니다.")

st.divider()

# --- 차트 4: 자치구별 복지시설 수 vs 독거노인 수 비교 (이중축 차트) ---
st.subheader("4. 자치구별 복지시설 수 vs 독거노인 수 비교")
sql4 = """
SELECT 
    W.자치구, 
    W.시설합계 AS 복지시설수, 
    SUM(S.독거노인수) AS 총_독거노인수
FROM 복지시설 W
JOIN 독거노인 S ON W.자치구_id = S.자치구_id
GROUP BY W.자치구_id, W.자치구, W.시설합계
ORDER BY 총_독거노인수 DESC;
"""
df4 = load_data(sql4)

col1, col2 = st.columns([1, 1])
with col1:
    # 이중축(Dual-axis) 차트 만들기
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    # 막대 차트: 독거노인 수 (왼쪽 축)
    fig4.add_trace(go.Bar(x=df4['자치구'], y=df4['총_독거노인수'], name="독거노인 수 (명)", marker_color='lightblue'), secondary_y=False)
    # 꺾은선 차트: 복지시설 수 (오른쪽 축)
    fig4.add_trace(go.Scatter(x=df4['자치구'], y=df4['복지시설수'], name="복지시설 수 (개)", mode='lines+markers', marker_color='red'), secondary_y=True)
    
    fig4.update_layout(title_text="돌봄 수요(독거노인)와 복지 인프라(시설) 불균형 파악")
    st.plotly_chart(fig4, use_container_width=True)
with col2:
    st.markdown("**사용된 SQL 쿼리:**")
    st.code(sql4, language="sql")
    st.info("💡 **인사이트:**\n"
            "파란색 막대(수요)는 높은데 빨간색 선(인프라)이 푹 꺼져있는 자치구를 찾아보세요.\n"
            "해당 지역이 바로 복지 인프라 확충이 가장 시급한 '복지 사각지대'임을 직관적으로 알 수 있습니다.")