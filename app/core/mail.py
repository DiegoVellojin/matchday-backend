import resend
from app.core.config import settings

def send_password_reset_email(to_email: str, reset_link: str, nombre: str = "Jugador"):
    """
    Envía el correo electrónico de recuperación de contraseña usando Resend API.
    """
    if not settings.RESEND_API_KEY:
        print("ERROR: RESEND_API_KEY no configurada. No se enviará el correo.", flush=True)
        return

    # Logo de la App
    logo_url = "https://firebasestorage.googleapis.com/v0/b/matchday-68b9a.firebasestorage.app/o/app_icon.png?alt=media&token=18be696c-c7b7-4933-a3cb-4eb8afceed50"
    primary_green = "#00A859" 

    # Nuevo diseño Premium
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap');
            body {{ margin: 0; padding: 0; background-color: #0A0A0A; font-family: 'Outfit', 'Segoe UI', sans-serif; }}
            .wrapper {{ background-color: #0A0A0A; padding: 40px 20px; text-align: center; }}
            .container {{ max-width: 500px; margin: 0 auto; background: #141414; border: 1px solid #222; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }}
            .header {{ padding: 40px 20px; background: linear-gradient(180deg, #1A1A1A 0%, #141414 100%); }}
            .logo {{ height: 50px; filter: drop-shadow(0 0 10px rgba(0, 168, 89, 0.3)); }}
            .content {{ padding: 0 40px 40px; color: #FFFFFF; }}
            .title {{ font-size: 28px; font-weight: 700; margin-bottom: 16px; color: #FFFFFF; letter-spacing: -0.5px; }}
            .greeting {{ color: {primary_green}; font-size: 18px; font-weight: 600; margin-bottom: 24px; }}
            .text {{ color: #A0A0A0; font-size: 16px; line-height: 1.6; margin-bottom: 32px; }}
            .btn-container {{ margin: 40px 0; }}
            .btn {{ background: linear-gradient(90deg, #00A859 0%, #008D4A 100%); color: #FFFFFF !important; padding: 18px 36px; text-decoration: none; border-radius: 16px; font-weight: 700; font-size: 16px; display: inline-block; box-shadow: 0 10px 20px rgba(0, 168, 89, 0.2); transition: transform 0.2s; }}
            .footer {{ background-color: #0F0F0F; padding: 30px; border-top: 1px solid #222; }}
            .footer-text {{ color: #444; font-size: 12px; line-height: 1.4; }}
            .expiry {{ color: #666; font-size: 13px; margin-top: 20px; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <img src="{logo_url}" class="logo" alt="MatchDay">
                </div>
                <div class="content">
                    <h1 class="title">Recupera tu acceso</h1>
                    <div class="greeting">¡Hola, {nombre}! ⚽</div>
                    <p class="text">Recibimos una solicitud para restablecer tu contraseña. Queremos que vuelvas a la cancha lo antes posible.</p>
                    
                    <div class="btn-container">
                        <a href="{reset_link}" class="btn">RESTABLECER MI CONTRASEÑA</a>
                    </div>
                    
                    <p class="expiry">Este enlace de seguridad expirará en 15 minutos por tu protección.</p>
                </div>
                <div class="footer">
                    <p class="footer-text">© 2026 MatchDay. Todos los derechos reservados.<br>Has recibido este correo porque se solicitó un cambio de clave en tu cuenta.</p>
                    <p class="footer-text" style="margin-top: 20px;">
                        ¿El botón no funciona? <a href="{reset_link}" style="color: {primary_green}; text-decoration: none;">Haz clic aquí</a>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        resend.api_key = settings.RESEND_API_KEY
        
        params = {
            "from": f"MatchDay <{settings.RESEND_FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Recuperar contraseña - MatchDay",
            "html": html_content
        }

        resend.Emails.send(params)
            
    except Exception as e:
        print(f"ERROR: Fallo al enviar correo con Resend a {to_email}: {str(e)}", flush=True)
