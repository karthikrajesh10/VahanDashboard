import pandas as pd
import os

def clean_vehicle_data_dynamic(df, vehicle_type, year):
    df_cleaned = df.iloc[4:].copy()
    column_count = df_cleaned.shape[1]
    new_columns = ['S_No', 'Vehicle_Class'] + [f'Category_{i+1}' for i in range(column_count - 2)]
    df_cleaned.columns = new_columns
    df_cleaned = df_cleaned.dropna(subset=['Vehicle_Class'])
    df_cleaned = df_cleaned[df_cleaned['S_No'].apply(lambda x: str(x).isdigit())]

    for col in new_columns[2:]:
        df_cleaned[col] = df_cleaned[col].astype(str).str.replace(',', '').replace('nan', '0').astype(int)

    df_melted = df_cleaned.melt(
        id_vars=['Vehicle_Class'],
        value_vars=new_columns[2:],
        var_name='Category',
        value_name='Registration_Count'
    )
    df_melted['Vehicle_Type'] = vehicle_type
    df_melted['Year'] = year
    return df_melted[['Year', 'Vehicle_Type', 'Vehicle_Class', 'Category', 'Registration_Count']]

def load_all_files(data_dir):
    combined_df = pd.DataFrame()

    for file in os.listdir(data_dir):
        if file.endswith('.xlsx'):
            file_path = os.path.join(data_dir, file)

            # Parse metadata from filename (e.g., "2w_2023.xlsx")
            parts = file.replace('.xlsx', '').split('_')
            if len(parts) == 2:
                vehicle_type = parts[0].upper()
                year = int(parts[1])
                print(f"Loading: {file} --> Vehicle Type: {vehicle_type}, Year: {year}")
                df = pd.read_excel(file_path)
                cleaned_df = clean_vehicle_data_dynamic(df, vehicle_type, year)
                combined_df = pd.concat([combined_df, cleaned_df], ignore_index=True)

    return combined_df

def compute_growth(df):
    # Sort and group to calculate YoY and QoQ
    df_sorted = df.sort_values(by=['Vehicle_Class', 'Category', 'Year'])
    df_sorted['YoY_Growth'] = df_sorted.groupby(['Vehicle_Type', 'Vehicle_Class', 'Category'])['Registration_Count'].pct_change() * 100
    return df_sorted

def summarize(df):
    print("\n📊 Total Vehicles by Year and Type:")
    print(df.groupby(['Year', 'Vehicle_Type'])['Registration_Count'].sum().reset_index())

if __name__ == "__main__":
    data_directory = "./data"  # Folder with your Excel files
    df_all = load_all_files(data_directory)
    df_with_growth = compute_growth(df_all)
    summarize(df_with_growth)

    # Save cleaned output
    df_with_growth.to_csv("cleaned_vehicle_data.csv", index=False)
    print("\n✅ Cleaned data saved as 'cleaned_vehicle_data.csv'")
