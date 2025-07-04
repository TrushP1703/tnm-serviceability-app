import streamlit as st
import pandas as pd

# Load Google Sheet as CSV
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()

# Streamlit Page Config
st.set_page_config(page_title="TNM Serviceability Checker", layout="centered")
st.markdown("<h1 style='text-align: center;'>📦 TNM Serviceability Checker</h1>", unsafe_allow_html=True)

# Mobile-Friendly Styling
st.markdown("""
    <style>
        .stButton>button { width: 100%; }
        .stTextInput>div>input { font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# Input Controls
service_type = st.selectbox("🛠️ Service Type", ["4W_Tyre", "4W_Battery", "2W_Tyre", "2W_Battery"])
pincode = st.text_input("📮 Enter Pincode")

# Button to trigger check
if st.button("🔍 Check Serviceability"):

    if not pincode.strip().isdigit():
        st.error("🚫 Invalid pincode. Enter a number like 400001.")
    else:
        pincode_int = int(pincode)
        row = df[df["Pincode"] == pincode_int]

        if row.empty:
            st.error("❌ Not Serviceable")
        else:
            row = row.iloc[0]

            # Column Mappings
            service_col_map = {
                "4W_Tyre": "4W Tyre Order",
                "4W_Battery": "4W Battery Order",
                "2W_Tyre": "2W Tyre Order",
                "2W_Battery": "2W Battery Order",
            }

            fitment_map = {
                "4W_Tyre": "4W Tyre (vendor fitment)",
                "4W_Battery": "Battery (vendor fitment)",
                "2W_Battery": "Battery (vendor fitment)",
            }

            fee_map = {
                "4W_Tyre": "Extra fitment fees 4W Tyre if applicable in Rs.",
                "4W_Battery": "Extra fitment fees 4W Battery if applicable in Rs.",
                "2W_Tyre": "Extra fitment fees 2W Tyre if applicable in Rs.",
                "2W_Battery": "Extra fitment fees 2W Battery if applicable in Rs.",
            }

            serviceable = row[service_col_map[service_type]].strip().lower() == "yes"

            if serviceable:
                st.success("✅ Serviceable")

                # 🚚 Vendor Fitment (only for 4W/2W Battery and 4W Tyre)
                if service_type in fitment_map:
                    fitment = row.get(fitment_map[service_type], "").strip().lower()
                    if fitment == "yes":
                        st.info("🚚 Vendor Fitment Available")
                    else:
                        st.info("🚚 Vendor Fitment Not Available")

                # 💰 Extra Fitment Fee (if > 0)
                fee_val = row.get(fee_map[service_type], "0")
                try:
                    fee = float(fee_val)
                    if fee > 0:
                        st.warning(f"💰 Fitment Fee: ₹{int(fee)}")
                except:
                    pass  # Ignore if fee can't be parsed

                # 📝 Remark Logic
                show_remark = False
                is_only_4w_tyre = (
                    row["4W Tyre Order"].strip().lower() == "yes" and
                    row["4W Battery Order"].strip().lower() == "no" and
                    row["2W Tyre Order"].strip().lower() == "no" and
                    row["2W Battery Order"].strip().lower() == "no"
                )

                if service_type == "4W_Tyre" and is_only_4w_tyre:
                    st.info("🟡 Remark: Only 4W Tyre available — check with CM before confirming.")
                elif service_type in ["4W_Tyre", "4W_Battery"] and row["Remark"].strip():
                    show_remark = True
                elif service_type in ["2W_Tyre", "2W_Battery"] and serviceable and row["Remark"].strip():
                    show_remark = True

                if show_remark:
                    st.info(f"📍 Remark: {row['Remark']}")

            else:
                st.error("❌ Not Serviceable")
