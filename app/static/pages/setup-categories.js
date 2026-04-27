(function () {
    const { Icon } = window.Shared;

    window.Pages['setup-categories'] = function SetupCategoriesPage() {
        const { categories, setItemForm, setShowCategoryModal, API, fetchData, showToast } = React.useContext(window.AppContext);

        const getCategoryPath = (cat) => {
            const path = [cat.name];
            let current = cat;
            while (current.parent_id) {
                const parent = categories.find(c => c.id === current.parent_id);
                if (!parent) break;
                path.unshift(parent.name);
                current = parent;
            }
            return path.join(' › ');
        };

        return (
            <div className="animate-slide">
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
                    <button className="btn-primary" onClick={() => { setItemForm({}); setShowCategoryModal(true); }} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <Icon name="plus-circle" size={16} />
                        New Category
                    </button>
                </div>

                <div className="table-container">
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead><tr><th>Category</th><th>Hierarchy Path</th><th>Products</th><th>Actions</th></tr></thead>
                            <tbody>
                                {categories.map(c => (
                                    <tr key={c.id}>
                                        <td>
                                            <strong>{c.name}</strong>
                                            {c.description && <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.description}</div>}
                                        </td>
                                        <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{getCategoryPath(c)}</td>
                                        <td>{c.product_count ?? '—'}</td>
                                        <td>
                                            <div className="table-actions">
                                                <button className="btn-icon" title="Edit" onClick={() => { setItemForm({ ...c }); setShowCategoryModal(true); }}>
                                                    <Icon name="edit" size={14} />
                                                </button>
                                                <button className="btn-icon delete" title="Delete" onClick={async () => {
                                                    if (confirm(`Delete category "${c.name}"?`)) {
                                                        try { await API.delete(`/categories/${c.id}`); fetchData(); showToast('Category removed'); }
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
                    {categories.length === 0 && (
                        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <Icon name="layers" size={40} style={{ marginBottom: '1rem', opacity: 0.4 }} />
                            <p>No categories defined yet</p>
                        </div>
                    )}
                </div>
            </div>
        );
    };
})();
