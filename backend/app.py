
import os
import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import google.generativeai as genai
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import traceback
import logging
import io
from datetime import datetime, timedelta
from google.cloud import vision
from google.oauth2 import service_account
from werkzeug.utils import secure_filename # Import secure_filename
import joblib # Import joblib for loading ML models
import pandas as pd # Import pandas for ML model input

# Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
import numpy as np

# Import ReportLab components for PDF generation
try:
    # Commented out ReportLab imports as per previous turn, using dummy PDF for now.
    # from reportlab.pdfgen import canvas
    # from reportlab.lib.pagesizes import letter
    # from reportlab.lib.units import inch
    # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    # from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
    # from reportlab.lib.enums import TA_CENTER
    REPORTLAB_AVAILABLE = False # Set to False since using dummy PDF
except ImportError:
    logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
    REPORTLAB_AVAILABLE = False


# Configure logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration (IMPORTANT: Using hardcoded keys as per user's request) ---
# In a real-world production environment, these should ALWAYS be loaded from
# environment variables (e.g., using os.getenv) and never hardcoded.
GEMINI_API_KEY_HARDCODED = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs"
MONGO_URI_HARDCODED = "mongodb://localhost:27017/"
JWT_SECRET_KEY_HARDCODED = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# Ensure the path for Vision API key is correct for your system. Use a raw string (r"")
# or forward slashes (/) for paths to avoid issues with backslashes.
VISION_API_KEY_PATH_HARDCODED = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json"

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all origins, allowing frontend to communicate. For production, restrict this.
CORS(app, supports_credentials=True) # Ensure supports_credentials is True for cookie/JWT handling

# --- JWT Configuration ---
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY_HARDCODED
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Tokens expire in 24 hours
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
jwt = JWTManager(app)

# Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logging.warning("JWT token expired.")
    return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback_error):
    logging.warning(f"Invalid JWT token: {callback_error}")
    return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def unauthorized_callback(callback_error):
    logging.warning(f"Unauthorized access attempt: {callback_error}")
    return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401
# --- End JWT Configuration ---


# --- MongoDB Connection ---
client = None
db = None
users_collection = None
tax_records_collection = None
contact_messages_collection = None

try:
    client = MongoClient(MONGO_URI_HARDCODED)
    db = client['garudatax_db'] # Using a more specific database name for tax application
    users_collection = db['users']
    tax_records_collection = db['tax_records'] # This collection will store aggregated records per FY
    contact_messages_collection = db['contact_messages']
    logging.info("MongoDB connected successfully.")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {traceback.format_exc()}")
    db = None # Ensure db is None if connection fails, so app can handle it gracefully.


# --- Google Cloud Vision API Configuration ---
vision_client = None
try:
    if not os.path.exists(VISION_API_KEY_PATH_HARDCODED):
        logging.error(f"Vision API key file not found at: {VISION_API_KEY_PATH_HARDCODED}. Vision features will be disabled.")
    else:
        credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH_HARDCODED)
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        logging.info("Google Cloud Vision API client initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing Google Cloud Vision API client: {traceback.format_exc()}. Vision features will be disabled.")
    vision_client = None


# --- Google Gemini API Configuration ---
# Ensure API key is set before configuring Gemini
if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
    logging.error("GEMINI_API_KEY is not set or is still the placeholder! Gemini features will not work.")
genai.configure(api_key=GEMINI_API_KEY_HARDCODED)

# Initialize Gemini models. Using gemini-2.0-flash for multimodal capabilities (though OCR is done by Vision first).
gemini_pro_model = genai.GenerativeModel('gemini-2.0-flash')
logging.info("Google Gemini API client initialized.")


# --- UPLOAD FOLDER CONFIGURATION ---
# Define the upload folder relative to the current working directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create UPLOAD_FOLDER if it doesn't exist. exist_ok=True prevents error if it already exists.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")
# --- END UPLOAD FOLDER CONFIGURATION ---

# --- ML Model Loading ---
# Load trained ML models for tax regime classification and tax liability regression
tax_regime_classifier_model = None
tax_regressor_model = None

try:
    # Ensure these .pkl files are generated by running model_trainer.py first.
    # Make sure xgboost is installed in your environment for model_trainer.py
    classifier_path = 'tax_regime_classifier_model.pkl'
    if os.path.exists(classifier_path):
        tax_regime_classifier_model = joblib.load(classifier_path)
        logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
    else:
        logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

    regressor_path = 'final_tax_regressor_model.pkl'
    if os.path.exists(regressor_path):
        tax_regressor_model = joblib.load(regressor_path)
        logging.info(f"Tax Regressor model loaded from {regressor_path}.")
    else:
        logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

except Exception as e:
    logging.error(f"Error loading ML models: {traceback.format_exc()}")
    tax_regime_classifier_model = None
    tax_regressor_model = None


# --- Helper Functions ---

def convert_numpy_types(obj):
    """
    Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
    This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
    """
    if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
        return obj.item() # Converts numpy scalar to Python scalar
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(elem) for elem in obj]
    else:
        return obj

def extract_text_with_vision_api(image_bytes):
    """
    Uses Google Cloud Vision API to perform OCR on image bytes and return the full text.
    Requires `vision_client` to be initialized.
    """
    if vision_client is None:
        logging.error("Google Cloud Vision client is not initialized. Cannot perform OCR.")
        raise RuntimeError("OCR service unavailable.")
    try:
        image = vision.Image(content=image_bytes)
        # Using document_text_detection for comprehensive text extraction from documents
        response = vision_client.document_text_detection(image=image)
        if response.full_text_annotation:
            logging.info("Successfully extracted text using Google Cloud Vision API.")
            return response.full_text_annotation.text
        else:
            logging.warning("Google Cloud Vision API returned no full text annotation.")
            return ""
    except Exception as e:
        logging.error(f"Error extracting text with Vision API: {traceback.format_exc()}")
        raise # Re-raise the exception to be handled by the calling function

