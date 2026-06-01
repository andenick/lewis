#!/usr/bin/env python3
"""
Lewis Database System - SQLite implementation with performance optimization.
Provides robust data storage, indexing, and query optimization for the Lewis Platform.
"""

import sqlite3
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import json
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import pickle
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configuration for Lewis database system."""
    db_path: str
    enable_wal: bool = True
    enable_foreign_keys: bool = True
    cache_size: int = 10000  # pages
    temp_store: str = "MEMORY"
    synchronous: str = "NORMAL"
    journal_mode: str = "WAL"
    query_timeout: int = 30
    connection_pool_size: int = 5

@dataclass
class QueryPerformance:
    """Query performance metrics."""
    query: str
    execution_time: float
    rows_returned: int
    timestamp: datetime
    table_name: Optional[str] = None

class LewisDatabaseSystem:
    """
    High-performance SQLite database system for Lewis International Economics Platform.
    Features connection pooling, query optimization, and comprehensive indexing.
    """

    def __init__(self, config: DatabaseConfig):
        """Initialize the Lewis database system."""
        self.config = config
        self.db_path = Path(config.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connection pool for thread safety
        self._connections = []
        self._lock = threading.Lock()
        self._connection_pool_size = config.connection_pool_size

        # Performance tracking
        self.query_history: List[QueryPerformance] = []
        self._performance_enabled = True

        # Initialize database
        self._initialize_database()
        self._initialize_connection_pool()

        logger.info(f"Lewis Database System initialized: {self.db_path}")

    def _initialize_database(self):
        """Initialize database schema and optimize settings."""
        with self.get_connection() as conn:
            # Set pragma settings for performance
            conn.execute(f"PRAGMA journal_mode = {self.config.journal_mode}")
            conn.execute(f"PRAGMA synchronous = {self.config.synchronous}")
            conn.execute(f"PRAGMA cache_size = {self.config.cache_size}")
            conn.execute(f"PRAGMA temp_store = {self.config.temp_store}")
            conn.execute(f"PRAGMA foreign_keys = {self.config.enable_foreign_keys}")
            conn.execute(f"PRAGMA query_timeout = {self.config.query_timeout}")

            # Create schema
            self._create_schema(conn)

            conn.commit()

    def _create_schema(self, conn: sqlite3.Connection):
        """Create database schema with optimized tables."""
        logger.info("Creating database schema...")

        # Countries table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                country_code TEXT PRIMARY KEY,
                country_name TEXT NOT NULL,
                region TEXT,
                income_group TEXT,
                gdp_usd REAL,
                population INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Economic indicators table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS economic_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT NOT NULL,
                indicator_id TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                date DATE NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (country_code) REFERENCES countries(country_code),
                UNIQUE(country_code, indicator_id, date)
            )
        """)

        # Trade data table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trade_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exporter_code TEXT NOT NULL,
                importer_code TEXT NOT NULL,
                year INTEGER NOT NULL,
                trade_value REAL NOT NULL,
                trade_volume REAL,
                product_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exporter_code) REFERENCES countries(country_code),
                FOREIGN KEY (importer_code) REFERENCES countries(country_code),
                UNIQUE(exporter_code, importer_code, year, product_category)
            )
        """)

        # Capital flows table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS capital_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT NOT NULL,
                flow_type TEXT NOT NULL,
                year INTEGER NOT NULL,
                flow_value REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (country_code) REFERENCES countries(country_code),
                UNIQUE(country_code, flow_type, year)
            )
        """)

        # Forecasts table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT NOT NULL,
                indicator_id TEXT NOT NULL,
                forecast_date DATE NOT NULL,
                target_date DATE NOT NULL,
                predicted_value REAL NOT NULL,
                confidence_lower REAL,
                confidence_upper REAL,
                model_type TEXT,
                model_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (country_code) REFERENCES countries(country_code)
            )
        """)

        # Analysis results cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                cache_key TEXT PRIMARY KEY,
                analysis_type TEXT NOT NULL,
                result_data BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)

        # Performance metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT NOT NULL,
                query_text TEXT NOT NULL,
                execution_time REAL NOT NULL,
                rows_returned INTEGER,
                table_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        self._create_indexes(conn)

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create optimized indexes for performance."""
        logger.info("Creating database indexes...")

        # Economic indicators indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_econ_country_date ON economic_indicators(country_code, date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_econ_indicator_date ON economic_indicators(indicator_id, date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_econ_country_indicator ON economic_indicators(country_code, indicator_id)")

        # Trade data indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trade_exporter_year ON trade_data(exporter_code, year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trade_importer_year ON trade_data(importer_code, year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trade_year_value ON trade_data(year, trade_value)")

        # Capital flows indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_capital_country_year ON capital_flows(country_code, year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_capital_flow_type ON capital_flows(flow_type)")

        # Forecasts indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_forecast_country_target ON forecasts(country_code, target_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_forecast_indicator_target ON forecasts(indicator_id, target_date)")

        # Performance metrics indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_perf_table ON performance_metrics(table_name)")

    def _initialize_connection_pool(self):
        """Initialize connection pool for thread safety."""
        with self._lock:
            for _ in range(self._connection_pool_size):
                conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=self.config.query_timeout
                )
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                # Apply pragma settings
                conn.execute(f"PRAGMA journal_mode = {self.config.journal_mode}")
                conn.execute(f"PRAGMA foreign_keys = {self.config.enable_foreign_keys}")
                self._connections.append(conn)

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        conn = None
        try:
            with self._lock:
                if self._connections:
                    conn = self._connections.pop()
                else:
                    # Create new connection if pool is empty
                    conn = sqlite3.connect(
                        self.db_path,
                        check_same_thread=False,
                        timeout=self.config.query_timeout
                    )
                    conn.row_factory = sqlite3.Row
                    conn.execute(f"PRAGMA journal_mode = {self.config.journal_mode}")
                    conn.execute(f"PRAGMA foreign_keys = {self.config.enable_foreign_keys}")

            yield conn

        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                with self._lock:
                    if len(self._connections) < self._connection_pool_size:
                        self._connections.append(conn)
                    else:
                        conn.close()

    def execute_query(self, query: str, params: Tuple = (), fetch: str = "all",
                     table_name: Optional[str] = None) -> List[Dict]:
        """Execute SQL query with performance tracking."""
        start_time = time.time()
        query_hash = hashlib.md5(query.encode()).hexdigest()

        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                execution_time = time.time() - start_time

                # Fetch results based on fetch type
                if fetch == "all":
                    results = [dict(row) for row in cursor.fetchall()]
                elif fetch == "one":
                    row = cursor.fetchone()
                    results = [dict(row)] if row else []
                elif fetch == "many":
                    results = [dict(row) for row in cursor.fetchmany()]
                else:
                    results = []

                rows_returned = len(results)

                # Log performance if enabled
                if self._performance_enabled:
                    self._log_query_performance(query, execution_time, rows_returned, table_name)

                return results

        except Exception as e:
            logger.error(f"Query execution failed: {query[:100]}... Error: {e}")
            raise e

    def _log_query_performance(self, query: str, execution_time: float,
                             rows_returned: int, table_name: Optional[str] = None):
        """Log query performance metrics."""
        performance = QueryPerformance(
            query=query,
            execution_time=execution_time,
            rows_returned=rows_returned,
            timestamp=datetime.now(),
            table_name=table_name
        )

        self.query_history.append(performance)

        # Store in database if execution time is significant
        if execution_time > 0.1:  # Log queries taking more than 100ms
            query_hash = hashlib.md5(query.encode()).hexdigest()
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO performance_metrics
                    (query_hash, query_text, execution_time, rows_returned, table_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (query_hash, query, execution_time, rows_returned, table_name))
                conn.commit()

        # Keep only recent performance history in memory
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-500:]

    def insert_countries(self, countries_data: List[Dict[str, Any]]) -> int:
        """Batch insert countries data."""
        query = """
            INSERT OR REPLACE INTO countries
            (country_code, country_name, region, income_group, gdp_usd, population)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.executemany(query, [
                (
                    country.get('country_code'),
                    country.get('country_name'),
                    country.get('region'),
                    country.get('income_group'),
                    country.get('gdp_usd'),
                    country.get('population')
                )
                for country in countries_data
            ])
            conn.commit()
            return cursor.rowcount

    def insert_economic_indicators(self, indicators_data: List[Dict[str, Any]]) -> int:
        """Batch insert economic indicators data."""
        query = """
            INSERT OR REPLACE INTO economic_indicators
            (country_code, indicator_id, indicator_name, date, value, unit, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.executemany(query, [
                (
                    indicator.get('country_code'),
                    indicator.get('indicator_id'),
                    indicator.get('indicator_name'),
                    indicator.get('date'),
                    indicator.get('value'),
                    indicator.get('unit'),
                    indicator.get('source')
                )
                for indicator in indicators_data
            ])
            conn.commit()
            return cursor.rowcount

    def insert_trade_data(self, trade_data: List[Dict[str, Any]]) -> int:
        """Batch insert trade data."""
        query = """
            INSERT OR REPLACE INTO trade_data
            (exporter_code, importer_code, year, trade_value, trade_volume, product_category)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.executemany(query, [
                (
                    trade.get('exporter_code'),
                    trade.get('importer_code'),
                    trade.get('year'),
                    trade.get('trade_value'),
                    trade.get('trade_volume'),
                    trade.get('product_category')
                )
                for trade in trade_data
            ])
            conn.commit()
            return cursor.rowcount

    def get_economic_indicators(self, country_code: str, indicator_ids: List[str],
                               start_date: str, end_date: str) -> pd.DataFrame:
        """Get economic indicators with optimized query."""
        placeholders = ','.join(['?' for _ in indicator_ids])
        query = f"""
            SELECT indicator_id, date, value, unit
            FROM economic_indicators
            WHERE country_code = ?
            AND indicator_id IN ({placeholders})
            AND date BETWEEN ? AND ?
            ORDER BY indicator_id, date
        """

        params = [country_code] + indicator_ids + [start_date, end_date]
        results = self.execute_query(query, tuple(params), table_name='economic_indicators')

        return pd.DataFrame(results) if results else pd.DataFrame()

    def get_trade_data(self, year: int = None, exporter_code: str = None,
                      importer_code: str = None) -> pd.DataFrame:
        """Get trade data with optional filters."""
        query = "SELECT * FROM trade_data WHERE 1=1"
        params = []

        if year:
            query += " AND year = ?"
            params.append(year)

        if exporter_code:
            query += " AND exporter_code = ?"
            params.append(exporter_code)

        if importer_code:
            query += " AND importer_code = ?"
            params.append(importer_code)

        query += " ORDER BY year, trade_value DESC"

        results = self.execute_query(query, tuple(params), table_name='trade_data')
        return pd.DataFrame(results) if results else pd.DataFrame()

    def get_top_trading_partners(self, country_code: str, year: int,
                                limit: int = 10) -> List[Dict]:
        """Get top trading partners for a country."""
        query = """
            SELECT
                CASE WHEN exporter_code = ? THEN importer_code ELSE exporter_code END as partner_code,
                SUM(trade_value) as total_trade_value
            FROM trade_data
            WHERE (exporter_code = ? OR importer_code = ?) AND year = ?
            GROUP BY partner_code
            ORDER BY total_trade_value DESC
            LIMIT ?
        """

        return self.execute_query(
            query, (country_code, country_code, country_code, year, limit),
            table_name='trade_data'
        )

    def cache_analysis_result(self, cache_key: str, analysis_type: str,
                            result_data: Any, expiry_hours: int = 24) -> bool:
        """Cache analysis results for performance optimization."""
        try:
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            serialized_data = pickle.dumps(result_data)

            query = """
                INSERT OR REPLACE INTO analysis_cache
                (cache_key, analysis_type, result_data, expires_at)
                VALUES (?, ?, ?, ?)
            """

            with self.get_connection() as conn:
                conn.execute(query, (cache_key, analysis_type, serialized_data, expires_at))
                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to cache analysis result: {e}")
            return False

    def get_cached_analysis(self, cache_key: str) -> Optional[Any]:
        """Get cached analysis result."""
        query = """
            SELECT result_data, expires_at
            FROM analysis_cache
            WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
        """

        results = self.execute_query(query, (cache_key,))

        if results:
            try:
                return pickle.loads(results[0]['result_data'])
            except Exception as e:
                logger.error(f"Failed to deserialize cached result: {e}")
                return None

        return None

    def get_performance_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics for the database."""
        query = """
            SELECT
                table_name,
                COUNT(*) as query_count,
                AVG(execution_time) as avg_execution_time,
                MAX(execution_time) as max_execution_time,
                SUM(rows_returned) as total_rows_returned
            FROM performance_metrics
            WHERE timestamp > datetime('now', '-{} hours')
            GROUP BY table_name
        """.format(hours)

        results = self.execute_query(query, table_name='performance_metrics')

        # Get overall stats
        overall_query = """
            SELECT
                COUNT(*) as total_queries,
                AVG(execution_time) as avg_time,
                MAX(execution_time) as max_time
            FROM performance_metrics
            WHERE timestamp > datetime('now', '-{} hours')
        """.format(hours)

        overall_results = self.execute_query(overall_query, table_name='performance_metrics')

        return {
            'by_table': {r['table_name']: dict(r) for r in results} if results else {},
            'overall': overall_results[0] if overall_results else {},
            'period_hours': hours
        }

    def optimize_database(self):
        """Run database optimization routines."""
        logger.info("Running database optimization...")

        optimization_queries = [
            "ANALYZE",
            "VACUUM",
            "REINDEX"
        ]

        with self.get_connection() as conn:
            for query in optimization_queries:
                try:
                    conn.execute(query)
                    logger.info(f"Executed: {query}")
                except Exception as e:
                    logger.warning(f"Optimization query failed: {query} - {e}")

            conn.commit()

    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        stats = {}

        # Table sizes
        tables = [
            'countries', 'economic_indicators', 'trade_data',
            'capital_flows', 'forecasts', 'analysis_cache', 'performance_metrics'
        ]

        for table in tables:
            try:
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}", table_name=table)
                stats[f'{table}_count'] = result[0]['count'] if result else 0
            except Exception as e:
                logger.warning(f"Failed to get count for {table}: {e}")
                stats[f'{table}_count'] = 0

        # Database file size
        try:
            file_size = self.db_path.stat().st_size
            stats['database_size_mb'] = round(file_size / (1024 * 1024), 2)
        except:
            stats['database_size_mb'] = 0

        # Index info
        try:
            index_info = self.execute_query("SELECT name FROM sqlite_master WHERE type='index'")
            stats['index_count'] = len(index_info)
        except:
            stats['index_count'] = 0

        return stats

    def export_table_to_csv(self, table_name: str, output_path: str,
                          query_filter: str = None) -> bool:
        """Export table to CSV file."""
        try:
            if query_filter:
                query = f"SELECT * FROM {table_name} WHERE {query_filter}"
            else:
                query = f"SELECT * FROM {table_name}"

            results = self.execute_query(query, table_name=table_name)

            if results:
                df = pd.DataFrame(results)
                df.to_csv(output_path, index=False)
                logger.info(f"Exported {len(df)} rows from {table_name} to {output_path}")
                return True
            else:
                logger.warning(f"No data found in {table_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to export {table_name}: {e}")
            return False

    def close(self):
        """Close all database connections."""
        with self._lock:
            for conn in self._connections:
                conn.close()
            self._connections.clear()
        logger.info("Database connections closed")

