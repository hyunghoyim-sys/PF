import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Integrated Investment Master Model",
    page_icon="📈",
    layout="wide"
)

# --- 유틸리티 함수 ---
def format_currency(value):
    return f"₩{int(value):,}"

# --- 사이드바: 입력 패널 ---
st.sidebar.header("🎛️ Market Context Simulator")
st.sidebar.markdown("현재 시장 상황을 입력하세요.")

# 1. 자본금 설정
total_capital = st.sidebar.number_input(
    "총 운용 자산 (원)", 
    min_value=1000000, 
    value=100000000, 
    step=1000000,
    format="%d"
)

st.sidebar.markdown("---")

# 2. Track A: 단기 전술 입력
st.sidebar.subheader("⚡ Track A: 단기 전술 (LW)")
lw_strength = st.sidebar.slider(
    "변동성 돌파 강도 (LW Strength)", 
    min_value=0, max_value=100, value=50,
    help="0(추세 붕괴) ~ 100(강력 돌파). 래리 윌리엄스 변동성 돌파 전략 기반."
)

st.sidebar.markdown("---")

# 3. Track B: 중기 전략 입력
st.sidebar.subheader("🎯 Track B: 중기 전략 (Contrarian)")
sentiment_index = st.sidebar.slider(
    "대중 심리 (Fear & Greed)", 
    min_value=0, max_value=100, value=50,
    help="0(극도의 공포) ~ 100(극도의 탐욕). 시장 참여자들의 심리 지표."
)
analyst_consensus = st.sidebar.slider(
    "애널리스트 컨센서스", 
    min_value=1, max_value=5, value=3,
    help="1(매도) ~ 5(강력 매수). 전문가들의 의견 종합."
)

# --- 메인 헤더 ---
st.title("📈 Integrated Investment Master Model (v2.5)")
st.markdown("""
**철학적 엔진(Engine)과 실전 시뮬레이션(Simulation)의 결합** 이 모델은 **단기 전술(20%)**과 **중기 전략(80%)**을 분리하여 운용하며, 
소로스, 하워드 막스, 래리 윌리엄스의 투자 철학을 기반으로 자산 배분 신호를 생성합니다.
""")

st.divider()

# --- 데이터베이스 및 로직 ---

# 1. 종목 DB
core_stocks = [
    {'name': '테슬라 (TSLA)', 'weight': 0.30, 'type': 'Strategic (Core)', 'rationale': '[Body] 유일한 양산형 휴머노이드 & AI 자율주행 데이터 독점. 로봇 시대의 애플.'},
    {'name': '엔비디아 (NVDA)', 'weight': 0.15, 'type': 'Strategic (Core)', 'rationale': '[Brain] Physical AI를 위한 시뮬레이션(Isaac)과 두뇌(GPU) 독점. 대체 불가능한 인프라.'},
    {'name': '팔란티어 (PLTR)', 'weight': 0.15, 'type': 'Strategic (Core)', 'rationale': '[OS] 국방/산업 현장의 엣지 AI 운영체제. 하드웨어와 소프트웨어를 연결하는 신경망.'},
    {'name': '버티브 (VRT)', 'weight': 0.10, 'type': 'Strategic (Core)', 'rationale': '[Power] AI 학습/운용을 위한 데이터센터 전력 및 액체 냉각 대장주.'},
    {'name': '비트코인 (BTC)', 'weight': 0.10, 'type': 'Strategic (Core)', 'rationale': '[Hedge] 중앙화된 화폐 시스템 붕괴 및 유동성 확장에 대한 헷지(Digital Gold).'},
    {'name': 'LS ELECTRIC', 'weight': 0.05, 'type': 'Strategic (Core)', 'rationale': '[Infra] 북미 AI 데이터센터향 초고압 변압기 수요 폭증 수혜. 한국 전력 기기 대장주.'},
    {'name': '레인보우로보틱스', 'weight': 0.05, 'type': 'Strategic (Core)', 'rationale': '[Robot] 삼성전자가 선택한 휴머노이드 기술력. 이족보행 플랫폼 및 핵심 부품 내재화.'},
    {'name': 'ASTS (Space)', 'weight': 0.05, 'type': 'Strategic (Core)', 'rationale': '[Net] 전 세계 어디서나 로봇이 연결되는 우주 통신망. 스페이스X의 통신 대안.'},
]

