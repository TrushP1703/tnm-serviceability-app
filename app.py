import streamlit as st
import pandas as pd

# Load data from Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()

# Streamlit App Config for Mobile
st.set_page_config(page_title="TNM Service Check", page_icon="📦", layout="centered")

# 🔹 Title
st.markdown("## 📦 TNM Serviceability Checker")
st.markdown("Check if a pincode is serviceable by service type:")

# Inputs: Minimal layout for mobile
agent_type = st.selectbox("👤 Agent Type", ["Online", "Inbound", "Outbound"])
service_type = st.selectbox("🔧 Service Type", ["4W_Tyre", "4W_Battery", "2W_Tyre", "2W_Battery"])
pincode = st.text_input("📮 Enter Pincode")

# 🔘 Button
if st.button("🔍 Check Serviceability"):
    service_column_map = {
        "4W_Tyre": "4W Tyre Order",
        "4W_Battery": "4W Battery Order",
        "2W_Tyre": "2W Tyre Order",
        "2W_Battery": "2W Battery Order",
    }

    fitment_column_map = {
        "4W_Tyre": "4W Tyre (vendor fitment)",
        "4W_Battery": "Battery (vendor fitment)",
        "2W_Tyre": None,
        "2W_Battery": "Battery (vendor fitment)",
    }

    fee_column_map = {
        "4W_Tyre": "Extra fitment fees 4W Tyre if applicable in Rs.",
        "4W_Battery": "Extra fitment fees 4W Battery if applicable in Rs.",
        "2W_Tyre": "Extra fitment fees 2W Tyre if applicable in Rs.",
        "2W_Battery": "Extra fitment fees 2W Battery if applicable in Rs.",
    }

    try:
        pincode_int = int(pincode)
        row = df[df["Pincode"] == pincode_int]

        if row.empty:
            st.error("❌ Not Serviceable")
        else:
            row = row.iloc[0]
            service_status = row[service_column_map[service_type]].strip().lower()

            only_4w_tyre = (
                row["4W Tyre Order"].strip().lower() == "yes"
                and row["4W Battery Order"].strip().lower() == "no"
                and row["2W Tyre Order"].strip().lower() == "no"
                and row["2W Battery Order"].strip().lower() == "no"
            )

            if agent_type == "Online" and only_4w_tyre and service_type != "4W_Tyre":
                st.error("❌ Not Serviceable")
            elif service_status == "yes":
                st.success("✅ Serviceable")

                # Vendor Fitment
                fitment_column = fitment_column_map.get(service_type)
                if fitment_column:
                    fitment = row[fitment_column]
                    if isinstance(fitment, str) and fitment.strip().lower() == "yes":
                        st.info("🚚 Vendor Fitment Available")
                    else:
                        st.info("🚚 Vendor Fitment Not Available")

                # Fitment Fee
                fee_column = fee_column_map.get(service_type)
                if fee_column:
                    fee = row[fee_column]
                    if pd.notna(fee) and float(fee) > 0:
                        st.info(f"💰 Extra Fitment Fee: ₹{int(float(fee))}")

                # Remarks
                if service_type == "4W_Tyre" and only_4w_tyre:
                    st.warning("📝 Only 4W Tyre available — check with CM before confirming.")
                elif service_type in ["4W_Tyre", "4W_Battery", "2W_Tyre", "2W_Battery"]:
                    remark = row["Remark"]
                    if isinstance(remark, str) and remark.strip():
                        st.info(f"📝 {remark}")
            else:
                st.error("❌ Not Serviceable")

    except ValueError:
        st.error("🚫 Invalid pincode. Enter a number like 400001.")
