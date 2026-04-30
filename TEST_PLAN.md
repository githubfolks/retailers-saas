# Automated Testing Plan — Odoo SaaS

## Current State
- `pytest` and `pytest-asyncio` are installed; zero tests exist
- No `conftest.py`, no `tests/` directory, no database fixtures
- External dependencies: PostgreSQL, Redis, Odoo, Razorpay, OpenAI, SMTP, WhatsApp, n8n

---

## Layer 1 — Infrastructure (Do This First)

### Test directory structure
```
tests/
├── conftest.py               # shared fixtures
├── factories.py              # data factories (tenant, order, product, etc.)
├── mocks/
│   ├── mock_email.py         # patch send_email → returns True
│   ├── mock_whatsapp.py      # patch send_whatsapp_message → returns {}
│   ├── mock_razorpay.py      # patch create_payment_link → returns fake URL
│   ├── mock_openai.py        # patch OpenAI client → returns fixture response
│   └── mock_odoo.py          # patch OdooClient → returns fixture product list
├── unit/
│   ├── services/
│   │   ├── test_auth_service.py
│   │   ├── test_return_service.py
│   │   ├── test_order_service.py
│   │   ├── test_inventory_service.py
│   │   ├── test_procurement_service.py
│   │   ├── test_analytics_service.py
│   │   └── test_coupon_service.py
│   └── tasks/
│       ├── test_inventory_tasks.py
│       └── test_sync_tasks.py
├── integration/
│   └── api/
│       ├── test_auth_api.py
│       ├── test_orders_api.py
│       ├── test_products_api.py
│       ├── test_inventory_api.py
│       ├── test_procurement_api.py
│       ├── test_returns_api.py
│       ├── test_admin_api.py
│       ├── test_customers_api.py
│       ├── test_coupons_api.py
│       ├── test_catalog_api.py
│       ├── test_sku_api.py
│       ├── test_shifts_api.py
│       ├── test_analytics_api.py
│       ├── test_payment_webhook.py
│       ├── test_odoo_webhooks.py
│       └── test_whatsapp_webhook.py
└── e2e/
    ├── test_order_to_return_lifecycle.py
    ├── test_low_stock_to_supplier_email.py
    └── test_pos_shift_lifecycle.py
```

### `tests/conftest.py` — Core fixtures to build
```python
@pytest.fixture(scope="session")
def engine():
    # Create a separate test PostgreSQL database
    # Run Base.metadata.create_all()

@pytest.fixture
def db(engine):
    # Wrap each test in a transaction, ROLLBACK after
    # Provides isolation without dropping/recreating tables

@pytest.fixture
def client(db):
    # FastAPI TestClient with db dependency override

@pytest.fixture
def tenant(db):
    # Factory: creates a test Tenant row, returns it

@pytest.fixture
def auth_headers(tenant):
    # Returns {"Authorization": "Bearer <jwt>"} scoped to test tenant
```

**Note:** Use a real PostgreSQL test database (not SQLite — dialect differences cause false passes). Override `get_db` via FastAPI's `app.dependency_overrides`.

### `pytest.ini`
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
env =
    DATABASE_URL=postgresql://test:test@localhost:5432/test_db
    SMTP_USER=test@example.com
    REDIS_URL=redis://localhost:6379/1
```

### GitHub Actions (`.github/workflows/test.yml`)
```yaml
services:
  postgres:
    image: postgres:15
    env: { POSTGRES_DB: test_db, POSTGRES_USER: test, POSTGRES_PASSWORD: test }
  redis:
    image: redis:7

steps:
  - run: pip install -r requirements-base.txt pytest-cov httpx
  - run: pytest tests/ --cov=app --cov-report=xml -v
