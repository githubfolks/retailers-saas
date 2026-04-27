(function () {
    const { Icon } = window.Shared;

    // Renders a QR code into a canvas element using the bundled qrcode library
    function QRCanvas({ url }) {
        const canvasRef = React.useRef(null);
        React.useEffect(() => {
            if (!canvasRef.current || !url) return;
            if (typeof QRCode === 'undefined') return;
            QRCode.toCanvas(canvasRef.current, url, { width: 220, margin: 1 }, () => {});
        }, [url]);
        return React.createElement('canvas', { ref: canvasRef });
    }

    // Modal shown when payment_method === 'upi' — shows QR, polls for payment, then shows receipt
    function UPIPaymentModal({ orderId, paymentUrl, orderData, onPaid, onCancel, API }) {
        const [status, setStatus] = React.useState('pending'); // pending | paid | timeout
        const [copied, setCopied]   = React.useState(false);
        const intervalRef = React.useRef(null);
        const attemptsRef = React.useRef(0);
        const MAX_POLLS = 60; // 3 min at 3 s intervals

        React.useEffect(() => {
            if (!orderId || !paymentUrl) return;
            intervalRef.current = setInterval(async () => {
                attemptsRef.current += 1;
                if (attemptsRef.current > MAX_POLLS) {
                    clearInterval(intervalRef.current);
                    setStatus('timeout');
                    return;
                }
                try {
                    const res = await API.get(`/orders/${orderId}/payment-status`);
                    if (res.data.payment_status === 'paid') {
                        clearInterval(intervalRef.current);
                        setStatus('paid');
                        setTimeout(onPaid, 1200);
                    }
                } catch (_) {}
            }, 3000);
            return () => clearInterval(intervalRef.current);
        }, [orderId]);

        const copyLink = () => {
            navigator.clipboard.writeText(paymentUrl).then(() => {
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            });
        };

        return (
            <div className="modal-overlay" onClick={onCancel}>
                <div className="modal-content animate-pop" onClick={e => e.stopPropagation()} style={{ maxWidth: '420px', borderRadius: '20px', padding: 0, overflow: 'hidden' }}>
                    <div style={{ background: 'var(--bg-glass)', padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <Icon name="smartphone" size={20} style={{ color: 'var(--primary)' }} />
                            <h3 className="outfit" style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>UPI Payment</h3>
                        </div>
                        <button className="btn-icon" onClick={onCancel}><Icon name="x" size={20} /></button>
                    </div>

                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        {status === 'paid' ? (
                            <div style={{ padding: '2rem 0' }}>
                                <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem', color: 'white' }}>
                                    <Icon name="check" size={36} />
                                </div>
                                <h3 className="outfit" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--success)', marginBottom: '0.5rem' }}>Payment Received!</h3>
                                <p style={{ color: 'var(--text-secondary)' }}>Generating receipt…</p>
                            </div>
                        ) : status === 'timeout' ? (
                            <div style={{ padding: '1rem 0' }}>
                                <Icon name="clock" size={48} style={{ color: 'var(--warning)', marginBottom: '1rem' }} />
                                <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Payment link expired</p>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Ask the customer to scan again or switch to cash.</p>
                                <button className="btn-secondary" style={{ marginTop: '1rem' }} onClick={onCancel}>Close</button>
                            </div>
                        ) : (
                            <>
                                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem', fontSize: '0.9rem' }}>Ask the customer to scan this QR with any UPI app</p>

                                <div style={{ display: 'inline-block', padding: '1rem', background: 'white', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '1.25rem' }}>
                                    <QRCanvas url={paymentUrl} />
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-main)', borderRadius: '8px', padding: '0.5rem 0.75rem', marginBottom: '1.25rem' }}>
                                    <span style={{ flex: 1, fontSize: '0.8rem', color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{paymentUrl}</span>
                                    <button className="btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem', flexShrink: 0 }} onClick={copyLink}>
                                        <Icon name={copied ? 'check' : 'copy'} size={14} /> {copied ? 'Copied' : 'Copy'}
                                    </button>
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    <Icon name="loader" size={14} />
                                    Waiting for payment confirmation…
                                </div>

                                <div style={{ marginTop: '1.5rem', padding: '0.75rem 1rem', background: 'var(--bg-glass)', borderRadius: '10px', textAlign: 'left', fontSize: '0.875rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: 'var(--text-primary)' }}>
                                        <span>Amount Due</span>
                                        <span>₹{orderData.total_amount?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    // Receipt modal shown after a completed sale
    function ReceiptModal({ orderData, onClose }) {
        const now = new Date();
        const dateStr = now.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
        const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

        return (
            <div className="modal-overlay" onClick={onClose}>
                <div className="modal-content animate-pop" onClick={e => e.stopPropagation()} style={{ maxWidth: '380px', borderRadius: '20px', padding: 0, overflow: 'hidden' }}>
                    <div style={{ background: 'var(--primary)', padding: '1.25rem 1.5rem', color: 'white', textAlign: 'center' }}>
                        <Icon name="check-circle" size={32} style={{ marginBottom: '0.5rem' }} />
                        <h3 className="outfit" style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Sale Complete</h3>
                        <p style={{ margin: '0.25rem 0 0', opacity: 0.85, fontSize: '0.85rem' }}>{orderData.business_name}</p>
                    </div>

                    <div style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                            <span>Order #{orderData.order_id}</span>
                            <span>{dateStr} {timeStr}</span>
                        </div>

                        <div style={{ borderTop: '1px dashed var(--border)', borderBottom: '1px dashed var(--border)', padding: '0.75rem 0', marginBottom: '1rem' }}>
                            {orderData.items?.map((item, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{item.name} <span style={{ color: 'var(--text-muted)' }}>×{item.quantity}</span></span>
                                    <span style={{ fontWeight: 600 }}>₹{(item.unit_price * item.quantity).toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                                </div>
                            ))}
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: '1.1rem', marginBottom: '1.5rem' }}>
                            <span>Total Paid</span>
                            <span style={{ color: 'var(--primary)' }}>₹{orderData.total_amount?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
                            <span style={{ padding: '0.25rem 1rem', borderRadius: '20px', background: 'var(--primary-light)', color: 'var(--primary)', fontWeight: 600, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                {orderData.payment_method === 'upi' ? 'UPI' : orderData.payment_method === 'cash' ? 'Cash' : 'Card'} · Paid
                            </span>
                        </div>

                        <button className="btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.875rem' }} onClick={onClose}>
                            <Icon name="plus" size={18} /> New Sale
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    window.Pages['pos'] = function POSPage() {
        const {
            products, customers, API, showToast, fetchData,
            posCart, setPosCart, posSearchSearch, setPosSearch,
            posPaymentMethod, setPosPaymentMethod, posSelectedCustomer, setPosSelectedCustomer,
            posCategory, setPosCategory, setLastOrder
        } = React.useContext(window.AppContext);

        const [loading, setLoading]           = React.useState(false);
        const [upiModal, setUpiModal]         = React.useState(null);  // { orderId, paymentUrl, orderData }
        const [receiptData, setReceiptData]   = React.useState(null);

        const categories = ['All', ...new Set(products.map(p => p.category_rel?.name || 'Uncategorized'))];

        const filteredProducts = products.filter(p => {
            const matchesSearch = p.name.toLowerCase().includes((posSearchSearch || '').toLowerCase()) ||
                                  (p.sku && p.sku.toLowerCase().includes((posSearchSearch || '').toLowerCase()));
            const matchesCategory = posCategory === 'All' || (p.category_rel?.name || 'Uncategorized') === posCategory;
            return matchesSearch && matchesCategory;
        });

        const addToCart = (product) => {
            if (product.stock <= 0) { showToast('This product is out of stock', 'error'); return; }
            setPosCart(prev => {
                const existing = prev.find(item => item.product_id === product.id);
                if (existing) {
                    return prev.map(item => item.product_id === product.id ? { ...item, quantity: item.quantity + 1 } : item);
                }
                return [...prev, { product_id: product.id, name: product.name, price: product.price, quantity: 1, image_url: product.image_url }];
            });
        };

        const updateQuantity = (productId, delta) => {
            setPosCart(prev =>
                prev.map(item => item.product_id === productId
                    ? { ...item, quantity: Math.max(0, item.quantity + delta) }
                    : item
                ).filter(item => item.quantity > 0)
            );
        };

        const cartSubtotal = posCart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const taxTotal     = cartSubtotal * 0.18;
        const grandTotal   = cartSubtotal + taxTotal;

        const clearSale = () => {
            setPosCart([]);
            setPosSelectedCustomer(null);
            setPosSearch('');
            fetchData();
        };

        const handleCheckout = async () => {
            if (posCart.length === 0) { showToast('Cart is empty', 'error'); return; }
            setLoading(true);
            try {
                const payload = {
                    customer_id: posSelectedCustomer?.id || null,
                    payment_method: posPaymentMethod,
                    items: posCart.map(item => ({
                        product_id: item.product_id,
                        quantity: item.quantity,
                        unit_price: item.price
                    })),
                    total_amount: grandTotal
                };

                const res = await API.post('/orders/pos', payload);
                const data = res.data;
                setLastOrder(data);

                if (posPaymentMethod === 'upi' && data.payment_url) {
                    setUpiModal({ orderId: data.order_id, paymentUrl: data.payment_url, orderData: data });
                } else {
                    setReceiptData(data);
                    showToast('Sale recorded successfully');
                    clearSale();
                }
            } catch (err) {
                showToast('Checkout failed. Please try again.', 'error');
            } finally {
                setLoading(false);
            }
        };

        const handleUpiPaid = () => {
            const data = upiModal.orderData;
            setUpiModal(null);
            setReceiptData(data);
            showToast('Payment confirmed!');
            clearSale();
        };

        return (
            <div className="pos-container animate-fade" style={{ display: 'flex', gap: '1.5rem', height: 'calc(100vh - 140px)' }}>

                {/* UPI Payment Modal */}
                {upiModal && (
                    <UPIPaymentModal
                        orderId={upiModal.orderId}
                        paymentUrl={upiModal.paymentUrl}
                        orderData={upiModal.orderData}
                        API={API}
                        onPaid={handleUpiPaid}
                        onCancel={() => setUpiModal(null)}
                    />
                )}

                {/* Receipt Modal */}
                {receiptData && (
                    <ReceiptModal
                        orderData={receiptData}
                        onClose={() => setReceiptData(null)}
                    />
                )}

                {/* LEFT PANEL: PRODUCT CATALOG */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                    <div style={{ padding: '0.875rem 1rem 0', borderBottom: '1px solid var(--border)' }}>
                        {/* Search bar */}
                        <div style={{ position: 'relative', marginBottom: '0.75rem' }}>
                            <Icon name="search" size={16} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }} />
                            <input
                                type="text"
                                placeholder="Search by name or SKU…"
                                value={posSearchSearch || ''}
                                onChange={e => setPosSearch(e.target.value)}
                                style={{
                                    width: '100%',
                                    paddingLeft: '40px',
                                    paddingRight: posSearchSearch ? '36px' : '14px',
                                    borderRadius: '999px',
                                    border: '1.5px solid var(--border)',
                                    background: 'var(--bg-main)',
                                    fontSize: '0.875rem',
                                    height: '38px',
                                    transition: 'border-color 0.15s, box-shadow 0.15s',
                                    outline: 'none',
                                }}
                                onFocus={e => { e.target.style.borderColor = 'var(--primary)'; e.target.style.boxShadow = '0 0 0 3px rgba(13,148,136,0.12)'; }}
                                onBlur={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none'; }}
                            />
                            {posSearchSearch && (
                                <button
                                    onClick={() => setPosSearch('')}
                                    style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'transparent', cursor: 'pointer', padding: '2px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}
                                >
                                    <Icon name="x-circle" size={15} />
                                </button>
                            )}
                        </div>

                        {/* Category chips */}
                        <div className="custom-scrollbar" style={{ display: 'flex', gap: '0.4rem', overflowX: 'auto', paddingBottom: '0.75rem', scrollbarWidth: 'none' }}>
                            {categories.map(c => (
                                <button
                                    key={c}
                                    onClick={() => setPosCategory(c)}
                                    style={{
                                        flexShrink: 0,
                                        padding: '0.28rem 0.85rem',
                                        borderRadius: '999px',
                                        border: `1.5px solid ${posCategory === c ? 'var(--primary)' : 'var(--border)'}`,
                                        background: posCategory === c ? 'var(--primary)' : 'transparent',
                                        color: posCategory === c ? 'white' : 'var(--text-secondary)',
                                        fontWeight: posCategory === c ? 700 : 500,
                                        fontSize: '0.78rem',
                                        cursor: 'pointer',
                                        transition: 'all 0.15s',
                                        whiteSpace: 'nowrap',
                                    }}
                                >
                                    {c}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="custom-scrollbar" style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '0.875rem' }}>
                            {filteredProducts.map((p, idx) => (
                                <div
                                    key={p.id}
                                    className={`pos-product-card animate-pop delay-${(idx % 3) + 1}`}
                                    onClick={() => addToCart(p)}
                                    style={{
                                        cursor: p.stock > 0 ? 'pointer' : 'not-allowed',
                                        background: 'var(--surface)',
                                        border: '1.5px solid var(--border)',
                                        borderRadius: '14px',
                                        overflow: 'hidden',
                                        transition: 'box-shadow 0.18s, border-color 0.18s, transform 0.15s',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                                    }}
                                    onMouseEnter={e => { if (p.stock > 0) { e.currentTarget.style.boxShadow = '0 4px 16px rgba(13,148,136,0.18)'; e.currentTarget.style.borderColor = 'var(--primary)'; e.currentTarget.style.transform = 'translateY(-2px)'; } }}
                                    onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.06)'; e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = 'none'; }}
                                >
                                    {/* Image */}
                                    <div style={{ position: 'relative', paddingTop: '72%', background: 'var(--bg-main)', overflow: 'hidden' }}>
                                        {p.image_url
                                            ? <img src={p.image_url} alt={p.name} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
                                            : <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <Icon name="package" size={36} style={{ color: 'var(--text-muted)', opacity: 0.25 }} />
                                              </div>
                                        }
                                        {/* Out-of-stock overlay */}
                                        {p.stock <= 0 && (
                                            <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <span style={{ color: 'white', fontWeight: 700, fontSize: '0.72rem', letterSpacing: '0.08em', textTransform: 'uppercase', background: 'rgba(0,0,0,0.4)', padding: '3px 10px', borderRadius: '20px' }}>Out of Stock</span>
                                            </div>
                                        )}
                                        {/* Low-stock badge */}
                                        {p.stock > 0 && p.stock <= 5 && (
                                            <div style={{ position: 'absolute', top: '7px', right: '7px', background: 'var(--warning)', color: 'white', fontSize: '0.62rem', fontWeight: 700, padding: '2px 7px', borderRadius: '20px', letterSpacing: '0.04em' }}>
                                                {p.stock} left
                                            </div>
                                        )}
                                    </div>

                                    {/* Info */}
                                    <div style={{ padding: '0.65rem 0.75rem 0.75rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                                        {p.brand_rel?.name && (
                                            <div style={{ fontSize: '0.6rem', color: 'var(--primary)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', opacity: 0.85 }}>{p.brand_rel.name}</div>
                                        )}
                                        <div style={{ fontSize: '0.82rem', fontWeight: 600, lineHeight: 1.35, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', color: 'var(--text-primary)' }}>{p.name}</div>
                                        {p.sku && <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{p.sku}</div>}
                                        <div style={{ marginTop: 'auto', paddingTop: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div style={{ fontWeight: 800, color: 'var(--primary)', fontSize: '0.95rem' }}>₹{p.price?.toLocaleString()}</div>
                                            <div style={{
                                                width: '26px', height: '26px', borderRadius: '50%',
                                                background: p.stock > 0 ? 'var(--primary)' : 'var(--border)',
                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                flexShrink: 0, transition: 'background 0.15s'
                                            }}>
                                                <Icon name="plus" size={13} style={{ color: p.stock > 0 ? 'white' : 'var(--text-muted)' }} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        {filteredProducts.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                                <Icon name="search-x" size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
                                <div>No products found</div>
                            </div>
                        )}
                    </div>
                </div>

                {/* RIGHT PANEL: CART & CHECKOUT */}
                <div style={{ width: '380px', display: 'flex', flexDirection: 'column', background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                    <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)', background: 'var(--bg-glass)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3 className="outfit" style={{ margin: 0 }}>Current Order</h3>
                            <button className="btn-icon" onClick={() => setPosCart([])} title="Clear cart">
                                <Icon name="trash-2" size={16} />
                            </button>
                        </div>
                        <select
                            value={posSelectedCustomer?.id || ''}
                            onChange={e => {
                                const cid = e.target.value;
                                setPosSelectedCustomer(cid ? customers.find(c => c.id == cid) : null);
                            }}
                            style={{ width: '100%' }}
                        >
                            <option value="">Walk-in Customer</option>
                            {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.mobile})</option>)}
                        </select>
                    </div>

                    <div className="custom-scrollbar" style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
                        {posCart.length === 0 ? (
                            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                                <Icon name="shopping-cart" size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                                <div>Cart is empty</div>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                {posCart.map(item => (
                                    <div key={item.product_id} style={{ display: 'flex', gap: '1rem', paddingBottom: '1rem', borderBottom: '1px dashed var(--border)' }}>
                                        <div style={{ width: '50px', height: '50px', background: '#f1f5f9', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', flexShrink: 0 }}>
                                            {item.image_url
                                                ? <img src={item.image_url} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                                : <Icon name="package" size={24} style={{ color: 'var(--text-muted)', opacity: 0.5 }} />
                                            }
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>{item.name}</div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <div style={{ fontWeight: 700, color: 'var(--primary)', fontSize: '0.875rem' }}>₹{(item.price * item.quantity).toLocaleString()}</div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-primary)', borderRadius: '4px', padding: '2px' }}>
                                                    <button style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: '2px 6px' }} onClick={() => updateQuantity(item.product_id, -1)}><Icon name="minus" size={14} /></button>
                                                    <span style={{ fontSize: '0.875rem', fontWeight: 600, minWidth: '20px', textAlign: 'center' }}>{item.quantity}</span>
                                                    <button style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: '2px 6px' }} onClick={() => updateQuantity(item.product_id, 1)}><Icon name="plus" size={14} /></button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', background: 'var(--bg-primary)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            <span>Subtotal</span><span>₹{cartSubtotal.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            <span>GST (18%)</span><span>₹{taxTotal.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.25rem', fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                            <span>Total</span><span>₹{grandTotal.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                        </div>

                        {/* Payment method selector */}
                        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                            {[
                                { method: 'upi',  icon: 'smartphone', label: 'UPI' },
                                { method: 'cash', icon: 'banknote',   label: 'Cash' },
                                { method: 'card', icon: 'credit-card', label: 'Card' },
                            ].map(({ method, icon, label }) => (
                                <button
                                    key={method}
                                    onClick={() => setPosPaymentMethod(method)}
                                    style={{
                                        flex: 1, padding: '0.6rem 0.25rem', border: `2px solid ${posPaymentMethod === method ? 'var(--primary)' : 'var(--border)'}`,
                                        borderRadius: '8px', background: posPaymentMethod === method ? 'var(--primary-light)' : 'transparent',
                                        color: posPaymentMethod === method ? 'var(--primary)' : 'var(--text-secondary)',
                                        fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem', transition: 'all 0.15s'
                                    }}
                                >
                                    <Icon name={icon} size={15} /> {label}
                                </button>
                            ))}
                        </div>

                        <button
                            className="btn-primary"
                            style={{ width: '100%', padding: '1rem', fontSize: '1rem', justifyContent: 'center' }}
                            onClick={handleCheckout}
                            disabled={posCart.length === 0 || loading}
                        >
                            {loading
                                ? <><Icon name="loader" size={18} /><span>Processing…</span></>
                                : posPaymentMethod === 'upi'
                                    ? <><Icon name="smartphone" size={18} /><span>Request UPI Payment</span></>
                                    : <><Icon name="check-circle" size={18} /><span>Complete Sale</span></>
                            }
                        </button>
                    </div>
                </div>
            </div>
        );
    };
})();
