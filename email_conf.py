from config import ENV, MAIL_FROM, MAIL_PASS, MAIL_PORT, MAIL_SERVER, MAIL_USER
from fastapi_mail import ConnectionConfig, FastMail
from jinja2 import Environment, FileSystemLoader


email_conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USER,
    MAIL_PASSWORD=MAIL_PASS,       
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=True,            
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=ENV == 'production',
)

template_env = Environment(
    loader=FileSystemLoader("templates")
)

