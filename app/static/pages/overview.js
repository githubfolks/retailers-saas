(function () {
    const { Icon, StatCard } = window.Shared;

    window.Pages['overview'] = function OverviewPage() {
        const {
            summary, products, posSummary, aiBriefing, generateBriefing,
            showToast, loading, setLoading, API, fetchData, settings
        } = React.useContext(window.AppContext);

        return (
            <div className="dashboard-content">
                <div className="dashboard-grid">
                    <StatCard index={0} label="Total Revenue" value={`₹${summary.total_revenue.toLocaleString()}`} icon="trending-up" variant="success" />
                    <StatCard index={1} label="Total Orders" value={summary.total_orders} icon="shopping-bag" variant="primary" />
                    <StatCard index={2} label="Total Products" value={products.length} icon="package" variant="secondary" />
                    <StatCard index={3} label="Pending Orders" value={summary.pending_orders} icon="clock" variant="warning" />
                </div>

                <div className="form-card animate-slide delay-1" style={{ maxWidth: '100%', marginTop: '1.5rem' }}>
                    <div className="form-header">
                        <h3 className="outfit">System Integrations</h3>
                        <p>Real-time sync status with Odoo ERP and WhatsApp</p>
                    </div>
                    <div style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem', background: 'var(--bg-main)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                            <div style={{ padding: '0.875rem', borderRadius: '10px', background: 'var(--primary-light)', color: 'var(--primary)', flexShrink: 0 }}>
                                <Icon name="layers" size={22} />
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Odoo ERP</div>
                                <div style={{ fontWeight: 700, color: 'var(--success)', fontSize: '0.875rem' }}>Connected</div>
                            </div>
                            <button
                                className="btn-primary"
                                style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem', flexShrink: 0 }}
                                onClick={async () => {
                                    try {
                                        showToast('Syncing data...');
                                        setLoading(true);
                                        const prodSync = await API.post('/sync/products/');
                                        showToast(`Synced ${prodSync.data.count} products`, 'success');
                                        const orderSync = await API.post('/sync/orders/');
                                        showToast(`Synced ${orderSync.data.count} orders`, 'success');
                                        await fetchData();
                                        showToast('All data synchronized', 'success');
                                    } catch (err) {
                                        showToast(err.response?.data?.detail || 'Sync failed', 'error');
                                    } finally {
                                        setLoading(false);
                                    }
                                }}
                                disabled={loading}
                            >
                                <Icon name="refresh-cw" size={14} />
                                <span>{loading ? 'Syncing...' : 'Sync Now'}</span>
                            </button>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem', background: 'var(--bg-main)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                            <div style={{ padding: '0.875rem', borderRadius: '10px', background: 'rgba(59,130,246,0.1)', color: '#3b82f6', flexShrink: 0 }}>
                                <Icon name="message-circle" size={22} />
                            </div>
                            <div>
                                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>WhatsApp</div>
                                <div style={{ fontWeight: 700, color: 'var(--success)', fontSize: '0.875rem' }}>Online</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };
})();
