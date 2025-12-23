from email_conf import template_env, email_conf
from fastapi_mail import FastMail, MessageSchema

async def send_email(email: str, subject: str, template_file_name: str, template_data: dict):

    template = template_env.get_template(template_file_name)
    html_content = template.render(**template_data)

    
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(email_conf)
    await fm.send_message(message)
