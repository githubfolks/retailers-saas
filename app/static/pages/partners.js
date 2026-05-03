(function () {
    const { Icon } = window.Shared;

    window.Pages['partners'] = function PartnersPage() {
        const { suppliers, customers, API, fetchData, showToast } = React.useContext(window.AppContext);

        const [showForm, setShowForm] = React.useState(false);
        const [editSupplier, setEditSupplier] = React.useState(null);
        const [saving, setSaving] = React.useState(false);
        const [form, setForm] = React.useState({
            supplier_name: '', phone: '', whatsapp_number: '', email: '',
            contact_person: '', address: '', lead_time_days: 7, payment_terms: ''
        });

        const topCustomers = [...customers].sort((a, b) => (b.total_spent || 0) - (a.total_spent || 0)).slice(0, 10);

        function openAdd() {
            setEditSupplier(null);
            setForm({ supplier_name: '', phone: '', whatsapp_number: '', email: '', contact_person: '', address: '', lead_time_days: 7, payment_terms: '' });
            setShowForm(true);
        }

        function openEdit(s) {
            setEditSupplier(s);
            setForm({
                supplier_name: s.supplier_name || s.name || '',
                phone: s.phone || '',
                whatsapp_number: s.whatsapp_number || '',
                email: s.email || '',
                contact_person: s.contact_person || '',
                address: s.address || '',
                lead_time_days: s.lead_time_days || 7,
                payment_terms: s.payment_terms || ''
            });
            setShowForm(true);
        }

        async function saveSupplier(e) {
            e.preventDefault();
            if (!form.supplier_name.trim() || !form.phone.trim()) {
                showToast('Name and phone are required', 'error');
                return;
            }
            setSaving(true);
            try {
                if (editSupplier) {
                    await API.put(`/procurement/suppliers/${editSupplier.id}`, form);
                    showToast('Supplier updated');
                } else {
                    const params = new URLSearchParams({
                        supplier_name: form.supplier_name,
                        phone: form.phone,
                        ...(form.whatsapp_number && { whatsapp_number: form.whatsapp_number }),
                        ...(form.email && { email: form.email }),
                        lead_time_days: form.lead_time_days
                    });
                    await API.post(`/procurement/suppliers?${params}`);
                    showToast('Supplier added');
                }
                fetchData();
                setShowForm(false);
            } catch (err) {
                showToast('Failed to save supplier', 'error');
            } finally {
                setSaving(false);
            }
        }

        async function deleteSupplier(s) {
            if (!confirm(`Delete "${s.supplier_name || s.name}"?`)) return;
            try {
                await API.delete(`/procurement/suppliers/${s.id}`);
                showToast('Supplier deleted');
                fetchData();
            } catch (err) {
                showToast('Failed to delete supplier', 'error');
            }
        }

        const fieldStyle = { display: 'flex', flexDirection: 'column', gap: '0.25rem' };
        const labelStyle = { fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' };

        return (
            <div className="animate-slide" style={{ display: 'grid', gridTemplateColumns: showForm ? '1fr 1fr 1fr' : '1fr 1fr', gap: '2rem' }}>
                {/* Supply Partners */}
                <div className="table-container">
                    <div className="form-header" style={{ padding: '1.5rem 1.5rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <h4 className="outfit">Supply Partners</h4>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{suppliers.filter(s => s.is_active !== false).length} active vendors</p>
                        </div>
                        <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.9rem', fontSize: '0.8rem' }} onClick={openAdd}>
                            <Icon name="plus" size={14} /> Add Supplier
                        </button>
                    </div>
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead><tr><th>Vendor</th><th>Lead Time</th><th>Status</th><th></th></tr></thead>
                            <tbody>
                                {suppliers.map(s => (
                                    <tr key={s.id} style={{ background: editSupplier?.id === s.id ? 'var(--bg-glass)' : '' }}>
                                        <td>
                                            <div style={{ fontWeight: 600 }}>{s.supplier_name || s.name}</div>
                                            {s.email && <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{s.email}</div>}
                                            {s.phone && <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{s.phone}</div>}
                                        </td>
                                        <td><strong>{s.lead_time_days}d</strong></td>
                                        <td><span className={`badge badge-${s.is_active !== false ? 'success' : 'warning'}`}>{s.is_active !== false ? 'ACTIVE' : 'INACTIVE'}</span></td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.3rem' }}>
                                                <button className="btn-icon" title="Edit" onClick={() => openEdit(s)}><Icon name="edit" size={14} /></button>
                                                <button className="btn-icon" title="Delete" style={{ color: 'var(--danger)' }} onClick={() => deleteSupplier(s)}><Icon name="trash-2" size={14} /></button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {suppliers.length === 0 && <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No supply partners yet. Add your first supplier.</div>}
                    </div>
                </div>

                {/* Top Customers */}
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

                {/* Add / Edit Supplier Panel */}
                {showForm && (
                    <div className="form-card animate-pop" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
                        <div className="form-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h4 className="outfit">{editSupplier ? 'Edit Supplier' : 'New Supplier'}</h4>
                            <button className="btn-icon" onClick={() => setShowForm(false)}><Icon name="x" size={18} /></button>
                        </div>
                        <div className="form-body">
                            <form onSubmit={saveSupplier} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Supplier Name *</label>
                                    <input className="form-input" placeholder="e.g. Global Textiles Ltd." value={form.supplier_name} onChange={e => setForm(f => ({ ...f, supplier_name: e.target.value }))} required />
                                </div>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Contact Person</label>
                                    <input className="form-input" placeholder="Name" value={form.contact_person} onChange={e => setForm(f => ({ ...f, contact_person: e.target.value }))} />
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                                    <div style={fieldStyle}>
                                        <label style={labelStyle}>Phone *</label>
                                        <input className="form-input" placeholder="+91..." value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} required />
                                    </div>
                                    <div style={fieldStyle}>
                                        <label style={labelStyle}>WhatsApp</label>
                                        <input className="form-input" placeholder="+91..." value={form.whatsapp_number} onChange={e => setForm(f => ({ ...f, whatsapp_number: e.target.value }))} />
                                    </div>
                                </div>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Email</label>
                                    <input className="form-input" type="email" placeholder="supplier@email.com" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
                                </div>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Address</label>
                                    <input className="form-input" placeholder="City, State" value={form.address} onChange={e => setForm(f => ({ ...f, address: e.target.value }))} />
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                                    <div style={fieldStyle}>
                                        <label style={labelStyle}>Lead Time (days)</label>
                                        <input className="form-input" type="number" min="1" value={form.lead_time_days} onChange={e => setForm(f => ({ ...f, lead_time_days: parseInt(e.target.value) || 7 }))} />
                                    </div>
                                    <div style={fieldStyle}>
                                        <label style={labelStyle}>Payment Terms</label>
                                        <input className="form-input" placeholder="e.g. Net 30, COD" value={form.payment_terms} onChange={e => setForm(f => ({ ...f, payment_terms: e.target.value }))} />
                                    </div>
                                </div>
                                <button type="submit" className="btn-primary" disabled={saving} style={{ marginTop: '0.5rem' }}>
                                    {saving ? 'Saving...' : (editSupplier ? 'Update Supplier' : 'Add Supplier')}
                                </button>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        );
    };
})();
