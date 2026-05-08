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
                        <p>Real-time status of platform services</p>
                    </div>
                    <div style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem', background: 'var(--bg-main)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                            <div style={{ padding: '0.875rem', borderRadius: '10px', background: 'rgba(59,130,246,0.1)', color: '#3b82f6', flexShrink: 0 }}>
                                <Icon name="message-circle" size={22} />
                            </div>
                            <div>
                                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>WhatsApp</div>
                                <div style={{ fontWeight: 700, color: 'var(--success)', fontSize: '0.875rem' }}>Online</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem', background: 'var(--bg-main)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                            <div style={{ padding: '0.875rem', borderRadius: '10px', background: 'rgba(245,158,11,0.1)', color: '#f59e0b', flexShrink: 0 }}>
                                <Icon name="credit-card" size={22} />
                            </div>
                            <div>
                                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Razorpay</div>
                                <div style={{ fontWeight: 700, color: 'var(--success)', fontSize: '0.875rem' }}>Active</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };
})();
