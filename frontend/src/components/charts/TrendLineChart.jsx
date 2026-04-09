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

                // 3. Generate distinct colors for the lines
                const colors = ['#0d6efd', '#dc3545', '#198754', '#ffc107', '#6f42c1', '#fd7e14'];

                // 4. Format into Chart.js datasets
                const datasets = Object.keys(diseases).map((diseaseName, index) => {
                    return {
                        label: diseaseName,
                        // Map the cases to the sorted dates (insert 0 if no cases that day)
                        data: uniqueDates.map(date => diseases[diseaseName][date] || 0),
                        borderColor: colors[index % colors.length],
                        backgroundColor: colors[index % colors.length],
                        tension: 0.3, // Adds a slight curve to the lines
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
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: '30-Day Disease Case Trends' },
        },
        scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Number of Cases' } },
            x: { title: { display: true, text: 'Date' } }
        }
    };

    if (loading) return <div className="spinner-border text-primary" role="status"></div>;
    
    if (!chartData) return <div className="alert alert-info">No trend data available for this period.</div>;

    return (
        <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
                <Line options={options} data={chartData} />
            </div>
        </div>
    );
};

export default TrendLineChart;
