(function () {
    window.Pages['procurement'] = function ProcurementPage() {
        const { suppliers, purchaseOrders, loading, setLoading, API, fetchData, showToast } = React.useContext(window.AppContext);
        const { Icon } = window.Shared;

        return (
            <div className="procurement-view animate-slide">
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 1fr) 2fr', gap: '1.5rem' }}>
                    <div className="table-container">
                        <div className="form-header" style={{ padding: '1.25rem 1.5rem 0' }}>
                            <h4 className="outfit">Suppliers</h4>
                            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Registered vendor directory</p>
                        </div>
                        <div className="data-table-wrapper">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Vendor</th>
                                        <th>Lead Time</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {suppliers.map(s => (
                                        <tr key={s.id}>
                                            <td><strong>{s.supplier_name || s.name}</strong></td>
                                            <td>
                                                <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '0.375rem' }}>{s.lead_time_days} days</div>
                                                <span className="badge badge-success">Active</span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {suppliers.length === 0 && (
                                <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    <p>No suppliers registered</p>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="table-container">
                        <div className="form-header" style={{ padding: '1.25rem 1.5rem 0' }}>
                            <h4 className="outfit">Purchase Orders</h4>
                            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Track incoming inventory orders</p>
                        </div>
                        <div className="data-table-wrapper">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>PO Reference</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {purchaseOrders.map(po => (
                                        <tr key={po.id}>
                                            <td>
                                                <div style={{ fontWeight: 600 }}>{po.reference}</div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Supplier: {po.supplier_name}</div>
                                            </td>
                                            <td>
                                                <span className={`badge badge-${po.status === 'received' ? 'success' : 'primary'}`}>
                                                    {po.status === 'received' ? 'Received' : po.status.charAt(0).toUpperCase() + po.status.slice(1)}
                                                </span>
                                            </td>
                                            <td>
                                                {po.status === 'sent' && (
                                                    <button className="btn-secondary" style={{ padding: '0.375rem 0.75rem', fontSize: '0.8125rem' }} onClick={async () => {
                                                        setLoading(true);
                                                        try {
                                                            await API.post(`/procurement/purchase-orders/${po.id}/receive`);
                                                            showToast('Items received into inventory');
                                                            fetchData();
                                                        }
                                                        catch (err) { showToast('Failed to mark as received', 'error'); }
                                                        finally { setLoading(false); }
                                                    }}>
                                                        <Icon name="package-check" size={14} />
                                                        Mark Received
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {purchaseOrders.length === 0 && (
                                <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    <Icon name="shopping-cart" size={36} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                                    <p style={{ fontWeight: 500 }}>No purchase orders found</p>
                                    <p style={{ fontSize: '0.875rem', marginTop: '0.375rem' }}>Purchase orders will appear here once created</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };
})();
