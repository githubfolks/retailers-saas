(function () {
    const { Icon } = window.Shared;

    window.Pages['customers'] = function CustomersPage() {
        const { customers, selectedCustomer, setSelectedCustomer, selectCustomer, loading } = React.useContext(window.AppContext);

        return (
            <div className="animate-slide" style={{ display: 'grid', gridTemplateColumns: selectedCustomer ? '1fr 1.4fr' : '1fr', gap: '2rem' }}>
                <div className="table-container">
                    <div className="form-header" style={{ padding: '1.5rem 1.5rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h4 className="outfit">Customer Registry</h4>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{customers.length} records</span>
                    </div>
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead><tr><th>Customer</th><th>Lifetime Value</th><th>Profile</th></tr></thead>
                            <tbody>
                                {customers.map(c => (
                                    <tr key={c.id} onClick={() => selectCustomer(c)} style={{ cursor: 'pointer', background: selectedCustomer?.id === c.id ? 'var(--bg-glass)' : '' }}>
                                        <td>
                                            <div style={{ fontWeight: 600 }}>{c.name || c.mobile}</div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.mobile}</div>
                                        </td>
                                        <td><strong>₹{(c.total_spent || 0).toLocaleString()}</strong></td>
                                        <td>
                                            <span className={`badge badge-${c.order_count > 5 ? 'success' : 'primary'}`}>
                                                {c.order_count || 0} orders
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {customers.length === 0 && <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>No customer data available</div>}
                    </div>
                </div>

                {selectedCustomer && (
                    <div className="form-card animate-pop" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
                        <div className="form-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div>
                                <h4 className="outfit">{selectedCustomer.name || selectedCustomer.mobile}</h4>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{selectedCustomer.mobile} · {selectedCustomer.email || 'No email'}</p>
                            </div>
                            <button className="btn-icon" onClick={() => setSelectedCustomer(null)}><Icon name="x" size={18} /></button>
                        </div>
                        <div className="form-body">
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                                <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '10px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)' }}>{selectedCustomer.order_count || 0}</div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Total Orders</div>
                                </div>
                                <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '10px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--success)' }}>₹{(selectedCustomer.total_spent || 0).toLocaleString()}</div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Lifetime Value</div>
                                </div>
                                <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '10px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>₹{selectedCustomer.order_count > 0 ? ((selectedCustomer.total_spent || 0) / selectedCustomer.order_count).toFixed(0) : 0}</div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Avg Order</div>
                                </div>
                            </div>

                            {selectedCustomer.orders && selectedCustomer.orders.length > 0 && (
                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '0.75rem', fontSize: '0.875rem' }}>Order History</div>
                                    <table className="data-table" style={{ background: 'transparent' }}>
                                        <thead><tr><th>Product</th><th>Amount</th><th>Status</th><th>Date</th></tr></thead>
                                        <tbody>
                                            {selectedCustomer.orders.map(o => (
                                                <tr key={o.id}>
                                                    <td style={{ fontSize: '0.8rem' }}>{o.product_name}</td>
                                                    <td style={{ fontWeight: 600 }}>₹{o.total_amount.toLocaleString()}</td>
                                                    <td><span className={`badge badge-${o.status === 'completed' ? 'success' : 'primary'}`}>{o.status.toUpperCase()}</span></td>
                                                    <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(o.created_at).toLocaleDateString()}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        );
    };
})();
