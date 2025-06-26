import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Header from '../Header';
import './index.css'; // NEW: Import the CSS file

const History = () => {
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Helper function to safely format currency values
  const formatCurrency = (value) => {
    // Check if value is null, undefined, or cannot be converted to a finite number
    if (value === null || value === undefined || isNaN(parseFloat(value))) {
      return 'N/A';
    }
    // Convert to number and format
    return parseFloat(value).toLocaleString('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  // Helper function to safely format general numbers
  const formatNumber = (value) => {
    // Check if value is null, undefined, or cannot be converted to a finite number
    if (value === null || value === undefined || isNaN(parseFloat(value))) {
      return 'N/A';
    }
    return parseFloat(value).toLocaleString('en-IN');
  };

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      setError('');
      const jwt_token = Cookies.get('jwt_token');

      if (!jwt_token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      try {
        const config = {
          headers: {
            'Authorization': `Bearer ${jwt_token}`,
          }
        };
        // Changed the API endpoint from '/api/get_tax_history' to '/api/history'
        const response = await axios.get('http://127.0.0.1:5000/api/history', config); 
        
        if (response.data.status === 'success') {
          setHistoryData(response.data.history);
        } else {
          setError(response.data.message || 'Failed to fetch history.');
        }
      } catch (err) {
        console.error('Error fetching history:', err);
        if (err.response) {
          if (err.response.status === 401) {
            setError('Authentication failed. Please log in again.');
          } else if (err.response.status === 404) {
            setError('No history found for your account. Upload some documents first!');
          } else {
            setError(`Server error: ${err.response.data.message || err.response.status}`);
          }
        } else {
          setError('Network error. Could not connect to the server.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  return (
    <>
      <Header />
      <div className="history-container">
        <h2 className="history-title">Tax Computation History</h2>

        {loading && <p className="loading-message">Loading history...</p>}
        {error && <p className="error-message">{error}</p>}

        {!loading && !error && historyData.length === 0 && (
          <p className="no-history-message">No tax computation history found. Upload your documents to see past analyses here!</p>
        )}

        <div className="history-list">
          {historyData.map((record, index) => (
            <div key={record._id || index} className="history-item">
              <h3 className="history-item-title">Record {index + 1}</h3>
              {record.timestamp && (
                <p><strong>Date Processed:</strong> {new Date(record.timestamp).toLocaleString()}</p>
              )}
              {record.user_id && (
                <p><strong>User ID:</strong> {record.user_id}</p>
              )}

              {record.document_processing_summary && record.document_processing_summary.length > 0 && (
                <div className="summary-section">
                  <h4>Document Processing Summary:</h4>
                  {record.document_processing_summary.map((doc, docIndex) => (
                    <div key={docIndex} className="doc-summary-item">
                      <p><strong>File:</strong> {doc.filename || 'N/A'} (<a href={`http://127.0.0.1:5000${doc.stored_path}`} target="_blank" rel="noopener noreferrer">View Stored Document</a>)</p>
                      <p><strong>Status:</strong> <span className={`status-${doc.status || 'unknown'}`}>{doc.status?.toUpperCase() || 'N/A'}</span></p>
                      <p><strong>Identified Type:</strong> {doc.identified_type || 'N/A'}</p>
                      <p><strong>Message:</strong> {doc.message || 'N/A'}</p>
                    </div>
                  ))}
                </div>
              )}

              {record.aggregated_financial_data && (
                <div className="summary-section">
                  <h4>Aggregated Financial Data:</h4>
                  <div className="data-grid">
                    {Object.entries(record.aggregated_financial_data).map(([key, value]) => (
                      <div key={key} className="data-item">
                        <strong>{key}:</strong> {typeof value === 'number' ? formatCurrency(value) : (value || 'N/A')}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {record.final_tax_computation_summary && (
                <div className="summary-section">
                  <h4>Final Tax Computation (Rule-Based):</h4>
                  <p><strong>Calculated Gross Income:</strong> {formatCurrency(record.final_tax_computation_summary.calculated_gross_income)}</p>
                  <p><strong>Calculated Total Deductions:</strong> {formatCurrency(record.final_tax_computation_summary.calculated_total_deductions)}</p>
                  <p><strong>Computed Taxable Income:</strong> {formatCurrency(record.final_tax_computation_summary.computed_taxable_income)}</p>
                  <p><strong>Estimated Tax Payable:</strong> {formatCurrency(record.final_tax_computation_summary.estimated_tax_payable)}</p>
                  <p><strong>Total TDS Credit:</strong> {formatCurrency(record.final_tax_computation_summary.total_tds_credit)}</p>
                  <p><strong>Tax Regime Considered:</strong> <span className="highlight-regime">{record.final_tax_computation_summary.regime_consideration || 'N/A'}</span></p>
                  {record.final_tax_computation_summary.refund_due_from_tax > 0 && (
                    <p className="refund-amount"><strong>Refund Due from Tax:</strong> {formatCurrency(record.final_tax_computation_summary.refund_due_from_tax)}</p>
                  )}
                  {record.final_tax_computation_summary.tax_due_to_government > 0 && (
                    <p className="tax-due-amount"><strong>Tax Due to Government:</strong> {formatCurrency(record.final_tax_computation_summary.tax_due_to_government)}</p>
                  )}
                  {record.final_tax_computation_summary.notes && (
                    <p><strong>Notes:</strong> {record.final_tax_computation_summary.notes}</p>
                  )}
                </div>
              )}

              {record.ml_prediction_summary && (
                <div className="summary-section">
                  <h4>ML Model Prediction:</h4>
                  <p><strong>Predicted Tax Regime:</strong> {record.ml_prediction_summary.predicted_tax_regime || 'N/A'}</p>
                  <p><strong>Predicted Tax Liability:</strong> {formatCurrency(record.ml_prediction_summary.predicted_tax_liability)}</p>
                  <p><strong>Predicted Refund Due:</strong> {formatCurrency(record.ml_prediction_summary.predicted_refund_due)}</p>
                  <p><strong>Predicted Additional Due:</strong> {formatCurrency(record.ml_prediction_summary.predicted_additional_due)}</p>
                  {record.ml_prediction_summary.notes && (
                    <p><strong>Notes:</strong> {record.ml_prediction_summary.notes}</p>
                  )}
                </div>
              )}

              {record.gemini_suggestions && record.gemini_suggestions.length > 0 && (
                <div className="summary-section">
                  <h4>Gemini AI Suggestions:</h4>
                  <ul className="suggestions-list">
                    {record.gemini_suggestions.map((suggestion, suggestionIndex) => (
                      <li key={suggestionIndex}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default History;