def main():
    """Main function for testing the Lewis database system."""
    print("=== Lewis Database System Test ===")
    print()

    # Initialize database
    db_path = Path(__file__).parent.parent.parent.parent / "Output" / "Data" / "lewis_database.db"
    config = DatabaseConfig(
        db_path=str(db_path),
        enable_wal=True,
        connection_pool_size=3
    )

    db = LewisDatabaseSystem(config)

    try:
        # Test database operations
        print("1. Testing database initialization...")
        stats = db.get_database_stats()
        print(f"SUCCESS: Database initialized")
        print(f"  Database size: {stats.get('database_size_mb', 0)} MB")
        print(f"  Tables: {len([k for k in stats.keys() if k.endswith('_count')])}")

        # Test data insertion
        print("\n2. Testing data insertion...")
        countries_data = [
            {
                'country_code': 'USA',
                'country_name': 'United States',
                'region': 'North America',
                'income_group': 'High income',
                'gdp_usd': 25000000000000,
                'population': 331000000
            },
            {
                'country_code': 'CHN',
                'country_name': 'China',
                'region': 'East Asia',
                'income_group': 'Upper middle income',
                'gdp_usd': 17000000000000,
                'population': 1400000000
            }
        ]

        inserted = db.insert_countries(countries_data)
        print(f"SUCCESS: Inserted {inserted} countries")

        # Test indicator insertion
        indicators_data = []
        for i in range(100):
            indicators_data.append({
                'country_code': 'USA' if i % 2 == 0 else 'CHN',
                'indicator_id': 'GDP_GROWTH',
                'indicator_name': 'GDP Growth Rate',
                'date': f"2024-{(i % 12) + 1:02d}-01",
                'value': np.random.uniform(1.0, 5.0),
                'unit': 'percent',
                'source': 'FRED'
            })

        inserted = db.insert_economic_indicators(indicators_data)
        print(f"SUCCESS: Inserted {inserted} indicator records")

        # Test data retrieval
        print("\n3. Testing data retrieval...")
        indicators = db.get_economic_indicators('USA', ['GDP_GROWTH'], '2024-01-01', '2024-12-31')
        print(f"SUCCESS: Retrieved {len(indicators)} indicator records")

        # Test caching
        print("\n4. Testing caching system...")
        test_data = {'result': 'test_data', 'values': [1, 2, 3, 4, 5]}
        cache_success = db.cache_analysis_result('test_key', 'test_analysis', test_data)
        cached_result = db.get_cached_analysis('test_key')
        print(f"SUCCESS: Caching system working - {cache_success and cached_result is not None}")

        # Test performance tracking
        print("\n5. Testing performance tracking...")
        perf_stats = db.get_performance_stats(1)
        print(f"SUCCESS: Performance tracking active")
        print(f"  Total queries: {perf_stats['overall'].get('total_queries', 0)}")
        print(f"  Average execution time: {perf_stats['overall'].get('avg_time', 0):.3f}s")

        # Database optimization
        print("\n6. Running database optimization...")
        db.optimize_database()
        print("SUCCESS: Database optimization completed")

        # Final stats
        print("\n7. Final database statistics...")
        final_stats = db.get_database_stats()
        print(f"SUCCESS: Database contains:")
        for key, value in final_stats.items():
            if key.endswith('_count'):
                table_name = key.replace('_count', '')
                print(f"  {table_name}: {value:,} records")
        print(f"  Database size: {final_stats.get('database_size_mb', 0)} MB")

        print(f"\n*** LEWIS DATABASE SYSTEM TEST COMPLETED SUCCESSFULLY! ***")
        print(f"Database location: {db_path}")

    except Exception as e:
        print(f"Database test failed: {e}")
        raise

    finally:
        db.close()

if __name__ == "__main__":
    main()