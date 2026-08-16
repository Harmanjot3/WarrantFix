import { useState } from 'react';
import { Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Login({ setAuth }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '', password: '', email: '', phone_number: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const endpoint = isLogin ? '/api/login' : '/api/register';
    
    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.detail || 'Something went wrong');
        return;
      }

      if (isLogin) {
        localStorage.setItem('token', data.access_token);
        setAuth(true);
      } else {
        setIsLogin(true);
        setError('Registration successful! Please login.');
      }
    } catch (err) {
      setError('Failed to connect to server');
    }
  };

  return (
    <div className="glass-panel" style={{ width: '100%', maxWidth: '400px' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <Shield size={48} color="#3b82f6" style={{ marginBottom: '1rem', margin: '0 auto' }} />
        <h2 className="title" style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="subtitle" style={{ fontSize: '0.9rem', marginBottom: 0 }}>
          {isLogin ? 'Login to manage your warranties' : 'Sign up for WarrantFix'}
        </p>
      </div>

      {error && <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Username</label>
          <input required type="text" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} />
        </div>
        {!isLogin && (
          <>
            <div className="input-group">
              <label>Email</label>
              <input required type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
            </div>
            <div className="input-group">
              <label>Phone Number (e.g. +1234567890)</label>
              <input required type="text" value={formData.phone_number} onChange={e => setFormData({...formData, phone_number: e.target.value})} />
            </div>
          </>
        )}
        <div className="input-group">
          <label>Password</label>
          <input required type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} />
        </div>
        <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
          {isLogin ? 'Login' : 'Register'}
        </button>
      </form>
      
      <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        {isLogin ? "Don't have an account? " : "Already have an account? "}
        <button onClick={() => {setIsLogin(!isLogin); setError('');}} style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontWeight: 600, padding: 0 }}>
          {isLogin ? 'Sign up' : 'Login'}
        </button>
      </p>
    </div>
  );
}
