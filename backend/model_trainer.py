# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
# import joblib
# import os
# import warnings

# # Suppress all warnings to keep output clean, especially for sklearn updates
# warnings.filterwarnings("ignore")

# print("--- Starting Model Training Script ---")

# # Load the dataset
# try:
#     dataset_path = os.getenv('DATASET_PATH', 'trainingSet.csv') # Corrected typo: 'tariningSet.csv' to 'trainingSet.csv'
#     print(f"Looking for dataset at: {dataset_path}")
#     df = pd.read_csv(dataset_path)
#     print(f"Dataset '{os.path.basename(dataset_path)}' loaded successfully. Shape: {df.shape}")
#     print("Dataset columns:", df.columns.tolist())
# except FileNotFoundError:
#     print(f"Error: Dataset '{dataset_path}' not found. Please ensure it's in the correct directory.")
#     print("If you don't have a trainingSet.csv, you will need to create one with relevant tax data.")
#     exit()
# except Exception as e:
#     print(f"Error loading dataset: {e}")
#     exit()

# # --- Define Features and Targets ---
# # These features must align with what your Gemini extraction and aggregation provides,
# # and what generate_ml_prediction_summary in app.py prepares.
# # Ensure all numerical values are handled as numbers.
# common_features = [
#     'Age', # Derived from Date_of_Birth in app.py
#     'Gross Annual Salary', # Mapped from total_gross_salary
#     'HRA Received', # Mapped from HRA_Received
#     'Rent Paid', # Mapped from Rent_Paid
#     'Basic Salary', # Mapped from Basic_Salary
#     'Standard Deduction Claimed', # Mapped from standard_deduction
#     'Professional Tax', # Mapped from professional_tax
#     'Interest on Home Loan Deduction (Section 24(b))', # Mapped from interest_on_housing_loan_24b
#     'Section 80C Investments Claimed', # Mapped from deduction_80C
#     'Section 80D (Health Insurance Premiums) Claimed', # Mapped from deduction_80D
#     'Section 80E (Education Loan Interest) Claimed', # Mapped from deduction_80E
#     'Other Deductions (80CCD, 80G, etc.) Claimed', # Aggregated from 80CCD1B, 80G, 80TTA, 80TTB
#     'Total Exempt Allowances Claimed' # Mapped from exempt_allowances
# ]

# # Add categorical features for the classifier
# classifier_features = common_features + [
#     'Residential Status', # Mapped from Residential_Status
#     'Gender' # Mapped from Gender
# ]

# # Target for regime classification
# regime_target = 'Tax Regime Chosen' # This should be a column in your CSV (e.g., 'Old Regime', 'New Regime')

# # Target for tax amount regression
# tax_amount_target = 'Final Tax Payable' # This should be a column in your CSV

# # --- Pre-check for missing columns ---
# all_required_columns = list(set(classifier_features + [regime_target, tax_amount_target]))
# missing_columns = [col for col in all_required_columns if col not in df.columns]

# if missing_columns:
#     print(f"\nError: Missing required columns in dataset: {missing_columns}")
#     print("Please ensure your 'trainingSet.csv' contains these columns or adjust feature/target names.")
#     print("Available columns in your CSV:", df.columns.tolist())
#     exit()

# # --- Data Splitting ---
# # X for classifier will use classifier_features
# # X for regressor will use common_features + 'Tax Regime Chosen' (which will be predicted by classifier)
# # We split the full dataset to maintain consistency.
# X_full = df[list(set(classifier_features + common_features + [regime_target]))] # Include regime_target in X_full for splitting
# y_regime = df[regime_target]
# y_tax_amount = df[tax_amount_target]

# # Use stratify on the classification target to ensure balanced classes in train/test sets
# X_train_full, X_test_full, y_train_regime, y_test_regime, y_train_tax, y_test_tax = train_test_split(
#     X_full, y_regime, y_tax_amount, test_size=0.2, random_state=42, stratify=y_regime
# )

# print(f"\nTraining set size: {len(X_train_full)} samples")
# print(f"Test set size: {len(X_test_full)} samples")

