// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import Cookies from 'js-cookie';
// import './index.css'; // Import TaxHistory specific CSS

// const TaxHistory = () => {
//     const [history, setHistory] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [message, setMessage] = useState('');
//     const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
//     const [selectedRecord, setSelectedRecord] = useState(null); // To view full details of a record
//     const [isGeneratingITR, setIsGeneratingITR] = useState(false);

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

//     // Helper function to render extracted fields dynamically (duplicated from TaxUploader for self-containment)
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

//     useEffect(() => {
//         const fetchHistory = async () => {
//             setLoading(true);
//             setMessage('Fetching your tax history...');
//             setMessageType('info');
//             const jwt_token = Cookies.get('jwt_token');

//             try {
//                 const config = {
//                     headers: {
//                         'Authorization': `Bearer ${jwt_token}`,
//                     }
//                 };
//                 // Fetch aggregated tax records for the user, organized by financial year
//                 const response = await axios.get('http://127.0.0.1:5000/api/tax-records', config);

//                 if (response.data.status === 'success') {
//                     if (Array.isArray(response.data.history)) {
//                         setHistory(response.data.history);
//                         setMessage('Tax history loaded successfully.');
//                         setMessageType('success');
//                     } else {
//                         console.error('API returned non-array data for history property:', response.data.history);
//                         setHistory([]);
//                         setMessage('Failed to load tax history: Unexpected data format.');
//                         setMessageType('error');
//                     }
//                 } else {
//                     setMessage(response.data.message || 'Failed to fetch tax history.');
//                     setMessageType('error');
//                     setHistory([]);
//                 }
//             } catch (error) {
//                 console.error('Fetch history error:', error);
//                 if (error.response) {
//                     if (error.response.status === 401) {
//                         setMessage('Authentication required. Please log in.');
//                         Cookies.remove('jwt_token');
//                         window.location.href = '/login';
//                     } else if (error.response.data && error.response.data.message) {
//                         setMessage(`Error: ${error.response.data.message}`);
//                     } else {
//                         setMessage(`Server responded with status ${error.response.status}`);
//                     }
//                 } else {
//                     setMessage('An error occurred while fetching tax history. Check network connection and backend server.');
//                 }
//                 setMessageType('error');
//                 setHistory([]);
//             } finally {
//                 setLoading(false);
//             }
//         };

//         fetchHistory();
//     }, []); // Empty dependency array means this runs once on mount

//     const handleViewDetails = (record) => {
//         setSelectedRecord(record);
//     };

//     const handleCloseDetails = () => {
//         setSelectedRecord(null);
//     };

//     const handleGenerateITRForm = async (recordId) => {
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
            
//             // The backend route for generating ITR should use the record ID to fetch the aggregated data
//             const response = await axios.get(`http://127.0.0.1:5000/api/generate-itr/${recordId}`, config);

//             if (response.status === 200) {
//                 const blob = new Blob([response.data], { type: 'application/pdf' });
//                 const downloadUrl = window.URL.createObjectURL(blob);
//                 const contentDisposition = response.headers['content-disposition'];
//                 let filename = `ITR_Form_${recordId}.pdf`; // Default filename

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


//     return (
//         <div className="tax-history-container section-box">
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

//                 /* Tax History Container */
//                 .tax-history-container {
//                     max-width: 900px;
//                     margin: 30px auto;
//                     padding: 30px;
//                     background-color: #fff;
//                     border-radius: 15px;
//                     box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
//                     border: 1px solid #d0d0d0;
//                 }

//                 .tax-history-title {
//                     text-align: center;
//                     color: #2c3e50;
//                     margin-bottom: 30px;
//                     font-size: 2.2em;
//                     font-weight: 700;
//                     letter-spacing: -0.5px;
//                 }

//                 /* Loading Spinner */
//                 .tax-history-loading {
//                     display: flex;
//                     align-items: center;
//                     justify-content: center;
//                     margin-top: 25px;
//                     font-size: 1.1em;
//                     color: #007bff;
//                     font-weight: 500;
//                 }

//                 .tax-history-spinner {
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
//                 .tax-history-message {
//                     padding: 15px;
//                     margin-top: 25px;
//                     border-radius: 8px;
//                     font-size: 1em;
//                     font-weight: 500;
//                     text-align: center;
//                 }

//                 .tax-history-message.info {
//                     background-color: #e7f3ff;
//                     color: #0056b3;
//                     border: 1px solid #b3d7ff;
//                 }

//                 .tax-history-message.success {
//                     background-color: #d4edda;
//                     color: #155724;
//                     border: 1px solid #c3e6cb;
//                 }

//                 .tax-history-message.error {
//                     background-color: #f8d7da;
//                     color: #721c24;
//                     border: 1px solid #f5c6cb;
//                 }

//                 /* No Records Message */
//                 .no-records-message {
//                     text-align: center;
//                     font-size: 1.1em;
//                     color: #6c757d;
//                     margin-top: 30px;
//                     padding: 20px;
//                     border: 1px dashed #ced4da;
//                     border-radius: 8px;
//                     background-color: #f8f9fa;
//                 }

//                 /* History List and Item */
//                 .history-list {
//                     margin-top: 30px;
//                 }

//                 .history-item {
//                     background-color: #ffffff;
//                     padding: 20px;
//                     margin-bottom: 20px;
//                     border-radius: 10px;
//                     box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
//                     border: 1px solid #e9ecef;
//                     transition: transform 0.2s ease, box-shadow 0.2s ease;
//                 }

//                 .history-item:hover {
//                     transform: translateY(-3px);
//                     box-shadow: 0 6px 15px rgba(0, 0, 0, 0.12);
//                 }

//                 .history-item-header {
//                     display: flex;
//                     justify-content: space-between;
//                     align-items: center;
//                     margin-bottom: 15px;
//                     padding-bottom: 10px;
//                     border-bottom: 1px solid #f0f2f5;
//                 }

//                 .history-item-header h3 {
//                     color: #007bff;
//                     font-size: 1.4em;
//                     margin: 0;
//                 }

//                 .history-item-header .timestamp {
//                     font-size: 0.9em;
//                     color: #777;
//                 }

//                 .history-item-details p {
//                     margin: 8px 0;
//                     font-size: 0.95em;
//                     color: #333;
//                 }

//                 .history-item-actions {
//                     margin-top: 20px;
//                     display: flex;
//                     gap: 10px;
//                     justify-content: flex-end;
//                 }

//                 .history-item-actions button {
//                     padding: 10px 18px;
//                     border: none;
//                     border-radius: 8px;
//                     font-size: 0.95em;
//                     font-weight: 600;
//                     cursor: pointer;
//                     transition: background-color 0.3s ease, transform 0.2s ease;
//                 }

//                 .view-details-button {
//                     background-color: #007bff;
//                     color: white;
//                     box-shadow: 0 3px 8px rgba(0, 123, 255, 0.2);
//                 }

//                 .view-details-button:hover {
//                     background-color: #0056b3;
//                     transform: translateY(-1px);
//                 }

//                 .generate-itr-button {
//                     background-color: #28a745;
//                     color: white;
//                     box-shadow: 0 3px 8px rgba(40, 167, 69, 0.2);
//                 }

//                 .generate-itr-button:hover {
//                     background-color: #218838;
//                     transform: translateY(-1px);
//                 }

//                 .generate-itr-button:disabled {
//                     background-color: #a0c9f1;
//                     cursor: not-allowed;
//                     box-shadow: none;
//                     transform: none;
//                 }

//                 /* Selected Record Details View */
//                 .selected-record-details {
//                     margin-top: 30px;
//                     background-color: #f9f9f9;
//                     padding: 25px;
//                     border-radius: 12px;
//                     box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
//                     border: 1px solid #eee;
//                 }

//                 .selected-record-details .back-button {
//                     background-color: #6c757d;
//                     color: white;
//                     padding: 10px 15px;
//                     border-radius: 8px;
//                     border: none;
//                     cursor: pointer;
//                     margin-bottom: 25px;
//                     display: inline-flex;
//                     align-items: center;
//                     gap: 5px;
//                     transition: background-color 0.3s ease;
//                 }

//                 .selected-record-details .back-button:hover {
//                     background-color: #5a6268;
//                 }

//                 .selected-record-title {
//                     text-align: center;
//                     color: #2c3e50;
//                     margin-bottom: 30px;
//                     font-size: 2em;
//                     font-weight: 700;
//                 }

//                 .document-processing-summary-section,
//                 .aggregated-financial-data-section,
//                 .final-tax-computation-section,
//                 .suggestions-output {
//                     margin-top: 20px;
//                     padding: 20px;
//                     background-color: #ffffff;
//                     border-radius: 10px;
//                     box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
//                     border: 1px solid #e9ecef;
//                 }

//                 .document-processing-summary-section h4,
//                 .aggregated-financial-data-section h4,
//                 .final-tax-computation-section h4,
//                 .suggestions-output h4 {
//                     color: #34495e;
//                     font-size: 1.6em;
//                     margin-bottom: 20px;
//                     border-bottom: 2px solid #f0f2f5;
//                     padding-bottom: 10px;
//                     text-align: center;
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

//                 .computation-detail-item {
//                     margin-bottom: 5px;
//                     font-size: 0.95em;
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

//                 .gemini-regime-analysis h5 {
//                     color: #0056b3;
//                     margin-bottom: 10px;
//                 }

//                 /* Responsive Adjustments */
//                 @media (max-width: 768px) {
//                     .tax-history-container {
//                         margin: 20px 10px;
//                         padding: 20px;
//                     }

//                     .tax-history-title {
//                         font-size: 1.8em;
//                     }

//                     .history-item-header h3 {
//                         font-size: 1.2em;
//                     }

//                     .history-item-actions button {
//                         padding: 8px 12px;
//                         font-size: 0.85em;
//                     }

//                     .selected-record-title {
//                         font-size: 1.8em;
//                     }

//                     .document-processing-summary-section h4,
//                     .aggregated-financial-data-section h4,
//                     .final-tax-computation-section h4,
//                     .suggestions-output h4 {
//                         font-size: 1.4em;
//                     }

//                     .income-details-section h5,
//                     .deductions-section h5,
//                     .taxation-summary-section h5,
//                     .suggestions-output h5 {
//                         font-size: 1.1em;
//                     }
//                 }

//                 @media (max-width: 480px) {
//                     body {
//                         padding: 10px;
//                     }

//                     .tax-history-container {
//                         margin: 10px;
//                         padding: 15px;
//                     }

//                     .tax-history-title {
//                         font-size: 1.5em;
//                     }

//                     .tax-history-message {
//                         font-size: 0.9em;
//                         padding: 10px;
//                     }
//                 }
//             `}</style>
//             <h2 className="tax-history-title">Your Tax Filing History</h2>

//             {loading && (
//                 <div className="tax-history-loading">
//                     <div className="tax-history-spinner"></div>
//                     {message}
//                 </div>
//             )}

//             {message && !loading && (
//                 <div className={`tax-history-message ${messageType}`}>
//                     {message}
//                 </div>
//             )}

//             {history.length === 0 && !loading && messageType !== 'error' && (
//                 <p className="no-records-message">No tax records found. Upload documents to get started!</p>
//             )}

//             {/* Display history records (list view) */}
//             {!selectedRecord && history.length > 0 && !loading && (
//                 <div className="history-list">
//                     {history.map((record) => (
//                         <div key={record._id} className="history-item section-box">
//                             <div className="history-item-header">
//                                 <h3>
//                                     {record.aggregated_financial_data?.financial_year || 'N/A'} (PAN: {record.aggregated_financial_data?.pan_of_employee || 'N/A'})
//                                 </h3>
//                                 <span className="timestamp">
//                                     Last Updated: {new Date(record.timestamp).toLocaleString()}
//                                 </span>
//                             </div>
//                             <div className="history-item-details">
//                                 <p><strong>Assessment Year:</strong> {record.aggregated_financial_data?.assessment_year || 'N/A'}</p>
//                                 <p><strong>Name:</strong> {record.aggregated_financial_data?.name_of_employee || 'N/A'}</p>
//                                 <p><strong>Estimated Tax Payable:</strong> {formatCurrency(record.final_tax_computation_summary?.estimated_tax_payable)}</p>
//                                 {/* Display refund due or additional tax due from prediction summary */}
//                                 {record.final_tax_computation_summary?.predicted_refund_due > 0 && (
//                                     <p className="refund-amount"><strong>Refund Due:</strong> {formatCurrency(record.final_tax_computation_summary?.predicted_refund_due)}</p>
//                                 )}
//                                 {record.final_tax_computation_summary?.predicted_additional_due > 0 && (
//                                     <p className="tax-due-amount"><strong>Additional Tax Due:</strong> {formatCurrency(record.final_tax_computation_summary?.predicted_additional_due)}</p>
//                                 )}
//                             </div>
//                             <div className="history-item-actions">
//                                 <button onClick={() => handleViewDetails(record)} className="view-details-button">
//                                     View Details
//                                 </button>
//                                 <button
//                                     onClick={() => handleGenerateITRForm(record._id)}
//                                     className="generate-itr-button"
//                                     disabled={isGeneratingITR}
//                                 >
//                                     {isGeneratingITR ? 'Generating...' : 'Generate ITR Form'}
//                                 </button>
//                             </div>
//                         </div>
//                     ))}
//                 </div>
//             )}

//             {/* Display selected record details */}
//             {selectedRecord && (
//                 <div className="selected-record-details">
//                     <button onClick={handleCloseDetails} className="back-button">
//                         &larr; Back to History
//                     </button>
//                     <h3 className="selected-record-title">
//                         Details for {selectedRecord.aggregated_financial_data?.financial_year || 'N/A'} (PAN: {selectedRecord.aggregated_financial_data?.pan_of_employee || 'N/A'})
//                     </h3>

//                     {/* Document Processing Summary */}
//                     {selectedRecord.document_processing_summary && selectedRecord.document_processing_summary.length > 0 && (
//                         <div className="document-processing-summary-section section-box">
//                             <h4>Documents Processed for this Year</h4>
//                             {selectedRecord.document_processing_summary.map((doc, index) => {
//                                 const statusClass = doc.status === 'success' ? 'status-success' :
//                                                     doc.status === 'warning' ? 'status-warning' : 'status-error';
//                                 return (
//                                     <div key={index} className="document-status-item">
//                                         <p><strong>File:</strong> {doc.filename} ({doc.stored_path && <a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer">View Stored Document</a>})</p>
//                                         <p><strong>Status:</strong> <span className={statusClass}>{doc.status?.toUpperCase() || 'N/A'}</span></p>
//                                         <p><strong>Identified Type:</strong> {doc.identified_type || 'N/A'}</p>
//                                         <p><strong>Message:</strong> {doc.message || 'N/A'}</p>
//                                         {doc.extracted_fields && Object.keys(doc.extracted_fields).length > 0 && (
//                                             <p><strong>Extracted Fields:</strong>
//                                                 <pre className="extracted-fields-preview">
//                                                     {renderExtractedFields(doc.extracted_fields)}
//                                                 </pre>
//                                             </p>
//                                         )}
//                                         {doc.extracted_raw_text && (
//                                             <p><strong>Extracted Raw Text Snippet:</strong> <pre className="extracted-raw-text-preview">{doc.extracted_raw_text.substring(0, 200)}...</pre></p>
//                                         )}
//                                     </div>
//                                 );
//                             })}
//                         </div>
//                     )}

//                     {/* Aggregated Financial Data */}
//                     {selectedRecord.aggregated_financial_data && (
//                         <div className="aggregated-financial-data-section section-box">
//                             <h4>Aggregated Financial Data Summary</h4>
//                             <div className="income-details-section">
//                                 <h5>Income Details</h5>
//                                 <p><strong>Financial Year:</strong> {selectedRecord.aggregated_financial_data.financial_year || 'N/A'}</p>
//                                 <p><strong>Assessment Year:</strong> {selectedRecord.aggregated_financial_data.assessment_year || 'N/A'}</p>
//                                 <p><strong>Name:</strong> {selectedRecord.aggregated_financial_data.name_of_employee || 'N/A'}</p>
//                                 <p><strong>PAN:</strong> {selectedRecord.aggregated_financial_data.pan_of_employee || 'N/A'}</p>
//                                 <p><strong>Date of Birth:</strong> {selectedRecord.aggregated_financial_data.date_of_birth !== "0000-01-01" ? selectedRecord.aggregated_financial_data.date_of_birth : 'N/A'}</p>
//                                 <p><strong>Age:</strong> {selectedRecord.aggregated_financial_data.Age || 'N/A'}</p>
//                                 <p><strong>Gross Annual Salary:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.gross_salary_total)}</p>
//                                 <p><strong>Exempt Allowances:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_exempt_allowances)}</p>
//                                 <p><strong>Income from House Property:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_house_property)}</p>
//                                 <p><strong>Income from Other Sources:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_other_sources)}</p>
//                                 <p><strong>Long Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_long_term)}</p>
//                                 <p><strong>Short Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_short_term)}</p>
//                                 <p><strong>Total Gross Income (Aggregated):</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.calculated_gross_income)}</p>
//                             </div>

