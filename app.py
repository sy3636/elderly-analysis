import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. 페이지 및 기본 설정
# ==========================================
st.set_page_config(layout="wide", page_title="서울시 고령인구 및 복지시설 분석 대시보드")
st.title("📊 서울시 고령인구 및 복지시설 분석 대시보드")
st.write("서울시의 고령화 추이와 자치구별 복지 인프라 현황을 분석한 대시보드입니다.")
st.markdown("---")

# ==========================================
# 2. 데이터베이스 연결 및 에러 처리
# ==========================================
# DB 파일이 같은 폴더에 있는지 확인합니다.
if not os.path.exists("seoul_elderly.db"):
    st.error("🚨 데이터베이스 파일('seoul_elderly.db')을 찾을 수 없습니다. app.py와 같은 폴더에 파일이 있는지 확인해주세요!")
    st.stop() # 에러가 나면 아래 코드를 실행하지 않고 멈춥니다.

# SQL 쿼리를 실행하고 결과를 데이터프레임(표)으로 반환하는 함수입니다.
def run_query(query):
    conn = sqlite3.connect("seoul_elderly.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==========================================
# 3. 차트 생성 파트
# ==========================================

# -----------------------------------------------------------
# ① 서울시 연도별 고령인구 추이 (2022~2034)
# -----------------------------------------------------------
st.subheader("1. 서울시 연도별 고령인구 추이 (2022~2034)")
col1, col2 = st.columns([2, 1])

with col1:
    query1 = """
    SELECT 연도, SUM(고령인구수) as 총고령인구 
    FROM 고령인구 
    GROUP BY 연도 
    ORDER BY 연도
    """
    df1 = run_query(query1)
    
    # 실선과 점선을 잇기 위해 2025년을 양쪽 데이터에 모두 포함시킵니다.
    df_actual = df1[df1['연도'] <= 2025]
    df_pred = df1[df1['연도'] >= 2025]
    
    fig1 = go.Figure()
    # 실제 데이터 (실선)
    fig1.add_trace(go.Scatter(x=df_actual['연도'], y=df_actual['총고령인구'], 
                              mode='lines+markers', name='실제 데이터', 
                              line=dict(color='royalblue')))
    # 추계 데이터 (점선)
    fig1.add_trace(go.Scatter(x=df_pred['연도'], y=df_pred['총고령인구'], 
                              mode='lines+markers', name='추계 데이터 (예측)', 
                              line=dict(color='royalblue', dash='dot')))
    
    fig1.update_layout(template='plotly_white', hovermode='x unified',
                       xaxis_title="연도 (년)", yaxis_title="총 고령인구 수 (명)")
    fig1.update_yaxes(tickformat=",d") # K, M 단위 없이 콤마(,)만 표시
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query1, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 2025년을 기점으로 서울시 고령인구 증가세가 더욱 가팔라지는 양상을 보입니다.
    * 2030년 이후에는 2022년 대비 약 1.5배 이상의 고령인구가 거주할 것으로 예측됩니다.
    * 향후 10년간 폭발적으로 증가하는 노인 인구를 대비한 장기적인 복지 예산 편성이 시급합니다.
    """)

st.markdown("---")

# -----------------------------------------------------------
# ② 2024년 자치구별 고령인구 순위
# -----------------------------------------------------------
st.subheader("2. 2024년 서울시 자치구별 노인 인구")
col1, col2 = st.columns([2, 1])

with col1:
    query2 = """
    SELECT 자치구, 고령인구수 
    FROM 고령인구 
    WHERE 연도 = 2024 
    ORDER BY 고령인구수 ASC
    """
    df2 = run_query(query2)
    
    fig2 = px.bar(df2, x='고령인구수', y='자치구', orientation='h', 
                  color='고령인구수', color_continuous_scale='Blues')
    fig2.update_layout(template='plotly_white', coloraxis_showscale=False,
                       xaxis_title="고령인구 수 (명)", yaxis_title="자치구 명")
    fig2.update_xaxes(tickformat=",d")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query2, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 송파구와 강서구가 서울시 내에서 고령인구가 가장 많은 자치구로 확인됩니다.
    * 인구 규모가 큰 자치구일수록 고령인구의 절대 수치도 높게 나타나는 경향이 있습니다.
    * 하위권 구와 비교했을 때 최대 3배 이상의 인구 차이가 발생하여 자치구별 맞춤 전략이 필요합니다.
    """)

