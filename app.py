import streamlit as st
import pandas as pd

# Load data from Google Sheet (public link)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url, dtype={'Pincode': str})

# Rename columns for consistency (optional)
df.columns = df.columns.str.strip()

# Map user-friendly service keys to actual sheet column names
service_map = {
    "4W_Tyre": "4W Tyre Order",
    "4W_Battery": "4W Battery Order",
    "2W_Tyre": "2W Tyre Order",
    "2W_Battery": "2W Battery Order"
}

vendor_fitment_map = {
    "4W_Tyre": "4W Tyre (vendor fitment)",
    "4W_Battery": "Battery (vendor fitment)",
    "2W_Tyre": "",
    "2W_Battery": ""
}

fitment_fee_map = {
    "4W_Tyre": "Extra fitment fees 4W Tyre if applicable in Rs.",
    "4W_Battery": "Extra fitment fees 4W Battery if applicable in Rs.",
    "2W_Tyre": "Extra fitment fees 2W Tyre if applicable in Rs.",
    "2W_Battery": "Extra fitment fees 2W Battery if applicable in Rs."
}

# Streamlit UI
st.set_page_config(page_title="TNM Serviceability Lookup Tool", page_icon="📦")
st.title("📦 TNM Serviceability Lookup Tool")
st.header("Check Serviceability")

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
            service_status = row[service_map[service_type]].strip().lower()

            # Special logic for Online agents
            if agent_type == "Online":
                all_services = {
                    k: row[v].strip().lower() for k, v in service_map.items()
                }
                only_4w_tyre = (
                    all_services["4W_Tyre"] == "yes" and
                    all_services["4W_Battery"] == "no" and
                    all_services["2W_Tyre"] == "no" and
                    all_services["2W_Battery"] == "no"
                )
                if only_4w_tyre:
                    st.error("❌ Not Serviceable\n\n🟡 Only 4W Tyre available — check with CM before confirming.")
                    st.info(f"📍 Remark: {row['Remark']}")
                elif service_status == "yes":
                    st.success("✅ Serviceable")
                else:
                    st.error("❌ Not Serviceable")
                    st.info(f"📍 Nearest Service Distance: {row['If No in serviceable area in TNM mention Distance']}")
                    st.info(f"📝 Remark: {row['Remark']}")
            else:
                if service_status == "yes":
                    st.success("✅ Serviceable")
                else:
                    st.error("❌ Not Serviceable")
                    st.info(f"📍 Nearest Service Distance: {row['If No in serviceable area in TNM mention Distance']}")
                    st.info(f"📝 Remark: {row['Remark']}")

            # Show vendor fitment if applicable
            vendor_column = vendor_fitment_map[service_type]
            if vendor_column:
                st.info(f"🚚 Vendor Fitment Available: {row[vendor_column]}")

            # Show extra fitment fee
            fee_column = fitment_fee_map[service_type]
            st.info(f"💰 Extra Fitment Fee: ₹{row[fee_column]}")