//                             <div className="deductions-section">
//                                 <h5>Deductions Claimed</h5>
//                                 {selectedRecord.aggregated_financial_data.standard_deduction > 0 && 
//                                     <p><strong>Standard Deduction:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.standard_deduction)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.professional_tax > 0 &&
//                                     <p><strong>Professional Tax:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.professional_tax)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b !== 0 &&
//                                     <p><strong>Interest on Home Loan (Section 24(b)):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80C > 0 &&
//                                     <p><strong>Section 80C Investments:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80C)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80CCD1B > 0 &&
//                                     <p><strong>Section 80CCD1B:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80CCD1B)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80D > 0 &&
//                                     <p><strong>Section 80D (Health Insurance):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80D)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80G > 0 &&
//                                     <p><strong>Section 80G:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80G)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80TTA > 0 &&
//                                     <p><strong>Section 80TTA:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTA)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80TTB > 0 &&
//                                     <p><strong>Section 80TTB:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTB)}</p>
//                                 }
//                                 {selectedRecord.aggregated_financial_data.deduction_80E > 0 &&
//                                     <p><strong>Section 80E (Education Loan Interest):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80E)}</p>
//                                 }
//                                 <p><strong>Total Deductions (Aggregated for Display):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deductions)}</p>
//                             </div>

//                             <div className="taxation-summary-section">
//                                 <h5>Tax Payments & Regime</h5>
//                                 <p><strong>Total TDS Credit:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.total_tds_credit)}</p>
//                                 <p><strong>Advance Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.advance_tax)}</p>
//                                 <p><strong>Self-Assessment Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.self_assessment_tax)}</p>
//                                 <p><strong>Tax Regime Chosen (from docs):</strong> <span className="highlight-regime">{selectedRecord.aggregated_financial_data.tax_regime_chosen || 'Not Specified'}</span></p>
//                             </div>
//                         </div>
//                     )}

//                     {/* Final Tax Computation Summary (Rule-Based) */}
//                     {selectedRecord.final_tax_computation_summary && (
//                         <div className="final-tax-computation-section section-box">
//                             <h4>Final Tax Computation Summary (Rule-Based)</h4>
//                             {selectedRecord.final_tax_computation_summary.calculation_details && selectedRecord.final_tax_computation_summary.calculation_details.length > 0 && (
//                                 <div className="computation-details-list">
//                                     <h5>Calculation Steps:</h5>
//                                     <ul style={{ listStyleType: 'decimal', marginLeft: '20px', paddingLeft: '0' }}>
//                                         {selectedRecord.final_tax_computation_summary.calculation_details.map((detail, idx) => (
//                                             <li key={idx} className="computation-detail-item">{detail}</li>
//                                         ))}
//                                     </ul>
//                                 </div>
//                             )}
//                             <div className="final-amount-box">
//                                 <p><strong>Computed Taxable Income:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.computed_taxable_income)}</p>
//                                 <p><strong>Estimated Tax Payable:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.estimated_tax_payable)}</p>
//                                 <p><strong>Tax Regime Considered for Rule-Based Calculation:</strong> <span className="highlight-regime">{selectedRecord.final_tax_computation_summary.regime_considered || 'N/A'}</span></p>
//                                 {selectedRecord.final_tax_computation_summary.predicted_refund_due > 0 && (
//                                     <p className="refund-amount">
//                                         <strong>Refund Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_refund_due)}
//                                     </p>
//                                 )}
//                                 {selectedRecord.final_tax_computation_summary.predicted_additional_due > 0 && (
//                                     <p className="tax-due-amount">
//                                         <strong>Additional Tax Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_additional_due)}
//                                     </p>
//                                 )}
//                             </div>
//                             {selectedRecord.final_tax_computation_summary.notes && selectedRecord.final_tax_computation_summary.notes.length > 0 && (
//                                 <p className="computation-notes">
//                                     <strong>Note:</strong> {Array.isArray(selectedRecord.final_tax_computation_summary.notes) ? selectedRecord.final_tax_computation_summary.notes.join(', ') : selectedRecord.final_tax_computation_summary.notes}
//                                 </p>
//                             )}
//                         </div>
//                     )}

//                     {/* AI Recommendations & Predictions */}
//                     {selectedRecord.ml_prediction_summary || selectedRecord.suggestions_from_gemini?.length > 0 || selectedRecord.gemini_regime_analysis ? (
//                         <div className="suggestions-output section-box">
//                             <h4>AI Recommendations & Predictions</h4>
//                             {selectedRecord.suggestions_from_gemini && selectedRecord.suggestions_from_gemini.length > 0 ? (
//                                 <>
//                                     <h5>Based on Gemini AI:</h5>
//                                     <ul className="suggestions-list">
//                                         {selectedRecord.suggestions_from_gemini.map((suggestion, index) => (
//                                             <li key={index}>{suggestion}</li>
//                                         ))}
//                                     </ul>
//                                 </>
//                             ) : (
//                                 <p>Gemini did not provide specific tax-saving suggestions for this record.</p>
//                             )}

//                             {selectedRecord.gemini_regime_analysis && (
//                                 <div className="gemini-regime-analysis">
//                                     <h5>Gemini's Regime Analysis:</h5>
//                                     <p>{selectedRecord.gemini_regime_analysis}</p>
//                                 </div>
//                             )}

//                             {selectedRecord.ml_prediction_summary && (
//                                 <>
//                                     <h5>ML Model Prediction:</h5>
//                                     {selectedRecord.ml_prediction_summary.predicted_tax_regime && (
//                                         <p><strong>Predicted Tax Regime:</strong> {selectedRecord.ml_prediction_summary.predicted_tax_regime}</p>
//                                     )}
//                                     <p><strong>Predicted Tax Liability:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_tax_liability)}</p>
//                                     <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_refund_due)}</p>
//                                     <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_additional_due)}</p>
//                                     {selectedRecord.ml_prediction_summary.notes && (
//                                         <p><strong>Notes:</strong> {selectedRecord.ml_prediction_summary.notes}</p>
//                                     )}
//                                 </>
//                             )}
//                         </div>
//                     ) : (
//                         <div className="section-box">
//                             <p>No AI recommendations or ML predictions available for this record yet. These are generated when you click "Get AI Suggestions & ML Predictions" after uploading documents.</p>
//                         </div>
//                     )}

//                 </div>
//             )}
//         </div>
//     );
// };

// export default TaxHistory;






// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import Cookies from 'js-cookie';

// const TaxHistory = () => {
//     const [history, setHistory] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [message, setMessage] = useState('');
//     const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
//     const [selectedRecord, setSelectedRecord] = useState(null); // To view full details of a record
//     const [isGeneratingITR, setIsGeneratingITR] = useState(false);
//     const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false); // Added for history re-generation

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

//     // Helper function to render extracted fields dynamically, similar to TaxUploader
//     const renderExtractedFields = (fields, identifiedType) => {
//         if (!fields) return null;

//         // Define a comprehensive list of all possible fields and their display names
//         const fieldDefinitions = {
//             // Personal & Employer Info
//             "name_of_employee": { label: "Name of Employee", type: "text" },
//             "pan_of_employee": { label: "PAN of Employee", type: "text" },
//             "date_of_birth": { label: "Date of Birth", type: "date" },
//             "gender": { label: "Gender", type: "text" },
//             "residential_status": { label: "Residential Status", type: "text" },
//             "employer_name": { label: "Employer Name", type: "text" },
//             "employer_address": { label: "Employer Address", type: "text" },
//             "pan_of_deductor": { label: "PAN of Deductor", type: "text" },
//             "tan_of_deductor": { label: "TAN of Deductor", type: "text" },
//             "designation_of_employee": { label: "Designation", type: "text" },
//             // Financial Years & Period
//             "financial_year": { label: "Financial Year", type: "text" },
//             "assessment_year": { label: "Assessment Year", type: "text" },
//             "period_from": { label: "Period From", type: "date" },
//             "period_to": { label: "Period To", type: "date" },
//             "statement_start_date": { label: "Statement Start Date", type: "date" },
//             "statement_end_date": { label: "Statement End Date", type: "date" },
//             // Income
//             "gross_salary_total": { label: "Gross Salary Total", type: "currency" },
//             "salary_as_per_sec_17_1": { label: "Salary U/S 17(1)", type: "currency" },
//             "value_of_perquisites_u_s_17_2": { label: "Perquisites U/S 17(2)", type: "currency" },
//             "profits_in_lieu_of_salary_u_s_17_3": { label: "Profits in Lieu of Salary U/S 17(3)", type: "currency" },
//             "basic_salary": { label: "Basic Salary", type: "currency" },
//             "hra_received": { label: "HRA Received", type: "currency" },
//             "conveyance_allowance": { label: "Conveyance Allowance", type: "currency" },
//             "transport_allowance": { label: "Transport Allowance", type: "currency" },
//             "overtime_pay": { label: "Overtime Pay", type: "currency" },
//             "total_exempt_allowances": { label: "Total Exempt Allowances", type: "currency" },
//             "income_from_house_property": { label: "Income from House Property", type: "currency" },
//             "income_from_other_sources": { label: "Income from Other Sources", type: "currency" },
//             "capital_gains_long_term": { label: "Long Term Capital Gains", type: "currency" },
//             "capital_gains_short_term": { label: "Short Term Capital Gains", type: "currency" },
//             "gross_total_income_as_per_document": { label: "Gross Total Income (Doc)", type: "currency" },
//             // Deductions
//             "professional_tax": { label: "Professional Tax", type: "currency" },
//             "interest_on_housing_loan_self_occupied": { label: "Interest on Home Loan (Self Occupied)", type: "currency" },
//             "deduction_80c": { label: "Deduction 80C", type: "currency" },
//             "deduction_80c_epf": { label: "Deduction 80C (EPF)", type: "currency" },
//             "deduction_80c_insurance_premium": { label: "Deduction 80C (Insurance Premium)", type: "currency" },
//             "deduction_80ccc": { label: "Deduction 80CCC", type: "currency" },
//             "deduction_80ccd": { label: "Deduction 80CCD", type: "currency" },
//             "deduction_80ccd1b": { label: "Deduction 80CCD(1B)", type: "currency" },
//             "deduction_80d": { label: "Deduction 80D", type: "currency" },
//             "deduction_80g": { label: "Deduction 80G", type: "currency" },
//             "deduction_80tta": { label: "Deduction 80TTA", type: "currency" },
//             "deduction_80ttb": { label: "Deduction 80TTB", type: "currency" },
//             "deduction_80e": { label: "Deduction 80E", type: "currency" },
//             "total_deductions_chapter_via": { label: "Total Chapter VI-A Deductions", type: "currency" },
//             "aggregate_of_deductions_from_salary": { label: "Aggregate Deductions from Salary", type: "currency" },
//             "epf_contribution": { label: "EPF Contribution", type: "currency" },
//             "esi_contribution": { label: "ESI Contribution", type: "currency" },
//             // Tax Paid
//             "total_tds": { label: "Total TDS", type: "currency" },
//             "total_tds_deducted_summary": { label: "Total TDS Deducted (Summary)", type: "currency" },
//             "total_tds_deposited_summary": { label: "Total TDS Deposited (Summary)", type: "currency" },
//             "quarter_1_receipt_number": { label: "Q1 Receipt Number", type: "text" },
//             "quarter_1_tds_deducted": { label: "Q1 TDS Deducted", type: "currency" },
//             "quarter_1_tds_deposited": { label: "Q1 TDS Deposited", type: "currency" },
//             "advance_tax": { label: "Advance Tax", type: "currency" },
//             "self_assessment_tax": { label: "Self-Assessment Tax", type: "currency" },
//             // Other Tax Info
//             "taxable_income_as_per_document": { label: "Taxable Income (Doc)", type: "currency" },
//             "tax_payable_as_per_document": { label: "Tax Payable (Doc)", type: "currency" },
//             "refund_status_as_per_document": { label: "Refund Status (Doc)", type: "text" },
//             "tax_regime_chosen": { label: "Tax Regime Chosen", type: "text" },
//             "net_amount_payable": { label: "Net Amount Payable", type: "currency" },
//             "days_present": { label: "Days Present", type: "number" },
//             "overtime_hours": { label: "Overtime Hours", type: "number" },
//             // Bank Statement Details
//             "account_holder_name": { label: "Account Holder Name", type: "text" },
//             "account_number": { label: "Account Number", type: "text" },
//             "ifsc_code": { label: "IFSC Code", type: "text" },
//             "bank_name": { label: "Bank Name", type: "text" },
//             "branch_address": { label: "Branch Address", type: "text" },
//             "opening_balance": { label: "Opening Balance", type: "currency" },
//             "closing_balance": { label: "Closing Balance", type: "currency" },
//             "total_deposits": { label: "Total Deposits", type: "currency" },
//             "total_withdrawals": { label: "Total Withdrawals", type: "currency" },
//             "transaction_summary": { label: "Transaction Summary", type: "array_of_objects" }
//         };

//         const taxRelatedFields = [
//             "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
//             "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
//             "total_exempt_allowances", "income_from_house_property", "income_from_other_sources", "capital_gains_long_term",
//             "capital_gains_short_term", "gross_total_income_as_per_document", "professional_tax", "interest_on_housing_loan_self_occupied",
//             "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
//             "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
//             "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
//             "epf_contribution", "esi_contribution", "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
//             "quarter_1_receipt_number", "quarter_1_tds_deducted", "quarter_1_tds_deposited", "advance_tax", "self_assessment_tax",
//             "taxable_income_as_per_document", "tax_payable_as_per_document", "refund_status_as_per_document", "tax_regime_chosen",
//             "net_amount_payable", "days_present", "overtime_hours"
//         ];

//         const bankStatementFields = [
//             "account_holder_name", "account_number", "ifsc_code", "bank_name", "branch_address",
//             "statement_start_date", "statement_end_date", "opening_balance", "closing_balance",
//             "total_deposits", "total_withdrawals", "transaction_summary"
//         ];
        
//         let fieldsToRender = [];
//         if (identifiedType === 'Bank Statement') {
//             fieldsToRender = bankStatementFields.filter(key => fields[key] !== undefined);
//         } else {
//             // For other document types, primarily show tax-related fields plus common ones
//             fieldsToRender = Object.keys(fields).filter(key => 
//                 taxRelatedFields.includes(key) ||
//                 ["name_of_employee", "pan_of_employee", "financial_year", "assessment_year", "date_of_birth"].includes(key)
//             );
//         }

//         // Sort fields to render according to the predefined order for consistency
//         fieldsToRender.sort((a, b) => {
//             const indexA = Object.keys(fieldDefinitions).indexOf(a);
//             const indexB = Object.keys(fieldDefinitions).indexOf(b);
//             return indexA - indexB;
//         });


//         return (
//             <ul style={{ listStyleType: 'none', padding: 0 }}>
//                 {fieldsToRender.map(key => {
//                     const fieldDef = fieldDefinitions[key];
//                     let value = fields[key];

//                     if (!fieldDef || value === null || value === undefined || (typeof value === 'string' && value.toLowerCase() === 'null') || (typeof value === 'string' && value.trim() === '')) {
//                         return null; // Skip if no definition, null, undefined, "null", or empty string
//                     }

//                     // Handle date fields that might come as "0000-01-01"
//                     if (fieldDef.type === "date" && value === "0000-01-01") {
//                         value = "N/A";
//                     } else if (fieldDef.type === "currency" && typeof value === 'number') {
//                         value = formatCurrency(value);
//                     } else if (Array.isArray(value) && value.length === 0) {
//                         return null; // Skip empty arrays
//                     }

//                     // Special handling for transaction_summary
//                     if (key === "transaction_summary" && Array.isArray(value)) {
//                         return (
//                             <li key={key}>
//                                 <strong>{fieldDef.label}:</strong>
//                                 <pre className="extracted-fields-preview mt-2">
//                                     {value.length > 0 ? JSON.stringify(value.map(tx => ({
//                                         date: tx.date !== "0000-01-01" ? tx.date : "N/A",
//                                         description: tx.description,
//                                         amount: formatCurrency(tx.amount)
//                                     })), null, 2) : 'No transactions found.'}
//                                 </pre>
//                             </li>
//                         );
//                     }
                    
//                     return (
//                         <li key={key}>
//                             <strong>{fieldDef.label}:</strong> {value.toString()}
//                         </li>
//                     );
//                 })}
//             </ul>
//         );
//     };

