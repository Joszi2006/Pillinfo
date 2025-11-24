"""
Drug Database - SQLite storage for drug products and dosing charts
"""
import sqlite3
import os
from typing import Dict, Optional, List



class DrugDatabase:
    """SQLite database for caching drug products and FDA data."""
    
    def __init__(self, db_path: str = "data/pillinfo.db"):
        self.db_path = db_path
        self._ensure_directory()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _ensure_directory(self):
        """Create data directory if needed."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create tables for products and dosing charts."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS drug_products (
                rxcui TEXT PRIMARY KEY,
                brand_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                purpose TEXT,
                dosage_instructions TEXT,
                warnings TEXT,
                contraindications TEXT,
                adverse_reactions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS dosing_charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rxcui TEXT NOT NULL,
                min_weight_lb REAL,
                max_weight_lb REAL,
                min_age_months INTEGER,
                max_age_months INTEGER,
                dose_ml REAL,
                dose_text TEXT,
                FOREIGN KEY (rxcui) REFERENCES drug_products(rxcui) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_brand_name ON drug_products(brand_name);
            CREATE INDEX IF NOT EXISTS idx_dosing_rxcui ON dosing_charts(rxcui);
        """)
        self.conn.commit()
    
    # ==================== PRODUCT METHODS ====================
    
    def save_product(self, rxcui: str, brand_name: str, product_name: str):
        """Save basic product info from RxNorm."""
        self.conn.execute("""
            INSERT OR IGNORE INTO drug_products (rxcui, brand_name, product_name)
            VALUES (?, ?, ?)
        """, (rxcui, brand_name, product_name))
        self.conn.commit()
    
    def save_fda_info(self, rxcui: str, fda_data: Dict):
        """
        Save cleaned FDA data for a product.
        Updates existing product with FDA fields.
        """
        self.conn.execute("""
            UPDATE drug_products 
            SET purpose = ?, dosage_instructions = ?, warnings = ?, 
                contraindications = ?, adverse_reactions = ?
            WHERE rxcui = ?
        """, (
            fda_data.get("purpose"),
            fda_data.get("dosage_instructions"),
            fda_data.get("warnings"),
            fda_data.get("contraindications"),
            fda_data.get("adverse_reactions"),
            rxcui
        ))
        self.conn.commit()
        
        # Save dosing chart if exists
        chart = fda_data.get("dosing_chart", [])
        if chart:
            self.save_dosing_chart(rxcui, chart)
    
    def get_product(self, rxcui: str) -> Optional[Dict]:
        """Get product with all FDA data."""
        cursor = self.conn.execute(
            "SELECT * FROM drug_products WHERE rxcui = ?", (rxcui,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_products_by_brand(self, brand_name: str) -> List[Dict]:
        """Get all products for a brand."""
        cursor = self.conn.execute(
            "SELECT * FROM drug_products WHERE LOWER(brand_name) = LOWER(?)",
            (brand_name,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_brands(self) -> List[str]:
        """Get unique brand names."""
        cursor = self.conn.execute(
            "SELECT DISTINCT brand_name FROM drug_products ORDER BY brand_name"
        )
        return [row[0] for row in cursor.fetchall()]
    
    # ==================== DOSING CHART METHODS ====================
    
    def save_dosing_chart(self, rxcui: str, chart: List[Dict]):
        """
        Save dosing chart rows for a product.
        Deletes existing rows first.
        """
        # Delete old chart
        self.conn.execute("DELETE FROM dosing_charts WHERE rxcui = ?", (rxcui,))
        
        # Insert new rows
        for row in chart:
            self.conn.execute("""
                INSERT INTO dosing_charts 
                (rxcui, min_weight_lb, max_weight_lb, min_age_months, max_age_months, dose_ml, dose_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                rxcui,
                row.get("min_weight_lb"),
                row.get("max_weight_lb"),
                row.get("min_age_months"),
                row.get("max_age_months"),
                row.get("dose_ml"),
                row.get("dose_text")
            ))
        
        self.conn.commit()
    
    def get_dosing_chart(self, rxcui: str) -> List[Dict]:
        """Get dosing chart for a product."""
        cursor = self.conn.execute(
            "SELECT * FROM dosing_charts WHERE rxcui = ? ORDER BY min_age_months",
            (rxcui,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def has_dosing_chart(self, rxcui: str) -> bool:
        """Check if product has a dosing chart."""
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM dosing_charts WHERE rxcui = ?", (rxcui,)
        )
        return cursor.fetchone()[0] > 0
    
    # ==================== UTILITY METHODS ====================
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM drug_products")
        total_products = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(DISTINCT brand_name) FROM drug_products")
        total_brands = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(DISTINCT rxcui) FROM dosing_charts")
        products_with_charts = cursor.fetchone()[0]
        
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        return {
            "total_products": total_products,
            "total_brands": total_brands,
            "products_with_dosing_charts": products_with_charts,
            "db_size_bytes": db_size,
            "db_size_mb": round(db_size / (1024 * 1024), 2)
        }
    
    def clear(self):
        """Clear all data."""
        self.conn.execute("DELETE FROM dosing_charts")
        self.conn.execute("DELETE FROM drug_products")
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        self.conn.close()