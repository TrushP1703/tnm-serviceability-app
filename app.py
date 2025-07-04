import streamlit as st
import pandas as pd

# 🔗 Load data from Google Sheet (make sure it's published as CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()

# ⚙️ Streamlit page settings
st.set_page_config(page_title="TNM Serviceability Lookup Tool", page_icon="📦", layout="centered")
st.title("📦 TNM Serviceability Lookup Tool")
st.subheader("Check Serviceability")

# 🧾 Inputs
agent_type = st.selectbox("Select Agent Type", ["Online", "Inbound", "Outbound"])
service_type = st.selectbox("Select Service Type", ["4W_Tyre", "4W_Battery", "2W_Tyre", "2W_Battery"])
pincode = st.text_input("Enter Pincode")

# 🔘 Trigger logic only on button click
if st.button("🔍 Check Serviceability"):
    # 🔄 Column mappings
    service_column_map = {
        "4W_Tyre": "4W Tyre Order",
        "4W_Battery": "4W Battery Order",
        "2W_Tyre": "2W Tyre Order",
        "2W_Battery": "2W Battery Order",
    }

    # ✅ CHANGE: Add Vendor Fitment support for 4W Tyre, 4W Battery, 2W Battery
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
            st.error("❌ Not Serviceable")  # ✅ CLEAN: Show only this if no match
        else:
            row = row.iloc[0]
            service_status = row[service_column_map[service_type]].strip().lower()

            # 🔎 Check if it's a "4W Tyre Only" pincode
            only_4w_tyre = (
                row["4W Tyre Order"].strip().lower() == "yes"
                and row["4W Battery Order"].strip().lower() == "no"
                and row["2W Tyre Order"].strip().lower() == "no"
                and row["2W Battery Order"].strip().lower() == "no"
            )

            # 🧠 Special logic for Online agents on non-4W_Tyre requests
            if agent_type == "Online" and only_4w_tyre and service_type != "4W_Tyre":
                st.error("❌ Not Serviceable")

            elif service_status == "yes":
                st.success("✅ Serviceable")

                # 🚚 Vendor Fitment (✅ CHANGE: for 4W Tyre, 4W Battery, 2W Battery only)
                fitment_column = fitment_column_map.get(service_type)
                if fitment_column:
                    fitment = row[fitment_column]
                    if isinstance(fitment, str) and fitment.strip().lower() == "yes":
                        st.info("🚚 Vendor Fitment Available")
                    else:
                        st.info("🚚 Vendor Fitment Not Available")

                # 💰 Extra Fitment Fee (✅ Only if non-zero)
                fee_column = fee_column_map.get(service_type)
                if fee_column:
                    fee = row[fee_column]
                    if pd.notna(fee) and float(fee) > 0:
                        st.info(f"💰 Extra Fitment Fee: ₹{int(float(fee))}")

                # 📝 Remark (✅ Only if service is Yes and 4W Tyre/Battery, OR special logic)
                if service_type == "4W_Tyre" and only_4w_tyre:
                    st.warning("📝 Remark: Only 4W Tyre available — check with CM before confirming.")
                elif service_type in ["4W_Tyre", "4W_Battery", "2W_Battery", "2W_Tyre"]:
                    remark = row["Remark"]
                    if isinstance(remark, str) and remark.strip():
                        st.info(f"📝 Remark: {remark}")

            else:
                st.error("❌ Not Serviceable")  # ✅ CLEAN: Show only this if No

    except ValueError:
        st.error("Please enter a valid numeric pincode.")
