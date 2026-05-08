const AdminDashboard = () => {
  const [token, setToken] = React.useState(localStorage.getItem('admin_token') || '');
  const [password, setPassword] = React.useState('');
  const [isLoggedIn, setIsLoggedIn] = React.useState(!!token);
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [dashboard, setDashboard] = React.useState(null);
  const [tenants, setTenants] = React.useState([]);
  const [selectedTenant, setSelectedTenant] = React.useState(null);
  const [tenantForm, setTenantForm] = React.useState({
    tenant_id: '',
    business_name: '',
    whatsapp_number: '',
    razorpay_key: '',
    razorpay_secret: '',
    n8n_webhook_url: '',
  });
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [success, setSuccess] = React.useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('/api/admin/login', { password });
      const newToken = response.data.access_token;
      setToken(newToken);
      localStorage.setItem('admin_token', newToken);
      setIsLoggedIn(true);
      setPassword('');
      setSuccess('Logged in successfully');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Invalid password');
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
    localStorage.removeItem('admin_token');
    setIsLoggedIn(false);
    setCurrentPage('dashboard');
  };

  const fetchDashboard = async () => {
    try {
      const response = await axios.get('/api/admin/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      setDashboard(response.data);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
    }
  };

  const fetchTenants = async () => {
    try {
      const response = await axios.get('/api/admin/tenants', {
        headers: { 'Authorization': `Bearer ${token}` },
        params: { skip: 0, limit: 50 },
      });
      setTenants(response.data);
    } catch (err) {
      console.error('Error fetching tenants:', err);
    }
  };

  React.useEffect(() => {
    if (isLoggedIn && currentPage === 'dashboard') {
      fetchDashboard();
    } else if (isLoggedIn && currentPage === 'tenants') {
      fetchTenants();
    }
  }, [isLoggedIn, currentPage]);

  const handleCreateTenant = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post('/api/admin/tenants', tenantForm, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      setSuccess('Tenant created successfully');
      setTenantForm({
        tenant_id: '',
        business_name: '',
        whatsapp_number: '',
        razorpay_key: '',
        razorpay_secret: '',
        n8n_webhook_url: '',
      });
      fetchTenants();
      setCurrentPage('tenants');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating tenant');
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTenant = async (tenantId) => {
    if (!window.confirm('Are you sure you want to delete this tenant?')) return;
    setLoading(true);
    try {
      await axios.delete(`/api/admin/tenants/${tenantId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      setSuccess('Tenant deleted successfully');
      fetchTenants();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Error deleting tenant');
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setTenantForm({ ...tenantForm, [name]: value });
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h1>Admin Panel</h1>
          <form onSubmit={handleLogin}>
            <input
              type="password"
              placeholder="Admin Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <nav className="navbar">
        <div className="nav-left">
          <h1>Admin Panel</h1>
          <ul className="nav-links">
            <li>
              <button
                className={currentPage === 'dashboard' ? 'active' : ''}
                onClick={() => setCurrentPage('dashboard')}
              >
                Dashboard
              </button>
            </li>
            <li>
              <button
                className={currentPage === 'tenants' ? 'active' : ''}
                onClick={() => setCurrentPage('tenants')}
              >
                Tenants
              </button>
            </li>
            <li>
              <button
                className={currentPage === 'create' ? 'active' : ''}
                onClick={() => setCurrentPage('create')}
              >
                Create Tenant
              </button>
            </li>
          </ul>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </nav>

      <div className="content">
        {error && <div className="alert error">{error}</div>}
        {success && <div className="alert success">{success}</div>}

        {currentPage === 'dashboard' && dashboard && (
          <div className="dashboard-view">
            <h2>Dashboard Overview</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Tenants</h3>
                <p className="stat-value">{dashboard.total_tenants}</p>
              </div>
              <div className="stat-card">
                <h3>Total Orders</h3>
                <p className="stat-value">{dashboard.total_orders}</p>
              </div>
              <div className="stat-card">
                <h3>Total Products</h3>
                <p className="stat-value">{dashboard.total_products}</p>
              </div>
              <div className="stat-card">
                <h3>Total Revenue</h3>
                <p className="stat-value">₹{dashboard.total_revenue.toFixed(2)}</p>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'tenants' && (
          <div className="tenants-view">
            <h2>All Tenants</h2>
            {tenants.length === 0 ? (
              <p>No tenants found</p>
            ) : (
              <table className="tenants-table">
                <thead>
                  <tr>
                    <th>Tenant ID</th>
                    <th>Business Name</th>
                    <th>WhatsApp</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tenants.map((tenant) => (
                    <tr key={tenant.id}>
                      <td>{tenant.tenant_id}</td>
                      <td>{tenant.business_name}</td>
                      <td>{tenant.whatsapp_number}</td>
                      <td>
                        <button
                          className="view-btn"
                          onClick={() => {
                            setSelectedTenant(tenant);
                            setCurrentPage('tenant-detail');
                          }}
                        >
                          View
                        </button>
                        <button
                          className="delete-btn"
                          onClick={() => handleDeleteTenant(tenant.tenant_id)}
                          disabled={loading}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {currentPage === 'create' && (
          <div className="create-tenant-view">
            <h2>Create New Tenant</h2>
            <form onSubmit={handleCreateTenant} className="tenant-form">
              <div className="form-group">
                <label>Tenant ID *</label>
                <input
                  type="text"
                  name="tenant_id"
                  value={tenantForm.tenant_id}
                  onChange={handleFormChange}
                  required
                  placeholder="unique-tenant-id"
                />
              </div>
              <div className="form-group">
                <label>Business Name *</label>
                <input
                  type="text"
                  name="business_name"
                  value={tenantForm.business_name}
                  onChange={handleFormChange}
                  required
                  placeholder="Your Business Name"
                />
              </div>
              <div className="form-group">
                <label>WhatsApp Number *</label>
                <input
                  type="text"
                  name="whatsapp_number"
                  value={tenantForm.whatsapp_number}
                  onChange={handleFormChange}
                  required
                  placeholder="91xxxxxxxxxx"
                />
              </div>
              <div className="form-group">
                <label>Razorpay Key *</label>
                <input
                  type="text"
                  name="razorpay_key"
                  value={tenantForm.razorpay_key}
                  onChange={handleFormChange}
                  required
                  placeholder="rzp_live_xxxxx"
                />
              </div>
              <div className="form-group">
                <label>Razorpay Secret *</label>
                <input
                  type="password"
                  name="razorpay_secret"
                  value={tenantForm.razorpay_secret}
                  onChange={handleFormChange}
                  required
                  placeholder="secret"
                />
              </div>
              <div className="form-group">
                <label>n8n Webhook URL</label>
                <input
                  type="text"
                  name="n8n_webhook_url"
                  value={tenantForm.n8n_webhook_url}
                  onChange={handleFormChange}
                  placeholder="https://n8n.example.com/webhook"
                />
              </div>
              <button type="submit" disabled={loading} className="submit-btn">
                {loading ? 'Creating...' : 'Create Tenant'}
              </button>
            </form>
          </div>
        )}

        {currentPage === 'tenant-detail' && selectedTenant && (
          <div className="tenant-detail-view">
            <button className="back-btn" onClick={() => setCurrentPage('tenants')}>
              ← Back to Tenants
            </button>
            <h2>{selectedTenant.business_name}</h2>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Tenant ID:</label>
                <p>{selectedTenant.tenant_id}</p>
              </div>
              <div className="detail-item">
                <label>WhatsApp:</label>
                <p>{selectedTenant.whatsapp_number}</p>
              </div>
              <div className="detail-item">
                <label>Razorpay Key:</label>
                <p>{selectedTenant.razorpay_key}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<AdminDashboard />);
