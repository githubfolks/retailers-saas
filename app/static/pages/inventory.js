(function () {
    const { Icon } = window.Shared;

    window.Pages['inventory'] = function InventoryPage() {
        const { alerts, suggestions, aiBriefing, loading, setLoading, API, fetchData, showToast, generateBriefing, setShowScanner } = React.useContext(window.AppContext);

        return (
            <div className="inventory-view animate-slide">
                <div className="form-card" style={{ maxWidth: '100%', marginBottom: '1.5rem', border: '1px solid var(--primary)', background: 'var(--bg-glass)' }}>
                    <div className="form-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(13,148,136,0.15)' }}>
                        <div>
                            <h3 className="outfit" style={{ color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                                <Icon name="sparkles" size={20} />
                                AI Inventory Assistant
                            </h3>
                            <p>AI-powered analysis of your stock levels and reorder needs</p>
                        </div>
                        <div style={{ display: 'flex', gap: '0.75rem' }}>
                            <button className="btn-secondary" onClick={() => setShowScanner(true)}>
                                <Icon name="scan-barcode" size={18} /><span>Scan Barcode</span>
                            </button>
                            <button className="btn-primary" onClick={generateBriefing} disabled={loading}>
                                <Icon name="refresh-cw" size={16} />
                                {loading ? 'Analyzing...' : 'Refresh Analysis'}
                            </button>
                        </div>
                    </div>
                    <div style={{ padding: '1.5rem', whiteSpace: 'pre-wrap', lineHeight: '1.7', color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
                        {aiBriefing || "Click 'Refresh Analysis' to generate an AI overview of your current inventory health, reorder recommendations, and demand trends."}
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div className="table-container">
                        <div className="form-header" style={{ padding: '1.25rem 1.5rem 0' }}>
                            <h4 className="outfit">Stock Alerts</h4>
                            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Products below minimum stock level</p>
                        </div>
                        <div className="data-table-wrapper" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Reason</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {alerts.map(a => (
                                        <tr key={a.id}>
                                            <td><strong>{a.product_name}</strong></td>
                                            <td><span style={{ color: 'var(--warning)', fontWeight: 500, fontSize: '0.8125rem' }}>{a.reason}</span></td>
                                            <td><span className="badge badge-warning">Low Stock</span></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {alerts.length === 0 && (
                                <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    <Icon name="check-circle" size={32} style={{ marginBottom: '0.75rem', color: 'var(--success)' }} />
                                    <p style={{ fontWeight: 500 }}>All stock levels are healthy</p>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="table-container">
                        <div className="form-header" style={{ padding: '1.25rem 1.5rem 0' }}>
                            <h4 className="outfit">Restock Recommendations</h4>
                            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>AI-suggested purchase orders</p>
                        </div>
                        <div className="data-table-wrapper" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Qty</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {suggestions.map(s => (
                                        <tr key={s.id}>
                                            <td>
                                                <div style={{ fontWeight: 500 }}>Restock {s.product_name}</div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.reason}</div>
                                            </td>
                                            <td><strong>{s.suggested_quantity}</strong></td>
                                            <td>
                                                <button className="btn-primary" style={{ padding: '0.375rem 0.75rem', fontSize: '0.8125rem' }} onClick={async () => {
                                                    setLoading(true);
                                                    try {
                                                        await API.post(`/inventory/reorder-suggestions/${s.id}/approve`);
                                                        showToast('Purchase order created');
                                                        fetchData();
                                                    }
                                                    catch (err) { showToast('Failed to create order', 'error'); }
                                                    finally { setLoading(false); }
                                                }}>Create PO</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {suggestions.length === 0 && (
                                <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    <p>No restock recommendations at this time</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };
})();
