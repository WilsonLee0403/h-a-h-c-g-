# -*- coding: utf-8 -*-
"""
🌿 PHÒNG PHÂN TÍCH & ĐIỀU CHẾ NƯỚC HOA BỐN MÙA — L'AURA ATELIER x STEM HÓA 12
Bản hoàn thiện: Giữ nguyên 100% nguyên liệu & dữ liệu gốc, chỉ đổi màu giao diện theo 4 Mùa
Lệnh chạy: streamlit run app.py
"""

import os
import json
import time
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st

import io
import re
try:
    from gtts import gTTS
    TTS_READY = True
except ImportError:
    TTS_READY = False

def speak_vietnamese(text):
    """Chuyển văn bản trả lời của AI thành giọng nói tiếng Việt"""
    if not TTS_READY or not text:
        return
    try:
        # Lọc bỏ các ký hiệu Markdown (*, #, _) để AI đọc mượt tự nhiên
        clean_text = re.sub(r'[*#_`~>-]', '', text)
        tts = gTTS(text=clean_text, lang='vi')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        st.audio(audio_fp, format='audio/mp3', autoplay=True)
    except Exception:
        pass
# Thư viện Google GenAI chính thức
try:
    from google import genai
    from google.genai import types
    GEMINI_READY = True
except ImportError:
    GEMINI_READY = False

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Vườn Nhiệt Đới | STEM Lab Hóa 12 & L'Aura Atelier",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Bảng màu giao diện tự động đổi theo mùa (KHÔNG đụng vào dữ liệu nguyên liệu)
SEASON_THEMES = {
    "Mùa Xuân": {
        "bg_gradient": "radial-gradient(circle at 15% 20%, #4a192c 0%, #240b16 60%, #12040a 100%)",
        "accent": "#ff85a2",
        "accent_secondary": "#ffb3c6",
        "title_grad": "linear-gradient(90deg, #ffe5ec, #ff85a2, #fb6f92)",
        "badge_bg": "rgba(255, 133, 162, 0.14)",
        "badge_border": "rgba(255, 133, 162, 0.4)",
        "flask_glow": "rgba(255, 133, 162, 0.25)",
        "layer_top": "rgba(255, 214, 165, 0.88)",
        "layer_heart": "rgba(255, 133, 162, 0.88)",
        "layer_base": "rgba(199, 125, 255, 0.88)",
    },
    "Mùa Hạ": {
        "bg_gradient": "radial-gradient(circle at 10% 20%, #163842 0%, #0b1a1f 60%, #050d10 100%)",
        "accent": "#00ffe0",
        "accent_secondary": "#80e6a2",
        "title_grad": "linear-gradient(90deg, #ffe000, #80e6a2, #00ffe0)",
        "badge_bg": "rgba(0, 255, 224, 0.1)",
        "badge_border": "rgba(0, 255, 224, 0.3)",
        "flask_glow": "rgba(0, 255, 224, 0.15)",
        "layer_top": "rgba(255, 224, 0, 0.85)",
        "layer_heart": "rgba(128, 230, 162, 0.85)",
        "layer_base": "rgba(0, 255, 224, 0.85)",
    },
    "Mùa Thu": {
        "bg_gradient": "radial-gradient(circle at 15% 20%, #4a1c11 0%, #260d08 60%, #120503 100%)",
        "accent": "#ff7b54",
        "accent_secondary": "#ffb26b",
        "title_grad": "linear-gradient(90deg, #ffd56b, #ff7b54, #e63946)",
        "badge_bg": "rgba(255, 123, 84, 0.15)",
        "badge_border": "rgba(255, 123, 84, 0.4)",
        "flask_glow": "rgba(255, 123, 84, 0.25)",
        "layer_top": "rgba(255, 213, 107, 0.88)",
        "layer_heart": "rgba(255, 123, 84, 0.88)",
        "layer_base": "rgba(181, 65, 36, 0.9)",
    },
    "Mùa Đông": {
        "bg_gradient": "radial-gradient(circle at 15% 20%, #132a4a 0%, #091326 60%, #040812 100%)",
        "accent": "#70d6ff",
        "accent_secondary": "#a9def9",
        "title_grad": "linear-gradient(90deg, #ffffff, #a9def9, #70d6ff)",
        "badge_bg": "rgba(112, 214, 255, 0.14)",
        "badge_border": "rgba(112, 214, 255, 0.4)",
        "flask_glow": "rgba(112, 214, 255, 0.25)",
        "layer_top": "rgba(226, 234, 252, 0.88)",
        "layer_heart": "rgba(112, 214, 255, 0.88)",
        "layer_base": "rgba(67, 97, 238, 0.88)",
    },
}

