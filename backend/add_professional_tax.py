import pandas as pd
import os

def calculate_professional_tax(monthly_salary):
    if monthly_salary <= 15000:
        return 0
    elif 15001 <= monthly_salary <= 20000:
        return 150 * 12 # Annualize monthly tax for consistency with annual data
    else: # monthly_salary > 20000
        return 200 * 12 # Annualize monthly tax

# Define the path to your dataset
dataset_path = os.getenv('DATASET_PATH', 'tariningSet.csv')

try:
    df = pd.read_csv(dataset_path)
    print(f"Dataset '{os.path.basename(dataset_path)}' loaded successfully for PT calculation.")
except FileNotFoundError:
    print(f"Error: Dataset '{dataset_path}' not found. Please ensure it's in the correct directory.")
    exit()
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

# Calculate monthly gross salary
df['Monthly Gross Salary'] = df['Gross Annual Salary'] / 12

# Calculate Professional Tax (Annual) and add the column
df['Professional Tax'] = df['Monthly Gross Salary'].apply(calculate_professional_tax)

# Drop the temporary 'Monthly Gross Salary' column if not needed
df = df.drop(columns=['Monthly Gross Salary'])

# Save the updated DataFrame back to the CSV file
df.to_csv(dataset_path, index=False)
print(f"Successfully added 'Professional Tax' column and saved updated '{os.path.basename(dataset_path)}'.")

# Display a sample of the updated DataFrame
print("\nUpdated dataset head (with Professional Tax):")
print(df[['Gross Annual Salary', 'Professional Tax']].head())