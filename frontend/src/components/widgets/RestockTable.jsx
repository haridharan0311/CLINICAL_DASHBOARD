import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const RestockTable = () => {
    const [restockData, setRestockData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRestockData = async () => {
            try {
                // Calls the Django RestockSuggestionView
                const response = await api.get('restock-suggestions/');
                setRestockData(response.data);
            } catch (error) {
                console.error("Failed to fetch restock suggestions:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchRestockData();
    }, []);

    if (loading) return <div className="spinner-border text-primary" role="status"></div>;

    if (restockData.length === 0) {
        return <div className="alert alert-success">✅ All drug stocks are currently above safety buffers.</div>;
    }

    return (
        <div className="table-responsive">
            <table className="table table-hover align-middle">
                <thead className="table-light">
                    <tr>
                        <th>Drug Name</th>
                        <th>Category</th>
                        <th className="text-center">Current Stock</th>
                        <th className="text-center">Safety Buffer</th>
                        <th className="text-center">30-Day Predicted Demand</th>
                        <th className="text-center">Suggested Order</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {restockData.map((drug) => (
                        <tr key={drug.drug_id} className={drug.needs_urgent_restock ? "table-danger" : ""}>
                            <td className="fw-bold">{drug.brand_name} <span className="text-muted small d-block">{drug.drug_id}</span></td>
                            <td>{drug.category}</td>
                            <td className="text-center fw-bold text-danger">{drug.current_stock_level}</td>
                            <td className="text-center text-secondary">{drug.minimum_safety_buffer}</td>
                            <td className="text-center">{drug.predicted_demand}</td>
                            <td className="text-center fw-bold text-primary">+{drug.suggested_restock_quantity}</td>
                            <td>
                                {drug.needs_urgent_restock ? (
                                    <span className="badge bg-danger">Critical Low</span>
                                ) : (
                                    <span className="badge bg-warning text-dark">Below Buffer</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default RestockTable;
