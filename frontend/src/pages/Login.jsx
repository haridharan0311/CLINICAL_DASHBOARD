import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        const success = await login(username, password);
        if (success) {
            navigate('/dashboard'); // Redirect to dashboard on success!
        } else {
            setError('Invalid username or password.');
        }
    };

    return (
        <div className="container d-flex justify-content-center align-items-center" style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
            <div className="card shadow-lg border-0" style={{ width: '400px', borderRadius: '15px' }}>
                <div className="card-body p-5">
                    <div className="text-center mb-4">
                        <h3 className="fw-bold text-primary">MedIntel Dashboard</h3>
                        <p className="text-muted small">Please login to your account</p>
                    </div>
                    
                    {error && <div className="alert alert-danger py-2">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="mb-3">
                            <label className="form-label text-secondary fw-semibold">Username</label>
                            <input 
                                type="text" 
                                className="form-control form-control-lg bg-light" 
                                value={username} 
                                onChange={(e) => setUsername(e.target.value)} 
                                required 
                            />
                        </div>
                        <div className="mb-4">
                            <label className="form-label text-secondary fw-semibold">Password</label>
                            <input 
                                type="password" 
                                className="form-control form-control-lg bg-light" 
                                value={password} 
                                onChange={(e) => setPassword(e.target.value)} 
                                required 
                            />
                        </div>
                        <button type="submit" className="btn btn-primary btn-lg w-100 fw-bold">
                            Secure Login
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Login;
