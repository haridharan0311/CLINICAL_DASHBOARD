import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  PointElement, LineElement, Title, Tooltip, Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import api from '../../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend
);

const TrendLineChart = () => {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrends = async () => {
            try {
                // Fetch the last 30 days of data
                const response = await api.get('disease-trends/?days=30');
                const rawData = response.data;

                if (rawData.length === 0) {
                    setChartData(null);
                    setLoading(false);
                    return;
                }

                // 1. Extract unique dates for the X-axis and sort them
                const uniqueDates = [...new Set(rawData.map(item => item.date))].sort();

                // 2. Group cases by disease
                const diseases = {};
                rawData.forEach(item => {
                    if (!diseases[item.disease_name]) {
                        diseases[item.disease_name] = {};
                    }
                    diseases[item.disease_name][item.date] = item.cases;
                });


                // NEW: Find the Top 5 Diseases to prevent the "Spaghetti Chart" effect
                const diseaseTotals = Object.keys(diseases).map(name => {
                    const totalCases = Object.values(diseases[name]).reduce((sum, cases) => sum + cases, 0);
                    return { name, totalCases };
                });
                
                // Sort descending and slice the top 5
                const top5Diseases = diseaseTotals.sort((a, b) => b.totalCases - a.totalCases).slice(0, 5).map(d => d.name);

                const colors = ['#0d6efd', '#dc3545', '#198754', '#6f42c1', '#fd7e14'];

                // Format into Chart.js datasets, FILTERING only for the Top 5
                const datasets = top5Diseases.map((diseaseName, index) => {
                    return {
                        label: diseaseName,
                        data: uniqueDates.map(date => diseases[diseaseName][date] || 0),
                        borderColor: colors[index % colors.length],
                        backgroundColor: colors[index % colors.length],
                        borderWidth: 1, 
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        tension: 0.4,
                    };
                });

                setChartData({
                    labels: uniqueDates,
                    datasets: datasets
                });

            } catch (error) {
                console.error("Failed to fetch trends:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTrends();
    }, []);

    const options = {
        responsive: true,
        maintainAspectRatio: false, // CRITICAL: Allows the chart to fill our custom container height
        interaction: { mode: 'index', intersect: false }, // Better tooltip behavior
        plugins: {
            legend: { 
                position: 'bottom', 
                labels: { boxWidth: 12, usePointStyle: true, font: { size: 11 } } 
            },
            title: { display: false }, // We handle the title in our own HTML header
        },
        scales: {
            y: { 
                beginAtZero: true, 
                grid: { color: '#f1f5f9' }, // Very faint grid lines
                ticks: { font: { size: 11 }, color: '#64748b' }
            },
            x: { 
                grid: { display: false }, // Remove vertical grid lines completely for a cleaner look
                ticks: { maxTicksLimit: 10, font: { size: 10 }, color: '#94a3b8' } 
            }
        }
    };

    if (loading) return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary"></div></div>;
    if (!chartData) return <div className="alert alert-light text-sm p-3">No trend data available.</div>;

    return (
        <div className="card shadow-sm dashboard-card">
            <div className="card-header bg-white border-bottom py-3">
                <h6 className="mb-0 text-dark fw-bold">30-Day Disease Case Trends</h6>
            </div>
            <div className="card-body chart-wrapper">
                <Line options={options} data={chartData} />
            </div>
        </div>
    );
};

export default TrendLineChart;
