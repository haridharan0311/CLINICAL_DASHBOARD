import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const SpikeAlertPanel = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                // Calls the Django SpikeDetectionView (GET)
                const response = await api.get('spike-detection/');
                setAlerts(response.data);
            } catch (error) {
                console.error("Failed to fetch alerts:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
    }, []);

    // Helper to map severity to Bootstrap colors
    const getBadgeColor = (severity) => {
        if (severity === 'Critical') return 'bg-danger';
        if (severity === 'High') return 'bg-warning text-dark';
        return 'bg-info text-dark';
    };

    if (loading) return <div className="spinner-border text-primary" role="status"></div>;

    if (alerts.length === 0) {
        return <div className="alert alert-success">✅ No active outbreaks detected. System nominal.</div>;
    }

    return (
        <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-bottom-0 pt-4 pb-0">
                <h5 className="mb-0 text-danger fw-bold">
                    <i className="fas fa-exclamation-triangle me-2"></i> Active Spike Alerts
                </h5>
            </div>
            <div className="card-body">
                <div className="list-group list-group-flush">
                    {alerts.map((alert) => (
                        <div key={alert.alert_id} className="list-group-item px-0 py-3 d-flex align-items-start">
                            <div className="ms-2 me-auto">
                                <div className="fw-bold text-dark">
                                    {/* Converts alert_type (e.g., 'Disease_Spike') to readable text */}
                                    {alert.alert_type.replace('_', ' ')}
                                </div>
                                <span className="text-muted small">{alert.trigger_metric}</span>
                                <div className="mt-1 text-secondary" style={{ fontSize: '0.8rem' }}>
                                    Detected: {alert.triggered_date}
                                </div>
                            </div>
                            <span className={`badge rounded-pill ${getBadgeColor(alert.severity)}`}>
                                {alert.severity}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default SpikeAlertPanel;