from .models import User
import tempfile, re

def check_password(password: str):
    errors = []

    # Lunghezza minima
    if len(password) < 8:
        errors.append("The password must contain at least 8 characters.")
    
    # Lettera minuscola
    if not re.search("[a-z]", password):
        errors.append("The password must contain at least one lowercase letter.")
    
    # Lettera maiuscola
    if not re.search("[A-Z]", password):
        errors.append("The password must contain at least one uppercase letter.")
    
    # Numero
    if not re.search("[0-9]", password):
        errors.append("The password must contain at least one number.")
    
    # Simbolo speciale
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("The password must contain at least one special character.")
    
    # Controllo per spazi
    if " " in password:
        errors.append("The password must not contain spaces.")
    
    # Controllo di caratteri consecutivi ripetuti (ad es. 4 o più caratteri identici)
    if re.search(r"(.)\1{3,}", password):
        errors.append("The password must not contain 4 or more consecutive identical characters.")
    
    # Blacklist delle password comuni
    common_passwords = {"password", "12345678", "qwerty", "abc123", "letmein", "welcome"}
    if password.lower() in common_passwords:
        errors.append("The password is too common and easily guessable. Please choose a stronger password.")
    
    # Risultato finale
    if errors:
        return False, " ".join(errors)
    return True, ""

def check_email(email: str):
    errors = []

    # Controllo formato email con regex
    if not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$", email):
        errors.append("The email address format is invalid.")

    # Controllo case-insensitive di esistenza dell'email
    if User.query.filter(User.email.ilike(email)).first():
        errors.append("The email address already exists.")

    # Blacklist dei domini usa e getta (opzionale)
    blacklist_domains = {"tempmail.com", "10minutemail.com", "mailinator.com"}
    domain = email.split('@')[-1].lower()
    if domain in blacklist_domains:
        errors.append("Email addresses from this domain are not allowed.")

    # Risultato finale
    if errors:
        return False, " ".join(errors)

    return True, ""
