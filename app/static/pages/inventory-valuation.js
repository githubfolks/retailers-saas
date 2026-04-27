(function () {
    const { Icon } = window.Shared;

    window.Pages['inventory-valuation'] = function InventoryValuationPage() {
        const { valuationLedger } = React.useContext(window.AppContext);

        const totalValue = valuationLedger.reduce((sum, e) => sum + (e.total_value || 0), 0);
        const totalUnits = valuationLedger.reduce((sum, e) => sum + (e.quantity || 0), 0);

        return (
            <div className="animate-slide">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                    <div className="stat-card animate-pop">
                        <div className="stat-label">Total Stock Value</div>
                        <div className="stat-value">₹{totalValue.toLocaleString()}</div>
                        <div className="stat-footer success">At Cost Price</div>
                    </div>
                    <div className="stat-card animate-pop delay-1">
                        <div className="stat-label">Total Units</div>
                        <div className="stat-value">{totalUnits.toLocaleString()}</div>
                        <div className="stat-footer">Across All SKUs</div>
                    </div>
                    <div className="stat-card animate-pop delay-2">
                        <div className="stat-label">SKUs Tracked</div>
                        <div className="stat-value">{valuationLedger.length}</div>
                        <div className="stat-footer">Active Products</div>
                    </div>
                </div>

                <div className="table-container">
                    <div className="form-header" style={{ padding: '1.5rem 1.5rem 0' }}>
                        <h4 className="outfit">Stock Valuation Ledger</h4>
                    </div>
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Product / SKU</th>
                                    <th>Qty on Hand</th>
                                    <th>Cost Price</th>
                                    <th>Total Value</th>
                                    <th>% of Portfolio</th>
                                </tr>
                            </thead>
                            <tbody>
                                {valuationLedger.map((e, i) => {
                                    const pct = totalValue > 0 ? ((e.total_value || 0) / totalValue * 100) : 0;
                                    return (
                                        <tr key={e.sku || i}>
                                            <td>
                                                <div style={{ fontWeight: 600 }}>{e.product_name}</div>
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{e.sku}</div>
                                            </td>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <div style={{ width: '4px', height: '16px', borderRadius: '2px', background: e.quantity > 10 ? 'var(--success)' : 'var(--accent)' }}></div>
                                                    <span>{e.quantity}</span>
                                                </div>
                                            </td>
                                            <td>₹{(e.cost_price || 0).toLocaleString()}</td>
                                            <td><strong>₹{(e.total_value || 0).toLocaleString()}</strong></td>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <div style={{ flex: 1, height: '4px', background: 'var(--border)', borderRadius: '2px', maxWidth: '80px' }}>
                                                        <div style={{ width: `${Math.min(pct, 100)}%`, height: '100%', background: 'var(--primary)', borderRadius: '2px' }}></div>
                                                    </div>
                                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{pct.toFixed(1)}%</span>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                    {valuationLedger.length === 0 && (
                        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="dollar-sign" size={48} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                            <p>No valuation data available</p>
                        </div>
                    )}
                </div>
            </div>
        );
    };
})();
