import pandas as pd
import os

# Define quarters
quarters = {
    'Q1': ['JAN', 'FEB', 'MAR'],
    'Q2': ['APR', 'MAY', 'JUN'],
    'Q3': ['JUL', 'AUG', 'SEP'],
    'Q4': ['OCT', 'NOV', 'DEC']
}

# Folder with your 2022–2025 files
data_folder = 'data'
records = []

for file_name in sorted(os.listdir(data_folder)):
    if file_name.endswith('.xlsx') and 'month_wise' in file_name:
        year = file_name[:4]
        print(f"🔄 Processing: {file_name}")
        file_path = os.path.join(data_folder, file_name)

        try:
            # Skip top 3 rows, take 4th row as header
            df = pd.read_excel(file_path, skiprows=3)

            # Rename 'Vehicle Category' column and drop NaNs
            df.rename(columns={df.columns[1]: 'Vehicle Category'}, inplace=True)
            available_months = [col for col in df.columns if isinstance(col, str) and col.upper() in sum(quarters.values(), [])]

            # Skip file if no valid months
            if len(available_months) == 0:
                print(f"⚠️ No valid month columns found in {file_name}. Skipping.")
                continue

            df = df[['Vehicle Category'] + available_months]
            df = df[df['Vehicle Category'].notna()]
            df = df[~df['Vehicle Category'].str.contains('TOTAL', na=False, case=False)]

            # Clean values
            for month in available_months:
                df[month] = df[month].astype(str).str.replace(',', '', regex=False)
                df[month] = pd.to_numeric(df[month], errors='coerce').fillna(0).astype(int)

            # Compute quarterly totals (only if all 3 months are available)
            for _, row in df.iterrows():
                for q_name, q_months in quarters.items():
                    if all(month in available_months for month in q_months):
                        count = sum(row[m] for m in q_months)
                        records.append({
                            'Year': int(year),
                            'Quarter': q_name,
                            'Vehicle Category': row['Vehicle Category'],
                            'Count': count
                        })

        except Exception as e:
            print(f"⚠️ Error reading {file_name}: {e}")

# Build final DataFrame
df_qoq = pd.DataFrame(records)

if df_qoq.empty:
    print("❌ No valid data to process.")
else:
    # Sort and calculate QoQ growth
    df_qoq.sort_values(by=['Vehicle Category', 'Year', 'Quarter'], inplace=True)
    df_qoq['QoQ_Growth (%)'] = df_qoq.groupby('Vehicle Category')['Count'].pct_change() * 100
    df_qoq['QoQ_Growth (%)'] = df_qoq['QoQ_Growth (%)'].round(2)

    # Save to CSV
    output_file = 'cleaned_qoq_data.csv'
    df_qoq.to_csv(output_file, index=False)
    print(f"✅ Cleaned data with QoQ saved to {output_file}")
