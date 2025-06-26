// import React, { useState } from 'react';
// import axios from 'axios';
// import Cookies from 'js-cookie';

// const TaxUploader = () => {
//     const [selectedFiles, setSelectedFiles] = useState([]);
//     const [loading, setLoading] = useState(false);
//     const [message, setMessage] = useState('');
//     const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
//     const [uploadResult, setUploadResult] = useState(null); // Stores initial processing result (record_id, doc summary, aggregated_data, computation_summary)
//     const [suggestionsResult, setSuggestionsResult] = useState(null); // Stores suggestions and ML predictions
//     const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);
//     const [isGeneratingITR, setIsGeneratingITR] = useState(false);
//     const [documentTypeHint, setDocumentTypeHint] = useState('Auto-Detect'); // Default value

//     // List of common document types for the dropdown
//     const documentTypes = [
//         'Auto-Detect', // Default option, AI attempts to detect
//         'Form 16',
//         'Bank Statement',
//         'Form 26AS',
//         'Salary Slip',
//         'Investment Proof',
//         'Home Loan Statement',
//         'Other Document',
//     ];

//     // Helper function to safely format currency values
//     const formatCurrency = (value) => {
//         if (value === null || value === undefined || isNaN(parseFloat(value))) {
//             return 'N/A';
//         }
//         return parseFloat(value).toLocaleString('en-IN', {
//             style: 'currency',
//             currency: 'INR',
//             minimumFractionDigits: 2,
//             maximumFractionDigits: 2,
//         });
//     };

//     const handleFileChange = (event) => {
//         setSelectedFiles(Array.from(event.target.files));
//         // Clear all previous results/messages on new file selection
//         setMessage('');
//         setMessageType('');
//         setUploadResult(null);
//         setSuggestionsResult(null);
//         setIsGeneratingSuggestions(false);
//         setIsGeneratingITR(false);
//     };

//     const handleDocumentTypeChange = (event) => {
//         setDocumentTypeHint(event.target.value);
//     };

//     const handleSubmit = async (event) => {
//         event.preventDefault();
//         if (selectedFiles.length === 0) {
//             setMessage('Please select at least one file.');
//             setMessageType('error');
//             return;
//         }

//         setLoading(true);
//         setMessage('Uploading and processing documents with AI...');
//         setMessageType('info');
//         setUploadResult(null); // Clear previous results
//         setSuggestionsResult(null);
//         setIsGeneratingSuggestions(false);
//         setIsGeneratingITR(false);

