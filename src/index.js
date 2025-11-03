import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // This will be your global.css content
import App from './App'; // Import our App component

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App /> {/* Render our App component */}
  </React.StrictMode>
);