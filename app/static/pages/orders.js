(function () {
    const { Icon } = window.Shared;

    window.Pages['orders'] = function OrdersPage() {
        const { orders, loading, API, fetchData, showToast, fetchInvoice, initiateFulfillment } = React.useContext(window.AppContext);

        const [searchTerm, setSearchTerm] = React.useState('');
        const [currentPage, setCurrentPage] = React.useState(1);
        const itemsPerPage = 10;

        const filteredOrders = orders.filter(o => 
            (o.customer_mobile || '').toLowerCase().includes(searchTerm.toLowerCase()) || 
            (o.product_name || '').toLowerCase().includes(searchTerm.toLowerCase())
        );
        const totalPages = Math.ceil(filteredOrders.length / itemsPerPage) || 1;
        const currentOrders = filteredOrders.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

        return (
            <div className="tenants-view animate-slide">
                <div className="view-header" style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ position: 'relative', width: '300px' }}>
                        <Icon name="search" size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input 
                            type="text" 
                            placeholder="Search by customer mobile or product..." 
                            value={searchTerm}
                            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                            style={{ width: '100%', padding: '0.6rem 1rem 0.6rem 2.5rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--bg-main)' }}
                        />
                    </div>
                </div>
                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Customer</th>
                                    <th>Item / Qty</th>
                                    <th>Profit / Margin</th>
                                    <th>Promise Date</th>
                                    <th>Status</th>
                                    <th>Amount</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {currentOrders.map((o, idx) => (
                                    <tr key={o.id} className={`animate-fade delay-${(idx % 3) + 1}`}>
                                        <td>
                                            <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '0.25rem', fontSize: '0.8rem' }}>#ORD-{o.id.toString().padStart(4, '0')}</div>
                                            <div style={{ fontWeight: 600 }}>{o.customer_mobile}</div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{new Date(o.created_at).toLocaleDateString()}</div>
                                        </td>
                                        <td>
                                            <div style={{ fontWeight: 500 }}>{o.product_name}</div>
                                            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Qty: {o.quantity}</div>
                                        </td>
                                        <td>
                                            {o.unit_cost_at_sale ? (
                                                <div style={{ color: (o.total_amount - (o.unit_cost_at_sale * o.quantity)) > 0 ? 'var(--success)' : 'var(--error)' }}>
                                                    <div style={{ fontWeight: 600 }}>₹{(o.total_amount - (o.unit_cost_at_sale * o.quantity)).toFixed(0)}</div>
                                                    <div style={{ fontSize: '10px' }}>{((o.total_amount - (o.unit_cost_at_sale * o.quantity)) / o.total_amount * 100).toFixed(1)}% Margin</div>
                                                </div>
                                            ) : <span style={{ color: 'var(--text-muted)' }}>No Cost Data</span>}
                                        </td>
                                        <td>
                                            <div style={{ fontWeight: 500 }}>{o.commitment_date ? new Date(o.commitment_date).toLocaleDateString() : '-'}</div>
                                            {o.commitment_date && new Date(o.commitment_date) < new Date() && o.status !== 'completed' &&
                                                <div style={{ fontSize: '10px', color: 'var(--error)', fontWeight: 600 }}>OVERDUE</div>
                                            }
                                        </td>
                                        <td>
                                            <span className={`badge badge-${o.status === 'completed' ? 'success' : o.status === 'draft' ? 'secondary' : 'accent'}`}>
                                                {o.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td><div style={{ fontWeight: 700 }}>₹{o.total_amount.toLocaleString()}</div></td>
                                        <td>
                                            <div className="table-actions">
                                                <button className="btn-icon" title="View Invoice" onClick={() => fetchInvoice(o.id)}>
                                                    <Icon name="file-text" size={16} />
                                                </button>
                                                {o.status === 'draft' && (
                                                    <button className="btn-icon" style={{ color: 'var(--primary)' }} title="Confirm Order" onClick={async () => {
                                                        try { await API.post(`/orders/${o.id}/confirm`); showToast('Quotation confirmed!', 'success'); fetchData(); }
                                                        catch (e) { showToast('Confirmation failed', 'error'); }
                                                    }}>
                                                        <Icon name="check-circle" size={16} />
                                                    </button>
                                                )}
                                                {o.status !== 'completed' && o.status !== 'draft' && (
                                                    <button className="btn-icon" style={{ color: 'var(--success)' }} title="Pack & Ship" onClick={() => initiateFulfillment(o)}>
                                                        <Icon name="truck" size={16} />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {orders.length === 0 && !loading && (
                        <div style={{ padding: '6rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="shopping-bag" size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                            <p>No transactions detected today</p>
                        </div>
                    )}
                    {filteredOrders.length === 0 && orders.length > 0 && (
                        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <p>No orders match your search.</p>
                        </div>
                    )}
                    {totalPages > 1 && (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1.5rem', padding: '1rem', borderTop: '1px solid var(--border)', background: 'var(--bg-main)' }}>
                            <button className="btn-icon" disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)} style={{ opacity: currentPage === 1 ? 0.3 : 1 }}><Icon name="chevron-left" size={20} /></button>
                            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Page {currentPage} of {totalPages}</span>
                            <button className="btn-icon" disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => p + 1)} style={{ opacity: currentPage === totalPages ? 0.3 : 1 }}><Icon name="chevron-right" size={20} /></button>
                        </div>
                    )}
                </div>
            </div>
        );
    };
})();
