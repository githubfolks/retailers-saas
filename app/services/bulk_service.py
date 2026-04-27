import csv
import io
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.sku import ProductSKU
from app.models.category import Category
from app.models.image import ProductImage
from app.models.brand import Brand
from app.models.season import Season, Collection
from app.models.attribute import Attribute, AttributeValue
from app.core.logger import get_logger

logger = get_logger(__name__)

class BulkUploadService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def get_template(self, format: str = "csv") -> io.BytesIO:
        """Generate a sample template for bulk upload."""
        headers = [
            "name", "description", "price", "sku", "quantity", 
            "category", "brand", "size", "color", "cost_price", 
            "selling_price", "image_urls"
        ]
        sample_data = [
            {
                "name": "Classic Cotton T-Shirt",
                "description": "100% Organic Cotton",
                "price": 29.99,
                "sku": "TSH-COT-RED-L",
                "quantity": 100,
                "category": "Apparel > Men > T-Shirts",
                "brand": "Acme Wear",
                "size": "L",
                "color": "Red",
                "cost_price": 10.00,
                "selling_price": 29.99,
                "image_urls": "https://example.com/img1.jpg, https://example.com/img2.jpg"
            }
        ]
        
        output = io.BytesIO()
        df = pd.DataFrame(sample_data, columns=headers)
        
        # Add season and collection headers
        headers.extend(["season", "collection"])
        
        if format.lower() == "xlsx":
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Template")
        else:
            df.to_csv(output, index=False)
            
        output.seek(0)
        return output

    def _get_or_create_category(self, category_path: str) -> Optional[int]:
        """Parse 'Parent > Child' and return the leaf category ID."""
        if not category_path or pd.isna(category_path):
            return None
            
        parts = [p.strip() for p in str(category_path).split('>') if p.strip()]
        parent_id = None
        
        for part in parts:
            cat = self.db.query(Category).filter(
                Category.tenant_id == self.tenant_id,
                Category.name == part,
                Category.parent_id == parent_id
            ).first()
            
            if not cat:
                cat = Category(tenant_id=self.tenant_id, name=part, parent_id=parent_id)
                self.db.add(cat)
                self.db.flush()
            
            parent_id = cat.id
            
        return parent_id

    def _get_or_create_brand(self, brand_name: str) -> Optional[int]:
        """Get or create brand by name."""
        if not brand_name or pd.isna(brand_name):
            return None
            
        brand = self.db.query(Brand).filter(
            Brand.tenant_id == self.tenant_id,
            Brand.name == str(brand_name).strip()
        ).first()
        
        if not brand:
            brand = Brand(tenant_id=self.tenant_id, name=str(brand_name).strip())
            self.db.add(brand)
            self.db.flush()
            
        return brand.id

        return brand.id

    def _get_or_create_season(self, season_name: str) -> Optional[int]:
        """Get or create season."""
        if not season_name or pd.isna(season_name):
            return None
            
        season = self.db.query(Season).filter(
            Season.tenant_id == self.tenant_id,
            Season.name == str(season_name).strip()
        ).first()
        
        if not season:
            season = Season(tenant_id=self.tenant_id, name=str(season_name).strip())
            self.db.add(season)
            self.db.flush()
            
        return season.id

    def _get_or_create_collection(self, collection_name: str, season_id: Optional[int]) -> Optional[int]:
        """Get or create collection."""
        if not collection_name or pd.isna(collection_name):
            return None
            
        coll = self.db.query(Collection).filter(
            Collection.tenant_id == self.tenant_id,
            Collection.name == str(collection_name).strip(),
            Collection.season_id == season_id
        ).first()
        
        if not coll:
            coll = Collection(tenant_id=self.tenant_id, name=str(collection_name).strip(), season_id=season_id)
            self.db.add(coll)
            self.db.flush()
            
        return coll.id

    def _get_or_create_attr_value(self, attr_name: str, value_name: str) -> Optional[AttributeValue]:
        """Get or create attribute (e.g. Size) and its value (e.g. XL)."""
        if not value_name or pd.isna(value_name):
            return None
            
        # 1. Ensure Attribute exists
        attr = self.db.query(Attribute).filter(
            Attribute.tenant_id == self.tenant_id,
            Attribute.name == attr_name
        ).first()
        
        if not attr:
            attr = Attribute(tenant_id=self.tenant_id, name=attr_name)
            self.db.add(attr)
            self.db.flush()
            
        # 2. Ensure Value exists
        val = self.db.query(AttributeValue).filter(
            AttributeValue.attribute_id == attr.id,
            AttributeValue.value == str(value_name)
        ).first()
        
        if not val:
            val = AttributeValue(attribute_id=attr.id, value=str(value_name))
            self.db.add(val)
            self.db.flush()
            
        return val

    def process_bulk_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Unified entry point for CSV and Excel processing."""
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                return {"status": "error", "message": "Unsupported file format. Use .csv or .xlsx"}
            
            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Failed to read file {filename}: {str(e)}")
            return {"status": "error", "message": f"Could not read file: {str(e)}"}

    def _process_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """The core logic to process the data rows."""
        success_count = 0
        error_count = 0
        errors = []
        seen_skus = set()
        
        # Normalize column names
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        
        for idx, row in df.iterrows():
            row_num = idx + 2 # Header is row 1
            try:
                sku = str(row.get('sku', '')).strip()
                if not sku or sku == 'nan':
                    raise ValueError("SKU is required")
                
                if sku in seen_skus:
                    raise ValueError(f"Duplicate SKU '{sku}' found within the file")
                seen_skus.add(sku)

                name = str(row.get('name', 'Unnamed Product')).strip()
                price = float(row.get('price', 0.0))
                qty = int(row.get('quantity', 0))
                
                # 1. Category, Brand, Season, Collection
                cat_id = self._get_or_create_category(row.get('category'))
                brand_id = self._get_or_create_brand(row.get('brand'))
                season_id = self._get_or_create_season(row.get('season'))
                collection_id = self._get_or_create_collection(row.get('collection'), season_id)
                
                # 2. Upsert Product Template
                db_product = self.db.query(Product).filter(
                    Product.tenant_id == self.tenant_id,
                    Product.sku == sku
                ).first()
                
                if not db_product:
                    db_product = Product(
                        tenant_id=self.tenant_id,
                        sku=sku,
                        name=name,
                        description=str(row.get('description', '')),
                        price=price,
                        quantity=qty,
                        category_id=cat_id,
                        brand_id=brand_id,
                        season_id=season_id,
                        collection_id=collection_id
                    )
                    self.db.add(db_product)
                else:
                    db_product.name = name
                    db_product.price = price
                    db_product.quantity = qty
                    db_product.category_id = cat_id
                    db_product.brand_id = brand_id
                    db_product.season_id = season_id
                    db_product.collection_id = collection_id
                
                self.db.flush()

                # 3. Handle Images
                img_str = str(row.get('image_urls', ''))
                if img_str and img_str != 'nan':
                    image_urls = [u.strip() for u in img_str.split(',') if u.strip()]
                    # Clear old images
                    self.db.query(ProductImage).filter(ProductImage.product_id == db_product.id).delete()
                    for pos, url in enumerate(image_urls):
                        img = ProductImage(
                            tenant_id=self.tenant_id,
                            product_id=db_product.id,
                            url=url,
                            is_primary=(pos == 0),
                            position=pos
                        )
                        self.db.add(img)

                # 4. Upsert Product SKU (Variant Catalog)
                db_sku = self.db.query(ProductSKU).filter(
                    ProductSKU.tenant_id == self.tenant_id,
                    ProductSKU.sku == sku
                ).first()
                
                if not db_sku:
                    db_sku = ProductSKU(
                        tenant_id=self.tenant_id,
                        sku=sku,
                        product_id=db_product.id,
                        product_name=name,
                        cost_price=float(row.get('cost_price', price * 0.7)),
                        selling_price=float(row.get('selling_price', price)),
                        category_id=cat_id,
                        brand_id=brand_id,
                        size=str(row.get('size', '')),
                        color=str(row.get('color', ''))
                    )
                    self.db.add(db_sku)
                else:
                    db_sku.product_name = name
                    db_sku.selling_price = float(row.get('selling_price', db_sku.selling_price))
                    db_sku.cost_price = float(row.get('cost_price', db_sku.cost_price))
                    db_sku.category_id = cat_id
                    db_sku.brand_id = brand_id
                    db_sku.size = str(row.get('size', db_sku.size))
                    db_sku.color = str(row.get('color', db_sku.color))
                
                self.db.flush()

                # 5. Link Attribute Values (Size/Color)
                size_val = self._get_or_create_attr_value("Size", row.get('size'))
                color_val = self._get_or_create_attr_value("Color", row.get('color'))
                
                if size_val and size_val not in db_sku.attribute_values:
                    db_sku.attribute_values.append(size_val)
                if color_val and color_val not in db_sku.attribute_values:
                    db_sku.attribute_values.append(color_val)

                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append({"row": row_num, "error": str(e)})
                logger.error(f"Row {row_num} failed: {str(e)}")

        self.db.commit()
        
        return {
            "status": "completed",
            "total_rows": len(df),
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:50] # Return up to 50 errors for debugging
        }
