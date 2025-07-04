import streamlit as st
import pandas as pd

# Streamlit setup
st.set_page_config(page_title="TNM Serviceability Lookup Tool", page_icon="📦", layout="centered")
st.title("📦 TNM Serviceability Lookup Tool")
st.header("Check Serviceability")

# Load data from Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url, dtype={'Pincode': str})
df.columns = df.columns.str.strip()

# Mapping
service_map = {
    "4W_Tyre": "4W Tyre Order",
    "4W_Battery": "4W Battery Order",
    "2W_Tyre": "2W Tyre Order",
    "2W_Battery": "2W Battery Order"
}

vendor_fitment_map = {
    "4W_Tyre": "4W Tyre (vendor fitment)",
    "4W_Battery": "Battery (vendor fitment)",
    "2W_Tyre": "",  # No vendor fitment
    "2W_Battery": "Battery (vendor fitment)"
}

fitment_fee_map = {
    "4W_Tyre": "Extra fitment fees 4W Tyre if applicable in Rs.",
    "4W_Battery": "Extra fitment fees 4W Battery if applicable in Rs.",
    "2W_Tyre": "Extra fitment fees 2W Tyre if applicable in Rs.",
    "2W_Battery": "Extra fitment fees 2W Battery if applicable in Rs."
}

# Inputs
agent_type = st.selectbox("Select Agent Type", ["Online", "Inbound", "Outbound"])
service_type = st.selectbox("Select Service Type", list(service_map.keys()))
pincode = st.text_input("Enter Pincode")

if pincode:
    if not pincode.strip().isdigit():
        st.error("❌ Invalid pincode. Please enter a numeric value.")
    else:
        df["Pincode"] = df["Pincode"].astype(str).str.strip()
        result = df[df["Pincode"] == pincode.strip()]

        if result.empty:
            st.error("❌ No data found for this pincode.")
        else:
            row = result.iloc[0]
            service_column = service_map[service_type]
            service_status = row[service_column].strip().lower()

            all_services = {
                k: row[v].strip().lower() for k, v in service_map.items()
            }

            only_4w_tyre = (
                all_services["4W_Tyre"] == "yes" and
                all_services["4W_Battery"] == "no" and
                all_services["2W_Tyre"] == "no" and
                all_services["2W_Battery"] == "no"
            )

            fee_column = fitment_fee_map.get(service_type)
            fitment_column = vendor_fitment_map.get(service_type)

            # Case 1: Only 4W Tyre is available and selected
            if only_4w_tyre and service_type == "4W_Tyre":
                st.success("✅ Serviceable")
                st.warning("🟡 Remark: Only 4W Tyre available — check with CM before confirming.")
                if fitment_column:
                    st.info(f"🚚 Vendor Fitment Available: {row[fitment_column]}")
                if fee_column:
                    st.info(f"💰 Extra Fitment Fee: ₹{row[fee_column]}")

            # Case 2: Only 4W Tyre is available but user selects something else
            elif only_4w_tyre and service_type != "4W_Tyre":
                st.error("❌ Not Serviceable")

            # Case 3: Regular Yes condition
            elif service_status == "yes":
                st.success("✅ Serviceable")
                if fitment_column:
                    st.info(f"🚚 Vendor Fitment Available: {row[fitment_column]}")
                if fee_column:
                    st.info(f"💰 Extra Fitment Fee: ₹{row[fee_column]}")
                remark = row["Remark"]
                if isinstance(remark, str) and remark.strip():
                    st.info(f"📝 Remark: {remark}")

            # Case 4: Regular No condition
            else:
                st.error("❌ Not Serviceable")
                st.info(f"📍 Nearest Service Distance: {row['If No in serviceable area in TNM mention Distance']}")
                remark = row["Remark"]
                if isinstance(remark, str) and remark.strip():
                    st.info(f"📝 Remark: {remark}")
