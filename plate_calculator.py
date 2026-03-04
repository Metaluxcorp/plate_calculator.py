import streamlit as st
import smtplib
import base64
import datetime
from email.message import EmailMessage

# 1. Page Configuration
st.set_page_config(
    page_title="metaluX Steel Plate Order Portal", 
    page_icon="Metalux_White.jpg",
    layout="wide" 
)

# 2. Function to load the custom font (Sansation Light)
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
    
    html, body, [class*="css"], .stMarkdown, .stButton, label, .stSelectbox, .stNumberInput, p, span, .stTextArea, .stTextInput {{
        font-family: 'SansationLight', sans-serif !important;
    }}
    
    .brand-container {{
        text-align: center;
        padding-top: 10px;
        margin-bottom: 30px;
    }}
    
    .brand-main {{
        color: black;
        font-size: 65px; 
        font-weight: normal;
        display: block;
        line-height: 1.2;
    }}
    
    .orange-x {{
        color: #FF6600;
        text-transform: uppercase;
    }}
    
    .brand-sub {{
        color: #333333;
        font-size: 24px;
        font-weight: normal;
        display: block;
        margin-top: 5px;
        letter-spacing: 3px;
    }}
    
    /* Main Action Button - metaluX Orange */
    div.stButton > button:first-of-type {{
        background-color: #FF6600 !important;
        color: white !important;
        border: none !important;
        height: 3.5em;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100%;
        border-radius: 8px;
    }}
    
    div.stButton > button:first-of-type:hover {{
        background-color: #e65c00 !important;
    }}

    /* Row management buttons (X and Add Part) - Neutral Gray */
    div[data-testid="column"] button, div.add-btn button {{
        background-color: #f0f2f6 !important;
        color: #333 !important;
        border: 1px solid #dcdfe6 !important;
        font-size: 14px !important;
        height: 2.5em !important;
        width: auto !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #f8f9fa;
    }}
    .heartbeat {{
        color: #28a745;
        font-weight: bold;
    }}
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

# 4. Sidebar Heartbeat (Keeps app awake with UptimeRobot)
with st.sidebar:
    st.markdown("### 🖥️ System Status")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"**Portal Status:** <span class='heartbeat'>● ACTIVE</span>", unsafe_allow_html=True)
    st.caption(f"Last Server Heartbeat: {now}")
    st.divider()
    st.info("This portal is monitored 24/7 to ensure zero downtime for Boltco orders.")

# Display Header
st.markdown("""
    <div class="brand-container">
        <div class="brand-main">metalu<span class="orange-x">X</span></div>
        <div class="brand-sub">STEEL PLATE ORDER PORTAL</div>
    </div>
    """, unsafe_allow_html=True)

# 5. Data Reference
FRACTION_MAP = {
    'Select Thickness...': None,
    '1/8"': 0.125, '3/16"': 0.1875, '1/4"': 0.25, '5/16"': 0.3125,
    '3/8"': 0.375, '1/2"': 0.5, '5/8"': 0.625, '3/4"': 0.75,
    '7/8"': 0.875, '1"': 1.0, '1-1/4"': 1.25, '1-1/2"': 1.5
}

CUSTOMER_OPTIONS = [
    "Select Customer...",
    "Boltco/Brett",
    "Boltco/Brooke",
    "Boltco/Katrina",
    "Boltco/Michelle"
]

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

# 6. Session State
if 'parts' not in st.session_state:
    st.session_state.parts = [{'id': 0}]
if 'part_counter' not in st.session_state:
    st.session_state.part_counter = 1

def add_part():
    st.session_state.parts.append({'id': st.session_state.part_counter})
    st.session_state.part_counter += 1

def remove_part(index):
    if len(st.session_state.parts) > 1:
        st.session_state.parts.pop(index)

# 7. Dimensions UI
total_all_parts_quote = 0.0
total_all_parts_weight = 0.0
parts_data_for_email = []

st.write("### Plate Dimensions")
h1, h2, h3, h4, h5 = st.columns([2, 2, 2, 2, 1])
h1.markdown("**Thickness**")
h2.markdown("**Width (in)**")
h3.markdown("**Height (in)**")
h4.markdown("**Quantity**")

