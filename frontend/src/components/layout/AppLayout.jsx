import React, { useContext } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { FiActivity, FiBox, FiLogOut, FiUser } from 'react-icons/fi'; // Professional icons

const AppLayout = ({ children }) => {
    const { user, logout } = useContext(AuthContext);
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Helper to highlight the active menu item
    const isActive = (path) => location.pathname === path ? 'bg-primary text-white' : 'text-light opacity-75 custom-hover';

    return (
        <div className="d-flex" style={{ height: '100vh', overflow: 'hidden', backgroundColor: '#f4f7f9' }}>
            
            {/* SIDEBAR */}
            <div className="d-flex flex-column flex-shrink-0 p-3 text-white" style={{ width: '260px', backgroundColor: '#0f172a' }}>
                <Link to="/" className="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">
                    <div className="bg-primary text-white rounded p-2 me-2 d-flex align-items-center justify-content-center">
                        <FiActivity size={24} />
                    </div>
                    <span className="fs-5 fw-bold tracking-wide">MedIntel</span>
                </Link>
                <hr className="border-secondary opacity-50" />
                
                <ul className="nav nav-pills flex-column mb-auto mt-2 gap-2">
                    <li className="nav-item">
                        <Link to="/dashboard" className={`nav-link d-flex align-items-center gap-3 py-3 rounded-3 transition ${isActive('/dashboard')}`}>
                            <FiActivity size={20} />
                            <span className="fw-medium">Command Center</span>
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link to="/inventory" className={`nav-link d-flex align-items-center gap-3 py-3 rounded-3 transition ${isActive('/inventory')}`}>
                            <FiBox size={20} />
                            <span className="fw-medium">Inventory</span>
                        </Link>
                    </li>
                </ul>

                <hr className="border-secondary opacity-50" />
                <div className="dropdown">
                    <div className="d-flex align-items-center text-white text-decoration-none px-2 py-1">
                        <div className="bg-secondary rounded-circle me-3 d-flex align-items-center justify-content-center" style={{width: '35px', height: '35px'}}>
                            <FiUser />
                        </div>
                        <div className="d-flex flex-column">
                            <strong className="small">{user?.name}</strong>
                            <span className="small text-info opacity-75">{user?.role_type}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* MAIN CONTENT AREA */}
            <div className="d-flex flex-column flex-grow-1" style={{ overflowY: 'auto' }}>
                {/* TOP HEADER */}
                <header className="bg-white border-bottom px-4 py-3 d-flex justify-content-between align-items-center sticky-top" style={{ zIndex: 10 }}>
                    <h5 className="mb-0 text-dark fw-bold" style={{ textTransform: 'capitalize' }}>
                        {location.pathname.replace('/', '').replace('-', ' ')}
                    </h5>
                    <button className="btn btn-sm btn-light text-danger fw-medium d-flex align-items-center gap-2 border" onClick={handleLogout}>
                        <FiLogOut /> Logout
                    </button>
                </header>

                {/* PAGE CONTENT */}
                <main className="p-4 flex-grow-1">
                    {children}
                </main>
            </div>
            
            {/* Inline style for the hover effect missing in raw bootstrap */}
            <style>{`
                .custom-hover:hover { opacity: 1 !important; background-color: rgba(255,255,255,0.05); }
                .transition { transition: all 0.2s; }
            `}</style>
        </div>
    );
};

export default AppLayout;