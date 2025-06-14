#!/usr/bin/env python
"""
Jammin' Eats Database Migration Tool

This script manages database migrations for the Jammin' Eats game,
creating and updating the SQLite database schema as needed.

Usage:
    python tools/db_migrate.py upgrade [target]   # Update to target version (default: head)
    python tools/db_migrate.py downgrade [-n]     # Downgrade n versions (default: -1)
    python tools/db_migrate.py init               # Initialize migration environment
    python tools/db_migrate.py status             # Show current migration status
"""

import sys
import argparse
from pathlib import Path
import sqlite3

# Add project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Data directory for storing the database
data_dir = root_dir / "data"
data_dir.mkdir(exist_ok=True)
db_path = data_dir / "jammin.db"

# Migrations directory
migrations_dir = root_dir / "migrations"
migrations_dir.mkdir(exist_ok=True)

# Import src modules
try:
    from src.debug.logger import log, log_error
except ImportError:
    # Fallback if logger isn't available
    def log(message):
        print(f"[INFO] {message}")

    def log_error(message):
        print(f"[ERROR] {message}")


class MigrationManager:
    """Manages database migrations for Jammin' Eats."""

    def __init__(self):
        """Initialize the migration manager."""
        self.migrations = []
        self._find_migrations()
        self._ensure_version_table()

    def _find_migrations(self):
        """Find all migration files in the migrations directory."""
        if not migrations_dir.exists():
            log(f"Creating migrations directory at {migrations_dir}")
            migrations_dir.mkdir(exist_ok=True)
            return

        for migration_file in migrations_dir.glob("*.sql"):
            # Parse migration version from filename (e.g., 001_init.sql -> 1)
            version_str = migration_file.name.split("_")[0]
            try:
                version = int(version_str)
                self.migrations.append(
                    {
                        "version": version,
                        "path": migration_file,
                        "name": (
                            migration_file.stem.split("_", 1)[1]
                            if "_" in migration_file.stem
                            else "unknown"
                        ),
                    }
                )
            except ValueError:
                log_error(f"Invalid migration filename format: {migration_file.name}")

        # Sort migrations by version
        self.migrations.sort(key=lambda m: m["version"])

        if self.migrations:
            log(f"Found {len(self.migrations)} migrations")

    def _ensure_version_table(self):
        """Create the version tracking table if it doesn't exist."""
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                conn.commit()
        except sqlite3.Error as e:
            log_error(f"Failed to create version table: {e}")
            sys.exit(1)

    def get_current_version(self):
        """Get the currently applied schema version."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_version")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except sqlite3.Error as e:
            log_error(f"Failed to get current version: {e}")
            return 0

    def upgrade(self, target="head"):
        """Upgrade the database to the specified version."""
        current = self.get_current_version()

        if target == "head" and self.migrations:
            target = self.migrations[-1]["version"]
        else:
            try:
                target = int(target)
            except ValueError:
                log_error(f"Invalid target version: {target}")
                return False

        if current >= target:
            log(f"Database already at version {current}, no upgrade needed")
            return True

        log(f"Upgrading database from version {current} to {target}")

        # Filter migrations that need to be applied
        to_apply = [
            m
            for m in self.migrations
            if m["version"] > current and m["version"] <= target
        ]

        for migration in to_apply:
            try:
                log(f"Applying migration {migration['version']}: {migration['name']}")
                with open(migration["path"], "r") as f:
                    sql = f.read()

                # Extract upgrade script from file (between --UP-- and --DOWN--)
                up_script = sql.split("--UP--")[1].split("--DOWN--")[0].strip()

                with sqlite3.connect(db_path) as conn:
                    conn.executescript(up_script)
                    conn.execute(
                        "INSERT INTO schema_version (version) VALUES (?)",
                        (migration["version"],),
                    )
                    conn.commit()
                log(f"Successfully applied migration {migration['version']}")
            except Exception as e:
                log_error(f"Failed to apply migration {migration['version']}: {e}")
                return False

        log(f"Database upgraded to version {target}")
        return True

    def downgrade(self, steps=1):
        """Downgrade the database by the specified number of steps."""
        current = self.get_current_version()
        if current == 0:
            log("Database is already at the base version")
            return True

        try:
            steps = int(steps)
        except ValueError:
            log_error(f"Invalid downgrade steps: {steps}")
            return False

        target = current - steps
        if target < 0:
            target = 0

        log(f"Downgrading database from version {current} to {target}")

        # Find migrations that need to be downgraded
        to_downgrade = [
            m
            for m in reversed(self.migrations)
            if m["version"] <= current and m["version"] > target
        ]

        for migration in to_downgrade:
            try:
                log(
                    f"Downgrading migration {migration['version']}: {migration['name']}"
                )
                with open(migration["path"], "r") as f:
                    sql = f.read()

                # Extract downgrade script from file
                down_parts = sql.split("--DOWN--")
                if len(down_parts) < 2:
                    log_error(f"No downgrade script found in {migration['path']}")
                    return False

                down_script = down_parts[1].strip()

                with sqlite3.connect(db_path) as conn:
                    conn.executescript(down_script)
                    conn.execute(
                        "DELETE FROM schema_version WHERE version = ?",
                        (migration["version"],),
                    )
                    conn.commit()
                log(f"Successfully downgraded migration {migration['version']}")
            except Exception as e:
                log_error(f"Failed to downgrade migration {migration['version']}: {e}")
                return False

        log(f"Database downgraded to version {target}")
        return True

    def create_migration(self, name):
        """Create a new migration file."""
        # Find the next version number
        next_version = 1
        if self.migrations:
            next_version = self.migrations[-1]["version"] + 1

        # Format version as 3-digit string
        version_str = f"{next_version:03d}"
        filename = f"{version_str}_{name}.sql"
        filepath = migrations_dir / filename

        # Create migration file with template
        with open(filepath, "w") as f:
            f.write(
                f"""-- Migration: {name}
