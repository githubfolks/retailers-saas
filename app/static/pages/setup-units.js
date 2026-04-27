(function () {
    const { Icon } = window.Shared;

    window.Pages['setup-units'] = function SetupUnitsPage() {
        const { units, setItemForm, setShowUnitModal, API, fetchData, showToast } = React.useContext(window.AppContext);

        return (
            <div className="animate-slide">
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
                    <button className="btn-primary" onClick={() => { setItemForm({}); setShowUnitModal(true); }} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <Icon name="plus-circle" size={16} />
                        New Unit
                    </button>
                </div>

                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead><tr><th>Unit Name</th><th>Symbol</th><th>Products</th><th>Actions</th></tr></thead>
                            <tbody>
                                {units.map(u => (
                                    <tr key={u.id}>
                                        <td><strong>{u.name}</strong></td>
                                        <td>
                                            <code style={{ background: 'var(--bg-glass)', padding: '0.2rem 0.6rem', borderRadius: '6px', fontFamily: 'monospace', fontWeight: 700, color: 'var(--primary)' }}>
                                                {u.abbreviation}
                                            </code>
                                        </td>
                                        <td>{u.product_count ?? '—'}</td>
                                        <td>
                                            <div className="table-actions">
                                                <button className="btn-icon" title="Edit" onClick={() => { setItemForm({ ...u }); setShowUnitModal(true); }}>
                                                    <Icon name="edit" size={14} />
                                                </button>
                                                <button className="btn-icon delete" title="Delete" onClick={async () => {
                                                    if (confirm(`Delete unit "${u.name}"?`)) {
                                                        try { await API.delete(`/units/${u.id}`); fetchData(); showToast('Unit removed'); }
                                                        catch (e) { showToast('Delete failed', 'error'); }
                                                    }
                                                }}>
                                                    <Icon name="trash-2" size={14} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {units.length === 0 && (
                        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="ruler" size={40} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                            <p>No units of measure defined</p>
                        </div>
                    )}
                </div>
            </div>
        );
    };
})();