# 3. Dữ liệu hệ thống 4 Mùa NGUYÊN BẢN 100% (Mùa Hạ = Vườn Nhiệt Đới)
GV_LIMITS = {
    "Mùa Xuân": {
        "Bergamot FCF": 4.0, "Sweet orange": 3.0, "Lavender": 4.0,
        "Geranium": 3.0, "Cedarwood": 2.0, "Vanilla accord": 1.0
    },
    "Mùa Hạ": {
        "White Osmanthus": 4.0, "Jasmine": 4.0, "Dừa (Coconut)": 2.0, "Nước cất": 15.0
    },
    "Mùa Thu": {
        "Sweet orange": 3.0, "Bergamot FCF": 3.0, "Lavender": 4.0,
        "Geranium": 3.0, "Cedarwood": 3.0, "Vanilla accord": 1.5
    },
    "Mùa Đông": {
        "Bergamot FCF": 3.0, "Sweet orange": 2.5, "Lavender": 3.5,
        "Geranium": 3.0, "Cedarwood": 3.0, "Vanilla accord": 2.0
    },
}

MAX_FRAGRANCE_PCT = 30.0
SLIDER_OVERFLOW = 0.0  # Khóa cứng ở trần Giáo viên
TOTAL_VOLUME_MIN, TOTAL_VOLUME_MAX = 1.0, 50.0

TIER_TARGET = {
    "Mùa Xuân": (35, 45, 20),
    "Mùa Hạ": (40, 50, 10),
    "Mùa Thu": (25, 40, 35),
    "Mùa Đông": (20, 35, 45),
}

SAFETY_RULES = [
    "<strong>1. Không tự pha tại nhà</strong> — chỉ thực hiện tại phòng lab có giáo viên hướng dẫn.",
    "<strong>2. Thử trên giấy thử (blotter)</strong> — TUYỆT ĐỐI không xịt trực tiếp lên da.",
    "<strong>3. Không nếm, tránh mắt</strong> — bảo quản hóa chất xa tầm tay trẻ em.",
    "<strong>4. Ethanol 90° dễ cháy</strong> — tránh xa nguồn lửa, nhiệt độ cao và tĩnh điện.",
    "<strong>5. Đeo bảo hộ (găng, kính)</strong> — luôn chuẩn bị sẵn bảng chỉ dẫn hóa chất SDS/IFRA.",
    "<strong>6. Đạt 100% chưa hẳn an toàn</strong> — mọi mẻ pha phải được GV thẩm định trước."
]

seasons_data = {
    "Mùa Xuân": {
        "label": "Mùa Xuân — Tươi Mới & Sắc Hoa",
        "display_name": "Mùa Xuân",
        "slug": "xuan", "icon": "🌸",
        "desc_profile": "Hương cam chanh hòa quyện cùng oải hương, phong lữ dịu nhẹ và lớp nền gỗ tuyết tùng êm ái.",
        "ingredients": [
            ("Bergamot FCF", 3.8, "Hương đầu (Top)", "top"),
            ("Sweet orange", 2.0, "Hương đầu (Top)", "top"),
            ("Lavender", 3.5, "Hương giữa (Heart)", "middle"),
            ("Geranium", 2.5, "Hương giữa (Heart)", "middle"),
            ("Cedarwood", 1.3, "Hương cuối (Base)", "base"),
            ("Vanilla accord", 0.6, "Hương cuối (Base)", "base"),
        ],
    },
    "Mùa Hạ": {
        "label": "Vườn Nhiệt Đới — Mùa Hạ (Mẫu B Chuẩn)",
        "display_name": "Vườn Nhiệt Đới",
        "slug": "vuon_nhiet_doi", "icon": "🌿",
        "desc_profile": "Hương đầu bừng sáng hoa mộc trắng, hương giữa nhài thanh tao đằm thắm và lớp nền dừa ngọt dịu béo nhẹ.",
        "ingredients": [
            ("White Osmanthus", 2.0, "Hương đầu (Top)", "top"),
            ("Jasmine", 2.5, "Hương giữa (Heart)", "middle"),
            ("Dừa (Coconut)", 0.5, "Hương cuối (Base)", "base"),
            ("Nước cất", 10.0, "Dung dịch đệm", "water"),
        ],
    },
    "Mùa Thu": {
        "label": "Mùa Thu — Dịu Êm & Sâu Lắng",
        "display_name": "Mùa Thu",
        "slug": "thu", "icon": "🍁",
        "desc_profile": "Ấm áp với cam ngọt đằm thắm và nền tuyết tùng phảng phất hương vani dịu ngọt.",
        "ingredients": [
            ("Sweet orange", 2.5, "Hương đầu (Top)", "top"),
            ("Bergamot FCF", 1.8, "Hương đầu (Top)", "top"),
            ("Lavender", 3.0, "Hương giữa (Heart)", "middle"),
            ("Geranium", 2.5, "Hương giữa (Heart)", "middle"),
            ("Cedarwood", 2.2, "Hương cuối (Base)", "base"),
            ("Vanilla accord", 0.9, "Hương cuối (Base)", "base"),
        ],
    },
    "Mùa Đông": {
        "label": "Mùa Đông — Ấm Áp & Sang Trọng",
        "display_name": "Mùa Đông",
        "slug": "dong", "icon": "❄️",
        "desc_profile": "Hương cuối đậm sâu, sang trọng với hợp hương gỗ tuyết tùng và vanilla lưu hương vượt trội.",
        "ingredients": [
            ("Bergamot FCF", 1.8, "Hương đầu (Top)", "top"),
            ("Sweet orange", 1.5, "Hương đầu (Top)", "top"),
            ("Lavender", 2.5, "Hương giữa (Heart)", "middle"),
            ("Geranium", 2.0, "Hương giữa (Heart)", "middle"),
            ("Cedarwood", 2.5, "Hương cuối (Base)", "base"),
            ("Vanilla accord", 1.2, "Hương cuối (Base)", "base"),
        ],
    },
}