st.markdown("---")

# -----------------------------------------------------------
# ③ 2024년 고령인구 대비 독거노인 비율
# -----------------------------------------------------------
st.subheader("3. 2024년 자치구별 고령인구 대비 독거노인 비율")
col1, col2 = st.columns([2, 1])

with col1:
    query3 = """
    SELECT 
        p.자치구, 
        (SUM(a.독거노인수) * 100.0 / p.고령인구수) AS 독거비율
    FROM 고령인구 p
    JOIN 독거노인 a ON p.자치구_id = a.자치구_id
    WHERE p.연도 = 2024
    GROUP BY p.자치구_id, p.자치구, p.고령인구수
    ORDER BY 독거비율 ASC
    """
    df3 = run_query(query3)
    
    fig3 = px.bar(df3, x='독거비율', y='자치구', orientation='h', 
                  color_discrete_sequence=['indianred'])
    fig3.update_layout(template='plotly_white',
                       xaxis_title="독거노인 비율 (%)", yaxis_title="자치구 명")
    # 소수점 1자리까지 표시
    fig3.update_xaxes(tickformat=".1f")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query3, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 강북구와 중구 지역이 전체 고령인구 중 홀로 거주하는 노인의 비율이 가장 높습니다.
    * 인구수가 많았던 송파구보다 오히려 도심권이나 전통적인 주거 밀집 지역의 독거 비율이 높게 나타납니다.
    * 비율이 높은 지역은 고독사 예방 등 밀착형 돌봄 서비스의 우선 순위가 높아야 함을 의미합니다.
    """)

st.markdown("---")

# -----------------------------------------------------------
# ④ 자치구별 복지시설 수 vs 독거노인 수 비교
# -----------------------------------------------------------
st.subheader("4. 자치구별 복지시설 수 vs 독거노인 수 비교")
col1, col2 = st.columns([2, 1])

with col1:
    query4 = """
    SELECT 
        w.자치구, 
        SUM(a.독거노인수) AS 총독거노인수, 
        w.시설합계 AS 복지시설수
    FROM 복지시설 w
    JOIN 독거노인 a ON w.자치구_id = a.자치구_id
    GROUP BY w.자치구_id, w.자치구, w.시설합계
    ORDER BY 총독거노인수 DESC
    """
    df4 = run_query(query4)
    
    # 이중축 차트 생성
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 막대 차트 (왼쪽 y축 - 독거노인 수)
    fig4.add_trace(go.Bar(x=df4['자치구'], y=df4['총독거노인수'], 
                          name="독거노인 수", marker_color='lightblue'),
                   secondary_y=False)
    
    # 라인 차트 (오른쪽 y축 - 복지시설 수)
    fig4.add_trace(go.Scatter(x=df4['자치구'], y=df4['복지시설수'], 
                              name="복지시설 수", mode='lines+markers', 
                              marker_color='red'),
                   secondary_y=True)
    
    fig4.update_layout(template='plotly_white', hovermode='x unified',
                       xaxis_title="자치구 명")
    fig4.update_yaxes(title_text="독거노인 수 (명)", tickformat=",d", secondary_y=False)
    fig4.update_yaxes(title_text="복지시설 수 (개)", tickformat=",d", secondary_y=True)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("##### 💻 사용한 SQL")
    st.code(query4, language="sql")
    st.markdown("##### 💡 데이터 인사이트")
    st.info("""
    * 독거노인 수가 많은 구라고 해서 반드시 복지시설 수가 많은 것은 아님이 확인됩니다.
    * 특정 자치구는 돌봄 수요(독거노인)에 비해 인프라(시설)가 부족한 '복지 불균형' 상태를 보입니다.
    * 시설 확충 시 단순히 인구수가 아닌, 독거노인 밀집도를 고려한 자원 배분이 시급합니다.
    """)

# 하단 출처 표기
st.caption("데이터 출처: 서울 열린데이터 광장")
