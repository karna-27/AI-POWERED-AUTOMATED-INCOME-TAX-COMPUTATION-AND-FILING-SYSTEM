# # import os
# # import json
# # from flask import Flask, request, jsonify, send_from_directory, send_file
# # from flask_cors import CORS
# # import google.generativeai as genai
# # from pymongo import MongoClient
# # from bson.objectid import ObjectId
# # import bcrypt
# # import traceback
# # import logging
# # import io
# # from datetime import datetime, timedelta
# # from google.cloud import vision
# # from google.oauth2 import service_account
# # from werkzeug.utils import secure_filename # Import secure_filename
# # import joblib # Import joblib for loading ML models
# # import pandas as pd # Import pandas for ML model input

# # # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# # import numpy as np

# # # Import ReportLab components for PDF generation
# # try:
# #     # Commented out ReportLab imports as per previous turn, using dummy PDF for now.
# #     # from reportlab.pdfgen import canvas
# #     # from reportlab.lib.pagesizes import letter
# #     # from reportlab.lib.units import inch
# #     # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# #     # from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
# #     # from reportlab.lib.enums import TA_CENTER
# #     REPORTLAB_AVAILABLE = False # Set to False since using dummy PDF
# # except ImportError:
# #     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
# #     REPORTLAB_AVAILABLE = False


# # # Configure logging for better visibility
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # --- Configuration (IMPORTANT: Using hardcoded keys as per user's request) ---
# # # In a real-world production environment, these should ALWAYS be loaded from
# # # environment variables (e.g., using os.getenv) and never hardcoded.
# # GEMINI_API_KEY_HARDCODED = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs"
# # MONGO_URI_HARDCODED = "mongodb://localhost:27017/"
# # JWT_SECRET_KEY_HARDCODED = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# # # Ensure the path for Vision API key is correct for your system. Use a raw string (r"")
# # # or forward slashes (/) for paths to avoid issues with backslashes.
# # VISION_API_KEY_PATH_HARDCODED = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json"

# # # Initialize Flask app
# # app = Flask(__name__)
# # # Enable CORS for all origins, allowing frontend to communicate. For production, restrict this.
# # CORS(app)

# # # --- JWT Configuration ---
# # app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY_HARDCODED
# # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Tokens expire in 24 hours
# # # UNCOMMENTED: Corrected the NameError by uncommenting the import below
# # from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# # jwt = JWTManager(app)

# # # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# # @jwt.expired_token_loader
# # def expired_token_callback(jwt_header, jwt_payload):
# #     logging.warning("JWT token expired.")
# #     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# # @jwt.invalid_token_loader
# # def invalid_token_callback(callback_error):
# #     logging.warning(f"Invalid JWT token: {callback_error}")
# #     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# # @jwt.unauthorized_loader
# # def unauthorized_callback(callback_error):
# #     logging.warning(f"Unauthorized access attempt: {callback_error}")
# #     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401
# # # --- End JWT Configuration ---


# # # --- MongoDB Connection ---
# # client = None
# # db = None
# # users_collection = None
# # tax_records_collection = None
# # contact_messages_collection = None

# # try:
# #     client = MongoClient(MONGO_URI_HARDCODED)
# #     db = client['garudatax_db'] # Using a more specific database name for tax application
# #     users_collection = db['users']
# #     tax_records_collection = db['tax_records'] # This collection will store aggregated records per FY
# #     contact_messages_collection = db['contact_messages']
# #     logging.info("MongoDB connected successfully.")
# # except Exception as e:
# #     logging.error(f"Error connecting to MongoDB: {traceback.format_exc()}")
# #     db = None # Ensure db is None if connection fails, so app can handle it gracefully.


# # # --- Google Cloud Vision API Configuration ---
# # vision_client = None
# # try:
# #     if not os.path.exists(VISION_API_KEY_PATH_HARDCODED):
# #         logging.error(f"Vision API key file not found at: {VISION_API_KEY_PATH_HARDCODED}. Vision features will be disabled.")
# #     else:
# #         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH_HARDCODED)
# #         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
# #         logging.info("Google Cloud Vision API client initialized successfully.")
# # except Exception as e:
# #     logging.error(f"Error initializing Google Cloud Vision API client: {traceback.format_exc()}. Vision features will be disabled.")
# #     vision_client = None


# # # --- Google Gemini API Configuration ---
# # # Ensure API key is set before configuring Gemini
# # if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
# #     logging.error("GEMINI_API_KEY is not set or is still the placeholder! Gemini features will not work.")
# # genai.configure(api_key=GEMINI_API_KEY_HARDCODED)

# # # Initialize Gemini models. Using gemini-2.0-flash for multimodal capabilities (though OCR is done by Vision first).
# # gemini_pro_model = genai.GenerativeModel('gemini-2.0-flash')
# # logging.info("Google Gemini API client initialized.")


# # # --- UPLOAD FOLDER CONFIGURATION ---
# # # Define the upload folder relative to the current working directory
# # UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # # Create UPLOAD_FOLDER if it doesn't exist. exist_ok=True prevents error if it already exists.
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# # logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")
# # # --- END UPLOAD FOLDER CONFIGURATION ---

# # # --- ML Model Loading ---
# # # Load trained ML models for tax regime classification and tax liability regression
# # tax_regime_classifier_model = None
# # tax_regressor_model = None

# # try:
# #     # Ensure these .pkl files are generated by running model_trainer.py first.
# #     # Make sure xgboost is installed in your environment for model_trainer.py
# #     classifier_path = 'tax_regime_classifier_model.pkl'
# #     if os.path.exists(classifier_path):
# #         tax_regime_classifier_model = joblib.load(classifier_path)
# #         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
# #     else:
# #         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

# #     regressor_path = 'final_tax_regressor_model.pkl'
# #     if os.path.exists(regressor_path):
# #         tax_regressor_model = joblib.load(regressor_path)
# #         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
# #     else:
# #         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# # except Exception as e:
# #     logging.error(f"Error loading ML models: {traceback.format_exc()}")
# #     tax_regime_classifier_model = None
# #     tax_regressor_model = None


# # # --- Helper Functions ---

# # def convert_numpy_types(obj):
# #     """
# #     Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
# #     This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
# #     """
# #     if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
# #         return obj.item() # Converts numpy scalar to Python scalar
# #     elif isinstance(obj, dict):
# #         return {k: convert_numpy_types(v) for k, v in obj.items()}
# #     elif isinstance(obj, list):
# #         return [convert_numpy_types(elem) for elem in obj]
# #     else:
# #         return obj

# # def extract_text_with_vision_api(image_bytes):
# #     """
# #     Uses Google Cloud Vision API to perform OCR on image bytes and return the full text.
# #     Requires `vision_client` to be initialized.
# #     """
# #     if vision_client is None:
# #         logging.error("Google Cloud Vision client is not initialized. Cannot perform OCR.")
# #         raise RuntimeError("OCR service unavailable.")
# #     try:
# #         image = vision.Image(content=image_bytes)
# #         # Using document_text_detection for comprehensive text extraction from documents
# #         response = vision_client.document_text_detection(image=image)
# #         if response.full_text_annotation:
# #             logging.info("Successfully extracted text using Google Cloud Vision API.")
# #             return response.full_text_annotation.text
# #         else:
# #             logging.warning("Google Cloud Vision API returned no full text annotation.")
# #             return ""
# #     except Exception as e:
# #         logging.error(f"Error extracting text with Vision API: {traceback.format_exc()}")
# #         raise # Re-raise the exception to be handled by the calling function

# # def get_gemini_response(prompt_text, file_data=None, mime_type=None, filename="unknown_file"):
# #     """
# #     Sends a prompt to Gemini and returns the structured JSON response.
# #     If image/pdf data is provided, it first uses Vision API for OCR.
# #     The response is strictly expected in a JSON format based on the defined schema.
# #     """
# #     try:
# #         final_prompt_content = prompt_text
        
# #         if file_data and mime_type and ("image" in mime_type or "pdf" in mime_type):
# #             # If image or PDF, first extract text using Vision API
# #             extracted_text_from_vision = extract_text_with_vision_api(file_data)
# #             final_prompt_content += f"\n\n--- Document Content for Extraction ---\n{extracted_text_from_vision}"
# #             logging.info(f"Feeding Vision API extracted text to Gemini for '{filename}'.")
            
# #         else:
# #             # For pure text inputs, assume prompt_text already contains all necessary info
# #             logging.info(f"Processing text content directly with Gemini for '{filename}'.")
        
# #         # --- DEFINITIVE JSON SCHEMA FOR GEMINI OUTPUT ---
# #         # This schema MUST be comprehensive and match all keys expected by your frontend.
# #         # Gemini will attempt to adhere to this schema and fill in defaults.
# #         # Ensure all fields are explicitly defined to help Gemini produce consistent output.
# #         response_schema = {
# #             "type": "OBJECT",
# #             "properties": {
# #                 "identified_type": {"type": "STRING", "description": "Type of document, e.g., 'Form 16', 'Bank Statement', 'Form 26AS', 'Salary Slip', 'Investment Proof', 'Home Loan Statement', 'Other Document'. Choose the most relevant one if possible."},
# #                 "employer_name": {"type": "STRING", "description": "Name of the Employer"},
# #                 "employer_address": {"type": "STRING", "description": "Address of the Employer"},
# #                 "pan_of_deductor": {"type": "STRING", "description": "PAN of the Employer (Deductor)"},
# #                 "tan_of_deductor": {"type": "STRING", "description": "TAN of the Employer (Deductor)"},
# #                 "name_of_employee": {"type": "STRING", "description": "Name of the Employee/Assessee"},
# #                 "designation_of_employee": {"type": "STRING", "description": "Designation of the Employee"},
# #                 "pan_of_employee": {"type": "STRING", "description": "PAN of the Employee/Assessee"},
# #                 "date_of_birth": {"type": "STRING", "format": "date-time", "description": "Date of Birth (YYYY-MM-DD)"},
# #                 "gender": {"type": "STRING", "description": "Gender (e.g., 'Male', 'Female', 'Other')"},
# #                 "residential_status": {"type": "STRING", "description": "Residential Status (e.g., 'Resident', 'Non-Resident')"},
# #                 "assessment_year": {"type": "STRING", "description": "Income Tax Assessment Year (e.g., '2024-25')"},
# #                 "financial_year": {"type": "STRING", "description": "Financial Year (e.g., '2023-24')"},
# #                 "period_from": {"type": "STRING", "format": "date-time", "description": "Start date of the document period (YYYY-MM-DD)"},
# #                 "period_to": {"type": "STRING", "format": "date-time", "description": "End date of the document period (YYYY-MM-DD)"},
# #                 "quarter_1_receipt_number": {"type": "STRING"},
# #                 "quarter_1_tds_deducted": {"type": "NUMBER"},
# #                 "quarter_1_tds_deposited": {"type": "NUMBER"},
# #                 "total_tds_deducted_summary": {"type": "NUMBER", "description": "Total TDS deducted from salary (Form 16 Part A)"},
# #                 "total_tds_deposited_summary": {"type": "NUMBER", "description": "Total TDS deposited from salary (Form 16 Part A)"},
# #                 "salary_as_per_sec_17_1": {"type": "NUMBER", "description": "Salary as per Section 17(1)"},
# #                 "value_of_perquisites_u_s_17_2": {"type": "NUMBER", "description": "Value of perquisites u/s 17(2)"},
# #                 "profits_in_lieu_of_salary_u_s_17_3": {"type": "NUMBER", "description": "Profits in lieu of salary u/s 17(3)"},
# #                 "gross_salary_total": {"type": "NUMBER", "description": "Total Gross Salary (sum of 17(1), 17(2), 17(3) from Form 16, or derived from payslip total earnings)"},
# #                 "conveyance_allowance": {"type": "NUMBER"},
# #                 "transport_allowance": {"type": "NUMBER"},
# #                 "total_exempt_allowances": {"type": "NUMBER", "description": "Total allowances exempt u/s 10"},
# #                 "balances_1_2": {"type": "NUMBER", "description": "Balance after subtracting allowances from gross salary"},
# #                 "professional_tax": {"type": "NUMBER", "description": "Professional Tax"},
# #                 "aggregate_of_deductions_from_salary": {"type": "NUMBER", "description": "Total deductions from salary (e.g., Prof Tax, Standard Deduction)"},
# #                 "income_chargable_under_head_salaries": {"type": "NUMBER", "description": "Income chargeable under 'Salaries'"},
# #                 "income_from_house_property": {"type": "NUMBER", "description": "Income From House Property (can be negative for loss)"},
# #                 "income_from_other_sources": {"type": "NUMBER", "description": "Income From Other Sources (e.g., interest, dividend)"},
# #                 "interest_on_housing_loan_self_occupied": {"type": "NUMBER", "description": "Interest on Housing Loan - Self Occupied Property"},
# #                 "capital_gains_long_term": {"type": "NUMBER", "description": "Long Term Capital Gains"},
# #                 "capital_gains_short_term": {"type": "NUMBER", "description": "Short Term Capital Gains"},
# #                 "gross_total_income_as_per_document": {"type": "NUMBER", "description": "Gross total income as stated in the document"},
# #                 "deduction_80c": {"type": "NUMBER", "description": "Total deduction under Section 80C (includes EPF, PPF, LIC, etc.)"},
# #                 "deduction_80c_epf": {"type": "NUMBER", "description": "EPF contribution under 80C"},
# #                 "deduction_80c_insurance_premium": {"type": "NUMBER", "description": "Life Insurance Premium under 80C"},
# #                 "deduction_80ccc": {"type": "NUMBER", "description": "Deduction for contribution to certain pension funds under Section 80CCC"},
# #                 "deduction_80ccd": {"type": "NUMBER", "description": "Deduction for contribution to NPS under Section 80CCD"},
# #                 "deduction_80ccd1b": {"type": "NUMBER", "description": "Additional deduction under Section 80CCD(1B) for NPS"},
# #                 "deduction_80d": {"type": "NUMBER", "description": "Deduction for Health Insurance Premium under Section 80D"},
# #                 "deduction_80g": {"type": "NUMBER", "description": "Deduction for Donations under Section 80G"},
# #                 "deduction_80tta": {"type": "NUMBER", "description": "Deduction for Interest on Savings Account under Section 80TTA"},
# #                 "deduction_80ttb": {"type": "NUMBER", "description": "Deduction for Interest for Senior Citizens under Section 80TTB"},
# #                 "deduction_80e": {"type": "NUMBER", "description": "Deduction for Interest on Education Loan under Section 80E"},
# #                 "total_deductions_chapter_via": {"type": "NUMBER", "description": "Total of all deductions under Chapter VI-A"},
# #                 "taxable_income_as_per_document": {"type": "NUMBER", "description": "Taxable Income as stated in the document"},
# #                 "tax_payable_as_per_document": {"type": "NUMBER", "description": "Final tax payable as stated in the document"},
# #                 "refund_status_as_per_document": {"type": "STRING", "description": "Refund status as stated in the document (e.g., 'Refund due', 'Tax payable', 'No demand no refund')"},
# #                 "tax_regime_chosen": {"type": "STRING", "description": "Tax Regime Chosen (e.g., 'Old Regime' or 'New Regime' if explicitly indicated in document)"},
# #                 "total_tds": {"type": "NUMBER", "description": "Total TDS credit from all sources (e.g., Form 26AS, Form 16 Part A)"},
# #                 "advance_tax": {"type": "NUMBER", "description": "Advance Tax paid"},
# #                 "self_assessment_tax": {"type": "NUMBER", "description": "Self-Assessment Tax paid"},
                
# #                 # --- NEW PAYSLIP SPECIFIC FIELDS ---
# #                 "basic_salary": {"type": "NUMBER", "description": "Basic Salary component from payslip"},
# #                 "hra_received": {"type": "NUMBER", "description": "House Rent Allowance (HRA) received from payslip"},
# #                 "epf_contribution": {"type": "NUMBER", "description": "Employee Provident Fund (EPF) contribution from payslip"},
# #                 "esi_contribution": {"type": "NUMBER", "description": "Employee State Insurance (ESI) contribution from payslip"},
# #                 "net_amount_payable": {"type": "NUMBER", "description": "Net amount payable (take home pay) from payslip"},
# #                 "overtime_pay": {"type": "NUMBER", "description": "Overtime pay from payslip"},
# #                 "overtime_hours": {"type": "STRING", "description": "Overtime hours from payslip (e.g., '100-0 Hrs')"},
# #                 "days_present": {"type": "STRING", "description": "Days present from payslip (e.g., '250 Days')"},

# #                 # Additional fields for Bank Statements (if applicable)
# #                 "account_holder_name": {"type": "STRING", "description": "Name of the account holder"},
# #                 "account_number": {"type": "STRING", "description": "Bank account number"},
# #                 "ifsc_code": {"type": "STRING", "description": "IFSC code of the bank branch"},
# #                 "bank_name": {"type": "STRING", "description": "Name of the bank"},
# #                 "branch_address": {"type": "STRING", "description": "Address of the bank branch"},
# #                 "statement_start_date": {"type": "STRING", "format": "date-time", "description": "Start date of the bank statement period (YYYY-MM-DD)"},
# #                 "statement_end_date": {"type": "STRING", "format": "date-time", "description": "End date of the bank statement period (YYYY-MM-DD)"},
# #                 "opening_balance": {"type": "NUMBER", "description": "Opening balance on the statement"},
# #                 "closing_balance": {"type": "NUMBER", "description": "Closing balance on the statement"},
# #                 "total_deposits": {"type": "NUMBER", "description": "Total deposits during the statement period"},
# #                 "total_withdrawals": {"type": "NUMBER", "description": "Total withdrawals during the statement period"},
# #                 "transaction_summary": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"date": {"type": "STRING", "format": "date-time", "description": "Date of the transaction (YYYY-MM-DD)"}, "description": {"type": "STRING"}, "amount": {"type": "NUMBER"}}}, "description": "A summary or key entries of transactions from the statement (e.g., large deposits/withdrawals)."}
# #             },
# #             "required": ["identified_type"] # Minimum required field from Gemini's side
# #         }

# #         generation_config = {
# #             "response_mime_type": "application/json",
# #             "response_schema": response_schema
# #         }
        
# #         # Call Gemini model with the prompt and schema
# #         response = genai.GenerativeModel('gemini-2.0-flash').generate_content([{"text": final_prompt_content}], generation_config=generation_config)

# #         if not response.text:
# #             logging.warning(f"Gemini returned an empty response text for {filename}.")
# #             # Return an error with an empty dictionary for extracted_data to prevent KeyError
# #             return json.dumps({"error": "Empty response from AI.", "extracted_data": {}})

# #         # Clean the response text from markdown fences (```json ... ```) if present
# #         response_text_cleaned = response.text.strip()
# #         if response_text_cleaned.startswith("```json") and response_text_cleaned.endswith("```"):
# #             response_text_cleaned = response_text_cleaned[len("```json"):].rstrip("```").strip()
# #             logging.info("Stripped markdown JSON fences from Gemini response.")

# #         try:
# #             # Parse the cleaned JSON response from Gemini
# #             parsed_json = json.loads(response_text_cleaned)
            
# #             # --- CRITICAL FIX: Ensure all keys from schema are present and correctly typed ---
# #             extracted_data = parsed_json # Gemini should return directly according to schema
# #             final_extracted_data = {}

# #             for key, prop_details in response_schema['properties'].items():
# #                 if key in extracted_data and extracted_data[key] is not None:
# #                     # Safely convert to the expected type
# #                     if prop_details['type'] == 'NUMBER':
# #                         final_extracted_data[key] = safe_float(extracted_data[key])
# #                     elif prop_details['type'] == 'STRING':
# #                         # Special handling for date formats if needed, otherwise just safe_string
# #                         if 'format' in prop_details and prop_details['format'] == 'date-time':
# #                             # Attempt to parse date, default if unable
# #                             try:
# #                                 dt_obj = datetime.strptime(str(extracted_data[key]).split('T')[0], '%Y-%m-%d')
# #                                 final_extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
# #                             except ValueError:
# #                                 final_extracted_data[key] = "0000-01-01" # Default invalid date string
# #                         else:
# #                             final_extracted_data[key] = safe_string(extracted_data[key])
# #                     elif prop_details['type'] == 'ARRAY':
# #                         if key == "transaction_summary" and isinstance(extracted_data[key], list):
# #                             # Process each transaction summary item
# #                             processed_transactions = []
# #                             for item in extracted_data[key]:
# #                                 processed_item = {
# #                                     "date": "0000-01-01", # Default date for transaction
# #                                     "description": safe_string(item.get("description")),
# #                                     "amount": safe_float(item.get("amount"))
# #                                 }
# #                                 if 'date' in item and item['date'] is not None:
# #                                     try:
# #                                         # Assuming transaction date might be YYYY-MM-DD or similar
# #                                         dt_obj = datetime.strptime(str(item['date']).split('T')[0], '%Y-%m-%d')
# #                                         processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
# #                                     except ValueError:
# #                                         pass # Keep default if parsing fails
# #                                 processed_transactions.append(processed_item)
# #                             final_extracted_data[key] = processed_transactions
# #                         else:
# #                             final_extracted_data[key] = extracted_data[key] if isinstance(extracted_data[key], list) else []
# #                     else: # Fallback for other types
# #                         final_extracted_data[key] = extracted_data[key]
# #                 else:
# #                     # Set default based on schema's type
# #                     if prop_details['type'] == 'NUMBER':
# #                         final_extracted_data[key] = 0.0
# #                     elif prop_details['type'] == 'STRING':
# #                         if 'format' in prop_details and prop_details['format'] == 'date-time':
# #                             final_extracted_data[key] = "0000-01-01" # Default date string
# #                         else:
# #                             final_extracted_data[key] = "null" # Use string "null" as per schema description
# #                     elif prop_details['type'] == 'ARRAY':
# #                         final_extracted_data[key] = []
# #                     else:
# #                         final_extracted_data[key] = None # Generic default if type is not recognized

# #             logging.info(f"Successfully retrieved and validated structured info from Gemini for {filename}.")
# #             return json.dumps({"error": None, "extracted_data": final_extracted_data})
# #         except json.JSONDecodeError:
# #             logging.error(f"Gemini response was not valid JSON for {filename}. Raw response: {response_text_cleaned[:500]}...")
# #             return json.dumps({"error": "Invalid JSON format from AI", "extracted_data": {"raw_text_response": response_text_cleaned}})
# #         except Exception as e:
# #             logging.error(f"Error processing Gemini's parsed JSON for {filename}: {traceback.format_exc()}")
# #             return json.dumps({"error": f"Error processing AI data: {str(e)}", "extracted_data": {}})

# #     except Exception as e:
# #         logging.error(f"Overall error in get_gemini_response for {filename}: {traceback.format_exc()}")
# #         return json.dumps({"error": str(e), "extracted_data": {}})

# # def safe_float(val):
# #     """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
# #     Handles commas and currency symbols."""
# #     try:
# #         if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
# #             return 0.0
# #         if isinstance(val, str):
# #             # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
# #             # This handles values like "₹7,20,000.00", "720,000.00", "720000"
# #             val = val.replace(',', '').replace('₹', '').strip()
            
# #         return float(val)
# #     except (ValueError, TypeError):
# #         logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
# #         return 0.0

# # def safe_string(val):
# #     """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
# #     if val is None:
# #         return "null"
# #     s_val = str(val).strip()
# #     if s_val == "":
# #         return "null"
# #     return s_val

# # def _aggregate_financial_data(extracted_data_list):
# #     """
# #     Aggregates financial data from multiple extracted documents, applying reconciliation rules.
# #     Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
# #     """
    
# #     aggregated_data = {
# #         # Initialize all fields that are expected in the final aggregated output
# #         "identified_type": "Other Document", # Overall identified type if mixed documents
# #         "employer_name": "null", "employer_address": "null",
# #         "pan_of_deductor": "null", "tan_of_deductor": "null",
# #         "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
# #         "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
# #         "assessment_year": "null", "financial_year": "null",
# #         "period_from": "0000-01-01", "period_to": "0000-01-01",
        
# #         # Income Components - These should be summed
# #         "basic_salary": 0.0,
# #         "hra_received": 0.0,
# #         "conveyance_allowance": 0.0,
# #         "transport_allowance": 0.0,
# #         "overtime_pay": 0.0,
# #         "salary_as_per_sec_17_1": 0.0,
# #         "value_of_perquisites_u_s_17_2": 0.0,
# #         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
# #         "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

# #         "income_from_house_property": 0.0,
# #         "income_from_other_sources": 0.0,
# #         "capital_gains_long_term": 0.0,
# #         "capital_gains_short_term": 0.0,

# #         # Deductions - These should be summed, capped later if needed
# #         "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
# #         "professional_tax": 0.0,
# #         "interest_on_housing_loan_self_occupied": 0.0,
# #         "deduction_80c": 0.0,
# #         "deduction_80c_epf": 0.0,
# #         "deduction_80c_insurance_premium": 0.0,
# #         "deduction_80ccc": 0.0,
# #         "deduction_80ccd": 0.0,
# #         "deduction_80ccd1b": 0.0,
# #         "deduction_80d": 0.0,
# #         "deduction_80g": 0.0,
# #         "deduction_80tta": 0.0,
# #         "deduction_80ttb": 0.0,
# #         "deduction_80e": 0.0,
# #         "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
# #         "epf_contribution": 0.0, # Initialize epf_contribution
# #         "esi_contribution": 0.0, # Initialize esi_contribution


# #         # Tax Paid
# #         "total_tds": 0.0,
# #         "advance_tax": 0.0,
# #         "self_assessment_tax": 0.0,
# #         "total_tds_deducted_summary": 0.0, # From Form 16 Part A

# #         # Document Specific (Non-summable, usually taken from most authoritative source)
# #         "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

# #         # Bank Account Details (Take from the most complete or latest if multiple)
# #         "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
# #         "bank_name": "null", "branch_address": "null",
# #         "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
# #         "opening_balance": 0.0, "closing_balance": 0.0,
# #         "total_deposits": 0.0, "total_withdrawals": 0.0,
# #         "transaction_summary": [], # Aggregate all transactions

# #         # Other fields from the schema, ensuring they exist
# #         "net_amount_payable": 0.0,
# #         "days_present": "null",
# #         "overtime_hours": "null",

# #         # Calculated fields for frontend
# #         "Age": "N/A", 
# #         "total_gross_income": 0.0, # Overall sum of all income heads
# #         "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
# #         "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
# #         "deduction_80C": 0.0, # Alias for deduction_80c
# #         "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
# #         "deduction_80D": 0.0, # Alias for deduction_80d
# #         "deduction_80G": 0.0, # Alias for deduction_80g
# #         "deduction_80TTA": 0.0, # Alias for deduction_80tta
# #         "deduction_80TTB": 0.0, # Alias for deduction_80ttb
# #         "deduction_80E": 0.0, # Alias for deduction_80e
# #         "total_deductions": 0.0, # Overall total deductions used in calculation
# #     }

# #     # Define document priority for overriding fields (higher value means higher priority)
# #     # Form 16 should provide definitive income/deduction figures.
# #     doc_priority = {
# #         "Form 16": 5,
# #         "Form 26AS": 4,
# #         "Salary Slip": 3,
# #         "Investment Proof": 2,
# #         "Home Loan Statement": 2,
# #         "Bank Statement": 1,
# #         "Other Document": 0,
# #         "Unknown": 0,
# #         "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
# #     }

# #     # Sort documents by priority (higher priority first)
# #     sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

# #     # Use a dictionary to track which field was last set by which document priority
# #     # This helps in overriding with higher-priority document data.
# #     field_source_priority = {key: -1 for key in aggregated_data}

# #     # Iterate through sorted documents and aggregate data
# #     for data in sorted_extracted_data:
# #         doc_type = safe_string(data.get('identified_type'))
# #         current_priority = doc_priority.get(doc_type, 0)
# #         logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

# #         # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
# #         # Otherwise, individual components will be summed later.
# #         extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
# #         if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
# #             aggregated_data["gross_salary_total"] = extracted_gross_salary_total
# #             field_source_priority["gross_salary_total"] = current_priority
# #             logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

# #         # Update core personal details only from highest priority document or if current is 'null'
# #         personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
# #         for p_field in personal_fields:
# #             if safe_string(data.get(p_field)) != "null" and \
# #                (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
# #                 aggregated_data[p_field] = safe_string(data.get(p_field))
# #                 field_source_priority[p_field] = current_priority


# #         for key, value in data.items():
# #             # Skip keys already handled explicitly or which have specific aggregation logic
# #             if key in personal_fields or key == "gross_salary_total":
# #                 continue 
# #             if key == "transaction_summary":
# #                 if isinstance(value, list):
# #                     aggregated_data[key].extend(value)
# #                 continue
# #             if key == "identified_type":
# #                 # Ensure highest priority identified_type is kept
# #                 if current_priority > field_source_priority.get(key, -1):
# #                     aggregated_data[key] = safe_string(value)
# #                     field_source_priority[key] = current_priority
# #                 continue
            
# #             # General handling for numerical fields: sum them up
# #             if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
# #                 # Special handling for bank balances: take from latest/highest priority statement
# #                 if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
# #                     if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
# #                         # Only update if the current document is a bank statement and has higher or equal priority
# #                         # (or if the existing aggregated value is 0)
# #                         if current_priority >= field_source_priority.get(key, -1):
# #                             aggregated_data[key] = safe_float(value)
# #                             field_source_priority[key] = current_priority
# #                     else: # For other document types, just sum the numbers if they appear
# #                         aggregated_data[key] += safe_float(value)
# #                 else:
# #                     aggregated_data[key] += safe_float(value)
# #             # General handling for string fields: take from highest priority document
# #             elif key in aggregated_data and isinstance(aggregated_data[key], str):
# #                 if safe_string(value) != "null" and safe_string(value) != "" and \
# #                    (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
# #                     aggregated_data[key] = safe_string(value)
# #                     field_source_priority[key] = current_priority
# #             # Default for other types if they are not explicitly handled
# #             elif key in aggregated_data and value is not None:
# #                 if current_priority > field_source_priority.get(key, -1):
# #                     aggregated_data[key] = value
# #                     field_source_priority[key] = current_priority

# #     # --- Post-aggregation calculations and reconciliation ---
    
# #     # Calculate `total_gross_income` (overall income from all heads)
# #     # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
# #     # try to derive it from payslip components like basic, HRA, etc.
# #     if aggregated_data["gross_salary_total"] == 0.0:
# #         aggregated_data["gross_salary_total"] = (
# #             safe_float(aggregated_data["basic_salary"]) +
# #             safe_float(aggregated_data["hra_received"]) +
# #             safe_float(aggregated_data["conveyance_allowance"]) +
# #             safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
# #             safe_float(aggregated_data["overtime_pay"]) +
# #             safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
# #             safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
# #         )
# #         # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
# #         # Assuming extracted values are already annual or normalized.

# #     # Now calculate the comprehensive total_gross_income for tax computation
# #     aggregated_data["total_gross_income"] = (
# #         safe_float(aggregated_data["gross_salary_total"]) +
# #         safe_float(aggregated_data["income_from_house_property"]) +
# #         safe_float(aggregated_data["income_from_other_sources"]) + 
# #         safe_float(aggregated_data["capital_gains_long_term"]) +
# #         safe_float(aggregated_data["capital_gains_short_term"])
# #     )
# #     aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

# #     # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
# #     # This prevents double counting if EPF is reported separately and also included in 80C
# #     # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
# #     # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
# #     # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
# #     if safe_float(aggregated_data["epf_contribution"]) > 0:
# #         aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
# #     # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
# #     aggregated_data["total_deductions_chapter_via"] = (
# #         safe_float(aggregated_data["deduction_80c"]) +
# #         safe_float(aggregated_data["deduction_80ccc"]) +
# #         safe_float(aggregated_data["deduction_80ccd"]) +
# #         safe_float(aggregated_data["deduction_80ccd1b"]) +
# #         safe_float(aggregated_data["deduction_80d"]) +
# #         safe_float(aggregated_data["deduction_80g"]) +
# #         safe_float(aggregated_data["deduction_80tta"]) +
# #         safe_float(aggregated_data["deduction_80ttb"]) +
# #         safe_float(aggregated_data["deduction_80e"])
# #     )
# #     aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


# #     # Aliases for frontend (ensure these are correctly populated from derived values)
# #     aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
# #     # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
# #     # This is a fallback and might not always reflect actual exemptions as per tax rules.
# #     if aggregated_data["total_exempt_allowances"] == 0.0:
# #         aggregated_data["total_exempt_allowances"] = (
# #             safe_float(aggregated_data.get("conveyance_allowance")) +
# #             safe_float(aggregated_data.get("transport_allowance")) +
# #             safe_float(aggregated_data.get("hra_received")) 
# #         )
# #         logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

# #     # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
# #     # This is a fixed amount applied during tax calculation, not a sum from documents.
# #     aggregated_data["standard_deduction"] = 50000.0 

# #     # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
# #     dob_str = safe_string(aggregated_data.get("date_of_birth"))
# #     if dob_str != "null" and dob_str != "0000-01-01":
# #         try:
# #             dob = datetime.strptime(dob_str, '%Y-%m-%d')
# #             today = datetime.now()
# #             age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
# #             aggregated_data["Age"] = age
# #         except ValueError:
# #             logging.warning(f"Could not parse date_of_birth: {dob_str}")
# #             aggregated_data["Age"] = "N/A"
# #     else:
# #         aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

# #     # Populate aliases for frontend display consistency
# #     aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
# #     aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
# #     aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
# #     aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
# #     aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
# #     aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
# #     aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
# #     aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
# #     aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

# #     # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
# #     # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
# #     # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
# #     # For display, we can show sum of what's *claimed* or *extracted*.
# #     # Let's make `total_deductions` a sum of all potential deductions for display.
# #     aggregated_data["total_deductions"] = (
# #         aggregated_data["standard_deduction"] + 
# #         aggregated_data["professional_tax"] +
# #         aggregated_data["interest_on_housing_loan_self_occupied"] +
# #         aggregated_data["total_deductions_chapter_via"]
# #     )
# #     aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


# #     # Sort all_transactions by date (oldest first)
# #     for tx in aggregated_data['transaction_summary']:
# #         if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
# #             try:
# #                 tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
# #             except ValueError:
# #                 tx['date_sortable'] = datetime.min # Fallback for unparseable dates
# #         else:
# #             tx['date_sortable'] = datetime.min

# #     aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
# #     # Remove the temporary sortable key
# #     for tx in aggregated_data['transaction_summary']:
# #         tx.pop('date_sortable', None)

# #     # If identified_type is still "null" or "Unknown" and some other fields populated,
# #     # try to infer a better type if possible, or leave as "Other Document"
# #     if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
# #         if safe_string(aggregated_data.get('employer_name')) != "null" and \
# #            safe_float(aggregated_data.get('gross_salary_total')) > 0:
# #            aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
# #         elif safe_string(aggregated_data.get('account_number')) != "null" and \
# #              (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
# #              aggregated_data["identified_type"] = "Bank Statement"
# #         elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
# #              safe_float(aggregated_data.get('hra_received')) > 0 or \
# #              safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
# #              aggregated_data["identified_type"] = "Salary Slip"

# #     # Ensure PAN and Financial Year are properly set for database grouping
# #     # If not extracted, try to get from previous records or default to "null"
# #     if safe_string(aggregated_data.get("pan_of_employee")) == "null":
# #         aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

# #     # Derive financial year from assessment year if financial_year is null
# #     if safe_string(aggregated_data.get("financial_year")) == "null" and safe_string(aggregated_data.get("assessment_year")) != "null":
# #         try:
# #             ay_parts = aggregated_data["assessment_year"].split('-')
# #             if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
# #                 start_year = int(ay_parts[0]) -1
# #                 end_year = int(ay_parts[0])
# #                 aggregated_data["financial_year"] = f"{start_year}-{str(end_year)[-2:]}"
# #         except Exception:
# #             logging.warning(f"Could not derive financial year from assessment year: {aggregated_data.get('assessment_year')}")
# #             aggregated_data["financial_year"] = "UNKNOWNFY"
# #     elif safe_string(aggregated_data.get("financial_year")) == "null":
# #         aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
# #     logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
# #     return aggregated_data

# # def calculate_final_tax_summary(aggregated_data):
# #     """
# #     Calculates the estimated tax payable and refund status based on aggregated financial data.
# #     This function implements a SIMPLIFIED Indian income tax calculation for demonstration.
# #     !!! IMPORTANT: This must be replaced with actual, up-to-date, and comprehensive
# #     Indian income tax laws, considering both Old and New regimes, age groups,
# #     surcharges, cess, etc., for a production system. !!!

# #     Args:
# #         aggregated_data (dict): A dictionary containing aggregated financial fields.

# #     Returns:
# #         dict: A dictionary with computed tax liability, refund/due status, and notes.
# #     """
    
# #     # Safely extract and convert relevant values from aggregated_data
# #     gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
# #     # Deductions used for tax calculation (subject to limits and regime)
# #     total_chapter_via_deductions = safe_float(aggregated_data.get("total_deductions_chapter_via", 0)) 
# #     professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
# #     standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 0)) # Ensure standard deduction is fetched
# #     interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))

# #     # Sum all TDS and advance tax for comparison
# #     total_tds_credit = (
# #         safe_float(aggregated_data.get("total_tds", 0)) + 
# #         safe_float(aggregated_data.get("advance_tax", 0)) + 
# #         safe_float(aggregated_data.get("self_assessment_tax", 0))
# #     )

# #     tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
# #     age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
# #     if age == "N/A":
# #         age_group = "General"
# #     elif age < 60:
# #         age_group = "General"
# #     elif age >= 60 and age < 80:
# #         age_group = "Senior Citizen"
# #     else: # age >= 80
# #         age_group = "Super Senior Citizen"

# #     # --- Calculation Details List (for frontend display) ---
# #     calculation_details = []

# #     # --- Check for insufficient data for tax computation ---
# #     if gross_total_income < 100.0 and total_chapter_via_deductions < 100.0 and total_tds_credit < 100.0:
# #         calculation_details.append("Insufficient data provided for comprehensive tax calculation. Please upload documents with income and deduction details.")
# #         return {
# #             "calculated_gross_income": gross_total_income,
# #             "calculated_total_deductions": 0.0, # No significant deductions processed yet
# #             "computed_taxable_income": 0.0,
# #             "estimated_tax_payable": 0.0,
# #             "total_tds_credit": total_tds_credit,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "predicted_tax_regime": "N/A",
# #             "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
# #             "old_regime_tax_payable": 0.0,
# #             "new_regime_tax_payable": 0.0,
# #             "calculation_details": calculation_details,
# #         }

# #     calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

# #     # --- Old Tax Regime Calculation ---
# #     # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
# #     # Chapter VI-A deductions are capped at their respective limits or overall 1.5L for 80C, etc.
# #     # For simplicity, we'll use the extracted `total_deductions_chapter_via` but it should ideally be capped.
# #     # The actual tax deduction limits should be applied here.
    
# #     # Cap 80C related deductions at 1.5 Lakhs
# #     deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
# #     # Cap 80D (Health Insurance) - simplified max 25k for general, 50k for senior parent (adjust as per actual rules)
# #     deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0) 
# #     # Cap Housing Loan Interest for self-occupied at 2 Lakhs
# #     interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

# #     # Simplified Chapter VI-A deductions for old regime (summing specific 80C, 80D, 80CCD1B, 80E, 80G, 80TTA, 80TTB)
# #     total_chapter_via_deductions_old_regime = (
# #         deduction_80c_actual +
# #         safe_float(aggregated_data.get("deduction_80ccc", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ccd", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ccd1b", 0)) +
# #         safe_float(aggregated_data.get("deduction_80d", 0)) + # Corrected to use deduction_80d_actual later if needed
# #         safe_float(aggregated_data.get("deduction_80g", 0)) +
# #         safe_float(aggregated_data.get("deduction_80tta", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ttb", 0)) +
# #         safe_float(aggregated_data.get("deduction_80e", 0))
# #     )
# #     total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)


# #     # Total deductions for Old Regime
# #     total_deductions_old_regime_for_calc = (
# #         standard_deduction_applied + 
# #         professional_tax + 
# #         interest_on_housing_loan_actual + 
# #         total_chapter_via_deductions_old_regime
# #     )
# #     total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

# #     taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
# #     tax_before_cess_old_regime = 0

# #     calculation_details.append(f"2. Deductions under Old Regime:")
# #     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
# #     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
# #     calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
# #     calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
# #     calculation_details.append(f"   - Section 80D (capped at ₹25,000/₹50,000): ₹{deduction_80d_actual:,.2f}")
# #     calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual):,.2f}")
# #     calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
# #     calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

# #     # Old Regime Tax Slabs (simplified for AY 2024-25)
# #     if age_group == "General":
# #         if taxable_income_old_regime <= 250000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
# #     elif age_group == "Senior Citizen": # 60 to < 80
# #         if taxable_income_old_regime <= 300000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 300000) * 0.05
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
# #     else: # Super Senior Citizen >= 80
# #         if taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

# #     rebate_87a_old_regime = 0
# #     if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
# #         rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
# #     tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
# #     total_tax_old_regime = round(tax_after_rebate_old_regime * 1.04, 2) # Add 4% Health and Education Cess
# #     calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
# #     calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
# #     calculation_details.append(f"6. Tax after Rebate (Old Regime): ₹{tax_after_rebate_old_regime:,.2f}")
# #     calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


# #     # --- New Tax Regime Calculation ---
# #     # From AY 2024-25, standard deduction is also applicable in the New Regime for salaried individuals.
# #     # Most Chapter VI-A deductions are *not* allowed in the New Regime, except employer's NPS contribution u/s 80CCD(2).
# #     # For simplicity, we assume only standard deduction and professional tax are applicable.
# #     # Also, housing loan interest deduction is NOT allowed for self-occupied property in New Regime.

# #     taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
# #     # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
# #     tax_before_cess_new_regime = 0

# #     calculation_details.append(f"8. Deductions under New Regime:")
# #     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
# #     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
# #     calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") # Only allowed ones
# #     calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


# #     # New Regime Tax Slabs (simplified for AY 2024-25 onwards)
# #     if taxable_income_new_regime <= 300000:
# #         tax_before_cess_new_regime = 0
# #     elif taxable_income_new_regime <= 600000:
# #         tax_before_cess_new_regime = (taxable_income_new_regime - 300000) * 0.05
# #     elif taxable_income_new_regime <= 900000:
# #         tax_before_cess_new_regime = 15000 + (taxable_income_new_regime - 600000) * 0.10
# #     elif taxable_income_new_regime <= 1200000:
# #         tax_before_cess_new_regime = 45000 + (taxable_income_new_regime - 900000) * 0.15
# #     elif taxable_income_new_regime <= 1500000:
# #         tax_before_cess_new_regime = 90000 + (taxable_income_new_regime - 1200000) * 0.20
# #     else:
# #         tax_before_cess_new_regime = 150000 + (taxable_income_new_regime - 1500000) * 0.30

# #     rebate_87a_new_regime = 0
# #     if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs
# #         rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
# #     tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
# #     total_tax_new_regime = round(tax_after_rebate_new_regime * 1.04, 2) # Add 4% Health and Education Cess

# #     calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
# #     calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
# #     calculation_details.append(f"12. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


# #     # --- Determine Optimal Regime and Final Summary ---
# #     final_tax_regime_applied = "N/A"
# #     estimated_tax_payable = 0.0
# #     computed_taxable_income = 0.0
# #     computation_notes = []

# #     # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
# #     if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
# #         estimated_tax_payable = total_tax_new_regime
# #         computed_taxable_income = taxable_income_new_regime
# #         final_tax_regime_applied = "New Regime (Chosen by User from Document)"
# #         computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
# #     elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
# #         estimated_tax_payable = total_tax_old_regime
# #         computed_taxable_income = taxable_income_old_regime
# #         final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
# #         computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
# #     else: # If no regime is explicitly chosen in documents, recommend the optimal one
# #         if total_tax_old_regime <= total_tax_new_regime:
# #             estimated_tax_payable = total_tax_old_regime
# #             computed_taxable_income = taxable_income_old_regime
# #             final_tax_regime_applied = "Old Regime (Optimal)"
# #             computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
# #         else:
# #             estimated_tax_payable = total_tax_new_regime
# #             computed_taxable_income = taxable_income_new_regime
# #             final_tax_regime_applied = "New Regime (Optimal)"
# #             computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

# #     estimated_tax_payable = round(estimated_tax_payable, 2)
# #     computed_taxable_income = round(computed_taxable_income, 2)

# #     # --- Calculate Refund/Tax Due ---
# #     refund_due_from_tax = 0.0
# #     tax_due_to_government = 0.0

# #     calculation_details.append(f"13. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
# #     if total_tds_credit > estimated_tax_payable:
# #         refund_due_from_tax = total_tds_credit - estimated_tax_payable
# #         calculation_details.append(f"14. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
# #     elif total_tds_credit < estimated_tax_payable:
# #         tax_due_to_government = estimated_tax_payable - total_tds_credit
# #         calculation_details.append(f"14. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
# #     else:
# #         calculation_details.append("14. No Refund or Additional Tax Due.")


# #     return {
# #         "calculated_gross_income": gross_total_income,
# #         "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
# #         "computed_taxable_income": computed_taxable_income,
# #         "estimated_tax_payable": estimated_tax_payable,
# #         "total_tds_credit": total_tds_credit,
# #         "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
# #         "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
# #         "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
# #         "notes": computation_notes, # List of notes
# #         "old_regime_tax_payable": total_tax_old_regime,
# #         "new_regime_tax_payable": total_tax_new_regime,
# #         "calculation_details": calculation_details,
# #     }

# # def generate_ml_prediction_summary(financial_data):
# #     """
# #     Generates ML model prediction summary using the loaded models.
# #     """
# #     if tax_regime_classifier_model is None or tax_regressor_model is None:
# #         logging.warning("ML models are not loaded. Cannot generate ML predictions.")
# #         return {
# #             "predicted_tax_regime": "N/A",
# #             "predicted_tax_liability": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "notes": "ML prediction service unavailable (models not loaded or training failed)."
# #         }

# #     # Define the features expected by the ML models (must match model_trainer.py)
# #     # IMPORTANT: These must precisely match the features used in model_trainer.py
# #     # Re-verify against your `model_trainer.py` to ensure exact match.
# #     ml_common_numerical_features = [
# #         'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
# #         'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
# #         'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
# #         'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
# #         'Total Exempt Allowances Claimed'
# #     ]
# #     ml_categorical_features = ['Residential Status', 'Gender']
    
# #     # Prepare input for classifier model
# #     age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
# #     # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
# #     # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
# #     # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
# #     calculated_other_deductions = (
# #         safe_float(financial_data.get('deduction_80ccc', 0)) +
# #         safe_float(financial_data.get('deduction_80ccd', 0)) +
# #         safe_float(financial_data.get('deduction_80ccd1b', 0)) +
# #         safe_float(financial_data.get('deduction_80g', 0)) +
# #         safe_float(financial_data.get('deduction_80tta', 0)) +
# #         safe_float(financial_data.get('deduction_80ttb', 0))
# #     )
# #     calculated_other_deductions = round(calculated_other_deductions, 2)


# #     classifier_input_data = {
# #         'Age': age_value,
# #         'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
# #         'HRA Received': safe_float(financial_data.get('hra_received', 0)),
# #         'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
# #         'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
# #         'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
# #         'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
# #         'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
# #         'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
# #         'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
# #         'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
# #         'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
# #         'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
# #         'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
# #         'Gender': safe_string(financial_data.get('gender', 'Unknown'))
# #     }
    
# #     # Create DataFrame for classifier prediction, ensuring column order
# #     # The order must match `model_trainer.py`'s `classifier_all_features`
# #     ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
# #     classifier_df = pd.DataFrame([classifier_input_data])
    
# #     predicted_tax_regime = "N/A"
# #     try:
# #         classifier_df_processed = classifier_df[ordered_classifier_features]
# #         predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
# #         logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
# #     except Exception as e:
# #         logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
# #         predicted_tax_regime = "Prediction Failed (Error)"
        
# #     # Prepare input for regressor model
# #     # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
# #     regressor_input_data = {
# #         k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
# #     }
# #     regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

# #     regressor_df = pd.DataFrame([regressor_input_data])
    
# #     predicted_tax_liability = 0.0
# #     try:
# #         # The regressor's preprocessor will handle the categorical feature conversion.
# #         # Just ensure the input DataFrame has the correct columns and order.
# #         ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
# #         regressor_df_processed = regressor_df[ordered_regressor_features]
# #         predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
# #         logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
# #     except Exception as e:
# #         logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
# #         predicted_tax_liability = 0.0 # Default to 0 if prediction fails

# #     # Calculate refund/additional due based on ML prediction and actual TDS
# #     total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

# #     predicted_refund_due = 0.0
# #     predicted_additional_due = 0.0

# #     if total_tds_credit > predicted_tax_liability:
# #         predicted_refund_due = total_tds_credit - predicted_tax_liability
# #     elif total_tds_credit < predicted_tax_liability:
# #         predicted_additional_due = predicted_tax_liability - total_tds_credit
        
# #     # Convert any numpy types before returning
# #     return convert_numpy_types({
# #         "predicted_tax_regime": predicted_tax_regime,
# #         "predicted_tax_liability": predicted_tax_liability,
# #         "predicted_refund_due": round(predicted_refund_due, 2),
# #         "predicted_additional_due": round(predicted_additional_due, 2),
# #         "notes": "ML model predictions for optimal regime and tax liability."
# #     })

# # def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
# #     """Generates tax-saving suggestions and regime analysis using Gemini API."""
# #     if gemini_pro_model is None:
# #         logging.error("Gemini API (gemini_pro_model) not initialized.")
# #         return ["AI suggestions unavailable."], "AI regime analysis unavailable."

# #     # Check if tax computation was not possible
# #     if "Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]:
# #         return (
# #             ["Please upload your Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts) for a comprehensive tax analysis and personalized tax-saving suggestions."],
# #             "Tax regime analysis requires complete income and deduction data."
# #         )

# #     # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
# #     financial_data_for_gemini = aggregated_financial_data.copy()

# #     # Add specific structure for Bank Statement details if identified as such, or if bank details are present
# #     if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
# #         financial_data_for_gemini['Bank Details'] = {
# #             'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
# #             'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
# #             'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
# #             'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
# #             'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
# #             'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
# #             'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
# #             'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
# #         }
# #         # Optionally, remove transaction_summary if it's too verbose for the prompt
# #         # financial_data_for_gemini.pop('transaction_summary', None)


# #     prompt = f"""
# #     You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
# #     Based on this data:
# #     1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
# #     2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

# #     **Financial Data Summary:**
# #     {json.dumps(financial_data_for_gemini, indent=2)}

# #     **Final Tax Computation Summary:**
# #     {json.dumps(final_tax_computation_summary, indent=2)}

# #     Please format your response strictly as follows:
# #     Suggestions:
# #     - [Suggestion 1]
# #     - [Suggestion 2]
# #     ...
# #     Regime Analysis: [Your analysis paragraph here].
# #     """
# #     try:
# #         response = gemini_pro_model.generate_content(prompt)
# #         text = response.text.strip()
        
# #         suggestions = []
# #         regime_analysis = ""

# #         # Attempt to parse the structured output
# #         if "Suggestions:" in text and "Regime Analysis:" in text:
# #             parts = text.split("Regime Analysis:")
# #             suggestions_part = parts[0].replace("Suggestions:", "").strip()
# #             regime_analysis = parts[1].strip()

# #             # Split suggestions into bullet points and filter out empty strings
# #             suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
# #             if not suggestions: # If parsing as bullets failed, treat as single suggestion
# #                 suggestions = [suggestions_part]
# #         else:
# #             # Fallback if format is not as expected, return raw text as suggestions
# #             suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
# #             regime_analysis = "AI could not parse structured regime analysis."
# #             logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

# #         return suggestions, regime_analysis
# #     except Exception as e:
# #         logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
# #         return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

# # def generate_itr_pdf(tax_record_data):
# #     """
# #     Generates a dummy ITR form PDF.
# #     This uses a basic PDF string structure as a placeholder.
# #     """
# #     aggregated_data = tax_record_data.get('aggregated_financial_data', {})
# #     final_computation = tax_record_data.get('final_tax_computation_summary', {})

# #     # Determine ITR type (simplified logic)
# #     itr_type = "ITR-1 (SAHAJ - DUMMY)"
# #     if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
# #        safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
# #        safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
# #         itr_type = "ITR-2 (DUMMY)"
    
# #     # Extract key info for the dummy PDF
# #     name = aggregated_data.get('name_of_employee', 'N/A')
# #     pan = aggregated_data.get('pan_of_employee', 'N/A')
# #     financial_year = aggregated_data.get('financial_year', 'N/A')
# #     assessment_year = aggregated_data.get('assessment_year', 'N/A')
# #     total_income = final_computation.get('computed_taxable_income', 'N/A')
# #     tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
# #     refund_due = final_computation.get('predicted_refund_due', 0.0)
# #     tax_due = final_computation.get('predicted_additional_due', 0.0)
# #     regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

# #     # Add bank statement specific details to the PDF content if available
# #     bank_details_for_pdf = ""
# #     if aggregated_data.get('identified_type') == 'Bank Statement' or \
# #        (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
# #         bank_details_for_pdf = f"""
# # BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
# # BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
# # """

# #     # Core PDF content without xref and EOF for length calculation
# #     core_pdf_content_lines = [
# #         f"%PDF-1.4",
# #         f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
# #         f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
# #         f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
# #         f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
# #         f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
# #         f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
# #         f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
# #         f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
# #         f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
# #         f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
# #         f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
# #         f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
# #         f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
# #         f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
# #     ]
    
# #     # Append bank details if available
# #     if bank_details_for_pdf:
# #         core_pdf_content_lines.append(bank_details_for_pdf)
# #         # Adjust vertical position for the Note if bank details were added
# #         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
# #     else:
# #         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

# #     core_pdf_content_lines.extend([
# #         f"endstream",
# #         f"endobj",
# #         f"xref",
# #         f"0 5",
# #         f"0000000000 65535 f",
# #         f"0000000010 00000 n",
# #         f"0000000057 00000 n",
# #         f"0000000114 00000 n",
# #         f"0000000222 00000 n",
# #         f"trailer <</Size 5 /Root 1 0 R>>",
# #     ])
    
# #     # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
# #     core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
# #     core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

# #     # Calculate the startxref position
# #     startxref_position = len(core_pdf_bytes)

# #     # Now assemble the full PDF content including startxref and EOF
# #     full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
# #     # Final encode
# #     dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

# #     return io.BytesIO(dummy_pdf_content_bytes), itr_type


# # # --- API Routes ---

# # # Serves the main page (assuming index.html is in the root)
# # @app.route('/')
# # def home():
# #     """Serves the main landing page, typically index.html."""
# #     return send_from_directory('.', 'index.html')

# # # Serves other static files (CSS, JS, images, etc.)
# # @app.route('/<path:path>')
# # def serve_static_files(path):
# #     """Serves static files from the root directory."""
# #     return send_from_directory('.', path)

# # # Serves uploaded files from the uploads folder
# # @app.route('/uploads/<filename>')
# # def uploaded_file(filename):
# #     """Allows access to temporarily stored uploaded files."""
# #     try:
# #         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# #     except FileNotFoundError:
# #         logging.warning(f"File '{filename}' not found in uploads folder.")
# #         return jsonify({"message": "File not found"}), 404
# #     except Exception as e:
# #         logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


# # @app.route('/api/register', methods=['POST'])
# # def register_user():
# #     """Handles user registration."""
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         email = data.get('email')
# #         password = data.get('password')

# #         if not username or not email or not password:
# #             logging.warning("Registration attempt with missing fields.")
# #             return jsonify({"message": "Username, email, and password are required"}), 400

# #         # Check if email or username already exists
# #         if users_collection.find_one({"email": email}):
# #             logging.warning(f"Registration failed: Email '{email}' already exists.")
# #             return jsonify({"message": "Email already exists"}), 409
# #         if users_collection.find_one({"username": username}):
# #             logging.warning(f"Registration failed: Username '{username}' already exists.")
# #             return jsonify({"message": "Username already exists"}), 409

# #         # Hash the password before storing
# #         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
# #         # Prepare user data for MongoDB insertion
# #         new_user_data = {
# #             "username": username,
# #             "email": email,
# #             "password": hashed_password.decode('utf-8'), # Store hashed password as string
# #             "full_name": data.get('fullName', ''),
# #             "pan": data.get('pan', ''),
# #             "aadhaar": data.get('aadhaar', ''),
# #             "address": data.get('address', ''),
# #             "phone": data.get('phone', ''),
# #             "created_at": datetime.utcnow()
# #         }
# #         # Insert the new user record and get the inserted ID
# #         user_id = users_collection.insert_one(new_user_data).inserted_id
# #         logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
# #         return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
# #     except Exception as e:
# #         logging.error(f"Error during registration: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred during registration."}), 500

# # @app.route('/api/login', methods=['POST'])
# # def login_user():
# #     """Handles user login and JWT token generation."""
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         password = data.get('password')

# #         if not username or not password:
# #             logging.warning("Login attempt with missing credentials.")
# #             return jsonify({"error_msg": "Username and password are required"}), 400

# #         # Find the user by username
# #         user = users_collection.find_one({"username": username})

# #         # Verify user existence and password
# #         if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')): # Corrected this line
# #             # Create a JWT access token with the user's MongoDB ObjectId as identity
# #             access_token = create_access_token(identity=str(user['_id']))
# #             logging.info(f"User '{username}' logged in successfully.")
# #             return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
# #         else:
# #             logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
# #             return jsonify({"error_msg": "Invalid credentials"}), 401
# #     except Exception as e:
# #         logging.error(f"Error during login: {traceback.format_exc()}")
# #         return jsonify({"error_msg": "An error occurred during login."}), 500

# # @app.route('/api/profile', methods=['GET'])
# # @jwt_required()
# # def get_user_profile():
# #     """Fetches the profile of the currently authenticated user."""
# #     try:
# #         # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
# #         current_user_id = get_jwt_identity()
# #         # Find user by ObjectId, exclude password from the result
# #         user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
# #         if not user:
# #             logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
# #             return jsonify({"message": "User not found"}), 404

# #         # Convert ObjectId to string for JSON serialization
# #         user['_id'] = str(user['_id'])
# #         logging.info(f"Profile fetched for user ID: {current_user_id}")
# #         return jsonify({"user": user}), 200
# #     except Exception as e:
# #         logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

# # @app.route('/api/profile', methods=['PUT', 'PATCH'])
# # @jwt_required()
# # def update_user_profile():
# #     """Updates the profile of the currently authenticated user."""
# #     try:
# #         current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #         data = request.get_json()

# #         # Define allowed fields for update
# #         updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
# #         update_data = {k: data[k] for k in updatable_fields if k in data}

# #         if not update_data:
# #             logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
# #             return jsonify({"message": "No fields to update provided."}), 400
        
# #         # Prevent username from being updated via this route for security/simplicity
# #         if 'username' in data:
# #             logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

# #         # If email is being updated, ensure it's not already in use by another user
# #         if 'email' in update_data:
# #             existing_user_with_email = users_collection.find_one({"email": update_data['email']})
# #             if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
# #                 logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
# #                 return jsonify({"message": "Email already in use by another account."}), 409

# #         # Perform the update operation in MongoDB
# #         result = users_collection.update_one(
# #             {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
# #             {"$set": update_data}
# #         )

# #         if result.matched_count == 0:
# #             logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
# #             return jsonify({"message": "User not found."}), 404
# #         if result.modified_count == 0:
# #             logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
# #             return jsonify({"message": "Profile data is the same, no changes made."}), 200

# #         logging.info(f"Profile updated successfully for user ID: {current_user_id}")
# #         return jsonify({"message": "Profile updated successfully!"}), 200
# #     except Exception as e:
# #         logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred while updating your profile."}), 500


# # @app.route('/api/process_documents', methods=['POST'])
# # @jwt_required()
# # def process_documents():
# #     """
# #     Handles uploaded documents, extracts financial data using Gemini and Vision API,
# #     aggregates data from multiple files, computes tax, and saves the comprehensive
# #     record to MongoDB, grouped by PAN and Financial Year.
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

# #     if 'documents' not in request.files:
# #         logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
# #         return jsonify({"message": "No 'documents' part in the request"}), 400

# #     files = request.files.getlist('documents')
# #     if not files:
# #         logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
# #         return jsonify({"message": "No selected file"}), 400

# #     extracted_data_from_current_upload = []
# #     document_processing_summary_current_upload = [] # To provide feedback on each file

# #     # Get the selected document type hint from the form data (if provided)
# #     document_type_hint = request.form.get('document_type', 'Auto-Detect') 
# #     logging.info(f"Received document type hint from frontend: {document_type_hint}")

# #     for file in files:
# #         if file.filename == '':
# #             document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
# #             continue
        
# #         filename = secure_filename(file.filename)
# #         # Create a unique filename for storing the original document
# #         unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
# #         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
# #         try:
# #             file_content_bytes = file.read() # Read content before saving
# #             file.seek(0) # Reset file pointer for subsequent operations if needed

# #             # Save the file temporarily (or permanently if you wish to retain originals)
# #             with open(file_path, 'wb') as f:
# #                 f.write(file_content_bytes)
# #             logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

# #             mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default

# #             # Construct the base prompt for Gemini
# #             base_prompt_instructions = (
# #                 f"You are an expert financial data extractor and tax document analyzer for Indian context. "
# #                 f"Analyze the provided document (filename: '{filename}', MIME type: {mime_type}). "
# #                 f"The user has indicated this document is of type: '{document_type_hint}'. " 
# #                 "Extract ALL relevant financial information for Indian income tax filing. "
# #                 "Your response MUST be a JSON object conforming precisely to the provided schema. "
# #                 "For numerical fields, if a value is not explicitly found or is clearly zero, you MUST use `0.0`. "
# #                 "For string fields (like names, PAN, year, dates, identified_type, gender, residential_status), if a value is not explicitly found, you MUST use the string `null`. "
# #                 "For dates, if found, use 'YYYY-MM-DD' format if possible; otherwise, `0000-01-01` if not found or cannot be parsed.\n\n"
# #             )

# #             # Add specific instructions based on document type hint
# #             if document_type_hint == 'Bank Statement':
# #                 base_prompt_instructions += (
# #                     "Specifically for a Bank Statement, extract the following details accurately:\n"
# #                     "- Account Holder Name\n- Account Number\n- IFSC Code (if present)\n- Bank Name\n"
# #                     "- Branch Address\n- Statement Start Date (YYYY-MM-DD)\n- Statement End Date (YYYY-MM-DD)\n"
# #                     "- Opening Balance\n- Closing Balance\n- Total Deposits\n- Total Withdrawals\n"
# #                     "- A summary of key transactions, including date (YYYY-MM-DD), description, and amount. Prioritize large transactions or those with specific identifiable descriptions (e.g., 'salary', 'rent', 'interest').\n"
# #                     "If a field is not found or not applicable, use `null` for strings and `0.0` for numbers. Ensure dates are in YYYY-MM-DD format."
# #                 )
# #             elif document_type_hint == 'Form 16':
# #                 base_prompt_instructions += (
# #                     "Specifically for Form 16, extract details related to employer, employee, PAN, TAN, financial year, assessment year, "
# #                     "salary components (basic, HRA, perquisites, profits in lieu of salary), exempt allowances, professional tax, "
# #                     "income from house property, income from other sources, capital gains, "
# #                     "deductions under Chapter VI-A (80C, 80D, 80G, 80E, 80CCD, etc.), TDS details (total, quarter-wise), "
# #                     "and any mentioned tax regime (Old/New). Ensure all monetary values are extracted as numbers."
# #                 )
# #             elif document_type_hint == 'Salary Slip':
# #                 base_prompt_instructions += (
# #                     "Specifically for a Salary Slip, extract employee name, PAN, employer name, basic salary, HRA, "
# #                     "conveyance allowance, transport allowance, overtime pay, EPF contribution, ESI contribution, "
# #                     "professional tax, net amount payable, days present, and overtime hours. Ensure all monetary values are extracted as numbers."
# #                 )
# #             # Add more elif blocks for other specific document types if needed

# #             if "image" in mime_type or "pdf" in mime_type:
# #                 gemini_response_json_str = get_gemini_response(base_prompt_instructions, file_data=file_content_bytes, mime_type=mime_type, filename=filename)
# #             elif "text" in mime_type or "json" in mime_type:
# #                 extracted_raw_text = file_content_bytes.decode('utf-8')
# #                 final_prompt_content = base_prompt_instructions + f"\n\nDocument Content:\n{extracted_raw_text}"
# #                 gemini_response_json_str = get_gemini_response(final_prompt_content, filename=filename)
# #             else:
# #                 document_processing_summary_current_upload.append({
# #                     "filename": filename, "status": "skipped", "identified_type": "Unsupported",
# #                     "message": f"Unsupported file type: {mime_type}"
# #                 })
# #                 continue
            
# #             try:
# #                 gemini_parsed_response = json.loads(gemini_response_json_str)
# #                 if gemini_parsed_response.get("error"):
# #                     raise ValueError(f"AI processing error: {gemini_parsed_response['error']}")

# #                 extracted_data = gemini_parsed_response.get('extracted_data', {})
                
# #                 if "raw_text_response" in extracted_data:
# #                     document_processing_summary_current_upload.append({
# #                         "filename": filename, "status": "warning", "identified_type": "Unstructured Text",
# #                         "message": "AI could not extract structured JSON. Raw text available.",
# #                         "extracted_raw_text": extracted_data["raw_text_response"],
# #                         "stored_path": f"/uploads/{unique_filename}"
# #                     })
# #                     extracted_data_from_current_upload.append({"identified_type": "Unstructured Text", "raw_text": extracted_data["raw_text_response"]})
# #                     continue 
# #                 # Add the path to the stored document for future reference in history
# #                 extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
# #                 extracted_data_from_current_upload.append(extracted_data)

# #                 document_processing_summary_current_upload.append({
# #                     "filename": filename, "status": "success", "identified_type": extracted_data['identified_type'],
# #                     "message": "Processed successfully.", "extracted_fields": extracted_data,
# #                     "stored_path": f"/uploads/{unique_filename}" 
# #                 })
# #             except (json.JSONDecodeError, ValueError) as ve:
# #                 logging.error(f"Error parsing Gemini response or AI error for '{filename}': {ve}")
# #                 document_processing_summary_current_upload.append({
# #                     "filename": filename, "status": "failed", "message": f"AI response error: {str(ve)}",
# #                     "stored_path": f"/uploads/{unique_filename}"
# #                 })
# #             except Exception as e:
# #                 logging.error(f"Unexpected error processing Gemini data for '{filename}': {traceback.format_exc()}")
# #                 document_processing_summary_current_upload.append({
# #                     "filename": filename, "status": "failed", "message": f"Error processing AI data: {str(e)}",
# #                     "stored_path": f"/uploads/{unique_filename}"
# #                 })
# #             finally:
# #                 pass 

# #         except Exception as e:
# #             logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
# #             document_processing_summary_current_upload.append({
# #                 "filename": filename, "status": "error",
# #                 "message": f"An unexpected error occurred during file processing: {str(e)}",
# #                 "stored_path": f"/uploads/{unique_filename}"
# #             })
# #             pass 

# #     if not extracted_data_from_current_upload:
# #         logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
# #         return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

# #     # --- Determine PAN and Financial Year for grouping ---
# #     # Try to find PAN and FY from the currently uploaded documents first
# #     pan_of_employee = "UNKNOWNPAN"
# #     financial_year = "UNKNOWNFY"

# #     for data in extracted_data_from_current_upload:
# #         if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
# #             pan_of_employee = safe_string(data["pan_of_employee"])
# #         if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
# #             financial_year = safe_string(data["financial_year"])
# #         # If both are found, we can break early (or continue to see if a higher priority doc has them)
# #         if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
# #             break
    
# #     # If still unknown, check if the user profile has a PAN.
# #     if pan_of_employee == "UNKNOWNPAN":
# #         user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
# #         if user_profile and safe_string(user_profile.get("pan")) != "null":
# #             pan_of_employee = safe_string(user_profile["pan"])
# #             logging.info(f"Using PAN from user profile: {pan_of_employee}")
# #         else:
# #             # If PAN is still unknown, log a warning and use the placeholder
# #             logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

# #     # Derive financial year from assessment year if financial_year is null
# #     if financial_year == "UNKNOWNFY":
# #         for data in extracted_data_from_current_upload:
# #             if safe_string(data.get("assessment_year")) != "null":
# #                 try:
# #                     ay_parts = safe_string(data["assessment_year"]).split('-')
# #                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
# #                         start_year = int(ay_parts[0]) -1
# #                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
# #                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
# #                             financial_year = fy
# #                             break
# #                 except Exception:
# #                     pass # Keep default if parsing fails
# #         if financial_year == "UNKNOWNFY":
# #             logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


# #     # Try to find an existing record for this user, PAN, and financial year
# #     existing_tax_record = tax_records_collection.find_one({
# #         "user_id": current_user_id,
# #         "aggregated_financial_data.pan_of_employee": pan_of_employee,
# #         "aggregated_financial_data.financial_year": financial_year
# #     })

# #     if existing_tax_record:
# #         logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
# #         # Merge new extracted data with existing data
# #         all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
# #         all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

# #         # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
# #         updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
# #         updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

# #         # Clear previous AI/ML results as they need to be re-generated for the updated data
# #         tax_records_collection.update_one(
# #             {"_id": existing_tax_record["_id"]},
# #             {"$set": {
# #                 "extracted_documents_data": all_extracted_data_for_fy,
# #                 "document_processing_summary": all_document_processing_summary_for_fy,
# #                 "aggregated_financial_data": updated_aggregated_financial_data,
# #                 "final_tax_computation_summary": updated_final_tax_computation_summary,
# #                 "timestamp": datetime.utcnow(), # Update timestamp of last modification
# #                 "suggestions_from_gemini": [], # Reset suggestions
# #                 "gemini_regime_analysis": "null", # Reset regime analysis
# #                 "ml_prediction_summary": {}, # Reset ML predictions
# #             }}
# #         )
# #         record_id = existing_tax_record["_id"]
# #         logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

# #     else:
# #         logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
# #         # If no existing record, aggregate only the newly uploaded data
# #         new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
# #         new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

# #         # Prepare the comprehensive tax record to save to MongoDB
# #         tax_record_to_save = {
# #             "user_id": current_user_id, 
# #             "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
# #             "financial_year": financial_year, # Store FY at top level for easy query
# #             "timestamp": datetime.utcnow(),
# #             "document_processing_summary": document_processing_summary_current_upload, 
# #             "extracted_documents_data": extracted_data_from_current_upload, 
# #             "aggregated_financial_data": new_aggregated_financial_data,
# #             "final_tax_computation_summary": new_final_tax_computation_summary,
# #             "suggestions_from_gemini": [], 
# #             "gemini_regime_analysis": "null", 
# #             "ml_prediction_summary": {},    
# #         }
# #         record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
# #         logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
# #         updated_aggregated_financial_data = new_aggregated_financial_data
# #         updated_final_tax_computation_summary = new_final_tax_computation_summary


# #     # Return success response with computed data
# #     # Ensure all data sent back is JSON serializable (e.g., no numpy types)
# #     response_data = {
# #         "status": "success",
# #         "message": "Documents processed and financial data aggregated and tax computed successfully",
# #         "record_id": str(record_id), 
# #         "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
# #         "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
# #         "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
# #     }
# #     return jsonify(response_data), 200


# # @app.route('/api/get_suggestions', methods=['POST'])
# # @jwt_required()
# # def get_suggestions():
# #     """
# #     Generates AI-driven tax-saving suggestions and provides an ML prediction summary
# #     based on a specific processed tax record (grouped by PAN/FY).
# #     """
# #     current_user_id = get_jwt_identity()

# #     data = request.get_json()
# #     record_id = data.get('record_id')

# #     if not record_id:
# #         logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
# #         return jsonify({"message": "Record ID is required to get suggestions."}), 400

# #     try:
# #         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
# #         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
# #         if not tax_record:
# #             logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
# #             return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
# #         # Get the aggregated financial data and final tax computation summary from the record
# #         aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
# #         final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

# #         # Generate suggestions and ML predictions
# #         suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
# #         ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

# #         # Update the record in DB with generated suggestions and predictions
# #         tax_records_collection.update_one(
# #             {"_id": ObjectId(record_id)},
# #             {"$set": {
# #                 "suggestions_from_gemini": suggestions,
# #                 "gemini_regime_analysis": regime_analysis,
# #                 "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
# #                 "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
# #             }}
# #         )
# #         logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

# #         return jsonify({
# #             "status": "success",
# #             "message": "AI suggestions and ML predictions generated successfully!",
# #             "suggestions_from_gemini": suggestions,
# #             "gemini_regime_analysis": regime_analysis,
# #             "ml_prediction_summary": ml_prediction_summary # Already converted
# #         }), 200
# #     except Exception as e:
# #         logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
# #         # Fallback for ML prediction summary even if overall suggestions fail
# #         ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
# #         return jsonify({
# #             "status": "error",
# #             "message": "An error occurred while generating suggestions.",
# #             "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
# #             "gemini_regime_analysis": "An error occurred.",
# #             "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
# #         }), 500

# # @app.route('/api/save_extracted_data', methods=['POST'])
# # @jwt_required()
# # def save_extracted_data():
# #     """
# #     Saves extracted and computed tax data to MongoDB.
# #     This route can be used for explicit saving if `process_documents` doesn't
# #     cover all saving scenarios or for intermediate saves.
# #     NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
# #     For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #     data = request.get_json()
# #     if not data:
# #         logging.warning(f"Save data request from user {current_user_id} with no data provided.")
# #         return jsonify({"message": "No data provided to save"}), 400
# #     try:
# #         # This route might be less relevant with the new aggregation by PAN/FY,
# #         # as `process_documents` handles the upsert logic.
# #         # However, if used for manual saving of *already aggregated* data,
# #         # ensure PAN and FY are part of `data.aggregated_financial_data`
# #         # or extracted from the `data` directly.
# #         # Example: Try to get PAN and FY from input data for consistency
# #         input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
# #         input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

# #         # Check for existing record for upsert behavior
# #         existing_record = tax_records_collection.find_one({
# #             "user_id": current_user_id,
# #             "aggregated_financial_data.pan_of_employee": input_pan,
# #             "aggregated_financial_data.financial_year": input_fy
# #         })

# #         if existing_record:
# #             # Update existing record
# #             update_result = tax_records_collection.update_one(
# #                 {"_id": existing_record["_id"]},
# #                 {"$set": {
# #                     **data, # Overwrite with new data, ensuring user_id and timestamp are also set
# #                     "user_id": current_user_id,
# #                     "timestamp": datetime.utcnow(),
# #                     "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
# #                     "financial_year": input_fy, # Ensure top-level FY is consistent
# #                 }}
# #             )
# #             record_id = existing_record["_id"]
# #             logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
# #             if update_result.modified_count == 0:
# #                 return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
# #         else:
# #             # Insert new record
# #             data['user_id'] = current_user_id
# #             data['timestamp'] = datetime.utcnow()
# #             data['pan_of_employee'] = input_pan
# #             data['financial_year'] = input_fy
# #             record_id = tax_records_collection.insert_one(data).inserted_id
# #             logging.info(f"New data saved for user {current_user_id} with record ID: {record_id}")
        
# #         return jsonify({"message": "Data saved successfully", "record_id": str(record_id)}), 200
# #     except Exception as e:
# #         logging.error(f"Error saving data for user {current_user_id}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to save data", "error": str(e)}), 500

# # # --- Corrected route path to /tax-records to match frontend call ---
# # @app.route('/api/tax-records', methods=['GET'])
# # @jwt_required()
# # def get_tax_records():
# #     """
# #     Fetches all aggregated tax records for the logged-in user, grouped by Financial Year.
# #     Records are sorted by timestamp in descending order (most recent first).
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #     logging.info(f"Fetching tax records for user: {current_user_id}")
# #     try:
# #         # Fetch all records for the current user, sorted by financial_year and then by timestamp
# #         # The 'user_id', 'pan_of_employee', and 'financial_year' are top-level fields now
# #         records = list(tax_records_collection.find({"user_id": current_user_id})
# #                         .sort([("financial_year", -1), ("timestamp", -1)]))

# #         # Convert MongoDB ObjectId to string for JSON serialization
# #         for record in records:
# #             record['_id'] = str(record['_id'])
# #             # Ensure 'user_id' is also a string when sending to frontend
# #             if 'user_id' in record:
# #                 record['user_id'] = str(record['user_id'])
# #             # Remove potentially large raw data fields for history list view to save bandwidth
# #             record.pop('extracted_documents_data', None)
# #         logging.info(f"Found {len(records)} tax records for user {current_user_id}")
# #         # The frontend's TaxHistory component expects a 'history' key in the response data.
# #         return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200 # Convert numpy types
# #     except Exception as e:
# #         logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
# #         return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

# # # --- Corrected route path to /api/generate-itr/ to match frontend call ---
# # @app.route('/api/generate-itr/<record_id>', methods=['GET'])
# # @jwt_required()
# # def generate_itr_form_route(record_id):
# #     """
# #     Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
# #     """
# #     current_user_id = get_jwt_identity()
# #     try:
# #         record_obj_id = ObjectId(record_id) # Convert record_id string to ObjectId for DB query
# #         # Ensure the tax record belongs to the current user (user_id check)
# #         tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

# #         if not tax_record:
# #             logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
# #             return jsonify({"message": "Tax record not found or unauthorized."}), 404

# #         # Generate the dummy PDF content
# #         pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
# #         pdf_buffer.seek(0) # Rewind the buffer to the beginning

# #         response = send_file(
# #             pdf_buffer,
# #             mimetype='application/pdf',
# #             as_attachment=True,
# #             download_name=f"{itr_type.replace(' ', '_')}_{record_id}.pdf"
# #         )
# #         logging.info(f"Generated and sent dummy ITR form for record ID: {record_id}")
# #         return response
# #     except Exception as e:
# #         logging.error(f"Error generating ITR form for record {record_id}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to generate ITR form.", "error": str(e)}), 500

# # @app.route('/api/contact', methods=['POST'])
# # def contact_message():
# #     """Handles contact form submissions."""
# #     try:
# #         data = request.get_json()
# #         name = data.get('name')
# #         email = data.get('email')
# #         subject = data.get('subject')
# #         message = data.get('message')

# #         if not all([name, email, subject, message]):
# #             logging.warning("Contact form submission with missing fields.")
# #             return jsonify({"message": "All fields are required."}), 400
        
# #         # Insert contact message into MongoDB
# #         contact_messages_collection.insert_one({
# #             "name": name,
# #             "email": email,
# #             "subject": subject,
# #             "message": message,
# #             "timestamp": datetime.utcnow()
# #         })
# #         logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

# #         return jsonify({"message": "Message sent successfully!"}), 200
# #     except Exception as e:
# #         logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred while sending your message."}), 500

# # # --- Main application entry point ---
# # if __name__ == '__main__':
# #     # Ensure MongoDB connection is established before running the app
# #     if db is None:
# #         logging.error("MongoDB connection failed at startup. Exiting.")
# #         exit(1)
    
# #     logging.info("Starting Flask application...")
# #     # Run the Flask app
# #     # debug=True enables reloader and debugger (should be False in production)
# #     # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
# #     # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
# #     app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)



















# # import os
# # import json
# # from flask import Flask, request, jsonify, send_from_directory, send_file
# # from flask_cors import CORS
# # import google.generativeai as genai
# # from pymongo import MongoClient
# # from bson.objectid import ObjectId
# # import bcrypt
# # import traceback
# # import logging
# # import io
# # from datetime import datetime, timedelta
# # from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# # import base64
# # from google.cloud import vision
# # from google.oauth2 import service_account
# # from werkzeug.utils import secure_filename # Import secure_filename
# # import joblib # Import joblib for loading ML models
# # import pandas as pd # Import pandas for ML model input

# # # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# # import numpy as np

# # # Import ReportLab components for PDF generation
# # try:
# #     # We are using a dummy PDF for now, so ReportLab is not strictly needed for functionality
# #     # but the import block is kept for reference if actual PDF generation is implemented.
# #     from reportlab.pdfgen import canvas
# #     from reportlab.lib.pagesizes import letter
# #     from reportlab.lib.units import inch
# #     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# #     from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
# #     from reportlab.lib.enums import TA_CENTER
# #     REPORTLAB_AVAILABLE = True # Set to True if you install ReportLab
# # except ImportError:
# #     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
# #     REPORTLAB_AVAILABLE = False


# # # Configure logging for better visibility
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # --- Configuration (IMPORTANT: Use environment variables in production) ---
# # GEMINI_API_KEY = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs" # Replace with your actual key or env var
# # MONGO_URI = "mongodb://localhost:27017/"
# # JWT_SECRET_KEY = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# # VISION_API_KEY_PATH = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json" # Path to your GCP service account key file
# # # GEMINI_API_KEY_HARDCODED = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs"
# # # MONGO_URI_HARDCODED = "mongodb://localhost:27017/"
# # # JWT_SECRET_KEY_HARDCODED = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# # # # Ensure the path for Vision API key is correct for your system. Use a raw string (r"")
# # # # or forward slashes (/) for paths to avoid issues with backslashes.
# # # VISION_API_KEY_PATH_HARDCODED = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json"
# # # Initialize Flask app
# # app = Flask(__name__, static_folder='static') # Serve static files from 'static' folder
# # CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# # # Setup Flask-JWT-Extended
# # app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
# # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Token validity
# # jwt = JWTManager(app)
# # UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# # # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# # @jwt.expired_token_loader
# # def expired_token_callback(jwt_header, jwt_payload):
# #     logging.warning("JWT token expired.")
# #     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# # @jwt.invalid_token_loader
# # def invalid_token_callback(callback_error):
# #     logging.warning(f"Invalid JWT token: {callback_error}")
# #     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# # @jwt.unauthorized_loader
# # def unauthorized_callback(callback_error):
# #     logging.warning(f"Unauthorized access attempt: {callback_error}")
# #     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401


# # # Initialize MongoDB
# # client = None
# # db = None
# # users_collection = None
# # tax_records_collection = None
# # contact_messages_collection = None
# # try:
# #     client = MongoClient(MONGO_URI)
# #     db = client.garudatax_ai # Your database name
# #     users_collection = db['users']
# #     tax_records_collection = db['tax_records'] # Collection for processed tax documents
# #     contact_messages_collection = db['contact_messages']
# #     logging.info("MongoDB connected successfully.")
# # except Exception as e:
# #     logging.error(f"Could not connect to MongoDB: {e}")
# #     db = None # Set db to None if connection fails

# # # Configure Google Gemini API
# # try:
# #     genai.configure(api_key=GEMINI_API_KEY)
# #     gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Or 'gemini-pro'
# #     logging.info("Google Gemini API configured.")
# # except Exception as e:
# #     logging.error(f"Could not configure Google Gemini API: {e}")
# #     gemini_model = None

# # # Configure Google Cloud Vision API
# # vision_client = None
# # try:
# #     if os.path.exists(VISION_API_KEY_PATH):
# #         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH)
# #         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
# #         logging.info("Google Cloud Vision API configured.")
# #     else:
# #         logging.warning(f"Vision API key file not found at {VISION_API_KEY_PATH}. OCR functionality may be limited.")
# # except Exception as e:
# #     logging.error(f"Could not configure Google Cloud Vision API: {e}")
# #     vision_client = None

# # # Load ML Models (Classifier for Tax Regime, Regressor for Tax Liability)
# # tax_regime_classifier_model = None
# # tax_regressor_model = None
# # try:
# #     # Ensure these paths are correct relative to where app1.py is run
# #     # Assuming models are in a 'models' directory at the same level as app1.py
# #     classifier_path = 'tax_regime_classifier_model.pkl'
# #     regressor_path = 'final_tax_regressor_model.pkl'

# #     if os.path.exists(classifier_path):
# #         tax_regime_classifier_model = joblib.load(classifier_path)
# #         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
# #     else:
# #         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

# #     if os.path.exists(regressor_path):
# #         tax_regressor_model = joblib.load(regressor_path)
# #         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
# #     else:
# #         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# # except Exception as e:
# #     logging.error(f"Error loading ML models: {e}. Ensure 'models/' directory exists and models are trained.")

# # # --- Helper Functions ---
# # def get_user_id():
# #     """Retrieves user ID from JWT token."""
# #     try:
# #         return get_jwt_identity()
# #     except Exception as e:
# #         logging.warning(f"Could not get JWT identity: {e}")
# #         return None

# # def allowed_file(filename):
# #     """Checks if the uploaded file has an allowed extension."""
# #     return '.' in filename and \
# #            filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

# # def ocr_document(file_bytes):
# #     """Performs OCR on the document using Google Cloud Vision API."""
# #     if not vision_client:
# #         logging.error("Google Cloud Vision client not initialized.")
# #         return {"error": "OCR service unavailable."}, None

# #     image = vision.Image(content=file_bytes)
# #     try:
# #         response = vision_client.document_text_detection(image=image)
# #         full_text = response.full_text_annotation.text
# #         return None, full_text
# #     except Exception as e:
# #         logging.error(f"Error during OCR with Vision API: {traceback.format_exc()}")
# #         return {"error": f"OCR failed: {e}"}, None

# # def safe_float(val):
# #     """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
# #     Handles commas and currency symbols."""
# #     try:
# #         if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
# #             return 0.0
# #         if isinstance(val, str):
# #             # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
# #             val = val.replace(',', '').replace('₹', '').strip()
            
# #         return float(val)
# #     except (ValueError, TypeError):
# #         logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
# #         return 0.0

# # def safe_string(val):
# #     """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
# #     if val is None:
# #         return "null"
# #     s_val = str(val).strip()
# #     if s_val == "":
# #         return "null"
# #     return s_val

# # def convert_numpy_types(obj):
# #     """
# #     Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
# #     This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
# #     """
# #     if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
# #         return obj.item() # Converts numpy scalar to Python scalar
# #     elif isinstance(obj, dict):
# #         return {k: convert_numpy_types(v) for k, v in obj.items()}
# #     elif isinstance(obj, list):
# #         return [convert_numpy_types(elem) for elem in obj]
# #     else:
# #         return obj

# # def extract_fields_with_gemini(document_text, document_type_hint='Auto-Detect'):
# #     """
# #     Extracts key financial and personal fields from document text using Gemini.
# #     The prompt is designed to elicit specific, structured JSON output.
# #     """
# #     if not gemini_model:
# #         return {"error": "Gemini model not initialized."}, None

# #     # Refined prompt for more specific and structured extraction
# #     prompt_template = """
# #     You are an expert AI assistant for Indian income tax documents.
# #     Extract the following details from the provided document text.
# #     If a field is not present, use "null" for string values, 0 for numerical values, and "0000-01-01" for dates.
# #     Be precise and use the exact keys provided.
# #     For financial figures, extract the numerical value. For dates, use 'YYYY-MM-DD' format if available.
    
# #     Document Type Hint (provided by user, use if it helps but auto-detect if necessary): {document_type_hint}

# #     Extracted Fields (Strict JSON Format):
# #     {{
# #         "identified_type": "Detect the document type (e.g., 'Form 16', 'Bank Statement', 'Salary Slip', 'Form 26AS', 'Investment Proof', 'Home Loan Statement', 'Other Document').",
# #         "financial_year": "e.g., 2023-24",
# #         "assessment_year": "e.g., 2024-25",
# #         "name_of_employee": "Full name of employee/account holder",
# #         "pan_of_employee": "PAN number",
# #         "date_of_birth": "YYYY-MM-DD",
# #         "gender": "M/F/Other",
# #         "residential_status": "Resident/Non-Resident",
# #         "employer_name": "Employer's name",
# #         "employer_address": "Employer's address",
# #         "pan_of_deductor": "Deductor's PAN",
# #         "tan_of_deductor": "Deductor's TAN",
# #         "designation_of_employee": "Employee's designation",
# #         "period_from": "YYYY-MM-DD (e.g., start date of salary slip period)",
# #         "period_to": "YYYY-MM-DD (e.g., end date of salary slip period)",

# #         // Income Details
# #         "gross_salary_total": 0.0,
# #         "salary_as_per_sec_17_1": 0.0,
# #         "value_of_perquisites_u_s_17_2": 0.0,
# #         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
# #         "basic_salary": 0.0,
# #         "hra_received": 0.0,
# #         "conveyance_allowance": 0.0,
# #         "transport_allowance": 0.0,
# #         "overtime_pay": 0.0,
# #         "total_exempt_allowances": 0.0,
# #         "income_from_house_property": 0.0,
# #         "income_from_other_sources": 0.0,
# #         "capital_gains_long_term": 0.0,
# #         "capital_gains_short_term": 0.0,
# #         "gross_total_income_as_per_document": 0.0,

# #         // Deductions
# #         "professional_tax": 0.0,
# #         "interest_on_housing_loan_self_occupied": 0.0,
# #         "deduction_80c": 0.0,
# #         "deduction_80c_epf": 0.0,
# #         "deduction_80c_insurance_premium": 0.0,
# #         "deduction_80ccc": 0.0,
# #         "deduction_80ccd": 0.0,
# #         "deduction_80ccd1b": 0.0,
# #         "deduction_80d": 0.0,
# #         "deduction_80g": 0.0,
# #         "deduction_80tta": 0.0,
# #         "deduction_80ttb": 0.0,
# #         "deduction_80e": 0.0,
# #         "total_deductions_chapter_via": 0.0,
# #         "aggregate_of_deductions_from_salary": 0.0,
# #         "epf_contribution": 0.0,
# #         "esi_contribution": 0.0,

# #         // Tax Paid
# #         "total_tds": 0.0,
# #         "total_tds_deducted_summary": 0.0,
# #         "total_tds_deposited_summary": 0.0,
# #         "quarter_1_receipt_number": "null",
# #         "quarter_1_tds_deducted": 0.0,
# #         "quarter_1_tds_deposited": 0.0,
# #         "advance_tax": 0.0,
# #         "self_assessment_tax": 0.0,

# #         // Other Tax Info
# #         "taxable_income_as_per_document": 0.0,
# #         "tax_payable_as_per_document": 0.0,
# #         "refund_status_as_per_document": "null",
# #         "tax_regime_chosen": "Old/New/null",
# #         "net_amount_payable": 0.0,
# #         "days_present": "null",
# #         "overtime_hours": "null",

# #         // Bank Statement Details (prioritize these if identified_type is Bank Statement)
# #         "account_holder_name": "null",
# #         "account_number": "null",
# #         "ifsc_code": "null",
# #         "bank_name": "null",
# #         "branch_address": "null",
# #         "statement_start_date": "0000-01-01",
# #         "statement_end_date": "0000-01-01",
# #         "opening_balance": 0.0,
# #         "closing_balance": 0.0,
# #         "total_deposits": 0.0,
# #         "total_withdrawals": 0.0,
# #         "transaction_summary": [
# #             {
# #                 "date": "YYYY-MM-DD",
# #                 "description": "transaction description",
# #                 "type": "CR/DR",
# #                 "amount": 0.0
# #             }
# #         ]
# #     }}
    
# #     Document Text:
# #     {document_text}
# #     """

# #     full_prompt = prompt_template.format(document_type_hint=document_type_hint, document_text=document_text)

# #     try:
# #         response = gemini_model.generate_content(full_prompt)
# #         extracted_json_str = response.candidates[0].content.parts[0].text
# #         # Clean the string to ensure it's valid JSON
# #         # Sometimes Gemini might include markdown ```json ... ``` or extra text
# #         if extracted_json_str.strip().startswith("```json"):
# #             extracted_json_str = extracted_json_str.replace("```json", "").replace("```", "").strip()
        
# #         extracted_data = json.loads(extracted_json_str)
# #         # Ensure all keys from schema are present and correctly typed (even if null or 0 from Gemini)
# #         # This explicit casting is crucial for consistent data types in MongoDB and frontend.
# #         for key, prop_details in { # Define expected types for all fields that Gemini outputs
# #                 "identified_type": "STRING", "financial_year": "STRING", "assessment_year": "STRING",
# #                 "name_of_employee": "STRING", "pan_of_employee": "STRING", "date_of_birth": "DATE_STRING",
# #                 "gender": "STRING", "residential_status": "STRING", "employer_name": "STRING",
# #                 "employer_address": "STRING", "pan_of_deductor": "STRING", "tan_of_deductor": "STRING",
# #                 "designation_of_employee": "STRING", "period_from": "DATE_STRING", "period_to": "DATE_STRING",
# #                 "gross_salary_total": "NUMBER", "salary_as_per_sec_17_1": "NUMBER", "value_of_perquisites_u_s_17_2": "NUMBER",
# #                 "profits_in_lieu_of_salary_u_s_17_3": "NUMBER", "basic_salary": "NUMBER", "hra_received": "NUMBER",
# #                 "conveyance_allowance": "NUMBER", "transport_allowance": "NUMBER", "overtime_pay": "NUMBER",
# #                 "total_exempt_allowances": "NUMBER", "income_from_house_property": "NUMBER", "income_from_other_sources": "NUMBER",
# #                 "capital_gains_long_term": "NUMBER", "capital_gains_short_term": "NUMBER",
# #                 "gross_total_income_as_per_document": "NUMBER", "professional_tax": "NUMBER",
# #                 "interest_on_housing_loan_self_occupied": "NUMBER", "deduction_80c": "NUMBER",
# #                 "deduction_80c_epf": "NUMBER", "deduction_80c_insurance_premium": "NUMBER", "deduction_80ccc": "NUMBER",
# #                 "deduction_80ccd": "NUMBER", "deduction_80ccd1b": "NUMBER", "deduction_80d": "NUMBER",
# #                 "deduction_80g": "NUMBER", "deduction_80tta": "NUMBER", "deduction_80ttb": "NUMBER",
# #                 "deduction_80e": "NUMBER", "total_deductions_chapter_via": "NUMBER", "aggregate_of_deductions_from_salary": "NUMBER",
# #                 "epf_contribution": "NUMBER", "esi_contribution": "NUMBER", "total_tds": "NUMBER",
# #                 "total_tds_deducted_summary": "NUMBER", "total_tds_deposited_summary": "NUMBER",
# #                 "quarter_1_receipt_number": "STRING", "quarter_1_tds_deducted": "NUMBER", "quarter_1_tds_deposited": "NUMBER",
# #                 "advance_tax": "NUMBER", "self_assessment_tax": "NUMBER", "taxable_income_as_per_document": "NUMBER",
# #                 "tax_payable_as_per_document": "NUMBER", "refund_status_as_per_document": "STRING",
# #                 "tax_regime_chosen": "STRING", "net_amount_payable": "NUMBER", "days_present": "STRING",
# #                 "overtime_hours": "STRING",
# #                 "account_holder_name": "STRING", "account_number": "STRING", "ifsc_code": "STRING",
# #                 "bank_name": "STRING", "branch_address": "STRING", "statement_start_date": "DATE_STRING",
# #                 "statement_end_date": "DATE_STRING", "opening_balance": "NUMBER", "closing_balance": "NUMBER",
# #                 "total_deposits": "NUMBER", "total_withdrawals": "NUMBER", "transaction_summary": "ARRAY_OF_OBJECTS"
# #         }.items():
# #             if key not in extracted_data or extracted_data[key] is None:
# #                 if prop_details == "NUMBER":
# #                     extracted_data[key] = 0.0
# #                 elif prop_details == "DATE_STRING":
# #                     extracted_data[key] = "0000-01-01"
# #                 elif prop_details == "ARRAY_OF_OBJECTS":
# #                     extracted_data[key] = []
# #                 else: # Default for STRING
# #                     extracted_data[key] = "null"
# #             else:
# #                 # Type conversion/validation
# #                 if prop_details == "NUMBER":
# #                     extracted_data[key] = safe_float(extracted_data[key])
# #                 elif prop_details == "DATE_STRING":
# #                     # Validate and format date strings
# #                     date_val = safe_string(extracted_data[key])
# #                     try:
# #                         if date_val and date_val != "0000-01-01":
# #                             dt_obj = datetime.strptime(date_val.split('T')[0], '%Y-%m-%d')
# #                             extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
# #                         else:
# #                             extracted_data[key] = "0000-01-01"
# #                     except ValueError:
# #                         extracted_data[key] = "0000-01-01"
# #                 elif prop_details == "STRING":
# #                     extracted_data[key] = safe_string(extracted_data[key])
# #                 elif prop_details == "ARRAY_OF_OBJECTS":
# #                     if key == "transaction_summary" and isinstance(extracted_data[key], list):
# #                         processed_transactions = []
# #                         for item in extracted_data[key]:
# #                             processed_item = {
# #                                 "date": safe_string(item.get("date", "0000-01-01")),
# #                                 "description": safe_string(item.get("description")),
# #                                 "type": safe_string(item.get("type", "null")),
# #                                 "amount": safe_float(item.get("amount"))
# #                             }
# #                             # Re-validate and format transaction date
# #                             try:
# #                                 if processed_item['date'] and processed_item['date'] != "0000-01-01":
# #                                     dt_obj = datetime.strptime(processed_item['date'].split('T')[0], '%Y-%m-%d')
# #                                     processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
# #                                 else:
# #                                     processed_item['date'] = "0000-01-01"
# #                             except ValueError:
# #                                 processed_item['date'] = "0000-01-01"
# #                             processed_transactions.append(processed_item)
# #                         extracted_data[key] = processed_transactions
# #                     else:
# #                         extracted_data[key] = [] # Fallback to empty list if not expected format
        
# #         return None, extracted_data
# #     except Exception as e:
# #         logging.error(f"Error during Gemini extraction or post-processing: {traceback.format_exc()}")
# #         return {"error": f"Gemini extraction failed or data parsing error: {e}"}, None


# # def _aggregate_financial_data(extracted_data_list):
# #     """
# #     Aggregates financial data from multiple extracted documents, applying reconciliation rules.
# #     Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
# #     """
    
# #     aggregated_data = {
# #         # Initialize all fields that are expected in the final aggregated output
# #         "identified_type": "Other Document", # Overall identified type if mixed documents
# #         "employer_name": "null", "employer_address": "null",
# #         "pan_of_deductor": "null", "tan_of_deductor": "null",
# #         "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
# #         "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
# #         "assessment_year": "null", "financial_year": "null",
# #         "period_from": "0000-01-01", "period_to": "0000-01-01",
        
# #         # Income Components - These should be summed
# #         "basic_salary": 0.0,
# #         "hra_received": 0.0,
# #         "conveyance_allowance": 0.0,
# #         "transport_allowance": 0.0,
# #         "overtime_pay": 0.0,
# #         "salary_as_per_sec_17_1": 0.0,
# #         "value_of_perquisites_u_s_17_2": 0.0,
# #         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
# #         "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

# #         "income_from_house_property": 0.0,
# #         "income_from_other_sources": 0.0,
# #         "capital_gains_long_term": 0.0,
# #         "capital_gains_short_term": 0.0,

# #         # Deductions - These should be summed, capped later if needed
# #         "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
# #         "professional_tax": 0.0,
# #         "interest_on_housing_loan_self_occupied": 0.0,
# #         "deduction_80c": 0.0,
# #         "deduction_80c_epf": 0.0,
# #         "deduction_80c_insurance_premium": 0.0,
# #         "deduction_80ccc": 0.0,
# #         "deduction_80ccd": 0.0,
# #         "deduction_80ccd1b": 0.0,
# #         "deduction_80d": 0.0,
# #         "deduction_80g": 0.0,
# #         "deduction_80tta": 0.0,
# #         "deduction_80ttb": 0.0,
# #         "deduction_80e": 0.0,
# #         "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
# #         "epf_contribution": 0.0, # Initialize epf_contribution
# #         "esi_contribution": 0.0, # Initialize esi_contribution


# #         # Tax Paid
# #         "total_tds": 0.0,
# #         "advance_tax": 0.0,
# #         "self_assessment_tax": 0.0,
# #         "total_tds_deducted_summary": 0.0, # From Form 16 Part A

# #         # Document Specific (Non-summable, usually taken from most authoritative source)
# #         "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

# #         # Bank Account Details (Take from the most complete or latest if multiple)
# #         "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
# #         "bank_name": "null", "branch_address": "null",
# #         "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
# #         "opening_balance": 0.0, "closing_balance": 0.0,
# #         "total_deposits": 0.0, "total_withdrawals": 0.0,
# #         "transaction_summary": [], # Aggregate all transactions

# #         # Other fields from the schema, ensuring they exist
# #         "net_amount_payable": 0.0,
# #         "days_present": "null",
# #         "overtime_hours": "null",

# #         # Calculated fields for frontend
# #         "Age": "N/A", 
# #         "total_gross_income": 0.0, # Overall sum of all income heads
# #         "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
# #         "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
# #         "deduction_80C": 0.0, # Alias for deduction_80c
# #         "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
# #         "deduction_80D": 0.0, # Alias for deduction_80d
# #         "deduction_80G": 0.0, # Alias for deduction_80g
# #         "deduction_80TTA": 0.0, # Alias for deduction_80tta
# #         "deduction_80TTB": 0.0, # Alias for deduction_80ttb
# #         "deduction_80E": 0.0, # Alias for deduction_80e
# #         "total_deductions": 0.0, # Overall total deductions used in calculation
# #     }

# #     # Define document priority for overriding fields (higher value means higher priority)
# #     # Form 16 should provide definitive income/deduction figures.
# #     doc_priority = {
# #         "Form 16": 5,
# #         "Form 26AS": 4,
# #         "Salary Slip": 3,
# #         "Investment Proof": 2,
# #         "Home Loan Statement": 2,
# #         "Bank Statement": 1, # Lowest priority for financial figures, highest for bank-specific
# #         "Other Document": 0,
# #         "Unknown": 0,
# #         "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
# #     }

# #     # Sort documents by priority (higher priority first)
# #     sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

# #     # Use a dictionary to track which field was last set by which document priority
# #     # This helps in overriding with higher-priority document data.
# #     field_source_priority = {key: -1 for key in aggregated_data}

# #     # Iterate through sorted documents and aggregate data
# #     for data in sorted_extracted_data:
# #         doc_type = safe_string(data.get('identified_type'))
# #         current_priority = doc_priority.get(doc_type, 0)
# #         logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

# #         # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
# #         # Otherwise, individual components will be summed later.
# #         extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
# #         if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
# #             aggregated_data["gross_salary_total"] = extracted_gross_salary_total
# #             field_source_priority["gross_salary_total"] = current_priority
# #             logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

# #         # Update core personal details only from highest priority document or if current is 'null'
# #         personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
# #         for p_field in personal_fields:
# #             if safe_string(data.get(p_field)) != "null" and \
# #                (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
# #                 aggregated_data[p_field] = safe_string(data.get(p_field))
# #                 field_source_priority[p_field] = current_priority


# #         for key, value in data.items():
# #             # Skip keys already handled explicitly or which have specific aggregation logic
# #             if key in personal_fields or key == "gross_salary_total":
# #                 continue 
# #             if key == "transaction_summary":
# #                 if isinstance(value, list):
# #                     aggregated_data[key].extend(value)
# #                 continue
# #             if key == "identified_type":
# #                 # Ensure highest priority identified_type is kept
# #                 if current_priority > field_source_priority.get(key, -1):
# #                     aggregated_data[key] = safe_string(value)
# #                     field_source_priority[key] = current_priority
# #                 continue
            
# #             # General handling for numerical fields: sum them up
# #             if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
# #                 # Special handling for bank balances: take from latest/highest priority statement
# #                 if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
# #                     if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
# #                         # Only update if the current document is a bank statement and has higher or equal priority
# #                         # (or if the existing aggregated value is 0)
# #                         if current_priority >= field_source_priority.get(key, -1):
# #                             aggregated_data[key] = safe_float(value)
# #                             field_source_priority[key] = current_priority
# #                     else: # For other document types, just sum the numbers if they appear
# #                         aggregated_data[key] += safe_float(value)
# #                 else:
# #                     aggregated_data[key] += safe_float(value)
# #             # General handling for string fields: take from highest priority document
# #             elif key in aggregated_data and isinstance(aggregated_data[key], str):
# #                 if safe_string(value) != "null" and safe_string(value) != "" and \
# #                    (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
# #                     aggregated_data[key] = safe_string(value)
# #                     field_source_priority[key] = current_priority
# #             # Default for other types if they are not explicitly handled
# #             elif key in aggregated_data and value is not None:
# #                 if current_priority > field_source_priority.get(key, -1):
# #                     aggregated_data[key] = value
# #                     field_source_priority[key] = current_priority

# #     # --- Post-aggregation calculations and reconciliation ---
    
# #     # Calculate `total_gross_income` (overall income from all heads)
# #     # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
# #     # try to derive it from payslip components like basic, HRA, etc.
# #     if aggregated_data["gross_salary_total"] == 0.0:
# #         aggregated_data["gross_salary_total"] = (
# #             safe_float(aggregated_data["basic_salary"]) +
# #             safe_float(aggregated_data["hra_received"]) +
# #             safe_float(aggregated_data["conveyance_allowance"]) +
# #             safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
# #             safe_float(aggregated_data["overtime_pay"]) +
# #             safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
# #             safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
# #         )
# #         # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
# #         # Assuming extracted values are already annual or normalized.

# #     # Now calculate the comprehensive total_gross_income for tax computation
# #     aggregated_data["total_gross_income"] = (
# #         safe_float(aggregated_data["gross_salary_total"]) +
# #         safe_float(aggregated_data["income_from_house_property"]) +
# #         safe_float(aggregated_data["income_from_other_sources"]) + 
# #         safe_float(aggregated_data["capital_gains_long_term"]) +
# #         safe_float(aggregated_data["capital_gains_short_term"])
# #     )
# #     aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

# #     # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
# #     # This prevents double counting if EPF is reported separately and also included in 80C
# #     # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
# #     # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
# #     # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
# #     if safe_float(aggregated_data["epf_contribution"]) > 0:
# #         aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
# #     # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
# #     aggregated_data["total_deductions_chapter_via"] = (
# #         safe_float(aggregated_data["deduction_80c"]) +
# #         safe_float(aggregated_data["deduction_80ccc"]) +
# #         safe_float(aggregated_data["deduction_80ccd"]) +
# #         safe_float(aggregated_data["deduction_80ccd1b"]) +
# #         safe_float(aggregated_data["deduction_80d"]) +
# #         safe_float(aggregated_data["deduction_80g"]) +
# #         safe_float(aggregated_data["deduction_80tta"]) +
# #         safe_float(aggregated_data["deduction_80ttb"]) +
# #         safe_float(aggregated_data["deduction_80e"])
# #     )
# #     aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


# #     # Aliases for frontend (ensure these are correctly populated from derived values)
# #     aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
# #     # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
# #     # This is a fallback and might not always reflect actual exemptions as per tax rules.
# #     if aggregated_data["total_exempt_allowances"] == 0.0:
# #         aggregated_data["total_exempt_allowances"] = (
# #             safe_float(aggregated_data.get("conveyance_allowance")) +
# #             safe_float(aggregated_data.get("transport_allowance")) +
# #             safe_float(aggregated_data.get("hra_received")) 
# #         )
# #         logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

# #     # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
# #     # This is a fixed amount applied during tax calculation, not a sum from documents.
# #     aggregated_data["standard_deduction"] = 50000.0 

# #     # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
# #     dob_str = safe_string(aggregated_data.get("date_of_birth"))
# #     if dob_str != "null" and dob_str != "0000-01-01":
# #         try:
# #             dob = datetime.strptime(dob_str, '%Y-%m-%d')
# #             today = datetime.now()
# #             age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
# #             aggregated_data["Age"] = age
# #         except ValueError:
# #             logging.warning(f"Could not parse date_of_birth: {dob_str}")
# #             aggregated_data["Age"] = "N/A"
# #     else:
# #         aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

# #     # Populate aliases for frontend display consistency
# #     aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
# #     aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
# #     aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
# #     aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
# #     aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
# #     aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
# #     aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
# #     aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
# #     aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

# #     # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
# #     # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
# #     # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
# #     # For display, we can show sum of what's *claimed* or *extracted*.
# #     # Let's make `total_deductions` a sum of all potential deductions for display.
# #     aggregated_data["total_deductions"] = (
# #         aggregated_data["standard_deduction"] + 
# #         aggregated_data["professional_tax"] +
# #         aggregated_data["interest_on_housing_loan_self_occupied"] +
# #         aggregated_data["total_deductions_chapter_via"]
# #     )
# #     aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


# #     # Sort all_transactions by date (oldest first)
# #     for tx in aggregated_data['transaction_summary']:
# #         if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
# #             try:
# #                 tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
# #             except ValueError:
# #                 tx['date_sortable'] = datetime.min # Fallback for unparseable dates
# #         else:
# #             tx['date_sortable'] = datetime.min

# #     aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
# #     # Remove the temporary sortable key
# #     for tx in aggregated_data['transaction_summary']:
# #         tx.pop('date_sortable', None)

# #     # If identified_type is still "null" or "Unknown" and some other fields populated,
# #     # try to infer a better type if possible, or leave as "Other Document"
# #     if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
# #         if safe_string(aggregated_data.get('employer_name')) != "null" and \
# #            safe_float(aggregated_data.get('gross_salary_total')) > 0:
# #            aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
# #         elif safe_string(aggregated_data.get('account_number')) != "null" and \
# #              (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
# #              aggregated_data["identified_type"] = "Bank Statement"
# #         elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
# #              safe_float(aggregated_data.get('hra_received')) > 0 or \
# #              safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
# #              aggregated_data["identified_type"] = "Salary Slip"

# #     # Ensure PAN and Financial Year are properly set for database grouping
# #     # If not extracted, try to get from previous records or default to "null"
# #     if safe_string(aggregated_data.get("pan_of_employee")) == "null":
# #         aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

# #     # Derive financial year from assessment year if financial_year is null
# #     if safe_string(aggregated_data.get("financial_year")) == "null" and safe_string(aggregated_data.get("assessment_year")) != "null":
# #         try:
# #             ay_parts = safe_string(aggregated_data["assessment_year"]).split('-')
# #             if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
# #                 start_year = int(ay_parts[0]) -1
# #                 end_year = int(ay_parts[0])
# #                 aggregated_data["financial_year"] = f"{start_year}-{str(end_year)[-2:]}"
# #         except Exception:
# #             logging.warning(f"Could not derive financial year from assessment year: {aggregated_data.get('assessment_year')}")
# #             aggregated_data["financial_year"] = "UNKNOWNFY"
# #     elif safe_string(aggregated_data.get("financial_year")) == "null":
# #         aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
# #     logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
# #     return aggregated_data

# # def calculate_final_tax_summary(aggregated_data):
# #     """
# #     Calculates the estimated tax payable and refund status based on aggregated financial data.
# #     This function implements a SIMPLIFIED Indian income tax calculation for demonstration.
# #     !!! IMPORTANT: This must be replaced with actual, up-to-date, and comprehensive
# #     Indian income tax laws, considering both Old and New regimes, age groups,
# #     surcharges, cess, etc., for a production system. !!!

# #     Args:
# #         aggregated_data (dict): A dictionary containing aggregated financial fields.

# #     Returns:
# #         dict: A dictionary with computed tax liability, refund/due status, and notes.
# #     """
    
# #     # If the document type is a Bank Statement, skip tax calculation
# #     if aggregated_data.get('identified_type') == 'Bank Statement':
# #         return {
# #             "calculated_gross_income": 0.0,
# #             "calculated_total_deductions": 0.0,
# #             "computed_taxable_income": 0.0,
# #             "estimated_tax_payable": 0.0,
# #             "total_tds_credit": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "predicted_tax_regime": "N/A",
# #             "notes": ["Tax computation is not applicable for Bank Statements. Please upload tax-related documents like Form 16 or Salary Slips for tax calculation."],
# #             "old_regime_tax_payable": 0.0,
# #             "new_regime_tax_payable": 0.0,
# #             "calculation_details": ["Tax computation is not applicable for Bank Statements."],
# #             "regime_considered": "N/A"
# #         }

# #     # Safely extract and convert relevant values from aggregated_data
# #     gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
# #     # Deductions used for tax calculation (subject to limits and regime)
# #     total_chapter_via_deductions = safe_float(aggregated_data.get("total_deductions_chapter_via", 0)) 
# #     professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
# #     standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 0)) # Ensure standard deduction is fetched
# #     interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))

# #     # Sum all TDS and advance tax for comparison
# #     total_tds_credit = (
# #         safe_float(aggregated_data.get("total_tds", 0)) + 
# #         safe_float(aggregated_data.get("advance_tax", 0)) + 
# #         safe_float(aggregated_data.get("self_assessment_tax", 0))
# #     )

# #     tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
# #     age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
# #     if age == "N/A":
# #         age_group = "General"
# #     elif age < 60:
# #         age_group = "General"
# #     elif age >= 60 and age < 80:
# #         age_group = "Senior Citizen"
# #     else: # age >= 80
# #         age_group = "Super Senior Citizen"

# #     # --- Calculation Details List (for frontend display) ---
# #     calculation_details = []

# #     # --- Check for insufficient data for tax computation ---
# #     if gross_total_income < 100.0 and total_chapter_via_deductions < 100.0 and total_tds_credit < 100.0:
# #         calculation_details.append("Insufficient data provided for comprehensive tax calculation. Please upload documents with income and deduction details.")
# #         return {
# #             "calculated_gross_income": gross_total_income,
# #             "calculated_total_deductions": 0.0, # No significant deductions processed yet
# #             "computed_taxable_income": 0.0,
# #             "estimated_tax_payable": 0.0,
# #             "total_tds_credit": total_tds_credit,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "predicted_tax_regime": "N/A",
# #             "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
# #             "old_regime_tax_payable": 0.0,
# #             "new_regime_tax_payable": 0.0,
# #             "calculation_details": calculation_details,
# #             "regime_considered": "N/A"
# #         }

# #     calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

# #     # --- Old Tax Regime Calculation ---
# #     # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
# #     # Chapter VI-A deductions are capped at their respective limits or overall 1.5L for 80C, etc.
# #     # For simplicity, we'll use the extracted `total_deductions_chapter_via` but it should ideally be capped.
# #     # The actual tax deduction limits should be applied here.
    
# #     # Cap 80C related deductions at 1.5 Lakhs
# #     deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
# #     # Cap 80D (Health Insurance) - simplified max 25k for general, 50k for senior parent (adjust as per actual rules)
# #     deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0) 
# #     # Cap Housing Loan Interest for self-occupied at 2 Lakhs
# #     interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

# #     # Simplified Chapter VI-A deductions for old regime (summing specific 80C, 80D, 80CCD1B, 80E, 80G, 80TTA, 80TTB)
# #     total_chapter_via_deductions_old_regime = (
# #         deduction_80c_actual +
# #         safe_float(aggregated_data.get("deduction_80ccc", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ccd", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ccd1b", 0)) +
# #         safe_float(aggregated_data.get("deduction_80d", 0)) + # Corrected to use deduction_80d_actual later if needed
# #         safe_float(aggregated_data.get("deduction_80g", 0)) +
# #         safe_float(aggregated_data.get("deduction_80tta", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ttb", 0)) +
# #         safe_float(aggregated_data.get("deduction_80e", 0))
# #     )
# #     total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)


# #     # Total deductions for Old Regime
# #     total_deductions_old_regime_for_calc = (
# #         standard_deduction_applied + 
# #         professional_tax + 
# #         interest_on_housing_loan_actual + 
# #         total_chapter_via_deductions_old_regime
# #     )
# #     total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

# #     taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
# #     tax_before_cess_old_regime = 0

# #     calculation_details.append(f"2. Deductions under Old Regime:")
# #     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
# #     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
# #     calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
# #     calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
# #     calculation_details.append(f"   - Section 80D (capped at ₹25,000/₹50,000): ₹{deduction_80d_actual:,.2f}")
# #     calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual):,.2f}")
# #     calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
# #     calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

# #     # Old Regime Tax Slabs (simplified for AY 2024-25)
# #     if age_group == "General":
# #         if taxable_income_old_regime <= 250000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
# #     elif age_group == "Senior Citizen": # 60 to < 80
# #         if taxable_income_old_regime <= 300000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 300000) * 0.05
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
# #     else: # Super Senior Citizen >= 80
# #         if taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

# #     rebate_87a_old_regime = 0
# #     if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
# #         rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
# #     tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
# #     total_tax_old_regime = round(tax_after_rebate_old_regime * 1.04, 2) # Add 4% Health and Education Cess
# #     calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
# #     calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
# #     calculation_details.append(f"6. Tax after Rebate (Old Regime): ₹{tax_after_rebate_old_regime:,.2f}")
# #     calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


# #     # --- New Tax Regime Calculation ---
# #     # From AY 2024-25, standard deduction is also applicable in the New Regime for salaried individuals.
# #     # Most Chapter VI-A deductions are *not* allowed in the New Regime, except employer's NPS contribution u/s 80CCD(2).
# #     # For simplicity, we assume only standard deduction and professional tax are applicable.
# #     # Also, housing loan interest deduction is NOT allowed for self-occupied property in New Regime.

# #     taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
# #     # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
# #     tax_before_cess_new_regime = 0

# #     calculation_details.append(f"8. Deductions under New Regime:")
# #     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
# #     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
# #     calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") # Only allowed ones
# #     calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


# #     # New Regime Tax Slabs (simplified for AY 2024-25 onwards)
# #     if taxable_income_new_regime <= 300000:
# #         tax_before_cess_new_regime = 0
# #     elif taxable_income_new_regime <= 600000:
# #         tax_before_cess_new_regime = (taxable_income_new_regime - 300000) * 0.05
# #     elif taxable_income_new_regime <= 900000:
# #         tax_before_cess_new_regime = 15000 + (taxable_income_new_regime - 600000) * 0.10
# #     elif taxable_income_new_regime <= 1200000:
# #         tax_before_cess_new_regime = 45000 + (taxable_income_new_regime - 900000) * 0.15
# #     elif taxable_income_new_regime <= 1500000:
# #         tax_before_cess_new_regime = 90000 + (taxable_income_new_regime - 1200000) * 0.20
# #     else:
# #         tax_before_cess_new_regime = 150000 + (taxable_income_new_regime - 1500000) * 0.30

# #     rebate_87a_new_regime = 0
# #     if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs
# #         rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
# #     tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
# #     total_tax_new_regime = round(tax_after_rebate_new_regime * 1.04, 2) # Add 4% Health and Education Cess
# #     calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
# #     calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
# #     calculation_details.append(f"12. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


# #     # --- Determine Optimal Regime and Final Summary ---
# #     final_tax_regime_applied = "N/A"
# #     estimated_tax_payable = 0.0
# #     computed_taxable_income = 0.0
# #     computation_notes = []

# #     # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
# #     if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
# #         estimated_tax_payable = total_tax_new_regime
# #         computed_taxable_income = taxable_income_new_regime
# #         final_tax_regime_applied = "New Regime (Chosen by User from Document)"
# #         computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
# #     elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
# #         estimated_tax_payable = total_tax_old_regime
# #         computed_taxable_income = taxable_income_old_regime
# #         final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
# #         computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
# #     else: # If no regime is explicitly chosen in documents, recommend the optimal one
# #         if total_tax_old_regime <= total_tax_new_regime:
# #             estimated_tax_payable = total_tax_old_regime
# #             computed_taxable_income = taxable_income_old_regime
# #             final_tax_regime_applied = "Old Regime (Optimal)"
# #             computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
# #         else:
# #             estimated_tax_payable = total_tax_new_regime
# #             computed_taxable_income = taxable_income_new_regime
# #             final_tax_regime_applied = "New Regime (Optimal)"
# #             computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

# #     estimated_tax_payable = round(estimated_tax_payable, 2)
# #     computed_taxable_income = round(computed_taxable_income, 2)

# #     # --- Calculate Refund/Tax Due ---
# #     refund_due_from_tax = 0.0
# #     tax_due_to_government = 0.0

# #     calculation_details.append(f"13. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
# #     if total_tds_credit > estimated_tax_payable:
# #         refund_due_from_tax = total_tds_credit - estimated_tax_payable
# #         calculation_details.append(f"14. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
# #     elif total_tds_credit < estimated_tax_payable:
# #         tax_due_to_government = estimated_tax_payable - total_tds_credit
# #         calculation_details.append(f"14. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
# #     else:
# #         calculation_details.append("14. No Refund or Additional Tax Due.")


# #     return {
# #         "calculated_gross_income": gross_total_income,
# #         "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
# #         "computed_taxable_income": computed_taxable_income,
# #         "estimated_tax_payable": estimated_tax_payable,
# #         "total_tds_credit": total_tds_credit,
# #         "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
# #         "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
# #         "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
# #         "notes": computation_notes, # List of notes
# #         "old_regime_tax_payable": total_tax_old_regime,
# #         "new_regime_tax_payable": total_tax_new_regime,
# #         "calculation_details": calculation_details,
# #         "regime_considered": final_tax_regime_applied # For clarity in the UI
# #     }

# # def generate_ml_prediction_summary(financial_data):
# #     """
# #     Generates ML model prediction summary using the loaded models.
# #     """
# #     if tax_regime_classifier_model is None or tax_regressor_model is None:
# #         logging.warning("ML models are not loaded. Cannot generate ML predictions.")
# #         return {
# #             "predicted_tax_regime": "N/A",
# #             "predicted_tax_liability": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "notes": "ML prediction service unavailable (models not loaded or training failed)."
# #         }
    
# #     # If the aggregated data is primarily from a bank statement, ML prediction for tax is not relevant
# #     if financial_data.get('identified_type') == 'Bank Statement' and financial_data.get('total_gross_income', 0.0) < 100.0:
# #         return {
# #             "predicted_tax_regime": "N/A",
# #             "predicted_tax_liability": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "notes": "ML prediction not applicable for bank statements. Please upload tax-related documents."
# #         }

# #     # Define the features expected by the ML models (must match model_trainer.py)
# #     # IMPORTANT: These must precisely match the features used in model_trainer.py
# #     # Re-verify against your `model_trainer.py` to ensure exact match.
# #     ml_common_numerical_features = [
# #         'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
# #         'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
# #         'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
# #         'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
# #         'Total Exempt Allowances Claimed'
# #     ]
# #     ml_categorical_features = ['Residential Status', 'Gender']
    
# #     # Prepare input for classifier model
# #     age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
# #     # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
# #     # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
# #     # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
# #     calculated_other_deductions = (
# #         safe_float(financial_data.get('deduction_80ccc', 0)) +
# #         safe_float(financial_data.get('deduction_80ccd', 0)) +
# #         safe_float(financial_data.get('deduction_80ccd1b', 0)) +
# #         safe_float(financial_data.get('deduction_80g', 0)) +
# #         safe_float(financial_data.get('deduction_80tta', 0)) +
# #         safe_float(financial_data.get('deduction_80ttb', 0))
# #     )
# #     calculated_other_deductions = round(calculated_other_deductions, 2)


# #     classifier_input_data = {
# #         'Age': age_value,
# #         'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
# #         'HRA Received': safe_float(financial_data.get('hra_received', 0)),
# #         'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
# #         'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
# #         'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
# #         'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
# #         'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
# #         'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
# #         'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
# #         'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
# #         'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
# #         'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
# #         'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
# #         'Gender': safe_string(financial_data.get('gender', 'Unknown'))
# #     }
    
# #     # Create DataFrame for classifier prediction, ensuring column order
# #     # The order must match `model_trainer.py`'s `classifier_all_features`
# #     ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
# #     classifier_df = pd.DataFrame([classifier_input_data])
    
# #     predicted_tax_regime = "N/A"
# #     try:
# #         classifier_df_processed = classifier_df[ordered_classifier_features]
# #         predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
# #         logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
# #     except Exception as e:
# #         logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
# #         predicted_tax_regime = "Prediction Failed (Error)"
        
# #     # Prepare input for regressor model
# #     # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
# #     regressor_input_data = {
# #         k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
# #     }
# #     regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

# #     regressor_df = pd.DataFrame([regressor_input_data])
    
# #     predicted_tax_liability = 0.0
# #     try:
# #         # The regressor's preprocessor will handle the categorical feature conversion.
# #         # Just ensure the input DataFrame has the correct columns and order.
# #         ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
# #         regressor_df_processed = regressor_df[ordered_regressor_features]
# #         predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
# #         logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
# #     except Exception as e:
# #         logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
# #         predicted_tax_liability = 0.0 # Default to 0 if prediction fails

# #     # Calculate refund/additional due based on ML prediction and actual TDS
# #     total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

# #     predicted_refund_due = 0.0
# #     predicted_additional_due = 0.0

# #     if total_tds_credit > predicted_tax_liability:
# #         predicted_refund_due = total_tds_credit - predicted_tax_liability
# #     elif total_tds_credit < predicted_tax_liability:
# #         predicted_additional_due = predicted_tax_liability - total_tds_credit
        
# #     # Convert any numpy types before returning
# #     return convert_numpy_types({
# #         "predicted_tax_regime": predicted_tax_regime,
# #         "predicted_tax_liability": predicted_tax_liability,
# #         "predicted_refund_due": round(predicted_refund_due, 2),
# #         "predicted_additional_due": round(predicted_additional_due, 2),
# #         "notes": "ML model predictions for optimal regime and tax liability."
# #     })

# # def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
# #     """Generates tax-saving suggestions and regime analysis using Gemini API."""
# #     if gemini_model is None:
# #         logging.error("Gemini API (gemini_model) not initialized.")
# #         return ["AI suggestions unavailable."], "AI regime analysis unavailable."

# #     # If the document type is a Bank Statement, provide a generic suggestion
# #     if aggregated_financial_data.get('identified_type') == 'Bank Statement' or \
# #        ("Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]):
# #         return (
# #             ["For comprehensive tax analysis and personalized tax-saving suggestions, please upload tax-related documents such as Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts). Bank statements are primarily for transactional summaries."],
# #             "Tax regime analysis requires complete income and deduction data, typically found in tax-specific documents."
# #         )


# #     # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
# #     financial_data_for_gemini = aggregated_financial_data.copy()

# #     # Add specific structure for Bank Statement details if identified as such, or if bank details are present
# #     if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
# #         financial_data_for_gemini['Bank Details'] = {
# #             'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
# #             'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
# #             'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
# #             'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
# #             'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
# #             'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
# #             'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
# #             'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
# #         }
# #         # Optionally, remove transaction_summary if it's too verbose for the prompt
# #         # financial_data_for_gemini.pop('transaction_summary', None)


# #     prompt = f"""
# #     You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
# #     Based on this data:
# #     1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
# #     2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

# #     **Financial Data Summary:**
# #     {json.dumps(financial_data_for_gemini, indent=2)}

# #     **Final Tax Computation Summary:**
# #     {json.dumps(final_tax_computation_summary, indent=2)}

# #     Please format your response strictly as follows:
# #     Suggestions:
# #     - [Suggestion 1]
# #     - [Suggestion 2]
# #     ...
# #     Regime Analysis: [Your analysis paragraph here].
# #     """
# #     try:
# #         response = gemini_model.generate_content(prompt)
# #         text = response.text.strip()
        
# #         suggestions = []
# #         regime_analysis = ""

# #         # Attempt to parse the structured output
# #         if "Suggestions:" in text and "Regime Analysis:" in text:
# #             parts = text.split("Regime Analysis:")
# #             suggestions_part = parts[0].replace("Suggestions:", "").strip()
# #             regime_analysis = parts[1].strip()

# #             # Split suggestions into bullet points and filter out empty strings
# #             suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
# #             if not suggestions: # If parsing as bullets failed, treat as single suggestion
# #                 suggestions = [suggestions_part]
# #         else:
# #             # Fallback if format is not as expected, return raw text as suggestions
# #             suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
# #             regime_analysis = "AI could not parse structured regime analysis."
# #             logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

# #         return suggestions, regime_analysis
# #     except Exception as e:
# #         logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
# #         return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

# # def generate_itr_pdf(tax_record_data):
# #     """
# #     Generates a dummy ITR form PDF.
# #     This uses a basic PDF string structure as a placeholder.
# #     """
# #     aggregated_data = tax_record_data.get('aggregated_financial_data', {})
# #     final_computation = tax_record_data.get('final_tax_computation_summary', {})

# #     # Determine ITR type (simplified logic)
# #     itr_type = "ITR-1 (SAHAJ - DUMMY)"
# #     if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
# #        safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
# #        safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
# #         itr_type = "ITR-2 (DUMMY)"
    
# #     # Extract key info for the dummy PDF
# #     name = aggregated_data.get('name_of_employee', 'N/A')
# #     pan = aggregated_data.get('pan_of_employee', 'N/A')
# #     financial_year = aggregated_data.get('financial_year', 'N/A')
# #     assessment_year = aggregated_data.get('assessment_year', 'N/A')
# #     total_income = final_computation.get('computed_taxable_income', 'N/A')
# #     tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
# #     refund_due = final_computation.get('predicted_refund_due', 0.0)
# #     tax_due = final_computation.get('predicted_additional_due', 0.0)
# #     regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

# #     # Add bank statement specific details to the PDF content if available
# #     bank_details_for_pdf = ""
# #     # Check if the aggregated data's identified type is 'Bank Statement' or if it contains core bank details
# #     if aggregated_data.get('identified_type') == 'Bank Statement' or \
# #        (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
# #         bank_details_for_pdf = f"""
# # BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
# # BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
# # """

# #     # Core PDF content without xref and EOF for length calculation
# #     core_pdf_content_lines = [
# #         f"%PDF-1.4",
# #         f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
# #         f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
# #         f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
# #         f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
# #         f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
# #         f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
# #         f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
# #         f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
# #         f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
# #         f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
# #         f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
# #         f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
# #         f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
# #         f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
# #     ]
    
# #     # Append bank details if available
# #     if bank_details_for_pdf:
# #         core_pdf_content_lines.append(bank_details_for_pdf)
# #         # Adjust vertical position for the Note if bank details were added
# #         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
# #     else:
# #         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

# #     core_pdf_content_lines.extend([
# #         f"endstream",
# #         f"endobj",
# #         f"xref",
# #         f"0 5",
# #         f"0000000000 65535 f",
# #         f"0000000010 00000 n",
# #         f"0000000057 00000 n",
# #         f"0000000114 00000 n",
# #         f"0000000222 00000 n",
# #         f"trailer <</Size 5 /Root 1 0 R>>",
# #     ])
    
# #     # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
# #     core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
# #     core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

# #     # Calculate the startxref position
# #     startxref_position = len(core_pdf_bytes)

# #     # Now assemble the full PDF content including startxref and EOF
# #     full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
# #     # Final encode
# #     dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

# #     return io.BytesIO(dummy_pdf_content_bytes), itr_type


# # # --- API Routes ---

# # # Serves the main page (assuming index.html is in the root)
# # @app.route('/')
# # def home():
# #     """Serves the main landing page, typically index.html."""
# #     return send_from_directory('.', 'index.html')

# # # Serves other static files (CSS, JS, images, etc.)
# # @app.route('/<path:path>')
# # def serve_static_files(path):
# #     """Serves static files from the root directory."""
# #     return send_from_directory('.', path)

# # # Serves uploaded files from the uploads folder
# # @app.route('/uploads/<filename>')
# # def uploaded_file(filename):
# #     """Allows access to temporarily stored uploaded files."""
# #     try:
# #         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# #     except FileNotFoundError:
# #         logging.warning(f"File '{filename}' not found in uploads folder.")
# #         return jsonify({"message": "File not found"}), 404
# #     except Exception as e:
# #         logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


# # @app.route('/api/register', methods=['POST'])
# # def register_user():
# #     """Handles user registration."""
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         email = data.get('email')
# #         password = data.get('password')

# #         if not username or not email or not password:
# #             logging.warning("Registration attempt with missing fields.")
# #             return jsonify({"message": "Username, email, and password are required"}), 400

# #         # Check if email or username already exists
# #         if users_collection.find_one({"email": email}):
# #             logging.warning(f"Registration failed: Email '{email}' already exists.")
# #             return jsonify({"message": "Email already exists"}), 409
# #         if users_collection.find_one({"username": username}):
# #             logging.warning(f"Registration failed: Username '{username}' already exists.")
# #             return jsonify({"message": "Username already exists"}), 409

# #         # Hash the password before storing
# #         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
# #         # Prepare user data for MongoDB insertion
# #         new_user_data = {
# #             "username": username,
# #             "email": email,
# #             "password": hashed_password.decode('utf-8'), # Store hashed password as string
# #             "full_name": data.get('fullName', ''),
# #             "pan": data.get('pan', ''),
# #             "aadhaar": data.get('aadhaar', ''),
# #             "address": data.get('address', ''),
# #             "phone": data.get('phone', ''),
# #             "created_at": datetime.utcnow()
# #         }
# #         # Insert the new user record and get the inserted ID
# #         user_id = users_collection.insert_one(new_user_data).inserted_id
# #         logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
# #         return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
# #     except Exception as e:
# #         logging.error(f"Error during registration: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred during registration."}), 500

# # @app.route('/api/login', methods=['POST'])
# # def login_user():
# #     """Handles user login and JWT token generation."""
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         password = data.get('password')

# #         if not username or not password:
# #             logging.warning("Login attempt with missing credentials.")
# #             return jsonify({"error_msg": "Username and password are required"}), 400

# #         # Find the user by username
# #         user = users_collection.find_one({"username": username})

# #         # Verify user existence and password
# #         if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
# #             # Create a JWT access token with the user's MongoDB ObjectId as identity
# #             access_token = create_access_token(identity=str(user['_id']))
# #             logging.info(f"User '{username}' logged in successfully.")
# #             return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
# #         else:
# #             logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
# #             return jsonify({"error_msg": "Invalid credentials"}), 401
# #     except Exception as e:
# #         logging.error(f"Error during login: {traceback.format_exc()}")
# #         return jsonify({"error_msg": "An error occurred during login."}), 500

# # @app.route('/api/profile', methods=['GET'])
# # @jwt_required()
# # def get_user_profile():
# #     """Fetches the profile of the currently authenticated user."""
# #     try:
# #         # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
# #         current_user_id = get_jwt_identity()
# #         # Find user by ObjectId, exclude password from the result
# #         user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
# #         if not user:
# #             logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
# #             return jsonify({"message": "User not found"}), 404

# #         # Convert ObjectId to string for JSON serialization
# #         user['_id'] = str(user['_id'])
# #         logging.info(f"Profile fetched for user ID: {current_user_id}")
# #         return jsonify({"user": user}), 200
# #     except Exception as e:
# #         logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

# # @app.route('/api/profile', methods=['PUT', 'PATCH'])
# # @jwt_required()
# # def update_user_profile():
# #     """Updates the profile of the currently authenticated user."""
# #     try:
# #         current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #         data = request.get_json()

# #         # Define allowed fields for update
# #         updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
# #         update_data = {k: data[k] for k in updatable_fields if k in data}

# #         if not update_data:
# #             logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
# #             return jsonify({"message": "No fields to update provided."}), 400
        
# #         # Prevent username from being updated via this route for security/simplicity
# #         if 'username' in data:
# #             logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

# #         # If email is being updated, ensure it's not already in use by another user
# #         if 'email' in update_data:
# #             existing_user_with_email = users_collection.find_one({"email": update_data['email']})
# #             if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
# #                 logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
# #                 return jsonify({"message": "Email already in use by another account."}), 409

# #         # Perform the update operation in MongoDB
# #         result = users_collection.update_one(
# #             {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
# #             {"$set": update_data}
# #         )

# #         if result.matched_count == 0:
# #             logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
# #             return jsonify({"message": "User not found."}), 404
# #         if result.modified_count == 0:
# #             logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
# #             return jsonify({"message": "Profile data is the same, no changes made."}), 200

# #         logging.info(f"Profile updated successfully for user ID: {current_user_id}")
# #         return jsonify({"message": "Profile updated successfully!"}), 200
# #     except Exception as e:
# #         logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred while updating your profile."}), 500


# # @app.route('/api/process_documents', methods=['POST'])
# # @jwt_required()
# # def process_documents():
# #     """
# #     Handles uploaded documents, extracts financial data using Gemini and Vision API,
# #     aggregates data from multiple files, computes tax, and saves the comprehensive
# #     record to MongoDB, grouped by PAN and Financial Year.
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

# #     if 'documents' not in request.files:
# #         logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
# #         return jsonify({"message": "No 'documents' part in the request"}), 400

# #     files = request.files.getlist('documents')
# #     if not files:
# #         logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
# #         return jsonify({"message": "No selected file"}), 400

# #     extracted_data_from_current_upload = []
# #     document_processing_summary_current_upload = [] # To provide feedback on each file

# #     # Get the selected document type hint from the form data (if provided)
# #     document_type_hint = request.form.get('document_type', 'Auto-Detect') 
# #     logging.info(f"Received document type hint from frontend: {document_type_hint}")

# #     for file in files:
# #         if file.filename == '':
# #             document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
# #             continue
        
# #         filename = secure_filename(file.filename)
# #         # Create a unique filename for storing the original document
# #         unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        
# #         # --- FIX STARTS HERE ---
# #         # Ensure UPLOAD_FOLDER is part of app.config
# #         if 'UPLOAD_FOLDER' not in app.config:
# #             app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Use the globally defined UPLOAD_FOLDER
# #             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Ensure it exists
# #         # --- FIX ENDS HERE ---
        
# #         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
# #         try:
# #             file_content_bytes = file.read() # Read content before saving
# #             file.seek(0) # Reset file pointer for subsequent operations if needed

# #             # Save the file temporarily (or permanently if you wish to retain originals)
# #             with open(file_path, 'wb') as f:
# #                 f.write(file_content_bytes)
# #             logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

# #             mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default

# #             # Construct the base prompt for Gemini
# #             base_prompt_instructions = (
# #                 f"You are an expert financial data extractor and tax document analyzer for Indian context. "
# #                 f"Analyze the provided document (filename: '{filename}', MIME type: {mime_type}). "
# #                 f"The user has indicated this document is of type: '{document_type_hint}'. " 
# #                 "Extract ALL relevant financial information for Indian income tax filing. "
# #                 "Your response MUST be a JSON object conforming precisely to the provided schema. "
# #                 "For numerical fields, if a value is not explicitly found or is clearly zero, you MUST use `0.0`. "
# #                 "For string fields (like names, PAN, year, dates, identified_type, gender, residential_status), if a value is not explicitly found, you MUST use the string `null`. "
# #                 "For dates, if found, use 'YYYY-MM-DD' format if possible; otherwise, `0000-01-01` if not found or cannot be parsed.\n\n"
# #             )

# #             # Add specific instructions based on document type hint
# #             if document_type_hint == 'Bank Statement':
# #                 base_prompt_instructions += (
# #                     "Specifically for a Bank Statement, extract the following details accurately:\n"
# #                     "- Account Holder Name\n- Account Number\n- IFSC Code (if present)\n- Bank Name\n"
# #                     "- Branch Address\n- Statement Start Date (YYYY-MM-DD)\n- Statement End Date (YYYY-MM-DD)\n"
# #                     "- Opening Balance\n- Closing Balance\n- Total Deposits\n- Total Withdrawals\n"
# #                     "- A summary of key transactions, including date (YYYY-MM-DD), description, and amount. Prioritize large transactions or those with specific identifiable descriptions (e.g., 'salary', 'rent', 'interest').\n"
# #                     "If a field is not found or not applicable, use `null` for strings and `0.0` for numbers. Ensure dates are in YYYY-MM-DD format."
# #                 )
# #             elif document_type_hint == 'Form 16':
# #                 base_prompt_instructions += (
# #                     "Specifically for Form 16, extract details related to employer, employee, PAN, TAN, financial year, assessment year, "
# #                     "salary components (basic, HRA, perquisites, profits in lieu of salary), exempt allowances, professional tax, "
# #                     "income from house property, income from other sources, capital gains, "
# #                     "deductions under Chapter VI-A (80C, 80D, 80G, 80E, 80CCD, etc.), TDS details (total, quarter-wise), "
# #                     "and any mentioned tax regime (Old/New). Ensure all monetary values are extracted as numbers."
# #                 )
# #             elif document_type_hint == 'Salary Slip':
# #                 base_prompt_instructions += (
# #                     "Specifically for a Salary Slip, extract employee name, PAN, employer name, basic salary, HRA, "
# #                     "conveyance allowance, transport allowance, overtime pay, EPF contribution, ESI contribution, "
# #                     "professional tax, net amount payable, days present, and overtime hours. Ensure all monetary values are extracted as numbers."
# #                 )
# #             # Add more elif blocks for other specific document types if needed

# #             error_gemini, extracted_data = extract_fields_with_gemini(base_prompt_instructions, document_type_hint)

# #             if error_gemini:
# #                 document_processing_summary_current_upload.append({
# #                     "filename": filename, "status": "failed", "message": f"AI processing error: {error_gemini['error']}",
# #                     "stored_path": f"/uploads/{unique_filename}"
# #                 })
# #                 continue
            
# #             # Add the path to the stored document for future reference in history
# #             extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
# #             extracted_data_from_current_upload.append(extracted_data)

# #             document_processing_summary_current_upload.append({
# #                 "filename": filename, "status": "success", "identified_type": extracted_data.get('identified_type', 'Unknown'),
# #                 "message": "Processed successfully.", "extracted_fields": extracted_data,
# #                 "stored_path": f"/uploads/{unique_filename}" 
# #             })

# #         except Exception as e:
# #             logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
# #             document_processing_summary_current_upload.append({
# #                 "filename": filename, "status": "error",
# #                 "message": f"An unexpected error occurred during file processing: {str(e)}",
# #                 "stored_path": f"/uploads/{unique_filename}"
# #             })
# #             continue 

# #     if not extracted_data_from_current_upload:
# #         logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
# #         return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

# #     # --- Determine PAN and Financial Year for grouping ---
# #     # Try to find PAN and FY from the currently uploaded documents first
# #     pan_of_employee = "UNKNOWNPAN"
# #     financial_year = "UNKNOWNFY"

# #     for data in extracted_data_from_current_upload:
# #         if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
# #             pan_of_employee = safe_string(data["pan_of_employee"])
# #         if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
# #             financial_year = safe_string(data["financial_year"])
# #         # If both are found, we can break early (or continue to see if a higher priority doc has them)
# #         if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
# #             break
    
# #     # If still unknown, check if the user profile has a PAN.
# #     if pan_of_employee == "UNKNOWNPAN":
# #         user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
# #         if user_profile and safe_string(user_profile.get("pan")) != "null":
# #             pan_of_employee = safe_string(user_profile["pan"])
# #             logging.info(f"Using PAN from user profile: {pan_of_employee}")
# #         else:
# #             # If PAN is still unknown, log a warning and use the placeholder
# #             logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

# #     # Derive financial year from assessment year if financial_year is null
# #     if financial_year == "UNKNOWNFY":
# #         for data in extracted_data_from_current_upload:
# #             if safe_string(data.get("assessment_year")) != "null":
# #                 try:
# #                     ay_parts = safe_string(data["assessment_year"]).split('-')
# #                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
# #                         start_year = int(ay_parts[0]) -1
# #                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
# #                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
# #                             financial_year = fy
# #                             break
# #                 except Exception:
# #                     pass # Keep default if parsing fails
# #         if financial_year == "UNKNOWNFY":
# #             logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


# #     # Try to find an existing record for this user, PAN, and financial year
# #     existing_tax_record = tax_records_collection.find_one({
# #         "user_id": current_user_id,
# #         "aggregated_financial_data.pan_of_employee": pan_of_employee,
# #         "aggregated_financial_data.financial_year": financial_year
# #     })

# #     if existing_tax_record:
# #         logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
# #         # Merge new extracted data with existing data
# #         all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
# #         all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

# #         # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
# #         updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
# #         updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

# #         # Clear previous AI/ML results as they need to be re-generated for the updated data
# #         tax_records_collection.update_one(
# #             {"_id": existing_tax_record["_id"]},
# #             {"$set": {
# #                 "extracted_documents_data": all_extracted_data_for_fy,
# #                 "document_processing_summary": all_document_processing_summary_for_fy,
# #                 "aggregated_financial_data": updated_aggregated_financial_data,
# #                 "final_tax_computation_summary": updated_final_tax_computation_summary,
# #                 "timestamp": datetime.utcnow(), # Update timestamp of last modification
# #                 "suggestions_from_gemini": [], # Reset suggestions
# #                 "gemini_regime_analysis": "null", # Reset regime analysis
# #                 "ml_prediction_summary": {}, # Reset ML predictions
# #             }}
# #         )
# #         record_id = existing_tax_record["_id"]
# #         logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

# #     else:
# #         logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
# #         # If no existing record, aggregate only the newly uploaded data
# #         new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
# #         new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

# #         # Prepare the comprehensive tax record to save to MongoDB
# #         tax_record_to_save = {
# #             "user_id": current_user_id, 
# #             "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
# #             "financial_year": financial_year, # Store FY at top level for easy query
# #             "timestamp": datetime.utcnow(),
# #             "document_processing_summary": document_processing_summary_current_upload, 
# #             "extracted_documents_data": extracted_data_from_current_upload, 
# #             "aggregated_financial_data": new_aggregated_financial_data,
# #             "final_tax_computation_summary": new_final_tax_computation_summary,
# #             "suggestions_from_gemini": [], 
# #             "gemini_regime_analysis": "null", 
# #             "ml_prediction_summary": {},    
# #         }
# #         record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
# #         logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
# #         updated_aggregated_financial_data = new_aggregated_financial_data
# #         updated_final_tax_computation_summary = new_final_tax_computation_summary


# #     # Return success response with computed data
# #     # Ensure all data sent back is JSON serializable (e.g., no numpy types)
# #     response_data = {
# #         "status": "success",
# #         "message": "Documents processed and financial data aggregated and tax computed successfully",
# #         "record_id": str(record_id), 
# #         "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
# #         "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
# #         "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
# #     }
# #     return jsonify(response_data), 200


# # @app.route('/api/get_suggestions', methods=['POST'])
# # @jwt_required()
# # def get_suggestions():
# #     """
# #     Generates AI-driven tax-saving suggestions and provides an ML prediction summary
# #     based on a specific processed tax record (grouped by PAN/FY).
# #     """
# #     current_user_id = get_jwt_identity()

# #     data = request.get_json()
# #     record_id = data.get('record_id')

# #     if not record_id:
# #         logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
# #         return jsonify({"message": "Record ID is required to get suggestions."}), 400

# #     try:
# #         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
# #         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
# #         if not tax_record:
# #             logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
# #             return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
# #         # Get the aggregated financial data and final tax computation summary from the record
# #         aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
# #         final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

# #         # Generate suggestions and ML predictions
# #         suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
# #         ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

# #         # Update the record in DB with generated suggestions and predictions
# #         tax_records_collection.update_one(
# #             {"_id": ObjectId(record_id)},
# #             {"$set": {
# #                 "suggestions_from_gemini": suggestions,
# #                 "gemini_regime_analysis": regime_analysis,
# #                 "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
# #                 "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
# #             }}
# #         )
# #         logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

# #         return jsonify({
# #             "status": "success",
# #             "message": "AI suggestions and ML predictions generated successfully!",
# #             "suggestions_from_gemini": suggestions,
# #             "gemini_regime_analysis": regime_analysis,
# #             "ml_prediction_summary": ml_prediction_summary # Already converted
# #         }), 200

# #     except Exception as e:
# #         logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
# #         # Fallback for ML prediction summary even if overall suggestions fail
# #         ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
# #         return jsonify({
# #             "status": "error",
# #             "message": "An error occurred while generating suggestions.",
# #             "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
# #             "gemini_regime_analysis": "An error occurred.",
# #             "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
# #         }), 500

# # @app.route('/api/save_extracted_data', methods=['POST'])
# # @jwt_required()
# # def save_extracted_data():
# #     """
# #     Saves extracted and computed tax data to MongoDB.
# #     This route can be used for explicit saving if `process_documents` doesn't
# #     cover all saving scenarios or for intermediate saves.
# #     NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
# #     For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #     data = request.get_json()
# #     if not data:
# #         logging.warning(f"Save data request from user {current_user_id} with no data provided.")
# #         return jsonify({"message": "No data provided to save"}), 400
# #     try:
# #         # This route might be less relevant with the new aggregation by PAN/FY,
# #         # as `process_documents` handles the upsert logic.
# #         # However, if used for manual saving of *already aggregated* data,
# #         # ensure PAN and FY are part of `data.aggregated_financial_data`
# #         # or extracted from the `data` directly.
        
# #         # Example: Try to get PAN and FY from input data for consistency
# #         input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
# #         input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

# #         # Check for existing record for upsert behavior
# #         existing_record = tax_records_collection.find_one({
# #             "user_id": current_user_id,
# #             "aggregated_financial_data.pan_of_employee": input_pan,
# #             "aggregated_financial_data.financial_year": input_fy
# #         })

# #         if existing_record:
# #             # Update existing record
# #             update_result = tax_records_collection.update_one(
# #                 {"_id": existing_record["_id"]},
# #                 {"$set": {
# #                     **data, # Overwrite with new data, ensuring user_id and timestamp are also set
# #                     "user_id": current_user_id,
# #                     "timestamp": datetime.utcnow(),
# #                     "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
# #                     "financial_year": input_fy, # Ensure top-level FY is consistent
# #                 }}
# #             )
# #             record_id = existing_record["_id"]
# #             logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
# #             if update_result.modified_count == 0:
# #                 return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
# #         else:
# #             # Insert new record
# #             data['user_id'] = current_user_id
# #             data['timestamp'] = datetime.utcnow()
# #             data['pan_of_employee'] = input_pan
# #             data['financial_year'] = input_fy
# #             record_id = tax_records_collection.insert_one(data).inserted_id
# #             logging.info(f"New data saved for user {current_user_id} with record ID: {record_id}")
        
# #         return jsonify({"message": "Data saved successfully", "record_id": str(record_id)}), 200
# #     except Exception as e:
# #         logging.error(f"Error saving data for user {current_user_id}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to save data", "error": str(e)}), 500

# # @app.route('/api/tax_history', methods=['GET'])
# # @jwt_required()
# # def get_tax_records():
# #     """
# #     Fetches all aggregated tax records for the logged-in user, grouped by Financial Year.
# #     Records are sorted by timestamp in descending order (most recent first).
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #     logging.info(f"Fetching tax records for user: {current_user_id}")
# #     try:
# #         # Fetch all records for the current user, sorted by financial_year and then by timestamp
# #         # The 'user_id', 'pan_of_employee', and 'financial_year' are top-level fields now
# #         records = list(tax_records_collection.find({"user_id": current_user_id})
# #                         .sort([("financial_year", -1), ("timestamp", -1)]))

# #         # Convert MongoDB ObjectId to string for JSON serialization
# #         for record in records:
# #             record['_id'] = str(record['_id'])
# #             # Ensure 'user_id' is also a string when sending to frontend
# #             if 'user_id' in record:
# #                 record['user_id'] = str(record['user_id'])
# #             # Remove potentially large raw data fields for history list view to save bandwidth
# #             record.pop('extracted_documents_data', None) 
# #         logging.info(f"Found {len(records)} tax records for user {current_user_id}")
# #         # The frontend's TaxHistory component expects a 'history' key in the response data.
# #         return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200 # Convert numpy types
# #     except Exception as e:
# #         logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
# #         return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

# # @app.route('/api/generate-itr/<record_id>', methods=['GET'])
# # @jwt_required()
# # def generate_itr_form_route(record_id):
# #     """
# #     Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
# #     """
# #     current_user_id = get_jwt_identity()
# #     try:
# #         record_obj_id = ObjectId(record_id) # Convert record_id string to ObjectId for DB query
# #         # Ensure the tax record belongs to the current user (user_id check)
# #         tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

# #         if not tax_record:
# #             logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
# #             return jsonify({"message": "Tax record not found or you are not authorized to access it."}), 404

# #         # Generate the dummy PDF content
# #         pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
# #         pdf_buffer.seek(0) # Rewind the buffer to the beginning

# #         response = send_file(
# #             pdf_buffer,
# #             mimetype='application/pdf',
# #             as_attachment=True,
# #             download_name=f"{itr_type.replace(' ', '_')}_{record_id}.pdf"
# #         )
# #         logging.info(f"Generated and sent dummy ITR form for record ID: {record_id}")
# #         return response
# #     except Exception as e:
# #         logging.error(f"Error generating ITR form for record {record_id}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to generate ITR form.", "error": str(e)}), 500

# # @app.route('/api/contact', methods=['POST'])
# # def contact_message():
# #     """Handles contact form submissions."""
# #     try:
# #         data = request.get_json()
# #         name = data.get('name')
# #         email = data.get('email')
# #         subject = data.get('subject')
# #         message = data.get('message')

# #         if not all([name, email, subject, message]):
# #             logging.warning("Contact form submission with missing fields.")
# #             return jsonify({"message": "All fields are required."}), 400
        
# #         # Insert contact message into MongoDB
# #         contact_messages_collection.insert_one({
# #             "name": name,
# #             "email": email,
# #             "subject": subject,
# #             "message": message,
# #             "timestamp": datetime.utcnow()
# #         })
# #         logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

# #         return jsonify({"message": "Message sent successfully!"}), 200
# #     except Exception as e:
# #         logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred while sending your message."}), 500

# # # --- Main application entry point ---
# # if __name__ == '__main__':
# #     # Ensure MongoDB connection is established before running the app
# #     if db is None:
# #         logging.error("MongoDB connection failed at startup. Exiting.")
# #         exit(1)
    
# #     logging.info("Starting Flask application...")
# #     # Run the Flask app
# #     # debug=True enables reloader and debugger (should be False in production)
# #     # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
# #     # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
# #     app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)















# # import os
# # import json
# # from flask import Flask, request, jsonify, send_from_directory, send_file
# # from flask_cors import CORS
# # import google.generativeai as genai
# # from pymongo import MongoClient
# # from bson.objectid import ObjectId
# # import bcrypt
# # import traceback
# # import logging
# # import io
# # from datetime import datetime, timedelta
# # from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# # import base64
# # from google.cloud import vision
# # from google.oauth2 import service_account
# # from werkzeug.utils import secure_filename # Import secure_filename
# # import joblib # Import joblib for loading ML models
# # import pandas as pd # Import pandas for ML model input

# # # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# # import numpy as np

# # # Import ReportLab components for PDF generation
# # try:
# #     # We are using a dummy PDF for now, so ReportLab is not strictly needed for functionality
# #     # but the import block is kept for reference if actual PDF generation is implemented.
# #     from reportlab.pdfgen import canvas
# #     from reportlab.lib.pagesizes import letter
# #     from reportlab.lib.units import inch
# #     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# #     from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
# #     from reportlab.lib.enums import TA_CENTER
# #     REPORTLAB_AVAILABLE = True # Set to True if you install ReportLab
# # except ImportError:
# #     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
# #     REPORTLAB_AVAILABLE = False


# # # Configure logging for better visibility
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # --- Configuration (IMPORTANT: Using hardcoded keys as per user's request) ---
# # # In a real-world production environment, these should ALWAYS be loaded from
# # # environment variables (e.g., using os.getenv) and never hardcoded.
# # GEMINI_API_KEY = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs" # Replace with your actual key or env var
# # MONGO_URI ="mongodb://localhost:27017/"
# # JWT_SECRET_KEY = "super-secret-jwt-key-replace-with-a-strong-one"
# # VISION_API_KEY_PATH = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json" # Path to your GCP service account key file

# # # Initialize Flask app
# # app = Flask(__name__, static_folder='static') # Serve static files from 'static' folder
# # CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# # # Setup Flask-JWT-Extended
# # app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
# # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Token validity
# # jwt = JWTManager(app)

# # # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# # @jwt.expired_token_loader
# # def expired_token_callback(jwt_header, jwt_payload):
# #     logging.warning("JWT token expired.")
# #     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# # @jwt.invalid_token_loader
# # def invalid_token_callback(callback_error):
# #     logging.warning(f"Invalid JWT token: {callback_error}")
# #     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# # @jwt.unauthorized_loader
# # def unauthorized_callback(callback_error):
# #     logging.warning(f"Unauthorized access attempt: {callback_error}")
# #     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401


# # # Initialize MongoDB
# # client = None
# # db = None
# # users_collection = None
# # tax_records_collection = None
# # contact_messages_collection = None
# # try:
# #     client = MongoClient(MONGO_URI)
# #     db = client.garudatax_ai # Your database name
# #     users_collection = db['users']
# #     tax_records_collection = db['tax_records'] # Collection for processed tax documents
# #     contact_messages_collection = db['contact_messages']
# #     logging.info("MongoDB connected successfully.")
# # except Exception as e:
# #     logging.error(f"Could not connect to MongoDB: {e}")
# #     db = None # Set db to None if connection fails

# # # Configure Google Gemini API
# # try:
# #     genai.configure(api_key=GEMINI_API_KEY)
# #     gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Or 'gemini-pro'
# #     logging.info("Google Gemini API configured.")
# # except Exception as e:
# #     logging.error(f"Could not configure Google Gemini API: {e}")
# #     gemini_model = None

# # # Configure Google Cloud Vision API
# # vision_client = None
# # try:
# #     if os.path.exists(VISION_API_KEY_PATH):
# #         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH)
# #         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
# #         logging.info("Google Cloud Vision API configured.")
# #     else:
# #         logging.warning(f"Vision API key file not found at {VISION_API_KEY_PATH}. OCR functionality may be limited.")
# # except Exception as e:
# #     logging.error(f"Could not configure Google Cloud Vision API: {e}")
# #     vision_client = None

# # # --- UPLOAD FOLDER CONFIGURATION ---
# # # Define the upload folder relative to the current working directory
# # UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# # # Ensure UPLOAD_FOLDER is part of app.config
# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # # Create UPLOAD_FOLDER if it doesn't exist. exist_ok=True prevents error if it already exists.
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# # logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")
# # # --- END UPLOAD FOLDER CONFIGURATION ---

# # # Load ML Models (Classifier for Tax Regime, Regressor for Tax Liability)
# # tax_regime_classifier_model = None
# # tax_regressor_model = None
# # try:
# #     # --- CORRECTED MODEL LOADING PATHS AND FILENAMES ---
# #     # Model trainer saves as .pkl in the current directory.
# #     classifier_path = 'tax_regime_classifier_model.pkl'
# #     regressor_path = 'final_tax_regressor_model.pkl'

# #     if os.path.exists(classifier_path):
# #         tax_regime_classifier_model = joblib.load(classifier_path)
# #         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
# #     else:
# #         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

# #     if os.path.exists(regressor_path):
# #         tax_regressor_model = joblib.load(regressor_path)
# #         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
# #     else:
# #         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# # except Exception as e:
# #     logging.error(f"Error loading ML models: {e}. Ensure 'models/' directory exists and models are trained.")

# # # --- Helper Functions ---
# # def get_user_id():
# #     """Retrieves user ID from JWT token."""
# #     try:
# #         return get_jwt_identity()
# #     except Exception as e:
# #         logging.warning(f"Could not get JWT identity: {e}")
# #         return None

# # def allowed_file(filename):
# #     """Checks if the uploaded file has an allowed extension."""
# #     return '.' in filename and \
# #            filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

# # def ocr_document(file_bytes):
# #     """Performs OCR on the document using Google Cloud Vision API."""
# #     if not vision_client:
# #         logging.error("Google Cloud Vision client not initialized.")
# #         return {"error": "OCR service unavailable."}, None

# #     image = vision.Image(content=file_bytes)
# #     try:
# #         response = vision_client.document_text_detection(image=image)
# #         full_text = response.full_text_annotation.text
# #         return None, full_text
# #     except Exception as e:
# #         logging.error(f"Error during OCR with Vision API: {traceback.format_exc()}")
# #         return {"error": f"OCR failed: {e}"}, None

# # def safe_float(val):
# #     """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
# #     Handles commas and currency symbols."""
# #     try:
# #         if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
# #             return 0.0
# #         if isinstance(val, str):
# #             # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
# #             val = val.replace(',', '').replace('₹', '').strip()
            
# #         return float(val)
# #     except (ValueError, TypeError):
# #         logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
# #         return 0.0

# # def safe_string(val):
# #     """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
# #     if val is None:
# #         return "null"
# #     s_val = str(val).strip()
# #     if s_val == "":
# #         return "null"
# #     return s_val

# # def convert_numpy_types(obj):
# #     """
# #     Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
# #     This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
# #     """
# #     if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
# #         return obj.item() # Converts numpy scalar to Python scalar
# #     elif isinstance(obj, dict):
# #         return {k: convert_numpy_types(v) for k, v in obj.items()}
# #     elif isinstance(obj, list):
# #         return [convert_numpy_types(elem) for elem in obj]
# #     else:
# #         return obj

# # def extract_fields_with_gemini(document_text, document_type_hint='Auto-Detect'):
# #     """
# #     Extracts key financial and personal fields from document text using Gemini.
# #     The prompt is designed to elicit specific, structured JSON output.
# #     """
# #     if not gemini_model:
# #         return {"error": "Gemini model not initialized."}, None

# #     # Refined prompt for more specific and structured extraction
# #     prompt_template = """
# #     You are an expert AI assistant for Indian income tax documents.
# #     Extract the following details from the provided document text.
# #     If a field is not present, use "null" for string values, 0 for numerical values, and "0000-01-01" for dates.
# #     Be precise and use the exact keys provided.
# #     For financial figures, extract the numerical value. For dates, use 'YYYY-MM-DD' format if available.
    
# #     Document Type Hint (provided by user, use if it helps but auto-detect if necessary): {document_type_hint}

# #     Extracted Fields (Strict JSON Format):
# #     {{
# #         "identified_type": "Detect the document type (e.g., 'Form 16', 'Bank Statement', 'Salary Slip', 'Form 26AS', 'Investment Proof', 'Home Loan Statement', 'Other Document').",
# #         "financial_year": "e.g., 2023-24",
# #         "assessment_year": "e.g., 2024-25",
# #         "name_of_employee": "Full name of employee/account holder",
# #         "pan_of_employee": "PAN number",
# #         "date_of_birth": "YYYY-MM-DD",
# #         "gender": "M/F/Other",
# #         "residential_status": "Resident/Non-Resident",
# #         "employer_name": "Employer's name",
# #         "employer_address": "Employer's address",
# #         "pan_of_deductor": "Deductor's PAN",
# #         "tan_of_deductor": "Deductor's TAN",
# #         "designation_of_employee": "Employee's designation",
# #         "period_from": "YYYY-MM-DD (e.g., start date of salary slip period)",
# #         "period_to": "YYYY-MM-DD (e.g., end date of salary slip period)",

# #         // Income Details
# #         "gross_salary_total": 0.0,
# #         "salary_as_per_sec_17_1": 0.0,
# #         "value_of_perquisites_u_s_17_2": 0.0,
# #         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
# #         "basic_salary": 0.0,
# #         "hra_received": 0.0,
# #         "conveyance_allowance": 0.0,
# #         "transport_allowance": 0.0,
# #         "overtime_pay": 0.0,
# #         "total_exempt_allowances": 0.0,
# #         "income_from_house_property": 0.0,
# #         "income_from_other_sources": 0.0,
# #         "capital_gains_long_term": 0.0,
# #         "capital_gains_short_term": 0.0,
# #         "gross_total_income_as_per_document": 0.0,

# #         // Deductions
# #         "professional_tax": 0.0,
# #         "interest_on_housing_loan_self_occupied": 0.0,
# #         "deduction_80c": 0.0,
# #         "deduction_80c_epf": 0.0,
# #         "deduction_80c_insurance_premium": 0.0,
# #         "deduction_80ccc": 0.0,
# #         "deduction_80ccd": 0.0,
# #         "deduction_80ccd1b": 0.0,
# #         "deduction_80d": 0.0,
# #         "deduction_80g": 0.0,
# #         "deduction_80tta": 0.0,
# #         "deduction_80ttb": 0.0,
# #         "deduction_80e": 0.0,
# #         "total_deductions_chapter_via": 0.0,
# #         "aggregate_of_deductions_from_salary": 0.0,
# #         "epf_contribution": 0.0,
# #         "esi_contribution": 0.0,

# #         // Tax Paid
# #         "total_tds": 0.0,
# #         "total_tds_deducted_summary": 0.0,
# #         "total_tds_deposited_summary": 0.0,
# #         "quarter_1_receipt_number": "null",
# #         "quarter_1_tds_deducted": 0.0,
# #         "quarter_1_tds_deposited": 0.0,
# #         "advance_tax": 0.0,
# #         "self_assessment_tax": 0.0,

# #         // Other Tax Info
# #         "taxable_income_as_per_document": 0.0,
# #         "tax_payable_as_per_document": 0.0,
# #         "refund_status_as_per_document": "null",
# #         "tax_regime_chosen": "Old/New/null",
# #         "net_amount_payable": 0.0,
# #         "days_present": "null",
# #         "overtime_hours": "null",

# #         // Bank Statement Details (prioritize these if identified_type is Bank Statement)
# #         "account_holder_name": "null",
# #         "account_number": "null",
# #         "ifsc_code": "null",
# #         "bank_name": "null",
# #         "branch_address": "null",
# #         "statement_start_date": "0000-01-01",
# #         "statement_end_date": "0000-01-01",
# #         "opening_balance": 0.0,
# #         "closing_balance": 0.0,
# #         "total_deposits": 0.0,
# #         "total_withdrawals": 0.0,
# #         "transaction_summary": [
# #             {
# #                 "date": "YYYY-MM-DD",
# #                 "description": "transaction description",
# #                 "type": "CR/DR",
# #                 "amount": 0.0
# #             }
# #         ]
# #     }}
    
# #     Document Text:
# #     {document_text}
# #     """

# #     full_prompt = prompt_template.format(document_type_hint=document_type_hint, document_text=document_text)

# #     try:
# #         response = gemini_model.generate_content(full_prompt)
# #         extracted_json_str = response.candidates[0].content.parts[0].text
# #         # Clean the string to ensure it's valid JSON
# #         # Sometimes Gemini might include markdown ```json ... ``` or extra text
# #         if extracted_json_str.strip().startswith("```json"):
# #             extracted_json_str = extracted_json_str.replace("```json", "").replace("```", "").strip()
        
# #         extracted_data = json.loads(extracted_json_str)
# #         # Ensure all keys from schema are present and correctly typed (even if null or 0 from Gemini)
# #         # This explicit casting is crucial for consistent data types in MongoDB and frontend.
# #         for key, prop_details in { # Define expected types for all fields that Gemini outputs
# #                 "identified_type": "STRING", "financial_year": "STRING", "assessment_year": "STRING",
# #                 "name_of_employee": "STRING", "pan_of_employee": "STRING", "date_of_birth": "DATE_STRING",
# #                 "gender": "STRING", "residential_status": "STRING", "employer_name": "STRING",
# #                 "employer_address": "STRING", "pan_of_deductor": "STRING", "tan_of_deductor": "STRING",
# #                 "designation_of_employee": "STRING", "period_from": "DATE_STRING", "period_to": "DATE_STRING",
# #                 "gross_salary_total": "NUMBER", "salary_as_per_sec_17_1": "NUMBER", "value_of_perquisites_u_s_17_2": "NUMBER",
# #                 "profits_in_lieu_of_salary_u_s_17_3": "NUMBER", "basic_salary": "NUMBER", "hra_received": "NUMBER",
# #                 "conveyance_allowance": "NUMBER", "transport_allowance": "NUMBER", "overtime_pay": "NUMBER",
# #                 "total_exempt_allowances": "NUMBER", "income_from_house_property": "NUMBER", "income_from_other_sources": "NUMBER",
# #                 "capital_gains_long_term": "NUMBER", "capital_gains_short_term": "NUMBER",
# #                 "gross_total_income_as_per_document": "NUMBER", "professional_tax": "NUMBER",
# #                 "interest_on_housing_loan_self_occupied": "NUMBER", "deduction_80c": "NUMBER",
# #                 "deduction_80c_epf": "NUMBER", "deduction_80c_insurance_premium": "NUMBER", "deduction_80ccc": "NUMBER",
# #                 "deduction_80ccd": "NUMBER", "deduction_80ccd1b": "NUMBER", "deduction_80d": "NUMBER",
# #                 "deduction_80g": "NUMBER", "deduction_80tta": "NUMBER", "deduction_80ttb": "NUMBER",
# #                 "deduction_80e": "NUMBER", "total_deductions_chapter_via": "NUMBER", "aggregate_of_deductions_from_salary": "NUMBER",
# #                 "epf_contribution": "NUMBER", "esi_contribution": "NUMBER", "total_tds": "NUMBER",
# #                 "total_tds_deducted_summary": "NUMBER", "total_tds_deposited_summary": "NUMBER",
# #                 "quarter_1_receipt_number": "STRING", "quarter_1_tds_deducted": "NUMBER", "quarter_1_tds_deposited": "NUMBER",
# #                 "advance_tax": "NUMBER", "self_assessment_tax": "NUMBER", "taxable_income_as_per_document": "NUMBER",
# #                 "tax_payable_as_per_document": "NUMBER", "refund_status_as_per_document": "STRING",
# #                 "tax_regime_chosen": "STRING", "net_amount_payable": "NUMBER", "days_present": "STRING",
# #                 "overtime_hours": "STRING",
# #                 "account_holder_name": "STRING", "account_number": "STRING", "ifsc_code": "STRING",
# #                 "bank_name": "STRING", "branch_address": "STRING", "statement_start_date": "DATE_STRING",
# #                 "statement_end_date": "DATE_STRING", "opening_balance": "NUMBER", "closing_balance": "NUMBER",
# #                 "total_deposits": "NUMBER", "total_withdrawals": "NUMBER", "transaction_summary": "ARRAY_OF_OBJECTS"
# #         }.items():
# #             if key not in extracted_data or extracted_data[key] is None:
# #                 if prop_details == "NUMBER":
# #                     extracted_data[key] = 0.0
# #                 elif prop_details == "DATE_STRING":
# #                     extracted_data[key] = "0000-01-01"
# #                 elif prop_details == "ARRAY_OF_OBJECTS":
# #                     extracted_data[key] = []
# #                 else: # Default for STRING
# #                     extracted_data[key] = "null"
# #             else:
# #                 # Type conversion/validation
# #                 if prop_details == "NUMBER":
# #                     extracted_data[key] = safe_float(extracted_data[key])
# #                 elif prop_details == "DATE_STRING":
# #                     # Validate and format date strings
# #                     date_val = safe_string(extracted_data[key])
# #                     try:
# #                         if date_val and date_val != "0000-01-01":
# #                             dt_obj = datetime.strptime(date_val.split('T')[0], '%Y-%m-%d')
# #                             extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
# #                         else:
# #                             extracted_data[key] = "0000-01-01"
# #                     except ValueError:
# #                         extracted_data[key] = "0000-01-01"
# #                 elif prop_details == "STRING":
# #                     extracted_data[key] = safe_string(extracted_data[key])
# #                 elif prop_details == "ARRAY_OF_OBJECTS":
# #                     if key == "transaction_summary" and isinstance(extracted_data[key], list):
# #                         processed_transactions = []
# #                         for item in extracted_data[key]:
# #                             processed_item = {
# #                                 "date": safe_string(item.get("date", "0000-01-01")),
# #                                 "description": safe_string(item.get("description")),
# #                                 "type": safe_string(item.get("type", "null")),
# #                                 "amount": safe_float(item.get("amount"))
# #                             }
# #                             # Re-validate and format transaction date
# #                             try:
# #                                 if processed_item['date'] and processed_item['date'] != "0000-01-01":
# #                                     dt_obj = datetime.strptime(processed_item['date'].split('T')[0], '%Y-%m-%d')
# #                                     processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
# #                                 else:
# #                                     processed_item['date'] = "0000-01-01"
# #                             except ValueError:
# #                                 processed_item['date'] = "0000-01-01"
# #                             processed_transactions.append(processed_item)
# #                         extracted_data[key] = processed_transactions
# #                     else:
# #                         extracted_data[key] = [] # Fallback to empty list if not expected format
        
# #         return None, extracted_data
# #     except Exception as e:
# #         logging.error(f"Error during Gemini extraction or post-processing: {traceback.format_exc()}")
# #         return {"error": f"Gemini extraction failed or data parsing error: {e}"}, None


# # def _aggregate_financial_data(extracted_data_list):
# #     """
# #     Aggregates financial data from multiple extracted documents, applying reconciliation rules.
# #     Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
# #     """
    
# #     aggregated_data = {
# #         # Initialize all fields that are expected in the final aggregated output
# #         "identified_type": "Other Document", # Overall identified type if mixed documents
# #         "employer_name": "null", "employer_address": "null",
# #         "pan_of_deductor": "null", "tan_of_deductor": "null",
# #         "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
# #         "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
# #         "assessment_year": "null", "financial_year": "null",
# #         "period_from": "0000-01-01", "period_to": "0000-01-01",
        
# #         # Income Components - These should be summed
# #         "basic_salary": 0.0,
# #         "hra_received": 0.0,
# #         "conveyance_allowance": 0.0,
# #         "transport_allowance": 0.0,
# #         "overtime_pay": 0.0,
# #         "salary_as_per_sec_17_1": 0.0,
# #         "value_of_perquisites_u_s_17_2": 0.0,
# #         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
# #         "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

# #         "income_from_house_property": 0.0,
# #         "income_from_other_sources": 0.0,
# #         "capital_gains_long_term": 0.0,
# #         "capital_gains_short_term": 0.0,

# #         # Deductions - These should be summed, capped later if needed
# #         "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
# #         "professional_tax": 0.0,
# #         "interest_on_housing_loan_self_occupied": 0.0,
# #         "deduction_80c": 0.0,
# #         "deduction_80c_epf": 0.0,
# #         "deduction_80c_insurance_premium": 0.0,
# #         "deduction_80ccc": 0.0,
# #         "deduction_80ccd": 0.0,
# #         "deduction_80ccd1b": 0.0,
# #         "deduction_80d": 0.0,
# #         "deduction_80g": 0.0,
# #         "deduction_80tta": 0.0,
# #         "deduction_80ttb": 0.0,
# #         "deduction_80e": 0.0,
# #         "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
# #         "epf_contribution": 0.0, # Initialize epf_contribution
# #         "esi_contribution": 0.0, # Initialize esi_contribution


# #         # Tax Paid
# #         "total_tds": 0.0,
# #         "advance_tax": 0.0,
# #         "self_assessment_tax": 0.0,
# #         "total_tds_deducted_summary": 0.0, # From Form 16 Part A

# #         # Document Specific (Non-summable, usually taken from most authoritative source)
# #         "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

# #         # Bank Account Details (Take from the most complete or latest if multiple)
# #         "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
# #         "bank_name": "null", "branch_address": "null",
# #         "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
# #         "opening_balance": 0.0, "closing_balance": 0.0,
# #         "total_deposits": 0.0, "total_withdrawals": 0.0,
# #         "transaction_summary": [], # Aggregate all transactions

# #         # Other fields from the schema, ensuring they exist
# #         "net_amount_payable": 0.0,
# #         "days_present": "null",
# #         "overtime_hours": "null",

# #         # Calculated fields for frontend
# #         "Age": "N/A", 
# #         "total_gross_income": 0.0, # Overall sum of all income heads
# #         "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
# #         "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
# #         "deduction_80C": 0.0, # Alias for deduction_80c
# #         "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
# #         "deduction_80D": 0.0, # Alias for deduction_80d
# #         "deduction_80G": 0.0, # Alias for deduction_80g
# #         "deduction_80TTA": 0.0, # Alias for deduction_80tta
# #         "deduction_80TTB": 0.0, # Alias for deduction_80ttb
# #         "deduction_80E": 0.0, # Alias for deduction_80e
# #         "total_deductions": 0.0, # Overall total deductions used in calculation
# #     }

# #     # Define document priority for overriding fields (higher value means higher priority)
# #     # Form 16 should provide definitive income/deduction figures.
# #     doc_priority = {
# #         "Form 16": 5,
# #         "Form 26AS": 4,
# #         "Salary Slip": 3,
# #         "Investment Proof": 2,
# #         "Home Loan Statement": 2,
# #         "Bank Statement": 1, # Lowest priority for financial figures, highest for bank-specific
# #         "Other Document": 0,
# #         "Unknown": 0,
# #         "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
# #     }

# #     # Sort documents by priority (higher priority first)
# #     sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

# #     # Use a dictionary to track which field was last set by which document priority
# #     # This helps in overriding with higher-priority document data.
# #     field_source_priority = {key: -1 for key in aggregated_data}

# #     # Iterate through sorted documents and aggregate data
# #     for data in sorted_extracted_data:
# #         doc_type = safe_string(data.get('identified_type'))
# #         current_priority = doc_priority.get(doc_type, 0)
# #         logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

# #         # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
# #         # Otherwise, individual components will be summed later.
# #         extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
# #         if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
# #             aggregated_data["gross_salary_total"] = extracted_gross_salary_total
# #             field_source_priority["gross_salary_total"] = current_priority
# #             logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

# #         # Update core personal details only from highest priority document or if current is 'null'
# #         personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
# #         for p_field in personal_fields:
# #             if safe_string(data.get(p_field)) != "null" and \
# #                (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
# #                 aggregated_data[p_field] = safe_string(data.get(p_field))
# #                 field_source_priority[p_field] = current_priority


# #         for key, value in data.items():
# #             # Skip keys already handled explicitly or which have specific aggregation logic
# #             if key in personal_fields or key == "gross_salary_total":
# #                 continue 
# #             if key == "transaction_summary":
# #                 if isinstance(value, list):
# #                     aggregated_data[key].extend(value)
# #                 continue
# #             if key == "identified_type":
# #                 # Ensure highest priority identified_type is kept
# #                 if current_priority > field_source_priority.get(key, -1):
# #                     aggregated_data[key] = safe_string(value)
# #                     field_source_priority[key] = current_priority
# #                 continue
            
# #             # General handling for numerical fields: sum them up
# #             if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
# #                 # Special handling for bank balances: take from latest/highest priority statement
# #                 if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
# #                     if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
# #                         # Only update if the current document is a bank statement and has higher or equal priority
# #                         # (or if the existing aggregated value is 0)
# #                         if current_priority >= field_source_priority.get(key, -1):
# #                             aggregated_data[key] = safe_float(value)
# #                             field_source_priority[key] = current_priority
# #                     else: # For other document types, just sum the numbers if they appear
# #                         aggregated_data[key] += safe_float(value)
# #                 else:
# #                     aggregated_data[key] += safe_float(value)
# #             # General handling for string fields: take from highest priority document
# #             elif key in aggregated_data and isinstance(aggregated_data[key], str):
# #                 if safe_string(value) != "null" and safe_string(value) != "" and \
# #                    (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
# #                     aggregated_data[key] = safe_string(value)
# #                     field_source_priority[key] = current_priority
# #             # Default for other types if they are not explicitly handled
# #             elif key in aggregated_data and value is not None:
# #                 if current_priority > field_source_priority.get(key, -1):
# #                     aggregated_data[key] = value
# #                     field_source_priority[key] = current_priority

# #     # --- Post-aggregation calculations and reconciliation ---
    
# #     # Calculate `total_gross_income` (overall income from all heads)
# #     # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
# #     # try to derive it from payslip components like basic, HRA, etc.
# #     if aggregated_data["gross_salary_total"] == 0.0:
# #         aggregated_data["gross_salary_total"] = (
# #             safe_float(aggregated_data["basic_salary"]) +
# #             safe_float(aggregated_data["hra_received"]) +
# #             safe_float(aggregated_data["conveyance_allowance"]) +
# #             safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
# #             safe_float(aggregated_data["overtime_pay"]) +
# #             safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
# #             safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
# #         )
# #         # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
# #         # Assuming extracted values are already annual or normalized.

# #     # Now calculate the comprehensive total_gross_income for tax computation
# #     aggregated_data["total_gross_income"] = (
# #         safe_float(aggregated_data["gross_salary_total"]) +
# #         safe_float(aggregated_data["income_from_house_property"]) +
# #         safe_float(aggregated_data["income_from_other_sources"]) + 
# #         safe_float(aggregated_data["capital_gains_long_term"]) +
# #         safe_float(aggregated_data["capital_gains_short_term"])
# #     )
# #     aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

# #     # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
# #     # This prevents double counting if EPF is reported separately and also included in 80C
# #     # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
# #     # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
# #     # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
# #     if safe_float(aggregated_data["epf_contribution"]) > 0:
# #         aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
# #     # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
# #     aggregated_data["total_deductions_chapter_via"] = (
# #         safe_float(aggregated_data["deduction_80c"]) +
# #         safe_float(aggregated_data["deduction_80ccc"]) +
# #         safe_float(aggregated_data["deduction_80ccd"]) +
# #         safe_float(aggregated_data["deduction_80ccd1b"]) +
# #         safe_float(aggregated_data["deduction_80d"]) +
# #         safe_float(aggregated_data["deduction_80g"]) +
# #         safe_float(aggregated_data["deduction_80tta"]) +
# #         safe_float(aggregated_data["deduction_80ttb"]) +
# #         safe_float(aggregated_data["deduction_80e"])
# #     )
# #     aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


# #     # Aliases for frontend (ensure these are correctly populated from derived values)
# #     aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
# #     # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
# #     # This is a fallback and might not always reflect actual exemptions as per tax rules.
# #     if aggregated_data["total_exempt_allowances"] == 0.0:
# #         aggregated_data["total_exempt_allowances"] = (
# #             safe_float(aggregated_data.get("conveyance_allowance")) +
# #             safe_float(aggregated_data.get("transport_allowance")) +
# #             safe_float(aggregated_data.get("hra_received")) 
# #         )
# #         logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

# #     # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
# #     # This is a fixed amount applied during tax calculation, not a sum from documents.
# #     aggregated_data["standard_deduction"] = 50000.0 

# #     # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
# #     dob_str = safe_string(aggregated_data.get("date_of_birth"))
# #     if dob_str != "null" and dob_str != "0000-01-01":
# #         try:
# #             dob = datetime.strptime(dob_str, '%Y-%m-%d')
# #             today = datetime.now()
# #             age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
# #             aggregated_data["Age"] = age
# #         except ValueError:
# #             logging.warning(f"Could not parse date_of_birth: {dob_str}")
# #             aggregated_data["Age"] = "N/A"
# #     else:
# #         aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

# #     # Populate aliases for frontend display consistency
# #     aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
# #     aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
# #     aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
# #     aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
# #     aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
# #     aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
# #     aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
# #     aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
# #     aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

# #     # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
# #     # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
# #     # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
# #     # For display, we can show sum of what's *claimed* or *extracted*.
# #     # Let's make `total_deductions` a sum of all potential deductions for display.
# #     aggregated_data["total_deductions"] = (
# #         aggregated_data["standard_deduction"] + 
# #         aggregated_data["professional_tax"] +
# #         aggregated_data["interest_on_housing_loan_self_occupied"] +
# #         aggregated_data["total_deductions_chapter_via"]
# #     )
# #     aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


# #     # Sort all_transactions by date (oldest first)
# #     for tx in aggregated_data['transaction_summary']:
# #         if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
# #             try:
# #                 tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
# #             except ValueError:
# #                 tx['date_sortable'] = datetime.min # Fallback for unparseable dates
# #         else:
# #             tx['date_sortable'] = datetime.min

# #     aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
# #     # Remove the temporary sortable key
# #     for tx in aggregated_data['transaction_summary']:
# #         tx.pop('date_sortable', None)

# #     # If identified_type is still "null" or "Unknown" and some other fields populated,
# #     # try to infer a better type if possible, or leave as "Other Document"
# #     if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
# #         if safe_string(aggregated_data.get('employer_name')) != "null" and \
# #            safe_float(aggregated_data.get('gross_salary_total')) > 0:
# #            aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
# #         elif safe_string(aggregated_data.get('account_number')) != "null" and \
# #              (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
# #              aggregated_data["identified_type"] = "Bank Statement"
# #         elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
# #              safe_float(aggregated_data.get('hra_received')) > 0 or \
# #              safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
# #              aggregated_data["identified_type"] = "Salary Slip"

# #     # Ensure PAN and Financial Year are properly set for database grouping
# #     # If not extracted, try to get from previous records or default to "null"
# #     if safe_string(aggregated_data.get("pan_of_employee")) == "null":
# #         aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

# #     # Derive financial year from assessment year if financial_year is null
# #     if financial_year == "UNKNOWNFY":
# #         for data in extracted_data_from_current_upload:
# #             if safe_string(data.get("assessment_year")) != "null":
# #                 try:
# #                     ay_parts = safe_string(data["assessment_year"]).split('-')
# #                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
# #                         start_year = int(ay_parts[0]) -1
# #                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
# #                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
# #                             financial_year = fy
# #                             break
# #                 except Exception:
# #                     pass # Keep default if parsing fails
# #         if financial_year == "UNKNOWNFY":
# #             aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
# #     logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
# #     return aggregated_data

# # def calculate_final_tax_summary(aggregated_data):
# #     """
# #     Calculates the estimated tax payable and refund status based on aggregated financial data.
# #     This function implements a SIMPLIFIED Indian income tax calculation for demonstration.
# #     !!! IMPORTANT: This must be replaced with actual, up-to-date, and comprehensive
# #     Indian income tax laws, considering both Old and New regimes, age groups,
# #     surcharges, cess, etc., for a production system. !!!

# #     Args:
# #         aggregated_data (dict): A dictionary containing aggregated financial fields.

# #     Returns:
# #         dict: A dictionary with computed tax liability, refund/due status, and notes.
# #     """
    
# #     # If the document type is a Bank Statement, skip tax calculation
# #     if aggregated_data.get('identified_type') == 'Bank Statement':
# #         return {
# #             "calculated_gross_income": 0.0,
# #             "calculated_total_deductions": 0.0,
# #             "computed_taxable_income": 0.0,
# #             "estimated_tax_payable": 0.0,
# #             "total_tds_credit": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "predicted_tax_regime": "N/A",
# #             "notes": ["Tax computation is not applicable for Bank Statements. Please upload tax-related documents like Form 16 or Salary Slips for tax calculation."],
# #             "old_regime_tax_payable": 0.0,
# #             "new_regime_tax_payable": 0.0,
# #             "calculation_details": ["Tax computation is not applicable for Bank Statements."],
# #             "regime_considered": "N/A"
# #         }

# #     # Safely extract and convert relevant values from aggregated_data
# #     gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
# #     # Deductions used for tax calculation (subject to limits and regime)
# #     total_chapter_via_deductions = safe_float(aggregated_data.get("total_deductions_chapter_via", 0)) 
# #     professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
# #     standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 0)) # Ensure standard deduction is fetched
# #     interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))

# #     # Sum all TDS and advance tax for comparison
# #     total_tds_credit = (
# #         safe_float(aggregated_data.get("total_tds", 0)) + 
# #         safe_float(aggregated_data.get("advance_tax", 0)) + 
# #         safe_float(aggregated_data.get("self_assessment_tax", 0))
# #     )

# #     tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
# #     age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
# #     if age == "N/A":
# #         age_group = "General"
# #     elif age < 60:
# #         age_group = "General"
# #     elif age >= 60 and age < 80:
# #         age_group = "Senior Citizen"
# #     else: # age >= 80
# #         age_group = "Super Senior Citizen"

# #     # --- Calculation Details List (for frontend display) ---
# #     calculation_details = []

# #     # --- Check for insufficient data for tax computation ---
# #     if gross_total_income < 100.0 and total_chapter_via_deductions < 100.0 and total_tds_credit < 100.0:
# #         calculation_details.append("Insufficient data provided for comprehensive tax calculation. Please upload documents with income and deduction details.")
# #         return {
# #             "calculated_gross_income": gross_total_income,
# #             "calculated_total_deductions": 0.0, # No significant deductions processed yet
# #             "computed_taxable_income": 0.0,
# #             "estimated_tax_payable": 0.0,
# #             "total_tds_credit": total_tds_credit,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "predicted_tax_regime": "N/A",
# #             "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
# #             "old_regime_tax_payable": 0.0,
# #             "new_regime_tax_payable": 0.0,
# #             "calculation_details": calculation_details,
# #             "regime_considered": "N/A"
# #         }

# #     calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

# #     # --- Old Tax Regime Calculation ---
# #     # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
# #     # Chapter VI-A deductions are capped at their respective limits or overall 1.5L for 80C, etc.
# #     # For simplicity, we'll use the extracted `total_deductions_chapter_via` but it should ideally be capped.
# #     # The actual tax deduction limits should be applied here.
    
# #     # Cap 80C related deductions at 1.5 Lakhs
# #     deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
# #     # Cap 80D (Health Insurance) - simplified max 25k for general, 50k for senior parent (adjust as per actual rules)
# #     deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0) 
# #     # Cap Housing Loan Interest for self-occupied at 2 Lakhs
# #     interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

# #     # Simplified Chapter VI-A deductions for old regime (summing specific 80C, 80D, 80CCD1B, 80E, 80G, 80TTA, 80TTB)
# #     total_chapter_via_deductions_old_regime = (
# #         deduction_80c_actual +
# #         safe_float(aggregated_data.get("deduction_80ccc", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ccd", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ccd1b", 0)) +
# #         safe_float(aggregated_data.get("deduction_80d", 0)) + # Corrected to use deduction_80d_actual later if needed
# #         safe_float(aggregated_data.get("deduction_80g", 0)) +
# #         safe_float(aggregated_data.get("deduction_80tta", 0)) +
# #         safe_float(aggregated_data.get("deduction_80ttb", 0)) +
# #         safe_float(aggregated_data.get("deduction_80e", 0))
# #     )
# #     total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)


# #     # Total deductions for Old Regime
# #     total_deductions_old_regime_for_calc = (
# #         standard_deduction_applied + 
# #         professional_tax + 
# #         interest_on_housing_loan_actual + 
# #         total_chapter_via_deductions_old_regime
# #     )
# #     total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

# #     taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
# #     tax_before_cess_old_regime = 0

# #     calculation_details.append(f"2. Deductions under Old Regime:")
# #     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
# #     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
# #     calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
# #     calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
# #     calculation_details.append(f"   - Section 80D (capped at ₹25,000/₹50,000): ₹{deduction_80d_actual:,.2f}")
# #     calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual):,.2f}")
# #     calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
# #     calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

# #     # Old Regime Tax Slabs (simplified for AY 2024-25)
# #     if age_group == "General":
# #         if taxable_income_old_regime <= 250000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
# #     elif age_group == "Senior Citizen": # 60 to < 80
# #         if taxable_income_old_regime <= 300000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 300000) * 0.05
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
# #     else: # Super Senior Citizen >= 80
# #         if taxable_income_old_regime <= 500000:
# #             tax_before_cess_old_regime = 0
# #         elif taxable_income_old_regime <= 1000000:
# #             tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
# #         else:
# #             tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

# #     rebate_87a_old_regime = 0
# #     if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
# #         rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
# #     tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
# #     total_tax_old_regime = round(tax_after_rebate_old_regime * 1.04, 2) # Add 4% Health and Education Cess
# #     calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
# #     calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
# #     calculation_details.append(f"6. Tax after Rebate (Old Regime): ₹{tax_after_rebate_old_regime:,.2f}")
# #     calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


# #     # --- New Tax Regime Calculation ---
# #     # From AY 2024-25, standard deduction is also applicable in the New Regime for salaried individuals.
# #     # Most Chapter VI-A deductions are *not* allowed in the New Regime, except employer's NPS contribution u/s 80CCD(2).
# #     # For simplicity, we assume only standard deduction and professional tax are applicable.
# #     # Also, housing loan interest deduction is NOT allowed for self-occupied property in New Regime.

# #     taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
# #     # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
# #     tax_before_cess_new_regime = 0

# #     calculation_details.append(f"8. Deductions under New Regime:")
# #     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
# #     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
# #     calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") # Only allowed ones
# #     calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


# #     # New Regime Tax Slabs (simplified for AY 2024-25 onwards)
# #     if taxable_income_new_regime <= 300000:
# #         tax_before_cess_new_regime = 0
# #     elif taxable_income_new_regime <= 600000:
# #         tax_before_cess_new_regime = (taxable_income_new_regime - 300000) * 0.05
# #     elif taxable_income_new_regime <= 900000:
# #         tax_before_cess_new_regime = 15000 + (taxable_income_new_regime - 600000) * 0.10
# #     elif taxable_income_new_regime <= 1200000:
# #         tax_before_cess_new_regime = 45000 + (taxable_income_new_regime - 900000) * 0.15
# #     elif taxable_income_new_regime <= 1500000:
# #         tax_before_cess_new_regime = 90000 + (taxable_income_new_regime - 1200000) * 0.20
# #     else:
# #         tax_before_cess_new_regime = 150000 + (taxable_income_new_regime - 1500000) * 0.30

# #     rebate_87a_new_regime = 0
# #     if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs
# #         rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
# #     tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
# #     total_tax_new_regime = round(tax_after_rebate_new_regime * 1.04, 2) # Add 4% Health and Education Cess
# #     calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
# #     calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
# #     calculation_details.append(f"12. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


# #     # --- Determine Optimal Regime and Final Summary ---
# #     final_tax_regime_applied = "N/A"
# #     estimated_tax_payable = 0.0
# #     computed_taxable_income = 0.0
# #     computation_notes = []

# #     # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
# #     if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
# #         estimated_tax_payable = total_tax_new_regime
# #         computed_taxable_income = taxable_income_new_regime
# #         final_tax_regime_applied = "New Regime (Chosen by User from Document)"
# #         computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
# #     elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
# #         estimated_tax_payable = total_tax_old_regime
# #         computed_taxable_income = taxable_income_old_regime
# #         final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
# #         computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
# #     else: # If no regime is explicitly chosen in documents, recommend the optimal one
# #         if total_tax_old_regime <= total_tax_new_regime:
# #             estimated_tax_payable = total_tax_old_regime
# #             computed_taxable_income = taxable_income_old_regime
# #             final_tax_regime_applied = "Old Regime (Optimal)"
# #             computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
# #         else:
# #             estimated_tax_payable = total_tax_new_regime
# #             computed_taxable_income = taxable_income_new_regime
# #             final_tax_regime_applied = "New Regime (Optimal)"
# #             computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

# #     estimated_tax_payable = round(estimated_tax_payable, 2)
# #     computed_taxable_income = round(computed_taxable_income, 2)

# #     # --- Calculate Refund/Tax Due ---
# #     refund_due_from_tax = 0.0
# #     tax_due_to_government = 0.0

# #     calculation_details.append(f"13. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
# #     if total_tds_credit > estimated_tax_payable:
# #         refund_due_from_tax = total_tds_credit - estimated_tax_payable
# #         calculation_details.append(f"14. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
# #     elif total_tds_credit < estimated_tax_payable:
# #         tax_due_to_government = estimated_tax_payable - total_tds_credit
# #         calculation_details.append(f"14. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
# #     else:
# #         calculation_details.append("14. No Refund or Additional Tax Due.")


# #     return {
# #         "calculated_gross_income": gross_total_income,
# #         "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
# #         "computed_taxable_income": computed_taxable_income,
# #         "estimated_tax_payable": estimated_tax_payable,
# #         "total_tds_credit": total_tds_credit,
# #         "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
# #         "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
# #         "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
# #         "notes": computation_notes, # List of notes
# #         "old_regime_tax_payable": total_tax_old_regime,
# #         "new_regime_tax_payable": total_tax_new_regime,
# #         "calculation_details": calculation_details,
# #         "regime_considered": final_tax_regime_applied # For clarity in the UI
# #     }

# # def generate_ml_prediction_summary(financial_data):
# #     """
# #     Generates ML model prediction summary using the loaded models.
# #     """
# #     if tax_regime_classifier_model is None or tax_regressor_model is None:
# #         logging.warning("ML models are not loaded. Cannot generate ML predictions.")
# #         return {
# #             "predicted_tax_regime": "N/A",
# #             "predicted_tax_liability": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "notes": "ML prediction service unavailable (models not loaded or training failed)."
# #         }
    
# #     # If the aggregated data is primarily from a bank statement, ML prediction for tax is not relevant
# #     if financial_data.get('identified_type') == 'Bank Statement' and financial_data.get('total_gross_income', 0.0) < 100.0:
# #         return {
# #             "predicted_tax_regime": "N/A",
# #             "predicted_tax_liability": 0.0,
# #             "predicted_refund_due": 0.0,
# #             "predicted_additional_due": 0.0,
# #             "notes": "ML prediction not applicable for bank statements. Please upload tax-related documents."
# #         }

# #     # Define the features expected by the ML models (must match model_trainer.py)
# #     # IMPORTANT: These must precisely match the features used in model_trainer.py
# #     # Re-verify against your `model_trainer.py` to ensure exact match.
# #     ml_common_numerical_features = [
# #         'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
# #         'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
# #         'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
# #         'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
# #         'Total Exempt Allowances Claimed'
# #     ]
# #     ml_categorical_features = ['Residential Status', 'Gender']
    
# #     # Prepare input for classifier model
# #     age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
# #     # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
# #     # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
# #     # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
# #     calculated_other_deductions = (
# #         safe_float(financial_data.get('deduction_80ccc', 0)) +
# #         safe_float(financial_data.get('deduction_80ccd', 0)) +
# #         safe_float(financial_data.get('deduction_80ccd1b', 0)) +
# #         safe_float(financial_data.get('deduction_80g', 0)) +
# #         safe_float(financial_data.get('deduction_80tta', 0)) +
# #         safe_float(financial_data.get('deduction_80ttb', 0))
# #     )
# #     calculated_other_deductions = round(calculated_other_deductions, 2)


# #     classifier_input_data = {
# #         'Age': age_value,
# #         'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
# #         'HRA Received': safe_float(financial_data.get('hra_received', 0)),
# #         'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
# #         'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
# #         'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
# #         'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
# #         'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
# #         'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
# #         'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
# #         'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
# #         'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
# #         'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
# #         'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
# #         'Gender': safe_string(financial_data.get('gender', 'Unknown'))
# #     }
    
# #     # Create DataFrame for classifier prediction, ensuring column order
# #     # The order must match `model_trainer.py`'s `classifier_all_features`
# #     ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
# #     classifier_df = pd.DataFrame([classifier_input_data])
    
# #     predicted_tax_regime = "N/A"
# #     try:
# #         classifier_df_processed = classifier_df[ordered_classifier_features]
# #         predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
# #         logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
# #     except Exception as e:
# #         logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
# #         predicted_tax_regime = "Prediction Failed (Error)"
        
# #     # Prepare input for regressor model
# #     # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
# #     regressor_input_data = {
# #         k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
# #     }
# #     regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

# #     regressor_df = pd.DataFrame([regressor_input_data])
    
# #     predicted_tax_liability = 0.0
# #     try:
# #         # The regressor's preprocessor will handle the categorical feature conversion.
# #         # Just ensure the input DataFrame has the correct columns and order.
# #         ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
# #         regressor_df_processed = regressor_df[ordered_regressor_features]
# #         predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
# #         logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
# #     except Exception as e:
# #         logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
# #         predicted_tax_liability = 0.0 # Default to 0 if prediction fails

# #     # Calculate refund/additional due based on ML prediction and actual TDS
# #     total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

# #     predicted_refund_due = 0.0
# #     predicted_additional_due = 0.0

# #     if total_tds_credit > predicted_tax_liability:
# #         predicted_refund_due = total_tds_credit - predicted_tax_liability
# #     elif total_tds_credit < predicted_tax_liability:
# #         predicted_additional_due = predicted_tax_liability - total_tds_credit
        
# #     # Convert any numpy types before returning
# #     return convert_numpy_types({
# #         "predicted_tax_regime": predicted_tax_regime,
# #         "predicted_tax_liability": predicted_tax_liability,
# #         "predicted_refund_due": round(predicted_refund_due, 2),
# #         "predicted_additional_due": round(predicted_additional_due, 2),
# #         "notes": "ML model predictions for optimal regime and tax liability."
# #     })

# # def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
# #     """Generates tax-saving suggestions and regime analysis using Gemini API."""
# #     if gemini_model is None:
# #         logging.error("Gemini API (gemini_model) not initialized.")
# #         return ["AI suggestions unavailable."], "AI regime analysis unavailable."

# #     # If the document type is a Bank Statement, provide a generic suggestion
# #     if aggregated_financial_data.get('identified_type') == 'Bank Statement' or \
# #        ("Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]):
# #         return (
# #             ["For comprehensive tax analysis and personalized tax-saving suggestions, please upload tax-related documents such as Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts). Bank statements are primarily for transactional summaries."],
# #             "Tax regime analysis requires complete income and deduction data, typically found in tax-specific documents."
# #         )


# #     # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
# #     financial_data_for_gemini = aggregated_financial_data.copy()

# #     # Add specific structure for Bank Statement details if identified as such, or if bank details are present
# #     if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
# #         financial_data_for_gemini['Bank Details'] = {
# #             'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
# #             'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
# #             'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
# #             'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
# #             'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
# #             'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
# #             'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
# #             'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
# #         }
# #         # Optionally, remove transaction_summary if it's too verbose for the prompt
# #         # financial_data_for_gemini.pop('transaction_summary', None)


# #     prompt = f"""
# #     You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
# #     Based on this data:
# #     1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
# #     2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

# #     **Financial Data Summary:**
# #     {json.dumps(financial_data_for_gemini, indent=2)}

# #     **Final Tax Computation Summary:**
# #     {json.dumps(final_tax_computation_summary, indent=2)}

# #     Please format your response strictly as follows:
# #     Suggestions:
# #     - [Suggestion 1]
# #     - [Suggestion 2]
# #     ...
# #     Regime Analysis: [Your analysis paragraph here].
# #     """
# #     try:
# #         response = gemini_model.generate_content(prompt)
# #         text = response.text.strip()
        
# #         suggestions = []
# #         regime_analysis = ""

# #         # Attempt to parse the structured output
# #         if "Suggestions:" in text and "Regime Analysis:" in text:
# #             parts = text.split("Regime Analysis:")
# #             suggestions_part = parts[0].replace("Suggestions:", "").strip()
# #             regime_analysis = parts[1].strip()

# #             # Split suggestions into bullet points and filter out empty strings
# #             suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
# #             if not suggestions: # If parsing as bullets failed, treat as single suggestion
# #                 suggestions = [suggestions_part]
# #         else:
# #             # Fallback if format is not as expected, return raw text as suggestions
# #             suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
# #             regime_analysis = "AI could not parse structured regime analysis."
# #             logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

# #         return suggestions, regime_analysis
# #     except Exception as e:
# #         logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
# #         return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

# # def generate_itr_pdf(tax_record_data):
# #     """
# #     Generates a dummy ITR form PDF.
# #     This uses a basic PDF string structure as a placeholder.
# #     """
# #     aggregated_data = tax_record_data.get('aggregated_financial_data', {})
# #     final_computation = tax_record_data.get('final_tax_computation_summary', {})

# #     # Determine ITR type (simplified logic)
# #     itr_type = "ITR-1 (SAHAJ - DUMMY)"
# #     if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
# #        safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
# #        safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
# #         itr_type = "ITR-2 (DUMMY)"
    
# #     # Extract key info for the dummy PDF
# #     name = aggregated_data.get('name_of_employee', 'N/A')
# #     pan = aggregated_data.get('pan_of_employee', 'N/A')
# #     financial_year = aggregated_data.get('financial_year', 'N/A')
# #     assessment_year = aggregated_data.get('assessment_year', 'N/A')
# #     total_income = final_computation.get('computed_taxable_income', 'N/A')
# #     tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
# #     refund_due = final_computation.get('predicted_refund_due', 0.0)
# #     tax_due = final_computation.get('predicted_additional_due', 0.0)
# #     regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

# #     # Add bank statement specific details to the PDF content if available
# #     bank_details_for_pdf = ""
# #     # Check if the aggregated data's identified type is 'Bank Statement' or if it contains core bank details
# #     if aggregated_data.get('identified_type') == 'Bank Statement' or \
# #        (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
# #         bank_details_for_pdf = f"""
# # BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
# # BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
# # BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
# # BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
# # """

# #     # Core PDF content without xref and EOF for length calculation
# #     core_pdf_content_lines = [
# #         f"%PDF-1.4",
# #         f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
# #         f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
# #         f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
# #         f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
# #         f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
# #         f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
# #         f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
# #         f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
# #         f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
# #         f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
# #         f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
# #         f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
# #         f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
# #         f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
# #         f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
# #     ]
    
# #     # Append bank details if available
# #     if bank_details_for_pdf:
# #         core_pdf_content_lines.append(bank_details_for_pdf)
# #         # Adjust vertical position for the Note if bank details were added
# #         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
# #     else:
# #         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

# #     core_pdf_content_lines.extend([
# #         f"endstream",
# #         f"endobj",
# #         f"xref",
# #         f"0 5",
# #         f"0000000000 65535 f",
# #         f"0000000010 00000 n",
# #         f"0000000057 00000 n",
# #         f"0000000114 00000 n",
# #         f"0000000222 00000 n",
# #         f"trailer <</Size 5 /Root 1 0 R>>",
# #     ])
    
# #     # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
# #     core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
# #     core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

# #     # Calculate the startxref position
# #     startxref_position = len(core_pdf_bytes)

# #     # Now assemble the full PDF content including startxref and EOF
# #     full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
# #     # Final encode
# #     dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

# #     return io.BytesIO(dummy_pdf_content_bytes), itr_type


# # # --- API Routes ---

# # # Serves the main page (assuming index.html is in the root)
# # @app.route('/')
# # def home():
# #     """Serves the main landing page, typically index.html."""
# #     return send_from_directory('.', 'index.html')

# # # Serves other static files (CSS, JS, images, etc.)
# # @app.route('/<path:path>')
# # def serve_static_files(path):
# #     """Serves static files from the root directory."""
# #     return send_from_directory('.', path)

# # # Serves uploaded files from the uploads folder
# # @app.route('/uploads/<filename>')
# # def uploaded_file(filename):
# #     """Allows access to temporarily stored uploaded files."""
# #     try:
# #         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# #     except FileNotFoundError:
# #         logging.warning(f"File '{filename}' not found in uploads folder.")
# #         return jsonify({"message": "File not found"}), 404
# #     except Exception as e:
# #         logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


# # @app.route('/api/register', methods=['POST'])
# # def register_user():
# #     """Handles user registration."""
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         email = data.get('email')
# #         password = data.get('password')

# #         if not username or not email or not password:
# #             logging.warning("Registration attempt with missing fields.")
# #             return jsonify({"message": "Username, email, and password are required"}), 400

# #         # Check if email or username already exists
# #         if users_collection.find_one({"email": email}):
# #             logging.warning(f"Registration failed: Email '{email}' already exists.")
# #             return jsonify({"message": "Email already exists"}), 409
# #         if users_collection.find_one({"username": username}):
# #             logging.warning(f"Registration failed: Username '{username}' already exists.")
# #             return jsonify({"message": "Username already exists"}), 409

# #         # Hash the password before storing
# #         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
# #         # Prepare user data for MongoDB insertion
# #         new_user_data = {
# #             "username": username,
# #             "email": email,
# #             "password": hashed_password.decode('utf-8'), # Store hashed password as string
# #             "full_name": data.get('fullName', ''),
# #             "pan": data.get('pan', ''),
# #             "aadhaar": data.get('aadhaar', ''),
# #             "address": data.get('address', ''),
# #             "phone": data.get('phone', ''),
# #             "created_at": datetime.utcnow()
# #         }
# #         # Insert the new user record and get the inserted ID
# #         user_id = users_collection.insert_one(new_user_data).inserted_id
# #         logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
# #         return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
# #     except Exception as e:
# #         logging.error(f"Error during registration: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred during registration."}), 500

# # @app.route('/api/login', methods=['POST'])
# # def login_user():
# #     """Handles user login and JWT token generation."""
# #     try:
# #         data = request.get_json()
# #         username = data.get('username')
# #         password = data.get('password')

# #         if not username or not password:
# #             logging.warning("Login attempt with missing credentials.")
# #             return jsonify({"error_msg": "Username and password are required"}), 400

# #         # Find the user by username
# #         user = users_collection.find_one({"username": username})

# #         # Verify user existence and password
# #         if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
# #             # Create a JWT access token with the user's MongoDB ObjectId as identity
# #             access_token = create_access_token(identity=str(user['_id']))
# #             logging.info(f"User '{username}' logged in successfully.")
# #             return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
# #         else:
# #             logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
# #             return jsonify({"error_msg": "Invalid credentials"}), 401
# #     except Exception as e:
# #         logging.error(f"Error during login: {traceback.format_exc()}")
# #         return jsonify({"error_msg": "An error occurred during login."}), 500

# # @app.route('/api/profile', methods=['GET'])
# # @jwt_required()
# # def get_user_profile():
# #     """Fetches the profile of the currently authenticated user."""
# #     try:
# #         # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
# #         current_user_id = get_jwt_identity()
# #         # Find user by ObjectId, exclude password from the result
# #         user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
# #         if not user:
# #             logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
# #             return jsonify({"message": "User not found"}), 404

# #         # Convert ObjectId to string for JSON serialization
# #         user['_id'] = str(user['_id'])
# #         logging.info(f"Profile fetched for user ID: {current_user_id}")
# #         return jsonify({"user": user}), 200
# #     except Exception as e:
# #         logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

# # @app.route('/api/profile', methods=['PUT', 'PATCH'])
# # @jwt_required()
# # def update_user_profile():
# #     """Updates the profile of the currently authenticated user."""
# #     try:
# #         current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #         data = request.get_json()

# #         # Define allowed fields for update
# #         updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
# #         update_data = {k: data[k] for k in updatable_fields if k in data}

# #         if not update_data:
# #             logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
# #             return jsonify({"message": "No fields to update provided."}), 400
        
# #         # Prevent username from being updated via this route for security/simplicity
# #         if 'username' in data:
# #             logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

# #         # If email is being updated, ensure it's not already in use by another user
# #         if 'email' in update_data:
# #             existing_user_with_email = users_collection.find_one({"email": update_data['email']})
# #             if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
# #                 logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
# #                 return jsonify({"message": "Email already in use by another account."}), 409

# #         # Perform the update operation in MongoDB
# #         result = users_collection.update_one(
# #             {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
# #             {"$set": update_data}
# #         )

# #         if result.matched_count == 0:
# #             logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
# #             return jsonify({"message": "User not found."}), 404
# #         if result.modified_count == 0:
# #             logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
# #             return jsonify({"message": "Profile data is the same, no changes made."}), 200

# #         logging.info(f"Profile updated successfully for user ID: {current_user_id}")
# #         return jsonify({"message": "Profile updated successfully!"}), 200
# #     except Exception as e:
# #         logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred while updating your profile."}), 500


# # @app.route('/api/process_documents', methods=['POST'])
# # @jwt_required()
# # def process_documents():
# #     """
# #     Handles uploaded documents, extracts financial data using Gemini and Vision API,
# #     aggregates data from multiple files, computes tax, and saves the comprehensive
# #     record to MongoDB, grouped by PAN and Financial Year.
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

# #     if 'documents' not in request.files:
# #         logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
# #         return jsonify({"message": "No 'documents' part in the request"}), 400

# #     files = request.files.getlist('documents')
# #     if not files:
# #         logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
# #         return jsonify({"message": "No selected file"}), 400

# #     extracted_data_from_current_upload = []
# #     document_processing_summary_current_upload = [] # To provide feedback on each file

# #     # Get the selected document type hint from the form data (if provided)
# #     document_type_hint = request.form.get('document_type', 'Auto-Detect') 
# #     logging.info(f"Received document type hint from frontend: {document_type_hint}")

# #     for file in files:
# #         if file.filename == '':
# #             document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
# #             continue
        
# #         filename = secure_filename(file.filename)
# #         # Create a unique filename for storing the original document
# #         unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        
# #         # --- UPLOAD FOLDER CONFIGURATION (ENSURE IT'S ALWAYS SET HERE) ---
# #         # This part was the source of the KeyError previously.
# #         # It's better to ensure app.config['UPLOAD_FOLDER'] is set at the module level
# #         # right after app = Flask(__name__), but for robustness, this check ensures it.
# #         # However, since we defined it and set app.config['UPLOAD_FOLDER'] globally now,
# #         # this if condition can be simplified, but keeping for maximum compatibility.
# #         if 'UPLOAD_FOLDER' not in app.config or app.config['UPLOAD_FOLDER'] != UPLOAD_FOLDER:
# #             app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# #             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# #         # --- END UPLOAD FOLDER CONFIGURATION ---
        
# #         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
# #         try:
# #             file_content_bytes = file.read() # Read content before saving
# #             file.seek(0) # Reset file pointer for subsequent operations if needed

# #             # Save the file temporarily (or permanently if you wish to retain originals)
# #             with open(file_path, 'wb') as f:
# #                 f.write(file_content_bytes)
# #             logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

# #             mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default

# #             # Construct the base prompt for Gemini
# #             base_prompt_instructions = (
# #                 f"You are an expert financial data extractor and tax document analyzer for Indian context. "
# #                 f"Analyze the provided document (filename: '{filename}', MIME type: {mime_type}). "
# #                 f"The user has indicated this document is of type: '{document_type_hint}'. " 
# #                 "Extract ALL relevant financial information for Indian income tax filing. "
# #                 "Your response MUST be a JSON object conforming precisely to the provided schema. "
# #                 "For numerical fields, if a value is not explicitly found or is clearly zero, you MUST use `0.0`. "
# #                 "For string fields (like names, PAN, year, dates, identified_type, gender, residential_status), if a value is not explicitly found, you MUST use the string `null`. "
# #                 "For dates, if found, use 'YYYY-MM-DD' format if possible; otherwise, `0000-01-01` if not found or cannot be parsed.\n\n"
# #             )

# #             # Add specific instructions based on document type hint
# #             if document_type_hint == 'Bank Statement':
# #                 base_prompt_instructions += (
# #                     "Specifically for a Bank Statement, extract the following details accurately:\n"
# #                     "- Account Holder Name\n- Account Number\n- IFSC Code (if present)\n- Bank Name\n"
# #                     "- Branch Address\n- Statement Start Date (YYYY-MM-DD)\n- Statement End Date (YYYY-MM-DD)\n"
# #                     "- Opening Balance\n- Closing Balance\n- Total Deposits\n- Total Withdrawals\n"
# #                     "- A summary of key transactions, including date (YYYY-MM-DD), description, and amount. Prioritize large transactions or those with specific identifiable descriptions (e.g., 'salary', 'rent', 'interest').\n"
# #                     "If a field is not found or not applicable, use `null` for strings and `0.0` for numbers. Ensure dates are in YYYY-MM-DD format."
# #                 )
# #             elif document_type_hint == 'Form 16':
# #                 base_prompt_instructions += (
# #                     "Specifically for Form 16, extract details related to employer, employee, PAN, TAN, financial year, assessment year, "
# #                     "salary components (basic, HRA, perquisites, profits in lieu of salary), exempt allowances, professional tax, "
# #                     "income from house property, income from other sources, capital gains, "
# #                     "deductions under Chapter VI-A (80C, 80D, 80G, 80E, 80CCD, etc.), TDS details (total, quarter-wise), "
# #                     "and any mentioned tax regime (Old/New). Ensure all monetary values are extracted as numbers."
# #                 )
# #             elif document_type_hint == 'Salary Slip':
# #                 base_prompt_instructions += (
# #                     "Specifically for a Salary Slip, extract employee name, PAN, employer name, basic salary, HRA, "
# #                     "conveyance allowance, transport allowance, overtime pay, EPF contribution, ESI contribution, "
# #                     "professional tax, net amount payable, days present, and overtime hours. Ensure all monetary values are extracted as numbers."
# #                 )
# #             # Add more elif blocks for other specific document types if needed

# #             error_gemini, extracted_data = extract_fields_with_gemini(base_prompt_instructions, document_type_hint)

# #             if error_gemini:
# #                 document_processing_summary_current_upload.append({
# #                     "filename": filename, "status": "failed", "message": f"AI processing error: {error_gemini['error']}",
# #                     "stored_path": f"/uploads/{unique_filename}"
# #                 })
# #                 continue
            
# #             # Add the path to the stored document for future reference in history
# #             extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
# #             extracted_data_from_current_upload.append(extracted_data)

# #             document_processing_summary_current_upload.append({
# #                 "filename": filename, "status": "success", "identified_type": extracted_data.get('identified_type', 'Unknown'),
# #                 "message": "Processed successfully.", "extracted_fields": extracted_data,
# #                 "stored_path": f"/uploads/{unique_filename}" 
# #             })

# #         except Exception as e:
# #             logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
# #             document_processing_summary_current_upload.append({
# #                 "filename": filename, "status": "error",
# #                 "message": f"An unexpected error occurred during file processing: {str(e)}",
# #                 "stored_path": f"/uploads/{unique_filename}"
# #             })
# #             continue 

# #     if not extracted_data_from_current_upload:
# #         logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
# #         return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

# #     # --- Determine PAN and Financial Year for grouping ---
# #     # Try to find PAN and FY from the currently uploaded documents first
# #     pan_of_employee = "UNKNOWNPAN"
# #     financial_year = "UNKNOWNFY"

# #     for data in extracted_data_from_current_upload:
# #         if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
# #             pan_of_employee = safe_string(data["pan_of_employee"])
# #         if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
# #             financial_year = safe_string(data["financial_year"])
# #         # If both are found, we can break early (or continue to see if a higher priority doc has them)
# #         if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
# #             break
    
# #     # If still unknown, check if the user profile has a PAN.
# #     if pan_of_employee == "UNKNOWNPAN":
# #         user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
# #         if user_profile and safe_string(user_profile.get("pan")) != "null":
# #             pan_of_employee = safe_string(user_profile["pan"])
# #             logging.info(f"Using PAN from user profile: {pan_of_employee}")
# #         else:
# #             # If PAN is still unknown, log a warning and use the placeholder
# #             logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

# #     # Derive financial year from assessment year if financial_year is null
# #     if financial_year == "UNKNOWNFY":
# #         for data in extracted_data_from_current_upload:
# #             if safe_string(data.get("assessment_year")) != "null":
# #                 try:
# #                     ay_parts = safe_string(data["assessment_year"]).split('-')
# #                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
# #                         start_year = int(ay_parts[0]) -1
# #                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
# #                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
# #                             financial_year = fy
# #                             break
# #                 except Exception:
# #                     pass # Keep default if parsing fails
# #         if financial_year == "UNKNOWNFY":
# #             financial_year = "UNKNOWNFY" # A placeholder for missing FY


# #     # Try to find an existing record for this user, PAN, and financial year
# #     existing_tax_record = tax_records_collection.find_one({
# #         "user_id": current_user_id,
# #         "aggregated_financial_data.pan_of_employee": pan_of_employee,
# #         "aggregated_financial_data.financial_year": financial_year
# #     })

# #     if existing_tax_record:
# #         logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
# #         # Merge new extracted data with existing data
# #         all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
# #         all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

# #         # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
# #         updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
# #         updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

# #         # Clear previous AI/ML results as they need to be re-generated for the updated data
# #         tax_records_collection.update_one(
# #             {"_id": existing_tax_record["_id"]},
# #             {"$set": {
# #                 "extracted_documents_data": all_extracted_data_for_fy,
# #                 "document_processing_summary": all_document_processing_summary_for_fy,
# #                 "aggregated_financial_data": updated_aggregated_financial_data,
# #                 "final_tax_computation_summary": updated_final_tax_computation_summary,
# #                 "timestamp": datetime.utcnow(), # Update timestamp of last modification
# #                 "suggestions_from_gemini": [], # Reset suggestions
# #                 "gemini_regime_analysis": "null", # Reset regime analysis
# #                 "ml_prediction_summary": {}, # Reset ML predictions
# #             }}
# #         )
# #         record_id = existing_tax_record["_id"]
# #         logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

# #     else:
# #         logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
# #         # If no existing record, aggregate only the newly uploaded data
# #         new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
# #         new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

# #         # Prepare the comprehensive tax record to save to MongoDB
# #         tax_record_to_save = {
# #             "user_id": current_user_id, 
# #             "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
# #             "financial_year": financial_year, # Store FY at top level for easy query
# #             "timestamp": datetime.utcnow(),
# #             "document_processing_summary": document_processing_summary_current_upload, 
# #             "extracted_documents_data": extracted_data_from_current_upload, 
# #             "aggregated_financial_data": new_aggregated_financial_data,
# #             "final_tax_computation_summary": new_final_tax_computation_summary,
# #             "suggestions_from_gemini": [], 
# #             "gemini_regime_analysis": "null", 
# #             "ml_prediction_summary": {},    
# #         }
# #         record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
# #         logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
# #         updated_aggregated_financial_data = new_aggregated_financial_data
# #         updated_final_tax_computation_summary = new_final_tax_computation_summary


# #     # Return success response with computed data
# #     # Ensure all data sent back is JSON serializable (e.g., no numpy types)
# #     response_data = {
# #         "status": "success",
# #         "message": "Documents processed and financial data aggregated and tax computed successfully",
# #         "record_id": str(record_id), 
# #         "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
# #         "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
# #         "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
# #     }
# #     return jsonify(response_data), 200


# # @app.route('/api/get_suggestions', methods=['POST'])
# # @jwt_required()
# # def get_suggestions():
# #     """
# #     Generates AI-driven tax-saving suggestions and provides an ML prediction summary
# #     based on a specific processed tax record (grouped by PAN/FY).
# #     """
# #     current_user_id = get_jwt_identity()

# #     data = request.get_json()
# #     record_id = data.get('record_id')

# #     if not record_id:
# #         logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
# #         return jsonify({"message": "Record ID is required to get suggestions."}), 400

# #     try:
# #         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
# #         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
# #         if not tax_record:
# #             logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
# #             return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
# #         # Get the aggregated financial data and final tax computation summary from the record
# #         aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
# #         final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

# #         # Generate suggestions and ML predictions
# #         suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
# #         ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

# #         # Update the record in DB with generated suggestions and predictions
# #         tax_records_collection.update_one(
# #             {"_id": ObjectId(record_id)},
# #             {"$set": {
# #                 "suggestions_from_gemini": suggestions,
# #                 "gemini_regime_analysis": regime_analysis,
# #                 "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
# #                 "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
# #             }}
# #         )
# #         logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

# #         return jsonify({
# #             "status": "success",
# #             "message": "AI suggestions and ML predictions generated successfully!",
# #             "suggestions_from_gemini": suggestions,
# #             "gemini_regime_analysis": regime_analysis,
# #             "ml_prediction_summary": ml_prediction_summary # Already converted
# #         }), 200

# #     except Exception as e:
# #         logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
# #         # Fallback for ML prediction summary even if overall suggestions fail
# #         ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
# #         return jsonify({
# #             "status": "error",
# #             "message": "An error occurred while generating suggestions.",
# #             "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
# #             "gemini_regime_analysis": "An error occurred.",
# #             "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
# #         }), 500

# # @app.route('/api/save_extracted_data', methods=['POST'])
# # @jwt_required()
# # def save_extracted_data():
# #     """
# #     Saves extracted and computed tax data to MongoDB.
# #     This route can be used for explicit saving if `process_documents` doesn't
# #     cover all saving scenarios or for intermediate saves.
# #     NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
# #     For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #     data = request.get_json()
# #     if not data:
# #         logging.warning(f"Save data request from user {current_user_id} with no data provided.")
# #         return jsonify({"message": "No data provided to save"}), 400
# #     try:
# #         # This route might be less relevant with the new aggregation by PAN/FY,
# #         # as `process_documents` handles the upsert logic.
# #         # However, if used for manual saving of *already aggregated* data,
# #         # ensure PAN and FY are part of `data.aggregated_financial_data`
# #         # or extracted from the `data` directly.
        
# #         # Example: Try to get PAN and FY from input data for consistency
# #         input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
# #         input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

# #         # Check for existing record for upsert behavior
# #         existing_record = tax_records_collection.find_one({
# #             "user_id": current_user_id,
# #             "aggregated_financial_data.pan_of_employee": input_pan,
# #             "aggregated_financial_data.financial_year": input_fy
# #         })

# #         if existing_record:
# #             # Update existing record
# #             update_result = tax_records_collection.update_one(
# #                 {"_id": existing_record["_id"]},
# #                 {"$set": {
# #                     **data, # Overwrite with new data, ensuring user_id and timestamp are also set
# #                     "user_id": current_user_id,
# #                     "timestamp": datetime.utcnow(),
# #                     "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
# #                     "financial_year": input_fy, # Ensure top-level FY is consistent
# #                 }}
# #             )
# #             record_id = existing_record["_id"]
# #             logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
# #             if update_result.modified_count == 0:
# #                 return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
# #         else:
# #             # Insert new record
# #             data['user_id'] = current_user_id
# #             data['timestamp'] = datetime.utcnow()
# #             data['pan_of_employee'] = input_pan
# #             data['financial_year'] = input_fy
# #             record_id = tax_records_collection.insert_one(data).inserted_id
# #             logging.info(f"New data saved for user {current_user_id} with record ID: {record_id}")
        
# #         return jsonify({"message": "Data saved successfully", "record_id": str(record_id)}), 200
# #     except Exception as e:
# #         logging.error(f"Error saving data for user {current_user_id}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to save data", "error": str(e)}), 500

# # @app.route('/api/tax_history', methods=['GET'])
# # @jwt_required()
# # def get_tax_records():
# #     """
# #     Fetches all aggregated tax records for the logged-in user, grouped by Financial Year.
# #     Records are sorted by timestamp in descending order (most recent first).
# #     """
# #     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
# #     logging.info(f"Fetching tax records for user: {current_user_id}")
# #     try:
# #         # Fetch all records for the current user, sorted by financial_year and then by timestamp
# #         # The 'user_id', 'pan_of_employee', and 'financial_year' are top-level fields now
# #         records = list(tax_records_collection.find({"user_id": current_user_id})
# #                         .sort([("financial_year", -1), ("timestamp", -1)]))

# #         # Convert MongoDB ObjectId to string for JSON serialization
# #         for record in records:
# #             record['_id'] = str(record['_id'])
# #             # Ensure 'user_id' is also a string when sending to frontend
# #             if 'user_id' in record:
# #                 record['user_id'] = str(record['user_id'])
# #             # Remove potentially large raw data fields for history list view to save bandwidth
# #             record.pop('extracted_documents_data', None) 
# #         logging.info(f"Found {len(records)} tax records for user {current_user_id}")
# #         # The frontend's TaxHistory component expects a 'history' key in the response data.
# #         return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200 # Convert numpy types
# #     except Exception as e:
# #         logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
# #         return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

# # @app.route('/api/generate-itr/<record_id>', methods=['GET'])
# # @jwt_required()
# # def generate_itr_form_route(record_id):
# #     """
# #     Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
# #     """
# #     current_user_id = get_jwt_identity()
# #     try:
# #         record_obj_id = ObjectId(record_id) # Convert record_id string to ObjectId for DB query
# #         # Ensure the tax record belongs to the current user (user_id check)
# #         tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

# #         if not tax_record:
# #             logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
# #             return jsonify({"message": "Tax record not found or you are not authorized to access it."}), 404

# #         # Generate the dummy PDF content
# #         pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
# #         pdf_buffer.seek(0) # Rewind the buffer to the beginning

# #         response = send_file(
# #             pdf_buffer,
# #             mimetype='application/pdf',
# #             as_attachment=True,
# #             download_name=f"{itr_type.replace(' ', '_')}_{record_id}.pdf"
# #         )
# #         logging.info(f"Generated and sent dummy ITR form for record ID: {record_id}")
# #         return response
# #     except Exception as e:
# #         logging.error(f"Error generating ITR form for record {record_id}: {traceback.format_exc()}")
# #         return jsonify({"message": "Failed to generate ITR form.", "error": str(e)}), 500

# # @app.route('/api/contact', methods=['POST'])
# # def contact_message():
# #     """Handles contact form submissions."""
# #     try:
# #         data = request.get_json()
# #         name = data.get('name')
# #         email = data.get('email')
# #         subject = data.get('subject')
# #         message = data.get('message')

# #         if not all([name, email, subject, message]):
# #             logging.warning("Contact form submission with missing fields.")
# #             return jsonify({"message": "All fields are required."}), 400
        
# #         # Insert contact message into MongoDB
# #         contact_messages_collection.insert_one({
# #             "name": name,
# #             "email": email,
# #             "subject": subject,
# #             "message": message,
# #             "timestamp": datetime.utcnow()
# #         })
# #         logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

# #         return jsonify({"message": "Message sent successfully!"}), 200
# #     except Exception as e:
# #         logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
# #         return jsonify({"message": "An error occurred while sending your message."}), 500

# # # --- Main application entry point ---
# # if __name__ == '__main__':
# #     # Ensure MongoDB connection is established before running the app
# #     if db is None:
# #         logging.error("MongoDB connection failed at startup. Exiting.")
# #         exit(1)
    
# #     logging.info("Starting Flask application...")
# #     # Run the Flask app
# #     # debug=True enables reloader and debugger (should be False in production)
# #     # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
# #     # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
# #     app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)




# import os
# import json
# from flask import Flask, request, jsonify, send_from_directory, send_file
# from flask_cors import CORS
# import google.generativeai as genai
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import bcrypt
# import traceback
# import logging
# import io
# from datetime import datetime, timedelta
# from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# import base64
# from google.cloud import vision
# from google.oauth2 import service_account
# from werkzeug.utils import secure_filename # Import secure_filename
# import joblib # Import joblib for loading ML models
# import pandas as pd # Import pandas for ML model input

# # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# import numpy as np

# # Import ReportLab components for PDF generation
# try:
#     # We are using a dummy PDF for now, so ReportLab is not strictly needed for functionality
#     # but the import block is kept for reference if actual PDF generation is implemented.
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     from reportlab.lib.units import inch
#     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
#     from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
#     from reportlab.lib.enums import TA_CENTER
#     REPORTLAB_AVAILABLE = True # Set to True if you install ReportLab
# except ImportError:
#     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
#     REPORTLAB_AVAILABLE = False


# # Configure logging for better visibility
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Configuration (IMPORTANT: Use environment variables in production) ---
# GEMINI_API_KEY = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs" # Replace with your actual key or env var
# MONGO_URI = "mongodb://localhost:27017/"
# JWT_SECRET_KEY = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# VISION_API_KEY_PATH = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json" # Path to your GCP service account key file

# # Define the upload folder relative to the current working directory
# UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# # Create UPLOAD_FOLDER if it doesn't exist. exist_ok=True prevents error if it already exists.
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")

# # Initialize Flask app
# app = Flask(__name__, static_folder='static') # Serve static files from 'static' folder
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Set UPLOAD_FOLDER in app config
# CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# # Setup Flask-JWT-Extended
# app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Token validity
# jwt = JWTManager(app)

# # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# @jwt.expired_token_loader
# def expired_token_callback(jwt_header, jwt_payload):
#     logging.warning("JWT token expired.")
#     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# @jwt.invalid_token_loader
# def invalid_token_callback(callback_error):
#     logging.warning(f"Invalid JWT token: {callback_error}")
#     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# @jwt.unauthorized_loader
# def unauthorized_callback(callback_error):
#     logging.warning(f"Unauthorized access attempt: {callback_error}")
#     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401


# # Initialize MongoDB
# client = None
# db = None
# users_collection = None
# tax_records_collection = None
# contact_messages_collection = None
# try:
#     client = MongoClient(MONGO_URI)
#     db = client.garudatax_ai # Your database name
#     users_collection = db['users']
#     tax_records_collection = db['tax_records'] # Collection for processed tax documents
#     contact_messages_collection = db['contact_messages']
#     logging.info("MongoDB connected successfully.")
# except Exception as e:
#     logging.error(f"Could not connect to MongoDB: {e}")
#     db = None # Set db to None if connection fails

# # Configure Google Gemini API
# try:
#     genai.configure(api_key=GEMINI_API_KEY)
#     gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Or 'gemini-pro'
#     logging.info("Google Gemini API configured.")
# except Exception as e:
#     logging.error(f"Could not configure Google Gemini API: {e}")
#     gemini_model = None

# # Configure Google Cloud Vision API
# vision_client = None
# try:
#     if os.path.exists(VISION_API_KEY_PATH):
#         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH)
#         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
#         logging.info("Google Cloud Vision API configured.")
#     else:
#         logging.warning(f"Vision API key file not found at {VISION_API_KEY_PATH}. OCR functionality may be limited.")
# except Exception as e:
#     logging.error(f"Could not configure Google Cloud Vision API: {e}")
#     vision_client = None

# # Load ML Models (Classifier for Tax Regime, Regressor for Tax Liability)
# tax_regime_classifier_model = None
# tax_regressor_model = None
# try:
#     # Ensure these paths are correct relative to where app1.py is run
#     # Assuming models are in a 'models' directory at the same level as app1.py
#     classifier_path = 'tax_regime_classifier_model.pkl'
#     regressor_path = 'final_tax_regressor_model.pkl'
# #C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\backend\final_tax_regressor_model.pkl
# #C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\backend\tax_regime_classifier_model.pkl
#     if os.path.exists(classifier_path):
#         tax_regime_classifier_model = joblib.load(classifier_path)
#         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
#     else:
#         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

#     if os.path.exists(regressor_path):
#         tax_regressor_model = joblib.load(regressor_path)
#         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
#     else:
#         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# except Exception as e:
#     logging.error(f"Error loading ML models: {e}. Ensure 'models/' directory exists and models are trained.")

# # --- Helper Functions ---
# def get_user_id():
#     """Retrieves user ID from JWT token."""
#     try:
#         return get_jwt_identity()
#     except Exception as e:
#         logging.warning(f"Could not get JWT identity: {e}")
#         return None

# def allowed_file(filename):
#     """Checks if the uploaded file has an allowed extension."""
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

# def ocr_document(file_bytes):
#     """Performs OCR on the document using Google Cloud Vision API."""
#     if not vision_client:
#         logging.error("Google Cloud Vision client not initialized.")
#         return {"error": "OCR service unavailable."}, None

#     image = vision.Image(content=file_bytes)
#     try:
#         response = vision_client.document_text_detection(image=image)
#         full_text = response.full_text_annotation.text
#         return None, full_text
#     except Exception as e:
#         logging.error(f"Error during OCR with Vision API: {traceback.format_exc()}")
#         return {"error": f"OCR failed: {e}"}, None

# def safe_float(val):
#     """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
#     Handles commas and currency symbols."""
#     try:
#         if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
#             return 0.0
#         if isinstance(val, str):
#             # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
#             val = val.replace(',', '').replace('₹', '').strip()
            
#         return float(val)
#     except (ValueError, TypeError):
#         logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
#         return 0.0

# def safe_string(val):
#     """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
#     if val is None:
#         return "null"
#     s_val = str(val).strip()
#     if s_val == "":
#         return "null"
#     return s_val

# def convert_numpy_types(obj):
#     """
#     Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
#     This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
#     """
#     if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
#         return obj.item() # Converts numpy scalar to Python scalar
#     elif isinstance(obj, dict):
#         return {k: convert_numpy_types(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_numpy_types(elem) for elem in obj]
#     else:
#         return obj

# def extract_fields_with_gemini(document_text, document_type_hint='Auto-Detect'):
#     """
#     Extracts key financial and personal fields from document text using Gemini.
#     The prompt is designed to elicit specific, structured JSON output.
#     """
#     if not gemini_model:
#         return {"error": "Gemini model not initialized."}, None

#     # Refined prompt for more specific and structured extraction
#     prompt_template = """
#     You are an expert AI assistant for Indian income tax documents.
#     Extract the following details from the provided document text.
#     If a field is not present, use "null" for string values, 0 for numerical values, and "0000-01-01" for dates.
#     Be precise and use the exact keys provided.
#     For financial figures, extract the numerical value. For dates, use 'YYYY-MM-DD' format if available.
    
#     Document Type Hint (provided by user, use if it helps but auto-detect if necessary): {document_type_hint}

#     Extracted Fields (Strict JSON Format):
#     {{
#         "identified_type": "Detect the document type (e.g., 'Form 16', 'Bank Statement', 'Salary Slip', 'Form 26AS', 'Investment Proof', 'Home Loan Statement', 'Other Document').",
#         "financial_year": "e.g., 2023-24",
#         "assessment_year": "e.g., 2024-25",
#         "name_of_employee": "Full name of employee/account holder",
#         "pan_of_employee": "PAN number",
#         "date_of_birth": "YYYY-MM-DD",
#         "gender": "M/F/Other",
#         "residential_status": "Resident/Non-Resident",
#         "employer_name": "Employer's name",
#         "employer_address": "Employer's address",
#         "pan_of_deductor": "Deductor's PAN",
#         "tan_of_deductor": "Deductor's TAN",
#         "designation_of_employee": "Employee's designation",
#         "period_from": "YYYY-MM-DD (e.g., start date of salary slip period)",
#         "period_to": "YYYY-MM-DD (e.g., end date of salary slip period)",

#         // Income Details
#         "gross_salary_total": 0.0,
#         "salary_as_per_sec_17_1": 0.0,
#         "value_of_perquisites_u_s_17_2": 0.0,
#         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
#         "basic_salary": 0.0,
#         "hra_received": 0.0,
#         "conveyance_allowance": 0.0,
#         "transport_allowance": 0.0,
#         "overtime_pay": 0.0,
#         "total_exempt_allowances": 0.0,
#         "income_from_house_property": 0.0,
#         "income_from_other_sources": 0.0,
#         "capital_gains_long_term": 0.0,
#         "capital_gains_short_term": 0.0,
#         "gross_total_income_as_per_document": 0.0,

#         // Deductions
#         "professional_tax": 0.0,
#         "interest_on_housing_loan_self_occupied": 0.0,
#         "deduction_80c": 0.0,
#         "deduction_80c_epf": 0.0,
#         "deduction_80c_insurance_premium": 0.0,
#         "deduction_80ccc": 0.0,
#         "deduction_80ccd": 0.0,
#         "deduction_80ccd1b": 0.0,
#         "deduction_80d": 0.0,
#         "deduction_80g": 0.0,
#         "deduction_80tta": 0.0,
#         "deduction_80ttb": 0.0,
#         "deduction_80e": 0.0,
#         "total_deductions_chapter_via": 0.0,
#         "aggregate_of_deductions_from_salary": 0.0,
#         "epf_contribution": 0.0,
#         "esi_contribution": 0.0,

#         // Tax Paid
#         "total_tds": 0.0,
#         "total_tds_deducted_summary": 0.0,
#         "total_tds_deposited_summary": 0.0,
#         "quarter_1_receipt_number": "null",
#         "quarter_1_tds_deducted": 0.0,
#         "quarter_1_tds_deposited": 0.0,
#         "advance_tax": 0.0,
#         "self_assessment_tax": 0.0,

#         // Other Tax Info
#         "taxable_income_as_per_document": 0.0,
#         "tax_payable_as_per_document": 0.0,
#         "refund_status_as_per_document": "null",
#         "tax_regime_chosen": "Old/New/null",
#         "net_amount_payable": 0.0,
#         "days_present": "null",
#         "overtime_hours": "null",

#         // Bank Statement Details (prioritize these if identified_type is Bank Statement)
#         "account_holder_name": "null",
#         "account_number": "null",
#         "ifsc_code": "null",
#         "bank_name": "null",
#         "branch_address": "null",
#         "statement_start_date": "0000-01-01",
#         "statement_end_date": "0000-01-01",
#         "opening_balance": 0.0,
#         "closing_balance": 0.0,
#         "total_deposits": 0.0,
#         "total_withdrawals": 0.0,
#         "transaction_summary": [
#             {{
#                 "date": "YYYY-MM-DD",
#                 "description": "transaction description",
#                 "type": "CR/DR",
#                 "amount": 0.0
#             }}
#         ]
#     }}
    
#     Document Text:
#     {document_text}
#     """

#     full_prompt = prompt_template.format(document_type_hint=document_type_hint, document_text=document_text)

#     try:
#         response = gemini_model.generate_content(full_prompt)
#         extracted_json_str = response.candidates[0].content.parts[0].text
#         # Clean the string to ensure it's valid JSON
#         # Sometimes Gemini might include markdown ```json ... ``` or extra text
#         if extracted_json_str.strip().startswith("```json"):
#             extracted_json_str = extracted_json_str.replace("```json", "").replace("```", "").strip()
        
#         extracted_data = json.loads(extracted_json_str)
#         # Ensure all keys from schema are present and correctly typed (even if null or 0 from Gemini)
#         # This explicit casting is crucial for consistent data types in MongoDB and frontend.
#         for key, prop_details in { # Define expected types for all fields that Gemini outputs
#                 "identified_type": "STRING", "financial_year": "STRING", "assessment_year": "STRING",
#                 "name_of_employee": "STRING", "pan_of_employee": "STRING", "date_of_birth": "DATE_STRING",
#                 "gender": "STRING", "residential_status": "STRING", "employer_name": "STRING",
#                 "employer_address": "STRING", "pan_of_deductor": "STRING", "tan_of_deductor": "STRING",
#                 "designation_of_employee": "STRING", "period_from": "DATE_STRING", "period_to": "DATE_STRING",
#                 "gross_salary_total": "NUMBER", "salary_as_per_sec_17_1": "NUMBER", "value_of_perquisites_u_s_17_2": "NUMBER",
#                 "profits_in_lieu_of_salary_u_s_17_3": "NUMBER", "basic_salary": "NUMBER", "hra_received": "NUMBER",
#                 "conveyance_allowance": "NUMBER", "transport_allowance": "NUMBER", "overtime_pay": "NUMBER",
#                 "total_exempt_allowances": "NUMBER", "income_from_house_property": "NUMBER", "income_from_other_sources": "NUMBER",
#                 "capital_gains_long_term": "NUMBER", "capital_gains_short_term": "NUMBER",
#                 "gross_total_income_as_per_document": "NUMBER", "professional_tax": "NUMBER",
#                 "interest_on_housing_loan_self_occupied": "NUMBER", "deduction_80c": "NUMBER",
#                 "deduction_80c_epf": "NUMBER", "deduction_80c_insurance_premium": "NUMBER", "deduction_80ccc": "NUMBER",
#                 "deduction_80ccd": "NUMBER", "deduction_80ccd1b": "NUMBER", "deduction_80d": "NUMBER",
#                 "deduction_80g": "NUMBER", "deduction_80tta": "NUMBER", "deduction_80ttb": "NUMBER",
#                 "deduction_80e": "NUMBER", "total_deductions_chapter_via": "NUMBER", "aggregate_of_deductions_from_salary": "NUMBER",
#                 "epf_contribution": "NUMBER", "esi_contribution": "NUMBER", "total_tds": "NUMBER",
#                 "total_tds_deducted_summary": "NUMBER", "total_tds_deposited_summary": "NUMBER",
#                 "quarter_1_receipt_number": "STRING", "quarter_1_tds_deducted": "NUMBER", "quarter_1_tds_deposited": "NUMBER",
#                 "advance_tax": "NUMBER", "self_assessment_tax": "NUMBER", "taxable_income_as_per_document": "NUMBER",
#                 "tax_payable_as_per_document": "NUMBER", "refund_status_as_per_document": "STRING",
#                 "tax_regime_chosen": "STRING", "net_amount_payable": "NUMBER", "days_present": "STRING",
#                 "overtime_hours": "STRING",
#                 "account_holder_name": "STRING", "account_number": "STRING", "ifsc_code": "STRING",
#                 "bank_name": "STRING", "branch_address": "STRING", "statement_start_date": "DATE_STRING",
#                 "statement_end_date": "DATE_STRING", "opening_balance": "NUMBER", "closing_balance": "NUMBER",
#                 "total_deposits": "NUMBER", "total_withdrawals": "NUMBER", "transaction_summary": "ARRAY_OF_OBJECTS"
#         }.items():
#             if key not in extracted_data or extracted_data[key] is None:
#                 if prop_details == "NUMBER":
#                     extracted_data[key] = 0.0
#                 elif prop_details == "DATE_STRING":
#                     extracted_data[key] = "0000-01-01"
#                 elif prop_details == "ARRAY_OF_OBJECTS":
#                     extracted_data[key] = []
#                 else: # Default for STRING
#                     extracted_data[key] = "null"
#             else:
#                 # Type conversion/validation
#                 if prop_details == "NUMBER":
#                     extracted_data[key] = safe_float(extracted_data[key])
#                 elif prop_details == "DATE_STRING":
#                     # Validate and format date strings
#                     date_val = safe_string(extracted_data[key])
#                     try:
#                         if date_val and date_val != "0000-01-01":
#                             dt_obj = datetime.strptime(date_val.split('T')[0], '%Y-%m-%d')
#                             extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
#                         else:
#                             extracted_data[key] = "0000-01-01"
#                     except ValueError:
#                         extracted_data[key] = "0000-01-01"
#                 elif prop_details == "STRING":
#                     extracted_data[key] = safe_string(extracted_data[key])
#                 elif prop_details == "ARRAY_OF_OBJECTS":
#                     if key == "transaction_summary" and isinstance(extracted_data[key], list):
#                         processed_transactions = []
#                         for item in extracted_data[key]:
#                             processed_item = {
#                                 "date": safe_string(item.get("date", "0000-01-01")),
#                                 "description": safe_string(item.get("description")),
#                                 "type": safe_string(item.get("type", "null")),
#                                 "amount": safe_float(item.get("amount"))
#                             }
#                             # Re-validate and format transaction date
#                             try:
#                                 if processed_item['date'] and processed_item['date'] != "0000-01-01":
#                                     dt_obj = datetime.strptime(processed_item['date'].split('T')[0], '%Y-%m-%d')
#                                     processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
#                                 else:
#                                     processed_item['date'] = "0000-01-01"
#                             except ValueError:
#                                 processed_item['date'] = "0000-01-01"
#                             processed_transactions.append(processed_item)
#                         extracted_data[key] = processed_transactions
#                     else:
#                         extracted_data[key] = [] # Fallback to empty list if not expected format
        
#         return None, extracted_data
#     except Exception as e:
#         logging.error(f"Error during Gemini extraction or post-processing: {traceback.format_exc()}")
#         return {"error": f"Gemini extraction failed or data parsing error: {e}"}, None


# def _aggregate_financial_data(extracted_data_list):
#     """
#     Aggregates financial data from multiple extracted documents, applying reconciliation rules.
#     Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
#     """
    
#     aggregated_data = {
#         # Initialize all fields that are expected in the final aggregated output
#         "identified_type": "Other Document", # Overall identified type if mixed documents
#         "employer_name": "null", "employer_address": "null",
#         "pan_of_deductor": "null", "tan_of_deductor": "null",
#         "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
#         "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
#         "assessment_year": "null", "financial_year": "null",
#         "period_from": "0000-01-01", "period_to": "0000-01-01",
        
#         # Income Components - These should be summed
#         "basic_salary": 0.0,
#         "hra_received": 0.0,
#         "conveyance_allowance": 0.0,
#         "transport_allowance": 0.0,
#         "overtime_pay": 0.0,
#         "salary_as_per_sec_17_1": 0.0,
#         "value_of_perquisites_u_s_17_2": 0.0,
#         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
#         "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

#         "income_from_house_property": 0.0,
#         "income_from_other_sources": 0.0,
#         "capital_gains_long_term": 0.0,
#         "capital_gains_short_term": 0.0,

#         # Deductions - These should be summed, capped later if needed
#         "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
#         "professional_tax": 0.0,
#         "interest_on_housing_loan_self_occupied": 0.0,
#         "deduction_80c": 0.0,
#         "deduction_80c_epf": 0.0,
#         "deduction_80c_insurance_premium": 0.0,
#         "deduction_80ccc": 0.0,
#         "deduction_80ccd": 0.0,
#         "deduction_80ccd1b": 0.0,
#         "deduction_80d": 0.0,
#         "deduction_80g": 0.0,
#         "deduction_80tta": 0.0,
#         "deduction_80ttb": 0.0,
#         "deduction_80e": 0.0,
#         "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
#         "epf_contribution": 0.0, # Initialize epf_contribution
#         "esi_contribution": 0.0, # Initialize esi_contribution


#         # Tax Paid
#         "total_tds": 0.0,
#         "advance_tax": 0.0,
#         "self_assessment_tax": 0.0,
#         "total_tds_deducted_summary": 0.0, # From Form 16 Part A

#         # Document Specific (Non-summable, usually taken from most authoritative source)
#         "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

#         # Bank Account Details (Take from the most complete or latest if multiple)
#         "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
#         "bank_name": "null", "branch_address": "null",
#         "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
#         "opening_balance": 0.0, "closing_balance": 0.0,
#         "total_deposits": 0.0, "total_withdrawals": 0.0,
#         "transaction_summary": [], # Aggregate all transactions

#         # Other fields from the schema, ensuring they exist
#         "net_amount_payable": 0.0,
#         "days_present": "null",
#         "overtime_hours": "null",

#         # Calculated fields for frontend
#         "Age": "N/A", 
#         "total_gross_income": 0.0, # Overall sum of all income heads
#         "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
#         "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
#         "deduction_80C": 0.0, # Alias for deduction_80c
#         "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
#         "deduction_80D": 0.0, # Alias for deduction_80d
#         "deduction_80G": 0.0, # Alias for deduction_80g
#         "deduction_80TTA": 0.0, # Alias for deduction_80tta
#         "deduction_80TTB": 0.0, # Alias for deduction_80ttb
#         "deduction_80E": 0.0, # Alias for deduction_80e
#         "total_deductions": 0.0, # Overall total deductions used in calculation
#     }

#     # Define document priority for overriding fields (higher value means higher priority)
#     # Form 16 should provide definitive income/deduction figures.
#     doc_priority = {
#         "Form 16": 5,
#         "Form 26AS": 4,
#         "Salary Slip": 3,
#         "Investment Proof": 2,
#         "Home Loan Statement": 2,
#         "Bank Statement": 1, # Lowest priority for financial figures, highest for bank-specific
#         "Other Document": 0,
#         "Unknown": 0,
#         "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
#     }

#     # Sort documents by priority (higher priority first)
#     sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

#     # Use a dictionary to track which field was last set by which document priority
#     # This helps in overriding with higher-priority document data.
#     field_source_priority = {key: -1 for key in aggregated_data}

#     # Iterate through sorted documents and aggregate data
#     for data in sorted_extracted_data:
#         doc_type = safe_string(data.get('identified_type'))
#         current_priority = doc_priority.get(doc_type, 0)
#         logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

#         # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
#         # Otherwise, individual components will be summed later.
#         extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
#         if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
#             aggregated_data["gross_salary_total"] = extracted_gross_salary_total
#             field_source_priority["gross_salary_total"] = current_priority
#             logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

#         # Update core personal details only from highest priority document or if current is 'null'
#         personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
#         for p_field in personal_fields:
#             if safe_string(data.get(p_field)) != "null" and \
#                (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
#                 aggregated_data[p_field] = safe_string(data.get(p_field))
#                 field_source_priority[p_field] = current_priority


#         for key, value in data.items():
#             # Skip keys already handled explicitly or which have specific aggregation logic
#             if key in personal_fields or key == "gross_salary_total":
#                 continue 
#             if key == "transaction_summary":
#                 if isinstance(value, list):
#                     aggregated_data[key].extend(value)
#                 continue
#             if key == "identified_type":
#                 # Ensure highest priority identified_type is kept
#                 if current_priority > field_source_priority.get(key, -1):
#                     aggregated_data[key] = safe_string(value)
#                     field_source_priority[key] = current_priority
#                 continue
            
#             # General handling for numerical fields: sum them up
#             if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
#                 # Special handling for bank balances: take from latest/highest priority statement
#                 if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
#                     if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
#                         # Only update if the current document is a bank statement and has higher or equal priority
#                         # (or if the existing aggregated value is 0)
#                         if current_priority >= field_source_priority.get(key, -1):
#                             aggregated_data[key] = safe_float(value)
#                             field_source_priority[key] = current_priority
#                     else: # For other document types, just sum the numbers if they appear
#                         aggregated_data[key] += safe_float(value)
#                 else:
#                     aggregated_data[key] += safe_float(value)
#             # General handling for string fields: take from highest priority document
#             elif key in aggregated_data and isinstance(aggregated_data[key], str):
#                 if safe_string(value) != "null" and safe_string(value) != "" and \
#                    (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
#                     aggregated_data[key] = safe_string(value)
#                     field_source_priority[key] = current_priority
#             # Default for other types if they are not explicitly handled
#             elif key in aggregated_data and value is not None:
#                 if current_priority > field_source_priority.get(key, -1):
#                     aggregated_data[key] = value
#                     field_source_priority[key] = current_priority

#     # --- Post-aggregation calculations and reconciliation ---
    
#     # Calculate `total_gross_income` (overall income from all heads)
#     # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
#     # try to derive it from payslip components like basic, HRA, etc.
#     if aggregated_data["gross_salary_total"] == 0.0:
#         aggregated_data["gross_salary_total"] = (
#             safe_float(aggregated_data["basic_salary"]) +
#             safe_float(aggregated_data["hra_received"]) +
#             safe_float(aggregated_data["conveyance_allowance"]) +
#             safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
#             safe_float(aggregated_data["overtime_pay"]) +
#             safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
#             safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
#         )
#         # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
#         # Assuming extracted values are already annual or normalized.

#     # Now calculate the comprehensive total_gross_income for tax computation
#     aggregated_data["total_gross_income"] = (
#         safe_float(aggregated_data["gross_salary_total"]) +
#         safe_float(aggregated_data["income_from_house_property"]) +
#         safe_float(aggregated_data["income_from_other_sources"]) + 
#         safe_float(aggregated_data["capital_gains_long_term"]) +
#         safe_float(aggregated_data["capital_gains_short_term"])
#     )
#     aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

#     # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
#     # This prevents double counting if EPF is reported separately and also included in 80C
#     # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
#     # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
#     # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
#     if safe_float(aggregated_data["epf_contribution"]) > 0:
#         aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
#     # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
#     aggregated_data["total_deductions_chapter_via"] = (
#         safe_float(aggregated_data["deduction_80c"]) +
#         safe_float(aggregated_data["deduction_80ccc"]) +
#         safe_float(aggregated_data["deduction_80ccd"]) +
#         safe_float(aggregated_data["deduction_80ccd1b"]) +
#         safe_float(aggregated_data["deduction_80d"]) +
#         safe_float(aggregated_data["deduction_80g"]) +
#         safe_float(aggregated_data["deduction_80tta"]) +
#         safe_float(aggregated_data["deduction_80ttb"]) +
#         safe_float(aggregated_data["deduction_80e"])
#     )
#     aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


#     # Aliases for frontend (ensure these are correctly populated from derived values)
#     aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
#     # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
#     # This is a fallback and might not always reflect actual exemptions as per tax rules.
#     if aggregated_data["total_exempt_allowances"] == 0.0:
#         aggregated_data["total_exempt_allowances"] = (
#             safe_float(aggregated_data.get("conveyance_allowance")) +
#             safe_float(aggregated_data.get("transport_allowance")) +
#             safe_float(aggregated_data.get("hra_received")) 
#         )
#         logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

#     # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
#     # This is a fixed amount applied during tax calculation, not a sum from documents.
#     aggregated_data["standard_deduction"] = 50000.0 

#     # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
#     dob_str = safe_string(aggregated_data.get("date_of_birth"))
#     if dob_str != "null" and dob_str != "0000-01-01":
#         try:
#             dob = datetime.strptime(dob_str, '%Y-%m-%d')
#             today = datetime.now()
#             age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#             aggregated_data["Age"] = age
#         except ValueError:
#             logging.warning(f"Could not parse date_of_birth: {dob_str}")
#             aggregated_data["Age"] = "N/A"
#     else:
#         aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

#     # Populate aliases for frontend display consistency
#     aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
#     aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
#     aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
#     aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
#     aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
#     aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
#     aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
#     aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
#     aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

#     # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
#     # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
#     # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
#     # For display, we can show sum of what's *claimed* or *extracted*.
#     # Let's make `total_deductions` a sum of all potential deductions for display.
#     aggregated_data["total_deductions"] = (
#         aggregated_data["standard_deduction"] + 
#         aggregated_data["professional_tax"] +
#         aggregated_data["interest_on_housing_loan_self_occupied"] +
#         aggregated_data["total_deductions_chapter_via"]
#     )
#     aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


#     # Sort all_transactions by date (oldest first)
#     for tx in aggregated_data['transaction_summary']:
#         if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
#             try:
#                 tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
#             except ValueError:
#                 tx['date_sortable'] = datetime.min # Fallback for unparseable dates
#         else:
#             tx['date_sortable'] = datetime.min

#     aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
#     # Remove the temporary sortable key
#     for tx in aggregated_data['transaction_summary']:
#         tx.pop('date_sortable', None)

#     # If identified_type is still "null" or "Unknown" and some other fields populated,
#     # try to infer a better type if possible, or leave as "Other Document"
#     if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
#         if safe_string(aggregated_data.get('employer_name')) != "null" and \
#            safe_float(aggregated_data.get('gross_salary_total')) > 0:
#            aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
#         elif safe_string(aggregated_data.get('account_number')) != "null" and \
#              (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
#              aggregated_data["identified_type"] = "Bank Statement"
#         elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
#              safe_float(aggregated_data.get('hra_received')) > 0 or \
#              safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
#              aggregated_data["identified_type"] = "Salary Slip"

#     # Ensure PAN and Financial Year are properly set for database grouping
#     # If not extracted, try to get from previous records or default to "null"
#     if safe_string(aggregated_data.get("pan_of_employee")) == "null":
#         aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

#     # Derive financial year from assessment year if financial_year is null
#     if safe_string(aggregated_data.get("financial_year")) == "null" and safe_string(aggregated_data.get("assessment_year")) != "null":
#         try:
#             ay_parts = safe_string(aggregated_data["assessment_year"]).split('-')
#             if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
#                 start_year = int(ay_parts[0]) -1
#                 end_year = int(ay_parts[0])
#                 aggregated_data["financial_year"] = f"{start_year}-{str(end_year)[-2:]}"
#         except Exception:
#             logging.warning(f"Could not derive financial year from assessment year: {aggregated_data.get('assessment_year')}")
#             aggregated_data["financial_year"] = "UNKNOWNFY"
#     elif safe_string(aggregated_data.get("financial_year")) == "null":
#         aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
#     logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
#     return aggregated_data

# def calculate_final_tax_summary(aggregated_data):
#     """
#     Calculates the estimated tax payable and refund status based on aggregated financial data.
#     This function implements a SIMPLIFIED Indian income tax calculation for demonstration.
#     !!! IMPORTANT: This must be replaced with actual, up-to-date, and comprehensive
#     Indian income tax laws, considering both Old and New regimes, age groups,
#     surcharges, cess, etc., for a production system. !!!

#     Args:
#         aggregated_data (dict): A dictionary containing aggregated financial fields.

#     Returns:
#         dict: A dictionary with computed tax liability, refund/due status, and notes.
#     """
    
#     # If the document type is a Bank Statement, skip tax calculation
#     if aggregated_data.get('identified_type') == 'Bank Statement':
#         return {
#             "calculated_gross_income": 0.0,
#             "calculated_total_deductions": 0.0,
#             "computed_taxable_income": 0.0,
#             "estimated_tax_payable": 0.0,
#             "total_tds_credit": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "predicted_tax_regime": "N/A",
#             "notes": ["Tax computation is not applicable for Bank Statements. Please upload tax-related documents like Form 16 or Salary Slips for tax calculation."],
#             "old_regime_tax_payable": 0.0,
#             "new_regime_tax_payable": 0.0,
#             "calculation_details": ["Tax computation is not applicable for Bank Statements."],
#             "regime_considered": "N/A"
#         }

#     # Safely extract and convert relevant values from aggregated_data
#     gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
#     # Deductions used for tax calculation (subject to limits and regime)
#     total_chapter_via_deductions = safe_float(aggregated_data.get("total_deductions_chapter_via", 0)) 
#     professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
#     standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 0)) # Ensure standard deduction is fetched
#     interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))

#     # Sum all TDS and advance tax for comparison
#     total_tds_credit = (
#         safe_float(aggregated_data.get("total_tds", 0)) + 
#         safe_float(aggregated_data.get("advance_tax", 0)) + 
#         safe_float(aggregated_data.get("self_assessment_tax", 0))
#     )

#     tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
#     age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
#     if age == "N/A":
#         age_group = "General"
#     elif age < 60:
#         age_group = "General"
#     elif age >= 60 and age < 80:
#         age_group = "Senior Citizen"
#     else: # age >= 80
#         age_group = "Super Senior Citizen"

#     # --- Calculation Details List (for frontend display) ---
#     calculation_details = []

#     # --- Check for insufficient data for tax computation ---
#     if gross_total_income < 100.0 and total_chapter_via_deductions < 100.0 and total_tds_credit < 100.0:
#         calculation_details.append("Insufficient data provided for comprehensive tax calculation. Please upload documents with income and deduction details.")
#         return {
#             "calculated_gross_income": gross_total_income,
#             "calculated_total_deductions": 0.0, # No significant deductions processed yet
#             "computed_taxable_income": 0.0,
#             "estimated_tax_payable": 0.0,
#             "total_tds_credit": total_tds_credit,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "predicted_tax_regime": "N/A",
#             "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
#             "old_regime_tax_payable": 0.0,
#             "new_regime_tax_payable": 0.0,
#             "calculation_details": calculation_details,
#             "regime_considered": "N/A"
#         }

#     calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

#     # --- Old Tax Regime Calculation ---
#     # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
#     # Chapter VI-A deductions are capped at their respective limits or overall 1.5L for 80C, etc.
#     # For simplicity, we'll use the extracted `total_deductions_chapter_via` but it should ideally be capped.
#     # The actual tax deduction limits should be applied here.
    
#     # Cap 80C related deductions at 1.5 Lakhs
#     deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
#     # Cap 80D (Health Insurance) - simplified max 25k for general, 50k for senior parent (adjust as per actual rules)
#     deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0) 
#     # Cap Housing Loan Interest for self-occupied at 2 Lakhs
#     interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

#     # Simplified Chapter VI-A deductions for old regime (summing specific 80C, 80D, 80CCD1B, 80E, 80G, 80TTA, 80TTB)
#     total_chapter_via_deductions_old_regime = (
#         deduction_80c_actual +
#         safe_float(aggregated_data.get("deduction_80ccc", 0)) +
#         safe_float(aggregated_data.get("deduction_80ccd", 0)) +
#         safe_float(aggregated_data.get("deduction_80ccd1b", 0)) +
#         safe_float(aggregated_data.get("deduction_80d", 0)) + # Corrected to use deduction_80d_actual later if needed
#         safe_float(aggregated_data.get("deduction_80g", 0)) +
#         safe_float(aggregated_data.get("deduction_80tta", 0)) +
#         safe_float(aggregated_data.get("deduction_80ttb", 0)) +
#         safe_float(aggregated_data.get("deduction_80e", 0))
#     )
#     total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)


#     # Total deductions for Old Regime
#     total_deductions_old_regime_for_calc = (
#         standard_deduction_applied + 
#         professional_tax + 
#         interest_on_housing_loan_actual + 
#         total_chapter_via_deductions_old_regime
#     )
#     total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

#     taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
#     tax_before_cess_old_regime = 0

#     calculation_details.append(f"2. Deductions under Old Regime:")
#     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
#     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
#     calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
#     calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
#     calculation_details.append(f"   - Section 80D (capped at ₹25,000/₹50,000): ₹{deduction_80d_actual:,.2f}")
#     calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual):,.2f}")
#     calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
#     calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

#     # Old Regime Tax Slabs (simplified for AY 2024-25)
#     if age_group == "General":
#         if taxable_income_old_regime <= 250000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
#     elif age_group == "Senior Citizen": # 60 to < 80
#         if taxable_income_old_regime <= 300000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 300000) * 0.05
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
#     else: # Super Senior Citizen >= 80
#         if taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

#     rebate_87a_old_regime = 0
#     if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
#         rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
#     tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
#     total_tax_old_regime = round(tax_after_rebate_old_regime * 1.04, 2) # Add 4% Health and Education Cess
#     calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
#     calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
#     calculation_details.append(f"6. Tax after Rebate (Old Regime): ₹{tax_after_rebate_old_regime:,.2f}")
#     calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


#     # --- New Tax Regime Calculation ---
#     # From AY 2024-25, standard deduction is also applicable in the New Regime for salaried individuals.
#     # Most Chapter VI-A deductions are *not* allowed in the New Regime, except employer's NPS contribution u/s 80CCD(2).
#     # For simplicity, we assume only standard deduction and professional tax are applicable.
#     # Also, housing loan interest deduction is NOT allowed for self-occupied property in New Regime.

#     taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
#     # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
#     tax_before_cess_new_regime = 0

#     calculation_details.append(f"8. Deductions under New Regime:")
#     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
#     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
#     calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") # Only allowed ones
#     calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


#     # New Regime Tax Slabs (simplified for AY 2024-25 onwards)
#     if taxable_income_new_regime <= 300000:
#         tax_before_cess_new_regime = 0
#     elif taxable_income_new_regime <= 600000:
#         tax_before_cess_new_regime = (taxable_income_new_regime - 300000) * 0.05
#     elif taxable_income_new_regime <= 900000:
#         tax_before_cess_new_regime = 15000 + (taxable_income_new_regime - 600000) * 0.10
#     elif taxable_income_new_regime <= 1200000:
#         tax_before_cess_new_regime = 45000 + (taxable_income_new_regime - 900000) * 0.15
#     elif taxable_income_new_regime <= 1500000:
#         tax_before_cess_new_regime = 90000 + (taxable_income_new_regime - 1200000) * 0.20
#     else:
#         tax_before_cess_new_regime = 150000 + (taxable_income_new_regime - 1500000) * 0.30

#     rebate_87a_new_regime = 0
#     if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs
#         rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
#     tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
#     total_tax_new_regime = round(tax_after_rebate_new_regime * 1.04, 2) # Add 4% Health and Education Cess
#     calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
#     calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
#     calculation_details.append(f"12. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


#     # --- Determine Optimal Regime and Final Summary ---
#     final_tax_regime_applied = "N/A"
#     estimated_tax_payable = 0.0
#     computed_taxable_income = 0.0
#     computation_notes = []

#     # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
#     if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
#         estimated_tax_payable = total_tax_new_regime
#         computed_taxable_income = taxable_income_new_regime
#         final_tax_regime_applied = "New Regime (Chosen by User from Document)"
#         computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
#     elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
#         estimated_tax_payable = total_tax_old_regime
#         computed_taxable_income = taxable_income_old_regime
#         final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
#         computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
#     else: # If no regime is explicitly chosen in documents, recommend the optimal one
#         if total_tax_old_regime <= total_tax_new_regime:
#             estimated_tax_payable = total_tax_old_regime
#             computed_taxable_income = taxable_income_old_regime
#             final_tax_regime_applied = "Old Regime (Optimal)"
#             computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
#         else:
#             estimated_tax_payable = total_tax_new_regime
#             computed_taxable_income = taxable_income_new_regime
#             final_tax_regime_applied = "New Regime (Optimal)"
#             computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

#     estimated_tax_payable = round(estimated_tax_payable, 2)
#     computed_taxable_income = round(computed_taxable_income, 2)

#     # --- Calculate Refund/Tax Due ---
#     refund_due_from_tax = 0.0
#     tax_due_to_government = 0.0

#     calculation_details.append(f"13. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
#     if total_tds_credit > estimated_tax_payable:
#         refund_due_from_tax = total_tds_credit - estimated_tax_payable
#         calculation_details.append(f"14. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
#     elif total_tds_credit < estimated_tax_payable:
#         tax_due_to_government = estimated_tax_payable - total_tds_credit
#         calculation_details.append(f"14. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
#     else:
#         calculation_details.append("14. No Refund or Additional Tax Due.")


#     return {
#         "calculated_gross_income": gross_total_income,
#         "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
#         "computed_taxable_income": computed_taxable_income,
#         "estimated_tax_payable": estimated_tax_payable,
#         "total_tds_credit": total_tds_credit,
#         "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
#         "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
#         "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
#         "notes": computation_notes, # List of notes
#         "old_regime_tax_payable": total_tax_old_regime,
#         "new_regime_tax_payable": total_tax_new_regime,
#         "calculation_details": calculation_details,
#         "regime_considered": final_tax_regime_applied # For clarity in the UI
#     }

# def generate_ml_prediction_summary(financial_data):
#     """
#     Generates ML model prediction summary using the loaded models.
#     """
#     if tax_regime_classifier_model is None or tax_regressor_model is None:
#         logging.warning("ML models are not loaded. Cannot generate ML predictions.")
#         return {
#             "predicted_tax_regime": "N/A",
#             "predicted_tax_liability": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "notes": "ML prediction service unavailable (models not loaded or training failed)."
#         }
    
#     # If the aggregated data is primarily from a bank statement, ML prediction for tax is not relevant
#     if financial_data.get('identified_type') == 'Bank Statement' and financial_data.get('total_gross_income', 0.0) < 100.0:
#         return {
#             "predicted_tax_regime": "N/A",
#             "predicted_tax_liability": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "notes": "ML prediction not applicable for bank statements. Please upload tax-related documents."
#         }

#     # Define the features expected by the ML models (must match model_trainer.py)
#     # IMPORTANT: These must precisely match the features used in model_trainer.py
#     # Re-verify against your `model_trainer.py` to ensure exact match.
#     ml_common_numerical_features = [
#         'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
#         'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
#         'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
#         'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
#         'Total Exempt Allowances Claimed'
#     ]
#     ml_categorical_features = ['Residential Status', 'Gender']
    
#     # Prepare input for classifier model
#     age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
#     # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
#     # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
#     # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
#     calculated_other_deductions = (
#         safe_float(financial_data.get('deduction_80ccc', 0)) +
#         safe_float(financial_data.get('deduction_80ccd', 0)) +
#         safe_float(financial_data.get('deduction_80ccd1b', 0)) +
#         safe_float(financial_data.get('deduction_80g', 0)) +
#         safe_float(financial_data.get('deduction_80tta', 0)) +
#         safe_float(financial_data.get('deduction_80ttb', 0))
#     )
#     calculated_other_deductions = round(calculated_other_deductions, 2)


#     classifier_input_data = {
#         'Age': age_value,
#         'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
#         'HRA Received': safe_float(financial_data.get('hra_received', 0)),
#         'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
#         'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
#         'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
#         'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
#         'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
#         'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
#         'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
#         'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
#         'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
#         'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
#         'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
#         'Gender': safe_string(financial_data.get('gender', 'Unknown'))
#     }
    
#     # Create DataFrame for classifier prediction, ensuring column order
#     # The order must match `model_trainer.py`'s `classifier_all_features`
#     ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
#     classifier_df = pd.DataFrame([classifier_input_data])
    
#     predicted_tax_regime = "N/A"
#     try:
#         classifier_df_processed = classifier_df[ordered_classifier_features]
#         predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
#         logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
#     except Exception as e:
#         logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
#         predicted_tax_regime = "Prediction Failed (Error)"
        
#     # Prepare input for regressor model
#     # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
#     regressor_input_data = {
#         k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
#     }
#     regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

#     regressor_df = pd.DataFrame([regressor_input_data])
    
#     predicted_tax_liability = 0.0
#     try:
#         # The regressor's preprocessor will handle the categorical feature conversion.
#         # Just ensure the input DataFrame has the correct columns and order.
#         ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
#         regressor_df_processed = regressor_df[ordered_regressor_features]
#         predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
#         logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
#     except Exception as e:
#         logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
#         predicted_tax_liability = 0.0 # Default to 0 if prediction fails

#     # Calculate refund/additional due based on ML prediction and actual TDS
#     total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

#     predicted_refund_due = 0.0
#     predicted_additional_due = 0.0

#     if total_tds_credit > predicted_tax_liability:
#         predicted_refund_due = total_tds_credit - predicted_tax_liability
#     elif total_tds_credit < predicted_tax_liability:
#         predicted_additional_due = predicted_tax_liability - total_tds_credit
        
#     # Convert any numpy types before returning
#     return convert_numpy_types({
#         "predicted_tax_regime": predicted_tax_regime,
#         "predicted_tax_liability": predicted_tax_liability,
#         "predicted_refund_due": round(predicted_refund_due, 2),
#         "predicted_additional_due": round(predicted_additional_due, 2),
#         "notes": "ML model predictions for optimal regime and tax liability."
#     })

# def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
#     """Generates tax-saving suggestions and regime analysis using Gemini API."""
#     if gemini_model is None:
#         logging.error("Gemini API (gemini_model) not initialized.")
#         return ["AI suggestions unavailable."], "AI regime analysis unavailable."

#     # If the document type is a Bank Statement, provide a generic suggestion
#     if aggregated_financial_data.get('identified_type') == 'Bank Statement' or \
#        ("Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]):
#         return (
#             ["For comprehensive tax analysis and personalized tax-saving suggestions, please upload tax-related documents such as Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts). Bank statements are primarily for transactional summaries."],
#             "Tax regime analysis requires complete income and deduction data, typically found in tax-specific documents."
#         )


#     # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
#     financial_data_for_gemini = aggregated_financial_data.copy()

#     # Add specific structure for Bank Statement details if identified as such, or if bank details are present
#     if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
#         financial_data_for_gemini['Bank Details'] = {
#             'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
#             'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
#             'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
#             'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
#             'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
#             'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
#             'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
#             'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
#         }
#         # Optionally, remove transaction_summary if it's too verbose for the prompt
#         # financial_data_for_gemini.pop('transaction_summary', None)


#     prompt = f"""
#     You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
#     Based on this data:
#     1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
#     2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

#     **Financial Data Summary:**
#     {json.dumps(financial_data_for_gemini, indent=2)}

#     **Final Tax Computation Summary:**
#     {json.dumps(final_tax_computation_summary, indent=2)}

#     Please format your response strictly as follows:
#     Suggestions:
#     - [Suggestion 1]
#     - [Suggestion 2]
#     ...
#     Regime Analysis: [Your analysis paragraph here].
#     """
#     try:
#         response = gemini_model.generate_content(prompt)
#         text = response.text.strip()
        
#         suggestions = []
#         regime_analysis = ""

#         # Attempt to parse the structured output
#         if "Suggestions:" in text and "Regime Analysis:" in text:
#             parts = text.split("Regime Analysis:")
#             suggestions_part = parts[0].replace("Suggestions:", "").strip()
#             regime_analysis = parts[1].strip()

#             # Split suggestions into bullet points and filter out empty strings
#             suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
#             if not suggestions: # If parsing as bullets failed, treat as single suggestion
#                 suggestions = [suggestions_part]
#         else:
#             # Fallback if format is not as expected, return raw text as suggestions
#             suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
#             regime_analysis = "AI could not parse structured regime analysis."
#             logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

#         return suggestions, regime_analysis
#     except Exception as e:
#         logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
#         return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

# def generate_itr_pdf(tax_record_data):
#     """
#     Generates a dummy ITR form PDF.
#     This uses a basic PDF string structure as a placeholder.
#     """
#     aggregated_data = tax_record_data.get('aggregated_financial_data', {})
#     final_computation = tax_record_data.get('final_tax_computation_summary', {})

#     # Determine ITR type (simplified logic)
#     itr_type = "ITR-1 (SAHAJ - DUMMY)"
#     if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
#        safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
#        safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
#         itr_type = "ITR-2 (DUMMY)"
    
#     # Extract key info for the dummy PDF
#     name = aggregated_data.get('name_of_employee', 'N/A')
#     pan = aggregated_data.get('pan_of_employee', 'N/A')
#     financial_year = aggregated_data.get('financial_year', 'N/A')
#     assessment_year = aggregated_data.get('assessment_year', 'N/A')
#     total_income = final_computation.get('computed_taxable_income', 'N/A')
#     tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
#     refund_due = final_computation.get('predicted_refund_due', 0.0)
#     tax_due = final_computation.get('predicted_additional_due', 0.0)
#     regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

#     # Add bank statement specific details to the PDF content if available
#     bank_details_for_pdf = ""
#     # Check if the aggregated data's identified type is 'Bank Statement' or if it contains core bank details
#     if aggregated_data.get('identified_type') == 'Bank Statement' or \
#        (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
#         bank_details_for_pdf = f"""
# BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
# BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
# """

#     # Core PDF content without xref and EOF for length calculation
#     core_pdf_content_lines = [
#         f"%PDF-1.4",
#         f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
#         f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
#         f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
#         f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
#         f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
#         f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
#         f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
#         f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
#         f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
#         f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
#         f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
#         f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
#         f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
#         f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
#     ]
    
#     # Append bank details if available
#     if bank_details_for_pdf:
#         core_pdf_content_lines.append(bank_details_for_pdf)
#         # Adjust vertical position for the Note if bank details were added
#         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
#     else:
#         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

#     core_pdf_content_lines.extend([
#         f"endstream",
#         f"endobj",
#         f"xref",
#         f"0 5",
#         f"0000000000 65535 f",
#         f"0000000010 00000 n",
#         f"0000000057 00000 n",
#         f"0000000114 00000 n",
#         f"0000000222 00000 n",
#         f"trailer <</Size 5 /Root 1 0 R>>",
#     ])
    
#     # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
#     core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
#     core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

#     # Calculate the startxref position
#     startxref_position = len(core_pdf_bytes)

#     # Now assemble the full PDF content including startxref and EOF
#     full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
#     # Final encode
#     dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

#     return io.BytesIO(dummy_pdf_content_bytes), itr_type


# # --- API Routes ---

# # Serves the main page (assuming index.html is in the root)
# @app.route('/')
# def home():
#     """Serves the main landing page, typically index.html."""
#     return send_from_directory('.', 'index.html')

# # Serves other static files (CSS, JS, images, etc.)
# @app.route('/<path:path>')
# def serve_static_files(path):
#     """Serves static files from the root directory."""
#     return send_from_directory('.', path)

# # Serves uploaded files from the uploads folder
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     """Allows access to temporarily stored uploaded files."""
#     try:
#         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#     except FileNotFoundError:
#         logging.warning(f"File '{filename}' not found in uploads folder.")
#         return jsonify({"message": "File not found"}), 404
#     except Exception as e:
#         logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
#         return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


# @app.route('/api/register', methods=['POST'])
# def register_user():
#     """Handles user registration."""
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')

#         if not username or not email or not password:
#             logging.warning("Registration attempt with missing fields.")
#             return jsonify({"message": "Username, email, and password are required"}), 400

#         # Check if email or username already exists
#         if users_collection.find_one({"email": email}):
#             logging.warning(f"Registration failed: Email '{email}' already exists.")
#             return jsonify({"message": "Email already exists"}), 409
#         if users_collection.find_one({"username": username}):
#             logging.warning(f"Registration failed: Username '{username}' already exists.")
#             return jsonify({"message": "Username already exists"}), 409

#         # Hash the password before storing
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         # Prepare user data for MongoDB insertion
#         new_user_data = {
#             "username": username,
#             "email": email,
#             "password": hashed_password.decode('utf-8'), # Store hashed password as string
#             "full_name": data.get('fullName', ''),
#             "pan": data.get('pan', ''),
#             "aadhaar": data.get('aadhaar', ''),
#             "address": data.get('address', ''),
#             "phone": data.get('phone', ''),
#             "created_at": datetime.utcnow()
#         }
#         # Insert the new user record and get the inserted ID
#         user_id = users_collection.insert_one(new_user_data).inserted_id
#         logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
#         return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
#     except Exception as e:
#         logging.error(f"Error during registration: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred during registration."}), 500

# @app.route('/api/login', methods=['POST'])
# def login_user():
#     """Handles user login and JWT token generation."""
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')

#         if not username or not password:
#             logging.warning("Login attempt with missing credentials.")
#             return jsonify({"error_msg": "Username and password are required"}), 400

#         # Find the user by username
#         user = users_collection.find_one({"username": username})

#         # Verify user existence and password
#         if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
#             # Create a JWT access token with the user's MongoDB ObjectId as identity
#             access_token = create_access_token(identity=str(user['_id']))
#             logging.info(f"User '{username}' logged in successfully.")
#             return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
#         else:
#             logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
#             return jsonify({"error_msg": "Invalid credentials"}), 401
#     except Exception as e:
#         logging.error(f"Error during login: {traceback.format_exc()}")
#         return jsonify({"error_msg": "An error occurred during login."}), 500

# @app.route('/api/profile', methods=['GET'])
# @jwt_required()
# def get_user_profile():
#     """Fetches the profile of the currently authenticated user."""
#     try:
#         # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
#         current_user_id = get_jwt_identity()
#         # Find user by ObjectId, exclude password from the result
#         user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
#         if not user:
#             logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
#             return jsonify({"message": "User not found"}), 404

#         # Convert ObjectId to string for JSON serialization
#         user['_id'] = str(user['_id'])
#         logging.info(f"Profile fetched for user ID: {current_user_id}")
#         return jsonify({"user": user}), 200
#     except Exception as e:
#         logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

# @app.route('/api/profile', methods=['PUT', 'PATCH'])
# @jwt_required()
# def update_user_profile():
#     """Updates the profile of the currently authenticated user."""
#     try:
#         current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#         data = request.get_json()

#         # Define allowed fields for update
#         updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
#         update_data = {k: data[k] for k in updatable_fields if k in data}

#         if not update_data:
#             logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
#             return jsonify({"message": "No fields to update provided."}), 400
        
#         # Prevent username from being updated via this route for security/simplicity
#         if 'username' in data:
#             logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

#         # If email is being updated, ensure it's not already in use by another user
#         if 'email' in update_data:
#             existing_user_with_email = users_collection.find_one({"email": update_data['email']})
#             if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
#                 logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
#                 return jsonify({"message": "Email already in use by another account."}), 409

#         # Perform the update operation in MongoDB
#         result = users_collection.update_one(
#             {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
#             {"$set": update_data}
#         )

#         if result.matched_count == 0:
#             logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
#             return jsonify({"message": "User not found."}), 404
#         if result.modified_count == 0:
#             logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
#             return jsonify({"message": "Profile data is the same, no changes made."}), 200

#         logging.info(f"Profile updated successfully for user ID: {current_user_id}")
#         return jsonify({"message": "Profile updated successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while updating your profile."}), 500


# @app.route('/api/process_documents', methods=['POST'])
# @jwt_required()
# def process_documents():
#     """
#     Handles uploaded documents, extracts financial data using Gemini and Vision API,
#     aggregates data from multiple files, computes tax, and saves the comprehensive
#     record to MongoDB, grouped by PAN and Financial Year.
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

#     if 'documents' not in request.files:
#         logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
#         return jsonify({"message": "No 'documents' part in the request"}), 400

#     files = request.files.getlist('documents')
#     if not files:
#         logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
#         return jsonify({"message": "No selected file"}), 400

#     extracted_data_from_current_upload = []
#     document_processing_summary_current_upload = [] # To provide feedback on each file

#     # Get the selected document type hint from the form data (if provided)
#     document_type_hint = request.form.get('document_type', 'Auto-Detect') 
#     logging.info(f"Received document type hint from frontend: {document_type_hint}")

#     for file in files:
#         if file.filename == '':
#             document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
#             continue
        
#         filename = secure_filename(file.filename)
#         # Create a unique filename for storing the original document
#         unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
#         try:
#             file_content_bytes = file.read() # Read content before saving
#             file.seek(0) # Reset file pointer for subsequent operations if needed

#             # Save the file temporarily (or permanently if you wish to retain originals)
#             with open(file_path, 'wb') as f:
#                 f.write(file_content_bytes)
#             logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

#             mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default

#             # Perform OCR if the file is an image or PDF
#             document_text_for_gemini = ""
#             if "image" in mime_type or "pdf" in mime_type:
#                 ocr_error, extracted_ocr_text = ocr_document(file_content_bytes)
#                 if ocr_error:
#                     logging.warning(f"OCR failed for {filename}: {ocr_error['error']}")
#                     document_processing_summary_current_upload.append({
#                         "filename": filename, "status": "failed", "message": f"OCR failed: {ocr_error['error']}",
#                         "identified_type": "OCR Failed", "stored_path": f"/uploads/{unique_filename}"
#                     })
#                     continue
#                 document_text_for_gemini = extracted_ocr_text
#             elif "text" in mime_type or "json" in mime_type:
#                 document_text_for_gemini = file_content_bytes.decode('utf-8')
#             else:
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "skipped", "identified_type": "Unsupported",
#                     "message": f"Unsupported file type: {mime_type}", "stored_path": f"/uploads/{unique_filename}"
#                 })
#                 continue

#             # Construct the base prompt for Gemini
#             # The actual document content is passed as a separate argument to extract_fields_with_gemini
#             # and is then formatted into the prompt_template inside that function.
#             # No need to build the full prompt string here.
            
#             error_gemini, extracted_data = extract_fields_with_gemini(document_text_for_gemini, document_type_hint)

#             if error_gemini:
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "failed", "message": f"AI processing error: {error_gemini['error']}",
#                     "identified_type": "AI Processing Failed", "stored_path": f"/uploads/{unique_filename}"
#                 })
#                 continue
            
#             # Add the path to the stored document for future reference in history
#             extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
#             extracted_data_from_current_upload.append(extracted_data)

#             document_processing_summary_current_upload.append({
#                 "filename": filename, "status": "success", "identified_type": extracted_data.get('identified_type', 'Unknown'),
#                 "message": "Processed successfully.", "extracted_fields": extracted_data,
#                 "stored_path": f"/uploads/{unique_filename}" 
#             })

#         except Exception as e:
#             logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
#             document_processing_summary_current_upload.append({
#                 "filename": filename, "status": "error",
#                 "message": f"An unexpected error occurred during file processing: {str(e)}",
#                 "stored_path": f"/uploads/{unique_filename}"
#             })
#             continue 

#     if not extracted_data_from_current_upload:
#         logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
#         return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

#     # --- Determine PAN and Financial Year for grouping ---
#     # Try to find PAN and FY from the currently uploaded documents first
#     pan_of_employee = "UNKNOWNPAN"
#     financial_year = "UNKNOWNFY"

#     for data in extracted_data_from_current_upload:
#         if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
#             pan_of_employee = safe_string(data["pan_of_employee"])
#         if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
#             financial_year = safe_string(data["financial_year"])
#         # If both are found, we can break early (or continue to see if a higher priority doc has them)
#         if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
#             break
    
#     # If still unknown, check if the user profile has a PAN.
#     if pan_of_employee == "UNKNOWNPAN":
#         user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
#         if user_profile and safe_string(user_profile.get("pan")) != "null":
#             pan_of_employee = safe_string(user_profile["pan"])
#             logging.info(f"Using PAN from user profile: {pan_of_employee}")
#         else:
#             # If PAN is still unknown, log a warning and use the placeholder
#             logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

#     # Derive financial year from assessment year if financial_year is null
#     if financial_year == "UNKNOWNFY":
#         for data in extracted_data_from_current_upload:
#             if safe_string(data.get("assessment_year")) != "null":
#                 try:
#                     ay_parts = safe_string(data["assessment_year"]).split('-')
#                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
#                         start_year = int(ay_parts[0]) -1
#                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
#                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
#                             financial_year = fy
#                             break
#                 except Exception:
#                     pass # Keep default if parsing fails
#         if financial_year == "UNKNOWNFY":
#             logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


#     # Try to find an existing record for this user, PAN, and financial year
#     existing_tax_record = tax_records_collection.find_one({
#         "user_id": current_user_id,
#         "aggregated_financial_data.pan_of_employee": pan_of_employee,
#         "aggregated_financial_data.financial_year": financial_year
#     })

#     if existing_tax_record:
#         logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
#         # Merge new extracted data with existing data
#         all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
#         all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

#         # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
#         updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
#         updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

#         # Clear previous AI/ML results as they need to be re-generated for the updated data
#         tax_records_collection.update_one(
#             {"_id": existing_tax_record["_id"]},
#             {"$set": {
#                 "extracted_documents_data": all_extracted_data_for_fy,
#                 "document_processing_summary": all_document_processing_summary_for_fy,
#                 "aggregated_financial_data": updated_aggregated_financial_data,
#                 "final_tax_computation_summary": updated_final_tax_computation_summary,
#                 "timestamp": datetime.utcnow(), # Update timestamp of last modification
#                 "suggestions_from_gemini": [], # Reset suggestions
#                 "gemini_regime_analysis": "null", # Reset regime analysis
#                 "ml_prediction_summary": {}, # Reset ML predictions
#             }}
#         )
#         record_id = existing_tax_record["_id"]
#         logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

#     else:
#         logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
#         # If no existing record, aggregate only the newly uploaded data
#         new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
#         new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

#         # Prepare the comprehensive tax record to save to MongoDB
#         tax_record_to_save = {
#             "user_id": current_user_id, 
#             "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
#             "financial_year": financial_year, # Store FY at top level for easy query
#             "timestamp": datetime.utcnow(),
#             "document_processing_summary": document_processing_summary_current_upload, 
#             "extracted_documents_data": extracted_data_from_current_upload, 
#             "aggregated_financial_data": new_aggregated_financial_data,
#             "final_tax_computation_summary": new_final_tax_computation_summary,
#             "suggestions_from_gemini": [], 
#             "gemini_regime_analysis": "null", 
#             "ml_prediction_summary": {},    
#         }
#         record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
#         logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
#         updated_aggregated_financial_data = new_aggregated_financial_data
#         updated_final_tax_computation_summary = new_final_tax_computation_summary


#     # Return success response with computed data
#     # Ensure all data sent back is JSON serializable (e.g., no numpy types)
#     response_data = {
#         "status": "success",
#         "message": "Documents processed and financial data aggregated and tax computed successfully",
#         "record_id": str(record_id), 
#         "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
#         "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
#         "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
#     }
#     return jsonify(response_data), 200


# @app.route('/api/get_suggestions', methods=['POST'])
# @jwt_required()
# def get_suggestions():
#     """
#     Generates AI-driven tax-saving suggestions and provides an ML prediction summary
#     based on a specific processed tax record (grouped by PAN/FY).
#     """
#     current_user_id = get_jwt_identity()

#     data = request.get_json()
#     record_id = data.get('record_id')

#     if not record_id:
#         logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
#         return jsonify({"message": "Record ID is required to get suggestions."}), 400

#     try:
#         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
#         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
#         if not tax_record:
#             logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
#         # Get the aggregated financial data and final tax computation summary from the record
#         aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
#         final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

#         # Generate suggestions and ML predictions
#         suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
#         ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

#         # Update the record in DB with generated suggestions and predictions
#         tax_records_collection.update_one(
#             {"_id": ObjectId(record_id)},
#             {"$set": {
#                 "suggestions_from_gemini": suggestions,
#                 "gemini_regime_analysis": regime_analysis,
#                 "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
#                 "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
#             }}
#         )
#         logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

#         return jsonify({
#             "status": "success",
#             "message": "AI suggestions and ML predictions generated successfully!",
#             "suggestions_from_gemini": suggestions,
#             "gemini_regime_analysis": regime_analysis,
#             "ml_prediction_summary": ml_prediction_summary # Already converted
#         }), 200

#     except Exception as e:
#         logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
#         # Fallback for ML prediction summary even if overall suggestions fail
#         ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
#         return jsonify({
#             "status": "error",
#             "message": "An error occurred while generating suggestions.",
#             "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
#             "gemini_regime_analysis": "An error occurred.",
#             "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
#         }), 500

# @app.route('/api/save_extracted_data', methods=['POST'])
# @jwt_required()
# def save_extracted_data():
#     """
#     Saves extracted and computed tax data to MongoDB.
#     This route can be used for explicit saving if `process_documents` doesn't
#     cover all saving scenarios or for intermediate saves.
#     NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
#     For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#     data = request.get_json()
#     if not data:
#         logging.warning(f"Save data request from user {current_user_id} with no data provided.")
#         return jsonify({"message": "No data provided to save"}), 400
#     try:
#         # This route might be less relevant with the new aggregation by PAN/FY,
#         # as `process_documents` handles the upsert logic.
#         # However, if used for manual saving of *already aggregated* data,
#         # ensure PAN and FY are part of `data.aggregated_financial_data`
#         # or extracted from the `data` directly.
        
#         # Example: Try to get PAN and FY from input data for consistency
#         input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
#         input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

#         # Check for existing record for upsert behavior
#         existing_record = tax_records_collection.find_one({
#             "user_id": current_user_id,
#             "aggregated_financial_data.pan_of_employee": input_pan,
#             "aggregated_financial_data.financial_year": input_fy
#         })

#         if existing_record:
#             # Update existing record
#             update_result = tax_records_collection.update_one(
#                 {"_id": existing_record["_id"]},
#                 {"$set": {
#                     **data, # Overwrite with new data, ensuring user_id and timestamp are also set
#                     "user_id": current_user_id,
#                     "timestamp": datetime.utcnow(),
#                     "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
#                     "financial_year": input_fy, # Ensure top-level FY is consistent
#                 }}
#             )
#             record_id = existing_record["_id"]
#             logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
#             if update_result.modified_count == 0:
#                 return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
#         else:
#             # Insert new record
#             data['user_id'] = current_user_id
#             data['timestamp'] = datetime.utcnow()
#             data['pan_of_employee'] = input_pan
#             data['financial_year'] = input_fy
#             record_id = tax_records_collection.insert_one(data).inserted_id
#             logging.info(f"New data saved for user {current_user_id} with record ID: {record_id}")
        
#         return jsonify({"message": "Data saved successfully", "record_id": str(record_id)}), 200
#     except Exception as e:
#         logging.error(f"Error saving data for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to save data", "error": str(e)}), 500

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
#             # Remove potentially large raw data fields for history list view to save bandwidth
#             record.pop('extracted_documents_data', None) 
#         logging.info(f"Found {len(records)} tax records for user {current_user_id}")
#         # The frontend's TaxHistory component expects a 'history' key in the response data.
#         return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200 # Convert numpy types
#     except Exception as e:
#         logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

# @app.route('/api/generate-itr/<record_id>', methods=['GET'])
# @jwt_required()
# def generate_itr_form_route(record_id):
#     """
#     Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
#     """
#     current_user_id = get_jwt_identity()
#     try:
#         record_obj_id = ObjectId(record_id) # Convert record_id string to ObjectId for DB query
#         # Ensure the tax record belongs to the current user (user_id check)
#         tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

#         if not tax_record:
#             logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or you are not authorized to access it."}), 404

#         # Generate the dummy PDF content
#         pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
#         pdf_buffer.seek(0) # Rewind the buffer to the beginning

#         response = send_file(
#             pdf_buffer,
#             mimetype='application/pdf',
#             as_attachment=True,
#             download_name=f"{itr_type.replace(' ', '_')}_{record_id}.pdf"
#         )
#         logging.info(f"Generated and sent dummy ITR form for record ID: {record_id}")
#         return response
#     except Exception as e:
#         logging.error(f"Error generating ITR form for record {record_id}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to generate ITR form.", "error": str(e)}), 500

# @app.route('/api/contact', methods=['POST'])
# def contact_message():
#     """Handles contact form submissions."""
#     try:
#         data = request.get_json()
#         name = data.get('name')
#         email = data.get('email')
#         subject = data.get('subject')
#         message = data.get('message')

#         if not all([name, email, subject, message]):
#             logging.warning("Contact form submission with missing fields.")
#             return jsonify({"message": "All fields are required."}), 400
        
#         # Insert contact message into MongoDB
#         contact_messages_collection.insert_one({
#             "name": name,
#             "email": email,
#             "subject": subject,
#             "message": message,
#             "timestamp": datetime.utcnow()
#         })
#         logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

#         return jsonify({"message": "Message sent successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while sending your message."}), 500

# # --- Main application entry point ---
# if __name__ == '__main__':
#     # Ensure MongoDB connection is established before running the app
#     if db is None:
#         logging.error("MongoDB connection failed at startup. Exiting.")
#         exit(1)
    
#     logging.info("Starting Flask application...")
#     # Run the Flask app
#     # debug=True enables reloader and debugger (should be False in production)
#     # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
#     # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
#     app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)












# import os
# import json
# from flask import Flask, request, jsonify, send_from_directory, send_file
# from flask_cors import CORS
# import google.generativeai as genai
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import bcrypt
# import traceback
# import logging
# import io
# from datetime import datetime, timedelta
# from google.cloud import vision
# from google.oauth2 import service_account
# from werkzeug.utils import secure_filename # Import secure_filename
# import joblib # Import joblib for loading ML models
# import pandas as pd # Import pandas for ML model input

# # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# import numpy as np

# # Import ReportLab components for PDF generation
# try:
#     # Commented out ReportLab imports as per previous turn, using dummy PDF for now.
#     # from reportlab.pdfgen import canvas
#     # from reportlab.lib.pagesizes import letter
#     # from reportlab.lib.units import inch
#     # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
#     # from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
#     # from reportlab.lib.enums import TA_CENTER
#     REPORTLAB_AVAILABLE = False # Set to False since using dummy PDF
# except ImportError:
#     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
#     REPORTLAB_AVAILABLE = False


# # Configure logging for better visibility
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Configuration (IMPORTANT: Using hardcoded keys as per user's request) ---
# # In a real-world production environment, these should ALWAYS be loaded from
# # environment variables (e.g., using os.getenv) and never hardcoded.
# GEMINI_API_KEY_HARDCODED = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs"
# MONGO_URI_HARDCODED = "mongodb://localhost:27017/"
# JWT_SECRET_KEY_HARDCODED = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# # Ensure the path for Vision API key is correct for your system. Use a raw string (r"")
# # or forward slashes (/) for paths to avoid issues with backslashes.
# VISION_API_KEY_PATH_HARDCODED = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json"

# # Initialize Flask app
# app = Flask(__name__)
# # Enable CORS for all origins, allowing frontend to communicate. For production, restrict this.
# CORS(app, supports_credentials=True) # Ensure supports_credentials is True for cookie/JWT handling



































































# import os
# import json
# from flask import Flask, request, jsonify, send_from_directory, send_file
# from flask_cors import CORS
# import google.generativeai as genai
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import bcrypt
# import traceback
# import logging
# import io
# from datetime import datetime, timedelta
# from google.cloud import vision
# from google.oauth2 import service_account
# from werkzeug.utils import secure_filename # Import secure_filename
# import joblib # Import joblib for loading ML models
# import pandas as pd # Import pandas for ML model input

# # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# import numpy as np

# # Import ReportLab components for PDF generation
# try:
#     # Commented out ReportLab imports as per previous turn, using dummy PDF for now.
#     # from reportlab.pdfgen import canvas
#     # from reportlab.lib.pagesizes import letter
#     # from reportlab.lib.units import inch
#     # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
#     # from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
#     # from reportlab.lib.enums import TA_CENTER
#     REPORTLAB_AVAILABLE = False # Set to False since using dummy PDF
# except ImportError:
#     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
#     REPORTLAB_AVAILABLE = False


# # Configure logging for better visibility
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Configuration (IMPORTANT: Using hardcoded keys as per user's request) ---
# # In a real-world production environment, these should ALWAYS be loaded from
# # environment variables (e.g., using os.getenv) and never hardcoded.
# GEMINI_API_KEY_HARDCODED = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs"
# MONGO_URI_HARDCODED = "mongodb://localhost:27017/"
# JWT_SECRET_KEY_HARDCODED = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# # Ensure the path for Vision API key is correct for your system. Use a raw string (r"")
# # or forward slashes (/) for paths to avoid issues with backslashes.
# VISION_API_KEY_PATH_HARDCODED = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json"

# # Initialize Flask app
# app = Flask(__name__)
# # Enable CORS for all origins, allowing frontend to communicate. For production, restrict this.
# CORS(app)

# # --- JWT Configuration ---
# app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY_HARDCODED
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Tokens expire in 24 hours
# from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# jwt = JWTManager(app)

# # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# @jwt.expired_token_loader
# def expired_token_callback(jwt_header, jwt_payload):
#     logging.warning("JWT token expired.")
#     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# @jwt.invalid_token_loader
# def invalid_token_callback(callback_error):
#     logging.warning(f"Invalid JWT token: {callback_error}")
#     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# @jwt.unauthorized_loader
# def unauthorized_callback(callback_error):
#     logging.warning(f"Unauthorized access attempt: {callback_error}")
#     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401
# # --- End JWT Configuration ---


# # --- MongoDB Connection ---
# client = None
# db = None
# users_collection = None
# tax_records_collection = None
# contact_messages_collection = None

# try:
#     client = MongoClient(MONGO_URI_HARDCODED)
#     db = client['garudatax_db'] # Using a more specific database name for tax application
#     users_collection = db['users']
#     tax_records_collection = db['tax_records'] # This collection will store aggregated records per FY
#     contact_messages_collection = db['contact_messages']
#     logging.info("MongoDB connected successfully.")
# except Exception as e:
#     logging.error(f"Error connecting to MongoDB: {traceback.format_exc()}")
#     db = None # Ensure db is None if connection fails, so app can handle it gracefully.


# # --- Google Cloud Vision API Configuration ---
# vision_client = None
# try:
#     if not os.path.exists(VISION_API_KEY_PATH_HARDCODED):
#         logging.error(f"Vision API key file not found at: {VISION_API_KEY_PATH_HARDCODED}. Vision features will be disabled.")
#     else:
#         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH_HARDCODED)
#         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
#         logging.info("Google Cloud Vision API client initialized successfully.")
# except Exception as e:
#     logging.error(f"Error initializing Google Cloud Vision API client: {traceback.format_exc()}. Vision features will be disabled.")
#     vision_client = None


# # --- Google Gemini API Configuration ---
# # Ensure API key is set before configuring Gemini
# if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
#     logging.error("GEMINI_API_KEY is not set or is still the placeholder! Gemini features will not work.")
# genai.configure(api_key=GEMINI_API_KEY_HARDCODED)

# # Initialize Gemini models. Using gemini-2.0-flash for multimodal capabilities (though OCR is done by Vision first).
# gemini_pro_model = genai.GenerativeModel('gemini-2.0-flash')
# logging.info("Google Gemini API client initialized.")


# # --- UPLOAD FOLDER CONFIGURATION ---
# # Define the upload folder relative to the current working directory
# UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Create UPLOAD_FOLDER if it doesn't exist. exist_ok=True prevents error if it already exists.
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")
# # --- END UPLOAD FOLDER CONFIGURATION ---

# # --- ML Model Loading ---
# # Load trained ML models for tax regime classification and tax liability regression
# tax_regime_classifier_model = None
# tax_regressor_model = None

# try:
#     # Ensure these .pkl files are generated by running model_trainer.py first.
#     # Make sure xgboost is installed in your environment for model_trainer.py
#     classifier_path = 'tax_regime_classifier_model.pkl'
#     if os.path.exists(classifier_path):
#         tax_regime_classifier_model = joblib.load(classifier_path)
#         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
#     else:
#         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

#     regressor_path = 'final_tax_regressor_model.pkl'
#     if os.path.exists(regressor_path):
#         tax_regressor_model = joblib.load(regressor_path)
#         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
#     else:
#         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# except Exception as e:
#     logging.error(f"Error loading ML models: {traceback.format_exc()}")
#     tax_regime_classifier_model = None
#     tax_regressor_model = None


# # --- Helper Functions ---

# def convert_numpy_types(obj):
#     """
#     Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
#     This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
#     """
#     if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
#         return obj.item() # Converts numpy scalar to Python scalar
#     elif isinstance(obj, dict):
#         return {k: convert_numpy_types(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_numpy_types(elem) for elem in obj]
#     else:
#         return obj

# def extract_text_with_vision_api(image_bytes):
#     """
#     Uses Google Cloud Vision API to perform OCR on image bytes and return the full text.
#     Requires `vision_client` to be initialized.
#     """
#     if vision_client is None:
#         logging.error("Google Cloud Vision client is not initialized. Cannot perform OCR.")
#         raise RuntimeError("OCR service unavailable.")
#     try:
#         image = vision.Image(content=image_bytes)
#         # Using document_text_detection for comprehensive text extraction from documents
#         response = vision_client.document_text_detection(image=image)
#         if response.full_text_annotation:
#             logging.info("Successfully extracted text using Google Cloud Vision API.")
#             return response.full_text_annotation.text
#         else:
#             logging.warning("Google Cloud Vision API returned no full text annotation.")
#             return ""
#     except Exception as e:
#         logging.error(f"Error extracting text with Vision API: {traceback.format_exc()}")
#         raise # Re-raise the exception to be handled by the calling function

# def get_gemini_response(prompt_text, file_data=None, mime_type=None, filename="unknown_file"):
#     """
#     Sends a prompt to Gemini and returns the structured JSON response.
#     If image/pdf data is provided, it first uses Vision API for OCR.
#     The response is strictly expected in a JSON format based on the defined schema.
#     """
#     try:
#         final_prompt_content = prompt_text
        
#         if file_data and mime_type and ("image" in mime_type or "pdf" in mime_type):
#             # If image or PDF, first extract text using Vision API
#             extracted_text_from_vision = extract_text_with_vision_api(file_data)
#             final_prompt_content += f"\n\n--- Document Content for Extraction ---\n{extracted_text_from_vision}"
#             logging.info(f"Feeding Vision API extracted text to Gemini for '{filename}'.")
            
#         else:
#             # For pure text inputs, assume prompt_text already contains all necessary info
#             logging.info(f"Processing text content directly with Gemini for '{filename}'.")
        
#         # --- DEFINITIVE JSON SCHEMA FOR GEMINI OUTPUT ---
#         # This schema MUST be comprehensive and match all keys expected by your frontend.
#         # Gemini will attempt to adhere to this schema and fill in defaults.
#         # Ensure all fields are explicitly defined to help Gemini produce consistent output.
#         response_schema = {
#             "type": "OBJECT",
#             "properties": {
#                 "identified_type": {"type": "STRING", "description": "Type of document, e.g., 'Form 16', 'Bank Statement', 'Form 26AS', 'Salary Slip', 'Investment Proof', 'Home Loan Statement', 'Other Document'. Choose the most relevant one if possible."},
#                 "employer_name": {"type": "STRING", "description": "Name of the Employer"},
#                 "employer_address": {"type": "STRING", "description": "Address of the Employer"},
#                 "pan_of_deductor": {"type": "STRING", "description": "PAN of the Employer (Deductor)"},
#                 "tan_of_deductor": {"type": "STRING", "description": "TAN of the Employer (Deductor)"},
#                 "name_of_employee": {"type": "STRING", "description": "Name of the Employee/Assessee"},
#                 "designation_of_employee": {"type": "STRING", "description": "Designation of the Employee"},
#                 "pan_of_employee": {"type": "STRING", "description": "PAN of the Employee/Assessee"},
#                 "date_of_birth": {"type": "STRING", "format": "date-time", "description": "Date of Birth (YYYY-MM-DD)"},
#                 "gender": {"type": "STRING", "description": "Gender (e.g., 'Male', 'Female', 'Other')"},
#                 "residential_status": {"type": "STRING", "description": "Residential Status (e.g., 'Resident', 'Non-Resident')"},
#                 "assessment_year": {"type": "STRING", "description": "Income Tax Assessment Year (e.g., '2024-25')"},
#                 "financial_year": {"type": "STRING", "description": "Financial Year (e.g., '2023-24')"},
#                 "period_from": {"type": "STRING", "format": "date-time", "description": "Start date of the document period (YYYY-MM-DD)"},
#                 "period_to": {"type": "STRING", "format": "date-time", "description": "End date of the document period (YYYY-MM-DD)"},
#                 "quarter_1_receipt_number": {"type": "STRING"},
#                 "quarter_1_tds_deducted": {"type": "NUMBER"},
#                 "quarter_1_tds_deposited": {"type": "NUMBER"},
#                 "total_tds_deducted_summary": {"type": "NUMBER", "description": "Total TDS deducted from salary (Form 16 Part A)"},
#                 "total_tds_deposited_summary": {"type": "NUMBER", "description": "Total TDS deposited from salary (Form 16 Part A)"},
#                 "salary_as_per_sec_17_1": {"type": "NUMBER", "description": "Salary as per Section 17(1)"},
#                 "value_of_perquisites_u_s_17_2": {"type": "NUMBER", "description": "Value of perquisites u/s 17(2)"},
#                 "profits_in_lieu_of_salary_u_s_17_3": {"type": "NUMBER", "description": "Profits in lieu of salary u/s 17(3)"},
#                 "gross_salary_total": {"type": "NUMBER", "description": "Total Gross Salary (sum of 17(1), 17(2), 17(3) from Form 16, or derived from payslip total earnings)"},
#                 "conveyance_allowance": {"type": "NUMBER"},
#                 "transport_allowance": {"type": "NUMBER"},
#                 "total_exempt_allowances": {"type": "NUMBER", "description": "Total allowances exempt u/s 10"},
#                 "balances_1_2": {"type": "NUMBER", "description": "Balance after subtracting allowances from gross salary"},
#                 "professional_tax": {"type": "NUMBER", "description": "Professional Tax"},
#                 "aggregate_of_deductions_from_salary": {"type": "NUMBER", "description": "Total deductions from salary (e.g., Prof Tax, Standard Deduction)"},
#                 "income_chargable_under_head_salaries": {"type": "NUMBER", "description": "Income chargeable under 'Salaries'"},
#                 "income_from_house_property": {"type": "NUMBER", "description": "Income From House Property (can be negative for loss)"},
#                 "income_from_other_sources": {"type": "NUMBER", "description": "Income From Other Sources (e.g., interest, dividend)"},
#                 "interest_on_housing_loan_self_occupied": {"type": "NUMBER", "description": "Interest on Housing Loan - Self Occupied Property"},
#                 "capital_gains_long_term": {"type": "NUMBER", "description": "Long Term Capital Gains"},
#                 "capital_gains_short_term": {"type": "NUMBER", "description": "Short Term Capital Gains"},
#                 "gross_total_income_as_per_document": {"type": "NUMBER", "description": "Gross total income as stated in the document"},
#                 "deduction_80c": {"type": "NUMBER", "description": "Total deduction under Section 80C (includes EPF, PPF, LIC, etc.)"},
#                 "deduction_80c_epf": {"type": "NUMBER", "description": "EPF contribution under 80C"},
#                 "deduction_80c_insurance_premium": {"type": "NUMBER", "description": "Life Insurance Premium under 80C"},
#                 "deduction_80ccc": {"type": "NUMBER", "description": "Deduction for contribution to certain pension funds under Section 80CCC"},
#                 "deduction_80ccd": {"type": "NUMBER", "description": "Deduction for contribution to NPS under Section 80CCD"},
#                 "deduction_80ccd1b": {"type": "NUMBER", "description": "Additional deduction under Section 80CCD(1B) for NPS"},
#                 "deduction_80d": {"type": "NUMBER", "description": "Deduction for Health Insurance Premium under Section 80D"},
#                 "deduction_80g": {"type": "NUMBER", "description": "Deduction for Donations under Section 80G"},
#                 "deduction_80tta": {"type": "NUMBER", "description": "Deduction for Interest on Savings Account under Section 80TTA"},
#                 "deduction_80ttb": {"type": "NUMBER", "description": "Deduction for Interest for Senior Citizens under Section 80TTB"},
#                 "deduction_80e": {"type": "NUMBER", "description": "Deduction for Interest on Education Loan under Section 80E"},
#                 "total_deductions_chapter_via": {"type": "NUMBER", "description": "Total of all deductions under Chapter VI-A"},
#                 "taxable_income_as_per_document": {"type": "NUMBER", "description": "Taxable Income as stated in the document"},
#                 "tax_payable_as_per_document": {"type": "NUMBER", "description": "Final tax payable as stated in the document"},
#                 "refund_status_as_per_document": {"type": "STRING", "description": "Refund status as stated in the document (e.g., 'Refund due', 'Tax payable', 'No demand no refund')"},
#                 "tax_regime_chosen": {"type": "STRING", "description": "Tax Regime Chosen (e.g., 'Old Regime' or 'New Regime' if explicitly indicated in document)"},
#                 "total_tds": {"type": "NUMBER", "description": "Total TDS credit from all sources (e.g., Form 26AS, Form 16 Part A)"},
#                 "advance_tax": {"type": "NUMBER", "description": "Advance Tax paid"},
#                 "self_assessment_tax": {"type": "NUMBER", "description": "Self-Assessment Tax paid"},
                
#                 # --- NEW PAYSLIP SPECIFIC FIELDS ---
#                 "basic_salary": {"type": "NUMBER", "description": "Basic Salary component from payslip"},
#                 "hra_received": {"type": "NUMBER", "description": "House Rent Allowance (HRA) received from payslip"},
#                 "epf_contribution": {"type": "NUMBER", "description": "Employee Provident Fund (EPF) contribution from payslip"},
#                 "esi_contribution": {"type": "NUMBER", "description": "Employee State Insurance (ESI) contribution from payslip"},
#                 "net_amount_payable": {"type": "NUMBER", "description": "Net amount payable (take home pay) from payslip"},
#                 "overtime_pay": {"type": "NUMBER", "description": "Overtime pay from payslip"},
#                 "overtime_hours": {"type": "STRING", "description": "Overtime hours from payslip (e.g., '100-0 Hrs')"},
#                 "days_present": {"type": "STRING", "description": "Days present from payslip (e.g., '250 Days')"},

#                 # Additional fields for Bank Statements (if applicable)
#                 "account_holder_name": {"type": "STRING", "description": "Name of the account holder"},
#                 "account_number": {"type": "STRING", "description": "Bank account number"},
#                 "ifsc_code": {"type": "STRING", "description": "IFSC code of the bank branch"},
#                 "bank_name": {"type": "STRING", "description": "Name of the bank"},
#                 "branch_address": {"type": "STRING", "description": "Address of the bank branch"},
#                 "statement_start_date": {"type": "STRING", "format": "date-time", "description": "Start date of the bank statement period (YYYY-MM-DD)"},
#                 "statement_end_date": {"type": "STRING", "format": "date-time", "description": "End date of the bank statement period (YYYY-MM-DD)"},
#                 "opening_balance": {"type": "NUMBER", "description": "Opening balance on the statement"},
#                 "closing_balance": {"type": "NUMBER", "description": "Closing balance on the statement"},
#                 "total_deposits": {"type": "NUMBER", "description": "Total deposits during the statement period"},
#                 "total_withdrawals": {"type": "NUMBER", "description": "Total withdrawals during the statement period"},
#                 "transaction_summary": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"date": {"type": "STRING", "format": "date-time", "description": "Date of the transaction (YYYY-MM-DD)"}, "description": {"type": "STRING"}, "amount": {"type": "NUMBER"}}}, "description": "A summary or key entries of transactions from the statement (e.g., large deposits/withdrawals)."}
#             },
#             "required": ["identified_type"] # Minimum required field from Gemini's side
#         }

#         generation_config = {
#             "response_mime_type": "application/json",
#             "response_schema": response_schema
#         }
        
#         # Call Gemini model with the prompt and schema
#         response = genai.GenerativeModel('gemini-2.0-flash').generate_content([{"text": final_prompt_content}], generation_config=generation_config)

#         if not response.text:
#             logging.warning(f"Gemini returned an empty response text for {filename}.")
#             # Return an error with an empty dictionary for extracted_data to prevent KeyError
#             return json.dumps({"error": "Empty response from AI.", "extracted_data": {}})

#         # Clean the response text from markdown fences (```json ... ```) if present
#         response_text_cleaned = response.text.strip()
#         if response_text_cleaned.startswith("```json") and response_text_cleaned.endswith("```"):
#             response_text_cleaned = response_text_cleaned[len("```json"):].rstrip("```").strip()
#             logging.info("Stripped markdown JSON fences from Gemini response.")

#         try:
#             # Parse the cleaned JSON response from Gemini
#             parsed_json = json.loads(response_text_cleaned)
            
#             # --- CRITICAL FIX: Ensure all keys from schema are present and correctly typed ---
#             extracted_data = parsed_json # Gemini should return directly according to schema
#             final_extracted_data = {}

#             for key, prop_details in response_schema['properties'].items():
#                 if key in extracted_data and extracted_data[key] is not None:
#                     # Safely convert to the expected type
#                     if prop_details['type'] == 'NUMBER':
#                         final_extracted_data[key] = safe_float(extracted_data[key])
#                     elif prop_details['type'] == 'STRING':
#                         # Special handling for date formats if needed, otherwise just safe_string
#                         if 'format' in prop_details and prop_details['format'] == 'date-time':
#                             # Attempt to parse date, default if unable
#                             try:
#                                 dt_obj = datetime.strptime(str(extracted_data[key]).split('T')[0], '%Y-%m-%d')
#                                 final_extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
#                             except ValueError:
#                                 final_extracted_data[key] = "0000-01-01" # Default invalid date string
#                         else:
#                             final_extracted_data[key] = safe_string(extracted_data[key])
#                     elif prop_details['type'] == 'ARRAY':
#                         if key == "transaction_summary" and isinstance(extracted_data[key], list):
#                             # Process each transaction summary item
#                             processed_transactions = []
#                             for item in extracted_data[key]:
#                                 processed_item = {
#                                     "date": "0000-01-01", # Default date for transaction
#                                     "description": safe_string(item.get("description")),
#                                     "amount": safe_float(item.get("amount"))
#                                 }
#                                 if 'date' in item and item['date'] is not None:
#                                     try:
#                                         # Assuming transaction date might be YYYY-MM-DD or similar
#                                         dt_obj = datetime.strptime(str(item['date']).split('T')[0], '%Y-%m-%d')
#                                         processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
#                                     except ValueError:
#                                         pass # Keep default if parsing fails
#                                 processed_transactions.append(processed_item)
#                             final_extracted_data[key] = processed_transactions
#                         else:
#                             final_extracted_data[key] = extracted_data[key] if isinstance(extracted_data[key], list) else []
#                     else: # Fallback for other types
#                         final_extracted_data[key] = extracted_data[key]
#                 else:
#                     # Set default based on schema's type
#                     if prop_details['type'] == 'NUMBER':
#                         final_extracted_data[key] = 0.0
#                     elif prop_details['type'] == 'STRING':
#                         if 'format' in prop_details and prop_details['format'] == 'date-time':
#                             final_extracted_data[key] = "0000-01-01" # Default date string
#                         else:
#                             final_extracted_data[key] = "null" # Use string "null" as per schema description
#                     elif prop_details['type'] == 'ARRAY':
#                         final_extracted_data[key] = []
#                     else:
#                         final_extracted_data[key] = None # Generic default if type is not recognized

#             logging.info(f"Successfully retrieved and validated structured info from Gemini for {filename}.")
#             return json.dumps({"error": None, "extracted_data": final_extracted_data})
#         except json.JSONDecodeError:
#             logging.error(f"Gemini response was not valid JSON for {filename}. Raw response: {response_text_cleaned[:500]}...")
#             return json.dumps({"error": "Invalid JSON format from AI", "extracted_data": {"raw_text_response": response_text_cleaned}})
#         except Exception as e:
#             logging.error(f"Error processing Gemini's parsed JSON for {filename}: {traceback.format_exc()}")
#             return json.dumps({"error": f"Error processing AI data: {str(e)}", "extracted_data": {}})

#     except Exception as e:
#         logging.error(f"Overall error in get_gemini_response for {filename}: {traceback.format_exc()}")
#         return json.dumps({"error": str(e), "extracted_data": {}})

# def safe_float(val):
#     """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
#     Handles commas and currency symbols."""
#     try:
#         if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
#             return 0.0
#         if isinstance(val, str):
#             # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
#             # This handles values like "₹7,20,000.00", "720,000.00", "720000"
#             val = val.replace(',', '').replace('₹', '').strip()
            
#         return float(val)
#     except (ValueError, TypeError):
#         logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
#         return 0.0

# def safe_string(val):
#     """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
#     if val is None:
#         return "null"
#     s_val = str(val).strip()
#     if s_val == "":
#         return "null"
#     return s_val

# def _aggregate_financial_data(extracted_data_list):
#     """
#     Aggregates financial data from multiple extracted documents, applying reconciliation rules.
#     Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
#     """
    
#     aggregated_data = {
#         # Initialize all fields that are expected in the final aggregated output
#         "identified_type": "Other Document", # Overall identified type if mixed documents
#         "employer_name": "null", "employer_address": "null",
#         "pan_of_deductor": "null", "tan_of_deductor": "null",
#         "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
#         "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
#         "assessment_year": "null", "financial_year": "null",
#         "period_from": "0000-01-01", "period_to": "0000-01-01",
        
#         # Income Components - These should be summed
#         "basic_salary": 0.0,
#         "hra_received": 0.0,
#         "conveyance_allowance": 0.0,
#         "transport_allowance": 0.0,
#         "overtime_pay": 0.0,
#         "salary_as_per_sec_17_1": 0.0,
#         "value_of_perquisites_u_s_17_2": 0.0,
#         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
#         "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

#         "income_from_house_property": 0.0,
#         "income_from_other_sources": 0.0,
#         "capital_gains_long_term": 0.0,
#         "capital_gains_short_term": 0.0,

#         # Deductions - These should be summed, capped later if needed
#         "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
#         "professional_tax": 0.0,
#         "interest_on_housing_loan_self_occupied": 0.0,
#         "deduction_80c": 0.0,
#         "deduction_80c_epf": 0.0,
#         "deduction_80c_insurance_premium": 0.0,
#         "deduction_80ccc": 0.0,
#         "deduction_80ccd": 0.0,
#         "deduction_80ccd1b": 0.0,
#         "deduction_80d": 0.0,
#         "deduction_80g": 0.0,
#         "deduction_80tta": 0.0,
#         "deduction_80ttb": 0.0,
#         "deduction_80e": 0.0,
#         "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
#         "epf_contribution": 0.0, # Initialize epf_contribution
#         "esi_contribution": 0.0, # Initialize esi_contribution


#         # Tax Paid
#         "total_tds": 0.0,
#         "advance_tax": 0.0,
#         "self_assessment_tax": 0.0,
#         "total_tds_deducted_summary": 0.0, # From Form 16 Part A

#         # Document Specific (Non-summable, usually taken from most authoritative source)
#         "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

#         # Bank Account Details (Take from the most complete or latest if multiple)
#         "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
#         "bank_name": "null", "branch_address": "null",
#         "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
#         "opening_balance": 0.0, "closing_balance": 0.0,
#         "total_deposits": 0.0, "total_withdrawals": 0.0,
#         "transaction_summary": [], # Aggregate all transactions

#         # Other fields from the schema, ensuring they exist
#         "net_amount_payable": 0.0,
#         "days_present": "null",
#         "overtime_hours": "null",

#         # Calculated fields for frontend
#         "Age": "N/A", 
#         "total_gross_income": 0.0, # Overall sum of all income heads
#         "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
#         "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
#         "deduction_80C": 0.0, # Alias for deduction_80c
#         "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
#         "deduction_80D": 0.0, # Alias for deduction_80d
#         "deduction_80G": 0.0, # Alias for deduction_80g
#         "deduction_80TTA": 0.0, # Alias for deduction_80tta
#         "deduction_80TTB": 0.0, # Alias for deduction_80ttb
#         "deduction_80E": 0.0, # Alias for deduction_80e
#         "total_deductions": 0.0, # Overall total deductions used in calculation
#     }

#     # Define document priority for overriding fields (higher value means higher priority)
#     # Form 16 should provide definitive income/deduction figures.
#     doc_priority = {
#         "Form 16": 5,
#         "Form 26AS": 4,
#         "Salary Slip": 3,
#         "Investment Proof": 2,
#         "Home Loan Statement": 2,
#         "Bank Statement": 1,
#         "Other Document": 0,
#         "Unknown": 0,
#         "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
#     }

#     # Sort documents by priority (higher priority first)
#     sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

#     # Use a dictionary to track which field was last set by which document priority
#     # This helps in overriding with higher-priority document data.
#     field_source_priority = {key: -1 for key in aggregated_data}

#     # Iterate through sorted documents and aggregate data
#     for data in sorted_extracted_data:
#         doc_type = safe_string(data.get('identified_type'))
#         current_priority = doc_priority.get(doc_type, 0)
#         logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

#         # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
#         # Otherwise, individual components will be summed later.
#         extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
#         if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
#             aggregated_data["gross_salary_total"] = extracted_gross_salary_total
#             field_source_priority["gross_salary_total"] = current_priority
#             logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

#         # Update core personal details only from highest priority document or if current is 'null'
#         personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
#         for p_field in personal_fields:
#             if safe_string(data.get(p_field)) != "null" and \
#                (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
#                 aggregated_data[p_field] = safe_string(data.get(p_field))
#                 field_source_priority[p_field] = current_priority


#         for key, value in data.items():
#             # Skip keys already handled explicitly or which have specific aggregation logic
#             if key in personal_fields or key == "gross_salary_total":
#                 continue 
#             if key == "transaction_summary":
#                 if isinstance(value, list):
#                     aggregated_data[key].extend(value)
#                 continue
#             if key == "identified_type":
#                 # Ensure highest priority identified_type is kept
#                 if current_priority > field_source_priority.get(key, -1):
#                     aggregated_data[key] = safe_string(value)
#                     field_source_priority[key] = current_priority
#                 continue
            
#             # General handling for numerical fields: sum them up
#             if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
#                 # Special handling for bank balances: take from latest/highest priority statement
#                 if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
#                     if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
#                         # Only update if the current document is a bank statement and has higher or equal priority
#                         # (or if the existing aggregated value is 0)
#                         if current_priority >= field_source_priority.get(key, -1):
#                             aggregated_data[key] = safe_float(value)
#                             field_source_priority[key] = current_priority
#                     else: # For other document types, just sum the numbers if they appear
#                         aggregated_data[key] += safe_float(value)
#                 else:
#                     aggregated_data[key] += safe_float(value)
#             # General handling for string fields: take from highest priority document
#             elif key in aggregated_data and isinstance(aggregated_data[key], str):
#                 if safe_string(value) != "null" and safe_string(value) != "" and \
#                    (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
#                     aggregated_data[key] = safe_string(value)
#                     field_source_priority[key] = current_priority
#             # Default for other types if they are not explicitly handled
#             elif key in aggregated_data and value is not None:
#                 if current_priority > field_source_priority.get(key, -1):
#                     aggregated_data[key] = value
#                     field_source_priority[key] = current_priority

#     # --- Post-aggregation calculations and reconciliation ---
    
#     # Calculate `total_gross_income` (overall income from all heads)
#     # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
#     # try to derive it from payslip components like basic, HRA, etc.
#     if aggregated_data["gross_salary_total"] == 0.0:
#         aggregated_data["gross_salary_total"] = (
#             safe_float(aggregated_data["basic_salary"]) +
#             safe_float(aggregated_data["hra_received"]) +
#             safe_float(aggregated_data["conveyance_allowance"]) +
#             safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
#             safe_float(aggregated_data["overtime_pay"]) +
#             safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
#             safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
#         )
#         # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
#         # Assuming extracted values are already annual or normalized.

#     # Now calculate the comprehensive total_gross_income for tax computation
#     aggregated_data["total_gross_income"] = (
#         safe_float(aggregated_data["gross_salary_total"]) +
#         safe_float(aggregated_data["income_from_house_property"]) +
#         safe_float(aggregated_data["income_from_other_sources"]) + 
#         safe_float(aggregated_data["capital_gains_long_term"]) +
#         safe_float(aggregated_data["capital_gains_short_term"])
#     )
#     aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

#     # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
#     # This prevents double counting if EPF is reported separately and also included in 80C
#     # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
#     # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
#     # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
#     if safe_float(aggregated_data["epf_contribution"]) > 0:
#         aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
#     # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
#     aggregated_data["total_deductions_chapter_via"] = (
#         safe_float(aggregated_data["deduction_80c"]) +
#         safe_float(aggregated_data["deduction_80ccc"]) +
#         safe_float(aggregated_data["deduction_80ccd"]) +
#         safe_float(aggregated_data["deduction_80ccd1b"]) +
#         safe_float(aggregated_data["deduction_80d"]) + # Corrected to use deduction_80d_actual later if needed
#         safe_float(aggregated_data["deduction_80g"]) +
#         safe_float(aggregated_data["deduction_80tta"]) +
#         safe_float(aggregated_data["deduction_80ttb"]) +
#         safe_float(aggregated_data["deduction_80e"])
#     )
#     aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


#     # Aliases for frontend (ensure these are correctly populated from derived values)
#     aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
#     # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
#     # This is a fallback and might not always reflect actual exemptions as per tax rules.
#     if aggregated_data["total_exempt_allowances"] == 0.0:
#         aggregated_data["total_exempt_allowances"] = (
#             safe_float(aggregated_data.get("conveyance_allowance")) +
#             safe_float(aggregated_data.get("transport_allowance")) +
#             safe_float(aggregated_data.get("hra_received")) 
#         )
#         logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

#     # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
#     # This is a fixed amount applied during tax calculation, not a sum from documents.
#     aggregated_data["standard_deduction"] = 50000.0 

#     # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
#     dob_str = safe_string(aggregated_data.get("date_of_birth"))
#     if dob_str != "null" and dob_str != "0000-01-01":
#         try:
#             dob = datetime.strptime(dob_str, '%Y-%m-%d')
#             today = datetime.now()
#             age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#             aggregated_data["Age"] = age
#         except ValueError:
#             logging.warning(f"Could not parse date_of_birth: {dob_str}")
#             aggregated_data["Age"] = "N/A"
#     else:
#         aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

#     # Populate aliases for frontend display consistency
#     aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
#     aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
#     aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
#     aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
#     aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
#     aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
#     aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
#     aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
#     aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

#     # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
#     # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
#     # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
#     # For display, we can show sum of what's *claimed* or *extracted*.
#     # Let's make `total_deductions` a sum of all potential deductions for display.
#     aggregated_data["total_deductions"] = (
#         aggregated_data["standard_deduction"] + 
#         aggregated_data["professional_tax"] +
#         aggregated_data["interest_on_housing_loan_self_occupied"] +
#         aggregated_data["total_deductions_chapter_via"]
#     )
#     aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


#     # Sort all_transactions by date (oldest first)
#     for tx in aggregated_data['transaction_summary']:
#         if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
#             try:
#                 tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
#             except ValueError:
#                 tx['date_sortable'] = datetime.min # Fallback for unparseable dates
#         else:
#             tx['date_sortable'] = datetime.min

#     aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
#     # Remove the temporary sortable key
#     for tx in aggregated_data['transaction_summary']:
#         tx.pop('date_sortable', None)

#     # If identified_type is still "null" or "Unknown" and some other fields populated,
#     # try to infer a better type if possible, or leave as "Other Document"
#     if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
#         if safe_string(aggregated_data.get('employer_name')) != "null" and \
#            safe_float(aggregated_data.get('gross_salary_total')) > 0:
#            aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
#         elif safe_string(aggregated_data.get('account_number')) != "null" and \
#              (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
#              aggregated_data["identified_type"] = "Bank Statement"
#         elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
#              safe_float(aggregated_data.get('hra_received')) > 0 or \
#              safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
#              aggregated_data["identified_type"] = "Salary Slip"

#     # Ensure PAN and Financial Year are properly set for database grouping
#     # If not extracted, try to get from previous records or default to "null"
#     if safe_string(aggregated_data.get("pan_of_employee")) == "null":
#         aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

#     # Derive financial year from assessment year if financial_year is null
#     if safe_string(aggregated_data.get("financial_year")) == "null" and safe_string(aggregated_data.get("assessment_year")) != "null":
#         try:
#             ay_parts = safe_string(aggregated_data["assessment_year"]).split('-')
#             if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
#                 start_year = int(ay_parts[0]) -1
#                 fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
#                 if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
#                     financial_year = fy
#         except Exception:
#             logging.warning(f"Could not derive financial year from assessment year: {aggregated_data.get('assessment_year')}")
#             aggregated_data["financial_year"] = "UNKNOWNFY"
#     elif safe_string(aggregated_data.get("financial_year")) == "null":
#         aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
#     logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
#     return aggregated_data

# def calculate_final_tax_summary(aggregated_data):
#     """
#     Calculates the estimated tax payable and refund status based on aggregated financial data.
#     This function implements Indian income tax calculation for FY 2024-25 (AY 2025-26),
#     considering both Old and New regimes, age groups, surcharges, and cess.

#     Args:
#         aggregated_data (dict): A dictionary containing aggregated financial fields.

#     Returns:
#         dict: A dictionary with computed tax liability, refund/due status, and notes.
#     """
    
#     # If the document type is a Bank Statement, skip tax calculation as it's not directly for tax
#     if aggregated_data.get('identified_type') == 'Bank Statement' and aggregated_data.get('total_gross_income', 0.0) < 100.0:
#         return {
#             "calculated_gross_income": 0.0,
#             "calculated_total_deductions": 0.0,
#             "computed_taxable_income": 0.0,
#             "estimated_tax_payable": 0.0,
#             "total_tds_credit": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "predicted_tax_regime": "N/A",
#             "notes": ["Tax computation is not applicable for Bank Statements. Please upload tax-related documents like Form 16 or Salary Slips for tax calculation."],
#             "old_regime_tax_payable": 0.0,
#             "new_regime_tax_payable": 0.0,
#             "calculation_details": ["Tax computation is not applicable for Bank Statements."],
#             "regime_considered": "N/A"
#         }

#     # Safely extract and convert relevant values from aggregated_data
#     gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
#     professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
#     standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 50000)) # Default to 50k

#     # Sum all TDS and advance tax for comparison
#     total_tds_credit = (
#         safe_float(aggregated_data.get("total_tds", 0)) + 
#         safe_float(aggregated_data.get("advance_tax", 0)) + 
#         safe_float(aggregated_data.get("self_assessment_tax", 0))
#     )

#     tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
#     age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
    
#     age_group = "General"
#     if age != "N/A":
#         if age < 60:
#             age_group = "General"
#         elif age >= 60 and age < 80:
#             age_group = "Senior Citizen"
#         else: # age >= 80
#             age_group = "Super Senior Citizen"

#     # --- Calculation Details List (for frontend display) ---
#     calculation_details = []

#     # --- Check for insufficient data for tax computation ---
#     if gross_total_income < 100.0 and total_tds_credit < 100.0 and \
#        safe_float(aggregated_data.get("salary_as_per_sec_17_1", 0)) < 100.0 and \
#        safe_float(aggregated_data.get("gross_salary_total", 0)) < 100.0:
#         calculation_details.append("Insufficient primary income data provided for comprehensive tax calculation. Please upload documents with income (e.g., Form 16, Salary Slips).")
#         return {
#             "calculated_gross_income": gross_total_income,
#             "calculated_total_deductions": 0.0,
#             "computed_taxable_income": 0.0,
#             "estimated_tax_payable": 0.0,
#             "total_tds_credit": total_tds_credit,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "predicted_tax_regime": "N/A",
#             "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
#             "old_regime_tax_payable": 0.0,
#             "new_regime_tax_payable": 0.0,
#             "calculation_details": calculation_details,
#             "regime_considered": "N/A"
#         }

#     calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

#     # --- Old Tax Regime Calculation (FY 2024-25 / AY 2025-26) ---
#     # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
    
#     # Cap 80C related deductions at 1.5 Lakhs
#     deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
    
#     # Cap 80D (Health Insurance) - max 25k for general, additional 25k for senior parent (total 50k if self/family/parents are senior)
#     deduction_80d_self_family = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0)
#     deduction_80d_parents = 0.0 # Placeholder for parents if data available
#     # Simplified assumption for 80D: if deduction_80d is > 25k, assume it includes senior citizen component, cap at 50k.
#     deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 50000.0) # More generous cap for simplicity

#     # Cap Housing Loan Interest for self-occupied property at 2 Lakhs (Section 24(b))
#     interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

#     # Sum of other Chapter VI-A deductions explicitly mentioned (excluding 80C, 80D which are separately capped)
#     other_chapter_via_deductions_sum = (
#         safe_float(aggregated_data.get("deduction_80ccc", 0)) +
#         safe_float(aggregated_data.get("deduction_80ccd", 0)) + # Employer's NPS contribution u/s 80CCD(2) - usually taken separately
#         min(safe_float(aggregated_data.get("deduction_80ccd1b", 0)), 50000.0) + # 80CCD(1B) has a separate cap of 50k
#         safe_float(aggregated_data.get("deduction_80g", 0)) +
#         safe_float(aggregated_data.get("deduction_80tta", 0)) +
#         safe_float(aggregated_data.get("deduction_80ttb", 0)) +
#         safe_float(aggregated_data.get("deduction_80e", 0))
#     )
#     # Total Chapter VI-A deductions for old regime, considering the caps
#     total_chapter_via_deductions_old_regime = (
#         deduction_80c_actual +
#         deduction_80d_actual +
#         min(safe_float(aggregated_data.get("deduction_80ccd1b", 0)), 50000.0) + # Ensuring 80CCD(1B) is correctly added and capped
#         other_chapter_via_deductions_sum # Other uncapped ones (80G, 80E, 80TTA/B are generally exact amounts)
#     )
#     total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)

#     # Total deductions for Old Regime
#     total_deductions_old_regime_for_calc = (
#         standard_deduction_applied + 
#         professional_tax + 
#         interest_on_housing_loan_actual + 
#         total_chapter_via_deductions_old_regime
#     )
#     total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

#     taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
#     tax_before_cess_old_regime = 0

#     calculation_details.append(f"2. Deductions under Old Regime:")
#     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
#     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
#     calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
#     calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
#     calculation_details.append(f"   - Section 80D (capped at ₹50,000 for simplified calculation): ₹{deduction_80d_actual:,.2f}")
#     calculation_details.append(f"   - Section 80CCD(1B) (NPS, capped at ₹50,000): ₹{min(safe_float(aggregated_data.get('deduction_80ccd1b', 0)), 50000.0):,.2f}")
#     calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual - min(safe_float(aggregated_data.get('deduction_80ccd1b', 0)), 50000.0)):,.2f}") # Sum of others
#     calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
#     calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

#     # Old Regime Tax Slabs (AY 2025-26 / FY 2024-25) - Standard Slabs (No change for age in old regime for tax calculation itself, only basic exemption differs)
#     if age_group == "General":
#         if taxable_income_old_regime <= 250000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
#     elif age_group == "Senior Citizen": # 60 to < 80
#         if taxable_income_old_regime <= 300000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 300000) * 0.05
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
#     else: # Super Senior Citizen >= 80
#         if taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

#     rebate_87a_old_regime = 0
#     if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
#         rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
#     tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
#     # Surcharge (Simplified: apply if income > 50L) - Add more complex slabs if needed
#     surcharge_old_regime = 0.0
#     if gross_total_income > 5000000 and gross_total_income <= 10000000: # 50 Lakhs to 1 Crore
#         surcharge_old_regime = tax_after_rebate_old_regime * 0.10
#     elif gross_total_income > 10000000 and gross_total_income <= 20000000: # 1 Crore to 2 Crore
#         surcharge_old_regime = tax_after_rebate_old_regime * 0.15
#     elif gross_total_income > 20000000 and gross_total_income <= 50000000: # 2 Crore to 5 Crore
#         surcharge_old_regime = tax_after_rebate_old_regime * 0.25
#     elif gross_total_income > 50000000: # Above 5 Crore
#         surcharge_old_regime = tax_after_rebate_old_regime * 0.37


#     total_tax_old_regime = round((tax_after_rebate_old_regime + surcharge_old_regime) * 1.04, 2) # Add 4% Health and Education Cess
    
#     calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
#     calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
#     calculation_details.append(f"6. Surcharge (Old Regime): ₹{surcharge_old_regime:,.2f}")
#     calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


#     # --- New Tax Regime Calculation (FY 2024-25 / AY 2025-26) ---
#     # Standard deduction of ₹50,000 is applicable.
#     # Professional tax is allowed.
#     # No other common deductions (80C, 80D, 24(b) housing loan interest, etc.) are allowed, except employer's NPS contribution u/s 80CCD(2).
#     # For simplicity, we assume only standard deduction and professional tax for salaried.
    
#     # Calculate effective taxable income for new regime
#     taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
#     # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
#     tax_before_cess_new_regime = 0

#     calculation_details.append(f"8. Deductions under New Regime:")
#     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
#     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
#     calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") 
#     calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


#     # New Regime Tax Slabs (Provided by user for FY 2024-25 / AY 2025-26)
#     if taxable_income_new_regime <= 300000:
#         tax_before_cess_new_regime = 0
#     elif taxable_income_new_regime <= 700000:
#         tax_before_cess_new_regime = (taxable_income_new_regime - 300000) * 0.05
#     elif taxable_income_new_regime <= 1000000:
#         tax_before_cess_new_regime = 20000 + (taxable_income_new_regime - 700000) * 0.10 # (400000 * 0.05) = 20000
#     elif taxable_income_new_regime <= 1200000:
#         tax_before_cess_new_regime = 50000 + (taxable_income_new_regime - 1000000) * 0.15 # (20000 + 300000 * 0.10) = 50000
#     elif taxable_income_new_regime <= 1500000:
#         tax_before_cess_new_regime = 80000 + (taxable_income_new_regime - 1200000) * 0.20 # (50000 + 200000 * 0.15) = 80000
#     else: # Above 15,00,000
#         tax_before_cess_new_regime = 140000 + (taxable_income_new_regime - 1500000) * 0.30 # (80000 + 300000 * 0.20) = 140000

#     rebate_87a_new_regime = 0
#     if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs for AY 2024-25
#         rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
#     tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime

#     surcharge_new_regime = 0.0
#     if gross_total_income > 5000000 and gross_total_income <= 10000000: # 50 Lakhs to 1 Crore
#         surcharge_new_regime = tax_after_rebate_new_regime * 0.10
#     elif gross_total_income > 10000000 and gross_total_income <= 20000000: # 1 Crore to 2 Crore
#         surcharge_new_regime = tax_after_rebate_new_regime * 0.15
#     elif gross_total_income > 20000000 and gross_total_income <= 50000000: # 2 Crore to 5 Crore
#         surcharge_new_regime = tax_after_rebate_new_regime * 0.25
#     elif gross_total_income > 50000000: # Above 5 Crore
#         surcharge_new_regime = tax_after_rebate_new_regime * 0.37 # Note: For new regime, surcharge above 5 Cr income is capped at 25% of tax after rebate, if tax liability is high. This simple calc assumes direct 37%.

#     total_tax_new_regime = round((tax_after_rebate_new_regime + surcharge_new_regime) * 1.04, 2) # Add 4% Health and Education Cess

#     calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
#     calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
#     calculation_details.append(f"12. Surcharge (New Regime): ₹{surcharge_new_regime:,.2f}")
#     calculation_details.append(f"13. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


#     # --- Determine Optimal Regime and Final Summary ---
#     final_tax_regime_applied = "N/A"
#     estimated_tax_payable = 0.0
#     computed_taxable_income = 0.0
#     computation_notes = []

#     # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
#     if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
#         estimated_tax_payable = total_tax_new_regime
#         computed_taxable_income = taxable_income_new_regime
#         final_tax_regime_applied = "New Regime (Chosen by User from Document)"
#         computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
#     elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
#         estimated_tax_payable = total_tax_old_regime
#         computed_taxable_income = taxable_income_old_regime
#         final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
#         computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
#     else: # If no regime is explicitly chosen in documents, recommend the optimal one
#         if total_tax_old_regime <= total_tax_new_regime:
#             estimated_tax_payable = total_tax_old_regime
#             computed_taxable_income = taxable_income_old_regime
#             final_tax_regime_applied = "Old Regime (Optimal)"
#             computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
#         else:
#             estimated_tax_payable = total_tax_new_regime
#             computed_taxable_income = taxable_income_new_regime
#             final_tax_regime_applied = "New Regime (Optimal)"
#             computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

#     estimated_tax_payable = round(estimated_tax_payable, 2)
#     computed_taxable_income = round(computed_taxable_income, 2)

#     # --- Calculate Refund/Tax Due ---
#     refund_due_from_tax = 0.0
#     tax_due_to_government = 0.0

#     calculation_details.append(f"14. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
#     if total_tds_credit > estimated_tax_payable:
#         refund_due_from_tax = total_tds_credit - estimated_tax_payable
#         calculation_details.append(f"15. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
#     elif total_tds_credit < estimated_tax_payable:
#         tax_due_to_government = estimated_tax_payable - total_tds_credit
#         calculation_details.append(f"15. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
#     else:
#         calculation_details.append("15. No Refund or Additional Tax Due.")


#     return {
#         "calculated_gross_income": gross_total_income,
#         "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
#         "computed_taxable_income": computed_taxable_income,
#         "estimated_tax_payable": estimated_tax_payable,
#         "total_tds_credit": total_tds_credit,
#         "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
#         "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
#         "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
#         "notes": computation_notes, # List of notes
#         "old_regime_tax_payable": total_tax_old_regime,
#         "new_regime_tax_payable": total_tax_new_regime,
#         "calculation_details": calculation_details,
#         "regime_considered": final_tax_regime_applied # For clarity in the UI
#     }

# def generate_ml_prediction_summary(financial_data):
#     """
#     Generates ML model prediction summary using the loaded models.
#     """
#     if tax_regime_classifier_model is None or tax_regressor_model is None:
#         logging.warning("ML models are not loaded. Cannot generate ML predictions.")
#         return {
#             "predicted_tax_regime": "N/A",
#             "predicted_tax_liability": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "notes": "ML prediction service unavailable (models not loaded or training failed)."
#         }

#     # If the aggregated data is primarily from a bank statement, ML prediction for tax is not relevant
#     if financial_data.get('identified_type') == 'Bank Statement' and financial_data.get('total_gross_income', 0.0) < 100.0:
#         return {
#             "predicted_tax_regime": "N/A",
#             "predicted_tax_liability": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "notes": "ML prediction not applicable for bank statements. Please upload tax-related documents."
#         }

#     # Define the features expected by the ML models (must match model_trainer.py)
#     # IMPORTANT: These must precisely match the features used in model_trainer.py
#     # Re-verify against your `model_trainer.py` to ensure exact match.
#     ml_common_numerical_features = [
#         'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
#         'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
#         'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
#         'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
#         'Total Exempt Allowances Claimed'
#     ]
#     ml_categorical_features = ['Residential Status', 'Gender']
    
#     # Prepare input for classifier model
#     age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
#     # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
#     # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
#     # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
#     calculated_other_deductions = (
#         safe_float(financial_data.get('deduction_80ccc', 0)) +
#         safe_float(financial_data.get('deduction_80ccd', 0)) +
#         safe_float(financial_data.get('deduction_80ccd1b', 0)) +
#         safe_float(financial_data.get('deduction_80g', 0)) +
#         safe_float(financial_data.get('deduction_80tta', 0)) +
#         safe_float(financial_data.get('deduction_80ttb', 0))
#     )
#     calculated_other_deductions = round(calculated_other_deductions, 2)


#     classifier_input_data = {
#         'Age': age_value,
#         'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
#         'HRA Received': safe_float(financial_data.get('hra_received', 0)),
#         'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
#         'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
#         'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
#         'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
#         'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
#         'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
#         'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
#         'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
#         'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
#         'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
#         'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
#         'Gender': safe_string(financial_data.get('gender', 'Unknown'))
#     }
    
#     # Create DataFrame for classifier prediction, ensuring column order
#     # The order must match `model_trainer.py`'s `classifier_all_features`
#     ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
#     classifier_df = pd.DataFrame([classifier_input_data])
    
#     predicted_tax_regime = "N/A"
#     try:
#         classifier_df_processed = classifier_df[ordered_classifier_features]
#         predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
#         logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
#     except Exception as e:
#         logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
#         predicted_tax_regime = "Prediction Failed (Error)"
        
#     # Prepare input for regressor model
#     # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
#     regressor_input_data = {
#         k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
#     }
#     regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

#     regressor_df = pd.DataFrame([regressor_input_data])
    
#     predicted_tax_liability = 0.0
#     try:
#         # The regressor's preprocessor will handle the categorical feature conversion.
#         # Just ensure the input DataFrame has the correct columns and order.
#         ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
#         regressor_df_processed = regressor_df[ordered_regressor_features]
#         predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
#         logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
#     except Exception as e:
#         logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
#         predicted_tax_liability = 0.0 # Default to 0 if prediction fails

#     # Calculate refund/additional due based on ML prediction and actual TDS
#     total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

#     predicted_refund_due = 0.0
#     predicted_additional_due = 0.0

#     if total_tds_credit > predicted_tax_liability:
#         predicted_refund_due = total_tds_credit - predicted_tax_liability
#     elif total_tds_credit < predicted_tax_liability:
#         predicted_additional_due = predicted_tax_liability - total_tds_credit
        
#     # Convert any numpy types before returning
#     return convert_numpy_types({
#         "predicted_tax_regime": predicted_tax_regime,
#         "predicted_tax_liability": predicted_tax_liability,
#         "predicted_refund_due": round(predicted_refund_due, 2),
#         "predicted_additional_due": round(predicted_additional_due, 2),
#         "notes": "ML model predictions for optimal regime and tax liability."
#     })

# def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
#     """Generates tax-saving suggestions and regime analysis using Gemini API."""
#     if gemini_pro_model is None:
#         logging.error("Gemini API (gemini_pro_model) not initialized.")
#         return ["AI suggestions unavailable."], "AI regime analysis unavailable."

#     # Check if tax computation was not possible
#     if "Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]:
#         return (
#             ["Please upload your Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts) for a comprehensive tax analysis and personalized tax-saving suggestions."],
#             "Tax regime analysis requires complete income and deduction data."
#         )

#     # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
#     financial_data_for_gemini = aggregated_financial_data.copy()

#     # Add specific structure for Bank Statement details if identified as such, or if bank details are present
#     if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
#         financial_data_for_gemini['Bank Details'] = {
#             'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
#             'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
#             'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
#             'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
#             'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
#             'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
#             'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
#             'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
#         }
#         # Optionally, remove transaction_summary if it's too verbose for the prompt
#         # financial_data_for_gemini.pop('transaction_summary', None)


#     prompt = f"""
#     You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
#     Based on this data:
#     1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
#     2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

#     **Financial Data Summary:**
#     {json.dumps(financial_data_for_gemini, indent=2)}

#     **Final Tax Computation Summary:**
#     {json.dumps(final_tax_computation_summary, indent=2)}

#     Please format your response strictly as follows:
#     Suggestions:
#     - [Suggestion 1]
#     - [Suggestion 2]
#     ...
#     Regime Analysis: [Your analysis paragraph here].
#     """
#     try:
#         response = gemini_pro_model.generate_content(prompt)
#         text = response.text.strip()
        
#         suggestions = []
#         regime_analysis = ""

#         # Attempt to parse the structured output
#         if "Suggestions:" in text and "Regime Analysis:" in text:
#             parts = text.split("Regime Analysis:")
#             suggestions_part = parts[0].replace("Suggestions:", "").strip()
#             regime_analysis = parts[1].strip()

#             # Split suggestions into bullet points and filter out empty strings
#             suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
#             if not suggestions: # If parsing as bullets failed, treat as single suggestion
#                 suggestions = [suggestions_part]
#         else:
#             # Fallback if format is not as expected, return raw text as suggestions
#             suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
#             regime_analysis = "AI could not parse structured regime analysis."
#             logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

#         return suggestions, regime_analysis
#     except Exception as e:
#         logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
#         return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

# def generate_itr_pdf(tax_record_data):
#     """
#     Generates a dummy ITR form PDF.
#     This uses a basic PDF string structure as a placeholder.
#     """
#     aggregated_data = tax_record_data.get('aggregated_financial_data', {})
#     final_computation = tax_record_data.get('final_tax_computation_summary', {})

#     # Determine ITR type (simplified logic)
#     itr_type = "ITR-1 (SAHAJ - DUMMY)"
#     if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
#        safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
#        safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
#         itr_type = "ITR-2 (DUMMY)"
    
#     # Extract key info for the dummy PDF
#     name = aggregated_data.get('name_of_employee', 'N/A')
#     pan = aggregated_data.get('pan_of_employee', 'N/A')
#     financial_year = aggregated_data.get('financial_year', 'N/A')
#     assessment_year = aggregated_data.get('assessment_year', 'N/A')
#     total_income = final_computation.get('computed_taxable_income', 'N/A')
#     tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
#     refund_due = final_computation.get('predicted_refund_due', 0.0)
#     tax_due = final_computation.get('predicted_additional_due', 0.0)
#     regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

#     # Add bank statement specific details to the PDF content if available
#     bank_details_for_pdf = ""
#     if aggregated_data.get('identified_type') == 'Bank Statement' or \
#        (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
#         bank_details_for_pdf = f"""
# BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
# BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
# """

#     # Core PDF content without xref and EOF for length calculation
#     core_pdf_content_lines = [
#         f"%PDF-1.4",
#         f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
#         f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
#         f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
#         f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
#         f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
#         f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
#         f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
#         f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
#         f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
#         f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
#         f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
#         f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
#         f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
#         f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
#     ]
    
#     # Append bank details if available
#     if bank_details_for_pdf:
#         core_pdf_content_lines.append(bank_details_for_pdf)
#         # Adjust vertical position for the Note if bank details were added
#         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
#     else:
#         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

#     core_pdf_content_lines.extend([
#         f"endstream",
#         f"endobj",
#         f"xref",
#         f"0 5",
#         f"0000000000 65535 f",
#         f"0000000010 00000 n",
#         f"0000000057 00000 n",
#         f"0000000114 00000 n",
#         f"0000000222 00000 n",
#         f"trailer <</Size 5 /Root 1 0 R>>",
#     ])
    
#     # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
#     core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
#     core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

#     # Calculate the startxref position
#     startxref_position = len(core_pdf_bytes)

#     # Now assemble the full PDF content including startxref and EOF
#     full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
#     # Final encode
#     dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

#     return io.BytesIO(dummy_pdf_content_bytes), itr_type


# # --- API Routes ---

# # Serves the main page (assuming index.html is in the root)
# @app.route('/')
# def home():
#     """Serves the main landing page, typically index.html."""
#     return send_from_directory('.', 'index.html')

# # Serves other static files (CSS, JS, images, etc.)
# @app.route('/<path:path>')
# def serve_static_files(path):
#     """Serves static files from the root directory."""
#     return send_from_directory('.', path)

# # Serves uploaded files from the uploads folder
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     """Allows access to temporarily stored uploaded files."""
#     try:
#         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#     except FileNotFoundError:
#         logging.warning(f"File '{filename}' not found in uploads folder.")
#         return jsonify({"message": "File not found"}), 404
#     except Exception as e:
#         logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
#         return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


# @app.route('/api/register', methods=['POST'])
# def register_user():
#     """Handles user registration."""
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')

#         if not username or not email or not password:
#             logging.warning("Registration attempt with missing fields.")
#             return jsonify({"message": "Username, email, and password are required"}), 400

#         # Check if email or username already exists
#         if users_collection.find_one({"email": email}):
#             logging.warning(f"Registration failed: Email '{email}' already exists.")
#             return jsonify({"message": "Email already exists"}), 409
#         if users_collection.find_one({"username": username}):
#             logging.warning(f"Registration failed: Username '{username}' already exists.")
#             return jsonify({"message": "Username already exists"}), 409

#         # Hash the password before storing
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         # Prepare user data for MongoDB insertion
#         new_user_data = {
#             "username": username,
#             "email": email,
#             "password": hashed_password.decode('utf-8'), # Store hashed password as string
#             "full_name": data.get('fullName', ''),
#             "pan": data.get('pan', ''),
#             "aadhaar": data.get('aadhaar', ''),
#             "address": data.get('address', ''),
#             "phone": data.get('phone', ''),
#             "created_at": datetime.utcnow()
#         }
#         # Insert the new user record and get the inserted ID
#         user_id = users_collection.insert_one(new_user_data).inserted_id
#         logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
#         return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
#     except Exception as e:
#         logging.error(f"Error during registration: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred during registration."}), 500

# @app.route('/api/login', methods=['POST'])
# def login_user():
#     """Handles user login and JWT token generation."""
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')

#         if not username or not password:
#             logging.warning("Login attempt with missing credentials.")
#             return jsonify({"error_msg": "Username and password are required"}), 400

#         # Find the user by username
#         user = users_collection.find_one({"username": username})

#         # Verify user existence and password
#         if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')): 
#             # Create a JWT access token with the user's MongoDB ObjectId as identity
#             access_token = create_access_token(identity=str(user['_id']))
#             logging.info(f"User '{username}' logged in successfully.")
#             return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
#         else:
#             logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
#             return jsonify({"error_msg": "Invalid credentials"}), 401
#     except Exception as e:
#         logging.error(f"Error during login: {traceback.format_exc()}")
#         return jsonify({"error_msg": "An error occurred during login."}), 500

# @app.route('/api/profile', methods=['GET'])
# @jwt_required()
# def get_user_profile():
#     """Fetches the profile of the currently authenticated user."""
#     try:
#         # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
#         current_user_id = get_jwt_identity()
#         # Find user by ObjectId, exclude password from the result
#         user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
#         if not user:
#             logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
#             return jsonify({"message": "User not found"}), 404

#         # Convert ObjectId to string for JSON serialization
#         user['_id'] = str(user['_id'])
#         logging.info(f"Profile fetched for user ID: {current_user_id}")
#         return jsonify({"user": user}), 200
#     except Exception as e:
#         logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

# @app.route('/api/profile', methods=['PUT', 'PATCH'])
# @jwt_required()
# def update_user_profile():
#     """Updates the profile of the currently authenticated user."""
#     try:
#         current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#         data = request.get_json()

#         # Define allowed fields for update
#         updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
#         update_data = {k: data[k] for k in updatable_fields if k in data}

#         if not update_data:
#             logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
#             return jsonify({"message": "No fields to update provided."}), 400
        
#         # Prevent username from being updated via this route for security/simplicity
#         if 'username' in data:
#             logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

#         # If email is being updated, ensure it's not already in use by another user
#         if 'email' in update_data:
#             existing_user_with_email = users_collection.find_one({"email": update_data['email']})
#             if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
#                 logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
#                 return jsonify({"message": "Email already in use by another account."}), 409

#         # Perform the update operation in MongoDB
#         result = users_collection.update_one(
#             {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
#             {"$set": update_data}
#         )

#         if result.matched_count == 0:
#             logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
#             return jsonify({"message": "User not found."}), 404
#         if result.modified_count == 0:
#             logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
#             return jsonify({"message": "Profile data is the same, no changes made."}), 200

#         logging.info(f"Profile updated successfully for user ID: {current_user_id}")
#         return jsonify({"message": "Profile updated successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while updating your profile."}), 500


# @app.route('/api/process_documents', methods=['POST'])
# @jwt_required()
# def process_documents():
#     """
#     Handles uploaded documents, extracts financial data using Gemini and Vision API,
#     aggregates data from multiple files, computes tax, and saves the comprehensive
#     record to MongoDB, grouped by PAN and Financial Year.
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

#     if 'documents' not in request.files:
#         logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
#         return jsonify({"message": "No 'documents' part in the request"}), 400

#     files = request.files.getlist('documents')
#     if not files:
#         logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
#         return jsonify({"message": "No selected file"}), 400

#     extracted_data_from_current_upload = []
#     document_processing_summary_current_upload = [] # To provide feedback on each file

#     # Get the selected document type hint from the form data (if provided)
#     document_type_hint = request.form.get('document_type', 'Auto-Detect') 
#     logging.info(f"Received document type hint from frontend: {document_type_hint}")

#     for file in files:
#         if file.filename == '':
#             document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
#             continue
        
#         filename = secure_filename(file.filename)
#         # Create a unique filename for storing the original document
#         unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
#         try:
#             file_content_bytes = file.read() # Read content before saving
#             file.seek(0) # Reset file pointer for subsequent operations if needed

#             # Save the file temporarily (or permanently if you wish to retain originals)
#             with open(file_path, 'wb') as f:
#                 f.write(file_content_bytes)
#             logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

#             mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default

#             # Construct the base prompt for Gemini
#             base_prompt_instructions = (
#                 f"You are an expert financial data extractor and tax document analyzer for Indian context. "
#                 f"Analyze the provided document (filename: '{filename}', MIME type: {mime_type}). "
#                 f"The user has indicated this document is of type: '{document_type_hint}'. " 
#                 "Extract ALL relevant financial information for Indian income tax filing. "
#                 "Your response MUST be a JSON object conforming precisely to the provided schema. "
#                 "For numerical fields, if a value is not explicitly found or is clearly zero, you MUST use `0.0`. "
#                 "For string fields (like names, PAN, year, dates, identified_type, gender, residential_status), if a value is not explicitly found, you MUST use the string `null`. "
#                 "For dates, if found, use 'YYYY-MM-DD' format if possible; otherwise, `0000-01-01` if not found or cannot be parsed.\n\n"
#             )

#             # Add specific instructions based on document type hint
#             if document_type_hint == 'Bank Statement':
#                 base_prompt_instructions += (
#                     "Specifically for a Bank Statement, extract the following details accurately:\n"
#                     "- Account Holder Name\n- Account Number\n- IFSC Code (if present)\n- Bank Name\n"
#                     "- Branch Address\n- Statement Start Date (YYYY-MM-DD)\n- Statement End Date (YYYY-MM-DD)\n"
#                     "- Opening Balance\n- Closing Balance\n- Total Deposits\n- Total Withdrawals\n"
#                     "- A summary of key transactions, including date (YYYY-MM-DD), description, and amount. Prioritize large transactions or those with specific identifiable descriptions (e.g., 'salary', 'rent', 'interest').\n"
#                     "If a field is not found or not applicable, use `null` for strings and `0.0` for numbers. Ensure dates are in YYYY-MM-DD format."
#                 )
#             elif document_type_hint == 'Form 16':
#                 base_prompt_instructions += (
#                     "Specifically for Form 16, extract details related to employer, employee, PAN, TAN, financial year, assessment year, "
#                     "salary components (basic, HRA, perquisites, profits in lieu of salary), exempt allowances, professional tax, "
#                     "income from house property, income from other sources, capital gains, "
#                     "deductions under Chapter VI-A (80C, 80D, 80G, 80E, 80CCD, etc.), TDS details (total, quarter-wise), "
#                     "and any mentioned tax regime (Old/New). Ensure all monetary values are extracted as numbers."
#                 )
#             elif document_type_hint == 'Salary Slip':
#                 base_prompt_instructions += (
#                     "Specifically for a Salary Slip, extract employee name, PAN, employer name, basic salary, HRA, "
#                     "conveyance allowance, transport allowance, overtime pay, EPF contribution, ESI contribution, "
#                     "professional tax, net amount payable, days present, and overtime hours. Ensure all monetary values are extracted as numbers."
#                 )
#             # Add more elif blocks for other specific document types if needed

#             if "image" in mime_type or "pdf" in mime_type:
#                 gemini_response_json_str = get_gemini_response(base_prompt_instructions, file_data=file_content_bytes, mime_type=mime_type, filename=filename)
#             elif "text" in mime_type or "json" in mime_type:
#                 extracted_raw_text = file_content_bytes.decode('utf-8')
#                 final_prompt_content = base_prompt_instructions + f"\n\nDocument Content:\n{extracted_raw_text}"
#                 gemini_response_json_str = get_gemini_response(final_prompt_content, filename=filename)
#             else:
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "skipped", "identified_type": "Unsupported",
#                     "message": f"Unsupported file type: {mime_type}"
#                 })
#                 continue
            
#             try:
#                 gemini_parsed_response = json.loads(gemini_response_json_str)
#                 if gemini_parsed_response.get("error"):
#                     raise ValueError(f"AI processing error: {gemini_parsed_response['error']}")

#                 extracted_data = gemini_parsed_response.get('extracted_data', {})
                
#                 if "raw_text_response" in extracted_data:
#                     document_processing_summary_current_upload.append({
#                         "filename": filename, "status": "warning", "identified_type": "Unstructured Text",
#                         "message": "AI could not extract structured JSON. Raw text available.",
#                         "extracted_raw_text": extracted_data["raw_text_response"],
#                         "stored_path": f"/uploads/{unique_filename}"
#                     })
#                     extracted_data_from_current_upload.append({"identified_type": "Unstructured Text", "raw_text": extracted_data["raw_text_response"]})
#                     continue 
#                 # Add the path to the stored document for future reference in history
#                 extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
#                 extracted_data_from_current_upload.append(extracted_data)

#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "success", "identified_type": extracted_data['identified_type'],
#                     "message": "Processed successfully.", "extracted_fields": extracted_data,
#                     "stored_path": f"/uploads/{unique_filename}" 
#                 })
#             except (json.JSONDecodeError, ValueError) as ve:
#                 logging.error(f"Error parsing Gemini response or AI error for '{filename}': {ve}")
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "failed", "message": f"AI response error: {str(ve)}",
#                     "stored_path": f"/uploads/{unique_filename}"
#                 })
#             except Exception as e:
#                 logging.error(f"Unexpected error processing Gemini data for '{filename}': {traceback.format_exc()}")
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "failed", "message": f"Error processing AI data: {str(e)}",
#                     "stored_path": f"/uploads/{unique_filename}"
#                 })
#             finally:
#                 pass 

#         except Exception as e:
#             logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
#             document_processing_summary_current_upload.append({
#                 "filename": filename, "status": "error",
#                 "message": f"An unexpected error occurred during file processing: {str(e)}",
#                 "stored_path": f"/uploads/{unique_filename}"
#             })
#             pass 

#     if not extracted_data_from_current_upload:
#         logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
#         return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

#     # --- Determine PAN and Financial Year for grouping ---
#     # Try to find PAN and FY from the currently uploaded documents first
#     pan_of_employee = "UNKNOWNPAN"
#     financial_year = "UNKNOWNFY"

#     for data in extracted_data_from_current_upload:
#         if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
#             pan_of_employee = safe_string(data["pan_of_employee"])
#         if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
#             financial_year = safe_string(data["financial_year"])
#         # If both are found, we can break early (or continue to see if a higher priority doc has them)
#         if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
#             break
    
#     # If still unknown, check if the user profile has a PAN.
#     if pan_of_employee == "UNKNOWNPAN":
#         user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
#         if user_profile and safe_string(user_profile.get("pan")) != "null":
#             pan_of_employee = safe_string(user_profile["pan"])
#             logging.info(f"Using PAN from user profile: {pan_of_employee}")
#         else:
#             # If PAN is still unknown, log a warning and use the placeholder
#             logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

#     # Derive financial year from assessment year if financial_year is null
#     if financial_year == "UNKNOWNFY":
#         for data in extracted_data_from_current_upload:
#             if safe_string(data.get("assessment_year")) != "null":
#                 try:
#                     ay_parts = safe_string(data["assessment_year"]).split('-')
#                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
#                         start_year = int(ay_parts[0]) -1
#                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
#                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
#                             financial_year = fy
#                             break
#                 except Exception:
#                     pass # Keep default if parsing fails
#         if financial_year == "UNKNOWNFY":
#             logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


#     # Try to find an existing record for this user, PAN, and financial year
#     existing_tax_record = tax_records_collection.find_one({
#         "user_id": current_user_id,
#         "aggregated_financial_data.pan_of_employee": pan_of_employee,
#         "aggregated_financial_data.financial_year": financial_year
#     })

#     if existing_tax_record:
#         logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
#         # Merge new extracted data with existing data
#         all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
#         all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

#         # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
#         updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
#         updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

#         # Clear previous AI/ML results as they need to be re-generated for the updated data
#         tax_records_collection.update_one(
#             {"_id": existing_tax_record["_id"]},
#             {"$set": {
#                 "extracted_documents_data": all_extracted_data_for_fy,
#                 "document_processing_summary": all_document_processing_summary_for_fy,
#                 "aggregated_financial_data": updated_aggregated_financial_data,
#                 "final_tax_computation_summary": updated_final_tax_computation_summary,
#                 "timestamp": datetime.utcnow(), # Update timestamp of last modification
#                 "suggestions_from_gemini": [], # Reset suggestions
#                 "gemini_regime_analysis": "null", # Reset regime analysis
#                 "ml_prediction_summary": {}, # Reset ML predictions
#             }}
#         )
#         record_id = existing_tax_record["_id"]
#         logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

#     else:
#         logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
#         # If no existing record, aggregate only the newly uploaded data
#         new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
#         new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

#         # Prepare the comprehensive tax record to save to MongoDB
#         tax_record_to_save = {
#             "user_id": current_user_id, 
#             "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
#             "financial_year": financial_year, # Store FY at top level for easy query
#             "timestamp": datetime.utcnow(),
#             "document_processing_summary": document_processing_summary_current_upload, 
#             "extracted_documents_data": extracted_data_from_current_upload, 
#             "aggregated_financial_data": new_aggregated_financial_data,
#             "final_tax_computation_summary": new_final_tax_computation_summary,
#             "suggestions_from_gemini": [], 
#             "gemini_regime_analysis": "null", 
#             "ml_prediction_summary": {},    
#         }
#         record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
#         logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
#         updated_aggregated_financial_data = new_aggregated_financial_data
#         updated_final_tax_computation_summary = new_final_tax_computation_summary


#     # Return success response with computed data
#     # Ensure all data sent back is JSON serializable (e.g., no numpy types)
#     response_data = {
#         "status": "success",
#         "message": "Documents processed and financial data aggregated and tax computed successfully",
#         "record_id": str(record_id), 
#         "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
#         "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
#         "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
#     }
#     return jsonify(response_data), 200


# @app.route('/api/get_suggestions', methods=['POST'])
# @jwt_required()
# def get_suggestions():
#     """
#     Generates AI-driven tax-saving suggestions and provides an ML prediction summary
#     based on a specific processed tax record (grouped by PAN/FY).
#     """
#     current_user_id = get_jwt_identity()

#     data = request.get_json()
#     record_id = data.get('record_id')

#     if not record_id:
#         logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
#         return jsonify({"message": "Record ID is required to get suggestions."}), 400

#     try:
#         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
#         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
#         if not tax_record:
#             logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or unauthorized."}), 404

#         # Get the aggregated financial data and final tax computation summary from the record
#         aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
#         final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

#         # Generate suggestions and ML predictions
#         suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
#         ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

#         # Update the record in DB with generated suggestions and predictions
#         tax_records_collection.update_one(
#             {"_id": ObjectId(record_id)},
#             {"$set": {
#                 "suggestions_from_gemini": suggestions,
#                 "gemini_regime_analysis": regime_analysis,
#                 "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
#                 "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
#             }}
#         )
#         logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

#         return jsonify({
#             "status": "success",
#             "message": "AI suggestions and ML predictions generated successfully!",
#             "suggestions_from_gemini": suggestions,
#             "gemini_regime_analysis": regime_analysis,
#             "ml_prediction_summary": ml_prediction_summary # Already converted
#         }), 200
#     except Exception as e:
#         logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
#         # Fallback for ML prediction summary even if overall suggestions fail
#         ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
#         return jsonify({
#             "status": "error",
#             "message": "An error occurred while generating suggestions.",
#             "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
#             "gemini_regime_analysis": "An error occurred.",
#             "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
#         }), 500

# @app.route('/api/save_extracted_data', methods=['POST'])
# @jwt_required()
# def save_extracted_data():
#     """
#     Saves extracted and computed tax data to MongoDB.
#     This route can be used for explicit saving if `process_documents` doesn't
#     cover all saving scenarios or for intermediate saves.
#     NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
#     For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#     data = request.get_json()

#     if not data:
#         logging.warning(f"Save data request from user {current_user_id} with no data provided.")
#         return jsonify({"message": "No data provided to save"}), 400

#     try:
#         # This route might be less relevant with the new aggregation by PAN/FY,
#         # as `process_documents` handles the upsert logic.
#         # However, if used for manual saving of *already aggregated* data,
#         # ensure PAN and FY are part of `data.aggregated_financial_data`
#         # or extracted from the `data` directly.
#         # Example: Try to get PAN and FY from input data for consistency
#         input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
#         input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

#         # Check for existing record for upsert behavior
#         existing_record = tax_records_collection.find_one({
#             "user_id": current_user_id,
#             "aggregated_financial_data.pan_of_employee": input_pan,
#             "aggregated_financial_data.financial_year": input_fy
#         })

#         if existing_record:
#             # Update existing record
#             update_result = tax_records_collection.update_one(
#                 {"_id": existing_record["_id"]},
#                 {"$set": {
#                     **data, # Overwrite with new data, ensuring user_id and timestamp are also set
#                     "user_id": current_user_id,
#                     "timestamp": datetime.utcnow(),
#                     "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
#                     "financial_year": input_fy, # Ensure top-level FY is consistent
#                 }}
#             )
#             record_id = existing_record["_id"]
#             logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
#             message = "Data updated successfully."
#         else:
#             # Create a new record
#             data_to_save = {
#                 **data,
#                 "user_id": current_user_id,
#                 "timestamp": datetime.utcnow(),
#                 "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
#                 "financial_year": input_fy, # Ensure top-level FY is consistent
#             }
#             record_id = tax_records_collection.insert_one(data_to_save).inserted_id
#             logging.info(f"New record created via save_extracted_data for user {current_user_id}. ID: {record_id}")
#             message = "Data saved successfully."

#         return jsonify({"message": message, "record_id": str(record_id)}), 200

#     except Exception as e:
#         logging.error(f"Error saving extracted data for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while saving data.", "error": str(e)}), 500


# @app.route('/api/tax-records', methods=['GET'])
# @jwt_required()
# def get_tax_history():
#     """
#     Fetches the tax records (aggregated financial data and tax computation)
#     for the authenticated user.
#     """
#     current_user_id = get_jwt_identity()
#     try:
#         # Fetch all records for the current user, ordered by timestamp descending
#         history_records = list(tax_records_collection.find({"user_id": current_user_id}).sort("timestamp", -1))

#         # Convert ObjectId to string for JSON serialization and convert numpy types
#         for record in history_records:
#             record['_id'] = str(record['_id'])
#             # Ensure aggregated_financial_data and final_tax_computation_summary are converted
#             record['aggregated_financial_data'] = convert_numpy_types(record.get('aggregated_financial_data', {}))
#             record['final_tax_computation_summary'] = convert_numpy_types(record.get('final_tax_computation_summary', {}))
#             record['ml_prediction_summary'] = convert_numpy_types(record.get('ml_prediction_summary', {}))


#         logging.info(f"Fetched {len(history_records)} tax records for user {current_user_id}.")
#         return jsonify({"history": history_records}), 200
#     except Exception as e:
#         logging.error(f"Error fetching tax history for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to fetch tax history", "error": str(e)}), 500

# @app.route('/api/get_itr_pdf/<record_id>', methods=['GET'])
# @jwt_required()
# def get_itr_pdf(record_id):
#     """
#     Generates and serves a dummy ITR PDF for a given tax record ID.
#     """
#     current_user_id = get_jwt_identity()
#     try:
#         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
#         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
#         if not tax_record:
#             logging.warning(f"PDF generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or unauthorized."}), 404

#         if REPORTLAB_AVAILABLE:
#             # Placeholder for actual ReportLab PDF generation if enabled and correctly implemented
#             # For now, it will use the dummy_pdf_content_bytes.
#             # Replace this with actual ReportLab calls when you install ReportLab
#             # and enable REPORTLAB_AVAILABLE = True.
#             # Example:
#             # from reportlab.pdfgen import canvas
#             # from reportlab.lib.pagesizes import letter
#             # from reportlab.lib.units import inch
#             # buffer = io.BytesIO()
#             # p = canvas.Canvas(buffer, pagesize=letter)
#             # p.drawString(inch, 10 * inch, "Hello ReportLab!")
#             # p.save()
#             # buffer.seek(0)
#             # return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f"ITR_Summary_{record_id}.pdf")
#             pdf_buffer, itr_type = generate_itr_pdf(tax_record)
#             return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f"{itr_type.replace(' (DUMMY)', '')}_{record_id}.pdf")
#         else:
#             # Use the dummy PDF content if ReportLab is not available
#             pdf_buffer, itr_type = generate_itr_pdf(tax_record) # This will create the hardcoded PDF string
#             logging.info(f"Generated dummy PDF for record {record_id} due to ReportLab unavailability.")
#             return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f"{itr_type.replace(' (DUMMY)', '')}_{record_id}.pdf")

#     except Exception as e:
#         logging.error(f"Error generating PDF for record {record_id} for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to generate PDF", "error": str(e)}), 500

# @app.route('/api/delete_record/<record_id>', methods=['DELETE'])
# @jwt_required()
# def delete_record(record_id):
#     """
#     Deletes a tax record for the authenticated user.
#     """
#     current_user_id = get_jwt_identity()
#     try:
#         result = tax_records_collection.delete_one({"_id": ObjectId(record_id), "user_id": current_user_id})

#         if result.deleted_count == 0:
#             logging.warning(f"Delete failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or unauthorized."}), 404

#         logging.info(f"Record {record_id} deleted successfully for user {current_user_id}.")
#         return jsonify({"message": "Record deleted successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error deleting record {record_id} for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while deleting the record.", "error": str(e)}), 500

# @app.route('/api/contact', methods=['POST'])
# def submit_contact_form():
#     """Handles submission of contact messages."""
#     try:
#         data = request.get_json()
#         name = data.get('name')
#         email = data.get('email')
#         subject = data.get('subject')
#         message = data.get('message')

#         if not name or not email or not subject or not message:
#             logging.warning("Contact form submission with missing fields.")
#             return jsonify({"message": "All fields are required."}), 400
        
#         # Insert contact message into MongoDB
#         contact_messages_collection.insert_one({
#             "name": name,
#             "email": email,
#             "subject": subject,
#             "message": message,
#             "timestamp": datetime.utcnow()
#         })
#         logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

#         return jsonify({"message": "Message sent successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while sending your message."}), 500

# # --- Main application entry point ---
# if __name__ == '__main__':
#     # Ensure MongoDB connection is established before running the app
#     if db is None:
#         logging.error("MongoDB connection failed at startup. Exiting.")
#         exit(1)
    
#     logging.info("Starting Flask application...")
#     # Run the Flask app
#     # debug=True enables reloader and debugger (should be False in production)
#     # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
#     # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
#     app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)





























# # import os
# # import json
# # from flask import Flask, request, jsonify, send_from_directory, send_file
# # from flask_cors import CORS
# # import google.generativeai as genai
# # from pymongo import MongoClient
# # from bson.objectid import ObjectId
# # import bcrypt
# # import traceback
# # import logging
# # import io
# # from datetime import datetime, timedelta
# # from google.cloud import vision
# # from google.oauth2 import service_account
# # from werkzeug.utils import secure_filename # Import secure_filename
# # import joblib # Import joblib for loading ML models
# # import pandas as pd # Import pandas for ML model input

# # # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# # import numpy as np

# # # Import ReportLab components for PDF generation
# # try:
# #     # Commented out ReportLab imports as per previous turn, using dummy PDF for now.
# #     # from reportlab.pdfgen import canvas
# #     # from reportlab.lib.pagesizes import letter
# #     # from reportlab.lib.units import inch
# #     # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# #     # from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
# #     # from reportlab.lib.enums import TA_CENTER
# #     REPORTLAB_AVAILABLE = False # Set to False since using dummy PDF
# # except ImportError:
# #     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
# #     REPORTLAB_AVAILABLE = False


# # # Configure logging for better visibility
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # # --- Configuration (IMPORTANT: Using hardcoded keys as per user's request) ---
# # # In a real-world production environment, these should ALWAYS be loaded from
# # # environment variables (e.g., using os.getenv) and never hardcoded.
# # GEMINI_API_KEY_HARDCODED = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs"
# # MONGO_URI_HARDCODED = "mongodb://localhost:27017/"
# # JWT_SECRET_KEY_HARDCODED = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# # # Ensure the path for Vision API key is correct for your system. Use a raw string (r"")
# # # or forward slashes (/) for paths to avoid issues with backslashes.
# # VISION_API_KEY_PATH_HARDCODED = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json"

# # # Initialize Flask app
# # app = Flask(__name__)
# # # Enable CORS for all origins, allowing frontend to communicate. For production, restrict this.
# # CORS(app)

# # # --- JWT Configuration ---
# # app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY_HARDCODED
# # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Tokens expire in 24 hours
# # # UNCOMMENTED: Corrected the NameError by uncommenting the import below
# # from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# # jwt = JWTManager(app)

# # # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# # @jwt.expired_token_loader
# # def expired_token_callback(jwt_header, jwt_payload):
# #     logging.warning("JWT token expired.")
# #     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# # @jwt.invalid_token_loader
# # def invalid_token_callback(callback_error):
# #     logging.warning(f"Invalid JWT token: {callback_error}")
# #     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# # @jwt.unauthorized_loader
# # def unauthorized_callback(callback_error):
# #     logging.warning(f"Unauthorized access attempt: {callback_error}")
# #     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401
# # # --- End JWT Configuration ---


# # # --- MongoDB Connection ---
# # client = None
# # db = None
# # users_collection = None
# # tax_records_collection = None
# # contact_messages_collection = None

# # try:
# #     client = MongoClient(MONGO_URI_HARDCODED)
# #     db = client['garudatax_db'] # Using a more specific database name for tax application
# #     users_collection = db['users']
# #     tax_records_collection = db['tax_records'] # This collection will store aggregated records per FY
# #     contact_messages_collection = db['contact_messages']
# #     logging.info("MongoDB connected successfully.")
# # except Exception as e:
# #     logging.error(f"Error connecting to MongoDB: {traceback.format_exc()}")
# #     db = None # Ensure db is None if connection fails, so app can handle it gracefully.


# # # --- Google Cloud Vision API Configuration ---
# # vision_client = None
# # try:
# #     if not os.path.exists(VISION_API_KEY_PATH_HARDCODED):
# #         logging.error(f"Vision API key file not found at: {VISION_API_KEY_PATH_HARDCODED}. Vision features will be disabled.")
# #     else:
# #         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH_HARDCODED)
# #         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
# #         logging.info("Google Cloud Vision API client initialized successfully.")
# # except Exception as e:
# #     logging.error(f"Error initializing Google Cloud Vision API client: {traceback.format_exc()}. Vision features will be disabled.")
# #     vision_client = None


# # # --- Google Gemini API Configuration ---
# # # Ensure API key is set before configuring Gemini
# # if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
# #     logging.error("GEMINI_API_KEY is not set or is still the placeholder! Gemini features will not work.")
# # genai.configure(api_key=GEMINI_API_KEY_HARDCODED)

# # # Initialize Gemini models. Using gemini-2.0-flash for multimodal capabilities (though OCR is done by Vision first).
# # gemini_pro_model = genai.GenerativeModel('gemini-2.0-flash')
# # logging.info("Google Gemini API client initialized.")


# # # --- UPLOAD FOLDER CONFIGURATION ---
# # # Define the upload folder relative to the current working directory
# # UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # # Create UPLOAD_FOLDER if it doesn't exist. exist_ok=True prevents error if it already exists.
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# # logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")
# # # --- END UPLOAD FOLDER CONFIGURATION ---

# # # --- ML Model Loading ---
# # # Load trained ML models for tax regime classification and tax liability regression
# # tax_regime_classifier_model = None
# # tax_regressor_model = None

# # try:
# #     # Ensure these .pkl files are generated by running model_trainer.py first.
# #     # Make sure xgboost is installed in your environment for model_trainer.py
# #     classifier_path = 'tax_regime_classifier_model.pkl'
# #     if os.path.exists(classifier_path):
# #         tax_regime_classifier_model = joblib.load(classifier_path)
# #         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
# #     else:
# #         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

# #     regressor_path = 'final_tax_regressor_model.pkl'
# #     if os.path.exists(regressor_path):
# #         tax_regressor_model = joblib.load(regressor_path)
# #         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
# #     else:
# #         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# # except Exception as e:
# #     logging.error(f"Error loading ML models: {traceback.format_exc()}")
# #     tax_regime_classifier_model = None
# #     tax_regressor_model = None


# # --- Helper Functions ---

# # IMPORTANT: The user's provided traceback indicates a NameError for 'convert_numpy_types'.
# # This function was commented out in the provided 'app1.py' content.
# # I am re-adding and uncommenting it here, as it's crucial for serializing
# # data that might contain NumPy types (e.g., from ML model predictions) to JSON.

































# import os
# import json
# from flask import Flask, request, jsonify, send_from_directory, send_file
# from flask_cors import CORS
# import google.generativeai as genai
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import bcrypt
# import traceback
# import logging
# import io
# from datetime import datetime, timedelta
# from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
# import base64
# from google.cloud import vision
# from google.oauth2 import service_account
# from werkzeug.utils import secure_filename # Import secure_filename
# import joblib # Import joblib for loading ML models
# import pandas as pd # Import pandas for ML model input

# # Import numpy to handle float32 conversion (used in safe_float/convert_numpy_types if needed)
# import numpy as np

# # Import ReportLab components for PDF generation
# try:
#     # We are using a dummy PDF for now, so ReportLab is not strictly needed for functionality
#     # but the import block is kept for reference if actual PDF generation is implemented.
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     from reportlab.lib.units import inch
#     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
#     from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
#     from reportlab.lib.enums import TA_CENTER
#     REPORTLAB_AVAILABLE = True # Set to True if you install ReportLab
# except ImportError:
#     logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
#     REPORTLAB_AVAILABLE = False


# # Configure logging for better visibility
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Configuration (IMPORTANT: Use environment variables in production) ---
# # In a real-world production environment, these should ALWAYS be loaded from
# # environment variables (e.g., using os.getenv) and never hardcoded.
# GEMINI_API_KEY = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs" # Replace with your actual key or env var
# MONGO_URI = "mongodb://localhost:27017/"
# JWT_SECRET_KEY = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
# VISION_API_KEY_PATH = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json" # Path to your GCP service account key file

# # Initialize Flask app
# app = Flask(__name__, static_folder='static') # Serve static files from 'static' folder
# CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# # Setup Flask-JWT-Extended
# app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Token validity
# jwt = JWTManager(app)

# # Define the upload folder relative to the current working directory
# UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# logging.info(f"UPLOAD_FOLDER ensures existence: {UPLOAD_FOLDER}")

# # Custom error handlers for Flask-JWT-Extended to provide meaningful responses to the frontend
# @jwt.expired_token_loader
# def expired_token_callback(jwt_header, jwt_payload):
#     logging.warning("JWT token expired.")
#     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

# @jwt.invalid_token_loader
# def invalid_token_callback(callback_error):
#     logging.warning(f"Invalid JWT token: {callback_error}")
#     return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

# @jwt.unauthorized_loader
# def unauthorized_callback(callback_error):
#     logging.warning(f"Unauthorized access attempt: {callback_error}")
#     return jsonify({"message": "Bearer token missing or invalid", "error": "authorization_required"}), 401


# # Initialize MongoDB
# client = None
# db = None
# users_collection = None
# tax_records_collection = None
# contact_messages_collection = None
# try:
#     client = MongoClient(MONGO_URI)
#     db = client.garudatax_ai # Your database name
#     users_collection = db['users']
#     tax_records_collection = db['tax_records'] # Collection for processed tax documents
#     contact_messages_collection = db['contact_messages']
#     logging.info("MongoDB connected successfully.")
# except Exception as e:
#     logging.error(f"Could not connect to MongoDB: {e}")
#     db = None # Set db to None if connection fails

# # Configure Google Gemini API
# try:
#     genai.configure(api_key=GEMINI_API_KEY)
#     gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Or 'gemini-pro'
#     logging.info("Google Gemini API configured.")
# except Exception as e:
#     logging.error(f"Could not configure Google Gemini API: {e}")
#     gemini_model = None

# # Configure Google Cloud Vision API
# vision_client = None
# try:
#     if os.path.exists(VISION_API_KEY_PATH):
#         credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH)
#         vision_client = vision.ImageAnnotatorClient(credentials=credentials)
#         logging.info("Google Cloud Vision API configured.")
#     else:
#         logging.warning(f"Vision API key file not found at {VISION_API_KEY_PATH}. OCR functionality may be limited.")
# except Exception as e:
#     logging.error(f"Could not configure Google Cloud Vision API: {e}")
#     vision_client = None

# # Load ML Models (Classifier for Tax Regime, Regressor for Tax Liability)
# tax_regime_classifier_model = None
# tax_regressor_model = None
# try:
#     # Ensure these paths are correct relative to where app1.py is run
#     classifier_path = 'tax_regime_classifier_model.pkl'
#     regressor_path = 'final_tax_regressor_model.pkl'

#     if os.path.exists(classifier_path):
#         tax_regime_classifier_model = joblib.load(classifier_path)
#         logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
#     else:
#         logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

#     if os.path.exists(regressor_path):
#         tax_regressor_model = joblib.load(regressor_path)
#         logging.info(f"Tax Regressor model loaded from {regressor_path}.")
#     else:
#         logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

# except Exception as e:
#     logging.error(f"Error loading ML models: {e}. Ensure 'models/' directory exists and models are trained.")

# # --- Helper Functions ---
# def get_user_id():
#     """Retrieves user ID from JWT token."""
#     try:
#         return get_jwt_identity()
#     except Exception as e:
#         logging.warning(f"Could not get JWT identity: {e}")
#         return None

# def allowed_file(filename):
#     """Checks if the uploaded file has an allowed extension."""
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

# def ocr_document(file_bytes):
#     """Performs OCR on the document using Google Cloud Vision API."""
#     if not vision_client:
#         logging.error("Google Cloud Vision client not initialized.")
#         return {"error": "OCR service unavailable."}, None

#     image = vision.Image(content=file_bytes)
#     try:
#         response = vision_client.document_text_detection(image=image)
#         full_text = response.full_text_annotation.text
#         return None, full_text
#     except Exception as e:
#         logging.error(f"Error during OCR with Vision API: {traceback.format_exc()}")
#         return {"error": f"OCR failed: {e}"}, None

# def safe_float(val):
#     """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
#     Handles commas and currency symbols."""
#     try:
#         if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
#             return 0.0
#         if isinstance(val, str):
#             # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
#             val = val.replace(',', '').replace('₹', '').strip()
            
#         return float(val)
#     except (ValueError, TypeError):
#         logging.debug(f"Could not convert '{val}' to float. Defaulting to 0.0")
#         return 0.0

# def safe_string(val):
#     """Safely converts a value to string, defaulting to 'null' for None/empty strings."""
#     if val is None:
#         return "null"
#     s_val = str(val).strip()
#     if s_val == "":
#         return "null"
#     return s_val

# def convert_numpy_types(obj):
#     """
#     Recursively converts numpy types (like float32, int64) to standard Python types (float, int).
#     This prevents `TypeError: Object of type <numpy.generic> is not JSON serializable`.
#     """
#     if isinstance(obj, np.generic): # Covers np.float32, np.int64, etc.
#         return obj.item() # Converts numpy scalar to Python scalar
#     elif isinstance(obj, dict):
#         return {k: convert_numpy_types(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_numpy_types(elem) for elem in obj]
#     else:
#         return obj

# def get_gemini_response(prompt_text, file_data=None, mime_type=None, filename="unknown_file"):
#     """
#     Sends a prompt to Gemini and returns the structured JSON response.
#     If image/pdf data is provided, it first uses Vision API for OCR.
#     The response is strictly expected in a JSON format based on the defined schema.
#     """
#     try:
#         final_prompt_content = prompt_text
        
#         if file_data and mime_type and ("image" in mime_type or "pdf" in mime_type):
#             # If image or PDF, first extract text using Vision API
#             # OCR is performed in process_documents before calling this function for efficiency
#             pass # OCR content already in prompt_text from process_documents
            
#         else:
#             # For pure text inputs, assume prompt_text already contains all necessary info
#             logging.info(f"Processing text content directly with Gemini for '{filename}'.")
        
#         # --- DEFINITIVE JSON SCHEMA FOR GEMINI OUTPUT ---
#         # This schema MUST be comprehensive and match all keys expected by your frontend.
#         # Gemini will attempt to adhere to this schema and fill in defaults.
#         # Ensure all fields are explicitly defined to help Gemini produce consistent output.
#         response_schema = {
#             "type": "OBJECT",
#             "properties": {
#                 "identified_type": {"type": "STRING", "description": "Type of document, e.g., 'Form 16', 'Bank Statement', 'Form 26AS', 'Salary Slip', 'Investment Proof', 'Home Loan Statement', 'Other Document'. Choose the most relevant one if possible."},
#                 "employer_name": {"type": "STRING", "description": "Name of the Employer"},
#                 "employer_address": {"type": "STRING", "description": "Address of the Employer"},
#                 "pan_of_deductor": {"type": "STRING", "description": "PAN of the Employer (Deductor)"},
#                 "tan_of_deductor": {"type": "STRING", "description": "TAN of the Employer (Deductor)"},
#                 "name_of_employee": {"type": "STRING", "description": "Name of the Employee/Assessee"},
#                 "designation_of_employee": {"type": "STRING", "description": "Designation of the Employee"},
#                 "pan_of_employee": {"type": "STRING", "description": "PAN of the Employee/Assessee"},
#                 "date_of_birth": {"type": "STRING", "format": "date-time", "description": "Date of Birth (YYYY-MM-DD)"},
#                 "gender": {"type": "STRING", "description": "Gender (e.g., 'Male', 'Female', 'Other')"},
#                 "residential_status": {"type": "STRING", "description": "Residential Status (e.g., 'Resident', 'Non-Resident')"},
#                 "assessment_year": {"type": "STRING", "description": "Income Tax Assessment Year (e.g., '2024-25')"},
#                 "financial_year": {"type": "STRING", "description": "Financial Year (e.g., '2023-24')"},
#                 "period_from": {"type": "STRING", "format": "date-time", "description": "Start date of the document period (YYYY-MM-DD)"},
#                 "period_to": {"type": "STRING", "format": "date-time", "description": "End date of the document period (YYYY-MM-DD)"},
#                 "quarter_1_receipt_number": {"type": "STRING"},
#                 "quarter_1_tds_deducted": {"type": "NUMBER"},
#                 "quarter_1_tds_deposited": {"type": "NUMBER"},
#                 "total_tds_deducted_summary": {"type": "NUMBER", "description": "Total TDS deducted from salary (Form 16 Part A)"},
#                 "total_tds_deposited_summary": {"type": "NUMBER", "description": "Total TDS deposited from salary (Form 16 Part A)"},
#                 "salary_as_per_sec_17_1": {"type": "NUMBER", "description": "Salary as per Section 17(1)"},
#                 "value_of_perquisites_u_s_17_2": {"type": "NUMBER", "description": "Value of perquisites u/s 17(2)"},
#                 "profits_in_lieu_of_salary_u_s_17_3": {"type": "NUMBER", "description": "Profits in lieu of salary u/s 17(3)"},
#                 "gross_salary_total": {"type": "NUMBER", "description": "Total Gross Salary (sum of 17(1), 17(2), 17(3) from Form 16, or derived from payslip total earnings)"},
#                 "conveyance_allowance": {"type": "NUMBER"},
#                 "transport_allowance": {"type": "NUMBER"},
#                 "total_exempt_allowances": {"type": "NUMBER", "description": "Total allowances exempt u/s 10"},
#                 "balances_1_2": {"type": "NUMBER", "description": "Balance after subtracting allowances from gross salary"},
#                 "professional_tax": {"type": "NUMBER", "description": "Professional Tax"},
#                 "aggregate_of_deductions_from_salary": {"type": "NUMBER", "description": "Total deductions from salary (e.g., Prof Tax, Standard Deduction)"},
#                 "income_chargable_under_head_salaries": {"type": "NUMBER", "description": "Income chargeable under 'Salaries'"},
#                 "income_from_house_property": {"type": "NUMBER", "description": "Income From House Property (can be negative for loss)"},
#                 "income_from_other_sources": {"type": "NUMBER", "description": "Income From Other Sources (e.g., interest, dividend)"},
#                 "interest_on_housing_loan_self_occupied": {"type": "NUMBER", "description": "Interest on Housing Loan - Self Occupied Property"},
#                 "capital_gains_long_term": {"type": "NUMBER", "description": "Long Term Capital Gains"},
#                 "capital_gains_short_term": {"type": "NUMBER", "description": "Short Term Capital Gains"},
#                 "gross_total_income_as_per_document": {"type": "NUMBER", "description": "Gross total income as stated in the document"},
#                 "deduction_80c": {"type": "NUMBER", "description": "Total deduction under Section 80C (includes EPF, PPF, LIC, etc.)"},
#                 "deduction_80c_epf": {"type": "NUMBER", "description": "EPF contribution under 80C"},
#                 "deduction_80c_insurance_premium": {"type": "NUMBER", "description": "Life Insurance Premium under 80C"},
#                 "deduction_80ccc": {"type": "NUMBER", "description": "Deduction for contribution to certain pension funds under Section 80CCC"},
#                 "deduction_80ccd": {"type": "NUMBER", "description": "Deduction for contribution to NPS under Section 80CCD"},
#                 "deduction_80ccd1b": {"type": "NUMBER", "description": "Additional deduction under Section 80CCD(1B) for NPS"},
#                 "deduction_80d": {"type": "NUMBER", "description": "Deduction for Health Insurance Premium under Section 80D"},
#                 "deduction_80g": {"type": "NUMBER", "description": "Deduction for Donations under Section 80G"},
#                 "deduction_80tta": {"type": "NUMBER", "description": "Deduction for Interest on Savings Account under Section 80TTA"},
#                 "deduction_80ttb": {"type": "NUMBER", "description": "Deduction for Interest for Senior Citizens under Section 80TTB"},
#                 "deduction_80e": {"type": "NUMBER", "description": "Deduction for Interest on Education Loan under Section 80E"},
#                 "total_deductions_chapter_via": {"type": "NUMBER", "description": "Total of all deductions under Chapter VI-A"},
#                 "taxable_income_as_per_document": {"type": "NUMBER", "description": "Taxable Income as stated in the document"},
#                 "tax_payable_as_per_document": {"type": "NUMBER", "description": "Final tax payable as stated in the document"},
#                 "refund_status_as_per_document": {"type": "STRING", "description": "Refund status as stated in the document (e.g., 'Refund due', 'Tax payable', 'No demand no refund')"},
#                 "tax_regime_chosen": {"type": "STRING", "description": "Tax Regime Chosen (e.g., 'Old Regime' or 'New Regime' if explicitly indicated in document)"},
#                 "total_tds": {"type": "NUMBER", "description": "Total TDS credit from all sources (e.g., Form 26AS, Form 16 Part A)"},
#                 "advance_tax": {"type": "NUMBER", "description": "Advance Tax paid"},
#                 "self_assessment_tax": {"type": "NUMBER", "description": "Self-Assessment Tax paid"},
                
#                 # --- NEW PAYSLIP SPECIFIC FIELDS ---
#                 "basic_salary": {"type": "NUMBER", "description": "Basic Salary component from payslip"},
#                 "hra_received": {"type": "NUMBER", "description": "House Rent Allowance (HRA) received from payslip"},
#                 "epf_contribution": {"type": "NUMBER", "description": "Employee Provident Fund (EPF) contribution from payslip"},
#                 "esi_contribution": {"type": "NUMBER", "description": "Employee State Insurance (ESI) contribution from payslip"},
#                 "net_amount_payable": {"type": "NUMBER", "description": "Net amount payable (take home pay) from payslip"},
#                 "overtime_pay": {"type": "NUMBER", "description": "Overtime pay from payslip"},
#                 "overtime_hours": {"type": "STRING", "description": "Overtime hours from payslip (e.g., '100-0 Hrs')"},
#                 "days_present": {"type": "STRING", "description": "Days present from payslip (e.g., '250 Days')"},

#                 # Additional fields for Bank Statements (if applicable)
#                 "account_holder_name": {"type": "STRING", "description": "Name of the account holder"},
#                 "account_number": {"type": "STRING", "description": "Bank account number"},
#                 "ifsc_code": {"type": "STRING", "description": "IFSC code of the bank branch"},
#                 "bank_name": {"type": "STRING", "description": "Name of the bank"},
#                 "branch_address": {"type": "STRING", "description": "Address of the bank branch"},
#                 "statement_start_date": {"type": "STRING", "format": "date-time", "description": "Start date of the bank statement period (YYYY-MM-DD)"},
#                 "statement_end_date": {"type": "STRING", "format": "date-time", "description": "End date of the bank statement period (YYYY-MM-DD)"},
#                 "opening_balance": {"type": "NUMBER", "description": "Opening balance on the statement"},
#                 "closing_balance": {"type": "NUMBER", "description": "Closing balance on the statement"},
#                 "total_deposits": {"type": "NUMBER", "description": "Total deposits during the statement period"},
#                 "total_withdrawals": {"type": "NUMBER", "description": "Total withdrawals during the statement period"},
#                 "transaction_summary": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"date": {"type": "STRING", "format": "date-time", "description": "Date of the transaction (YYYY-MM-DD)"}, "description": {"type": "STRING"}, "amount": {"type": "NUMBER"}}}, "description": "A summary or key entries of transactions from the statement (e.g., large deposits/withdrawals)."}
#             },
#             "required": ["identified_type"] # Minimum required field from Gemini's side
#         }

#         generation_config = {
#             "response_mime_type": "application/json",
#             "response_schema": response_schema
#         }
        
#         # Call Gemini model with the prompt and schema
#         response = genai.GenerativeModel('gemini-2.0-flash').generate_content([{"text": final_prompt_content}], generation_config=generation_config)

#         if not response.text:
#             logging.warning(f"Gemini returned an empty response text for {filename}.")
#             # Return an error with an empty dictionary for extracted_data to prevent KeyError
#             return {"error": "Empty response from AI.", "extracted_data": {}}

#         # Clean the response text from markdown fences (```json ... ```) if present
#         response_text_cleaned = response.text.strip()
#         if response_text_cleaned.startswith("```json") and response_text_cleaned.endswith("```"):
#             response_text_cleaned = response_text_cleaned[len("```json"):].rstrip("```").strip()
#             logging.info("Stripped markdown JSON fences from Gemini response.")

#         try:
#             # Parse the cleaned JSON response from Gemini
#             parsed_json = json.loads(response_text_cleaned)
            
#             # --- CRITICAL FIX: Ensure all keys from schema are present and correctly typed ---
#             extracted_data = parsed_json # Gemini should return directly according to schema
#             final_extracted_data = {}

#             for key, prop_details in response_schema['properties'].items():
#                 if key in extracted_data and extracted_data[key] is not None:
#                     # Safely convert to the expected type
#                     if prop_details['type'] == 'NUMBER':
#                         final_extracted_data[key] = safe_float(extracted_data[key])
#                     elif prop_details['type'] == 'STRING':
#                         # Special handling for date formats if needed, otherwise just safe_string
#                         if 'format' in prop_details and prop_details['format'] == 'date-time':
#                             # Attempt to parse date, default if unable
#                             try:
#                                 dt_obj = datetime.strptime(str(extracted_data[key]).split('T')[0], '%Y-%m-%d')
#                                 final_extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
#                             except ValueError:
#                                 final_extracted_data[key] = "0000-01-01" # Default invalid date string
#                         else:
#                             final_extracted_data[key] = safe_string(extracted_data[key])
#                     elif prop_details['type'] == 'ARRAY':
#                         if key == "transaction_summary" and isinstance(extracted_data[key], list):
#                             # Process each transaction summary item
#                             processed_transactions = []
#                             for item in extracted_data[key]:
#                                 processed_item = {
#                                     "date": "0000-01-01", # Default date for transaction
#                                     "description": safe_string(item.get("description")),
#                                     "amount": safe_float(item.get("amount"))
#                                 }
#                                 if 'date' in item and item['date'] is not None:
#                                     try:
#                                         # Assuming transaction date might be YYYY-MM-DD or similar
#                                         dt_obj = datetime.strptime(str(item['date']).split('T')[0], '%Y-%m-%d')
#                                         processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
#                                     except ValueError:
#                                         pass # Keep default if parsing fails
#                                 processed_transactions.append(processed_item)
#                             final_extracted_data[key] = processed_transactions
#                         else:
#                             final_extracted_data[key] = extracted_data[key] if isinstance(extracted_data[key], list) else []
#                     else: # Fallback for other types
#                         final_extracted_data[key] = extracted_data[key]
#                 else:
#                     # Set default based on schema's type
#                     if prop_details['type'] == 'NUMBER':
#                         final_extracted_data[key] = 0.0
#                     elif prop_details['type'] == 'STRING':
#                         if 'format' in prop_details and prop_details['format'] == 'date-time':
#                             final_extracted_data[key] = "0000-01-01" # Default date string
#                         else:
#                             final_extracted_data[key] = "null" # Use string "null" as per schema description
#                     elif prop_details['type'] == 'ARRAY':
#                         final_extracted_data[key] = []
#                     else:
#                         final_extracted_data[key] = None # Generic default if type is not recognized

#             logging.info(f"Successfully retrieved and validated structured info from Gemini for {filename}.")
#             return {"error": None, "extracted_data": final_extracted_data}
#         except json.JSONDecodeError:
#             logging.error(f"Gemini response was not valid JSON for {filename}. Raw response: {response_text_cleaned[:500]}...")
#             return {"error": "Invalid JSON format from AI", "extracted_data": {"raw_text_response": response_text_cleaned}}
#         except Exception as e:
#             logging.error(f"Error processing Gemini's parsed JSON for {filename}: {traceback.format_exc()}")
#             return {"error": f"Error processing AI data: {str(e)}", "extracted_data": {}}

#     except Exception as e:
#         logging.error(f"Overall error in get_gemini_response for {filename}: {traceback.format_exc()}")
#         return {"error": str(e), "extracted_data": {}}


# def _aggregate_financial_data(extracted_data_list):
#     """
#     Aggregates financial data from multiple extracted documents, applying reconciliation rules.
#     Numerical fields are summed, and non-numerical fields are taken from the highest priority document.
#     """
    
#     aggregated_data = {
#         # Initialize all fields that are expected in the final aggregated output
#         "identified_type": "Other Document", # Overall identified type if mixed documents
#         "employer_name": "null", "employer_address": "null",
#         "pan_of_deductor": "null", "tan_of_deductor": "null",
#         "name_of_employee": "null", "designation_of_employee": "null", "pan_of_employee": "null",
#         "date_of_birth": "0000-01-01", "gender": "null", "residential_status": "null",
#         "assessment_year": "null", "financial_year": "null",
#         "period_from": "0000-01-01", "period_to": "0000-01-01",
        
#         # Income Components - These should be summed
#         "basic_salary": 0.0,
#         "hra_received": 0.0,
#         "conveyance_allowance": 0.0,
#         "transport_allowance": 0.0,
#         "overtime_pay": 0.0,
#         "salary_as_per_sec_17_1": 0.0,
#         "value_of_perquisites_u_s_17_2": 0.0,
#         "profits_in_lieu_of_salary_u_s_17_3": 0.0,
#         "gross_salary_total": 0.0, # This will be the direct 'Gross Salary' from Form 16/Payslip, or computed

#         "income_from_house_property": 0.0,
#         "income_from_other_sources": 0.0,
#         "capital_gains_long_term": 0.0,
#         "capital_gains_short_term": 0.0,

#         # Deductions - These should be summed, capped later if needed
#         "total_exempt_allowances": 0.0, # Will sum individual exempt allowances
#         "professional_tax": 0.0,
#         "interest_on_housing_loan_self_occupied": 0.0,
#         "deduction_80c": 0.0,
#         "deduction_80c_epf": 0.0,
#         "deduction_80c_insurance_premium": 0.0,
#         "deduction_80ccc": 0.0,
#         "deduction_80ccd": 0.0,
#         "deduction_80ccd1b": 0.0,
#         "deduction_80d": 0.0,
#         "deduction_80g": 0.0,
#         "deduction_80tta": 0.0,
#         "deduction_80ttb": 0.0,
#         "deduction_80e": 0.0,
#         "total_deductions_chapter_via": 0.0, # Will be calculated sum of 80C etc.
#         "epf_contribution": 0.0, # Initialize epf_contribution
#         "esi_contribution": 0.0, # Initialize esi_contribution


#         # Tax Paid
#         "total_tds": 0.0,
#         "advance_tax": 0.0,
#         "self_assessment_tax": 0.0,
#         "total_tds_deducted_summary": 0.0, # From Form 16 Part A

#         # Document Specific (Non-summable, usually taken from most authoritative source)
#         "tax_regime_chosen": "null", # U/s 115BAC or Old Regime

#         # Bank Account Details (Take from the most complete or latest if multiple)
#         "account_holder_name": "null", "account_number": "null", "ifsc_code": "null",
#         "bank_name": "null", "branch_address": "null",
#         "statement_start_date": "0000-01-01", "statement_end_date": "0000-01-01",
#         "opening_balance": 0.0, "closing_balance": 0.0,
#         "total_deposits": 0.0, "total_withdrawals": 0.0,
#         "transaction_summary": [], # Aggregate all transactions

#         # Other fields from the schema, ensuring they exist
#         "net_amount_payable": 0.0,
#         "days_present": "null",
#         "overtime_hours": "null",

#         # Calculated fields for frontend
#         "Age": "N/A", 
#         "total_gross_income": 0.0, # Overall sum of all income heads
#         "standard_deduction": 50000.0, # Fixed as per current Indian tax laws
#         "interest_on_housing_loan_24b": 0.0, # Alias for interest_on_housing_loan_self_occupied
#         "deduction_80C": 0.0, # Alias for deduction_80c
#         "deduction_80CCD1B": 0.0, # Alias for deduction_80ccd1b
#         "deduction_80D": 0.0, # Alias for deduction_80d
#         "deduction_80G": 0.0, # Alias for deduction_80g
#         "deduction_80TTA": 0.0, # Alias for deduction_80tta
#         "deduction_80TTB": 0.0, # Alias for deduction_80ttb
#         "deduction_80E": 0.0, # Alias for deduction_80e
#         "total_deductions": 0.0, # Overall total deductions used in calculation
#     }

#     # Define document priority for overriding fields (higher value means higher priority)
#     # Form 16 should provide definitive income/deduction figures.
#     doc_priority = {
#         "Form 16": 5,
#         "Form 26AS": 4,
#         "Salary Slip": 3,
#         "Investment Proof": 2,
#         "Home Loan Statement": 2,
#         "Bank Statement": 1,
#         "Other Document": 0,
#         "Unknown": 0,
#         "Unstructured Text": 0 # For cases where Gemini fails to extract structured data
#     }

#     # Sort documents by priority (higher priority first)
#     sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

#     # Use a dictionary to track which field was last set by which document priority
#     # This helps in overriding with higher-priority document data.
#     field_source_priority = {key: -1 for key in aggregated_data}

#     # Iterate through sorted documents and aggregate data
#     for data in sorted_extracted_data:
#         doc_type = safe_string(data.get('identified_type'))
#         current_priority = doc_priority.get(doc_type, 0)
#         logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

#         # Explicitly handle gross_salary_total. If it comes from Form 16, it's definitive.
#         # Otherwise, individual components will be summed later.
#         extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
#         if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
#             aggregated_data["gross_salary_total"] = extracted_gross_salary_total
#             field_source_priority["gross_salary_total"] = current_priority
#             logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

#         # Update core personal details only from highest priority document or if current is 'null'
#         personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
#         for p_field in personal_fields:
#             if safe_string(data.get(p_field)) != "null" and \
#                (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
#                 aggregated_data[p_field] = safe_string(data.get(p_field))
#                 field_source_priority[p_field] = current_priority


#         for key, value in data.items():
#             # Skip keys already handled explicitly or which have specific aggregation logic
#             if key in personal_fields or key == "gross_salary_total":
#                 continue 
#             if key == "transaction_summary":
#                 if isinstance(value, list):
#                     aggregated_data[key].extend(value)
#                 continue
#             if key == "identified_type":
#                 # Ensure highest priority identified_type is kept
#                 if current_priority > field_source_priority.get(key, -1):
#                     aggregated_data[key] = safe_string(value)
#                     field_source_priority[key] = current_priority
#                 continue
            
#             # General handling for numerical fields: sum them up
#             if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
#                 # Special handling for bank balances: take from latest/highest priority statement
#                 if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
#                     if doc_type == "Bank Statement": # For bank statements, these are cumulative or final
#                         # Only update if the current document is a bank statement and has higher or equal priority
#                         # (or if the existing aggregated value is 0)
#                         if current_priority >= field_source_priority.get(key, -1):
#                             aggregated_data[key] = safe_float(value)
#                             field_source_priority[key] = current_priority
#                     else: # For other document types, just sum the numbers if they appear
#                         aggregated_data[key] += safe_float(value)
#                 else:
#                     aggregated_data[key] += safe_float(value)
#             # General handling for string fields: take from highest priority document
#             elif key in aggregated_data and isinstance(aggregated_data[key], str):
#                 if safe_string(value) != "null" and safe_string(value) != "" and \
#                    (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
#                     aggregated_data[key] = safe_string(value)
#                     field_source_priority[key] = current_priority
#             # Default for other types if they are not explicitly handled
#             elif key in aggregated_data and value is not None:
#                 if current_priority > field_source_priority.get(key, -1):
#                     aggregated_data[key] = value
#                     field_source_priority[key] = current_priority

#     # --- Post-aggregation calculations and reconciliation ---
    
#     # Calculate `total_gross_income` (overall income from all heads)
#     # If `gross_salary_total` is still 0 (meaning no direct GSI from Form 16),
#     # try to derive it from payslip components like basic, HRA, etc.
#     if aggregated_data["gross_salary_total"] == 0.0:
#         aggregated_data["gross_salary_total"] = (
#             safe_float(aggregated_data["basic_salary"]) +
#             safe_float(aggregated_data["hra_received"]) +
#             safe_float(aggregated_data["conveyance_allowance"]) +
#             safe_float(aggregated_data["transport_allowance"]) + # Added transport allowance
#             safe_float(aggregated_data["overtime_pay"]) +
#             safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
#             safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
#         )
#         # Note: If basic_salary, HRA, etc. are monthly, this sum needs to be multiplied by 12.
#         # Assuming extracted values are already annual or normalized.

#     # Now calculate the comprehensive total_gross_income for tax computation
#     aggregated_data["total_gross_income"] = (
#         safe_float(aggregated_data["gross_salary_total"]) +
#         safe_float(aggregated_data["income_from_house_property"]) +
#         safe_float(aggregated_data["income_from_other_sources"]) + 
#         safe_float(aggregated_data["capital_gains_long_term"]) +
#         safe_float(aggregated_data["capital_gains_short_term"])
#     )
#     aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

#     # Ensure `deduction_80c` includes `epf_contribution` if not already counted by Gemini
#     # This prevents double counting if EPF is reported separately and also included in 80C
#     # Logic: if 80C is zero, and EPF is non-zero, assume EPF *is* the 80C.
#     # If 80C is non-zero, assume EPF is already part of it, or if separate, it will be added.
#     # For now, let's sum them if 80C explicitly extracted is low, to ensure EPF is captured.
#     if safe_float(aggregated_data["epf_contribution"]) > 0:
#         aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
#     # Correctly sum up all Chapter VI-A deductions (this will be capped by tax law later)
#     aggregated_data["total_deductions_chapter_via"] = (
#         safe_float(aggregated_data["deduction_80c"]) +
#         safe_float(aggregated_data["deduction_80ccc"]) +
#         safe_float(aggregated_data["deduction_80ccd"]) +
#         safe_float(aggregated_data["deduction_80ccd1b"]) +
#         safe_float(aggregated_data["deduction_80d"]) +
#         safe_float(aggregated_data["deduction_80g"]) +
#         safe_float(aggregated_data["deduction_80tta"]) +
#         safe_float(aggregated_data["deduction_80ttb"]) +
#         safe_float(aggregated_data["deduction_80e"])
#     )
#     aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)


#     # Aliases for frontend (ensure these are correctly populated from derived values)
#     aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
#     # If `total_exempt_allowances` is still 0, but individual components are non-zero, sum them.
#     # This is a fallback and might not always reflect actual exemptions as per tax rules.
#     if aggregated_data["total_exempt_allowances"] == 0.0:
#         aggregated_data["total_exempt_allowances"] = (
#             safe_float(aggregated_data.get("conveyance_allowance")) +
#             safe_float(aggregated_data.get("transport_allowance")) +
#             safe_float(aggregated_data.get("hra_received")) 
#         )
#         logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

#     # Apply standard deduction of 50,000 for salaried individuals regardless of regime (from AY 2024-25)
#     # This is a fixed amount applied during tax calculation, not a sum from documents.
#     aggregated_data["standard_deduction"] = 50000.0 

#     # Calculate Age (assuming 'date_of_birth' is available and in YYYY-MM-DD format)
#     dob_str = safe_string(aggregated_data.get("date_of_birth"))
#     if dob_str != "null" and dob_str != "0000-01-01":
#         try:
#             dob = datetime.strptime(dob_str, '%Y-%m-%d')
#             today = datetime.now()
#             age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#             aggregated_data["Age"] = age
#         except ValueError:
#             logging.warning(f"Could not parse date_of_birth: {dob_str}")
#             aggregated_data["Age"] = "N/A"
#     else:
#         aggregated_data["Age"] = "N/A" # Set to N/A if DOB is null or invalid

#     # Populate aliases for frontend display consistency
#     aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
#     aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
#     aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
#     aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
#     aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
#     aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
#     aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
#     aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
#     aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

#     # Final overall total deductions considered for tax calculation (this will be capped by law, see tax calculation)
#     # This should include standard deduction, professional tax, home loan interest, and Chapter VI-A deductions.
#     # The actual 'total_deductions' for tax computation will be derived in `calculate_final_tax_summary` based on regime.
#     # For display, we can show sum of what's *claimed* or *extracted*.
#     # Let's make `total_deductions` a sum of all potential deductions for display.
#     aggregated_data["total_deductions"] = (
#         aggregated_data["standard_deduction"] + 
#         aggregated_data["professional_tax"] +
#         aggregated_data["interest_on_housing_loan_self_occupied"] +
#         aggregated_data["total_deductions_chapter_via"]
#     )
#     aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


#     # Sort all_transactions by date (oldest first)
#     for tx in aggregated_data['transaction_summary']:
#         if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
#             try:
#                 tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
#             except ValueError:
#                 tx['date_sortable'] = datetime.min # Fallback for unparseable dates
#         else:
#             tx['date_sortable'] = datetime.min

#     aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
#     # Remove the temporary sortable key
#     for tx in aggregated_data['transaction_summary']:
#         tx.pop('date_sortable', None)

#     # If identified_type is still "null" or "Unknown" and some other fields populated,
#     # try to infer a better type if possible, or leave as "Other Document"
#     if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
#         if safe_string(aggregated_data.get('employer_name')) != "null" and \
#            safe_float(aggregated_data.get('gross_salary_total')) > 0:
#            aggregated_data["identified_type"] = "Salary Related Document" # Could be Form 16 or Payslip
#         elif safe_string(aggregated_data.get('account_number')) != "null" and \
#              (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
#              aggregated_data["identified_type"] = "Bank Statement"
#         elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
#              safe_float(aggregated_data.get('hra_received')) > 0 or \
#              safe_float(aggregated_data.get('net_amount_payable')) > 0: # More robust check for payslip
#              aggregated_data["identified_type"] = "Salary Slip"

#     # Ensure PAN and Financial Year are properly set for database grouping
#     # If not extracted, try to get from previous records or default to "null"
#     if safe_string(aggregated_data.get("pan_of_employee")) == "null":
#         aggregated_data["pan_of_employee"] = "UNKNOWNPAN" # A placeholder for missing PAN

#     # Derive financial year from assessment year if financial_year is null
#     if safe_string(aggregated_data.get("financial_year")) == "null" and safe_string(aggregated_data.get("assessment_year")) != "null":
#         try:
#             ay_parts = aggregated_data["assessment_year"].split('-')
#             if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
#                 start_year = int(ay_parts[0]) -1
#                 end_year = int(ay_parts[0])
#                 aggregated_data["financial_year"] = f"{start_year}-{str(end_year)[-2:]}"
#         except Exception:
#             logging.warning(f"Could not derive financial year from assessment year: {aggregated_data.get('assessment_year')}")
#             aggregated_data["financial_year"] = "UNKNOWNFY"
#     elif safe_string(aggregated_data.get("financial_year")) == "null":
#         aggregated_data["financial_year"] = "UNKNOWNFY" # A placeholder for missing FY
        
#     logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
#     return aggregated_data

# def calculate_final_tax_summary(aggregated_data):
#     """
#     Calculates the estimated tax payable and refund status based on aggregated financial data.
#     This function implements a SIMPLIFIED Indian income tax calculation for demonstration.
#     !!! IMPORTANT: This must be replaced with actual, up-to-date, and comprehensive
#     Indian income tax laws, considering both Old and New regimes, age groups,
#     surcharges, cess, etc., for a production system. !!!

#     Args:
#         aggregated_data (dict): A dictionary containing aggregated financial fields.

#     Returns:
#         dict: A dictionary with computed tax liability, refund/due status, and notes.
#     """
    
#     # Safely extract and convert relevant values from aggregated_data
#     gross_total_income = safe_float(aggregated_data.get("total_gross_income", 0))
#     # Deductions used for tax calculation (subject to limits and regime)
#     total_chapter_via_deductions = safe_float(aggregated_data.get("total_deductions_chapter_via", 0)) 
#     professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
#     standard_deduction_applied = safe_float(aggregated_data.get("standard_deduction", 0)) # Ensure standard deduction is fetched
#     interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))

#     # Sum all TDS and advance tax for comparison
#     total_tds_credit = (
#         safe_float(aggregated_data.get("total_tds", 0)) + 
#         safe_float(aggregated_data.get("advance_tax", 0)) + 
#         safe_float(aggregated_data.get("self_assessment_tax", 0))
#     )

#     tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
#     age = aggregated_data.get('Age', "N/A") # Get age, will be N/A if not calculated
#     if age == "N/A":
#         age_group = "General"
#     elif age < 60:
#         age_group = "General"
#     elif age >= 60 and age < 80:
#         age_group = "Senior Citizen"
#     else: # age >= 80
#         age_group = "Super Senior Citizen"

#     # --- Calculation Details List (for frontend display) ---
#     calculation_details = []

#     # --- Check for insufficient data for tax computation ---
#     if gross_total_income < 100.0 and total_chapter_via_deductions < 100.0 and total_tds_credit < 100.0:
#         calculation_details.append("Insufficient data provided for comprehensive tax calculation. Please upload documents with income and deduction details.")
#         return {
#             "calculated_gross_income": gross_total_income,
#             "calculated_total_deductions": 0.0, # No significant deductions processed yet
#             "computed_taxable_income": 0.0,
#             "estimated_tax_payable": 0.0,
#             "total_tds_credit": total_tds_credit,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "predicted_tax_regime": "N/A",
#             "notes": ["Tax computation not possible. Please upload documents containing sufficient income (e.g., Form 16, Salary Slips) and/or deductions (e.g., investment proofs)."],
#             "old_regime_tax_payable": 0.0,
#             "new_regime_tax_payable": 0.0,
#             "calculation_details": calculation_details,
#         }

#     calculation_details.append(f"1. Gross Total Income (Aggregated): ₹{gross_total_income:,.2f}")

#     # --- Old Tax Regime Calculation ---
#     # Deductions allowed in Old Regime: Standard Deduction (for salaried), Professional Tax, Housing Loan Interest, Chapter VI-A deductions (80C, 80D, etc.)
#     # Chapter VI-A deductions are capped at their respective limits or overall 1.5L for 80C, etc.
#     # For simplicity, we'll use the extracted `total_deductions_chapter_via` but it should ideally be capped.
#     # The actual tax deduction limits should be applied here.
    
#     # Cap 80C related deductions at 1.5 Lakhs
#     deduction_80c_actual = min(safe_float(aggregated_data.get("deduction_80c", 0)), 150000.0)
#     # Cap 80D (Health Insurance) - simplified max 25k for general, 50k for senior parent (adjust as per actual rules)
#     deduction_80d_actual = min(safe_float(aggregated_data.get("deduction_80d", 0)), 25000.0) 
#     # Cap Housing Loan Interest for self-occupied at 2 Lakhs
#     interest_on_housing_loan_actual = min(safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0)), 200000.0)

#     # Simplified Chapter VI-A deductions for old regime (summing specific 80C, 80D, 80CCD1B, 80E, 80G, 80TTA, 80TTB)
#     total_chapter_via_deductions_old_regime = (
#         deduction_80c_actual +
#         safe_float(aggregated_data.get("deduction_80ccc", 0)) +
#         safe_float(aggregated_data.get("deduction_80ccd", 0)) +
#         safe_float(aggregated_data.get("deduction_80ccd1b", 0)) +
#         safe_float(aggregated_data.get("deduction_80d", 0)) + # Corrected to use deduction_80d_actual later if needed
#         safe_float(aggregated_data.get("deduction_80g", 0)) +
#         safe_float(aggregated_data.get("deduction_80tta", 0)) +
#         safe_float(aggregated_data.get("deduction_80ttb", 0)) +
#         safe_float(aggregated_data.get("deduction_80e", 0))
#     )
#     total_chapter_via_deductions_old_regime = round(total_chapter_via_deductions_old_regime, 2)


#     # Total deductions for Old Regime
#     total_deductions_old_regime_for_calc = (
#         standard_deduction_applied + 
#         professional_tax + 
#         interest_on_housing_loan_actual + 
#         total_chapter_via_deductions_old_regime
#     )
#     total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

#     taxable_income_old_regime = max(0, gross_total_income - total_deductions_old_regime_for_calc)
#     tax_before_cess_old_regime = 0

#     calculation_details.append(f"2. Deductions under Old Regime:")
#     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
#     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
#     calculation_details.append(f"   - Interest on Housing Loan (Section 24(b) capped at ₹2,00,000): ₹{interest_on_housing_loan_actual:,.2f}")
#     calculation_details.append(f"   - Section 80C (capped at ₹1,50,000): ₹{deduction_80c_actual:,.2f}")
#     calculation_details.append(f"   - Section 80D (capped at ₹25,000/₹50,000): ₹{deduction_80d_actual:,.2f}")
#     calculation_details.append(f"   - Other Chapter VI-A Deductions: ₹{(total_chapter_via_deductions_old_regime - deduction_80c_actual - deduction_80d_actual):,.2f}")
#     calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
#     calculation_details.append(f"3. Taxable Income (Old Regime): Gross Total Income - Total Deductions = ₹{taxable_income_old_regime:,.2f}")

#     # Old Regime Tax Slabs (simplified for AY 2024-25)
#     if age_group == "General":
#         if taxable_income_old_regime <= 250000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 250000) * 0.05
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = 12500 + (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 112500 + (taxable_income_old_regime - 1000000) * 0.30
#     elif age_group == "Senior Citizen": # 60 to < 80
#         if taxable_income_old_regime <= 300000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 300000) * 0.05
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = 10000 + (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 110000 + (taxable_income_old_regime - 1000000) * 0.30
#     else: # Super Senior Citizen >= 80
#         if taxable_income_old_regime <= 500000:
#             tax_before_cess_old_regime = 0
#         elif taxable_income_old_regime <= 1000000:
#             tax_before_cess_old_regime = (taxable_income_old_regime - 500000) * 0.20
#         else:
#             tax_before_cess_old_regime = 100000 + (taxable_income_old_regime - 1000000) * 0.30

#     rebate_87a_old_regime = 0
#     if taxable_income_old_regime <= 500000: # Rebate limit for Old Regime is 5 Lakhs
#         rebate_87a_old_regime = min(tax_before_cess_old_regime, 12500)
    
#     tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
#     total_tax_old_regime = round(tax_after_rebate_old_regime * 1.04, 2) # Add 4% Health and Education Cess
#     calculation_details.append(f"4. Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
#     calculation_details.append(f"5. Rebate U/S 87A (Old Regime, if taxable income <= ₹5,00,000): ₹{rebate_87a_old_regime:,.2f}")
#     calculation_details.append(f"6. Tax after Rebate (Old Regime): ₹{tax_after_rebate_old_regime:,.2f}")
#     calculation_details.append(f"7. Total Tax Payable (Old Regime, with 4% Cess): ₹{total_tax_old_regime:,.2f}")


#     # --- New Tax Regime Calculation ---
#     # From AY 2024-25, standard deduction is also applicable in the New Regime for salaried individuals.
#     # Most Chapter VI-A deductions are *not* allowed in the New Regime, except employer's NPS contribution u/s 80CCD(2).
#     # For simplicity, we assume only standard deduction and professional tax are applicable.
#     # Also, housing loan interest deduction is NOT allowed for self-occupied property in New Regime.

#     taxable_income_new_regime = max(0, gross_total_income - standard_deduction_applied - professional_tax) 
#     # For simplification, we are not considering 80CCD(2) here. Add if needed for precision.
#     tax_before_cess_new_regime = 0

#     calculation_details.append(f"8. Deductions under New Regime:")
#     calculation_details.append(f"   - Standard Deduction: ₹{standard_deduction_applied:,.2f}")
#     calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
#     calculation_details.append(f"   - Total Deductions (New Regime): ₹{(standard_deduction_applied + professional_tax):,.2f}") # Only allowed ones
#     calculation_details.append(f"9. Taxable Income (New Regime): Gross Total Income - Total Deductions = ₹{taxable_income_new_regime:,.2f}")


#     # New Regime Tax Slabs (simplified for AY 2024-25 onwards)
#     # Corrected the indentation here based on previous user input.
#     slabs_to_use = [
#         (0, 300000, 0.0),
#         (300000, 600000, 0.05),
#         (600000, 900000, 0.10),
#         (900000, 1200000, 0.15),
#         (1200000, 1500000, 0.20),
#         (1500000, float('inf'), 0.30)
#     ]
    
#     tax_calculated = 0.0
#     taxable_income = taxable_income_new_regime # Use new regime taxable income for this slab calculation
#     for lower_bound, upper_bound, rate in slabs_to_use:
#         if taxable_income > lower_bound:
#             Slab_income = min(taxable_income, upper_bound) - lower_bound
#             tax_calculated += Slab_income * rate
#             logging.debug(f"Slab: {lower_bound}-{upper_bound}, Income in slab: {Slab_income}, Rate: {rate}, Tax from slab: {Slab_income * rate}")

#     tax_before_cess_new_regime = round(tax_calculated) # Round to nearest Rupee

#     rebate_87a_new_regime = 0
#     if taxable_income_new_regime <= 700000: # Rebate limit for New Regime is 7 Lakhs
#         rebate_87a_new_regime = min(tax_before_cess_new_regime, 25000) # Maximum rebate is 25000
    
#     tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
#     total_tax_new_regime = round(tax_after_rebate_new_regime * 1.04, 2) # Add 4% Health and Education Cess

#     calculation_details.append(f"10. Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
#     calculation_details.append(f"11. Rebate U/S 87A (New Regime, if taxable income <= ₹7,00,000): ₹{rebate_87a_new_regime:,.2f}")
#     calculation_details.append(f"12. Total Tax Payable (New Regime, with 4% Cess): ₹{total_tax_new_regime:,.2f}")


#     # --- Determine Optimal Regime and Final Summary ---
#     final_tax_regime_applied = "N/A"
#     estimated_tax_payable = 0.0
#     computed_taxable_income = 0.0
#     computation_notes = []

#     # If the document indicates "U/s 115BAC", it means the New Regime was chosen.
#     if tax_regime_chosen_by_user and ("115BAC" in tax_regime_chosen_by_user or "New Regime" in tax_regime_chosen_by_user):
#         estimated_tax_payable = total_tax_new_regime
#         computed_taxable_income = taxable_income_new_regime
#         final_tax_regime_applied = "New Regime (Chosen by User from Document)"
#         computation_notes.append(f"Tax computed as per New Tax Regime based on document indication (U/s 115BAC). Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}.")
#     elif tax_regime_chosen_by_user and "Old Regime" in tax_regime_chosen_by_user:
#         estimated_tax_payable = total_tax_old_regime
#         computed_taxable_income = taxable_income_old_regime
#         final_tax_regime_applied = "Old Regime (Chosen by User from Document)"
#         computation_notes.append(f"Tax computed as per Old Tax Regime based on document indication. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}.")
#     else: # If no regime is explicitly chosen in documents, recommend the optimal one
#         if total_tax_old_regime <= total_tax_new_regime:
#             estimated_tax_payable = total_tax_old_regime
#             computed_taxable_income = taxable_income_old_regime
#             final_tax_regime_applied = "Old Regime (Optimal)"
#             computation_notes.append(f"Old Regime appears optimal for your income and deductions. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
#         else:
#             estimated_tax_payable = total_tax_new_regime
#             computed_taxable_income = taxable_income_new_regime
#             final_tax_regime_applied = "New Regime (Optimal)"
#             computation_notes.append(f"New Regime appears optimal for your income and deductions. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

#     estimated_tax_payable = round(estimated_tax_payable, 2)
#     computed_taxable_income = round(computed_taxable_income, 2)

#     # --- Calculate Refund/Tax Due ---
#     refund_due_from_tax = 0.0
#     tax_due_to_government = 0.0

#     calculation_details.append(f"13. Total Tax Paid (TDS, Advance Tax, etc.): ₹{total_tds_credit:,.2f}")
#     if total_tds_credit > estimated_tax_payable:
#         refund_due_from_tax = total_tds_credit - estimated_tax_payable
#         calculation_details.append(f"14. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
#     elif total_tds_credit < estimated_tax_payable:
#         tax_due_to_government = estimated_tax_payable - total_tds_credit
#         calculation_details.append(f"14. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
#     else:
#         calculation_details.append("14. No Refund or Additional Tax Due.")


#     return {
#         "calculated_gross_income": gross_total_income,
#         "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else (standard_deduction_applied + professional_tax), # Show relevant deductions
#         "computed_taxable_income": computed_taxable_income,
#         "estimated_tax_payable": estimated_tax_payable,
#         "total_tds_credit": total_tds_credit,
#         "predicted_refund_due": round(refund_due_from_tax, 2), # Renamed for consistency with frontend
#         "predicted_additional_due": round(tax_due_to_government, 2), # Renamed for consistency with frontend
#         "predicted_tax_regime": final_tax_regime_applied, # Renamed for consistency with frontend
#         "notes": computation_notes, # List of notes
#         "old_regime_tax_payable": total_tax_old_regime,
#         "new_regime_tax_payable": total_tax_new_regime,
#         "calculation_details": calculation_details,
#     }

# def generate_ml_prediction_summary(financial_data):
#     """
#     Generates ML model prediction summary using the loaded models.
#     """
#     if tax_regime_classifier_model is None or tax_regressor_model is None:
#         logging.warning("ML models are not loaded. Cannot generate ML predictions.")
#         return {
#             "predicted_tax_regime": "N/A",
#             "predicted_tax_liability": 0.0,
#             "predicted_refund_due": 0.0,
#             "predicted_additional_due": 0.0,
#             "notes": "ML prediction service unavailable (models not loaded or training failed)."
#         }

#     # Define the features expected by the ML models (must match model_trainer.py)
#     # IMPORTANT: These must precisely match the features used in model_trainer.py
#     # Re-verify against your `model_trainer.py` to ensure exact match.
#     ml_common_numerical_features = [
#         'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
#         'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
#         'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
#         'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
#         'Total Exempt Allowances Claimed'
#     ]
#     ml_categorical_features = ['Residential Status', 'Gender']
    
#     # Prepare input for classifier model
#     age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
#     # Calculate 'Other Deductions (80CCD, 80G, etc.) Claimed' for input
#     # This sums all Chapter VI-A deductions *minus* 80C, 80D, 80E which are explicitly listed.
#     # This should include 80CCC, 80CCD, 80CCD1B, 80G, 80TTA, 80TTB.
#     calculated_other_deductions = (
#         safe_float(financial_data.get('deduction_80ccc', 0)) +
#         safe_float(financial_data.get('deduction_80ccd', 0)) +
#         safe_float(financial_data.get('deduction_80ccd1b', 0)) +
#         safe_float(financial_data.get('deduction_80g', 0)) +
#         safe_float(financial_data.get('deduction_80tta', 0)) +
#         safe_float(financial_data.get('deduction_80ttb', 0))
#     )
#     calculated_other_deductions = round(calculated_other_deductions, 2)


#     classifier_input_data = {
#         'Age': age_value,
#         'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
#         'HRA Received': safe_float(financial_data.get('hra_received', 0)),
#         'Rent Paid': 0.0, # Placeholder. If your documents extract rent, map it here.
#         'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
#         'Standard Deduction Claimed': safe_float(financial_data.get('standard_deduction', 50000)),
#         'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
#         'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
#         'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
#         'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
#         'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
#         'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
#         'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
#         'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')), # Default to Resident
#         'Gender': safe_string(financial_data.get('gender', 'Unknown'))
#     }
    
#     # Create DataFrame for classifier prediction, ensuring column order
#     # The order must match `model_trainer.py`'s `classifier_all_features`
#     ordered_classifier_features = ml_common_numerical_features + ml_categorical_features
#     classifier_df = pd.DataFrame([classifier_input_data])
    
#     predicted_tax_regime = "N/A"
#     try:
#         classifier_df_processed = classifier_df[ordered_classifier_features]
#         predicted_tax_regime = tax_regime_classifier_model.predict(classifier_df_processed)[0]
#         logging.info(f"ML Predicted tax regime: {predicted_tax_regime}")
#     except Exception as e:
#         logging.error(f"Error predicting tax regime with ML model: {traceback.format_exc()}")
#         predicted_tax_regime = "Prediction Failed (Error)"
        
#     # Prepare input for regressor model
#     # The regressor expects common numerical features PLUS the predicted tax regime as a categorical feature
#     regressor_input_data = {
#         k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
#     }
#     regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime # Add the predicted regime as a feature for regression

#     regressor_df = pd.DataFrame([regressor_input_data])
    
#     predicted_tax_liability = 0.0
#     try:
#         # The regressor's preprocessor will handle the categorical feature conversion.
#         # Just ensure the input DataFrame has the correct columns and order.
#         ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen'] # Must match regressor_all_features from trainer
#         regressor_df_processed = regressor_df[ordered_regressor_features]
#         predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
#         logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
#     except Exception as e:
#         logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
#         predicted_tax_liability = 0.0 # Default to 0 if prediction fails

#     # Calculate refund/additional due based on ML prediction and actual TDS
#     total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

#     predicted_refund_due = 0.0
#     predicted_additional_due = 0.0

#     if total_tds_credit > predicted_tax_liability:
#         predicted_refund_due = total_tds_credit - predicted_tax_liability
#     elif total_tds_credit < predicted_tax_liability:
#         predicted_additional_due = predicted_tax_liability - total_tds_credit
        
#     # Convert any numpy types before returning
#     return convert_numpy_types({
#         "predicted_tax_regime": predicted_tax_regime,
#         "predicted_tax_liability": predicted_tax_liability,
#         "predicted_refund_due": round(predicted_refund_due, 2),
#         "predicted_additional_due": round(predicted_additional_due, 2),
#         "notes": "ML model predictions for optimal regime and tax liability."
#     })

# def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
#     """Generates tax-saving suggestions and regime analysis using Gemini API."""
#     if gemini_model is None: # Changed gemini_pro_model to gemini_model
#         logging.error("Gemini API (gemini_model) not initialized.")
#         return ["AI suggestions unavailable."], "AI regime analysis unavailable."

#     # Check if tax computation was not possible
#     if "Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]:
#         return (
#             ["Please upload your Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts) for a comprehensive tax analysis and personalized tax-saving suggestions."],
#             "Tax regime analysis requires complete income and deduction data."
#         )

#     # Prepare a copy of financial data to avoid modifying the original and for targeted prompting
#     financial_data_for_gemini = aggregated_financial_data.copy()

#     # Add specific structure for Bank Statement details if identified as such, or if bank details are present
#     if financial_data_for_gemini.get('identified_type') == 'Bank Statement':
#         financial_data_for_gemini['Bank Details'] = {
#             'Account Holder': financial_data_for_gemini.get('account_holder_name', 'N/A'),
#             'Account Number': financial_data_for_gemini.get('account_number', 'N/A'),
#             'Bank Name': financial_data_for_gemini.get('bank_name', 'N/A'),
#             'Opening Balance': financial_data_for_gemini.get('opening_balance', 0.0),
#             'Closing Balance': financial_data_for_gemini.get('closing_balance', 0.0),
#             'Total Deposits': financial_data_for_gemini.get('total_deposits', 0.0),
#             'Total Withdrawals': financial_data_for_gemini.get('total_withdrawals', 0.0),
#             'Statement Period': f"{financial_data_for_gemini.get('statement_start_date', 'N/A')} to {financial_data_for_gemini.get('statement_end_date', 'N/A')}"
#         }
#         # Optionally, remove transaction_summary if it's too verbose for the prompt
#         # financial_data_for_gemini.pop('transaction_summary', None)


#     prompt = f"""
#     You are an expert Indian tax advisor. Analyze the provided financial and tax computation data for an Indian taxpayer.
    
#     Based on this data:
#     1. Provide 3-5 clear, concise, and actionable tax-saving suggestions specific to Indian income tax provisions (e.g., maximizing 80C, 80D, NPS, HRA, etc.). If current deductions are low, suggest increasing them. If already maximized, suggest alternative.
#     2. Provide a brief and clear analysis (2-3 sentences) comparing the Old vs New Tax Regimes. Based on the provided income and deductions, explicitly state which regime appears more beneficial for the taxpayer.

#     **Financial Data Summary:**
#     {json.dumps(financial_data_for_gemini, indent=2)}

#     **Final Tax Computation Summary:**
#     {json.dumps(final_tax_computation_summary, indent=2)}

#     Please format your response strictly as follows:
#     Suggestions:
#     - [Suggestion 1]
#     - [Suggestion 2]
#     ...
#     Regime Analysis: [Your analysis paragraph here].
#     """
#     try:
#         response = gemini_model.generate_content(prompt) # Changed gemini_pro_model to gemini_model
#         text = response.text.strip()
        
#         suggestions = []
#         regime_analysis = ""

#         # Attempt to parse the structured output
#         if "Suggestions:" in text and "Regime Analysis:" in text:
#             parts = text.split("Regime Analysis:")
#             suggestions_part = parts[0].replace("Suggestions:", "").strip()
#             regime_analysis = parts[1].strip()

#             # Split suggestions into bullet points and filter out empty strings
#             suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
#             if not suggestions: # If parsing as bullets failed, treat as single suggestion
#                 suggestions = [suggestions_part]
#         else:
#             # Fallback if format is not as expected, return raw text as suggestions
#             suggestions = ["AI could not parse structured suggestions. Raw AI output:", text]
#             regime_analysis = "AI could not parse structured regime analysis."
#             logging.warning(f"Gemini response did not match expected format. Raw response: {text[:500]}...")

#         return suggestions, regime_analysis
#     except Exception as e:
#         logging.error(f"Error generating Gemini suggestions: {traceback.format_exc()}")
#         return ["Failed to generate AI suggestions due to an error."], "Failed to generate AI regime analysis."

# def generate_itr_pdf(tax_record_data):
#     """
#     Generates a dummy ITR form PDF.
#     This uses a basic PDF string structure as a placeholder.
#     """
#     aggregated_data = tax_record_data.get('aggregated_financial_data', {})
#     final_computation = tax_record_data.get('final_tax_computation_summary', {})

#     # Determine ITR type (simplified logic)
#     itr_type = "ITR-1 (SAHAJ - DUMMY)"
#     if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
#        safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
#        safe_float(aggregated_data.get('income_from_house_property', 0)) < 0: # Loss from HP
#         itr_type = "ITR-2 (DUMMY)"
    
#     # Extract key info for the dummy PDF
#     name = aggregated_data.get('name_of_employee', 'N/A')
#     pan = aggregated_data.get('pan_of_employee', 'N/A')
#     financial_year = aggregated_data.get('financial_year', 'N/A')
#     assessment_year = aggregated_data.get('assessment_year', 'N/A')
#     total_income = final_computation.get('computed_taxable_income', 'N/A')
#     tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
#     refund_due = final_computation.get('predicted_refund_due', 0.0)
#     tax_due = final_computation.get('predicted_additional_due', 0.0)
#     regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

#     # Add bank statement specific details to the PDF content if available
#     bank_details_for_pdf = ""
#     if aggregated_data.get('identified_type') == 'Bank Statement' or \
#        (aggregated_data.get('account_holder_name') != 'null' and aggregated_data.get('account_number') != 'null'):
#         bank_details_for_pdf = f"""
# BT /F1 12 Tf 100 380 Td (Bank Details:) Tj ET
# BT /F1 10 Tf 100 365 Td (Account Holder Name: {aggregated_data.get('account_holder_name', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 350 Td (Account Number: {aggregated_data.get('account_number', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 335 Td (Bank Name: {aggregated_data.get('bank_name', 'N/A')}) Tj ET
# BT /F1 10 Tf 100 320 Td (Opening Balance: {safe_float(aggregated_data.get('opening_balance', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 305 Td (Closing Balance: {safe_float(aggregated_data.get('closing_balance', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 290 Td (Total Deposits: {safe_float(aggregated_data.get('total_deposits', 0)):,.2f}) Tj ET
# BT /F1 10 Tf 100 275 Td (Total Withdrawals: {safe_float(aggregated_data.get('total_withdrawals', 0)):,.2f}) Tj ET
# """

#     # Core PDF content without xref and EOF for length calculation
#     core_pdf_content_lines = [
#         f"%PDF-1.4",
#         f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
#         f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
#         f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
#         f"4 0 obj <</Length 700>> stream", # Increased length to accommodate more text
#         f"BT /F1 24 Tf 100 750 Td ({itr_type} - Tax Filing Summary) Tj ET",
#         f"BT /F1 12 Tf 100 720 Td (Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj ET",
#         f"BT /F1 12 Tf 100 690 Td (Financial Year: {financial_year}) Tj ET",
#         f"BT /F1 12 Tf 100 670 Td (Assessment Year: {assessment_year}) Tj ET",
#         f"BT /F1 12 Tf 100 640 Td (Name: {name}) Tj ET",
#         f"BT /F1 12 Tf 100 620 Td (PAN: {pan}) Tj ET",
#         f"BT /F1 12 Tf 100 590 Td (Aggregated Gross Income: {safe_float(aggregated_data.get('total_gross_income', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 570 Td (Total Deductions: {safe_float(aggregated_data.get('total_deductions', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 550 Td (Computed Taxable Income: {total_income}) Tj ET",
#         f"BT /F1 12 Tf 100 530 Td (Estimated Tax Payable: {tax_payable}) Tj ET",
#         f"BT /F1 12 Tf 100 510 Td (Total Tax Paid (TDS, Adv. Tax, etc.): {safe_float(final_computation.get('total_tds_credit', 0)):,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 490 Td (Tax Regime Applied: {regime_considered}) Tj ET",
#         f"BT /F1 12 Tf 100 460 Td (Refund Due: {refund_due:,.2f}) Tj ET",
#         f"BT /F1 12 Tf 100 440 Td (Tax Due to Govt: {tax_due:,.2f}) Tj ET",
#     ]
    
#     # Append bank details if available
#     if bank_details_for_pdf:
#         core_pdf_content_lines.append(bank_details_for_pdf)
#         # Adjust vertical position for the Note if bank details were added
#         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 240 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")
#     else:
#         core_pdf_content_lines.append(f"BT /F1 10 Tf 100 410 Td (Note: This is a DUMMY PDF for demonstration purposes only. Do not use for official tax filing.) Tj ET")

#     core_pdf_content_lines.extend([
#         f"endstream",
#         f"endobj",
#         f"xref",
#         f"0 5",
#         f"0000000000 65535 f",
#         f"0000000010 00000 n",
#         f"0000000057 00000 n",
#         f"0000000114 00000 n",
#         f"0000000222 00000 n",
#         f"trailer <</Size 5 /Root 1 0 R>>",
#     ])
    
#     # Join lines to form the content string, encoding to 'latin-1' early to get correct byte length
#     core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
#     core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace') # Replace unencodable chars

#     # Calculate the startxref position
#     startxref_position = len(core_pdf_bytes)

#     # Now assemble the full PDF content including startxref and EOF
#     full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
#     # Final encode
#     dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

#     return io.BytesIO(dummy_pdf_content_bytes), itr_type


# # --- API Routes ---

# # Serves the main page (assuming index.html is in the root)
# @app.route('/')
# def home():
#     """Serves the main landing page, typically index.html."""
#     return send_from_directory('.', 'index.html')

# # Serves other static files (CSS, JS, images, etc.)
# @app.route('/<path:path>')
# def serve_static_files(path):
#     """Serves static files from the root directory."""
#     # Prevent directory traversal if ".." in path or path.startswith('/'):
#     if ".." in path or path.startswith('/'):
#         return "Forbidden", 403
#     return send_from_directory('.', path)

# # Serves uploaded files from the uploads folder
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     """Allows access to temporarily stored uploaded files."""
#     try:
#         # Ensure filename is safe to prevent directory traversal
#         safe_filename = secure_filename(filename)
#         return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)
#     except FileNotFoundError:
#         logging.warning(f"File '{filename}' not found in uploads folder.")
#         return jsonify({"message": "File not found"}), 404
#     except Exception as e:
#         logging.error(f"Error serving uploaded file '{filename}': {traceback.format_exc()}")
#         return jsonify({"message": "Failed to retrieve file", "error": str(e)}), 500


# @app.route('/api/register', methods=['POST'])
# def register_user():
#     """Handles user registration."""
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')

#         if not username or not email or not password:
#             logging.warning("Registration attempt with missing fields.")
#             return jsonify({"message": "Username, email, and password are required"}), 400

#         # Check if email or username already exists
#         if users_collection.find_one({"email": email}):
#             logging.warning(f"Registration failed: Email '{email}' already exists.")
#             return jsonify({"message": "Email already exists"}), 409
#         if users_collection.find_one({"username": username}):
#             logging.warning(f"Registration failed: Username '{username}' already exists.")
#             return jsonify({"message": "Username already exists"}), 409

#         # Hash the password before storing
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         # Prepare user data for MongoDB insertion
#         new_user_data = {
#             "username": username,
#             "email": email,
#             "password": hashed_password.decode('utf-8'), # Store hashed password as string
#             "full_name": data.get('fullName', ''),
#             "pan": data.get('pan', ''),
#             "aadhaar": data.get('aadhaar', ''),
#             "address": data.get('address', ''),
#             "phone": data.get('phone', ''),
#             "created_at": datetime.utcnow()
#         }
#         # Insert the new user record and get the inserted ID
#         user_id = users_collection.insert_one(new_user_data).inserted_id
#         logging.info(f"User '{username}' registered successfully with ID: {user_id}.")
#         return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
#     except Exception as e:
#         logging.error(f"Error during registration: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred during registration."}), 500

# @app.route('/api/login', methods=['POST'])
# def login_user():
#     """Handles user login and JWT token generation."""
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')

#         if not username or not password:
#             logging.warning("Login attempt with missing credentials.")
#             return jsonify({"error_msg": "Username and password are required"}), 400

#         # Find the user by username
#         user = users_collection.find_one({"username": username})

#         # Verify user existence and password
#         if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
#             # Create a JWT access token with the user's MongoDB ObjectId as identity
#             access_token = create_access_token(identity=str(user['_id']))
#             logging.info(f"User '{username}' logged in successfully.")
#             return jsonify({"jwt_token": access_token, "message": "Login successful!"}), 200
#         else:
#             logging.warning(f"Failed login attempt for username: '{username}' (invalid credentials).")
#             return jsonify({"error_msg": "Invalid credentials"}), 401
#     except Exception as e:
#         logging.error(f"Error during login: {traceback.format_exc()}")
#         return jsonify({"error_msg": "An error occurred during login."}), 500

# @app.route('/api/profile', methods=['GET'])
# @jwt_required()
# def get_user_profile():
#     """Fetches the profile of the currently authenticated user."""
#     try:
#         # Get user ID from JWT token (this will be the MongoDB ObjectId as a string)
#         current_user_id = get_jwt_identity()
#         # Find user by ObjectId, exclude password from the result
#         user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
#         if not user:
#             logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
#             return jsonify({"message": "User not found"}), 404

#         # Convert ObjectId to string for JSON serialization
#         user['_id'] = str(user['_id'])
#         logging.info(f"Profile fetched for user ID: {current_user_id}")
#         return jsonify({"user": user}), 200
#     except Exception as e:
#         logging.error(f"Error fetching user profile for ID {get_jwt_identity()}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to fetch user profile", "error": str(e)}), 500

# @app.route('/api/profile', methods=['PUT', 'PATCH'])
# @jwt_required()
# def update_user_profile():
#     """Updates the profile of the currently authenticated user."""
#     try:
#         current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#         data = request.get_json()

#         # Define allowed fields for update
#         updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
#         update_data = {k: data[k] for k in updatable_fields if k in data}

#         if not update_data:
#             logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
#             return jsonify({"message": "No fields to update provided."}), 400
        
#         # Prevent username from being updated via this route for security/simplicity
#         if 'username' in data:
#             logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

#         # If email is being updated, ensure it's not already in use by another user
#         if 'email' in update_data:
#             existing_user_with_email = users_collection.find_one({"email": update_data['email']})
#             if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
#                 logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
#                 return jsonify({"message": "Email already in use by another account."}), 409

#         # Perform the update operation in MongoDB
#         result = users_collection.update_one(
#             {"_id": ObjectId(current_user_id)}, # Query using ObjectId for the _id field
#             {"$set": update_data}
#         )

#         if result.matched_count == 0:
#             logging.warning(f"Profile update failed: User {current_user_id} not found in DB for update.")
#             return jsonify({"message": "User not found."}), 404
#         if result.modified_count == 0:
#             logging.info(f"Profile for user {current_user_id} was already up to date, no changes made.")
#             return jsonify({"message": "Profile data is the same, no changes made."}), 200

#         logging.info(f"Profile updated successfully for user ID: {current_user_id}")
#         return jsonify({"message": "Profile updated successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error updating profile for user {get_jwt_identity()}: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while updating your profile."}), 500


# @app.route('/api/process_documents', methods=['POST'])
# @jwt_required()
# def process_documents():
#     """
#     Handles uploaded documents, extracts financial data using Gemini and Vision API,
#     aggregates data from multiple files, computes tax, and saves the comprehensive
#     record to MongoDB, grouped by PAN and Financial Year.
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string

#     if 'documents' not in request.files:
#         logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
#         return jsonify({"message": "No 'documents' part in the request"}), 400

#     files = request.files.getlist('documents')
#     if not files:
#         logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
#         return jsonify({"message": "No selected file"}), 400

#     extracted_data_from_current_upload = []
#     document_processing_summary_current_upload = [] # To provide feedback on each file

#     # Get the selected document type hint from the form data (if provided)
#     document_type_hint = request.form.get('document_type', 'Auto-Detect') 
#     logging.info(f"Received document type hint from frontend: {document_type_hint}")

#     for file in files:
#         if file.filename == '':
#             document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
#             continue
        
#         filename = secure_filename(file.filename)
#         # Create a unique filename for storing the original document
#         unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
#         try:
#             file_content_bytes = file.read() # Read content before saving
#             file.seek(0) # Reset file pointer for subsequent operations if needed

#             # Save the file temporarily (or permanently if you wish to retain originals)
#             with open(file_path, 'wb') as f:
#                 f.write(file_content_bytes)
#             logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

#             mime_type = file.mimetype or 'application/octet-stream' # Get MIME type or default
            
#             document_text_content = ""
#             if "image" in mime_type or "pdf" in mime_type:
#                 error_ocr, ocr_text = ocr_document(file_content_bytes)
#                 if error_ocr:
#                     logging.error(f"OCR failed for {filename}: {error_ocr['error']}")
#                     document_processing_summary_current_upload.append({
#                         "filename": filename, "status": "failed_ocr", "message": f"OCR failed: {error_ocr['error']}",
#                         "stored_path": f"/uploads/{unique_filename}"
#                     })
#                     continue # Skip to next file
#                 document_text_content = ocr_text
#             elif "text" in mime_type or "json" in mime_type:
#                 document_text_content = file_content_bytes.decode('utf-8', errors='ignore')
#             else:
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "skipped", "identified_type": "Unsupported",
#                     "message": f"Unsupported file type: {mime_type}", "stored_path": f"/uploads/{unique_filename}"
#                 })
#                 continue
            
#             if not document_text_content.strip():
#                 logging.warning(f"No extractable text found in {filename}.")
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "no_text_extracted", "message": "No text could be extracted from the document.",
#                     "stored_path": f"/uploads/{unique_filename}"
#                 })
#                 continue

#             # Construct the base prompt for Gemini
#             base_prompt_instructions = (
#                 f"You are an expert financial data extractor and tax document analyzer for Indian context. "
#                 f"Analyze the provided document (filename: '{filename}', MIME type: {mime_type}). "
#                 f"The user has indicated this document is of type: '{document_type_hint}'. " 
#                 "Extract ALL relevant financial information for Indian income tax filing. "
#                 "Your response MUST be a JSON object conforming precisely to the provided schema. "
#                 "For numerical fields, if a value is not explicitly found or is clearly zero, you MUST use `0.0`. "
#                 "For string fields (like names, PAN, year, dates, identified_type, gender, residential_status), if a value is not explicitly found, you MUST use the string `null`. "
#                 "For dates, if found, use 'YYYY-MM-DD' format if possible; otherwise, `0000-01-01` if not found or cannot be parsed.\n\n"
#             )

#             # Add specific instructions based on document type hint
#             if document_type_hint == 'Bank Statement':
#                 base_prompt_instructions += (
#                     "Specifically for a Bank Statement, extract the following details accurately:\n"
#                     "- Account Holder Name\n- Account Number\n- IFSC Code (if present)\n- Bank Name\n"
#                     "- Branch Address\n- Statement Start Date (YYYY-MM-DD)\n- Statement End Date (YYYY-MM-DD)\n"
#                     "- Opening Balance\n- Closing Balance\n- Total Deposits\n- Total Withdrawals\n"
#                     "- A summary of key transactions, including date (YYYY-MM-DD), description, and amount. Prioritize large transactions or those with specific identifiable descriptions (e.g., 'salary', 'rent', 'interest').\n"
#                     "If a field is not found or not applicable, use `null` for strings and `0.0` for numbers. Ensure dates are in YYYY-MM-DD format."
#                 )
#             elif document_type_hint == 'Form 16':
#                 base_prompt_instructions += (
#                     "Specifically for Form 16, extract details related to employer, employee, PAN, TAN, financial year, assessment year, "
#                     "salary components (basic, HRA, perquisites, profits in lieu of salary), exempt allowances, professional tax, "
#                     "income from house property, income from other sources, capital gains, "
#                     "deductions under Chapter VI-A (80C, 80D, 80G, 80E, 80CCD, etc.), TDS details (total, quarter-wise), "
#                     "and any mentioned tax regime (Old/New). Ensure all monetary values are extracted as numbers."
#                 )
#             elif document_type_hint == 'Salary Slip':
#                 base_prompt_instructions += (
#                     "Specifically for a Salary Slip, extract employee name, PAN, employer name, basic salary, HRA, "
#                     "conveyance allowance, transport allowance, overtime pay, EPF contribution, ESI contribution, "
#                     "professional tax, net amount payable, days present, and overtime hours. Ensure all monetary values are extracted as numbers."
#                 )
#             # Add more elif blocks for other specific document types if needed

#             final_prompt_content = base_prompt_instructions + f"\n\n--- Document Content for Extraction ---\n{document_text_content}"
#             gemini_response_parsed = get_gemini_response(final_prompt_content, filename=filename) # No file_data here as OCR is done

#             if gemini_response_parsed.get("error"):
#                 logging.error(f"Gemini processing error for '{filename}': {gemini_response_parsed['error']}")
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "failed", "message": f"AI processing error: {gemini_response_parsed['error']}",
#                     "stored_path": f"/uploads/{unique_filename}"
#                 })
#                 continue
            
#             extracted_data = gemini_response_parsed.get('extracted_data', {})
#             if "raw_text_response" in extracted_data:
#                 document_processing_summary_current_upload.append({
#                     "filename": filename, "status": "warning", "identified_type": "Unstructured Text",
#                     "message": "AI could not extract structured JSON. Raw text available.",
#                     "extracted_raw_text": extracted_data["raw_text_response"],
#                     "stored_path": f"/uploads/{unique_filename}"
#                 })
#                 extracted_data_from_current_upload.append({"identified_type": "Unstructured Text", "raw_text": extracted_data["raw_text_response"]})
#                 continue 
            
#             # Add the path to the stored document for future reference in history
#             extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
#             extracted_data_from_current_upload.append(extracted_data)

#             document_processing_summary_current_upload.append({
#                 "filename": filename, "status": "success", "identified_type": extracted_data.get('identified_type', 'Unknown'),
#                 "message": "Processed successfully.", "extracted_fields": extracted_data,
#                 "stored_path": f"/uploads/{unique_filename}" 
#             })
#         except Exception as e:
#             logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
#             document_processing_summary_current_upload.append({
#                 "filename": filename, "status": "error",
#                 "message": f"An unexpected error occurred during file processing: {str(e)}",
#                 "stored_path": f"/uploads/{unique_filename}"
#             })
#             continue 

#     if not extracted_data_from_current_upload:
#         logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
#         return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

#     # --- Determine PAN and Financial Year for grouping ---
#     # Try to find PAN and FY from the currently uploaded documents first
#     pan_of_employee = "UNKNOWNPAN"
#     financial_year = "UNKNOWNFY"

#     for data in extracted_data_from_current_upload:
#         if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
#             pan_of_employee = safe_string(data["pan_of_employee"])
#         if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
#             financial_year = safe_string(data["financial_year"])
#         # If both are found, we can break early (or continue to see if a higher priority doc has them)
#         if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
#             break
    
#     # If still unknown, check if the user profile has a PAN.
#     if pan_of_employee == "UNKNOWNPAN":
#         user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
#         if user_profile and safe_string(user_profile.get("pan")) != "null":
#             pan_of_employee = safe_string(user_profile["pan"])
#             logging.info(f"Using PAN from user profile: {pan_of_employee}")
#         else:
#             # If PAN is still unknown, log a warning and use the placeholder
#             logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

#     # Derive financial year from assessment year if financial_year is null
#     if financial_year == "UNKNOWNFY":
#         for data in extracted_data_from_current_upload:
#             if safe_string(data.get("assessment_year")) != "null":
#                 try:
#                     ay_parts = safe_string(data["assessment_year"]).split('-')
#                     if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
#                         start_year = int(ay_parts[0]) -1
#                         fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
#                         if fy != "UNKNOWNFY": # Only assign if a valid FY was derived
#                             financial_year = fy
#                             break
#                 except Exception:
#                     pass # Keep default if parsing fails
#         if financial_year == "UNKNOWNFY":
#             logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


#     # Try to find an existing record for this user, PAN, and financial year
#     existing_tax_record = tax_records_collection.find_one({
#         "user_id": current_user_id,
#         "aggregated_financial_data.pan_of_employee": pan_of_employee,
#         "aggregated_financial_data.financial_year": financial_year
#     })

#     if existing_tax_record:
#         logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
#         # Merge new extracted data with existing data
#         all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
#         all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

#         # Re-aggregate ALL data for this financial year to ensure consistency and correct reconciliation
#         updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
#         updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

#         # Clear previous AI/ML results as they need to be re-generated for the updated data
#         tax_records_collection.update_one(
#             {"_id": existing_tax_record["_id"]},
#             {"$set": {
#                 "extracted_documents_data": all_extracted_data_for_fy,
#                 "document_processing_summary": all_document_processing_summary_for_fy,
#                 "aggregated_financial_data": updated_aggregated_financial_data,
#                 "final_tax_computation_summary": updated_final_tax_computation_summary,
#                 "timestamp": datetime.utcnow(), # Update timestamp of last modification
#                 "suggestions_from_gemini": [], # Reset suggestions
#                 "gemini_regime_analysis": "null", # Reset regime analysis
#                 "ml_prediction_summary": {}, # Reset ML predictions
#             }}
#         )
#         record_id = existing_tax_record["_id"]
#         logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

#     else:
#         logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
#         # If no existing record, aggregate only the newly uploaded data
#         new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
#         new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

#         # Prepare the comprehensive tax record to save to MongoDB
#         tax_record_to_save = {
#             "user_id": current_user_id, 
#             "pan_of_employee": pan_of_employee, # Store PAN at top level for easy query
#             "financial_year": financial_year, # Store FY at top level for easy query
#             "timestamp": datetime.utcnow(),
#             "document_processing_summary": document_processing_summary_current_upload, 
#             "extracted_documents_data": extracted_data_from_current_upload, 
#             "aggregated_financial_data": new_aggregated_financial_data,
#             "final_tax_computation_summary": new_final_tax_computation_summary,
#             "suggestions_from_gemini": [], 
#             "gemini_regime_analysis": "null", 
#             "ml_prediction_summary": {},    
#         }
#         record_id = tax_records_collection.insert_one(tax_record_to_save).inserted_id
#         logging.info(f"New tax record created for user {current_user_id}. Record ID: {record_id}")
        
#         updated_aggregated_financial_data = new_aggregated_financial_data
#         updated_final_tax_computation_summary = new_final_tax_computation_summary


#     # Return success response with computed data
#     # Ensure all data sent back is JSON serializable (e.g., no numpy types)
#     response_data = {
#         "status": "success",
#         "message": "Documents processed and financial data aggregated and tax computed successfully",
#         "record_id": str(record_id), 
#         "document_processing_summary": document_processing_summary_current_upload, # Summary of current upload only
#         "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data), # Ensure conversion
#         "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary), # Ensure conversion
#     }
#     return jsonify(response_data), 200


# @app.route('/api/get_suggestions', methods=['POST'])
# @jwt_required()
# def get_suggestions():
#     """
#     Generates AI-driven tax-saving suggestions and provides an ML prediction summary
#     based on a specific processed tax record (grouped by PAN/FY).
#     """
#     current_user_id = get_jwt_identity()

#     data = request.get_json()
#     record_id = data.get('record_id')

#     if not record_id:
#         logging.warning(f"Suggestions request from user {current_user_id} with missing record_id.")
#         return jsonify({"message": "Record ID is required to get suggestions."}), 400

#     try:
#         # Retrieve the tax record using its ObjectId and ensuring it belongs to the current user
#         tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
#         if not tax_record:
#             logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
#         # Get the aggregated financial data and final tax computation summary from the record
#         aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
#         final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

#         # Generate suggestions and ML predictions
#         suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
#         ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data) # Pass aggregated data

#         # Update the record in DB with generated suggestions and predictions
#         tax_records_collection.update_one(
#             {"_id": ObjectId(record_id)},
#             {"$set": {
#                 "suggestions_from_gemini": suggestions,
#                 "gemini_regime_analysis": regime_analysis,
#                 "ml_prediction_summary": ml_prediction_summary, # This will be already converted by generate_ml_prediction_summary
#                 "analysis_timestamp": datetime.utcnow() # Optional: add a timestamp for when analysis was done
#             }}
#         )
#         logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

#         return jsonify({
#             "status": "success",
#             "message": "AI suggestions and ML predictions generated successfully!",
#             "suggestions_from_gemini": suggestions,
#             "gemini_regime_analysis": regime_analysis,
#             "ml_prediction_summary": ml_prediction_summary # Already converted
#         }), 200
#     except Exception as e:
#         logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
#         # Fallback for ML prediction summary even if overall suggestions fail
#         ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {}))
#         return jsonify({
#             "status": "error",
#             "message": "An error occurred while generating suggestions.",
#             "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
#             "gemini_regime_analysis": "An error occurred.",
#             "ml_prediction_summary": ml_prediction_summary_fallback # Already converted
#         }), 500

# @app.route('/api/save_extracted_data', methods=['POST'])
# @jwt_required()
# def save_extracted_data():
#     """
#     Saves extracted and computed tax data to MongoDB.
#     This route can be used for explicit saving if `process_documents` doesn't
#     cover all saving scenarios or for intermediate saves.
#     NOTE: With the new PAN/FY grouping, this route's utility might change or be deprecated.
#     For now, it's kept as-is, but `process_documents` is the primary entry point for new data.
#     """
#     current_user_id = get_jwt_identity() # User's MongoDB ObjectId as a string
#     data = request.get_json()
#     if not data:
#         logging.warning(f"Save data request from user {current_user_id} with no data provided.")
#         return jsonify({"message": "No data provided to save"}), 400
#     try:
#         # This route might be less relevant with the new aggregation by PAN/FY,
#         # as `process_documents` handles the upsert logic.
#         # However, if used for manual saving of *already aggregated* data,
#         # ensure PAN and FY are part of `data.aggregated_financial_data`
#         # or extracted from the `data` directly.
#         # Example: Try to get PAN and FY from input data for consistency
#         input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
#         input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

#         # Check for existing record for upsert behavior
#         existing_record = tax_records_collection.find_one({
#             "user_id": current_user_id,
#             "aggregated_financial_data.pan_of_employee": input_pan,
#             "aggregated_financial_data.financial_year": input_fy
#         })

#         if existing_record:
#             # Update existing record
#             update_result = tax_records_collection.update_one(
#                 {"_id": existing_record["_id"]},
#                 {"$set": {
#                     **data, # Overwrite with new data, ensuring user_id and timestamp are also set
#                     "user_id": current_user_id,
#                     "timestamp": datetime.utcnow(),
#                     "pan_of_employee": input_pan, # Ensure top-level PAN is consistent
#                     "financial_year": input_fy, # Ensure top-level FY is consistent
#                 }}
#             )
#             record_id = existing_record["_id"]
#             logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
#             if update_result.modified_count == 0:
#                 return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
#         else:
#             # Insert new record
#             data['user_id'] = current_user_id
#             data['timestamp'] = datetime.utcnow()
#             data['pan_of_employee'] = input_pan
#             data['financial_year'] = input_fy
#             record_id = tax_records_collection.insert_one(data).inserted_id
#             logging.info(f"New data saved for user {current_user_id} with record ID: {record_id}")
        
#         return jsonify({"message": "Data saved successfully", "record_id": str(record_id)}), 200
#     except Exception as e:
#         logging.error(f"Error saving data for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to save data", "error": str(e)}), 500

# # --- Corrected route path to /tax-records to match frontend call ---
# @app.route('/api/tax-records', methods=['GET'])
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
#             # Remove potentially large raw data fields for history list view to save bandwidth
#             record.pop('extracted_documents_data', None)
#         logging.info(f"Found {len(records)} tax records for user {current_user_id}")
#         # The frontend's TaxHistory component expects a 'history' key in the response data.
#         return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200 # Convert numpy types
#     except Exception as e:
#         logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

# # --- Corrected route path to /api/generate-itr/ to match frontend call ---
# @app.route('/api/generate-itr/<record_id>', methods=['GET'])
# @jwt_required()
# def generate_itr_form_route(record_id):
#     """
#     Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
#     """
#     current_user_id = get_jwt_identity()
#     try:
#         record_obj_id = ObjectId(record_id) # Convert record_id string to ObjectId for DB query
#         # Ensure the tax record belongs to the current user (user_id check)
#         tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

#         if not tax_record:
#             logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or you are not authorized to access it."}), 404

#         # Generate the dummy PDF content
#         pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
#         pdf_buffer.seek(0) # Rewind the buffer to the beginning

#         response = send_file(
#             pdf_buffer,
#             mimetype='application/pdf',
#             as_attachment=True,
#             download_name=f"{itr_type.replace(' ', '_')}_{record_id}.pdf"
#         )
#         logging.info(f"Generated and sent dummy ITR form for record ID: {record_id}")
#         return response
#     except Exception as e:
#         logging.error(f"Error generating ITR form for record {record_id}: {traceback.format_exc()}")
#         return jsonify({"message": "Failed to generate ITR form.", "error": str(e)}), 500

# @app.route('/api/delete_record/<record_id>', methods=['DELETE'])
# @jwt_required()
# def delete_record(record_id):
#     """
#     Deletes a tax record for the authenticated user.
#     """
#     current_user_id = get_jwt_identity()
#     try:
#         result = tax_records_collection.delete_one({"_id": ObjectId(record_id), "user_id": current_user_id})
#         if result.deleted_count == 0:
#             logging.warning(f"Delete failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
#             return jsonify({"message": "Tax record not found or unauthorized."}), 404
#         logging.info(f"Record {record_id} deleted successfully for user {current_user_id}.")
#         return jsonify({"message": "Record deleted successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error deleting record {record_id} for user {current_user_id}: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while deleting the record.", "error": str(e)}), 500

# @app.route('/api/contact', methods=['POST'])
# def contact_message():
#     """Handles contact form submissions."""
#     try:
#         data = request.get_json()
#         name = data.get('name')
#         email = data.get('email')
#         subject = data.get('subject')
#         message = data.get('message')

#         if not all([name, email, subject, message]):
#             logging.warning("Contact form submission with missing fields.")
#             return jsonify({"message": "All fields are required."}), 400
        
#         # Insert contact message into MongoDB
#         contact_messages_collection.insert_one({
#             "name": name,
#             "email": email,
#             "subject": subject,
#             "message": message,
#             "timestamp": datetime.utcnow()
#         })
#         logging.info(f"New contact message from {name} ({email}) saved to MongoDB.")

#         return jsonify({"message": "Message sent successfully!"}), 200
#     except Exception as e:
#         logging.error(f"Error handling contact form submission: {traceback.format_exc()}")
#         return jsonify({"message": "An error occurred while sending your message."}), 500

# # --- Main application entry point ---
# if __name__ == '__main__':
#     # Ensure MongoDB connection is established before running the app
#     if db is None:
#         logging.error("MongoDB connection failed at startup. Exiting.")
#         exit(1)
    
#     logging.info("Starting Flask application...")
#     # Run the Flask app
#     # debug=True enables reloader and debugger (should be False in production)
#     # host='0.0.0.0' makes the server accessible externally (e.g., in Docker or cloud)
#     # use_reloader=False prevents double-loading issues in some environments (e.g., when integrated with external runners)
#     app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)















































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
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, decode_token
import base64
from google.cloud import vision
from google.oauth2 import service_account
from werkzeug.utils import secure_filename
import joblib
import pandas as pd
import numpy as np

# Import ReportLab components for PDF generation
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    logging.error("ReportLab library not found. PDF generation will be disabled. Please install it using 'pip install reportlab'.")
    REPORTLAB_AVAILABLE = False


# Configure logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration (IMPORTANT: Use environment variables in production) ---
GEMINI_API_KEY = "AIzaSyDuGBK8Qnp4i2K4LLoS-9GY_OSSq3eTsLs" # Replace with your actual key or env var
MONGO_URI = "mongodb://localhost:27017/"
JWT_SECRET_KEY = "P_fN-t3j2q8y7x6w5v4u3s2r1o0n9m8l7k6j5i4h3g2f1e0d"
VISION_API_KEY_PATH = r"C:\Users\gumma\Downloads\All_Projects\GarudaTaxAi\vision_key.json" # Path to your GCP service account key file

# Initialize Flask app
app = Flask(__name__, static_folder='static') # Serve static files from 'static' folder
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Setup Flask-JWT-Extended
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # Token validity
jwt = JWTManager(app)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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


# Initialize MongoDB
client = None
db = None
users_collection = None
tax_records_collection = None
contact_messages_collection = None
try:
    client = MongoClient(MONGO_URI)
    db = client.garudatax_ai # Your database name
    users_collection = db['users']
    tax_records_collection = db['tax_records'] # Collection for processed tax documents
    contact_messages_collection = db['contact_messages']
    logging.info("MongoDB connected successfully.")
except Exception as e:
    logging.error(f"Could not connect to MongoDB: {e}")
    db = None # Set db to None if connection fails

# Configure Google Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Or 'gemini-pro'
    logging.info("Google Gemini API configured.")
except Exception as e:
    logging.error(f"Could not configure Google Gemini API: {e}")
    gemini_model = None

# Configure Google Cloud Vision API
vision_client = None
try:
    if os.path.exists(VISION_API_KEY_PATH):
        credentials = service_account.Credentials.from_service_account_file(VISION_API_KEY_PATH)
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        logging.info("Google Cloud Vision API configured.")
    else:
        logging.warning(f"Vision API key file not found at {VISION_API_KEY_PATH}. OCR functionality may be limited.")
except Exception as e:
    logging.error(f"Could not configure Google Cloud Vision API: {e}")
    vision_client = None

# Load ML Models (Classifier for Tax Regime, Regressor for Tax Liability)
tax_regime_classifier_model = None
tax_regressor_model = None
try:
    # Ensure these paths are correct relative to where app1.py is run
    classifier_path = 'tax_regime_classifier_model.pkl'
    regressor_path = 'final_tax_regressor_model.pkl'

    if os.path.exists(classifier_path):
        tax_regime_classifier_model = joblib.load(classifier_path)
        logging.info(f"Tax Regime Classifier model loaded from {classifier_path}.")
    else:
        logging.warning(f"Tax Regime Classifier model not found at {classifier_path}. ML predictions for regime will be disabled.")

    if os.path.exists(regressor_path):
        tax_regressor_model = joblib.load(regressor_path)
        logging.info(f"Tax Regressor model loaded from {regressor_path}.")
    else:
        logging.warning(f"Tax Regressor model not found at {regressor_path}. ML predictions for tax liability will be disabled.")

except Exception as e:
    logging.error(f"Error loading ML models: {e}. Ensure 'models/' directory exists and models are trained.")

# --- Helper Functions ---
def get_user_id():
    """Retrieves user ID from JWT token."""
    try:
        return get_jwt_identity()
    except Exception as e:
        logging.warning(f"Could not get JWT identity: {e}")
        return None

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

def ocr_document(file_bytes):
    """Performs OCR on the document using Google Cloud Vision API."""
    if not vision_client:
        logging.error("Google Cloud Vision client not initialized.")
        return {"error": "OCR service unavailable."}, None

    image = vision.Image(content=file_bytes)
    try:
        response = vision_client.document_text_detection(image=image)
        full_text = response.full_text_annotation.text
        return None, full_text
    except Exception as e:
        logging.error(f"Error during OCR with Vision API: {traceback.format_exc()}")
        return {"error": f"OCR failed: {e}"}, None

def safe_float(val):
    """Safely converts a value to float, defaulting to 0.0 on error or if 'null' string.
    Handles commas and currency symbols."""
    try:
        if val is None or (isinstance(val, str) and val.lower() in ['null', 'n/a', '']) :
            return 0.0
        if isinstance(val, str):
            # Remove commas, currency symbols, and any non-numeric characters except for digits and a single dot
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

def extract_fields_with_gemini(document_text, document_type_hint='Auto-Detect'):
    """
    Extracts key financial and personal fields from document text using Gemini.
    The prompt is designed to elicit specific, structured JSON output.
    """
    if not gemini_model:
        return {"error": "Gemini model not initialized."}, None

    # Refined prompt for more specific and structured extraction
    prompt_template = """
    You are an expert AI assistant for Indian income tax documents.
    Extract the following details from the provided document text.
    If a field is not present, use "null" for string values, 0 for numerical values, and "0000-01-01" for dates.
    Be precise and use the exact keys provided.
    For financial figures, extract the numerical value. For dates, use 'YYYY-MM-DD' format if available.
    
    Document Type Hint (provided by user, use if it helps but auto-detect if necessary): {document_type_hint}

    Extracted Fields (Strict JSON Format):
    {{
        "identified_type": "Detect the document type (e.g., 'Form 16', 'Bank Statement', 'Salary Slip', 'Form 26AS', 'Investment Proof', 'Home Loan Statement', 'Other Document').",
        "financial_year": "e.g., 2023-24",
        "assessment_year": "e.g., 2024-25",
        "name_of_employee": "Full name of employee/account holder",
        "pan_of_employee": "PAN number",
        "date_of_birth": "YYYY-MM-DD",
        "gender": "M/F/Other",
        "residential_status": "Resident/Non-Resident",
        "employer_name": "Employer's name",
        "employer_address": "Employer's address",
        "pan_of_deductor": "PAN of Deductor",
        "tan_of_deductor": "TAN of Deductor",
        "designation_of_employee": "Employee's designation",
        "period_from": "YYYY-MM-DD",
        "period_to": "YYYY-MM-DD",
        "gross_salary_total": 0.0,
        "salary_as_per_sec_17_1": 0.0,
        "value_of_perquisites_u_s_17_2": 0.0,
        "profits_in_lieu_of_salary_u_s_17_3": 0.0,
        "basic_salary": 0.0,
        "hra_received": 0.0,
        "conveyance_allowance": 0.0,
        "transport_allowance": 0.0,
        "overtime_pay": 0.0,
        "total_exempt_allowances": 0.0,
        "income_from_house_property": 0.0,
        "income_from_other_sources": 0.0,
        "capital_gains_long_term": 0.0,
        "capital_gains_short_term": 0.0,
        "gross_total_income_as_per_document": 0.0,
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
        "total_deductions_chapter_via": 0.0,
        "aggregate_of_deductions_from_salary": 0.0,
        "epf_contribution": 0.0,
        "esi_contribution": 0.0,
        "total_tds": 0.0,
        "total_tds_deducted_summary": 0.0,
        "total_tds_deposited_summary": 0.0,
        "quarter_1_receipt_number": "null",
        "quarter_1_tds_deducted": 0.0,
        "quarter_1_tds_deposited": 0.0,
        "advance_tax": 0.0,
        "self_assessment_tax": 0.0,
        "taxable_income_as_per_document": 0.0,
        "tax_payable_as_per_document": 0.0,
        "refund_status_as_per_document": "null",
        "tax_regime_chosen": "null",
        "net_amount_payable": 0.0,
        "days_present": "null",
        "overtime_hours": "null",
        "account_holder_name": "null",
        "account_number": "null",
        "ifsc_code": "null",
        "bank_name": "null",
        "branch_address": "null",
        "statement_start_date": "YYYY-MM-DD",
        "statement_end_date": "YYYY-MM-DD",
        "opening_balance": 0.0,
        "closing_balance": 0.0,
        "total_deposits": 0.0,
        "total_withdrawals": 0.0,
        "transaction_summary": []
    }}
    Document Text:
    {document_text}
    """
    full_prompt = prompt_template.format(document_type_hint=document_type_hint, document_text=document_text)

    try:
        # Assuming gemini_model is initialized globally
        response = gemini_model.generate_content(full_prompt)
        extracted_json_str = response.candidates[0].content.parts[0].text

        # Clean the string to ensure it's valid JSON
        if extracted_json_str.strip().startswith("```json"):
            extracted_json_str = extracted_json_str.replace("```json", "").replace("```", "").strip()
        
        extracted_data = json.loads(extracted_json_str)

        # Define expected types for all fields that Gemini outputs for validation and casting
        # This explicit mapping helps ensure data consistency, even if Gemini misses a field or provides wrong type
        field_definitions = {
            "identified_type": {"type": "STRING"}, "financial_year": {"type": "STRING"}, "assessment_year": {"type": "STRING"},
            "name_of_employee": {"type": "STRING"}, "pan_of_employee": {"type": "STRING"}, "date_of_birth": {"type": "DATE_STRING"},
            "gender": {"type": "STRING"}, "residential_status": {"type": "STRING"}, "employer_name": {"type": "STRING"},
            "employer_address": {"type": "STRING"}, "pan_of_deductor": {"type": "STRING"}, "tan_of_deductor": {"type": "STRING"},
            "designation_of_employee": {"type": "STRING"}, "period_from": {"type": "DATE_STRING"}, "period_to": {"type": "DATE_STRING"},
            "gross_salary_total": {"type": "NUMBER"}, "salary_as_per_sec_17_1": {"type": "NUMBER"}, "value_of_perquisites_u_s_17_2": {"type": "NUMBER"},
            "profits_in_lieu_of_salary_u_s_17_3": {"type": "NUMBER"}, "basic_salary": {"type": "NUMBER"}, "hra_received": {"type": "NUMBER"},
            "conveyance_allowance": {"type": "NUMBER"}, "transport_allowance": {"type": "NUMBER"}, "overtime_pay": {"type": "NUMBER"},
            "total_exempt_allowances": {"type": "NUMBER"}, "income_from_house_property": {"type": "NUMBER"}, "income_from_other_sources": {"type": "NUMBER"},
            "capital_gains_long_term": {"type": "NUMBER"}, "capital_gains_short_term": {"type": "NUMBER"},
            "gross_total_income_as_per_document": {"type": "NUMBER"}, "professional_tax": {"type": "NUMBER"},
            "interest_on_housing_loan_self_occupied": {"type": "NUMBER"}, "deduction_80c": {"type": "NUMBER"},
            "deduction_80c_epf": {"type": "NUMBER"}, "deduction_80c_insurance_premium": {"type": "NUMBER"}, "deduction_80ccc": {"type": "NUMBER"},
            "deduction_80ccd": {"type": "NUMBER"}, "deduction_80ccd1b": {"type": "NUMBER"}, "deduction_80d": {"type": "NUMBER"},
            "deduction_80g": {"type": "NUMBER"}, "deduction_80tta": {"type": "NUMBER"}, "deduction_80ttb": {"type": "NUMBER"},
            "deduction_80e": {"type": "NUMBER"}, "total_deductions_chapter_via": {"type": "NUMBER"}, "aggregate_of_deductions_from_salary": {"type": "NUMBER"},
            "epf_contribution": {"type": "NUMBER"}, "esi_contribution": {"type": "NUMBER"}, "total_tds": {"type": "NUMBER"},
            "total_tds_deducted_summary": {"type": "NUMBER"}, "total_tds_deposited_summary": {"type": "NUMBER"},
            "quarter_1_receipt_number": {"type": "STRING"}, "quarter_1_tds_deducted": {"type": "NUMBER"}, "quarter_1_tds_deposited": {"type": "NUMBER"},
            "advance_tax": {"type": "NUMBER"}, "self_assessment_tax": {"type": "NUMBER"}, "taxable_income_as_per_document": {"type": "NUMBER"},
            "tax_payable_as_per_document": {"type": "NUMBER"}, "refund_status_as_per_document": {"type": "STRING"},
            "tax_regime_chosen": {"type": "STRING"}, "net_amount_payable": {"type": "NUMBER"}, "days_present": {"type": "STRING"},
            "overtime_hours": {"type": "STRING"},
            "account_holder_name": {"type": "STRING"}, "account_number": {"type": "STRING"}, "ifsc_code": {"type": "STRING"},
            "bank_name": {"type": "STRING"}, "branch_address": {"type": "STRING"}, "statement_start_date": {"type": "DATE_STRING"},
            "statement_end_date": {"type": "DATE_STRING"}, "opening_balance": {"type": "NUMBER"}, "closing_balance": {"type": "NUMBER"},
            "total_deposits": {"type": "NUMBER"}, "total_withdrawals": {"type": "NUMBER"}, "transaction_summary": {"type": "ARRAY_OF_OBJECTS"}
        }

        # Ensure all keys from schema are present and correctly typed (even if null or 0 from Gemini)
        # This explicit casting is crucial for consistent data types in MongoDB and frontend.
        for key, prop_details in field_definitions.items():
            if key not in extracted_data or extracted_data[key] is None:
                if prop_details["type"] == "NUMBER":
                    extracted_data[key] = 0.0
                elif prop_details["type"] == "DATE_STRING":
                    extracted_data[key] = "0000-01-01"
                elif prop_details["type"] == "ARRAY_OF_OBJECTS":
                    extracted_data[key] = []
                else: # Default for STRING
                    extracted_data[key] = "null"
            else:
                # Type conversion/validation
                if prop_details["type"] == "NUMBER":
                    extracted_data[key] = safe_float(extracted_data[key])
                elif prop_details["type"] == "DATE_STRING":
                    # Validate and format date strings
                    date_val = safe_string(extracted_data[key])
                    try:
                        if date_val and date_val != "0000-01-01":
                            dt_obj = datetime.strptime(date_val.split('T')[0], '%Y-%m-%d')
                            extracted_data[key] = dt_obj.strftime('%Y-%m-%d')
                        else:
                            extracted_data[key] = "0000-01-01"
                    except ValueError:
                        extracted_data[key] = "0000-01-01"
                elif prop_details["type"] == "STRING":
                    extracted_data[key] = safe_string(extracted_data[key])
                elif prop_details["type"] == "ARRAY_OF_OBJECTS":
                    if key == "transaction_summary" and isinstance(extracted_data[key], list):
                        processed_transactions = []
                        for item in extracted_data[key]:
                            processed_item = {
                                "date": safe_string(item.get("date", "0000-01-01")),
                                "description": safe_string(item.get("description")),
                                "type": safe_string(item.get("type", "null")),
                                "amount": safe_float(item.get("amount"))
                            }
                            # Re-validate and format transaction date
                            try:
                                if processed_item['date'] and processed_item['date'] != "0000-01-01":
                                    dt_obj = datetime.strptime(processed_item['date'].split('T')[0], '%Y-%m-%d')
                                    processed_item['date'] = dt_obj.strftime('%Y-%m-%d')
                                else:
                                    processed_item['date'] = "0000-01-01"
                            except ValueError:
                                processed_item['date'] = "0000-01-01"
                            processed_transactions.append(processed_item)
                        extracted_data[key] = processed_transactions
                    else:
                        extracted_data[key] = [] # Fallback to empty list if not expected format
        return None, extracted_data
    except Exception as e:
        logging.error(f"Error during Gemini extraction or post-processing: {traceback.format_exc()}")
        return {"error": f"Gemini extraction failed or data parsing error: {e}"}, None


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
        "standard_deduction": 0.0, # Will be set based on FY later
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
    doc_priority = {
        "Form 16": 5,
        "Form 26AS": 4,
        "Salary Slip": 3,
        "Investment Proof": 2,
        "Home Loan Statement": 2,
        "Bank Statement": 1,
        "Other Document": 0,
        "Unknown": 0,
        "Unstructured Text": 0
    }

    # Sort documents by priority (higher priority first)
    sorted_extracted_data = sorted(extracted_data_list, key=lambda x: doc_priority.get(safe_string(x.get('identified_type')), 0), reverse=True)

    # Use a dictionary to track which field was last set by which document priority
    field_source_priority = {key: -1 for key in aggregated_data}

    # Iterate through sorted documents and aggregate data
    for data in sorted_extracted_data:
        doc_type = safe_string(data.get('identified_type'))
        current_priority = doc_priority.get(doc_type, 0)
        logging.debug(f"Aggregating from {doc_type} (Priority: {current_priority})")

        extracted_gross_salary_total = safe_float(data.get("gross_salary_total"))
        if extracted_gross_salary_total > 0 and current_priority >= field_source_priority.get("gross_salary_total", -1):
            aggregated_data["gross_salary_total"] = extracted_gross_salary_total
            field_source_priority["gross_salary_total"] = current_priority
            logging.debug(f"Set gross_salary_total to {aggregated_data['gross_salary_total']} from {doc_type}")

        personal_fields = ["name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status", "financial_year", "assessment_year"]
        for p_field in personal_fields:
            if safe_string(data.get(p_field)) != "null" and \
               (current_priority > field_source_priority.get(p_field, -1) or safe_string(aggregated_data.get(p_field)) == "null"):
                aggregated_data[p_field] = safe_string(data.get(p_field))
                field_source_priority[p_field] = current_priority


        for key, value in data.items():
            if key in personal_fields or key == "gross_salary_total":
                continue 
            if key == "transaction_summary":
                if isinstance(value, list):
                    aggregated_data[key].extend(value)
                continue
            if key == "identified_type":
                if current_priority > field_source_priority.get(key, -1):
                    aggregated_data[key] = safe_string(value)
                    field_source_priority[key] = current_priority
                continue
            
            if key in aggregated_data and isinstance(aggregated_data[key], (int, float)):
                if key in ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"]:
                    if doc_type == "Bank Statement":
                        if current_priority >= field_source_priority.get(key, -1):
                            aggregated_data[key] = safe_float(value)
                            field_source_priority[key] = current_priority
                    else:
                        aggregated_data[key] += safe_float(value)
                else:
                    aggregated_data[key] += safe_float(value)
            elif key in aggregated_data and isinstance(aggregated_data[key], str):
                if safe_string(value) != "null" and safe_string(value) != "" and \
                   (current_priority > field_source_priority.get(key, -1) or safe_string(aggregated_data[key]) == "null"):
                    aggregated_data[key] = safe_string(value)
                    field_source_priority[key] = current_priority
            elif key in aggregated_data and value is not None:
                if current_priority > field_source_priority.get(key, -1):
                    aggregated_data[key] = value
                    field_source_priority[key] = current_priority

    # --- Post-aggregation calculations and reconciliation ---
    
    if aggregated_data["gross_salary_total"] == 0.0:
        aggregated_data["gross_salary_total"] = (
            safe_float(aggregated_data["basic_salary"]) +
            safe_float(aggregated_data["hra_received"]) +
            safe_float(aggregated_data["conveyance_allowance"]) +
            safe_float(aggregated_data["transport_allowance"]) +
            safe_float(aggregated_data["overtime_pay"]) +
            safe_float(aggregated_data["value_of_perquisites_u_s_17_2"]) +
            safe_float(aggregated_data["profits_in_lieu_of_salary_u_s_17_3"])
        )

    aggregated_data["total_gross_income"] = (
        safe_float(aggregated_data["gross_salary_total"]) +
        safe_float(aggregated_data["income_from_house_property"]) +
        safe_float(aggregated_data["income_from_other_sources"]) + 
        safe_float(aggregated_data["capital_gains_long_term"]) +
        safe_float(aggregated_data["capital_gains_short_term"])
    )
    aggregated_data["total_gross_income"] = round(aggregated_data["total_gross_income"], 2)

    if safe_float(aggregated_data["epf_contribution"]) > 0:
        aggregated_data["deduction_80c"] = max(aggregated_data["deduction_80c"], safe_float(aggregated_data["epf_contribution"]))
    
    aggregated_data["total_deductions_chapter_via"] = (
        safe_float(aggregated_data["deduction_80c"]) +
        safe_float(aggregated_data["deduction_80ccc"]) +
        safe_float(aggregated_data["deduction_80ccd"]) +
        safe_float(aggregated_data["deduction_80ccd1b"]) +
        safe_float(aggregated_data["deduction_80d"]) +
        safe_float(aggregated_data["deduction_80g"]) +
        safe_float(aggregated_data["deduction_80tta"]) +
        safe_float(aggregated_data["deduction_80ttb"]) +
        safe_float(aggregated_data["deduction_80e"])
    )
    aggregated_data["total_deductions_chapter_via"] = round(aggregated_data["total_deductions_chapter_via"], 2)

    aggregated_data["total_gross_salary"] = aggregated_data["gross_salary_total"]
    
    if aggregated_data["total_exempt_allowances"] == 0.0:
        aggregated_data["total_exempt_allowances"] = (
            safe_float(aggregated_data.get("conveyance_allowance")) +
            safe_float(aggregated_data.get("transport_allowance")) +
            safe_float(aggregated_data.get("hra_received")) 
        )
        logging.info(f"Derived total_exempt_allowances: {aggregated_data['total_exempt_allowances']}")

    # Standard deduction will be determined by FY in calculate_final_tax_summary
    # aggregated_data["standard_deduction"] = 50000.0 

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
        aggregated_data["Age"] = "N/A"

    aggregated_data["exempt_allowances"] = aggregated_data["total_exempt_allowances"]
    aggregated_data["interest_on_housing_loan_24b"] = aggregated_data["interest_on_housing_loan_self_occupied"]
    aggregated_data["deduction_80C"] = aggregated_data["deduction_80c"]
    aggregated_data["deduction_80CCD1B"] = aggregated_data["deduction_80ccd1b"]
    aggregated_data["deduction_80D"] = aggregated_data["deduction_80d"]
    aggregated_data["deduction_80G"] = aggregated_data["deduction_80g"]
    aggregated_data["deduction_80TTA"] = aggregated_data["deduction_80tta"]
    aggregated_data["deduction_80TTB"] = aggregated_data["deduction_80ttb"]
    aggregated_data["deduction_80E"] = aggregated_data["deduction_80e"]

    aggregated_data["total_deductions"] = (
        safe_float(aggregated_data["professional_tax"]) +
        safe_float(aggregated_data["interest_on_housing_loan_self_occupied"]) +
        safe_float(aggregated_data["total_deductions_chapter_via"])
    )
    # Standard deduction will be added during final tax calculation based on regime/FY
    aggregated_data["total_deductions"] = round(aggregated_data["total_deductions"], 2)


    for tx in aggregated_data['transaction_summary']:
        if 'date' in tx and safe_string(tx['date']) != "0000-01-01":
            try:
                tx['date_sortable'] = datetime.strptime(tx['date'], '%Y-%m-%d')
            except ValueError:
                tx['date_sortable'] = datetime.min
        else:
            tx['date_sortable'] = datetime.min

    aggregated_data['transaction_summary'] = sorted(aggregated_data['transaction_summary'], key=lambda x: x.get('date_sortable', datetime.min))
    for tx in aggregated_data['transaction_summary']:
        tx.pop('date_sortable', None)

    if aggregated_data["identified_type"] in ["null", "Unknown", None, "Other Document"]:
        if safe_string(aggregated_data.get('employer_name')) != "null" and \
           safe_float(aggregated_data.get('gross_salary_total')) > 0:
           aggregated_data["identified_type"] = "Salary Related Document"
        elif safe_string(aggregated_data.get('account_number')) != "null" and \
             (safe_float(aggregated_data.get('total_deposits')) > 0 or safe_float(aggregated_data.get('total_withdrawals')) > 0):
             aggregated_data["identified_type"] = "Bank Statement"
        elif safe_float(aggregated_data.get('basic_salary')) > 0 or \
             safe_float(aggregated_data.get('hra_received')) > 0 or \
             safe_float(aggregated_data.get('net_amount_payable')) > 0:
             aggregated_data["identified_type"] = "Salary Slip"

    if safe_string(aggregated_data.get("pan_of_employee")) == "null":
        aggregated_data["pan_of_employee"] = "UNKNOWNPAN"

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
        aggregated_data["financial_year"] = "UNKNOWNFY"
        
    logging.info(f"Final Aggregated Data after processing: {aggregated_data}")
    return aggregated_data

def calculate_final_tax_summary(aggregated_data):
    """
    Calculates the estimated tax payable and refund status based on aggregated financial data,
    considering the specified Indian income tax rules for FY 2023-24 and FY 2024-25.
    """
    
    # If the document type is a Bank Statement, skip tax calculation as it's not directly for tax
    if aggregated_data.get('identified_type') == 'Bank Statement' and aggregated_data.get('total_gross_income', 0.0) < 100.0:
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
    professional_tax = safe_float(aggregated_data.get("professional_tax", 0))
    interest_on_housing_loan = safe_float(aggregated_data.get("interest_on_housing_loan_self_occupied", 0))
    
    # Deductions from Chapter VI-A
    deduction_80c_claimed = safe_float(aggregated_data.get("deduction_80c", 0))
    deduction_80ccc_claimed = safe_float(aggregated_data.get("deduction_80ccc", 0))
    deduction_80ccd_claimed = safe_float(aggregated_data.get("deduction_80ccd", 0))
    deduction_80ccd1b_claimed = safe_float(aggregated_data.get("deduction_80ccd1b", 0))
    deduction_80d_claimed = safe_float(aggregated_data.get("deduction_80d", 0))
    deduction_80g_claimed = safe_float(aggregated_data.get("deduction_80g", 0))
    deduction_80tta_claimed = safe_float(aggregated_data.get("deduction_80tta", 0))
    deduction_80ttb_claimed = safe_float(aggregated_data.get("deduction_80ttb", 0))
    deduction_80e_claimed = safe_float(aggregated_data.get("deduction_80e", 0))


    # Sum all TDS and advance tax for comparison
    total_tds_credit = (
        safe_float(aggregated_data.get("total_tds", 0)) + 
        safe_float(aggregated_data.get("advance_tax", 0)) + 
        safe_float(aggregated_data.get("self_assessment_tax", 0))
    )

    tax_regime_chosen_by_user = safe_string(aggregated_data.get("tax_regime_chosen"))
    age = aggregated_data.get('Age', "N/A")
    financial_year = safe_string(aggregated_data.get("financial_year", "UNKNOWNFY"))
    
    # Determine Age Group
    age_group = "General"
    if age != "N/A":
        if age >= 60 and age < 80:
            age_group = "Senior Citizen"
        elif age >= 80:
            age_group = "Super Senior Citizen"

    # --- Define Tax Slabs, Standard Deductions, and Rebates based on Financial Year ---
    # Default to FY 2024-25 if FY is unknown or invalid for new calculations
    current_fy_rules = {}
    if financial_year == "2023-24":
        current_fy_rules = {
            "old_regime_slabs_general": [(250000, 0.0), (500000, 0.05), (1000000, 0.20), (float('inf'), 0.30)],
            "old_regime_slabs_senior": [(300000, 0.0), (500000, 0.05), (1000000, 0.20), (float('inf'), 0.30)],
            "old_regime_slabs_super_senior": [(500000, 0.0), (1000000, 0.20), (float('inf'), 0.30)],
            "new_regime_slabs": [(300000, 0.0), (600000, 0.05), (900000, 0.10), (1200000, 0.15), (1500000, 0.20), (float('inf'), 0.30)],
            "standard_deduction_old_regime": 50000.0,
            "standard_deduction_new_regime": 0.0, # Not applicable for FY 2023-24 new regime (for salaried)
            "rebate_87a_income_limit_old": 500000,
            "rebate_87a_amount_old": 12500,
            "rebate_87a_income_limit_new": 700000,
            "rebate_87a_amount_new": 25000 # Increased for new regime from FY 2023-24
        }
    else: # Default to FY 2024-25 (AY 2025-26) rules if financial year is not 2023-24 or is UNKNOWNFY
        current_fy_rules = {
            "old_regime_slabs_general": [(250000, 0.0), (500000, 0.05), (1000000, 0.20), (float('inf'), 0.30)],
            "old_regime_slabs_senior": [(300000, 0.0), (500000, 0.05), (1000000, 0.20), (float('inf'), 0.30)],
            "old_regime_slabs_super_senior": [(500000, 0.0), (1000000, 0.20), (float('inf'), 0.30)],
            "new_regime_slabs": [(300000, 0.0), (700000, 0.05), (1000000, 0.10), (1200000, 0.15), (1500000, 0.20), (float('inf'), 0.30)],
            "standard_deduction_old_regime": 75000.0, # Increased for FY 2024-25
            "standard_deduction_new_regime": 75000.0, # Applicable for FY 2024-25 new regime
            "rebate_87a_income_limit_old": 500000,
            "rebate_87a_amount_old": 12500,
            "rebate_87a_income_limit_new": 700000,
            "rebate_87a_amount_new": 25000
        }
        # Override financial_year if it was UNKNOWNFY, for clarity in output
        if financial_year == "UNKNOWNFY":
            financial_year = "2024-25 (Defaulted)"
            aggregated_data["financial_year"] = financial_year


    calculation_details = []
    calculation_details.append(f"Applying tax rules for Financial Year: {financial_year}")
    calculation_details.append(f"Assessee Age Group: {age_group}")

    # --- Common income computation across regimes (before deductions) ---
    # "Income Chargeable under Head Salaries" is generally gross salary minus exempt allowances like HRA (if claimed) and professional tax.
    # For computation, we take gross_salary_total as the starting point.
    
    # Gross Income Heads
    total_income_from_salary = safe_float(aggregated_data.get("gross_salary_total", 0)) # Includes 17(1), 17(2), 17(3)
    income_from_house_property = safe_float(aggregated_data.get("income_from_house_property", 0))
    income_from_other_sources = safe_float(aggregated_data.get("income_from_other_sources", 0))
    capital_gains_long_term = safe_float(aggregated_data.get("capital_gains_long_term", 0))
    capital_gains_short_term = safe_float(aggregated_data.get("capital_gains_short_term", 0))

    # Calculate Gross Total Income (GTI)
    gross_total_income_for_calc = (
        total_income_from_salary +
        income_from_house_property +
        income_from_other_sources +
        capital_gains_long_term +
        capital_gains_short_term
    )
    gross_total_income_for_calc = round(gross_total_income_for_calc, 2)
    calculation_details.append(f"\n1. Gross Total Income (Total of all income heads): ₹{gross_total_income_for_calc:,.2f}")

    # --- Old Tax Regime Calculation ---
    standard_deduction_old = current_fy_rules["standard_deduction_old_regime"]
    
    # Cap deductions for Old Regime
    deduction_80c_effective = min(deduction_80c_claimed, 150000.0)
    # Simplified 80D limit for self/family and parents
    deduction_80d_effective = min(deduction_80d_claimed, 25000.0) # Assuming non-senior citizen, non-parent
    if age_group in ["Senior Citizen", "Super Senior Citizen"] or (age_group == "General" and deduction_80d_claimed > 25000):
        deduction_80d_effective = min(deduction_80d_claimed, 50000.0) # Max for senior citizens

    interest_on_housing_loan_effective = min(interest_on_housing_loan, 200000.0)

    total_chapter_via_deductions_old_regime = (
        deduction_80c_effective +
        min(deduction_80ccc_claimed, 150000.0) + # 80CCC part of 80C limit (1.5L)
        min(deduction_80ccd_claimed, 150000.0) + # 80CCD part of 80C limit (1.5L)
        deduction_80ccd1b_claimed + # Additional 50k for NPS (outside 80C limit)
        deduction_80d_effective +
        deduction_80g_claimed + # Can be 50% or 100% depending on fund, simplified as claimed
        deduction_80tta_claimed + # Max 10k for interest on savings a/c
        deduction_80ttb_claimed + # Max 50k for senior citizen interest income
        deduction_80e_claimed # Full interest on education loan
    )
    # Ensure total 80C, 80CCC, 80CCD(1) is capped at 1.5L
    capped_80c_group_deduction = min(deduction_80c_effective + min(deduction_80ccc_claimed,150000.0) + min(deduction_80ccd_claimed,150000.0), 150000.0)
    
    # Recalculate total Chapter VI-A based on caps and sum of components, including 80CCD(1B) separately
    total_chapter_via_deductions_old_regime = (
        capped_80c_group_deduction +
        min(deduction_80ccd1b_claimed, 50000.0) + # 80CCD(1B) has its own 50k limit
        deduction_80d_effective +
        deduction_80g_claimed +
        min(deduction_80tta_claimed, 10000.0) +
        min(deduction_80ttb_claimed, 50000.0) +
        deduction_80e_claimed
    )
    
    total_deductions_old_regime_for_calc = (
        standard_deduction_old + 
        professional_tax + 
        interest_on_housing_loan_effective + 
        total_chapter_via_deductions_old_regime
    )
    total_deductions_old_regime_for_calc = round(total_deductions_old_regime_for_calc, 2)

    taxable_income_old_regime = max(0, gross_total_income_for_calc - total_deductions_old_regime_for_calc)
    tax_before_cess_old_regime = 0

    calculation_details.append(f"\n2. Old Tax Regime Calculation:")
    calculation_details.append(f"   - Gross Total Income: ₹{gross_total_income_for_calc:,.2f}")
    calculation_details.append(f"   - Standard Deduction (Salaried): ₹{standard_deduction_old:,.2f}")
    calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
    calculation_details.append(f"   - Interest on Housing Loan (Sec 24b, capped at ₹2L): ₹{interest_on_housing_loan_effective:,.2f}")
    calculation_details.append(f"   - Deductions under Chapter VI-A (incl. 80C capped at ₹1.5L, 80D capped): ₹{total_chapter_via_deductions_old_regime:,.2f}")
    calculation_details.append(f"   - Total Deductions (Old Regime): ₹{total_deductions_old_regime_for_calc:,.2f}")
    calculation_details.append(f"   - Taxable Income (Old Regime): ₹{taxable_income_old_regime:,.2f}")

    # Apply Old Regime Tax Slabs
    tax_slabs_old_regime = []
    if age_group == "General":
        tax_slabs_old_regime = current_fy_rules["old_regime_slabs_general"]
    elif age_group == "Senior Citizen":
        tax_slabs_old_regime = current_fy_rules["old_regime_slabs_senior"]
    else: # Super Senior Citizen
        tax_slabs_old_regime = current_fy_rules["old_regime_slabs_super_senior"]

    current_income = taxable_income_old_regime
    prev_slab_limit = 0
    for slab_limit, rate in tax_slabs_old_regime:
        if current_income > prev_slab_limit:
            taxable_in_slab = min(current_income, slab_limit) - prev_slab_limit
            tax_before_cess_old_regime += taxable_in_slab * rate
        prev_slab_limit = slab_limit

    rebate_87a_old_regime = 0
    if taxable_income_old_regime <= current_fy_rules["rebate_87a_income_limit_old"]:
        rebate_87a_old_regime = min(tax_before_cess_old_regime, current_fy_rules["rebate_87a_amount_old"])
    
    tax_after_rebate_old_regime = tax_before_cess_old_regime - rebate_87a_old_regime
    health_cess_old_regime = tax_after_rebate_old_regime * 0.04
    total_tax_old_regime = round(tax_after_rebate_old_regime + health_cess_old_regime, 2)
    
    calculation_details.append(f"   - Tax before Rebate (Old Regime): ₹{tax_before_cess_old_regime:,.2f}")
    calculation_details.append(f"   - Rebate U/S 87A (Old Regime, if taxable income <= ₹{current_fy_rules['rebate_87a_income_limit_old']:,}: ₹{rebate_87a_old_regime:,.2f}")
    calculation_details.append(f"   - Health and Education Cess (4%): ₹{health_cess_old_regime:,.2f}")
    calculation_details.append(f"   - Total Tax Payable (Old Regime): ₹{total_tax_old_regime:,.2f}")


    # --- New Tax Regime Calculation ---
    standard_deduction_new = current_fy_rules["standard_deduction_new_regime"]

    # Only standard deduction and professional tax are generally allowed.
    # Employer's NPS contribution u/s 80CCD(2) is allowed.
    # For simplicity, we are considering it directly here if reported.
    # The new regime typically does not allow 80C, 80D, HRA exemption, etc.
    total_deductions_new_regime_for_calc = (
        standard_deduction_new + 
        professional_tax +
        min(deduction_80ccd_claimed, 7500000.0) # Capping 80CCD(2) at a very high number as actual limit is 10% of salary for private, or 14% for govt.
    )
    total_deductions_new_regime_for_calc = round(total_deductions_new_regime_for_calc, 2)

    taxable_income_new_regime = max(0, gross_total_income_for_calc - total_deductions_new_regime_for_calc) 
    tax_before_cess_new_regime = 0

    calculation_details.append(f"\n3. New Tax Regime Calculation:")
    calculation_details.append(f"   - Gross Total Income: ₹{gross_total_income_for_calc:,.2f}")
    calculation_details.append(f"   - Standard Deduction (Salaried): ₹{standard_deduction_new:,.2f}")
    calculation_details.append(f"   - Professional Tax: ₹{professional_tax:,.2f}")
    calculation_details.append(f"   - Total Deductions (New Regime): ₹{total_deductions_new_regime_for_calc:,.2f}")
    calculation_details.append(f"   - Taxable Income (New Regime): ₹{taxable_income_new_regime:,.2f}")

    # Apply New Regime Tax Slabs
    tax_slabs_new_regime = current_fy_rules["new_regime_slabs"]

    current_income = taxable_income_new_regime
    prev_slab_limit = 0
    for slab_limit, rate in tax_slabs_new_regime:
        if current_income > prev_slab_limit:
            taxable_in_slab = min(current_income, slab_limit) - prev_slab_limit
            tax_before_cess_new_regime += taxable_in_slab * rate
        prev_slab_limit = slab_limit

    rebate_87a_new_regime = 0
    if taxable_income_new_regime <= current_fy_rules["rebate_87a_income_limit_new"]:
        rebate_87a_new_regime = min(tax_before_cess_new_regime, current_fy_rules["rebate_87a_amount_new"])
    
    tax_after_rebate_new_regime = tax_before_cess_new_regime - rebate_87a_new_regime
    health_cess_new_regime = tax_after_rebate_new_regime * 0.04
    total_tax_new_regime = round(tax_after_rebate_new_regime + health_cess_new_regime, 2)

    calculation_details.append(f"   - Tax before Rebate (New Regime): ₹{tax_before_cess_new_regime:,.2f}")
    calculation_details.append(f"   - Rebate U/S 87A (New Regime, if taxable income <= ₹{current_fy_rules['rebate_87a_income_limit_new']:,}): ₹{rebate_87a_new_regime:,.2f}")
    calculation_details.append(f"   - Health and Education Cess (4%): ₹{health_cess_new_regime:,.2f}")
    calculation_details.append(f"   - Total Tax Payable (New Regime): ₹{total_tax_new_regime:,.2f}")


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
            computation_notes.append(f"Old Regime appears optimal for your income and deductions for FY {financial_year}. Tax under Old Regime: ₹{total_tax_old_regime:,.2f}, New Regime: ₹{total_tax_new_regime:,.2f}. You can choose to opt for this.")
        else:
            estimated_tax_payable = total_tax_new_regime
            computed_taxable_income = taxable_income_new_regime
            final_tax_regime_applied = "New Regime (Optimal)"
            computation_notes.append(f"New Regime appears optimal for your income and deductions for FY {financial_year}. Tax under New Regime: ₹{total_tax_new_regime:,.2f}, Old Regime: ₹{total_tax_old_regime:,.2f}. You can choose to opt for this.")

    estimated_tax_payable = round(estimated_tax_payable, 2)
    computed_taxable_income = round(computed_taxable_income, 2)

    # --- Calculate Refund/Tax Due ---
    refund_due_from_tax = 0.0
    tax_due_to_government = 0.0

    calculation_details.append(f"\n4. Total Tax Paid (TDS, Advance Tax, Self-Assessment Tax): ₹{total_tds_credit:,.2f}")
    if total_tds_credit > estimated_tax_payable:
        refund_due_from_tax = total_tds_credit - estimated_tax_payable
        calculation_details.append(f"5. Since Total Tax Paid > Estimated Tax Payable, Refund Due: ₹{refund_due_from_tax:,.2f}")
    elif total_tds_credit < estimated_tax_payable:
        tax_due_to_government = estimated_tax_payable - total_tds_credit
        calculation_details.append(f"5. Since Total Tax Paid < Estimated Tax Payable, Additional Tax Due: ₹{tax_due_to_government:,.2f}")
    else:
        calculation_details.append("5. No Refund or Additional Tax Due.")


    return {
        "calculated_gross_income": gross_total_income_for_calc,
        "calculated_total_deductions": total_deductions_old_regime_for_calc if final_tax_regime_applied.startswith("Old Regime") else total_deductions_new_regime_for_calc,
        "computed_taxable_income": computed_taxable_income,
        "estimated_tax_payable": estimated_tax_payable,
        "total_tds_credit": total_tds_credit,
        "predicted_refund_due": round(refund_due_from_tax, 2),
        "predicted_additional_due": round(tax_due_to_government, 2),
        "predicted_tax_regime": final_tax_regime_applied,
        "notes": computation_notes,
        "old_regime_tax_payable": total_tax_old_regime,
        "new_regime_tax_payable": total_tax_new_regime,
        "calculation_details": calculation_details,
        "regime_considered": final_tax_regime_applied
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
    ml_common_numerical_features = [
        'Age', 'Gross Annual Salary', 'HRA Received', 'Rent Paid', 'Basic Salary',
        'Standard Deduction Claimed', 'Professional Tax', 'Interest on Home Loan Deduction (Section 24(b))',
        'Section 80C Investments Claimed', 'Section 80D (Health Insurance Premiums) Claimed',
        'Section 80E (Education Loan Interest) Claimed', 'Other Deductions (80CCD, 80G, etc.) Claimed',
        'Total Exempt Allowances Claimed'
    ]
    ml_categorical_features = ['Residential Status', 'Gender']
    
    age_value = safe_float(financial_data.get('Age', 0)) if safe_string(financial_data.get('Age', "N/A")) != "N/A" else 0.0
    
    calculated_other_deductions = (
        safe_float(financial_data.get('deduction_80ccc', 0)) +
        safe_float(financial_data.get('deduction_80ccd', 0)) +
        safe_float(financial_data.get('deduction_80ccd1b', 0)) +
        safe_float(financial_data.get('deduction_80g', 0)) +
        safe_float(financial_data.get('deduction_80tta', 0)) +
        safe_float(financial_data.get('deduction_80ttb', 0))
    )
    calculated_other_deductions = round(calculated_other_deductions, 2)

    # Determine standard deduction based on financial year
    financial_year_for_ml = safe_string(financial_data.get("financial_year", "2024-25")).split('-')[0]
    std_deduction_for_ml = 50000.0 # Default for FY 2023-24
    if financial_year_for_ml == "2024": # Assuming 2024-25 FY
        std_deduction_for_ml = 75000.0

    classifier_input_data = {
        'Age': age_value,
        'Gross Annual Salary': safe_float(financial_data.get('total_gross_income', 0)),
        'HRA Received': safe_float(financial_data.get('hra_received', 0)),
        'Rent Paid': 0.0,
        'Basic Salary': safe_float(financial_data.get('basic_salary', 0)),
        'Standard Deduction Claimed': std_deduction_for_ml,
        'Professional Tax': safe_float(financial_data.get('professional_tax', 0)),
        'Interest on Home Loan Deduction (Section 24(b))': safe_float(financial_data.get('interest_on_housing_loan_24b', 0)),
        'Section 80C Investments Claimed': safe_float(financial_data.get('deduction_80C', 0)),
        'Section 80D (Health Insurance Premiums) Claimed': safe_float(financial_data.get('deduction_80D', 0)),
        'Section 80E (Education Loan Interest) Claimed': safe_float(financial_data.get('deduction_80E', 0)),
        'Other Deductions (80CCD, 80G, etc.) Claimed': calculated_other_deductions,
        'Total Exempt Allowances Claimed': safe_float(financial_data.get('total_exempt_allowances', 0)),
        'Residential Status': safe_string(financial_data.get('residential_status', 'Resident')),
        'Gender': safe_string(financial_data.get('gender', 'Unknown'))
    }
    
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
        
    regressor_input_data = {
        k: v for k, v in classifier_input_data.items() if k in ml_common_numerical_features
    }
    regressor_input_data['Tax Regime Chosen'] = predicted_tax_regime

    regressor_df = pd.DataFrame([regressor_input_data])
    
    predicted_tax_liability = 0.0
    try:
        ordered_regressor_features = ml_common_numerical_features + ['Tax Regime Chosen']
        regressor_df_processed = regressor_df[ordered_regressor_features]
        predicted_tax_liability = round(tax_regressor_model.predict(regressor_df_processed)[0], 2)
        logging.info(f"ML Predicted tax liability: {predicted_tax_liability}")
    except Exception as e:
        logging.error(f"Error predicting tax liability with ML model: {traceback.format_exc()}")
        predicted_tax_liability = 0.0

    total_tds_credit = safe_float(financial_data.get("total_tds", 0)) + safe_float(financial_data.get("advance_tax", 0)) + safe_float(financial_data.get("self_assessment_tax", 0))

    predicted_refund_due = 0.0
    predicted_additional_due = 0.0

    if total_tds_credit > predicted_tax_liability:
        predicted_refund_due = total_tds_credit - predicted_tax_liability
    elif total_tds_credit < predicted_tax_liability:
        predicted_additional_due = predicted_tax_liability - total_tds_credit
        
    return convert_numpy_types({
        "predicted_tax_regime": predicted_tax_regime,
        "predicted_tax_liability": predicted_tax_liability,
        "predicted_refund_due": round(predicted_refund_due, 2),
        "predicted_additional_due": round(predicted_additional_due, 2),
        "notes": "ML model predictions for optimal regime and tax liability."
    })

def generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary):
    """Generates tax-saving suggestions and regime analysis using Gemini API."""
    if gemini_model is None:
        logging.error("Gemini API (gemini_model) not initialized.")
        return ["AI suggestions unavailable."], "AI regime analysis unavailable."

    # Check if tax computation was not possible
    if "Tax computation not possible" in final_tax_computation_summary.get("notes", [""])[0]:
        return (
            ["Please upload your Form 16, salary slips, Form 26AS, and investment proofs (e.g., LIC, PPF, ELSS statements, home loan certificates, health insurance premium receipts) for a comprehensive tax analysis and personalized tax-saving suggestions."],
            "Tax regime analysis requires complete income and deduction data."
        )

    financial_data_for_gemini = aggregated_financial_data.copy()

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
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        
        suggestions = []
        regime_analysis = ""

        if "Suggestions:" in text and "Regime Analysis:" in text:
            parts = text.split("Regime Analysis:")
            suggestions_part = parts[0].replace("Suggestions:", "").strip()
            regime_analysis = parts[1].strip()

            suggestions = [s.strip() for s in suggestions_part.split('-') if s.strip()]
            if not suggestions:
                suggestions = [suggestions_part]
        else:
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
    """
    aggregated_data = tax_record_data.get('aggregated_financial_data', {})
    final_computation = tax_record_data.get('final_tax_computation_summary', {})

    itr_type = "ITR-1 (SAHAJ - DUMMY)"
    if safe_float(aggregated_data.get('capital_gains_long_term', 0)) > 0 or \
       safe_float(aggregated_data.get('capital_gains_short_term', 0)) > 0 or \
       safe_float(aggregated_data.get('income_from_house_property', 0)) < 0:
        itr_type = "ITR-2 (DUMMY)"
    
    name = aggregated_data.get('name_of_employee', 'N/A')
    pan = aggregated_data.get('pan_of_employee', 'N/A')
    financial_year = aggregated_data.get('financial_year', 'N/A')
    assessment_year = aggregated_data.get('assessment_year', 'N/A')
    total_income = final_computation.get('computed_taxable_income', 'N/A')
    tax_payable = final_computation.get('estimated_tax_payable', 'N/A')
    refund_due = final_computation.get('predicted_refund_due', 0.0)
    tax_due = final_computation.get('predicted_additional_due', 0.0)
    regime_considered = final_computation.get('predicted_tax_regime', 'N/A')

    bank_details_for_pdf = ""
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

    core_pdf_content_lines = [
        f"%PDF-1.4",
        f"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj",
        f"2 0 obj <</Type /Pages /Count 1 /Kids [3 0 R]>> endobj",
        f"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj",
        f"4 0 obj <</Length 700>> stream",
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
    
    if bank_details_for_pdf:
        core_pdf_content_lines.append(bank_details_for_pdf)
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
    
    core_pdf_content = "\n".join(core_pdf_content_lines) + "\n"
    core_pdf_bytes = core_pdf_content.encode('latin-1', errors='replace')

    startxref_position = len(core_pdf_bytes)

    full_pdf_content = core_pdf_content + f"startxref\n{startxref_position}\n%%EOF"
    
    dummy_pdf_content_bytes = full_pdf_content.encode('latin-1', errors='replace')

    return io.BytesIO(dummy_pdf_content_bytes), itr_type


# --- API Routes ---

@app.route('/')
def home():
    """Serves the main landing page, typically index.html."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serves static files from the root directory."""
    return send_from_directory('.', path)

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

        if users_collection.find_one({"email": email}):
            logging.warning(f"Registration failed: Email '{email}' already exists.")
            return jsonify({"message": "Email already exists"}), 409
        if users_collection.find_one({"username": username}):
            logging.warning(f"Registration failed: Username '{username}' already exists.")
            return jsonify({"message": "Username already exists"}), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        new_user_data = {
            "username": username,
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "full_name": data.get('fullName', ''),
            "pan": data.get('pan', ''),
            "aadhaar": data.get('aadhaar', ''),
            "address": data.get('address', ''),
            "phone": data.get('phone', ''),
            "created_at": datetime.utcnow()
        }
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

        user = users_collection.find_one({"username": username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
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
        current_user_id = get_jwt_identity()
        user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})
        if not user:
            logging.warning(f"Profile fetch failed: User {current_user_id} not found in DB.")
            return jsonify({"message": "User not found"}), 404

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
        current_user_id = get_jwt_identity()
        data = request.get_json()

        updatable_fields = ['full_name', 'pan', 'aadhaar', 'address', 'phone', 'email']
        update_data = {k: data[k] for k in updatable_fields if k in data}

        if not update_data:
            logging.warning(f"Profile update request from user {current_user_id} with no fields to update.")
            return jsonify({"message": "No fields to update provided."}), 400
        
        if 'username' in data:
            logging.warning(f"Attempted to update username for {current_user_id} via profile endpoint. Ignored.")

        if 'email' in update_data:
            existing_user_with_email = users_collection.find_one({"email": update_data['email']})
            if existing_user_with_email and str(existing_user_with_email['_id']) != current_user_id:
                logging.warning(f"Email update failed for user {current_user_id}: Email '{update_data['email']}' already in use.")
                return jsonify({"message": "Email already in use by another account."}), 409

        result = users_collection.update_one(
            {"_id": ObjectId(current_user_id)},
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
    current_user_id = get_jwt_identity()

    if 'documents' not in request.files:
        logging.warning(f"Process documents request from user {current_user_id} with no 'documents' part.")
        return jsonify({"message": "No 'documents' part in the request"}), 400

    files = request.files.getlist('documents')
    if not files:
        logging.warning(f"Process documents request from user {current_user_id} with no selected files.")
        return jsonify({"message": "No selected file"}), 400

    extracted_data_from_current_upload = []
    document_processing_summary_current_upload = []

    document_type_hint = request.form.get('document_type', 'Auto-Detect') 
    logging.info(f"Received document type hint from frontend: {document_type_hint}")

    for file in files:
        if file.filename == '':
            document_processing_summary_current_upload.append({"filename": "N/A", "status": "skipped", "message": "No selected file"})
            continue
        
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file_content_bytes = file.read()
            file.seek(0)

            with open(file_path, 'wb') as f:
                f.write(file_content_bytes)
            logging.info(f"File '{filename}' saved temporarily to {file_path} for user {current_user_id}.")

            mime_type = file.mimetype or 'application/octet-stream'

            document_text_content = ""
            if "image" in mime_type or "pdf" in mime_type:
                error_ocr, ocr_text = ocr_document(file_content_bytes)
                if error_ocr:
                    document_processing_summary_current_upload.append({
                        "filename": filename, "status": "failed", "message": f"OCR failed: {error_ocr['error']}",
                        "identified_type": "OCR Failed", "stored_path": f"/uploads/{unique_filename}"
                    })
                    continue
                document_text_content = ocr_text
            elif "text" in mime_type or "json" in mime_type:
                document_text_content = file_content_bytes.decode('utf-8')
            else:
                document_processing_summary_current_upload.append({
                    "filename": filename, "status": "skipped", "identified_type": "Unsupported",
                    "message": f"Unsupported file type: {mime_type}", "stored_path": f"/uploads/{unique_filename}"
                })
                continue
            
            error_gemini, extracted_data = extract_fields_with_gemini(document_text_content, document_type_hint)
            if error_gemini:
                document_processing_summary_current_upload.append({
                    "filename": filename, "status": "failed", "message": f"AI processing error: {error_gemini['error']}",
                    "identified_type": "AI Processing Failed", "stored_path": f"/uploads/{unique_filename}"
                })
                continue
            
            extracted_data['stored_document_path'] = f"/uploads/{unique_filename}"
            extracted_data_from_current_upload.append(extracted_data)

            document_processing_summary_current_upload.append({
                "filename": filename, "status": "success", "identified_type": extracted_data.get('identified_type', 'Unknown'),
                "message": "Processed successfully.", "extracted_fields": extracted_data,
                "stored_path": f"/uploads/{unique_filename}" 
            })
        except Exception as e:
            logging.error(f"General error processing file '{filename}': {traceback.format_exc()}")
            document_processing_summary_current_upload.append({
                "filename": filename, "status": "error",
                "message": f"An unexpected error occurred during file processing: {str(e)}",
                "stored_path": f"/uploads/{unique_filename}"
            })
            continue

    if not extracted_data_from_current_upload:
        logging.warning(f"No valid data extracted from any file for user {current_user_id}.")
        return jsonify({"message": "No valid data extracted from any file.", "document_processing_summary": document_processing_summary_current_upload}), 400

    pan_of_employee = "UNKNOWNPAN"
    financial_year = "UNKNOWNFY"

    for data in extracted_data_from_current_upload:
        if safe_string(data.get("pan_of_employee")) != "null" and safe_string(data.get("pan_of_employee")) != "UNKNOWNPAN":
            pan_of_employee = safe_string(data["pan_of_employee"])
        if safe_string(data.get("financial_year")) != "null" and safe_string(data.get("financial_year")) != "UNKNOWNFY":
            financial_year = safe_string(data["financial_year"])
        if pan_of_employee != "UNKNOWNPAN" and financial_year != "UNKNOWNFY":
            break
    
    if pan_of_employee == "UNKNOWNPAN":
        user_profile = users_collection.find_one({"_id": ObjectId(current_user_id)}, {"pan": 1})
        if user_profile and safe_string(user_profile.get("pan")) != "null":
            pan_of_employee = safe_string(user_profile["pan"])
            logging.info(f"Using PAN from user profile: {pan_of_employee}")
        else:
            logging.warning(f"PAN could not be determined for user {current_user_id} from documents or profile. Using default: {pan_of_employee}")

    if financial_year == "UNKNOWNFY":
        for data in extracted_data_from_current_upload:
            if safe_string(data.get("assessment_year")) != "null":
                try:
                    ay_parts = safe_string(data["assessment_year"]).split('-')
                    if len(ay_parts) == 2 and ay_parts[0].isdigit() and ay_parts[1].isdigit():
                        start_year = int(ay_parts[0]) -1
                        fy = f"{start_year}-{str(int(ay_parts[0]))[-2:]}"
                        if fy != "UNKNOWNFY":
                            financial_year = fy
                            break
                except Exception:
                    pass
        if financial_year == "UNKNOWNFY":
            logging.warning(f"Financial Year could not be determined for user {current_user_id}. Using default: {financial_year}")


    existing_tax_record = tax_records_collection.find_one({
        "user_id": current_user_id,
        "aggregated_financial_data.pan_of_employee": pan_of_employee,
        "aggregated_financial_data.financial_year": financial_year
    })

    if existing_tax_record:
        logging.info(f"Existing tax record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Merging data.")
        all_extracted_data_for_fy = existing_tax_record.get('extracted_documents_data', []) + extracted_data_from_current_upload
        all_document_processing_summary_for_fy = existing_tax_record.get('document_processing_summary', []) + document_processing_summary_current_upload

        updated_aggregated_financial_data = _aggregate_financial_data(all_extracted_data_for_fy)
        updated_final_tax_computation_summary = calculate_final_tax_summary(updated_aggregated_financial_data)

        tax_records_collection.update_one(
            {"_id": existing_tax_record["_id"]},
            {"$set": {
                "extracted_documents_data": all_extracted_data_for_fy,
                "document_processing_summary": all_document_processing_summary_for_fy,
                "aggregated_financial_data": updated_aggregated_financial_data,
                "final_tax_computation_summary": updated_final_tax_computation_summary,
                "timestamp": datetime.utcnow(),
                "suggestions_from_gemini": [],
                "gemini_regime_analysis": "null",
                "ml_prediction_summary": {},
            }}
        )
        record_id = existing_tax_record["_id"]
        logging.info(f"Tax record {record_id} updated successfully with new documents for user {current_user_id}.")

    else:
        logging.info(f"No existing record found for user {current_user_id}, PAN {pan_of_employee}, FY {financial_year}. Creating new record.")
        new_aggregated_financial_data = _aggregate_financial_data(extracted_data_from_current_upload)
        new_final_tax_computation_summary = calculate_final_tax_summary(new_aggregated_financial_data)

        tax_record_to_save = {
            "user_id": current_user_id, 
            "pan_of_employee": pan_of_employee,
            "financial_year": financial_year,
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


    response_data = {
        "status": "success",
        "message": "Documents processed and financial data aggregated and tax computed successfully",
        "record_id": str(record_id), 
        "document_processing_summary": document_processing_summary_current_upload,
        "aggregated_financial_data": convert_numpy_types(updated_aggregated_financial_data),
        "final_tax_computation_summary": convert_numpy_types(updated_final_tax_computation_summary),
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
        tax_record = tax_records_collection.find_one({"_id": ObjectId(record_id), "user_id": current_user_id})
        if not tax_record:
            logging.warning(f"Suggestions failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
            return jsonify({"message": "Tax record not found or unauthorized."}), 404
        
        aggregated_financial_data = tax_record.get('aggregated_financial_data', {})
        final_tax_computation_summary = tax_record.get('final_tax_computation_summary', {})

        suggestions, regime_analysis = generate_gemini_suggestions(aggregated_financial_data, final_tax_computation_summary)
        ml_prediction_summary = generate_ml_prediction_summary(aggregated_financial_data)

        tax_records_collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": {
                "suggestions_from_gemini": suggestions,
                "gemini_regime_analysis": regime_analysis,
                "ml_prediction_summary": ml_prediction_summary,
                "analysis_timestamp": datetime.utcnow()
            }}
        )
        logging.info(f"AI/ML analysis generated and saved for record ID: {record_id}")

        return jsonify({
            "status": "success",
            "message": "AI suggestions and ML predictions generated successfully!",
            "suggestions_from_gemini": suggestions,
            "gemini_regime_analysis": regime_analysis,
            "ml_prediction_summary": ml_prediction_summary
        }), 200
    except Exception as e:
        logging.error(f"Error generating suggestions for user {current_user_id} (record {record_id}): {traceback.format_exc()}")
        ml_prediction_summary_fallback = generate_ml_prediction_summary(tax_record.get('aggregated_financial_data', {})) if 'tax_record' in locals() else {}
        return jsonify({
            "status": "error",
            "message": "An error occurred while generating suggestions.",
            "suggestions_from_gemini": ["An unexpected error occurred while getting AI suggestions."],
            "gemini_regime_analysis": "An error occurred.",
            "ml_prediction_summary": ml_prediction_summary_fallback
        }), 500

@app.route('/api/save_extracted_data', methods=['POST'])
@jwt_required()
def save_extracted_data():
    """
    Saves extracted and computed tax data to MongoDB.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        logging.warning(f"Save data request from user {current_user_id} with no data provided.")
        return jsonify({"message": "No data provided to save"}), 400
    try:
        input_pan = data.get('aggregated_financial_data', {}).get('pan_of_employee', 'UNKNOWNPAN_SAVE')
        input_fy = data.get('aggregated_financial_data', {}).get('financial_year', 'UNKNOWNFY_SAVE')

        existing_record = tax_records_collection.find_one({
            "user_id": current_user_id,
            "aggregated_financial_data.pan_of_employee": input_pan,
            "aggregated_financial_data.financial_year": input_fy
        })

        if existing_record:
            update_result = tax_records_collection.update_one(
                {"_id": existing_record["_id"]},
                {"$set": {
                    **data,
                    "user_id": current_user_id,
                    "timestamp": datetime.utcnow(),
                    "pan_of_employee": input_pan,
                    "financial_year": input_fy,
                }}
            )
            record_id = existing_record["_id"]
            logging.info(f"Existing record {record_id} updated via save_extracted_data for user {current_user_id}.")
            if update_result.modified_count == 0:
                return jsonify({"message": "Data already up to date, no changes made.", "record_id": str(record_id)}), 200
        else:
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

@app.route('/api/tax-records', methods=['GET'])
@jwt_required()
def get_tax_records():
    """
    Fetches all aggregated tax records for the logged-in user, grouped by Financial Year.
    Records are sorted by timestamp in descending order (most recent first).
    """
    current_user_id = get_jwt_identity()
    logging.info(f"Fetching tax records for user: {current_user_id}")
    try:
        records = list(tax_records_collection.find({"user_id": current_user_id})
                        .sort([("financial_year", -1), ("timestamp", -1)]))

        for record in records:
            record['_id'] = str(record['_id'])
            if 'user_id' in record:
                record['user_id'] = str(record['user_id'])
            record.pop('extracted_documents_data', None)
        logging.info(f"Found {len(records)} tax records for user {current_user_id}")
        return jsonify({"status": "success", "history": convert_numpy_types(records)}), 200
    except Exception as e:
        logging.error(f"Error fetching tax records for user {current_user_id}: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "Failed to retrieve history", "error": str(e)}), 500

@app.route('/api/tax-records/<record_id>', methods=['DELETE'])
@jwt_required()
def delete_tax_record(record_id):
    """
    Deletes a specific tax record for the logged-in user and its associated uploaded files.
    """
    current_user_id = get_jwt_identity()
    try:
        record_obj_id = ObjectId(record_id)
        
        # Find the record to get associated file paths before deleting it
        tax_record = tax_records_collection.find_one(
            {"_id": record_obj_id, "user_id": current_user_id},
            {"extracted_documents_data.stored_document_path": 1} # Only fetch the paths
        )

        if not tax_record:
            logging.warning(f"Delete failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
            return jsonify({"message": "Tax record not found or unauthorized."}), 404

        # Delete associated files
        deleted_files_count = 0
        if 'extracted_documents_data' in tax_record and isinstance(tax_record['extracted_documents_data'], list):
            for doc_data in tax_record['extracted_documents_data']:
                file_path_relative = doc_data.get('stored_document_path')
                if file_path_relative and file_path_relative.startswith('/uploads/'):
                    absolute_file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(file_path_relative))
                    if os.path.exists(absolute_file_path):
                        try:
                            os.remove(absolute_file_path)
                            deleted_files_count += 1
                            logging.info(f"Deleted associated file: {absolute_file_path}")
                        except OSError as e:
                            logging.error(f"Error deleting file {absolute_file_path}: {e}")
                    else:
                        logging.warning(f"Associated file not found, skipping: {absolute_file_path}")

        # Delete the record from MongoDB
        delete_result = tax_records_collection.delete_one({"_id": record_obj_id, "user_id": current_user_id})

        if delete_result.deleted_count == 1:
            logging.info(f"Tax record {record_id} and {deleted_files_count} associated files deleted successfully for user {current_user_id}.")
            return jsonify({"message": "Tax record deleted successfully!", "deleted_files_count": deleted_files_count}), 200
        else:
            logging.error(f"Failed to delete tax record {record_id} for user {current_user_id}.")
            return jsonify({"message": "Failed to delete tax record."}), 500

    except Exception as e:
        logging.error(f"Error deleting tax record {record_id} for user {current_user_id}: {traceback.format_exc()}")
        return jsonify({"message": "An error occurred while deleting the tax record.", "error": str(e)}), 500

@app.route('/api/generate-itr/<record_id>', methods=['GET'])
@jwt_required()
def generate_itr_form_route(record_id):
    """
    Generates a mock ITR form PDF for a given tax record using the dummy PDF generation logic.
    """
    current_user_id = get_jwt_identity()
    try:
        record_obj_id = ObjectId(record_id)
        tax_record = tax_records_collection.find_one({"_id": record_obj_id, "user_id": current_user_id})

        if not tax_record:
            logging.warning(f"ITR generation failed: Record {record_id} not found for user {current_user_id} or unauthorized.")
            return jsonify({"message": "Tax record not found or unauthorized."}), 404

        pdf_buffer, itr_type = generate_itr_pdf(tax_record)
        
        pdf_buffer.seek(0)

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
    if db is None:
        logging.error("MongoDB connection failed at startup. Exiting.")
        exit(1)
    
    logging.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)