# # --- Model 1: Tax Regime Classifier ---
# print("\n--- Training Tax Regime Classifier ---")

# # Identify categorical and numerical features for the classifier
# classifier_categorical_features = ['Residential Status', 'Gender']
# classifier_numerical_features = [col for col in common_features if col not in classifier_categorical_features]

# # Create a preprocessor for the classifier
# classifier_preprocessor = ColumnTransformer(
#     transformers=[
#         ('num', StandardScaler(), classifier_numerical_features),
#         ('cat', OneHotEncoder(handle_unknown='ignore'), classifier_categorical_features)
#     ],
#     remainder='passthrough' # Keep other columns if any, though none expected after this setup
# )

# # Create the classifier pipeline
# classifier_pipeline = Pipeline(steps=[
#     ('preprocessor', classifier_preprocessor),
#     ('classifier', LogisticRegression(random_state=42, solver='liblinear')) # Using liblinear for small datasets/binary classification
# ])

# # Extract features specifically for the classifier training from X_train_full
# X_train_classifier = X_train_full[classifier_features]
# X_test_classifier = X_test_full[classifier_features] # For evaluation

# # Fit the classifier model
# classifier_pipeline.fit(X_train_classifier, y_train_regime)
# y_pred_regime = classifier_pipeline.predict(X_test_classifier)

# print(f"\nClassifier Accuracy: {accuracy_score(y_test_regime, y_pred_regime):.4f}")
# print("\nClassifier Classification Report:")
# print(classification_report(y_test_regime, y_pred_regime))

# # Save the trained classifier model
# classifier_filename = 'tax_regime_classifier_model.pkl'
# joblib.dump(classifier_pipeline, classifier_filename)
# print(f"\nTax regime classifier model saved as {classifier_filename}")


# # --- Model 2: Final Tax Payable Regressor ---
# print("\n--- Training Final Tax Payable Regressor ---")

# # For the regressor, we'll use common_features and the 'Tax Regime Chosen' column.
# # The 'Tax Regime Chosen' will be treated as a categorical feature for the regressor.
# regressor_features = common_features + [regime_target] # Include the actual regime for training

# # Identify categorical and numerical features for the regressor
# regressor_categorical_features = [regime_target] # Only 'Tax Regime Chosen' is categorical for regressor
# regressor_numerical_features = [col for col in common_features if col not in regressor_categorical_features]

# # Create a preprocessor for the regressor
# regressor_preprocessor = ColumnTransformer(
#     transformers=[
#         ('num', StandardScaler(), regressor_numerical_features),
#         ('cat', OneHotEncoder(handle_unknown='ignore'), regressor_categorical_features)
#     ],
#     remainder='passthrough'
# )

# # Using RandomForestRegressor for potentially better performance on tax calculation
# regressor_pipeline = Pipeline(steps=[
#     ('preprocessor', regressor_preprocessor),
#     ('regressor', RandomForestRegressor(random_state=42, n_estimators=100)) # Added n_estimators for better performance
# ])

# # Prepare X for the regressor: common_features + actual 'Tax Regime Chosen' for training
# X_train_regressor = X_train_full[regressor_features]
# X_test_regressor = X_test_full[regressor_features] # Use actual regime for testing evaluation

# # Fit the regressor model
# regressor_pipeline.fit(X_train_regressor, y_train_tax)
# y_pred_tax = regressor_pipeline.predict(X_test_regressor)

# print(f"\nRegressor Mean Absolute Error (MAE): {mean_absolute_error(y_test_tax, y_pred_tax):.2f}")
# print(f"Regressor R-squared (R2): {r2_score(y_test_tax, y_pred_tax):.2f}")

# # Save the trained regressor model
# regressor_filename = 'final_tax_regressor_model.pkl'
# joblib.dump(regressor_pipeline, regressor_filename)
# print(f"Final tax regressor model saved as {regressor_filename}")

# print("\n--- Both models trained and saved successfully. ---")
# print("Remember to run this script whenever your training data changes or you want to retrain models.")





import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier # For tax regime classification
from xgboost import XGBRegressor # For final tax liability regression
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
import joblib
import os
import warnings

