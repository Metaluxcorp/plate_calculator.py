import streamlit as st
import smtplib
from email.message import EmailMessage

# 1. Page Configuration
st.set_page_config(page_title="Metalux Plate Calculator", page_icon="metalux_square.jpg")

# 2. Reference Data (Translated from your "Data" sheet)
PLATE_DATA = {
    0.125:  {"lbs_sqft": 6.16,  "price_lb": 0.45, "min_run": 3.0},
    0.1875: {"lbs_sqft": 7.66,  "price_lb": 0.45, "min_run": 4.0},
    0.25:   {"lbs_sqft": 10.21, "price_lb": 0.65, "min_run": 5.0},
    0.3125: {"lbs_sqft": 12.76, "price_lb": 0.65, "min_run": 8.0},
    0.375:  {"lbs_sqft": 15.32, "price_lb": 0.72, "min_run": 10.0},
    0.5:    {"lbs_sqft": 20.42, "price_lb": 0.69, "min_run": 15.0},
    0.625:  {"lbs_sqft": 25.53, "price_lb": 0.75, "min_run": 20.0},
    0.75:   {"lbs_sqft": 30.63, "price_lb": 0.77, "min_run": 25.0},
    0.875:  {"lbs_sqft": 35.74, "price_lb": 0.75, "min_run": 30.0},
    1.0:    {"lbs_sqft": 40.84, "price_lb": 0.80, "min_run": 35.0},
    1.25:   {"lbs_sqft": 51.05, "price_lb": 0.70, "min_run": 45.0},
    1.5:    {"lbs_sqft": 61.27, "price_lb": 0.75, "min_run": 55.0},
}

st.title("🛡️ Metalux Plate Calculator")
st.write("Select your plate specs to receive an instant quote.")

# 3. Customer Inputs
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        thickness = st.selectbox("Plate Thickness (inches)", options=list(PLATE_DATA.keys()))
        width = st.number_input("Width (inches)", min_value=1.0, value=12.0, step=0.25)
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        height = st.number_input("Height (inches)", min_value=1.0, value=12.0, step=0.25)

# 4. Calculation Logic (The "Excel Brain")
data = PLATE_DATA[thickness]
total_sqft = (width * height * quantity) / 144
total_lbs = total_sqft * data["lbs_sqft"]

material_cost = total_lbs * data["price_lb"]
plasma_cost = total_sqft * (data["min_run"] / 1.2)
fab_cost = quantity * 0.708333
drafting_fee = 23.00

taxable_subtotal = material_cost + plasma_cost + fab_cost
tax = taxable_subtotal * 0.07
subtotal = taxable_subtotal + drafting_fee + tax

# OHP Logic (50% standard, 45% if subtotal > $500)
ohp_rate = 0.45 if subtotal > 500 else 0.50
ohp_amount = subtotal * ohp_rate
final_total = subtotal + ohp_amount

# 5. Display Results
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Total Weight", f"{total_lbs:.1f} lbs")
c2.metric("Price per Plate", f"${(final_total/quantity):.2f}")
st.header(f"Total Quote: ${final_total:,.2f}")

# 6. Order Form
st.write("### Ready to order?")
customer_name = st.text_input("Company / Customer Name")
customer_notes = st.text_area("Additional requirements (holes, finish, etc.)")

if st.button("PLACE ORDER", type="primary"):
    if not customer_name:
        st.warning("Please enter your name/company to place the order.")
    else:
        # Email Logic
        email_body = f"""
        NEW PLATE ORDER RECEIVED:
        -------------------------
        Customer: {customer_name}
        Plate: {width}" x {height}" x {thickness}"
        Quantity: {quantity}
        Total Weight: {total_lbs:.1f} lbs
        
        Final Quote: ${final_total:,.2f}
        
        Notes: {customer_notes}
        """
        try:
            msg = EmailMessage()
            msg.set_content(email_body)
            msg['Subject'] = f"PLATE ORDER: {customer_name}"
            msg['From'] = "Metaluxcorp@gmail.com"
            msg['To'] = "Metaluxcorp@gmail.com"
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("Metaluxcorp@gmail.com", "jihihaxgrvtgcstz")
                smtp.send_message(msg)
            
            st.balloons()
            st.success("Order Placed! Metalux will contact you for payment/pickup.")
        except Exception as e:
            st.error("Email failed to send. Please contact the office directly.")
