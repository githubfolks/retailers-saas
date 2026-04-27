from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc
from datetime import datetime
from app.models.inventory import StockLocation, StockMovement, Warehouse
from app.models.valuation import StockValuationLayer
from app.models.procurement import PurchaseOrderLine
from app.core.logger import request_logger

class InventoryService:
    """Core inventory and valuation logic"""
    
    @staticmethod
    def create_warehouse(db: Session, tenant_id: str, name: str, code: str, 
                         address: str, capacity: float):
        """
        Creates a new warehouse and automatically initializes a 'Default' internal location.
        """
        warehouse = Warehouse(
            tenant_id=tenant_id,
            warehouse_name=name,
            warehouse_code=code,
            location_address=address,
            capacity=capacity
        )
        db.add(warehouse)
        db.flush() # Get warehouse ID
        
        # Create Default Internal Location
        default_loc = StockLocation(
            tenant_id=tenant_id,
            warehouse_id=warehouse.id,
            name="Default Storage",
            location_type="internal",
            is_active=True
        )
        db.add(default_loc)
        db.commit()
        return warehouse

    @staticmethod
    def get_warehouses(db: Session, tenant_id: str):
        return db.query(Warehouse).filter(Warehouse.tenant_id == tenant_id).all()

    @staticmethod
    def create_location(db: Session, tenant_id: str, warehouse_id: int, 
                        name: str, parent_id: Optional[int] = None, 
                        location_type: str = "internal"):
        location = StockLocation(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            name=name,
            parent_id=parent_id,
            location_type=location_type
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def get_valuation_ledger(db: Session, tenant_id: str, product_id: Optional[int] = None):
        """
        Returns a detailed ledger of valuation layers for reporting.
        """
        query = db.query(StockValuationLayer).filter(StockValuationLayer.tenant_id == tenant_id)
        if product_id:
            query = query.filter(StockValuationLayer.product_id == product_id)
        return query.order_by(asc(StockValuationLayer.created_at)).all()

    @staticmethod
    def process_receipt(db: Session, tenant_id: str, product_id: int, sku: str, 
                        quantity: float, unit_cost: float, reference_id: str):
        """
        Processes incoming stock and creates a new FIFO valuation layer.
        """
        # 1. Create Valuation Layer
        layer = StockValuationLayer(
            tenant_id=tenant_id,
            product_id=product_id,
            sku=sku,
            original_quantity=quantity,
            remaining_quantity=quantity,
            unit_cost=unit_cost,
            total_value=quantity * unit_cost,
            reference_id=reference_id,
            reference_type="purchase_order"
        )
        db.add(layer)
        
        # 2. Update Stock Location (Default to primary location)
        location = db.query(StockLocation).filter(
            StockLocation.tenant_id == tenant_id,
            StockLocation.product_id == product_id,
            StockLocation.location_type == "internal"
        ).first()
        
        if not location:
            # Create a default location if none exists
            location = StockLocation(
                tenant_id=tenant_id,
                product_id=product_id,
                name="Main Internal",
                location_type="internal",
                quantity=0
            )
            db.add(location)
            db.flush()
            
        location.quantity += quantity
        location.available_quantity += quantity
        
        # 3. Log Movement
        movement = StockMovement(
            tenant_id=tenant_id,
            product_id=product_id,
            location_id=location.id,
            movement_type="in",
            quantity=quantity,
            reference_id=reference_id,
            reference_type="purchase_order",
            reason="purchase"
        )
        db.add(movement)
        
        db.commit()
        return layer

    @staticmethod
    def consume_stock(db: Session, tenant_id: str, product_id: int, 
                      quantity: float, reference_id: str):
        """
        Consumes stock using FIFO (First-In-First-Out).
        Returns a list of valuation details consumed.
        """
        # 1. Get available layers in FIFO order
        layers = db.query(StockValuationLayer).filter(
            StockValuationLayer.tenant_id == tenant_id,
            StockValuationLayer.product_id == product_id,
            StockValuationLayer.is_fully_consumed == False,
            StockValuationLayer.remaining_quantity > 0
        ).order_by(asc(StockValuationLayer.created_at)).all()
        
        remaining_to_consume = quantity
        consumption_details = []
        
        for layer in layers:
            if remaining_to_consume <= 0:
                break
                
            can_consume = min(layer.remaining_quantity, remaining_to_consume)
            
            layer.remaining_quantity -= can_consume
            if layer.remaining_quantity <= 0:
                layer.is_fully_consumed = True
                
            remaining_to_consume -= can_consume
            consumption_details.append({
                "layer_id": layer.id,
                "qty": can_consume,
                "unit_cost": layer.unit_cost,
                "total_cost": can_consume * layer.unit_cost
            })
            
        if remaining_to_consume > 0:
            request_logger.warning(f"Stock deficit for product {product_id}: requested {quantity}, missing {remaining_to_consume}")
            # Optional: Allow negative stock or raise error
            
        # 2. Update Stock Location
        location = db.query(StockLocation).filter(
            StockLocation.tenant_id == tenant_id,
            StockLocation.product_id == product_id,
            StockLocation.location_type == "internal"
        ).first()
        
        if location:
            location.quantity -= quantity
            location.available_quantity -= (quantity - remaining_to_consume)
            
            # 2b. Check for Low Stock Alert
            if location.available_quantity <= location.reorder_point:
                from app.services.whatsapp_bot_service import WhatsAppBotService
                from app.models.tenant import Tenant
                tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
                if tenant and tenant.owner_phone:
                    import asyncio
                    asyncio.create_task(WhatsAppBotService.send_stock_alert(
                        tenant, tenant.owner_phone, f"PROD-{product_id}", location.available_quantity
                    ))
            
        # 3. Log Movement
        movement = StockMovement(
            tenant_id=tenant_id,
            product_id=product_id,
            location_id=location.id if location else None,
            movement_type="out",
            quantity=-quantity,
            reference_id=reference_id,
            reference_type="order",
            reason="sale"
        )
        db.add(movement)
        
        db.commit()
        return consumption_details

    @staticmethod
    def allocate_landed_costs(db: Session, tenant_id: str, landed_cost_id: int, 
                               layer_ids: List[int], total_amount: float, method: str = "equal"):
        """
        Allocates landed costs to specific valuation layers.
        """
        from app.models.valuation import LandedCost, LandedCostAssignment, StockValuationLayer
        
        layers = db.query(StockValuationLayer).filter(
            StockValuationLayer.id.in_(layer_ids)
        ).all()
        
        if not layers:
            return []
            
        assignments = []
        if method == "equal":
            amount_per_layer = total_amount / len(layers)
            for layer in layers:
                assignment = LandedCostAssignment(
                    tenant_id=tenant_id,
                    landed_cost_id=landed_cost_id,
                    valuation_layer_id=layer.id,
                    allocated_amount=amount_per_layer,
                    allocation_method="equal"
                )
                layer.landed_cost_value += amount_per_layer
                layer.unit_cost += (amount_per_layer / layer.original_quantity) # Increase base cost
                db.add(assignment)
                assignments.append(assignment)
                
        elif method == "value":
            total_valuation = sum(layer.total_value for layer in layers)
            for layer in layers:
                pct = layer.total_value / total_valuation if total_valuation > 0 else 0
                allocated = total_amount * pct
                assignment = LandedCostAssignment(
                    tenant_id=tenant_id,
                    landed_cost_id=landed_cost_id,
                    valuation_layer_id=layer.id,
                    allocated_amount=allocated,
                    allocation_method="value"
                )
                layer.landed_cost_value += allocated
                layer.unit_cost += (allocated / layer.original_quantity)
                db.add(assignment)
                assignments.append(assignment)
                
        db.commit()
        return assignments

    @staticmethod
    def move_stock(db: Session, tenant_id: str, product_id: int, 
                   from_location_id: int, to_location_id: int, quantity: float, 
                   operator_id: str):
        """
        Moves stock between two internal locations.
        Does not change valuation layers, only physical tracking.
        """
        from_loc = db.query(StockLocation).filter(
            StockLocation.id == from_location_id,
            StockLocation.tenant_id == tenant_id
        ).first()
        
        to_loc = db.query(StockLocation).filter(
            StockLocation.id == to_location_id,
            StockLocation.tenant_id == tenant_id
        ).first()
        
        if not from_loc or not to_loc:
            raise ValueError("Invalid source or destination location")
            
        if from_loc.quantity < quantity:
            raise ValueError(f"Insufficient stock in source location: {from_loc.name}")
            
        # 1. Update quantities
        from_loc.quantity -= quantity
        from_loc.available_quantity -= quantity
        
        to_loc.quantity += quantity
        to_loc.available_quantity += quantity
        
        # 2. Log Transfer Movement
        # Out from source
        mov_out = StockMovement(
            tenant_id=tenant_id,
            product_id=product_id,
            location_id=from_location_id,
            movement_type="transfer",
            quantity=-quantity,
            reason="internal_transfer",
            created_by=operator_id
        )
        db.add(mov_out)
        
        # In to destination
        mov_in = StockMovement(
            tenant_id=tenant_id,
            product_id=product_id,
            location_id=to_location_id,
            movement_type="transfer",
            quantity=quantity,
            reason="internal_transfer",
            created_by=operator_id
        )
        db.add(mov_in)
        
        db.commit()
        return True

    @staticmethod
    def create_picking_batch(db: Session, tenant_id: str, warehouse_id: int, 
                             order_ids: List[int], batch_name: str):
        """
        Groups multiple fulfillments into a single picking batch.
        """
        from app.models.procurement import PickingBatch, OrderFulfillment
        
        batch = PickingBatch(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            batch_name=batch_name,
            status="draft"
        )
        db.add(batch)
        db.flush()
        
        # Update fulfillments to link to this batch
        fulfillments = db.query(OrderFulfillment).filter(
            OrderFulfillment.tenant_id == tenant_id,
            OrderFulfillment.order_id.in_(order_ids)
        ).all()
        
        for f in fulfillments:
            f.batch_id = batch.id
            f.fulfillment_status = "picking"
            
        db.commit()
        return batch