for i, part in enumerate(st.session_state.parts):
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
    with c1:
        selected_frac = st.selectbox(f"Thick_{part['id']}", options=list(FRACTION_MAP.keys()), key=f"thick_sel_{part['id']}", label_visibility="collapsed")
        decimal_thick = FRACTION_MAP[selected_frac]
    with c2:
        p_width = st.number_input(f"Width_{part['id']}", min_value=0.0, value=None, placeholder="0.00", step=0.25, key=f"width_{part['id']}", label_visibility="collapsed")
    with c3:
        p_height = st.number_input(f"Height_{part['id']}", min_value=0.0, value=None, placeholder="0.00", step=0.25, key=f"height_{part['id']}", label_visibility="collapsed")
    with c4:
        p_qty = st.number_input(f"Qty_{part['id']}", min_value=0, value=None, placeholder="0", step=1, key=f"qty_{part['id']}", label_visibility="collapsed")
    with c5:
        if st.button("X", key=f"rem_{part['id']}"):
            remove_part(i)
            st.rerun()

    if decimal_thick and p_width and p_height and p_qty:
        row_data = PLATE_DATA[decimal_thick]
        row_sqft = (p_width * p_height * p_qty) / 144
        row_lbs = row_sqft * row_data["lbs_sqft"]
        row_taxable = (row_lbs * row_data["price_lb"]) + (row_sqft * (row_data["min_run"] / 1.2)) + (p_qty * 0.708333)
        row_subtotal = row_taxable + 23.00 + (row_taxable * 0.07)
        row_total = row_subtotal * (1.45 if row_subtotal > 500 else 1.50)
        
        total_all_parts_weight += row_lbs
        total_all_parts_quote += row_total
        parts_data_for_email.append(f"({p_qty}) {p_width}\" x {p_height}\" x {selected_frac}")

st.markdown('<div class="add-btn">', unsafe_allow_html=True)
st.button("+ ADD PART", on_click=add_part)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
res_col1, res_col2 = st.columns([2, 1])
res_col1.markdown(f"#### Total Combined Weight: **{total_all_parts_weight:.1f} lbs**")
res_col2.markdown(f"## Total Quote: ${total_all_parts_quote:,.2f}")

# 8. Project Details
st.write("---")
st.write("### 📝 Project & Shipping Details")
det1, det2 = st.columns(2)
with det1:
    customer = st.selectbox("Customer / Company Name", options=CUSTOMER_OPTIONS)
    po_number = st.text_input("Purchase Order (PO) Number")
with det2:
    uploaded_files = st.file_uploader("Upload Drawing/PDF (Multiple allowed)", type=["pdf"], accept_multiple_files=True)

notes = st.text_area("Additional Project Notes")

if st.button("SEND ORDER TO OFFICE"):
    if customer == "Select Customer...":
        st.error("Please select a customer name.")
    elif not parts_data_for_email:
        st.error("Please enter at least one part with valid dimensions.")
    else:
        email_parts_list = "\n".join(parts_data_for_email)
        email_content = f"""
NEW PLATE ORDER
---------------------------
Customer: {customer}
PO Number: {po_number if po_number else 'N/A'}

PARTS LIST:
{email_parts_list}

---------------------------
GRAND TOTAL WEIGHT: {total_all_parts_weight:.1f} lbs
GRAND TOTAL QUOTE: ${total_all_parts_quote:,.2f}

Notes:
{notes}
"""
        try:
            msg = EmailMessage()
            msg.set_content(email_content)
            msg['Subject'] = f"ORDER: {customer} (PO: {po_number if po_number else 'N/A'})"
            msg['From'] = "Metaluxcorp@gmail.com"
            msg['To'] = "Metaluxcorp@gmail.com"
            
            if uploaded_files:
                for f in uploaded_files:
                    msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=f.name)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("Metaluxcorp@gmail.com", "jihihaxgrvtgcstz")
                smtp.send_message(msg)
            st.balloons()
            st.success(f"Order for {customer} and files sent successfully!")
        except Exception as e:
            st.error(f"Error: {e}")
