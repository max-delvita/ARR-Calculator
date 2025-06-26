# This script is designed for use in a local Python environment with Streamlit.
# Please run it using `streamlit run filename.py` after installing Streamlit via `pip install streamlit`

try:
    import streamlit as st
    import pandas as pd
except ImportError:
    st = None
    print("[WARNING] Streamlit or Pandas is not installed. Please install with 'pip install streamlit pandas' and run using 'streamlit run filename.py'")

if st:
    # Set page config with light theme
    st.set_page_config(
        page_title="ARR Calculator",
        page_icon="📊",
        layout="wide"
    )
    
    # Set light theme
    st.markdown("""
    <style>
    /* Force light theme */
    [data-testid="stAppViewContainer"] {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force text color */
    * {
        color: black !important;
    }
    
    /* Table styles */
    .stDataFrame {
        color: black !important;
        background-color: white !important;
    }
    
    /* Table cells */
    .stDataFrame th,
    .stDataFrame td,
    .stDataFrame tr,
    .stDataFrame thead,
    .stDataFrame tbody,
    .stDataFrame tbody th,
    .stDataFrame tbody td {
        color: black !important;
        background-color: white !important;
    }
    
    /* Table header */
    .stDataFrame thead th {
        background-color: #f0f0f0 !important;
        color: black !important;
        font-weight: bold !important;
    }
    
    /* Alternate row colors */
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #f9f9f9 !important;
    }
    
    /* Hover effect */
    .stDataFrame tbody tr:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* Ensure text is visible in all elements */
    body, p, h1, h2, h3, h4, h5, h6, div, span, td, th {
        color: black !important;
    }
    
    /* Style for buttons */
    .stButton>button {
        color: white !important;
        background-color: #1f77b4 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover {
        background-color: #0d5a9e !important;
    }
    .stButton>button:active {
        background-color: #0a4a87 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Alternative approach: Use st.dataframe with custom CSS
    st.markdown("""
    <style>
    /* Base styles */
    .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force light theme for all components */
    :root {
        --primary-color: #1f77b4;
        --background-color: #ffffff;
        --secondary-background-color: #f8f9fa;
        --text-color: #000000;
        --font: sans-serif;
    }
    
    /* Force text color in all elements */
    * {
        color: black !important;
    }
    
    /* Table specific overrides */
    .stDataFrame {
        color: black !important;
        background-color: white !important;
    }
    
    .stDataFrame * {
        color: black !important;
        background-color: white !important;
    }
    
    /* Force table cells to show black text */
    .stDataFrame th,
    .stDataFrame td,
    .stDataFrame tbody,
    .stDataFrame thead,
    .stDataFrame tbody tr,
    .stDataFrame tbody td,
    .stDataFrame tbody th {
        color: black !important;
        background-color: white !important;
    }
    
    /* Header row */
    .stDataFrame thead th {
        background-color: #f8f9fa !important;
        font-weight: bold !important;
        color: black !important;
    }
    
    /* Alternate row colors */
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #f8f9fa !important;
    }
    
    /* Hover effect */
    .stDataFrame tbody tr:hover {
        background-color: #e9ecef !important;
    }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Constants
    DAYS_PER_YEAR = 365
    FLAT_FEE_YEARLY = 25 * 12
    COMMISSION_RATE = 0.03
    TOTAL_PROPERTIES_SEA = 248000

    st.title("Symplehost.ai ARR Sensitivity Table")
    st.markdown("Explore ARR outcomes based on different occupancy rates and % of direct bookings.")
    
    # Add reset button with custom styling
    st.markdown("""
    <style>
    .stButton>button {
        color: white !important;
        background-color: #1f77b4 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover {
        background-color: #0d5a9e !important;
    }
    .stButton>button:active {
        background-color: #0a4a87 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Use session state to manage reset
    if 'reset' not in st.session_state:
        st.session_state.reset = False
    
    # Reset button
    if st.button("Reset to Defaults"):
        st.session_state.reset = True
    
    # Inputs with default values
    col1, col2, col3 = st.columns(3)
    with col1:
        properties = st.slider(
            "Number of Properties per Host", 
            1, 10, 
            value=5 if not st.session_state.reset else 5,
            key='properties_slider'
        )
    with col2:
        nightly_rate = st.slider(
            "Nightly Rate (USD)", 
            50, 200, 
            value=100 if not st.session_state.reset else 100,
            key='nightly_rate_slider'
        )
    with col3:
        market_share_pct = st.slider(
            "Market Share of SEA STR Market (%)", 
            1, 30, 
            value=15 if not st.session_state.reset else 15,
            key='market_share_slider'
        ) / 100
    
    # Reset the reset state after updating sliders
    if st.session_state.reset:
        st.session_state.reset = False
        st.rerun()
    
    # Flat fee note
    st.caption("💡 Note: The flat fee is $25 per host per month ($300 per year), plus 3% commission on direct bookings.")

    # Sensitivity variables
    occupancy_range = range(50, 101, 10)  # 50% to 100%
    direct_pct_range = range(10, 51, 10)   # 10% to 50% (excluding 0%)

    # Build DataFrame
    table = pd.DataFrame(index=[f"{o}%" for o in occupancy_range], columns=[f"{d}%" for d in direct_pct_range])
    
    # Add label to the first cell
    table.index.name = "Occupancy rate / Direct Booking %"

    for occ in occupancy_range:
        for d_pct in direct_pct_range:
            occ_frac = occ / 100
            d_frac = d_pct / 100

            nights_per_year = DAYS_PER_YEAR * occ_frac
            revenue_per_property = nights_per_year * nightly_rate
            total_revenue = revenue_per_property * properties
            direct_revenue = total_revenue * d_frac
            commission = direct_revenue * COMMISSION_RATE
            arr_per_host = FLAT_FEE_YEARLY + commission
            target_hosts = TOTAL_PROPERTIES_SEA * market_share_pct
            total_arr = arr_per_host * target_hosts

            table.loc[f"{occ}%", f"{d_pct}%"] = f"${total_arr/1_000_000:,.1f}M"

    st.subheader("Total ARR (in millions)")
    
    # Style the table with CSS
    st.markdown("""
    <style>
    /* Style the container that holds the table */
    [data-testid="stTable"] {
        color: black !important;
        background-color: white !important;
    }
    
    /* Style the table */
    [data-testid="stTable"] table {
        color: black !important;
        background-color: white !important;
    }
    
    /* Style table headers */
    [data-testid="stTable"] th {
        color: black !important;
        background-color: #f2f2f2 !important;
    }
    
    /* Style table cells */
    [data-testid="stTable"] td {
        color: black !important;
        background-color: white !important;
    }
    
    /* Style even rows */
    [data-testid="stTable"] tbody tr:nth-child(even) {
        background-color: #f9f9f9 !important;
    }
    
    /* Style on hover */
    [data-testid="stTable"] tbody tr:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* Style the expander */
    [data-testid="stExpander"] {
        background-color: white !important;
        color: black !important;
    }
    
    [data-testid="stExpander"] .st-emotion-cache-1q7spjk {
        color: black !important;
    }
    
    [data-testid="stExpander"] .st-emotion-cache-1q7spjk p,
    [data-testid="stExpander"] .st-emotion-cache-1q7spjk code,
    [data-testid="stExpander"] .st-emotion-cache-1q7spjk pre,
    [data-testid="stExpander"] .st-emotion-cache-1q7spjk li {
        color: black !important;
        background-color: white !important;
    }
    
    /* Ensure all text in expander is black */
    [data-testid="stExpander"] * {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the table using st.table()
    st.table(table.style.set_properties(**{'color': 'black', 'background-color': 'white'}).set_table_styles([
        {'selector': 'th', 'props': [('color', 'black'), ('background-color', '#f2f2f2')]},
        {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
        {'selector': 'tr:hover', 'props': [('background-color', '#f0f0f0')]}
    ]))
    
    # Add a small note about the calculations
    st.caption("Note: Calculations assume 365 days per year and include both flat fee and commission revenue streams.")

    with st.expander("How is this calculated?"):
        # Create a container with white background
        st.markdown("""
        <style>
        .formula-container {
            background-color: white !important;
            color: black !important;
            padding: 15px;
            border-radius: 5px;
        }
        .formula-container * {
            color: black !important;
        }
        .formula-container code {
            background-color: #f8f9fa;
            color: #333 !important;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
            border: 1px solid #dee2e6;
        }
        
        /* Style for code blocks */
        .st-emotion-cache-u88jwt {
            padding: 0.2em 0.4em !important;
            overflow-wrap: break-word !important;
            white-space: pre-wrap !important;
            margin: 0px !important;
            border-radius: 0.25rem !important;
            background: #f0f0f0 !important;
            color: rgb(26, 28, 36) !important;
            font-family: "Source Code Pro", monospace !important;
            font-size: 0.75em !important;
        }
        </style>
        <div class="formula-container">
        """, unsafe_allow_html=True)
        
        # Content using Streamlit markdown
        st.markdown("**Formula per host:**")
        st.markdown("- `Flat fee = $25/month = $300/year`")
        st.markdown("- `Commission = 3% of revenue from direct bookings`")
        st.markdown("- `Total ARR = (Flat fee + Commission) * Target Hosts`")
        st.markdown("")
        
        
        # Close the container
        st.markdown("</div>", unsafe_allow_html=True)

