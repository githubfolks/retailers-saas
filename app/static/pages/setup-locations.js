(function () {
    const { Icon } = window.Shared;

    window.Pages['setup-locations'] = function SetupLocationsPage() {
        const {
            locations, warehouses, showLocationModal, setShowLocationModal,
            locationForm, setLocationForm, handleCreateLocation, loading
        } = React.useContext(window.AppContext);

        const [selectedWarehouse, setSelectedWarehouse] = React.useState('all');

        const filtered = selectedWarehouse === 'all' ? locations : locations.filter(l => String(l.warehouse_id) === String(selectedWarehouse));

        const typeColor = { internal: 'success', view: 'primary', inventory: 'accent', production: 'secondary' };

        return (
            <div className="animate-slide">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                        <select
                            style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1.5px solid var(--border)', background: 'var(--bg-card)', fontSize: '0.875rem' }}
                            value={selectedWarehouse}
                            onChange={e => setSelectedWarehouse(e.target.value)}
                        >
                            <option value="all">All Warehouses</option>
                            {warehouses.map(w => <option key={w.id} value={w.id}>{w.warehouse_name || w.name}</option>)}
                        </select>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{filtered.length} locations</span>
                    </div>
                    <button
                        className="btn-primary"
                        disabled={warehouses.length === 0}
                        onClick={() => {
                            setLocationForm({ warehouse_id: warehouses[0]?.id || '', name: '', parent_id: '', location_type: 'internal' });
                            setShowLocationModal(true);
                        }}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}
                    >
                        <Icon name="plus-circle" size={16} />
                        New Location
                    </button>
                </div>

                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr><th>Location Name</th><th>Warehouse</th><th>Parent</th><th>Type</th><th>Stock</th></tr>
                            </thead>
                            <tbody>
                                {filtered.map(l => {
                                    const wh = warehouses.find(w => w.id === l.warehouse_id);
                                    const parent = locations.find(p => p.id === l.parent_id);
                                    return (
                                        <tr key={l.id}>
                                            <td><strong>{l.name}</strong></td>
                                            <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{wh?.warehouse_name || wh?.name || '—'}</td>
                                            <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{parent?.name || <span style={{ opacity: 0.4 }}>Root</span>}</td>
                                            <td><span className={`badge badge-${typeColor[l.location_type] || 'primary'}`}>{l.location_type?.toUpperCase()}</span></td>
                                            <td>{l.stock_count != null ? `${l.stock_count} units` : '—'}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                    {filtered.length === 0 && (
                        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="map-pin" size={40} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                            <p>{warehouses.length === 0 ? 'Create a warehouse first to add locations.' : 'No locations defined for this warehouse.'}</p>
                        </div>
                    )}
                </div>
            </div>
        );
    };
})();