```

---

## Layer 2 — Unit Tests (Services)

### Auth (`test_auth_service.py`)
| Test | What to verify |
|------|----------------|
| `test_login_valid_credentials` | Returns JWT token |
| `test_login_wrong_password` | Raises 401 |
| `test_pos_login_valid_pin` | POS PIN login works |
| `test_signup_duplicate_tenant` | Raises on existing tenant_id |
| `test_token_refresh` | New access token issued |
| `test_expired_token_rejected` | Middleware blocks expired JWT |

### Orders (`test_order_service.py`)
| Test | What to verify |
|------|----------------|
| `test_create_order_deducts_stock` | StockLocation.quantity decreases |
| `test_create_order_insufficient_stock` | ValueError when qty > available |
| `test_confirm_order_transitions_status` | draft → pending |
| `test_generate_payment_link` | Calls Razorpay mock, returns URL |
| `test_pos_checkout_applies_coupon` | Discount applied correctly |
| `test_pos_checkout_expired_coupon_rejected` | Raises on expired coupon |
| `test_fulfill_order_creates_fulfillment_record` | Fulfillment row created |

### Inventory (`test_inventory_service.py`)
| Test | What to verify |
|------|----------------|
| `test_reserve_stock_decrements_available` | Available stock drops |
| `test_reserve_beyond_available_raises` | Cannot over-reserve |
| `test_release_stock_restores` | Release brings stock back |
| `test_adjust_stock_negative` | Damage adjustment reduces qty |
| `test_internal_transfer_moves_stock` | Source down, destination up |
| `test_warehouse_transfer_creates_record` | Transfer row created |
| `test_acknowledge_alert_closes_it` | Alert status → acknowledged |

### Procurement (`test_procurement_service.py`)
| Test | What to verify |
|------|----------------|
| `test_create_purchase_order` | PO row created with correct total |
| `test_receive_po_restocks_inventory` | Stock location quantity increases |
| `test_receive_po_wrong_status_raises` | Cannot receive a draft PO |
| `test_inventory_count_complete_adjusts_stock` | Count discrepancy creates adjustment |
| `test_backorder_notify_sends_whatsapp` | WhatsApp mock called with correct message |
| `test_supplier_performance_metrics` | Returns on-time delivery %, avg lead time |

### Coupons (`test_coupon_service.py`)
| Test | What to verify |
|------|----------------|
| `test_validate_active_coupon` | Returns discount amount |
| `test_validate_expired_coupon` | Returns invalid |
| `test_validate_min_order_not_met` | Fails when order amount < minimum |
| `test_deactivate_coupon` | is_active = False |

### Analytics (`test_analytics_service.py`)
| Test | What to verify |
|------|----------------|
| `test_inventory_valuation_calculation` | qty × cost_price summed correctly |
| `test_dead_stock_30_days` | Products with no movement in 30 days |
| `test_abc_analysis_classification` | Top 80% revenue → A, next 15% → B, rest → C |
| `test_sku_pl_calculation` | Revenue − COGS = gross profit |
| `test_sales_trend_returns_daily_buckets` | One row per day |

### Return Service (`test_return_service.py`)
| Test | What to verify |
|------|----------------|
| `test_process_return_creates_record` | OrderReturn row created, status=`return_requested` |
| `test_process_return_exceeds_quantity_raises` | ValueError when qty > order.quantity |
| `test_process_return_order_not_found_raises` | ValueError on wrong tenant/order |
| `test_approve_return_sets_status` | status→`approved`, `approved_by` and `approved_at` set |
| `test_approve_wrong_status_raises` | Cannot approve when not in `return_requested` |
| `test_reject_return` | status→`rejected` |
| `test_schedule_pickup_creates_record` | ReturnPickup created, return→`pickup_scheduled` |
| `test_schedule_pickup_no_address_raises` | ValueError when no address available |
| `test_schedule_pickup_already_scheduled_raises` | Prevents duplicate pickup |
| `test_update_pickup_picked_up` | picked_up_at set, return→`picked_up` |
| `test_update_pickup_failed` | failure_reason stored |
| `test_update_pickup_attempted_increments_count` | attempt_count += 1 |
| `test_create_shipment_requires_pickup` | Cannot create before `picked_up` |
| `test_update_shipment_received` | received_at set, return→`received` |
| `test_record_inspection_restocks_resellable` | StockLocation.quantity increases, StockMovement created |
| `test_record_inspection_no_restock_damaged` | Damaged item does not restock |
| `test_process_refund_calculates_deduction` | Refund amount = price × (1 - deduction_pct/100) |
| `test_process_refund_marks_order_returned` | Order→`returned` (full qty) or `partially_returned` |
| `test_process_refund_requires_inspection_approval` | Raises if `approved_for_refund=False` |

### Inventory Tasks (`test_inventory_tasks.py`)
Mock `send_email`, `send_whatsapp_message`, `get_all_products`. Test logic only.

| Test | What to verify |
|------|----------------|
| `test_check_low_stock_creates_alerts` | Alert created when qty ≤ reorder_point |
| `test_check_low_stock_no_duplicate_alerts` | Existing active alert prevents second one |
| `test_notify_suppliers_skips_if_disabled` | `is_enabled=False` → no notifications queued |
| `test_notify_suppliers_respects_cooldown` | Recent sent email → skip |
| `test_notify_suppliers_skips_no_supplier` | Product with no PO supplier → skipped |
| `test_notify_suppliers_queues_email` | Creates `InventoryNotification(channel="email", status="pending")` |
| `test_send_pending_routes_email_channel` | `send_email` called for email-channel notifications |
| `test_send_pending_routes_whatsapp_channel` | `send_whatsapp_message` called for whatsapp |
| `test_send_pending_marks_sent` | status→`sent`, `sent_at` set on success |
| `test_send_pending_increments_retries` | retries += 1 on failure, status→`failed` at retries > 3 |

### Sync Tasks (`test_sync_tasks.py`)
| Test | What to verify |
|------|----------------|
| `test_sync_products_creates_new` | New Odoo product → Product row inserted |
| `test_sync_products_updates_existing` | Changed price on Odoo → Product.price updated |
| `test_sync_orders_creates_order` | Odoo order → Order row created |
| `test_sync_fails_gracefully` | Odoo mock raises → task retries, no crash |

---

## Layer 3 — Integration Tests (HTTP + DB)

Use FastAPI `TestClient` with `dependency_overrides` for `get_db`. Mock all external calls.

### `test_auth_api.py`
| Test | What to verify |
|------|----------------|
| `test_login_returns_token` | POST /auth/login → 200 with access_token |
| `test_login_bad_password` | POST /auth/login → 401 |
| `test_signup_creates_tenant` | POST /auth/signup → 200, tenant row exists |
| `test_signup_duplicate_rejected` | POST /auth/signup → 400 |
| `test_refresh_returns_new_token` | POST /auth/refresh → 200 |
| `test_protected_endpoint_no_token` | Any protected endpoint → 401 |
| `test_protected_endpoint_wrong_tenant` | Cross-tenant access → 403 |

### `test_orders_api.py`
| Test | What to verify |
|------|----------------|
| `test_create_order` | POST /orders/ → 200, stock decremented |
| `test_list_orders_tenant_isolation` | GET /orders/ → only own tenant's orders |
| `test_update_order_status` | PATCH /{id}/status → status changed |
| `test_generate_payment_link` | POST /{id}/generate-payment → Razorpay mock called |
| `test_pos_checkout_with_coupon` | POST /orders/pos → discount applied |
| `test_get_invoice` | GET /{id}/invoice → correct GST fields |

### `test_inventory_api.py`
| Test | What to verify |
|------|----------------|
| `test_get_stock_level` | GET /inventory/stock/{id} → correct qty |
| `test_reserve_stock` | POST /inventory/stock/reserve → qty reserved |
| `test_adjust_stock` | POST /inventory/stock/adjust → qty changed |
| `test_list_alerts_tenant_isolation` | GET /inventory/alerts → only own alerts |
| `test_acknowledge_alert` | POST /inventory/alerts/{id}/acknowledge → status changes |
| `test_get_movements` | GET /inventory/movements/{id} → movement history |

### `test_products_api.py`
| Test | What to verify |
|------|----------------|
| `test_create_product` | POST /products/ → product row created |
| `test_list_products_with_season_filter` | GET /products/?season_id=X → filtered |
| `test_update_product` | PUT /{id} → fields updated |
| `test_delete_product` | DELETE /{id} → 200, row removed |
| `test_download_template` | GET /products/template → file response |

### `test_procurement_api.py`
| Test | What to verify |
|------|----------------|
| `test_create_supplier` | POST /procurement/suppliers → supplier row created |
| `test_create_purchase_order` | POST /procurement/purchase-orders → PO created |
| `test_receive_purchase_order` | POST /procurement/purchase-orders/{id}/receive → stock updated |
| `test_supplier_performance` | GET /procurement/suppliers/{id}/performance → metrics shape |

### `test_returns_api.py`
| Test | What to verify |
|------|----------------|
| `test_create_return` | POST /returns/ → return_requested |
| `test_approve_return` | PATCH /returns/{id}/approve → approved |
| `test_schedule_pickup` | POST /returns/{id}/pickup → pickup_scheduled |
| `test_update_pickup_status` | PATCH /returns/{id}/pickup → picked_up |
| `test_create_shipment` | POST /returns/{id}/shipment → in_transit |
| `test_update_shipment_received` | PATCH /returns/{id}/shipment → received |
| `test_record_inspection` | POST /returns/{id}/inspection → inspected |
| `test_process_refund` | POST /returns/refund → completed, refund row created |
| `test_get_return_detail` | GET /returns/{id} → nested pickup/shipment/inspection/refund |

### `test_admin_api.py`
| Test | What to verify |
|------|----------------|
| `test_list_tenants_requires_token` | GET /api/admin/tenants → 401 without token |
| `test_create_tenant` | POST /api/admin/tenants → tenant created |
| `test_supplier_settings_defaults` | GET supplier-email-settings → defaults when not configured |
| `test_supplier_settings_update` | PUT supplier-email-settings → settings persisted |
| `test_cancel_pending_notification` | DELETE notification → status=failed |
| `test_cancel_sent_notification_rejected` | DELETE sent notification → 400 |

### `test_customers_api.py`
| Test | What to verify |
|------|----------------|
| `test_create_customer` | POST /customers/ → customer created |
| `test_list_customers` | GET /customers/ → list with search |
| `test_update_customer` | PUT /{id} → fields updated |
| `test_get_customer_with_order_history` | GET /{id} → includes orders |
| `test_delete_customer` | DELETE /{id} → removed |

### `test_coupons_api.py`
| Test | What to verify |
|------|----------------|
| `test_create_coupon` | POST /coupons/ → created |
| `test_list_coupons` | GET /coupons/ → list, active filter works |
| `test_validate_valid_coupon` | GET /coupons/validate/{code} → discount amount |
| `test_validate_expired_coupon` | GET /coupons/validate/{code} → invalid |
| `test_deactivate_coupon` | DELETE /{id} → is_active=False |

### `test_catalog_api.py` (brands, categories, attributes, units, seasons)
| Test | What to verify |
|------|----------------|
| CRUD for brands | create, list, update, delete |
| CRUD for categories | create, list, update, delete |
| CRUD for units | create, list, update, delete |
| `test_create_season` | POST /seasons/ → season created |
| `test_apply_season_discount` | POST /seasons/{id}/apply-discount → prices updated |
| `test_close_season` | POST /seasons/{id}/close → status changes |

### `test_sku_api.py`
| Test | What to verify |
|------|----------------|
| `test_lookup_by_sku` | GET /sku/lookup/{sku} → product returned |
| `test_lookup_by_barcode` | GET /sku/lookup/barcode/{code} → product returned |
| `test_search` | GET /sku/search?q=name → matches returned |
| `test_low_stock_list` | GET /sku/low-stock/list → only below-reorder products |

### `test_shifts_api.py`
| Test | What to verify |
|------|----------------|
| `test_open_shift` | POST /shifts/open → shift created |
| `test_get_current_shift` | GET /shifts/current → active shift |
| `test_close_shift` | POST /shifts/close → reconciliation recorded |
| `test_sales_report` | GET /shifts/sales-report → per-staff breakdown |

### `test_analytics_api.py`
| Test | What to verify |
|------|----------------|
| `test_inventory_valuation` | GET /analytics/valuation → correct totals |
| `test_dead_stock_report` | GET /analytics/dead-stock → products with no movement |
| `test_abc_analysis` | GET /analytics/abc-analysis → A/B/C classifications |
| `test_export_valuation` | GET /analytics/export/valuation → file content-type header |

### `test_payment_webhook.py`
| Test | What to verify |
|------|----------------|
| `test_valid_signature_processes_payment` | Order status → paid, n8n mock called |
| `test_invalid_signature_rejected` | 400 returned, order not updated |
| `test_duplicate_webhook_idempotent` | Second call with same payment_id ignored |

### `test_odoo_webhooks.py`
| Test | What to verify |
|------|----------------|
| `test_stock_update_syncs_quantity` | StockLocation.quantity updated |
| `test_order_confirmation_reserves_stock` | Stock reserved on confirm |
| `test_po_received_restocks` | Receiving PO increases stock |
| `test_invalid_payload_400` | Missing fields → 400 |

### `test_whatsapp_webhook.py`
| Test | What to verify |
|------|----------------|
| `test_verify_token_challenge` | GET /whatsapp/webhook → returns hub.challenge |
| `test_incoming_message_calls_bot` | POST /whatsapp/webhook → WhatsAppBotService called |
| `test_unknown_tenant_returns_200` | POST with unknown number → 200 no-op (Meta requires 200) |

---

## Layer 4 — AI / Forecasting Tests (Mocked)

Mock OpenAI entirely. Test logic, not the model output.

| Test | What to verify |
|------|----------------|
| `test_demand_forecast_returns_prediction` | OpenAI mock → DemandForecast row created |
| `test_reorder_suggestion_above_zero` | Suggestion created only when qty > 0 |
| `test_recommendations_bought_together` | Returns products co-purchased with given SKU |
| `test_personal_recommendations` | Returns history-based recommendations for mobile |
| `test_ai_query_returns_response` | LLM mock called with inventory context |

---

## Layer 5 — End-to-End Scenarios

### `test_order_to_return_lifecycle.py`
Full flow: Order created → paid → fulfilled → return requested → approved → pickup → shipment received → inspected → refunded → stock restocked

### `test_low_stock_to_supplier_email.py`
Stock adjusted below reorder point → `check_low_stock_alerts` task → alert created → `notify_suppliers_low_stock` task → notification queued → `send_pending_notifications` task → `send_email` mock called

### `test_pos_shift_lifecycle.py`
Shift opened → POS sale with coupon applied → shift closed → sales report totals match

---

## Coverage Targets

| Module | Target |
|--------|--------|
| `app/services/return_service.py` | 90% |
| `app/tasks/inventory_tasks.py` | 80% |
| `app/api/returns.py` | 85% |
| `app/api/admin.py` | 80% |
| `app/services/` (all) | 75% |
| `app/api/` (all) | 75% |
| Overall | 70% |

---

## Coverage Map

| Module | Unit | Integration | E2E |
|--------|------|------------|-----|
| Auth | ✓ | ✓ | — |
| Orders | ✓ | ✓ | ✓ |
| Products / Catalog | — | ✓ | — |
| Inventory | ✓ | ✓ | ✓ |
| Procurement | ✓ | ✓ | — |
| Returns | ✓ | ✓ | ✓ |
| Analytics | ✓ | ✓ | — |
| Coupons | ✓ | ✓ | — |
| SKU lookup | — | ✓ | — |
| Shifts / POS | — | ✓ | ✓ |
| Seasons | — | ✓ | — |
| Admin | — | ✓ | — |
| Celery tasks (inventory) | ✓ | — | ✓ |
| Celery tasks (sync) | ✓ | — | — |
| Payment webhooks | ✓ | ✓ | — |
| Odoo webhooks | ✓ | ✓ | — |
| WhatsApp webhook | — | ✓ | — |
| AI / Forecasting | ✓ | — | — |
| Email sender | ✓ | — | — |

**Estimated total: ~180–220 tests**

---

## Implementation Order

1. `tests/conftest.py` + rollback isolation fixture
2. `tests/factories.py` — Tenant, Order, Product, StockLocation, Supplier factories
3. `tests/mocks/` — email, WhatsApp, Razorpay, OpenAI, Odoo mocks
4. `tests/unit/services/test_return_service.py` — highest business value
5. `tests/unit/tasks/test_inventory_tasks.py`
6. `tests/unit/services/test_order_service.py`
7. `tests/unit/services/test_inventory_service.py`
8. `tests/integration/api/test_returns_api.py`
9. `tests/integration/api/test_orders_api.py`
10. `tests/integration/api/test_admin_api.py`
11. Remaining integration tests (procurement, analytics, catalog, webhooks)
12. E2E scenarios
13. CI pipeline (`.github/workflows/test.yml`)
