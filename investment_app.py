import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Integrated Investment Master Model",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일 커스터마이징 (CSS) ---
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif !important;
            color: #333333;
        }
        .stApp { background-color: #F8F9FA; }
        .main .block-container { padding-top: 2rem; max-width: 1200px; }
        
        h1 { font-family: 'Merriweather', serif !important; color: #1E3A8A !important; }
        h2, h3 { color: #1F2937 !important; }

        .report-card {
            background-color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid #E5E7EB;
            margin-bottom: 20px;
        }
        
        /* 부동산 전용 스타일 */
        .re-card {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .re-card h3 { color: white !important; }
        .re-card p { color: #E0E7FF !important; }
        
        .signal-box {
            padding: 15px; border-radius: 8px; font-weight: 600; margin-bottom: 15px;
            display: flex; align-items: center; justify-content: space-between;
        }
    </style>
""", unsafe_allow_html=True)

def format_currency(value):
    return f"₩{int(value):,}"

# --- 사이드바 ---
with st.sidebar:
    st.header("🎛️ 시뮬레이션 설정")
    
    st.markdown("### 1. 금융 자산 설정")
    financial_capital = st.number_input("금융 운용 자산 (원)", min_value=0, value=100000000, step=1000000, format="%d")

    st.markdown("### 2. 부동산 자산 설정")
    real_estate_value = st.number_input("부동산 현재 시세 (원)", min_value=0, value=550000000, step=10000000, format="%d", help="가락동 유진빌리지 추정 시세")
    
    st.markdown("---")
    
    st.markdown("### 3. 모델 변수")
    lw_strength = st.slider("LW 변동성 돌파 강도", 0, 100, 50)
    sentiment_index = st.slider("대중 심리 (Fear/Greed)", 0, 100, 50)
    analyst_consensus = st.slider("애널리스트 컨센서스", 1, 5, 3)

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
    bg = "#F3F4F6"
    text = "#374151"

    if strength >= 80:
        equity_ratio = 1.0; signal = "🚀 강력 돌파"; bg = "#FEF2F2"; text = "#DC2626"
    elif strength >= 60:
        equity_ratio = 0.6; signal = "📈 추세 추종"; bg = "#FFF7ED"; text = "#EA580C"
    elif strength <= 20:
        equity_ratio = 0.0; signal = "🛡️ 추세 붕괴"; bg = "#EFF6FF"; text = "#2563EB"
    else:
        equity_ratio = 0.2; signal = "👀 관망/탐색"; bg = "#F3F4F6"; text = "#4B5563"
    
    alloc = financial_capital * tactical_ratio
    return alloc * equity_ratio, alloc * (1 - equity_ratio), signal, bg, text

# 중기 전략 로직
def run_strategic_sim(sent, ana):
    risk_score = (sent * 0.7) + ((ana - 1) * 25 * 0.3)
    target_cash = 0.05
    stance = ""
    bg = "#F3F4F6"
    text = "#374151"

    if risk_score >= 80:
        target_cash = 0.30; stance = "🚨 과열 (Reduce)"; bg = "#FEF2F2"; text = "#DC2626"
    elif risk_score >= 60:
        target_cash = 0.15; stance = "⚠️ 경계 (Hold)"; bg = "#FFF7ED"; text = "#EA580C"
    elif risk_score <= 20:
        target_cash = 0.0; stance = "💎 바닥 (Buy)"; bg = "#EFF6FF"; text = "#2563EB"
    else:
        target_cash = 0.05; stance = "⚖️ 균형 (Neutral)"; bg = "#F3F4F6"; text = "#4B5563"
        
    alloc = financial_capital * strategic_ratio
    cash = alloc * target_cash
    stock = alloc - cash
    return stock, cash, stance, bg, text

tac_stock, tac_cash, tac_sig, tac_bg, tac_txt = run_tactical_sim(lw_strength)
str_stock, str_cash, str_sta, str_bg, str_txt = run_strategic_sim(sentiment_index, analyst_consensus)

# --- 메인 화면 ---
st.markdown("""
<div style='text-align: left; margin-bottom: 20px;'>
    <h1 style='margin-bottom: 0;'>My Asset & Investment Model</h1>
    <p style='color: #6B7280;'>Financial Portfolio + Real Estate (Garak-dong Project)</p>
</div>
""", unsafe_allow_html=True)

# 탭 구성: 전체 요약 / 금융 포트폴리오 / 부동산 분석
tab_main1, tab_main2, tab_main3 = st.tabs(["📊 자산 현황 요약", "💸 금융 포트폴리오", "apt 부동산 (유진빌리지)"])

with tab_main1:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    
    total_asset = financial_capital + real_estate_value
    c1, c2, c3 = st.columns(3)
    c1.metric("총 자산 (Total)", format_currency(total_asset), delta="Estimated")
    c2.metric("부동산 (Real Estate)", format_currency(real_estate_value), "57% (비중)")
    c3.metric("금융 자산 (Financial)", format_currency(financial_capital), "43% (비중)")
    
    # 도넛 차트
    fig_donut = px.pie(
        names=['부동산 (유진빌리지)', '금융 자산'],
        values=[real_estate_value, financial_capital],
        hole=0.6,
        color_discrete_sequence=['#1e3a8a', '#3b82f6']
    )
    fig_donut.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab_main2:
    # (기존 금융 모델 UI)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='report-card'><h4 style='color:{tac_txt}'>⚡ 단기 전술: {tac_sig}</h4></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='report-card'><h4 style='color:{str_txt}'>🎯 중기 전략: {str_sta}</h4></div>", unsafe_allow_html=True)
    
    # 통합 포트폴리오 표 생성
    final_pf = []
    for s in core_stocks:
        amt = (str_stock * s['weight']) / 0.95
        final_pf.append({'종목': s['name'], '금액': amt, '유형': s['type']})
    if tac_stock > 0: final_pf.append({'종목': '단기 ETF (TQQQ)', '금액': tac_stock, '유형': 'Tactical'})
    final_pf.append({'종목': '현금 (Cash)', '금액': tac_cash + str_cash, '유형': 'Buffer'})
    
    df_pf = pd.DataFrame(final_pf).sort_values('금액', ascending=False)
    
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    fig_bar = px.bar(df_pf, x='금액', y='종목', orientation='h', text='금액', color='유형')
    fig_bar.update_traces(texttemplate='%{text:,.0f}원')
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab_main3:
    # 부동산 분석 탭
    st.markdown("""
    <div class='re-card'>
        <h3>🏢 송파구 가락동 유진빌리지 (약 20평)</h3>
        <p style='font-size: 1.1em;'><strong>"송파 ICT 보안 클러스터(중앙전파관리소 개발)의 1열 직관 수혜지"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col_re1, col_re2 = st.columns([1, 1])
    
    with col_re1:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.markdown("#### 🏗️ 핵심 호재: 송파 ICT 보안 클러스터")
        st.info("""
        **1. 사업 개요**
        - **위치:** 중앙전파관리소 부지 (가락동 100번지) - **도보 2분 거리**
        - **규모:** 5,500억 원 투입, 연면적 5만 평 (사이버 보안 판교)
        - **일정:** 1단계(2026 착공) -> 2단계(2027 착공) -> **2030년 완공**
        
        **2. 기대 효과**
        - 국정원, KISA 등 8개 보안 기관 입주
        - 고소득 보안 인력 수천 명 상주 → **직주근접 전월세 수요 폭발**
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_re2:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.markdown("#### 📈 미래 가치 시뮬레이션 (단위: 억 원)")
        
        # 가치 상승 차트 데이터
        years = ['현재(2025)', '3년후(착공)', '5년후(완공)', '10년후(성숙)']
        values = [real_estate_value/100000000, real_estate_value*1.2/100000000, real_estate_value*1.4/100000000, real_estate_value*1.8/100000000]
        
        fig_re = go.Figure()
        fig_re.add_trace(go.Scatter(x=years, y=values, mode='lines+markers+text', 
                                    text=[f"{v:.1f}억" for v in values], textposition="top center",
                                    line=dict(color='#3b82f6', width=4), marker=dict(size=10)))
        fig_re.update_layout(title="예상 시세 추이", template="plotly_white", yaxis_title="금액 (억)", showlegend=False)
        st.plotly_chart(fig_re, use_container_width=True)
        
        st.caption("* 10년 후는 주변 재개발(모아타운 등) 압력에 따른 프리미엄 반영 가정")
        st.markdown("</div>", unsafe_allow_html=True)