import streamlit as st
import pandas as pd

st.set_page_config(page_title="Serviceability Checker", layout="centered")
st.title("📦 TNM Serviceability Lookup Tool")

# Link to your published Google Sheet CSV
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)

df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace(".", "")

# Input Form
st.subheader("Check Serviceability")
agent_type = st.selectbox("Select Agent Type", ["Online", "Inbound", "Outbound"])
service_type = st.selectbox("Select Service Type", ["4W_Tyre", "2W_Tyre", "4W_Battery", "2W_Battery"])
pincode = st.text_input("Enter Pincode")

if pincode:
    try:
        result = df[df["Pincode"] == int(pincode)]
        if not result.empty:
            row = result.iloc[0]
            is_serviceable = row[service_type] == "Yes"
            vendor_key = "Vendor_Fitment_4W_Tyre" if "Tyre" in service_type else "Vendor_Fitment_4W_Battery"
            fee_key = f"Extra_Fee_{service_type}"

            # Special logic for Online agents
            if (agent_type == "Online" and row["4W_Tyre"] == "Yes" and
                row["4W_Battery"] == "No" and row["2W_Tyre"] == "No" and row["2W_Battery"] == "No"):
                is_serviceable = False
                special_remark = "⚠️ Only 4W Tyre available — check with CM before confirming."
            else:
                special_remark = row["Remark"]

            st.markdown(f"### ✅ Serviceable: {'Yes' if is_serviceable else 'No'}")

            if not is_serviceable:
                st.markdown(f"📍 Nearest TNM Area Distance: {row['Distance_If_Not_Serviceable']}")

            if "4W" in service_type:
                st.markdown(f"🚚 Vendor Fitment: {row[vendor_key]}")

            st.markdown(f"💰 Extra Fee: ₹{row[fee_key]}")
            st.markdown(f"📝 Remark: {special_remark}")
        else:
            st.warning("❗ Pincode not found.")
    except:
        st.error("Invalid pincode. Please enter a numeric value.")
