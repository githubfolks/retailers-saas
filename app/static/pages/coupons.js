(function () {
    const { Icon } = window.Shared;

    window.Pages['coupons'] = function CouponsPage() {
        const { coupons, setShowCouponModal, handleDeactivateCoupon } = React.useContext(window.AppContext);

        return (
            <div className="animate-slide">
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
                    <button className="btn-primary" onClick={() => setShowCouponModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <Icon name="plus-circle" size={16} />
                        New Promotion
                    </button>
                </div>

                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Coupon Code</th>
                                    <th>Discount</th>
                                    <th>Min Purchase</th>
                                    <th>Status</th>
                                    <th>Usage</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {coupons.map(c => (
                                    <tr key={c.id}>
                                        <td>
                                            <code style={{ fontFamily: 'monospace', fontWeight: 700, background: 'var(--bg-glass)', padding: '0.2rem 0.5rem', borderRadius: '6px', color: 'var(--primary)' }}>{c.code}</code>
                                        </td>
                                        <td>
                                            <strong>{c.discount_type === 'percentage' ? `${c.discount_value}%` : `₹${c.discount_value}`}</strong>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.discount_type}</div>
                                        </td>
                                        <td>₹{(c.min_purchase_amount || 0).toLocaleString()}</td>
                                        <td>
                                            <span className={`badge badge-${c.is_active ? 'success' : 'secondary'}`}>
                                                {c.is_active ? 'ACTIVE' : 'INACTIVE'}
                                            </span>
                                        </td>
                                        <td>{c.usage_count || 0}×</td>
                                        <td>
                                            {c.is_active && (
                                                <button className="btn-icon delete" title="Deactivate" onClick={() => { if (confirm(`Deactivate coupon ${c.code}?`)) handleDeactivateCoupon(c.id); }}>
                                                    <Icon name="x-circle" size={15} />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {coupons.length === 0 && (
                        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="tag" size={40} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                            <p>No promotions configured</p>
                        </div>
                    )}
                </div>
            </div>
        );
    };
})();
