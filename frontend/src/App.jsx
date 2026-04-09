import React, { useContext } from 'react';
// FIX 1: We added useNavigate to the imports
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';

import Login from './pages/Login';
import Inventory from './pages/Inventory';
import TrendLineChart from './components/charts/TrendLineChart';
import SpikeAlertPanel from './components/widgets/SpikeAlertPanel';

// ---------------------------------------------------------
// NEW: The "Bouncer" Component (Protected Route)
// ---------------------------------------------------------
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useContext(AuthContext);

    // Wait for the AuthContext to finish checking localStorage
    if (loading) {
        return <div className="text-center mt-5"><div className="spinner-border text-primary"></div></div>;
    }

    // If there is no user logged in, forcefully redirect to the Login page
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // If they are logged in, let them see the page!
    return children;
};

// ---------------------------------------------------------
// 1. Navigation Bar Component
// ---------------------------------------------------------
const Navigation = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate(); // Hook to programmatically change pages

    if (!user) return null; 

    // FIX 2: Trigger logout AND change the page
    const handleLogout = () => {
        logout();
        navigate('/login'); 
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4 shadow-sm">
            <div className="container">
                <span className="navbar-brand fw-bold text-info">MedIntel</span>
                <div className="navbar-nav me-auto">
                    <Link className="nav-link" to="/dashboard">Command Center</Link>
                    <Link className="nav-link" to="/inventory">Inventory</Link>
                </div>
                <div className="navbar-nav">
                    <span className="nav-item nav-link text-light me-3">
                        Logged in as: <span className="fw-bold">{user.name}</span> ({user.role_type})
                    </span>
                    {/* Call our new handleLogout function */}
                    <button className="btn btn-sm btn-outline-light mt-1 mb-1" onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
};

// ---------------------------------------------------------
// 2. Dashboard Component
// ---------------------------------------------------------
const Dashboard = () => (
    <div className="container mt-4">
        <h2 className="mb-4 fw-bold text-secondary">Command Center</h2>
        <div className="row g-4">
            <div className="col-lg-8">
                <TrendLineChart />
            </div>
            <div className="col-lg-4">
                <SpikeAlertPanel />
            </div>
        </div>
    </div>
);

// ---------------------------------------------------------
// 3. Main App Routing
// ---------------------------------------------------------
function App() {
    return (
        <AuthProvider>
            <Router>
                <Navigation />
                <Routes>
                    <Route path="/login" element={<Login />} />
                    
                    {/* FIX 3: Wrap our secure pages in the ProtectedRoute Bouncer */}
                    <Route 
                        path="/dashboard" 
                        element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        } 
                    />
                    
                    <Route 
                        path="/inventory" 
                        element={
                            <ProtectedRoute>
                                <Inventory />
                            </ProtectedRoute>
                        } 
                    />
                    
                    {/* Default route catches all and sends to dashboard (which will kick them to login if needed) */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;

