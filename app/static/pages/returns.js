(function () {
    const { Icon } = window.Shared;

    window.Pages['returns'] = function ReturnsPage() {
        const {
            returns, showReturnModal, setShowReturnModal,
            returnForm, setReturnForm, handleCreateReturn, handleProcessRefund, loading
        } = React.useContext(window.AppContext);

        return (
            <div className="animate-slide">
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
                    <button className="btn-primary" onClick={() => setShowReturnModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <Icon name="plus-circle" size={16} />
                        Log Return
                    </button>
                </div>

                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Return ID</th>
                                    <th>Order Ref</th>
                                    <th>Qty</th>
                                    <th>Reason</th>
                                    <th>Condition</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {returns.map(r => (
                                    <tr key={r.id}>
                                        <td><strong>RET-{r.id}</strong></td>
                                        <td>
                                            <div style={{ fontWeight: 500 }}>Order #{r.order_id}</div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{new Date(r.created_at).toLocaleDateString()}</div>
                                        </td>
                                        <td>{r.quantity}</td>
                                        <td style={{ maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '0.85rem' }}>{r.reason}</td>
                                        <td><span className={`badge badge-${r.condition === 'resellable' ? 'success' : r.condition === 'damaged' ? 'accent' : 'secondary'}`}>{r.condition?.toUpperCase()}</span></td>
                                        <td><span className={`badge badge-${r.refund_status === 'refunded' ? 'success' : 'primary'}`}>{r.refund_status?.toUpperCase() || 'PENDING'}</span></td>
                                        <td>
                                            {r.refund_status !== 'refunded' && (
                                                <button className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.7rem' }} disabled={loading} onClick={() => handleProcessRefund(r.id)}>
                                                    Process Refund
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {returns.length === 0 && (
                        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="refresh-cw" size={40} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                            <p>No return requests logged</p>
                        </div>
                    )}
                </div>

                {showReturnModal && (
                    <div className="modal-overlay" onClick={() => setShowReturnModal(false)}>
                        <div className="modal-content animate-pop" onClick={e => e.stopPropagation()} style={{ maxWidth: '480px' }}>
                            <div className="modal-header">
                                <h3 className="outfit">Log Customer Return</h3>
                                <button className="btn-icon" onClick={() => setShowReturnModal(false)}><Icon name="x" size={20} /></button>
                            </div>
                            <div className="modal-body">
                                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                                    <label>Order ID</label>
                                    <input type="number" value={returnForm.order_id} onChange={e => setReturnForm({ ...returnForm, order_id: e.target.value })} placeholder="Enter order ID" />
                                </div>
                                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                                    <label>Return Quantity</label>
                                    <input type="number" min="1" value={returnForm.quantity} onChange={e => setReturnForm({ ...returnForm, quantity: parseInt(e.target.value) })} />
                                </div>
                                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                                    <label>Return Reason</label>
                                    <textarea
                                        style={{ width: '100%', borderRadius: 'var(--radius-md)', border: '1.5px solid var(--border)', padding: '0.75rem', background: 'var(--bg-main)', minHeight: '80px' }}
                                        value={returnForm.reason}
                                        onChange={e => setReturnForm({ ...returnForm, reason: e.target.value })}
                                        placeholder="Customer reported defect, wrong item, etc."
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Item Condition</label>
                                    <select value={returnForm.condition} onChange={e => setReturnForm({ ...returnForm, condition: e.target.value })}>
                                        <option value="resellable">Resellable</option>
                                        <option value="damaged">Damaged</option>
                                        <option value="disposed">Disposed</option>
                                    </select>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button className="btn-secondary" onClick={() => setShowReturnModal(false)}>Cancel</button>
                                <button className="btn-primary" onClick={handleCreateReturn} disabled={loading || !returnForm.order_id || !returnForm.reason}>
                                    <Icon name="check" size={16} />
                                    Submit Return
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };
})();