def get_gemini_response(prompt_text, file_data=None, mime_type=None, filename="unknown_file"):
    """
    Sends a prompt to Gemini and returns the structured JSON response.
    If image/pdf data is provided, it first uses Vision API for OCR.
    The response is strictly expected in a JSON format based on the defined schema.
    """
    try:
        final_prompt_content = prompt_text
        
        if file_data and mime_type and ("image" in mime_type or "pdf" in mime_type):
            # If image or PDF, first extract text using Vision API
            extracted_text_from_vision = extract_text_with_vision_api(file_data)
            final_prompt_content += f"\n\n--- Document Content for Extraction ---\n{extracted_text_from_vision}"
            logging.info(f"Feeding Vision API extracted text to Gemini for '{filename}'.")
            
        else:
            # For pure text inputs, assume prompt_text already contains all necessary info
            logging.info(f"Processing text content directly with Gemini for '{filename}'.")
        
        # --- DEFINITIVE JSON SCHEMA FOR GEMINI OUTPUT ---
        # This schema MUST be comprehensive and match all keys expected by your frontend.
        # Gemini will attempt to adhere to this schema and fill in defaults.
        # Ensure all fields are explicitly defined to help Gemini produce consistent output.
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "identified_type": {"type": "STRING", "description": "Type of document, e.g., 'Form 16', 'Bank Statement', 'Form 26AS', 'Salary Slip', 'Investment Proof', 'Home Loan Statement', 'Other Document'. Choose the most relevant one if possible."},
                "employer_name": {"type": "STRING", "description": "Name of the Employer"},
                "employer_address": {"type": "STRING", "description": "Address of the Employer"},
                "pan_of_deductor": {"type": "STRING", "description": "PAN of the Employer (Deductor)"},
                "tan_of_deductor": {"type": "STRING", "description": "TAN of the Employer (Deductor)"},
                "name_of_employee": {"type": "STRING", "description": "Name of the Employee/Assessee"},
                "designation_of_employee": {"type": "STRING", "description": "Designation of the Employee"},
                "pan_of_employee": {"type": "STRING", "description": "PAN of the Employee/Assessee"},
                "date_of_birth": {"type": "STRING", "format": "date-time", "description": "Date of Birth (YYYY-MM-DD)"},
                "gender": {"type": "STRING", "description": "Gender (e.g., 'Male', 'Female', 'Other')"},
                "residential_status": {"type": "STRING", "description": "Residential Status (e.g., 'Resident', 'Non-Resident')"},
                "assessment_year": {"type": "STRING", "description": "Income Tax Assessment Year (e.g., '2024-25')"},
                "financial_year": {"type": "STRING", "description": "Financial Year (e.g., '2023-24')"},
                "period_from": {"type": "STRING", "format": "date-time", "description": "Start date of the document period (YYYY-MM-DD)"},
                "period_to": {"type": "STRING", "format": "date-time", "description": "End date of the document period (YYYY-MM-DD)"},
                "quarter_1_receipt_number": {"type": "STRING"},
                "quarter_1_tds_deducted": {"type": "NUMBER"},
                "quarter_1_tds_deposited": {"type": "NUMBER"},
                "total_tds_deducted_summary": {"type": "NUMBER", "description": "Total TDS deducted from salary (Form 16 Part A)"},
                "total_tds_deposited_summary": {"type": "NUMBER", "description": "Total TDS deposited from salary (Form 16 Part A)"},
                "salary_as_per_sec_17_1": {"type": "NUMBER", "description": "Salary as per Section 17(1)"},
                "value_of_perquisites_u_s_17_2": {"type": "NUMBER", "description": "Value of perquisites u/s 17(2)"},
                "profits_in_lieu_of_salary_u_s_17_3": {"type": "NUMBER", "description": "Profits in lieu of salary u/s 17(3)"},
                "gross_salary_total": {"type": "NUMBER", "description": "Total Gross Salary (sum of 17(1), 17(2), 17(3) from Form 16, or derived from payslip total earnings)"},
                "conveyance_allowance": {"type": "NUMBER"},
                "transport_allowance": {"type": "NUMBER"},
                "total_exempt_allowances": {"type": "NUMBER", "description": "Total allowances exempt u/s 10"},
                "balances_1_2": {"type": "NUMBER", "description": "Balance after subtracting allowances from gross salary"},
                "professional_tax": {"type": "NUMBER", "description": "Professional Tax"},
                "aggregate_of_deductions_from_salary": {"type": "NUMBER", "description": "Total deductions from salary (e.g., Prof Tax, Standard Deduction)"},
                "income_chargable_under_head_salaries": {"type": "NUMBER", "description": "Income chargeable under 'Salaries'"},
                "income_from_house_property": {"type": "NUMBER", "description": "Income From House Property (can be negative for loss)"},
                "income_from_other_sources": {"type": "NUMBER", "description": "Income From Other Sources (e.g., interest, dividend)"},
                "capital_gains_long_term": {"type": "NUMBER", "description": "Long Term Capital Gains"},
                "capital_gains_short_term": {"type": "NUMBER", "description": "Short Term Capital Gains"},
                "gross_total_income_as_per_document": {"type": "NUMBER", "description": "Gross total income as stated in the document"},
                "deduction_80c": {"type": "NUMBER", "description": "Total deduction under Section 80C (includes EPF, PPF, LIC, etc.)"},
                "deduction_80c_epf": {"type": "NUMBER", "description": "EPF contribution under 80C"},
                "deduction_80c_insurance_premium": {"type": "NUMBER", "description": "Life Insurance Premium under 80C"},
                "deduction_80ccc": {"type": "NUMBER", "description": "Deduction for contribution to certain pension funds under Section 80CCC"},
                "deduction_80ccd": {"type": "NUMBER", "description": "Deduction for contribution to NPS under Section 80CCD"},
                "deduction_80ccd1b": {"type": "NUMBER", "description": "Additional deduction under Section 80CCD(1B) for NPS"},
                "deduction_80d": {"type": "NUMBER", "description": "Deduction for Health Insurance Premium under Section 80D"},
                "deduction_80g": {"type": "NUMBER", "description": "Deduction for Donations under Section 80G"},
                "deduction_80tta": {"type": "NUMBER", "description": "Deduction for Interest on Savings Account under Section 80TTA"},
                "deduction_80ttb": {"type": "NUMBER", "description": "Deduction for Interest for Senior Citizens under Section 80TTB"},
                "deduction_80e": {"type": "NUMBER", "description": "Deduction for Interest on Education Loan under Section 80E"},
                "total_deductions_chapter_via": {"type": "NUMBER", "description": "Total of all deductions under Chapter VI-A"},
                "taxable_income_as_per_document": {"type": "NUMBER", "description": "Taxable Income as stated in the document"},
                "tax_payable_as_per_document": {"type": "NUMBER", "description": "Final tax payable as stated in the document"},
                "refund_status_as_per_document": {"type": "STRING", "description": "Refund status as stated in the document (e.g., 'Refund due', 'Tax payable', 'No demand no refund')"},
                "tax_regime_chosen": {"type": "STRING", "description": "Tax Regime Chosen (e.g., 'Old Regime' or 'New Regime' if explicitly indicated in document)"},
                "total_tds": {"type": "NUMBER", "description": "Total TDS credit from all sources (e.g., Form 26AS, Form 16 Part A)"},
                "advance_tax": {"type": "NUMBER", "description": "Advance Tax paid"},
                "self_assessment_tax": {"type": "NUMBER", "description": "Self-Assessment Tax paid"},
                
                # --- NEW PAYSLIP SPECIFIC FIELDS ---
                "basic_salary": {"type": "NUMBER", "description": "Basic Salary component from payslip"},
                "hra_received": {"type": "NUMBER", "description": "House Rent Allowance (HRA) received from payslip"},
                "epf_contribution": {"type": "NUMBER", "description": "Employee Provident Fund (EPF) contribution from payslip"},
                "esi_contribution": {"type": "NUMBER", "description": "Employee State Insurance (ESI) contribution from payslip"},
                "net_amount_payable": {"type": "NUMBER", "description": "Net amount payable (take home pay) from payslip"},
                "overtime_pay": {"type": "NUMBER", "description": "Overtime pay from payslip"},
                "overtime_hours": {"type": "STRING", "description": "Overtime hours from payslip (e.g., '100-0 Hrs')"},
                "days_present": {"type": "STRING", "description": "Days present from payslip (e.g., '250 Days')"},

                # Additional fields for Bank Statements (if applicable)
                "account_holder_name": {"type": "STRING", "description": "Name of the account holder"},
                "account_number": {"type": "STRING", "description": "Bank account number"},
                "ifsc_code": {"type": "STRING", "description": "IFSC code of the bank branch"},
                "bank_name": {"type": "STRING", "description": "Name of the bank"},
                "branch_address": {"type": "STRING", "description": "Address of the bank branch"},
                "statement_start_date": {"type": "STRING", "format": "date-time", "description": "Start date of the bank statement period (YYYY-MM-DD)"},
                "statement_end_date": {"type": "STRING", "format": "date-time", "description": "End date of the bank statement period (YYYY-MM-DD)"},
                "opening_balance": {"type": "NUMBER", "description": "Opening balance on the statement"},
                "closing_balance": {"type": "NUMBER", "description": "Closing balance on the statement"},
                "total_deposits": {"type": "NUMBER", "description": "Total deposits during the statement period"},
                "total_withdrawals": {"type": "NUMBER", "description": "Total withdrawals during the statement period"},
                "transaction_summary": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"date": {"type": "STRING", "format": "date-time", "description": "Date of the transaction (YYYY-MM-DD)"}, "description": {"type": "STRING"}, "amount": {"type": "NUMBER"}}}, "description": "A summary or key entries of transactions from the statement (e.g., large deposits/withdrawals)."}
            },
            "required": ["identified_type"] # Minimum required field from Gemini's side
        }

        generation_config = {
            "response_mime_type": "application/json",
            "response_schema": response_schema
        }
        
        # Call Gemini model with the prompt and schema
        response = genai.GenerativeModel('gemini-2.0-flash').generate_content([{"text": final_prompt_content}], generation_config=generation_config)

        if not response.text:
            logging.warning(f"Gemini returned an empty response text for {filename}.")
            # Return an error with an empty dictionary for extracted_data to prevent KeyError
            return json.dumps({"error": "Empty response from AI.", "extracted_data": {}})

        # Clean the response text from markdown fences (```json ... ```) if present
        response_text_cleaned = response.text.strip()
        if response_text_cleaned.startswith("```json") and response_text_cleaned.endswith("```"):
            response_text_cleaned = response_text_cleaned[len("```json"):].rstrip("```").strip()
            logging.info("Stripped markdown JSON fences from Gemini response.")

        try:
            # Parse the cleaned JSON response from Gemini
            parsed_json = json.loads(response_text_cleaned)
            
            # --- CRITICAL FIX: Ensure all keys from schema are present and correctly typed ---
            extracted_data = parsed_json # Gemini should return directly according to schema
            final_extracted_data = {}

            for key, prop_details in response_schema['properties'].items():
                if key in extracted_data and extracted_data[key] is not None:
                    # Safely convert to the expected type
                    if prop_details['type'] == 'NUMBER':
                        final_extracted_data[key] = safe_float(extracted_data[key])
                    elif prop_details['type'] == 'STRING':
                        # Special handling for date formats if needed, otherwise just safe_string
                        if 'format' in prop_details and prop_details['format'] == 'date-time':
                            # Attempt to parse date, default if unable
                            try:
                                dt_obj = datetime.strptime(str(extracted_data[key]).split('T')[0], '%Y-%m-%d')
                                final_extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
                            except ValueError:
                                final_extracted_data[key] = "0000-01-01" # Default invalid date string
                        else:
                            final_extracted_data[key] = safe_string(extracted_data[key])
                    elif prop_details['type'] == 'ARRAY':
                        if key == "transaction_summary" and isinstance(extracted_data[key], list):
                            # Process each transaction summary item
                            processed_transactions = []
                            for item in extracted_data[key]:
                                processed_item = {
                                    "date": "0000-01-01", # Default date for transaction
                                    "description": safe_string(item.get("description")),
                                    "amount": safe_float(item.get("amount"))
                                }
                                if 'date' in item and item['date'] is not None:
                                    try:
                                        # Assuming transaction date might be YYYY-MM-DD or similar
                                        dt_obj = datetime.strptime(str(item['date']).split('T')[0], '%Y-%m-%d')
                                        processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
                                    except ValueError:
                                        pass # Keep default if parsing fails
                                processed_transactions.append(processed_item)
                            final_extracted_data[key] = processed_transactions
                        else:
                            final_extracted_data[key] = extracted_data[key] if isinstance(extracted_data[key], list) else []
                    else: # Fallback for other types
                        final_extracted_data[key] = extracted_data[key]
                else:
                    # Set default based on schema's type
                    if prop_details['type'] == 'NUMBER':
                        final_extracted_data[key] = 0.0
                    elif prop_details['type'] == 'STRING':
                        if 'format' in prop_details and prop_details['format'] == 'date-time':
                            final_extracted_data[key] = "0000-01-01" # Default date string
                        else:
                            final_extracted_data[key] = "null" # Use string "null" as per schema description
                    elif prop_details['type'] == 'ARRAY':
                        final_extracted_data[key] = []
                    else:
                        final_extracted_data[key] = None # Generic default if type is not recognized

            logging.info(f"Successfully retrieved and validated structured info from Gemini for {filename}.")
            return json.dumps({"error": None, "extracted_data": final_extracted_data})
        except json.JSONDecodeError:
            logging.error(f"Gemini response was not valid JSON for {filename}. Raw response: {response_text_cleaned[:500]}...")
            return json.dumps({"error": "Invalid JSON format from AI", "extracted_data": {"raw_text_response": response_text_cleaned}})
        except Exception as e:
            logging.error(f"Error processing Gemini's parsed JSON for {filename}: {traceback.format_exc()}")
            return json.dumps({"error": f"Error processing AI data: {str(e)}", "extracted_data": {}})

    except Exception as e:
        logging.error(f"Overall error in get_gemini_response for {filename}: {traceback.format_exc()}")
        return json.dumps({"error": str(e), "extracted_data": {}})

