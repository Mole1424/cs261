from flask_mail import Mail

mail = Mail()


class MailService:
    """Manager for emails"""

    FromEmail = "ruben.saunders@warwick.ac.uk"  # Account to send emails from