# 4. Sidebar: Điều khiển mẫu & Thể tích
with st.sidebar:
    season_options = ["Mùa Xuân", "Mùa Hạ", "Mùa Thu", "Mùa Đông"]
    current_s = st.session_state.get("season_selector", "Mùa Hạ")
    active_theme = SEASON_THEMES[current_s]

    st.markdown(f"<h3 style='text-align: center; color: {active_theme['accent']};'>🎛️ BẢNG ĐIỀU KHIỂN</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**🌿 Chọn công thức mùa:**")
    selected_season_key = st.selectbox("Chọn công thức mẫu:", season_options, index=1, key="season_selector")
    
    season_info = seasons_data[selected_season_key]
    limits = GV_LIMITS[selected_season_key]
    theme = SEASON_THEMES[selected_season_key]

    st.markdown("---")
    st.markdown("**🧪 Thể tích mẻ sản xuất (mL):**")
    
    if "vol_state" not in st.session_state:
        st.session_state.vol_state = 20.0

    def set_preset_volume(v):
        st.session_state.vol_state = float(v)

    c1, c2, c3, c4 = st.columns(4)
    for col, ml in zip((c1, c2, c3, c4), (5.0, 10.0, 20.0, 50.0)):
        with col:
            st.button(f"{int(ml)}ml", key=f"btn_vol_{int(ml)}", on_click=set_preset_volume, args=(ml,), use_container_width=True)

    volume = st.number_input(
        "Tùy chỉnh thể tích (mL):",
        min_value=TOTAL_VOLUME_MIN,
        max_value=TOTAL_VOLUME_MAX,
        step=0.5,
        key="vol_state",
        help=f"Giới hạn an toàn phòng lab: {TOTAL_VOLUME_MIN} – {TOTAL_VOLUME_MAX} mL"
    )

    st.markdown("---")
    st.markdown("#### ⚠️ 6 Quy tắc an toàn bắt buộc")
    for rule in SAFETY_RULES:
        st.markdown(f"<div class='safety-box-custom'>{rule}</div>", unsafe_allow_html=True)

