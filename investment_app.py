import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Integrated Investment Master Model",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일 커스터마이징 (CSS) ---
# 컨셉: Professional Financial Report (깔끔한 화이트/네이비 톤)
st.markdown("""
    <style>
        /* 1. 폰트 설정: Pretendard (본문), Merriweather (헤더 포인트) */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif !important;
            color: #333333;
        }

        /* 2. 배경 및 컨테이너 스타일 */
        .stApp {
            background-color: #F8F9FA; /* 아주 연한 회색 배경 */
        }
        
        /* 메인 컨텐츠 영역 패딩 조정 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 1200px;
        }

        /* 3. 헤더 스타일링 */
        h1 {
            font-family: 'Merriweather', serif !important;
            color: #1E3A8A !important; /* 진한 네이비 */
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        h2, h3 {
            font-family: 'Pretendard', sans-serif !important;
            color: #1F2937 !important; /* 다크 그레이 */
            font-weight: 700 !important;
        }

        /* 4. 카드(컨테이너) 디자인 - 그림자 효과로 입체감 부여 */
        .report-card {
            background-color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
            border: 1px solid #E5E7EB;
            margin-bottom: 20px;
        }

        /* 5. 메트릭(숫자) 스타일 */
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #6B7280 !important;
            font-weight: 500;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Merriweather', serif !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }

        /* 6. 반응형 테이블 스타일 */
        [data-testid="stDataFrame"] {
            width: 100%;
        }
        
        /* 7. 사이드바 스타일 */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E5E7EB;
        }
        
        /* 구분선 */
        hr {
            margin: 30px 0;
            border-color: #E5E7EB;
        }
        
        /* 사용자 정의 박스 (신호등) */
        .signal-box {
            padding: 15px;
            border-radius: 8px;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
    </style>
""", unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def format_currency(value):
    return f"₩{int(value):,}"

# --- 사이드바: 입력 패널 ---
with st.sidebar:
    st.header("🎛️ 시뮬레이션 설정")
    st.caption("시장 상황 및 자본금을 설정하여 시뮬레이션을 실행하세요.")
    
    st.markdown("### 1. 기본 설정")
    total_capital = st.number_input(
        "총 운용 자산 (원)", 
        min_value=1000000, 
        value=100000000, 
        step=1000000,
        format="%d"
    )

    st.markdown("---")
    
    st.markdown("### 2. 단기 전술 (Track A)")
    lw_strength = st.slider(
        "LW 변동성 돌파 강도", 
        min_value=0, max_value=100, value=50,
        help="래리 윌리엄스 전략: 0(추세 붕괴) ~ 100(강력 돌파)"
    )
    
    st.markdown("---")
    
    st.markdown("### 3. 중기 전략 (Track B)")
    sentiment_index = st.slider(
        "대중 심리 지수 (Fear & Greed)", 
        min_value=0, max_value=100, value=50,
        help="0(극도의 공포) ~ 100(극도의 탐욕)"
    )
    analyst_consensus = st.slider(
        "애널리스트 컨센서스", 
        min_value=1, max_value=5, value=3,
        help="1(매도) ~ 5(강력 매수)"
    )
    
    st.info("💡 **Tip:** 왼쪽 패널 값을 조정하면 오른쪽 리포트가 실시간으로 변경됩니다.")

# --- 로직 함수들 (기존과 동일) ---
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
    status_bg = "#F3F4F6" # default gray
    status_text = "#374151"

    if strength >= 80:
        equity_ratio = 1.0
        signal = "🚀 강력 돌파 (Strong Breakout)"
        status_bg = "#FEF2F2" # Red light
        status_text = "#DC2626"
    elif strength >= 60:
        equity_ratio = 0.6
        signal = "📈 추세 추종 (Trend Following)"
        status_bg = "#FFF7ED" # Orange light
        status_text = "#EA580C"
    elif strength <= 20:
        equity_ratio = 0.0
        signal = "🛡️ 추세 붕괴 (Stop Loss)"
        status_bg = "#EFF6FF" # Blue light
        status_text = "#2563EB"
    else:
        equity_ratio = 0.2
        signal = "👀 관망/탐색 (Watching)"
        status_bg = "#F3F4F6"
        status_text = "#4B5563"
    
    allocated = total_capital * tactical_ratio
    stock_amt = allocated * equity_ratio
    cash_amt = allocated * (1 - equity_ratio)
    
    return stock_amt, cash_amt, signal, status_bg, status_text

# 3. 로직: 중기 전략 (Track B)
def run_strategic_sim(sent, ana):
    analyst_score = (ana - 1) * 25
    risk_score = (sent * 0.7) + (analyst_score * 0.3)
    
    target_cash_ratio = 0.05
    stance = ""
    status_bg = "#F3F4F6"
    status_text = "#374151"

    if risk_score >= 80:
        target_cash_ratio = 0.30
        stance = "🚨 과열 경보 (Reduce)"
        status_bg = "#FEF2F2" # Red light
        status_text = "#DC2626"
    elif risk_score >= 60:
        target_cash_ratio = 0.15
        stance = "⚠️ 경계 구간 (Hold)"
        status_bg = "#FFF7ED" # Orange light
        status_text = "#EA580C"
    elif risk_score <= 20:
        target_cash_ratio = 0.0
        stance = "💎 바닥 줍줍 (Strong Buy)"
        status_bg = "#EFF6FF" # Blue light
        status_text = "#2563EB"
    else:
        target_cash_ratio = 0.05
        stance = "⚖️ 균형 유지 (Neutral)"
        status_bg = "#F3F4F6"
        status_text = "#4B5563"
        
    allocated = total_capital * strategic_ratio
    cash_amt = allocated * target_cash_ratio
    stock_amt = allocated - cash_amt
    
    return stock_amt, cash_amt, stance, status_bg, status_text, risk_score

# 시뮬레이션 실행
tac_stock, tac_cash, tac_signal, tac_bg, tac_text = run_tactical_sim(lw_strength)
str_stock, str_cash, str_stance, str_bg, str_text, risk_score = run_strategic_sim(sentiment_index, analyst_consensus)

# --- 메인 컨텐츠 ---

# 타이틀 섹션
st.markdown("""
<div style='text-align: left; padding-bottom: 20px;'>
    <h1 style='margin-bottom: 0;'>Investment Master Model <span style='font-size: 0.5em; color: #6B7280; vertical-align: middle;'>v2.5</span></h1>
    <p style='font-size: 1.1em; color: #4B5563; margin-top: 10px;'>
        <b>철학적 엔진(Philosophy)</b>과 <b>실전 시뮬레이션(Simulation)</b>의 결합<br>
        소로스(재귀성), 하워드 막스(2차적 사고), 래리 윌리엄스(변동성) 이론을 통합한 자동 자산 배분 모델
    </p>
</div>
""", unsafe_allow_html=True)

# 2열 레이아웃 (반응형: Streamlit 컬럼은 화면이 작아지면 자동으로 스택됨)
col1, col2 = st.columns(2, gap="large")

with col1:
    # 카드형 디자인 적용 (HTML/CSS)
    st.markdown("""<div class='report-card'>""", unsafe_allow_html=True)
    
    st.subheader("⚡ Track A: 단기 전술 (20%)")
    st.caption("Engine: 래리 윌리엄스 (변동성 돌파)")
    
    # 신호 박스
    st.markdown(f"""
        <div class='signal-box' style='background-color: {tac_bg}; color: {tac_text}; border: 1px solid {tac_text}30;'>
            <span>SIGNAL</span>
            <span>{tac_signal}</span>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.metric("공격 자산 (ETF)", format_currency(tac_stock))
    with c2: st.metric("현금 (Buffer)", format_currency(tac_cash))
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""<div class='report-card'>""", unsafe_allow_html=True)
    
    st.subheader("🎯 Track B: 중기 전략 (80%)")
    st.caption("Engine: 소로스 & 하워드 막스 (역발상)")
    
    st.markdown(f"""
        <div class='signal-box' style='background-color: {str_bg}; color: {str_text}; border: 1px solid {str_text}30;'>
            <span>STANCE</span>
            <span>{str_stance}</span>
        </div>
    """, unsafe_allow_html=True)
        
    c1, c2 = st.columns(2)
    with c1: st.metric("핵심 자산 (Core)", format_currency(str_stock))
    with c2: st.metric("현금 비중 목표", f"{int((str_cash / (total_capital * strategic_ratio)) * 100)}%")
    
    st.markdown("</div>", unsafe_allow_html=True)


# --- 통합 포트폴리오 데이터 생성 ---
final_portfolio = []

# Core Stocks
for stock in core_stocks:
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
    '투자 근거 (Rationale)': '[Option] 폭락장 및 새로운 기회를 위한 현금성 자산.'
})

