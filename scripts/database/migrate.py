#!/usr/bin/env python3
"""
Database Migration Script for AutoServe
Handles database schema migrations and data migrations
"""

import os
import sys
import psycopg2
import argparse
from datetime import datetime
from pathlib import Path

class DatabaseMigrator:
    def __init__(self, database_url):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        
    def connect(self):
        """Create database connection"""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)
    
    def create_migration_table(self):
        """Create migrations tracking table"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                return [row[0] for row in cur.fetchall()]
    
    def get_pending_migrations(self):
        """Get list of pending migrations"""
        applied = set(self.get_applied_migrations())
        all_migrations = []
        
        for migration_file in sorted(self.migrations_dir.glob("*.sql")):
            version = migration_file.stem
            if version not in applied:
                all_migrations.append((version, migration_file))
        
        return all_migrations
    
    def apply_migration(self, version, filepath):
        """Apply a single migration"""
        print(f"Applying migration: {version}")
        
        with open(filepath, 'r') as f:
            migration_sql = f.read()
        
        with self.connect() as conn:
            with conn.cursor() as cur:
                try:
                    # Execute the migration
                    cur.execute(migration_sql)
                    
                    # Record the migration
                    cur.execute(
                        "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
                        (version, filepath.name)
                    )
                    
                    conn.commit()
                    print(f"✅ Successfully applied: {version}")
                    
                except Exception as e:
                    conn.rollback()
                    print(f"❌ Failed to apply {version}: {e}")
                    raise
    
    def run_migrations(self):
        """Run all pending migrations"""
        self.create_migration_table()
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations")
            return
        
        print(f"Found {len(pending)} pending migrations")
        
        for version, filepath in pending:
            self.apply_migration(version, filepath)
        
        print("All migrations completed successfully!")
    
    def create_migration(self, name):
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"{timestamp}_{name}"
        filepath = self.migrations_dir / f"{version}.sql"
        
        template = f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}
-- Description: {name.replace('_', ' ').title()}

-- Add your migration SQL here
-- Remember to use transactions and add rollback logic if needed

BEGIN;

-- Example:
-- ALTER TABLE users ADD COLUMN new_column VARCHAR(255);
-- CREATE INDEX idx_users_new_column ON users(new_column);

COMMIT;
"""
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        print(f"Created migration: {filepath}")
        return filepath
    
    def rollback_migration(self, version):
        """Rollback a specific migration (if rollback file exists)"""
        rollback_file = self.migrations_dir / f"{version}_rollback.sql"
        
        if not rollback_file.exists():
            print(f"No rollback file found for {version}")
            return
        
        print(f"Rolling back migration: {version}")
        
        with open(rollback_file, 'r') as f:
            rollback_sql = f.read()
        
        with self.connect() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(rollback_sql)
                    cur.execute(
                        "DELETE FROM schema_migrations WHERE version = %s",
                        (version,)
                    )
                    conn.commit()
                    print(f"✅ Successfully rolled back: {version}")
                    
                except Exception as e:
                    conn.rollback()
                    print(f"❌ Failed to rollback {version}: {e}")
                    raise
    
    def status(self):
        """Show migration status"""
        self.create_migration_table()
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print("Migration Status:")
        print(f"Applied migrations: {len(applied)}")
        for migration in applied:
            print(f"  ✅ {migration}")
        
        print(f"\nPending migrations: {len(pending)}")
        for version, filepath in pending:
            print(f"  ⏳ {version}")

def main():
    parser = argparse.ArgumentParser(description="AutoServe Database Migrator")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/autoserve"),
        help="Database connection URL"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Migrate command
    subparsers.add_parser("migrate", help="Run pending migrations")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("name", help="Migration name (snake_case)")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback a migration")
    rollback_parser.add_argument("version", help="Migration version to rollback")
    
    # Status command
    subparsers.add_parser("status", help="Show migration status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    migrator = DatabaseMigrator(args.database_url)
    
    if args.command == "migrate":
        migrator.run_migrations()
    elif args.command == "create":
        migrator.create_migration(args.name)
    elif args.command == "rollback":
        migrator.rollback_migration(args.version)
    elif args.command == "status":
        migrator.status()

if __name__ == "__main__":
    main()