# 5. CSS Custom Theme: Đổi màu động theo mùa
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .stApp {{
        background: {theme['bg_gradient']} !important;
        color: #f0f4f8;
        transition: background 0.5s ease;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid {theme['badge_border']} !important;
        border-radius: 18px !important;
        padding: 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35) !important;
    }}

    .hero-header {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid {theme['badge_border']};
        border-radius: 20px;
        padding: 24px 20px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
    }}

    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2.3rem;
        font-weight: 700;
        background: {theme['title_grad']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }}

    .hero-sub {{
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.1rem;
        color: #d1d9e0;
        margin-bottom: 12px;
    }}

    .hero-badge {{
        display: inline-block;
        background: {theme['badge_bg']};
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        border: 1px solid {theme['badge_border']};
        color: {theme['accent']};
        font-weight: 600;
    }}

    .metric-card-custom {{
        background: rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
    }}
    .metric-val {{
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 4px;
    }}
    .metric-lbl {{
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .flask-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 15px 0;
    }}
    .flask-cap {{
        width: 44px;
        height: 16px;
        background: linear-gradient(90deg, #ffd700, #fff8dc);
        border-radius: 4px 4px 0 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
    }}
    .flask-container {{
        width: 140px;
        height: 210px;
        border: 3.5px solid rgba(255, 255, 255, 0.75);
        border-radius: 12px 12px 30px 30px;
        position: relative;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.02);
        box-shadow: 0 0 25px {theme['flask_glow']}, inset 0 0 15px rgba(255, 255, 255, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }}
    .flask-liquid-layer {{
        width: 100%;
        transition: height 0.4s ease;
    }}
    .layer-top {{ background: {theme['layer_top']}; }}
    .layer-heart {{ background: {theme['layer_heart']}; }}
    .layer-base {{ background: {theme['layer_base']}; }}
    .layer-solvent {{ background: rgba(148, 163, 184, 0.25); }}

    .flask-label {{
        position: absolute;
        top: 34%;
        left: 8%;
        width: 84%;
        background: rgba(255, 255, 255, 0.94);
        color: #0f172a;
        padding: 6px 2px;
        text-align: center;
        border-radius: 6px;
        font-family: 'Playfair Display', serif;
        font-size: 0.7rem;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35);
        z-index: 2;
    }}

    .safety-box-custom {{
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
        margin-bottom: 8px !important;
        color: #cbd5e1 !important;
    }}
</style>
""", unsafe_allow_html=True)

# 6. Header Section nguyên bản
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🌿 PHÒNG PHA CHẾ NƯỚC HOA BỐN MÙA</div>
    <div class="hero-sub">"Gói trọn hương sắc mùa hè vào từng nhịp đập tuổi trẻ"</div>
    <div class="hero-badge">✨ Dự Án STEM Hóa Học 12 & AI • THPT Nguyễn Thị Minh Khai • Tổ 4 - Lớp 12A10</div>
</div>
""", unsafe_allow_html=True)

