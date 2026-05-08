(function () {
    const { Icon } = window.Shared;

    window.Pages['products'] = function ProductsPage() {
        const {
            products, attributes, loading, API, fetchData, showToast, handleBulkUpload,
            setProductForm, setWizardStep, setShowProductWizard,
            setSkuDetail, setSkuPlatforms, setSkuBarcodes, setShowSkuPanel, setSkuPanelLoading
        } = React.useContext(window.AppContext);

        const [searchTerm, setSearchTerm] = React.useState('');
        const [currentPage, setCurrentPage] = React.useState(1);
        const itemsPerPage = 10;

        const filteredProducts = products.filter(p => 
            (p.name || '').toLowerCase().includes(searchTerm.toLowerCase()) || 
            (p.sku || '').toLowerCase().includes(searchTerm.toLowerCase())
        );
        const totalPages = Math.ceil(filteredProducts.length / itemsPerPage) || 1;
        const currentProducts = filteredProducts.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

        return (
            <div className="view-container animate-fade">
                <div className="view-header" style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ position: 'relative', width: '300px' }}>
                        <Icon name="search" size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input 
                            type="text" 
                            placeholder="Search products or SKUs..." 
                            value={searchTerm}
                            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                            style={{ width: '100%', padding: '0.6rem 1rem 0.6rem 2.5rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--bg-main)' }}
                        />
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <label className="btn-secondary" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.8rem', padding: '0.6rem 1.2rem', borderRadius: '10px' }}>
                            <Icon name="upload-cloud" size={18} />
                            <span style={{ fontWeight: 600 }}>Bulk Import (CSV)</span>
                            <input type="file" accept=".csv" style={{ display: 'none' }} onChange={handleBulkUpload} />
                        </label>
                        <button className="btn-primary"
                            onClick={() => { setWizardStep(1); setProductForm({ name: '', description: '', price: 0, category_id: '', brand_id: '', unit_id: '', variants: [], image_urls: [] }); setShowProductWizard(true); }}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', padding: '0.6rem 1.2rem', borderRadius: '10px' }}>
                            <Icon name="plus-circle" size={18} />
                            <span style={{ fontWeight: 600 }}>Add Product</span>
                        </button>
                    </div>
                </div>
                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>SKU / Product Name</th>
                                    <th>Brand / Category</th>
                                    <th>Price (INR)</th>
                                    <th>Qty / Unit</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {currentProducts.map((p, idx) => (
                                    <tr key={p.id} className={`animate-fade delay-${(idx % 3) + 1}`}>
                                        <td style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                            <div style={{ width: '48px', height: '48px', borderRadius: '8px', background: 'var(--bg-glass)', overflow: 'hidden', flexShrink: 0, border: '1px solid var(--border)' }}>
                                                {p.images && p.images.find(img => img.is_primary)
                                                    ? <img src={p.images.find(img => img.is_primary).url} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                                    : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}><Icon name="image" size={16} /></div>
                                                }
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '14px', fontWeight: 600 }}>{p.name}</div>
                                                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{p.sku}</div>
                                                {p.variants && p.variants.length > 0 && (
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.3rem', flexWrap: 'wrap' }}>
                                                        <span style={{ padding: '0.1rem 0.45rem', background: 'var(--primary)', color: 'white', borderRadius: '999px', fontSize: '0.6rem', fontWeight: 800 }}>{p.variants.length} variants</span>
                                                        {[...new Set(p.variants.map(v => v.color).filter(Boolean))].slice(0, 6).map((clr, ci) => {
                                                            const colorAttrVal = attributes.flatMap(a => a.values).find(av => av.value === clr);
                                                            return colorAttrVal?.hex_color
                                                                ? <div key={ci} title={clr} style={{ width: '10px', height: '10px', borderRadius: '50%', background: colorAttrVal.hex_color, border: '1.5px solid var(--border)', flexShrink: 0 }}></div>
                                                                : <span key={ci} style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{clr}</span>;
                                                        })}
                                                        {[...new Set(p.variants.map(v => v.size).filter(Boolean))].slice(0, 5).map((sz, si) => (
                                                            <span key={si} style={{ fontSize: '0.6rem', padding: '0 0.3rem', border: '1px solid var(--border)', borderRadius: '4px', color: 'var(--text-muted)' }}>{sz}</span>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td>
                                            <div style={{ fontSize: '12px', fontWeight: 500, color: 'var(--primary)' }}>{p.brand_rel ? p.brand_rel.name : 'No Brand'}</div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{p.category_rel ? p.category_rel.name : 'Uncategorized'}</div>
                                        </td>
                                        <td><div style={{ fontWeight: 700 }}>₹{p.price.toLocaleString()}</div></td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <div style={{ width: '4px', height: '16px', borderRadius: '2px', background: p.quantity > 5 ? 'var(--success)' : 'var(--accent)' }}></div>
                                                <span>{p.quantity} Units</span>
                                            </div>
                                        </td>
                                        <td>
                                            <div className="table-actions">
                                                <button className="btn-icon" title="Edit Product" onClick={() => { setProductForm({ ...p, image_urls: p.images ? p.images.map(img => img.url) : [], category_id: p.category_id || '', brand_id: p.brand_id || '', unit_id: p.unit_id || '' }); setWizardStep(1); setShowProductWizard(true); }}><Icon name="edit" size={14} /></button>
                                                <button className="btn-icon" style={{ color: 'var(--primary)' }} title="Full Trace" onClick={async () => {
                                                    setSkuDetail(null); setSkuPlatforms([]); setSkuBarcodes([]);
                                                    setShowSkuPanel(true); setSkuPanelLoading(true);
                                                    try {
                                                        const [lookupRes, platformsRes, barcodesRes] = await Promise.all([
                                                            API.get('/sku/lookup/' + p.sku),
                                                            API.get('/sku/' + p.sku + '/platforms'),
                                                            API.get('/sku/' + p.sku + '/barcodes')
                                                        ]);
                                                        setSkuDetail(lookupRes.data);
                                                        setSkuPlatforms(platformsRes.data);
                                                        setSkuBarcodes(barcodesRes.data);
                                                    } catch (e) { showToast('SKU trace failed', 'error'); setShowSkuPanel(false); }
                                                    finally { setSkuPanelLoading(false); }
                                                }}><Icon name="search" size={14} /></button>
                                                <button className="btn-icon delete" title="Delete Product" onClick={async () => { if (confirm('Delete ' + p.name + '?')) { try { await API.delete('/products/' + p.id); showToast('Product deleted', 'success'); fetchData(); } catch (e) { showToast('Delete failed', 'error'); } } }}><Icon name="trash-2" size={14} /></button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {products.length === 0 && !loading && (
                        <div style={{ padding: '6rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="package-search" size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                            <p>Catalog is empty. Add your first product to begin.</p>
                        </div>
                    )}
                    {filteredProducts.length === 0 && products.length > 0 && (
                        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <p>No products match your search.</p>
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
