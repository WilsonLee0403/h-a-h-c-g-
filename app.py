import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(
    page_title="Phòng pha chế nước hoa bốn mùa",
    page_icon="🌸",
    layout="centered"
)

st.title("🌸 Phòng Pha Chế Nước Hoa Bốn Mùa")
st.markdown("*Dự án STEM Hóa học 12 – Tích hợp Lập trình & Dữ liệu an toàn.*")

# 1. Chọn chủ đề mùa
season = st.selectbox(
    "Chọn chủ đề mùa cho mẻ pha chế:",
    ["Mùa xuân (Tươi mới, hoa nở)", "Mùa hạ (Mát, sáng, năng động)", "Mùa thu (Dịu, ấm, sâu lắng)", "Mùa đông (Ấm áp, sang trọng)"]
)

# 2. Nhập thể tích mẻ
volume = st.number_input("Thể tích mẻ nước hoa (mL)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)

st.markdown("---")
st.subheader("🎚️ Điều chỉnh tỷ lệ các thành phần hương liệu")
st.markdown("Điều chỉnh phần trăm (%) cho từng tầng hương (Tổng hàm lượng hương liệu tối đa cho phép theo chuẩn an toàn mẻ học tập là **30%**):")

ingredients_config = {
    "Hương đầu (Top notes)": {"max": 10.0, "value": 5.0, "desc": "Bay hơi nhanh, tạo ấn tượng ban đầu (Cam/Bergamot/Chanh)"},
    "Hương giữa (Heart notes)": {"max": 10.0, "value": 5.0, "desc": "Hương chủ đạo của mẻ (Oải hương/Hoa hồng/Gia vị dịu)"},
    "Hương cuối (Base notes)": {"max": 10.0, "value": 3.0, "desc": "Lưu hương lâu, sâu lắng (Gỗ tuyết tùng/Vanilla/Patchouli)"}
}

rows = []
all_valid_limits = True

for name, rule in ingredients_config.items():
    pct = st.slider(f"{name} (%)", min_value=0.0, max_value=15.0, value=rule["value"], step=0.1, help=rule["desc"])

    is_safe = pct <= rule["max"]
    if not is_safe:
        all_valid_limits = False

    rows.append({
        "Thành phần": name,
        "%": pct,
        "Giới hạn tối đa (%)": rule["max"],
        "mL": round(volume * pct / 100, 2),
        "Trạng thái": "Đạt" if is_safe else "Vượt giới hạn"
    })

fragrance_total = sum(r["%"] for r in rows)
solvent_pct = round(100.0 - fragrance_total, 2)
solvent_ml = round(volume * solvent_pct / 100, 2)

rows.append({
    "Thành phần": "Dung môi (Ethanol/Cồn thực phẩm)",
    "%": solvent_pct,
    "Giới hạn tối đa (%)": 100.0,
    "mL": solvent_ml,
    "Trạng thái": "Đạt" if solvent_pct >= 0 else "Không hợp lệ"
})

df = pd.DataFrame(rows)

st.markdown("---")
st.subheader("📊 Bảng công thức chi tiết quy đổi")
st.dataframe(df.style.format({"%": "{:.2f}%", "Giới hạn tối đa (%)": "{:.1f}%", "mL": "{:.2f} mL"}), use_container_width=True)

is_total_valid = abs(fragrance_total + solvent_pct - 100.0) < 0.01
is_fragrance_allowed = fragrance_total <= 30.0
valid = is_total_valid and is_fragrance_allowed and all_valid_limits and (solvent_pct >= 0)

st.markdown("### 🚦 Trạng thái kiểm duyệt an toàn công thức")
if valid:
    st.success(f"✨ **ĐƯỢC GỬI GV DUYỆT:** Công thức cho **{season}** hoàn toàn hợp lệ (Tổng hương liệu: {fragrance_total:.1f}% ≤ 30%). Bạn có thể tải tệp CSV để nộp cho nhóm dữ liệu hoặc giáo viên.")

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Tải xuống công thức CSV",
        data=csv_data,
        file_name=f"cong_thuc_nuoc_hoa_{season.split()[0].lower()}.csv",
        mime="text/csv"
    )
else:
    st.error("⚠️ **CHƯA HỢP LỆ:** Công thức vi phạm quy tắc an toàn (Tổng hương liệu vượt quá 30% giới hạn học tập hoặc thông số âm). Vui lòng điều chỉnh lại các thanh trượt.")

st.markdown("---")
with st.expander("🤖 Gợi ý khung Prompt tương tác với AI (Dành cho nhóm AI & Dữ liệu)"):
    st.markdown("""
    Sao chép đoạn mẫu dưới đây để đưa cho AI (như ChatGPT/Gemini) khi bạn cần tinh chỉnh công thức dựa trên điểm cảm quan:
    > *“Bạn là trợ lý phân tích dữ liệu mùi hương STEM lớp 12. Dựa trên bảng điểm cảm quan mẫu thử vòng 1 của chủ đề **{}**, hãy đề xuất phương án cải tiến tỉ lệ các tầng hương (tăng/giảm tối đa ±1.0%), đảm bảo tổng hương liệu $\le 30\%$, tổng thể tích $100\%$, không thêm nguyên liệu mới và giải thích lý do dựa trên bằng chứng thực nghiệm.”*
    """.format(season))