def safe_float(val):
    """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
    Handles commas and currency symbols."""
    try:
        if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
            return 0.0
        if isinstance(val, str):
            # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
            # This handles values like "₹7,20,000.00", "720,000.00", "720000"
            val = val.replace(',', '').replace('₹', '').strip()
            
        return float(val)
    except (ValueError, TypeError):
        logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
        return 0.0

def safe_string(val):
    """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
    if val is None:
        return "null"
    s_val = str(val).strip()
    if s_val == "":
        return "null"
    return s_val

def _aggregate_financial_data(extracted_data_list):
    """
    Aggregates financial data from multiple extracted documents, applying reconciliation rules.
    Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
    """
    
    aggregated_data = {
        # Initialize all fields that are expected in the final aggregated output
        "identified_type": "Other Document", # Overall identified type if mixed documents
        "employer_name": "null", "employer_address": "null",
        "pan_of_deductor": "null", "tan_of_deductor": "null",
        "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
        "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
        "assessment_year": "null", "financial_year": "null",
        "period_from": "0000-01-01", "period_to": "0000-01-01",
        
        # Income Components - These should be summed
        "basic_salary": 0.0,
        "hra_received": 0.0,
        "conveyance_allowance": 0.0,
        "transport_allowance": 0.0,
        "overtime_pay": 0.0,
        "salary_as_per_sec_17_1": 0.0,
        "value_of_perquisites_u_s_17_2": 0.0,
        "profits_in_lieu_of_salary_u_s_17_3": 0.0,
        "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

        "income_from_house_property": 0.0,
        "income_from_other_sources": 0.0,
        "capital_gains_long_term": 0.0,
        "capital_gains_short_term": 0.0,

        # Deductions - These should be summed, capped later if needed
        "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
        "professional_tax": 0.0,
        "interest_on_housing_loan_self_occupied": 0.0,
        "deduction_80c": 0.0,
        "deduction_80c_epf": 0.0,
        "deduction_80c_insurance_premium": 0.0,
        "deduction_80ccc": 0.0,
        "deduction_80ccd": 0.0,
        "deduction_80ccd1b": 0.0,
        "deduction_80d": 0.0,
        "deduction_80g": 0.0,
        "deduction_80tta": 0.0,
        "deduction_80ttb": 0.0,
        "deduction_80e": 0.0,
        "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
        "epf_contribution": 0.0, # Initialize epf_contribution
        "esi_contribution": 0.0, # Initialize esi_contribution


        # Tax Paid
        "total_tds": 0.0,
        "advance_tax": 0.0,
        "self_assessment_tax": 0.0,
        "total_tds_deducted_summary": 0.0, # From Form 16 Part A

        # Document Specific (Non-summable, usually taken from most authoritative source)
        "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

        # Bank Account Details (Take from the most complete or latest if multiple)
        "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
        "bank_name": "null", "branch_address": "null",
        "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
        "opening_balance": 0.0, "closing_balance": 0.0,
        "total_deposits": 0.0, "total_withdrawals": 0.0,
        "transaction_summary": [], # Aggregate all transactions

        # Other fields from the schema, ensuring they exist
        "net_amount_payable": 0.0,
        "days_present": "null",
        "overtime_hours": "null",

        # Calculated fields for frontend
        "Age": "N/A", 
        "total_gross_income": 0.0, # Overall sum of all income heads
        "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
        "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
        "deduction_80C": 0.0, # Alias for deduction_80c
        "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
        "deduction_80D": 0.0, # Alias for deduction_80d
        "deduction_80G": 0.0, # Alias for deduction_80g
        "deduction_80TTA": 0.0, # Alias for deduction_80tta
        "deduction_80TTB": 0.0, # Alias for deduction_80ttb
        "deduction_80E": 0.0, # Alias for deduction_80e
        "total_deductions": 0.0, # Overall total deductions used in calculation
    }

    # Define document priority for overriding fields (higher value means higher priority)
    # Form 16 should provide definitive income/deduction figures.
    doc_priority = {
        "Form 16": 5,
        "Form 26AS": 4,
        "Salary Slip": 3,
        "Investment Proof": 2,
        "Home Loan Statement": 2,
        "Bank Statement": 1,
        "Other Document": 0,
        "Unknown": 0,
        "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
    }

    # Sort documents by priority (higher priority first)
    sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

    # Use a dictionary to track which field was last set by which document priority
    # This helps in overriding with higher-priority document data.
    field_source_priority = {key: -1 for key in aggregated_data}

    # Iterate through sorted documents and aggregate data
    for data in sorted_extracted_data:
        doc_type = safe_string(data.get('identified_type'))
        current_priority = doc_priority.get(doc_type, 0)
        logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

        # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
        # Otherwise, individual components will be summed later.
        extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
        if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
            aggregated_data["gross_salary_total"] = extracted_gross_salary_total
            field_source_priority["gross_salary_total"] = current_priority
            logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

        # Update core personal details only from highest priority document or if current is 'null'
        personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
        for p_field in personal_fields:
            if safe_string(data.get(p_field)) != "null" and \
               (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
                aggregated_data[p_field] = safe_string(data.get(p_field))
                field_source_priority[p_field] = current_priority


        for key, value in data.items():
            # Skip keys already handled explicitly or which have specific aggregation logic
            if key in personal_fields or key == "gross_salary_total":
                continue 
            if key == "transaction_summary":
                if isinstance(value, list):
                    aggregated_data[key].extend(value)
                continue
            if key == "identified_type":
                # Ensure highest priority identified_type is kept
                if current_priority > field_source_priority.get(key, -1):
                    aggregated_data[key] = safe_string(value)
                    field_source_priority[key] = current_priority
                continue
            
            # General handling for numerical fields: sum them up
            if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
                # Special handling for bank balances: take from latest/highest priority statement
                if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
                    if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
                        # Only update if the current document is a bank statement and has higher or equal priority
                        # (or if the existing aggregated value is 0)
                        if current_priority >= field_source_priority.get(key, -1):
                            aggregated_data[key] = safe_float(value)
                            field_source_priority[key] = current_priority
                    else: # For other document types, just sum the numbers if they appear
                        aggregated_data[key] += safe_float(value)
                else:
                    aggregated_data[key] += safe_float(value)
            # General handling for string fields: take from highest priority document
            elif key in aggregated_data and isinstance(aggregated_data[key], str):
                if safe_string(value) != "null" and safe_string(value) != "" and \
                   (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
                    aggregated_data[key] = safe_string(value)
                    field_source_priority[key] = current_priority
            # Default for other types if they are not explicitly handled
            elif key in aggregated_data and value is not None:
                if current_priority > field_source_priority.get(key, -1):
                    aggregated_data[key] = value
                    field_source_priority[key] = current_priority

    # --- Post-aggregation calculations and reconciliation ---
    
    # Calculate `total_gross_income` (overall income from all heads)
    # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
    # try to derive it from payslip components like basic, HRA, etc.
    if aggregated_data["gross_salary_total"] == 0.0:
        aggregated_data["gross_salary_total"] = (
            safe_float(aggregated_data["basic_salary"]) +
            safe_float(aggregated_data["hra_received"]) +
            safe_float(aggregated_data["conveyance_allowance"]) +
            safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
            safe_float(aggregated_data["overtime_pay"]) +
            safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
            safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
        )
        # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
        # Assuming extracted values are already annual or normalized.

    # Now calculate the comprehensive total_gross_income for tax computation
    aggregated_data["total_gross_income"] = (
        safe_float(aggregated_data["gross_salary_total"]) +
        safe_float(aggregated_data["income_from_house_property"]) +
        safe_float(aggregated_data["income_from_other_sources"]) + 
        safe_float(aggregated_data["capital_gains_long_term"]) +
        safe_float(aggregated_data["capital_gains_short_term"])
    )
    aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

    # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
    # This prevents double counting if EPF is reported separately and also included in 80C
    # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
    # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
    # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
    if safe_float(aggregated_data["epf_contribution"]) > 0:
        aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
    # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
    aggregated_data["total_deductions_chapter_via"] = (
        safe_float(aggregated_data["deduction_80c"]) +
        safe_float(aggregated_data["deduction_80ccc"]) +
        safe_float(aggregated_data["deduction_80ccd"]) +
        safe_float(aggregated_data["deduction_80ccd1b"]) +
        safe_float(aggregated_data["deduction_80d"]) + # Corrected to use deduction_80d_actual later if needed
        safe_float(aggregated_data["deduction_80g"]) +
        safe_float(aggregated_data["deduction_80tta"]) +
        safe_float(aggregated_data["deduction_80ttb"]) +
        safe_float(aggregated_data["deduction_80e"])
    )
    aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


    # Aliases for frontend (ensure these are correctly populated from derived values)
    aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
    # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
    # This is a fallback and might not always reflect actual exemptions as per tax rules.
    if aggregated_data["total_exempt_allowances"] == 0.0:
        aggregated_data["total_exempt_allowances"] = (
            safe_float(aggregated_data.get("conveyance_allowance")) +
            safe_float(aggregated_data.get("transport_allowance")) +
            safe_float(aggregated_data.get("hra_received")) 
        )
        logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

    # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
    # This is a fixed amount applied during tax calculation, not a sum from documents.
    aggregated_data["standard_deduction"] = 50000.0 

    # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
    dob_str = safe_string(aggregated_data.get("date_of_birth"))
    if dob_str != "null" and dob_str != "0000-01-01":
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            aggregated_data["Age"] = age
        except ValueError:
            logging.warning(f"Could not parse date_of_birth: {dob_str}")
            aggregated_data["Age"] = "N/A"
    else:
        aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

    # Populate aliases for frontend display consistency
    aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
    aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
    aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
    aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
    aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
    aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
    aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
    aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
    aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

    # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
    # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
    # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
    # For display, we can show sum of what's *claimed* or *extracted*.
    # Let's make `total_deductions` a sum of all potential deductions for display.
    aggregated_data["total_deductions"] = (
        aggregated_data["standard_deduction"] + 
        aggregated_data["professional_tax"] +
        aggregated_data["interest_on_housing_loan_self_occupied"] +
        aggregated_data["total_deductions_chapter_via"]
    )
    aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


    # Sort all_transactions by date (oldest first)
    for tx in aggregated_data['transaction_summary']:
        if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
            try:
                tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
            except ValueError:
                tx['date_sortable'] = datetime.min # Fallback for unparseable dates
        else:
            tx['date_sortable'] = datetime.min

    aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
    # Remove the temporary sortable key
    for tx in aggregated_data['transaction_summary']:
        tx.pop('date_sortable', None)

    # If identified_type is still "null" or "Unknown" and some other fields populated,
    # try to infer a better type if possible, or leave as "Other Document"
    if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
        if safe_string(aggregated_data.get('employer_name')) != "null" and \
           safe_float(aggregated_data.get('gross_salary_total')) > 0:
           aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
        elif safe_string(aggregated_data.get('account_number')) != "null" and \
             (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
             aggregated_data["identified_type"] = "Bank Statement"
        elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
             safe_float(aggregated_data.get('hra_received')) > 0 or \
             safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
             aggregated_data["identified_type"] = "Salary Slip"

    # Ensure PAN and Financial Year are properly set for database grouping
    # If not extracted, try to get from previous records or default to "null"
    if safe_string(aggregated_data.get("pan_of_employee")) == "null":
        aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

    # Derive financial year from assessment year if financial_year is null
    if safe_string(aggregated_data.get("financial_year")) == "null" and safe_string(aggregated_data.get("assessment_year")) != "null":
        try:
            ay_parts = aggregated_data["assessment_year"].split('-')
            if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
                start_year = int(ay_parts[0]) -1
                end_year = int(ay_parts[0])
                aggregated_data["financial_year"] = f"{start_year}-{str(end_year)[-2:]}"
        except Exception:
            logging.warning(f"Could not derive financial year from assessment year: {aggregated_data.get('assessment_year')}")
            aggregated_data["financial_year"] = "UNKNOWNFY"
    elif safe_string(aggregated_data.get("financial_year")) == "null":
        aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
    logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
    return aggregated_data

def calculate_final_tax_summary(aggregated_data):
    """
    Calculates the estimated tax payable and refund status based on aggregated financial data.
    This function implements a SIMPLIFIED Indian income tax calculation for demonstration.
    !!! IMPORTANT: This must be replaced with actual, up-to-date, and comprehensive
    Indian income tax laws, considering both Old and New regimes, age groups,
    surcharges, cess, etc., for a production system. !!!

    Args:
        aggregated_data (dict): A dictionary containing aggregated financial fields.

    Returns:
        dict: A dictionary with computed tax liability, refund/due status, and notes.
    """
    
    # If the document type is a Bank Statement, skip tax calculation
    if aggregated_data.get('identified_type') == 'Bank Statement':
        return {
            "calculated_gross_income": 0.0,
            "calculated_total_deductions": 0.0,
            "computed_taxable_income": 0.0,
            "estimated_tax_payable": 0.0,
            "total_tds_credit": 0.0,
            "predicted_refund_due": 0.0,
            "predicted_additional_due": 0.0,
            "predicted_tax_regime": "N/A",
            "notes": ["Tax computation is not applicable for Bank Statements. Please upload tax-related documents like Form 16 or Salary Slips for tax calculation."],
            "old_regime_tax_payable": 0.0,
            "new_regime_tax_payable": 0.0,
            "calculation_details": ["Tax computation is not applicable for Bank Statements."],
            "regime_considered": "N/A"
        }

    # Safely extract and convert relevant values from aggregated_data
    gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
    # Deductions used for tax calculation (subject to limits and regime)
    total_chapter_via_deductions = safe_float(aggregated_data.get("total_deductions_chapter_via", 0)) 
    professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
    standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 0)) # Ensure standard deduction is fetched
    interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))

    # Sum all TDS and advance tax for comparison
    total_tds_credit = (
        safe_float(aggregated_data.get("total_tds", 0)) + 
        safe_float(aggregated_data.get("advance_tax", 0)) + 
        safe_float(aggregated_data.get("self_assessment_tax", 0))
    )

    tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
    age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
    if age == "N/A":
        age_group = "General"
    elif age < 60:
        age_group = "General"
    elif age >= 60 and age < 80:
        age_group = "Senior Citizen"
    else: # age >= 80
        age_group = "Super Senior Citizen"

    # --- Calculation Details List (for frontend display) ---
    calculation_details = []

    # --- Check for insufficient data for tax computation ---
    if gross_total_income < 100.0 and total_chapter_via_deductions < 100.0 and total_tds_credit < 100.0:
        calculation_details.append("Insufficient data provided for comprehensive tax calculation. Please upload documents with income and deduction details.")
        return {
            "calculated_gross_income": gross_total_income,
            "calculated_total_deductions": 0.0, # No significant deductions processed yet
            "computed_taxable_income": 0.0,
            "estimated_tax_payable": 0.0,
            "total_tds_credit": total_tds_credit,
            "predicted_refund_due": 0.0,
            "predicted_additional_due": 0.0,
            "predicted_tax_regime": "N/A",
            "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
            "old_regime_tax_payable": 0.0,
            "new_regime_tax_payable": 0.0,
            "calculation_details": calculation_details,
            "regime_considered": "N/A"
        }

    calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

    # --- Old Tax Regime Calculation ---
    # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
    # Chapter VI-A deductions are capped at their respective limits or overall 1.5L for 80C, etc.
    # For simplicity, we'll use the extracted `total_deductions_chapter_via` but it should ideally be capped.
    # The actual tax deduction limits should be applied here.
    
    # Cap 80C related deductions at 1.5 Lakhs
    deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
    # Cap 80D (Health Insurance) - simplified max 25k for general, 50k for senior parent (adjust as per actual rules)
    deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0) 
    # Cap Housing Loan Interest for self-occupied at 2 Lakhs
    interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

    # Simplified Chapter VI-A deductions for old regime (summing specific 80C, 80D, 80CCD1B, 80E, 80G, 80TTA, 80TTB)
    total_chapter_via_deductions_old_regime = (
        deduction_80c_actual +
        safe_float(aggregated_data.get("deduction_80ccc", 0)) +
        safe_float(aggregated_data.get("deduction_80ccd", 0)) +
        safe_float(aggregated_data.get("deduction_80ccd1b", 0)) +
        safe_float(aggregated_data.get("deduction_80d", 0)) + # Corrected to use deduction_80d_actual later if needed
        safe_float(aggregated_data.get("deduction_80g", 0)) +
        safe_float(aggregated_data.get("deduction_80tta", 0)) +
        safe_float(aggregated_data.get("deduction_80ttb", 0)) +
        safe_float(aggregated_data.get("deduction_80e", 0))
    )
    total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)


    # Total deductions for Old Regime
    total_deductions_old_regime_for_calc = (
        standard_deduction_applied + 
        professional_tax + 
        interest_on_housing_loan_actual + 
        total_chapter_via_deductions_old_regime
    )
    total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

    taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
    tax_before_cess_old_regime = 0

    calculation_details.append(f"2. Deductions under Old Regime:")
    calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
    calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
    calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
    calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
    calculation_details.append(f"   - Section 80D (capped at ₹25,000/₹50,000): ₹{deduction_80d_actual:,.2f}")
    calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual):,.2f}")
    calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
    calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

    # Old Regime Tax Slabs (simplified for AY 2024-25)
    if age_group == "General":
        if taxable_income_old_regime <= 250000:
            tax_before_cess_old_regime = 0
        elif taxable_income_old_regime <= 500000:
            tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
        elif taxable_income_old_regime <= 1000000:
            tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
        else:
            tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
    elif age_group == "Senior Citizen": # 60 to < 80
        if taxable_income_old_regime <= 300000:
            tax_before_cess_old_regime = 0
        elif taxable_income_old_regime <= 500000:
            tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
        elif taxable_income_old_regime <= 1000000:
            tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
        else:
            tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
    else: # Super Senior Citizen >= 80
        if taxable_income_old_regime <= 500000:
            tax_before_cess_old_regime = 0
        elif taxable_income_old_regime <= 1000000:
            tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
        else:
            tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

    rebate_87a_old_regime = 0
    if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
        rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
    tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
    total_tax_old_regime = round(tax_after_rebate_old_regime * 1.04, 2) # Add 4% Health and Education Cess
    calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
    calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
    calculation_details.append(f"6. Tax after Rebate (Old Regime): ₹{tax_after_rebate_old_regime:,.2f}")
    calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


    # --- New Tax Regime Calculation ---
    # From AY 2024-25, standard deduction is also applicable in the New Regime for salaried individuals.
    # Most Chapter VI-A deductions are *not* allowed in the New Regime, except employer's NPS contribution u/s 80CCD(2).
    # For simplicity, we assume only standard deduction and professional tax are applicable.
    # Also, housing loan interest deduction is NOT allowed for self-occupied property in New Regime.

    taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
    # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
    tax_before_cess_new_regime = 0

    calculation_details.append(f"8. Deductions under New Regime:")
    calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
    calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
    calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") # Only allowed ones
    calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


    # New Regime Tax Slabs (simplified for AY 2024-25 onwards)
    if taxable_income_new_regime <= 300000:
        tax_before_cess_new_regime = 0
    elif taxable_income_new_regime <= 700000:
        tax_before_cess_new_regime = (taxable_income_new_regime - 300000) * 0.05
    elif taxable_income_new_regime <= 1000000:
        tax_before_cess_new_regime = 15000 + (taxable_income_new_regime - 700000) * 0.10
    elif taxable_income_new_regime <= 1200000:
        tax_before_cess_new_regime = 45000 + (taxable_income_new_regime - 1000000) * 0.15
    elif taxable_income_new_regime <= 1500000:
        tax_before_cess_new_regime = 90000 + (taxable_income_new_regime - 1200000) * 0.20
    else:
        tax_before_cess_new_regime = 150000 + (taxable_income_new_regime - 1500000) * 0.30

    rebate_87a_new_regime = 0
    if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs
        rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
    tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
    total_tax_new_regime = round(tax_after_rebate_new_regime * 1.04, 2) # Add 4% Health and Education Cess

    calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
    calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
    calculation_details.append(f"12. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


    # --- Determine Optimal Regime and Final Summary ---
    final_tax_regime_applied = "N/A"
    estimated_tax_payable = 0.0
    computed_taxable_income = 0.0
    computation_notes = []

    # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
    if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
        estimated_tax_payable = total_tax_new_regime
        computed_taxable_income = taxable_income_new_regime
        final_tax_regime_applied = "New Regime (Chosen by User from Document)"
        computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
    elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
        estimated_tax_payable = total_tax_old_regime
        computed_taxable_income = taxable_income_old_regime
        final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
        computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
    else: # If no regime is explicitly chosen in documents, recommend the optimal one
        if total_tax_old_regime <= total_tax_new_regime:
            estimated_tax_payable = total_tax_old_regime
            computed_taxable_income = taxable_income_old_regime
            final_tax_regime_applied = "Old Regime (Optimal)"
            computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
        else:
            estimated_tax_payable = total_tax_new_regime
            computed_taxable_income = taxable_income_new_regime
            final_tax_regime_applied = "New Regime (Optimal)"
            computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

    estimated_tax_payable = round(estimated_tax_payable, 2)
    computed_taxable_income = round(computed_taxable_income, 2)

    # --- Calculate Refund/Tax Due ---
    refund_due_from_tax = 0.0
    tax_due_to_government = 0.0

    calculation_details.append(f"13. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
    if total_tds_credit > estimated_tax_payable:
        refund_due_from_tax = total_tds_credit - estimated_tax_payable
        calculation_details.append(f"14. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
    elif total_tds_credit < estimated_tax_payable:
        tax_due_to_government = estimated_tax_payable - total_tds_credit
        calculation_details.append(f"14. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
    else:
        calculation_details.append("14. No Refund or Additional Tax Due.")


    return {
        "calculated_gross_income": gross_total_income,
        "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
        "computed_taxable_income": computed_taxable_income,
        "estimated_tax_payable": estimated_tax_payable,
        "total_tds_credit": total_tds_credit,
        "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
        "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
        "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
        "notes": computation_notes, # List of notes
        "old_regime_tax_payable": total_tax_old_regime,
        "new_regime_tax_payable": total_tax_new_regime,
        "calculation_details": calculation_details,
        "regime_considered": final_tax_regime_applied # For clarity in the UI
    }

def generate_ml_prediction_summary(financial_data):
    """
    Generates ML model prediction summary using the loaded models.
    """
    if tax_regime_classifier_model is None or tax_regressor_model is None:
        logging.warning("ML models are not loaded. Cannot generate ML predictions.")
        return {
            "predicted_tax_regime": "N/A",
            "predicted_tax_liability": 0.0,
            "predicted_refund_due": 0.0,
            "predicted_additional_due": 0.0,
            "notes": "ML prediction service unavailable (models not loaded or training failed)."
        }

    # If the aggregated data is primarily from a bank statement, ML prediction for tax is not relevant
    if financial_data.get('identified_type') == 'Bank Statement' and financial_data.get('total_gross_income', 0.0) < 100.0:
        return {
            "predicted_tax_regime": "N/A",
            "predicted_tax_liability": 0.0,
            "predicted_refund_due": 0.0,
            "predicted_additional_due": 0.0,
            "notes": "ML prediction not applicable for bank statements. Please upload tax-related documents."
        }
    # Define the features expected by the ML models (must match model_trainer.py)
    # IMPORTANT: These must precisely match the features used in model_trainer.py
    # Re-verify against your `model_trainer.py` to ensure exact match.
    ml_common_numerical_features = [
        'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
        'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
        'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
        'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
        'Total Exempt Allowances Claimed'
    ]
    ml_categorical_features = ['Residential Status', 'Gender']
    
    # Prepare input for classifier model
    age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
    # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
    # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
    # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
    calculated_other_deductions = (
        safe_float(financial_data.get('deduction_80ccc', 0)) +
        safe_float(financial_data.get('deduction_80ccd', 0)) +
        safe_float(financial_data.get('deduction_80ccd1b', 0)) +
        safe_float(financial_data.get('deduction_80g', 0)) +
        safe_float(financial_data.get('deduction_80tta', 0)) +
        safe_float(financial_data.get('deduction_80ttb', 0))
    )
    calculated_other_deductions = round(calculated_other_deductions, 2)


    classifier_input_data = {
        'Age': age_value,
        'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
        'HRA Received': safe_float(financial_data.get('hra_received', 0)),
        'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
        'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
        'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
        'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
        'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
        'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
        'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
        'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
        'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
        'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
        'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
        'Gender': safe_string(financial_data.get('gender', 'Unknown'))
    }
    
    # Create DataFrame for classifier prediction, ensuring column order
    # The order must match `model_trainer.py`'s `classifier_all_features`
    ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
    classifier_df = pd.DataFrame([classifier_input_data])
    
    predicted_tax_regime = "N/A"
    try:
        classifier_df_processed = classifier_df[ordered_classifier_features]
        predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
        logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
    except Exception as e:
        logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
        predicted_tax_regime = "Prediction Failed (Error)"
        
    # Prepare input for regressor model
    # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
    regressor_input_data = {
        k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
    }
    regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

    regressor_df = pd.DataFrame([regressor_input_data])
    
    predicted_tax_liability = 0.0
    try:
        # The regressor's preprocessor will handle the categorical feature conversion.
        # Just ensure the input DataFrame has the correct columns and order.
        ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
        regressor_df_processed = regressor_df[ordered_regressor_features]
        predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
        logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
    except Exception as e:
        logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
        predicted_tax_liability = 0.0 # Default to 0 if prediction fails

    # Calculate refund/additional due based on ML prediction and actual TDS
    total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

    predicted_refund_due = 0.0
    predicted_additional_due = 0.0

    if total_tds_credit > predicted_tax_liability:
        predicted_refund_due = total_tds_credit - predicted_tax_liability
    elif total_tds_credit < predicted_tax_liability:
        predicted_additional_due = predicted_tax_liability - total_tds_credit
        
    # Convert any numpy types before returning
    return convert_numpy_types({
        "predicted_tax_regime": predicted_tax_regime,
        "predicted_tax_liability": predicted_tax_liability,
        "predicted_refund_due": round(predicted_refund_due, 2),
        "predicted_additional_due": round(predicted_additional_due, 2),
        "notes": "ML model predictions for optimal regime and tax liability."
    })

def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
    """Generates tax-saving suggestions and regime analysis using Gemini API."""
    if gemini_pro_model is None:
        logging.error("Gemini API (gemini_pro_model) not initialized.")
        return ["AI suggestions unavailable."], "AI regime analysis unavailable."

    # Check if tax computation was not possible (e.g., for Bank Statements or insufficient data)
    if "Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0] or \
       aggregated_financial_data.get('identified_type') == 'Bank Statement':
        return (
            ["For personalized tax-saving suggestions, please upload tax-related documents like Form 16, Salary Slips, Form 26AS, and investment proofs."],
            "Tax regime analysis requires complete income and deduction data from tax-related documents."
        )


    # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
    financial_data_for_gemini = aggregated_financial_data.copy()

    # Add specific structure for Bank Statement details if identified as such, or if bank details are present
    if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
        financial_data_for_gemini['Bank Details'] = {
            'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
            'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
            'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
            'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
            'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
            'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
            'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
            'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
        }
        # Optionally, remove transaction_summary if it's too verbose for the prompt
        # financial_data_for_gemini.pop('transaction_summary', None)


    prompt = f"""
    You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
    Based on this data:
    1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
    2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

    **Financial Data Summary:**
    {json.dumps(financial_data_for_gemini, indent=2)}

    **Final Tax Computation Summary:**
    {json.dumps(final_tax_computation_summary, indent=2)}

    Please format your response strictly as follows:
    Suggestions:
    - [Suggestion 1]
    - [Suggestion 2]
    ...
    Regime Analysis: [Your analysis paragraph here].
    """
    try:
        response = gemini_pro_model.generate_content(prompt)
        text = response.text.strip()
        
        suggestions = []
        regime_analysis = ""

        # Attempt to parse the structured output
        if "Suggestions:" in text and "Regime Analysis:" in text:
            parts = text.split("Regime Analysis:")
            suggestions_part = parts[0].replace("Suggestions:", "").strip()
            regime_analysis = parts[1].strip()

            # Split suggestions into bullet points and filter out empty strings
            suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
            if not suggestions: # If parsing as bullets failed, treat as single suggestion
                suggestions = [suggestions_part]
        else:
            # Fallback if format is not as expected, return raw text as suggestions
            suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
            regime_analysis = "AI could not parse structured regime analysis."
            logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

        return suggestions, regime_analysis
    except Exception as e:
        logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
        return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

def generate_itr_pdf(tax_record_data):
    """
    Generates a dummy ITR form PDF.
    This uses a basic PDF string structure as a placeholder.
    """
    aggregated_data = tax_record_data.get('aggregated_financial_data', {})
    final_computation = tax_record_data.get('final_tax_computation_summary', {})

    # Determine ITR type (simplified logic)
    itr_type = "ITR-1 (SAHAJ - DUMMY)"
    if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
       safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
       safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
        itr_type = "ITR-2 (DUMMY)"
    
    # Extract key info for the dummy PDF
    name = aggregated_data.get('name_of_employee', 'N/A')
    pan = aggregated_data.get('pan_of_employee', 'N/A')
    financial_year = aggregated_data.get('financial_year', 'N/A')
    assessment_year = aggregated_data.get('assessment_year', 'N/A')
    total_income = final_computation.get('computed_taxable_income', 'N/A')
    tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
    refund_due = final_computation.get('predicted_refund_due', 0.0)
    tax_due = final_computation.get('predicted_additional_due', 0.0)
    regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

    # Add bank statement specific details to the PDF content if available
    bank_details_for_pdf = ""
    # Check if the aggregated data's identified type is 'Bank Statement' or if it contains core bank details
    if aggregated_data.get('identified_type') == 'Bank Statement' or \
       (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
        bank_details_for_pdf = f"""
BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
"""

    # Core PDF content without xref and EOF for length calculation
    core_pdf_content_lines = [
        f"%PDF-1.4",
        f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
        f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
        f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
        f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
        f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
        f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
        f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
        f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
        f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
        f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
        f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
        f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
        f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
        f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
        f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
        f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
        f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
        f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
    ]
    
    # Append bank details if available
    if bank_details_for_pdf:
        core_pdf_content_lines.append(bank_details_for_pdf)
        # Adjust vertical position for the Note if bank details were added
        core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
    else:
        core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

    core_pdf_content_lines.extend([
        f"endstream",
        f"endobj",
        f"xref",
        f"0 5",
        f"0000000000 65535 f",
        f"0000000010 00000 n",
        f"0000000057 00000 n",
        f"0000000114 00000 n",
        f"0000000222 00000 n",
        f"trailer <</Size 5 /Root 1 0 R>>",
    ])
    
    # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
    core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
    core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

    # Calculate the startxref position
    startxref_position = len(core_pdf_bytes)

    # Now assemble the full PDF content including startxref and EOF
    full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
    # Final encode
    dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

    return io.BytesIO(dummy_pdf_content_bytes), itr_type


# --- API Routes ---

# Serves the main page (assuming index.html is in the root)
@app.route('/')
def home():
    """Serves the main landing page, typically index.html."""
    return send_from_directory('.', 'index.html')

# Serves other static files (CSS, JS, images, etc.)
@app.route('/<path:path>')
def serve_static_files(path):
    """Serves static files from the root directory."""
    return send_from_directory('.', path)

# Serves uploaded files from the uploads folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Allows access to temporarily stored uploaded files."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        logging.warning(f"File '{filename}' not found in uploads folder.")
        return jsonify({"message": "File not found"}), 404
    except Exception as e:
        logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
        return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


@app.route('/api/register', methods=['POST'])
def register_user():
    """Handles user registration."""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            logging.warning("Registration attempt with missing fields.")
            return jsonify({"message": "Username, email, and password are required"}), 400

        # Check if email or username already exists
        if users_collection.find_one({"email": email}):
            logging.warning(f"Registration failed: Email '{email}' already exists.")
            return jsonify({"message": "Email already exists"}), 409
        if users_collection.find_one({"username": username}):
            logging.warning(f"Registration failed: Username '{username}' already exists.")
            return jsonify({"message": "Username already exists"}), 409

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Prepare user data for MongoDB insertion
        new_user_data = {
            "username": username,
            "email": email,
            "password": hashed_password.decode('utf-8'), # Store hashed password as string
            "full_name": data.get('fullName', ''),
            "pan": data.get('pan', ''),
            "aadhaar": data.get('aadhaar', ''),
            "address": data.get('address', ''),
            "phone": data.get('phone', ''),
            "created_at": datetime.utcnow()
        }
        # Insert the new user record and get the inserted ID
        user_id = users_collection.insert_one(new_user_data).inserted_id
        logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
        return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
    except Exception as e:
        logging.error(f"Error during registration: {traceback.format_exc()}")
        return jsonify({"message": "An error occurred during registration."}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """Handles user login and JWT token generation."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logging.warning("Login attempt with missing credentials.")
            return jsonify({"error_msg": "Username and password are required"}), 400

        # Find the user by username
        user = users_collection.find_one({"username": username})

        # Verify user existence and password
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')): # Corrected this line
            # Create a JWT access token with the user's MongoDB ObjectId as identity
            access_token = create_access_token(identity=str(user['_id']))
            logging.info(f"User '{username}' logged in successfully.")
            return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
        else:
            logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
            return jsonify({"error_msg": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Error during login: {traceback.format_exc()}")
        return jsonify({"error_msg": "An error occurred during login."}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Fetches the profile of the currently authenticated user."""
    try:
        # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
        current_user_id = get_jwt_identity()
        # Find user by ObjectId, exclude password from the result
        user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
        if not user:
            logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
            return jsonify({"message": "User not found"}), 404

        # Convert ObjectId to string for JSON serialization
        user['_id'] = str(user['_id'])
        logging.info(f"Profile fetched for user ID: {current_user_id}")
        return jsonify({"user": user}), 200
    except Exception as e:
        logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
        return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

@app.route('/api/profile', methods=['PUT', 'PATCH'])
@jwt_required()
def update_user_profile():
    """Updates the profile of the currently authenticated user."""
    try:
        current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
        data = request.get_json()

        # Define allowed fields for update
        updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
        update_data = {k: data[k] for k in updatable_fields if k in data}

        if not update_data:
            logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
            return jsonify({"message": "No fields to update provided."}), 400
        
        # Prevent username from being updated via this route for security/simplicity
        if 'username' in data:
            logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

        # If email is being updated, ensure it's not already in use by another user
        if 'email' in update_data:
            existing_user_with_email = users_collection.find_one({"email": update_data['email']})
            if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
                logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
                return jsonify({"message": "Email already in use by another account."}), 409

        # Perform the update operation in MongoDB
        result = users_collection.update_one(
            {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
            {"$set": update_data}
        )

        if result.matched_count == 0:
            logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
            return jsonify({"message": "User not found."}), 404
        if result.modified_count == 0:
            logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
            return jsonify({"message": "Profile data is the same, no changes made."}), 200

        logging.info(f"Profile updated successfully for user ID: {current_user_id}")
        return jsonify({"message": "Profile updated successfully!"}), 200
    except Exception as e:
        logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
        return jsonify({"message": "An error occurred while updating your profile."}), 500


@app.route('/api/process_documents', methods=['POST'])
@jwt_required()
def process_documents():
    """
    Handles uploaded documents, extracts financial data using Gemini and Vision API,
    aggregates data from multiple files, computes tax, and saves the comprehensive
    record to MongoDB, grouped by PAN and Financial Year.
    """
    current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

    if 'documents' not in request.files:
        logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
        return jsonify({"message": "No 'documents' part in the request"}), 400

    files = request.files.getlist('documents')
    if not files:
        logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
        return jsonify({"message": "No selected file"}), 400

    extracted_data_from_current_upload = []
    document_processing_summary_current_upload = [] # To provide feedback on each file

    # Get the selected document type hint from the form data (if provided)
    document_type_hint = request.form.get('document_type', 'Auto-Detect') 
    logging.info(f"Received document type hint from frontend: {document_type_hint}")

    for file in files:
        if file.filename == '':
            document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
            continue
        
        filename = secure_filename(file.filename)
        # Create a unique filename for storing the original document
        unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file_content_bytes = file.read() # Read content before saving
            file.seek(0) # Reset file pointer for subsequent operations if needed

            # Save the file temporarily (or permanently if you wish to retain originals)
            with open(file_path, 'wb') as f:
                f.write(file_content_bytes)
            logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

            mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default

            # Construct the base prompt for Gemini
            base_prompt_instructions = (
                f"You are an expert financial data extractor and tax document analyzer for Indian context. "
                f"Analyze the provided document (filename: '{filename}', MIME type: {mime_type}). "
                f"The user has indicated this document is of type: '{document_type_hint}'. " 
                "Extract ALL relevant financial information for Indian income tax filing. "
                "Your response MUST be a JSON object conforming precisely to the provided schema. "
                "For numerical fields, if a value is not explicitly found or is clearly zero, you MUST use `0.0`. "
                "For string fields (like names, PAN, year, dates, identified_type, gender, residential_status), if a value is not explicitly found, you MUST use the string `null`. "
                "For dates, if found, use 'YYYY-MM-DD' format if possible; otherwise, `0000-01-01` if not found or cannot be parsed.\n\n"
            )

            # Add specific instructions based on document type hint
            if document_type_hint == 'Bank Statement':
                base_prompt_instructions += (
                    "Specifically for a Bank Statement, extract the following details accurately:\n"
                    "- Account Holder Name\n- Account Number\n- IFSC Code (if present)\n- Bank Name\n"
                    "- Branch Address\n- Statement Start Date (YYYY-MM-DD)\n- Statement End Date (YYYY-MM-DD)\n"
                    "- Opening Balance\n- Closing Balance\n- Total Deposits\n- Total Withdrawals\n"
                    "- A summary of key transactions, including date (YYYY-MM-DD), description, and amount. Prioritize large transactions or those with specific identifiable descriptions (e.g., 'salary', 'rent', 'interest').\n"
                    "If a field is not found or not applicable, use `null` for strings and `0.0` for numbers. Ensure dates are in YYYY-MM-DD format."
                )
            elif document_type_hint == 'Form 16':
                base_prompt_instructions += (
                    "Specifically for Form 16, extract details related to employer, employee, PAN, TAN, financial year, assessment year, "
                    "salary components (basic, HRA, perquisites, profits in lieu of salary), exempt allowances, professional tax, "
                    "income from house property, income from other sources, capital gains, "
                    "deductions under Chapter VI-A (80C, 80D, 80G, 80E, 80CCD, etc.), TDS details (total, quarter-wise), "
                    "and any mentioned tax regime (Old/New). Ensure all monetary values are extracted as numbers."
                )
            elif document_type_hint == 'Salary Slip':
                base_prompt_instructions += (
                    "Specifically for a Salary Slip, extract employee name, PAN, employer name, basic salary, HRA, "
                    "conveyance allowance, transport allowance, overtime pay, EPF contribution, ESI contribution, "
                    "professional tax, net amount payable, days present, and overtime hours. Ensure all monetary values are extracted as numbers."
                )
            # Add more elif blocks for other specific document types if needed

            if "image" in mime_type or "pdf" in mime_type:
                gemini_response_json_str = get_gemini_response(base_prompt_instructions, file_data=file_content_bytes, mime_type=mime_type, filename=filename)
            elif "text" in mime_type or "json" in mime_type:
                extracted_raw_text = file_content_bytes.decode('utf-8')
                final_prompt_content = base_prompt_instructions + f"\n\nDocument Content:\n{extracted_raw_text}"
                gemini_response_json_str = get_gemini_response(final_prompt_content, filename=filename)
            else:
                document_processing_summary_current_upload.append({
                    "filename": filename, "status": "skipped", "identified_type": "Unsupported",
                    "message": f"Unsupported file type: {mime_type}"
                })
                continue
            
            try:
                gemini_parsed_response = json.loads(gemini_response_json_str)
                if gemini_parsed_response.get("error"):
                    raise ValueError(f"AI processing error: {gemini_parsed_response['error']}")

                extracted_data = gemini_parsed_response.get('extracted_data', {})
                
                if "raw_text_response" in extracted_data:
                    document_processing_summary_current_upload.append({
                        "filename": filename, "status": "warning", "identified_type": "Unstructured Text",
                        "message": "AI could not extract structured JSON. Raw text available.",
                        "extracted_raw_text": extracted_data["raw_text_response"],
                        "stored_path": f"/uploads/{unique_filename}"
                    })
                    extracted_data_from_current_upload.append({"identified_type": "Unstructured Text", "raw_text": extracted_data["raw_text_response"]})
                    continue 
                # Add the path to the stored document for future reference in history
                extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
                extracted_data_from_current_upload.append(extracted_data)

                document_processing_summary_current_upload.append({
                    "filename": filename, "status": "success", "identified_type": extracted_data['identified_type'],
                    "message": "Processed successfully.", "extracted_fields": extracted_data,
                    "stored_path": f"/uploads/{unique_filename}" 
                })
            except (json.JSONDecodeError, ValueError) as ve:
                logging.error(f"Error parsing Gemini response or AI error for '{filename}': {ve}")
                document_processing_summary_current_upload.append({
                    "filename": filename, "status": "failed", "message": f"AI response error: {str(ve)}",
                    "stored_path": f"/uploads/{unique_filename}"
                })
            except Exception as e:
                logging.error(f"Unexpected error processing Gemini data for '{filename}': {traceback.format_exc()}")
                document_processing_summary_current_upload.append({
                    "filename": filename, "status": "failed", "message": f"Error processing AI data: {str(e)}",
                    "stored_path": f"/uploads/{unique_filename}"
                })
            finally:
                pass 

        except Exception as e:
            logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
            document_processing_summary_current_upload.append({
                "filename": filename, "status": "error",
                "message": f"An unexpected error occurred during file processing: {str(e)}",
                "stored_path": f"/uploads/{unique_filename}"
            })
            pass 

    if not extracted_data_from_current_upload:
        logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
        return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

    # --- Determine PAN and Financial Year for grouping ---
    # Try to find PAN and FY from the currently uploaded documents first
    pan_of_employee = "UNKNOWNPAN"
    financial_year = "UNKNOWNFY"

    for data in extracted_data_from_current_upload:
        if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
            pan_of_employee = safe_string(data["pan_of_employee"])
        if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
            financial_year = safe_string(data["financial_year"])
        # If both are found, we can break early (or continue to see if a higher priority doc has them)
        if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
            break
    
    # If still unknown, check if the user profile has a PAN.
    if pan_of_employee == "UNKNOWNPAN":
        user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
        if user_profile and safe_string(user_profile.get("pan")) != "null":
            pan_of_employee = safe_string(user_profile["pan"])
            logging.info(f"Using PAN from user profile: {pan_of_employee}")
        else:
            # If PAN is still unknown, log a warning and use the placeholder
            logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

    # Derive financial year from assessment year if financial_year is null
    if financial_year == "UNKNOWNFY":
        for data in extracted_data_from_current_upload:
            if safe_string(data.get("assessment_year")) != "null":
                try:
                    ay_parts = safe_string(data["assessment_year"]).split('-')
                    if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
                        start_year = int(ay_parts[0]) -1
                        fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
                        if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
                            financial_year = fy
                            break
                except Exception:
                    pass # Keep default if parsing fails
        if financial_year == "UNKNOWNFY":
            logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


    # Try to find an existing record for this user, PAN, and financial year
    existing_tax_record = tax_records_collection.find_one({
        "user_id": current_user_id,
        "pan_of_employee": pan_of_employee, # Querying top-level field
        "financial_year": financial_year    # Querying top-level field
    })

    if existing_tax_record:
        logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
        # Merge new extracted data with existing data
        all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
        all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

        # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
        updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
        updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

        # Clear previous AI/ML results as they need to be re-generated for the updated data
        tax_records_collection.update_one(
            {"_id": existing_tax_record["_id"]},
            {"$set": {
                "extracted_documents_data": all_extracted_data_for_fy,
                "document_processing_summary": all_document_processing_summary_for_fy,
                "aggregated_financial_data": updated_aggregated_financial_data,
                "final_tax_computation_summary": updated_final_tax_computation_summary,
                "timestamp": datetime.utcnow(), # Update timestamp of last modification
                "suggestions_from_gemini": [], # Reset suggestions
                "gemini_regime_analysis": "null", # Reset regime analysis
                "ml_prediction_summary": {}, # Reset ML predictions
            }}
        )
        record_id = existing_tax_record["_id"]
        logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

    else:
        logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
        # If no existing record, aggregate only the newly uploaded data
        new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
        new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

        # Prepare the comprehensive tax record to save to MongoDB
        tax_record_to_save = {
            "user_id": current_user_id, 
            "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
            "financial_year": financial_year, # Store FY at top level for easy query
            "timestamp": datetime.utcnow(),
            "document_processing_summary": document_processing_summary_current_upload, 
            "extracted_documents_data": extracted_data_from_current_upload, 
            "aggregated_financial_data": new_aggregated_financial_data,
            "final_tax_computation_summary": new_final_tax_computation_summary,
            "suggestions_from_gemini": [], 
            "gemini_regime_analysis": "null", 
            "ml_prediction_summary": {},    
        }
        record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
        logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
        updated_aggregated_financial_data = new_aggregated_financial_data
        updated_final_tax_computation_summary = new_final_tax_computation_summary


    # Return success response with computed data
    # Ensure all data sent back is JSON serializable (e.g., no numpy types)
    response_data = {
        "status": "success",
        "message": "Documents processed and financial data aggregated and tax computed successfully",
        "record_id": str(record_id), 
        "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
        "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
        "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
    }
    return jsonify(response_data), 200


@app.route('/api/get_suggestions', methods=['POST'])
@jwt_required()
def get_suggestions():
    """
    Generates AI-driven tax-saving suggestions and provides an ML prediction summary
    based on a specific processed tax record (grouped by PAN/FY).
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    record_id = data.get('record_id')

    if not record_id:
        logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
        return jsonify({"message": "Record ID is required to get suggestions."}), 400

    try:
        # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
        tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
        if not tax_record:
            logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
            return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
        # Get the aggregated financial data and final tax computation summary from the record
        aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
        final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

        # Generate suggestions and ML predictions
        suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
        ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

        # Update the record in DB with generated suggestions and predictions
        tax_records_collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": {
                "suggestions_from_gemini": suggestions,
                "gemini_regime_analysis": regime_analysis,
                "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
                "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
            }}
        )
        logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

        return jsonify({
            "status": "success",
            "message": "AI suggestions and ML predictions generated successfully!",
            "suggestions_from_gemini": suggestions,
            "gemini_regime_analysis": regime_analysis,
            "ml_prediction_summary": ml_prediction_summary # Already converted
        }), 200
    except Exception as e:
        logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
        # Fallback for ML prediction summary even if overall suggestions fail
        ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
        return jsonify({
            "status": "error",
            "message": "An error occurred while generating suggestions.",
            "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
            "gemini_regime_analysis": "An error occurred.",
            "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
        }), 500

