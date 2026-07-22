# -*- coding: utf-8 -*-
"""
콩콩 좌표놀이터 🐰
특성화고 1학년, 학습결손이 많은 학생도 쉽게 따라올 수 있는
아주 쉬운 단계별 좌표 학습 웹앱

실행 방법:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

matplotlib.rcParams["axes.unicode_minus"] = False

# 한글 폰트가 있으면 사용, 없으면 기본 폰트로 자동 대체 (에러 방지)
for font_name in ["NanumGothic", "Malgun Gothic", "AppleGothic"]:
    try:
        fm.findfont(font_name, fallback_to_default=False)
        plt.rcParams["font.family"] = font_name
        break
    except Exception:
        continue

# ========================================================================
# 기본 설정
# ========================================================================
st.set_page_config(page_title="콩콩 좌표놀이터", page_icon="🐰", layout="wide")

CORAL = "#FF6B6B"      # 점 A
TEAL = "#4ECDC4"       # 점 B
PURPLE = "#A78BFA"     # 점 C
YELLOW = "#FFD93D"     # 강조색
CREAM = "#FFFDF7"
CARD = "#FFF3E0"
INK = "#2D3436"
LIM = 8  # 좌표 범위 -8 ~ 8 (숫자를 작게 해서 부담을 줄임)

st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{padding-top: 1.6rem; max-width: 1180px;}}
    html, body, [class*="css"] {{
        font-size: 17px;
    }}
    h1 {{font-weight: 900; letter-spacing: -0.5px; color: {INK};}}

    .big-title {{
        font-size: 40px; font-weight: 900; color: {INK};
        margin-bottom: 4px;
    }}
    .sub-title {{
        font-size: 18px; color: #636E72; margin-bottom: 18px;
    }}
    .step-badge {{
        display:inline-block; background:{CORAL}; color:white;
        border-radius:999px; padding:6px 20px; font-size:16px; font-weight:800;
        margin-bottom:10px;
    }}
    .talk-bubble {{
        background:{CARD}; border-radius:20px; padding:18px 24px;
        font-size:20px; line-height:1.6; margin-bottom:18px;
        border: 3px solid #FFE0B2;
    }}
    .result-card {{
        background:linear-gradient(135deg, #FFF3E0 0%, #FFE8E8 100%);
        border-radius:22px; padding:24px 28px; margin-top:14px;
        border: 3px dashed {CORAL};
        font-size:23px; line-height:2.0; font-weight:700; color:{INK};
        text-align:center;
    }}
    .result-number {{
        font-size:44px; font-weight:900; color:{CORAL};
    }}
    .nav-btn button {{
        border-radius:16px !important; font-weight:800 !important;
        font-size:17px !important; height:3.2em !important;
    }}
    div[data-testid="stSlider"] label p {{
        font-size:18px !important; font-weight:700 !important; color:{INK} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ========================================================================
# 공통 함수
# ========================================================================
def base_plot(size=6.4):
    fig, ax = plt.subplots(figsize=(size, size))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal")
    ax.grid(True, color="#FFE0B2", linewidth=1.3, linestyle="--")
    ax.axhline(0, color=INK, linewidth=2)
    ax.axvline(0, color=INK, linewidth=2)
    ax.set_xticks(range(-LIM, LIM + 1, 2))
    ax.set_yticks(range(-LIM, LIM + 1, 2))
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(labelsize=12, colors="#636E72")
    return fig, ax


def draw_point(ax, x, y, label, color, size=220):
    ax.scatter([x], [y], s=size, color=color, zorder=5, edgecolor="white", linewidth=3)
    ax.annotate(f" {label}", (x, y), textcoords="offset points",
                xytext=(12, 12), fontsize=18, fontweight="bold", color=color)


def step_title(num, emoji, title):
    st.markdown(f'<span class="step-badge">{num}단계</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="big-title">{emoji} {title}</div>', unsafe_allow_html=True)


def talk(text):
    st.markdown(f'<div class="talk-bubble">💬 {text}</div>', unsafe_allow_html=True)


def result(html):
    st.markdown(f'<div class="result-card">{html}</div>', unsafe_allow_html=True)


def point_sliders(label, default, color, key, y_too=True):
    st.markdown(f"**{label}** &nbsp;<span style='color:{color};font-size:22px;'>●</span>", unsafe_allow_html=True)
    if y_too:
        c1, c2 = st.columns(2)
        x = c1.slider("가로 위치", -LIM, LIM, default[0], 1, key=f"{key}x")
        y = c2.slider("세로 위치", -LIM, LIM, default[1], 1, key=f"{key}y")
        return x, y
    else:
        x = st.slider("위치", -LIM, LIM, default[0], 1, key=f"{key}x")
        return x


# ========================================================================
# STEP 1. 수직선 위, 두 점 사이의 거리
# ========================================================================
def step1():
    step_title(1, "🚶", "수직선 위, 두 점 사이의 거리")
    talk("두 친구가 수직선 위에 서 있어요. 두 사람은 몇 칸 떨어져 있을까요? 슬라이더를 움직여 친구들을 옮겨보세요!")

    col1, col2 = st.columns([1, 1.3])
    with col1:
        ax_ = point_sliders("친구 A", (-4,), CORAL, "s1a", y_too=False)
        bx_ = point_sliders("친구 B", (5,), TEAL, "s1b", y_too=False)
        dist = abs(bx_ - ax_)
        result(f"두 친구는 서로<br><span class='result-number'>{dist}칸</span> 떨어져 있어요! 🎉"
               f"<br><span style='font-size:16px;font-weight:400;color:#636E72;'>(큰 수 − 작은 수 = 거리 → "
               f"{max(ax_,bx_)} − {min(ax_,bx_)} = {dist})</span>")

    with col2:
        fig, ax = plt.subplots(figsize=(6.4, 2.6))
        fig.patch.set_facecolor(CREAM)
        ax.set_facecolor(CREAM)
        ax.set_xlim(-LIM, LIM)
        ax.set_ylim(-1.5, 1.5)
        ax.axhline(0, color=INK, linewidth=3)
        for t in range(-LIM, LIM + 1):
            ax.plot([t, t], [-0.12, 0.12], color="#B2BEC3", linewidth=1.5)
            ax.text(t, -0.45, str(t), ha="center", fontsize=11, color="#636E72")
        ax.plot([min(ax_, bx_), max(ax_, bx_)], [0.55, 0.55], color=YELLOW, linewidth=5, solid_capstyle="round")
        ax.scatter([ax_], [0], s=380, color=CORAL, zorder=5, edgecolor="white", linewidth=3)
        ax.scatter([bx_], [0], s=380, color=TEAL, zorder=5, edgecolor="white", linewidth=3)
        ax.text(ax_, 0.9, "A", ha="center", fontsize=20, fontweight="bold", color=CORAL)
        ax.text(bx_, 0.9, "B", ha="center", fontsize=20, fontweight="bold", color=TEAL)
        ax.text((ax_ + bx_) / 2, 1.2, f"{dist}칸", ha="center", fontsize=17, fontweight="bold", color="#E17055")
        ax.axis("off")
        st.pyplot(fig)


# ========================================================================
# STEP 2. 평면 위, 두 점 사이의 거리
# ========================================================================
def step2():
    step_title(2, "📍", "평면 위, 두 점 사이의 거리")
    talk("이번엔 위아래로도 움직일 수 있어요! 가로로 몇 칸, 세로로 몇 칸 떨어졌는지 세어 보면 두 점 사이의 거리를 구할 수 있어요.")

    col1, col2 = st.columns([1, 1.3])
    with col1:
        ax_, ay_ = point_sliders("점 A", (-4, -2), CORAL, "s2a")
        bx_, by_ = point_sliders("점 B", (3, 4), TEAL, "s2b")
        dx, dy = abs(bx_ - ax_), abs(by_ - ay_)
        dist = (dx ** 2 + dy ** 2) ** 0.5
        result(f"가로 {dx}칸, 세로 {dy}칸 떨어져 있어요<br>"
               f"두 점 사이의 거리는 약 <span class='result-number'>{dist:.1f}칸</span>이에요! 🎉"
               f"<br><span style='font-size:15px;font-weight:400;color:#636E72;'>"
               f"(가로×가로 + 세로×세로 = 거리×거리 → {dx}×{dx} + {dy}×{dy} = {dx**2+dy**2})</span>")

    with col2:
        fig, ax = base_plot()
        draw_point(ax, ax_, ay_, "A", CORAL)
        draw_point(ax, bx_, by_, "B", TEAL)
        ax.plot([ax_, bx_], [ay_, by_], color=INK, linewidth=3.2, zorder=4)
        ax.plot([ax_, bx_], [ay_, ay_], "--", color=YELLOW, linewidth=3)
        ax.plot([bx_, bx_], [ay_, by_], "--", color=YELLOW, linewidth=3)
        st.pyplot(fig)


# ========================================================================
# STEP 3. 내분점
# ========================================================================
def step3():
    step_title(3, "✂️", "선분을 나누는 점, 내분점")
    talk("점 A와 점 B를 잇는 선을 원하는 비율로 나눠 봐요. 슬라이더로 비율을 바꾸면 점 P가 움직여요!")

    col1, col2 = st.columns([1, 1.3])
    with col1:
        ax_, ay_ = point_sliders("점 A", (-6, -3), CORAL, "s3a")
        bx_, by_ = point_sliders("점 B", (6, 5), TEAL, "s3b")
        st.markdown("**P가 나누는 비율**")
        c1, c2 = st.columns(2)
        m = c1.slider("A쪽 비율 (m)", 1, 9, 1, 1, key="s3m")
        n = c2.slider("B쪽 비율 (n)", 1, 9, 1, 1, key="s3n")
        px = (m * bx_ + n * ax_) / (m + n)
        py = (m * by_ + n * ay_) / (m + n)
        result(f"점 P는 A와 B 사이를<br><b>{m} : {n}</b> 비율로 나누고 있어요<br>"
               f"P의 좌표는 <span class='result-number'>({px:.1f}, {py:.1f})</span> 예요! 🎉")

    with col2:
        fig, ax = base_plot()
        draw_point(ax, ax_, ay_, "A", CORAL)
        draw_point(ax, bx_, by_, "B", TEAL)
        ax.plot([ax_, px], [ay_, py], color=CORAL, linewidth=4, alpha=0.55, solid_capstyle="round")
        ax.plot([px, bx_], [py, by_], color=TEAL, linewidth=4, alpha=0.55, solid_capstyle="round")
        draw_point(ax, round(px, 2), round(py, 2), "P", "#F39C12", size=260)
        st.pyplot(fig)


# ========================================================================
# STEP 4. 중점
# ========================================================================
def step4():
    step_title(4, "🎯", "딱 절반, 중점")
    talk("중점은 선분을 정확히 반으로 나누는 점이에요. 바로 앞에서 배운 내분점에서 1 : 1로 나눈 것과 같아요!")

    col1, col2 = st.columns([1, 1.3])
    with col1:
        ax_, ay_ = point_sliders("점 A", (-5, 2), CORAL, "s4a")
        bx_, by_ = point_sliders("점 B", (5, -4), TEAL, "s4b")
        mx, my = (ax_ + bx_) / 2, (ay_ + by_) / 2
        result(f"중점 M의 좌표는<br><span class='result-number'>({mx:g}, {my:g})</span> 예요! 🎉"
               f"<br><span style='font-size:15px;font-weight:400;color:#636E72;'>"
               f"(A와 B의 좌표를 각각 더해서 2로 나누면 돼요)</span>")

    with col2:
        fig, ax = base_plot()
        draw_point(ax, ax_, ay_, "A", CORAL)
        draw_point(ax, bx_, by_, "B", TEAL)
        ax.plot([ax_, bx_], [ay_, by_], color="#DFE6E9", linewidth=4)
        draw_point(ax, mx, my, "M", "#F39C12", size=260)
        st.pyplot(fig)


# ========================================================================
# STEP 5. 무게중심
# ========================================================================
def step5():
    step_title(5, "⚖️", "삼각형의 균형점, 무게중심")
    talk("세 점으로 삼각형을 만들면, 무게중심은 삼각형이 완벽하게 균형을 잡는 점이에요. 손가락으로 받치면 쓰러지지 않는 지점이랍니다!")

    col1, col2 = st.columns([1, 1.3])
    with col1:
        ax_, ay_ = point_sliders("점 A", (-6, -4), CORAL, "s5a")
        bx_, by_ = point_sliders("점 B", (6, -4), TEAL, "s5b")
        cx_, cy_ = point_sliders("점 C", (0, 6), PURPLE, "s5c")
        gx, gy = (ax_ + bx_ + cx_) / 3, (ay_ + by_ + cy_) / 3
        result(f"무게중심 G의 좌표는<br><span class='result-number'>({gx:.1f}, {gy:.1f})</span> 예요! 🎉"
               f"<br><span style='font-size:15px;font-weight:400;color:#636E72;'>"
               f"(세 점의 좌표를 각각 더해서 3으로 나누면 돼요)</span>")

    with col2:
        fig, ax = base_plot()
        tri = plt.Polygon([(ax_, ay_), (bx_, by_), (cx_, cy_)], closed=True,
                           facecolor="#FFF3E0", edgecolor=INK, linewidth=3)
        ax.add_patch(tri)
        draw_point(ax, ax_, ay_, "A", CORAL)
        draw_point(ax, bx_, by_, "B", TEAL)
        draw_point(ax, cx_, cy_, "C", PURPLE)
        draw_point(ax, gx, gy, "G", "#F39C12", size=280)
        st.pyplot(fig)


# ========================================================================
# 메인
# ========================================================================
STEPS = {
    "1️⃣ 수직선 위 거리": step1,
    "2️⃣ 평면 위 거리": step2,
    "3️⃣ 내분점": step3,
    "4️⃣ 중점": step4,
    "5️⃣ 무게중심": step5,
}

st.markdown('<div class="big-title">🐰 콩콩 좌표놀이터</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">슬라이더를 움직이며 몸으로 익히는 아주 쉬운 좌표 이야기</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🗺️ 오늘의 모험")
    choice = st.radio("단계를 골라보세요", list(STEPS.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**놀이 방법**\n\n① 슬라이더를 좌우로 밀어보기\n\n② 그림이 바뀌는 모습 관찰하기\n\n③ 아래 말풍선에서 답 확인하기")

STEPS[choice]()