# 7. Khu vực chính: Điều chỉnh tỷ lệ & Mô phỏng
title_display = "Vườn Nhiệt Đới (Mùa Hạ)" if selected_season_key == "Mùa Hạ" else selected_season_key
st.markdown(f"<h3 style='color: {theme['accent']}; margin-bottom: 15px;'>✨ Điều Chỉnh Tỉ Lệ & Thẩm Định: {title_display}</h3>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.15, 1], gap="medium")
rows, errors = [], []

with col_left.container(border=True):
    st.subheader(f"🎚️ Thiết Lập Nồng Độ — {title_display}")
    st.caption("🔒 Thanh trượt đã được **khóa trần an toàn** theo đúng giới hạn của Giáo viên (không thể kéo vượt mức cho phép).")

    top_items = [i for i in season_info["ingredients"] if i[3] == "top"]
    heart_items = [i for i in season_info["ingredients"] if i[3] == "middle"]
    base_items = [i for i in season_info["ingredients"] if i[3] == "base"]
    water_items = [i for i in season_info["ingredients"] if i[3] == "water"]

    tier_groups = {}
    if top_items: tier_groups["Hương đầu (Top Notes) 🍋"] = top_items
    if heart_items: tier_groups["Hương giữa (Heart Notes) 🌸"] = heart_items
    if base_items: tier_groups["Hương cuối (Base Notes) 🥥"] = base_items
    if water_items: tier_groups["Dung dịch đệm (Nước cất) 💧"] = water_items

    for group_title, items in tier_groups.items():
        st.markdown(f"**{group_title}**")
        for name, default_val, tier, ttype in items:
            limit = float(limits[name])
            slider_key = f"slider_{season_info['slug']}_{name}"
            
            if slider_key in st.session_state and st.session_state[slider_key] > limit:
                st.session_state[slider_key] = limit

            cL, cS = st.columns([1.1, 2])
            with cL:
                st.markdown(f"<div style='padding-top:6px; font-weight:600; font-size:0.9rem;'>{name}</div>", unsafe_allow_html=True)
                st.caption(f"Trần GV: {limit:.1f}%")
            with cS:
                pct = st.slider(
                    f"Tỉ lệ {name}",
                    min_value=0.0,
                    max_value=limit,
                    value=min(float(default_val), limit),
                    step=0.1,
                    key=slider_key,
                    label_visibility="collapsed"
                )

            rows.append({
                "Thành phần": name,
                "Tầng hương": tier,
                "type": ttype,
                "%": pct,
                "Giới hạn GV (%)": limit,
                "mL": round(volume * pct / 100, 3)
            })
        st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    frag_rows = [r for r in rows if r["type"] in ("top", "middle", "base")]
    water_pct = sum(r["%"] for r in rows if r["type"] == "water")
    fragrance_total = round(sum(r["%"] for r in frag_rows), 2)
    non_solvent_total = fragrance_total + water_pct
    solvent_pct = round(100.0 - non_solvent_total, 2)
    solvent_ml = round(volume * solvent_pct / 100, 3)

    rows.append({
        "Thành phần": "Dung môi (Ethanol 90°)",
        "Tầng hương": "Dung môi",
        "type": "dung moi",
        "%": solvent_pct,
        "Giới hạn GV (%)": 100.0,
        "mL": solvent_ml
    })

    if fragrance_total <= 0:
        errors.append("Công thức rỗng! Vui lòng chọn ít nhất 1 thành phần tinh dầu.")
    if fragrance_total > MAX_FRAGRANCE_PCT:
        errors.append(f"Tổng nồng độ tinh dầu {fragrance_total:.1f}% vượt chuẩn an toàn học đường ({MAX_FRAGRANCE_PCT}%).")
    if solvent_pct < 0:
        errors.append("Tổng các chất vượt quá 100%, tỷ lệ dung môi Ethanol bị âm!")

    top_pct = sum(r["%"] for r in frag_rows if r["type"] == "top")
    mid_pct = sum(r["%"] for r in frag_rows if r["type"] == "middle")
    base_pct = sum(r["%"] for r in frag_rows if r["type"] == "base")
    
    share = {"Hương đầu": top_pct, "Hương giữa": mid_pct, "Hương cuối": base_pct}
    dom_tier = max(share, key=lambda k: share[k]) if fragrance_total > 0 else "Hương đầu"
    t_top, t_mid, t_base = TIER_TARGET[selected_season_key]

    df = pd.DataFrame(rows)

with col_right.container(border=True):
    st.subheader("📊 Thông Số Thể Tích & Trực Quan Hóa")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-card-custom">
            <div class="metric-lbl">Hương liệu</div>
            <div class="metric-val" style="color:{'#f87171' if fragrance_total > MAX_FRAGRANCE_PCT else theme['accent']};">{fragrance_total:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card-custom">
            <div class="metric-lbl">Dung môi cồn</div>
            <div class="metric-val" style="color:{'#f87171' if solvent_pct < 0 else theme['accent_secondary']};">{solvent_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card-custom">
            <div class="metric-lbl">Trạng thái</div>
            <div class="metric-val" style="color:{'#f87171' if errors else '#4ade80'}; font-size:1.15rem; line-height:2.2rem;">
                {'❌ Vi phạm' if errors else '✅ Đạt chuẩn'}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(min(max(fragrance_total / MAX_FRAGRANCE_PCT, 0.0), 1.0), text=f"Tải lượng hương: {fragrance_total:.1f}% / {MAX_FRAGRANCE_PCT}% Max")

    h_solvent = max(solvent_pct + water_pct, 0.0)
    bottle_tag = "VƯỜN NHIỆT ĐỚI" if selected_season_key == "Mùa Hạ" else season_info['display_name'].upper()

    st.markdown(f"""
    <div class="flask-wrapper">
        <div class="flask-cap"></div>
        <div class="flask-container">
            <div class="flask-label">L'AURA ATELIER<br><span style="font-size:0.56rem; letter-spacing:0.8px;">{bottle_tag}</span></div>
            <div class="flask-liquid-layer layer-top" style="height:{top_pct:.1f}%;" title="Hương đầu: {top_pct:.1f}%"></div>
            <div class="flask-liquid-layer layer-heart" style="height:{mid_pct:.1f}%;" title="Hương giữa: {mid_pct:.1f}%"></div>
            <div class="flask-liquid-layer layer-base" style="height:{base_pct:.1f}%;" title="Hương cuối: {base_pct:.1f}%"></div>
            <div class="flask-liquid-layer layer-solvent" style="height:{h_solvent:.1f}%;" title="Dung môi & Nước: {h_solvent:.1f}%"></div>
        </div>
        <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Mô phỏng 4 pha phân tầng tỉ lệ thực nghiệm</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📋 Bảng Quy Đổi Liều Lượng Thực Tế:**")
    df_display = df.drop(columns=["type"]).copy()
    st.dataframe(
        df_display.style.format({
            "%": "{:.2f}%",
            "Giới hạn GV (%)": "{:.1f}%",
            "mL": "{:.3f} mL"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); border-left:3px solid {theme['accent']}; padding:10px 14px; border-radius:6px; margin: 12px 0;">
        <b style="color:{theme['accent']};">🌿 Hồ sơ mùi hương:</b> {season_info['desc_profile']}<br>
        <small style="color:#94a3b8;">Đang chủ đạo ở <b>{dom_tier.lower()}</b> ({share[dom_tier]:.1f}% tổng hương). Tỉ lệ 3 tầng: {top_pct:.1f}% / {mid_pct:.1f}% / {base_pct:.1f}% (Khung chuẩn: {t_top}/{t_mid}/{t_base}).</small>
    </div>
    """, unsafe_allow_html=True)

    # Xuất file CSV
    st.markdown("---")
    if not errors:
        st.success(f"✨ Mẻ **{volume:.1f} mL** đã thỏa mãn toàn bộ tiêu chuẩn an toàn.")
        export_name = "Vườn Nhiệt Đới" if selected_season_key == "Mùa Hạ" else selected_season_key
        export_df = pd.DataFrame({
            "Tên công thức / Mẫu": [export_name] * len(rows),
            "Thành phần": [r["Thành phần"] for r in rows],
            "Tầng hương": [r["Tầng hương"] for r in rows],
            "Tỉ lệ (%)": [round(r["%"], 2) for r in rows],
            "Giới hạn GV (%)": [r["Giới hạn GV (%)"] for r in rows],
            "Kiểm định": ["Đạt" if r["%"] <= r["Giới hạn GV (%)"] + 1e-9 else "Vượt trần" for r in rows],
            "Thể tích (mL)": [r["mL"] for r in rows]
        })
        
        file_slug = "vuon_nhiet_doi" if selected_season_key == "Mùa Hạ" else season_info['slug']
        st.download_button(
            label="📥 Xuất Báo Cáo Kiểm Duyệt (CSV)",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"cong_thuc_{file_slug}_{int(volume)}ml.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.markdown("### ⚠️ Phát Hiện Lỗi Cần Điều Chỉnh")
        for err in errors:
            st.error(f"❌ {err}")
        st.info("Chức năng tải file CSV bị khóa cho đến khi toàn bộ chỉ số đạt chuẩn.")

# 8. Module Tích Hợp Gemini AI Lab (Bản chuẩn: Tự khóa vào model sống + In rõ lỗi nếu có)
# Tự động lấy Key từ két sắt Streamlit Secrets (không lo bị Google khóa khi để GitHub Public)
if "GEMINI_API_KEY" in st.secrets:
    FIXED_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    FIXED_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6I_SSQXNBP7J24ykRE7o4-qYzGAEKV7s7pZ4jc384_ntg")

@st.cache_resource
def get_cached_client():
    return genai.Client(api_key=FIXED_API_KEY.strip())

@st.cache_data(ttl=3600)
def get_fast_model_list():
    """Quét 1 lần duy nhất khi mở web để lấy đúng tên model đang mở trên Key AQ..."""
    client = get_cached_client()
    available = []
    try:
        for m in client.models.list():
            name = getattr(m, "name", "").replace("models/", "")
            if "gemini" in name and "vision" not in name and "embedding" not in name:
                available.append(name)
    except Exception:
        pass

    # Thứ tự ưu tiên từ nhanh nhất (Lite -> Flash)
    preferred = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        
    ]
    
    # Đưa các model vừa có trong preferred vừa có trong available lên đầu tiên
    result = [p for p in preferred if p in available]
    for a in available:
        if a not in result and ("flash" in a or "lite" in a or "pro" in a):
            result.append(a)
    for p in preferred:
        if p not in result:
            result.append(p)
    return result

def ask_real_gemini_stream(prompt_text, system_instruction=None):
    client = get_cached_client()
    models_to_try = get_fast_model_list()

    # Nếu lần trước đã tìm được model chạy ngon thì đưa thẳng lên đầu (không tốn thời gian thử lại)
    best_model = st.session_state.get("best_working_model")
    if best_model and best_model in models_to_try:
        models_to_try = [best_model] + [m for m in models_to_try if m != best_model]

    cfg = types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=8192,  # Mở trần tối đa để viết dài thoải mái
        system_instruction=system_instruction,
    )

    last_err = None
    for model_name in models_to_try:
        try:
            # Dùng generate_content lấy trọn vẹn 100% bài viết trước để không bao giờ bị đứt mạng giữa chừng
            res = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=cfg
            )
            if res and res.text:
                st.session_state["best_working_model"] = model_name
                # Vẫn tạo hiệu ứng gõ chữ mượt mà ra màn hình
                for word in res.text.split(" "):
                    yield word + " "
                    time.sleep(0.01)
                return
        except Exception as e:
            last_err = f"[{model_name}]: {e}"
            continue

    yield f"⚠️ Chi tiết lỗi kết nối: `{last_err}`"

def auto_tune_sliders_callback():
    total_target_frag = 12.0 if selected_season_key != "Mùa Hạ" else 6.0
    tier_weights = {"top": t_top / 100.0, "middle": t_mid / 100.0, "base": t_base / 100.0}
    
    for t_code in ("top", "middle", "base"):
        group_items = [i for i in season_info["ingredients"] if i[3] == t_code]
        if group_items:
            each_share = (total_target_frag * tier_weights[t_code]) / len(group_items)
            for name, _, _, _ in group_items:
                safe_val = min(round(each_share, 1), float(limits[name]))
                st.session_state[f"slider_{season_info['slug']}_{name}"] = max(safe_val, 0.5)
    
    for name, default_val, _, t_code in season_info["ingredients"]:
        if t_code == "water":
            st.session_state[f"slider_{season_info['slug']}_{name}"] = min(float(default_val), float(limits[name]))

    st.session_state["ai_tune_msg"] = f"✨ **AI đã tối ưu hóa các thanh trượt** theo đúng tỉ lệ vàng ({t_top}:{t_mid}:{t_base}) và khóa trong trần Giáo viên!"

st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown(f"<h3 style='color: {theme['accent']}; margin-top: 0;'>🤖 L'AURA AI LAB — Trợ Lý Hóa Học & Phản Biện Công Thức</h3>", unsafe_allow_html=True)
    st.caption("Thẩm định động học bay hơi, cân bằng este và hỏi đáp xử lý sự cố mùi hương trực tiếp.")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_ai_btn = st.button("🚀 Thẩm Định Công Thức Bằng AI", type="primary", use_container_width=True)
    with col_btn2:
        st.button(
            "🪄 AI Tự Cân Chỉnh Tỉ Lệ Chuẩn",
            on_click=auto_tune_sliders_callback,
            use_container_width=True
        )

    if "ai_tune_msg" in st.session_state:
        st.success(st.session_state.pop("ai_tune_msg"))

    formula_context = "\n".join([
        f"- Công thức đang chọn: {title_display} (Thể tích mẻ: {volume:.1f} mL)",
        *[f"- {r['Thành phần']} ({r['Tầng hương']}): {r['%']:.1f}% ≈ {r['mL']:.3f} mL (Trần GV: {r['Giới hạn GV (%)']:.1f}%)" for r in rows if r["type"] != "dung moi"],
        f"- Dung môi Ethanol 90°: {solvent_pct:.1f}% ≈ {solvent_ml:.3f} mL",
        f"- Tổng tinh dầu: {fragrance_total:.1f}% (Hương đầu: {top_pct:.1f}% | Hương giữa: {mid_pct:.1f}% | Hương cuối: {base_pct:.1f}%)",
        f"- Khung chuẩn mùa: Đầu {t_top}% / Giữa {t_mid}% / Cuối {t_base}%"
    ])

    tab_run, tab_chat, tab_view = st.tabs(["⚡ Phân Tích Trực Tuyến", "💬 Hỏi Đáp Hóa 12 Cùng AI", "📄 Xem Prompt"])

    with tab_run:
        if run_ai_btn:
            st.markdown("---")
            st.markdown("#### 📋 Đánh Giá Chuyên Môn Từ AI:")
            report_prompt = (
                f"Dưới đây là thông số công thức nước hoa của nhóm học sinh lớp 12:\n{formula_context}\n\n"
                f"Hãy thẩm định ngắn gọn, súc tích và sinh động theo 4 mục:\n"
                f"1. **Tương tác Hóa học & Độ tan**: Phân tích liên kết Hydrogen, độ tan của tinh dầu trong Ethanol 90° và nước cất.\n"
                f"2. **Dự báo Độ lưu & tỏa hương**: Đánh giá thực tế dựa trên % tổng tinh dầu và 3 tầng hương.\n"
                f"3. **Gợi ý tinh chỉnh**: Đề xuất tăng/giảm nhẹ thành phần nào cho mùi hương hoàn hảo hơn.\n"
                f"4. **Lưu ý an toàn Lab**: Nhắc nhở ngắn gọn."
            )
            full_rep = st.write_stream(ask_real_gemini_stream(report_prompt))
            st.session_state["gemini_analysis_result"] = full_rep
        elif "gemini_analysis_result" in st.session_state:
            st.markdown("---")
            st.markdown("#### 📋 Đánh Giá Chuyên Môn Từ AI:")
            st.markdown(st.session_state["gemini_analysis_result"])

    with tab_chat:
        col_c1, col_c2, col_c3 = st.columns([2.5, 1.5, 1])
        with col_c1:
            st.caption("💬 Hỏi đáp bằng chữ hoặc bấm Mic nói trực tiếp:")
        with col_c2:
            enable_tts = st.toggle("🔊 AI đọc giọng nói", value=True)
        with col_c3:
            if st.button("🗑️ Xóa chat", use_container_width=True):
                st.session_state.stem_chat_history = []
                st.rerun()

        if "stem_chat_history" not in st.session_state:
            st.session_state.stem_chat_history = []

        # 1. Khung chứa tin nhắn ở TRÊN
        chat_box = st.container(height=420, border=True)
        with chat_box:
            if not st.session_state.stem_chat_history:
                st.info("👋 Chào bạn! Hãy gõ câu hỏi hoặc bấm nút Mic bên dưới để trò chuyện.")
            for msg in st.session_state.stem_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # 2. Thanh công cụ nhập liệu ở DƯỚI CÙNG (Gồm cả Mic thu âm + Ô gõ chữ)
        voice_audio = st.audio_input("🎙️ Bấm biểu tượng Mic để nói câu hỏi (nói xong bấm dừng):")
        user_q = st.chat_input("Hoặc nhập câu hỏi bất kỳ của bạn tại đây...")

        sys_instruct = (
            "Bạn là trợ lý AI chuyên gia trong dự án STEM Hóa học 12 điều chế nước hoa. "
            "Hãy trả lời trực tiếp, súc tích, dễ hiểu và đúng trọng tâm câu hỏi của người dùng. "
            f"Thông số công thức hiện tại:\n{formula_context}"
        )

        # Trường hợp 1: Người dùng gõ chữ
        if user_q:
            st.session_state.stem_chat_history.append({"role": "user", "content": user_q})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(user_q)
                with st.chat_message("assistant"):
                    convo_lines = [f"{'Người dùng' if m['role']=='user' else 'AI'}: {m['content']}" for m in st.session_state.stem_chat_history[-10:]]
                    convo_prompt = "\n\n".join(convo_lines) + "\n\nAI:"
                    reply_text = st.write_stream(ask_real_gemini_stream(convo_prompt, system_instruction=sys_instruct))
                    st.session_state.stem_chat_history.append({"role": "assistant", "content": reply_text})
                    if enable_tts:
                        speak_vietnamese(reply_text)

        # Trường hợp 2: Người dùng nói vào Mic
        elif voice_audio is not None:
            audio_bytes = voice_audio.read()
            # Tránh xử lý lặp lại cùng 1 file ghi âm khi Streamlit rerun
            if st.session_state.get("last_audio_bytes") != audio_bytes:
                st.session_state["last_audio_bytes"] = audio_bytes
                st.session_state.stem_chat_history.append({"role": "user", "content": "🎙️ *[Đã gửi câu hỏi bằng giọng nói]*"})
                with chat_box:
                    with st.chat_message("user"):
                        st.markdown("🎙️ *[Đã gửi câu hỏi bằng giọng nói]*")
                    with st.chat_message("assistant"):
                        try:
                            client = get_cached_client()
                            models_to_try = get_fast_model_list()
                            res = client.models.generate_content(
                                model=models_to_try[0],
                                contents=[
                                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                                    "Hãy nghe câu hỏi tiếng Việt trong đoạn thu âm này và trả lời ngắn gọn, súc tích."
                                ],
                                config=types.GenerateContentConfig(system_instruction=sys_instruct)
                            )
                            reply_text = res.text if (res and res.text) else "Mình chưa nghe rõ, bạn nói lại nhé!"
                        except Exception as e:
                            reply_text = f"⚠️ Lỗi xử lý âm thanh: {e}"
                        
                        st.markdown(reply_text)
                        st.session_state.stem_chat_history.append({"role": "assistant", "content": reply_text})
                        if enable_tts:
                            speak_vietnamese(reply_text)

    with tab_view:
        st.code(formula_context, language="markdown")
