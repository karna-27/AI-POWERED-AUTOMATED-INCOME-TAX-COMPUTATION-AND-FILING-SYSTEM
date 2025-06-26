import React, { useState } from 'react';
import axios from 'axios';
import '../index.css'; // For general styling

const ContactUs = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submissionStatus, setSubmissionStatus] = useState(null); // 'success', 'error', 'loading'
  const [responseMessage, setResponseMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmissionStatus('loading');
    setResponseMessage('');

    try {
      const response = await axios.post('http://127.0.0.1:5000/contact', formData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setSubmissionStatus('success');
      setResponseMessage(response.data.message || 'Message sent successfully!');
      setFormData({ name: '', email: '', subject: '', message: '' }); // Clear form
    } catch (error) {
      console.error('Contact form submission error:', error);
      setSubmissionStatus('error');
      setResponseMessage(error.response?.data?.message || 'Failed to send message. Please try again later.');
    }
  };

  return (
    <div className="contact-us-container section-box">
      <h2 className="tax-uploader-title">Get Support</h2>
      <p className="contact-description">
        Have questions or need assistance? Fill out the form below and we'll get back to you as soon as possible.
      </p>

      <form onSubmit={handleSubmit} className="contact-form">
        <div className="form-group">
          <label htmlFor="name" className="tax-uploader-label">Your Name:</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="tax-uploader-input"
            required
            disabled={submissionStatus === 'loading'}
          />
        </div>
        <div className="form-group">
          <label htmlFor="email" className="tax-uploader-label">Your Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="tax-uploader-input"
            required
            disabled={submissionStatus === 'loading'}
          />
        </div>
        <div className="form-group">
          <label htmlFor="subject" className="tax-uploader-label">Subject:</label>
          <input
            type="text"
            id="subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            className="tax-uploader-input"
            required
            disabled={submissionStatus === 'loading'}
          />
        </div>
        <div className="form-group">
          <label htmlFor="message" className="tax-uploader-label">Message:</label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            className="tax-uploader-textarea"
            rows="5"
            required
            disabled={submissionStatus === 'loading'}
          ></textarea>
        </div>

        <button 
          type="submit" 
          className="tax-uploader-button" 
          disabled={submissionStatus === 'loading'}
        >
          {submissionStatus === 'loading' ? 'Sending...' : 'Send Message'}
        </button>
      </form>

      {responseMessage && (
        <div className={`tax-uploader-message ${submissionStatus === 'success' ? 'success' : 'error'}`}>
          {responseMessage}
        </div>
      )}
    </div>
  );
};

export default ContactUs;
