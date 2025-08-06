import pandas as pd

# Load Parquet file
df = pd.read_parquet("/data/external_datasets/OBD_Codes/obd_codes.parquet")

# Save as CSV
df.to_csv("C:\\Users\\Ibrahim_Hegazi\\Desktop\\Eagles\\Car_Clinic_Project\\data\\external_datasets\\OBD_Codes\\OBD_Codes.csv", index=False)

print(df.head())  # Optional: view data before saving
