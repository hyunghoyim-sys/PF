import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Investment Master Model (Black & Orange)",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일 커스터마이징 (CSS: Black & Orange Theme) ---
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        /* 1. 기본 폰트 및 배경 설정 */
        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif !important;
            color: #E0E0E0;
        }
        
        /* 전체 배경: 완전한 블랙에 가까운 다크 그레이 */
        .stApp {
            background-color: #050505;
        }
        
        /* 2. 헤더 및 텍스트 컬러 (주황색 포인트) */
        h1, h2, h3 {
            color: #FF9F1C !important; /* Vivid Orange */
            font-weight: 700 !important;
        }
        h4, h5, h6 {
            color: #FFBF69 !important; /* Light Orange */
        }
        p, li, label, .stMarkdown {
            color: #CCCCCC !important;
        }
        
        /* 3. 사이드바 스타일 */
        [data-testid="stSidebar"] {
            background-color: #111111;
            border-right: 1px solid #333;
        }
        
        /* 4. 메트릭(숫자) 스타일 */
        [data-testid="stMetricLabel"] {
            color: #888888 !important;
        }
        [data-testid="stMetricValue"] {
            color: #FF9F1C !important; /* 주황색 숫자 */
            font-family: 'Pretendard', monospace !important;
        }
        
        /* 5. 카드 컨테이너 스타일 */
        .dark-card {
            background-color: #161616;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
        }
        
        /* 6. 신호 박스 스타일 */
        .signal-box {
            background-color: #222;
            border-left: 5px solid #FF9F1C;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        
        /* 7. 부동산 카드 스타일 */
        .re-card {
            background: linear-gradient(135deg, #FF6B35 0%, #F7C59F 100%);
            color: #111 !important;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .re-card h3 { color: #000 !important; }
        .re-card p { color: #222 !important; }
        
        /* 구분선 */
        hr { border-color: #333; }
    </style>
""", unsafe_allow_html=True)

def format_currency(value):
    return f"₩{int(value):,}"

# --- 사이드바 ---
with st.sidebar:
    st.header("🎛️ 시뮬레이션 설정")
    
    st.markdown("### 1. 금융 자산 설정")
    financial_capital = st.number_input("금융 운용 자산 (원)", min_value=0, value=100000000, step=1000000, format="%d")
    
    st.markdown("---")
    
    st.markdown("### 2. 모델 변수")
    lw_strength = st.slider("LW 변동성 돌파 강도", 0, 100, 50)
    sentiment_index = st.slider("대중 심리 (Fear/Greed)", 0, 100, 50)
    analyst_consensus = st.slider("애널리스트 컨센서스", 1, 5, 3)

    st.markdown("---")
    st.markdown("### 3. 부동산 설정 (별도 분석용)")
    real_estate_value = st.number_input("부동산 현재 시세 (원)", min_value=0, value=550000000, step=10000000, format="%d")


# --- 로직: 금융 포트폴리오 ---
core_stocks = [
    {'name': '테슬라 (TSLA)', 'weight': 0.30, 'type': 'Strategic (Core)', 'rationale': '[Body] 유일한 양산형 휴머노이드 & AI 자율주행 데이터 독점.'},
    {'name': '엔비디아 (NVDA)', 'weight': 0.15, 'type': 'Strategic (Core)', 'rationale': '[Brain] Physical AI를 위한 시뮬레이션(Isaac)과 두뇌(GPU) 독점.'},
    {'name': '팔란티어 (PLTR)', 'weight': 0.15, 'type': 'Strategic (Core)', 'rationale': '[OS] 국방/산업 현장의 엣지 AI 운영체제.'},
    {'name': '버티브 (VRT)', 'weight': 0.10, 'type': 'Strategic (Core)', 'rationale': '[Power] AI 데이터센터 전력 및 액체 냉각 대장주.'},
    {'name': '비트코인 (BTC)', 'weight': 0.10, 'type': 'Strategic (Core)', 'rationale': '[Hedge] 유동성 확장 및 화폐 시스템 붕괴 헷지.'},
    {'name': 'LS ELECTRIC', 'weight': 0.05, 'type': 'Strategic (Core)', 'rationale': '[Infra] 북미 초고압 변압기 수요 폭증 수혜.'},
    {'name': '레인보우로보틱스', 'weight': 0.05, 'type': 'Strategic (Core)', 'rationale': '[Robot] 삼성전자가 선택한 휴머노이드 플랫폼.'},
    {'name': 'ASTS (Space)', 'weight': 0.05, 'type': 'Strategic (Core)', 'rationale': '[Net] 우주 통신망. 스페이스X의 통신 대안.'},
]

strategic_ratio = 0.8
tactical_ratio = 0.2

# 단기 전술 로직
def run_tactical_sim(strength):
    equity_ratio = 0.0
    signal = ""
    # 다크 모드용 텍스트 컬러 (주황 계열 위주)
    signal_color = "#AAAAAA"

    if strength >= 80:
        equity_ratio = 1.0; signal = "🚀 강력 돌파 (Strong Breakout)"; signal_color = "#FF4B4B" # Red-ish Orange
    elif strength >= 60:
        equity_ratio = 0.6; signal = "📈 추세 추종 (Trend Following)"; signal_color = "#FFA500" # Orange
    elif strength <= 20:
        equity_ratio = 0.0; signal = "🛡️ 추세 붕괴 (Stop Loss)"; signal_color = "#00BFFF" # Blue (대비색)
    else:
        equity_ratio = 0.2; signal = "👀 관망/탐색 (Watching)"; signal_color = "#888888"
    
    alloc = financial_capital * tactical_ratio
    return alloc * equity_ratio, alloc * (1 - equity_ratio), signal, signal_color

# 중기 전략 로직
def run_strategic_sim(sent, ana):
    risk_score = (sent * 0.7) + ((ana - 1) * 25 * 0.3)
    target_cash = 0.05
    stance = ""
    stance_color = "#AAAAAA"

    if risk_score >= 80:
        target_cash = 0.30; stance = "🚨 과열 (Reduce)"; stance_color = "#FF4B4B"
    elif risk_score >= 60:
        target_cash = 0.15; stance = "⚠️ 경계 (Hold)"; stance_color = "#FFA500"
    elif risk_score <= 20:
        target_cash = 0.0; stance = "💎 바닥 (Buy)"; stance_color = "#00BFFF"
    else:
        target_cash = 0.05; stance = "⚖️ 균형 (Neutral)"; stance_color = "#888888"
        
    alloc = financial_capital * strategic_ratio
    cash = alloc * target_cash
    stock = alloc - cash
    return stock, cash, stance, stance_color

tac_stock, tac_cash, tac_sig, tac_col = run_tactical_sim(lw_strength)
str_stock, str_cash, str_sta, str_col = run_strategic_sim(sentiment_index, analyst_consensus)

# --- 메인 화면 ---
st.title("Investment Master Model")
st.markdown("**Financial Portfolio Strategy & Real Estate Analysis**")

# 금융 포트폴리오 로직 계산
final_pf = []
for s in core_stocks:
    amt = (str_stock * s['weight']) / 0.95
    final_pf.append({'종목': s['name'], '금액': amt, '유형': s['type'], 'Rationale': s['rationale']})

if tac_stock > 0: 
    final_pf.append({'종목': '단기 트레이딩 (TQQQ 등)', '금액': tac_stock, '유형': 'Tactical', 'Rationale': '[Momentum] 단기 변동성 돌파'})
    
total_cash = tac_cash + str_cash
final_pf.append({'종목': '현금 (Cash Buffer)', '금액': total_cash, '유형': 'Buffer', 'Rationale': '[Option] 폭락장 대응 및 기회비용'})

df_pf = pd.DataFrame(final_pf).sort_values('금액', ascending=False)


# 탭 구성: 금융 포트폴리오 / 투자 철학 / 부동산 (별도)
tab1, tab2, tab3 = st.tabs(["💰 금융 포트폴리오", "🧠 투자 철학 (Engine)", "🏢 부동산 (별도 분석)"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Track A: 단기 전술 (20%)")
        st.markdown(f"<h3 style='color: {tac_col} !important;'>{tac_sig}</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("공격 자산", format_currency(tac_stock))
        c2.metric("현금 대기", format_currency(tac_cash))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.subheader("🎯 Track B: 중기 전략 (80%)")
        st.markdown(f"<h3 style='color: {str_col} !important;'>{str_sta}</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("핵심 자산", format_currency(str_stock))
        c2.metric("현금 비중", f"{int((str_cash / (financial_capital * strategic_ratio)) * 100)}%")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 통합 포트폴리오 시뮬레이션")
    # Plotly Bar Chart (Dark Theme)
    fig_bar = px.bar(
        df_pf, 
        x='금액', 
        y='종목', 
        orientation='h', 
        text='금액', 
        color='유형',
        color_discrete_map={
            'Strategic (Core)': '#FF9F1C', # Orange
            'Tactical': '#FF4B4B',        # Red-Orange
            'Buffer': '#2EC4B6'           # Teal (대비색)
        },
        template='plotly_dark'
    )
    fig_bar.update_traces(texttemplate='%{text:,.0f}원', textposition='outside')
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        yaxis={'categoryorder':'total ascending'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.info("**📈 조지 소로스 (재귀성)**: 가격이 펀더멘털을 왜곡한다. 쏠림 현상을 역이용하라.")
        st.warning("**⚓ 워런 버핏 (해자)**: 10년 뒤에도 살아남을 독점 기업의 본질 가치에 집중하라.")
    with c2:
        st.success("**📖 하워드 막스 (2차적 사고)**: 남들이 공포에 떨 때 사는 역발상을 가져라.")
        st.error("**⚡ 래리 윌리엄스 (변동성)**: 가격의 움직임(추세)이 곧 확신이다.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    # 부동산 별도 분석 탭
    st.markdown("""
    <div class='re-card'>
        <h3>🏢 송파구 가락동 유진빌리지 (약 20평)</h3>
        <p style='color: #111 !important;'><strong>"송파 ICT 보안 클러스터(중앙전파관리소 개발)의 1열 직관 수혜지"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col_re1, col_re2 = st.columns(2)
    
    with col_re1:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.markdown("#### 🏗️ 핵심 호재: 송파 ICT 보안 클러스터")
        st.markdown("""
        * **위치:** 중앙전파관리소 부지 (가락동 100번지)
        * **규모:** 5,500억 원 투입, 연면적 5만 평
        * **일정:** 1단계(2026 착공) -> 2단계(2027 착공) -> **2030년 완공**
        * **기대 효과:** 보안 인력 수천 명 상주 → **직주근접 수요 폭발**
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_re2:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.markdown("#### 📈 미래 가치 시뮬레이션")
        
        # 가치 상승 차트 데이터
        years = ['현재(2025)', '3년후(착공)', '5년후(완공)', '10년후(성숙)']
        values = [real_estate_value/100000000, real_estate_value*1.2/100000000, real_estate_value*1.4/100000000, real_estate_value*1.8/100000000]
        
        fig_re = go.Figure()
        fig_re.add_trace(go.Scatter(
            x=years, y=values, 
            mode='lines+markers+text', 
            text=[f"{v:.1f}억" for v in values], 
            textposition="top center",
            line=dict(color='#FF9F1C', width=4), # Orange Line
            marker=dict(size=10, color='#FFBF69')
        ))
        fig_re.update_layout(
            title="예상 시세 추이 (단위: 억)", 
            template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0'),
            showlegend=False
        )
        st.plotly_chart(fig_re, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)