//     useEffect(() => {
//         const fetchHistory = async () => {
//             setLoading(true);
//             setMessage('Fetching your tax history...');
//             setMessageType('info');
//             const jwt_token = Cookies.get('jwt_token');

//             try {
//                 const response = await axios.get('http://127.0.0.1:5000/api/tax-records', {
//                     headers: {
//                         'Authorization': `Bearer ${jwt_token}`
//                     },
//                     withCredentials: true,
//                 });

//                 if (response.data.status === 'success') {
//                     setHistory(response.data.history);
//                     setMessage('Tax history loaded successfully.');
//                     setMessageType('success');
//                 } else {
//                     setMessage(response.data.message || 'Failed to fetch tax history.');
//                     setMessageType('error');
//                 }
//             } catch (error) {
//                 console.error('Error fetching tax history:', error);
//                 setMessage(error.response?.data?.message || 'An error occurred while fetching history.');
//                 setMessageType('error');
//             } finally {
//                 setLoading(false);
//             }
//         };

//         fetchHistory();
//     }, []);

//     const handleViewDetails = (record) => {
//         setSelectedRecord(record);
//         window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top to view details
//     };

//     const handleBackToList = () => {
//         setSelectedRecord(null);
//         // setSuggestionsResult(null); // No need to clear global suggestions state in TaxHistory as it's part of selectedRecord now
//     };

//     const handleGetSuggestionsFromHistory = async (record) => {
//         setIsGeneratingSuggestions(true);
//         setMessage('Generating AI suggestions and ML predictions for this record...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const response = await axios.post('http://127.0.0.1:5000/api/get_suggestions', 
//                 { record_id: record._id }, 
//                 {
//                     headers: {
//                         'Content-Type': 'application/json',
//                         'Authorization': `Bearer ${jwt_token}`
//                     },
//                     withCredentials: true,
//                 }
//             );

//             if (response.data.status === 'success') {
//                 setMessage('Suggestions and predictions generated!');
//                 setMessageType('success');
//                 // Update the selected record with new suggestions directly
//                 setSelectedRecord(prev => ({
//                     ...prev,
//                     suggestions_from_gemini: response.data.suggestions_from_gemini,
//                     gemini_regime_analysis: response.data.gemini_regime_analysis,
//                     ml_prediction_summary: response.data.ml_prediction_summary,
//                 }));
//             } else {
//                 setMessage(response.data.message || 'Failed to get suggestions.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Error getting suggestions from history:', error);
//             setMessage(error.response?.data?.message || 'An error occurred while fetching suggestions.');
//             setMessageType('error');
//         } finally {
//             setIsGeneratingSuggestions(false);
//         }
//     };

//     const handleGenerateITRFromHistory = async (record) => {
//         setIsGeneratingITR(true);
//         setMessage('Generating ITR form...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const response = await axios.get(`http://127.0.0.1:5000/api/generate-itr/${record._id}`, {
//                 headers: {
//                     'Authorization': `Bearer ${jwt_token}`
//                 },
//                 responseType: 'blob', // Important: receive the response as a Blob
//                 withCredentials: true,
//             });

//             if (response.status === 200) {
//                 const blob = new Blob([response.data], { type: 'application/pdf' });
//                 const url = window.URL.createObjectURL(blob);
//                 const contentDisposition = response.headers['content-disposition'];
//                 let filename = 'ITR_Form.pdf';
//                 if (contentDisposition) {
//                     const filenameMatch = contentDisposition.match(/filename="(.+)"/);
//                     if (filenameMatch && filenameMatch[1]) {
//                         filename = filenameMatch[1];
//                     }
//                 }
//                 const link = document.createElement('a');
//                 link.href = url;
//                 link.setAttribute('download', filename);
//                 document.body.appendChild(link);
//                 link.click();
//                 link.parentNode.removeChild(link);
//                 window.URL.revokeObjectURL(url);

//                 setMessage('ITR form generated and downloaded!');
//                 setMessageType('success');
//             } else {
//                  // Try to read error message from non-PDF response
//                 const errorData = await new Response(response.data).text();
//                 setMessage(errorData || 'Failed to generate ITR form.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Error generating ITR from history:', error);
//             let errorMessage = 'An error occurred while generating ITR.';
//             if (axios.isAxiosError(error) && error.response && error.response.data) {
//                 const reader = new FileReader();
//                 reader.onload = function() {
//                     try {
//                         const errorJson = JSON.parse(reader.result);
//                         errorMessage = errorJson.message || errorMessage;
//                     } catch (e) {
//                         // Not a JSON error, use generic message
//                         errorMessage = reader.result || error.response.statusText;
//                     } finally {
//                         setMessage(errorMessage);
//                         setMessageType('error');
//                     }
//                 };
//                 reader.readAsText(error.response.data);
//             } else {
//                 setMessage(errorMessage);
//                 setMessageType('error');
//             }
//         } finally {
//             setIsGeneratingITR(false);
//         }
//     };


//     return (
//         <div className="p-6 max-w-7xl mx-auto bg-gray-100 min-h-screen font-sans">
//             <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Your Tax History</h2>

//             {message && (
//                 <div className={`message ${messageType}`}>
//                     {messageType === 'info' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {messageType === 'success' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {messageType === 'error' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {message}
//                 </div>
//             )}

//             {selectedRecord ? (
//                 // Detailed View of a Single Record
//                 <div className="container-card">
//                     <button onClick={handleBackToList} className="btn-secondary mb-4 flex items-center">
//                         <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
//                         Back to History List
//                     </button>
//                     <h3 className="text-xl font-semibold text-gray-700 mb-4">Details for Record: {selectedRecord._id}</h3>
                    
//                     {selectedRecord.document_processing_summary && selectedRecord.document_processing_summary.length > 0 && (
//                         <div className="section-box">
//                             <h4 className="text-lg font-medium text-gray-700 mb-2">Processed Documents Summary:</h4>
//                             {selectedRecord.document_processing_summary.map((doc, index) => (
//                                 <div key={index} className={`mb-4 p-3 rounded-md ${doc.status === 'success' ? 'bg-green-50 text-green-800' : doc.status === 'warning' ? 'bg-yellow-50 text-yellow-800' : 'bg-red-50 text-red-800'}`}>
//                                     <p><strong>File:</strong> {doc.filename} {doc.stored_path && <a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">(View Stored Document)</a>}</p>
//                                     <p><strong>Status:</strong> <span className="uppercase">{doc.status}</span></p>
//                                     <p><strong>Identified Type:</strong> {doc.identified_type}</p>
//                                     <p><strong>Message:</strong> {doc.message}</p>
//                                     {/* Extracted fields for each document, using the improved renderExtractedFields */}
//                                     {doc.extracted_fields && Object.keys(doc.extracted_fields).length > 0 && (
//                                         <p><strong>Extracted Fields:</strong>
//                                             <pre className="extracted-fields-preview">
//                                             {renderExtractedFields(doc.extracted_fields, doc.identified_type)}
//                                             </pre>
//                                         </p>
//                                     )}
//                                 </div>
//                             ))}
//                         </div>
//                     )}

//                     {selectedRecord.aggregated_financial_data && (
//                         <div className="section-box">
//                             <h3 className="text-lg font-medium text-gray-700 mb-2">Aggregated Financial Data Summary</h3>
                            
//                             {/* Conditional rendering for Bank Statement vs. Tax Data in aggregated summary */}
//                             {selectedRecord.aggregated_financial_data.identified_type === 'Bank Statement' || 
//                              (selectedRecord.aggregated_financial_data.account_number && selectedRecord.aggregated_financial_data.account_number !== 'null') ? (
//                                 <div className="income-details-section"> {/* Re-using for consistent styling */}
//                                     <h5>Bank Account Details</h5>
//                                     <p><strong>Account Holder Name:</strong> {selectedRecord.aggregated_financial_data.account_holder_name || 'N/A'}</p>
//                                     <p><strong>Account Number:</strong> {selectedRecord.aggregated_financial_data.account_number || 'N/A'}</p>
//                                     <p><strong>Bank Name:</strong> {selectedRecord.aggregated_financial_data.bank_name || 'N/A'}</p>
//                                     <p><strong>Branch Address:</strong> {selectedRecord.aggregated_financial_data.branch_address || 'N/A'}</p>
//                                     <p><strong>Statement Period:</strong> {selectedRecord.aggregated_financial_data.statement_start_date || 'N/A'} to {selectedRecord.aggregated_financial_data.statement_end_date || 'N/A'}</p>
//                                     <p><strong>Opening Balance:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.opening_balance)}</p>
//                                     <p><strong>Closing Balance:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.closing_balance)}</p>
//                                     <p><strong>Total Deposits:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deposits)}</p>
//                                     <p><strong>Total Withdrawals:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_withdrawals)}</p>
//                                     {selectedRecord.aggregated_financial_data.transaction_summary && selectedRecord.aggregated_financial_data.transaction_summary.length > 0 && (
//                                         <p>
//                                             <strong>Key Transactions:</strong> 
//                                             <pre className="extracted-fields-preview mt-2">
//                                                 {JSON.stringify(selectedRecord.aggregated_financial_data.transaction_summary.slice(0, 5).map(tx => ({ // Show first 5 transactions
//                                                     date: tx.date !== "0000-01-01" ? tx.date : "N/A",
//                                                     description: tx.description,
//                                                     amount: formatCurrency(tx.amount)
//                                                 })), null, 2)}
//                                                 {selectedRecord.aggregated_financial_data.transaction_summary.length > 5 ? '\n...' : ''}
//                                             </pre>
//                                         </p>
//                                     )}
//                                 </div>
//                             ) : (
//                                 <>
//                                     <div className="income-details-section">
//                                         <h5>Income Details</h5>
//                                         <p><strong>Financial Year:</strong> {selectedRecord.aggregated_financial_data.financial_year || 'N/A'}</p>
//                                         <p><strong>Assessment Year:</strong> {selectedRecord.aggregated_financial_data.assessment_year || 'N/A'}</p>
//                                         <p><strong>Name:</strong> {selectedRecord.aggregated_financial_data.name_of_employee || 'N/A'}</p>
//                                         <p><strong>PAN:</strong> {selectedRecord.aggregated_financial_data.pan_of_employee || 'N/A'}</p>
//                                         <p><strong>Date of Birth:</strong> {selectedRecord.aggregated_financial_data.date_of_birth !== "0000-01-01" ? selectedRecord.aggregated_financial_data.date_of_birth : 'N/A'}</p>
//                                         <p><strong>Age:</strong> {selectedRecord.aggregated_financial_data.Age || 'N/A'}</p>
//                                         <p><strong>Gross Annual Salary:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.gross_salary_total)}</p>
//                                         <p><strong>Exempt Allowances:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_exempt_allowances)}</p>
//                                         <p><strong>Income from House Property:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_house_property)}</p>
//                                         <p><strong>Income from Other Sources:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_other_sources)}</p>
//                                         <p><strong>Long Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_long_term)}</p>
//                                         <p><strong>Short Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_short_term)}</p>
//                                         <p><strong>Total Gross Income (Aggregated):</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.calculated_gross_income)}</p>
//                                     </div>
//                                     <div className="deductions-section">
//                                         <h5>Deductions Claimed</h5>
//                                         {selectedRecord.aggregated_financial_data.standard_deduction > 0 && 
//                                             <p><strong>Standard Deduction:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.standard_deduction)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.professional_tax > 0 &&
//                                             <p><strong>Professional Tax:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.professional_tax)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b !== 0 &&
//                                             <p><strong>Interest on Home Loan (Section 24(b)):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80C > 0 &&
//                                             <p><strong>Section 80C Investments:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80C)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80CCD1B > 0 &&
//                                             <p><strong>Section 80CCD1B:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80CCD1B)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80D > 0 &&
//                                             <p><strong>Section 80D (Health Insurance):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80D)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80G > 0 &&
//                                             <p><strong>Section 80G:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80G)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80TTA > 0 &&
//                                             <p><strong>Section 80TTA:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTA)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80TTB > 0 &&
//                                             <p><strong>Section 80TTB:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTB)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80E > 0 &&
//                                             <p><strong>Section 80E (Education Loan Interest):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80E)}</p>
//                                         }
//                                         <p><strong>Total Deductions (Aggregated for Display):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deductions)}</p>
//                                     </div>
//                                     <div className="taxation-summary-section">
//                                         <h5>Tax Payments & Regime</h5>
//                                         <p><strong>Total TDS Credit:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.total_tds_credit)}</p>
//                                         <p><strong>Advance Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.advance_tax)}</p>
//                                         <p><strong>Self-Assessment Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.self_assessment_tax)}</p>
//                                         <p><strong>Tax Regime Chosen (from docs):</strong> <span className="highlight-regime">{selectedRecord.aggregated_financial_data.tax_regime_chosen || 'Not Specified'}</span></p>
//                                     </div>
//                                 </>
//                             )}
//                         </div>
//                         <div className="final-tax-computation-section section-box">
//                             <h4 className="section-title">Final Tax Computation Summary (Rule-Based)</h4>
//                             {selectedRecord.final_tax_computation_summary.calculation_details && selectedRecord.final_tax_computation_summary.calculation_details.length > 0 && (
//                                 <div className="computation-details-list">
//                                     <h5>Calculation Steps:</h5>
//                                     <ul style={{ listStyleType: 'decimal', marginLeft: '20px', paddingLeft: '0' }}>
//                                         {selectedRecord.final_tax_computation_summary.calculation_details.map((detail, idx) => (
//                                             <li key={idx} className="computation-detail-item">{detail}</li>
//                                         ))}
//                                     </ul>
//                                 </div>
//                             )}
//                             <div className="final-amount-box">
//                                 <p><strong>Computed Taxable Income:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.computed_taxable_income)}</p>
//                                 <p><strong>Estimated Tax Payable:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.estimated_tax_payable)}</p>
//                                 <p><strong>Tax Regime Considered for Rule-Based Calculation:</strong> <span className="highlight-regime">{selectedRecord.final_tax_computation_summary.regime_considered || 'N/A'}</span></p>
//                                 {selectedRecord.final_tax_computation_summary.predicted_refund_due > 0 && (
//                                     <p className="refund-amount">
//                                         <strong>Refund Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_refund_due)}
//                                     </p>
//                                 )}
//                                 {selectedRecord.final_tax_computation_summary.predicted_additional_due > 0 && (
//                                     <p className="tax-due-amount">
//                                         <strong>Additional Tax Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_additional_due)}
//                                     </p>
//                                 )}
//                             </div>
//                             {selectedRecord.final_tax_computation_summary.notes && selectedRecord.final_tax_computation_summary.notes.length > 0 && (
//                                 <p className="computation-notes">
//                                     <strong>Note:</strong> {Array.isArray(selectedRecord.final_tax_computation_summary.notes) ? selectedRecord.final_tax_computation_summary.notes.join(', ') : selectedRecord.final_tax_computation_summary.notes}
//                                 </p>
//                             )}
//                         </div>
//                     )}

//                     <div className="action-buttons-container" style={{ justifyContent: 'center' }}>
//                         <button
//                             onClick={() => handleGetSuggestionsFromHistory(selectedRecord)}
//                             disabled={isGeneratingSuggestions}
//                             className={`tax-uploader-button get-suggestions-button ${isGeneratingSuggestions ? 'opacity-75 cursor-not-allowed' : ''}`}
//                         >
//                             {isGeneratingSuggestions ? (
//                                 <>
//                                     <div className="tax-uploader-spinner"></div>
//                                     Generating AI Suggestions...
//                                 </>
//                             ) : (
//                                 'Re-Generate AI Suggestions & ML Predictions'
//                             )}
//                         </button>
//                         <button
//                             onClick={() => handleGenerateITRFromHistory(selectedRecord)}
//                             disabled={isGeneratingITR}
//                             className={`tax-uploader-button generate-itr-button ${isGeneratingITR ? 'opacity-75 cursor-not-allowed' : ''}`}
//                         >
//                             {isGeneratingITR ? (
//                                 <>
//                                     <div className="tax-uploader-spinner"></div>
//                                     Generating ITR Form...
//                                 </>
//                             ) : (
//                                 'Generate Dummy ITR Form (PDF)'
//                             )}
//                         </button>
//                     </div>

