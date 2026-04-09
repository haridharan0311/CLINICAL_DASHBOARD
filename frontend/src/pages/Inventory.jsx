import React, { useState } from 'react';
import RestockTable from '../components/widgets/RestockTable';
import api from '../services/api';
import { FiFileText, FiPlus, FiBox, FiArrowLeft, FiX } from 'react-icons/fi';

const Inventory = () => {
    // --- State Management ---
    const [showRestockForm, setShowRestockForm] = useState(false);
    const [selectedDrug, setSelectedDrug] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);
    // FIX 1: Added the missing state for nextBatch
    const [nextBatch, setNextBatch] = useState('');

    // 1. When the user clicks "Restock", fetch the ID automatically
    const initiateRestock = async (drug) => {
        setSelectedDrug(drug);
        try {
            const response = await api.get(`inventory/next-batch/?drug_id=${drug.drug_id}`);
            setNextBatch(response.data.next_batch); 
            setShowRestockForm(true);
        } catch (err) {
            console.error("Error generating batch ID", err);
            alert("System could not generate a batch ID. Check if Django server is running.");
        }
    };

    const handleRestockSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        const formData = new FormData(e.target);
        
        const data = {
            drug_id: selectedDrug.drug_id,
            batch_number: nextBatch, // FIX: Use the state variable correctly
            expiry_date: formData.get('expiry_date'),
            quantity: formData.get('quantity')
        };

        try {
            const response = await api.post('inventory/restock/', data);
            
            // Success feedback
            console.log("Response:", response.data);
            setShowRestockForm(false);
            setSelectedDrug(null);
            
            // This key change forces the table to refresh with NEW stock values
            setRefreshKey(prev => prev + 1); 
            alert("Stock levels updated and batch recorded!");
        } catch (err) {
            console.error("Restock failed", err);
            // Better error messaging
            alert(err.response?.data?.error || "Submission failed. Please check if data is valid.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleExportCSV = async () => {
        try {
            const response = await api.get('export/?type=restock', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `restock_report_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error exporting CSV:", error);
        }
    };

    return (
        <div className="container-fluid px-0 animate-fade-in">
            {/* --- HEADER SECTION --- */}
            <div className="d-flex justify-content-between align-items-end mb-4 bg-white p-4 rounded shadow-sm border-start border-primary border-4">
                <div>
                    <div className="d-flex align-items-center gap-2 mb-1">
                        <FiBox className="text-primary" size={20} />
                        <h2 className="fw-bold text-dark mb-0">Inventory Intelligence</h2>
                    </div>
                    <p className="text-muted text-sm mb-0">AI-driven stock optimization and batch management system.</p>
                </div>
                <button className="btn btn-outline-primary btn-sm fw-bold d-flex align-items-center gap-2 px-3 py-2" onClick={handleExportCSV}>
                    <FiFileText /> Export Order List
                </button>
            </div>

            {/* --- DATA TABLE SECTION --- */}
            <div className="card shadow-sm border-0">
                <div className="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
                    <h6 className="mb-0 fw-bold text-secondary">Urgent Procurement Queue</h6>
                    <span className="badge bg-light text-primary border border-primary border-opacity-25 px-3 py-1 text-xs">
                        Real-time Sync
                    </span>
                </div>
                <div className="card-body p-0 overflow-hidden">
                    <RestockTable key={refreshKey} onRestockAction={initiateRestock} />
                </div>
            </div>

            {/* --- RESTOCK MODAL --- */}
            {showRestockForm && (
                <div className="custom-modal-wrapper">
                    <div className="custom-modal-content animate-slide-up">
                        <div className="modal-header-custom">
                            <h5 className="fw-bold mb-0">Receive Stock Batch</h5>
                            <button className="btn-close-custom" onClick={() => setShowRestockForm(false)}><FiX /></button>
                        </div>
                        
                        <form onSubmit={handleRestockSubmit}>
                            <div className="modal-body-custom">
                                <div className="drug-selection-banner mb-4">
                                    <label className="text-xs fw-bold text-primary text-uppercase">Inventory Item</label>
                                    <div className="d-flex justify-content-between align-items-center">
                                        <span className="fw-bold h6 mb-0 text-dark">{selectedDrug?.brand_name}</span>
                                        <span className="badge bg-dark bg-opacity-10 text-dark text-xs">{selectedDrug?.drug_id}</span>
                                    </div>
                                </div>

                                <div className="row g-3">
                                    <div className="col-12">
                                        <label className="form-label fw-bold text-xs text-uppercase">Assigned Batch ID</label>
                                        <input 
                                            type="text" 
                                            className="form-control bg-light border-0 fw-bold text-primary" 
                                            value={nextBatch} 
                                            readOnly 
                                        />
                                        <small className="text-muted">Generated automatically based on database records.</small>
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label text-xs fw-bold text-secondary text-uppercase">Quantity (Units)</label>
                                        <input type="number" name="quantity" className="form-control bg-light border-0 py-2" min="1" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label text-xs fw-bold text-secondary text-uppercase">Expiry Date</label>
                                        <input type="date" name="expiry_date" className="form-control bg-light border-0 py-2" required />
                                    </div>
                                </div>
                            </div>

                            <div className="modal-footer-custom">
                                <button type="button" className="btn btn-link text-decoration-none text-secondary fw-bold" onClick={() => setShowRestockForm(false)}>Cancel</button>
                                <button type="submit" className="btn btn-primary px-4 fw-bold shadow-sm" disabled={isSubmitting}>
                                    {isSubmitting ? 'Updating System...' : 'Finalize Entry'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <style>{`
                .animate-fade-in { animation: fadeIn 0.3s ease-in; }
                .animate-slide-up { animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
                .custom-modal-wrapper { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
                .custom-modal-content { background: white; width: 450px; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden; }
                .modal-header-custom { padding: 20px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
                .modal-body-custom { padding: 24px; }
                .modal-footer-custom { padding: 16px 24px; background: #f8fafc; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 12px; }
                .drug-selection-banner { background: #eff6ff; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #3b82f6; }
                .btn-close-custom { background: none; border: none; color: #64748b; font-size: 20px; }
                .text-xs { font-size: 0.7rem; letter-spacing: 0.025em; }
            `}</style>
        </div>
    );
};

export default Inventory;
