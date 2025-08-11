import os
import pandas as pd

# Set folder containing all maker Excel files
maker_folder = "data/maker"
all_data = []

for filename in os.listdir(maker_folder):
    if filename.endswith(".xlsx"):
        print(f"🔄 Processing: {filename}")
        parts = filename.replace(".xlsx", "").split("_")
        if len(parts) < 3:
            print(f"❌ Invalid filename format: {filename}")
            continue

        vehicle_type, year, _ = parts
        year = int(year)
        file_path = os.path.join(maker_folder, filename)

        try:
            # Read Excel from row 4 (index 3)
            df = pd.read_excel(file_path, sheet_name=0, header=3)

            # Drop completely empty columns
            df.dropna(axis=1, how='all', inplace=True)

            # Strip whitespace and rename columns
            df.columns = df.columns.str.strip()

            # Ensure first two columns are named correctly
            df.rename(columns={df.columns[0]: 'S No', df.columns[1]: 'Maker'}, inplace=True)

            # Drop rows with empty Maker
            df = df[df['Maker'].notna()]

            # Get all subcategory columns (excluding first two)
            subcategories = [col for col in df.columns if col not in ['S No', 'Maker']]

            # Melt into long format
            df_long = df.melt(id_vars='Maker', value_vars=subcategories,
                              var_name='Sub_Category', value_name='Count')

            # Strip extra whitespace and clean subcategory column
            df_long['Sub_Category'] = df_long['Sub_Category'].astype(str).str.strip()

            # Add year and vehicle type
            df_long['Year'] = year
            df_long['Vehicle_Type'] = vehicle_type.upper()

            all_data.append(df_long)

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

# Combine and Save
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    # Clean Count column
    final_df['Count'] = final_df['Count'].replace(',', '', regex=True)
    final_df['Count'] = final_df['Count'].fillna(0).astype(float).astype(int)

    final_df.to_csv("cleaned_maker_summary.csv", index=False)
    print("✅ Saved cleaned_maker_summary.csv")
else:
    print("❌ No valid data extracted.")
