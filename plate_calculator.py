import streamlit as st
import smtplib
import base64
from email.message import EmailMessage

# 1. Page Configuration
st.set_page_config(
    page_title="metaluX Steel Plate Calculator", 
    page_icon="Metalux_White.jpg",
    layout="centered"
)

# 2. Function to load the custom font file
def get_base64_font(font_file):
    with open(font_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load Sansation font
try:
    font_base64 = get_base64_font("Sansation_Regular.ttf")
    font_style = f"""
    <style>
    @font-face {{
        font-family: 'Sansation';
        src: url(data:font/truetype;base64,{font_base64}) format('truetype');
    }}
    </style>
    """
    st.markdown(font_style, unsafe_allow_html=True)
    font_family = "'Sansation', sans-serif"
except:
    font_family = "sans-serif" # Fallback if file is missing

# 3. Custom Branding (metaluX with 2x Orange X)
st.markdown(f"""
    <style>
    .brand-container {{
        font-family: {font_family};
        text-align: center;
        line-height: 0.8;
        padding-top: 20px;
        margin-bottom: 30px;
    }}
    .brand-main {{
        color: black;
        font-size: 80px; /* Large main name */
        font-weight: bold;
        display: block;
    }}
    .brand-sub {{
        color: #444444;
        font-size: 28px;
        font-weight: normal;
        display: block;
        margin-top: 5px;
        letter-spacing: 1px;
    }}
    .orange-x {{
        color: #FF6600;
        display: inline-block;
        transform: scale(2.2); /* Over 2x scale */
        margin-left: 20px;       /* Space for the large X */
    }}
    
    /* Global button styling */
    div.stButton > button:first-child {{
        background-color: #FF6600;
        color: white;
        border: none;
        font-family: {font_family};
        font-size: 20px;
        height: 3em;
    }}
    </style>
    
    <div class="brand-container">
        <span class="brand-main">metalu<span class="orange-x">X</span></span>
        <span class="brand-sub">STEEL PLATE CALCULATOR</span>
    </div>
    """, unsafe_allow_html=True)

# 4. Data Reference (From your Excel)
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

# 5. User Inputs
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        thickness = st.selectbox("Thickness (in)", options=list(PLATE_DATA.keys()))
        width = st.number_input("Width (in)", min_value=1.0, value=12.0, step=0.25)
    with c2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        height = st.number_input("Height (in)", min_value=1.0, value=12.0, step=0.25)

# 6. Calculations
data = PLATE_DATA[thickness]
total_sqft = (width * height * quantity) / 144
total_lbs = total_sqft * data["lbs_sqft"]

material_cost = total_lbs * data["price_lb"]
plasma_cost = total_sqft * (data["min_run"] / 1.2)
fab_cost = quantity * 0.708333
drafting_fee = 23.00

taxable = material_cost + plasma_cost + fab_cost
subtotal = taxable + drafting_fee + (taxable * 0.07)

ohp_rate = 0.45 if subtotal > 500 else 0.50
final_total = subtotal + (subtotal * ohp_rate)

# 7. Display Results
st.divider()
res1, res2, res3 = st.columns(3)
res1.metric("Weight", f"{total_lbs:.1f} lbs")
res2.metric("Unit Price", f"${(final_total/quantity):.2f}")
res3.subheader(f"Total: ${final_total:,.2f}")

# 8. Order Submission
st.write("---")
cust_name = st.text_input("Customer/Company Name")
cust_notes = st.text_area("Notes")

if st.button("PLACE ORDER NOW", use_container_width=True):
    if cust_name:
        email_content = f"Order: {cust_name}\nSpecs: {width}x{height}x{thickness}\nQty: {quantity}\nTotal: ${final_total:,.2f}"
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
            st.success("Order Sent!")
        except Exception as e:
            st.error("Failed to send.")
    else:
        st.error("Please enter a name.")
