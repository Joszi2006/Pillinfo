"""
Drug Database - PostgreSQL storage for drug products and dosing charts
"""
import psycopg
from psycopg.rows import dict_row
import os
from typing import Dict, Optional, List


class DrugDatabase:
    """PostgreSQL database for caching drug products and FDA data."""
    
    def __init__(self):
        """
        Initialize database connection.
        """
        self.db_url = os.getenv("DATABASE_URL")
        
        if not self.db_url:
            raise ValueError("DATABASE_PATH environment variable not set")
        
        # Parse URL to handle Render's postgres:// vs postgresql://
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)
        
        self.conn = psycopg.connect(self.db_url)
        self.conn.autocommit = False
        self._create_tables()
    
    def _create_tables(self):
        """Create tables for products and dosing charts."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
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
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dosing_charts (
                    id SERIAL PRIMARY KEY,
                    rxcui TEXT NOT NULL,
                    min_weight_lb REAL,
                    max_weight_lb REAL,
                    min_age_months INTEGER,
                    max_age_months INTEGER,
                    dose_ml REAL,
                    dose_text TEXT,
                    FOREIGN KEY (rxcui) REFERENCES drug_products(rxcui) ON DELETE CASCADE
                );
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_brand_name ON drug_products(brand_name);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dosing_rxcui ON dosing_charts(rxcui);
            """)
            
            self.conn.commit()
    
    # ==================== PRODUCT METHODS ====================
    
    def save_product(self, rxcui: str, brand_name: str, product_name: str):
        """Save basic product info from RxNorm."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO drug_products (rxcui, brand_name, product_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (rxcui) DO NOTHING
            """, (rxcui, brand_name, product_name))
            
            self.conn.commit()
    
    def save_fda_info(self, rxcui: str, fda_data: Dict):
        """
        Save cleaned FDA data for a product.
        Updates existing product with FDA fields.
        """
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE drug_products 
                SET purpose = %s, dosage_instructions = %s, warnings = %s, 
                    contraindications = %s, adverse_reactions = %s
                WHERE rxcui = %s
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
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM drug_products WHERE rxcui = %s", (rxcui,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_products_by_brand(self, brand_name: str) -> List[Dict]:
        """Get all products for a brand."""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM drug_products WHERE LOWER(brand_name) = LOWER(%s)",
                (brand_name,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_brands(self) -> List[str]:
        """Get unique brand names."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT brand_name FROM drug_products ORDER BY brand_name"
            )
            return [row[0] for row in cursor.fetchall()]
    
    # ==================== DOSING CHART METHODS ====================
    
    def save_dosing_chart(self, rxcui: str, chart: List[Dict]):
        """
        Save dosing chart rows for a product.
        Deletes existing rows first.
        """
        with self.conn.cursor() as cursor:
            # Delete old chart
            cursor.execute("DELETE FROM dosing_charts WHERE rxcui = %s", (rxcui,))
            
            # Insert new rows
            for row in chart:
                cursor.execute("""
                    INSERT INTO dosing_charts 
                    (rxcui, min_weight_lb, max_weight_lb, min_age_months, max_age_months, dose_ml, dose_text)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
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
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM dosing_charts WHERE rxcui = %s ORDER BY min_age_months",
                (rxcui,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def has_dosing_chart(self, rxcui: str) -> bool:
        """Check if product has a dosing chart."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM dosing_charts WHERE rxcui = %s", (rxcui,)
            )
            return cursor.fetchone()[0] > 0
    
    # ==================== UTILITY METHODS ====================
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM drug_products")
            total_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT brand_name) FROM drug_products")
            total_brands = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT rxcui) FROM dosing_charts")
            products_with_charts = cursor.fetchone()[0]
            
            # PostgreSQL database size query
            cursor.execute("SELECT pg_database_size(current_database())")
            db_size = cursor.fetchone()[0]
            
            return {
                "total_products": total_products,
                "total_brands": total_brands,
                "products_with_dosing_charts": products_with_charts,
                "db_size_bytes": db_size,
                "db_size_mb": round(db_size / (1024 * 1024), 2)
            }
    
    def clear(self):
        """Clear all data."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM dosing_charts")
            cursor.execute("DELETE FROM drug_products")
            self.conn.commit()
    
    def close(self):
        """Close database connection."""
        self.conn.close()