df = pd.DataFrame(final_portfolio)
df = df.sort_values(by='금액', ascending=False)

# --- 하단 탭 섹션 ---
st.markdown("### 📊 Portfolio Analysis Report")

tab1, tab2, tab3 = st.tabs(["포트폴리오 구성", "투자 철학 (Engine)", "상세 체크리스트"])

with tab1:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    # Plotly Chart (Clean White Theme)
    fig = px.bar(
        df, 
        x='비중(%)', 
        y='종목명', 
        orientation='h',
        text='금액',
        color='유형',
        color_discrete_map={
            'Strategic (Core)': '#6366F1',  # Indigo
            'Tactical (Swing)': '#EF4444',  # Red
            'Cash Buffer': '#3B82F6'        # Blue
        },
        height=500
    )
    
    fig.update_traces(
        texttemplate='%{text:,.0f}원', 
        textposition='outside',
        cliponaxis=False
    )
    fig.update_layout(
        template='plotly_white', # 깔끔한 화이트 테마
        yaxis={'categoryorder':'total ascending', 'title': None},
        xaxis={'title': '비중 (%)'},
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("""
        #### 📈 조지 소로스 (재귀성)
        > *"가격이 펀더멘털을 왜곡한다."*
        
        대중의 편향이 극에 달해 추세가 반전되는 지점을 포착하여 역으로 행동합니다.
        """)
        st.markdown("---")
        st.markdown("""
        #### ⚓ 워런 버핏 (해자)
        > *"이유(Rationale)를 모르면 사지 마라."*
        
        10년 뒤에도 존재할 기업의 본질가치(독점력)에 집중하여 흔들리지 않습니다.
        """)
    with col_p2:
        st.markdown("""
        #### 📖 하워드 막스 (2차적 사고)
        > *"남들이 공포에 떨 때 사는 역발상."*
        
        단순한 1차원적 예측(뉴스)을 넘어 시장 참여자의 심리 지수를 역이용합니다.
        """)
        st.markdown("---")
        st.markdown("""
        #### ⚡ 래리 윌리엄스 (변동성)
        > *"가격 움직임이 곧 확신이다."*
        
        추상적 심리를 넘어선 객관적 진입 타이밍(돌파 매매)을 잡아냅니다.
        """)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    # Streamlit dataframe with better formatting
    st.dataframe(
        df[['종목명', '유형', '비중(%)', '금액', '투자 근거 (Rationale)']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "금액": st.column_config.NumberColumn(format="₩%d"),
            "비중(%)": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
            "투자 근거 (Rationale)": st.column_config.TextColumn(width="large")
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)