import React from 'react';

const MetricCard = ({ title, value, subtext, icon, colorClass, highlight }) => {
    return (
        <div className={`card shadow-sm h-100 dashboard-card border-0 border-start border-4 ${colorClass}`}>
            <div className="card-body p-4 d-flex align-items-center justify-content-between">
                <div>
                    <p className="text-muted text-xs text-uppercase fw-bold mb-1 letter-spacing-wide">{title}</p>
                    <h3 className="fw-bold mb-1 text-dark">{value}</h3>
                    {subtext && (
                        <p className={`mb-0 text-sm fw-medium ${highlight ? 'text-danger' : 'text-secondary'}`}>
                            {subtext}
                        </p>
                    )}
                </div>
                <div className={`p-3 rounded-circle bg-light ${colorClass.replace('border-', 'text-')}`}>
                    {icon}
                </div>
            </div>
        </div>
    );
};

export default MetricCard;