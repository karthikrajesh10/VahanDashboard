import pandas as pd

# --- 1. Load files ---
maker = pd.read_csv('data/cleaned_maker_summary.csv')
vehicle = pd.read_csv('data/cleaned_vehicle_data.csv')
qoq = pd.read_csv('data/cleaned_qoq_data.csv')

# --- 2. Clean Manufacturer Data ---
# The file has highly repeated makers, with counts per Unnamed columns for each year.
# We'll melt these columns and standardize.
# Find which columns match year by checking the file since column names are odd (Unnamed: x)
columns = list(maker.columns)
# Identify all ['Maker','Year','Vehicle_Type','Count'] repeats or patterns in data.
# Your input is actually a wide-by-year pivot, so let's melt it.

# Let's simplify for you:
def wide_to_long_maker(df):
    # All columns except these are actual value columns per year
    id_vars = ['Maker']
    value_vars = [c for c in df.columns if c not in id_vars]
    melt = pd.melt(df, id_vars=id_vars, value_vars=value_vars,
                   var_name='aux', value_name='value')
    # Now parse value string: Unnamed,Count,Year,Vehicle_Type tuples
    # Try splitting value by comma and parse if possible
    def parse_value(row):
        # value string like: "Unnamed: 2,226,2023,2W"
        vals = str(row['value']).split(',')
        # We expect: ['Unnamed: x', count, year, vtype]
        count = None
        year = None
        vtype = None
        try:
            count = int(vals[1])
            year = int(vals[2])
            vtype = vals[3].strip()
        except Exception:
            pass
        return pd.Series([count, year, vtype])
    melt[['Registration_Count','Year','Vehicle_Type']] = melt.apply(parse_value, axis=1)
    melt['Manufacturer'] = melt['Maker']
    # There is no category info here. So we set it to 'All'
    melt['Category'] = 'All'
    melt['Quarter'] = 'Yearly'
    melt['YoY_Growth'] = ''
    melt['QoQ_Growth'] = ''
    out = melt[['Year','Quarter','Vehicle_Type','Category','Manufacturer','Registration_Count','YoY_Growth','QoQ_Growth']]
    # Remove rows with missing year or count
    out = out.dropna(subset=['Year','Vehicle_Type','Registration_Count'])
    out['Year'] = out['Year'].astype(int)
    out['Registration_Count'] = out['Registration_Count'].astype(int)
    return out

maker_clean = wide_to_long_maker(maker)

# --- 3. Clean Vehicle Data ---
vehicle_clean = vehicle.copy()
vehicle_clean['Quarter'] = 'Yearly'
vehicle_clean['Manufacturer'] = 'All'
vehicle_clean['QoQ_Growth'] = ''
vehicle_clean = vehicle_clean.rename(columns={
    'Vehicle_Type':'Vehicle_Type',
    'Category':'Category',
    'Registration_Count':'Registration_Count',
    'YoY_Growth':'YoY_Growth'
})
vehicle_clean = vehicle_clean[['Year','Quarter','Vehicle_Type','Category','Manufacturer',
                               'Registration_Count','YoY_Growth','QoQ_Growth']]

# --- 4. Clean QoQ Data ---
qoq_clean = qoq.rename(columns={
    'Vehicle Category': 'Category',
    'Count': 'Registration_Count',
    'QoQ_Growth (%)': 'QoQ_Growth'
})

qoq_clean['Category'] = qoq_clean['Category'].astype(str)

# Extract 2W/3W/4W etc based on presence of a number in category name
def extract_vtype(cat):
    cat = cat.upper()
    if 'TWO' in cat or '2W' in cat: return '2W'
    if 'THREE' in cat or '3W' in cat: return '3W'
    if 'FOUR' in cat or '4W' in cat: return '4W'
    if 'HEAVY' in cat: return '4W'
    if 'MEDIUM' in cat: return '4W'
    if 'LIGHT' in cat: return '4W'
    return 'Other'
qoq_clean['Vehicle_Type'] = qoq_clean['Category'].apply(extract_vtype)
qoq_clean['Manufacturer'] = 'All'
qoq_clean['YoY_Growth'] = ''
qoq_clean = qoq_clean[['Year', 'Quarter', 'Vehicle_Type', 'Category', 'Manufacturer',
                       'Registration_Count', 'YoY_Growth', 'QoQ_Growth']]

# Ensure Registration_Count is numeric for all
for df in [maker_clean, vehicle_clean, qoq_clean]:
    df['Registration_Count'] = pd.to_numeric(df['Registration_Count'], errors='coerce')

# --- 5. Combine All ---
combined = pd.concat([maker_clean, vehicle_clean, qoq_clean], ignore_index=True)

# Drop duplicate and invalid rows
combined = combined.dropna(subset=['Year','Vehicle_Type','Registration_Count'])
combined = combined.drop_duplicates()

# Final reordering and typization
combined['Year'] = combined['Year'].astype(int)
combined['Registration_Count'] = combined['Registration_Count'].astype(int)
combined['Quarter'] = combined['Quarter'].astype(str)
combined['Manufacturer'] = combined['Manufacturer'].astype(str)
combined['Vehicle_Type'] = combined['Vehicle_Type'].astype(str)
combined['Category'] = combined['Category'].astype(str)

# --- 6. Save out ---
combined.to_csv("combined_cleaned_data.csv", index=False)
print("✅ Unified CSV saved as combined_cleaned_data.csv")
