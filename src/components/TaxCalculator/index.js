import React, { useState } from 'react';
import './index.css'; // Import TaxCalculator specific CSS

// Helper function to safely parse float
const safeParseFloat = (value) => {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
};

// Helper function to safely format currency values - MOVED OUTSIDE COMPONENT
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

// Helper function to round numbers - MOVED OUTSIDE COMPONENT
const round = (value, decimals) => {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
};


const TaxCalculator = () => {
    const [incomeDetails, setIncomeDetails] = useState({
        grossSalary: '',
        exemptAllowances: '',
        incomeFromHouseProperty: '',
        otherIncome: '',
        capitalGainsLongTerm: '',
        capitalGainsShortTerm: '',
        age: '', // Added age for tax slab consideration
    });

    const [deductionDetails, setDeductionDetails] = useState({
        standardDeduction: '', // Will be auto-applied based on regime
        professionalTax: '',
        interestOnHomeLoan: '',
        deduction80C: '',
        deduction80CCD1B: '',
        deduction80D: '',
        deduction80G: '',
        deduction80TTA: '',
        deduction80TTB: '',
    });

    const [calculationResult, setCalculationResult] = useState(null);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('');

    const handleIncomeChange = (e) => {
        const { name, value } = e.target;
        setIncomeDetails(prev => ({ ...prev, [name]: value }));
    };

    const handleDeductionChange = (e) => {
        const { name, value } = e.target;
        setDeductionDetails(prev => ({ ...prev, [name]: value }));
    };

    const calculateTaxIndiaFY23_24 = (grossIncome, deductions, age, taxRegimeChoice = null) => {
        grossIncome = safeParseFloat(grossIncome);
        deductions = safeParseFloat(deductions);
        age = safeParseFloat(age);

        const isSeniorCitizen = (age >= 60 && age < 80);
        const isSuperSeniorCitizen = (age >= 80);

        // Standard Deduction (applicable only in Old Regime for salaried, and New Regime from FY23-24)
        const standardDeductionAmount = 50000.0;

        // --- Old Regime Calculation ---
        let basicExemptionOld = 250000;
        if (isSeniorCitizen) {
            basicExemptionOld = 300000;
        }
        if (isSuperSeniorCitizen) {
            basicExemptionOld = 500000;
        }

        const totalDeductionsOld = deductions + (grossIncome > 0 ? standardDeductionAmount : 0); // Add standard deduction for old regime
        const taxableIncomeOld = Math.max(0, grossIncome - totalDeductionsOld);
        let taxOld = 0;

        if (taxableIncomeOld <= basicExemptionOld) {
            taxOld = 0;
        } else if (taxableIncomeOld <= 500000) {
            taxOld = (taxableIncomeOld - basicExemptionOld) * 0.05;
        } else if (taxableIncomeOld <= 1000000) {
            taxOld = (500000 - basicExemptionOld) * 0.05 + (taxableIncomeOld - 500000) * 0.20;
        } else {
            taxOld = (500000 - basicExemptionOld) * 0.05 + 500000 * 0.20 + (taxableIncomeOld - 1000000) * 0.30;
        }
        
        // Rebate under Section 87A (Old Regime): Full tax rebate for taxable income up to 5 lakhs
        if (taxableIncomeOld <= 500000) {
            taxOld = 0;
        }

        // --- New Regime Calculation ---
        // Standard deduction is allowed in new regime from FY23-24
        const taxableIncomeNew = Math.max(0, grossIncome - standardDeductionAmount);
        let taxNew = 0;
        
        // New Regime Slabs FY 2023-24 (Default regime)
        if (taxableIncomeNew <= 300000) {
            taxNew = 0;
        } else if (taxableIncomeNew <= 600000) {
            taxNew = (taxableIncomeNew - 300000) * 0.05;
        } else if (taxableIncomeNew <= 900000) {
            taxNew = 15000 + (taxableIncomeNew - 600000) * 0.10;
        } else if (taxableIncomeNew <= 1200000) {
            taxNew = 45000 + (taxableIncomeNew - 900000) * 0.15;
        } else if (taxableIncomeNew <= 1500000) {
            taxNew = 90000 + (taxableIncomeNew - 1200000) * 0.20;
        } else {
            taxNew = 150000 + (taxableIncomeNew - 1500000) * 0.30;
        }

        // Rebate under Section 87A (New Regime): Full tax rebate for taxable income up to 7 lakhs
        if (taxableIncomeNew <= 700000) {
            taxNew = 0;
        }

        // Add 4% Health and Education Cess to both regimes
        taxOld += taxOld * 0.04;
        taxNew += taxNew * 0.04;

        let finalTaxPayable = 0;
        let regimeConsidered = "";
        let computedTaxableIncome = 0;

        if (taxRegimeChoice === "Old Regime") {
            finalTaxPayable = taxOld;
            regimeConsidered = "Old Regime (User Choice)";
            computedTaxableIncome = taxableIncomeOld;
        } else if (taxRegimeChoice === "New Regime") {
            finalTaxPayable = taxNew;
            regimeConsidered = "New Regime (User Choice)";
            computedTaxableIncome = taxableIncomeNew;
        } else { // Optimal choice
            if (taxNew <= taxOld) {
                finalTaxPayable = taxNew;
                regimeConsidered = "New Regime (Optimal)";
                computedTaxableIncome = taxableIncomeNew;
            } else {
                finalTaxPayable = taxOld;
                regimeConsidered = "Old Regime (Optimal)";
                computedTaxableIncome = taxableIncomeOld;
            }
        }

        return {
            taxOldRegime: round(taxOld, 2),
            taxNewRegime: round(taxNew, 2),
            optimalTaxPayable: round(finalTaxPayable, 2),
            optimalRegimeConsidered: regimeConsidered,
            computedTaxableIncomeOld: round(taxableIncomeOld, 2),
            computedTaxableIncomeNew: round(taxableIncomeNew, 2),
        };
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setMessage('');
        setMessageType('');

        // Calculate total gross income from input fields
        const totalGrossIncome = safeParseFloat(incomeDetails.grossSalary) +
                                 safeParseFloat(incomeDetails.incomeFromHouseProperty) +
                                 safeParseFloat(incomeDetails.otherIncome) +
                                 safeParseFloat(incomeDetails.capitalGainsLongTerm) +
                                 safeParseFloat(incomeDetails.capitalGainsShortTerm);

        // Calculate total deductions from input fields (applying basic limits for display)
        const totalDeductions = safeParseFloat(deductionDetails.professionalTax) +
                                Math.min(safeParseFloat(deductionDetails.interestOnHomeLoan), 200000) + // Cap home loan interest
                                Math.min(safeParseFloat(deductionDetails.deduction80C), 150000) + // Cap 80C
                                Math.min(safeParseFloat(deductionDetails.deduction80CCD1B), 50000) + // Cap 80CCD1B
                                safeParseFloat(deductionDetails.deduction80D) + // 80D has complex limits, simplified for now
                                safeParseFloat(deductionDetails.deduction80G) +
                                Math.min(safeParseFloat(deductionDetails.deduction80TTA), 10000) + // Cap 80TTA
                                Math.min(safeParseFloat(deductionDetails.deduction80TTB), 50000); // Cap 80TTB

        if (totalGrossIncome <= 0) {
            setMessage('Please enter a valid Gross Income to calculate tax.');
            setMessageType('error');
            setCalculationResult(null);
            return;
        }

        const result = calculateTaxIndiaFY23_24(totalGrossIncome, totalDeductions, incomeDetails.age);
        setCalculationResult(result);
        setMessage('Tax calculation complete.');
        setMessageType('success');
    };

    return (
        <div className="tax-calculator-container section-box">
            <h2 className="tax-calculator-title">Manual Tax Calculator</h2>
            <form onSubmit={handleSubmit}>
                <div className="calculator-section">
                    <h3>Income Details</h3>
                    <div className="form-group">
                        <label>Gross Salary (Before deductions & exemptions):</label>
                        <input type="number" name="grossSalary" value={incomeDetails.grossSalary} onChange={handleIncomeChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Exempt Allowances (e.g., HRA, LTA - if not part of gross salary):</label>
                        <input type="number" name="exemptAllowances" value={incomeDetails.exemptAllowances} onChange={handleIncomeChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Income from House Property (Net of interest paid):</label>
                        <input type="number" name="incomeFromHouseProperty" value={incomeDetails.incomeFromHouseProperty} onChange={handleIncomeChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Other Income (Interest, Dividend, etc.):</label>
                        <input type="number" name="otherIncome" value={incomeDetails.otherIncome} onChange={handleIncomeChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Long Term Capital Gains:</label>
                        <input type="number" name="capitalGainsLongTerm" value={incomeDetails.capitalGainsLongTerm} onChange={handleIncomeChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Short Term Capital Gains:</label>
                        <input type="number" name="capitalGainsShortTerm" value={incomeDetails.capitalGainsShortTerm} onChange={handleIncomeChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Age (for slab benefits):</label>
                        <input type="number" name="age" value={incomeDetails.age} onChange={handleIncomeChange} className="form-input" min="1" max="120" />
                    </div>
                </div>

                <div className="calculator-section">
                    <h3>Deduction Details (Chapter VI-A & Other)</h3>
                    <p className="note">Note: Standard Deduction of ₹50,000 is automatically applied for salaried individuals in Old Regime, and also in New Regime from FY23-24.</p>
                    <div className="form-group">
                        <label>Professional Tax:</label>
                        <input type="number" name="professionalTax" value={deductionDetails.professionalTax} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Interest on Home Loan (Section 24(b) - Max ₹2 Lakh for self-occupied):</label>
                        <input type="number" name="interestOnHomeLoan" value={deductionDetails.interestOnHomeLoan} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Section 80C Investments (Max ₹1.5 Lakh):</label>
                        <input type="number" name="deduction80C" value={deductionDetails.deduction80C} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Section 80CCD(1B) (NPS - Max ₹50,000):</label>
                        <input type="number" name="deduction80CCD1B" value={deductionDetails.deduction80CCD1B} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Section 80D (Health Insurance):</label>
                        <input type="number" name="deduction80D" value={deductionDetails.deduction80D} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Section 80G (Donations):</label>
                        <input type="number" name="deduction80G" value={deductionDetails.deduction80G} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Section 80TTA (Interest from Savings A/c - Max ₹10,000, not for seniors):</label>
                        <input type="number" name="deduction80TTA" value={deductionDetails.deduction80TTA} onChange={handleDeductionChange} className="form-input" />
                    </div>
                    <div className="form-group">
                        <label>Section 80TTB (Interest for Senior Citizens - Max ₹50,000):</label>
                        <input type="number" name="deduction80TTB" value={deductionDetails.deduction80TTB} onChange={handleDeductionChange} className="form-input" />
                    </div>
                </div>

                <button type="submit" className="calculate-button">Calculate Tax</button>
            </form>

            {message && (
                <div className={`message ${messageType}`}>
                    {message}
                </div>
            )}

            {calculationResult && (
                <div className="calculation-results section-box">
                    <h3>Tax Calculation Results</h3>
                    <div className="result-item">
                        <p><strong>Computed Taxable Income (Old Regime):</strong> {formatCurrency(calculationResult.computedTaxableIncomeOld)}</p>
                        <p><strong>Tax Payable (Old Regime):</strong> {formatCurrency(calculationResult.taxOldRegime)}</p>
                    </div>
                    <div className="result-item">
                        <p><strong>Computed Taxable Income (New Regime):</strong> {formatCurrency(calculationResult.computedTaxableIncomeNew)}</p>
                        <p><strong>Tax Payable (New Regime):</strong> {formatCurrency(calculationResult.taxNewRegime)}</p>
                    </div>
                    <div className="optimal-result">
                        <p><strong>Optimal Tax Payable:</strong> <span className="highlight-amount">{formatCurrency(calculationResult.optimalTaxPayable)}</span></p>
                        <p><strong>Optimal Regime:</strong> <span className="highlight-regime">{calculationResult.optimalRegimeConsidered}</span></p>
                    </div>
                    <p className="notes">
                        Note: This is a simplified calculation for demonstration purposes and does not account for all complex tax rules, surcharges, or specific conditions. Always consult a tax professional for accurate filing.
                    </p>
                </div>
            )}
        </div>
    );
};

export default TaxCalculator;
