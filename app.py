import streamlit as st
import pandas as pd

# 1. Cấu hình trang Dashboard rộng
st.set_page_config(
    page_title="Phòng Pha Chế Nước Hoa Bốn Mùa - STEM Lab",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Tùy biến: Triệt tiêu con trỏ chèn văn bản (I-beam cursor) & viền đỏ focus
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Ép tất cả các thẻ chọn (Selectbox / Dropdown) dùng con trỏ BÀN TAY (Pointer) */
    div[data-baseweb="select"], 
    div[data-baseweb="select"] *, 
    div[data-baseweb="select"] input {
        cursor: pointer !important;
        caret-color: transparent !important;
        user-select: none !important;
    }
    
    /* Triệt tiêu viền đỏ và viền bóng khi nhấp chuột (Focus Ring) */
    div[data-baseweb="select"]:focus-within,
    div[data-baseweb="select"] > div {
        border-color: #cbd5e0 !important;
        box-shadow: none !important;
    }
    
    /* Style Hero Banner Header */
    .hero-box {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
    }
    
    /* Style Thẻ Chỉ Số Metric */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #2d3748;
    }
    .metric-label {
        font-size: 12px;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 600;
    }
    
    /* Style Thẻ Mùi Hương */
    .profile-card {
        background: #ffffff;
        border: 1px dashed #cbd5e0;
        border-radius: 12px;
        padding: 14px 18px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Cơ sở dữ liệu 4 mùa chuẩn theo dự án STEM
seasons_data = {
    "Xuân": {
        "label": "Mùa Xuân — Tươi Mới & Sắc Hoa",
        "slug": "xuan",
        "icon": "🌸",
        "theme_color": "#d53f8c",
        "desc_profile": "Hương đầu tươi sáng của cam chanh hòa quyện cùng sắc hoa oải hương, phong lữ dịu nhẹ và lớp nền gỗ tuyết tùng mềm mại.",
        "rules": {
            "Bergamot FCF": {"limit": 4.0, "default": 3.8, "tier": "Hương đầu (Top)", "type": "top"},
            "Sweet orange": {"limit": 3.0, "default": 2.0, "tier": "Hương đầu (Top)", "type": "top"},
            "Lavender":     {"limit": 4.0, "default": 3.5, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Geranium":     {"limit": 3.0, "default": 2.5, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Cedarwood":    {"limit": 2.0, "default": 1.3, "tier": "Hương cuối (Base)", "type": "base"},
            "Vanilla accord":{"limit": 1.0, "default": 0.6, "tier": "Hương cuối (Base)", "type": "base"},
        }
    },
    "Hạ": {
        "label": "Mùa Hạ — Sảng Khoái & Năng Động",
        "slug": "ha",
        "icon": "🌊",
        "theme_color": "#3182ce",
        "desc_profile": "Mát lạnh sảng khoái với cam chanh và thảo mộc nổi bật, đánh thức năng lượng với nền gỗ thanh khiết.",
        "rules": {
            "Bergamot FCF": {"limit": 4.0, "default": 3.5, "tier": "Hương đầu (Top)", "type": "top"},
            "Chanh/Bưởi":   {"limit": 4.0, "default": 3.0, "tier": "Hương đầu (Top)", "type": "top"},
            "Lavender":     {"limit": 4.0, "default": 3.0, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Bạc hà (thấp)":{"limit": 1.5, "default": 0.8, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Cedarwood":    {"limit": 2.0, "default": 1.2, "tier": "Hương cuối (Base)", "type": "base"},
            "Vanilla accord":{"limit": 1.0, "default": 0.3, "tier": "Hương cuối (Base)", "type": "base"},
        }
    },
    "Thu": {
        "label": "Mùa Thu — Dịu Êm & Sâu Lắng",
        "slug": "thu",
        "icon": "🍁",
        "theme_color": "#dd6b20",
        "desc_profile": "Cảm giác chuyển mùa mềm mại, ấm áp với hương cam ngọt đằm thắm và nền gỗ tuyết tùng phảng phất vanilla.",
        "rules": {
            "Sweet orange": {"limit": 3.0, "default": 2.5, "tier": "Hương đầu (Top)", "type": "top"},
            "Bergamot FCF": {"limit": 3.0, "default": 1.8, "tier": "Hương đầu (Top)", "type": "top"},
            "Lavender":     {"limit": 4.0, "default": 3.0, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Geranium":     {"limit": 3.0, "default": 2.5, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Cedarwood":    {"limit": 3.0, "default": 2.2, "tier": "Hương cuối (Base)", "type": "base"},
            "Vanilla accord":{"limit": 1.5, "default": 0.9, "tier": "Hương cuối (Base)", "type": "base"},
        }
    },
    "Đông": {
        "label": "Mùa Đông — Ấm Áp & Sang Trọng",
        "slug": "dong",
        "icon": "❄️",
        "theme_color": "#805ad5",
        "desc_profile": "Hương cuối đậm sâu, sang trọng với hợp hương gỗ và vanilla hảo hạng mang lại độ lưu hương vượt trội.",
        "rules": {
            "Bergamot FCF": {"limit": 3.0, "default": 1.8, "tier": "Hương đầu (Top)", "type": "top"},
            "Sweet orange": {"limit": 2.5, "default": 1.5, "tier": "Hương đầu (Top)", "type": "top"},
            "Lavender":     {"limit": 3.5, "default": 2.5, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Geranium":     {"limit": 3.0, "default": 2.0, "tier": "Hương giữa (Heart)", "type": "middle"},
            "Cedarwood":    {"limit": 3.0, "default": 2.5, "tier": "Hương cuối (Base)", "type": "base"},
            "Vanilla accord":{"limit": 2.0, "default": 1.2, "tier": "Hương cuối (Base)", "type": "base"},
        }
    }
}

# 4. THANH ĐIỀU KHIỂN BÊN (SIDEBAR)
with st.sidebar:
    st.markdown("### 🎛️ Bảng Điều Khiển")
    st.markdown("---")
    
    st.markdown("**🌿 Chọn chủ đề mùa:**")
    
    # Nút bấm chọn mùa (Pills) thay cho Selectbox để hoàn toàn không bị con trỏ nhấp văn bản (I-beam)
    season_options = list(seasons_data.keys())
    
    if hasattr(st, "pills"):
        selected_season_key = st.pills(
            "Chủ đề mùa",
            options=season_options,
            format_func=lambda k: f"{seasons_data[k]['icon']} {k}",
            default="Xuân",
            label_visibility="collapsed"
        )
        if not selected_season_key:
            selected_season_key = "Xuân"
    else:
        selected_season_key = st.radio(
            "Chủ đề mùa",
            options=season_options,
            format_func=lambda k: f"{seasons_data[k]['icon']} {seasons_data[k]['label']}",
            index=0,
            label_visibility="collapsed"
        )
    
    season_info = seasons_data[selected_season_key]
    
    st.markdown("---")
    st.markdown("**🧪 Thể tích mẻ (mL):**")
    
    # Cải tiến Sáng tạo: Nút chọn nhanh thể tích thử nghiệm
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    if "selected_vol" not in st.session_state:
        st.session_state.selected_vol = 10.0
        
    with v_col1:
        if st.button("5ml", use_container_width=True):
            st.session_state.selected_vol = 5.0
    with v_col2:
        if st.button("10ml", use_container_width=True):
            st.session_state.selected_vol = 10.0
    with v_col3:
        if st.button("15ml", use_container_width=True):
            st.session_state.selected_vol = 15.0
    with v_col4:
        if st.button("20ml", use_container_width=True):
            st.session_state.selected_vol = 20.0

    volume = st.number_input(
        "Thể tích nhập tùy chỉnh",
        min_value=1.0,
        max_value=20.0,
        value=st.session_state.selected_vol,
        step=0.5,
        label_visibility="collapsed",
        help="Giới hạn an toàn mẻ học tập: 1.0 – 20.0 mL"
    )
    
    st.markdown("---")
    st.markdown("#### 📋 Tiêu chuẩn an toàn")
    st.markdown("""
    - **Thanh trượt Max:** Khóa chuẩn an toàn GV
    - **Nồng độ tinh dầu:** ≤ 30.0%
    - **Dung môi Ethanol:** Tự động bù
    - **Độ chính xác đo:** 3 chữ số (0.001 mL)
    """)

# 5. KHU VỰC CHÍNH (MAIN AREA)
st.markdown(f"""
<div class="hero-box">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin: 0; font-size: 26px; color: #1a202c;">{season_info['icon']} Phòng Pha Chế Nước Hoa Bốn Mùa</h1>
            <p style="margin: 5px 0 0 0; color: #4a5568; font-size: 14px;">Dự án STEM Hóa Học 12 — Thiết kế công thức hương thơm tích hợp Dữ liệu & AI</p>
        </div>
        <span style="background: {season_info['theme_color']}18; color: {season_info['theme_color']}; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 13px;">
            {season_info['label']}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# 6. BỐ CỤC Dashboard 2 CỘT HIỆN ĐẠI
col_left, col_right = st.columns([1.15, 1], gap="large")

rows = []
errors = []

# CỘT TRÁI: Thanh trượt tinh chỉnh tỷ lệ
with col_left:
    st.subheader("🎚️ Điều chỉnh tỷ lệ thành phần")
    st.caption("Kéo thanh trượt để điều chỉnh. Trần an toàn đã được khóa cố định theo chuẩn dự án.")

    tier_groups = {
        "Hương đầu (Top Notes) 🍋": [k for k, v in season_info["rules"].items() if v["type"] == "top"],
        "Hương giữa (Heart Notes) 🌸": [k for k, v in season_info["rules"].items() if v["type"] == "middle"],
        "Hương cuối (Base Notes) 🪵": [k for k, v in season_info["rules"].items() if v["type"] == "base"],
    }

    for group_title, items in tier_groups.items():
        with st.expander(f"**{group_title}**", expanded=True):
            for name in items:
                rule = season_info["rules"][name]
                limit = rule["limit"]
                default_val = rule["default"]
                tier = rule["tier"]

                c_label, c_slider = st.columns([1, 2])
                with c_label:
                    st.markdown(f"<div style='padding-top: 10px; font-weight: 500; font-size: 14px;'>{name}</div>", unsafe_allow_html=True)
                    st.caption(f"Tối đa: {limit:.1f}%")
                with c_slider:
                    pct = st.slider(
                        f"Tỷ lệ {name}",
                        min_value=0.0,
                        max_value=limit,
                        value=default_val,
                        step=0.1,
                        label_visibility="collapsed"
                    )

                if pct > limit:
                    errors.append(f"{name} vượt giới hạn ({limit}%)")

                rows.append({
                    "Thành phần": name,
                    "Tầng hương": tier,
                    "%": pct,
                    "Giới hạn GV (%)": limit,
                    "mL": round(volume * pct / 100, 3)
                })

# Tính toán dung môi và tổng tinh dầu
fragrance_total = sum(r["%"] for r in rows)
solvent_pct = round(100.0 - fragrance_total, 2)
solvent_ml = round(volume * solvent_pct / 100, 3)

if solvent_pct < 0:
    errors.append("Tổng nhóm hương vượt quá 100% (Dung môi bị âm)")
if fragrance_total > 30.0:
    errors.append("Tổng hương liệu vượt quá 30% ngưỡng an toàn mẻ học tập")

rows.append({
    "Thành phần": "Dung môi (Ethanol)",
    "Tầng hương": "Dung môi",
    "%": solvent_pct,
    "Giới hạn GV (%)": 100.0,
    "mL": solvent_ml
})

df = pd.DataFrame(rows)

# CỘT PHẢI: Bảng dữ liệu, Biểu đồ & Thẻ Metric
with col_right:
    st.subheader("📊 Thống kê mẻ pha chế")
    
    # 3 Thẻ Metric hiện đại
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Hương liệu</div>
            <div class="metric-value" style="color: {'#e53e3e' if fragrance_total > 30 else '#319795'};">{fragrance_total:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Dung môi</div>
            <div class="metric-value" style="color: {'#e53e3e' if solvent_pct < 0 else '#2b6cb0'};">{solvent_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        status_text = "Hợp lệ" if not errors else "Lỗi"
        status_color = "#38a169" if not errors else "#e53e3e"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Trạng thái</div>
            <div class="metric-value" style="color: {status_color}; font-size: 20px; line-height: 38px;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Thanh trực quan hóa tỷ lệ nồng độ hương liệu
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    pct_progress = min(max(fragrance_total / 30.0, 0.0), 1.0)
    st.progress(pct_progress, text=f"Nồng độ tinh dầu: {fragrance_total:.1f}% / 30.0% Max")

    # Cải tiến sáng tạo: Biểu đồ phân bổ thể tích (mL) trực quan hóa dữ liệu STEM
    with st.expander("📈 Biểu đồ phân bổ thể tích (mL)", expanded=False):
        chart_df = df[df["Thành phần"] != "Dung môi (Ethanol)"].set_index("Thành phần")["mL"]
        st.bar_chart(chart_df, color=season_info["theme_color"])

    # Bảng chi tiết quy đổi
    st.markdown("**Bảng quy đổi công thức chi tiết:**")
    
    df_display = df.copy()
    df_display["%"] = df_display["%"].map(lambda x: f"{x:.2f}%")
    df_display["Giới hạn GV (%)"] = df_display["Giới hạn GV (%)"].map(lambda x: f"{x:.1f}%")
    df_display["mL"] = df_display["mL"].map(lambda x: f"{x:.3f} mL")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Chú thích an toàn bắt buộc theo chuẩn tài liệu
    st.caption("⚠️ **Chú ý:** Hợp lệ toán học không đồng nghĩa an toàn. Cần giáo viên duyệt trước khi pha.")

    # Thẻ hiển thị hồ sơ mùi hương
    st.markdown(f"""
    <div class="profile-card">
        <span style="font-weight: 600; color: #2d3748;">🌿 Hồ sơ mùi hương:</span>
        <span style="color: #4a5568; font-size: 14px;"> {season_info['desc_profile']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Cải tiến sáng tạo: Trợ lý sinh Prompt AI hỗ trợ phản biện
    with st.expander("🤖 Trợ lý Prompt AI (Sao chép gửi AI phản biện)", expanded=False):
        prompt_text = f"Tôi đang pha mẻ nước hoa {season_info['label']} thể tích {volume} mL với công thức: " + ", ".join([f"{r['Thành phần']}: {r['%']}%" for r in rows if r['Thành phần'] != 'Dung môi (Ethanol)']) + ". Nhờ AI phân tích độ cân bằng 3 tầng hương và gợi ý hướng tối ưu theo đúng nguyên tắc không vượt quá trần an toàn."
        st.code(prompt_text, language="markdown")

    # Trạng thái phê duyệt & Nút tải
    st.markdown("---")
    if not errors:
        st.success(f"✨ **ĐỦ ĐIỀU KIỆN GỬI GIÁO VIÊN DUYỆT:** Công thức mẻ {volume:.1f} mL đã tối ưu.")
        
        # Xuất file CSV chuẩn UTF-8-sig
        export_func = getattr(df, "to_csv")
        csv_bytes = export_func(index=False).encode("utf-8-sig")
        
        dl_button = getattr(st, "download_button")
        dl_button(
            label="📥 Tải công thức nộp kiểm duyệt (CSV)",
            data=csv_bytes,
            file_name=f"cong_thuc_{season_info['slug']}_{int(volume)}ml.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        for err in errors:
            st.error(f"⚠️ {err}")
