import streamlit as st
import smtplib
import base64
from email.message import EmailMessage

# 1. Page Configuration
st.set_page_config(
    page_title="metaluX Steel Plate Calculator", 
    page_icon="Metalux_White.jpg",
    layout="wide" # Set to wide to accommodate multi-line inputs comfortably
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
    
    html, body, [class*="css"], .stMarkdown, .stButton, label, .stSelectbox, .stNumberInput, p, span {{
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
    
    /* Button Styles */
    div.stButton > button {{
        font-family: 'SansationLight', sans-serif !important;
        border-radius: 8px;
    }}
    
    /* Submit/Order Button */
    .submit-btn > div.stButton > button {{
        background-color: #FF6600;
        color: white;
        border: none;
        height: 3.5em;
        font-size: 18px;
        font-weight: bold;
    }}
    .submit-btn > div.stButton > button:hover {{
        background-color: #e65c00;
        color: white;
    }}

    /* Add/Remove buttons */
    .add-btn > div.stButton > button {{
        background-color: #f0f2f6;
        color: black;
        border: 1px solid #dcdfe6;
    }}
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

# Display the custom header
st.markdown("""
    <div class="brand-container">
        <div class="brand-main">metalu<span class="orange-x">X</span></div>
        <div class="brand-sub">STEEL PLATE CALCULATOR</div>
    </div>
    """, unsafe_allow_html=True)

# 4. Data Reference & Fraction Mapping
# Maps user-facing fractions to decimal math keys
FRACTION_MAP = {
    '1/8"': 0.125,
    '3/16"': 0.1875,
    '1/4"': 0.25,
    '5/16"': 0.3125,
    '3/8"': 0.375,
    '1/2"': 0.5,
    '5/8"': 0.625,
    '3/4"': 0.75,
    '7/8"': 0.875,
    '1"': 1.0,
    '1-1/4"': 1.25,
    '1-1/2"': 1.5
}

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

# 5. Session State for Multi-Part List
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

# 6. Multi-Line Input UI
total_all_parts_quote = 0.0
total_all_parts_weight = 0.0
order_summary_text = ""

st.write("### Plate Dimensions")

# Column headers
h1, h2, h3, h4, h5 = st.columns([2, 2, 2, 2, 1])
h1.markdown("**Thickness**")
h2.markdown("**Width (in)**")
h3.markdown("**Height (in)**")
h4.markdown("**Quantity**")
h5.write("")

parts_data_for_email = []

# Generate a row for each part
for i, part in enumerate(st.session_state.parts):
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
    
    with c1:
        selected_frac = st.selectbox(f"Thick_{part['id']}", options=list(FRACTION_MAP.keys()), key=f"thick_sel_{part['id']}", label_visibility="collapsed")
        decimal_thick = FRACTION_MAP[selected_frac]
    with c2:
        p_width = st.number_input(f"Width_{part['id']}", min_value=1.0, value=12.0, step=0.25, key=f"width_{part['id']}", label_visibility="collapsed")
    with c3:
        p_height = st.number_input(f"Height_{part['id']}", min_value=1.0, value=12.0, step=0.25, key=f"height_{part['id']}", label_visibility="collapsed")
    with c4:
        p_qty = st.number_input(f"Qty_{part['id']}", min_value=1, value=1, step=1, key=f"qty_{part['id']}", label_visibility="collapsed")
    with c5:
        if st.button("X", key=f"rem_{part['id']}", help="Remove this part"):
            remove_part(i)
            st.rerun()

    # --- Calculation for this specific row ---
    row_data = PLATE_DATA[decimal_thick]
    row_sqft = (p_width * p_height * p_qty) / 144
    row_lbs = row_sqft * row_data["lbs_sqft"]
    
    row_material_cost = row_lbs * row_data["price_lb"]
    row_plasma_cost = row_sqft * (row_data["min_run"] / 1.2)
    row_fab_cost = p_qty * 0.708333
    row_drafting = 23.00 # Assuming drafting fee is per unique plate size/line
    
    row_taxable = row_material_cost + row_plasma_cost + row_fab_cost
    row_subtotal = row_taxable + row_drafting + (row_taxable * 0.07)
    
    # Track totals
    total_all_parts_weight += row_lbs
    # Profit logic is applied to the grand subtotal usually, but per Excel it's row-based:
    row_ohp_rate = 0.45 if row_subtotal > 500 else 0.50
    row_total = row_subtotal + (row_subtotal * row_ohp_rate)
    
    total_all_parts_quote += row_total
    
    # Store text for email
    parts_data_for_email.append(f"- {p_qty}x {selected_frac} Plate ({p_width}\" x {p_height}\") | Weight: {row_lbs:.1f} lbs | Line Total: ${row_total:,.2f}")

# Add Part Button
st.markdown('<div class="add-btn">', unsafe_allow_html=True)
st.button("+ ADD PART", on_click=add_part)
st.markdown('</div>', unsafe_allow_html=True)

# 7. Grand Totals Display
st.divider()
res_col1, res_col2 = st.columns([2, 1])

with res_col1:
    st.markdown(f"#### Total Combined Weight: **{total_all_parts_weight:.1f} lbs**")

with res_col2:
    st.markdown(f"## Total Quote: ${total_all_parts_quote:,.2f}")

# 8. Final Order Submission
st.write("---")
st.write("### 📝 Project Details")
customer = st.text_input("Customer / Company Name")
notes = st.text_area("Additional Project Notes")

st.markdown('<div class="submit-btn">', unsafe_allow_html=True)
if st.button("SEND ORDER TO OFFICE", use_container_width=True):
    if not customer:
        st.error("Please enter a customer name.")
    else:
        # Build multi-line email body
        email_parts_list = "\n".join(parts_data_for_email)
        email_content = f"""
NEW MULTI-PART PLATE ORDER
---------------------------
Customer: {customer}

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
            msg['Subject'] = f"MULTI-PART ORDER: {customer}"
            msg['From'] = "Metaluxcorp@gmail.com"
            msg['To'] = "Metaluxcorp@gmail.com"
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("Metaluxcorp@gmail.com", "jihihaxgrvtgcstz")
                smtp.send_message(msg)
            st.balloons()
            st.success("Full order sent to metaluX office!")
        except Exception as e:
            st.error(f"Error: {e}")
st.markdown('</div>', unsafe_allow_html=True)
