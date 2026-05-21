import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Pharma Analytics Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.stApp {
    background-color: #f7f9fc;
}

.kpi-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    border-bottom: 4px solid #79addc;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

section[data-testid="stSidebar"] {
    background-color: white;
}

h1,h2,h3 {
    color:#2c3e50;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.markdown(
            "<h2 style='text-align:center;'>🔒 Pharma Dashboard Login</h2>",
            unsafe_allow_html=True
        )

        user = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            # Demo login
            if user == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    customers = pd.read_excel("Customers.xlsx")
    products = pd.read_excel("Products.xlsx")
    orders = pd.read_excel("Orders.xlsx")

    # Clean column names
    for d in [customers, products, orders]:
        d.columns = d.columns.str.strip()

    # Merge data
    df = orders.merge(
        customers,
        left_on="CustomerID",
        right_on="Customer_id"
    ).merge(products, on="ProductID")

    # Profit calculation
    df["Profit"] = df["Sales"] * 0.25

    return df

df = load_data()

# ---------------- COLORS ----------------
light_blues = [
    "#d1e3f3",
    "#a3c9e9",
    "#79addc",
    "#4c91d1",
    "#2471b3"
]

# ---------------- SIDEBAR ----------------
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3022/3022215.png",
    width=70
)

st.sidebar.title("Control Panel")

city = st.sidebar.multiselect(
    "📍 Filter by City",
    sorted(df['City'].unique()),
    default=df['City'].unique()
)

category = st.sidebar.multiselect(
    "💊 Product Class",
    sorted(df['Product Class'].unique()),
    default=df['Product Class'].unique()
)

year = st.sidebar.multiselect(
    "📅 Select Year",
    sorted(df['Year'].unique()),
    default=df['Year'].unique()
)

# ---------------- FILTER DATA ----------------
filtered = df[
    (df['City'].isin(city)) &
    (df['Product Class'].isin(category)) &
    (df['Year'].isin(year))
]

# ---------------- HEADER ----------------
st.markdown(
    "<h1 style='text-align:center;'>PHARMA SALES ANALYTICS DASHBOARD</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>Interactive Sales Trend Visualization</p>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- KPI SECTION ----------------
total_sales = filtered['Sales'].sum()
total_profit = filtered['Profit'].sum()
total_orders = len(filtered)
total_customers = filtered['Customer_id'].nunique()
avg_order_value = filtered['Sales'].mean()

k1,k2,k3,k4,k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class='kpi-card'>
    <p>Total Sales</p>
    <h2>${total_sales:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class='kpi-card'>
    <p>Total Profit</p>
    <h2>${total_profit:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class='kpi-card'>
    <p>Total Orders</p>
    <h2>{total_orders:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class='kpi-card'>
    <p>Customers</p>
    <h2>{total_customers}</h2>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class='kpi-card'>
    <p>Avg Order Value</p>
    <h2>${avg_order_value:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- MONTH ORDER ----------------
month_order = [
    'January','February','March','April',
    'May','June','July','August',
    'September','October','November','December'
]

# ---------------- CHARTS ----------------
c1,c2 = st.columns(2)

# TOP CUSTOMERS
with c1:

    top_customers = filtered.groupby(
        'Customer Name'
    )['Sales'].sum().nlargest(5).reset_index()

    fig_customer = px.bar(
        top_customers,
        x='Sales',
        y='Customer Name',
        orientation='h',
        title='🏆 Top 5 Customers',
        color='Sales',
        color_continuous_scale=light_blues,
        template='plotly_white',
        height=350
    )

    fig_customer.update_layout(
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_customer, use_container_width=True)

# MONTHLY TREND
with c2:

    monthly = filtered.groupby(
        'Month'
    )['Sales'].sum().reset_index()

    monthly['Month'] = pd.Categorical(
        monthly['Month'],
        categories=month_order,
        ordered=True
    )

    monthly = monthly.sort_values('Month')

    monthly['Growth %'] = monthly['Sales'].pct_change()*100

    fig_trend = px.line(
        monthly,
        x='Month',
        y='Sales',
        markers=True,
        title='📈 Monthly Sales Trend',
        template='plotly_white',
        height=350
    )

    fig_trend.update_traces(
        line_color='#2471b3',
        line_width=3
    )

    st.plotly_chart(fig_trend, use_container_width=True)

# SECOND ROW
c3,c4 = st.columns(2)

# PRODUCT CLASS DISTRIBUTION
with c3:

    fig_pie = px.pie(
        filtered,
        values='Sales',
        names='Product Class',
        hole=0.5,
        title='💊 Product Class Distribution',
        color_discrete_sequence=light_blues,
        template='plotly_white',
        height=350
    )

    st.plotly_chart(fig_pie, use_container_width=True)

# BEST PRODUCTS
with c4:

    top_products = filtered.groupby(
        'Product Name'
    )['Sales'].sum().nlargest(5).reset_index()

    fig_product = px.bar(
        top_products,
        x='Product Name',
        y='Sales',
        title='💰 Best Selling Products',
        color='Sales',
        color_continuous_scale=light_blues,
        template='plotly_white',
        height=350
    )

    fig_product.update_layout(
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_product, use_container_width=True)

# THIRD ROW
c5,c6 = st.columns(2)

# CITY SALES
with c5:

    city_sales = filtered.groupby(
        'City'
    )['Sales'].sum().reset_index()

    fig_city = px.bar(
        city_sales,
        x='City',
        y='Sales',
        title='🌍 City-wise Sales',
        color='Sales',
        color_continuous_scale=light_blues,
        template='plotly_white',
        height=350
    )

    fig_city.update_layout(
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_city, use_container_width=True)

# PROFIT ANALYSIS
with c6:

    profit_chart = filtered.groupby(
        'Product Class'
    )['Profit'].sum().reset_index()

    fig_profit = px.bar(
        profit_chart,
        x='Product Class',
        y='Profit',
        title='📊 Profit by Product Class',
        color='Profit',
        color_continuous_scale=light_blues,
        template='plotly_white',
        height=350
    )

    fig_profit.update_layout(
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_profit, use_container_width=True)

# ---------------- INSIGHTS ----------------
st.markdown("---")

st.markdown("## 💡 Business Insights")

best_product = top_products.iloc[0]['Product Name']
best_city = city_sales.sort_values(
    'Sales',
    ascending=False
).iloc[0]['City']

growth = monthly['Growth %'].iloc[-1]

st.success(f"Highest selling product: {best_product}")

st.info(f"Top revenue generating city: {best_city}")

st.warning(f"Latest monthly growth rate: {growth:.2f}%")

# ---------------- DATA TABLE ----------------
st.markdown("---")

st.markdown("## 📋 Dataset Preview")

st.dataframe(filtered.head(10), use_container_width=True)

# ---------------- DOWNLOAD BUTTON ----------------
csv = filtered.to_csv(index=False).encode('utf-8')

st.download_button(
    "📥 Download Filtered Data",
    data=csv,
    file_name="pharma_sales_filtered.csv",
    mime="text/csv",
    use_container_width=True
)

# ---------------- FOOTER ----------------
st.markdown("---")

st.markdown(
    "<center><p style='color:gray;'>Developed using Python, Pandas, Plotly & Streamlit</p></center>",
    unsafe_allow_html=True
)