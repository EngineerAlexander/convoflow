# check_db_connections.py
import os
import sys
from dotenv import load_dotenv

print("Loading environment variables from .env file...")
if not load_dotenv(verbose=True):
    print("Warning: .env file not found or empty.")
print("-" * 30)

# --- Neo4j Check ---
def check_neo4j():
    print("Attempting to connect to Neo4j...")
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        print("Error: Missing Neo4j connection details in environment variables.")
        print(f"  NEO4J_URI: {'Found' if neo4j_uri else 'Missing'}")
        print(f"  NEO4J_USERNAME: {'Found' if neo4j_user else 'Missing'}")
        print(f"  NEO4J_PASSWORD: {'Found' if neo4j_password else 'Missing'}")
        return False

    print(f"  Using URI: {neo4j_uri}")
    print(f"  Using User: {neo4j_user}")

    driver = None
    try:
        # Import here to ensure dotenv loads first
        from neo4j import GraphDatabase, exceptions
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        driver.verify_connectivity()
        print("SUCCESS: Neo4j connection verified.")
        return True
    except exceptions.AuthError:
        print("FAILURE: Neo4j connection failed - Authentication Error (check user/password).")
        return False
    except exceptions.ServiceUnavailable:
        print(f"FAILURE: Neo4j connection failed - Service Unavailable (is DB running at {neo4j_uri}?).")
        return False
    except Exception as e:
        print(f"FAILURE: Neo4j connection failed - Unexpected error: {e}")
        return False
    finally:
        if driver:
            driver.close()
        print("-" * 30)

# --- PostgreSQL Check ---
def check_postgres():
    print("Attempting to connect to PostgreSQL...")
    db_name = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")

    if not all([db_name, user, password, host]):
        print("Error: Missing PostgreSQL connection details in environment variables.")
        print(f"  POSTGRES_DB: {'Found' if db_name else 'Missing'}")
        print(f"  POSTGRES_USER: {'Found' if user else 'Missing'}")
        print(f"  POSTGRES_PASSWORD: {'Found' if password else 'Missing'}")
        print(f"  POSTGRES_HOST: {'Found' if host else 'Missing'}")
        print(f"  POSTGRES_PORT: {port}")
        return False

    print(f"  Using Host: {host}")
    print(f"  Using Port: {port}")
    print(f"  Using Database: {db_name}")
    print(f"  Using User: {user}")

    conn = None
    try:
        # Import here to ensure dotenv loads first
        import psycopg2
        from psycopg2 import OperationalError

        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=10
        )

        print("SUCCESS: PostgreSQL connection verified.")
        conn.close()
        return True
    except OperationalError as e:
        print(f"FAILURE: PostgreSQL connection failed - Operational Error: {e}")
        return False
    except ImportError:
         print("FAILURE: PostgreSQL connection failed - psycopg2 library not found.")
         print("         Please install it: pip install psycopg2-binary")
         return False
    except Exception as e:
        print(f"FAILURE: PostgreSQL connection failed - Unexpected error: {e}")
        return False
    finally:
        if conn and not conn.closed:
            conn.close()
        print("-" * 30)


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Database Connection Checks...")
    print("=" * 30)

    neo4j_ok = check_neo4j()
    postgres_ok = check_postgres()

    print("=" * 30)
    print("Summary:")
    print(f"Neo4j Connection: {'OK' if neo4j_ok else 'FAILED'}")
    print(f"PostgreSQL Connection: {'OK' if postgres_ok else 'FAILED'}")
    print("=" * 30)

    if not neo4j_ok or not postgres_ok:
        print("\nTroubleshooting Tips:")
        print("1. Ensure Docker containers for databases are running (`docker-compose ps` or `docker ps`).")
        print("2. Verify database credentials (user/password) in your `.env` file match the `docker-compose.yml` file.")
        print("3. Ensure `NEO4J_URI` and `POSTGRES_HOST` in `.env` are set to `localhost` (or the correct IP if Docker is remote).")
        print("4. Check firewall rules if Docker or databases are running on a different machine/network.")
        print("5. If Neo4j auth failed after reset, ensure you waited long enough after `docker-compose up -d` for initialization.")
        sys.exit(1)
    else:
        print("\nAll database connections successful!")
        sys.exit(0)
