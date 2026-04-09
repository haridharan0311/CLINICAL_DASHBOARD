import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const SpikeAlertPanel = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
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

    const getBadgeColor = (severity) => {
        if (severity === 'Critical') return 'bg-danger';
        if (severity === 'High') return 'bg-warning text-dark';
        return 'bg-info text-dark';
    };

    if (loading) return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary text-sm"></div></div>;

    if (alerts.length === 0) {
        return <div className="p-4 text-center text-success fw-medium text-sm">✅ No active outbreaks detected. System nominal.</div>;
    }

    return (
        <div className="card shadow-sm dashboard-card">
            <div className="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
                <h6 className="mb-0 text-dark fw-bold">Active Spike Alerts</h6>
                <span className="badge bg-danger rounded-pill">{alerts.length} New</span>
            </div>
            
            {/* Notice the custom class here that makes the table scrollable! */}
            <div className="card-body scrollable-body">
                <table className="table table-hover table-compact mb-0">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Alert Type</th>
                            <th>Severity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alerts.map((alert) => (
                            <tr key={alert.alert_id}>
                                <td className="text-secondary text-xs fw-medium" style={{ whiteSpace: 'nowrap' }}>
                                    {alert.triggered_date}
                                </td>
                                <td>
                                    <div className="fw-bold text-dark text-sm">
                                        {alert.alert_type.replace('_', ' ')}
                                    </div>
                                    <div className="text-muted text-xs mt-1" style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {alert.trigger_metric}
                                    </div>
                                </td>
                                <td>
                                    <span className={`badge rounded-1 fw-medium ${getBadgeColor(alert.severity)}`}>
                                        {alert.severity}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default SpikeAlertPanel;
