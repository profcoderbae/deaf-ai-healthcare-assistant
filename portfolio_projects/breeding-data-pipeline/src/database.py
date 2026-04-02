"""
Database Module
===============
SQLite database management for breeding trial data storage.
Handles schema creation, data insertion, and querying for
multi-year, multi-site trial datasets.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime


class BreedingDatabase:
    """Manages SQLite database for breeding trial data."""
    
    def __init__(self, db_path: str = "data/breeding_trials.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Open database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, *args):
        self.close()
    
    def create_schema(self):
        """Create database tables for breeding trial data."""
        cursor = self.conn.cursor()
        
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS genotypes (
                genotype_id TEXT PRIMARY KEY,
                crop TEXT NOT NULL,
                cross_year INTEGER,
                female_parent TEXT,
                male_parent TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS trial_sites (
                site_id TEXT PRIMARY KEY,
                location TEXT,
                latitude REAL,
                longitude REAL,
                altitude_m REAL,
                soil_type TEXT
            );
            
            CREATE TABLE IF NOT EXISTS phenotype_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                genotype_id TEXT NOT NULL,
                crop TEXT NOT NULL,
                site TEXT NOT NULL,
                season TEXT NOT NULL,
                rep INTEGER,
                block TEXT,
                row_num INTEGER,
                tree_position INTEGER,
                evaluation_date TEXT,
                evaluator TEXT,
                qc_status TEXT DEFAULT 'PENDING',
                source_file TEXT,
                ingestion_timestamp TEXT,
                FOREIGN KEY (genotype_id) REFERENCES genotypes(genotype_id)
            );
            
            CREATE TABLE IF NOT EXISTS trait_values (
                value_id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                trait_name TEXT NOT NULL,
                trait_value REAL,
                qc_flag TEXT,
                FOREIGN KEY (record_id) REFERENCES phenotype_records(record_id)
            );
            
            CREATE TABLE IF NOT EXISTS genotype_means (
                genotype_id TEXT,
                crop TEXT,
                site TEXT,
                season TEXT,
                trait_name TEXT,
                mean_value REAL,
                std_value REAL,
                n_reps INTEGER,
                PRIMARY KEY (genotype_id, site, season, trait_name)
            );
            
            CREATE TABLE IF NOT EXISTS qc_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TEXT NOT NULL,
                check_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                trait TEXT,
                site TEXT,
                season TEXT,
                detail TEXT,
                records_affected INTEGER
            );
            
            CREATE INDEX IF NOT EXISTS idx_phenotype_genotype 
                ON phenotype_records(genotype_id);
            CREATE INDEX IF NOT EXISTS idx_phenotype_site_season 
                ON phenotype_records(site, season);
            CREATE INDEX IF NOT EXISTS idx_trait_record 
                ON trait_values(record_id);
            CREATE INDEX IF NOT EXISTS idx_means_genotype 
                ON genotype_means(genotype_id);
        """)
        
        self.conn.commit()
        print("Database schema created successfully.")
    
    def insert_trial_data(self, df: pd.DataFrame, trait_cols: list):
        """
        Insert trial data into normalized database tables.
        
        Parameters
        ----------
        df : pd.DataFrame
            Validated trial data
        trait_cols : list
            Names of trait columns to store
        """
        cursor = self.conn.cursor()
        
        # Insert unique genotypes
        genotypes = df[["genotype_id", "crop"]].drop_duplicates()
        for _, row in genotypes.iterrows():
            cursor.execute(
                "INSERT OR IGNORE INTO genotypes (genotype_id, crop) VALUES (?, ?)",
                (row["genotype_id"], row["crop"])
            )
        
        # Insert phenotype records and trait values
        records_inserted = 0
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO phenotype_records 
                (genotype_id, crop, site, season, rep, block, row_num, 
                 tree_position, evaluation_date, evaluator, qc_status, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("genotype_id"), row.get("crop"), row.get("site"),
                row.get("season"), row.get("rep"), row.get("block"),
                row.get("row"), row.get("tree_position"),
                str(row.get("evaluation_date", "")), row.get("evaluator"),
                row.get("_qc_status", "PENDING"), row.get("source_file", "")
            ))
            
            record_id = cursor.lastrowid
            
            for trait in trait_cols:
                if trait in row and pd.notna(row[trait]):
                    flags = ""
                    if "_qc_flags" in row and isinstance(row["_qc_flags"], list):
                        flags = ",".join(f for f in row["_qc_flags"] if trait in f)
                    
                    cursor.execute("""
                        INSERT INTO trait_values (record_id, trait_name, trait_value, qc_flag)
                        VALUES (?, ?, ?, ?)
                    """, (record_id, trait, float(row[trait]), flags or None))
            
            records_inserted += 1
        
        self.conn.commit()
        print(f"  Inserted {records_inserted} phenotype records into database.")
    
    def insert_qc_log(self, issues_df: pd.DataFrame):
        """Log QC issues to the database."""
        if issues_df.empty:
            return
        
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        for _, issue in issues_df.iterrows():
            cursor.execute("""
                INSERT INTO qc_log (run_timestamp, check_type, severity, trait, site, season, detail)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                issue.get("check", ""),
                issue.get("severity", ""),
                issue.get("trait", None),
                issue.get("site", None),
                issue.get("season", None),
                issue.get("detail", ""),
            ))
        
        self.conn.commit()
        print(f"  Logged {len(issues_df)} QC issues.")
    
    def query_genotype_performance(self, crop: str, trait: str, top_n: int = 20) -> pd.DataFrame:
        """Query top-performing genotypes for a given trait."""
        query = """
            SELECT gm.genotype_id, gm.trait_name, 
                   AVG(gm.mean_value) as overall_mean,
                   COUNT(DISTINCT gm.site || gm.season) as n_environments,
                   AVG(gm.n_reps) as avg_reps
            FROM genotype_means gm
            WHERE gm.crop = ? AND gm.trait_name = ?
            GROUP BY gm.genotype_id, gm.trait_name
            HAVING n_environments >= 2
            ORDER BY overall_mean DESC
            LIMIT ?
        """
        return pd.read_sql_query(query, self.conn, params=(crop, trait, top_n))
    
    def get_trial_summary(self) -> pd.DataFrame:
        """Get summary statistics of the trial database."""
        query = """
            SELECT crop, site, season,
                   COUNT(DISTINCT genotype_id) as n_genotypes,
                   COUNT(*) as n_records,
                   COUNT(DISTINCT evaluator) as n_evaluators
            FROM phenotype_records
            GROUP BY crop, site, season
            ORDER BY crop, site, season
        """
        return pd.read_sql_query(query, self.conn)
