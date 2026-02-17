import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Investment Master Model Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일 커스터마이징 (CSS: Dark Blue-Grey Theme) ---
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        /* 1. 기본 폰트 및 전체 배경 설정 */
        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif !important;
            color: #E2E8F0; /* 밝은 회색 텍스트 */
        }
        
        /* 전체 배경: 세련된 다크 블루/그레이 (Obsidian/Slate) */
        .stApp {
            background-color: #0F172A; /* Tailwind Slate 900 */
        }
        
        /* 2. 헤더 및 강조 텍스트 (주황/골드 포인트) */
        h1, h2, h3 {
            color: #F59E0B !important; /* Amber 500 */
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        h4, h5 {
            color: #94A3B8 !important; /* Slate 400 */
        }
        
        /* 3. 탭 스타일링 (크고 가시성 있게) */
        button[data-baseweb="tab"] {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            padding: 1rem 2rem !important;
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            color: #94A3B8 !important;
            margin-right: 8px !important;
            border-radius: 8px 8px 0 0 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #F59E0B !important;
            color: #0F172A !important;
            border-bottom: none !important;
        }
        
        /* 4. 사이드바 스타일 */
        [data-testid="stSidebar"] {
            background-color: #020617; /* Slate 950 */
            border-right: 1px solid #1E293B;
        }
        
        /* 5. 카드 컨테이너 */
        .dark-card {
            background-color: #1E293B; /* Slate 800 */
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
            margin-bottom: 24px;
        }
        
        /* 6. 부동산 카드 (강조) */
        .re-card {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid #60A5FA;
        }
        .re-card h3, .re-card p, .re-card li { color: #FFFFFF !important; }
        
        /* 7. 철학 카드 스타일 */
        .philo-card {
            background-color: #1E293B;
            border-left: 4px solid #F59E0B;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .philo-title {
            font-size: 1.1em;
            font-weight: bold;
            color: #F59E0B;
            margin-bottom: 8px;
        }
        .philo-desc {
            font-size: 0.95em;
            color: #CBD5E1;
            line-height: 1.6;
        }

        /* 구분선 */
        hr { border-color: #334155; }
        
        /* 메트릭 값 색상 */
        [data-testid="stMetricValue"] {
            color: #F59E0B !important;
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
    
    st.markdown("---")
    
    st.markdown("### 2. 모델 변수")
    lw_strength = st.slider("LW 변동성 돌파 강도", 0, 100, 50, help="단기 추세의 강도를 설정합니다.")
    sentiment_index = st.slider("대중 심리 (Fear/Greed)", 0, 100, 50, help="시장의 공포와 탐욕 수준을 설정합니다.")
    analyst_consensus = st.slider("애널리스트 컨센서스", 1, 5, 3, help="전문가들의 매수/매도 의견을 설정합니다.")

    st.markdown("---")
    st.markdown("### 3. 부동산 설정 (별도 분석용)")
    real_estate_value = st.number_input("부동산 현재 시세 (원)", min_value=0, value=550000000, step=10000000, format="%d")


# --- 로직: 금융 포트폴리오 ---
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

# 단기 전술 로직
def run_tactical_sim(strength):
    equity_ratio = 0.0
    signal = ""
    signal_color = "#94A3B8"

    if strength >= 80:
        equity_ratio = 1.0; signal = "🚀 강력 돌파 (Strong Breakout)"; signal_color = "#EF4444" 
    elif strength >= 60:
        equity_ratio = 0.6; signal = "📈 추세 추종 (Trend Following)"; signal_color = "#F97316"
    elif strength <= 20:
        equity_ratio = 0.0; signal = "🛡️ 추세 붕괴 (Stop Loss)"; signal_color = "#3B82F6" 
    else:
        equity_ratio = 0.2; signal = "👀 관망/탐색 (Watching)"; signal_color = "#94A3B8"
    
    alloc = financial_capital * tactical_ratio
    return alloc * equity_ratio, alloc * (1 - equity_ratio), signal, signal_color

# 중기 전략 로직
def run_strategic_sim(sent, ana):
    risk_score = (sent * 0.7) + ((ana - 1) * 25 * 0.3)
    target_cash = 0.05
    stance = ""
    stance_color = "#94A3B8"

    if risk_score >= 80:
        target_cash = 0.30; stance = "🚨 과열 (Reduce)"; stance_color = "#EF4444"
    elif risk_score >= 60:
        target_cash = 0.15; stance = "⚠️ 경계 (Hold)"; stance_color = "#F97316"
    elif risk_score <= 20:
        target_cash = 0.0; stance = "💎 바닥 (Buy)"; stance_color = "#3B82F6"
    else:
        target_cash = 0.05; stance = "⚖️ 균형 (Neutral)"; stance_color = "#94A3B8"
        
    alloc = financial_capital * strategic_ratio
    cash = alloc * target_cash
    stock = alloc - cash
    return stock, cash, stance, stance_color

tac_stock, tac_cash, tac_sig, tac_col = run_tactical_sim(lw_strength)
str_stock, str_cash, str_sta, str_col = run_strategic_sim(sentiment_index, analyst_consensus)

# --- 메인 화면 ---
st.title("Investment Master Model")
st.markdown("**Financial Portfolio Strategy & Real Estate Analysis**")

# 금융 포트폴리오 데이터 생성
final_pf = []
for s in core_stocks:
    amt = (str_stock * s['weight']) / 0.95
    final_pf.append({'종목': s['name'], '금액': amt, '비중': 0, '유형': s['type'], 'Rationale': s['rationale']})

if tac_stock > 0: 
    final_pf.append({'종목': '단기 트레이딩 (TQQQ 등)', '금액': tac_stock, '비중': 0, '유형': 'Tactical', 'Rationale': '[Momentum] 단기 변동성 돌파 전략 실행을 위한 레버리지 ETF 운용.'})
    
total_cash = tac_cash + str_cash
final_pf.append({'종목': '현금 (Cash Buffer)', '금액': total_cash, '비중': 0, '유형': 'Buffer', 'Rationale': '[Option] 폭락장 대응 및 새로운 기회를 위한 현금성 자산.'})

df_pf = pd.DataFrame(final_pf)
df_pf['비중'] = (df_pf['금액'] / financial_capital) * 100
df_pf = df_pf.sort_values('금액', ascending=False)


# 탭 구성 (크게 키움)
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
    
    # Plotly Bar Chart (비중 % 표시 복구)
    fig_bar = px.bar(
        df_pf, 
        x='비중', 
        y='종목', 
        orientation='h', 
        text='비중', # 비중을 텍스트로 표시
        color='유형',
        color_discrete_map={
            'Strategic (Core)': '#F59E0B', # Amber
            'Tactical': '#EF4444',        # Red
            'Buffer': '#3B82F6'           # Blue
        },
        template='plotly_dark'
    )
    # 텍스트 포맷팅 (XX.X%)
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        yaxis={'categoryorder':'total ascending', 'title': None},
        xaxis={'title': '비중 (%)'},
        margin=dict(l=0, r=0, t=30, b=0),
        height=500
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📌 종목별 사업적 본질 및 투자 이유 (Rationale)")
    
    # Rationale Display
    for index, row in df_pf.iterrows():
        st.markdown(f"""
        <div style='background-color: #1E293B; border-left: 3px solid #F59E0B; padding: 15px; margin-bottom: 10px; border-radius: 4px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-weight: bold; font-size: 1.1em; color: #F59E0B;'>{row['종목']}</span>
                <span style='color: #94A3B8; font-size: 0.9em;'>{row['유형']} | {row['비중']:.1f}%</span>
            </div>
            <div style='color: #E2E8F0; font-size: 0.95em;'>{row['Rationale']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 🧠 Investment Engine Philosophy")
    st.caption("이 모델을 구동하는 4가지 핵심 투자 철학과 적용 방식입니다.")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("""
        <div class='philo-card'>
            <div class='philo-title'>1. 조지 소로스 : 재귀성 이론 (Reflexivity)</div>
            <div class='philo-desc'>
                <b>"시장의 가격은 펀더멘털을 반영하는 것이 아니라, 왜곡시킨다."</b><br><br>
                <ul>
                    <li><b>기대 효과:</b> 대중의 편향이 극에 달해 추세가 자기 강화(Self-reinforcing)를 넘어 붕괴되는 시점을 포착하여, 남들보다 먼저 빠져나오거나 진입할 수 있습니다.</li>
                    <li><b>모델 적용:</b> '대중 심리 지수'와 '애널리스트 컨센서스'가 모두 극단적일 때(탐욕), 기계적으로 현금 비중을 늘려 리스크를 헷지합니다.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='philo-card'>
            <div class='philo-title'>2. 워런 버핏 : 경제적 해자 (Economic Moat)</div>
            <div class='philo-desc'>
                <b>"10년 동안 보유할 주식이 아니라면 단 10분도 보유하지 마라."</b><br><br>
                <ul>
                    <li><b>기대 효과:</b> 단기 변동성에 흔들리지 않고, 복리의 마법을 통해 자산을 기하급수적으로 증대시킵니다.</li>
                    <li><b>모델 적용:</b> 포트폴리오의 80%(Core)를 '대체 불가능한 독점 기술력(Rationale)'을 가진 기업(테슬라, 엔비디아 등)으로만 구성하여 하락장에서도 버틸 수 있는 체력을 만듭니다.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class='philo-card'>
            <div class='philo-title'>3. 하워드 막스 : 2차적 사고 (Second-Level Thinking)</div>
            <div class='philo-desc'>
                <b>"남들과 다르게 생각하고, 남들보다 맞아야 한다."</b><br><br>
                <ul>
                    <li><b>기대 효과:</b> 모두가 공포에 질려 투매할 때(1차적 사고) 바닥에서 매수하고, 모두가 환호할 때 매도하여 초과 수익(Alpha)을 달성합니다.</li>
                    <li><b>모델 적용:</b> 시장 심리가 '공포(Fear)' 구간일 때 오히려 주식 비중을 최대치(풀매수)로 높이는 역발상 알고리즘으로 구현되었습니다.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='philo-card'>
            <div class='philo-title'>4. 래리 윌리엄스 : 변동성 돌파 (Volatility Breakout)</div>
            <div class='philo-desc'>
                <b>"가격의 움직임(Price Action)이 곧 모든 정보의 총합이다."</b><br><br>
                <ul>
                    <li><b>기대 효과:</b> 추상적인 심리나 뉴스에 의존하지 않고, 객관적인 가격 돌파 신호에 따라 매매하여 감정을 배제한 수익을 냅니다.</li>
                    <li><b>모델 적용:</b> Track A(단기 전술)에서 '변동성 강도' 지표가 특정 임계치를 넘을 때만 레버리지(TQQQ)를 투입하여 상승 추세의 수익을 극대화합니다.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    # 부동산 별도 분석 탭
    st.markdown("""
    <div class='re-card'>
        <h3>🏢 송파구 가락동 유진빌리지 (약 20평) 심층 분석</h3>
        <p><strong>"송파 ICT 보안 클러스터(중앙전파관리소 개발)의 1열 직관 수혜지"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col_re1, col_re2 = st.columns(2)
    
    with col_re1:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.markdown("#### 🏗️ 개발 계획 상세 및 현황")
        st.markdown("""
        **1. 사업 개요 (송파 ICT 보안 클러스터)**
        * **대상지:** 중앙전파관리소 부지 (가락동 100번지 일대)
        * **위치적 특성:** 유진빌리지와 불과 1블록 거리 (도보 1~2분). 개발의 소음은 피하고 수혜는 직접 받는 최적의 이격 거리.
        * **사업 규모:** 총 사업비 5,500억 원, 연면적 17.4만㎡ (약 5.3만 평). 판교 테크노밸리의 축소판.
        * **주요 일정:** * 1단계(청사 증축): 진행 중
            * 2단계(클러스터 착공): 2026~2027년 예정
            * **완공 목표:** 2030년

        **2. 입주 예정 기관 및 기업**
        * 국가 정보 보안의 핵심인 **국가정보원(지부), 한국인터넷진흥원(KISA), 정보보호산업협회** 등 8개 공공기관 입주 확정.
        * 보안 관련 민간 스타트업 및 IT 대기업 연구소 유치 예정.
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_re2:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.markdown("#### 📈 파급 효과 및 투자 가치")
        st.markdown("""
        **1. 직주근접 수요 폭발 (임대료 상승)**
        * 입주가 완료되면 수천 명의 **고소득 IT/보안 전문 인력**이 상주하게 됩니다.
        * 이들은 야근이 잦은 직군 특성상 도보 출퇴근이 가능한 인접 주거지를 선호합니다.
        * **효과:** 유진빌리지의 **전세 및 월세 시세가 급등**하며, 이는 매매가 하방을 강력하게 지지하고 밀어 올리는 역할을 합니다.

        **2. 배후지 재평가 (지가 상승)**
        * 현재는 조용한 주거지이지만, 클러스터 완공 시 **'첨단 업무지구의 배후 주거단지'**로 위상이 바뀝니다.
        * 주변 상권이 발달하고 유동인구가 늘어나며 토지 가치(공시지가)가 꾸준히 우상향할 것입니다.

        **3. 재개발 압력 (Long-term Upside)**
        * 지가가 상승하면 노후 빌라를 그대로 두는 것보다, 이를 합쳐서 아파트나 오피스텔로 개발하려는 압력(모아타운, 가로주택정비 등)이 강해집니다.
        * 10년 후에는 단순 빌라가 아닌 **재개발 입주권**으로서의 가치를 기대할 수 있습니다.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # 가치 상승 차트
    st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
    years = ['현재(2025)', '착공(2027)', '완공(2030)', '성숙기(2035)']
    values = [real_estate_value/100000000, real_estate_value*1.25/100000000, real_estate_value*1.6/100000000, real_estate_value*2.2/100000000]
    
    fig_re = go.Figure()
    fig_re.add_trace(go.Scatter(
        x=years, y=values, 
        mode='lines+markers+text', 
        text=[f"{v:.1f}억" for v in values], 
        textposition="top center",
        line=dict(color='#F59E0B', width=4), 
        marker=dict(size=12, color='#F59E0B')
    ))
    fig_re.update_layout(
        title="예상 가치 상승 시뮬레이션 (단위: 억)", 
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_re, use_container_width=True)
    st.caption("* 위 시뮬레이션은 개발 호재 반영 및 인플레이션을 감안한 추정치이며, 실제 시장 상황에 따라 달라질 수 있습니다.")
    st.markdown("</div>", unsafe_allow_html=True)