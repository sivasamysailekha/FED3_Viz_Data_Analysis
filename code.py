import pandas as pd
import matplotlib.pyplot as plt
 
# --------------------------
# Load CSV
# --------------------------
file_path = "your_file.csv"   # <-- change to your actual filename
 
df = pd.read_csv(file_path)
 
# --------------------------
# Fix date parsing
# --------------------------
# Your format = MM:DD:YYYY hh:mm
df['Datetime'] = pd.to_datetime(
    df['MM:DD:YYYY hh:mm:ss'],
    format='%m/%d/%Y %H:%M',
    errors='coerce'
)
 
# Check for parsing failures
bad_dates = df[df['Datetime'].isna()]
if not bad_dates.empty:
    print("⚠️ These rows failed to parse the date:")
    print(bad_dates[['MM:DD:YYYY hh:mm:ss']])
 
# Keep only valid datetime rows
df = df.dropna(subset=['Datetime'])
 
# Sort properly
df = df.sort_values('Datetime')
 
# --------------------------
# Compute Poke Count
# --------------------------
df['Total_Pokes'] = df['Left_Poke_Count'] + df['Right_Poke_Count']
 
# --------------------------
# Plot
# --------------------------
plt.figure(figsize=(12, 6))
plt.plot(df['Datetime'], df['Total_Pokes'], marker='o')
plt.xlabel("Time")
plt.ylabel("Poke Count")
plt.title("Poke Count Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

