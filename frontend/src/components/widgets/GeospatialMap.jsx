import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const GeospatialMap = ({ clinics, alerts }) => {
    // Center of Tamil Nadu roughly
    const center = [11.1271, 78.6569];

    return (
        <div className="card shadow-sm border-0 dashboard-card" style={{ height: '500px' }}>
            <div className="card-header bg-white border-bottom py-3">
                <h6 className="mb-0 fw-bold text-dark">Statewide Outbreak Clusters (Live)</h6>
            </div>
            <div className="card-body p-0" style={{ height: '100%', position: 'relative', zIndex: 1 }}>
                <MapContainer center={center} zoom={7} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; OpenStreetMap contributors'
                    />
                    
                    {/* Map through clinics to place markers */}
                    {clinics.map((clinic) => {
                        // Check if this clinic has an active critical alert
                        const hasSpike = alerts.some(a => a.clinic_id === clinic.clinic_id && a.severity === 'Critical');
                        
                        return (
                            <CircleMarker 
                                key={clinic.clinic_id}
                                center={[clinic.latitude, clinic.longitude]} 
                                radius={hasSpike ? 15 : 8}
                                pathOptions={{ 
                                    color: hasSpike ? '#dc3545' : '#0d6efd',
                                    fillColor: hasSpike ? '#dc3545' : '#0d6efd',
                                    fillOpacity: 0.6 
                                }}
                            >
                                <Tooltip direction="top" offset={[0, -5]} opacity={1}>
                                    <span className="fw-bold">{clinic.clinic_name}</span>
                                    {hasSpike && <div className="text-danger small fw-bold">Active Outbreak Alert</div>}
                                </Tooltip>
                                <Popup>
                                    <div className="p-2">
                                        <h6 className="fw-bold mb-1">{clinic.clinic_name}</h6>
                                        <p className="small text-muted mb-0">ID: {clinic.clinic_id}</p>
                                        <hr className="my-2" />
                                        <button className="btn btn-xs btn-primary w-100 py-1" style={{fontSize: '10px'}}>
                                            View Details
                                        </button>
                                    </div>
                                </Popup>
                            </CircleMarker>
                        );
                    })}
                </MapContainer>
            </div>
        </div>
    );
};

export default GeospatialMap;