# Suppress all warnings to keep output clean, especially for sklearn updates
warnings.filterwarnings("ignore")

print("--- Starting Model Training Script ---")

# Load the dataset
try:
    dataset_path = os.getenv('DATASET_PATH', 'trainingSet.csv')
    print(f"Looking for dataset at: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset '{os.path.basename(dataset_path)}' loaded successfully. Shape: {df.shape}")
    print("Dataset columns:", df.columns.tolist())
except FileNotFoundError:
    print(f"Error: Dataset '{dataset_path}' not found. Please ensure it's in the correct directory.")
    print("If you don't have a trainingSet.csv, you will need to create one with relevant tax data.")
    exit()
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

# --- Preprocessing: Fill NaN for numerical and categorical features ---
# This step is crucial before splitting to avoid NaN issues in transformers
numerical_cols = df.select_dtypes(include=['number']).columns
categorical_cols = df.select_dtypes(include=['object']).columns

for col in numerical_cols:
    df[col] = df[col].fillna(0) # Fill numerical NaNs with 0 (or median/mean as appropriate for data)

for col in categorical_cols:
    df[col] = df[col].fillna('Unknown') # Fill categorical NaNs with 'Unknown'

# --- Define Features and Targets ---
# Features for the regime classifier and tax regressor.
# These must align with what your Gemini extraction and aggregation provides,
# and what generate_ml_prediction_summary in app.py prepares.
# Ensure all numerical values are handled as numbers.

# Common features to be used by both models (numerical part)
common_numerical_features = [
    'Age', # Derived from Date_of_Birth in app.py
    'Gross Annual Salary', # Mapped from total_gross_income
    'HRA Received', # Mapped from hra_received
    'Rent Paid', # Placeholder if you have this in your CSV. Adjust if not.
    'Basic Salary', # Mapped from basic_salary
    'Standard Deduction Claimed', # Fixed 50000 in app.py, but could be a feature for learning if variable
    'Professional Tax', # Mapped from professional_tax
    'Interest on Home Loan Deduction (Section 24(b))', # Mapped from interest_on_housing_loan_self_occupied
    'Section 80C Investments Claimed', # Mapped from deduction_80c
    'Section 80D (Health Insurance Premiums) Claimed', # Mapped from deduction_80d
    'Section 80E (Education Loan Interest) Claimed', # Mapped from deduction_80e
    'Other Deductions (80CCD, 80G, etc.) Claimed', # Combined from 80ccd, 80g, 80tta, 80ttb
    'Total Exempt Allowances Claimed' # Mapped from total_exempt_allowances
]

# Categorical features specific to the classifier (or also used by regressor after one-hot encoding)
categorical_features = [
    'Residential Status', # Mapped from residential_status
    'Gender' # Mapped from gender
]

# All features for the classifier
classifier_all_features = common_numerical_features + categorical_features

# Target for tax regime classification
regime_target = 'Tax Regime Chosen' # This should be a column in your CSV (e.g., 'Old Regime', 'New Regime')
# Target for tax liability regression
# CORRECTED: Changed from 'Computed Taxable Income' to 'Final Tax Payable' based on your CSV
tax_amount_target = 'Final Tax Payable'

# Ensure targets are present in the dataset
if regime_target not in df.columns:
    print(f"Error: Target column '{regime_target}' not found in dataset. Please ensure the CSV has this column.")
    exit()
if tax_amount_target not in df.columns:
    print(f"Error: Target column '{tax_amount_target}' not found in dataset. Please ensure the CSV has this column.")
    exit()

# --- Pre-check for missing features in the dataset ---
all_required_features = list(set(classifier_all_features + [regime_target, tax_amount_target]))
missing_columns = [col for col in all_required_features if col not in df.columns]

if missing_columns:
    print(f"\nError: Missing required columns in dataset: {missing_columns}")
    print("Please ensure your 'trainingSet.csv' contains these columns or adjust feature/target names.")
    print("Available columns in your CSV:", df.columns.tolist())
    exit()

