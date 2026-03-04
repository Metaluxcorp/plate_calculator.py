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

# 2. Function to load the custom font file (Sansation Light)
def get_base64_font(font_file):
    try:
        with open(font_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

font_base64 = get_base64_font("Sansation_Light.ttf")

# 3. Custom Branding CSS
if font_base64:
    font_css = f"""
    <style>
    @font-face {{
        font-family: 'SansationLight';
        src: url(data:font/truetype;base64,{font_base64}) format('truetype');
    }}
    
    html, body, [class*="css"], .stMarkdown, .stButton, label {{
        font-family: 'SansationLight', sans-serif !important;
    }}
    
    .brand-container {{
        text-align: center;
        line-height: 0.9;
        padding-top: 10px;
        margin-bottom: 40px;
    }}
    
    .brand-main {{
        color: black;
        font-size: 85px;
        font-weight: normal;
        display: block;
    }}
    
    .brand-sub {{
        color: #333333;
        font-size: 26px;
        font-weight: normal;
        display: block;
        margin-top: 15px;
        letter-spacing: 2px;
    }}
    
    .orange-x {{
        color: #FF6600;
        display: inline-block;
        transform: scale(2.0); /* Exactly 2x size */
        margin-left: 25px;      /* Gap so it doesn't hit the 'u' */
    }}
    
    /* Button Color */
    div.stButton > button:first-child {{
        background-color: #FF6600;
        color: white;
        border: none;
        height: 3.5em;
        font-size: 18px;
        font-weight: bold;
    }}
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

# Display the custom header
st.markdown("""
    <div class="brand-container">
        <span class="brand-main">metalu<span class="orange-x">X</span></span>
        <span class="brand-sub">STEEL PLATE CALCULATOR</span>
    </div>
    """, unsafe_allow_html=True)

# 4. Reference Data (Exact Values from your Excel)
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

# 5. User Selection Interface
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        thickness = st.selectbox("Plate Thickness (inches)", options=list(PLATE_DATA.keys()))
        width = st.number_input("Width (inches)", min_value=1.0, value=12.0, step=0.25)
    with col2:
        quantity = st.number_input("Order Quantity", min_value=1, value=1, step=1)
        height = st.number_input("Height (inches)", min_value=1.0, value=12.0, step=0.25)

# 6. Calculation Logic (Excel Match)
data = PLATE_DATA[thickness]
total_sqft = (width * height * quantity) / 144
total_lbs = total_sqft * data["lbs_sqft"]

material_cost = total_lbs * data["price_lb"]
plasma_cost = total_sqft * (data["min_run"] / 1.2)
fab_cost = quantity * 0.708333
drafting_fee = 23.00

# Subtotal including 7% Tax
taxable_base = material_cost + plasma_cost + fab_cost
tax = taxable_base * 0.07
subtotal_with_tax = taxable_base + drafting_fee + tax

# Profit Margin Logic (OHP)
ohp_rate = 0.45 if subtotal_with_tax > 500 else 0.50
final_total = subtotal_with_tax + (subtotal_with_tax * ohp_rate)

# 7. Display Metrics
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Weight", f"{total_lbs:.1f} lbs")
m2.metric("Per Plate", f"${(final_total/quantity):.2f}")
m3.subheader(f"Total: ${final_total:,.2f}")

# 8. Production Request
st.write("---")
st.write("### 🏢 Client Information")
customer = st.text_input("Name or Company")
notes = st.text_area("Production Notes / Delivery Instructions")

if st.button("SUBMIT ORDER TO METALUX", use_container_width=True):
    if not customer:
        st.error("Please provide a name/company to submit.")
    else:
        email_body = f"""
        OFFICIAL PLATE ORDER
        --------------------
        Customer: {customer}
        Specs: {width}" x {height}" x {thickness}"
        Quantity: {quantity}
        Weight: {total_lbs:.1f} lbs
        Total Price: ${final_total:,.2f}
        Notes: {notes}
        """
        try:
            msg = EmailMessage()
            msg.set_content(email_body)
            msg['Subject'] = f"NEW PLATE ORDER: {customer}"
            msg['From'] = "Metaluxcorp@gmail.com"
            msg['To'] = "Metaluxcorp@gmail.com"
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("Metaluxcorp@gmail.com", "jihihaxgrvtgcstz")
                smtp.send_message(msg)
            st.balloons()
            st.success("Your order has been submitted successfully!")
        except:
            st.error("Communication error. Please call the office.")
