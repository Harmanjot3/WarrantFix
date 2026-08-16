import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Shield, LogOut, PlusCircle, LayoutDashboard } from 'lucide-react';

export default function Navbar({ setIsAuthenticated }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/');
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="nav-link" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', fontSize: '1.25rem', fontWeight: 700 }}>
        <Shield color="#3b82f6" /> WarrantFix
      </Link>
      <div className="nav-links" style={{ display: 'flex', alignItems: 'center' }}>
        <Link to="/dashboard" className={`nav-link ${isActive('/dashboard')}`}><LayoutDashboard size={18} style={{verticalAlign:'middle', marginRight: '4px'}}/> Dashboard</Link>
        <Link to="/add-product" className={`nav-link ${isActive('/add-product')}`}><PlusCircle size={18} style={{verticalAlign:'middle', marginRight: '4px'}}/> Add Product</Link>
        <button onClick={handleLogout} className="btn btn-outline" style={{ padding: '0.4rem 0.75rem', fontSize: '0.875rem' }}>
          <LogOut size={16} /> Logout
        </button>
      </div>
    </nav>
  );
}
