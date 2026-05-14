import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_password_reset_email(to_email: str, reset_link: str, nombre: str = "Jugador"):
    """
    Envía el correo electrónico de recuperación de contraseña.
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("ADVERTENCIA: Credenciales SMTP no configuradas. Correo no enviado.")
        print(f"Enlace generado para {to_email}: {reset_link}")
        return

    # Logo de la App
    logo_url = "https://firebasestorage.googleapis.com/v0/b/matchday-68b9a.firebasestorage.app/o/app_icon.png?alt=media&token=18be696c-c7b7-4933-a3cb-4eb8afceed50"

    primary_green = "#00A859" 

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f9f9; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .header {{ background-color: #111111; padding: 20px; text-align: center; }}
            .header img {{ height: 40px; }}

            .content {{ padding: 20px 40px; text-align: center; color: #333333; }}
            .content h1 {{ font-size: 22px; color: #111111; }}
            .content p {{ font-size: 16px; color: #666666; line-height: 1.5; }}
            .button-container {{ margin: 30px 0; }}
            .button {{ background-color: {primary_green}; color: #ffffff !important; padding: 15px 30px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; font-size: 16px; }}
            .footer {{ background-color: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; color: #999999; }}
            .link-fallback {{ font-size: 12px; color: #999999; margin-top: 20px; word-break: break-all; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{logo_url}" alt="MatchDay">
            </div>

            <div class="content">
                <h1>¡Hola, {nombre}!</h1>
                <p>Recibimos una solicitud para restablecer tu contraseña. Si fuiste tú, presiona el botón de abajo:</p>
                <div class="button-container">
                    <a href="{reset_link}" class="button">RESTABLECER MI CONTRASEÑA</a>
                </div>
                <p>Si no puedes presionar el botón, copia y pega este enlace en tu navegador:</p>
                <p class="link-fallback">{reset_link}</p>
                <p style="font-size: 13px; color: #999999;">Este enlace expirará en 15 minutos.</p>
            </div>
            <div class="footer">
                <p>&copy; 2026 MatchDay App. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = "Se ha solicitado restablecer tu contraseña de MatchDay"
    message["From"] = f"MatchDay Soporte <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        print(f"DEBUG: Intentando enviar correo a {to_email} vía {settings.SMTP_SERVER}:{settings.SMTP_PORT}...", flush=True)
        # Configuración para TLS
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
        server.quit()
        print(f"SUCCESS: Correo de recuperación enviado exitosamente a {to_email}", flush=True)
    except Exception as e:
        print(f"ERROR: No se pudo enviar el correo a {to_email}: {str(e)}", flush=True)
