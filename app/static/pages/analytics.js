(function () {
    window.Pages['analytics'] = function AnalyticsPage() {
        const { financials } = React.useContext(window.AppContext);
        if (!financials) return <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading financial data...</div>;

        return (
            <div className="dashboard-content">
                <div className="stats-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                    <div className="stat-card animate-pop">
                        <div className="stat-label">Total Revenue</div>
                        <div className="stat-value">₹{financials.financials.total_revenue.toLocaleString()}</div>
                        <div className="stat-footer success">Gross Billing</div>
                    </div>
                    <div className="stat-card animate-pop delay-1">
                        <div className="stat-label">Total COGS</div>
                        <div className="stat-value" style={{ color: 'var(--accent)' }}>₹{financials.financials.total_cogs.toLocaleString()}</div>
                        <div className="stat-footer">Cost of Goods</div>
                    </div>
                    <div className="stat-card animate-pop delay-2">
                        <div className="stat-label">Net Profit</div>
                        <div className="stat-value" style={{ color: 'var(--success)' }}>₹{financials.financials.gross_profit.toLocaleString()}</div>
                        <div className="stat-footer success">{financials.financials.gross_margin_pct}% Margin</div>
                    </div>
                    <div className="stat-card animate-pop delay-3">
                        <div className="stat-label">Tax Collected</div>
                        <div className="stat-value">₹{financials.taxes.total_gst.toLocaleString()}</div>
                        <div className="stat-footer">GST Liabilities</div>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                    <div className="form-card animate-slide">
                        <div className="form-header">
                            <h3 className="outfit">Profitability Breakdown</h3>
                            <p>Revenue vs. Procurement Cost (30 Days)</p>
                        </div>
                        <div className="form-body" style={{ minHeight: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)', borderRadius: '12px', margin: '1rem' }}>
                            <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                <p>Trend visualization available in Pro</p>
                            </div>
                        </div>
                    </div>

                    <div className="form-card animate-slide delay-1">
                        <div className="form-header">
                            <h3 className="outfit">Tax Summary (GST)</h3>
                            <p>Component-wise breakdown</p>
                        </div>
                        <div className="form-body">
                            <table className="data-table" style={{ background: 'transparent' }}>
                                <tbody>
                                    <tr><td><strong>IGST</strong></td><td style={{ textAlign: 'right' }}>₹{financials.taxes.breakdown.IGST.toLocaleString()}</td></tr>
                                    <tr><td><strong>CGST</strong></td><td style={{ textAlign: 'right' }}>₹{financials.taxes.breakdown.CGST.toLocaleString()}</td></tr>
                                    <tr><td><strong>SGST</strong></td><td style={{ textAlign: 'right' }}>₹{financials.taxes.breakdown.SGST.toLocaleString()}</td></tr>
                                    <tr style={{ borderTop: '2px solid var(--border)' }}>
                                        <td><strong>Total GST</strong></td>
                                        <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--primary)' }}>₹{financials.taxes.total_gst.toLocaleString()}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        );
    };
})();