-- Version: {next_version}
-- Created: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--UP--
-- Add your upgrade SQL here

--DOWN--
-- Add your downgrade SQL here
"""
            )

        log(f"Created migration file: {filepath}")
        return filepath

    def status(self):
        """Show the current migration status."""
        current = self.get_current_version()
        log(f"Current database version: {current}")

        if not self.migrations:
            log("No migrations found")
            return

        log("Available migrations:")
        for m in self.migrations:
            status = "APPLIED" if m["version"] <= current else "PENDING"
            log(f"  {m['version']} - {m['name']} - {status}")

        if current < self.migrations[-1]["version"]:
            pending = [m for m in self.migrations if m["version"] > current]
            log(f"Database needs upgrade. {len(pending)} migrations pending.")


def main():
    """Main entry point for the migration tool."""
    parser = argparse.ArgumentParser(description="Jammin' Eats Database Migration Tool")

    subparsers = parser.add_subparsers(dest="command", help="Migration command")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database schema")
    upgrade_parser.add_argument(
        "target", nargs="?", default="head", help="Target version (default: head)"
    )

    # Downgrade command
    downgrade_parser = subparsers.add_parser(
        "downgrade", help="Downgrade database schema"
    )
    downgrade_parser.add_argument(
        "steps", type=int, default=1, nargs="?", help="Steps to downgrade (default: 1)"
    )

    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("name", help="Migration name (e.g. 'add_user_table')")

    # Status command
    subparsers.add_parser("status", help="Show migration status")

    # Init command
    subparsers.add_parser("init", help="Initialize migration environment")

    # Parse arguments
    args = parser.parse_args()

    # Initialize migration manager
    manager = MigrationManager()

    # Execute command
    if args.command == "upgrade":
        success = manager.upgrade(args.target)
        if not success:
            sys.exit(1)
    elif args.command == "downgrade":
        success = manager.downgrade(args.steps)
        if not success:
            sys.exit(1)
    elif args.command == "create":
        manager.create_migration(args.name)
    elif args.command == "status":
        manager.status()
    elif args.command == "init":
        # Create directory structure if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        migrations_dir.mkdir(exist_ok=True)
        log("Initialized migration environment")
        log(f"Database path: {db_path}")
        log(f"Migrations directory: {migrations_dir}")

        # Create initial migration if none exist
        if not list(migrations_dir.glob("*.sql")):
            filepath = manager.create_migration("init")
            log(f"Created initial migration file: {filepath}")
            log("Please edit this file to define your schema")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