//                     {/* Display Suggestions from Gemini and ML Predictions */}
//                     {(selectedRecord.suggestions_from_gemini || selectedRecord.gemini_regime_analysis || selectedRecord.ml_prediction_summary) && (
//                         <div className="suggestions-output tax-summary-output">
//                             <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>AI Recommendations & Predictions</h3>
//                             <div className="section-box">
//                                 {selectedRecord.suggestions_from_gemini && selectedRecord.suggestions_from_gemini.length > 0 ? (
//                                     <>
//                                         <h4>Based on Gemini AI:</h4>
//                                         <ul className="suggestions-list">
//                                             {selectedRecord.suggestions_from_gemini.map((suggestion, index) => (
//                                                 <li key={index}>{suggestion}</li>
//                                             ))}
//                                         </ul>
//                                     </>
//                                 ) : (
//                                     <p>Gemini did not provide specific tax-saving suggestions for this record, but your tax situation seems optimized.</p>
//                                 )}
//                                 {selectedRecord.gemini_regime_analysis && (
//                                     <div className="gemini-regime-analysis">
//                                         <h4>Gemini's Regime Analysis:</h4>
//                                         <p>{selectedRecord.gemini_regime_analysis}</p>
//                                     </div>
//                                 )}
//                                 {selectedRecord.ml_prediction_summary && (
//                                     <>
//                                         <h4>ML Model Prediction:</h4>
//                                         {selectedRecord.ml_prediction_summary.predicted_tax_regime && (
//                                             <p><strong>Predicted Tax Regime:</strong> {selectedRecord.ml_prediction_summary.predicted_tax_regime}</p>
//                                         )}
//                                         <p><strong>Predicted Tax Liability:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_tax_liability)}</p>
//                                         <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_refund_due)}</p>
//                                         <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_additional_due)}</p>
//                                         {selectedRecord.ml_prediction_summary.notes && (
//                                             <p><strong>Notes:</strong> {selectedRecord.ml_prediction_summary.notes}</p>
//                                         )}
//                                     </>
//                                 )}
//                             </div>
//                         </div>
//                     )}

