import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 1. 페이지 기본 설정 (가장 먼저 와야 함)
st.set_page_config(page_title="서울시 고령인구 분석 대시보드", layout="wide")

# 2. 데이터베이스 파일 존재 여부 확인
DB_FILE = "seoul_elderly.db"
if not os.path.exists(DB_FILE):
    st.error(f"🚨 데이터베이스 파일('{DB_FILE}')을 찾을 수 없습니다. 파이썬 코드(app.py)와 같은 폴더에 파일이 있는지 확인해주세요!")
    st.stop()

# 3. 데이터베이스 조회용 공통 함수
@st.cache_data
def run_query(query):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 대시보드 제목
st.title("📊 서울시 고령인구 분석 대시보드")
st.write("서울시의 고령인구 추이와 독거노인, 복지시설 현황을 분석한 대시보드입니다.")
st.markdown("---")

# =====================================================================
# ① 서울시 연도별 고령인구 추이 (2022~2034)
# =====================================================================
query1 = """
SELECT 연도, SUM(고령인구수) AS 총_고령인구_수
FROM 고령인구
WHERE 연도 BETWEEN 2022 AND 2034
GROUP BY 연도
ORDER BY 연도;
"""
df1 = run_query(query1)

df1_real = df1[df1['연도'] <= 2025]
df1_pred = df1[df1['연도'] >= 2025]

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df1_real['연도'], y=df1_real['총_고령인구_수'],
    mode='lines+markers', name='실제 데이터',
    line=dict(color='royalblue', width=3)
))
fig1.add_trace(go.Scatter(
    x=df1_pred['연도'], y=df1_pred['총_고령인구_수'],
    mode='lines+markers', name='추계 데이터 (예측)',
    line=dict(color='royalblue', width=3, dash='dot')
))

fig1.update_layout(
    title_text="서울시 연도별 고령인구 추이 (2022~2034)",
    xaxis_title="연도 (년)",
    yaxis_title="총 고령인구 수 (명)",
    template='plotly_white',
    hovermode='x unified'
)
fig1.update_yaxes(tickformat=",d")

col1_1, col1_2 = st.columns([2, 1])
with col1_1:
    st.plotly_chart(fig1, use_container_width=True)
with col1_2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query1, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 2025년을 기점으로 서울시 고령인구 증가세가 더욱 가팔라지는 양상을 보입니다.
    * 2030년 이후에는 2022년 대비 약 1.5배 이상의 고령인구가 거주할 것으로 예측됩니다.
    * 향후 10년간 폭발적으로 증가하는 노인 인구를 대비한 장기적인 복지 예산 편성이 시급합니다.
    """)
st.markdown("---")

# =====================================================================
# ② 2024년 자치구별 고령인구 순위
# =====================================================================
query2 = """
SELECT 자치구 AS 자치구명, 고령인구수 AS 고령인구_수
FROM 고령인구
WHERE 연도 = 2024
ORDER BY 고령인구_수 ASC; 
"""
df2 = run_query(query2)

fig2 = px.bar(
    df2, x='고령인구_수', y='자치구명', orientation='h',
    color='고령인구_수', color_continuous_scale='Blues',
    title="2024년 자치구별 고령인구 순위",
    labels={'고령인구_수': '고령인구 수 (명)', '자치구명': '자치구'}
)
fig2.update_layout(template='plotly_white', height=700)  # ← height 추가
fig2.update_xaxes(tickformat=",d")

col2_1, col2_2 = st.columns([2, 1])
with col2_1:
    st.plotly_chart(fig2, use_container_width=True)
with col2_2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query2, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 송파구와 강서구가 서울시 내에서 고령인구가 가장 많은 자치구로 확인됩니다.
    * 인구 규모가 큰 자치구일수록 고령인구의 절대 수치도 높게 나타나는 경향이 있습니다.
    * 하위권 구와 비교했을 때 최대 3배 이상의 인구 차이가 발생하여 자치구별 맞춤 전략이 필요합니다.
    """)
st.markdown("---")

# =====================================================================
# ③ 2024년 고령인구 대비 독거노인 비율
# =====================================================================
query3 = """
SELECT 
    p.자치구 AS 자치구명,
    (SUM(a.독거노인수) * 100.0) / p.고령인구수 AS 독거노인_비율_퍼센트
FROM 고령인구 p
JOIN 독거노인 a ON p.자치구_id = a.자치구_id
WHERE p.연도 = 2024
GROUP BY p.자치구, p.고령인구수
ORDER BY 독거노인_비율_퍼센트 ASC;
"""
df3 = run_query(query3)

fig3 = px.bar(
    df3, x='독거노인_비율_퍼센트', y='자치구명', orientation='h',
    title="2024년 자치구별 고령인구 대비 독거노인 비율",
    labels={'독거노인_비율_퍼센트': '독거노인 비율 (%)', '자치구명': '자치구'}
)
fig3.update_traces(marker_color='indianred')
fig3.update_layout(template='plotly_white', height=700)  # ← height 추가
fig3.update_xaxes(tickformat=",.1f")

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    st.plotly_chart(fig3, use_container_width=True)
with col3_2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query3, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 금천구와 강서구 지역이 전체 고령인구 중 홀로 거주하는 노인의 비율이 가장 높습니다.
    * 인구수가 많았던 송파구보다 오히려 도심권이나 전통적인 주거 밀집 지역의 독거 비율이 높게 나타납니다.
    * 비율이 높은 지역은 복지시설 확충, 밀착형 돌봄 서비스 지원의 우선 순위가 높아야 함을 시사합니다.
    """)
st.markdown("---")

# =====================================================================
# ④ 자치구별 복지시설 수 vs 독거노인 수 비교
# =====================================================================
query4 = """
SELECT 
    w.자치구 AS 자치구명,
    SUM(a.독거노인수) AS 총_독거노인_수,
    w.시설합계 AS 복지시설_수
FROM 복지시설 w
JOIN 독거노인 a ON w.자치구_id = a.자치구_id
GROUP BY w.자치구_id, w.자치구, w.시설합계
ORDER BY 총_독거노인_수 DESC;
"""
df4 = run_query(query4)

fig4 = make_subplots(specs=[[{"secondary_y": True}]])

fig4.add_trace(
    go.Bar(x=df4['자치구명'], y=df4['총_독거노인_수'], name="독거노인 수", marker_color='lightblue'),
    secondary_y=False,
)
fig4.add_trace(
    go.Scatter(x=df4['자치구명'], y=df4['복지시설_수'], name="복지시설 수", mode='lines+markers', marker_color='red'),
    secondary_y=True,
)

fig4.update_layout(
    title_text="자치구별 돌봄 수요(독거노인) 대비 인프라(복지시설) 비교",
    template='plotly_white',
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig4.update_yaxes(title_text="독거노인 수 (명)", secondary_y=False, tickformat=",d")
fig4.update_yaxes(title_text="복지시설 수 (개)", secondary_y=True, tickformat=",d")

col4_1, col4_2 = st.columns([2, 1])
with col4_1:
    st.plotly_chart(fig4, use_container_width=True)
with col4_2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query4, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 독거노인 수가 많은 구라고 해서 복지시설 수가 비례하여 많지 않음이 확인됩니다.
    * 특정 자치구는 돌봄 수요(독거노인)에 비해 인프라(시설)가 부족한 '복지 불균형' 상태를 보입니다.
    * 시설 확충 시 단순히 인구수가 아닌, 독거노인 밀집도를 고려한 자원 배분이 필요합니다.
    """)

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("데이터 출처: 서울 열린데이터 광장")
