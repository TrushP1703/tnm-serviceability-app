import streamlit as st
import pandas as pd

# Load data from Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC7eGFDO4cthDWrY91NA5O97zFMeNREoy_wE5qDqCY6BcI__tBjsLJuZxAvaUyV48ZMZRJSQP1W-5G/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()  # clean column headers

# Streamlit page setup
st.set_page_config(page_title="TNM Serviceability Lookup Tool", page_icon="📦", layout="centered")
st.title("📦 TNM Serviceability Lookup Tool")
st.subheader("Check Serviceability")

# Inputs
agent_type = st.selectbox("Select Agent Type", ["Online", "Inbound", "Outbound"])
service_type = st.selectbox("Select Service Type", ["4W_Tyre", "4W_Battery", "2W_Tyre", "2W_Battery"])
pincode = st.text_input("Enter Pincode")

# Show button
if st.button("🔍 Check Serviceability"):
    # Define column maps
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
        "2W_Battery": None,
    }

    fee_column_map = {
        "4W_Tyre": "Extra fitment fees 4W Tyre if applicable in Rs.",
        "4W_Battery": "Extra fitment fees 4W Battery if applicable in Rs.",
        "2W_Tyre": "Extra fitment fees 2W Tyre if applicable in Rs.",
        "2W_Battery": "Extra fitment fees 2W Battery if applicable in Rs.",
    }

    # Handle logic
    if pincode:
        try:
            pincode_int = int(pincode)
            row = df[df["Pincode"] == pincode_int]

            if row.empty:
                st.error("❌ Pincode not found in serviceability list.")
            else:
                row = row.iloc[0]
                service_status = row[service_column_map[service_type]].strip().lower()

                # Special logic: Online Agent, only 4W Tyre = Yes, rest = No
                if (
                    agent_type == "Online"
                    and service_type != "4W_Tyre"
                    and row["4W Tyre Order"].strip().lower() == "yes"
                    and all(
                        row[svc].strip().lower() == "no"
                        for key, svc in service_column_map.items()
                        if key != "4W_Tyre"
                    )
                ):
                    st.error("❌ Not Serviceable")
                    st.warning("📝 Only 4W Tyre available — check with CM before confirming.")

                elif service_status == "yes":
                    st.success("✅ Serviceable")

                    # Vendor Fitment
                    fitment_column = fitment_column_map.get(service_type)
                    if fitment_column:
                        fitment = row[fitment_column]
                        if isinstance(fitment, str) and fitment.strip():
                            st.info(f"🚚 Vendor Fitment: {fitment}")

                    # Extra Fitment Fee
                    fee_column = fee_column_map.get(service_type)
                    if fee_column:
                        fee = row[fee_column]
                        if pd.notna(fee) and str(fee).strip() != "":
                            st.info(f"💰 Extra Fitment Fee: ₹{fee}")

                    # Remarks: only for 4W Tyre and Battery
                    if service_type in ["4W_Tyre", "4W_Battery"]:
                        remark = row["Remark"]
                        if isinstance(remark, str) and remark.strip():
                            st.info(f"📝 Remark: {remark}")

                else:
                    st.error("❌ Not Serviceable")
                    dist = row["If No in serviceable area in TNM mention Distance"]
                    if pd.notna(dist) and str(dist).strip() != "":
                        st.info(f"📍 Nearest Service Distance: {dist}")
                    # No remark if not serviceable

        except ValueError:
            st.error("Invalid pincode. Please enter a numeric value.")
