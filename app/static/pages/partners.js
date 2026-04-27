(function () {
    window.Pages['partners'] = function PartnersPage() {
        const { suppliers, customers } = React.useContext(window.AppContext);

        const topCustomers = [...customers].sort((a, b) => (b.total_spent || 0) - (a.total_spent || 0)).slice(0, 10);

        return (
            <div className="animate-slide" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                <div className="table-container">
                    <div className="form-header" style={{ padding: '1.5rem 1.5rem 0' }}>
                        <h4 className="outfit">Supply Partners</h4>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{suppliers.length} active vendors</p>
                    </div>
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead><tr><th>Vendor</th><th>Lead Time</th><th>Status</th></tr></thead>
                            <tbody>
                                {suppliers.map(s => (
                                    <tr key={s.id}>
                                        <td>
                                            <div style={{ fontWeight: 600 }}>{s.supplier_name || s.name}</div>
                                            {s.email && <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{s.email}</div>}
                                        </td>
                                        <td><strong>{s.lead_time_days}d</strong></td>
                                        <td><span className="badge badge-success">ACTIVE</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {suppliers.length === 0 && <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No supply partners</div>}
                    </div>
                </div>

                <div className="table-container">
                    <div className="form-header" style={{ padding: '1.5rem 1.5rem 0' }}>
                        <h4 className="outfit">Top Customers</h4>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>By lifetime value</p>
                    </div>
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead><tr><th>Customer</th><th>Orders</th><th>Lifetime Value</th></tr></thead>
                            <tbody>
                                {topCustomers.map((c, i) => (
                                    <tr key={c.id}>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                                <div style={{ width: '22px', height: '22px', borderRadius: '50%', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 800, flexShrink: 0 }}>{i + 1}</div>
                                                <div>
                                                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{c.name || c.mobile}</div>
                                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.mobile}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>{c.order_count || 0}</td>
                                        <td><strong style={{ color: 'var(--success)' }}>₹{(c.total_spent || 0).toLocaleString()}</strong></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {customers.length === 0 && <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No customer data</div>}
                    </div>
                </div>
            </div>
        );
    };
})();
