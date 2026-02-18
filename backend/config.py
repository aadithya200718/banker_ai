"""
Configuration Module
====================
Loads environment variables from .env file.
"""

import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Database Configuration
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "3306")
DB_USER = os.getenv("DATABASE_USER", "root")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DB_NAME = os.getenv("DATABASE_NAME", "banker_verification")
DB_SSL_CA = os.getenv("DATABASE_SSL_CA")

# Construct DATABASE_URL if not explicitly set
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # Check if we are using TiDB (often uses port 4000 or specific host) or generic MySQL
    # TiDB/MySQL connection string format: mysql+pymysql://user:password@host:port/dbname
    
    # Handle SSL for TiDB Cloud
    connect_args = ""
    if DB_SSL_CA:
        connect_args = f"?ssl_ca={DB_SSL_CA}&ssl_verify_cert=true&ssl_verify_identity=true"
    
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}{connect_args}"


JWT_SECRET = os.getenv("JWT_SECRET", "banker_face_verify_super_secret_key_2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
