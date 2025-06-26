import React, { Component } from "react";
import Header from '../Header';
import { withRouter } from "react-router-dom";
import './index.css'; // NEW: Import the CSS file

class Home extends Component {
  render() {
    return (
      <div>
        <Header />
        <div className="home-container">
          {/* Hero Section */}
          <section className="hero-section">
            <h1 className="hero-title">Welcome to Garuda AI – Your Smart Tax Companion</h1>
            <p className="hero-subtitle">
              Maximize your tax savings with intelligent, secure, and hassle-free filing powered by AI.
            </p>
            <div className="cta-buttons">
              <button className="btn-primary" onClick={() => this.props.history.push('/start')}>Start Now</button> {/* Will redirect to TaxUploader */}
              <button className="btn-secondary" onClick={() => this.props.history.push('/about')}>Learn More</button>
            </div>
          </section>

          {/* Features Section */}
          <section className="features-section">
            <h2>Why Choose Garuda AI?</h2>
            <div className="features-grid">
              <div className="feature-card">
                <h3> AI-Powered Tax Filing</h3>
                <p>Automatically extract and compute deductions using intelligent models.</p>
              </div>
              <div className="feature-card">
                <h3> Secure & Private</h3>
                <p>Military-grade encryption ensures your financial data remains safe.</p>
              </div>
              <div className="feature-card">
                <h3> Upload Any Document</h3>
                <p>From Form 16 to salary slips, we support all standard Indian tax formats.</p>
              </div>
              <div className="feature-card">
                <h3> Personalized Insights</h3>
                <p>Get suggestions for exemptions and avoid overpaying taxes.</p>
              </div>
            </div>
          </section>

          {/* How it Works */}
          <section className="how-it-works">
            <h2>How It Works</h2>
            <ol>
              <li><strong>Upload Documents:</strong> Drag and drop Form 16, investment proofs, etc.</li>
              <li><strong>Review Deductions:</strong> Our AI scans and calculates your savings.</li>
              <li><strong>File Easily:</strong> Submit to the IT department in one click or download filled forms.</li>
            </ol>
          </section>

          {/* Footer or Testimonials Placeholder */}
          <section className="call-to-action-final">
            <p>Join thousands of users who trust Garuda AI for simplified tax filing. Let’s get started!</p>
            <button className="btn-primary" onClick={() => this.props.history.push('/start')}>Try Now</button> {/* Will redirect to TaxUploader */}
          </section>
        </div>
      </div>
    );
  }
}
export default withRouter(Home);