//         const formData = new FormData();
//         selectedFiles.forEach(file => {
//             formData.append('documents', file);
//         });
//         formData.append('document_type', documentTypeHint);

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const config = {
//                 headers: {
//                     'Content-Type': 'multipart/form-data',
//                 }
//             };
//             if (jwt_token) {
//                 config.headers['Authorization'] = `Bearer ${jwt_token}`;
//             }

//             const response = await axios.post('http://127.0.0.1:5000/api/process_documents', formData, config);

//             if (response.data.status === 'success' || response.data.status === 'partial_success') {
//                 setMessage(response.data.message || 'Documents processed and data saved successfully!');
//                 setMessageType('success');
//                 setUploadResult(response.data); // Store the entire response for display
//                 setSelectedFiles([]);
//                 document.getElementById('file-input').value = '';
//             } else {
//                 setMessage(response.data.message || 'An unknown error occurred during processing.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Upload error:', error);
//             if (error.response) {
//                 if (error.response.status === 401) {
//                     setMessage('Authentication required. Please log in.');
//                     Cookies.remove('jwt_token');
//                     window.location.href = '/login';
//                 } else if (error.response.data && error.response.data.message) {
//                     setMessage(`Error: ${error.response.data.message}`);
//                 } else {
//                     setMessage(`Server responded with status ${error.response.status}`);
//                 }
//             } else {
//                 setMessage('An error occurred while uploading or processing documents. Check network connection and backend server.');
//             }
//             setMessageType('error');
//         } finally {
//             setLoading(false);
//         }
//     };

//     const handleGetSuggestions = async () => {
//         if (!uploadResult || !uploadResult.record_id) {
//             setMessage('Please upload and process documents first to get suggestions.');
//             setMessageType('error');
//             return;
//         }

//         setIsGeneratingSuggestions(true);
//         setMessage('Generating AI-powered suggestions and ML predictions...');
//         setMessageType('info');
//         setSuggestionsResult(null); // Clear previous suggestions

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const config = {
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'Authorization': `Bearer ${jwt_token}`,
//                 }
//             };

//             const payload = {
//                 record_id: uploadResult.record_id // Send the record_id to fetch data for suggestions
//             };

//             const response = await axios.post('http://127.0.0.1:5000/api/get_suggestions', payload, config);

//             if (response.data.status === 'success') {
//                 setMessage(response.data.message || 'AI suggestions and ML predictions generated.');
//                 setMessageType('success');
//                 setSuggestionsResult(response.data); // Store the full suggestions result
//             } else {
//                 setMessage(response.data.message || 'Failed to get suggestions.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Suggestions error:', error);
//             if (error.response) {
//                 if (error.response.status === 401) {
//                     setMessage('Authentication required. Please log in.');
//                     Cookies.remove('jwt_token');
//                     window.location.href = '/login';
//                 } else if (error.response.data && error.response.data.message) {
//                     setMessage(`Error: ${error.response.data.message}`);
//                 } else {
//                     setMessage(`Server responded with status ${error.response.status}`);
//                 }
//             } else {
//                 setMessage('Error fetching AI suggestions. Check backend connection and API keys.');
//             }
//             setMessageType('error');
//         } finally {
//             setIsGeneratingSuggestions(false);
//         }
//     };

//     const handleGenerateITRForm = async () => {
//         if (!uploadResult || !uploadResult.record_id) {
//             setMessage('Please upload and process documents first to generate ITR form.');
//             setMessageType('error');
//             return;
//         }

//         setIsGeneratingITR(true);
//         setMessage('Generating ITR form...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const config = {
//                 headers: {
//                     'Authorization': `Bearer ${jwt_token}`,
//                 },
//                 responseType: 'blob', // Important for receiving a file
//             };
            
//             // Fetch the ITR form using the record_id obtained after saving
//             const response = await axios.get(`http://127.0.0.1:5000/api/generate-itr/${uploadResult.record_id}`, config);

//             if (response.status === 200) {
//                 const blob = new Blob([response.data], { type: 'application/pdf' });
//                 const downloadUrl = window.URL.createObjectURL(blob);
//                 const contentDisposition = response.headers['content-disposition'];
//                 let filename = `ITR_Form_${uploadResult.record_id}.pdf`; // Default filename

//                 if (contentDisposition) {
//                     const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
//                     if (filenameMatch && filenameMatch[1]) {
//                         filename = filenameMatch[1];
//                     }
//                 }
                
//                 const link = document.createElement('a');
//                 link.href = downloadUrl;
//                 link.setAttribute('download', filename);
//                 document.body.appendChild(link);
//                 link.click();
//                 link.remove();
//                 window.URL.revokeObjectURL(downloadUrl);

//                 setMessage('ITR form generated and downloaded successfully!');
//                 setMessageType('success');
//             } else {
//                 const errorData = await new Response(response.data).text(); // Read blob as text for error
//                 setMessage(`Failed to generate ITR form: ${errorData || response.statusText}`);
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('ITR generation error:', error);
//             if (axios.isAxiosError(error) && error.response && error.response.data) {
//                 const reader = new FileReader();
//                 reader.onload = () => {
//                     try {
//                         const errorJson = JSON.parse(reader.result);
//                         setMessage(`Error generating ITR form: ${errorJson.message || JSON.stringify(errorJson)}`);
//                     } catch (e) {
//                         setMessage(`Error generating ITR form: ${reader.result || error.response.statusText}`);
//                     }
//                 };
//                 reader.readAsText(error.response.data);
//             } else {
//                 setMessage('Network error or server unavailable during ITR form generation.');
//             }
//             setMessageType('error');
//         } finally {
//             setIsGeneratingITR(false);
//         }
//     };

//     // Helper function to render extracted fields dynamically
//     const renderExtractedFields = (fields) => {
//         if (!fields) return null;

//         const fieldOrder = [
//             // Personal & Employer Info
//             "name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status",
//             "employer_name", "employer_address", "pan_of_deductor", "tan_of_deductor", "designation_of_employee",
//             // Financial Years & Period
//             "financial_year", "assessment_year", "period_from", "period_to", "statement_start_date", "statement_end_date",
//             // Income
//             "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
//             "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
//             "total_exempt_allowances",
//             "income_from_house_property", "income_from_other_sources", "capital_gains_long_term", "capital_gains_short_term",
//             "gross_total_income_as_per_document",
//             // Deductions
//             "professional_tax", "interest_on_housing_loan_self_occupied",
//             "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
//             "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
//             "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
//             "epf_contribution", "esi_contribution",
//             // Tax Paid
//             "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
//             "quarter_1_receipt_number", "quarter_1_tds_deducted", "quarter_1_tds_deposited",
//             "advance_tax", "self_assessment_tax",
//             // Other Tax Info
//             "taxable_income_as_per_document", "tax_payable_as_per_document", "refund_status_as_per_document", "tax_regime_chosen",
//             "net_amount_payable", "days_present", "overtime_hours",
//             // Bank Statement Details
//             "account_holder_name", "account_number", "ifsc_code", "bank_name", "branch_address",
//             "opening_balance", "closing_balance", "total_deposits", "total_withdrawals"
//         ];
        
//         // Define display names for better readability
//         const displayNames = {
//             "name_of_employee": "Name of Employee",
//             "pan_of_employee": "PAN of Employee",
//             "date_of_birth": "Date of Birth",
//             "gender": "Gender",
//             "residential_status": "Residential Status",
//             "employer_name": "Employer Name",
//             "employer_address": "Employer Address",
//             "pan_of_deductor": "PAN of Deductor",
//             "tan_of_deductor": "TAN of Deductor",
//             "designation_of_employee": "Designation",
//             "financial_year": "Financial Year",
//             "assessment_year": "Assessment Year",
//             "period_from": "Period From",
//             "period_to": "Period To",
//             "statement_start_date": "Statement Start Date",
//             "statement_end_date": "Statement End Date",
//             "gross_salary_total": "Gross Salary Total",
//             "salary_as_per_sec_17_1": "Salary U/S 17(1)",
//             "value_of_perquisites_u_s_17_2": "Perquisites U/S 17(2)",
//             "profits_in_lieu_of_salary_u_s_17_3": "Profits in Lieu of Salary U/S 17(3)",
//             "basic_salary": "Basic Salary",
//             "hra_received": "HRA Received",
//             "conveyance_allowance": "Conveyance Allowance",
//             "transport_allowance": "Transport Allowance",
//             "overtime_pay": "Overtime Pay",
//             "total_exempt_allowances": "Total Exempt Allowances",
//             "income_from_house_property": "Income from House Property",
//             "income_from_other_sources": "Income from Other Sources",
//             "capital_gains_long_term": "Long Term Capital Gains",
//             "capital_gains_short_term": "Short Term Capital Gains",
//             "gross_total_income_as_per_document": "Gross Total Income (Doc)",
//             "professional_tax": "Professional Tax",
//             "interest_on_housing_loan_self_occupied": "Interest on Home Loan (Self Occupied)",
//             "deduction_80c": "Deduction 80C",
//             "deduction_80c_epf": "Deduction 80C (EPF)",
//             "deduction_80c_insurance_premium": "Deduction 80C (Insurance Premium)",
//             "deduction_80ccc": "Deduction 80CCC",
//             "deduction_80ccd": "Deduction 80CCD",
//             "deduction_80ccd1b": "Deduction 80CCD(1B)",
//             "deduction_80d": "Deduction 80D",
//             "deduction_80g": "Deduction 80G",
//             "deduction_80tta": "Deduction 80TTA",
//             "deduction_80ttb": "Deduction 80TTB",
//             "deduction_80e": "Deduction 80E",
//             "total_deductions_chapter_via": "Total Chapter VI-A Deductions",
//             "aggregate_of_deductions_from_salary": "Aggregate Deductions from Salary",
//             "epf_contribution": "EPF Contribution",
//             "esi_contribution": "ESI Contribution",
//             "total_tds": "Total TDS",
//             "total_tds_deducted_summary": "Total TDS Deducted (Summary)",
//             "total_tds_deposited_summary": "Total TDS Deposited (Summary)",
//             "quarter_1_receipt_number": "Q1 Receipt Number",
//             "quarter_1_tds_deducted": "Q1 TDS Deducted",
//             "quarter_1_tds_deposited": "Q1 TDS Deposited",
//             "advance_tax": "Advance Tax",
//             "self_assessment_tax": "Self-Assessment Tax",
//             "taxable_income_as_per_document": "Taxable Income (Doc)",
//             "tax_payable_as_per_document": "Tax Payable (Doc)",
//             "refund_status_as_per_document": "Refund Status (Doc)",
//             "tax_regime_chosen": "Tax Regime Chosen",
//             "net_amount_payable": "Net Amount Payable",
//             "days_present": "Days Present",
//             "overtime_hours": "Overtime Hours",
//             "account_holder_name": "Account Holder Name",
//             "account_number": "Account Number",
//             "ifsc_code": "IFSC Code",
//             "bank_name": "Bank Name",
//             "branch_address": "Branch Address",
//             "opening_balance": "Opening Balance",
//             "closing_balance": "Closing Balance",
//             "total_deposits": "Total Deposits",
//             "total_withdrawals": "Total Withdrawals"
//         };
        
//         return (
//             <ul style={{ listStyleType: 'none', padding: 0 }}>
//                 {fieldOrder.map(key => {
//                     let value = fields[key];
//                     // Skip if value is null, undefined, "null", or 0 for numbers (unless it's a critical zero like a balance)
//                     // We'll display 0.0 for key financial figures explicitly, but filter "null" strings
//                     if (value === null || value === undefined || (typeof value === 'string' && value.toLowerCase() === 'null')) {
//                         return null;
//                     }

//                     // For numbers, convert to currency if applicable and not 0, or just display 0 if it's a financial figure
//                     if (typeof value === 'number') {
//                         if (key.includes('balance') || key.includes('total_deposits') || key.includes('total_withdrawals') || 
//                             key.includes('tax') || key.includes('income') || key.includes('deduction') || key.includes('salary') ||
//                             key.includes('allowance') || key.includes('perquisites') || key.includes('epf') || key.includes('esi') ||
//                             key.includes('overtime_pay') || key.includes('net_amount_payable')) {
//                             // Display 0.0 for actual zero financial values, otherwise format currency
//                             value = formatCurrency(value);
//                         } else {
//                             // For other numeric fields, just display the number directly
//                             value = value.toString();
//                         }
//                     }

//                     // Special handling for transaction_summary if it's an array and not empty
//                     if (key === "transaction_summary" && Array.isArray(value) && value.length > 0) {
//                         return (
//                             <li key={key}>
//                                 <strong>{displayNames[key] || key}:</strong>
//                                 <pre className="extracted-fields-preview mt-2">
//                                     {JSON.stringify(value.map(tx => ({
//                                         date: tx.date !== "0000-01-01" ? tx.date : "N/A", // Format date
//                                         description: tx.description,
//                                         amount: formatCurrency(tx.amount)
//                                     })), null, 2)}
//                                 </pre>
//                             </li>
//                         );
//                     }
                    
//                     // Filter out empty arrays as well
//                     if (Array.isArray(value) && value.length === 0) {
//                         return null;
//                     }

//                     // Render other fields if their value is not "null" (string) or empty string
//                     if (typeof value === 'string' && value.trim() === '') {
//                         return null;
//                     }

//                     return (
//                         <li key={key}>
//                             <strong>{displayNames[key] || key}:</strong> {value}
//                         </li>
//                     );
//                 })}
//             </ul>
//         );
//     };


//     return (
//         <div className="tax-uploader-container section-box">
//             {/* Inlined CSS for styling the component */}
//             <style>{`
//                 /* General Body Styling */
//                 body {
//                     font-family: 'Inter', sans-serif;
//                     background-color: #f0f2f5;
//                     margin: 0;
//                     padding: 20px;
//                     color: #333;
//                     line-height: 1.6;
//                 }

//                 /* Section Box Styling */
//                 .section-box {
//                     background-color: #ffffff;
//                     padding: 25px;
//                     border-radius: 12px;
//                     box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
//                     margin-bottom: 25px;
//                     border: 1px solid #e0e0e0;
//                 }

//                 /* Tax Uploader Container */
//                 .tax-uploader-container {
//                     max-width: 900px;
//                     margin: 30px auto;
//                     padding: 30px;
//                     background-color: #fff;
//                     border-radius: 15px;
//                     box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
//                     border: 1px solid #d0d0d0;
//                 }

//                 .tax-uploader-title {
//                     text-align: center;
//                     color: #2c3e50;
//                     margin-bottom: 30px;
//                     font-size: 2.2em;
//                     font-weight: 700;
//                     letter-spacing: -0.5px;
//                 }

//                 /* Form Group */
//                 .tax-uploader-form-group {
//                     margin-bottom: 25px;
//                 }

//                 .tax-uploader-label {
//                     display: block;
//                     margin-bottom: 10px;
//                     font-weight: 600;
//                     color: #34495e;
//                     font-size: 1.1em;
//                 }

//                 .tax-uploader-file-input {
//                     display: block;
//                     width: 100%;
//                     padding: 12px;
//                     border: 1px solid #ced4da;
//                     border-radius: 8px;
//                     font-size: 1em;
//                     color: #495057;
//                     background-color: #f8f9fa;
//                     transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
//                 }

//                 .tax-uploader-file-input:focus {
//                     border-color: #80bdff;
//                     box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
//                     outline: none;
//                 }

//                 .selected-files-text {
//                     margin-top: 10px;
//                     font-size: 0.95em;
//                     color: #555;
//                     font-style: italic;
//                 }

//                 /* Buttons */
//                 .tax-uploader-button {
//                     display: block;
//                     width: 100%;
//                     padding: 14px 20px;
//                     background-color: #007bff;
//                     color: white;
//                     border: none;
//                     border-radius: 8px;
//                     font-size: 1.1em;
//                     font-weight: 600;
//                     cursor: pointer;
//                     transition: background-color 0.3s ease, transform 0.2s ease;
//                     box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
//                     margin-top: 20px;
//                 }

//                 .tax-uploader-button:hover {
//                     background-color: #0056b3;
//                     transform: translateY(-2px);
//                 }

//                 .tax-uploader-button:disabled {
//                     background-color: #a0c9f1;
//                     cursor: not-allowed;
//                     box-shadow: none;
//                     transform: none;
//                 }

//                 .action-buttons-container {
//                     display: flex;
//                     flex-wrap: wrap;
//                     gap: 15px;
//                     margin-top: 30px;
//                     justify-content: center;
//                 }

//                 .action-buttons-container .tax-uploader-button {
//                     flex: 1;
//                     min-width: 250px;
//                     margin: 0; /* Override default margin */
//                 }

//                 .get-suggestions-button {
//                     background-color: #28a745;
//                     box-shadow: 0 4px 10px rgba(40, 167, 69, 0.2);
//                 }

//                 .get-suggestions-button:hover {
//                     background-color: #218838;
//                 }

//                 .generate-itr-button {
//                     background-color: #6c757d;
//                     box-shadow: 0 4px 10px rgba(108, 117, 125, 0.2);
//                 }

//                 .generate-itr-button:hover {
//                     background-color: #5a6268;
//                 }

//                 /* Loading Spinner */
//                 .tax-uploader-loading {
//                     display: flex;
//                     align-items: center;
//                     justify-content: center;
//                     margin-top: 25px;
//                     font-size: 1.1em;
//                     color: #007bff;
//                     font-weight: 500;
//                 }

//                 .tax-uploader-spinner {
//                     border: 4px solid #f3f3f3;
//                     border-top: 4px solid #007bff;
//                     border-radius: 50%;
//                     width: 24px;
//                     height: 24px;
//                     animation: spin 1s linear infinite;
//                     margin-right: 10px;
//                 }

//                 @keyframes spin {
//                     0% { transform: rotate(0deg); }
//                     100% { transform: rotate(360deg); }
//                 }

//                 /* Messages */
//                 .tax-uploader-message {
//                     padding: 15px;
//                     margin-top: 25px;
//                     border-radius: 8px;
//                     font-size: 1em;
//                     font-weight: 500;
//                     text-align: center;
//                 }

//                 .tax-uploader-message.info {
//                     background-color: #e7f3ff;
//                     color: #0056b3;
//                     border: 1px solid #b3d7ff;
//                 }

//                 .tax-uploader-message.success {
//                     background-color: #d4edda;
//                     color: #155724;
//                     border: 1px solid #c3e6cb;
//                 }

//                 .tax-uploader-message.error {
//                     background-color: #f8d7da;
//                     color: #721c24;
//                     border: 1px solid #f5c6cb;
//                 }

//                 /* Tax Summary Output */
//                 .tax-summary-output {
//                     margin-top: 40px;
//                     background-color: #f9f9f9;
//                     padding: 25px;
//                     border-radius: 12px;
//                     box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
//                     border: 1px solid #eee;
//                 }

//                 .tax-summary-output h3 {
//                     color: #2c3e50;
//                     margin-bottom: 25px;
//                     text-align: center;
//                     font-size: 2em;
//                     font-weight: 700;
//                 }

//                 .document-processing-summary-section,
//                 .aggregated-financial-data-section,
//                 .final-tax-computation-section,
//                 .suggestions-output .section-box {
//                     margin-top: 20px;
//                     padding: 20px;
//                     background-color: #ffffff;
//                     border-radius: 10px;
//                     box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
//                     border: 1px solid #e9ecef;
//                 }

//                 .section-title {
//                     color: #34495e;
//                     font-size: 1.6em;
//                     margin-bottom: 20px;
//                     border-bottom: 2px solid #f0f2f5;
//                     padding-bottom: 10px;
//                     text-align: center;
//                 }

//                 .document-status-item {
//                     background-color: #fdfdfd;
//                     padding: 15px;
//                     border-radius: 8px;
//                     margin-bottom: 15px;
//                     border: 1px solid #f0f0f0;
//                     box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
//                 }

//                 .document-status-item p {
//                     margin: 5px 0;
//                     font-size: 0.95em;
//                     color: #444;
//                 }

//                 .document-status-item strong {
//                     color: #2c3e50;
//                 }

//                 .status-success {
//                     color: #28a745;
//                     font-weight: 700;
//                 }

//                 .status-warning {
//                     color: #ffc107;
//                     font-weight: 700;
//                 }

//                 .status-error {
//                     color: #dc3545;
//                     font-weight: 700;
//                 }

//                 .extracted-fields-preview, .extracted-raw-text-preview {
//                     background-color: #e9ecef;
//                     border: 1px solid #dee2e6;
//                     padding: 10px;
//                     border-radius: 5px;
//                     font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
//                     font-size: 0.85em;
//                     white-space: pre-wrap; /* Ensures text wraps */
//                     word-break: break-all; /* Breaks words if necessary */
//                     max-height: 200px; /* Limit height for long outputs */
//                     overflow-y: auto; /* Add scroll for overflow */
//                 }

//                 .income-details-section,
//                 .deductions-section,
//                 .taxation-summary-section {
//                     margin-bottom: 25px;
//                     padding: 15px;
//                     border: 1px solid #f0f0f0;
//                     border-radius: 8px;
//                     background-color: #fdfdfd;
//                 }

//                 .income-details-section h5,
//                 .deductions-section h5,
//                 .taxation-summary-section h5 {
//                     color: #007bff;
//                     font-size: 1.3em;
//                     margin-bottom: 15px;
//                     border-bottom: 1px solid #e0e0e0;
//                     padding-bottom: 8px;
//                 }

//                 .income-details-section p,
//                 .deductions-section p,
//                 .taxation-summary-section p {
//                     margin: 8px 0;
//                     font-size: 0.98em;
//                     color: #333;
//                 }

//                 .computation-detail {
//                     margin-bottom: 10px;
//                     padding-bottom: 5px;
//                     border-bottom: 1px dashed #e9ecef;
//                 }

//                 .computation-detail:last-child {
//                     border-bottom: none;
//                 }

//                 .computation-detail strong {
//                     color: #2c3e50;
//                 }

//                 .final-amount-box {
//                     margin-top: 20px;
//                     padding: 15px;
//                     border-radius: 8px;
//                     background-color: #e9f7ef; /* Light green for positive outcome */
//                     border: 1px solid #c3e6cb;
//                     text-align: center;
//                     font-size: 1.1em;
//                     font-weight: 600;
//                 }

//                 .final-amount-box .tax-due-amount {
//                     background-color: #f8d7da; /* Light red for tax due */
//                     color: #721c24;
//                     border: 1px solid #f5c6cb;
//                     padding: 10px;
//                     border-radius: 5px;
//                     margin-top: 10px;
//                 }

//                 .final-amount-box .refund-amount {
//                     background-color: #d4edda; /* Light green for refund */
//                     color: #155724;
//                     border: 1px solid #c3e6cb;
//                     padding: 10px;
//                     border-radius: 5px;
//                     margin-top: 10px;
//                 }

//                 .computation-notes {
//                     margin-top: 20px;
//                     padding: 10px;
//                     background-color: #f0f8ff;
//                     border: 1px solid #d1e7fd;
//                     border-radius: 8px;
//                     font-size: 0.9em;
//                     color: #444;
//                     font-style: italic;
//                 }

//                 .highlight-regime {
//                     font-weight: bold;
//                     color: #007bff;
//                 }

//                 /* Suggestions specific styling */
//                 .suggestions-list {
//                     list-style-type: disc;
//                     margin-left: 20px;
//                     padding-left: 0;
//                 }

//                 .suggestions-list li {
//                     margin-bottom: 8px;
//                     color: #333;
//                 }

//                 .gemini-regime-analysis {
//                     margin-top: 20px;
//                     padding: 15px;
//                     background-color: #e6f7ff;
//                     border: 1px solid #91d5ff;
//                     border-radius: 8px;
//                 }

//                 .gemini-regime-analysis h4 {
//                     color: #0056b3;
//                     margin-bottom: 10px;
//                 }

//                 /* Responsive Adjustments */
//                 @media (max-width: 768px) {
//                     .tax-uploader-container {
//                         margin: 20px 10px;
//                         padding: 20px;
//                     }

//                     .tax-uploader-title {
//                         font-size: 1.8em;
//                     }

//                     .tax-uploader-button {
//                         padding: 12px 15px;
//                         font-size: 1em;
//                     }

//                     .action-buttons-container {
//                         flex-direction: column;
//                         gap: 10px;
//                     }

//                     .action-buttons-container .tax-uploader-button {
//                         min-width: unset;
//                     }

//                     .tax-summary-output h3 {
//                         font-size: 1.6em;
//                     }

//                     .section-title {
//                         font-size: 1.4em;
//                     }

//                     .income-details-section h5,
//                     .deductions-section h5,
//                     .taxation-summary-section h5 {
//                         font-size: 1.1em;
//                     }
//                 }

//                 @media (max-width: 480px) {
//                     body {
//                         padding: 10px;
//                     }

//                     .tax-uploader-container {
//                         margin: 10px;
//                         padding: 15px;
//                     }

//                     .tax-uploader-title {
//                         font-size: 1.5em;
//                     }

//                     .tax-uploader-button {
//                         font-size: 0.9em;
//                         padding: 10px 12px;
//                     }

//                     .tax-uploader-message {
//                         font-size: 0.9em;
//                         padding: 10px;
//                     }
//                 }
//             `}</style>
//             <h2 className="tax-uploader-title">Upload Tax Documents</h2>
//             <form onSubmit={handleSubmit}>
//                 {/* Document Type Selection */}
//                 <div className="tax-uploader-form-group">
//                     <label htmlFor="documentType" className="tax-uploader-label">
//                         Specify Document Type (Optional, for better accuracy):
//                     </label>
//                     <select
//                         id="documentType"
//                         value={documentTypeHint}
//                         onChange={handleDocumentTypeChange}
//                         className="tax-uploader-file-input"
//                         disabled={loading || isGeneratingSuggestions || isGeneratingITR}
//                     >
//                         {documentTypes.map(type => (
//                             <option key={type} value={type}>{type}</option>
//                         ))}
//                     </select>
//                 </div>

//                 <div className="tax-uploader-form-group">
//                     <label htmlFor="file-input" className="tax-uploader-label">Choose Files (select multiple with Ctrl/Cmd+Click):</label>
//                     <input
//                         id="file-input"
//                         type="file"
//                         multiple
//                         onChange={handleFileChange}
//                         className="tax-uploader-file-input"
//                         disabled={loading || isGeneratingSuggestions || isGeneratingITR}
//                         accept=".pdf,.png,.jpg,.jpeg" // Specify accepted file types
//                     />
//                     {selectedFiles.length > 0 && (
//                         <p className="selected-files-text">
//                             Selected: {selectedFiles.map(file => file.name).join(', ')}
//                         </p>
//                     )}
//                 </div>

//                 <button
//                     type="submit"
//                     className="tax-uploader-button"
//                     disabled={loading || selectedFiles.length === 0 || isGeneratingSuggestions || isGeneratingITR}
//                 >
//                     {loading ? (
//                         <>
//                             <div className="tax-uploader-spinner"></div>
//                             Processing with AI...
//                         </>
//                     ) : (
//                         'Upload & Process Documents'
//                     )}
//                 </button>
//             </form>

//             {(loading || isGeneratingSuggestions || isGeneratingITR) && (
//                 <div className="tax-uploader-loading">
//                     <div className="tax-uploader-spinner"></div>
//                     {message}
//                 </div>
//             )}

//             {message && !loading && !isGeneratingSuggestions && !isGeneratingITR && (
//                 <div className={`tax-uploader-message ${messageType}`}>
//                     {message}
//                 </div>
//             )}

//             {/* Action buttons appear only after initial document processing is successful */}
//             {uploadResult && uploadResult.record_id && !loading && (
//                 <div className="action-buttons-container">
//                     <button
//                         type="button"
//                         onClick={handleGetSuggestions}
//                         className="tax-uploader-button get-suggestions-button"
//                         disabled={isGeneratingSuggestions || isGeneratingITR}
//                     >
//                         {isGeneratingSuggestions ? 'Generating Suggestions...' : 'Get AI Suggestions & ML Predictions'}
//                     </button>
//                     <button
//                         type="button"
//                         onClick={handleGenerateITRForm}
//                         className="tax-uploader-button generate-itr-button"
//                         disabled={isGeneratingITR || isGeneratingSuggestions}
//                     >
//                         {isGeneratingITR ? 'Generating ITR...' : 'Generate ITR Form'}
//                     </button>
//                 </div>
//             )}

//             {/* Display Document Processing Summary (from initial upload) */}
//             {uploadResult && uploadResult.document_processing_summary && (
//                 <div className="tax-summary-output">
//                     <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>Document Processing Summary</h3>
//                     <div className="document-processing-summary-section section-box">
//                         {uploadResult.document_processing_summary.map((doc, index) => {
//                             const statusClass = doc.status === 'success' ? 'status-success' :
//                                                 doc.status === 'warning' ? 'status-warning' : 'status-error';
//                             return (
//                                 <div key={index} className="document-status-item">
//                                     <p><strong>File:</strong> {doc.filename} ({doc.stored_path && <a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer">View Stored Document</a>})</p>
//                                     <p><strong>Status:</strong> <span className={statusClass}>{doc.status?.toUpperCase() || 'N/A'}</span></p>
//                                     <p><strong>Identified Type:</strong> {doc.identified_type || 'N/A'}</p>
//                                     <p><strong>Message:</strong> {doc.message || 'N/A'}</p>
//                                     {doc.extracted_fields && Object.keys(doc.extracted_fields).length > 0 && (
//                                         <p><strong>Extracted Fields:</strong>
//                                             <pre className="extracted-fields-preview">
//                                                 {renderExtractedFields(doc.extracted_fields)}
//                                             </pre>
//                                         </p>
//                                     )}
//                                     {doc.extracted_raw_text && (
//                                         <p><strong>Extracted Raw Text Snippet:</strong> <pre className="extracted-raw-text-preview">{doc.extracted_raw_text.substring(0, 200)}...</pre></p>
//                                     )}
//                                 </div>
//                             );
//                         })}
//                     </div>
//                 </div>
//             )}

//             {/* Display Aggregated Financial Data and Rule-Based Computation (from initial upload) */}
//             {uploadResult && uploadResult.aggregated_financial_data && uploadResult.final_tax_computation_summary && (
//                 <div className="tax-summary-output">
//                     <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>Aggregated & Rule-Based Computation</h3>

//                     <div className="aggregated-financial-data-section section-box">
//                         <h4 className="section-title">Aggregated Financial Data Summary</h4>
//                         <div className="income-details-section">
//                             <h5>Income Details</h5>
//                             <p><strong>Financial Year:</strong> {uploadResult.aggregated_financial_data.financial_year || 'N/A'}</p>
//                             <p><strong>Assessment Year:</strong> {uploadResult.aggregated_financial_data.assessment_year || 'N/A'}</p>
//                             <p><strong>Name:</strong> {uploadResult.aggregated_financial_data.name_of_employee || 'N/A'}</p>
//                             <p><strong>PAN:</strong> {uploadResult.aggregated_financial_data.pan_of_employee || 'N/A'}</p>
//                             <p><strong>Date of Birth:</strong> {uploadResult.aggregated_financial_data.date_of_birth !== "0000-01-01" ? uploadResult.aggregated_financial_data.date_of_birth : 'N/A'}</p>
//                             <p><strong>Age:</strong> {uploadResult.aggregated_financial_data.Age || 'N/A'}</p>
//                             <p><strong>Gross Annual Salary:</strong> {formatCurrency(uploadResult.aggregated_financial_data.gross_salary_total)}</p>
//                             <p><strong>Exempt Allowances:</strong> {formatCurrency(uploadResult.aggregated_financial_data.total_exempt_allowances)}</p>
//                             <p><strong>Income from House Property:</strong> {formatCurrency(uploadResult.aggregated_financial_data.income_from_house_property)}</p>
//                             <p><strong>Income from Other Sources:</strong> {formatCurrency(uploadResult.aggregated_financial_data.income_from_other_sources)}</p>
//                             <p><strong>Long Term Capital Gains:</strong> {formatCurrency(uploadResult.aggregated_financial_data.capital_gains_long_term)}</p>
//                             <p><strong>Short Term Capital Gains:</strong> {formatCurrency(uploadResult.aggregated_financial_data.capital_gains_short_term)}</p>
//                             <p><strong>Total Gross Income (Aggregated):</strong> {formatCurrency(uploadResult.final_tax_computation_summary.calculated_gross_income)}</p>
//                         </div>
//                         <div className="deductions-section">
//                             <h5>Deductions Claimed</h5>
//                             {uploadResult.aggregated_financial_data.standard_deduction > 0 && 
//                                 <p><strong>Standard Deduction:</strong> {formatCurrency(uploadResult.aggregated_financial_data.standard_deduction)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.professional_tax > 0 &&
//                                 <p><strong>Professional Tax:</strong> {formatCurrency(uploadResult.aggregated_financial_data.professional_tax)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.interest_on_housing_loan_24b !== 0 &&
//                                 <p><strong>Interest on Home Loan (Section 24(b)):</strong> {formatCurrency(uploadResult.aggregated_financial_data.interest_on_housing_loan_24b)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80C > 0 &&
//                                 <p><strong>Section 80C Investments:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80C)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80CCD1B > 0 &&
//                                 <p><strong>Section 80CCD1B:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80CCD1B)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80D > 0 &&
//                                 <p><strong>Section 80D (Health Insurance):</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80D)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80G > 0 &&
//                                 <p><strong>Section 80G:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80G)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80TTA > 0 &&
//                                 <p><strong>Section 80TTA:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80TTA)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80TTB > 0 &&
//                                 <p><strong>Section 80TTB:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80TTB)}</p>
//                             }
//                             {uploadResult.aggregated_financial_data.deduction_80E > 0 &&
//                                 <p><strong>Section 80E (Education Loan Interest):</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80E)}</p>
//                             }
//                             <p><strong>Total Deductions (Aggregated for Display):</strong> {formatCurrency(uploadResult.aggregated_financial_data.total_deductions)}</p>
//                         </div>
//                         <div className="taxation-summary-section">
//                             <h5>Tax Payments & Regime</h5>
//                             <p><strong>Total TDS Credit:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.total_tds_credit)}</p>
//                             <p><strong>Advance Tax Paid:</strong> {formatCurrency(uploadResult.aggregated_financial_data.advance_tax)}</p>
//                             <p><strong>Self-Assessment Tax Paid:</strong> {formatCurrency(uploadResult.aggregated_financial_data.self_assessment_tax)}</p>
//                             <p><strong>Tax Regime Chosen (from docs):</strong> <span className="highlight-regime">{uploadResult.aggregated_financial_data.tax_regime_chosen || 'Not Specified'}</span></p>
//                         </div>
//                     </div>
//                     <div className="final-tax-computation-section section-box">
//                         <h4 className="section-title">Final Tax Computation Summary (Rule-Based)</h4>
//                         {uploadResult.final_tax_computation_summary.calculation_details && uploadResult.final_tax_computation_summary.calculation_details.length > 0 && (
//                             <div className="computation-details-list">
//                                 <h5>Calculation Steps:</h5>
//                                 <ul style={{ listStyleType: 'decimal', marginLeft: '20px', paddingLeft: '0' }}>
//                                     {uploadResult.final_tax_computation_summary.calculation_details.map((detail, idx) => (
//                                         <li key={idx} className="computation-detail-item">{detail}</li>
//                                     ))}
//                                 </ul>
//                             </div>
//                         )}
//                         <div className="final-amount-box">
//                             <p><strong>Computed Taxable Income:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.computed_taxable_income)}</p>
//                             <p><strong>Estimated Tax Payable:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.estimated_tax_payable)}</p>
//                             <p><strong>Tax Regime Considered for Rule-Based Calculation:</strong> <span className="highlight-regime">{uploadResult.final_tax_computation_summary.regime_considered || 'N/A'}</span></p>
//                             {uploadResult.final_tax_computation_summary.predicted_refund_due > 0 && (
//                                 <p className="refund-amount">
//                                     <strong>Refund Due:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.predicted_refund_due)}
//                                 </p>
//                             )}
//                             {uploadResult.final_tax_computation_summary.predicted_additional_due > 0 && (
//                                 <p className="tax-due-amount">
//                                     <strong>Additional Tax Due:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.predicted_additional_due)}
//                                 </p>
//                             )}
//                         </div>
//                         {uploadResult.final_tax_computation_summary.notes && uploadResult.final_tax_computation_summary.notes.length > 0 && (
//                             <p className="computation-notes">
//                                 <strong>Note:</strong> {Array.isArray(uploadResult.final_tax_computation_summary.notes) ? uploadResult.final_tax_computation_summary.notes.join(', ') : uploadResult.final_tax_computation_summary.notes}
//                             </p>
//                         )}
//                     </div>
//                 </div>
//             )}

//             {/* Display Suggestions from Gemini and ML Predictions (only after Get Suggestions is clicked) */}
//             {suggestionsResult && !isGeneratingSuggestions && (
//                 <div className="suggestions-output tax-summary-output">
//                     <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>AI Recommendations & Predictions</h3>
//                     <div className="section-box">
//                         {suggestionsResult.suggestions_from_gemini && suggestionsResult.suggestions_from_gemini.length > 0 ? (
//                             <>
//                                 <h4>Based on Gemini AI:</h4>
//                                 <ul className="suggestions-list">
//                                     {suggestionsResult.suggestions_from_gemini.map((suggestion, index) => (
//                                         <li key={index}>{suggestion}</li>
//                                     ))}
//                                 </ul>
//                             </>
//                         ) : (
//                             <p>Gemini did not provide specific tax-saving suggestions at this moment, but your tax situation seems optimized.</p>
//                         )}
//                         {suggestionsResult.gemini_regime_analysis && (
//                             <div className="gemini-regime-analysis">
//                                 <h4>Gemini's Regime Analysis:</h4>
//                                 <p>{suggestionsResult.gemini_regime_analysis}</p>
//                             </div>
//                         )}
//                         {suggestionsResult.ml_prediction_summary && (
//                             <>
//                                 <h4>ML Model Prediction:</h4>
//                                 {suggestionsResult.ml_prediction_summary.predicted_tax_regime && (
//                                     <p><strong>Predicted Tax Regime:</strong> {suggestionsResult.ml_prediction_summary.predicted_tax_regime}</p>
//                                 )}
//                                 <p><strong>Predicted Tax Liability:</strong> {formatCurrency(suggestionsResult.ml_prediction_summary.predicted_tax_liability)}</p>
//                                 <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(suggestionsResult.ml_prediction_summary.predicted_refund_due)}</p>
//                                 <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(suggestionsResult.ml_prediction_summary.predicted_additional_due)}</p>
//                                 {suggestionsResult.ml_prediction_summary.notes && (
//                                     <p><strong>Notes:</strong> {suggestionsResult.ml_prediction_summary.notes}</p>
//                                 )}
//                             </>
//                         )}
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// };

// export default TaxUploader;
























import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

const TaxUploader = () => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
    const [uploadResult, setUploadResult] = useState(null); // Stores initial processing result (record_id, doc summary, aggregated_data, computation_summary)
    const [suggestionsResult, setSuggestionsResult] = useState(null); // Stores suggestions and ML predictions
    const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);
    const [isGeneratingITR, setIsGeneratingITR] = useState(false);
    const [documentTypeHint, setDocumentTypeHint] = useState('Auto-Detect'); // Default value

    // List of common document types for the dropdown
    const documentTypes = [
        'Auto-Detect', // Default option, AI attempts to detect
        'Form 16',
        'Bank Statement',
        'Form 26AS',
        'Salary Slip',
        'Investment Proof',
        'Home Loan Statement',
        'Other Document',
    ];

    // Helper function to safely format currency values
    const formatCurrency = (value) => {
        if (value === null || value === undefined || isNaN(parseFloat(value))) {
            return 'N/A';
        }
        return parseFloat(value).toLocaleString('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    };

    const handleFileChange = (event) => {
        setSelectedFiles(Array.from(event.target.files));
        // Clear all previous results/messages on new file selection
        setMessage('');
        setMessageType('');
        setUploadResult(null);
        setSuggestionsResult(null);
        setIsGeneratingSuggestions(false);
        setIsGeneratingITR(false);
    };

    const handleDocumentTypeChange = (event) => {
        setDocumentTypeHint(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (selectedFiles.length === 0) {
            setMessage('Please select at least one file.');
            setMessageType('error');
            return;
        }

        setLoading(true);
        setMessage('Uploading and processing documents with AI...');
        setMessageType('info');
        setUploadResult(null); // Clear previous results
        setSuggestionsResult(null);
        setIsGeneratingSuggestions(false);
        setIsGeneratingITR(false);

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('documents', file);
        });
        formData.append('document_type', documentTypeHint);

        const jwt_token = Cookies.get('jwt_token');

        try {
            const config = {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            };
            if (jwt_token) {
                config.headers['Authorization'] = `Bearer ${jwt_token}`;
            }

            const response = await axios.post('http://127.0.0.1:5000/api/process_documents', formData, config);

            if (response.data.status === 'success' || response.data.status === 'partial_success') {
                setMessage(response.data.message || 'Documents processed and data saved successfully!');
                setMessageType('success');
                setUploadResult(response.data); // Store the entire response for display
                setSelectedFiles([]);
                document.getElementById('file-input').value = ''; // Clear file input field
            } else {
                setMessage(response.data.message || 'An unknown error occurred during processing.');
                setMessageType('error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            if (error.response) {
                if (error.response.status === 401) {
                    setMessage('Authentication required. Please log in.');
                    Cookies.remove('jwt_token');
                    window.location.href = '/login';
                } else if (error.response.data && error.response.data.message) {
                    setMessage(`Error: ${error.response.data.message}`);
                } else {
                    setMessage(`Server responded with status ${error.response.status}`);
                }
            } else {
                setMessage('An error occurred while uploading or processing documents. Check network connection and backend server.');
            }
            setMessageType('error');
        } finally {
            setLoading(false);
        }
    };

    const handleGetSuggestions = async () => {
        if (!uploadResult || !uploadResult.record_id) {
            setMessage('Please upload and process documents first to get suggestions.');
            setMessageType('error');
            return;
        }

        setIsGeneratingSuggestions(true);
        setMessage('Generating AI-powered suggestions and ML predictions...');
        setMessageType('info');
        setSuggestionsResult(null); // Clear previous suggestions

        const jwt_token = Cookies.get('jwt_token');

        try {
            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt_token}`,
                }
            };

            const payload = {
                record_id: uploadResult.record_id // Send the record_id to fetch data for suggestions
            };

            const response = await axios.post('http://127.0.0.1:5000/api/get_suggestions', payload, config);

            if (response.data.status === 'success') {
                setMessage(response.data.message || 'AI suggestions and ML predictions generated.');
                setMessageType('success');
                setSuggestionsResult(response.data); // Store the full suggestions result
            } else {
                setMessage(response.data.message || 'Failed to get suggestions.');
                setMessageType('error');
            }
        } catch (error) {
            console.error('Suggestions error:', error);
            if (error.response) {
                if (error.response.status === 401) {
                    setMessage('Authentication required. Please log in.');
                    Cookies.remove('jwt_token');
                    window.location.href = '/login';
                } else if (error.response.data && error.response.data.message) {
                    setMessage(`Error: ${error.response.data.message}`);
                } else {
                    setMessage(`Server responded with status ${error.response.status}`);
                }
            } else {
                setMessage('Error fetching AI suggestions. Check backend connection and API keys.');
            }
            setMessageType('error');
        } finally {
            setIsGeneratingSuggestions(false);
        }
    };

    const handleGenerateITRForm = async () => {
        if (!uploadResult || !uploadResult.record_id) {
            setMessage('Please upload and process documents first to generate ITR form.');
            setMessageType('error');
            return;
        }

        setIsGeneratingITR(true);
        setMessage('Generating ITR form...');
        setMessageType('info');

        const jwt_token = Cookies.get('jwt_token');

        try {
            const config = {
                headers: {
                    'Authorization': `Bearer ${jwt_token}`,
                },
                responseType: 'blob', // Important for receiving a file
            };
            
            // Fetch the ITR form using the record_id obtained after saving
            const response = await axios.get(`http://127.0.0.1:5000/api/generate-itr/${uploadResult.record_id}`, config);

            if (response.status === 200) {
                const blob = new Blob([response.data], { type: 'application/pdf' });
                const downloadUrl = window.URL.createObjectURL(blob);
                const contentDisposition = response.headers['content-disposition'];
                let filename = `ITR_Form_${uploadResult.record_id}.pdf`; // Default filename

                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1];
                    }
                }
                
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove(); // Clean up the element
                window.URL.revokeObjectURL(downloadUrl); // Revoke the object URL

                setMessage('ITR form generated and downloaded successfully!');
                setMessageType('success');
            } else {
                // If it's not a PDF but an error JSON, try to parse it
                const errorData = await new Response(response.data).text(); // Read blob as text for error
                setMessage(`Failed to generate ITR form: ${errorData || response.statusText}`);
                setMessageType('error');
            }
        } catch (error) {
            console.error('ITR generation error:', error);
            if (axios.isAxiosError(error) && error.response && error.response.data) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorJson = JSON.parse(reader.result);
                        setMessage(`Error generating ITR form: ${errorJson.message || JSON.stringify(errorJson)}`);
                    } catch (e) {
                        // Not a JSON error, use generic message
                        setMessage(`Error generating ITR form: ${reader.result || error.response.statusText}`);
                    }
                };
                reader.readAsText(error.response.data);
            } else {
                setMessage('Network error or server unavailable during ITR form generation.');
            }
            setMessageType('error');
        } finally {
            setIsGeneratingITR(false);
        }
    };

    // Helper function to render extracted fields dynamically
    const renderExtractedFields = (fields, identifiedType) => {
        if (!fields) return null;

        // Define a comprehensive list of all possible fields and their display names
        const fieldDefinitions = {
            // Personal & Employer Info
            "name_of_employee": { label: "Name of Employee", type: "text" },
            "pan_of_employee": { label: "PAN of Employee", type: "text" },
            "date_of_birth": { label: "Date of Birth", type: "date" },
            "gender": { label: "Gender", type: "text" },
            "residential_status": { label: "Residential Status", type: "text" },
            "employer_name": { label: "Employer Name", type: "text" },
            "employer_address": { label: "Employer Address", type: "text" },
            "pan_of_deductor": { label: "PAN of Deductor", type: "text" },
            "tan_of_deductor": { label: "TAN of Deductor", type: "text" },
            "designation_of_employee": { label: "Designation", type: "text" },
            // Financial Years & Period
            "financial_year": { label: "Financial Year", type: "text" },
            "assessment_year": { label: "Assessment Year", type: "text" },
            "period_from": { label: "Period From", type: "date" },
            "period_to": { label: "Period To", type: "date" },
            "statement_start_date": { label: "Statement Start Date", type: "date" },
            "statement_end_date": { label: "Statement End Date", type: "date" },
            // Income
            "gross_salary_total": { label: "Gross Salary Total", type: "currency" },
            "salary_as_per_sec_17_1": { label: "Salary U/S 17(1)", type: "currency" },
            "value_of_perquisites_u_s_17_2": { label: "Perquisites U/S 17(2)", type: "currency" },
            "profits_in_lieu_of_salary_u_s_17_3": { label: "Profits in Lieu of Salary U/S 17(3)", type: "currency" },
            "basic_salary": { label: "Basic Salary", type: "currency" },
            "hra_received": { label: "HRA Received", type: "currency" },
            "conveyance_allowance": { label: "Conveyance Allowance", type: "currency" },
            "transport_allowance": { label: "Transport Allowance", type: "currency" },
            "overtime_pay": { label: "Overtime Pay", type: "currency" },
            "total_exempt_allowances": { label: "Total Exempt Allowances", type: "currency" },
            "income_from_house_property": { label: "Income from House Property", type: "currency" },
            "income_from_other_sources": { label: "Income from Other Sources", type: "currency" },
            "capital_gains_long_term": { label: "Long Term Capital Gains", type: "currency" },
            "capital_gains_short_term": { label: "Short Term Capital Gains", type: "currency" },
            "gross_total_income_as_per_document": { label: "Gross Total Income (Doc)", type: "currency" },
            // Deductions
            "professional_tax": { label: "Professional Tax", type: "currency" },
            "interest_on_housing_loan_self_occupied": { label: "Interest on Home Loan (Self Occupied)", type: "currency" },
            "deduction_80c": { label: "Deduction 80C", type: "currency" },
            "deduction_80c_epf": { label: "Deduction 80C (EPF)", type: "currency" },
            "deduction_80c_insurance_premium": { label: "Deduction 80C (Insurance Premium)", type: "currency" },
            "deduction_80ccc": { label: "Deduction 80CCC", type: "currency" },
            "deduction_80ccd": { label: "Deduction 80CCD", type: "currency" },
            "deduction_80ccd1b": { label: "Deduction 80CCD(1B)", type: "currency" },
            "deduction_80d": { label: "Deduction 80D", type: "currency" },
            "deduction_80g": { label: "Deduction 80G", type: "currency" },
            "deduction_80tta": { label: "Deduction 80TTA", type: "currency" },
            "deduction_80ttb": { label: "Deduction 80TTB", type: "currency" },
            "deduction_80e": { label: "Deduction 80E", type: "currency" },
            "total_deductions_chapter_via": { label: "Total Chapter VI-A Deductions", type: "currency" },
            "aggregate_of_deductions_from_salary": { label: "Aggregate Deductions from Salary", type: "currency" },
            "epf_contribution": { label: "EPF Contribution", type: "currency" },
            "esi_contribution": { label: "ESI Contribution", type: "currency" },
            // Tax Paid
            "total_tds": { label: "Total TDS", type: "currency" },
            "total_tds_deducted_summary": { label: "Total TDS Deducted (Summary)", type: "currency" },
            "total_tds_deposited_summary": { label: "Total TDS Deposited (Summary)", type: "currency" },
            "quarter_1_receipt_number": { label: "Q1 Receipt Number", type: "text" },
            "quarter_1_tds_deducted": { label: "Q1 TDS Deducted", type: "currency" },
            "quarter_1_tds_deposited": { label: "Q1 TDS Deposited", type: "currency" },
            "advance_tax": { label: "Advance Tax", type: "currency" },
            "self_assessment_tax": { label: "Self-Assessment Tax", type: "currency" },
            // Other Tax Info
            "taxable_income_as_per_document": { label: "Taxable Income (Doc)", type: "currency" },
            "tax_payable_as_per_document": { label: "Tax Payable (Doc)", type: "currency" },
            "refund_status_as_per_document": { label: "Refund Status (Doc)", type: "text" },
            "tax_regime_chosen": { label: "Tax Regime Chosen", type: "text" },
            "net_amount_payable": { label: "Net Amount Payable", type: "currency" },
            "days_present": { label: "Days Present", type: "number" },
            "overtime_hours": { label: "Overtime Hours", type: "number" },
            // Bank Statement Details
            "account_holder_name": { label: "Account Holder Name", type: "text" },
            "account_number": { label: "Account Number", type: "text" },
            "ifsc_code": { label: "IFSC Code", type: "text" },
            "bank_name": { label: "Bank Name", type: "text" },
            "branch_address": { label: "Branch Address", type: "text" },
            "opening_balance": { label: "Opening Balance", type: "currency" },
            "closing_balance": { label: "Closing Balance", type: "currency" },
            "total_deposits": { label: "Total Deposits", type: "currency" },
            "total_withdrawals": { label: "Total Withdrawals", type: "currency" },
            "transaction_summary": { label: "Transaction Summary", type: "array_of_objects" }
        };

        const taxRelatedFields = [
            "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
            "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
            "total_exempt_allowances", "income_from_house_property", "income_from_other_sources", "capital_gains_long_term",
            "capital_gains_short_term", "gross_total_income_as_per_document", "professional_tax", "interest_on_housing_loan_self_occupied",
            "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
            "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
            "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
            "epf_contribution", "esi_contribution", "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
            "quarter_1_receipt_number", "quarter_1_tds_deducted", "quarter_1_tds_deposited", "advance_tax", "self_assessment_tax",
            "taxable_income_as_per_document", "tax_payable_as_per_document", "refund_status_as_per_document", "tax_regime_chosen",
            "net_amount_payable", "days_present", "overtime_hours"
        ];

        const bankStatementFields = [
            "account_holder_name", "account_number", "ifsc_code", "bank_name", "branch_address",
            "statement_start_date", "statement_end_date", "opening_balance", "closing_balance",
            "total_deposits", "total_withdrawals", "transaction_summary"
        ];
        
        let fieldsToRender = [];
        if (identifiedType === 'Bank Statement') {
            fieldsToRender = bankStatementFields.filter(key => fields[key] !== undefined);
        } else {
            // For other document types, primarily show tax-related fields plus common ones
            fieldsToRender = Object.keys(fields).filter(key => 
                taxRelatedFields.includes(key) ||
                ["name_of_employee", "pan_of_employee", "financial_year", "assessment_year", "date_of_birth"].includes(key)
            );
        }

        // Sort fields to render according to the predefined order for consistency
        fieldsToRender.sort((a, b) => {
            const indexA = Object.keys(fieldDefinitions).indexOf(a);
            const indexB = Object.keys(fieldDefinitions).indexOf(b);
            return indexA - indexB;
        });


        return (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
                {fieldsToRender.map(key => {
                    const fieldDef = fieldDefinitions[key];
                    let value = fields[key];

                    if (!fieldDef || value === null || value === undefined || (typeof value === 'string' && value.toLowerCase() === 'null') || (typeof value === 'string' && value.trim() === '')) {
                        return null; // Skip if no definition, null, undefined, "null", or empty string
                    }

                    // Handle date fields that might come as "0000-01-01"
                    if (fieldDef.type === "date" && value === "0000-01-01") {
                        value = "N/A";
                    } else if (fieldDef.type === "currency" && typeof value === 'number') {
                        value = formatCurrency(value);
                    } else if (Array.isArray(value) && value.length === 0) {
                        return null; // Skip empty arrays
                    }

                    // Special handling for transaction_summary
                    if (key === "transaction_summary" && Array.isArray(value)) {
                        return (
                            <li key={key}>
                                <strong>{fieldDef.label}:</strong>
                                <pre className="extracted-fields-preview mt-2">
                                    {value.length > 0 ? JSON.stringify(value.map(tx => ({
                                        date: tx.date !== "0000-01-01" ? tx.date : "N/A",
                                        description: tx.description,
                                        amount: formatCurrency(tx.amount)
                                    })), null, 2) : 'No transactions found.'}
                                </pre>
                            </li>
                        );
                    }
                    
                    return (
                        <li key={key}>
                            <strong>{fieldDef.label}:</strong> {value.toString()}
                        </li>
                    );
                })}
            </ul>
        );
    };


    return (
        <div className="tax-uploader-container section-box">
            {/* Inlined CSS for styling the component */}
            <style>{`
                /* General Body Styling */
                body {
                    font-family: 'Inter', sans-serif;
                    background-color: #f0f2f5;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    line-height: 1.6;
                }

                /* Section Box Styling */
                .section-box {
                    background-color: #ffffff;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                    margin-bottom: 25px;
                    border: 1px solid #e0e0e0;
                }

                /* Tax Uploader Container */
                .tax-uploader-container {
                    max-width: 900px;
                    margin: 30px auto;
                    padding: 30px;
                    background-color: #fff;
                    border-radius: 15px;
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                    border: 1px solid #d0d0d0;
                }

                .tax-uploader-title {
                    text-align: center;
                    color: #2c3e50;
                    margin-bottom: 30px;
                    font-size: 2.2em;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }

                /* Form Group */
                .tax-uploader-form-group {
                    margin-bottom: 25px;
                }

                .tax-uploader-label {
                    display: block;
                    margin-bottom: 10px;
                    font-weight: 600;
                    color: #34495e;
                    font-size: 1.1em;
                }

                .tax-uploader-file-input {
                    display: block;
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ced4da;
                    border-radius: 8px;
                    font-size: 1em;
                    color: #495057;
                    background-color: #f8f9fa;
                    transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                }

                .tax-uploader-file-input:focus {
                    border-color: #80bdff;
                    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
                    outline: none;
                }

                .selected-files-text {
                    margin-top: 10px;
                    font-size: 0.95em;
                    color: #555;
                    font-style: italic;
                }

                /* Buttons */
                .tax-uploader-button {
                    display: block;
                    width: 100%;
                    padding: 14px 20px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 1.1em;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background-color 0.3s ease, transform 0.2s ease;
                    box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
                    margin-top: 20px;
                }

                .tax-uploader-button:hover {
                    background-color: #0056b3;
                    transform: translateY(-2px);
                }

                .tax-uploader-button:disabled {
                    background-color: #a0c9f1;
                    cursor: not-allowed;
                    box-shadow: none;
                    transform: none;
                }

                .action-buttons-container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-top: 30px;
                    justify-content: center;
                }

                .action-buttons-container .tax-uploader-button {
                    flex: 1;
                    min-width: 250px;
                    margin: 0; /* Override default margin */
                }

                .get-suggestions-button {
                    background-color: #28a745;
                    box-shadow: 0 4px 10px rgba(40, 167, 69, 0.2);
                }

                .get-suggestions-button:hover {
                    background-color: #218838;
                }

                .generate-itr-button {
                    background-color: #6c757d;
                    box-shadow: 0 4px 10px rgba(108, 117, 125, 0.2);
                }

                .generate-itr-button:hover {
                    background-color: #5a6268;
                }

                /* Loading Spinner */
                .tax-uploader-loading {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-top: 25px;
                    font-size: 1.1em;
                    color: #007bff;
                    font-weight: 500;
                }

                .tax-uploader-spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #007bff;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    animation: spin 1s linear infinite;
                    margin-right: 10px;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                /* Messages */
                .tax-uploader-message {
                    padding: 15px;
                    margin-top: 25px;
                    border-radius: 8px;
                    font-size: 1em;
                    font-weight: 500;
                    text-align: center;
                }

                .tax-uploader-message.info {
                    background-color: #e7f3ff;
                    color: #0056b3;
                    border: 1px solid #b3d7ff;
                }

                .tax-uploader-message.success {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }

                .tax-uploader-message.error {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }

                /* Tax Summary Output */
                .tax-summary-output {
                    margin-top: 40px;
                    background-color: #f9f9f9;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
                    border: 1px solid #eee;
                }

                .tax-summary-output h3 {
                    color: #2c3e50;
                    margin-bottom: 25px;
                    text-align: center;
                    font-size: 2em;
                    font-weight: 700;
                }

                .document-processing-summary-section,
                .aggregated-financial-data-section,
                .final-tax-computation-section,
                .suggestions-output .section-box {
                    margin-top: 20px;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
                    border: 1px solid #e9ecef;
                }

                .section-title {
                    color: #34495e;
                    font-size: 1.6em;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #f0f2f5;
                    padding-bottom: 10px;
                    text-align: center;
                }

                .document-status-item {
                    background-color: #fdfdfd;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border: 1px solid #f0f0f0;
                    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
                }

                .document-status-item p {
                    margin: 5px 0;
                    font-size: 0.95em;
                    color: #444;
                }

                .document-status-item strong {
                    color: #2c3e50;
                }

                .status-success {
                    color: #28a745;
                    font-weight: 700;
                }

                .status-warning {
                    color: #ffc107;
                    font-weight: 700;
                }

                .status-error {
                    color: #dc3545;
                    font-weight: 700;
                }

                .extracted-fields-preview, .extracted-raw-text-preview {
                    background-color: #e9ecef;
                    border: 1px solid #dee2e6;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                    font-size: 0.85em;
                    white-space: pre-wrap; /* Ensures text wraps */
                    word-break: break-all; /* Breaks words if necessary */
                    max-height: 200px; /* Limit height for long outputs */
                    overflow-y: auto; /* Add scroll for overflow */
                }

                .income-details-section,
                .deductions-section,
                .taxation-summary-section {
                    margin-bottom: 25px;
                    padding: 15px;
                    border: 1px solid #f0f0f0;
                    border-radius: 8px;
                    background-color: #fdfdfd;
                }

                .income-details-section h5,
                .deductions-section h5,
                .taxation-summary-section h5 {
                    color: #007bff;
                    font-size: 1.3em;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #e0e0e0;
                    padding-bottom: 8px;
                }

                .income-details-section p,
                .deductions-section p,
                .taxation-summary-section p {
                    margin: 8px 0;
                    font-size: 0.98em;
                    color: #333;
                }

                .computation-detail {
                    margin-bottom: 10px;
                    padding-bottom: 5px;
                    border-bottom: 1px dashed #e9ecef;
                }

                .computation-detail:last-child {
                    border-bottom: none;
                }

                .computation-detail strong {
                    color: #2c3e50;
                }

                .final-amount-box {
                    margin-top: 20px;
                    padding: 15px;
                    border-radius: 8px;
                    background-color: #e9f7ef; /* Light green for positive outcome */
                    border: 1px solid #c3e6cb;
                    text-align: center;
                    font-size: 1.1em;
                    font-weight: 600;
                }

                .final-amount-box .tax-due-amount {
                    background-color: #f8d7da; /* Light red for tax due */
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }

                .final-amount-box .refund-amount {
                    background-color: #d4edda; /* Light green for refund */
                    color: #155724;
                    border: 1px solid #c3e6cb;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }

                .computation-notes {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #f0f8ff;
                    border: 1px solid #d1e7fd;
                    border-radius: 8px;
                    font-size: 0.9em;
                    color: #444;
                    font-style: italic;
                }

                .highlight-regime {
                    font-weight: bold;
                    color: #007bff;
                }

                /* Suggestions specific styling */
                .suggestions-list {
                    list-style-type: disc;
                    margin-left: 20px;
                    padding-left: 0;
                }

                .suggestions-list li {
                    margin-bottom: 8px;
                    color: #333;
                }

                .gemini-regime-analysis {
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #e6f7ff;
                    border: 1px solid #91d5ff;
                    border-radius: 8px;
                }

                .gemini-regime-analysis h4 {
                    color: #0056b3;
                    margin-bottom: 10px;
                }

                /* Responsive Adjustments */
                @media (max-width: 768px) {
                    .tax-uploader-container {
                        margin: 20px 10px;
                        padding: 20px;
                    }

                    .tax-uploader-title {
                        font-size: 1.8em;
                    }

                    .tax-uploader-button {
                        padding: 12px 15px;
                        font-size: 1em;
                    }

                    .action-buttons-container {
                        flex-direction: column;
                        gap: 10px;
                    }

                    .action-buttons-container .tax-uploader-button {
                        min-width: unset;
                    }

                    .tax-summary-output h3 {
                        font-size: 1.6em;
                    }

                    .section-title {
                        font-size: 1.4em;
                    }

                    .income-details-section h5,
                    .deductions-section h5,
                    .taxation-summary-section h5 {
                        font-size: 1.1em;
                    }
                }

                @media (max-width: 480px) {
                    body {
                        padding: 10px;
                    }

                    .tax-uploader-container {
                        margin: 10px;
                        padding: 15px;
                    }

                    .tax-uploader-title {
                        font-size: 1.5em;
                    }

                    .tax-uploader-button {
                        font-size: 0.9em;
                        padding: 10px 12px;
                    }

                    .tax-uploader-message {
                        font-size: 0.9em;
                        padding: 10px;
                    }
                }
            `}</style>
            <h2 className="tax-uploader-title">Upload Tax Documents</h2>
            <form onSubmit={handleSubmit}>
                {/* Document Type Selection */}
                <div className="tax-uploader-form-group">
                    <label htmlFor="documentType" className="tax-uploader-label">
                        Specify Document Type (Optional, for better accuracy):
                    </label>
                    <select
                        id="documentType"
                        value={documentTypeHint}
                        onChange={handleDocumentTypeChange}
                        className="tax-uploader-file-input"
                        disabled={loading || isGeneratingSuggestions || isGeneratingITR}
                    >
                        {documentTypes.map(type => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </select>
                </div>

                <div className="tax-uploader-form-group">
                    <label htmlFor="file-input" className="tax-uploader-label">Choose Files (select multiple with Ctrl/Cmd+Click):</label>
                    <input
                        id="file-input"
                        type="file"
                        multiple
                        onChange={handleFileChange}
                        className="tax-uploader-file-input"
                        disabled={loading || isGeneratingSuggestions || isGeneratingITR}
                        accept=".pdf,.png,.jpg,.jpeg" // Specify accepted file types
                    />
                    {selectedFiles.length > 0 && (
                        <p className="selected-files-text">
                            Selected: {selectedFiles.map(file => file.name).join(', ')}
                        </p>
                    )}
                </div>

                <button
                    type="submit"
                    className="tax-uploader-button"
                    disabled={loading || selectedFiles.length === 0 || isGeneratingSuggestions || isGeneratingITR}
                >
                    {loading ? (
                        <>
                            <div className="tax-uploader-spinner"></div>
                            Processing with AI...
                        </>
                    ) : (
                        'Upload & Process Documents'
                    )}
                </button>
            </form>

            {(loading || isGeneratingSuggestions || isGeneratingITR) && (
                <div className="tax-uploader-loading">
                    <div className="tax-uploader-spinner"></div>
                    {message}
                </div>
            )}

            {message && !loading && !isGeneratingSuggestions && !isGeneratingITR && (
                <div className={`tax-uploader-message ${messageType}`}>
                    {message}
                </div>
            )}

            {/* Action buttons appear only after initial document processing is successful */}
            {uploadResult && uploadResult.record_id && !loading && (
                <div className="action-buttons-container">
                    <button
                        type="button"
                        onClick={handleGetSuggestions}
                        className="tax-uploader-button get-suggestions-button"
                        disabled={isGeneratingSuggestions || isGeneratingITR}
                    >
                        {isGeneratingSuggestions ? 'Generating Suggestions...' : 'Get AI Suggestions'}
                    </button>
                    <button
                        type="button"
                        onClick={handleGenerateITRForm}
                        className="tax-uploader-button generate-itr-button"
                        disabled={isGeneratingITR || isGeneratingSuggestions}
                    >
                        {isGeneratingITR ? 'Generating ITR...' : 'Generate ITR Form'}
                    </button>
                </div>
            )}

            {/* Display Document Processing Summary (from initial upload) */}
            {uploadResult && uploadResult.document_processing_summary && (
                <div className="tax-summary-output">
                    <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>Document Processing Summary</h3>
                    <div className="document-processing-summary-section section-box">
                        {uploadResult.document_processing_summary.map((doc, index) => {
                            const statusClass = doc.status === 'success' ? 'status-success' :
                                                doc.status === 'warning' ? 'status-warning' : 'status-error';
                            return (
                                <div key={index} className="document-status-item">
                                    <p><strong>File:</strong> {doc.filename} ({doc.stored_path && <a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer">View Stored Document</a>})</p>
                                    <p><strong>Status:</strong> <span className={statusClass}>{doc.status?.toUpperCase() || 'N/A'}</span></p>
                                    <p><strong>Identified Type:</strong> {doc.identified_type || 'N/A'}</p>
                                    <p><strong>Message:</strong> {doc.message || 'N/A'}</p>
                                    {doc.extracted_fields && Object.keys(doc.extracted_fields).length > 0 && (
                                        <p><strong>Extracted Fields:</strong>
                                            <pre className="extracted-fields-preview">
                                                {renderExtractedFields(doc.extracted_fields, doc.identified_type)}
                                            </pre>
                                        </p>
                                    )}
                                    {doc.extracted_raw_text && (
                                        <p><strong>Extracted Raw Text Snippet:</strong> <pre className="extracted-raw-text-preview">{doc.extracted_raw_text.substring(0, 200)}...</pre></p>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Display Aggregated Financial Data and Rule-Based Computation (from initial upload) */}
            {uploadResult && uploadResult.aggregated_financial_data && uploadResult.final_tax_computation_summary && (
                <div className="tax-summary-output">
                    <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>Aggregated & Rule-Based Computation</h3>

                    <div className="aggregated-financial-data-section section-box">
                        <h4 className="section-title">Aggregated Financial Data Summary</h4>
                        
                        {/* Conditional rendering for Bank Statement vs. Tax Data */}
                        {uploadResult.aggregated_financial_data.identified_type === 'Bank Statement' || 
                         (uploadResult.aggregated_financial_data.account_number && uploadResult.aggregated_financial_data.account_number !== 'null') ? (
                            <div className="income-details-section"> {/* Re-using for consistent styling */}
                                <h5>Bank Account Details</h5>
                                <p><strong>Account Holder Name:</strong> {uploadResult.aggregated_financial_data.account_holder_name || 'N/A'}</p>
                                <p><strong>Account Number:</strong> {uploadResult.aggregated_financial_data.account_number || 'N/A'}</p>
                                <p><strong>Bank Name:</strong> {uploadResult.aggregated_financial_data.bank_name || 'N/A'}</p>
                                <p><strong>Branch Address:</strong> {uploadResult.aggregated_financial_data.branch_address || 'N/A'}</p>
                                <p><strong>Statement Period:</strong> {uploadResult.aggregated_financial_data.statement_start_date || 'N/A'} to {uploadResult.aggregated_financial_data.statement_end_date || 'N/A'}</p>
                                <p><strong>Opening Balance:</strong> {formatCurrency(uploadResult.aggregated_financial_data.opening_balance)}</p>
                                <p><strong>Closing Balance:</strong> {formatCurrency(uploadResult.aggregated_financial_data.closing_balance)}</p>
                                <p><strong>Total Deposits:</strong> {formatCurrency(uploadResult.aggregated_financial_data.total_deposits)}</p>
                                <p><strong>Total Withdrawals:</strong> {formatCurrency(uploadResult.aggregated_financial_data.total_withdrawals)}</p>
                                {uploadResult.aggregated_financial_data.transaction_summary && uploadResult.aggregated_financial_data.transaction_summary.length > 0 && (
                                    <p>
                                        <strong>Key Transactions:</strong> 
                                        <pre className="extracted-fields-preview mt-2">
                                            {JSON.stringify(uploadResult.aggregated_financial_data.transaction_summary.slice(0, 5).map(tx => ({
                                                date: tx.date !== "0000-01-01" ? tx.date : "N/A",
                                                description: tx.description,
                                                amount: formatCurrency(tx.amount)
                                            })), null, 2)}
                                            {uploadResult.aggregated_financial_data.transaction_summary.length > 5 ? '\n...' : ''}
                                        </pre>
                                    </p>
                                )}
                            </div>
                        ) : (
                            <>
                                <div className="income-details-section">
                                    <h5>Income Details</h5>
                                    <p><strong>Financial Year:</strong> {uploadResult.aggregated_financial_data.financial_year || 'N/A'}</p>
                                    <p><strong>Assessment Year:</strong> {uploadResult.aggregated_financial_data.assessment_year || 'N/A'}</p>
                                    <p><strong>Name:</strong> {uploadResult.aggregated_financial_data.name_of_employee || 'N/A'}</p>
                                    <p><strong>PAN:</strong> {uploadResult.aggregated_financial_data.pan_of_employee || 'N/A'}</p>
                                    <p><strong>Date of Birth:</strong> {uploadResult.aggregated_financial_data.date_of_birth !== "0000-01-01" ? uploadResult.aggregated_financial_data.date_of_birth : 'N/A'}</p>
                                    <p><strong>Age:</strong> {uploadResult.aggregated_financial_data.Age || 'N/A'}</p>
                                    <p><strong>Gross Annual Salary:</strong> {formatCurrency(uploadResult.aggregated_financial_data.gross_salary_total)}</p>
                                    <p><strong>Exempt Allowances:</strong> {formatCurrency(uploadResult.aggregated_financial_data.total_exempt_allowances)}</p>
                                    <p><strong>Income from House Property:</strong> {formatCurrency(uploadResult.aggregated_financial_data.income_from_house_property)}</p>
                                    <p><strong>Income from Other Sources:</strong> {formatCurrency(uploadResult.aggregated_financial_data.income_from_other_sources)}</p>
                                    <p><strong>Long Term Capital Gains:</strong> {formatCurrency(uploadResult.aggregated_financial_data.capital_gains_long_term)}</p>
                                    <p><strong>Short Term Capital Gains:</strong> {formatCurrency(uploadResult.aggregated_financial_data.capital_gains_short_term)}</p>
                                    <p><strong>Total Gross Income (Aggregated):</strong> {formatCurrency(uploadResult.final_tax_computation_summary.calculated_gross_income)}</p>
                                </div>
                                <div className="deductions-section">
                                    <h5>Deductions Claimed</h5>
                                    {uploadResult.aggregated_financial_data.standard_deduction > 0 && 
                                        <p><strong>Standard Deduction:</strong> {formatCurrency(uploadResult.aggregated_financial_data.standard_deduction)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.professional_tax > 0 &&
                                        <p><strong>Professional Tax:</strong> {formatCurrency(uploadResult.aggregated_financial_data.professional_tax)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.interest_on_housing_loan_24b !== 0 &&
                                        <p><strong>Interest on Home Loan (Section 24(b)):</strong> {formatCurrency(uploadResult.aggregated_financial_data.interest_on_housing_loan_24b)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80C > 0 &&
                                        <p><strong>Section 80C Investments:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80C)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80CCD1B > 0 &&
                                        <p><strong>Section 80CCD1B:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80CCD1B)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80D > 0 &&
                                        <p><strong>Section 80D (Health Insurance):</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80D)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80G > 0 &&
                                        <p><strong>Section 80G:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80G)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80TTA > 0 &&
                                        <p><strong>Section 80TTA:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80TTA)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80TTB > 0 &&
                                        <p><strong>Section 80TTB:</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80TTB)}</p>
                                    }
                                    {uploadResult.aggregated_financial_data.deduction_80E > 0 &&
                                        <p><strong>Section 80E (Education Loan Interest):</strong> {formatCurrency(uploadResult.aggregated_financial_data.deduction_80E)}</p>
                                    }
                                    <p><strong>Total Deductions (Aggregated for Display):</strong> {formatCurrency(uploadResult.aggregated_financial_data.total_deductions)}</p>
                                </div>
                                <div className="taxation-summary-section">
                                    <h5>Tax Payments & Regime</h5>
                                    <p><strong>Total TDS Credit:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.total_tds_credit)}</p>
                                    <p><strong>Advance Tax Paid:</strong> {formatCurrency(uploadResult.aggregated_financial_data.advance_tax)}</p>
                                    <p><strong>Self-Assessment Tax Paid:</strong> {formatCurrency(uploadResult.aggregated_financial_data.self_assessment_tax)}</p>
                                    <p><strong>Tax Regime Chosen (from docs):</strong> <span className="highlight-regime">{uploadResult.aggregated_financial_data.tax_regime_chosen || 'Not Specified'}</span></p>
                                </div>
                            </>
                        )}
                    </div>
                    <div className="final-tax-computation-section section-box">
                        <h4 className="section-title">Final Tax Computation Summary (Rule-Based)</h4>
                        {uploadResult.final_tax_computation_summary.calculation_details && uploadResult.final_tax_computation_summary.calculation_details.length > 0 && (
                            <div className="computation-details-list">
                                <h5>Calculation Steps:</h5>
                                <ul style={{ listStyleType: 'decimal', marginLeft: '20px', paddingLeft: '0' }}>
                                    {uploadResult.final_tax_computation_summary.calculation_details.map((detail, idx) => (
                                        <li key={idx} className="computation-detail-item">{detail}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        <div className="final-amount-box">
                            <p><strong>Computed Taxable Income:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.computed_taxable_income)}</p>
                            <p><strong>Estimated Tax Payable:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.estimated_tax_payable)}</p>
                            <p><strong>Tax Regime Considered for Rule-Based Calculation:</strong> <span className="highlight-regime">{uploadResult.final_tax_computation_summary.regime_considered || 'N/A'}</span></p>
                            {uploadResult.final_tax_computation_summary.predicted_refund_due > 0 && (
                                <p className="refund-amount">
                                    <strong>Refund Due:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.predicted_refund_due)}
                                </p>
                            )}
                            {uploadResult.final_tax_computation_summary.predicted_additional_due > 0 && (
                                <p className="tax-due-amount">
                                    <strong>Additional Tax Due:</strong> {formatCurrency(uploadResult.final_tax_computation_summary.predicted_additional_due)}
                                </p>
                            )}
                        </div>
                        {uploadResult.final_tax_computation_summary.notes && uploadResult.final_tax_computation_summary.notes.length > 0 && (
                            <p className="computation-notes">
                                <strong>Note:</strong> {Array.isArray(uploadResult.final_tax_computation_summary.notes) ? uploadResult.final_tax_computation_summary.notes.join(', ') : uploadResult.final_tax_computation_summary.notes}
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* Display Suggestions from Gemini and ML Predictions (only after Get Suggestions is clicked) */}
            {suggestionsResult && !isGeneratingSuggestions && (
                <div className="suggestions-output tax-summary-output">
                    <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>AI Recommendations & Predictions</h3>
                    <div className="section-box">
                        {suggestionsResult.suggestions_from_gemini && suggestionsResult.suggestions_from_gemini.length > 0 ? (
                            <>
                                <h4>Based on Gemini AI:</h4>
                                <ul className="suggestions-list">
                                    {suggestionsResult.suggestions_from_gemini.map((suggestion, index) => (
                                        <li key={index}>{suggestion}</li>
                                    ))}
                                </ul>
                            </>
                        ) : (
                            <p>Gemini did not provide specific tax-saving suggestions at this moment, but your tax situation seems optimized.</p>
                        )}
                        {suggestionsResult.gemini_regime_analysis && (
                            <div className="gemini-regime-analysis">
                                <h4>Gemini's Regime Analysis:</h4>
                                <p>{suggestionsResult.gemini_regime_analysis}</p>
                            </div>
                        )}
                        {suggestionsResult.ml_prediction_summary && (
                            <>
                                <h4>ML Model Prediction:</h4>
                                {suggestionsResult.ml_prediction_summary.predicted_tax_regime && (
                                    <p><strong>Predicted Tax Regime:</strong> {suggestionsResult.ml_prediction_summary.predicted_tax_regime}</p>
                                )}
                                <p><strong>Predicted Tax Liability:</strong> {formatCurrency(suggestionsResult.ml_prediction_summary.predicted_tax_liability)}</p>
                                <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(suggestionsResult.ml_prediction_summary.predicted_refund_due)}</p>
                                <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(suggestionsResult.ml_prediction_summary.predicted_additional_due)}</p>
                                {suggestionsResult.ml_prediction_summary.notes && (
                                    <p><strong>Notes:</strong> {suggestionsResult.ml_prediction_summary.notes}</p>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TaxUploader;
