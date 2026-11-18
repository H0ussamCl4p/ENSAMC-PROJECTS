"""
Script de test pour vérifier la configuration email
"""
import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("="*70)
print("📧 TEST DE CONFIGURATION EMAIL")
print("="*70)

# Récupérer les variables
gmail_address = os.getenv('GMAIL_ADDRESS')
app_password = os.getenv('GMAIL_APP_PASSWORD')
from_name = os.getenv('FROM_NAME', 'Event Team')

print(f"\n📋 Configuration détectée :")
print(f"  Email     : {gmail_address}")
print(f"  Password  : {'*' * len(app_password) if app_password and app_password != 'your-app-password-here' else '❌ NON CONFIGURÉ'}")
print(f"  From Name : {from_name}")

# Vérifier si la configuration est complète
if not gmail_address or not app_password or app_password == 'your-app-password-here':
    print("\n❌ ERREUR : Configuration incomplète !")
    print("\n📝 Actions requises :")
    if not gmail_address:
        print("  - Ajoutez GMAIL_ADDRESS dans le fichier .env")
    if not app_password or app_password == 'your-app-password-here':
        print("  - Créez un mot de passe d'application Gmail")
        print("  - Ajoutez-le dans GMAIL_APP_PASSWORD du fichier .env")
    print("\n🔗 Guide : https://myaccount.google.com/apppasswords")
    print("\n💡 Lancez : python EMAIL_CONFIG_GUIDE.py")
    exit(1)

# Demander l'email de test
print("\n" + "="*70)
test_email = input("Entrez votre email pour recevoir le test (ou appuyez sur Entrée pour utiliser le même) : ").strip()
if not test_email:
    test_email = gmail_address

print(f"\n📤 Envoi d'un email de test à : {test_email}")
print("⏳ Connexion au serveur Gmail...")

try:
    # Créer le message
    msg = EmailMessage()
    msg['From'] = f"{from_name} <{gmail_address}>"
    msg['To'] = test_email
    msg['Subject'] = "✅ Test de Configuration - Système de Tickets"
    
    # Contenu du message
    body = f"""Bonjour !

Ce message confirme que votre configuration email fonctionne correctement ! 🎉

Configuration testée :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Email expéditeur : {gmail_address}
Nom d'affichage  : {from_name}
Serveur SMTP     : smtp.gmail.com:465 (SSL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Vous pouvez maintenant générer et envoyer des tickets !

Commandes disponibles :
  python generate_tickets.py              # Générer avec envoi email
  python generate_tickets.py --no-email   # Générer sans email

Bon événement ! 🎫
— Système de Tickets ADE NOVA
"""
    
    body_html = f"""<!doctype html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background: #f6f7fb; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 30px 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 30px 20px; }}
        .info-box {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; }}
        .footer {{ background: #f9fafb; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
        .success {{ color: #16a34a; font-size: 48px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="success">✅</div>
            <h1>Configuration Email Réussie !</h1>
        </div>
        <div class="content">
            <p>Bonjour !</p>
            <p>Ce message confirme que votre configuration email fonctionne correctement ! 🎉</p>
            
            <div class="info-box">
                <strong>Configuration testée :</strong><br>
                <strong>Email expéditeur :</strong> {gmail_address}<br>
                <strong>Nom d'affichage :</strong> {from_name}<br>
                <strong>Serveur SMTP :</strong> smtp.gmail.com:465 (SSL)
            </div>
            
            <p><strong>✅ Vous pouvez maintenant générer et envoyer des tickets !</strong></p>
            
            <p><strong>Commandes disponibles :</strong></p>
            <ul>
                <li><code>python generate_tickets.py</code> - Générer avec envoi email</li>
                <li><code>python generate_tickets.py --no-email</code> - Générer sans email</li>
            </ul>
            
            <p>Bon événement ! 🎫</p>
        </div>
        <div class="footer">
            Système de Tickets - ADE NOVA ENSAM Casablanca
        </div>
    </div>
</body>
</html>"""
    
    msg.set_content(body)
    msg.add_alternative(body_html, subtype='html')
    
    # Envoyer l'email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(gmail_address, app_password)
        server.send_message(msg)
    
    print("\n" + "="*70)
    print("✅ EMAIL ENVOYÉ AVEC SUCCÈS !")
    print("="*70)
    print(f"\n📬 Vérifiez votre boîte de réception : {test_email}")
    print("   (Vérifiez aussi le dossier Spam si vous ne le voyez pas)")
    print("\n🎉 Configuration email opérationnelle !")
    print("\n📝 Vous pouvez maintenant :")
    print("   1. Générer des tickets : python generate_tickets.py")
    print("   2. Les tickets seront envoyés automatiquement par email")
    print("\n" + "="*70)

except smtplib.SMTPAuthenticationError:
    print("\n" + "="*70)
    print("❌ ERREUR D'AUTHENTIFICATION")
    print("="*70)
    print("\n🔐 Le mot de passe d'application est incorrect.")
    print("\n📝 Actions à faire :")
    print("   1. Allez sur : https://myaccount.google.com/apppasswords")
    print("   2. Créez un nouveau mot de passe d'application")
    print("   3. Copiez-le SANS ESPACES")
    print("   4. Remplacez GMAIL_APP_PASSWORD dans le fichier .env")
    print("\n💡 Assurez-vous que :")
    print("   - La vérification en 2 étapes est activée")
    print("   - Vous utilisez un mot de passe d'application (pas votre mot de passe Gmail)")
    print("   - Il n'y a pas d'espaces dans le mot de passe")

except smtplib.SMTPException as e:
    print("\n" + "="*70)
    print("❌ ERREUR SMTP")
    print("="*70)
    print(f"\nDétails : {e}")
    print("\n💡 Vérifiez votre connexion internet")

except Exception as e:
    print("\n" + "="*70)
    print("❌ ERREUR INATTENDUE")
    print("="*70)
    print(f"\nDétails : {e}")
    print("\n💡 Vérifiez le guide : python EMAIL_CONFIG_GUIDE.py")
