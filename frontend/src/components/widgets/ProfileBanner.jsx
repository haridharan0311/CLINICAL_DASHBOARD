import React, { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { FiUser, FiMapPin, FiShield } from 'react-icons/fi';

const ProfileBanner = () => {
    const { user } = useContext(AuthContext);

    if (!user) return null;

    return (
        <div className="card shadow-sm border-0 mb-4 bg-white dashboard-card" style={{ height: 'auto' }}>
            <div className="card-body d-flex justify-content-between align-items-center p-4">
                <div className="d-flex align-items-center gap-4">
                    {/* Avatar */}
                    <div className="bg-light rounded-circle d-flex justify-content-center align-items-center shadow-sm" style={{ width: '60px', height: '60px' }}>
                        <FiUser size={28} className="text-primary" />
                    </div>
                    {/* User Info */}
                    <div>
                        <h4 className="fw-bold mb-1 text-dark">Welcome back, Dr. {user.name}</h4>
                        <div className="d-flex gap-3 text-muted text-sm fw-medium">
                            <span className="d-flex align-items-center gap-1"><FiShield className="text-info"/> Role: {user.role_type.replace('_', ' ')}</span>
                            <span className="d-flex align-items-center gap-1"><FiMapPin className="text-danger"/> Location: {user.clinic_name} ({user.clinic_id || 'HQ'})</span>
                        </div>
                    </div>
                </div>
                {/* System Status */}
                <div className="text-end d-none d-md-block">
                    <div className="text-xs text-muted text-uppercase fw-bold letter-spacing-wide mb-1">System Status</div>
                    <span className="badge bg-success bg-opacity-10 text-success border border-success fw-bold px-3 py-2 rounded-pill">
                        <span className="spinner-grow spinner-grow-sm me-2 text-success" style={{width: '8px', height: '8px'}} aria-hidden="true"></span>
                        Live Sync Active
                    </span>
                </div>
            </div>
        </div>
    );
};

export default ProfileBanner;