@app.route('/api/save_extracted_data', methods=['POST'])
@jwt_required()
def save_extracted_data():
    """
    Saves extracted and computed tax data to MongoDB.
    This route can be used for explicit saving if `process_documents` doesn't
    cover all saving scenarios or for intermediate saves.
    NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
    For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
    """
    current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
    data = request.get_json()
    if not data:
        logging.warning(f"Save data request from user {current_user_id} with no data provided.")
        return jsonify({"message": "No data provided to save"}), 400
    try:
        # This route might be less relevant with the new aggregation by PAN/FY,
        # as `process_documents` handles the upsert logic.
        # However, if used for manual saving of *already aggregated* data,
        # ensure PAN and FY are part of `data.aggregated_financial_data`
        # or extracted from the `data` directly.
        # Example: Try to get PAN and FY from input data for consistency
        input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
        input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

        # Check for existing record for upsert behavior
        existing_record = tax_records_collection.find_one({
            "user_id": current_user_id,
            "pan_of_employee": input_pan, # Querying top-level field
            "financial_year": input_fy    # Querying top-level field
        })

        if existing_record:
            # Update existing record
            update_result = tax_records_collection.update_one(
                {"_id": existing_record["_id"]},
                {"$set": {
                    **data, # Overwrite with new data, ensuring user_id and timestamp are also set
                    "user_id": current_user_id,
                    "timestamp": datetime.utcnow(),
                    "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
                    "financial_year": input_fy, # Ensure top-level FY is consistent
                }}
            )
            record_id = existing_record["_id"]
            logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
            if update_result.modified_count == 0:
                return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
        else:
            # Insert new record
            data['user_id'] = current_user_id
            data['timestamp'] = datetime.utcnow()
            data['pan_of_employee'] = input_pan
            data['financial_year'] = input_fy
            record_id = tax_records_collection.insert_one(data).inserted_id
            logging.info(f"New data saved for user {current_user_id} with record ID: {record_id}")
        
        return jsonify({"message": "Data saved successfully", "record_id": str(record_id)}), 200
    except Exception as e:
        logging.error(f"Error saving data for user {current_user_id}: {traceback.format_exc()}")
        return jsonify({"message": "Failed to save data", "error": str(e)}), 500

