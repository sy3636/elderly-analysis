import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="서울시 고령인구 및 복지시설 분석 대시보드",
    layout="wide"
)

st.title("📊 서울시 고령인구 및 복지시설 분석 대시보드")
st.write("서울시의 고령화 추이와 복지 인프라 현황을 분석하여 맞춤형 정책 수립의 인사이트를 제공합니다.")

# -----------------------------------------------------------------------------
# 2. 데이터베이스 연결 및 오류 처리
# -----------------------------------------------------------------------------
DB_PATH = 'seoul_elderly.db'

# DB 파일이 없으면 친절하게 에러를 띄우고 실행을 멈춥니다.
if not os.path.exists(DB_PATH):
    st.error("🚨 에러: 'seoul_elderly.db' 파일이 같은 폴더에 없습니다. 파일을 확인해주세요!")
    st.stop()

def run_query(query):
    """SQL 쿼리를 실행하고 Pandas 데이터프레임으로 반환하는 마법의 함수입니다."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 숫자를 '만', '천' 단위의 예쁜 한국어로 바꿔주는 도우미 함수
def format_korean_num(n):
    if n == 0: return "0"
    res = ""
    if n >= 10000:
        res += f"{int(n//10000)}만 "
        n = n % 10000
    if n > 0:
        if n >= 1000:
            res += f"{int(n//1000)}천"
        else:
            res += str(int(n))
    return res.strip() + "명"

# -----------------------------------------------------------------------------
# 차트 1: 서울시 연도별 고령인구 추이 (2022~2034)
# -----------------------------------------------------------------------------
st.markdown("### ① 서울시 연도별 고령인구 추이 (2022~2034)")

query_1 = """
SELECT 연도, SUM(고령인구수) AS 총고령인구
FROM 고령인구
WHERE 연도 BETWEEN 2022 AND 2034
GROUP BY 연도
ORDER BY 연도
"""
df_1 = run_query(query_1)

# 실제 데이터(2022~2025)와 추계 데이터(2025~2034) 분리 
# (연결을 위해 2025년은 양쪽 모두에 포함합니다)
df_1_actual = df_1[df_1['연도'] <= 2025]
df_1_predict = df_1[df_1['연도'] >= 2025]

fig_1 = go.Figure()

# 실제 데이터 라인 (실선)
fig_1.add_trace(go.Scatter(
    x=df_1_actual['연도'], y=df_1_actual['총고령인구'],
    mode='lines+markers', name='실제 데이터',
    line=dict(color='royalblue', width=3)
))

# 추계 데이터 라인 (점선)
fig_1.add_trace(go.Scatter(
    x=df_1_predict['연도'], y=df_1_predict['총고령인구'],
    mode='lines+markers', name='추계 데이터 (예측)',
    line=dict(color='royalblue', width=3, dash='dot')
))

# y축 한국어 단위 설정
min_val_1 = int(df_1['총고령인구'].min() * 0.9)
max_val_1 = int(df_1['총고령인구'].max() * 1.1)
tickvals_1 = list(range(min_val_1, max_val_1, 100000))
ticktext_1 = [format_korean_num(v) for v in tickvals_1]

fig_1.update_layout(
    template='plotly_white', hovermode='x unified',
    xaxis_title='연도', yaxis_title='고령인구수',
    yaxis=dict(tickvals=tickvals_1, ticktext=ticktext_1)
)

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig_1, use_container_width=True)
with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query_1, language='sql')
    st.markdown("##### 💡 데이터 인사이트")
    st.info(
        " * 2025년을 기점으로 서울시 고령인구 증가세가 더욱 가팔라지는 양상을 보입니다.\n"
        " * 2030년 이후에는 2022년 대비 약 1.5배 이상의 고령인구가 거주할 것으로 예측됩니다.\n"
        " * 향후 10년간 폭발적으로 증가하는 노인 인구를 대비한 장기적인 복지 예산 편성이 시급합니다."
    )

st.divider() # 시각적 구분을 위한 선

# -----------------------------------------------------------------------------
# 차트 2: 2024년 자치구별 고령인구 순위
# -----------------------------------------------------------------------------
st.markdown("### ② 2024년 서울시 자치구별 노인 인구")

query_2 = """
SELECT 자치구, 고령인구수
FROM 고령인구
WHERE 연도 = 2024
ORDER BY 고령인구수 ASC
"""
df_2 = run_query(query_2)

fig_2 = px.bar(
    df_2, x='고령인구수', y='자치구', orientation='h',
    color='고령인구수', color_continuous_scale='Blues',
    labels={'고령인구수': '고령인구 수', '자치구': '자치구 명'}
)

tickvals_2 = list(range(0, int(df_2['고령인구수'].max()) + 20000, 20000))
ticktext_2 = [format_korean_num(v) for v in tickvals_2]

fig_2.update_layout(
    template='plotly_white',
    xaxis=dict(tickvals=tickvals_2, ticktext=ticktext_2)
)

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig_2, use_container_width=True)
with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query_2, language='sql')
    st.markdown("##### 💡 데이터 인사이트")
    st.info(
        " * 송파구와 강서구가 서울시 내에서 고령인구가 가장 많은 자치구로 확인됩니다.\n"
        " * 인구 규모가 큰 자치구일수록 고령인구의 절대 수치도 높게 나타나는 경향이 있습니다.\n"
        " * 하위권 구와 비교했을 때 최대 3배 이상의 인구 차이가 발생하여 자치구별 맞춤 전략이 필요합니다."
    )

st.divider()

# -----------------------------------------------------------------------------
# 차트 3: 2024년 고령인구 대비 독거노인 비율
# -----------------------------------------------------------------------------
st.markdown("### ③ 2024년 자치구별 고령인구 대비 독거노인 비율")

query_3 = """
WITH 독거노인총합 AS (
    SELECT 자치구_id, 자치구, SUM(독거노인수) AS 총독거노인수
    FROM 독거노인
    GROUP BY 자치구_id, 자치구
),
고령인구_2024 AS (
    SELECT 자치구_id, 고령인구수
    FROM 고령인구
    WHERE 연도 = 2024
)
SELECT A.자치구, 
       (A.총독거노인수 * 100.0 / B.고령인구수) AS 독거비율
