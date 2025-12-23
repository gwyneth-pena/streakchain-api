import os


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "steakflow")
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
MONGO_URI = os.getenv("MONGO_URI", "your_mongo_uri")
MAIL_USER = os.getenv("MAIL_USER", "your_mail_user")
MAIL_PASS = os.getenv("MAIL_PASS", "your_mail_pass")
MAIL_SERVER = os.getenv("MAIL_SERVER", "your_mail_server")
MAIL_PORT = os.getenv("MAIL_PORT", "your_mail_port")
MAIL_FROM = os.getenv("MAIL_FROM", "your_mail_from")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ENV = os.getenv("ENV", "production") 
