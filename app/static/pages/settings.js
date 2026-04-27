(function () {
    const { SettingsField } = window.Shared;

    window.Pages['settings'] = function SettingsPage() {
        const { settings, setSettings, updateConfig, loading, userRole } = React.useContext(window.AppContext);

        return (
            <div className="dashboard-content">
                <div className="settings-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
                    <div className="form-card animate-slide delay-1">
                        <div className="form-header">
                            <h3 className="outfit">Integration Keys</h3>
                            <p>Manage secondary services (WhatsApp &amp; Razorpay)</p>
                        </div>
                        <div className="form-body">
                            <div style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '12px', marginBottom: '1.5rem', border: '1px solid rgba(59, 130, 246, 0.1)' }}>
                                <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: '#3b82f6' }}>WhatsApp Business API</h4>
                                <SettingsField label="WhatsApp Number" value={settings.whatsapp_number} onChange={v => setSettings({ ...settings, whatsapp_number: v })} placeholder="919876543210" />
                            </div>
                            <div style={{ padding: '1rem', background: 'rgba(139, 92, 246, 0.05)', borderRadius: '12px', border: '1px solid rgba(139, 92, 246, 0.1)' }}>
                                <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: '#8b5cf6' }}>Razorpay Payments</h4>
                                <SettingsField label="Account Key ID" value={settings.razorpay_key} onChange={v => setSettings({ ...settings, razorpay_key: v })} placeholder="rzp_live_..." />
                            </div>
                            <button className="btn-primary" onClick={updateConfig} disabled={loading || userRole !== 'owner'}
                                style={{ width: '100%', marginTop: '1.5rem', background: userRole === 'owner' ? 'var(--primary)' : 'var(--text-muted)', opacity: userRole === 'owner' ? 1 : 0.6, cursor: userRole === 'owner' ? 'pointer' : 'not-allowed' }}>
                                {userRole === 'owner' ? 'Update All Keys' : 'Owner Only Permission'}
                            </button>
                        </div>
                    </div>

                    <div className="form-card animate-slide delay-2">
                        <div className="form-header">
                            <h3 className="outfit">Brand Identity</h3>
                            <p>Personalize your dashboard and visual personality</p>
                        </div>
                        <div className="form-body">
                            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Primary Brand Color</label>
                                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                                    <input type="color" value={settings.primary_color || '#0d9488'} onChange={e => setSettings({ ...settings, primary_color: e.target.value })} style={{ width: '44px', height: '44px', padding: '0', border: 'none', background: 'none' }} disabled={userRole !== 'owner'} />
                                    <input type="text" value={settings.primary_color || '#0d9488'} onChange={e => setSettings({ ...settings, primary_color: e.target.value })} placeholder="#000000" style={{ flex: 1 }} disabled={userRole !== 'owner'} />
                                </div>
                            </div>
                            <SettingsField label="Logo Asset URL" value={settings.logo_url} onChange={v => setSettings({ ...settings, logo_url: v })} placeholder="https://assets.business.com/logo.png" hint="Provide a link to your brand logo (PNG/SVG recommended)" disabled={userRole !== 'owner'} />
                            <button className="btn-primary" onClick={updateConfig} disabled={loading || userRole !== 'owner'}
                                style={{ width: '100%', marginTop: '1.5rem', background: userRole === 'owner' ? 'var(--primary)' : 'var(--text-muted)', opacity: userRole === 'owner' ? 1 : 0.6, cursor: userRole === 'owner' ? 'pointer' : 'not-allowed' }}>
                                {userRole === 'owner' ? 'Update Brand Theme' : 'Owner Only Permission'}
                            </button>
                        </div>
                    </div>

                    <div className="form-card animate-slide delay-3">
                        <div className="form-header">
                            <h3 className="outfit">Business Profile</h3>
                            <p>Used for GST-compliant invoicing</p>
                        </div>
                        <div className="form-body">
                            <SettingsField label="GSTIN" value={settings.gstin} onChange={v => setSettings({ ...settings, gstin: v })} placeholder="27AAAAA0000A1Z5" />
                            <SettingsField label="Address Line 1" value={settings.address_line1} onChange={v => setSettings({ ...settings, address_line1: v })} placeholder="Unit No, Building Name" />
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                <SettingsField label="City" value={settings.city} onChange={v => setSettings({ ...settings, city: v })} placeholder="Mumbai" />
                                <SettingsField label="Pincode" value={settings.pincode} onChange={v => setSettings({ ...settings, pincode: v })} placeholder="400001" />
                            </div>
                            <SettingsField label="State" value={settings.state} onChange={v => setSettings({ ...settings, state: v })} placeholder="Maharashtra" />
                            <button className="btn-primary" onClick={updateConfig} disabled={loading || userRole !== 'owner'}
                                style={{ width: '100%', marginTop: '1.5rem', background: 'var(--accent)', cursor: userRole === 'owner' ? 'pointer' : 'not-allowed' }}>
                                Update Business Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    };
})();
