import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import './index.css'; // Import Profile specific CSS

const Profile = () => {
    const [userData, setUserData] = useState({
        username: '',
        email: '',
        fullName: '',
        pan: '',
        aadhaar: '',
        address: '',
        phone: '',
    });
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState(''); // 'info', 'success', 'error'

    useEffect(() => {
        const fetchProfile = async () => {
            setLoading(true);
            setMessage('Fetching your profile data...');
            setMessageType('info');
            const jwt_token = Cookies.get('jwt_token');

            try {
                const config = {
                    headers: {
                        'Authorization': `Bearer ${jwt_token}`,
                    }
                };
                const response = await axios.get('http://127.0.0.1:5000/api/profile', config); // Route is /profile

                if (response.data.user) {
                    setUserData({
                        username: response.data.user.username || '',
                        email: response.data.user.email || '',
                        fullName: response.data.user.full_name || '',
                        pan: response.data.user.pan || '',
                        aadhaar: response.data.user.aadhaar || '',
                        address: response.data.user.address || '',
                        phone: response.data.user.phone || '',
                    });
                    setMessage('Profile loaded successfully.');
                    setMessageType('success');
                } else {
                    setMessage(response.data.message || 'Failed to fetch profile data.');
                    setMessageType('error');
                }
            } catch (error) {
                console.error('Fetch profile error:', error);
                if (error.response) {
                    if (error.response.status === 401) {
                        setMessage('Authentication required. Please log in.');
                    } else if (error.response.data && error.response.data.message) {
                        setMessage(`Error: ${error.response.data.message}`);
                    } else {
                        setMessage(`Server responded with status ${error.response.status}`);
                    }
                } else {
                    setMessage('An error occurred while fetching profile. Check network connection and backend server.');
                }
                setMessageType('error');
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []); // Empty dependency array means this runs once on mount

    const handleChange = (e) => {
        const { name, value } = e.target;
        setUserData(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = async () => {
        setMessage('');
        setMessageType('');
        setLoading(true); // Re-use loading for save operation

        const jwt_token = Cookies.get('jwt_token');
        const config = {
            headers: {
                'Authorization': `Bearer ${jwt_token}`,
                'Content-Type': 'application/json',
            }
        };

        try {
            const response = await axios.put('http://127.0.0.1:5000/profile', userData, config); // Route is /profile

            if (response.status === 200) {
                setMessage('Profile updated successfully!');
                setMessageType('success');
                setIsEditing(false); // Exit edit mode
            } else {
                setMessage(response.data.message || 'Failed to update profile.');
                setMessageType('error');
            }
        } catch (error) {
            console.error('Save profile error:', error);
            if (error.response) {
                if (error.response.status === 401) {
                    setMessage('Authentication required. Please log in.');
                } else if (error.response.data && error.response.data.message) {
                    setMessage(`Error: ${error.response.data.message}`);
                } else {
                    setMessage(`Server responded with status ${error.response.status}`);
                }
            } else {
                setMessage('An error occurred while saving profile. Check network connection and backend server.');
            }
            setMessageType('error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="profile-container section-box">
            <h2 className="profile-title">Your Profile</h2>

            {loading && (
                <div className="profile-loading">
                    <div className="profile-spinner"></div>
                    {message}
                </div>
            )}

            {message && !loading && (
                <div className={`profile-message ${messageType}`}>
                    {message}
                </div>
            )}

            {!loading && (
                <div className="profile-details">
                    <div className="profile-group">
                        <label>Username:</label>
                        <p>{userData.username}</p>
                    </div>
                    <div className="profile-group">
                        <label htmlFor="email">Email:</label>
                        {isEditing ? (
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={userData.email}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        ) : (
                            <p>{userData.email || 'N/A'}</p>
                        )}
                    </div>
                    <div className="profile-group">
                        <label htmlFor="fullName">Full Name:</label>
                        {isEditing ? (
                            <input
                                type="text"
                                id="fullName"
                                name="fullName"
                                value={userData.fullName}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        ) : (
                            <p>{userData.fullName || 'N/A'}</p>
                        )}
                    </div>
                    <div className="profile-group">
                        <label htmlFor="pan">PAN:</label>
                        {isEditing ? (
                            <input
                                type="text"
                                id="pan"
                                name="pan"
                                value={userData.pan}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        ) : (
                            <p>{userData.pan || 'N/A'}</p>
                        )}
                    </div>
                    <div className="profile-group">
                        <label htmlFor="aadhaar">Aadhaar:</label>
                        {isEditing ? (
                            <input
                                type="text"
                                id="aadhaar"
                                name="aadhaar"
                                value={userData.aadhaar}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        ) : (
                            <p>{userData.aadhaar || 'N/A'}</p>
                        )}
                    </div>
                    <div className="profile-group">
                        <label htmlFor="address">Address:</label>
                        {isEditing ? (
                            <textarea
                                id="address"
                                name="address"
                                value={userData.address}
                                onChange={handleChange}
                                className="profile-textarea"
                                rows="3"
                            ></textarea>
                        ) : (
                            <p>{userData.address || 'N/A'}</p>
                        )}
                    </div>
                    <div className="profile-group">
                        <label htmlFor="phone">Phone Number:</label>
                        {isEditing ? (
                            <input
                                type="tel"
                                id="phone"
                                name="phone"
                                value={userData.phone}
                                onChange={handleChange}
                                className="profile-input"
                            />
                        ) : (
                            <p>{userData.phone || 'N/A'}</p>
                        )}
                    </div>

                    <div className="profile-actions">
                        {isEditing ? (
                            <>
                                <button onClick={handleSave} className="profile-button save-button" disabled={loading}>
                                    {loading ? 'Saving...' : 'Save Changes'}
                                </button>
                                <button onClick={() => setIsEditing(false)} className="profile-button cancel-button" disabled={loading}>
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <button onClick={() => setIsEditing(true)} className="profile-button edit-button">
                                Edit Profile
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;