# @app.route('/api/tax_history', methods=['GET'])
# @jwt_required()
# def get_tax_records():
#     """
#     Fetches all aggregated tax records for the logged-in user, grouped by Financial Year.
#     Records are sorted by timestamp in descending order (most recent first).
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#     logging.info(f"Fetching tax records for user: {current_user_id}")
#     try:
#         # Fetch all records for the current user, sorted by financial_year and then by timestamp
#         # The 'user_id', 'pan_of_employee', and 'financial_year' are top-level fields now
#         records = list(tax_records_collection.find({"user_id": current_user_id})
#                         .sort([("financial_year", -1), ("timestamp", -1)]))

#         # Convert MongoDB ObjectId to string for JSON serialization
#         for record in records:
#             record['_id'] = str(record['_id'])
#             # Ensure 'user_id' is also a string when sending to frontend
#             if 'user_id' in record:
#                 record['user_id'] = str(record['user_id'])
#             # Ensure required fields for frontend table display are present, even if 'N/A'
#             # This is crucial for records created before these fields were consistently populated or if parsing failed
#             if 'aggregated_financial_data' not in record:
#                 record['aggregated_financial_data'] = {}
#             if 'final_tax_computation_summary' not in record:
#                 record['final_tax_computation_summary'] = {}

#             # Populate display fields if missing from aggregated_financial_data
#             record['aggregated_financial_data']['financial_year'] = record.get('financial_year', 'N/A')
#             record['aggregated_financial_data']['total_gross_income'] = record['aggregated_financial_data'].get('total_gross_income', 0.0)
            