//                 </div>
//             ) : (
//                 // List View of Records
//                 <div className="container-card">
//                     <h3 className="text-xl font-semibold text-gray-700 mb-4">Your Processed Tax Records</h3>
//                     {loading ? (
//                         <p className="text-center text-gray-600 flex items-center justify-center">
//                             <span className="loading-spinner mr-2 border-indigo-500 border-t-indigo-500"></span>
//                             Loading tax records...
//                         </p>
//                     ) : history.length === 0 ? (
//                         <p className="text-center text-gray-600">No tax records found. Upload documents to get started!</p>
//                     ) : (
//                         <div className="overflow-x-auto">
//                             <table className="min-w-full bg-white rounded-lg shadow overflow-hidden history-table">
//                                 <thead className="bg-gray-200">
//                                     <tr>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Record ID</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Document Type</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Financial Year</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Last Processed</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Aggregated Gross Income</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Estimated Tax Payable</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Refund / Due</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
//                                     </tr>
//                                 </thead>
//                                 <tbody className="divide-y divide-gray-200">
//                                     {history.map((record) => (
//                                         <tr key={record._id} className="hover:bg-gray-50">
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record._id.substring(0, 8)}...</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record.document_processing_summary?.[0]?.identified_type || 'N/A'}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record.aggregated_financial_data.financial_year || 'N/A'}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{new Date(record.timestamp).toLocaleString()}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : formatCurrency(record.aggregated_financial_data.total_gross_income)}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : formatCurrency(record.final_tax_computation_summary.estimated_tax_payable)}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : (
//                                                     record.final_tax_computation_summary.predicted_refund_due > 0 ? (
//                                                         <span className="refund-amount">{formatCurrency(record.final_tax_computation_summary.predicted_refund_due)} Refund</span>
//                                                     ) : record.final_tax_computation_summary.predicted_additional_due > 0 ? (
//                                                         <span className="tax-due-amount">{formatCurrency(record.final_tax_computation_summary.predicted_additional_due)} Due</span>
//                                                     ) : (
//                                                         'N/A'
//                                                     )
//                                                 )}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm">
//                                                 <button
//                                                     onClick={() => handleViewDetails(record)}
//                                                     className="view-details-btn"
//                                                 >
//                                                     View Details
//                                                 </button>
//                                             </td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     )}
//                 </div>
//             )}
//         </div>
//     );
// };

// export default TaxHistory;










// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import Cookies from 'js-cookie';
// // Assuming index.css is in the same directory as TaxHistory. If not, you might need to adjust the path.
// import './index.css'; 

// const TaxHistory = () => {
//     const [history, setHistory] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [message, setMessage] = useState('');
//     const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
//     const [selectedRecord, setSelectedRecord] = useState(null); // To view full details of a record
//     const [isGeneratingITR, setIsGeneratingITR] = useState(false);
//     const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false); // Added for history re-generation

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

//     // Helper function to render extracted fields dynamically, similar to TaxUploader
//     const renderExtractedFields = (fields, identifiedType) => {
//         if (!fields) return null;

//         // Define a comprehensive list of all possible fields and their display names
//         const fieldDefinitions = {
//             // Personal & Employer Info
//             "name_of_employee": { label: "Name of Employee", type: "text" },
//             "pan_of_employee": { label: "PAN of Employee", type: "text" },
//             "date_of_birth": { label: "Date of Birth", type: "date" },
//             "gender": { label: "Gender", type: "text" },
//             "residential_status": { label: "Residential Status", type: "text" },
//             "employer_name": { label: "Employer Name", type: "text" },
//             "employer_address": { label: "Employer Address", type: "text" },
//             "pan_of_deductor": { label: "PAN of Deductor", type: "text" },
//             "tan_of_deductor": { label: "TAN of Deductor", type: "text" },
//             "designation_of_employee": { label: "Designation", type: "text" },
//             // Financial Years & Period
//             "financial_year": { label: "Financial Year", type: "text" },
//             "assessment_year": { label: "Assessment Year", type: "text" },
//             "period_from": { label: "Period From", type: "date" },
//             "period_to": { label: "Period To", type: "date" },
//             "statement_start_date": { label: "Statement Start Date", type: "date" },
//             "statement_end_date": { label: "Statement End Date", type: "date" },
//             // Income
//             "gross_salary_total": { label: "Gross Salary Total", type: "currency" },
//             "salary_as_per_sec_17_1": { label: "Salary U/S 17(1)", type: "currency" },
//             "value_of_perquisites_u_s_17_2": { label: "Perquisites U/S 17(2)", type: "currency" },
//             "profits_in_lieu_of_salary_u_s_17_3": { label: "Profits in Lieu of Salary U/S 17(3)", type: "currency" },
//             "basic_salary": { label: "Basic Salary", type: "currency" },
//             "hra_received": { label: "HRA Received", type: "currency" },
//             "conveyance_allowance": { label: "Conveyance Allowance", type: "currency" },
//             "transport_allowance": { label: "Transport Allowance", type: "currency" },
//             "overtime_pay": { label: "Overtime Pay", type: "currency" },
//             "total_exempt_allowances": { label: "Total Exempt Allowances", type: "currency" },
//             "income_from_house_property": { label: "Income from House Property", type: "currency" },
//             "income_from_other_sources": { label: "Income from Other Sources", type: "currency" },
//             "capital_gains_long_term": { label: "Long Term Capital Gains", type: "currency" },
//             "capital_gains_short_term": { label: "Short Term Capital Gains", type: "currency" },
//             "gross_total_income_as_per_document": { label: "Gross Total Income (Doc)", type: "currency" },
//             // Deductions
//             "professional_tax": { label: "Professional Tax", type: "currency" },
//             "interest_on_housing_loan_self_occupied": { label: "Interest on Home Loan (Self Occupied)", type: "currency" },
//             "deduction_80c": { label: "Deduction 80C", type: "currency" },
//             "deduction_80c_epf": { label: "Deduction 80C (EPF)", type: "currency" },
//             "deduction_80c_insurance_premium": { label: "Deduction 80C (Insurance Premium)", type: "currency" },
//             "deduction_80ccc": { label: "Deduction 80CCC", type: "currency" },
//             "deduction_80ccd": { label: "Deduction 80CCD", type: "currency" },
//             "deduction_80ccd1b": { label: "Deduction 80CCD(1B)", type: "currency" },
//             "deduction_80d": { label: "Deduction 80D", type: "currency" },
//             "deduction_80g": { label: "Deduction 80G", type: "currency" },
//             "deduction_80tta": { label: "Deduction 80TTA", type: "currency" },
//             "deduction_80ttb": { label: "Deduction 80TTB", type: "currency" },
//             "deduction_80e": { label: "Deduction 80E", type: "currency" },
//             "total_deductions_chapter_via": { label: "Total Chapter VI-A Deductions", type: "currency" },
//             "aggregate_of_deductions_from_salary": { label: "Aggregate Deductions from Salary", type: "currency" },
//             "epf_contribution": { label: "EPF Contribution", type: "currency" },
//             "esi_contribution": { label: "ESI Contribution", type: "currency" },
//             // Tax Paid
//             "total_tds": { label: "Total TDS", type: "currency" },
//             "total_tds_deducted_summary": { label: "Total TDS Deducted (Summary)", type: "currency" },
//             "total_tds_deposited_summary": { label: "Total TDS Deposited (Summary)", type: "currency" },
//             "quarter_1_receipt_number": { label: "Q1 Receipt Number", type: "text" },
//             "quarter_1_tds_deducted": { label: "Q1 TDS Deducted", type: "currency" },
//             "quarter_1_tds_deposited": { label: "Q1 TDS Deposited", type: "currency" },
//             "advance_tax": { label: "Advance Tax", type: "currency" },
//             "self_assessment_tax": { label: "Self-Assessment Tax", type: "currency" },
//             // Other Tax Info
//             "taxable_income_as_per_document": { label: "Taxable Income (Doc)", type: "currency" },
//             "tax_payable_as_per_document": { label: "Tax Payable (Doc)", type: "currency" },
//             "refund_status_as_per_document": { label: "Refund Status (Doc)", type: "text" },
//             "tax_regime_chosen": { label: "Tax Regime Chosen", type: "text" },
//             "net_amount_payable": { label: "Net Amount Payable", type: "currency" },
//             "days_present": { label: "Days Present", type: "number" },
//             "overtime_hours": { label: "Overtime Hours", type: "number" },
//             // Bank Statement Details
//             "account_holder_name": { label: "Account Holder Name", type: "text" },
//             "account_number": { label: "Account Number", type: "text" },
//             "ifsc_code": { label: "IFSC Code", type: "text" },
//             "bank_name": { label: "Bank Name", type: "text" },
//             "branch_address": { label: "Branch Address", type: "text" },
//             "opening_balance": { label: "Opening Balance", type: "currency" },
//             "closing_balance": { label: "Closing Balance", type: "currency" },
//             "total_deposits": { label: "Total Deposits", type: "currency" },
//             "total_withdrawals": { label: "Total Withdrawals", type: "currency" },
//             "transaction_summary": { label: "Transaction Summary", type: "array_of_objects" }
//         };

//         const taxRelatedFields = [
//             "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
//             "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
//             "total_exempt_allowances", "income_from_house_property", "income_from_other_sources", "capital_gains_long_term",
//             "capital_gains_short_term", "gross_total_income_as_per_document", "professional_tax", "interest_on_housing_loan_self_occupied",
//             "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
//             "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
//             "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
//             "epf_contribution", "esi_contribution", "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
//             "quarter_1_receipt_number", "quarter_1_tds_deducted", "quarter_1_tds_deposited", "advance_tax", "self_assessment_tax",
//             "taxable_income_as_per_document", "tax_payable_as_per_document", "refund_status_as_per_document", "tax_regime_chosen",
//             "net_amount_payable", "days_present", "overtime_hours"
//         ];

//         const bankStatementFields = [
//             "account_holder_name", "account_number", "ifsc_code", "bank_name", "branch_address",
//             "statement_start_date", "statement_end_date", "opening_balance", "closing_balance",
//             "total_deposits", "total_withdrawals", "transaction_summary"
//         ];
        
//         let fieldsToRender = [];
//         if (identifiedType === 'Bank Statement') {
//             fieldsToRender = bankStatementFields.filter(key => fields[key] !== undefined);
//         } else {
//             // For other document types, primarily show tax-related fields plus common ones
//             fieldsToRender = Object.keys(fields).filter(key => 
//                 taxRelatedFields.includes(key) ||
//                 ["name_of_employee", "pan_of_employee", "financial_year", "assessment_year", "date_of_birth"].includes(key)
//             );
//         }

//         // Sort fields to render according to the predefined order for consistency
//         fieldsToRender.sort((a, b) => {
//             const indexA = Object.keys(fieldDefinitions).indexOf(a);
//             const indexB = Object.keys(fieldDefinitions).indexOf(b);
//             return indexA - indexB;
//         });


//         return (
//             <ul style={{ listStyleType: 'none', padding: 0 }}>
//                 {fieldsToRender.map(key => {
//                     const fieldDef = fieldDefinitions[key];
//                     let value = fields[key];

//                     if (!fieldDef || value === null || value === undefined || (typeof value === 'string' && value.toLowerCase() === 'null') || (typeof value === 'string' && value.trim() === '')) {
//                         return null; // Skip if no definition, null, undefined, "null", or empty string
//                     }

//                     // Handle date fields that might come as "0000-01-01"
//                     if (fieldDef.type === "date" && value === "0000-01-01") {
//                         value = "N/A";
//                     } else if (fieldDef.type === "currency" && typeof value === 'number') {
//                         value = formatCurrency(value);
//                     } else if (Array.isArray(value) && value.length === 0) {
//                         return null; // Skip empty arrays
//                     }

//                     // Special handling for transaction_summary
//                     if (key === "transaction_summary" && Array.isArray(value)) {
//                         return (
//                             <li key={key}>
//                                 <strong>{fieldDef.label}:</strong>
//                                 <pre className="extracted-fields-preview mt-2">
//                                     {value.length > 0 ? JSON.stringify(value.map(tx => ({
//                                         date: tx.date !== "0000-01-01" ? tx.date : "N/A",
//                                         description: tx.description,
//                                         amount: formatCurrency(tx.amount)
//                                     })), null, 2) : 'No transactions found.'}
//                                 </pre>
//                             </li>
//                         );
//                     }
                    
//                     return (
//                         <li key={key}>
//                             <strong>{fieldDef.label}:</strong> {value.toString()}
//                         </li>
//                     );
//                 })}
//             </ul>
//         );
//     };

//     useEffect(() => {
//         const fetchHistory = async () => {
//             setLoading(true);
//             setMessage('Fetching your tax history...');
//             setMessageType('info');
//             const jwt_token = Cookies.get('jwt_token');

//             try {
//                 // Corrected endpoint to match backend (used in app1.py: /api/tax_history)
//                 const response = await axios.get('http://127.0.0.1:5000/api/tax_history', {
//                     headers: {
//                         'Authorization': `Bearer ${jwt_token}`
//                     },
//                     withCredentials: true,
//                 });

//                 if (response.data.status === 'success') {
//                     setHistory(response.data.history);
//                     setMessage('Tax history loaded successfully.');
//                     setMessageType('success');
//                 } else {
//                     setMessage(response.data.message || 'Failed to fetch tax history.');
//                     setMessageType('error');
//                 }
//             } catch (error) {
//                 console.error('Error fetching tax history:', error);
//                 setMessage(error.response?.data?.message || 'An error occurred while fetching history.');
//                 setMessageType('error');
//             } finally {
//                 setLoading(false);
//             }
//         };

//         fetchHistory();
//     }, []);

//     const handleViewDetails = (record) => {
//         setSelectedRecord(record);
//         window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top to view details
//     };

//     const handleBackToList = () => {
//         setSelectedRecord(null);
//     };

//     const handleGetSuggestionsFromHistory = async (record) => {
//         setIsGeneratingSuggestions(true);
//         setMessage('Generating AI suggestions and ML predictions for this record...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const response = await axios.post('http://127.0.0.1:5000/api/get_suggestions', 
//                 { record_id: record._id }, 
//                 {
//                     headers: {
//                         'Content-Type': 'application/json',
//                         'Authorization': `Bearer ${jwt_token}`
//                     },
//                     withCredentials: true,
//                 }
//             );

//             if (response.data.status === 'success') {
//                 setMessage('Suggestions and predictions generated!');
//                 setMessageType('success');
//                 // Update the selected record with new suggestions directly
//                 setSelectedRecord(prev => ({
//                     ...prev,
//                     suggestions_from_gemini: response.data.suggestions_from_gemini,
//                     gemini_regime_analysis: response.data.gemini_regime_analysis,
//                     ml_prediction_summary: response.data.ml_prediction_summary,
//                 }));
//             } else {
//                 setMessage(response.data.message || 'Failed to get suggestions.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Error getting suggestions from history:', error);
//             setMessage(error.response?.data?.message || 'An error occurred while fetching suggestions.');
//             setMessageType('error');
//         } finally {
//             setIsGeneratingSuggestions(false);
//         }
//     };

//     const handleGenerateITRFromHistory = async (record) => {
//         setIsGeneratingITR(true);
//         setMessage('Generating ITR form...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             // Corrected endpoint to match backend (used in app1.py: /api/generate-itr/<record_id>)
//             const response = await axios.get(`http://127.0.0.1:5000/api/generate-itr/${record._id}`, {
//                 headers: {
//                     'Authorization': `Bearer ${jwt_token}`
//                 },
//                 responseType: 'blob', // Important: receive the response as a Blob
//                 withCredentials: true,
//             });

//             if (response.status === 200) {
//                 const blob = new Blob([response.data], { type: 'application/pdf' });
//                 const url = window.URL.createObjectURL(blob);
//                 const contentDisposition = response.headers['content-disposition'];
//                 let filename = 'ITR_Form.pdf';
//                 if (contentDisposition) {
//                     const filenameMatch = contentDisposition.match(/filename="(.+)"/);
//                     if (filenameMatch && filenameMatch[1]) {
//                         filename = filenameMatch[1];
//                     }
//                 }
//                 const link = document.createElement('a');
//                 link.href = url;
//                 link.setAttribute('download', filename);
//                 document.body.appendChild(link);
//                 link.click();
//                 link.parentNode.removeChild(link);
//                 window.URL.revokeObjectURL(url);

//                 setMessage('ITR form generated and downloaded!');
//                 setMessageType('success');
//             } else {
//                  // Try to read error message from non-PDF response
//                 const errorData = await new Response(response.data).text();
//                 setMessage(errorData || 'Failed to generate ITR form.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Error generating ITR from history:', error);
//             let errorMessage = 'An error occurred while generating ITR.';
//             if (axios.isAxiosError(error) && error.response && error.response.data) {
//                 const reader = new FileReader();
//                 reader.onload = function() {
//                     try {
//                         const errorJson = JSON.parse(reader.result);
//                         errorMessage = errorJson.message || errorMessage;
//                     } catch (e) {
//                         // Not a JSON error, use generic message
//                         errorMessage = reader.result || error.response.statusText;
//                     } finally {
//                         setMessage(errorMessage);
//                         setMessageType('error');
//                     }
//                 };
//                 reader.readAsText(error.response.data);
//             } else {
//                 setMessage(errorMessage);
//                 setMessageType('error');
//             }
//         } finally {
//             setIsGeneratingITR(false);
//         }
//     };


//     return (
//         <div className="p-6 max-w-7xl mx-auto bg-gray-100 min-h-screen font-sans">
//             <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Your Tax History</h2>

//             {message && (
//                 <div className={`message ${messageType}`}>
//                     {messageType === 'info' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {messageType === 'success' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {messageType === 'error' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {message}
//                 </div>
//             )}

//             {selectedRecord ? (
//                 // Detailed View of a Single Record
//                 <div className="container-card">
//                     <button onClick={handleBackToList} className="btn-secondary mb-4 flex items-center">
//                         <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
//                         Back to History List
//                     </button>
//                     <h3 className="text-xl font-semibold text-gray-700 mb-4">Details for Record: {selectedRecord._id}</h3>
                    
//                     {selectedRecord.document_processing_summary && selectedRecord.document_processing_summary.length > 0 && (
//                         <div className="section-box">
//                             <h4 className="text-lg font-medium text-gray-700 mb-2">Processed Documents Summary:</h4>
//                             {selectedRecord.document_processing_summary.map((doc, index) => (
//                                 <div key={index} className={`mb-4 p-3 rounded-md ${doc.status === 'success' ? 'bg-green-50 text-green-800' : doc.status === 'warning' ? 'bg-yellow-50 text-yellow-800' : 'bg-red-50 text-red-800'}`}>
//                                     <p><strong>File:</strong> {doc.filename} {doc.stored_path && <a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">(View Stored Document)</a>}</p>
//                                     <p><strong>Status:</strong> <span className="uppercase">{doc.status}</span></p>
//                                     <p><strong>Identified Type:</strong> {doc.identified_type}</p>
//                                     <p><strong>Message:</strong> {doc.message}</p>
//                                     {/* Extracted fields for each document, using the improved renderExtractedFields */}
//                                     {doc.extracted_fields && Object.keys(doc.extracted_fields).length > 0 && (
//                                         <p><strong>Extracted Fields:</strong>
//                                             <pre className="extracted-fields-preview">
//                                             {renderExtractedFields(doc.extracted_fields, doc.identified_type)}
//                                             </pre>
//                                         </p>
//                                     )}
//                                 </div>
//                             ))}
//                         </div>
//                     )}

//                     {selectedRecord.aggregated_financial_data && (
//                         <div className="section-box">
//                             <h3 className="text-lg font-medium text-gray-700 mb-2">Aggregated Financial Data Summary</h3>
                            
//                             {/* Conditional rendering for Bank Statement vs. Tax Data in aggregated summary */}
//                             {selectedRecord.aggregated_financial_data.identified_type === 'Bank Statement' || 
//                              (selectedRecord.aggregated_financial_data.account_number && selectedRecord.aggregated_financial_data.account_number !== 'null') ? (
//                                 <div className="income-details-section"> {/* Re-using for consistent styling */}
//                                     <h5>Bank Account Details</h5>
//                                     <p><strong>Account Holder Name:</strong> {selectedRecord.aggregated_financial_data.account_holder_name || 'N/A'}</p>
//                                     <p><strong>Account Number:</strong> {selectedRecord.aggregated_financial_data.account_number || 'N/A'}</p>
//                                     <p><strong>Bank Name:</strong> {selectedRecord.aggregated_financial_data.bank_name || 'N/A'}</p>
//                                     <p><strong>Branch Address:</strong> {selectedRecord.aggregated_financial_data.branch_address || 'N/A'}</p>
//                                     <p><strong>Statement Period:</strong> {selectedRecord.aggregated_financial_data.statement_start_date || 'N/A'} to {selectedRecord.aggregated_financial_data.statement_end_date || 'N/A'}</p>
//                                     <p><strong>Opening Balance:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.opening_balance)}</p>
//                                     <p><strong>Closing Balance:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.closing_balance)}</p>
//                                     <p><strong>Total Deposits:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deposits)}</p>
//                                     <p><strong>Total Withdrawals:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_withdrawals)}</p>
//                                     {selectedRecord.aggregated_financial_data.transaction_summary && selectedRecord.aggregated_financial_data.transaction_summary.length > 0 && (
//                                         <p>
//                                             <strong>Key Transactions:</strong> 
//                                             <pre className="extracted-fields-preview mt-2">
//                                                 {JSON.stringify(selectedRecord.aggregated_financial_data.transaction_summary.slice(0, 5).map(tx => ({ // Show first 5 transactions
//                                                     date: tx.date !== "0000-01-01" ? tx.date : "N/A",
//                                                     description: tx.description,
//                                                     amount: formatCurrency(tx.amount)
//                                                 })), null, 2)}
//                                                 {selectedRecord.aggregated_financial_data.transaction_summary.length > 5 ? '\n...' : ''}
//                                             </pre>
//                                         </p>
//                                     )}
//                                 </div>
//                             ) : (
//                                 <>
//                                     <div className="income-details-section">
//                                         <h5>Income Details</h5>
//                                         <p><strong>Financial Year:</strong> {selectedRecord.aggregated_financial_data.financial_year || 'N/A'}</p>
//                                         <p><strong>Assessment Year:</strong> {selectedRecord.aggregated_financial_data.assessment_year || 'N/A'}</p>
//                                         <p><strong>Name:</strong> {selectedRecord.aggregated_financial_data.name_of_employee || 'N/A'}</p>
//                                         <p><strong>PAN:</strong> {selectedRecord.aggregated_financial_data.pan_of_employee || 'N/A'}</p>
//                                         <p><strong>Date of Birth:</strong> {selectedRecord.aggregated_financial_data.date_of_birth !== "0000-01-01" ? selectedRecord.aggregated_financial_data.date_of_birth : 'N/A'}</p>
//                                         <p><strong>Age:</strong> {selectedRecord.aggregated_financial_data.Age || 'N/A'}</p>
//                                         <p><strong>Gross Annual Salary:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.gross_salary_total)}</p>
//                                         <p><strong>Exempt Allowances:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_exempt_allowances)}</p>
//                                         <p><strong>Income from House Property:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_house_property)}</p>
//                                         <p><strong>Income from Other Sources:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_other_sources)}</p>
//                                         <p><strong>Long Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_long_term)}</p>
//                                         <p><strong>Short Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_short_term)}</p>
//                                         <p><strong>Total Gross Income (Aggregated):</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.calculated_gross_income)}</p>
//                                     </div>
//                                     <div className="deductions-section">
//                                         <h5>Deductions Claimed</h5>
//                                         {selectedRecord.aggregated_financial_data.standard_deduction > 0 && 
//                                             <p><strong>Standard Deduction:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.standard_deduction)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.professional_tax > 0 &&
//                                             <p><strong>Professional Tax:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.professional_tax)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b !== 0 &&
//                                             <p><strong>Interest on Home Loan (Section 24(b)):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80C > 0 &&
//                                             <p><strong>Section 80C Investments:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80C)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80CCD1B > 0 &&
//                                             <p><strong>Section 80CCD1B:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80CCD1B)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80D > 0 &&
//                                             <p><strong>Section 80D (Health Insurance):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80D)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80G > 0 &&
//                                             <p><strong>Section 80G:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80G)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80TTA > 0 &&
//                                             <p><strong>Section 80TTA:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTA)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80TTB > 0 &&
//                                             <p><strong>Section 80TTB:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTB)}</p>
//                                         }
//                                         {selectedRecord.aggregated_financial_data.deduction_80E > 0 &&
//                                             <p><strong>Section 80E (Education Loan Interest):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80E)}</p>
//                                         }
//                                         <p><strong>Total Deductions (Aggregated for Display):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deductions)}</p>
//                                     </div>
//                                     <div className="taxation-summary-section">
//                                         <h5>Tax Payments & Regime</h5>
//                                         <p><strong>Total TDS Credit:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.total_tds_credit)}</p>
//                                         <p><strong>Advance Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.advance_tax)}</p>
//                                         <p><strong>Self-Assessment Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.self_assessment_tax)}</p>
//                                         <p><strong>Tax Regime Chosen (from docs):</strong> <span className="highlight-regime">{selectedRecord.aggregated_financial_data.tax_regime_chosen || 'Not Specified'}</span></p>
//                                     </div>
//                                 </>
//                             )}
//                         </div>
//                         {/* FIX: Wrapped adjacent JSX elements in a fragment */}
//                         <> 
//                             <div className="final-tax-computation-section section-box">
//                                 <h4 className="section-title">Final Tax Computation Summary (Rule-Based)</h4>
//                                 {selectedRecord.final_tax_computation_summary.calculation_details && selectedRecord.final_tax_computation_summary.calculation_details.length > 0 && (
//                                     <div className="computation-details-list">
//                                         <h5>Calculation Steps:</h5>
//                                         <ul style={{ listStyleType: 'decimal', marginLeft: '20px', paddingLeft: '0' }}>
//                                             {selectedRecord.final_tax_computation_summary.calculation_details.map((detail, idx) => (
//                                                 <li key={idx} className="computation-detail-item">{detail}</li>
//                                             ))}
//                                         </ul>
//                                     </div>
//                                 )}
//                                 <div className="final-amount-box">
//                                     <p><strong>Computed Taxable Income:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.computed_taxable_income)}</p>
//                                     <p><strong>Estimated Tax Payable:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.estimated_tax_payable)}</p>
//                                     <p><strong>Tax Regime Considered for Rule-Based Calculation:</strong> <span className="highlight-regime">{selectedRecord.final_tax_computation_summary.regime_considered || 'N/A'}</span></p>
//                                     {selectedRecord.final_tax_computation_summary.predicted_refund_due > 0 && (
//                                         <p className="refund-amount">
//                                             <strong>Refund Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_refund_due)}
//                                         </p>
//                                     )}
//                                     {selectedRecord.final_tax_computation_summary.predicted_additional_due > 0 && (
//                                         <p className="tax-due-amount">
//                                             <strong>Additional Tax Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_additional_due)}
//                                         </p>
//                                     )}
//                                 </div>
//                                 {selectedRecord.final_tax_computation_summary.notes && selectedRecord.final_tax_computation_summary.notes.length > 0 && (
//                                     <p className="computation-notes">
//                                         <strong>Note:</strong> {Array.isArray(selectedRecord.final_tax_computation_summary.notes) ? selectedRecord.final_tax_computation_summary.notes.join(', ') : selectedRecord.final_tax_computation_summary.notes}
//                                     </p>
//                                 )}
//                             </div>
//                         </> {/* END FIX */}
//                     </div>

//                     <div className="action-buttons-container" style={{ justifyContent: 'center' }}>
//                         <button
//                             onClick={() => handleGetSuggestionsFromHistory(selectedRecord)}
//                             disabled={isGeneratingSuggestions}
//                             className={`tax-uploader-button get-suggestions-button ${isGeneratingSuggestions ? 'opacity-75 cursor-not-allowed' : ''}`}
//                         >
//                             {isGeneratingSuggestions ? (
//                                 <>
//                                     <div className="tax-uploader-spinner"></div>
//                                     Generating AI Suggestions...
//                                 </>
//                             ) : (
//                                 'Re-Generate AI Suggestions & ML Predictions'
//                             )}
//                         </button>
//                         <button
//                             onClick={() => handleGenerateITRFromHistory(selectedRecord)}
//                             disabled={isGeneratingITR}
//                             className={`tax-uploader-button generate-itr-button ${isGeneratingITR ? 'opacity-75 cursor-not-allowed' : ''}`}
//                         >
//                             {isGeneratingITR ? (
//                                 <>
//                                     <div className="tax-uploader-spinner"></div>
//                                     Generating ITR Form...
//                                 </>
//                             ) : (
//                                 'Generate Dummy ITR Form (PDF)'
//                             )}
//                         </button>
//                     </div>

//                     {/* Display Suggestions from Gemini and ML Predictions */}
//                     {(selectedRecord.suggestions_from_gemini || selectedRecord.gemini_regime_analysis || selectedRecord.ml_prediction_summary) && (
//                         <div className="suggestions-output tax-summary-output">
//                             <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>AI Recommendations & Predictions</h3>
//                             <div className="section-box">
//                                 {selectedRecord.suggestions_from_gemini && selectedRecord.suggestions_from_gemini.length > 0 ? (
//                                     <>
//                                         <h4>Based on Gemini AI:</h4>
//                                         <ul className="suggestions-list">
//                                             {selectedRecord.suggestions_from_gemini.map((suggestion, index) => (
//                                                 <li key={index}>{suggestion}</li>
//                                             ))}
//                                         </ul>
//                                     </>
//                                 ) : (
//                                     <p>Gemini did not provide specific tax-saving suggestions for this record, but your tax situation seems optimized.</p>
//                                 )}
//                                 {selectedRecord.gemini_regime_analysis && (
//                                     <div className="gemini-regime-analysis">
//                                         <h4>Gemini's Regime Analysis:</h4>
//                                         <p>{selectedRecord.gemini_regime_analysis}</p>
//                                     </div>
//                                 )}
//                                 {selectedRecord.ml_prediction_summary && (
//                                     <>
//                                         <h4>ML Model Prediction:</h4>
//                                         {selectedRecord.ml_prediction_summary.predicted_tax_regime && (
//                                             <p><strong>Predicted Tax Regime:</strong> {selectedRecord.ml_prediction_summary.predicted_tax_regime}</p>
//                                         )}
//                                         <p><strong>Predicted Tax Liability:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_tax_liability)}</p>
//                                         <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_refund_due)}</p>
//                                         <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_additional_due)}</p>
//                                         {selectedRecord.ml_prediction_summary.notes && (
//                                             <p><strong>Notes:</strong> {selectedRecord.ml_prediction_summary.notes}</p>
//                                         )}
//                                     </>
//                                 )}
//                             </div>
//                         </div>
//                     )}

//                 </div>
//             ) : (
//                 // List View of Records
//                 <div className="container-card">
//                     <h3 className="text-xl font-semibold text-gray-700 mb-4">Your Processed Tax Records</h3>
//                     {loading ? (
//                         <p className="text-center text-gray-600 flex items-center justify-center">
//                             <span className="loading-spinner mr-2 border-indigo-500 border-t-indigo-500"></span>
//                             Loading tax records...
//                         </p>
//                     ) : history.length === 0 ? (
//                         <p className="text-center text-gray-600">No tax records found. Upload documents to get started!</p>
//                     ) : (
//                         <div className="overflow-x-auto">
//                             <table className="min-w-full bg-white rounded-lg shadow overflow-hidden history-table">
//                                 <thead className="bg-gray-200">
//                                     <tr>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Record ID</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Document Type</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Financial Year</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Last Processed</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Aggregated Gross Income</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Estimated Tax Payable</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Refund / Due</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
//                                     </tr>
//                                 </thead>
//                                 <tbody className="divide-y divide-gray-200">
//                                     {history.map((record) => (
//                                         <tr key={record._id} className="hover:bg-gray-50">
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record._id.substring(0, 8)}...</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record.document_processing_summary?.[0]?.identified_type || 'N/A'}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record.aggregated_financial_data.financial_year || 'N/A'}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{new Date(record.timestamp).toLocaleString()}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : formatCurrency(record.aggregated_financial_data.total_gross_income)}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : formatCurrency(record.final_tax_computation_summary.estimated_tax_payable)}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : (
//                                                     record.final_tax_computation_summary.predicted_refund_due > 0 ? (
//                                                         <span className="refund-amount">{formatCurrency(record.final_tax_computation_summary.predicted_refund_due)} Refund</span>
//                                                     ) : record.final_tax_computation_summary.predicted_additional_due > 0 ? (
//                                                         <span className="tax-due-amount">{formatCurrency(record.final_tax_computation_summary.predicted_additional_due)} Due</span>
//                                                     ) : (
//                                                         'N/A'
//                                                     )
//                                                 )}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm">
//                                                 <button
//                                                     onClick={() => handleViewDetails(record)}
//                                                     className="view-details-btn"
//                                                 >
//                                                     View Details
//                                                 </button>
//                                             </td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     )}
//                 </div>
//             )}
//         </div>
//     );
// };

// export default TaxHistory;























// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import Cookies from 'js-cookie';
// // Assuming index.css is in the same directory as TaxHistory. If not, you might need to adjust the path.
// import './index.css'; 

// const TaxHistory = () => {
//     const [history, setHistory] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [message, setMessage] = useState('');
//     const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
//     const [selectedRecord, setSelectedRecord] = useState(null); // To view full details of a record
//     const [isGeneratingITR, setIsGeneratingITR] = useState(false);
//     const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false); // Added for history re-generation

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

//     // Helper function to render extracted fields dynamically, similar to TaxUploader
//     const renderExtractedFields = (fields, identifiedType) => {
//         if (!fields) return null;

//         // Define a comprehensive list of all possible fields and their display names
//         const fieldDefinitions = {
//             // Personal & Employer Info
//             "name_of_employee": { label: "Name of Employee", type: "text" },
//             "pan_of_employee": { label: "PAN of Employee", type: "text" },
//             "date_of_birth": { label: "Date of Birth", type: "date" },
//             "gender": { label: "Gender", type: "text" },
//             "residential_status": { label: "Residential Status", type: "text" },
//             "employer_name": { label: "Employer Name", type: "text" },
//             "employer_address": { label: "Employer Address", type: "text" },
//             "pan_of_deductor": { label: "PAN of Deductor", type: "text" },
//             "tan_of_deductor": { label: "TAN of Deductor", type: "text" },
//             "designation_of_employee": { label: "Designation", type: "text" },
//             // Financial Years & Period
//             "financial_year": { label: "Financial Year", type: "text" },
//             "assessment_year": { label: "Assessment Year", type: "text" },
//             "period_from": { label: "Period From", type: "date" },
//             "period_to": { label: "Period To", type: "date" },
//             "statement_start_date": { label: "Statement Start Date", type: "date" },
//             "statement_end_date": { label: "Statement End Date", type: "date" },
//             // Income
//             "gross_salary_total": { label: "Gross Salary Total", type: "currency" },
//             "salary_as_per_sec_17_1": { label: "Salary U/S 17(1)", type: "currency" },
//             "value_of_perquisites_u_s_17_2": { label: "Perquisites U/S 17(2)", type: "currency" },
//             "profits_in_lieu_of_salary_u_s_17_3": { label: "Profits in Lieu of Salary U/S 17(3)", type: "currency" },
//             "basic_salary": { label: "Basic Salary", type: "currency" },
//             "hra_received": { label: "HRA Received", type: "currency" },
//             "conveyance_allowance": { label: "Conveyance Allowance", type: "currency" },
//             "transport_allowance": { label: "Transport Allowance", type: "currency" },
//             "overtime_pay": { label: "Overtime Pay", type: "currency" },
//             "total_exempt_allowances": { label: "Total Exempt Allowances", type: "currency" },
//             "income_from_house_property": { label: "Income from House Property", type: "currency" },
//             "income_from_other_sources": { label: "Income from Other Sources", type: "currency" },
//             "capital_gains_long_term": { label: "Long Term Capital Gains", type: "currency" },
//             "capital_gains_short_term": { label: "Short Term Capital Gains", type: "currency" },
//             "gross_total_income_as_per_document": { label: "Gross Total Income (Doc)", type: "currency" },
//             // Deductions
//             "professional_tax": { label: "Professional Tax", type: "currency" },
//             "interest_on_housing_loan_self_occupied": { label: "Interest on Home Loan (Self Occupied)", type: "currency" },
//             "deduction_80c": { label: "Deduction 80C", type: "currency" },
//             "deduction_80c_epf": { label: "Deduction 80C (EPF)", type: "currency" },
//             "deduction_80c_insurance_premium": { label: "Deduction 80C (Insurance Premium)", type: "currency" },
//             "deduction_80ccc": { label: "Deduction 80CCC", type: "currency" },
//             "deduction_80ccd": { label: "Deduction 80CCD", type: "currency" },
//             "deduction_80ccd1b": { label: "Deduction 80CCD(1B)", type: "currency" },
//             "deduction_80d": { label: "Deduction 80D", type: "currency" },
//             "deduction_80g": { label: "Deduction 80G", type: "currency" },
//             "deduction_80tta": { label: "Deduction 80TTA", type: "currency" },
//             "deduction_80ttb": { label: "Deduction 80TTB", type: "currency" },
//             "deduction_80e": { label: "Deduction 80E", type: "currency" },
//             "total_deductions_chapter_via": { label: "Total Chapter VI-A Deductions", type: "currency" },
//             "aggregate_of_deductions_from_salary": { label: "Aggregate Deductions from Salary", type: "currency" },
//             "epf_contribution": { label: "EPF Contribution", type: "currency" },
//             "esi_contribution": { label: "ESI Contribution", type: "currency" },
//             // Tax Paid
//             "total_tds": { label: "Total TDS", type: "currency" },
//             "total_tds_deducted_summary": { label: "Total TDS Deducted (Summary)", type: "currency" },
//             "total_tds_deposited_summary": { label: "Total TDS Deposited (Summary)", type: "currency" },
//             "quarter_1_receipt_number": { label: "Q1 Receipt Number", type: "text" },
//             "quarter_1_tds_deducted": { label: "Q1 TDS Deducted", type: "currency" },
//             "quarter_1_tds_deposited": { label: "Q1 TDS Deposited", type: "currency" },
//             "advance_tax": { label: "Advance Tax", type: "currency" },
//             "self_assessment_tax": { label: "Self-Assessment Tax", type: "currency" },
//             // Other Tax Info
//             "taxable_income_as_per_document": { label: "Taxable Income (Doc)", type: "currency" },
//             "tax_payable_as_per_document": { label: "Tax Payable (Doc)", type: "currency" },
//             "refund_status_as_per_document": { label: "Refund Status (Doc)", type: "text" },
//             "tax_regime_chosen": { label: "Tax Regime Chosen", type: "text" },
//             "net_amount_payable": { label: "Net Amount Payable", type: "currency" },
//             "days_present": { label: "Days Present", type: "number" },
//             "overtime_hours": { label: "Overtime Hours", type: "number" },
//             // Bank Statement Details
//             "account_holder_name": { label: "Account Holder Name", type: "text" },
//             "account_number": { label: "Account Number", type: "text" },
//             "ifsc_code": { label: "IFSC Code", type: "text" },
//             "bank_name": { label: "Bank Name", type: "text" },
//             "branch_address": { label: "Branch Address", type: "text" },
//             "opening_balance": { label: "Opening Balance", type: "currency" },
//             "closing_balance": { label: "Closing Balance", type: "currency" },
//             "total_deposits": { label: "Total Deposits", type: "currency" },
//             "total_withdrawals": { label: "Total Withdrawals", type: "currency" },
//             "transaction_summary": { label: "Transaction Summary", type: "array_of_objects" }
//         };

//         const taxRelatedFields = [
//             "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
//             "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
//             "total_exempt_allowances", "income_from_house_property", "income_from_other_sources", "capital_gains_long_term",
//             "capital_gains_short_term", "gross_total_income_as_per_document", "professional_tax", "interest_on_housing_loan_self_occupied",
//             "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
//             "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
//             "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
//             "epf_contribution", "esi_contribution", "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
//             "quarter_1_receipt_number", "quarter_1_tds_deducted", "quarter_1_tds_deposited", "advance_tax", "self_assessment_tax",
//             "taxable_income_as_per_document", "tax_payable_as_per_document", "refund_status_as_per_document", "tax_regime_chosen",
//             "net_amount_payable", "days_present", "overtime_hours"
//         ];

//         const bankStatementFields = [
//             "account_holder_name", "account_number", "ifsc_code", "bank_name", "branch_address",
//             "statement_start_date", "statement_end_date", "opening_balance", "closing_balance",
//             "total_deposits", "total_withdrawals", "transaction_summary"
//         ];
        
//         let fieldsToRender = [];
//         if (identifiedType === 'Bank Statement') {
//             fieldsToRender = bankStatementFields.filter(key => fields[key] !== undefined);
//         } else {
//             // For other document types, primarily show tax-related fields plus common ones
//             fieldsToRender = Object.keys(fields).filter(key => 
//                 taxRelatedFields.includes(key) ||
//                 ["name_of_employee", "pan_of_employee", "financial_year", "assessment_year", "date_of_birth"].includes(key)
//             );
//         }

//         // Sort fields to render according to the predefined order for consistency
//         fieldsToRender.sort((a, b) => {
//             const indexA = Object.keys(fieldDefinitions).indexOf(a);
//             const indexB = Object.keys(fieldDefinitions).indexOf(b);
//             return indexA - indexB;
//         });


//         return (
//             <ul style={{ listStyleType: 'none', padding: 0 }}>
//                 {fieldsToRender.map(key => {
//                     const fieldDef = fieldDefinitions[key];
//                     let value = fields[key];

//                     if (!fieldDef || value === null || value === undefined || (typeof value === 'string' && value.toLowerCase() === 'null') || (typeof value === 'string' && value.trim() === '')) {
//                         return null; // Skip if no definition, null, undefined, "null", or empty string
//                     }

//                     // Handle date fields that might come as "0000-01-01"
//                     if (fieldDef.type === "date" && value === "0000-01-01") {
//                         value = "N/A";
//                     } else if (fieldDef.type === "currency" && typeof value === 'number') {
//                         value = formatCurrency(value);
//                     } else if (Array.isArray(value) && value.length === 0) {
//                         return null; // Skip empty arrays
//                     }

//                     // Special handling for transaction_summary
//                     if (key === "transaction_summary" && Array.isArray(value)) {
//                         return (
//                             <li key={key}>
//                                 <strong>{fieldDef.label}:</strong>
//                                 <pre className="extracted-fields-preview mt-2">
//                                     {value.length > 0 ? JSON.stringify(value.map(tx => ({
//                                         date: tx.date !== "0000-01-01" ? tx.date : "N/A",
//                                         description: tx.description,
//                                         amount: formatCurrency(tx.amount)
//                                     })), null, 2) : 'No transactions found.'}
//                                 </pre>
//                             </li>
//                         );
//                     }
                    
//                     return (
//                         <li key={key}>
//                             <strong>{fieldDef.label}:</strong> {value.toString()}
//                         </li>
//                     );
//                 })}
//             </ul>
//         );
//     };

//     useEffect(() => {
//         const fetchHistory = async () => {
//             setLoading(true);
//             setMessage('Fetching your tax history...');
//             setMessageType('info');
//             const jwt_token = Cookies.get('jwt_token');

//             try {
//                 // Corrected endpoint to match backend (used in app1.py: /api/tax_history)
//                 const response = await axios.get('http://127.0.0.1:5000/api/tax_history', {
//                     headers: {
//                         'Authorization': `Bearer ${jwt_token}`
//                     },
//                     withCredentials: true,
//                 });

//                 if (response.data.status === 'success') {
//                     setHistory(response.data.history);
//                     setMessage('Tax history loaded successfully.');
//                     setMessageType('success');
//                 } else {
//                     setMessage(response.data.message || 'Failed to fetch tax history.');
//                     setMessageType('error');
//                 }
//             } catch (error) {
//                 console.error('Error fetching tax history:', error);
//                 setMessage(error.response?.data?.message || 'An error occurred while fetching history.');
//                 setMessageType('error');
//             } finally {
//                 setLoading(false);
//             }
//         };

//         fetchHistory();
//     }, []);

//     const handleViewDetails = (record) => {
//         setSelectedRecord(record);
//         window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top to view details
//     };

//     const handleBackToList = () => {
//         setSelectedRecord(null);
//     };

//     const handleGetSuggestionsFromHistory = async (record) => {
//         setIsGeneratingSuggestions(true);
//         setMessage('Generating AI suggestions and ML predictions for this record...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             const response = await axios.post('http://127.0.0.1:5000/api/get_suggestions', 
//                 { record_id: record._id }, 
//                 {
//                     headers: {
//                         'Content-Type': 'application/json',
//                         'Authorization': `Bearer ${jwt_token}`
//                     },
//                     withCredentials: true,
//                 }
//             );

//             if (response.data.status === 'success') {
//                 setMessage('Suggestions and predictions generated!');
//                 setMessageType('success');
//                 // Update the selected record with new suggestions directly
//                 setSelectedRecord(prev => ({
//                     ...prev,
//                     suggestions_from_gemini: response.data.suggestions_from_gemini,
//                     gemini_regime_analysis: response.data.gemini_regime_analysis,
//                     ml_prediction_summary: response.data.ml_prediction_summary,
//                 }));
//             } else {
//                 setMessage(response.data.message || 'Failed to get suggestions.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Error getting suggestions from history:', error);
//             setMessage(error.response?.data?.message || 'An error occurred while fetching suggestions.');
//             setMessageType('error');
//         } finally {
//             setIsGeneratingSuggestions(false);
//         }
//     };

//     const handleGenerateITRFromHistory = async (record) => {
//         setIsGeneratingITR(true);
//         setMessage('Generating ITR form...');
//         setMessageType('info');

//         const jwt_token = Cookies.get('jwt_token');

//         try {
//             // Corrected endpoint to match backend (used in app1.py: /api/generate-itr/<record_id>)
//             const response = await axios.get(`http://127.0.0.1:5000/api/generate-itr/${record._id}`, {
//                 headers: {
//                     'Authorization': `Bearer ${jwt_token}`
//                 },
//                 responseType: 'blob', // Important: receive the response as a Blob
//                 withCredentials: true,
//             });

//             if (response.status === 200) {
//                 const blob = new Blob([response.data], { type: 'application/pdf' });
//                 const url = window.URL.createObjectURL(blob);
//                 const contentDisposition = response.headers['content-disposition'];
//                 let filename = 'ITR_Form.pdf';
//                 if (contentDisposition) {
//                     const filenameMatch = contentDisposition.match(/filename="(.+)"/);
//                     if (filenameMatch && filenameMatch[1]) {
//                         filename = filenameMatch[1];
//                     }
//                 }
//                 const link = document.createElement('a');
//                 link.href = url;
//                 link.setAttribute('download', filename);
//                 document.body.appendChild(link);
//                 link.click();
//                 link.parentNode.removeChild(link);
//                 window.URL.revokeObjectURL(url);

//                 setMessage('ITR form generated and downloaded!');
//                 setMessageType('success');
//             } else {
//                  // Try to read error message from non-PDF response
//                 const errorData = await new Response(response.data).text();
//                 setMessage(errorData || 'Failed to generate ITR form.');
//                 setMessageType('error');
//             }
//         } catch (error) {
//             console.error('Error generating ITR from history:', error);
//             let errorMessage = 'An error occurred while generating ITR.';
//             if (axios.isAxiosError(error) && error.response && error.response.data) {
//                 const reader = new FileReader();
//                 reader.onload = function() {
//                     try {
//                         const errorJson = JSON.parse(reader.result);
//                         errorMessage = errorJson.message || errorMessage;
//                     } catch (e) {
//                         // Not a JSON error, use generic message
//                         errorMessage = reader.result || error.response.statusText;
//                     } finally {
//                         setMessage(errorMessage);
//                         setMessageType('error');
//                     }
//                 };
//                 reader.readAsText(error.response.data);
//             } else {
//                 setMessage(errorMessage);
//                 setMessageType('error');
//             }
//         } finally {
//             setIsGeneratingITR(false);
//         }
//     };


//     return (
//         <div className="p-6 max-w-7xl mx-auto bg-gray-100 min-h-screen font-sans">
//             <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Your Tax History</h2>

//             {message && (
//                 <div className={`message ${messageType}`}>
//                     {messageType === 'info' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {messageType === 'success' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {messageType === 'error' && <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
//                     {message}
//                 </div>
//             )}

//             {selectedRecord ? (
//                 // Detailed View of a Single Record
//                 <div className="container-card">
//                     <button onClick={handleBackToList} className="btn-secondary mb-4 flex items-center">
//                         <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
//                         Back to History List
//                     </button>
//                     <h3 className="text-xl font-semibold text-gray-700 mb-4">Details for Record: {selectedRecord._id}</h3>
                    
//                     {/* Wrapped the inner sections in a fragment */}
//                     <>
//                         {selectedRecord.document_processing_summary && selectedRecord.document_processing_summary.length > 0 && (
//                             <div className="section-box">
//                                 <h4 className="text-lg font-medium text-gray-700 mb-2">Processed Documents Summary:</h4>
//                                 {selectedRecord.document_processing_summary.map((doc, index) => (
//                                     <div key={index} className={`mb-4 p-3 rounded-md ${doc.status === 'success' ? 'bg-green-50 text-green-800' : doc.status === 'warning' ? 'bg-yellow-50 text-yellow-800' : 'bg-red-50 text-red-800'}`}>
//                                         <p><strong>File:</strong> {doc.filename} {doc.stored_path && <a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">(View Stored Document)</a>}</p>
//                                         <p><strong>Status:</strong> <span className="uppercase">{doc.status}</span></p>
//                                         <p><strong>Identified Type:</strong> {doc.identified_type}</p>
//                                         <p><strong>Message:</strong> {doc.message}</p>
//                                         {/* Extracted fields for each document, using the improved renderExtractedFields */}
//                                         {doc.extracted_fields && Object.keys(doc.extracted_fields).length > 0 && (
//                                             <p><strong>Extracted Fields:</strong>
//                                                 <pre className="extracted-fields-preview">
//                                                 {renderExtractedFields(doc.extracted_fields, doc.identified_type)}
//                                                 </pre>
//                                             </p>
//                                         )}
//                                     </div>
//                                 ))}
//                             </div>
//                         )}

//                         {selectedRecord.aggregated_financial_data && (
//                             <div className="section-box">
//                                 <h3 className="text-lg font-medium text-gray-700 mb-2">Aggregated Financial Data Summary</h3>
                                
//                                 {/* Conditional rendering for Bank Statement vs. Tax Data in aggregated summary */}
//                                 {selectedRecord.aggregated_financial_data.identified_type === 'Bank Statement' || 
//                                  (selectedRecord.aggregated_financial_data.account_number && selectedRecord.aggregated_financial_data.account_number !== 'null') ? (
//                                     <div className="income-details-section"> {/* Re-using for consistent styling */}
//                                         <h5>Bank Account Details</h5>
//                                         <p><strong>Account Holder Name:</strong> {selectedRecord.aggregated_financial_data.account_holder_name || 'N/A'}</p>
//                                         <p><strong>Account Number:</strong> {selectedRecord.aggregated_financial_data.account_number || 'N/A'}</p>
//                                         <p><strong>Bank Name:</strong> {selectedRecord.aggregated_financial_data.bank_name || 'N/A'}</p>
//                                         <p><strong>Branch Address:</strong> {selectedRecord.aggregated_financial_data.branch_address || 'N/A'}</p>
//                                         <p><strong>Statement Period:</strong> {selectedRecord.aggregated_financial_data.statement_start_date || 'N/A'} to {selectedRecord.aggregated_financial_data.statement_end_date || 'N/A'}</p>
//                                         <p><strong>Opening Balance:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.opening_balance)}</p>
//                                         <p><strong>Closing Balance:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.closing_balance)}</p>
//                                         <p><strong>Total Deposits:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deposits)}</p>
//                                         <p><strong>Total Withdrawals:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_withdrawals)}</p>
//                                         {selectedRecord.aggregated_financial_data.transaction_summary && selectedRecord.aggregated_financial_data.transaction_summary.length > 0 && (
//                                             <p>
//                                                 <strong>Key Transactions:</strong> 
//                                                 <pre className="extracted-fields-preview mt-2">
//                                                     {JSON.stringify(selectedRecord.aggregated_financial_data.transaction_summary.slice(0, 5).map(tx => ({ // Show first 5 transactions
//                                                         date: tx.date !== "0000-01-01" ? tx.date : "N/A",
//                                                         description: tx.description,
//                                                         amount: formatCurrency(tx.amount)
//                                                     })), null, 2)}
//                                                     {selectedRecord.aggregated_financial_data.transaction_summary.length > 5 ? '\n...' : ''}
//                                                 </pre>
//                                             </p>
//                                         )}
//                                     </div>
//                                 ) : (
//                                     <>
//                                         <div className="income-details-section">
//                                             <h5>Income Details</h5>
//                                             <p><strong>Financial Year:</strong> {selectedRecord.aggregated_financial_data.financial_year || 'N/A'}</p>
//                                             <p><strong>Assessment Year:</strong> {selectedRecord.aggregated_financial_data.assessment_year || 'N/A'}</p>
//                                             <p><strong>Name:</strong> {selectedRecord.aggregated_financial_data.name_of_employee || 'N/A'}</p>
//                                             <p><strong>PAN:</strong> {selectedRecord.aggregated_financial_data.pan_of_employee || 'N/A'}</p>
//                                             <p><strong>Date of Birth:</strong> {selectedRecord.aggregated_financial_data.date_of_birth !== "0000-01-01" ? selectedRecord.aggregated_financial_data.date_of_birth : 'N/A'}</p>
//                                             <p><strong>Age:</strong> {selectedRecord.aggregated_financial_data.Age || 'N/A'}</p>
//                                             <p><strong>Gross Annual Salary:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.gross_salary_total)}</p>
//                                             <p><strong>Exempt Allowances:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_exempt_allowances)}</p>
//                                             <p><strong>Income from House Property:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_house_property)}</p>
//                                             <p><strong>Income from Other Sources:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.income_from_other_sources)}</p>
//                                             <p><strong>Long Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_long_term)}</p>
//                                             <p><strong>Short Term Capital Gains:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.capital_gains_short_term)}</p>
//                                             <p><strong>Total Gross Income (Aggregated):</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.calculated_gross_income)}</p>
//                                         </div>
//                                         <div className="deductions-section">
//                                             <h5>Deductions Claimed</h5>
//                                             {selectedRecord.aggregated_financial_data.standard_deduction > 0 && 
//                                                 <p><strong>Standard Deduction:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.standard_deduction)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.professional_tax > 0 &&
//                                                 <p><strong>Professional Tax:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.professional_tax)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b !== 0 &&
//                                                 <p><strong>Interest on Home Loan (Section 24(b)):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.interest_on_housing_loan_24b)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80C > 0 &&
//                                                 <p><strong>Section 80C Investments:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80C)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80CCD1B > 0 &&
//                                                 <p><strong>Section 80CCD1B:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80CCD1B)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80D > 0 &&
//                                                 <p><strong>Section 80D (Health Insurance):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80D)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80G > 0 &&
//                                                 <p><strong>Section 80G:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80G)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80TTA > 0 &&
//                                                 <p><strong>Section 80TTA:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTA)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80TTB > 0 &&
//                                                 <p><strong>Section 80TTB:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80TTB)}</p>
//                                             }
//                                             {selectedRecord.aggregated_financial_data.deduction_80E > 0 &&
//                                                 <p><strong>Section 80E (Education Loan Interest):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.deduction_80E)}</p>
//                                             }
//                                             <p><strong>Total Deductions (Aggregated for Display):</strong> {formatCurrency(selectedRecord.aggregated_financial_data.total_deductions)}</p>
//                                         </div>
//                                         <div className="taxation-summary-section">
//                                             <h5>Tax Payments & Regime</h5>
//                                             <p><strong>Total TDS Credit:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.total_tds_credit)}</p>
//                                             <p><strong>Advance Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.advance_tax)}</p>
//                                             <p><strong>Self-Assessment Tax Paid:</strong> {formatCurrency(selectedRecord.aggregated_financial_data.self_assessment_tax)}</p>
//                                             <p><strong>Tax Regime Chosen (from docs):</strong> <span className="highlight-regime">{selectedRecord.aggregated_financial_data.tax_regime_chosen || 'Not Specified'}</span></p>
//                                         </div>
//                                     </>
//                                 )}
//                             </div>
//                             <div className="final-tax-computation-section section-box">
//                                 <h4 className="section-title">Final Tax Computation Summary (Rule-Based)</h4>
//                                 {selectedRecord.final_tax_computation_summary.calculation_details && selectedRecord.final_tax_computation_summary.calculation_details.length > 0 && (
//                                     <div className="computation-details-list">
//                                         <h5>Calculation Steps:</h5>
//                                         <ul style={{ listStyleType: 'decimal', marginLeft: '20px', paddingLeft: '0' }}>
//                                             {selectedRecord.final_tax_computation_summary.calculation_details.map((detail, idx) => (
//                                                 <li key={idx} className="computation-detail-item">{detail}</li>
//                                             ))}
//                                         </ul>
//                                     </div>
//                                 )}
//                                 <div className="final-amount-box">
//                                     <p><strong>Computed Taxable Income:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.computed_taxable_income)}</p>
//                                     <p><strong>Estimated Tax Payable:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.estimated_tax_payable)}</p>
//                                     <p><strong>Tax Regime Considered for Rule-Based Calculation:</strong> <span className="highlight-regime">{selectedRecord.final_tax_computation_summary.regime_considered || 'N/A'}</span></p>
//                                     {selectedRecord.final_tax_computation_summary.predicted_refund_due > 0 && (
//                                         <p className="refund-amount">
//                                             <strong>Refund Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_refund_due)}
//                                         </p>
//                                     )}
//                                     {selectedRecord.final_tax_computation_summary.predicted_additional_due > 0 && (
//                                         <p className="tax-due-amount">
//                                             <strong>Additional Tax Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_additional_due)}
//                                         </p>
//                                     )}
//                                 </div>
//                                 {selectedRecord.final_tax_computation_summary.notes && selectedRecord.final_tax_computation_summary.notes.length > 0 && (
//                                     <p className="computation-notes">
//                                         <strong>Note:</strong> {Array.isArray(selectedRecord.final_tax_computation_summary.notes) ? selectedRecord.final_tax_computation_summary.notes.join(', ') : selectedRecord.final_tax_computation_summary.notes}
//                                     </p>
//                                 )}
//                             </div>
//                         </>
//                     </div>

//                     <div className="action-buttons-container" style={{ justifyContent: 'center' }}>
//                         <button
//                             onClick={() => handleGetSuggestionsFromHistory(selectedRecord)}
//                             disabled={isGeneratingSuggestions}
//                             className={`tax-uploader-button get-suggestions-button ${isGeneratingSuggestions ? 'opacity-75 cursor-not-allowed' : ''}`}
//                         >
//                             {isGeneratingSuggestions ? (
//                                 <>
//                                     <div className="tax-uploader-spinner"></div>
//                                     Generating AI Suggestions...
//                                 </>
//                             ) : (
//                                 'Re-Generate AI Suggestions & ML Predictions'
//                             )}
//                         </button>
//                         <button
//                             onClick={() => handleGenerateITRFromHistory(selectedRecord)}
//                             disabled={isGeneratingITR}
//                             className={`tax-uploader-button generate-itr-button ${isGeneratingITR ? 'opacity-75 cursor-not-allowed' : ''}`}
//                         >
//                             {isGeneratingITR ? (
//                                 <>
//                                     <div className="tax-uploader-spinner"></div>
//                                     Generating ITR Form...
//                                 </>
//                             ) : (
//                                 'Generate Dummy ITR Form (PDF)'
//                             )}
//                         </button>
//                     </div>

//                     {/* Display Suggestions from Gemini and ML Predictions */}
//                     {(selectedRecord.suggestions_from_gemini || selectedRecord.gemini_regime_analysis || selectedRecord.ml_prediction_summary) && (
//                         <div className="suggestions-output tax-summary-output">
//                             <h3 className="tax-uploader-title" style={{ marginTop: '30px', fontSize: '1.8em' }}>AI Recommendations & Predictions</h3>
//                             <div className="section-box">
//                                 {selectedRecord.suggestions_from_gemini && selectedRecord.suggestions_from_gemini.length > 0 ? (
//                                     <>
//                                         <h4>Based on Gemini AI:</h4>
//                                         <ul className="suggestions-list">
//                                             {selectedRecord.suggestions_from_gemini.map((suggestion, index) => (
//                                                 <li key={index}>{suggestion}</li>
//                                             ))}
//                                         </ul>
//                                     </>
//                                 ) : (
//                                     <p>Gemini did not provide specific tax-saving suggestions for this record, but your tax situation seems optimized.</p>
//                                 )}
//                                 {selectedRecord.gemini_regime_analysis && (
//                                     <div className="gemini-regime-analysis">
//                                         <h4>Gemini's Regime Analysis:</h4>
//                                         <p>{selectedRecord.gemini_regime_analysis}</p>
//                                     </div>
//                                 )}
//                                 {selectedRecord.ml_prediction_summary && (
//                                     <>
//                                         <h4>ML Model Prediction:</h4>
//                                         {selectedRecord.ml_prediction_summary.predicted_tax_regime && (
//                                             <p><strong>Predicted Tax Regime:</strong> {selectedRecord.ml_prediction_summary.predicted_tax_regime}</p>
//                                         )}
//                                         <p><strong>Predicted Tax Liability:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_tax_liability)}</p>
//                                         <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_refund_due)}</p>
//                                         <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_additional_due)}</p>
//                                         {selectedRecord.ml_prediction_summary.notes && (
//                                             <p><strong>Notes:</strong> {selectedRecord.ml_prediction_summary.notes}</p>
//                                         )}
//                                     </>
//                                 )}
//                             </div>
//                         </div>
//                     )}

//                 </div>
//             ) : (
//                 // List View of Records
//                 <div className="container-card">
//                     <h3 className="text-xl font-semibold text-gray-700 mb-4">Your Processed Tax Records</h3>
//                     {loading ? (
//                         <p className="text-center text-gray-600 flex items-center justify-center">
//                             <span className="loading-spinner mr-2 border-indigo-500 border-t-indigo-500"></span>
//                             Loading tax records...
//                         </p>
//                     ) : history.length === 0 ? (
//                         <p className="text-center text-gray-600">No tax records found. Upload documents to get started!</p>
//                     ) : (
//                         <div className="overflow-x-auto">
//                             <table className="min-w-full bg-white rounded-lg shadow overflow-hidden history-table">
//                                 <thead className="bg-gray-200">
//                                     <tr>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Record ID</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Document Type</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Financial Year</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Last Processed</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Aggregated Gross Income</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Estimated Tax Payable</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Refund / Due</th>
//                                         <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
//                                     </tr>
//                                 </thead>
//                                 <tbody className="divide-y divide-gray-200">
//                                     {history.map((record) => (
//                                         <tr key={record._id} className="hover:bg-gray-50">
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record._id.substring(0, 8)}...</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record.document_processing_summary?.[0]?.identified_type || 'N/A'}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{record.aggregated_financial_data.financial_year || 'N/A'}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">{new Date(record.timestamp).toLocaleString()}</td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : formatCurrency(record.aggregated_financial_data.total_gross_income)}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-800">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : formatCurrency(record.final_tax_computation_summary.estimated_tax_payable)}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm">
//                                                 {record.aggregated_financial_data.identified_type === 'Bank Statement' ? 'N/A' : (
//                                                     record.final_tax_computation_summary.predicted_refund_due > 0 ? (
//                                                         <span className="refund-amount">{formatCurrency(record.final_tax_computation_summary.predicted_refund_due)} Refund</span>
//                                                     ) : record.final_tax_computation_summary.predicted_additional_due > 0 ? (
//                                                         <span className="tax-due-amount">{formatCurrency(record.final_tax_computation_summary.predicted_additional_due)} Due</span>
//                                                     ) : (
//                                                         'N/A'
//                                                     )
//                                                 )}
//                                             </td>
//                                             <td className="py-3 px-4 whitespace-nowrap text-sm">
//                                                 <button
//                                                     onClick={() => handleViewDetails(record)}
//                                                     className="view-details-btn"
//                                                 >
//                                                     View Details
//                                                 </button>
//                                             </td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     )}
//                 </div>
//             )}
//         </div>
//     );
// };

