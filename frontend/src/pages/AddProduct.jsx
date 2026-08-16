import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle } from 'lucide-react';

export default function AddProduct() {
  const navigate = useNavigate();
  const [type, setType] = useState('offline');
  const [formData, setFormData] = useState({
    product_name: '', purchase_date: '', warranty_period: 12, warranty_code: '',
    seller: '', purchase_bill_path: '', source_url: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = type === 'offline' ? '/api/products/offline' : '/api/products/online';
    
    // Filter data based on type to prevent sending unnecessary fields
    const dataToSend = {
      product_name: formData.product_name,
      purchase_date: formData.purchase_date,
      warranty_period: parseInt(formData.warranty_period),
      warranty_code: formData.warranty_code,
    };
    if (type === 'offline') {
      dataToSend.seller = formData.seller;
      dataToSend.purchase_bill_path = formData.purchase_bill_path;
    } else {
      dataToSend.source_url = formData.source_url;
    }

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(dataToSend)
      });
      if (res.ok) {
        navigate('/dashboard');
      } else {
        alert('Failed to add product');
      }
    } catch (err) {
      alert('Network error');
    }
  };

  return (
    <div className="glass-panel animate-fade-in" style={{ maxWidth: '600px', margin: '0 auto', width: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <PlusCircle size={48} color="var(--accent)" style={{ marginBottom: '1rem', margin: '0 auto' }} />
        <h2 className="title" style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Add New Product</h2>
        <p className="subtitle" style={{ fontSize: '0.9rem', marginBottom: 0 }}>Register a new product to track its warranty.</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          type="button" 
          className={`btn ${type === 'offline' ? 'btn-accent' : 'btn-outline'}`} 
          style={{ flex: 1 }}
          onClick={() => setType('offline')}
        >
          Offline Purchase
        </button>
        <button 
          type="button" 
          className={`btn ${type === 'online' ? 'btn-primary' : 'btn-outline'}`} 
          style={{ flex: 1 }}
          onClick={() => setType('online')}
        >
          Online Purchase
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Product Name</label>
          <input required type="text" value={formData.product_name} onChange={e => setFormData({...formData, product_name: e.target.value})} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="input-group">
            <label>Purchase Date</label>
            <input required type="date" value={formData.purchase_date} onChange={e => setFormData({...formData, purchase_date: e.target.value})} />
          </div>
          <div className="input-group">
            <label>Warranty Period (Months)</label>
            <input required type="number" value={formData.warranty_period} onChange={e => setFormData({...formData, warranty_period: e.target.value})} />
          </div>
        </div>

        <div className="input-group">
          <label>Warranty Code</label>
          <input required type="text" value={formData.warranty_code} onChange={e => setFormData({...formData, warranty_code: e.target.value})} />
        </div>

        {type === 'offline' ? (
          <>
            <div className="input-group">
              <label>Seller / Store Name</label>
              <input required type="text" value={formData.seller} onChange={e => setFormData({...formData, seller: e.target.value})} />
            </div>
            <div className="input-group">
              <label>Purchase Bill Path / Reference</label>
              <input required type="text" value={formData.purchase_bill_path} onChange={e => setFormData({...formData, purchase_bill_path: e.target.value})} />
            </div>
          </>
        ) : (
          <div className="input-group">
            <label>Source URL</label>
            <input required type="url" value={formData.source_url} onChange={e => setFormData({...formData, source_url: e.target.value})} />
          </div>
        )}

        <button type="submit" className={`btn ${type === 'offline' ? 'btn-accent' : 'btn-primary'}`} style={{ width: '100%', marginTop: '1rem' }}>
          Register Product
        </button>
      </form>
    </div>
  );
}
