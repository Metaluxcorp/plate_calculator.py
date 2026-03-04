import streamlit as st
import smtplib
from email.message import EmailMessage

# 1. Page Configuration
st.set_page_config(
    page_title="metaluX Steel Plate Calculator", 
    page_icon="Metalux_White.jpg",
    layout="centered"
)

# 2. Custom Branding (Two-line Title with Oversized Orange X)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sansita:wght@400;700&display=swap');
    
    .brand-container {
        font-family: 'Sansita', sans-serif;
        text-align: center;
        line-height: 1.1;
        margin-bottom: 25px;
    }
    .brand-main {
        color: black;
        font-size: 60px;
        font-weight: 700;
        display: block;
    }
    .brand-sub {
        color: #333333;
        font-size: 32px;
        font-weight: 400;
        display: block;
        margin-top: 10px;
    }
    .orange-x {
        color: #FF6600;
        display: inline-block;
        transform: scale(1.8); /* Makes the X nearly 2x size */
        margin-left: 15px;      /* Prevents overlapping with 'metalu' */
    }
    
    /* Button Styling */
    div.stButton > button:first-child {
        background-color: #FF6600;
        color: white;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #e65c00;
        border: none;
    }
    </style>
    
    <div class="brand-container">
        <span class="brand-main">metalu<span class="orange-x">X</span></span>
        <span class="brand-sub">Steel Plate Calculator</span>
    </div>
    """, unsafe_allow_html=True)

# 3. Data Reference (From your Excel "Data" Sheet)
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

# 4. User Inputs
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        thickness = st.selectbox("Plate Thickness (in)", options=list(PLATE_DATA.keys()))
        width = st.number_input("Width (in)", min_value=1.0, value=12.0, step=0.25)
    with c2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        height = st.number_input("Height (in)", min_value=1.0, value=12.0, step=0.25)

# 5. Calculation Math
data = PLATE_DATA[thickness]
total_sqft = (width * height * quantity) / 144
total_lbs = total_sqft * data["lbs_sqft"]

material_cost = total_lbs * data["price_lb"]
plasma_cost = total_sqft * (data["min_run"] / 1.2)
fab_cost = quantity * 0.708333
drafting_fee = 23.00

taxable_items = material_cost + plasma_cost + fab_cost
tax = taxable_items * 0.07
subtotal = taxable_items + drafting_fee + tax

ohp_rate = 0.45 if subtotal > 500 else 0.50
ohp_amount = subtotal * ohp_rate
final_total = subtotal + ohp_amount

# 6. Results Display
st.divider()
res1, res2, res3 = st.columns(3)
res1.metric("Total Weight", f"{total_lbs:.1f} lbs")
res2.metric("Per Plate", f"${(final_total/quantity):.2f}")
res3.subheader(f"Total: ${final_total:,.2f}")

# 7. Ordering Section
st.write("---")
st.write("### 📝 Submit for Production")
cust_name = st.text_input("Customer/Company Name")
cust_notes = st.text_area("Additional Notes (Special Cuts, Delivery, etc.)")

if st.button("PLACE ORDER NOW", use_container_width=True):
    if not cust_name:
        st.error("Please enter a name to submit the order.")
    else:
        email_content = f"""
        NEW PLATE ORDER - metaluX Calculator
        -----------------------------------
        Customer: {cust_name}
        
        SPECS:
        Thickness: {thickness}"
        Dimensions: {width}" x {height}"
        Quantity: {quantity}
        Total Weight: {total_lbs:.1f} lbs
        
        PRICING:
        Total Quote: ${final_total:,.2f}
        Price Per Unit: ${final_total/quantity:.2f}
        
        NOTES:
        {cust_notes}
        """
        try:
            msg = EmailMessage()
            msg.set_content(email_content)
            msg['Subject'] = f"PLATE ORDER: {cust_name}"
            msg['From'] = "Metaluxcorp@gmail.com"
            msg['To'] = "Metaluxcorp@gmail.com"
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("Metaluxcorp@gmail.com", "jihihaxgrvtgcstz")
                smtp.send_message(msg)
            st.balloons()
            st.success("Order Successfully Sent to metaluX!")
        except Exception as e:
            st.error(f"Error: {e}")
