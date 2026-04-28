--
-- PostgreSQL database dump
--

\restrict IQ00ycDPvpXsNZn7H5pVTTFvnlNIS2OViYgKOflk55z1RnozDhMaEaIkGmmelbw

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: odoo_saas_retail_db; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA odoo_saas_retail_db;


ALTER SCHEMA odoo_saas_retail_db OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: attribute_values; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.attribute_values (
    id integer NOT NULL,
    attribute_id integer,
    value character varying(255),
    hex_color character varying(10)
);


ALTER TABLE odoo_saas_retail_db.attribute_values OWNER TO postgres;

--
-- Name: attribute_values_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.attribute_values_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.attribute_values_id_seq OWNER TO postgres;

--
-- Name: attribute_values_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.attribute_values_id_seq OWNED BY odoo_saas_retail_db.attribute_values.id;


--
-- Name: attributes; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.attributes (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying(100),
    display_type character varying(50)
);


ALTER TABLE odoo_saas_retail_db.attributes OWNER TO postgres;

--
-- Name: attributes_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.attributes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.attributes_id_seq OWNER TO postgres;

--
-- Name: attributes_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.attributes_id_seq OWNED BY odoo_saas_retail_db.attributes.id;


--
-- Name: automation_workflows; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.automation_workflows (
    id integer NOT NULL,
    tenant_id character varying,
    workflow_name character varying,
    workflow_description text,
    trigger_type character varying,
    trigger_condition text,
    steps text,
    notification_channels text,
    is_active boolean,
    execution_count integer,
    last_executed timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.automation_workflows OWNER TO postgres;

--
-- Name: automation_workflows_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.automation_workflows_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.automation_workflows_id_seq OWNER TO postgres;

--
-- Name: automation_workflows_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.automation_workflows_id_seq OWNED BY odoo_saas_retail_db.automation_workflows.id;


--
-- Name: backorder_alerts; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.backorder_alerts (
    id integer NOT NULL,
    tenant_id character varying,
    order_id integer,
    product_id integer,
    quantity_short integer,
    expected_restock_date timestamp without time zone,
    customer_notification_sent boolean,
    customer_notification_channel character varying,
    last_notification_at timestamp without time zone,
    backorder_status character varying,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.backorder_alerts OWNER TO postgres;

--
-- Name: backorder_alerts_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.backorder_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.backorder_alerts_id_seq OWNER TO postgres;

--
-- Name: backorder_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.backorder_alerts_id_seq OWNED BY odoo_saas_retail_db.backorder_alerts.id;


--
-- Name: brands; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.brands (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying(100),
    code character varying(10),
    description text,
    logo_url character varying(255)
);


ALTER TABLE odoo_saas_retail_db.brands OWNER TO postgres;

--
-- Name: brands_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.brands_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.brands_id_seq OWNER TO postgres;

--
-- Name: brands_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.brands_id_seq OWNED BY odoo_saas_retail_db.brands.id;


--
-- Name: categories; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.categories (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying,
    description text,
    parent_id integer,
    code character varying(10)
);


ALTER TABLE odoo_saas_retail_db.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.categories_id_seq OWNED BY odoo_saas_retail_db.categories.id;


--
-- Name: collections; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.collections (
    id integer NOT NULL,
    tenant_id character varying,
    season_id integer,
    name character varying(100)
);


ALTER TABLE odoo_saas_retail_db.collections OWNER TO postgres;

--
-- Name: collections_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.collections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.collections_id_seq OWNER TO postgres;

--
-- Name: collections_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.collections_id_seq OWNED BY odoo_saas_retail_db.collections.id;


--
-- Name: conversation_states; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.conversation_states (
    id integer NOT NULL,
    tenant_id character varying,
    mobile character varying,
    current_intent character varying,
    selected_product character varying,
    quantity integer,
    payment_status character varying,
    current_state character varying(50) DEFAULT 'IDLE'::character varying,
    selected_product_id integer,
    selected_sku character varying(255),
    context jsonb DEFAULT '{}'::jsonb,
    last_message_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE odoo_saas_retail_db.conversation_states OWNER TO postgres;

--
-- Name: conversation_states_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.conversation_states_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.conversation_states_id_seq OWNER TO postgres;

--
-- Name: conversation_states_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.conversation_states_id_seq OWNED BY odoo_saas_retail_db.conversation_states.id;


--
-- Name: count_lines; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.count_lines (
    id integer NOT NULL,
    count_id integer,
    product_id integer,
    barcode character varying,
    counted_qty integer,
    system_qty integer,
    variance integer,
    variance_reason character varying
);


ALTER TABLE odoo_saas_retail_db.count_lines OWNER TO postgres;

--
-- Name: count_lines_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.count_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.count_lines_id_seq OWNER TO postgres;

--
-- Name: count_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.count_lines_id_seq OWNED BY odoo_saas_retail_db.count_lines.id;


--
-- Name: coupons; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.coupons (
    id integer NOT NULL,
    tenant_id character varying,
    code character varying(50) NOT NULL,
    discount_type character varying(20),
    discount_value double precision,
    min_purchase_amount double precision,
    max_discount_amount double precision,
    is_active boolean,
    valid_from timestamp without time zone,
    valid_until timestamp without time zone,
    usage_limit integer,
    usage_count integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.coupons OWNER TO postgres;

--
-- Name: coupons_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.coupons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.coupons_id_seq OWNER TO postgres;

--
-- Name: coupons_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.coupons_id_seq OWNED BY odoo_saas_retail_db.coupons.id;


--
-- Name: customers; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.customers (
    id integer NOT NULL,
    tenant_id character varying,
    mobile character varying,
    name character varying,
    address character varying,
    email character varying,
    total_spend double precision,
    order_count integer,
    last_order_date timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.customers OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.customers_id_seq OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.customers_id_seq OWNED BY odoo_saas_retail_db.customers.id;


--
-- Name: demand_forecasts; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.demand_forecasts (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    forecast_date timestamp without time zone,
    forecast_period character varying,
    predicted_demand double precision,
    confidence_level double precision,
    model_type character varying,
    lower_bound double precision,
    upper_bound double precision,
    actual_demand double precision,
    accuracy_error double precision,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.demand_forecasts OWNER TO postgres;

--
-- Name: demand_forecasts_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.demand_forecasts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.demand_forecasts_id_seq OWNER TO postgres;

--
-- Name: demand_forecasts_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.demand_forecasts_id_seq OWNED BY odoo_saas_retail_db.demand_forecasts.id;


--
-- Name: fulfillments; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.fulfillments (
    id integer NOT NULL,
    tenant_id character varying,
    order_id integer,
    carrier_name character varying,
    tracking_number character varying,
    shipping_label_url character varying,
    status character varying,
    shipped_at timestamp without time zone,
    delivered_at timestamp without time zone,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.fulfillments OWNER TO postgres;

--
-- Name: fulfillments_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.fulfillments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.fulfillments_id_seq OWNER TO postgres;

--
-- Name: fulfillments_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.fulfillments_id_seq OWNED BY odoo_saas_retail_db.fulfillments.id;


--
-- Name: inventory_audit_logs; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.inventory_audit_logs (
    id integer NOT NULL,
    tenant_id character varying,
    entity_type character varying,
    entity_id integer,
    action character varying,
    old_values text,
    new_values text,
    changed_by character varying,
    change_reason character varying,
    ip_address character varying,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.inventory_audit_logs OWNER TO postgres;

--
-- Name: inventory_audit_logs_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.inventory_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.inventory_audit_logs_id_seq OWNER TO postgres;

--
-- Name: inventory_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.inventory_audit_logs_id_seq OWNED BY odoo_saas_retail_db.inventory_audit_logs.id;


--
-- Name: inventory_counts; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.inventory_counts (
    id integer NOT NULL,
    tenant_id character varying,
    count_date timestamp without time zone,
    count_by_user character varying,
    status character varying,
    warehouse_id integer,
    total_items_counted integer,
    total_discrepancies integer,
    variance_percentage double precision,
    notes text,
    completed_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.inventory_counts OWNER TO postgres;

--
-- Name: inventory_counts_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.inventory_counts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.inventory_counts_id_seq OWNER TO postgres;

--
-- Name: inventory_counts_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.inventory_counts_id_seq OWNED BY odoo_saas_retail_db.inventory_counts.id;


--
-- Name: inventory_notifications; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.inventory_notifications (
    id integer NOT NULL,
    tenant_id character varying,
    alert_id integer,
    recipient character varying,
    notification_type character varying,
    channel character varying,
    message text,
    status character varying,
    sent_at timestamp without time zone,
    read_at timestamp without time zone,
    retries integer,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.inventory_notifications OWNER TO postgres;

--
-- Name: inventory_notifications_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.inventory_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.inventory_notifications_id_seq OWNER TO postgres;

--
-- Name: inventory_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.inventory_notifications_id_seq OWNED BY odoo_saas_retail_db.inventory_notifications.id;


--
-- Name: inventory_rules; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.inventory_rules (
    id integer NOT NULL,
    tenant_id character varying,
    rule_name character varying,
    rule_description text,
    condition text,
    action text,
    rule_priority integer,
    is_enabled boolean,
    last_triggered timestamp without time zone,
    trigger_count integer,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.inventory_rules OWNER TO postgres;

--
-- Name: inventory_rules_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.inventory_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.inventory_rules_id_seq OWNER TO postgres;

--
-- Name: inventory_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.inventory_rules_id_seq OWNED BY odoo_saas_retail_db.inventory_rules.id;


--
-- Name: landed_cost_assignments; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.landed_cost_assignments (
    id integer NOT NULL,
    tenant_id character varying,
    landed_cost_id integer,
    valuation_layer_id integer,
    allocated_amount double precision,
    allocation_method character varying,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.landed_cost_assignments OWNER TO postgres;

--
-- Name: landed_cost_assignments_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.landed_cost_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.landed_cost_assignments_id_seq OWNER TO postgres;

--
-- Name: landed_cost_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.landed_cost_assignments_id_seq OWNED BY odoo_saas_retail_db.landed_cost_assignments.id;


--
-- Name: landed_costs; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.landed_costs (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying(255),
    cost_type character varying(50),
    amount double precision,
    status character varying,
    purchase_order_id integer,
    created_at timestamp without time zone,
    validated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.landed_costs OWNER TO postgres;

--
-- Name: landed_costs_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.landed_costs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.landed_costs_id_seq OWNER TO postgres;

--
-- Name: landed_costs_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.landed_costs_id_seq OWNED BY odoo_saas_retail_db.landed_costs.id;


--
-- Name: order_fulfillments; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.order_fulfillments (
    id integer NOT NULL,
    tenant_id character varying,
    order_id integer,
    fulfillment_status character varying,
    warehouse_id integer,
    picker_id character varying,
    packing_time timestamp without time zone,
    carrier character varying,
    tracking_number character varying,
    estimated_delivery timestamp without time zone,
    actual_delivery timestamp without time zone,
    proof_of_delivery character varying,
    delivery_signature character varying,
    delivery_notes text,
    batch_id integer,
    fulfillment_method character varying(50),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.order_fulfillments OWNER TO postgres;

--
-- Name: order_fulfillments_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.order_fulfillments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.order_fulfillments_id_seq OWNER TO postgres;

--
-- Name: order_fulfillments_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.order_fulfillments_id_seq OWNED BY odoo_saas_retail_db.order_fulfillments.id;


--
-- Name: order_returns; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.order_returns (
    id integer NOT NULL,
    tenant_id character varying,
    order_id integer,
    quantity integer,
    reason character varying(255),
    condition character varying(50),
    status character varying(50),
    return_date timestamp without time zone,
    processed_at timestamp without time zone,
    processed_by character varying,
    refund_id integer
);


ALTER TABLE odoo_saas_retail_db.order_returns OWNER TO postgres;

--
-- Name: order_returns_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.order_returns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.order_returns_id_seq OWNER TO postgres;

--
-- Name: order_returns_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.order_returns_id_seq OWNED BY odoo_saas_retail_db.order_returns.id;


--
-- Name: orders; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.orders (
    id integer NOT NULL,
    tenant_id character varying,
    customer_id integer,
    customer_mobile character varying,
    sku character varying,
    product_name character varying,
    quantity integer,
    unit_price double precision,
    total_amount double precision,
    status character varying,
    payment_status character varying,
    payment_id character varying,
    odoo_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    unit_cost_at_sale double precision,
    discount_amount double precision,
    coupon_code character varying(50),
    commitment_date timestamp without time zone,
    effective_delivery_date timestamp without time zone,
    invoice_number character varying(50),
    shipping_address text,
    customer_state character varying,
    tax_type character varying(10),
    tax_amount double precision,
    grand_total double precision,
    gst_rate double precision,
    cgst_amount double precision,
    sgst_amount double precision,
    igst_amount double precision,
    customer_gstin character varying(15),
    hsn_code character varying(10),
    notes text,
    payment_method character varying(20),
    source character varying(20) DEFAULT 'whatsapp'::character varying
);


ALTER TABLE odoo_saas_retail_db.orders OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.orders_id_seq OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.orders_id_seq OWNED BY odoo_saas_retail_db.orders.id;


--
-- Name: picking_batches; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.picking_batches (
    id integer NOT NULL,
    tenant_id character varying,
    batch_name character varying(100),
    status character varying(50),
    warehouse_id integer,
    picker_id character varying,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.picking_batches OWNER TO postgres;

--
-- Name: picking_batches_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.picking_batches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.picking_batches_id_seq OWNER TO postgres;

--
-- Name: picking_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.picking_batches_id_seq OWNED BY odoo_saas_retail_db.picking_batches.id;


--
-- Name: product_barcodes; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.product_barcodes (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    barcode character varying,
    barcode_type character varying,
    is_primary boolean,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.product_barcodes OWNER TO postgres;

--
-- Name: product_barcodes_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.product_barcodes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.product_barcodes_id_seq OWNER TO postgres;

--
-- Name: product_barcodes_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.product_barcodes_id_seq OWNED BY odoo_saas_retail_db.product_barcodes.id;


--
-- Name: product_images; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.product_images (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    url character varying(500),
    alt_text character varying(200),
    is_primary boolean,
    "position" integer
);


ALTER TABLE odoo_saas_retail_db.product_images OWNER TO postgres;

--
-- Name: product_images_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.product_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.product_images_id_seq OWNER TO postgres;

--
-- Name: product_images_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.product_images_id_seq OWNED BY odoo_saas_retail_db.product_images.id;


--
-- Name: product_skus; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.product_skus (
    id integer NOT NULL,
    tenant_id character varying,
    sku character varying(255),
    sku_type character varying(50),
    product_name character varying(255),
    description text,
    category character varying(100),
    sub_category character varying(100),
    product_id integer,
    category_id integer,
    brand_id integer,
    unit_id integer,
    cost_price double precision,
    selling_price double precision,
    minimum_selling_price double precision,
    reorder_point integer,
    reorder_quantity integer,
    max_stock_level integer,
    lead_time_days integer,
    odoo_product_id integer,
    shopify_product_id character varying(255),
    woocommerce_product_id integer,
    amazon_asin character varying(255),
    ebay_item_id character varying(255),
    external_sku character varying(255),
    is_active boolean,
    is_discontinued boolean,
    weight double precision,
    dimensions character varying(255),
    color character varying(100),
    size character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    updated_by character varying,
    sync_status character varying,
    hsn_code character varying(10),
    seasonal_price double precision,
    seasonal_discount_pct double precision DEFAULT 0.0,
    season_id integer,
    collection_id integer
);


ALTER TABLE odoo_saas_retail_db.product_skus OWNER TO postgres;

--
-- Name: product_skus_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.product_skus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.product_skus_id_seq OWNER TO postgres;

--
-- Name: product_skus_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.product_skus_id_seq OWNED BY odoo_saas_retail_db.product_skus.id;


--
-- Name: products; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.products (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying,
    description character varying,
    price double precision,
    sku character varying,
    quantity integer,
    odoo_id integer,
    category_id integer,
    brand_id integer,
    unit_id integer,
    season_id integer,
    collection_id integer
);


ALTER TABLE odoo_saas_retail_db.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.products_id_seq OWNED BY odoo_saas_retail_db.products.id;


--
-- Name: purchase_order_lines; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.purchase_order_lines (
    id integer NOT NULL,
    tenant_id character varying,
    po_id integer,
    product_id integer,
    product_name character varying,
    quantity integer,
    unit_cost double precision,
    total_cost double precision,
    received_quantity integer,
    received_date timestamp without time zone,
    quality_status character varying
);


ALTER TABLE odoo_saas_retail_db.purchase_order_lines OWNER TO postgres;

--
-- Name: purchase_order_lines_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.purchase_order_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.purchase_order_lines_id_seq OWNER TO postgres;

--
-- Name: purchase_order_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.purchase_order_lines_id_seq OWNED BY odoo_saas_retail_db.purchase_order_lines.id;


--
-- Name: purchase_orders; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.purchase_orders (
    id integer NOT NULL,
    tenant_id character varying,
    supplier_id integer,
    po_number character varying,
    po_date timestamp without time zone,
    expected_delivery timestamp without time zone,
    actual_delivery timestamp without time zone,
    po_status character varying,
    total_amount double precision,
    payment_status character varying,
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.purchase_orders OWNER TO postgres;

--
-- Name: purchase_orders_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.purchase_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.purchase_orders_id_seq OWNER TO postgres;

--
-- Name: purchase_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.purchase_orders_id_seq OWNED BY odoo_saas_retail_db.purchase_orders.id;


--
-- Name: refunds; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.refunds (
    id integer NOT NULL,
    tenant_id character varying,
    order_id integer,
    amount double precision,
    currency character varying(10),
    refund_method character varying(50),
    status character varying(50),
    transaction_id character varying(255),
    created_at timestamp without time zone,
    processed_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.refunds OWNER TO postgres;

--
-- Name: refunds_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.refunds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.refunds_id_seq OWNER TO postgres;

--
-- Name: refunds_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.refunds_id_seq OWNED BY odoo_saas_retail_db.refunds.id;


--
-- Name: reorder_suggestions; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.reorder_suggestions (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    suggested_quantity integer,
    reorder_point integer,
    lead_time_days integer,
    forecast_demand double precision,
    rationale text,
    ai_confidence double precision,
    status character varying,
    approved_by character varying,
    approved_at timestamp without time zone,
    created_at timestamp without time zone,
    expires_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.reorder_suggestions OWNER TO postgres;

--
-- Name: reorder_suggestions_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.reorder_suggestions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.reorder_suggestions_id_seq OWNER TO postgres;

--
-- Name: reorder_suggestions_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.reorder_suggestions_id_seq OWNED BY odoo_saas_retail_db.reorder_suggestions.id;


--
-- Name: seasons; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.seasons (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying(100),
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    status character varying(20) DEFAULT 'active'::character varying,
    discount_pct double precision DEFAULT 0.0
);


ALTER TABLE odoo_saas_retail_db.seasons OWNER TO postgres;

--
-- Name: seasons_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.seasons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.seasons_id_seq OWNER TO postgres;

--
-- Name: seasons_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.seasons_id_seq OWNED BY odoo_saas_retail_db.seasons.id;


--
-- Name: shifts; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.shifts (
    id integer NOT NULL,
    tenant_id character varying,
    user_id integer,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    opening_cash double precision DEFAULT 0.0,
    closing_cash double precision,
    total_sales double precision DEFAULT 0.0,
    total_returns double precision DEFAULT 0.0,
    total_tax double precision DEFAULT 0.0,
    expected_cash double precision DEFAULT 0.0,
    status character varying(20) DEFAULT 'open'::character varying,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE odoo_saas_retail_db.shifts OWNER TO postgres;

--
-- Name: shifts_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.shifts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.shifts_id_seq OWNER TO postgres;

--
-- Name: shifts_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.shifts_id_seq OWNED BY odoo_saas_retail_db.shifts.id;


--
-- Name: sku_alert_rules; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.sku_alert_rules (
    id integer NOT NULL,
    tenant_id character varying,
    sku character varying(255),
    alert_type character varying(50),
    trigger_threshold integer,
    alert_level character varying(20),
    notify_channels character varying(255),
    notify_recipients character varying(500),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.sku_alert_rules OWNER TO postgres;

--
-- Name: sku_alert_rules_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.sku_alert_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.sku_alert_rules_id_seq OWNER TO postgres;

--
-- Name: sku_alert_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.sku_alert_rules_id_seq OWNED BY odoo_saas_retail_db.sku_alert_rules.id;


--
-- Name: sku_attribute_values; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.sku_attribute_values (
    sku_id integer NOT NULL,
    value_id integer NOT NULL
);


ALTER TABLE odoo_saas_retail_db.sku_attribute_values OWNER TO postgres;

--
-- Name: sku_barcodes; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.sku_barcodes (
    id integer NOT NULL,
    tenant_id character varying,
    sku character varying(255),
    barcode character varying(255),
    barcode_type character varying(50),
    barcode_format character varying(50),
    is_primary boolean,
    is_active boolean,
    barcode_source character varying(50),
    supplier_reference character varying(255),
    created_at timestamp without time zone,
    scanned_count integer,
    last_scanned timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.sku_barcodes OWNER TO postgres;

--
-- Name: sku_barcodes_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.sku_barcodes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.sku_barcodes_id_seq OWNER TO postgres;

--
-- Name: sku_barcodes_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.sku_barcodes_id_seq OWNED BY odoo_saas_retail_db.sku_barcodes.id;


--
-- Name: sku_inventory_mappings; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.sku_inventory_mappings (
    id integer NOT NULL,
    tenant_id character varying,
    sku character varying(255),
    warehouse_id integer,
    zone_name character varying(50),
    bin_number character varying(50),
    quantity_on_hand integer,
    quantity_reserved integer,
    quantity_available integer,
    quantity_damaged integer,
    last_counted timestamp without time zone,
    last_movement timestamp without time zone,
    movement_count integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.sku_inventory_mappings OWNER TO postgres;

--
-- Name: sku_inventory_mappings_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.sku_inventory_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.sku_inventory_mappings_id_seq OWNER TO postgres;

--
-- Name: sku_inventory_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.sku_inventory_mappings_id_seq OWNED BY odoo_saas_retail_db.sku_inventory_mappings.id;


--
-- Name: sku_movement_logs; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.sku_movement_logs (
    id integer NOT NULL,
    tenant_id character varying,
    sku character varying(255),
    movement_type character varying(50),
    quantity integer,
    reference_type character varying(50),
    reference_id character varying(255),
    from_warehouse_id integer,
    from_zone character varying(50),
    from_bin character varying(50),
    to_warehouse_id integer,
    to_zone character varying(50),
    to_bin character varying(50),
    reason character varying(100),
    platform_source character varying(50),
    created_by character varying,
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.sku_movement_logs OWNER TO postgres;

--
-- Name: sku_movement_logs_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.sku_movement_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.sku_movement_logs_id_seq OWNER TO postgres;

--
-- Name: sku_movement_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.sku_movement_logs_id_seq OWNED BY odoo_saas_retail_db.sku_movement_logs.id;


--
-- Name: sku_platform_mappings; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.sku_platform_mappings (
    id integer NOT NULL,
    tenant_id character varying,
    sku character varying(255),
    platform_name character varying(50),
    platform_product_id character varying(255),
    platform_variant_id character varying(255),
    last_synced timestamp without time zone,
    sync_status character varying(50),
    sync_errors text,
    platform_stock_level integer,
    platform_reserved integer,
    platform_available integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.sku_platform_mappings OWNER TO postgres;

--
-- Name: sku_platform_mappings_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.sku_platform_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.sku_platform_mappings_id_seq OWNER TO postgres;

--
-- Name: sku_platform_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.sku_platform_mappings_id_seq OWNED BY odoo_saas_retail_db.sku_platform_mappings.id;


--
-- Name: stock_alerts; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.stock_alerts (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    alert_type character varying,
    alert_level character varying,
    threshold_value integer,
    current_value integer,
    status character varying,
    triggered_at timestamp without time zone,
    acknowledged_at timestamp without time zone,
    acknowledged_by character varying,
    resolved_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.stock_alerts OWNER TO postgres;

--
-- Name: stock_alerts_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.stock_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.stock_alerts_id_seq OWNER TO postgres;

--
-- Name: stock_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.stock_alerts_id_seq OWNED BY odoo_saas_retail_db.stock_alerts.id;


--
-- Name: stock_locations; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.stock_locations (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    parent_id integer,
    location_type character varying(50),
    name character varying(100),
    warehouse_id integer,
    zone_name character varying,
    bin_number character varying,
    is_scrap boolean,
    is_active boolean,
    quantity integer,
    reserved_quantity integer,
    available_quantity integer,
    reorder_point integer,
    reorder_quantity integer,
    last_counted timestamp without time zone,
    last_stock_check timestamp without time zone,
    updated_at timestamp without time zone,
    is_clearance boolean DEFAULT false
);


ALTER TABLE odoo_saas_retail_db.stock_locations OWNER TO postgres;

--
-- Name: stock_locations_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.stock_locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.stock_locations_id_seq OWNER TO postgres;

--
-- Name: stock_locations_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.stock_locations_id_seq OWNED BY odoo_saas_retail_db.stock_locations.id;


--
-- Name: stock_movements; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.stock_movements (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    location_id integer,
    movement_type character varying,
    quantity integer,
    reference_id character varying,
    reference_type character varying,
    reason character varying,
    created_by character varying,
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.stock_movements OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.stock_movements_id_seq OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.stock_movements_id_seq OWNED BY odoo_saas_retail_db.stock_movements.id;


--
-- Name: stock_transfers; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.stock_transfers (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    from_warehouse_id integer,
    to_warehouse_id integer,
    quantity integer,
    status character varying,
    transfer_date timestamp without time zone,
    received_date timestamp without time zone,
    received_by character varying,
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.stock_transfers OWNER TO postgres;

--
-- Name: stock_transfers_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.stock_transfers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.stock_transfers_id_seq OWNER TO postgres;

--
-- Name: stock_transfers_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.stock_transfers_id_seq OWNED BY odoo_saas_retail_db.stock_transfers.id;


--
-- Name: stock_valuation_layers; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.stock_valuation_layers (
    id integer NOT NULL,
    tenant_id character varying,
    product_id integer,
    sku character varying(255),
    original_quantity double precision,
    remaining_quantity double precision,
    unit_cost double precision,
    total_value double precision,
    reference_id character varying,
    reference_type character varying,
    landed_cost_value double precision,
    is_fully_consumed boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.stock_valuation_layers OWNER TO postgres;

--
-- Name: stock_valuation_layers_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.stock_valuation_layers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.stock_valuation_layers_id_seq OWNER TO postgres;

--
-- Name: stock_valuation_layers_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.stock_valuation_layers_id_seq OWNED BY odoo_saas_retail_db.stock_valuation_layers.id;


--
-- Name: supplier_performance; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.supplier_performance (
    id integer NOT NULL,
    supplier_id integer,
    tenant_id character varying,
    on_time_delivery_rate double precision,
    quality_score double precision,
    lead_time_average integer,
    defect_rate double precision,
    last_evaluated timestamp without time zone,
    evaluation_count integer,
    updated_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.supplier_performance OWNER TO postgres;

--
-- Name: supplier_performance_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.supplier_performance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.supplier_performance_id_seq OWNER TO postgres;

--
-- Name: supplier_performance_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.supplier_performance_id_seq OWNED BY odoo_saas_retail_db.supplier_performance.id;


--
-- Name: suppliers; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.suppliers (
    id integer NOT NULL,
    tenant_id character varying,
    supplier_name character varying,
    contact_person character varying,
    phone character varying,
    whatsapp_number character varying,
    email character varying,
    address character varying,
    lead_time_days integer,
    reliability_score double precision,
    payment_terms character varying,
    is_preferred boolean,
    is_active boolean,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.suppliers OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.suppliers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.suppliers_id_seq OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.suppliers_id_seq OWNED BY odoo_saas_retail_db.suppliers.id;


--
-- Name: tenants; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.tenants (
    id integer NOT NULL,
    tenant_id character varying,
    business_name character varying,
    whatsapp_number character varying,
    odoo_url character varying,
    odoo_db character varying,
    odoo_user character varying,
    odoo_password character varying,
    razorpay_key character varying,
    razorpay_secret character varying,
    n8n_webhook_url character varying,
    primary_color character varying,
    logo_url character varying,
    gstin character varying(15),
    address_line1 character varying,
    address_line2 character varying,
    city character varying,
    state character varying,
    pincode character varying(10)
);


ALTER TABLE odoo_saas_retail_db.tenants OWNER TO postgres;

--
-- Name: tenants_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.tenants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.tenants_id_seq OWNER TO postgres;

--
-- Name: tenants_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.tenants_id_seq OWNED BY odoo_saas_retail_db.tenants.id;


--
-- Name: units; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.units (
    id integer NOT NULL,
    tenant_id character varying,
    name character varying(50),
    abbreviation character varying(10)
);


ALTER TABLE odoo_saas_retail_db.units OWNER TO postgres;

--
-- Name: units_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.units_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.units_id_seq OWNER TO postgres;

--
-- Name: units_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.units_id_seq OWNED BY odoo_saas_retail_db.units.id;


--
-- Name: users; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    role character varying,
    tenant_id character varying NOT NULL,
    name character varying(255),
    pin character varying(4),
    permissions text
);


ALTER TABLE odoo_saas_retail_db.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.users_id_seq OWNED BY odoo_saas_retail_db.users.id;


--
-- Name: warehouses; Type: TABLE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE TABLE odoo_saas_retail_db.warehouses (
    id integer NOT NULL,
    tenant_id character varying,
    warehouse_name character varying,
    warehouse_code character varying,
    location_address character varying,
    latitude double precision,
    longitude double precision,
    capacity double precision,
    manager_name character varying,
    manager_phone character varying,
    is_active boolean,
    odoo_warehouse_id integer,
    created_at timestamp without time zone
);


ALTER TABLE odoo_saas_retail_db.warehouses OWNER TO postgres;

--
-- Name: warehouses_id_seq; Type: SEQUENCE; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE SEQUENCE odoo_saas_retail_db.warehouses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odoo_saas_retail_db.warehouses_id_seq OWNER TO postgres;

--
-- Name: warehouses_id_seq; Type: SEQUENCE OWNED BY; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER SEQUENCE odoo_saas_retail_db.warehouses_id_seq OWNED BY odoo_saas_retail_db.warehouses.id;


--
-- Name: attribute_values id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.attribute_values ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.attribute_values_id_seq'::regclass);


--
-- Name: attributes id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.attributes ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.attributes_id_seq'::regclass);


--
-- Name: automation_workflows id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.automation_workflows ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.automation_workflows_id_seq'::regclass);


--
-- Name: backorder_alerts id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.backorder_alerts ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.backorder_alerts_id_seq'::regclass);


--
-- Name: brands id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.brands ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.brands_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.categories ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.categories_id_seq'::regclass);


--
-- Name: collections id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.collections ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.collections_id_seq'::regclass);


--
-- Name: conversation_states id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.conversation_states ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.conversation_states_id_seq'::regclass);


--
-- Name: count_lines id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.count_lines ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.count_lines_id_seq'::regclass);


--
-- Name: coupons id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.coupons ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.coupons_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.customers ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.customers_id_seq'::regclass);


--
-- Name: demand_forecasts id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.demand_forecasts ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.demand_forecasts_id_seq'::regclass);


--
-- Name: fulfillments id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.fulfillments ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.fulfillments_id_seq'::regclass);


--
-- Name: inventory_audit_logs id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_audit_logs ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.inventory_audit_logs_id_seq'::regclass);


--
-- Name: inventory_counts id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_counts ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.inventory_counts_id_seq'::regclass);


--
-- Name: inventory_notifications id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_notifications ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.inventory_notifications_id_seq'::regclass);


--
-- Name: inventory_rules id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_rules ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.inventory_rules_id_seq'::regclass);


--
-- Name: landed_cost_assignments id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_cost_assignments ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.landed_cost_assignments_id_seq'::regclass);


--
-- Name: landed_costs id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_costs ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.landed_costs_id_seq'::regclass);


--
-- Name: order_fulfillments id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_fulfillments ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.order_fulfillments_id_seq'::regclass);


--
-- Name: order_returns id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_returns ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.order_returns_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.orders ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.orders_id_seq'::regclass);


--
-- Name: picking_batches id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.picking_batches ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.picking_batches_id_seq'::regclass);


--
-- Name: product_barcodes id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_barcodes ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.product_barcodes_id_seq'::regclass);


--
-- Name: product_images id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_images ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.product_images_id_seq'::regclass);


--
-- Name: product_skus id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.product_skus_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.products_id_seq'::regclass);


--
-- Name: purchase_order_lines id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_order_lines ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.purchase_order_lines_id_seq'::regclass);


--
-- Name: purchase_orders id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_orders ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.purchase_orders_id_seq'::regclass);


--
-- Name: refunds id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.refunds ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.refunds_id_seq'::regclass);


--
-- Name: reorder_suggestions id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.reorder_suggestions ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.reorder_suggestions_id_seq'::regclass);


--
-- Name: seasons id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.seasons ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.seasons_id_seq'::regclass);


--
-- Name: shifts id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.shifts ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.shifts_id_seq'::regclass);


--
-- Name: sku_alert_rules id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_alert_rules ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.sku_alert_rules_id_seq'::regclass);


--
-- Name: sku_barcodes id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_barcodes ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.sku_barcodes_id_seq'::regclass);


--
-- Name: sku_inventory_mappings id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_inventory_mappings ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.sku_inventory_mappings_id_seq'::regclass);


--
-- Name: sku_movement_logs id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_movement_logs ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.sku_movement_logs_id_seq'::regclass);


--
-- Name: sku_platform_mappings id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_platform_mappings ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.sku_platform_mappings_id_seq'::regclass);


--
-- Name: stock_alerts id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_alerts ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.stock_alerts_id_seq'::regclass);


--
-- Name: stock_locations id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_locations ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.stock_locations_id_seq'::regclass);


--
-- Name: stock_movements id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_movements ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.stock_movements_id_seq'::regclass);


--
-- Name: stock_transfers id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_transfers ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.stock_transfers_id_seq'::regclass);


--
-- Name: stock_valuation_layers id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_valuation_layers ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.stock_valuation_layers_id_seq'::regclass);


--
-- Name: supplier_performance id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.supplier_performance ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.supplier_performance_id_seq'::regclass);


--
-- Name: suppliers id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.suppliers ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.suppliers_id_seq'::regclass);


--
-- Name: tenants id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.tenants ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.tenants_id_seq'::regclass);


--
-- Name: units id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.units ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.units_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.users ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.users_id_seq'::regclass);


--
-- Name: warehouses id; Type: DEFAULT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.warehouses ALTER COLUMN id SET DEFAULT nextval('odoo_saas_retail_db.warehouses_id_seq'::regclass);


--
-- Data for Name: attribute_values; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.attribute_values (id, attribute_id, value, hex_color) FROM stdin;
1	1	M	\N
2	2	Blue	\N
3	1	OS	\N
4	2	Red	\N
13	5	S	\N
14	5	M	\N
15	5	L	\N
16	5	XL	\N
17	6	Black	\N
18	6	White	\N
19	6	Navy Blue	\N
20	6	Crimson Red	\N
\.


--
-- Data for Name: attributes; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.attributes (id, tenant_id, name, display_type) FROM stdin;
1	test_tenant_bulk	Size	select
2	test_tenant_bulk	Color	select
5	thread-trend	Size	select
6	thread-trend	Color	color_picker
\.


--
-- Data for Name: automation_workflows; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.automation_workflows (id, tenant_id, workflow_name, workflow_description, trigger_type, trigger_condition, steps, notification_channels, is_active, execution_count, last_executed, created_at) FROM stdin;
\.


--
-- Data for Name: backorder_alerts; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.backorder_alerts (id, tenant_id, order_id, product_id, quantity_short, expected_restock_date, customer_notification_sent, customer_notification_channel, last_notification_at, backorder_status, created_at) FROM stdin;
\.


--
-- Data for Name: brands; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.brands (id, tenant_id, name, code, description, logo_url) FROM stdin;
7	thread-trend	Zara	\N	Fast Fashion	\N
8	thread-trend	Levi's	\N	Denim Experts	\N
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.categories (id, tenant_id, name, description, parent_id, code) FROM stdin;
5	test_tenant_bulk	Apparel	\N	\N	\N
6	test_tenant_bulk	Outerwear	\N	5	\N
7	test_tenant_bulk	Accessories	\N	5	\N
17	thread-trend	Men's Wear	Apparel for Men	\N	\N
18	thread-trend	Women's Wear	Apparel for Women	\N	\N
19	thread-trend	Accessories	Bags, Belts, Hats	\N	\N
\.


--
-- Data for Name: collections; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.collections (id, tenant_id, season_id, name) FROM stdin;
\.


--
-- Data for Name: conversation_states; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.conversation_states (id, tenant_id, mobile, current_intent, selected_product, quantity, payment_status, current_state, selected_product_id, selected_sku, context, last_message_at, created_at) FROM stdin;
1	test_tenant_bulk	919876543210	\N	\N	\N	\N	IDLE	\N	\N	{}	2026-04-25 13:01:18.172261	2026-04-25 13:00:21.692323
\.


--
-- Data for Name: count_lines; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.count_lines (id, count_id, product_id, barcode, counted_qty, system_qty, variance, variance_reason) FROM stdin;
\.


--
-- Data for Name: coupons; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.coupons (id, tenant_id, code, discount_type, discount_value, min_purchase_amount, max_discount_amount, is_active, valid_from, valid_until, usage_limit, usage_count, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.customers (id, tenant_id, mobile, name, address, email, total_spend, order_count, last_order_date, created_at) FROM stdin;
1	acme-corp	Retail-Walk-In	Customer-k-In	\N	\N	5000	1	2026-04-24 07:32:31.750428	2026-04-24 07:32:31.74495
2	thread-trend	919000000001	John Doe	\N	john@example.com	150000	0	\N	2026-04-26 20:32:23.573273
3	thread-trend	919000000002	Jane Smith	\N	jane@example.com	12800	0	\N	2026-04-26 20:32:23.573274
4	thread-trend	919000000003	Alice Brown	\N	alice@example.com	53100	0	\N	2026-04-26 20:32:23.573274
\.


--
-- Data for Name: demand_forecasts; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.demand_forecasts (id, tenant_id, product_id, forecast_date, forecast_period, predicted_demand, confidence_level, model_type, lower_bound, upper_bound, actual_demand, accuracy_error, updated_at) FROM stdin;
\.


--
-- Data for Name: fulfillments; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.fulfillments (id, tenant_id, order_id, carrier_name, tracking_number, shipping_label_url, status, shipped_at, delivered_at, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: inventory_audit_logs; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.inventory_audit_logs (id, tenant_id, entity_type, entity_id, action, old_values, new_values, changed_by, change_reason, ip_address, created_at) FROM stdin;
\.


--
-- Data for Name: inventory_counts; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.inventory_counts (id, tenant_id, count_date, count_by_user, status, warehouse_id, total_items_counted, total_discrepancies, variance_percentage, notes, completed_at) FROM stdin;
\.


--
-- Data for Name: inventory_notifications; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.inventory_notifications (id, tenant_id, alert_id, recipient, notification_type, channel, message, status, sent_at, read_at, retries, created_at) FROM stdin;
\.


--
-- Data for Name: inventory_rules; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.inventory_rules (id, tenant_id, rule_name, rule_description, condition, action, rule_priority, is_enabled, last_triggered, trigger_count, created_at) FROM stdin;
\.


--
-- Data for Name: landed_cost_assignments; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.landed_cost_assignments (id, tenant_id, landed_cost_id, valuation_layer_id, allocated_amount, allocation_method, created_at) FROM stdin;
\.


--
-- Data for Name: landed_costs; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.landed_costs (id, tenant_id, name, cost_type, amount, status, purchase_order_id, created_at, validated_at) FROM stdin;
\.


--
-- Data for Name: order_fulfillments; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.order_fulfillments (id, tenant_id, order_id, fulfillment_status, warehouse_id, picker_id, packing_time, carrier, tracking_number, estimated_delivery, actual_delivery, proof_of_delivery, delivery_signature, delivery_notes, batch_id, fulfillment_method, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: order_returns; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.order_returns (id, tenant_id, order_id, quantity, reason, condition, status, return_date, processed_at, processed_by, refund_id) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.orders (id, tenant_id, customer_id, customer_mobile, sku, product_name, quantity, unit_price, total_amount, status, payment_status, payment_id, odoo_id, created_at, updated_at, unit_cost_at_sale, discount_amount, coupon_code, commitment_date, effective_delivery_date, invoice_number, shipping_address, customer_state, tax_type, tax_amount, grand_total, gst_rate, cgst_amount, sgst_amount, igst_amount, customer_gstin, hsn_code, notes, payment_method, source) FROM stdin;
18	thread-trend	2	919000000001	TT-SLI-M-BLA	Slim Fit Denim Jeans - M / Black	1	4500	4500	completed	completed	\N	\N	2026-04-26 20:32:23.576668	2026-04-26 20:54:26.610563	1500	0	\N	\N	\N	INV-THREAD-TREND-00018	\N	\N	IGST	540	5040	0	0	0	0	\N	\N	\N	\N	whatsapp
28	thread-trend	\N	0000000000	\N	Slim Fit Denim Jeans x1	1	5310	5310	pending	pending	\N	\N	2026-04-27 12:36:12.78051	2026-04-27 12:36:12.780512	\N	0	\N	\N	\N	\N	\N	\N	\N	0	5310	0	0	0	0	\N	\N	\N	upi	pos
27	thread-trend	\N	0000000000	\N	Classic Crewneck T-Shirt x1	1	1416	1416	pending	pending	\N	\N	2026-04-27 11:56:14.224297	2026-04-27 12:36:55.700238	\N	0	\N	\N	\N	INV-THREAD-TREND-00027	\N	\N	IGST	169.92	1585.92	0	0	0	0	\N	\N	\N	upi	pos
29	thread-trend	\N	0000000000	\N	Classic Crewneck T-Shirt x1	1	1416	1416	pending	pending	\N	\N	2026-04-27 12:37:10.377121	2026-04-27 12:37:10.377123	\N	0	\N	\N	\N	\N	\N	\N	\N	0	1416	0	0	0	0	\N	\N	\N	upi	pos
1	acme-corp	\N	919000000001	\N	Premium Subscription	1	5000	5000	completed	completed	\N	\N	2026-04-19 02:43:44.850531	\N	0	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	whatsapp
2	acme-corp	\N	919000000002	\N	Professional Node	2	12000	24000	pending	pending	\N	\N	2026-04-20 00:43:44.850531	\N	0	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	whatsapp
3	acme-corp	\N	919000000003	\N	Grid API Access	1	25000	25000	completed	completed	\N	\N	2026-04-13 02:43:44.850531	\N	0	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	whatsapp
9	acme-corp	1	Retail-Walk-In	ACME-PREM-01	Premium Subscription	1	5000	5000	completed	pending	\N	\N	2026-04-24 07:32:31.753208	2026-04-24 07:32:31.753211	3500	0	\N	\N	\N	\N	\N	\N	\N	0	0	\N	\N	\N	\N	\N	\N	\N	\N	whatsapp
10	test_tenant_bulk	\N	\N	JKT-DEN-BLU-M	Blue Denim Jacket	5	100	500	completed	pending	\N	\N	2026-04-25 12:42:55.915576	2026-04-25 12:42:55.916109	60	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
11	test_tenant_bulk	\N	919876543210	SHIRT-WA-001	WhatsApp Demo Shirt	3	999	2997	pending	pending	\N	\N	2026-04-25 13:01:18.174025	2026-04-25 13:01:18.174027	\N	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	Created via WhatsApp Bot	\N	whatsapp
12	thread-trend	4	919000000003	TT-SUM-M-BLA	Summer Floral Dress - M / Black	2	3200	6400	completed	completed	\N	\N	2026-04-19 20:32:23.576517	2026-04-26 20:32:23.578867	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
13	thread-trend	3	919000000002	TT-SUM-S-BLA	Summer Floral Dress - S / Black	1	3200	3200	completed	completed	\N	\N	2026-04-21 20:32:23.576562	2026-04-26 20:32:23.578868	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
14	thread-trend	4	919000000003	TT-SUM-M-WHI	Summer Floral Dress - M / White	3	3200	9600	completed	completed	\N	\N	2026-04-19 20:32:23.576578	2026-04-26 20:32:23.578868	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
15	thread-trend	4	919000000003	TT-SLI-M-BLA	Slim Fit Denim Jeans - M / Black	2	4500	9000	completed	completed	\N	\N	2026-04-25 20:32:23.576605	2026-04-26 20:32:23.578869	1500	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
16	thread-trend	2	919000000001	TT-SUM-M-WHI	Summer Floral Dress - M / White	3	3200	9600	completed	completed	\N	\N	2026-04-23 20:32:23.576629	2026-04-26 20:32:23.578869	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
17	thread-trend	4	919000000003	TT-SUM-M-WHI	Summer Floral Dress - M / White	1	3200	3200	completed	completed	\N	\N	2026-04-18 20:32:23.576644	2026-04-26 20:32:23.578878	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
19	thread-trend	2	919000000001	TT-LEA-L-WHI	Leather Moto Jacket - L / White	1	18500	18500	completed	completed	\N	\N	2026-04-24 20:32:23.576682	2026-04-26 20:32:23.578879	6000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
20	thread-trend	2	919000000001	TT-LEA-S-BLA	Leather Moto Jacket - S / Black	3	18500	55500	completed	completed	\N	\N	2026-04-16 20:32:23.576696	2026-04-26 20:32:23.578879	6000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
21	thread-trend	2	919000000001	TT-SUM-S-WHI	Summer Floral Dress - S / White	2	3200	6400	completed	completed	\N	\N	2026-04-24 20:32:23.576709	2026-04-26 20:32:23.578879	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
22	thread-trend	2	919000000001	TT-LEA-M-BLA	Leather Moto Jacket - M / Black	3	18500	55500	completed	completed	\N	\N	2026-04-20 20:32:23.57672	2026-04-26 20:32:23.57888	6000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
23	thread-trend	3	919000000002	TT-SUM-M-BLA	Summer Floral Dress - M / Black	3	3200	9600	completed	completed	\N	\N	2026-04-24 20:32:23.576743	2026-04-26 20:32:23.57888	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
24	thread-trend	4	919000000003	TT-SUM-M-BLA	Summer Floral Dress - M / Black	2	3200	6400	completed	completed	\N	\N	2026-04-16 20:32:23.576768	2026-04-26 20:32:23.57888	1000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
25	thread-trend	4	919000000003	TT-LEA-L-BLA	Leather Moto Jacket - L / Black	1	18500	18500	completed	completed	\N	\N	2026-04-20 20:32:23.576819	2026-04-26 20:32:23.578881	6000	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
26	thread-trend	4	919000000003	TT-SLI-L-WHI	Slim Fit Denim Jeans - L / White	1	4500	4500	pending	completed	\N	\N	2026-04-21 20:32:23.576847	2026-04-26 20:32:23.578881	1500	0	\N	\N	\N	\N	\N	\N	\N	0	0	0	0	0	0	\N	\N	\N	\N	whatsapp
\.


--
-- Data for Name: picking_batches; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.picking_batches (id, tenant_id, batch_name, status, warehouse_id, picker_id, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: product_barcodes; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.product_barcodes (id, tenant_id, product_id, barcode, barcode_type, is_primary, created_at) FROM stdin;
\.


--
-- Data for Name: product_images; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.product_images (id, tenant_id, product_id, url, alt_text, is_primary, "position") FROM stdin;
1	test_tenant_bulk	11	https://example.com/jack.jpg	\N	t	0
2	test_tenant_bulk	12	https://example.com/scarf.jpg	\N	t	0
\.


--
-- Data for Name: product_skus; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.product_skus (id, tenant_id, sku, sku_type, product_name, description, category, sub_category, product_id, category_id, brand_id, unit_id, cost_price, selling_price, minimum_selling_price, reorder_point, reorder_quantity, max_stock_level, lead_time_days, odoo_product_id, shopify_product_id, woocommerce_product_id, amazon_asin, ebay_item_id, external_sku, is_active, is_discontinued, weight, dimensions, color, size, created_at, updated_at, updated_by, sync_status, hsn_code, seasonal_price, seasonal_discount_pct, season_id, collection_id) FROM stdin;
1	default	SHIRT-BLUE-001	internal	Blue T-Shirt	\N	Apparel	\N	\N	\N	\N	\N	150	299	\N	20	100	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:38:43.177283	2026-04-20 02:38:43.177296	\N	pending	\N	\N	0	\N	\N
2	default	SHIRT-RED-001	internal	Red T-Shirt	\N	Apparel	\N	\N	\N	\N	\N	150	299	\N	20	100	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:38:43.177904	2026-04-20 02:38:43.177905	\N	pending	\N	\N	0	\N	\N
3	default	PANTS-BLACK-001	internal	Black Jeans	\N	Apparel	\N	\N	\N	\N	\N	400	899	\N	15	50	\N	5	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:38:43.178412	2026-04-20 02:38:43.178413	\N	pending	\N	\N	0	\N	\N
4	default	HAT-BASEBALL-001	internal	Baseball Cap	\N	Accessories	\N	\N	\N	\N	\N	100	199	\N	30	200	\N	10	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:38:43.178871	2026-04-20 02:38:43.178872	\N	pending	\N	\N	0	\N	\N
5	default	SHOE-RUNNING-001	internal	Running Shoes	\N	Footwear	\N	\N	\N	\N	\N	2000	4999	\N	10	50	\N	14	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:38:43.179338	2026-04-20 02:38:43.179339	\N	pending	\N	\N	0	\N	\N
6	acme-corp	ACME-PREM-01	internal	Premium Subscription	Access to all Acme premium features	\N	\N	1	\N	\N	\N	3500	5000	\N	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:44:40.603517	2026-04-20 02:44:40.603527	\N	pending	\N	\N	0	\N	\N
7	acme-corp	ACME-NODE-PRO	internal	Professional Node	High-performance compute node	\N	\N	2	\N	\N	\N	8400	12000	\N	1	7	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:44:40.604133	2026-04-20 02:44:40.604134	\N	pending	\N	\N	0	\N	\N
8	acme-corp	ACME-API-ENT	internal	Grid API Access	Enterprise API integration key	\N	\N	3	\N	\N	\N	17500	25000	\N	5	25	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-20 02:44:40.604624	2026-04-20 02:44:40.604625	\N	pending	\N	\N	0	\N	\N
14	test_tenant_bulk	JKT-DEN-BLU-M	internal	Blue Denim Jacket	\N	\N	\N	11	6	\N	\N	40	89.99	\N	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Blue	M	2026-04-25 12:39:03.307894	2026-04-25 12:48:13.500848	\N	pending	6105	62.99	30	\N	\N
15	test_tenant_bulk	SCR-SLK-RED-OS	internal	Red Silk Scarf	\N	\N	\N	12	7	\N	\N	15	45	\N	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Red	OS	2026-04-25 12:39:03.328027	2026-04-25 12:48:13.50085	\N	pending	6105	31.5	30	\N	\N
16	test_tenant_bulk	SHIRT-WA-001	internal	WhatsApp Demo Shirt	\N	\N	\N	\N	\N	\N	\N	\N	999	\N	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	\N	\N	2026-04-25 13:00:21.687081	2026-04-25 13:00:21.687088	\N	pending	6105	\N	0	\N	\N
41	thread-trend	TT-CLA-S-BLA	internal	Classic Crewneck T-Shirt - S / Black	\N	\N	\N	17	17	7	3	400	1200	960	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	S	2026-04-26 20:32:23.557664	2026-04-26 20:32:23.557666	\N	pending	6105	\N	0	\N	\N
42	thread-trend	TT-CLA-S-WHI	internal	Classic Crewneck T-Shirt - S / White	\N	\N	\N	17	17	7	3	400	1200	960	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	S	2026-04-26 20:32:23.557667	2026-04-26 20:32:23.557667	\N	pending	6105	\N	0	\N	\N
43	thread-trend	TT-CLA-M-BLA	internal	Classic Crewneck T-Shirt - M / Black	\N	\N	\N	17	17	7	3	400	1200	960	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	M	2026-04-26 20:32:23.557667	2026-04-26 20:32:23.557667	\N	pending	6105	\N	0	\N	\N
44	thread-trend	TT-CLA-M-WHI	internal	Classic Crewneck T-Shirt - M / White	\N	\N	\N	17	17	7	3	400	1200	960	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	M	2026-04-26 20:32:23.557668	2026-04-26 20:32:23.557668	\N	pending	6105	\N	0	\N	\N
45	thread-trend	TT-CLA-L-BLA	internal	Classic Crewneck T-Shirt - L / Black	\N	\N	\N	17	17	7	3	400	1200	960	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	L	2026-04-26 20:32:23.557668	2026-04-26 20:32:23.557669	\N	pending	6105	\N	0	\N	\N
46	thread-trend	TT-CLA-L-WHI	internal	Classic Crewneck T-Shirt - L / White	\N	\N	\N	17	17	7	3	400	1200	960	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	L	2026-04-26 20:32:23.557669	2026-04-26 20:32:23.557669	\N	pending	6105	\N	0	\N	\N
47	thread-trend	TT-SLI-S-BLA	internal	Slim Fit Denim Jeans - S / Black	\N	\N	\N	18	17	8	3	1500	4500	3600	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	S	2026-04-26 20:32:23.561786	2026-04-26 20:32:23.561787	\N	pending	6105	\N	0	\N	\N
48	thread-trend	TT-SLI-S-WHI	internal	Slim Fit Denim Jeans - S / White	\N	\N	\N	18	17	8	3	1500	4500	3600	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	S	2026-04-26 20:32:23.561788	2026-04-26 20:32:23.561788	\N	pending	6105	\N	0	\N	\N
49	thread-trend	TT-SLI-M-BLA	internal	Slim Fit Denim Jeans - M / Black	\N	\N	\N	18	17	8	3	1500	4500	3600	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	M	2026-04-26 20:32:23.561788	2026-04-26 20:32:23.561788	\N	pending	6105	\N	0	\N	\N
50	thread-trend	TT-SLI-M-WHI	internal	Slim Fit Denim Jeans - M / White	\N	\N	\N	18	17	8	3	1500	4500	3600	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	M	2026-04-26 20:32:23.561789	2026-04-26 20:32:23.561789	\N	pending	6105	\N	0	\N	\N
51	thread-trend	TT-SLI-L-BLA	internal	Slim Fit Denim Jeans - L / Black	\N	\N	\N	18	17	8	3	1500	4500	3600	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	L	2026-04-26 20:32:23.561789	2026-04-26 20:32:23.561789	\N	pending	6105	\N	0	\N	\N
52	thread-trend	TT-SLI-L-WHI	internal	Slim Fit Denim Jeans - L / White	\N	\N	\N	18	17	8	3	1500	4500	3600	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	L	2026-04-26 20:32:23.56179	2026-04-26 20:32:23.56179	\N	pending	6105	\N	0	\N	\N
53	thread-trend	TT-SUM-S-BLA	internal	Summer Floral Dress - S / Black	\N	\N	\N	19	18	7	3	1000	3200	2560	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	S	2026-04-26 20:32:23.564129	2026-04-26 20:32:23.56413	\N	pending	6105	\N	0	\N	\N
54	thread-trend	TT-SUM-S-WHI	internal	Summer Floral Dress - S / White	\N	\N	\N	19	18	7	3	1000	3200	2560	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	S	2026-04-26 20:32:23.564131	2026-04-26 20:32:23.564131	\N	pending	6105	\N	0	\N	\N
55	thread-trend	TT-SUM-M-BLA	internal	Summer Floral Dress - M / Black	\N	\N	\N	19	18	7	3	1000	3200	2560	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	M	2026-04-26 20:32:23.564131	2026-04-26 20:32:23.564131	\N	pending	6105	\N	0	\N	\N
56	thread-trend	TT-SUM-M-WHI	internal	Summer Floral Dress - M / White	\N	\N	\N	19	18	7	3	1000	3200	2560	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	M	2026-04-26 20:32:23.564132	2026-04-26 20:32:23.564132	\N	pending	6105	\N	0	\N	\N
57	thread-trend	TT-SUM-L-BLA	internal	Summer Floral Dress - L / Black	\N	\N	\N	19	18	7	3	1000	3200	2560	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	L	2026-04-26 20:32:23.564132	2026-04-26 20:32:23.564133	\N	pending	6105	\N	0	\N	\N
58	thread-trend	TT-SUM-L-WHI	internal	Summer Floral Dress - L / White	\N	\N	\N	19	18	7	3	1000	3200	2560	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	L	2026-04-26 20:32:23.564133	2026-04-26 20:32:23.564133	\N	pending	6105	\N	0	\N	\N
59	thread-trend	TT-LEA-S-BLA	internal	Leather Moto Jacket - S / Black	\N	\N	\N	20	18	7	3	6000	18500	14800	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	S	2026-04-26 20:32:23.566118	2026-04-26 20:32:23.566119	\N	pending	6105	\N	0	\N	\N
60	thread-trend	TT-LEA-S-WHI	internal	Leather Moto Jacket - S / White	\N	\N	\N	20	18	7	3	6000	18500	14800	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	S	2026-04-26 20:32:23.56612	2026-04-26 20:32:23.56612	\N	pending	6105	\N	0	\N	\N
61	thread-trend	TT-LEA-M-BLA	internal	Leather Moto Jacket - M / Black	\N	\N	\N	20	18	7	3	6000	18500	14800	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	M	2026-04-26 20:32:23.566121	2026-04-26 20:32:23.566121	\N	pending	6105	\N	0	\N	\N
62	thread-trend	TT-LEA-M-WHI	internal	Leather Moto Jacket - M / White	\N	\N	\N	20	18	7	3	6000	18500	14800	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	M	2026-04-26 20:32:23.566121	2026-04-26 20:32:23.566121	\N	pending	6105	\N	0	\N	\N
63	thread-trend	TT-LEA-L-BLA	internal	Leather Moto Jacket - L / Black	\N	\N	\N	20	18	7	3	6000	18500	14800	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	Black	L	2026-04-26 20:32:23.566122	2026-04-26 20:32:23.566122	\N	pending	6105	\N	0	\N	\N
64	thread-trend	TT-LEA-L-WHI	internal	Leather Moto Jacket - L / White	\N	\N	\N	20	18	7	3	6000	18500	14800	10	50	\N	7	\N	\N	\N	\N	\N	\N	t	f	\N	\N	White	L	2026-04-26 20:32:23.566122	2026-04-26 20:32:23.566123	\N	pending	6105	\N	0	\N	\N
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.products (id, tenant_id, name, description, price, sku, quantity, odoo_id, category_id, brand_id, unit_id, season_id, collection_id) FROM stdin;
1	acme-corp	Premium Subscription	Access to all Acme premium features	5000	ACME-PREM-01	100	\N	\N	\N	\N	\N	\N
2	acme-corp	Professional Node	High-performance compute node	12000	ACME-NODE-PRO	15	\N	\N	\N	\N	\N	\N
3	acme-corp	Grid API Access	Enterprise API integration key	25000	ACME-API-ENT	50	\N	\N	\N	\N	\N	\N
11	test_tenant_bulk	Blue Denim Jacket	High quality denim	89.99	JKT-DEN-BLU-M	50	\N	6	\N	\N	2	\N
12	test_tenant_bulk	Red Silk Scarf	100% Pure Silk	45	SCR-SLK-RED-OS	200	\N	7	\N	\N	2	\N
17	thread-trend	Classic Crewneck T-Shirt	Premium Classic Crewneck T-Shirt	1200	TT-CLA-MASTER	0	\N	17	7	3	\N	\N
18	thread-trend	Slim Fit Denim Jeans	Premium Slim Fit Denim Jeans	4500	TT-SLI-MASTER	0	\N	17	8	3	\N	\N
19	thread-trend	Summer Floral Dress	Premium Summer Floral Dress	3200	TT-SUM-MASTER	0	\N	18	7	3	\N	\N
20	thread-trend	Leather Moto Jacket	Premium Leather Moto Jacket	18500	TT-LEA-MASTER	0	\N	18	7	3	\N	\N
\.


--
-- Data for Name: purchase_order_lines; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.purchase_order_lines (id, tenant_id, po_id, product_id, product_name, quantity, unit_cost, total_cost, received_quantity, received_date, quality_status) FROM stdin;
\.


--
-- Data for Name: purchase_orders; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.purchase_orders (id, tenant_id, supplier_id, po_number, po_date, expected_delivery, actual_delivery, po_status, total_amount, payment_status, notes, created_at) FROM stdin;
\.


--
-- Data for Name: refunds; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.refunds (id, tenant_id, order_id, amount, currency, refund_method, status, transaction_id, created_at, processed_at) FROM stdin;
\.


--
-- Data for Name: reorder_suggestions; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.reorder_suggestions (id, tenant_id, product_id, suggested_quantity, reorder_point, lead_time_days, forecast_demand, rationale, ai_confidence, status, approved_by, approved_at, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: seasons; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.seasons (id, tenant_id, name, start_date, end_date, status, discount_pct) FROM stdin;
1	test_tenant_bulk	Summer 2024	2024-04-01 00:00:00	2024-08-31 00:00:00	active	0
2	test_tenant_bulk	Winter Test 20260425181813	2026-04-25 12:48:13.457461	2026-07-24 12:48:13.457472	finished	30
\.


--
-- Data for Name: shifts; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.shifts (id, tenant_id, user_id, start_time, end_time, opening_cash, closing_cash, total_sales, total_returns, total_tax, expected_cash, status, notes, created_at) FROM stdin;
\.


--
-- Data for Name: sku_alert_rules; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.sku_alert_rules (id, tenant_id, sku, alert_type, trigger_threshold, alert_level, notify_channels, notify_recipients, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sku_attribute_values; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.sku_attribute_values (sku_id, value_id) FROM stdin;
14	1
14	2
15	4
15	3
41	13
42	13
45	15
46	15
43	14
44	14
41	17
43	17
45	17
42	18
44	18
46	18
47	13
48	13
51	15
52	15
49	14
50	14
47	17
49	17
51	17
48	18
50	18
52	18
53	13
54	13
57	15
58	15
55	14
56	14
53	17
55	17
57	17
54	18
56	18
58	18
59	13
60	13
63	15
64	15
61	14
62	14
59	17
61	17
63	17
60	18
62	18
64	18
\.


--
-- Data for Name: sku_barcodes; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.sku_barcodes (id, tenant_id, sku, barcode, barcode_type, barcode_format, is_primary, is_active, barcode_source, supplier_reference, created_at, scanned_count, last_scanned) FROM stdin;
1	default	SHIRT-BLUE-001	1234567890001	EAN-13	linear	t	t	\N	\N	2026-04-20 02:38:43.18617	0	\N
2	default	SHIRT-BLUE-001	0001234567890	UPC-A	linear	f	t	\N	\N	2026-04-20 02:38:43.186602	0	\N
3	default	SHIRT-RED-001	1234567890002	EAN-13	linear	t	t	\N	\N	2026-04-20 02:38:43.186961	0	\N
4	default	PANTS-BLACK-001	1234567890003	EAN-13	linear	t	t	\N	\N	2026-04-20 02:38:43.187308	0	\N
5	default	HAT-BASEBALL-001	1234567890004	EAN-13	linear	t	t	\N	\N	2026-04-20 02:38:43.187674	0	\N
6	default	SHOE-RUNNING-001	1234567890005	EAN-13	linear	t	t	\N	\N	2026-04-20 02:38:43.188234	0	\N
\.


--
-- Data for Name: sku_inventory_mappings; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.sku_inventory_mappings (id, tenant_id, sku, warehouse_id, zone_name, bin_number, quantity_on_hand, quantity_reserved, quantity_available, quantity_damaged, last_counted, last_movement, movement_count, created_at, updated_at) FROM stdin;
1	default	SHIRT-BLUE-001	1	A	A1	50	10	40	0	\N	\N	0	2026-04-20 02:38:43.192461	2026-04-20 02:38:43.192494
2	default	SHIRT-RED-001	1	A	A2	35	5	30	0	\N	\N	0	2026-04-20 02:38:43.193047	2026-04-20 02:38:43.193048
3	default	PANTS-BLACK-001	1	B	B1	25	3	22	0	\N	\N	0	2026-04-20 02:38:43.193491	2026-04-20 02:38:43.193492
4	default	HAT-BASEBALL-001	2	C	C1	150	20	130	0	\N	\N	0	2026-04-20 02:38:43.193928	2026-04-20 02:38:43.193928
5	default	SHOE-RUNNING-001	2	D	D1	30	5	25	0	\N	\N	0	2026-04-20 02:38:43.194389	2026-04-20 02:38:43.194391
6	acme-corp	ACME-PREM-01	1	\N	\N	100	0	100	0	\N	\N	0	2026-04-20 02:48:48.213795	2026-04-20 02:48:48.213795
7	acme-corp	ACME-NODE-PRO	1	\N	\N	15	0	15	0	\N	\N	0	2026-04-20 02:48:48.216351	2026-04-20 02:48:48.216352
8	acme-corp	ACME-API-ENT	1	\N	\N	50	0	50	0	\N	\N	0	2026-04-20 02:48:48.218375	2026-04-20 02:48:48.218375
38	thread-trend	TT-CLA-S-BLA	10	\N	\N	43	0	43	0	\N	\N	0	2026-04-26 20:32:23.571552	2026-04-26 20:32:23.571553
39	thread-trend	TT-CLA-S-WHI	10	\N	\N	15	0	15	0	\N	\N	0	2026-04-26 20:32:23.571553	2026-04-26 20:32:23.571553
40	thread-trend	TT-CLA-M-BLA	10	\N	\N	21	0	21	0	\N	\N	0	2026-04-26 20:32:23.571554	2026-04-26 20:32:23.571554
41	thread-trend	TT-CLA-M-WHI	10	\N	\N	48	0	48	0	\N	\N	0	2026-04-26 20:32:23.571554	2026-04-26 20:32:23.571554
42	thread-trend	TT-CLA-L-BLA	10	\N	\N	44	0	44	0	\N	\N	0	2026-04-26 20:32:23.571555	2026-04-26 20:32:23.571555
43	thread-trend	TT-CLA-L-WHI	10	\N	\N	37	0	37	0	\N	\N	0	2026-04-26 20:32:23.571555	2026-04-26 20:32:23.571555
44	thread-trend	TT-SLI-S-BLA	10	\N	\N	11	0	11	0	\N	\N	0	2026-04-26 20:32:23.571556	2026-04-26 20:32:23.571556
45	thread-trend	TT-SLI-S-WHI	10	\N	\N	48	0	48	0	\N	\N	0	2026-04-26 20:32:23.571556	2026-04-26 20:32:23.571556
46	thread-trend	TT-SLI-M-BLA	10	\N	\N	34	0	34	0	\N	\N	0	2026-04-26 20:32:23.571557	2026-04-26 20:32:23.571557
47	thread-trend	TT-SLI-M-WHI	10	\N	\N	46	0	46	0	\N	\N	0	2026-04-26 20:32:23.571557	2026-04-26 20:32:23.571557
48	thread-trend	TT-SLI-L-BLA	10	\N	\N	31	0	31	0	\N	\N	0	2026-04-26 20:32:23.571558	2026-04-26 20:32:23.571558
49	thread-trend	TT-SLI-L-WHI	10	\N	\N	19	0	19	0	\N	\N	0	2026-04-26 20:32:23.571558	2026-04-26 20:32:23.571558
50	thread-trend	TT-SUM-S-BLA	10	\N	\N	45	0	45	0	\N	\N	0	2026-04-26 20:32:23.571558	2026-04-26 20:32:23.571559
51	thread-trend	TT-SUM-S-WHI	10	\N	\N	47	0	47	0	\N	\N	0	2026-04-26 20:32:23.571559	2026-04-26 20:32:23.571559
52	thread-trend	TT-SUM-M-BLA	10	\N	\N	29	0	29	0	\N	\N	0	2026-04-26 20:32:23.571559	2026-04-26 20:32:23.57156
53	thread-trend	TT-SUM-M-WHI	10	\N	\N	21	0	21	0	\N	\N	0	2026-04-26 20:32:23.57156	2026-04-26 20:32:23.57156
54	thread-trend	TT-SUM-L-BLA	10	\N	\N	31	0	31	0	\N	\N	0	2026-04-26 20:32:23.57156	2026-04-26 20:32:23.57156
55	thread-trend	TT-SUM-L-WHI	10	\N	\N	29	0	29	0	\N	\N	0	2026-04-26 20:32:23.571561	2026-04-26 20:32:23.571561
56	thread-trend	TT-LEA-S-BLA	10	\N	\N	37	0	37	0	\N	\N	0	2026-04-26 20:32:23.571561	2026-04-26 20:32:23.571561
57	thread-trend	TT-LEA-S-WHI	10	\N	\N	25	0	25	0	\N	\N	0	2026-04-26 20:32:23.571562	2026-04-26 20:32:23.571562
58	thread-trend	TT-LEA-M-BLA	10	\N	\N	49	0	49	0	\N	\N	0	2026-04-26 20:32:23.571562	2026-04-26 20:32:23.571562
59	thread-trend	TT-LEA-M-WHI	10	\N	\N	32	0	32	0	\N	\N	0	2026-04-26 20:32:23.571563	2026-04-26 20:32:23.571563
60	thread-trend	TT-LEA-L-BLA	10	\N	\N	26	0	26	0	\N	\N	0	2026-04-26 20:32:23.571563	2026-04-26 20:32:23.571563
61	thread-trend	TT-LEA-L-WHI	10	\N	\N	19	0	19	0	\N	\N	0	2026-04-26 20:32:23.571563	2026-04-26 20:32:23.571564
\.


--
-- Data for Name: sku_movement_logs; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.sku_movement_logs (id, tenant_id, sku, movement_type, quantity, reference_type, reference_id, from_warehouse_id, from_zone, from_bin, to_warehouse_id, to_zone, to_bin, reason, platform_source, created_by, notes, created_at) FROM stdin;
\.


--
-- Data for Name: sku_platform_mappings; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.sku_platform_mappings (id, tenant_id, sku, platform_name, platform_product_id, platform_variant_id, last_synced, sync_status, sync_errors, platform_stock_level, platform_reserved, platform_available, created_at, updated_at) FROM stdin;
1	default	SHIRT-BLUE-001	odoo	1001	\N	\N	pending	\N	50	0	0	2026-04-20 02:38:43.199186	2026-04-20 02:38:43.199191
2	default	SHIRT-BLUE-001	shopify	gid://shopify/Product/5678	\N	\N	pending	\N	15	0	0	2026-04-20 02:38:43.199658	2026-04-20 02:38:43.199659
3	default	SHIRT-BLUE-001	woocommerce	2001	\N	\N	pending	\N	20	0	0	2026-04-20 02:38:43.20019	2026-04-20 02:38:43.20019
4	default	PANTS-BLACK-001	amazon	B0ABC123DE	\N	\N	pending	\N	25	0	0	2026-04-20 02:38:43.200609	2026-04-20 02:38:43.20061
\.


--
-- Data for Name: stock_alerts; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.stock_alerts (id, tenant_id, product_id, alert_type, alert_level, threshold_value, current_value, status, triggered_at, acknowledged_at, acknowledged_by, resolved_at, created_at) FROM stdin;
\.


--
-- Data for Name: stock_locations; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.stock_locations (id, tenant_id, product_id, parent_id, location_type, name, warehouse_id, zone_name, bin_number, is_scrap, is_active, quantity, reserved_quantity, available_quantity, reorder_point, reorder_quantity, last_counted, last_stock_check, updated_at, is_clearance) FROM stdin;
1	acme-corp	1	\N	internal	Shelf-01	1	\N	\N	f	t	100	0	100	10	50	\N	2026-04-20 02:48:48.209278	2026-04-20 02:48:48.20928	f
2	acme-corp	2	\N	internal	Shelf-RO	1	\N	\N	f	t	15	0	15	10	50	\N	2026-04-20 02:48:48.213073	2026-04-20 02:48:48.213075	f
3	acme-corp	3	\N	internal	Shelf-NT	1	\N	\N	f	t	50	0	50	10	50	\N	2026-04-20 02:48:48.215818	2026-04-20 02:48:48.215819	f
11	thread-trend	\N	\N	internal	Zone A (Tops)	10	\N	\N	f	t	0	0	0	10	50	\N	2026-04-26 20:32:23.56961	2026-04-26 20:32:23.569611	f
12	thread-trend	\N	\N	internal	Zone B (Bottoms)	10	\N	\N	f	t	0	0	0	10	50	\N	2026-04-26 20:32:23.569637	2026-04-26 20:32:23.569638	f
\.


--
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.stock_movements (id, tenant_id, product_id, location_id, movement_type, quantity, reference_id, reference_type, reason, created_by, notes, created_at) FROM stdin;
\.


--
-- Data for Name: stock_transfers; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.stock_transfers (id, tenant_id, product_id, from_warehouse_id, to_warehouse_id, quantity, status, transfer_date, received_date, received_by, notes, created_at) FROM stdin;
\.


--
-- Data for Name: stock_valuation_layers; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.stock_valuation_layers (id, tenant_id, product_id, sku, original_quantity, remaining_quantity, unit_cost, total_value, reference_id, reference_type, landed_cost_value, is_fully_consumed, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: supplier_performance; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.supplier_performance (id, supplier_id, tenant_id, on_time_delivery_rate, quality_score, lead_time_average, defect_rate, last_evaluated, evaluation_count, updated_at) FROM stdin;
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.suppliers (id, tenant_id, supplier_name, contact_person, phone, whatsapp_number, email, address, lead_time_days, reliability_score, payment_terms, is_preferred, is_active, created_at) FROM stdin;
1	thread-trend	Global Textiles Ltd.	\N	1800111222	\N	\N	\N	14	0	\N	f	t	2026-04-26 20:32:23.575174
2	thread-trend	Denim Works Inc.	\N	1800333444	\N	\N	\N	21	0	\N	f	t	2026-04-26 20:32:23.575175
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.tenants (id, tenant_id, business_name, whatsapp_number, odoo_url, odoo_db, odoo_user, odoo_password, razorpay_key, razorpay_secret, n8n_webhook_url, primary_color, logo_url, gstin, address_line1, address_line2, city, state, pincode) FROM stdin;
1	acme-corp	Acme Global Solutions	919876543210	https://acme.odoo.com	acme_prod	admin@acme.com	pass123	rzp_test_acme123	secret_acme_456	https://n8n.acme.com/webhook	#0d9488	\N	\N	\N	\N	\N	\N	\N
2	tech-flow	TechFlow Innovations	919876543211	https://techflow.odoo.com	techflow_db	ops@techflow.io	secure_pass	rzp_test_tech789	secret_tech_012	https://n8n.techflow.io/webhook	#0d9488	\N	\N	\N	\N	\N	\N	\N
3	green-retail	GreenLeaf Retailers	919876543212	https://greenleaf.odoo.com	green_prod	admin@greenleaf.com	green123	rzp_test_green345	secret_green_678	\N	#0d9488	\N	\N	\N	\N	\N	\N	\N
4	swift-logistics	Swift Logistics Group	919876543213	https://swift.odoo.com	swift_db	super@swift.com	swift_secure	rzp_test_swift901	secret_swift_234	https://n8n.swift.com/webhook	#0d9488	\N	\N	\N	\N	\N	\N	\N
5	urban-style	UrbanStyle Fashion	919876543214	https://urban.odoo.com	urban_style_db	manager@urban.style	style_pass	rzp_test_urban567	secret_urban_890	\N	#0d9488	\N	\N	\N	\N	\N	\N	\N
7	test_tenant_bulk	Test Tenant for Bulk	\N	\N	\N	\N	\N	\N	\N	\N	#000000	\N	\N	\N	\N	\N	\N	\N
6	thread-trend	Thread & Trend Garments	919888777666	https://garments.odoo.com	garment_prod	ops@threadtrend.com	garments123	rzp_test_garment999	secret_garment_888	https://n8n.hook.garments.com	#6586ec	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: units; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.units (id, tenant_id, name, abbreviation) FROM stdin;
3	thread-trend	Pieces	Pcs
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.users (id, email, hashed_password, role, tenant_id, name, pin, permissions) FROM stdin;
1	admin@acme.com	$2b$12$NE/7h2wCl1aiPHLHeF6DUevUL0rFMTKRRQKOopy8FOExJ8..30vnu	owner	acme-corp	\N	\N	\N
2	ops@techflow.io	$2b$12$H0JCZOPCTypfs.Au9f.pIuXGbWjOhSYbzSmvyL44nNsj3SrfLGN5O	owner	tech-flow	\N	\N	\N
3	admin@greenleaf.com	$2b$12$jIBUkBnfFoKU0WS8GizrpepTUcSHfiHbrBN/SGzvLShGsYDLyQEPe	owner	green-retail	\N	\N	\N
4	super@swift.com	$2b$12$soofjlnq4KeARkdlSzde4upjU18zjftrdVYOqpPxzlrI9oVaplXSK	owner	swift-logistics	\N	\N	\N
5	manager@urban.style	$2b$12$1i09y19nYSGuG7fls1/GLuZyVSmKSgi3dLdbPt5gfBRdGtiCtX.L2	owner	urban-style	\N	\N	\N
6	ops@threadtrend.com	$2b$12$zcyp.rTmgdT8xv5jjRcYVeqJs8bVOecw0hdHaVfIxg0c14B0MsgOW	owner	thread-trend	\N	\N	\N
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: odoo_saas_retail_db; Owner: postgres
--

COPY odoo_saas_retail_db.warehouses (id, tenant_id, warehouse_name, warehouse_code, location_address, latitude, longitude, capacity, manager_name, manager_phone, is_active, odoo_warehouse_id, created_at) FROM stdin;
1	acme-corp	Main Warehouse	WH-ACME	Default Address	\N	\N	10000	\N	\N	t	\N	2026-04-20 02:48:48.203883
2	tech-flow	Main Warehouse	WH-TECH	Default Address	\N	\N	10000	\N	\N	t	\N	2026-04-20 02:48:48.217904
3	green-retail	Main Warehouse	WH-GREE	Default Address	\N	\N	10000	\N	\N	t	\N	2026-04-20 02:48:48.219756
4	swift-logistics	Main Warehouse	WH-SWIF	Default Address	\N	\N	10000	\N	\N	t	\N	2026-04-20 02:48:48.22099
5	urban-style	Main Warehouse	WH-URBA	Default Address	\N	\N	10000	\N	\N	t	\N	2026-04-20 02:48:48.222187
9	thread-trend	Main Distribution Center	MDC	\N	\N	\N	50000	\N	\N	t	\N	2026-04-26 20:32:23.568033
10	thread-trend	Downtown Retail Store	DRS	\N	\N	\N	5000	\N	\N	t	\N	2026-04-26 20:32:23.568034
\.


--
-- Name: attribute_values_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.attribute_values_id_seq', 20, true);


--
-- Name: attributes_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.attributes_id_seq', 6, true);


--
-- Name: automation_workflows_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.automation_workflows_id_seq', 1, false);


--
-- Name: backorder_alerts_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.backorder_alerts_id_seq', 1, false);


--
-- Name: brands_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.brands_id_seq', 8, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.categories_id_seq', 19, true);


--
-- Name: collections_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.collections_id_seq', 1, false);


--
-- Name: conversation_states_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.conversation_states_id_seq', 1, true);


--
-- Name: count_lines_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.count_lines_id_seq', 1, false);


--
-- Name: coupons_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.coupons_id_seq', 1, false);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.customers_id_seq', 4, true);


--
-- Name: demand_forecasts_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.demand_forecasts_id_seq', 1, false);


--
-- Name: fulfillments_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.fulfillments_id_seq', 1, false);


--
-- Name: inventory_audit_logs_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.inventory_audit_logs_id_seq', 1, false);


--
-- Name: inventory_counts_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.inventory_counts_id_seq', 1, false);


--
-- Name: inventory_notifications_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.inventory_notifications_id_seq', 1, false);


--
-- Name: inventory_rules_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.inventory_rules_id_seq', 1, false);


--
-- Name: landed_cost_assignments_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.landed_cost_assignments_id_seq', 1, false);


--
-- Name: landed_costs_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.landed_costs_id_seq', 1, false);


--
-- Name: order_fulfillments_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.order_fulfillments_id_seq', 1, false);


--
-- Name: order_returns_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.order_returns_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.orders_id_seq', 29, true);


--
-- Name: picking_batches_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.picking_batches_id_seq', 1, false);


--
-- Name: product_barcodes_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.product_barcodes_id_seq', 1, false);


--
-- Name: product_images_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.product_images_id_seq', 2, true);


--
-- Name: product_skus_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.product_skus_id_seq', 64, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.products_id_seq', 20, true);


--
-- Name: purchase_order_lines_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.purchase_order_lines_id_seq', 1, false);


--
-- Name: purchase_orders_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.purchase_orders_id_seq', 1, false);


--
-- Name: refunds_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.refunds_id_seq', 1, false);


--
-- Name: reorder_suggestions_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.reorder_suggestions_id_seq', 1, false);


--
-- Name: seasons_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.seasons_id_seq', 2, true);


--
-- Name: shifts_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.shifts_id_seq', 1, false);


--
-- Name: sku_alert_rules_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.sku_alert_rules_id_seq', 1, false);


--
-- Name: sku_barcodes_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.sku_barcodes_id_seq', 6, true);


--
-- Name: sku_inventory_mappings_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.sku_inventory_mappings_id_seq', 61, true);


--
-- Name: sku_movement_logs_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.sku_movement_logs_id_seq', 1, false);


--
-- Name: sku_platform_mappings_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.sku_platform_mappings_id_seq', 4, true);


--
-- Name: stock_alerts_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.stock_alerts_id_seq', 1, false);


--
-- Name: stock_locations_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.stock_locations_id_seq', 12, true);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.stock_movements_id_seq', 1, false);


--
-- Name: stock_transfers_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.stock_transfers_id_seq', 1, false);


--
-- Name: stock_valuation_layers_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.stock_valuation_layers_id_seq', 1, false);


--
-- Name: supplier_performance_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.supplier_performance_id_seq', 1, false);


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.suppliers_id_seq', 2, true);


--
-- Name: tenants_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.tenants_id_seq', 7, true);


--
-- Name: units_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.units_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.users_id_seq', 6, true);


--
-- Name: warehouses_id_seq; Type: SEQUENCE SET; Schema: odoo_saas_retail_db; Owner: postgres
--

SELECT pg_catalog.setval('odoo_saas_retail_db.warehouses_id_seq', 10, true);


--
-- Name: sku_platform_mappings _sku_platform_unique; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_platform_mappings
    ADD CONSTRAINT _sku_platform_unique UNIQUE (sku, platform_name, platform_product_id);


--
-- Name: attribute_values attribute_values_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.attribute_values
    ADD CONSTRAINT attribute_values_pkey PRIMARY KEY (id);


--
-- Name: attributes attributes_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.attributes
    ADD CONSTRAINT attributes_pkey PRIMARY KEY (id);


--
-- Name: automation_workflows automation_workflows_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.automation_workflows
    ADD CONSTRAINT automation_workflows_pkey PRIMARY KEY (id);


--
-- Name: backorder_alerts backorder_alerts_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.backorder_alerts
    ADD CONSTRAINT backorder_alerts_pkey PRIMARY KEY (id);


--
-- Name: brands brands_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.brands
    ADD CONSTRAINT brands_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: collections collections_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.collections
    ADD CONSTRAINT collections_pkey PRIMARY KEY (id);


--
-- Name: conversation_states conversation_states_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.conversation_states
    ADD CONSTRAINT conversation_states_pkey PRIMARY KEY (id);


--
-- Name: count_lines count_lines_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.count_lines
    ADD CONSTRAINT count_lines_pkey PRIMARY KEY (id);


--
-- Name: coupons coupons_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.coupons
    ADD CONSTRAINT coupons_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: demand_forecasts demand_forecasts_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.demand_forecasts
    ADD CONSTRAINT demand_forecasts_pkey PRIMARY KEY (id);


--
-- Name: fulfillments fulfillments_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.fulfillments
    ADD CONSTRAINT fulfillments_pkey PRIMARY KEY (id);


--
-- Name: inventory_audit_logs inventory_audit_logs_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_audit_logs
    ADD CONSTRAINT inventory_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: inventory_counts inventory_counts_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_counts
    ADD CONSTRAINT inventory_counts_pkey PRIMARY KEY (id);


--
-- Name: inventory_notifications inventory_notifications_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_notifications
    ADD CONSTRAINT inventory_notifications_pkey PRIMARY KEY (id);


--
-- Name: inventory_rules inventory_rules_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_rules
    ADD CONSTRAINT inventory_rules_pkey PRIMARY KEY (id);


--
-- Name: landed_cost_assignments landed_cost_assignments_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_cost_assignments
    ADD CONSTRAINT landed_cost_assignments_pkey PRIMARY KEY (id);


--
-- Name: landed_costs landed_costs_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_costs
    ADD CONSTRAINT landed_costs_pkey PRIMARY KEY (id);


--
-- Name: order_fulfillments order_fulfillments_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_fulfillments
    ADD CONSTRAINT order_fulfillments_pkey PRIMARY KEY (id);


--
-- Name: order_returns order_returns_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_returns
    ADD CONSTRAINT order_returns_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: picking_batches picking_batches_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.picking_batches
    ADD CONSTRAINT picking_batches_pkey PRIMARY KEY (id);


--
-- Name: product_barcodes product_barcodes_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_barcodes
    ADD CONSTRAINT product_barcodes_pkey PRIMARY KEY (id);


--
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (id);


--
-- Name: product_skus product_skus_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: purchase_order_lines purchase_order_lines_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_order_lines
    ADD CONSTRAINT purchase_order_lines_pkey PRIMARY KEY (id);


--
-- Name: purchase_orders purchase_orders_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_orders
    ADD CONSTRAINT purchase_orders_pkey PRIMARY KEY (id);


--
-- Name: refunds refunds_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.refunds
    ADD CONSTRAINT refunds_pkey PRIMARY KEY (id);


--
-- Name: reorder_suggestions reorder_suggestions_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.reorder_suggestions
    ADD CONSTRAINT reorder_suggestions_pkey PRIMARY KEY (id);


--
-- Name: seasons seasons_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.seasons
    ADD CONSTRAINT seasons_pkey PRIMARY KEY (id);


--
-- Name: shifts shifts_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.shifts
    ADD CONSTRAINT shifts_pkey PRIMARY KEY (id);


--
-- Name: sku_alert_rules sku_alert_rules_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_alert_rules
    ADD CONSTRAINT sku_alert_rules_pkey PRIMARY KEY (id);


--
-- Name: sku_attribute_values sku_attribute_values_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_attribute_values
    ADD CONSTRAINT sku_attribute_values_pkey PRIMARY KEY (sku_id, value_id);


--
-- Name: sku_barcodes sku_barcodes_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_barcodes
    ADD CONSTRAINT sku_barcodes_pkey PRIMARY KEY (id);


--
-- Name: sku_inventory_mappings sku_inventory_mappings_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_inventory_mappings
    ADD CONSTRAINT sku_inventory_mappings_pkey PRIMARY KEY (id);


--
-- Name: sku_movement_logs sku_movement_logs_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_movement_logs
    ADD CONSTRAINT sku_movement_logs_pkey PRIMARY KEY (id);


--
-- Name: sku_platform_mappings sku_platform_mappings_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_platform_mappings
    ADD CONSTRAINT sku_platform_mappings_pkey PRIMARY KEY (id);


--
-- Name: stock_alerts stock_alerts_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_alerts
    ADD CONSTRAINT stock_alerts_pkey PRIMARY KEY (id);


--
-- Name: stock_locations stock_locations_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_locations
    ADD CONSTRAINT stock_locations_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: stock_transfers stock_transfers_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_transfers
    ADD CONSTRAINT stock_transfers_pkey PRIMARY KEY (id);


--
-- Name: stock_valuation_layers stock_valuation_layers_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_valuation_layers
    ADD CONSTRAINT stock_valuation_layers_pkey PRIMARY KEY (id);


--
-- Name: supplier_performance supplier_performance_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.supplier_performance
    ADD CONSTRAINT supplier_performance_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: units units_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: idx_categories_code; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX idx_categories_code ON odoo_saas_retail_db.categories USING btree (code);


--
-- Name: idx_coupons_tenant_code; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX idx_coupons_tenant_code ON odoo_saas_retail_db.coupons USING btree (tenant_id, code);


--
-- Name: ix_attribute_values_attribute_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_attribute_values_attribute_id ON odoo_saas_retail_db.attribute_values USING btree (attribute_id);


--
-- Name: ix_attribute_values_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_attribute_values_id ON odoo_saas_retail_db.attribute_values USING btree (id);


--
-- Name: ix_attribute_values_value; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_attribute_values_value ON odoo_saas_retail_db.attribute_values USING btree (value);


--
-- Name: ix_attributes_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_attributes_id ON odoo_saas_retail_db.attributes USING btree (id);


--
-- Name: ix_attributes_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_attributes_name ON odoo_saas_retail_db.attributes USING btree (name);


--
-- Name: ix_attributes_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_attributes_tenant_id ON odoo_saas_retail_db.attributes USING btree (tenant_id);


--
-- Name: ix_automation_workflows_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_automation_workflows_id ON odoo_saas_retail_db.automation_workflows USING btree (id);


--
-- Name: ix_automation_workflows_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_automation_workflows_tenant_id ON odoo_saas_retail_db.automation_workflows USING btree (tenant_id);


--
-- Name: ix_backorder_alerts_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_backorder_alerts_id ON odoo_saas_retail_db.backorder_alerts USING btree (id);


--
-- Name: ix_backorder_alerts_order_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_backorder_alerts_order_id ON odoo_saas_retail_db.backorder_alerts USING btree (order_id);


--
-- Name: ix_backorder_alerts_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_backorder_alerts_tenant_id ON odoo_saas_retail_db.backorder_alerts USING btree (tenant_id);


--
-- Name: ix_brands_code; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_brands_code ON odoo_saas_retail_db.brands USING btree (code);


--
-- Name: ix_brands_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_brands_id ON odoo_saas_retail_db.brands USING btree (id);


--
-- Name: ix_brands_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_brands_name ON odoo_saas_retail_db.brands USING btree (name);


--
-- Name: ix_brands_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_brands_tenant_id ON odoo_saas_retail_db.brands USING btree (tenant_id);


--
-- Name: ix_conversation_states_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_conversation_states_id ON odoo_saas_retail_db.conversation_states USING btree (id);


--
-- Name: ix_conversation_states_mobile; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_conversation_states_mobile ON odoo_saas_retail_db.conversation_states USING btree (mobile);


--
-- Name: ix_conversation_states_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_conversation_states_tenant_id ON odoo_saas_retail_db.conversation_states USING btree (tenant_id);


--
-- Name: ix_count_lines_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_count_lines_id ON odoo_saas_retail_db.count_lines USING btree (id);


--
-- Name: ix_coupons_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_coupons_id ON odoo_saas_retail_db.coupons USING btree (id);


--
-- Name: ix_coupons_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_coupons_tenant_id ON odoo_saas_retail_db.coupons USING btree (tenant_id);


--
-- Name: ix_customers_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_customers_id ON odoo_saas_retail_db.customers USING btree (id);


--
-- Name: ix_customers_mobile; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_customers_mobile ON odoo_saas_retail_db.customers USING btree (mobile);


--
-- Name: ix_customers_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_customers_tenant_id ON odoo_saas_retail_db.customers USING btree (tenant_id);


--
-- Name: ix_demand_forecasts_forecast_date; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_demand_forecasts_forecast_date ON odoo_saas_retail_db.demand_forecasts USING btree (forecast_date);


--
-- Name: ix_demand_forecasts_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_demand_forecasts_id ON odoo_saas_retail_db.demand_forecasts USING btree (id);


--
-- Name: ix_demand_forecasts_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_demand_forecasts_product_id ON odoo_saas_retail_db.demand_forecasts USING btree (product_id);


--
-- Name: ix_demand_forecasts_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_demand_forecasts_tenant_id ON odoo_saas_retail_db.demand_forecasts USING btree (tenant_id);


--
-- Name: ix_fulfillments_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_fulfillments_id ON odoo_saas_retail_db.fulfillments USING btree (id);


--
-- Name: ix_fulfillments_order_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_fulfillments_order_id ON odoo_saas_retail_db.fulfillments USING btree (order_id);


--
-- Name: ix_fulfillments_status; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_fulfillments_status ON odoo_saas_retail_db.fulfillments USING btree (status);


--
-- Name: ix_fulfillments_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_fulfillments_tenant_id ON odoo_saas_retail_db.fulfillments USING btree (tenant_id);


--
-- Name: ix_fulfillments_tracking_number; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_fulfillments_tracking_number ON odoo_saas_retail_db.fulfillments USING btree (tracking_number);


--
-- Name: ix_inventory_audit_logs_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_audit_logs_created_at ON odoo_saas_retail_db.inventory_audit_logs USING btree (created_at);


--
-- Name: ix_inventory_audit_logs_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_audit_logs_id ON odoo_saas_retail_db.inventory_audit_logs USING btree (id);


--
-- Name: ix_inventory_audit_logs_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_audit_logs_tenant_id ON odoo_saas_retail_db.inventory_audit_logs USING btree (tenant_id);


--
-- Name: ix_inventory_counts_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_counts_id ON odoo_saas_retail_db.inventory_counts USING btree (id);


--
-- Name: ix_inventory_counts_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_counts_tenant_id ON odoo_saas_retail_db.inventory_counts USING btree (tenant_id);


--
-- Name: ix_inventory_notifications_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_notifications_created_at ON odoo_saas_retail_db.inventory_notifications USING btree (created_at);


--
-- Name: ix_inventory_notifications_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_notifications_id ON odoo_saas_retail_db.inventory_notifications USING btree (id);


--
-- Name: ix_inventory_notifications_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_notifications_tenant_id ON odoo_saas_retail_db.inventory_notifications USING btree (tenant_id);


--
-- Name: ix_inventory_rules_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_rules_id ON odoo_saas_retail_db.inventory_rules USING btree (id);


--
-- Name: ix_inventory_rules_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_inventory_rules_tenant_id ON odoo_saas_retail_db.inventory_rules USING btree (tenant_id);


--
-- Name: ix_landed_cost_assignments_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_landed_cost_assignments_id ON odoo_saas_retail_db.landed_cost_assignments USING btree (id);


--
-- Name: ix_landed_cost_assignments_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_landed_cost_assignments_tenant_id ON odoo_saas_retail_db.landed_cost_assignments USING btree (tenant_id);


--
-- Name: ix_landed_costs_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_landed_costs_id ON odoo_saas_retail_db.landed_costs USING btree (id);


--
-- Name: ix_landed_costs_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_landed_costs_tenant_id ON odoo_saas_retail_db.landed_costs USING btree (tenant_id);


--
-- Name: ix_order_fulfillments_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_fulfillments_id ON odoo_saas_retail_db.order_fulfillments USING btree (id);


--
-- Name: ix_order_fulfillments_order_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_fulfillments_order_id ON odoo_saas_retail_db.order_fulfillments USING btree (order_id);


--
-- Name: ix_order_fulfillments_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_fulfillments_tenant_id ON odoo_saas_retail_db.order_fulfillments USING btree (tenant_id);


--
-- Name: ix_order_fulfillments_tracking_number; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_fulfillments_tracking_number ON odoo_saas_retail_db.order_fulfillments USING btree (tracking_number);


--
-- Name: ix_order_returns_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_returns_id ON odoo_saas_retail_db.order_returns USING btree (id);


--
-- Name: ix_order_returns_order_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_returns_order_id ON odoo_saas_retail_db.order_returns USING btree (order_id);


--
-- Name: ix_order_returns_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_order_returns_tenant_id ON odoo_saas_retail_db.order_returns USING btree (tenant_id);


--
-- Name: ix_orders_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_orders_created_at ON odoo_saas_retail_db.orders USING btree (created_at);


--
-- Name: ix_orders_customer_mobile; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_orders_customer_mobile ON odoo_saas_retail_db.orders USING btree (customer_mobile);


--
-- Name: ix_orders_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_orders_id ON odoo_saas_retail_db.orders USING btree (id);


--
-- Name: ix_orders_invoice_number; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_orders_invoice_number ON odoo_saas_retail_db.orders USING btree (invoice_number);


--
-- Name: ix_orders_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_orders_sku ON odoo_saas_retail_db.orders USING btree (sku);


--
-- Name: ix_orders_status; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_orders_status ON odoo_saas_retail_db.orders USING btree (status);


--
-- Name: ix_orders_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_orders_tenant_id ON odoo_saas_retail_db.orders USING btree (tenant_id);


--
-- Name: ix_picking_batches_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_picking_batches_id ON odoo_saas_retail_db.picking_batches USING btree (id);


--
-- Name: ix_picking_batches_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_picking_batches_tenant_id ON odoo_saas_retail_db.picking_batches USING btree (tenant_id);


--
-- Name: ix_product_barcodes_barcode; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_product_barcodes_barcode ON odoo_saas_retail_db.product_barcodes USING btree (barcode);


--
-- Name: ix_product_barcodes_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_barcodes_id ON odoo_saas_retail_db.product_barcodes USING btree (id);


--
-- Name: ix_product_barcodes_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_barcodes_product_id ON odoo_saas_retail_db.product_barcodes USING btree (product_id);


--
-- Name: ix_product_barcodes_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_barcodes_tenant_id ON odoo_saas_retail_db.product_barcodes USING btree (tenant_id);


--
-- Name: ix_product_images_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_images_id ON odoo_saas_retail_db.product_images USING btree (id);


--
-- Name: ix_product_images_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_images_product_id ON odoo_saas_retail_db.product_images USING btree (product_id);


--
-- Name: ix_product_images_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_images_tenant_id ON odoo_saas_retail_db.product_images USING btree (tenant_id);


--
-- Name: ix_product_skus_amazon_asin; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_amazon_asin ON odoo_saas_retail_db.product_skus USING btree (amazon_asin);


--
-- Name: ix_product_skus_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_created_at ON odoo_saas_retail_db.product_skus USING btree (created_at);


--
-- Name: ix_product_skus_ebay_item_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_ebay_item_id ON odoo_saas_retail_db.product_skus USING btree (ebay_item_id);


--
-- Name: ix_product_skus_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_id ON odoo_saas_retail_db.product_skus USING btree (id);


--
-- Name: ix_product_skus_is_active; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_is_active ON odoo_saas_retail_db.product_skus USING btree (is_active);


--
-- Name: ix_product_skus_odoo_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_product_skus_odoo_product_id ON odoo_saas_retail_db.product_skus USING btree (odoo_product_id);


--
-- Name: ix_product_skus_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_product_id ON odoo_saas_retail_db.product_skus USING btree (product_id);


--
-- Name: ix_product_skus_product_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_product_name ON odoo_saas_retail_db.product_skus USING btree (product_name);


--
-- Name: ix_product_skus_shopify_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_shopify_product_id ON odoo_saas_retail_db.product_skus USING btree (shopify_product_id);


--
-- Name: ix_product_skus_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_product_skus_sku ON odoo_saas_retail_db.product_skus USING btree (sku);


--
-- Name: ix_product_skus_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_tenant_id ON odoo_saas_retail_db.product_skus USING btree (tenant_id);


--
-- Name: ix_product_skus_woocommerce_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_product_skus_woocommerce_product_id ON odoo_saas_retail_db.product_skus USING btree (woocommerce_product_id);


--
-- Name: ix_products_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_products_id ON odoo_saas_retail_db.products USING btree (id);


--
-- Name: ix_products_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_products_name ON odoo_saas_retail_db.products USING btree (name);


--
-- Name: ix_products_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_products_sku ON odoo_saas_retail_db.products USING btree (sku);


--
-- Name: ix_products_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_products_tenant_id ON odoo_saas_retail_db.products USING btree (tenant_id);


--
-- Name: ix_purchase_order_lines_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_purchase_order_lines_id ON odoo_saas_retail_db.purchase_order_lines USING btree (id);


--
-- Name: ix_purchase_order_lines_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_purchase_order_lines_tenant_id ON odoo_saas_retail_db.purchase_order_lines USING btree (tenant_id);


--
-- Name: ix_purchase_orders_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_purchase_orders_id ON odoo_saas_retail_db.purchase_orders USING btree (id);


--
-- Name: ix_purchase_orders_po_number; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_purchase_orders_po_number ON odoo_saas_retail_db.purchase_orders USING btree (po_number);


--
-- Name: ix_purchase_orders_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_purchase_orders_tenant_id ON odoo_saas_retail_db.purchase_orders USING btree (tenant_id);


--
-- Name: ix_refunds_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_refunds_id ON odoo_saas_retail_db.refunds USING btree (id);


--
-- Name: ix_refunds_order_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_refunds_order_id ON odoo_saas_retail_db.refunds USING btree (order_id);


--
-- Name: ix_refunds_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_refunds_tenant_id ON odoo_saas_retail_db.refunds USING btree (tenant_id);


--
-- Name: ix_reorder_suggestions_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_reorder_suggestions_created_at ON odoo_saas_retail_db.reorder_suggestions USING btree (created_at);


--
-- Name: ix_reorder_suggestions_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_reorder_suggestions_id ON odoo_saas_retail_db.reorder_suggestions USING btree (id);


--
-- Name: ix_reorder_suggestions_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_reorder_suggestions_product_id ON odoo_saas_retail_db.reorder_suggestions USING btree (product_id);


--
-- Name: ix_reorder_suggestions_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_reorder_suggestions_tenant_id ON odoo_saas_retail_db.reorder_suggestions USING btree (tenant_id);


--
-- Name: ix_sku_alert_rules_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_alert_rules_id ON odoo_saas_retail_db.sku_alert_rules USING btree (id);


--
-- Name: ix_sku_alert_rules_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_alert_rules_sku ON odoo_saas_retail_db.sku_alert_rules USING btree (sku);


--
-- Name: ix_sku_alert_rules_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_alert_rules_tenant_id ON odoo_saas_retail_db.sku_alert_rules USING btree (tenant_id);


--
-- Name: ix_sku_barcodes_barcode; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_sku_barcodes_barcode ON odoo_saas_retail_db.sku_barcodes USING btree (barcode);


--
-- Name: ix_sku_barcodes_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_barcodes_id ON odoo_saas_retail_db.sku_barcodes USING btree (id);


--
-- Name: ix_sku_barcodes_is_primary; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_barcodes_is_primary ON odoo_saas_retail_db.sku_barcodes USING btree (is_primary);


--
-- Name: ix_sku_barcodes_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_barcodes_sku ON odoo_saas_retail_db.sku_barcodes USING btree (sku);


--
-- Name: ix_sku_barcodes_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_barcodes_tenant_id ON odoo_saas_retail_db.sku_barcodes USING btree (tenant_id);


--
-- Name: ix_sku_inventory_mappings_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_inventory_mappings_id ON odoo_saas_retail_db.sku_inventory_mappings USING btree (id);


--
-- Name: ix_sku_inventory_mappings_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_inventory_mappings_sku ON odoo_saas_retail_db.sku_inventory_mappings USING btree (sku);


--
-- Name: ix_sku_inventory_mappings_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_inventory_mappings_tenant_id ON odoo_saas_retail_db.sku_inventory_mappings USING btree (tenant_id);


--
-- Name: ix_sku_movement_logs_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_movement_logs_created_at ON odoo_saas_retail_db.sku_movement_logs USING btree (created_at);


--
-- Name: ix_sku_movement_logs_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_movement_logs_id ON odoo_saas_retail_db.sku_movement_logs USING btree (id);


--
-- Name: ix_sku_movement_logs_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_movement_logs_sku ON odoo_saas_retail_db.sku_movement_logs USING btree (sku);


--
-- Name: ix_sku_movement_logs_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_movement_logs_tenant_id ON odoo_saas_retail_db.sku_movement_logs USING btree (tenant_id);


--
-- Name: ix_sku_platform_mappings_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_platform_mappings_id ON odoo_saas_retail_db.sku_platform_mappings USING btree (id);


--
-- Name: ix_sku_platform_mappings_platform_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_platform_mappings_platform_name ON odoo_saas_retail_db.sku_platform_mappings USING btree (platform_name);


--
-- Name: ix_sku_platform_mappings_platform_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_platform_mappings_platform_product_id ON odoo_saas_retail_db.sku_platform_mappings USING btree (platform_product_id);


--
-- Name: ix_sku_platform_mappings_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_platform_mappings_sku ON odoo_saas_retail_db.sku_platform_mappings USING btree (sku);


--
-- Name: ix_sku_platform_mappings_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_sku_platform_mappings_tenant_id ON odoo_saas_retail_db.sku_platform_mappings USING btree (tenant_id);


--
-- Name: ix_stock_alerts_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_alerts_created_at ON odoo_saas_retail_db.stock_alerts USING btree (created_at);


--
-- Name: ix_stock_alerts_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_alerts_id ON odoo_saas_retail_db.stock_alerts USING btree (id);


--
-- Name: ix_stock_alerts_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_alerts_product_id ON odoo_saas_retail_db.stock_alerts USING btree (product_id);


--
-- Name: ix_stock_alerts_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_alerts_tenant_id ON odoo_saas_retail_db.stock_alerts USING btree (tenant_id);


--
-- Name: ix_stock_locations_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_locations_id ON odoo_saas_retail_db.stock_locations USING btree (id);


--
-- Name: ix_stock_locations_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_locations_name ON odoo_saas_retail_db.stock_locations USING btree (name);


--
-- Name: ix_stock_locations_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_locations_product_id ON odoo_saas_retail_db.stock_locations USING btree (product_id);


--
-- Name: ix_stock_locations_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_locations_tenant_id ON odoo_saas_retail_db.stock_locations USING btree (tenant_id);


--
-- Name: ix_stock_movements_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_movements_created_at ON odoo_saas_retail_db.stock_movements USING btree (created_at);


--
-- Name: ix_stock_movements_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_movements_id ON odoo_saas_retail_db.stock_movements USING btree (id);


--
-- Name: ix_stock_movements_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_movements_product_id ON odoo_saas_retail_db.stock_movements USING btree (product_id);


--
-- Name: ix_stock_movements_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_movements_tenant_id ON odoo_saas_retail_db.stock_movements USING btree (tenant_id);


--
-- Name: ix_stock_transfers_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_transfers_id ON odoo_saas_retail_db.stock_transfers USING btree (id);


--
-- Name: ix_stock_transfers_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_transfers_product_id ON odoo_saas_retail_db.stock_transfers USING btree (product_id);


--
-- Name: ix_stock_transfers_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_transfers_tenant_id ON odoo_saas_retail_db.stock_transfers USING btree (tenant_id);


--
-- Name: ix_stock_valuation_layers_created_at; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_created_at ON odoo_saas_retail_db.stock_valuation_layers USING btree (created_at);


--
-- Name: ix_stock_valuation_layers_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_id ON odoo_saas_retail_db.stock_valuation_layers USING btree (id);


--
-- Name: ix_stock_valuation_layers_is_fully_consumed; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_is_fully_consumed ON odoo_saas_retail_db.stock_valuation_layers USING btree (is_fully_consumed);


--
-- Name: ix_stock_valuation_layers_product_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_product_id ON odoo_saas_retail_db.stock_valuation_layers USING btree (product_id);


--
-- Name: ix_stock_valuation_layers_reference_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_reference_id ON odoo_saas_retail_db.stock_valuation_layers USING btree (reference_id);


--
-- Name: ix_stock_valuation_layers_sku; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_sku ON odoo_saas_retail_db.stock_valuation_layers USING btree (sku);


--
-- Name: ix_stock_valuation_layers_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_stock_valuation_layers_tenant_id ON odoo_saas_retail_db.stock_valuation_layers USING btree (tenant_id);


--
-- Name: ix_supplier_performance_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_supplier_performance_id ON odoo_saas_retail_db.supplier_performance USING btree (id);


--
-- Name: ix_supplier_performance_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_supplier_performance_tenant_id ON odoo_saas_retail_db.supplier_performance USING btree (tenant_id);


--
-- Name: ix_suppliers_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_suppliers_id ON odoo_saas_retail_db.suppliers USING btree (id);


--
-- Name: ix_suppliers_supplier_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_suppliers_supplier_name ON odoo_saas_retail_db.suppliers USING btree (supplier_name);


--
-- Name: ix_suppliers_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_suppliers_tenant_id ON odoo_saas_retail_db.suppliers USING btree (tenant_id);


--
-- Name: ix_tenants_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_tenants_id ON odoo_saas_retail_db.tenants USING btree (id);


--
-- Name: ix_tenants_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_tenants_tenant_id ON odoo_saas_retail_db.tenants USING btree (tenant_id);


--
-- Name: ix_tenants_whatsapp_number; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_tenants_whatsapp_number ON odoo_saas_retail_db.tenants USING btree (whatsapp_number);


--
-- Name: ix_units_abbreviation; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_units_abbreviation ON odoo_saas_retail_db.units USING btree (abbreviation);


--
-- Name: ix_units_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_units_id ON odoo_saas_retail_db.units USING btree (id);


--
-- Name: ix_units_name; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_units_name ON odoo_saas_retail_db.units USING btree (name);


--
-- Name: ix_units_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_units_tenant_id ON odoo_saas_retail_db.units USING btree (tenant_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON odoo_saas_retail_db.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_users_id ON odoo_saas_retail_db.users USING btree (id);


--
-- Name: ix_warehouses_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_warehouses_id ON odoo_saas_retail_db.warehouses USING btree (id);


--
-- Name: ix_warehouses_tenant_id; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE INDEX ix_warehouses_tenant_id ON odoo_saas_retail_db.warehouses USING btree (tenant_id);


--
-- Name: ix_warehouses_warehouse_code; Type: INDEX; Schema: odoo_saas_retail_db; Owner: postgres
--

CREATE UNIQUE INDEX ix_warehouses_warehouse_code ON odoo_saas_retail_db.warehouses USING btree (warehouse_code);


--
-- Name: attribute_values attribute_values_attribute_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.attribute_values
    ADD CONSTRAINT attribute_values_attribute_id_fkey FOREIGN KEY (attribute_id) REFERENCES odoo_saas_retail_db.attributes(id);


--
-- Name: attributes attributes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.attributes
    ADD CONSTRAINT attributes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: automation_workflows automation_workflows_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.automation_workflows
    ADD CONSTRAINT automation_workflows_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: backorder_alerts backorder_alerts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.backorder_alerts
    ADD CONSTRAINT backorder_alerts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: brands brands_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.brands
    ADD CONSTRAINT brands_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES odoo_saas_retail_db.categories(id);


--
-- Name: collections collections_season_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.collections
    ADD CONSTRAINT collections_season_id_fkey FOREIGN KEY (season_id) REFERENCES odoo_saas_retail_db.seasons(id);


--
-- Name: conversation_states conversation_states_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.conversation_states
    ADD CONSTRAINT conversation_states_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: count_lines count_lines_count_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.count_lines
    ADD CONSTRAINT count_lines_count_id_fkey FOREIGN KEY (count_id) REFERENCES odoo_saas_retail_db.inventory_counts(id);


--
-- Name: coupons coupons_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.coupons
    ADD CONSTRAINT coupons_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: customers customers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.customers
    ADD CONSTRAINT customers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: demand_forecasts demand_forecasts_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.demand_forecasts
    ADD CONSTRAINT demand_forecasts_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: demand_forecasts demand_forecasts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.demand_forecasts
    ADD CONSTRAINT demand_forecasts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: fulfillments fulfillments_order_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.fulfillments
    ADD CONSTRAINT fulfillments_order_id_fkey FOREIGN KEY (order_id) REFERENCES odoo_saas_retail_db.orders(id);


--
-- Name: fulfillments fulfillments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.fulfillments
    ADD CONSTRAINT fulfillments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: inventory_audit_logs inventory_audit_logs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_audit_logs
    ADD CONSTRAINT inventory_audit_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: inventory_counts inventory_counts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_counts
    ADD CONSTRAINT inventory_counts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: inventory_notifications inventory_notifications_alert_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_notifications
    ADD CONSTRAINT inventory_notifications_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES odoo_saas_retail_db.stock_alerts(id);


--
-- Name: inventory_notifications inventory_notifications_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_notifications
    ADD CONSTRAINT inventory_notifications_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: inventory_rules inventory_rules_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.inventory_rules
    ADD CONSTRAINT inventory_rules_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: landed_cost_assignments landed_cost_assignments_landed_cost_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_cost_assignments
    ADD CONSTRAINT landed_cost_assignments_landed_cost_id_fkey FOREIGN KEY (landed_cost_id) REFERENCES odoo_saas_retail_db.landed_costs(id);


--
-- Name: landed_cost_assignments landed_cost_assignments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_cost_assignments
    ADD CONSTRAINT landed_cost_assignments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: landed_cost_assignments landed_cost_assignments_valuation_layer_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_cost_assignments
    ADD CONSTRAINT landed_cost_assignments_valuation_layer_id_fkey FOREIGN KEY (valuation_layer_id) REFERENCES odoo_saas_retail_db.stock_valuation_layers(id);


--
-- Name: landed_costs landed_costs_purchase_order_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_costs
    ADD CONSTRAINT landed_costs_purchase_order_id_fkey FOREIGN KEY (purchase_order_id) REFERENCES odoo_saas_retail_db.purchase_orders(id);


--
-- Name: landed_costs landed_costs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.landed_costs
    ADD CONSTRAINT landed_costs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: order_fulfillments order_fulfillments_batch_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_fulfillments
    ADD CONSTRAINT order_fulfillments_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES odoo_saas_retail_db.picking_batches(id);


--
-- Name: order_fulfillments order_fulfillments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_fulfillments
    ADD CONSTRAINT order_fulfillments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: order_returns order_returns_order_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_returns
    ADD CONSTRAINT order_returns_order_id_fkey FOREIGN KEY (order_id) REFERENCES odoo_saas_retail_db.orders(id);


--
-- Name: order_returns order_returns_refund_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_returns
    ADD CONSTRAINT order_returns_refund_id_fkey FOREIGN KEY (refund_id) REFERENCES odoo_saas_retail_db.refunds(id);


--
-- Name: order_returns order_returns_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.order_returns
    ADD CONSTRAINT order_returns_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES odoo_saas_retail_db.customers(id);


--
-- Name: orders orders_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.orders
    ADD CONSTRAINT orders_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: picking_batches picking_batches_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.picking_batches
    ADD CONSTRAINT picking_batches_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: picking_batches picking_batches_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.picking_batches
    ADD CONSTRAINT picking_batches_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES odoo_saas_retail_db.warehouses(id);


--
-- Name: product_barcodes product_barcodes_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_barcodes
    ADD CONSTRAINT product_barcodes_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: product_barcodes product_barcodes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_barcodes
    ADD CONSTRAINT product_barcodes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: product_images product_images_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_images
    ADD CONSTRAINT product_images_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: product_images product_images_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_images
    ADD CONSTRAINT product_images_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: product_skus product_skus_brand_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES odoo_saas_retail_db.brands(id);


--
-- Name: product_skus product_skus_category_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_category_id_fkey FOREIGN KEY (category_id) REFERENCES odoo_saas_retail_db.categories(id);


--
-- Name: product_skus product_skus_collection_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES odoo_saas_retail_db.collections(id);


--
-- Name: product_skus product_skus_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: product_skus product_skus_season_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_season_id_fkey FOREIGN KEY (season_id) REFERENCES odoo_saas_retail_db.seasons(id);


--
-- Name: product_skus product_skus_unit_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.product_skus
    ADD CONSTRAINT product_skus_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES odoo_saas_retail_db.units(id);


--
-- Name: products products_brand_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES odoo_saas_retail_db.brands(id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES odoo_saas_retail_db.categories(id);


--
-- Name: products products_collection_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES odoo_saas_retail_db.collections(id);


--
-- Name: products products_season_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_season_id_fkey FOREIGN KEY (season_id) REFERENCES odoo_saas_retail_db.seasons(id);


--
-- Name: products products_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: products products_unit_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.products
    ADD CONSTRAINT products_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES odoo_saas_retail_db.units(id);


--
-- Name: purchase_order_lines purchase_order_lines_po_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_order_lines
    ADD CONSTRAINT purchase_order_lines_po_id_fkey FOREIGN KEY (po_id) REFERENCES odoo_saas_retail_db.purchase_orders(id);


--
-- Name: purchase_order_lines purchase_order_lines_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_order_lines
    ADD CONSTRAINT purchase_order_lines_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: purchase_orders purchase_orders_supplier_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_orders
    ADD CONSTRAINT purchase_orders_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES odoo_saas_retail_db.suppliers(id);


--
-- Name: purchase_orders purchase_orders_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.purchase_orders
    ADD CONSTRAINT purchase_orders_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: refunds refunds_order_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.refunds
    ADD CONSTRAINT refunds_order_id_fkey FOREIGN KEY (order_id) REFERENCES odoo_saas_retail_db.orders(id);


--
-- Name: refunds refunds_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.refunds
    ADD CONSTRAINT refunds_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: reorder_suggestions reorder_suggestions_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.reorder_suggestions
    ADD CONSTRAINT reorder_suggestions_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: reorder_suggestions reorder_suggestions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.reorder_suggestions
    ADD CONSTRAINT reorder_suggestions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: shifts shifts_user_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.shifts
    ADD CONSTRAINT shifts_user_id_fkey FOREIGN KEY (user_id) REFERENCES odoo_saas_retail_db.users(id);


--
-- Name: sku_alert_rules sku_alert_rules_sku_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_alert_rules
    ADD CONSTRAINT sku_alert_rules_sku_fkey FOREIGN KEY (sku) REFERENCES odoo_saas_retail_db.product_skus(sku);


--
-- Name: sku_attribute_values sku_attribute_values_sku_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_attribute_values
    ADD CONSTRAINT sku_attribute_values_sku_id_fkey FOREIGN KEY (sku_id) REFERENCES odoo_saas_retail_db.product_skus(id);


--
-- Name: sku_attribute_values sku_attribute_values_value_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_attribute_values
    ADD CONSTRAINT sku_attribute_values_value_id_fkey FOREIGN KEY (value_id) REFERENCES odoo_saas_retail_db.attribute_values(id);


--
-- Name: sku_barcodes sku_barcodes_sku_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_barcodes
    ADD CONSTRAINT sku_barcodes_sku_fkey FOREIGN KEY (sku) REFERENCES odoo_saas_retail_db.product_skus(sku);


--
-- Name: sku_inventory_mappings sku_inventory_mappings_sku_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_inventory_mappings
    ADD CONSTRAINT sku_inventory_mappings_sku_fkey FOREIGN KEY (sku) REFERENCES odoo_saas_retail_db.product_skus(sku);


--
-- Name: sku_movement_logs sku_movement_logs_sku_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_movement_logs
    ADD CONSTRAINT sku_movement_logs_sku_fkey FOREIGN KEY (sku) REFERENCES odoo_saas_retail_db.product_skus(sku);


--
-- Name: sku_platform_mappings sku_platform_mappings_sku_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.sku_platform_mappings
    ADD CONSTRAINT sku_platform_mappings_sku_fkey FOREIGN KEY (sku) REFERENCES odoo_saas_retail_db.product_skus(sku);


--
-- Name: stock_alerts stock_alerts_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_alerts
    ADD CONSTRAINT stock_alerts_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: stock_alerts stock_alerts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_alerts
    ADD CONSTRAINT stock_alerts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: stock_locations stock_locations_parent_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_locations
    ADD CONSTRAINT stock_locations_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES odoo_saas_retail_db.stock_locations(id);


--
-- Name: stock_locations stock_locations_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_locations
    ADD CONSTRAINT stock_locations_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: stock_locations stock_locations_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_locations
    ADD CONSTRAINT stock_locations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: stock_locations stock_locations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_locations
    ADD CONSTRAINT stock_locations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES odoo_saas_retail_db.warehouses(id);


--
-- Name: stock_movements stock_movements_location_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_movements
    ADD CONSTRAINT stock_movements_location_id_fkey FOREIGN KEY (location_id) REFERENCES odoo_saas_retail_db.stock_locations(id);


--
-- Name: stock_movements stock_movements_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_movements
    ADD CONSTRAINT stock_movements_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: stock_movements stock_movements_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_movements
    ADD CONSTRAINT stock_movements_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: stock_transfers stock_transfers_from_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_transfers
    ADD CONSTRAINT stock_transfers_from_warehouse_id_fkey FOREIGN KEY (from_warehouse_id) REFERENCES odoo_saas_retail_db.warehouses(id);


--
-- Name: stock_transfers stock_transfers_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_transfers
    ADD CONSTRAINT stock_transfers_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: stock_transfers stock_transfers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_transfers
    ADD CONSTRAINT stock_transfers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: stock_transfers stock_transfers_to_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_transfers
    ADD CONSTRAINT stock_transfers_to_warehouse_id_fkey FOREIGN KEY (to_warehouse_id) REFERENCES odoo_saas_retail_db.warehouses(id);


--
-- Name: stock_valuation_layers stock_valuation_layers_product_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_valuation_layers
    ADD CONSTRAINT stock_valuation_layers_product_id_fkey FOREIGN KEY (product_id) REFERENCES odoo_saas_retail_db.products(id);


--
-- Name: stock_valuation_layers stock_valuation_layers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.stock_valuation_layers
    ADD CONSTRAINT stock_valuation_layers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: supplier_performance supplier_performance_supplier_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.supplier_performance
    ADD CONSTRAINT supplier_performance_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES odoo_saas_retail_db.suppliers(id);


--
-- Name: supplier_performance supplier_performance_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.supplier_performance
    ADD CONSTRAINT supplier_performance_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: suppliers suppliers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.suppliers
    ADD CONSTRAINT suppliers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: units units_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.units
    ADD CONSTRAINT units_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- Name: warehouses warehouses_tenant_id_fkey; Type: FK CONSTRAINT; Schema: odoo_saas_retail_db; Owner: postgres
--

ALTER TABLE ONLY odoo_saas_retail_db.warehouses
    ADD CONSTRAINT warehouses_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES odoo_saas_retail_db.tenants(tenant_id);


--
-- PostgreSQL database dump complete
--

\unrestrict IQ00ycDPvpXsNZn7H5pVTTFvnlNIS2OViYgKOflk55z1RnozDhMaEaIkGmmelbw

