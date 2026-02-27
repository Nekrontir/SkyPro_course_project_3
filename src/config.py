import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hh_parser")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

COMPANY_IDS_STR = os.getenv("COMPANY_IDS", "")
COMPANY_IDS = [int(x.strip()) for x in COMPANY_IDS_STR.split(",") if x.strip().isdigit()]
