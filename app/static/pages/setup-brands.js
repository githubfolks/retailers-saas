(function () {
    const { Icon } = window.Shared;

    window.Pages['setup-brands'] = function SetupBrandsPage() {
        const { brands, setItemForm, setShowBrandModal, API, fetchData, showToast } = React.useContext(window.AppContext);

        return (
            <div className="animate-slide">
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
                    <button className="btn-primary" onClick={() => { setItemForm({}); setShowBrandModal(true); }} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <Icon name="plus-circle" size={16} />
                        New Brand
                    </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1.25rem' }}>
                    {brands.map(b => (
                        <div key={b.id} className="form-card" style={{ margin: 0 }}>
                            <div style={{ padding: '1.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                                    {b.logo_url ? (
                                        <img src={b.logo_url} style={{ width: '44px', height: '44px', objectFit: 'contain', borderRadius: '8px', border: '1px solid var(--border)' }} />
                                    ) : (
                                        <div style={{ width: '44px', height: '44px', borderRadius: '8px', background: 'var(--bg-glass)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <Icon name="award" size={20} style={{ color: 'var(--primary)' }} />
                                        </div>
                                    )}
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 700 }}>{b.name}</div>
                                        {b.product_count != null && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{b.product_count} products</div>}
                                    </div>
                                </div>
                                {b.description && <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: 1.5 }}>{b.description}</div>}
                                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                                    <button className="btn-icon" title="Edit" onClick={() => { setItemForm({ ...b }); setShowBrandModal(true); }}>
                                        <Icon name="edit" size={14} />
                                    </button>
                                    <button className="btn-icon delete" title="Delete" onClick={async () => {
                                        if (confirm(`Delete brand "${b.name}"?`)) {
                                            try { await API.delete(`/brands/${b.id}`); fetchData(); showToast('Brand removed'); }
                                            catch (e) { showToast('Delete failed', 'error'); }
                                        }
                                    }}>
                                        <Icon name="trash-2" size={14} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {brands.length === 0 && (
                    <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        <Icon name="award" size={48} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                        <p>No brands registered yet</p>
                    </div>
                )}
            </div>
        );
    };
})();
