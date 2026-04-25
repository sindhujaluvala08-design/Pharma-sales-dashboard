import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG (Light Theme Default) ----------------
st.set_page_config(page_title="Pharma Analytics Pro", layout="wide", initial_sidebar_state="expanded")

# ---------------- CUSTOM CSS (Light & Airy UI) ----------------
st.markdown("""
    <style>
    /* Main Background - Clean White */
    .stApp {
        background-color: #f7f9fc;
        color: #333333;
    }
    
    /* KPI Card Styling - Light & Glassmorphism */
    .kpi-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        border-bottom: 4px solid #a3c9e9; /* Soft Light Blue */
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        background: #ffffff;
    }
    
    /* Sidebar Styling - Soft Gray */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e6ed;
    }
    
    /* Input Fields styling in Sidebar */
    .stMultiSelect, .stTextInput > div > div > input {
        border-color: #a3c9e9 !class;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #79addc !class; /* Light Blue Button */
        color: white;
        border-radius: 8px;
    }
    
    /* Headers - Professional Dark Gray */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN LOGIC ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h2 style='text-align:center; color:#2c3e50;'>🔒 Portal Access</h2>", unsafe_allow_html=True)
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Access Dashboard", use_container_width=True):
            if user == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- DATA LOADING (Same logic) ----------------
@st.cache_data
def load_data():
    try:
        # NOTE: Assumes files exist in the same directory
        customers = pd.read_excel("Customers.xlsx")
        products = pd.read_excel("Products.xlsx")
        orders = pd.read_excel("Orders.xlsx")
        
        # Clean column names
        for d in [customers, products, orders]:
            d.columns = d.columns.str.strip()
            
        df = orders.merge(customers, left_on="CustomerID", right_on="Customer_id") \
                   .merge(products, on="ProductID")
        
        df['Profit'] = df['Sales'] * 0.25
        return df
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

df = load_data()

# define light blue colorscale
light_blues = ["#d1e3f3", "#a3c9e9", "#79addc", "#4c91d1", "#2471b3"]

if df is not None:
    # ---------------- SIDEBAR FILTERS (Light & Clean) ----------------
    # (Optional: If you have a light-colored logo, you can use a local file instead)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3022/3022215.png", width=70) # Keeping placeholder
    st.sidebar.title("Control Panel")
    
    st.sidebar.markdown("---")
    city = st.sidebar.multiselect("📍 Filter by City", sorted(df['City'].unique()), default=df['City'].unique())
    category = st.sidebar.multiselect("💊 Product Class", sorted(df['Product Class'].unique()), default=df['Product Class'].unique())
    
    filtered = df[(df['City'].isin(city)) & (df['Product Class'].isin(category))]

    # ---------------- HEADER ----------------
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>PHARMA SALES ANALYTICS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7f8c8d;'>Light Theme | Real-time performance monitoring</p>", unsafe_allow_html=True)

    # ---------------- KPI CARDS (Light Blue accents) ----------------
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.markdown(f"<div class='kpi-card'><p style='color:#7f8c8d; margin:0;'>TOTAL REVENUE</p><h2 style='margin:0; color:#2471b3;'>${filtered['Sales'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='kpi-card'><p style='color:#7f8c8d; margin:0;'>TOTAL PROFIT</p><h2 style='margin:0; color:#2471b3;'>${filtered['Profit'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='kpi-card'><p style='color:#7f8c8d; margin:0;'>ORDERS</p><h2 style='margin:0; color:#2471b3;'>{len(filtered):,}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='kpi-card'><p style='color:#7f8c8d; margin:0;'>CUSTOMERS</p><h2 style='margin:0; color:#2471b3;'>{filtered['Customer_id'].nunique()}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- CHARTS (Compact, Light Blue Theme) ----------------
    c1, c2 = st.columns(2)

    with c1:
        # Top Customers - Compact Horizontal Bar
        top_cust = filtered.groupby('Customer Name')['Sales'].sum().nlargest(5).reset_index()
        fig_cust = px.bar(top_cust, x='Sales', y='Customer Name', orientation='h', 
                          title="🏆 Top 5 Customers", template="plotly_white", height=300,
                          color='Sales', color_continuous_scale=light_blues)
        fig_cust.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False, 
                              coloraxis_showscale=False) # Hide color scale for clean look
        st.plotly_chart(fig_cust, use_container_width=True)

    with c2:
        # Monthly Trend - Smooth Line
        monthly = filtered.groupby('Month')['Sales'].sum().reset_index()
        # Define a consistent month sort order if needed, but keeping existing structure
        fig_trend = px.line(monthly, x='Month', y='Sales', title="📅 Monthly Sales Trend",
                            template="plotly_white", height=300, markers=True)
        fig_trend.update_traces(line_color='#2471b3', line_width=3, marker_color='#a3c9e9') # Blue line, lighter blue markers
        fig_trend.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Class Distribution - Donut Chart
        fig_pie = px.pie(filtered, values='Sales', names='Product Class', hole=0.5,
                         title="📊 Class Distribution", template="plotly_white", height=300,
                         color_discrete_sequence=light_blues)
        fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c4:
        # Top Products
        top_p = filtered.groupby('Product Name')['Sales'].sum().nlargest(5).reset_index()
        fig_prod = px.bar(top_p, x='Product Name', y='Sales', title="💊 Best Selling Products",
                          template="plotly_white", height=300, color='Sales',
                          color_continuous_scale=light_blues)
        fig_prod.update_layout(margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_prod, use_container_width=True)

    # ---------------- FOOTER & DOWNLOAD ----------------
    st.markdown("---")
    f1, f2 = st.columns([2,1])
    
    with f1:
        st.markdown("### 💡 Quick Insights")
        avg_sale = filtered['Sales'].mean()
        # Use success type for a green accent, or just markdown
        st.markdown(f"**ℹ️ Average Order Value:** ${avg_sale:,.2f}")
        if not filtered.empty:
            st.markdown(f"**ℹ️ Most Active City:** {filtered['City'].mode()[0]}")
        
    with f2:
        st.markdown("### 📥 Export Data")
        csv = filtered.to_csv(index=False).encode('utf-8')
        # Custom button style applied in CSS
        st.download_button("Download Filtered Dataset", data=csv, file_name="pharma_extract.csv", 
                           mime="text/csv", use_container_width=True) 
