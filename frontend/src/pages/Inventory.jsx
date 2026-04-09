import React from 'react';
import RestockTable from '../components/widgets/RestockTable';
import api from '../services/api';

const Inventory = () => {

    // Function to trigger the CSV download from Django
    const handleExportCSV = async () => {
        try {
            // We use responseType: 'blob' because we are downloading a file, not JSON
            const response = await api.get('export/?type=restock', { responseType: 'blob' });
            
            // Create a fake link in the browser to force the file download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'restock_report.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error exporting CSV:", error);
            alert("Failed to export CSV. Please try again.");
        }
    };

    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="fw-bold text-secondary">Inventory Intelligence</h2>
                <button className="btn btn-outline-success fw-bold" onClick={handleExportCSV}>
                    <i className="fas fa-file-csv me-2"></i> Export Order to CSV
                </button>
            </div>

            <div className="card shadow-sm border-0">
                <div className="card-header bg-white border-bottom-0 pt-4 pb-2">
                    <h5 className="mb-0 text-primary fw-bold">
                        AI Restock Suggestions
                    </h5>
                    <p className="text-muted small mt-1 mb-0">
                        Drugs currently below the minimum safety buffer, cross-referenced with 30-day predictive demand.
                    </p>
                </div>
                <div className="card-body">
                    <RestockTable />
                </div>
            </div>
        </div>
    );
};

export default Inventory;