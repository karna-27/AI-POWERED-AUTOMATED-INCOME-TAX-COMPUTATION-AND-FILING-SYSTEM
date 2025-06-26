import React, { useState } from 'react';
import Header from '../Header'; // Assuming Header is in src/components/Header/index.js
import TaxUploader from '../TaxUploader'; // Assuming TaxUploader is in src/components/TaxUploader/index.js
import TaxHistory from '../TaxHistory';   // Assuming TaxHistory is in src/components/TaxHistory/index.js
import TaxCalculator from '../TaxCalculator'; // Assuming TaxCalculator is in src/components/TaxCalculator/index.js
import Profile from '../Profile'; // Assuming Profile is in src/components/Profile/index.js
import './index.css'; // Import Dashboard specific CSS

const Dashboard = ({ onLogout }) => {
  // State to manage the currently active content/tab
  const [activeContent, setActiveContent] = useState('upload'); // Default to 'upload'

  // Function to handle navigation clicks
  const handleNavigate = (content) => {
    setActiveContent(content);
  };

  // Render the appropriate component based on activeContent state
  const renderContent = () => {
    switch (activeContent) {
      case 'upload':
        return <TaxUploader />;
      case 'history':
        return <TaxHistory />;
      case 'calculator':
        return <TaxCalculator />;
      case 'profile':
        return <Profile />;
      default:
        return <TaxUploader />; // Fallback
    }
  };

  return (
    <div className="dashboard-container">
      {/* Header for navigation within the dashboard */}
      <Header onLogout={onLogout} onNavigate={handleNavigate} />
      
      <main className="dashboard-main-content">
        {renderContent()}
      </main>
    </div>
  );
};

export default Dashboard;