strategic_ratio = 0.8
tactical_ratio = 0.2

# 2. 로직: 단기 전술 (Track A)
def run_tactical_sim(strength):
    equity_ratio = 0.0
    signal = ""
    status_color = "inverse" # default

    if strength >= 80:
        equity_ratio = 1.0
        signal = "🚀 강력 돌파 (Strong Breakout)"
        status_color = "red"
    elif strength >= 60:
        equity_ratio = 0.6
        signal = "📈 추세 추종 (Trend Following)"
        status_color = "orange"
    elif strength <= 20:
        equity_ratio = 0.0
        signal = "🛡️ 추세 붕괴 (Stop Loss)"
        status_color = "blue"
    else:
        equity_ratio = 0.2
        signal = "👀 관망/탐색 (Watching)"
        status_color = "gray"
    
    allocated = total_capital * tactical_ratio
    stock_amt = allocated * equity_ratio
    cash_amt = allocated * (1 - equity_ratio)
    
    return stock_amt, cash_amt, signal, status_color

# 3. 로직: 중기 전략 (Track B)
def run_strategic_sim(sent, ana):
    analyst_score = (ana - 1) * 25
    risk_score = (sent * 0.7) + (analyst_score * 0.3)
    
    target_cash_ratio = 0.05
    stance = ""
    status_color = "inverse"

    if risk_score >= 80:
        target_cash_ratio = 0.30
        stance = "🚨 과열 경보 (Reduce)"
        status_color = "red"
    elif risk_score >= 60:
        target_cash_ratio = 0.15
        stance = "⚠️ 경계 구간 (Hold)"
        status_color = "orange"
    elif risk_score <= 20:
        target_cash_ratio = 0.0
        stance = "💎 바닥 줍줍 (Strong Buy)"
        status_color = "blue"
    else:
        target_cash_ratio = 0.05
        stance = "⚖️ 균형 유지 (Neutral)"
        status_color = "gray"
        
    allocated = total_capital * strategic_ratio
    cash_amt = allocated * target_cash_ratio
    stock_amt = allocated - cash_amt
    
    return stock_amt, cash_amt, stance, status_color, risk_score

# 시뮬레이션 실행
tac_stock, tac_cash, tac_signal, tac_color = run_tactical_sim(lw_strength)
str_stock, str_cash, str_stance, str_color, risk_score = run_strategic_sim(sentiment_index, analyst_consensus)

# --- 화면 구성: 결과 패널 ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Track A: 단기 전술 (20%)")
    st.caption("Engine: 래리 윌리엄스 (변동성 돌파)")
    
    # 카드 스타일
    if tac_color == "red":
        st.error(f"**Signal:** {tac_signal}")
    elif tac_color == "orange":
        st.warning(f"**Signal:** {tac_signal}")
    elif tac_color == "blue":
        st.info(f"**Signal:** {tac_signal}")
    else:
        st.secondary_background_message = f"**Signal:** {tac_signal}" # Custom handled roughly
        st.success(f"**Signal:** {tac_signal}")

    t_col1, t_col2 = st.columns(2)
    t_col1.metric("공격 자산 (TQQQ 등)", format_currency(tac_stock))
    t_col2.metric("방어 자산 (현금)", format_currency(tac_cash))