#             # Populate display fields if missing from final_tax_computation_summary
#             record['final_tax_computation_summary']['estimated_tax_payable'] = record['final_tax_computation_summary'].get('estimated_tax_payable', 0.0)
#             record['final_tax_computation_summary']['predicted_refund_due'] = record['final_tax_computation_summary'].get('predicted_refund_due', 0.0)
#             record['final_tax_computation_summary']['predicted_additional_due'] = record['final_tax_computation_summary'].get('predicted_additional_due', 0.0)

#             # Remove potentially large raw data fields for history list view to save bandwidth
#             record.pop('extracted_documents_data', None)
#         logging.info(f"Found {len(records)} tax records for user {current_user_id}")
#         # The frontend's TaxHistory component expects a 'history' key in the response data.
#         return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200 # Convert numpy types
#     except Exception as e:
#         logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

@app.route('/api/generate-itr/<record_id>', methods=['GET'])
@jwt_required()
def generate_itr_form_route(record_id):
    """
    Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
    """
    current_user_id = get_jwt_identity()
    try:
        record_obj_id = ObjectId(record_id) # Convert record_id string to ObjectId for DB query
        # Ensure the tax record belongs to the current user (user_id check)
        tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

        if not tax_record:
            logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
            return jsonify({"message": "Tax record not found or you are not authorized to access it."}), 404

        # Generate the dummy PDF content
        pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
        pdf_buffer.seek(0) # Rewind the buffer to the beginning

        response = send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{itr_type.replace(' ', '_')}_{record_id}.pdf"
        )
        logging.info(f"Generated and sent dummy ITR form for record ID: {record_id}")
        return response
    except Exception as e:
        logging.error(f"Error generating ITR form for record {record_id}: {traceback.format_exc()}")
        return jsonify({"message": "Failed to generate ITR form.", "error": str(e)}), 500