FROM 독거노인총합 A
JOIN 고령인구_2024 B ON A.자치구_id = B.자치구_id
ORDER BY 독거비율 ASC
"""
df_3 = run_query(query_3)

fig_3 = px.bar(
    df_3, x='독거비율', y='자치구', orientation='h',
    labels={'독거비율': '독거노인 비율 (%)', '자치구': '자치구 명'}
)
fig_3.update_traces(marker_color='indianred')
fig_3.update_layout(template='plotly_white')

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig_3, use_container_width=True)
with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query_3, language='sql')
    st.markdown("##### 💡 데이터 인사이트")
    st.info(
        " * 강북구와 중구 지역이 전체 고령인구 중 홀로 거주하는 노인의 비율이 가장 높습니다.\n"
        " * 인구수가 많았던 송파구보다 오히려 도심권이나 전통적인 주거 밀집 지역의 독거 비율이 높게 나타납니다.\n"
        " * 비율이 높은 지역은 고독사 예방 등 밀착형 돌봄 서비스의 우선 순위가 높아야 함을 의미합니다."
    )

st.divider()

# -----------------------------------------------------------------------------
# 차트 4: 자치구별 복지시설 수 vs 독거노인 수 비교 (이중축 차트)
# -----------------------------------------------------------------------------
st.markdown("### ④ 자치구별 복지시설 수 vs 독거노인 수 비교")

query_4 = """
WITH 독거노인총합 AS (
    SELECT 자치구_id, SUM(독거노인수) AS 총독거노인수
    FROM 독거노인
    GROUP BY 자치구_id
)
SELECT F.자치구, 
       S.총독거노인수 AS 독거노인수, 
       F.시설합계 AS 복지시설수
FROM 복지시설 F
JOIN 독거노인총합 S ON F.자치구_id = S.자치구_id
ORDER BY S.총독거노인수 DESC
"""
df_4 = run_query(query_4)

fig_4 = make_subplots(specs=[[{"secondary_y": True}]])

# 왼쪽 Y축: 독거노인 수 (막대형)
fig_4.add_trace(
    go.Bar(x=df_4['자치구'], y=df_4['독거노인수'], name="독거노인 수", marker_color='lightblue'),
    secondary_y=False,
)

# 오른쪽 Y축: 복지시설 수 (꺾은선형)
fig_4.add_trace(
    go.Scatter(x=df_4['자치구'], y=df_4['복지시설수'], name="복지시설 수", 
               mode='lines+markers', marker_color='red'),
    secondary_y=True,
)

# Y축 레이블 한국어 변환 적용
tickvals_4 = list(range(0, int(df_4['독거노인수'].max()) + 5000, 5000))
ticktext_4 = [format_korean_num(v) for v in tickvals_4]

fig_4.update_layout(
    template='plotly_white', hovermode='x unified',
    yaxis=dict(title='독거노인 수', tickvals=tickvals_4, ticktext=ticktext_4),
    yaxis2=dict(title='복지시설 수 (개소)')
)

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig_4, use_container_width=True)
with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query_4, language='sql')
    st.markdown("##### 💡 데이터 인사이트")
    st.info(
        " * 독거노인 수가 많은 구라고 해서 반드시 복지시설 수가 많은 것은 아님이 확인됩니다.\n"
        " * 특정 자치구는 돌봄 수요(독거노인)에 비해 인프라(시설)가 부족한 '복지 불균형' 상태를 보입니다.\n"
        " * 시설 확충 시 단순히 인구수가 아닌, 독거노인 밀집도를 고려한 자원 배분이 시급합니다."
    )

# -----------------------------------------------------------------------------
# 4. 하단 캡션
# -----------------------------------------------------------------------------
st.caption("데이터 출처: 서울 열린데이터 광장")
