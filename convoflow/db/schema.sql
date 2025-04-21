-- Schema for PostgreSQL

CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS routes (
    id BIGSERIAL PRIMARY KEY, -- Use BIGSERIAL for auto-incrementing 64-bit integer
    session_id UUID,          -- Reference the sessions table
    node_id TEXT,             -- Assuming node_id is generic text
    user_input TEXT,
    predicted_keyword TEXT,
    timestamp TIMESTAMPTZ,    -- Use timestamp with time zone
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);