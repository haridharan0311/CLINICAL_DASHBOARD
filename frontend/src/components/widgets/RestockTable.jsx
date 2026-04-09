import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { FiPlus } from 'react-icons/fi';

const RestockTable = ({ onRestockAction }) => {
    const [restockData, setRestockData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRestockData = async () => {
            try {
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

    if (loading) return <div className="p-4 text-center"><div className="spinner-border text-primary"></div></div>;

    return (
        <div className="table-responsive" style={{ maxHeight: '600px' }}>
            <table className="table table-hover align-middle table-compact mb-0">
                <thead className="table-light sticky-top">
                    <tr>
                        <th style={{ minWidth: '150px' }}>Drug Name</th>
                        <th>Category</th>
                        <th className="text-center">Stock</th>
                        <th className="text-center">Buffer</th>
                        <th className="text-center">Demand</th>
                        <th className="text-center">Suggest</th>
                        <th>Status</th>
                        <th className="text-center bg-light sticky-right" style={{ borderLeft: '1px solid #dee2e6' }}>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {restockData.map((drug) => (
                        <tr key={drug.drug_id}>
                            <td className="fw-bold text-sm">
                                {drug.brand_name}
                                <span className="text-muted text-xs d-block">{drug.drug_id}</span>
                            </td>
                            <td className="text-xs text-secondary">{drug.category}</td>
                            <td className={`text-center fw-bold ${drug.current_stock_level < drug.minimum_safety_buffer ? 'text-danger' : ''}`}>
                                {drug.current_stock_level}
                            </td>
                            <td className="text-center text-muted text-xs">{drug.minimum_safety_buffer}</td>
                            <td className="text-center text-xs">{drug.predicted_demand}</td>
                            <td className="text-center fw-bold text-primary text-sm">+{drug.suggested_restock_quantity}</td>
                            <td>
                                <span className={`badge ${drug.needs_urgent_restock ? 'bg-danger' : 'bg-warning text-dark'} text-xs px-2 py-1`}>
                                    {drug.needs_urgent_restock ? 'Critical' : 'Low'}
                                </span>
                            </td>
                            <td className="text-center bg-light sticky-right" style={{ borderLeft: '1px solid #dee2e6' }}>
                                <button 
                                    className="btn btn-primary btn-sm fw-bold px-3 py-1 shadow-sm d-flex align-items-center gap-1 mx-auto"
                                    onClick={() => onRestockAction(drug)}
                                    style={{ fontSize: '11px' }}
                                >
                                    <FiPlus size={14} /> Restock
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <style>{`
                .sticky-right {
                    position: sticky;
                    right: 0;
                    z-index: 2;
                }
                .table-compact td { padding: 0.5rem !important; }
                .text-xs { font-size: 0.75rem !important; }
            `}</style>
        </div>
    );
};

export default RestockTable;