@app.route("/api/tax-records", methods=["GET"])
@jwt_required()
def get_tax_history():
    current_user_id = get_jwt_identity()

    try:
        all_records = list(tax_records_collection.find({"user_id": current_user_id}))
        formatted_records = []

        for record in all_records:
            record["_id"] = str(record["_id"])
            formatted_records.append(record)

        return jsonify({
            "status": "success",
            "history": formatted_records
        }), 200

    except Exception as e:
        logging.error(f"Error fetching tax records: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve tax history"
        }), 500

@app.route('/api/contact', methods=['POST'])
def contact_message():
    """Handles contact form submissions."""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([name, email, subject, message]):
            logging.warning("Contact form submission with missing fields.")
            return jsonify({"message": "All fields are required."}), 400
        
        # Insert contact message into MongoDB
        contact_messages_collection.insert_one({
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.utcnow()
        })
        logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
        return jsonify({"message": "An error occurred while sending your message."}), 500

# --- Main application entry point ---
if __name__ == '__main__':
    # Ensure MongoDB connection is established before running the app
    if db is None:
        logging.error("MongoDB connection failed at startup. Exiting.")
        exit(1)
    
    logging.info("Starting Flask application...")
    # Run the Flask app
    # debug=True enables reloader and debugger (should be False in production)
    # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
    # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

