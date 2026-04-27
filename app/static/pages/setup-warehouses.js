(function () {
    const { Icon } = window.Shared;

    window.Pages['setup-warehouses'] = function SetupWarehousesPage() {
        const {
            warehouses, showWarehouseModal, setShowWarehouseModal,
            warehouseForm, setWarehouseForm, API, fetchData, showToast, loading
        } = React.useContext(window.AppContext);

        const handleCreate = async () => {
            try {
                await API.post('/inventory/warehouses', {
                    warehouse_name: warehouseForm.name,
                    code: warehouseForm.code,
                    address: warehouseForm.address,
                    capacity: parseInt(warehouseForm.capacity) || 1000
                });
                showToast('Warehouse established');
                setShowWarehouseModal(false);
                setWarehouseForm({ name: '', code: '', address: '', capacity: 1000 });
                fetchData();
            } catch (e) {
                showToast('Failed to create warehouse', 'error');
            }
        };

        return (
            <div className="animate-fade" style={{ padding: '1rem 0' }}>
                {/* Header Section */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border)' }}>
                    <div>
                        <h3 className="outfit" style={{ fontSize: '1.5rem', fontWeight: 800, margin: '0 0 0.25rem 0', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>Warehouse Network</h3>
                        <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Manage your physical fulfillment centers and distribution nodes across the globe.</p>
                    </div>
                    <button className="btn-primary animate-pop" onClick={() => setShowWarehouseModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1.25rem', borderRadius: '12px', fontWeight: 600, boxShadow: '0 4px 14px var(--bg-glass)' }}>
                        <Icon name="plus-circle" size={18} />
                        Establish New Node
                    </button>
                </div>

                {/* Grid Section */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '2rem' }}>
                    {warehouses.map((w, idx) => (
                        <div key={w.id} className={`form-card animate-pop delay-${(idx % 3) + 1}`} style={{
                            margin: 0,
                            background: 'linear-gradient(145deg, var(--surface) 0%, rgba(255,255,255,0.01) 100%)',
                            border: '1px solid var(--border)',
                            borderRadius: '16px',
                            overflow: 'hidden',
                            position: 'relative',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            cursor: 'pointer',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-6px)';
                            e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
                            e.currentTarget.style.borderColor = 'var(--primary-light)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)';
                            e.currentTarget.style.borderColor = 'var(--border)';
                        }}
                        >
                            {/* Card Header */}
                            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', background: 'rgba(255,255,255,0.03)' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 4px 12px var(--bg-glass)' }}>
                                        <Icon name="warehouse" size={22} />
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: 800, fontSize: '1.15rem', letterSpacing: '-0.02em', color: 'var(--text-primary)', marginBottom: '0.15rem' }}>{w.warehouse_name || w.name}</div>
                                        <div style={{ fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', background: 'var(--bg-glass)', color: 'var(--primary)', padding: '0.1rem 0.5rem', borderRadius: '4px', fontWeight: 700, letterSpacing: '0.05em' }}>
                                            {w.code}
                                        </div>
                                    </div>
                                </div>
                                <button className="btn-icon" style={{ padding: '0.25rem' }} title="Configure Node"><Icon name="more-horizontal" size={20}/></button>
                            </div>
                            
                            {/* Card Body */}
                            <div style={{ padding: '1.5rem' }}>
                                {w.address ? (
                                    <div style={{ display: 'flex', gap: '0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem', alignItems: 'flex-start' }}>
                                        <Icon name="map-pin" size={16} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--primary)' }} />
                                        <span style={{ lineHeight: '1.5' }}>{w.address}</span>
                                    </div>
                                ) : (
                                    <div style={{ display: 'flex', gap: '0.75rem', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem', opacity: 0.6 }}>
                                        <Icon name="map-pin" size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                                        <span>No physical address mapped</span>
                                    </div>
                                )}
                                
                                {/* Metrics */}
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', padding: '1rem', background: 'var(--bg-main)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                                    <div>
                                        <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 600 }}>Zones / Bins</div>
                                        <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <Icon name="layout-grid" size={16} style={{ color: 'var(--success)' }}/> {w.location_count || 0}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 600 }}>Total Capacity</div>
                                        <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <Icon name="box" size={16} style={{ color: 'var(--primary)' }}/> {(w.capacity || 0).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Empty State */}
                {warehouses.length === 0 && (
                    <div style={{ padding: '6rem 2rem', textAlign: 'center', background: 'var(--surface)', borderRadius: '24px', border: '1px dashed var(--border)', marginTop: '2rem' }}>
                        <div style={{ width: '80px', height: '80px', background: 'var(--bg-glass)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem', color: 'var(--primary)' }}>
                            <Icon name="warehouse" size={36} />
                        </div>
                        <h3 className="outfit" style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>No Warehouses Configured</h3>
                        <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto 2rem', lineHeight: '1.6' }}>Establish your first distribution node to start managing inventory locations, stock valuations, and fulfillments.</p>
                        <button className="btn-primary animate-pop" onClick={() => setShowWarehouseModal(true)} style={{ padding: '0.75rem 1.5rem', borderRadius: '12px', fontWeight: 600 }}>
                            <Icon name="plus" size={18} /> Establish First Node
                        </button>
                    </div>
                )}

                {/* Modal */}
                {showWarehouseModal && (
                    <div className="modal-overlay" onClick={() => setShowWarehouseModal(false)}>
                        <div className="modal-content animate-pop" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px', borderRadius: '20px', padding: 0, overflow: 'hidden' }}>
                            <div style={{ background: 'var(--bg-glass)', padding: '1.5rem', borderBottom: '1px solid var(--border)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div style={{ width: '40px', height: '40px', background: 'var(--primary)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                                            <Icon name="warehouse" size={20} />
                                        </div>
                                        <h3 className="outfit" style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Create Warehouse</h3>
                                    </div>
                                    <button className="btn-icon" onClick={() => setShowWarehouseModal(false)}><Icon name="x" size={20} /></button>
                                </div>
                            </div>
                            
                            <div className="modal-body" style={{ padding: '1.5rem' }}>
                                <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                                    <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'block' }}>Warehouse Name</label>
                                    <input 
                                        style={{ width: '100%', padding: '0.75rem', borderRadius: '10px', border: '1.5px solid var(--border)', background: 'var(--bg-main)', fontSize: '1rem', transition: 'border-color 0.2s' }}
                                        value={warehouseForm.name} 
                                        onChange={e => setWarehouseForm({ ...warehouseForm, name: e.target.value })} 
                                        placeholder="e.g., Main Distribution Centre" 
                                    />
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                                    <div className="form-group">
                                        <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'block' }}>Short Code</label>
                                        <input 
                                            style={{ width: '100%', padding: '0.75rem', borderRadius: '10px', border: '1.5px solid var(--border)', background: 'var(--bg-main)', fontSize: '1rem' }}
                                            value={warehouseForm.code} 
                                            onChange={e => setWarehouseForm({ ...warehouseForm, code: e.target.value.toUpperCase() })} 
                                            placeholder="e.g., WH01" 
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'block' }}>Capacity (units)</label>
                                        <input 
                                            type="number" 
                                            style={{ width: '100%', padding: '0.75rem', borderRadius: '10px', border: '1.5px solid var(--border)', background: 'var(--bg-main)', fontSize: '1rem' }}
                                            value={warehouseForm.capacity} 
                                            onChange={e => setWarehouseForm({ ...warehouseForm, capacity: e.target.value })} 
                                        />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'block' }}>Physical Address</label>
                                    <textarea
                                        style={{ width: '100%', borderRadius: '10px', border: '1.5px solid var(--border)', padding: '0.75rem', background: 'var(--bg-main)', minHeight: '80px', fontSize: '0.95rem', resize: 'vertical' }}
                                        value={warehouseForm.address}
                                        onChange={e => setWarehouseForm({ ...warehouseForm, address: e.target.value })}
                                        placeholder="Enter the complete address for logistics routing..."
                                    />
                                </div>
                            </div>
                            
                            <div className="modal-footer" style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                                <button className="btn-secondary" onClick={() => setShowWarehouseModal(false)} style={{ padding: '0.75rem 1.5rem', borderRadius: '10px', fontWeight: 600 }}>Cancel</button>
                                <button className="btn-primary animate-pop" onClick={handleCreate} disabled={loading || !warehouseForm.name || !warehouseForm.code} style={{ padding: '0.75rem 1.5rem', borderRadius: '10px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Icon name="check-circle" size={18} />
                                    Create Warehouse
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };
})();
