import streamlit as st
import smtplib
from email.message import EmailMessage

# 1. Page Configuration - Using your logo with white background
# Ensure 'Metalux_White.jpg' is uploaded to your GitHub folder
st.set_page_config(
    page_title="metaluX Steel Plate Calculator", 
    page_icon="Metalux_White.jpg",
    layout="centered"
)

# 2. Custom Styling for the Title (Sansation-style font & Orange X)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sansita:wght@400;700&display=swap');
    
    .main-title {
        font-family: 'Sansita', sans-serif; /* Closest Google Font to Sansation */
        color: black;
        font-size: 45px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
    }
    .orange-x {
        color: #FF6600; /* Your Metalux Orange */
    }
    </style>
    <div class="main-title">
        metalu<span class="orange-x">X</span> Steel Plate Calculator
    </div>
    """, unsafe_allow_html=True)

# 3. Reference Data (Same as your Excel 'Data' sheet)
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

# --- REST OF THE INPUTS AND CALCULATION LOGIC ---
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        thickness = st.selectbox("Plate Thickness (inches)", options=list(PLATE_DATA.keys()))
        width = st.number_input("Width (inches)", min_value=1.0, value=12.0, step=0.25)
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        height = st.number_input("Height (inches)", min_value=1.0, value=12.0, step=0.25)

# (Calculation math goes here - same as previous version)
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
ohp_rate = 0.45 if subtotal > 500 else 0.50
ohp_amount = subtotal * ohp_rate
final_total = subtotal + ohp_amount

st.divider()
st.header(f"Total Quote: ${final_total:,.2f}")

# Ordering logic...
