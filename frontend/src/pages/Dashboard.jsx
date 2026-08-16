import { useEffect, useState } from 'react';
import { ShieldCheck, Clock, Settings, ShoppingBag } from 'lucide-react';

export default function Dashboard() {
  const [products, setProducts] = useState([]);
  const [interval, setIntervalDays] = useState(30);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    const res = await fetch('http://localhost:8000/api/products', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    if (res.ok) {
      const data = await res.json();
      setProducts(data.products);
    }
  };

  const handleSetReminder = async () => {
    const res = await fetch('http://localhost:8000/api/reminders', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` 
      },
      body: JSON.stringify({ interval_days: interval })
    });
    if (res.ok) {
      alert('Reminders successfully configured!');
    } else {
      alert('Failed to configure reminders');
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="title" style={{ marginBottom: '0.5rem' }}>Your Dashboard</h1>
          <p className="subtitle" style={{ marginBottom: 0 }}>Manage your products and warranty reminders</p>
        </div>
        <div className="glass-panel" style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label style={{ fontSize: '0.75rem' }}>Reminder Interval (Days)</label>
            <input type="number" value={interval} onChange={e => setIntervalDays(parseInt(e.target.value))} style={{ width: '80px', padding: '0.5rem' }} />
          </div>
          <button onClick={handleSetReminder} className="btn btn-accent" style={{ padding: '0.5rem 1rem' }}>
            <Settings size={18} /> Apply
          </button>
        </div>
      </div>

      <div className="grid-layout">
        {products.length === 0 ? (
          <div className="glass-panel" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem 2rem' }}>
            <ShoppingBag size={48} color="var(--text-muted)" style={{ margin: '0 auto 1rem auto' }} />
            <h3>No products found</h3>
            <p className="subtitle" style={{ marginTop: '0.5rem' }}>Add a product to start tracking its warranty.</p>
          </div>
        ) : (
          products.map(p => (
            <div key={p.id + p.type} className="glass-panel product-card">
              <div className="product-card-header">
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{p.product_name}</h3>
                <span className={`badge badge-${p.type}`}>{p.type.toUpperCase()}</span>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                Purchased: {p.purchase_date}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                <ShieldCheck color="#3b82f6" size={20} />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Warranty Expires</div>
                  <div style={{ fontWeight: 600 }}>{p.expiry_date}</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
