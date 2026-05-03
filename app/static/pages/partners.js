(function () {
    const { Icon } = window.Shared;

    window.Pages['partners'] = function PartnersPage() {
        const { suppliers, customers, logisticsPartners, setLogisticsPartners, API, fetchData, showToast } = React.useContext(window.AppContext);

        const [showForm, setShowForm] = React.useState(false);
        const [editSupplier, setEditSupplier] = React.useState(null);
        const [saving, setSaving] = React.useState(false);
        const [form, setForm] = React.useState({
            supplier_name: '', phone: '', whatsapp_number: '', email: '',
            contact_person: '', address: '', lead_time_days: 7, payment_terms: ''
        });

        const [showLpForm, setShowLpForm] = React.useState(false);
        const [editLp, setEditLp] = React.useState(null);
        const [savingLp, setSavingLp] = React.useState(false);
        const [lpForm, setLpForm] = React.useState({
            name: '', provider_type: 'manual', api_email: '', api_password: '',
            pickup_location_name: '', tracking_url_template: '', contact_phone: '', contact_email: ''
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

        function openAddLp() {
            setEditLp(null);
            setLpForm({ name: '', tracking_url_template: '', contact_phone: '', contact_email: '' });
            setShowLpForm(true);
        }

        function openEditLp(lp) {
            setEditLp(lp);
            setLpForm({
                name: lp.name || '',
                provider_type: lp.provider_type || 'manual',
                api_email: lp.api_email || '',
                api_password: '',
                pickup_location_name: lp.pickup_location_name || '',
                tracking_url_template: lp.tracking_url_template || '',
                contact_phone: lp.contact_phone || '',
                contact_email: lp.contact_email || ''
            });
            setShowLpForm(true);
        }

        async function saveLp(e) {
            e.preventDefault();
            if (!lpForm.name.trim()) { showToast('Name is required', 'error'); return; }
            setSavingLp(true);
            try {
                const payload = { ...lpForm };
                if (editLp && !payload.api_password) delete payload.api_password;
                if (editLp) {
                    await API.put(`/procurement/logistics-partners/${editLp.id}`, payload);
                    showToast('Logistics partner updated');
                } else {
                    await API.post('/procurement/logistics-partners', payload);
                    showToast('Logistics partner added');
                }
                fetchData();
                setShowLpForm(false);
            } catch (err) {
                showToast('Failed to save logistics partner', 'error');
            } finally {
                setSavingLp(false);
            }
        }

        async function deleteLp(lp) {
            if (!confirm(`Remove "${lp.name}"?`)) return;
            try {
                await API.delete(`/procurement/logistics-partners/${lp.id}`);
                showToast('Logistics partner removed');
                fetchData();
            } catch (err) {
                showToast('Failed to remove logistics partner', 'error');
            }
        }

        const fieldStyle = { display: 'flex', flexDirection: 'column', gap: '0.25rem' };
        const labelStyle = { fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' };

        const panelOpen = showForm || showLpForm;

        return (
            <div className="animate-slide" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: panelOpen ? '1fr 1fr 1fr' : '1fr 1fr', gap: '2rem' }}>
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

                {/* Add / Edit Logistics Partner Panel */}
                {showLpForm && (
                    <div className="form-card animate-pop" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
                        <div className="form-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h4 className="outfit">{editLp ? 'Edit Courier' : 'New Courier'}</h4>
                            <button className="btn-icon" onClick={() => setShowLpForm(false)}><Icon name="x" size={18} /></button>
                        </div>
                        <div className="form-body">
                            <form onSubmit={saveLp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Courier Name *</label>
                                    <input className="form-input" placeholder="e.g. Shiprocket" value={lpForm.name} onChange={e => setLpForm(f => ({ ...f, name: e.target.value }))} required />
                                </div>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Provider Type</label>
                                    <select className="form-input" value={lpForm.provider_type} onChange={e => setLpForm(f => ({ ...f, provider_type: e.target.value }))}>
                                        <option value="manual">Manual (enter AWB yourself)</option>
                                        <option value="shiprocket">Shiprocket (auto-assign AWB)</option>
                                    </select>
                                </div>
                                {lpForm.provider_type === 'shiprocket' && (
                                    <>
                                        <div style={fieldStyle}>
                                            <label style={labelStyle}>Shiprocket Email *</label>
                                            <input className="form-input" type="email" placeholder="your@shiprocket.com" value={lpForm.api_email} onChange={e => setLpForm(f => ({ ...f, api_email: e.target.value }))} />
                                        </div>
                                        <div style={fieldStyle}>
                                            <label style={labelStyle}>{editLp ? 'Shiprocket Password (leave blank to keep)' : 'Shiprocket Password *'}</label>
                                            <input className="form-input" type="password" placeholder="••••••••" value={lpForm.api_password} onChange={e => setLpForm(f => ({ ...f, api_password: e.target.value }))} />
                                        </div>
                                        <div style={fieldStyle}>
                                            <label style={labelStyle}>Pickup Location Name</label>
                                            <input className="form-input" placeholder="Primary (as set in Shiprocket)" value={lpForm.pickup_location_name} onChange={e => setLpForm(f => ({ ...f, pickup_location_name: e.target.value }))} />
                                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Must match the pickup address label in your Shiprocket account</span>
                                        </div>
                                    </>
                                )}
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                                    <div style={fieldStyle}>
                                        <label style={labelStyle}>Contact Phone</label>
                                        <input className="form-input" placeholder="+91..." value={lpForm.contact_phone} onChange={e => setLpForm(f => ({ ...f, contact_phone: e.target.value }))} />
                                    </div>
                                    <div style={fieldStyle}>
                                        <label style={labelStyle}>Contact Email</label>
                                        <input className="form-input" type="email" placeholder="support@courier.com" value={lpForm.contact_email} onChange={e => setLpForm(f => ({ ...f, contact_email: e.target.value }))} />
                                    </div>
                                </div>
                                <div style={fieldStyle}>
                                    <label style={labelStyle}>Tracking URL Template</label>
                                    <input className="form-input" placeholder="https://courier.com/track/{awb}" value={lpForm.tracking_url_template} onChange={e => setLpForm(f => ({ ...f, tracking_url_template: e.target.value }))} />
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Use {'{awb}'} as placeholder for the tracking number</span>
                                </div>
                                <button type="submit" className="btn-primary" disabled={savingLp} style={{ marginTop: '0.5rem' }}>
                                    {savingLp ? 'Saving...' : (editLp ? 'Update Courier' : 'Add Courier')}
                                </button>
                            </form>
                        </div>
                    </div>
                )}
            </div>

            {/* Logistics Partners */}
            <div className="table-container">
                <div className="form-header" style={{ padding: '1.5rem 1.5rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h4 className="outfit">Logistics Partners</h4>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Courier companies used for shipping</p>
                    </div>
                    <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.9rem', fontSize: '0.8rem' }} onClick={openAddLp}>
                        <Icon name="plus" size={14} /> Add Courier
                    </button>
                </div>
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead><tr><th>Courier</th><th>Contact</th><th>Tracking URL</th><th></th></tr></thead>
                        <tbody>
                            {logisticsPartners.map(lp => (
                                <tr key={lp.id} style={{ background: editLp?.id === lp.id ? 'var(--bg-glass)' : '' }}>
                                    <td>
                                        <div style={{ fontWeight: 600 }}>{lp.name}</div>
                                        <span className={`badge badge-${lp.provider_type === 'shiprocket' ? 'accent' : 'secondary'}`} style={{ fontSize: '10px' }}>
                                            {lp.provider_type === 'shiprocket' ? 'Auto AWB' : 'Manual'}
                                        </span>
                                    </td>
                                    <td>
                                        {lp.contact_phone && <div style={{ fontSize: '12px' }}>{lp.contact_phone}</div>}
                                        {lp.contact_email && <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{lp.contact_email}</div>}
                                        {!lp.contact_phone && !lp.contact_email && <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>—</span>}
                                    </td>
                                    <td>
                                        {lp.tracking_url_template
                                            ? <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{lp.tracking_url_template.replace('{awb}', '…')}</span>
                                            : <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>—</span>}
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '0.3rem' }}>
                                            <button className="btn-icon" title="Edit" onClick={() => openEditLp(lp)}><Icon name="edit" size={14} /></button>
                                            <button className="btn-icon" title="Delete" style={{ color: 'var(--danger)' }} onClick={() => deleteLp(lp)}><Icon name="trash-2" size={14} /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {logisticsPartners.length === 0 && <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No couriers added yet. Add one to enable the dropdown in the Ship Order screen.</div>}
                </div>
            </div>
            </div>
        );
    };
})();
