import streamlit as st
import pandas as pd
import altair as alt

# --- 1. Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("combined_cleaned_data.csv")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)
    df['Registration_Count'] = pd.to_numeric(df['Registration_Count'], errors='coerce').fillna(0).astype(int)
    if 'YoY_Growth' in df.columns:
        df['YoY_Growth'] = pd.to_numeric(df['YoY_Growth'], errors='coerce')
    if 'QoQ_Growth' in df.columns:
        df['QoQ_Growth'] = pd.to_numeric(df['QoQ_Growth'], errors='coerce')
    # For selectors, ensure no nulls, as string for simplicity
    for col in ['Vehicle_Type', 'Category', 'Manufacturer', 'Quarter']:
        if col in df.columns:
            df[col] = df[col].fillna('All').astype(str)
    return df

df = load_data()

# --- 2. Sidebar Filters ---
st.sidebar.header("Filters")

years = sorted(df['Year'].unique())
year_min, year_max = min(years), max(years)
selected_years = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1
)
vehicle_types = ['All'] + sorted(df['Vehicle_Type'].unique())
selected_vehicle = st.sidebar.selectbox("Vehicle Type", vehicle_types)
categories = ['All'] + sorted(df['Category'].unique())
selected_category = st.sidebar.selectbox("Category", categories)
manufacturers = ['All'] + sorted([m for m in df['Manufacturer'].unique() if m not in ['', 'All', None]])
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers)

# --- 3. Apply Filters ---
filtered = df[
    (df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])
].copy()
if selected_vehicle != 'All':
    filtered = filtered[filtered['Vehicle_Type'] == selected_vehicle]
if selected_category != 'All':
    filtered = filtered[filtered['Category'] == selected_category]
if selected_manufacturer != 'All':
    filtered = filtered[filtered['Manufacturer'] == selected_manufacturer]

# --- 4. Main Title and Metrics ---
st.title("Vehicle Registration Dashboard")
st.caption("Investor-friendly analytics for YoY and QoQ growth by type, category, manufacturer.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Total Registrations",
        f"{int(filtered['Registration_Count'].sum()):,}" if not filtered.empty else "0"
    )
with col2:
    latest_yoy = filtered['YoY_Growth'].dropna()
    st.metric(
        "Latest YoY Growth",
        f"{latest_yoy.iloc[-1]:.2f}%" if not latest_yoy.empty else "N/A"
    )
with col3:
    latest_qoq = filtered['QoQ_Growth'].dropna()
    st.metric(
        "Latest QoQ Growth",
        f"{latest_qoq.iloc[-1]:.2f}%" if not latest_qoq.empty else "N/A"
    )

# --- 5. Trends and Growth Plots ---
trend_metric = st.radio("Growth metric for trend chart:", ["YoY Growth", "QoQ Growth"])
growth_field = "YoY_Growth" if trend_metric == "YoY Growth" else "QoQ_Growth"

if filtered.empty:
    st.warning("No data found for the selected filters. Try broadening your selection.")
else:
    # Use Year+Quarter if granular, else just Year
    group_cols = ['Year']
    if 'Quarter' in filtered.columns and filtered['Quarter'].nunique() > 1 and all(
        q not in ['', 'Yearly', None, 'nan'] for q in filtered['Quarter'].unique()
    ):
        group_cols.append('Quarter')
        filtered = filtered[filtered['Quarter'].notnull() & (filtered['Quarter'] != '')]
    main_agg = filtered.groupby(group_cols, as_index=False).agg(
        Registration_Count=('Registration_Count', 'sum'),
        Growth=(growth_field, 'last')
    )

    # Create x-axis field for Altair: Period (Year-Quarter) or Year
    if 'Quarter' in main_agg.columns and main_agg['Quarter'].nunique() > 1:
        main_agg['Period'] = main_agg['Year'].astype(str) + '-Q' + main_agg['Quarter'].astype(str).str.extract(r'(\d+)', expand=False).fillna(main_agg['Quarter'])
        x_col = 'Period'
        xaxis_label = "Year-Quarter"
        tooltip_reg = ['Year', 'Quarter', 'Registration_Count']
        tooltip_gro = ['Year', 'Quarter', 'Growth']
    else:
        x_col = 'Year'
        xaxis_label = "Year"
        tooltip_reg = ['Year', 'Registration_Count']
        tooltip_gro = ['Year', 'Growth']

    # Registration Count Trend Chart (Altair)
    if main_agg.empty or main_agg['Registration_Count'].isnull().all() or (main_agg['Registration_Count'] == 0).all():
        st.warning("No registration data found for these filters.")
    else:
        chart1 = alt.Chart(main_agg).mark_line(point=True).encode(
            x=alt.X(x_col, title=xaxis_label),
            y=alt.Y('Registration_Count', title="Registrations"),
            tooltip=tooltip_reg
        ).properties(
            title=f"Registration Count ({selected_vehicle}, {selected_category}, {selected_manufacturer})"
        )
        st.altair_chart(chart1, use_container_width=True)

    # Growth % Trend Chart
    if main_agg.empty or main_agg['Growth'].isnull().all():
        st.info("Growth data (YoY/QoQ) not available for these filters.")
    else:
        chart2 = alt.Chart(main_agg).mark_line(point=True, color="green").encode(
            x=alt.X(x_col, title=xaxis_label),
            y=alt.Y('Growth', title=f"{trend_metric} (%)"),
            tooltip=tooltip_gro
        ).properties(
            title=f"{trend_metric} Over Time"
        )
        st.altair_chart(chart2, use_container_width=True)

# --- 6. Show Table and Download ---
st.subheader("Filtered Data")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
st.download_button("Download filtered data as CSV", filtered.to_csv(index=False), "filtered_data.csv")

st.markdown("""
---
**Instructions:**
- Use the sidebar to filter by year, vehicle type, category, and manufacturer.
- If no chart appears, try broadening your filter (set filters to 'All').
- Dashboard shows registration counts and YoY/QoQ growth for your selected segment.
""")
