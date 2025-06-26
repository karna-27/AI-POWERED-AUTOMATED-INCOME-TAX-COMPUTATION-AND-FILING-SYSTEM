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

    useEffect(() => {
        const fetchHistory = async () => {
            setLoading(true);
            setMessage('Fetching your tax history...');
            setMessageType('info');
            const jwt_token = Cookies.get('jwt_token');

            try {
                const response = await axios.get('http://localhost:5000/api/tax_history', {
                    headers: {
                        'Authorization': `Bearer ${jwt_token}`
                    }
                });
                if (response.data.success) {
                    setHistory(response.data.history);
                    setMessage('Tax history loaded successfully.');
                    setMessageType('success');
                } else {
                    setMessage(response.data.message || 'Failed to fetch tax history.');
                    setMessageType('error');
                }
            } catch (error) {
                console.error('Error fetching tax history:', error);
                setMessage('Error fetching tax history. Please try again later.');
                setMessageType('error');
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    const handleViewDetails = (record) => {
        setSelectedRecord(record);
    };

    const handleBackToList = () => {
        setSelectedRecord(null);
    };

    const handleGenerateITR = async (recordId) => {
        setIsGeneratingITR(true);
        setMessage('Generating ITR for the selected record...');
        setMessageType('info');
        const jwt_token = Cookies.get('jwt_token');

        try {
            const response = await axios.post('http://localhost:5000/api/generate_itr', { record_id: recordId }, {
                headers: {
                    'Authorization': `Bearer ${jwt_token}`
                },
                responseType: 'blob', // Important for handling file downloads
            });

            // Create a blob from the response data
            const file = new Blob([response.data], { type: 'application/pdf' });
            // Create a link element
            const fileURL = URL.createObjectURL(file);
            const link = document.createElement('a');
            link.href = fileURL;
            link.setAttribute('download', `ITR_Report_${recordId}.pdf`); // Set the download file name
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(fileURL); // Clean up the URL object

            setMessage('ITR generated and downloaded successfully!');
            setMessageType('success');

        } catch (error) {
            console.error('Error generating ITR:', error);
            setMessage('Error generating ITR. Please try again later.');
            setMessageType('error');
        } finally {
            setIsGeneratingITR(false);
        }
    };

    return (
        <div className="tax-history-container">
            <h3>Your Tax History</h3>
            {loading && <p className={`message ${messageType}`}>{message}</p>}
            {!loading && message && messageType && (
                <p className={`message ${messageType}`}>{message}</p>
            )}

            {selectedRecord === null ? (
                // Display list of history records
                <div className="history-list-section">
                    {history.length > 0 ? (
                        <ul className="history-list">
                            {history.map((record) => (
                                <li key={record._id} className="history-item">
                                    <div className="record-summary">
                                        <p><strong>Upload Date:</strong> {new Date(record.upload_date).toLocaleDateString()}</p>
                                        <p><strong>Document Summary:</strong> {record.document_summary || 'N/A'}</p>
                                        <p><strong>Status:</strong> {record.status || 'Processed'}</p>
                                        {record.ml_prediction_summary && (
                                            <p><strong>Predicted Tax Liability:</strong> {formatCurrency(record.ml_prediction_summary.predicted_tax_liability)}</p>
                                        )}
                                    </div>
                                    <div className="record-actions">
                                        <button onClick={() => handleViewDetails(record)} className="view-details-button">View Details</button>
                                        <button
                                            onClick={() => handleGenerateITR(record._id)}
                                            className="generate-itr-button"
                                            disabled={isGeneratingITR}
                                        >
                                            {isGeneratingITR ? 'Generating...' : 'Generate ITR'}
                                        </button>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No tax history records found. Upload documents to get started!</p>
                    )}
                </div>
            ) : (
                // Display details of selected record
                <div className="record-details-section">
                    <button onClick={handleBackToList} className="back-button">← Back to History</button>
                    <h4>Details for Record: {new Date(selectedRecord.upload_date).toLocaleDateString()}</h4>

                    <div className="section-box">
                        <h5>Document Summary:</h5>
                        <p>{selectedRecord.document_summary || 'N/A'}</p>
                    </div>

                    {selectedRecord.aggregated_data && (
                        <div className="section-box">
                            <h5>Aggregated Data:</h5>
                            <pre>{JSON.stringify(selectedRecord.aggregated_data, null, 2)}</pre>
                        </div>
                    )}

                    {selectedRecord.computation_summary && (
                        <div className="section-box">
                            <h5>Tax Computation Summary:</h5>
                            <p><strong>Gross Total Income:</strong> {formatCurrency(selectedRecord.computation_summary.gross_total_income)}</p>
                            <p><strong>Deductions:</strong> {formatCurrency(selectedRecord.computation_summary.total_deductions)}</p>
                            <p><strong>Taxable Income:</strong> {formatCurrency(selectedRecord.computation_summary.taxable_income)}</p>
                            <p><strong>Tax Payable:</strong> {formatCurrency(selectedRecord.computation_summary.tax_payable)}</p>
                            <p><strong>TDS:</strong> {formatCurrency(selectedRecord.computation_summary.total_tds)}</p>
                            <p><strong>Advance Tax:</strong> {formatCurrency(selectedRecord.computation_summary.total_advance_tax)}</p>
                            <p><strong>Self-Assessment Tax:</strong> {formatCurrency(selectedRecord.computation_summary.total_self_assessment_tax)}</p>
                            {selectedRecord.computation_summary.final_tax_liability && (
                                <p><strong>Final Tax Liability:</strong> {formatCurrency(selectedRecord.computation_summary.final_tax_liability)}</p>
                            )}
                            {selectedRecord.computation_summary.refund_due && (
                                <p className="refund-amount"><strong>Refund Due:</strong> {formatCurrency(selectedRecord.computation_summary.refund_due)}</p>
                            )}
                            {selectedRecord.computation_summary.additional_tax_due && (
                                <p className="tax-due-amount"><strong>Additional Tax Due:</strong> {formatCurrency(selectedRecord.computation_summary.additional_tax_due)}</p>
                            )}
                            {selectedRecord.computation_summary.tax_regime_analysis && (
                                <p><strong>Tax Regime Analysis:</strong> {selectedRecord.computation_summary.tax_regime_analysis}</p>
                            )}
                        </div>
                    )}

                    {selectedRecord.suggestions_summary && (
                        <div className="section-box">
                            <h5>AI Recommendations:</h5>
                            <p>{selectedRecord.suggestions_summary.recommendations || 'N/A'}</p>
                            {selectedRecord.suggestions_summary.missing_documents_info && (
                                <p><strong>Missing Documents:</strong> {selectedRecord.suggestions_summary.missing_documents_info}</p>
                            )}
                            {selectedRecord.suggestions_summary.compliance_alerts && (
                                <p><strong>Compliance Alerts:</strong> {selectedRecord.suggestions_summary.compliance_alerts}</p>
                            )}
                            {selectedRecord.suggestions_summary.tax_saving_opportunities && (
                                <p><strong>Tax Saving Opportunities:</strong> {selectedRecord.suggestions_summary.tax_saving_opportunities}</p>
                            )}
                            {selectedRecord.suggestions_summary.tax_regime_analysis && (
                                <p><strong>Tax Regime Analysis:</strong> {selectedRecord.suggestions_summary.tax_regime_analysis}</p>
                            )}
                        </div>
                    )}

                    {selectedRecord.ml_prediction_summary ? (
                        <div className="section-box">
                            <h5>ML Model Prediction:</h5>
                            {selectedRecord.ml_prediction_summary.predicted_tax_regime && (
                                <p><strong>Predicted Tax Regime:</strong> {selectedRecord.ml_prediction_summary.predicted_tax_regime}</p>
                            )}
                            <p><strong>Predicted Tax Liability:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_tax_liability)}</p>
                            <p className="refund-amount"><strong>Predicted Refund Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_refund_due)}</p>
                            <p className="tax-due-amount"><strong>Predicted Additional Tax Due:</strong> {formatCurrency(selectedRecord.ml_prediction_summary.predicted_additional_due)}</p>
                            {selectedRecord.ml_prediction_summary.notes && (
                                <p><strong>Notes:</strong> {selectedRecord.ml_prediction_summary.notes}</p>
                            )}
                        </div>
                    ) : (
                        <div className="section-box">
                            <p>No AI recommendations or ML predictions available for this record yet. These are generated when you click "Get AI Suggestions & ML Predictions" after uploading documents.</p>
                        </div>
                    )}

                </div>
            )}
        </div>
    );
};

export default TaxHistory;