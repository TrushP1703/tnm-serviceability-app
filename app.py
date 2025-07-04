import streamlit as st
import pandas as pd

# Google Sheet CSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)

# Page Config
st.set_page_config(page_title="TNM Serviceability Checker", layout="centered")
st.markdown("<h1 style='text-align: center;'>📦 TNM Serviceability Checker</h1>", unsafe_allow_html=True)
st.markdown("#### Easily check if a pincode is serviceable by your selected service type.")

# Styling tweaks for mobile-friendly look
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
        }
        .stTextInput>div>input {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Input form
agent_type = st.selectbox("🧍 Agent Type", ["Online", "Inbound", "Outbound"])
service_type = st.selectbox("🛠️ Service Type", ["4W_Tyre", "4W_Battery", "2W_Tyre", "2W_Battery"])
pincode = st.text_input("📮 Enter Pincode")

# Button to check serviceability
if st.button("🔍 Check Serviceability"):

    # Validate Pincode
    if not pincode.strip().isdigit():
        st.error("🚫 Invalid pincode. Enter a number like 400001.")
    else:
        pincode_int = int(pincode)
        row = df[df["Pincode"] == pincode_int]

        if row.empty:
            st.error("❌ Not Serviceable")
        else:
            row = row.iloc[0]

            # Serviceability mapping
            service_col_map = {
                "4W_Tyre": "4W Tyre Order",
                "4W_Battery": "4W Battery Order",
                "2W_Tyre": "2W Tyre Order",
                "2W_Battery": "2W Battery Order",
            }

            fitment_map = {
                "4W_Tyre": "4W Tyre (vendor fitment)",
                "4W_Battery": "Battery (vendor fitment)",
                "2W_Battery": "Battery (vendor fitment)",  # same col used for both batteries
            }

            fitment_fee_map = {
                "4W_Tyre": "Extra fitment fees 4W Tyre if applicable in Rs.",
                "4W_Battery": "Extra fitment fees 4W Battery if applicable in Rs.",
                "2W_Tyre": "Extra fitment fees 2W Tyre if applicable in Rs.",
                "2W_Battery": "Extra fitment fees 2W Battery if applicable in Rs.",
            }

            serviceable = row[service_col_map[service_type]].strip().lower() == "yes"

            # Logic: Special case for Online + only 4W Tyre = Yes
            if agent_type == "Online":
                is_only_4w_tyre = (
                    row["4W Tyre Order"].strip().lower() == "yes" and
                    row["4W Battery Order"].strip().lower() == "no" and
                    row["2W Tyre Order"].strip().lower() == "no" and
                    row["2W Battery Order"].strip().lower() == "no"
                )
                if is_only_4w_tyre and service_type != "4W_Tyre":
                    st.error("❌ Not Serviceable")
                    st.stop()

            if serviceable:
                st.success("✅ Serviceable")

                # 🚚 Vendor Fitment (only for 4W_Tyre and Batteries)
                if service_type in ["4W_Tyre", "4W_Battery", "2W_Battery"]:
                    fitment_value = row.get(fitment_map[service_type], "").strip().lower()
                    if fitment_value == "yes":
                        st.info("🚚 Vendor Fitment Available")
                    else:
                        st.info("🚚 Vendor Fitment Not Available")

                # 💰 Extra Fitment Fee (show only if > 0)
                fee_value = row.get(fitment_fee_map[service_type], 0)
                try:
                    fee = float(fee_value)
                    if fee > 0:
                        st.warning(f"💰 Fitment Fee: ₹{int(fee)}")
                except:
                    pass  # Ignore if invalid

                # 📍 Remark
                show_remark = False
                if service_type == "4W_Tyre":
                    # Special condition for "Only 4W Tyre available"
                    if agent_type == "Online" and (
                        row["4W Tyre Order"].strip().lower() == "yes" and
                        row["4W Battery Order"].strip().lower() == "no" and
                        row["2W Tyre Order"].strip().lower() == "no" and
                        row["2W Battery Order"].strip().lower() == "no"
                    ):
                        st.info("🟡 Remark: Only 4W Tyre available — check with CM before confirming.")
                    elif row["Remark"].strip():
                        show_remark = True

                elif service_type == "4W_Battery" and row["Remark"].strip():
                    show_remark = True

                if show_remark:
                    st.info(f"📍 Remark: {row['Remark']}")

            else:
                st.error("❌ Not Serviceable")
