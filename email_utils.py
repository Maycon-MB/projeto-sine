import smtplib
from email.mime.text import MIMEText

def enviar_email(destinatario, assunto, mensagem):
    """
    Envia um e-mail usando o protocolo SMTP.
    :param destinatario: E-mail do destinatário.
    :param assunto: Assunto do e-mail.
    :param mensagem: Corpo do e-mail.
    """
    remetente = "seu_email@gmail.com"
    senha = "sua_senha_aqui"

    msg = MIMEText(mensagem)
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
            print(f"E-mail enviado para {destinatario}")
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar e-mail: {e}")
