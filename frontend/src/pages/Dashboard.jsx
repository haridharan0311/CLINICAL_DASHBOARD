import React, { useState, useEffect, useContext } from 'react';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import ProfileBanner from '../components/widgets/ProfileBanner';
import MetricCard from '../components/widgets/MetricCard';
import TrendLineChart from '../components/charts/TrendLineChart';
import SpikeAlertPanel from '../components/widgets/SpikeAlertPanel';
import RestockTable from '../components/widgets/RestockTable';
import { FiUsers, FiAlertTriangle, FiCheckCircle, FiPackage, FiTrendingUp, FiActivity } from 'react-icons/fi';

const Dashboard = () => {
    const { user } = useContext(AuthContext);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const response = await api.get('dashboard-summary/');
                setSummary(response.data);
            } catch (err) {
                console.error("Failed to load summary", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSummary();
    }, []);

    if (loading || !summary) return <div className="text-center p-5"><div className="spinner-border text-primary"></div></div>;

    // ==========================================
    // VIEW 1: PHARMACIST WORKSPACE
    // ==========================================
    if (user.role_type === 'Pharmacist') {
        return (
            <div className="container-fluid px-0">
                <ProfileBanner />
                <div className="row g-4 mb-4">
                    <div className="col-md-4">
                        <MetricCard title="Total Low Stock Items" value={summary.inventory.low_stock_total} subtext="Requires ordering" icon={<FiPackage size={24}/>} colorClass="border-warning" highlight={true} />
                    </div>
                    <div className="col-md-4">
                        <MetricCard title="Critical Depletion" value={summary.inventory.critical} subtext="Stock < 10 units" icon={<FiAlertTriangle size={24}/>} colorClass="border-danger" highlight={true} />
                    </div>
                    <div className="col-md-4">
                        <MetricCard title="Resolved Orders" value="12" subtext="Shipments received this week" icon={<FiCheckCircle size={24}/>} colorClass="border-success" />
                    </div>
                </div>
                <div className="card shadow-sm border-0 dashboard-card" style={{ height: 'auto' }}>
                    <div className="card-header bg-white border-bottom py-3"><h6 className="mb-0 fw-bold text-dark">Automated Restock Intelligence (AI Projected)</h6></div>
                    <div className="card-body p-0"><RestockTable /></div>
                </div>
            </div>
        );
    }

    // ==========================================
    // VIEW 2: DOCTOR WORKSPACE
    // ==========================================
    if (user.role_type === 'Doctor') {
        return (
            <div className="container-fluid px-0">
                <ProfileBanner />
                <div className="row g-4 mb-4">
                    <div className="col-md-4">
                        <MetricCard title="My Patient Cases Today" value={summary.cases.today} subtext="Active clinic visits" icon={<FiUsers size={24}/>} colorClass="border-primary" />
                    </div>
                    <div className="col-md-4">
                        <MetricCard title="Primary Local Disease" value={summary.cases.top_disease_30d} subtext="Highest volume in your clinic" icon={<FiActivity size={24}/>} colorClass="border-info" />
                    </div>
                    <div className="col-md-4">
                        <MetricCard title="Local Anomalies" value={summary.spikes.active_total} subtext="Spikes requiring attention" icon={<FiAlertTriangle size={24}/>} colorClass="border-danger" highlight={summary.spikes.active_total > 0} />
                    </div>
                </div>
                
                {/* STACKED FULL-WIDTH LAYOUT */}
                <div className="row g-4">
                    <div className="col-12">
                        <TrendLineChart />
                    </div>
                    <div className="col-12">
                        <SpikeAlertPanel />
                    </div>
                </div>
            </div>
        );
    }

    // ==========================================
    // VIEW 3: SUPER ADMIN / CLINIC ADMIN WORKSPACE
    // ==========================================
    return (
        <div className="container-fluid px-0">
            <ProfileBanner />
            <div className="row g-4 mb-4">
                <div className="col-xl-3 col-sm-6">
                    <MetricCard title="Statewide Cases Today" value={summary.cases.today} subtext={`${summary.cases.this_week} this week`} icon={<FiUsers size={24}/>} colorClass="border-primary" />
                </div>
                <div className="col-xl-3 col-sm-6">
                    <MetricCard title="Statewide Top Disease" value={summary.cases.top_disease_30d} subtext="AI tracking active spread" icon={<FiTrendingUp size={24}/>} colorClass="border-info" />
                </div>
                <div className="col-xl-3 col-sm-6">
                    <MetricCard title="Active Outbreak Clusters" value={summary.spikes.active_total} subtext={`${summary.spikes.breakdown['Critical'] || 0} Critical Level`} icon={<FiAlertTriangle size={24}/>} colorClass="border-danger" highlight={summary.spikes.active_total > 0} />
                </div>
                <div className="col-xl-3 col-sm-6">
                    <MetricCard title="Supply Chain Warnings" value={summary.inventory.low_stock_total} subtext="Clinics reporting shortages" icon={<FiPackage size={24}/>} colorClass="border-warning" highlight={true} />
                </div>
            </div>

            {/* STACKED FULL-WIDTH LAYOUT */}
            <div className="row g-4">
                <div className="col-12">
                    <TrendLineChart />
                </div>
                <div className="col-12">
                    <SpikeAlertPanel />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
