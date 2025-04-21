import psycopg2
import uuid
import os
from datetime import datetime, timezone
import logging
from dotenv import load_dotenv

# Load .env file at the start of the module
load_dotenv()

logger = logging.getLogger(__name__)

class SessionLogger:
    SCHEMA_PATH = "convoflow/db/schema.sql"

    def __init__(self):
        # Read connection details from environment variables
        db_name = os.getenv("POSTGRES_DB", "convoflow_metrics")
        user = os.getenv("POSTGRES_USER", "user")
        password = os.getenv("POSTGRES_PASSWORD", "sqlpassword")
        host = os.getenv("POSTGRES_HOST", "localhost") # Default to localhost for local execution
        port = os.getenv("POSTGRES_PORT", "5432")

        conn_string = f"dbname='{db_name}' user='{user}' password='{password}' host='{host}' port='{port}'"
        try:
            self.conn = psycopg2.connect(conn_string)
            self.conn.autocommit = True # Autocommit changes for simplicity
            logger.info(f"Successfully connected to PostgreSQL database '{db_name}' at {host}:{port}")
        except psycopg2.OperationalError as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            # Consider how to handle connection errors - maybe retry or raise
            raise

        self.session_id = str(uuid.uuid4()) # Generate UUID string
        self._init_schema()
        self._start_session()

    def _execute_query(self, query, params=None):
        """Helper method to execute a query with error handling."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                # Fetch results for SELECT, though not strictly needed for INSERT/UPDATE here
                # return cur.fetchall() if cur.description else None
        except Exception as e:
            logger.error(f"Error executing query: {query} | Params: {params} | Error: {e}")
            # Re-raise or handle as appropriate for your application
            raise

    def _init_schema(self):
        try:
            with open(self.SCHEMA_PATH, 'r') as f:
                schema_sql = f.read()
            # Note: psycopg2 cursor.execute() can generally only handle one statement at a time.
            # If schema.sql contains multiple statements, they need to be split or executed differently.
            # Assuming schema.sql contains compatible, single statements for simplicity.
            with self.conn.cursor() as cur:
                 # Check if tables exist before trying to create - basic idempotency
                 # A more robust migration tool (like Alembic) is better for complex cases.
                cur.execute("SELECT to_regclass('public.sessions');")
                sessions_exists = cur.fetchone()[0]
                cur.execute("SELECT to_regclass('public.routes');")
                routes_exists = cur.fetchone()[0]

                if not sessions_exists or not routes_exists:
                    logger.info(f"Schema tables not found, attempting to initialize from {self.SCHEMA_PATH}...")
                    cur.execute(schema_sql) # Execute the whole script
                    logger.info(f"Schema initialized or verified from {self.SCHEMA_PATH}")
                else:
                    logger.info("Schema tables already exist.")

        except FileNotFoundError:
            logger.error(f"Schema file not found at {self.SCHEMA_PATH}. Ensure the path is correct relative to the execution context.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize/verify schema from {self.SCHEMA_PATH}: {e}")
            # Consider if the application should proceed without the schema
            raise

    def _start_session(self):
        # Use UUID type directly if column is UUID
        query = "INSERT INTO sessions (session_id, start_time) VALUES (%s, %s)"
        params = (self.session_id, datetime.now(timezone.utc))
        self._execute_query(query, params)
        logger.info(f"Started session: {self.session_id}")

    def log_step(self, node_id, user_input, predicted_keyword):
        query = ( # Use %s placeholders for psycopg2
            "INSERT INTO routes (session_id, node_id, user_input, predicted_keyword, timestamp) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        params = (self.session_id, node_id, user_input, predicted_keyword, datetime.now(timezone.utc))
        self._execute_query(query, params)
        # logger.debug(f"Logged step for session {self.session_id}: Node {node_id}") # Optional: more verbose logging

    def end_session(self):
        query = "UPDATE sessions SET end_time = %s WHERE session_id = %s" # Use %s placeholders
        params = (datetime.now(timezone.utc), self.session_id)
        self._execute_query(query, params)
        logger.info(f"Ended session: {self.session_id}")

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("PostgreSQL connection closed.")