with col2:
    st.subheader("🎯 Track B: 중기 전략 (80%)")
    st.caption("Engine: 소로스 & 하워드 막스 (역발상)")
    
    if str_color == "red":
        st.error(f"**Stance:** {str_stance}")
    elif str_color == "orange":
        st.warning(f"**Stance:** {str_stance}")
    elif str_color == "blue":
        st.info(f"**Stance:** {str_stance}")
    else:
        st.success(f"**Stance:** {str_stance}")
        
    s_col1, s_col2 = st.columns(2)
    s_col1.metric("핵심 자산 (Core)", format_currency(str_stock))
    s_col2.metric("현금 비중 목표", f"{int((str_cash / (total_capital * strategic_ratio)) * 100)}%")


st.divider()

# --- 통합 포트폴리오 데이터 생성 ---
final_portfolio = []

# Core Stocks
for stock in core_stocks:
    # 전략적 주식 금액 * (개별 종목 비중 / 0.95 보정)
    amt = (str_stock * stock['weight']) / 0.95
    final_portfolio.append({
        '종목명': stock['name'],
        '금액': amt,
        '비중(%)': (amt / total_capital) * 100,
        '유형': stock['type'],
        '투자 근거 (Rationale)': stock['rationale']
    })

# Tactical Stock
if tac_stock > 0:
    final_portfolio.append({
        '종목명': '단기 트레이딩 (TQQQ 등)',
        '금액': tac_stock,
        '비중(%)': (tac_stock / total_capital) * 100,
        '유형': 'Tactical (Swing)',
        '투자 근거 (Rationale)': '[Momentum] 단기 변동성 돌파 전략 실행을 위한 레버리지 ETF 운용.'
    })

# Total Cash
total_cash_final = tac_cash + str_cash
final_portfolio.append({
    '종목명': '통합 현금 (Cash)',
    '금액': total_cash_final,
    '비중(%)': (total_cash_final / total_capital) * 100,
    '유형': 'Cash Buffer',
    '투자 근거 (Rationale)': '[Option] 폭락장 및 새로운 기회를 위한 현금성 자산 (CMA/파킹통장).'
})

df = pd.DataFrame(final_portfolio)
df = df.sort_values(by='금액', ascending=False)

# --- 시각화 ---
st.subheader("📊 최종 통합 포트폴리오 시뮬레이션")

tab1, tab2, tab3 = st.tabs(["포트폴리오 차트", "투자 철학 (Engine)", "상세 체크리스트"])

with tab1:
    # Plotly Bar Chart
    fig = px.bar(
        df, 
        x='비중(%)', 
        y='종목명', 
        orientation='h',
        text='금액',
        color='유형',
        color_discrete_map={
            'Strategic (Core)': '#8884d8',
            'Tactical (Swing)': '#ff6b6b',
            'Cash Buffer': '#2563eb'
        }
    )
    fig.update_traces(texttemplate='%{text:,.0f}원', textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 🏛️ Investment Philosophy Engine")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info("**📈 조지 소로스 (재귀성 이론)**\n\n'가격이 펀더멘털을 왜곡한다.' 대중의 편향이 극에 달해 추세가 반전되는 지점을 포착합니다.")
        st.warning("**⚓ 워런 버핏 (안전마진 & 해자)**\n\n'이유(Rationale)를 모르면 사지 마라.' 10년 뒤에도 존재할 기업의 본질가치에 집중합니다.")
    with col_p2:
        st.info("**📖 하워드 막스 (2차적 사고)**\n\n'남들이 좋다고 할 때 팔고, 공포에 떨 때 사는 역발상.' 시장 심리 지수를 역이용합니다.")
        st.error("**⚡ 래리 윌리엄스 (변동성 돌파)**\n\n'가격 움직임이 곧 확신이다.' 추상적 심리를 넘어선 객관적 진입 타이밍을 잡습니다.")

with tab3:
    st.markdown("### 📌 Rationale Checklist")
    st.dataframe(
        df[['종목명', '유형', '비중(%)', '투자 근거 (Rationale)']].style.format({'비중(%)': '{:.1f}%'}),
        use_container_width=True,
        height=400
    )