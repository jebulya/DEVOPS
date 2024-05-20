SELECT 'CREATE DATABASE temp_dbname' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'temp_dbname')\gexec
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'temp_repluser') THEN
        CREATE USER temp_repluser WITH REPLICATION ENCRYPTED PASSWORD 'temp_replpassword'; 
    END IF; 
END $$;

ALTER USER temp_postgresuser WITH PASSWORD 'temp_postgrespassword';

\c temp_dbname;
CREATE TABLE IF NOT EXISTS emails(
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS phone_numbers(
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(100) NOT NULL
);