# Filter out rows with 'null' or missing tax regime for classification training
df_cleaned_for_regime = df[df[regime_target].notna() & (df[regime_target] != 'null')].copy()
if df_cleaned_for_regime.empty:
    print(f"Warning: No valid data for '{regime_target}' after cleaning. Cannot train regime classifier. ML predictions for regime might be affected.")
    # Exit or handle gracefully if regime classifier is critical
    # For now, let's assume it's critical and exit if no data for training
    exit()

# Features and targets for training
X_regime = df_cleaned_for_regime[classifier_all_features]
y_regime = df_cleaned_for_regime[regime_target]

# Split data for regime classifier
X_train_regime, X_test_regime, y_train_regime, y_test_regime = train_test_split(
    X_regime, y_regime, test_size=0.2, random_state=42, stratify=y_regime
)

# Preprocessor for Regime Classifier
regime_preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), common_numerical_features), # Scale numerical features
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features) # One-hot encode categorical features
    ],
    remainder='passthrough' # Keep any other columns if they exist (though not expected with this setup)
)

# Regime Classifier Pipeline (RandomForestClassifier as requested)
regime_classifier_pipeline = Pipeline(steps=[
    ('preprocessor', regime_preprocessor),
    ('classifier', RandomForestClassifier(random_state=42, n_estimators=100)) # Using RandomForestClassifier
])

print("\n--- Training Tax Regime Classifier (RandomForestClassifier) ---")
regime_classifier_pipeline.fit(X_train_regime, y_train_regime)
y_pred_regime = regime_classifier_pipeline.predict(X_test_regime)

print(f"Regime Classifier Accuracy: {accuracy_score(y_test_regime, y_pred_regime):.4f}")
print("Regime Classifier Report:\n", classification_report(y_test_regime, y_pred_regime))

# Save the trained regime classifier model
classifier_filename = 'tax_regime_classifier_model.pkl'
joblib.dump(regime_classifier_pipeline, classifier_filename)
print(f"Tax Regime Classifier model saved as '{classifier_filename}'")


# --- Model 2: Final Tax Payable Regressor (XGBoost) ---
print("\n--- Training Final Tax Payable Regressor (XGBoostRegressor) ---")

# The regressor needs common numerical features PLUS the 'Tax Regime Chosen' as a categorical feature
regressor_all_features = common_numerical_features + [regime_target]

X_tax = df_cleaned_for_regime[regressor_all_features] # Use cleaned data for consistency
y_tax = df_cleaned_for_regime[tax_amount_target]

X_train_tax, X_test_tax, y_train_tax, y_test_tax = train_test_split(
    X_tax, y_tax, test_size=0.2, random_state=42
)

# Preprocessor for Tax Regressor
# For regressor, only 'Tax Regime Chosen' is treated as categorical for encoding
tax_regressor_categorical_features = [regime_target]
tax_regressor_numerical_features = common_numerical_features # All other features are numerical

tax_regressor_preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), tax_regressor_numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), tax_regressor_categorical_features)
    ],
    remainder='passthrough'
)

# Tax Regressor Pipeline (XGBoostRegressor as requested)
tax_regressor_pipeline = Pipeline(steps=[
    ('preprocessor', tax_regressor_preprocessor),
    ('regressor', XGBRegressor(random_state=42, n_estimators=100)) # Using XGBoostRegressor
])

tax_regressor_pipeline.fit(X_train_tax, y_train_tax)
y_pred_tax = tax_regressor_pipeline.predict(X_test_tax)

print(f"\nRegressor Mean Absolute Error (MAE): {mean_absolute_error(y_test_tax, y_pred_tax):.2f}")
print(f"Regressor R-squared (R2): {r2_score(y_test_tax, y_pred_tax):.2f}")

# Save the trained regressor model
regressor_filename = 'final_tax_regressor_model.pkl'
joblib.dump(tax_regressor_pipeline, regressor_filename)
print(f"Final Tax Regressor model saved as '{regressor_filename}'")

print("\n--- Both models trained and saved successfully. ---")
print("Remember to run this script whenever your training data changes or you want to retrain models.")