// export default TaxHistory;





















import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import './index.css'; // Import TaxHistory specific CSS

const TaxHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'
    const [selectedRecord, setSelectedRecord] = useState(null); // To view full details of a record
    const [isGeneratingITR, setIsGeneratingITR] = useState(false);

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

    // Helper function to render extracted fields dynamically (duplicated from TaxUploader for self-containment)
    const renderExtractedFields = (fields) => {
        if (!fields) return null;

        const fieldOrder = [
            // Personal & Employer Info
            "name_of_employee", "pan_of_employee", "date_of_birth", "gender", "residential_status",
            "employer_name", "employer_address", "pan_of_deductor", "tan_of_deductor", "designation_of_employee",
            // Financial Years & Period
            "financial_year", "assessment_year", "period_from", "period_to", "statement_start_date", "statement_end_date",
            // Income
            "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
            "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
            "total_exempt_allowances",
            "income_from_house_property", "income_from_other_sources", "capital_gains_long_term", "capital_gains_short_term",
            "gross_total_income_as_per_document",
            // Deductions
            "professional_tax", "interest_on_housing_loan_self_occupied",
            "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
            "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
            "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
            "epf_contribution", "esi_contribution",
            // Tax Paid
            "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
            "quarter_1_receipt_number", "quarter_1_tds_deducted", "quarter_1_tds_deposited",
            "advance_tax", "self_assessment_tax",
            // Other Tax Info
            "taxable_income_as_per_document", "tax_payable_as_per_document", "refund_status_as_per_document", "tax_regime_chosen",
            "net_amount_payable", "days_present", "overtime_hours",
            // Bank Statement Details
            "account_holder_name", "account_number", "ifsc_code", "bank_name", "branch_address",
            "opening_balance", "closing_balance", "total_deposits", "total_withdrawals"
        ];
        
        // Define display names for better readability
        const displayNames = {
            "name_of_employee": "Name of Employee",
            "pan_of_employee": "PAN of Employee",
            "date_of_birth": "Date of Birth",
            "gender": "Gender",
            "residential_status": "Residential Status",
            "employer_name": "Employer Name",
            "employer_address": "Employer Address",
            "pan_of_deductor": "PAN of Deductor",
            "tan_of_deductor": "TAN of Deductor",
            "designation_of_employee": "Designation",
            "financial_year": "Financial Year",
            "assessment_year": "Assessment Year",
            "period_from": "Period From",
            "period_to": "Period To",
            "statement_start_date": "Statement Start Date",
            "statement_end_date": "Statement End Date",
            "gross_salary_total": "Gross Salary Total",
            "salary_as_per_sec_17_1": "Salary U/S 17(1)",
            "value_of_perquisites_u_s_17_2": "Perquisites U/S 17(2)",
            "profits_in_lieu_of_salary_u_s_17_3": "Profits in Lieu of Salary U/S 17(3)",
            "basic_salary": "Basic Salary",
            "hra_received": "HRA Received",
            "conveyance_allowance": "Conveyance Allowance",
            "transport_allowance": "Transport Allowance",
            "overtime_pay": "Overtime Pay",
            "total_exempt_allowances": "Total Exempt Allowances",
            "income_from_house_property": "Income from House Property",
            "income_from_other_sources": "Income from Other Sources",
            "capital_gains_long_term": "Long Term Capital Gains",
            "capital_gains_short_term": "Short Term Capital Gains",
            "gross_total_income_as_per_document": "Gross Total Income (Document)",
            "professional_tax": "Professional Tax",
            "interest_on_housing_loan_self_occupied": "Interest on Housing Loan (Self-Occupied)",
            "deduction_80c": "Deduction 80C",
            "deduction_80c_epf": "80C - EPF",
            "deduction_80c_insurance_premium": "80C - Insurance Premium",
            "deduction_80ccc": "Deduction 80CCC",
            "deduction_80ccd": "Deduction 80CCD",
            "deduction_80ccd1b": "Deduction 80CCD(1B)",
            "deduction_80d": "Deduction 80D",
            "deduction_80g": "Deduction 80G",
            "deduction_80tta": "Deduction 80TTA",
            "deduction_80ttb": "Deduction 80TTB",
            "deduction_80e": "Deduction 80E",
            "total_deductions_chapter_via": "Total Deductions (Chapter VI-A)",
            "aggregate_of_deductions_from_salary": "Aggregate Deductions from Salary",
            "epf_contribution": "EPF Contribution",
            "esi_contribution": "ESI Contribution",
            "total_tds": "Total TDS",
            "total_tds_deducted_summary": "Total TDS Deducted (Summary)",
            "total_tds_deposited_summary": "Total TDS Deposited (Summary)",
            "quarter_1_receipt_number": "Q1 Receipt Number",
            "quarter_1_tds_deducted": "Q1 TDS Deducted",
            "quarter_1_tds_deposited": "Q1 TDS Deposited",
            "advance_tax": "Advance Tax",
            "self_assessment_tax": "Self-Assessment Tax",
            "taxable_income_as_per_document": "Taxable Income (Document)",
            "tax_payable_as_per_document": "Tax Payable (Document)",
            "refund_status_as_per_document": "Refund Status (Document)",
            "tax_regime_chosen": "Tax Regime Chosen (Document)",
            "net_amount_payable": "Net Amount Payable",
            "days_present": "Days Present",
            "overtime_hours": "Overtime Hours",
            "account_holder_name": "Account Holder Name",
            "account_number": "Account Number",
            "ifsc_code": "IFSC Code",
            "bank_name": "Bank Name",
            "branch_address": "Branch Address",
            "opening_balance": "Opening Balance",
            "closing_balance": "Closing Balance",
            "total_deposits": "Total Deposits",
            "total_withdrawals": "Total Withdrawals"
        };

        const currencyFields = [
            "gross_salary_total", "salary_as_per_sec_17_1", "value_of_perquisites_u_s_17_2", "profits_in_lieu_of_salary_u_s_17_3",
            "basic_salary", "hra_received", "conveyance_allowance", "transport_allowance", "overtime_pay",
            "total_exempt_allowances", "income_from_house_property", "income_from_other_sources", "capital_gains_long_term",
            "capital_gains_short_term", "gross_total_income_as_per_document", "professional_tax", "interest_on_housing_loan_self_occupied",
            "deduction_80c", "deduction_80c_epf", "deduction_80c_insurance_premium", "deduction_80ccc",
            "deduction_80ccd", "deduction_80ccd1b", "deduction_80d", "deduction_80g", "deduction_80tta",
            "deduction_80ttb", "deduction_80e", "total_deductions_chapter_via", "aggregate_of_deductions_from_salary",
            "epf_contribution", "esi_contribution",
            "total_tds", "total_tds_deducted_summary", "total_tds_deposited_summary",
            "quarter_1_tds_deducted", "quarter_1_tds_deposited", "advance_tax", "self_assessment_tax",
            "taxable_income_as_per_document", "tax_payable_as_per_document", "net_amount_payable",
            "opening_balance", "closing_balance", "total_deposits", "total_withdrawals"
        ];

        const dateFields = ["date_of_birth", "period_from", "period_to", "statement_start_date", "statement_end_date"];

        // Combine relevant fields from aggregated_financial_data and the top-level record
        const allFields = { ...fields.aggregated_financial_data, ...fields };
        // Prioritize fields from aggregated_financial_data where applicable
        if (fields.aggregated_financial_data) {
            Object.assign(allFields, fields.aggregated_financial_data);
        }
        // Prioritize fields from final_tax_computation_summary for tax-related figures
        if (fields.final_tax_computation_summary) {
            Object.assign(allFields, fields.final_tax_computation_summary);
        }
        // Prioritize fields from ml_prediction_summary for ML predictions
        if (fields.ml_prediction_summary) {
            Object.assign(allFields, fields.ml_prediction_summary);
        }


        return (
            <ul className="extracted-fields-list">
                {fieldOrder.map((key) => {
                    let value = allFields[key];
                    if (value === null || value === undefined || value === '') {
                        value = 'N/A';
                    } else if (currencyFields.includes(key)) {
                        value = formatCurrency(value);
                    } else if (dateFields.includes(key) && value !== 'N/A') {
                        try {
                            value = new Date(value).toLocaleDateString('en-IN', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric'
                            });
                        } catch (e) {
                            console.error(`Error formatting date for field ${key}:`, value, e);
                            value = 'Invalid Date';
                        }
                    } else if (typeof value === 'boolean') {
                        value = value ? 'Yes' : 'No';
                    } else if (Array.isArray(value) && key === 'transaction_summary') {
                        // Handle transaction summary specifically
                        if (value.length === 0) return null; // Don't show if empty

                        return (
                            <li key={key}>
                                <strong>{displayNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</strong>
                                <ul className="transaction-list">
                                    {value.map((transaction, index) => (
                                        <li key={index} className="transaction-item">
                                            {new Date(transaction.date).toLocaleDateString('en-IN', { month: 'numeric', day: 'numeric' })} - {transaction.description} ({transaction.type}) {formatCurrency(transaction.amount)}
                                        </li>
                                    ))}
                                </ul>
                            </li>
                        );
                    } else if (Array.isArray(value)) {
                        value = value.join(', ');
                    }

                    if (key === 'transaction_summary' && Array.isArray(allFields[key]) && allFields[key].length > 0) {
                        // Already handled above if it's an array and not empty
                        return null;
                    }

                    return (
                        <li key={key}>
                            <strong>{displayNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</strong> {value}
                        </li>
                    );
                })}
                {/* Displaying ML Prediction Summary */}
                {fields.ml_prediction_summary && (
                    <>
                        <h3>ML Prediction Summary</h3>
                        <li><strong>Recommended Regime:</strong> {fields.ml_prediction_summary.recommended_regime || 'N/A'}</li>
                        <li><strong>Predicted Refund:</strong> {formatCurrency(fields.ml_prediction_summary.predicted_refund)}</li>
                        <li><strong>Predicted Additional Due:</strong> {formatCurrency(fields.ml_prediction_summary.predicted_additional_due)}</li>
                    </>
                )}
            </ul>
        );
    };

    const fetchHistory = async () => {
        setLoading(true);
        setMessage('');
        setMessageType('');
        try {
            const token = Cookies.get('jwt_token');
            if (!token) {
                setMessage('Authentication required. Please log in.');
                setMessageType('error');
                setLoading(false);
                window.location.href = '/login';
                return;
            }
            const response = await axios.get('http://localhost:5000/api/tax-records', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.status === 200) {
                setHistory(response.data.history);
                setMessage('Tax history loaded successfully.');
                setMessageType('success');
            } else {
                setMessage(response.data.message || 'Failed to fetch tax history.');
                setMessageType('error');
                setHistory([]);
            }
        } catch (error) {
            console.error('Fetch history error:', error);
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
                setMessage('An error occurred while fetching tax history. Check network connection and backend server.');
            }
            setMessageType('error');
            setHistory([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []); // Empty dependency array means this runs once on mount

    const handleViewDetails = (record) => {
        setSelectedRecord(record);
    };

    const handleCloseDetails = () => {
        setSelectedRecord(null);
    };

    const handleGenerateITRForm = async (record) => {
        setIsGeneratingITR(true);
        setMessage('');
        setMessageType('');
        try {
            const token = Cookies.get('jwt_token');
            if (!token) {
                setMessage('Authentication required. Please log in.');
                setMessageType('error');
                setIsGeneratingITR(false);
                window.location.href = '/login';
                return;
            }

            const response = await axios.get(`http://localhost:5000/api/generate-itr/${record._id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                responseType: 'blob', // Important for downloading files
            });

            if (response.status === 200) {
                // Create a blob from the response data
                const blob = new Blob([response.data], { type: 'application/pdf' });
                // Create a link element
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                // Set the download filename based on the record's financial year and PAN
                const financialYear = record.financial_year || 'N_A';
                const pan = record.aggregated_financial_data?.pan_of_employee || 'N_A';
                link.setAttribute('download', `ITR_${financialYear}_${pan}.pdf`);
                // Append to body, click, and remove
                document.body.appendChild(link);
                link.click();
                link.parentNode.removeChild(link);
                window.URL.revokeObjectURL(url); // Clean up the URL object

                setMessage('ITR form generated and downloaded successfully!');
                setMessageType('success');
            } else {
                setMessage('Failed to generate ITR form.');
                setMessageType('error');
            }
        } catch (error) {
            console.error('Generate ITR error:', error);
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
                setMessage('An error occurred while generating the ITR form. Check network connection and backend server.');
            }
            setMessageType('error');
        } finally {
            setIsGeneratingITR(false);
        }
    };

    // New function to handle record deletion
    const handleDeleteRecord = async (recordId) => {
        if (window.confirm("Are you sure you want to delete this tax record? This action cannot be undone.")) {
            setMessage('');
            setMessageType('');
            try {
                const token = Cookies.get('jwt_token');
                if (!token) {
                    setMessage('Authentication required. Please log in.');
                    setMessageType('error');
                    window.location.href = '/login';
                    return;
                }

                const response = await axios.delete(`http://localhost:5000/api/tax-records/${recordId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.status === 200) {
                    setMessage('Tax record deleted successfully.');
                    setMessageType('success');
                    fetchHistory(); // Refresh the list after deletion
                } else {
                    setMessage(response.data.message || 'Failed to delete tax record.');
                    setMessageType('error');
                }
            } catch (error) {
                console.error('Delete record error:', error);
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
                    setMessage('An error occurred while deleting the tax record. Check network connection and backend server.');
                }
                setMessageType('error');
            }
        }
    };


    return (
        <div className="tax-history-container">
            <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Your Tax History</h2>

            {message && (
                <div className={`message ${messageType === 'success' ? 'message-success' : messageType === 'error' ? 'message-error' : 'message-info'}`}>
                    {message}
                </div>
            )}

            {loading ? (
                <div className="loading-indicator">Loading tax history...</div>
            ) : (
                <div>
                    {history.length === 0 ? (
                        <p className="text-center text-gray-600">No tax records found. Upload documents to see your history!</p>
                    ) : (
                        <div className="overflow-x-auto shadow-md rounded-lg">
                            <table className="min-w-full bg-white">
                                <thead className="bg-gray-200 text-gray-700">
                                    <tr>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Financial Year</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Assessment Year</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">PAN (Employee)</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Gross Salary</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Total Deductions</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Total Tax Liability</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">TDS Credit</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Status</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {history.map((record) => (
                                        <tr key={record._id} className="hover:bg-gray-50">
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">{record.financial_year || 'N/A'}</td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">{record.assessment_year || 'N/A'}</td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">
                                                {record.aggregated_financial_data?.pan_of_employee || 'N/A'}
                                            </td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">
                                                {formatCurrency(record.aggregated_financial_data?.gross_salary_total)}
                                            </td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">
                                                {formatCurrency(record.final_tax_computation_summary?.total_deductions)}
                                            </td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">
                                                {formatCurrency(record.final_tax_computation_summary?.total_tax_liability)}
                                            </td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">
                                                {formatCurrency(record.final_tax_computation_summary?.total_tds_credit)}
                                            </td>
                                            <td className={`py-3 px-4 whitespace-nowrap text-sm ${
                                                record.final_tax_computation_summary.predicted_refund > 0 ? 'text-green-600' :
                                                record.final_tax_computation_summary.predicted_additional_due > 0 ? 'text-red-600' : 'text-gray-600'
                                            }`}>
                                                {record.final_tax_computation_summary.predicted_refund > 0 ? (
                                                    <span className="tax-refund-amount">{formatCurrency(record.final_tax_computation_summary.predicted_refund)} Refund</span>
                                                ) : record.final_tax_computation_summary.predicted_additional_due > 0 ? (
                                                    <span className="tax-due-amount">{formatCurrency(record.final_tax_computation_summary.predicted_additional_due)} Due</span>
                                                ) : (
                                                    'N/A'
                                                )}
                                            </td>
                                            <td className="py-3 px-4 whitespace-nowrap text-sm">
                                                <button
                                                    onClick={() => handleViewDetails(record)}
                                                    className="view-details-btn"
                                                >
                                                    View Details
                                                </button>
                                                <button
                                                    onClick={() => handleGenerateITRForm(record)}
                                                    className="generate-itr-btn"
                                                    disabled={isGeneratingITR}
                                                >
                                                    {isGeneratingITR ? 'Generating...' : 'Generate ITR'}
                                                </button>
                                                {/* New Delete Button */}
                                                <button
                                                    onClick={() => handleDeleteRecord(record._id)}
                                                    className="delete-record-btn"
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Modal for displaying full record details */}
            {selectedRecord && (
                <div className="modal-overlay" onClick={handleCloseDetails}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">Tax Record Details for {selectedRecord.financial_year}</h3>
                            <button onClick={handleCloseDetails} className="modal-close-btn">&times;</button>
                        </div>
                        <div className="extracted-fields-grid">
                            {renderExtractedFields(selectedRecord)}
                            {selectedRecord.final_tax_computation_summary && (
                                <>
                                    <li><strong>Predicted Refund:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_refund)}</li>
                                    <li><strong>Predicted Additional Due:</strong> {formatCurrency(selectedRecord.final_tax_computation_summary.predicted_additional_due)}</li>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TaxHistory;