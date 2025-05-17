import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

import streamlit as st
from datetime import datetime
import pandas as pd

# ===== SETUP GIAO DIỆN =====
st.set_page_config(page_title="TikTok Dashboard", layout="wide", page_icon="📊")

# ===== CSS tuỳ chỉnh =====
st.markdown(
    """
    <style>
        /* Tổng thể */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h3, h4 {
            color: #333333;
        }
        .centered {
            text-align: center;
        }
        .upload-box {
            border: 2px dashed #cccccc;
            padding: 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ===== HEADER =====
col_logo, col_title, col_empty = st.columns([1, 4, 1])
with col_logo:
    st.image(
        "https://raw.githubusercontent.com/CaptainCattt/Report_of_shopee/main/logo-lamvlog.png",
        width=120,
    )
with col_title:
    st.markdown(
        """
        <div style='display: flex; justify-content: center; align-items: center; gap: 10px;'>
            <img src='https://img.icons8.com/?size=100&id=118638&format=png&color=000000' width='40'/>
            <h1 style='margin: 0;'>DASHBOARD BÁO CÁO TIKTOK</h1>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown(
    "<hr style='margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True
)

# ===== UPLOAD FILE =====
st.markdown("### 📤 Tải lên dữ liệu", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "<div class='upload-box'><h4 class='centered'>📁 File tất cả đơn hàng</h4>",
        unsafe_allow_html=True,
    )
    file_all = st.file_uploader("Chọn file Excel", type=["xlsx", "xls"], key="file_all")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        "<div class='upload-box'><h4 class='centered'>💰 File doanh thu TikTok</h4>",
        unsafe_allow_html=True,
    )
    file_income = st.file_uploader(
        "Chọn file Excel", type=["xlsx", "xls"], key="file_income"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ===== LỌC THEO NGÀY =====
st.markdown(
    """
    <br>
    <h4>📅 Chọn khoảng ngày cần phân tích <span style='font-weight: normal;'>(tuỳ chọn)</span></h4>
""",
    unsafe_allow_html=True,
)

col3, col4 = st.columns(2)
with col3:
    ngay_bat_dau = st.date_input("🔰 Ngày bắt đầu", value=datetime.now().date())
with col4:
    ngay_ket_thuc = st.date_input("🏁 Ngày kết thúc", value=datetime.now().date())

ngay_bat_dau = pd.to_datetime(ngay_bat_dau)
ngay_ket_thuc = pd.to_datetime(ngay_ket_thuc)


# ===== XỬ LÝ FILE =====
def read_file_tiktok(df_all, df_income, ngay_bat_dau, ngay_ket_thuc):
    df_income.columns = df_income.columns.str.strip()
    df_income["ABS_Total_Fees"] = df_income["Total fees"].abs()

    df_income["Classify"] = (
        df_income["Related order ID"]
        .duplicated(keep=False)
        .map({True: "Duplicate", False: "Not Duplicate"})
    )

    df_income["Paydouble"] = df_income.duplicated(
        subset=["Related order ID", "Order/adjustment ID"], keep=False
    ).map({True: "Yes", False: "No"})

    df_income["Order/adjustment ID"] = df_income["Order/adjustment ID"].astype(str)
    df_income["Related order ID"] = df_income["Related order ID"].astype(str)

    df_income["OID_start7"] = (
        df_income["Order/adjustment ID"].astype(str).str.startswith("7")
    )
    df_income["Not_Order_Type"] = df_income["Type"].astype(str) != "Order"

    df_income["RID_count"] = df_income.groupby("Related order ID")[
        "Related order ID"
    ].transform("count")

    grouped = df_income.groupby("Related order ID")
    is_compensation = grouped["OID_start7"].transform("any") | grouped[
        "Not_Order_Type"
    ].transform("any")
    is_doublepaid = (df_income["RID_count"] > 1) & ~is_compensation

    df_income["Actually Order Type"] = "Normal"  # Mặc định là Normal
    df_income.loc[is_compensation, "Actually Order Type"] = "Compensation"
    df_income.loc[is_doublepaid, "Actually Order Type"] = "DoublePaid"

    df_income.drop(columns=["OID_start7", "Not_Order_Type", "RID_count"], inplace=True)

    df_income = df_income.groupby("Order/adjustment ID", as_index=False).agg(
        {
            "Type": "first",
            "Order created time": "first",
            "Order settled time": "first",
            "Currency": "first",
            "Total settlement amount": "sum",
            "Total revenue": "sum",
            "Subtotal after seller discounts": "sum",
            "Subtotal before discounts": "sum",
            "Seller discounts": "sum",
            "Refund subtotal after seller discounts": "sum",
            "Refund subtotal before seller discounts": "sum",
            "Refund of seller discounts": "sum",
            "Total fees": "sum",
            "Transaction fee": "sum",
            "Seller shipping fee": "sum",
            "Actual shipping fee": "sum",
            "Platform shipping fee discount": "sum",
            "Customer shipping fee": "sum",
            "Refund customer shipping fee": "sum",
            "Actual return shipping fee": "sum",
            "TikTok Shop commission fee": "sum",
            "Shipping fee subsidy": "sum",
            "Affiliate commission": "sum",
            "Affiliate commission before PIT (personal income tax)": "sum",
            "Personal income tax withheld from affiliate commission": "sum",
            "Affiliate Shop Ads commission": "sum",
            "Affiliate Shop Ads Commission before PIT": "sum",
            "Personal income tax withheld from affiliate Shop Ads commission": "sum",
            "Affiliate partner commission": "sum",
            "SFP service fee": "sum",
            "LIVE Specials Service Fee": "sum",
            "Voucher Xtra Service Fee": "sum",
            "Flash Sale service fee": "sum",
            "Bonus cashback service fee": "sum",
            "Ajustment amount": "sum",
            "Related order ID": "first",  # Giữ lại giá trị đầu tiên
            "Customer payment": "sum",
            "Customer refund": "sum",
            "Seller co-funded voucher discount": "sum",
            "Refund of seller co-funded voucher discount": "sum",
            "Platform discounts": "sum",
            "Refund of platform discounts": "sum",
            "Platform co-funded voucher discounts": "sum",
            "Refund of platform co-funded voucher discounts": "sum",
            "Seller shipping fee discount": "sum",
            "Estimated package weight (g)": "max",  # Tính trung bình nếu là trọng lượng
            "Actual package weight (g)": "max",  # Tính trung bình nếu là trọng lượng
            "ABS_Total_Fees": "sum",
            "Classify": "first",  # Giữ lại giá trị phân loại của dòng đầu tiên
            "Paydouble": "first",
            "Actually Order Type": "first",
        }
    )

    # Data all

    df_all["Order ID"] = df_all["Order ID"].astype(str)

    # Chuẩn hóa cột Province và Country cho df_all
    df_all["Province"] = df_all["Province"].str.replace(
        r"^(Tỉnh |Tinh )", "", regex=True
    )
    df_all["Province"] = df_all["Province"].str.replace(
        r"^(Thanh pho |Thành phố |Thành Phố )", "", regex=True
    )

    df_all["Country"] = df_all["Country"].replace(
        {
            "Viêt Nam",
            "Vietnam",
            "The Socialist Republic of Viet Nam",
            "Socialist Republic of Vietnam",
        },
        "Việt Nam",
    )

    df_all["Province"] = df_all["Province"].replace(
        {
            "Ba Ria– Vung Tau": "Bà Rịa - Vũng Tàu",
            "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
            "Ba Ria - Vung Tau": "Bà Rịa - Vũng Tàu",
            "Bac Giang": "Bắc Giang",
            "Bac Lieu": "Bạc Liêu",
            "Bac Ninh": "Bắc Ninh",
            "Ben Tre": "Bến Tre",
            "Binh Dinh": "Bình Định",
            "Binh Duong": "Bình Dương",
            "Binh Duong Province": "Bình Dương",
            "Binh Phuoc": "Bình Phước",
            "Binh Thuan": "Bình Thuận",
            "Ca Mau": "Cà Mau",
            "Ca Mau Province": "Cà Mau",
            "Can Tho": "Cần Thơ",
            "Phố Cần Thơ": "Cần Thơ",
            "Da Nang": "Đà Nẵng",
            "Da Nang City": "Đà Nẵng",
            "Phố Đà Nẵng": "Đà Nẵng",
            "Dak Lak": "Đắk Lắk",
            "Đắc Lắk": "Đắk Lắk",
            "Ðắk Nông": "Đắk Nông",
            "Đắk Nông": "Đắk Nông",
            "Dak Nong": "Đắk Nông",
            "Dong Nai": "Đồng Nai",
            "Dong Nai Province": "Đồng Nai",
            "Dong Thap": "Đồng Tháp",
            "Dong Thap Province": "Đồng Tháp",
            "Ha Nam": "Hà Nam",
            "Ha Noi": "Hà Nội",
            "Ha Noi City": "Hà Nội",
            "Phố Hà Nội": "Hà Nội",
            "Hai Phong": "Hải Phòng",
            "Phố Hải Phòng": "Hải Phòng",
            "Ha Tinh": "Hà Tĩnh",
            "Hau Giang": "Hậu Giang",
            "Hô-Chi-Minh-Ville": "Hồ Chí Minh",
            "Ho Chi Minh": "Hồ Chí Minh",
            "Ho Chi Minh City": "Hồ Chí Minh",
            "Kota Ho Chi Minh": "Hồ Chí Minh",
            "Hoa Binh": "Hòa Bình",
            "Hoà Bình": "Hòa Bình",
            "Hung Yen": "Hưng Yên",
            "Khanh Hoa": "Khánh Hòa",
            "Khanh Hoa Province": "Khánh Hòa",
            "Khánh Hoà": "Khánh Hòa",
            "Kien Giang": "Kiên Giang",
            "Kiến Giang": "Kiên Giang",
            "Long An Province": "Long An",
            "Nam Dinh": "Nam Định",
            "Nghe An": "Nghệ An",
            "Ninh Binh": "Ninh Bình",
            "Ninh Thuan": "Ninh Thuận",
            "Quang Binh": "Quảng Bình",
            "Quang Tri": "Quảng Trị",
            "Quang Nam": "Quảng Nam",
            "Quang Ngai": "Quảng Ngãi",
            "Quang Ninh": "Quảng Ninh",
            "Quang Ninh Province": "Quảng Ninh",
            "Soc Trang": "Sóc Trăng",
            "Tay Ninh": "Tây Ninh",
            "Thai Binh": "Thái Bình",
            "Thanh Hoa": "Thanh Hóa",
            "Thanh Hoá": "Thanh Hóa",
            "Hai Duong": "Hải Dương",
            "Thừa Thiên Huế": "Thừa Thiên-Huế",
            "Thua Thien Hue": "Thừa Thiên-Huế",
            "Vinh Long": "Vĩnh Long",
            "Tra Vinh": "Trà Vinh",
            "Vinh Phuc": "Vĩnh Phúc",
            "Cao Bang": "Cao Bằng",
            "Lai Chau": "Lai Châu",
            "Ha Giang": "Hà Giang",
            "Lam Dong": "Lâm Đồng",
            "Lao Cai": "Lào Cai",
            "Phu Tho": "Phu Tho",
            "Phu Yen": "Phú Yên",
            "Thai Nguyen": "Thái Nguyên",
            "Son La": "Sơn La",
            "Tuyen Quang": "Tuyên Quang",
            "Yen Bai": "Yên Bái",
            "Dien Bien": "Điện Biên",
            "Tien Giang": "Tiền Giang",
        }
    )

    # Chuẩn hóa SKU Category
    df_all["SKU Category"] = df_all["Seller SKU"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX|SC_COMBO_MIX_LIVESTREAM|COMBO-SC_LIVESTREAM)$": "COMBO-SC",
        r"^SC_X1$": "SC-450g",
        r"^SC_X2$": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1|SC_COMBO_X1_LIVESTREAM|COMBO-SCX1|COMBO-SCX1_LIVESTREAM)$": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2|SC_COMBO_X2_LIVESTREAM|COMBO-SCX2|COMBO-SCX2_LIVESTREAM)$": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)$": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)$": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix)$": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay)$": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay)$": "BTHP-COMBO-CAY",
        r"^BTHP-COMBO\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP-COMBO\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^BTHP_COMBO_MIX\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP_COMBO_MIX\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^(BTHP-2Cay-2KhongCay)$": "COMBO_4BTHP",
        r"^(BTHP-4Hu-KhongCay)$": "4BTHP_0CAY",
        r"^(BTHP-4Hu-Cay)$": "4BTHP_CAY",
    }

    for pattern, replacement in replacements.items():
        df_all["SKU Category"] = df_all["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )

    date_columns = [
        "Created Time",
        "Paid Time",
        "RTS Time",
        "Shipped Time",
        "Delivered Time",
        "Cancelled Time",
    ]

    # Ép kiểu về datetime
    df_all[date_columns] = df_all[date_columns].apply(
        lambda col: pd.to_datetime(col, errors="coerce", format="%d/%m/%Y %H:%M:%S")
    )

    # Loại bỏ giờ, giữ lại phần ngày (vẫn là kiểu datetime)
    for col in date_columns:
        df_all[col] = df_all[col].dt.normalize()

    df_merged = pd.merge(
        df_income,
        df_all,
        how="left",
        right_on="Order ID",
        left_on="Related order ID",
    )

    df_merged["Order settled time"] = pd.to_datetime(
        df_merged["Order settled time"], errors="coerce"
    )

    df_main = df_merged[
        (df_merged["Order settled time"] >= ngay_bat_dau)
        & (df_merged["Order settled time"] <= ngay_ket_thuc)
    ]

    Don_hoan_thannh = df_main[
        (df_main["Total revenue"] > 0) & (df_main["Actually Order Type"] == "Normal")
    ]

    Don_dieu_chinh = df_main[(df_main["Type"] != "Order")]

    # Dieuchinh tru phi
    Don_dieu_chinh_tru_phi = df_main[
        (df_main["Type"] == "Deductions incurred by seller")
    ]

    # Dieu chinh san den bu
    Don_dieu_chinh_san_den_bu = df_main[
        (df_main["Type"].isin(["Logistics reimbursement", "Platform reimbursement"]))
    ]

    # Don thanh toan truoc
    Don_thanh_toan_truoc = df_main[
        (df_main["Type"] == "Order") & (df_main["Actually Order Type"] == "DoublePaid")
    ]

    # Don hoan tra
    Don_hoan_tra = df_main[
        (df_main["Type"] == "Order")
        & (df_main["Sku Quantity of return"] != 0)
        & (df_main["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_main["Classify"] == "Not Duplicate")
    ]

    # Don boom
    Don_boom = df_main[
        (df_main["Type"] == "Order")
        & (df_main["Cancelation/Return Type"] == "Cancel")
        & (df_main["Total revenue"] <= 0)
    ]

    return (
        df_all,
        df_income,
        df_merged,
        df_main,
        Don_hoan_thannh,
        Don_dieu_chinh,
        Don_hoan_tra,
        Don_boom,
    )


if "processing" not in st.session_state:
    st.session_state.processing = False

# Nút xử lý
process_btn = st.button("🔍 Xử lý dữ liệu", disabled=st.session_state.processing)

if process_btn:
    if file_all and file_income:
        with st.spinner("⏳ Đang xử lý dữ liệu, vui lòng chờ..."):
            df_all = pd.read_excel(file_all)
            df_income = pd.read_excel(file_income)

            (
                df_all,
                df_income,
                df_merged,
                df_main,
                Don_hoan_thannh,
                Don_dieu_chinh,
                Don_hoan_tra,
                Don_boom,
            ) = read_file_tiktok(df_all, df_income, ngay_bat_dau, ngay_ket_thuc)

            st.success("Đã xử lý xong dữ liệu!")

            st.session_state["Data"] = df_main
            st.session_state["Don_hoan_thanh"] = Don_hoan_thannh
            st.session_state["Don_dieu_chinh"] = Don_dieu_chinh
            st.session_state["Don_hoan_tra"] = Don_hoan_tra
            st.session_state["Don_boom"] = Don_boom

            # Hiển thị bảng các đơn đã quyết toán trong khoảng thời gian
            st.markdown(
                "### 📄 Danh sách các đơn quyết toán trong khoảng thời gian đã chọn:"
            )
            st.dataframe(df_main)

            st.markdown("### 📄 Danh sách các đơn hoàn thành:")
            st.dataframe(Don_hoan_thannh)

            st.markdown("### 📄 Danh sách các đơn điều chỉnh:")
            st.dataframe(Don_dieu_chinh)

            st.markdown("### 📄 Danh sách các đơn hoàn trả:")
            st.dataframe(Don_hoan_tra)

            st.markdown("### 📄 Danh sách các đơn hủy:")
            st.dataframe(Don_boom)

            # Hiển thị một vài thông tin cơ bản
            st.subheader("📊 Tổng quan đơn hàng:")
            st.metric(
                "Số đơn hàng đã giao",
                df_main["Order/adjustment ID"].drop_duplicates().nunique(),
            )
            # Loại bỏ dòng trùng theo mã đơn hàng
            # Loại bỏ các dòng trùng theo Order/adjustment ID
            Don_quyet_toan_unique = df_main.drop_duplicates(
                subset="Order/adjustment ID"
            )
            col1, col2, col3 = st.columns(3)

            with col1:
                total_revenue = Don_quyet_toan_unique["Total revenue"].sum()
                st.markdown(
                    f"""
                    <div style="font-size:28px; font-weight:bold; color:#00BFFF;">
                        📈 Tổng doanh thu
                    </div>
                    <div style="font-size:36px; font-weight:bold;">
                        {total_revenue:,.0f} đ
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                Total_settlement_amount = Don_quyet_toan_unique[
                    "Total settlement amount"
                ].sum()
                st.markdown(
                    f"""
                    <div style="font-size:28px; font-weight:bold; color:#FF6347;">
                        💰 Tổng quyết toán
                    </div>
                    <div style="font-size:36px; font-weight:bold;">
                        {Total_settlement_amount:,.0f} đ
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col3:
                Total_fees = Don_quyet_toan_unique["ABS_Total_Fees"].sum()
                st.markdown(
                    f"""
                    <div style="font-size:28px; font-weight:bold; color:#DC143C;">
                        💸 Tổng chi phí
                    </div>
                    <div style="font-size:36px; font-weight:bold;">
                        {Total_fees:,.0f} đ
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Chuyển datetime thành chỉ ngày (nếu cần)
            Don_quyet_toan_unique["Ngày"] = Don_quyet_toan_unique[
                "Order settled time"
            ].dt.date

            # Tổng doanh thu theo ngày
            doanhthu_theo_ngay = (
                Don_quyet_toan_unique.groupby("Ngày")["Total revenue"]
                .sum()
                .reset_index()
            )

            # Vẽ biểu đồ miền
            fig_doanhthu = px.area(
                doanhthu_theo_ngay,
                x="Ngày",
                y="Total revenue",
                title="📈 Doanh thu theo ngày",
                labels={"Ngày": "Ngày", "Total revenue": "Tổng doanh thu"},
            )

            # Hiển thị
            st.plotly_chart(fig_doanhthu, use_container_width=True)

            fig_cost = px.area(
                Don_quyet_toan_unique,
                x="Order settled time",
                y="ABS_Total_Fees",  # ✅ Cột chi phí
                title="💸 Chi phí theo ngày",
                labels={"Order settled time": "Ngày", "ABS_Total_Fees": "Chi phí"},
            )
            fig_cost.update_traces(
                line_color="#FF6347", fillcolor="rgba(255,99,71,0.4)"
            )
            fig_cost.update_layout(xaxis_title="Ngày", yaxis_title="Chi phí")
            st.plotly_chart(fig_cost, use_container_width=True)

            # Số lượng sản phẩm theo từng SKU
            fig_sanpham = px.histogram(
                Don_hoan_thannh,
                x="SKU Category",
                y="Quantity",
                color="SKU Category",  # Mỗi SKU sẽ có màu khác nhau
                title="Phân phối SKU theo số lượng sản phẩm",
                labels={"Quantity": "Tổng số lượng"},
            )

            st.plotly_chart(fig_sanpham, use_container_width=True)

            doanh_thu_theo_tinh = (
                Don_quyet_toan_unique.groupby("Province")["Total revenue"]
                .sum()
                .reset_index()
                .sort_values(by="Total revenue", ascending=False)
            )

            # Thêm cột phân loại top 10
            doanh_thu_theo_tinh["Top10"] = [
                "Top 10" if i < 10 else "Khác" for i in range(len(doanh_thu_theo_tinh))
            ]

            # Vẽ biểu đồ cột với màu theo top 10
            fig_tinh = px.bar(
                doanh_thu_theo_tinh,
                x="Province",
                y="Total revenue",
                color="Top10",
                color_discrete_map={"Top 10": "#EF553B", "Khác": "#636EFA"},
                title="🏙️ Doanh thu theo tỉnh thành (Top 10 nổi bật)",
                labels={"Province": "Tỉnh/Thành", "Total revenue": "Tổng doanh thu"},
                text_auto=".2s",
            )

            st.plotly_chart(fig_tinh, use_container_width=True)

            don_sanpham = (
                Don_quyet_toan_unique.groupby("Buyer Username")
                .agg(
                    So_don=("Order/adjustment ID", "count"),
                    Tong_san_pham=("Quantity", "sum"),
                )
                .reset_index()
                .sort_values(by="So_don", ascending=False)
            )

            col4, col5 = st.columns(2)

            # --- Biểu đồ 1: Top 20 theo số đơn ---
            with col4:
                top_20_don = don_sanpham.sort_values("So_don", ascending=False).head(20)
                df_don = top_20_don[["Buyer Username", "So_don"]].copy()
                df_don = df_don.rename(columns={"So_don": "Số lượng"})
                df_don["Chỉ số"] = "Số đơn"

                fig_don = px.bar(
                    df_don,
                    x="Buyer Username",
                    y="Số lượng",
                    color_discrete_sequence=["#1f77b4"],  # Màu xanh dương
                    title="📦 Top 20 người mua theo số đơn hàng",
                    labels={"Buyer Username": "Người mua"},
                )
                fig_don.update_layout(xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig_don, use_container_width=True)

            # --- Biểu đồ 2: Top 20 theo số lượng sản phẩm ---
            with col5:
                top_20_sanpham = don_sanpham.sort_values(
                    "Tong_san_pham", ascending=False
                ).head(20)
                df_sp = top_20_sanpham[["Buyer Username", "Tong_san_pham"]].copy()
                df_sp = df_sp.rename(columns={"Tong_san_pham": "Số lượng"})
                df_sp["Chỉ số"] = "Tổng sản phẩm"

                fig_sp = px.bar(
                    df_sp,
                    x="Buyer Username",
                    y="Số lượng",
                    color_discrete_sequence=["#FF7F0E"],  # Màu cam
                    title="🎁 Top 20 người mua theo số lượng sản phẩm",
                    labels={"Buyer Username": "Người mua"},
                )
                fig_sp.update_layout(xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig_sp, use_container_width=True)

            col6, col7 = st.columns(2)
            with col6:
                df_payment = (
                    Don_quyet_toan_unique["Payment Method"].value_counts().reset_index()
                )
                df_payment.columns = ["Phương thức thanh toán", "Số lượng"]
                fig_pie = px.pie(
                    df_payment,
                    names="Phương thức thanh toán",
                    values="Số lượng",
                    title="💳 Phân phối phương thức thanh toán",
                    color_discrete_sequence=px.colors.sequential.RdBu,
                    hole=0.4,  # Nếu muốn Doughnut chart
                )

                fig_pie.update_traces(textposition="inside", textinfo="percent+label")

                st.plotly_chart(fig_pie, use_container_width=True)

            with col7:
                fig_hoan_tra = px.bar(
                    Don_hoan_tra,
                    x="SKU Category",
                    color="SKU Category",
                    title="📦 Phân phối đơn hoàn trả theo SKU",
                    labels={"count": "Số đơn hoàn trả"},
                )

                # Đếm số đơn theo SKU
                fig_hoan_tra.update_traces(marker_line_width=1)
                fig_hoan_tra.update_layout(showlegend=False)
                st.plotly_chart(fig_hoan_tra, use_container_width=True)

            # ### DOWNLOAD
            # import io
            # import openpyxl

            # # Cho phép tải xuống
            # output = io.BytesIO()
            # with pd.ExcelWriter(output, engine="openpyxl") as writer:
            #     df_main.to_excel(writer, index=False, sheet_name="QuyetToan")
            # output.seek(0)

            # st.download_button(
            #     label="📥 Tải xuống danh sách quyết toán",
            #     data=output,
            #     file_name="df_main.xlsx",
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            # )
# ds_loai_don = [
#     "ĐƠN HÀNG INCOME",
#     "ĐƠN HOÀN THÀNH",
#     "ĐƠN ĐIỀU CHỈNH",
#     "ĐƠN BOOM",
#     "ĐƠN HOÀN TRẢ",
# ]

# # Hiển thị selectbox và cập nhật session_state
# loai_don = st.selectbox("📦 Chọn loại đơn hàng để xem chi tiết:", ds_loai_don)

# # Cập nhật lựa chọn vào session_state
# st.session_state["loai_don_selected"] = loai_don

# # Mapping loại đơn sang DataFrame trong session_state
# mapping = {
#     "ĐƠN HÀNG INCOME": st.session_state.get("Data", pd.DataFrame()),
#     "ĐƠN HOÀN THÀNH": st.session_state.get("Don_hoan_thanh", pd.DataFrame()),
#     "ĐƠN BOOM": st.session_state.get("Don_boom", pd.DataFrame()),
#     "ĐƠN HOÀN TRẢ": st.session_state.get("Don_hoan_tra", pd.DataFrame()),
#     "ĐƠN ĐIỀU CHỈNH": st.session_state.get("Don_dieu_chinh", pd.DataFrame()),
# }

# df_chi_tiet = mapping.get(loai_don, pd.DataFrame())

# # Hiển thị kết quả
# if not df_chi_tiet.empty:
#     st.markdown(f"#### 📋 Danh sách chi tiết {loai_don}")
#     st.dataframe(df_chi_tiet)
# else:
#     st.info("Không có dữ liệu cho loại đơn này.")
