import os
import sys
import pymysql
import getpass
import argparse
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import the project config
from config import config

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Setup the university grade prediction database')
    parser.add_argument('--env', type=str, default='development', 
                        choices=['development', 'testing', 'production'],
                        help='Environment to setup (default: development)')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Database host (default: localhost)')
    parser.add_argument('--port', type=int, default=3306,
                        help='Database port (default: 3306)')
    parser.add_argument('--user', type=str, default='root',
                        help='Database user (default: root)')
    parser.add_argument('--password', type=str,
                        help='Database password (if not provided, will prompt)')
    parser.add_argument('--no-seed', action='store_true',
                        help='Skip seeding initial data')
    parser.add_argument('--reset', action='store_true',
                        help='Drop database if exists and recreate')
    
    return parser.parse_args()

def get_db_name_from_url(db_url):
    """Extract database name from SQLAlchemy URL"""
    if not db_url or 'sqlite' in db_url:
        return 'university_grade_prediction'
    
    # Extract database name from URL
    parts = db_url.split('/')
    if len(parts) > 1:
        return parts[-1].split('?')[0]
    return 'university_grade_prediction'

def execute_sql_file(cursor, file_path):
    """Execute SQL statements from a file"""
    with open(file_path, 'r') as f:
        # Split file into statements
        sql_commands = f.read().split(';')
        
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    print(f"Executed: {command[:50]}...")
                except Exception as e:
                    print(f"Error executing: {command[:50]}...")
                    print(f"Error: {str(e)}")

def setup_database(args):
    """Setup the university grade prediction database"""
    # Get configuration for specified environment
    env_config = config[args.env]
    
    # Get database name from config URL or use default
    db_url = env_config.SQLALCHEMY_DATABASE_URI
    db_name = get_db_name_from_url(db_url)
    
    # Get password securely if not provided
    password = args.password or getpass.getpass("Enter MySQL password: ")
    
    # Connect to MySQL server (without selecting a database)
    try:
        connection = pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=password
        )
        print(f"Connected to MySQL server at {args.host}:{args.port}")
    except Exception as e:
        print(f"Error connecting to MySQL server: {str(e)}")
        sys.exit(1)
    
    try:
        with connection.cursor() as cursor:
            # Drop database if reset flag is set
            if args.reset:
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                print(f"Dropped database {db_name}")
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Created database {db_name}")
            
            # Use the database
            cursor.execute(f"USE {db_name}")
            
            # Get base directory for schema files
            base_dir = Path(__file__).resolve().parent.parent
            schema_dir = base_dir / 'database' / 'schema'
            
            # Check if schema directory exists
            if not schema_dir.exists() or not schema_dir.is_dir():
                print(f"Schema directory not found: {schema_dir}")
                sys.exit(1)
            
            # Execute schema files in order
            schema_files = sorted([f for f in schema_dir.glob('*.sql')])
            if not schema_files:
                print("No schema files found.")
                sys.exit(1)
            
            print(f"Found {len(schema_files)} schema files. Creating tables...")
            for schema_file in schema_files:
                print(f"Executing {schema_file.name}...")
                execute_sql_file(cursor, schema_file)
            
            # Seed initial data if not skipped
            if not args.no_seed:
                seed_dir = base_dir / 'database' / 'seeds'
                if seed_dir.exists() and seed_dir.is_dir():
                    seed_files = sorted([f for f in seed_dir.glob('*.sql')])
                    if seed_files:
                        print(f"Found {len(seed_files)} seed files. Seeding data...")
                        for seed_file in seed_files:
                            print(f"Executing {seed_file.name}...")
                            execute_sql_file(cursor, seed_file)
                    else:
                        print("No seed files found. Skipping data seeding.")
                else:
                    print(f"Seed directory not found: {seed_dir}")
            
            # Commit changes
            connection.commit()
            print("Database setup completed successfully!")
            
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        sys.exit(1)
    finally:
        connection.close()

if __name__ == "__main__":
    args = parse_args()
    setup_database(args)