import React, { useState } from 'react';
import axios from 'axios';
import Header from '../Header'; // Assuming Header is in src/components/Header/index.js
import './index.css'; // Import ContactUs specific CSS

const ContactUs = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: '',
        message: '',
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setMessageType('');
        setLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:5000/contact', formData); // Route is /contact

            if (response.status === 200) {
                setMessage('Your message has been sent successfully! We will get back to you soon.');
                setMessageType('success');
                setFormData({ name: '', email: '', subject: '', message: '' }); // Clear form
            } else {
                setMessage(response.data.message || 'Failed to send message. Please try again.');
                setMessageType('error');
            }
        } catch (error) {
            console.error('Contact form submission error:', error);
            if (error.response) {
                setMessage(error.response.data.message || 'An error occurred. Please check your input.');
            } else {
                setMessage('Network error. Please check your connection and try again.');
            }
            setMessageType('error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Header /> {/* Render Header on the Contact Us page */}
            <div className="contact-container">
                <div className="contact-box section-box">
                    <h2 className="contact-title">Contact Us</h2>
                    <p className="contact-intro">
                        Have questions, feedback, or need support? Fill out the form below, and we'll get back to you as soon as possible.
                    </p>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="name">Your Name</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                                className="form-input"
                                disabled={loading}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="email">Your Email</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                                className="form-input"
                                disabled={loading}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="subject">Subject</label>
                            <input
                                type="text"
                                id="subject"
                                name="subject"
                                value={formData.subject}
                                onChange={handleChange}
                                required
                                className="form-input"
                                disabled={loading}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="message">Message</label>
                            <textarea
                                id="message"
                                name="message"
                                value={formData.message}
                                onChange={handleChange}
                                required
                                className="form-textarea"
                                rows="5"
                                disabled={loading}
                            ></textarea>
                        </div>
                        <button type="submit" className="contact-button" disabled={loading}>
                            {loading ? 'Sending...' : 'Send Message'}
                        </button>
                    </form>

                    {message && (
                        <div className={`message ${messageType}`}>
                            {message}
                        </div>
                    )}

                    <div className="contact-info">
                        <h3>Other Ways to Reach Us</h3>
                        <p><strong>Email:</strong> support@garudatax.ai</p>
                        <p><strong>Phone:</strong> +91 98765 43210</p>
                        <p><strong>Address:</strong> 123 Tax Lane, Financial District, Hyderabad, Telangana, India</p>
                    </div>
                </div>
            </div>
        </>
    );
};

export default ContactUs;
