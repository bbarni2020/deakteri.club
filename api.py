from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import smtplib
import email.mime.text
import email.mime.multipart
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import jwt
from functools import wraps

load_dotenv()

app = Flask(__name__)

allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:7896,http://127.0.0.1:7896,http://localhost:8000,http://127.0.0.1:8000').split(',')

if os.getenv('DEBUG', 'False').lower() == 'true':
    CORS(app, origins="*", supports_credentials=True, 
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
else:
    CORS(app, origins=allowed_origins, supports_credentials=True, 
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SPONSORS_FILE = 'sponsors.json'
DONATORS_FILE = 'donators.json'
INVOICE_SUBMISSIONS_FILE = 'invoice_submissions.json'
RECURRING_SPONSORS_FILE = 'recurring_sponsors.json'
HACKCLUB_REGISTRATIONS_FILE = 'hackclub_registrations.json'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'deakteri2025')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'deakteri-hackclub-secret-2025')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'email': os.getenv('EMAIL_USER'),
    'password': os.getenv('EMAIL_PASSWORD'),
    'recipient': os.getenv('RECIPIENT_EMAIL', 'hackclub@deakteri.hu')
}

def admin_required(f):
    """Decorator to require admin authentication for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header missing'}), 401
        
        try:
            if not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'error': 'Invalid authorization header format'}), 401
            
            token = auth_header.split(' ')[1]
            
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            
            if payload.get('role') != 'admin':
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def load_data(filename):
    """Load data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return []

def save_data(filename, data):
    """Save data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

def send_email(subject, body, recipient=None, is_html=False):
    """Send email notification"""
    try:
        if not EMAIL_CONFIG['email'] or not EMAIL_CONFIG['password']:
            logger.warning("Email credentials not configured")
            return False
            
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = recipient or EMAIL_CONFIG['recipient']
        msg['Subject'] = subject
        
        text_type = 'html' if is_html else 'plain'
        msg.attach(email.mime.text.MIMEText(body, text_type, 'utf-8'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {msg['To']}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def calculate_next_due_date(frequency, start_date=None):
    """Calculate next due date based on frequency"""
    if start_date is None:
        start_date = datetime.now()
    elif isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    if frequency == 'weekly':
        return start_date + timedelta(weeks=1)
    elif frequency == 'monthly':
        return start_date + timedelta(days=30)
    elif frequency == 'quarterly':
        return start_date + timedelta(days=90)
    elif frequency == 'yearly':
        return start_date + timedelta(days=365)
    else:
        return start_date + timedelta(days=30)

def generate_confirmation_email_html(name, class_name, age, readable_interests):
    """Generate HTML confirmation email for Hack Club registration"""
    interests_html = ''.join([f'<li style="color: #4ecdc4; margin-bottom: 8px; font-weight: 500;">• {interest}</li>' for interest in readable_interests])
    
    return f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hack Club Jelentkezés Megerősítés</title>
    <link rel="icon" href="https://deakteri.club/icon.ico" type="image/x-icon">
</head>
<body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: linear-gradient(135deg, #1a1a3e 0%, #2d1b69 50%, #0a0a23 100%); min-height: 100vh;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #45b7d1 100%); padding: 40px 30px; text-align: center; position: relative;">
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 30% 70%, rgba(255,255,255,0.1) 0%, transparent 50%); pointer-events: none;"></div>
            <div style="position: relative; z-index: 2;">
                <img src="https://deakteri.club/icon.png" alt="Hack Club Icon" style="width: 64px; height: 64px; margin-bottom: 15px; filter: drop-shadow(0 0 20px rgba(255,255,255,0.3));" />
                <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 700; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                    Hack Club Jelentkezés
                </h1>
                <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 500;">
                    Sikeres regisztráció! 🎉
                </p>
            </div>
        </div>
        
        <div style="padding: 40px 30px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #2d1b69; font-size: 24px; font-weight: 700; margin: 0 0 10px 0;">
                    Szia {name}! 👋
                </h2>
                <p style="color: #666; font-size: 16px; line-height: 1.6; margin: 0;">
                    Köszönjük a jelentkezésedet a <strong>Deáktéri Hack Club</strong>-ba!
                </p>
            </div>
            
            <div style="background: linear-gradient(145deg, rgba(78, 205, 196, 0.05) 0%, rgba(69, 183, 209, 0.05) 100%); border: 2px solid rgba(78, 205, 196, 0.2); border-radius: 15px; padding: 25px; margin-bottom: 30px;">
                <h3 style="color: #4ecdc4; font-size: 18px; font-weight: 600; margin: 0 0 20px 0; text-align: center;">
                    📋 Jelentkezésed összesítése
                </h3>
                
                <div style="display: grid; gap: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(78, 205, 196, 0.1);">
                        <span style="color: #666; font-weight: 500;">Név:</span>
                        <span style="color: #2d1b69; font-weight: 600;"> {name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(78, 205, 196, 0.1);">
                        <span style="color: #666; font-weight: 500;">Osztály:</span>
                        <span style="color: #2d1b69; font-weight: 600;"> {class_name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(78, 205, 196, 0.1);">
                        <span style="color: #666; font-weight: 500;">Kor:</span>
                        <span style="color: #2d1b69; font-weight: 600;"> {age} év</span>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4 style="color: #4ecdc4; font-size: 16px; font-weight: 600; margin: 0 0 15px 0;">
                        🎯 Érdeklődési területeid:
                    </h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        {interests_html}
                    </ul>
                </div>
            </div>
            
            <div style="background: linear-gradient(145deg, rgba(236, 55, 80, 0.05) 0%, rgba(255, 107, 138, 0.05) 100%); border: 2px solid rgba(236, 55, 80, 0.2); border-radius: 15px; padding: 25px; margin-bottom: 30px;">
                <h3 style="color: #ec3750; font-size: 18px; font-weight: 600; margin: 0 0 20px 0; text-align: center;">
                    🚀 Mi következik?
                </h3>
                
                <div style="color: #666; line-height: 1.7;">
                    <div style="display: flex; align-items: flex-start; margin-bottom: 15px;">
                        <span style="color: #ec3750; font-size: 18px; margin-right: 10px; margin-top: 2px;">📅</span>
                        <span>Még irunk egy emailt a találkozó előtt.</span>
                    </div>
                    <div style="display: flex; align-items: flex-start;">
                        <span style="color: #ec3750; font-size: 18px; margin-right: 10px; margin-top: 2px;">💻</span>
                        <span>Készülj fel menő projektekre és közös alkotásra!</span>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-bottom: 30px;">
                <a href="https://hackclub.com" style="display: inline-block; background: linear-gradient(45deg, #4ecdc4, #45b7d1); color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3); transition: all 0.3s ease;">
                    🌐 Fedezd fel a Hack Club-ot
                </a>
            </div>
            
            <div style="background: #f8f9fa; border-radius: 10px; padding: 20px; text-align: center;">
                <h4 style="color: #2d1b69; font-size: 16px; font-weight: 600; margin: 0 0 15px 0;">
                    📧 Kérdésed van?
                </h4>
                <p style="color: #666; margin: 0 0 15px 0; line-height: 1.6;">
                    Ha bármilyen kérdésed van, írj nekünk bizalommal!
                </p>
                <a href="mailto:contact@deakteri.club" style="color: #4ecdc4; text-decoration: none; font-weight: 600;">
                    contact@deakteri.club
                </a>
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #2d1b69 0%, #1a1a3e 100%); padding: 30px; text-align: center;">
            <div style="margin-bottom: 20px;">
                <img src="https://deakteri.club/icon.png" alt="Hack Club Icon" style="width: 48px; height: 48px;" />
            </div>
            <h3 style="color: white; font-size: 18px; font-weight: 600; margin: 0 0 10px 0;">
                Deák Téri Evangélikus Gimnázium Hack Club
            </h3>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                <a href="https://hackclub.com" style="color: #4ecdc4; text-decoration: none; font-size: 14px;">
                    🌐 Hack Club  
                </a>
                <a href="mailto:contact@deakteri.club" style="color: #4ecdc4; text-decoration: none; font-size: 14px;">
                    📧 Kapcsolat
                </a>
            </div>
        </div>
    </div>
    
    <style>
        @media only screen and (max-width: 600px) {{
            body {{
                padding: 0 !important;
            }}
            
            .container {{
                width: 100% !important;
                padding: 0 !important;
            }}
            
            .content {{
                padding: 30px 20px !important;
            }}
            
            .header {{
                padding: 30px 20px !important;
            }}
            
            .card {{
                padding: 20px !important;
                margin-bottom: 20px !important;
            }}
            
            .footer {{
                padding: 20px !important;
            }}
            
            h1 {{
                font-size: 24px !important;
            }}
            
            h2 {{
                font-size: 20px !important;
            }}
            
            .stats {{
                flex-direction: column !important;
            }}
        }}
    </style>
</body>
</html>
    """.strip()

def generate_admin_notification_email_html(name, email, class_name, age, readable_interests):
    """Generate HTML admin notification email for Hack Club registration"""
    interests_html = ''.join([f'<li style="color: #4ecdc4; margin-bottom: 5px;">• {interest}</li>' for interest in readable_interests])
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Új Hack Club Jelentkezés</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #ec3750 0%, #d63447 100%); padding: 30px; text-align: center;">
            <div style="font-size: 36px; margin-bottom: 10px;">🎯</div>
            <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">
                Új Hack Club Jelentkezés
            </h1>
            <p style="margin: 5px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">
                {timestamp}
            </p>
        </div>
        
        <div style="padding: 30px;">
            <div style="margin-bottom: 25px;">
                <h2 style="color: #ec3750; font-size: 20px; font-weight: 600; margin: 0 0 15px 0;">
                    👤 Jelentkező adatok
                </h2>
                
                <div style="background: #f8f9fa; border-radius: 10px; padding: 20px;">
                    <div style="display: grid; gap: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                            <span style="color: #666; font-weight: 500;">Név:</span>
                            <span style="color: #2d1b69; font-weight: 600;">{name}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                            <span style="color: #666; font-weight: 500;">Email:</span>
                            <a href="mailto:{email}" style="color: #4ecdc4; text-decoration: none; font-weight: 600;">{email}</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                            <span style="color: #666; font-weight: 500;">Osztály:</span>
                            <span style="color: #2d1b69; font-weight: 600;">{class_name}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
                            <span style="color: #666; font-weight: 500;">Kor:</span>
                            <span style="color: #2d1b69; font-weight: 600;">{age} év</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #4ecdc4; font-size: 16px; font-weight: 600; margin: 0 0 15px 0;">
                    🎯 Érdeklődési területek:
                </h3>
                <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.2); border-radius: 8px; padding: 15px;">
                    <ul style="list-style: none; padding: 0; margin: 0; color: #333;">
                        {interests_html}
                    </ul>
                </div>
            </div>
            
            <div style="background: linear-gradient(145deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 10px; padding: 20px; text-align: center;">
                <h3 style="color: #ff6b00; font-size: 16px; font-weight: 600; margin: 0 0 10px 0;">
                    ⚡ Teendő
                </h3>
                <p style="color: #666; margin: 0; line-height: 1.5;">
                    Vedd fel a kapcsolatot a jelentkezővel és add hozzá a Discord szerverhez vagy értesítsd az első találkozó időpontjáról.
                </p>
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
            <p style="margin: 0; color: #666; font-size: 12px;">
                Ez egy automatikus értesítés a Deáktéri Hack Club regisztrációs rendszerből.
            </p>
            <div style="margin-top: 10px;">
                <a href="http://localhost:7896/dashboard.html" style="color: #4ecdc4; text-decoration: none; font-size: 12px; font-weight: 500;">
                    📊 Admin Dashboard
                </a>
            </div>
        </div>
    </div>
</body>
</html>
    """.strip()

def check_and_notify_due_recurring_sponsors():
    """Check for due recurring sponsors and send email notifications"""
    try:
        recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
        now = datetime.now()
        
        due_sponsors = []
        for sponsor in recurring_sponsors:
            if sponsor.get('status') == 'active':
                next_due = datetime.fromisoformat(sponsor['next_due_date'].replace('Z', '+00:00'))
                if next_due <= now:
                    due_sponsors.append(sponsor)
        
        if due_sponsors:
            subject = f"Ismétlődő szponzorok fizetése esedékes - {len(due_sponsors)} sponsor"
            
            body = "A következő ismétlődő szponzorok fizetése esedékes:\n\n"
            for sponsor in due_sponsors:
                body += f"- {sponsor['companyName']} ({sponsor['contactEmail']})\n"
                body += f"  Összeg: ${sponsor['amount']} USD\n"
                body += f"  Gyakoriság: {sponsor['frequency']}\n"
                body += f"  Esedékesség: {sponsor['next_due_date']}\n\n"
            
            body += "\nKérjük, ellenőrizzék az admin panelt és jelöljék meg teljesítettként a beérkezett fizetéseket."
            
            send_email(subject, body)
            logger.info(f"Notification sent for {len(due_sponsors)} due recurring sponsors")
        
        return due_sponsors
        
    except Exception as e:
        logger.error(f"Error checking due recurring sponsors: {e}")
        return []

@app.route('/api/sponsors', methods=['GET'])
def get_sponsors():
    """Get list of sponsors"""
    try:
        sponsors = load_data(SPONSORS_FILE)
        return jsonify({
            'success': True,
            'sponsors': sponsors,
            'count': len(sponsors)
        })
    except Exception as e:
        logger.error(f"Error getting sponsors: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/donators', methods=['GET'])
def get_donators():
    """Get list of personal donators"""
    try:
        donators = load_data(DONATORS_FILE)
        return jsonify({
            'success': True,
            'donators': donators,
            'count': len(donators)
        })
    except Exception as e:
        logger.error(f"Error getting donators: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sponsors', methods=['POST'])
@admin_required
def add_sponsor():
    """Add new sponsor (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'logo_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        sponsors = load_data(SPONSORS_FILE)
        
        new_sponsor = {
            'id': len(sponsors) + 1,
            'name': data['name'],
            'logo_url': data['logo_url'],
            'website': data.get('website', ''),
            'added_date': datetime.now().isoformat()
        }
        
        sponsors.append(new_sponsor)
        
        if save_data(SPONSORS_FILE, sponsors):
            logger.info(f"New sponsor added: {new_sponsor['name']}")
            return jsonify({'success': True, 'sponsor': new_sponsor})
        else:
            return jsonify({'success': False, 'error': 'Failed to save sponsor'}), 500
            
    except Exception as e:
        logger.error(f"Error adding sponsor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/donators', methods=['POST'])
@admin_required
def add_donator():
    """Add new donator (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        donators = load_data(DONATORS_FILE)
        
        new_donator = {
            'id': len(donators) + 1,
            'name': data['name'],
            'amount': data['amount'],
            'currency': 'USD',
            'message': data.get('message', ''),
            'anonymous': data.get('anonymous', False),
            'added_date': datetime.now().isoformat()
        }
        
        donators.append(new_donator)
        
        if save_data(DONATORS_FILE, donators):
            logger.info(f"New donator added: {new_donator['name']}")
            return jsonify({'success': True, 'donator': new_donator})
        else:
            return jsonify({'success': False, 'error': 'Failed to save donator'}), 500
            
    except Exception as e:
        logger.error(f"Error adding donator: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/invoice', methods=['POST'])
def submit_invoice():
    """Handle invoice form submission"""
    try:
        data = request.get_json()
        
        required_fields = ['companyName', 'contactEmail', 'streetAddress', 'city', 'zip', 'country', 'amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        is_recurring = data.get('sponsorshipType') == 'recurring'
        frequency = data.get('frequency', '') if is_recurring else ''
        
        subject = f"Számlázási kérelem - {data['companyName']}"
        
        body = f"""
Új számlázási kérelem érkezett a Deáktéri Hack Club weboldalról.

SZPONZOR ADATOK:
===============
Név/Cégnév: {data['companyName']}
Kapcsolattartó email: {data['contactEmail']}
Utca, házszám: {data['streetAddress']}
Emelet/Iroda: {data.get('suite', 'Nincs megadva')}
Város: {data['city']}
Megye/Állam: {data.get('state', 'Nincs megadva')}
Irányítószám: {data['zip']}
Ország: {data['country']}

SZÁMLÁZÁSI RÉSZLETEK:
===================
Támogatás típusa: {'Ismétlődő' if is_recurring else 'Egyszeri'}
{f'Gyakoriság: {frequency}' if frequency else ''}
Összeg: ${data['amount']} USD

IDŐBÉLYEG:
=========
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Kérjük, vegyék fel a kapcsolatot a fenti email címen a számlázási folyamat megkezdéséhez.
        """.strip()
        
        email_sent = send_email(subject, body)
        
        logger.info(f"Invoice request submitted by {data['companyName']} ({data['contactEmail']}) for ${data['amount']} - {'Recurring' if is_recurring else 'One-time'}")
        
        try:
            submissions = load_data(INVOICE_SUBMISSIONS_FILE)
            
            submission = {
                'id': len(submissions) + 1,
                'timestamp': datetime.now().isoformat(),
                'email_sent': email_sent,
                'is_recurring': is_recurring,
                'frequency': frequency,
                **data
            }
            
            submissions.append(submission)
            save_data(INVOICE_SUBMISSIONS_FILE, submissions)
            
            if is_recurring and frequency:
                recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
                
                recurring_sponsor = {
                    'id': len(recurring_sponsors) + 1,
                    'submission_id': submission['id'],
                    'companyName': data['companyName'],
                    'contactEmail': data['contactEmail'],
                    'amount': data['amount'],
                    'frequency': frequency,
                    'status': 'pending',
                    'created_date': datetime.now().isoformat(),
                    'next_due_date': None,
                    'total_payments': 0,
                    'last_payment_date': None,
                    'full_data': data
                }
                
                recurring_sponsors.append(recurring_sponsor)
                save_data(RECURRING_SPONSORS_FILE, recurring_sponsors)
                
                logger.info(f"Recurring sponsor added to pending list: {data['companyName']}")
                
        except Exception as e:
            logger.error(f"Error saving submission backup: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Számlázási kérelem sikeresen elküldve!',
            'email_sent': email_sent,
            'is_recurring': is_recurring
        })
        
    except Exception as e:
        logger.error(f"Error processing invoice submission: {e}")
        return jsonify({'success': False, 'error': 'Hiba történt a kérelem feldolgozása során'}), 500

@app.route('/api/sponsors/<int:sponsor_id>', methods=['DELETE'])
@admin_required
def delete_sponsor(sponsor_id):
    """Delete a sponsor by ID"""
    try:
        sponsors = load_data(SPONSORS_FILE)
        
        sponsor_to_delete = None
        for i, sponsor in enumerate(sponsors):
            if sponsor.get('id') == sponsor_id:
                sponsor_to_delete = sponsors.pop(i)
                break
        
        if sponsor_to_delete is None:
            return jsonify({'success': False, 'error': 'Sponsor not found'}), 404
        
        save_data(SPONSORS_FILE, sponsors)
        
        logger.info(f"Sponsor deleted: {sponsor_to_delete['name']} (ID: {sponsor_id})")
        
        return jsonify({
            'success': True,
            'message': f'Sponsor "{sponsor_to_delete["name"]}" successfully deleted',
            'deleted_sponsor': sponsor_to_delete
        })
        
    except Exception as e:
        logger.error(f"Error deleting sponsor {sponsor_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete sponsor'}), 500

@app.route('/api/donators/<int:donator_id>', methods=['DELETE'])
@admin_required
def delete_donator(donator_id):
    """Delete a donator by ID"""
    try:
        donators = load_data(DONATORS_FILE)
        
        donator_to_delete = None
        for i, donator in enumerate(donators):
            if donator.get('id') == donator_id:
                donator_to_delete = donators.pop(i)
                break
        
        if donator_to_delete is None:
            return jsonify({'success': False, 'error': 'Donator not found'}), 404
        
        save_data(DONATORS_FILE, donators)
        
        logger.info(f"Donator deleted: {donator_to_delete['name']} (ID: {donator_id})")
        
        return jsonify({
            'success': True,
            'message': f'Donator "{donator_to_delete["name"]}" successfully deleted',
            'deleted_donator': donator_to_delete
        })
        
    except Exception as e:
        logger.error(f"Error deleting donator {donator_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete donator'}), 500

@app.route('/api/auth/login', methods=['POST'])
def admin_login():
    """Authenticate admin user and return JWT token"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password == ADMIN_PASSWORD:
            payload = {
                'role': 'admin',
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'token': token
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid password'
            }), 401
            
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return jsonify({'success': False, 'error': 'Authentication failed'}), 500

@app.route('/api/invoice-submissions', methods=['GET'])
@admin_required
def get_invoice_submissions():
    """Get all invoice submissions"""
    try:
        submissions = load_data(INVOICE_SUBMISSIONS_FILE)
        return jsonify({
            'success': True,
            'submissions': submissions
        })
    except Exception as e:
        logger.error(f"Error fetching invoice submissions: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch invoice submissions'}), 500

@app.route('/api/invoice-submissions/<int:submission_id>', methods=['DELETE'])
@admin_required
def mark_invoice_done(submission_id):
    """Mark invoice submission as done and delete it"""
    try:
        submissions = load_data(INVOICE_SUBMISSIONS_FILE)
        
        submission_to_delete = None
        for i, submission in enumerate(submissions):
            if submission.get('id') == submission_id:
                submission_to_delete = submissions.pop(i)
                break
        
        if submission_to_delete is None:
            return jsonify({'success': False, 'error': 'Invoice submission not found'}), 404
        
        save_data(INVOICE_SUBMISSIONS_FILE, submissions)
        
        logger.info(f"Invoice submission marked as done and deleted: {submission_to_delete['companyName']} (ID: {submission_id})")
        
        return jsonify({
            'success': True,
            'message': f'Invoice submission for "{submission_to_delete["companyName"]}" marked as done',
            'deleted_submission': submission_to_delete
        })
        
    except Exception as e:
        logger.error(f"Error marking invoice submission as done {submission_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to mark invoice submission as done'}), 500

@app.route('/api/recurring-sponsors', methods=['GET'])
@admin_required
def get_recurring_sponsors():
    """Get all recurring sponsors"""
    try:
        check_and_notify_due_recurring_sponsors()
        
        recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
        return jsonify({
            'success': True,
            'recurring_sponsors': recurring_sponsors
        })
    except Exception as e:
        logger.error(f"Error fetching recurring sponsors: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch recurring sponsors'}), 500

@app.route('/api/recurring-sponsors/<int:sponsor_id>/activate', methods=['POST'])
@admin_required
def activate_recurring_sponsor(sponsor_id):
    """Activate a pending recurring sponsor and set first due date"""
    try:
        recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
        
        sponsor_to_activate = None
        for sponsor in recurring_sponsors:
            if sponsor.get('id') == sponsor_id:
                sponsor_to_activate = sponsor
                break
        
        if sponsor_to_activate is None:
            return jsonify({'success': False, 'error': 'Recurring sponsor not found'}), 404
        
        now = datetime.now()
        sponsor_to_activate['status'] = 'active'
        sponsor_to_activate['last_payment_date'] = now.isoformat()
        sponsor_to_activate['total_payments'] = 1
        sponsor_to_activate['next_due_date'] = calculate_next_due_date(
            sponsor_to_activate['frequency'], now
        ).isoformat()
        
        save_data(RECURRING_SPONSORS_FILE, recurring_sponsors)
        
        logger.info(f"Recurring sponsor activated: {sponsor_to_activate['companyName']} (ID: {sponsor_id})")
        
        return jsonify({
            'success': True,
            'message': f'Recurring sponsor "{sponsor_to_activate["companyName"]}" activated',
            'sponsor': sponsor_to_activate
        })
        
    except Exception as e:
        logger.error(f"Error activating recurring sponsor {sponsor_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to activate recurring sponsor'}), 500

@app.route('/api/recurring-sponsors/<int:sponsor_id>/payment', methods=['POST'])
@admin_required
def record_recurring_payment(sponsor_id):
    """Record a payment for a recurring sponsor and update next due date"""
    try:
        recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
        
        sponsor = None
        for s in recurring_sponsors:
            if s.get('id') == sponsor_id:
                sponsor = s
                break
        
        if sponsor is None:
            return jsonify({'success': False, 'error': 'Recurring sponsor not found'}), 404
        
        if sponsor['status'] != 'active':
            return jsonify({'success': False, 'error': 'Sponsor is not active'}), 400
        
        now = datetime.now()
        sponsor['last_payment_date'] = now.isoformat()
        sponsor['total_payments'] = sponsor.get('total_payments', 0) + 1
        sponsor['next_due_date'] = calculate_next_due_date(
            sponsor['frequency'], now
        ).isoformat()
        
        save_data(RECURRING_SPONSORS_FILE, recurring_sponsors)
        
        logger.info(f"Payment recorded for recurring sponsor: {sponsor['companyName']} (ID: {sponsor_id})")
        
        return jsonify({
            'success': True,
            'message': f'Payment recorded for "{sponsor["companyName"]}"',
            'sponsor': sponsor
        })
        
    except Exception as e:
        logger.error(f"Error recording payment for recurring sponsor {sponsor_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to record payment'}), 500

@app.route('/api/recurring-sponsors/<int:sponsor_id>/status', methods=['PUT'])
@admin_required
def update_recurring_sponsor_status(sponsor_id):
    """Update status of a recurring sponsor (active, paused, cancelled)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['active', 'paused', 'cancelled']:
            return jsonify({'success': False, 'error': 'Invalid status. Must be active, paused, or cancelled'}), 400
        
        recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
        
        sponsor = None
        for s in recurring_sponsors:
            if s.get('id') == sponsor_id:
                sponsor = s
                break
        
        if sponsor is None:
            return jsonify({'success': False, 'error': 'Recurring sponsor not found'}), 404
        
        old_status = sponsor['status']
        sponsor['status'] = new_status
        sponsor['status_updated'] = datetime.now().isoformat()
        
        save_data(RECURRING_SPONSORS_FILE, recurring_sponsors)
        
        logger.info(f"Recurring sponsor status updated: {sponsor['companyName']} (ID: {sponsor_id}) - {old_status} -> {new_status}")
        
        return jsonify({
            'success': True,
            'message': f'Sponsor status updated to {new_status}',
            'sponsor': sponsor
        })
        
    except Exception as e:
        logger.error(f"Error updating recurring sponsor status {sponsor_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to update sponsor status'}), 500

@app.route('/api/recurring-sponsors/<int:sponsor_id>', methods=['DELETE'])
@admin_required
def delete_recurring_sponsor(sponsor_id):
    """Delete a recurring sponsor"""
    try:
        recurring_sponsors = load_data(RECURRING_SPONSORS_FILE)
        
        sponsor_to_delete = None
        for i, sponsor in enumerate(recurring_sponsors):
            if sponsor.get('id') == sponsor_id:
                sponsor_to_delete = recurring_sponsors.pop(i)
                break
        
        if sponsor_to_delete is None:
            return jsonify({'success': False, 'error': 'Recurring sponsor not found'}), 404
        
        save_data(RECURRING_SPONSORS_FILE, recurring_sponsors)
        
        logger.info(f"Recurring sponsor deleted: {sponsor_to_delete['companyName']} (ID: {sponsor_id})")
        
        return jsonify({
            'success': True,
            'message': f'Recurring sponsor "{sponsor_to_delete["companyName"]}" deleted',
            'deleted_sponsor': sponsor_to_delete
        })
        
    except Exception as e:
        logger.error(f"Error deleting recurring sponsor {sponsor_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete recurring sponsor'}), 500

@app.route('/api/hackclub-register', methods=['POST'])
def hackclub_register():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'class', 'age', 'interests']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        if not isinstance(data['interests'], list) or len(data['interests']) == 0:
            return jsonify({'success': False, 'error': 'At least one interest must be selected'}), 400

        interest_mapping = {
            'coding': 'Kódolás (webek, appok, játékok)',
            '3d': '3D Design (Autodesk Fusion)',
            'content': 'Content Creation (videók, social media)'
        }
        
        readable_interests = [interest_mapping.get(interest, interest) for interest in data['interests']]
        
        student_subject = "Jelentkezésed a Deáktéri Hack Club-ba sikeresen elküldve! 🎉"
        
        # Generate HTML email for student
        student_html_body = generate_confirmation_email_html(
            name=data['name'],
            class_name=data['class'],
            age=data['age'],
            readable_interests=readable_interests
        )
        
        # Generate HTML admin notification email
        admin_subject = f"Új Hack Club jelentkezés - {data['name']}"
        admin_html_body = generate_admin_notification_email_html(
            name=data['name'],
            email=data['email'],
            class_name=data['class'],
            age=data['age'],
            readable_interests=readable_interests
        )
        
        # Send emails
        admin_email_sent = send_email(admin_subject, admin_html_body, EMAIL_CONFIG['recipient'], is_html=True)
        student_email_sent = send_email(student_subject, student_html_body, data['email'], is_html=True)

        try:
            registrations = load_data(HACKCLUB_REGISTRATIONS_FILE)
            
            registration = {
                'id': len(registrations) + 1,
                'timestamp': datetime.now().isoformat(),
                'name': data['name'],
                'email': data['email'],
                'class': data['class'],
                'age': data['age'],
                'interests': data['interests'],
                'readable_interests': readable_interests,
                'admin_email_sent': admin_email_sent,
                'student_email_sent': student_email_sent,
                'status': 'registered'
            }
            
            registrations.append(registration)
            save_data(HACKCLUB_REGISTRATIONS_FILE, registrations)
            
            logger.info(f"New Hack Club registration: {data['name']} ({data['email']}) - {', '.join(data['interests'])}")
            
        except Exception as e:
            logger.error(f"Error saving registration: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Siker! Köszönjük {data["name"]}, hogy jelentkeztél! Hamarosan felvesszük veled a kapcsolatot.',
            'admin_email_sent': admin_email_sent,
            'student_email_sent': student_email_sent
        })
        
    except Exception as e:
        logger.error(f"Error processing Hack Club registration: {e}")
        return jsonify({'success': False, 'error': 'Hiba történt a jelentkezés feldolgozása során'}), 500

@app.route('/api/hackclub-registrations', methods=['GET'])
@admin_required
def get_hackclub_registrations():
    try:
        registrations = load_data(HACKCLUB_REGISTRATIONS_FILE)
        return jsonify({
            'success': True,
            'registrations': registrations,
            'count': len(registrations)
        })
    except Exception as e:
        logger.error(f"Error fetching Hack Club registrations: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch registrations'}), 500

@app.route('/api/hackclub-registrations/<int:registration_id>', methods=['DELETE'])
@admin_required
def delete_hackclub_registration(registration_id):
    try:
        registrations = load_data(HACKCLUB_REGISTRATIONS_FILE)
        
        registration_to_delete = None
        for i, registration in enumerate(registrations):
            if registration.get('id') == registration_id:
                registration_to_delete = registrations.pop(i)
                break
        
        if registration_to_delete is None:
            return jsonify({'success': False, 'error': 'Registration not found'}), 404
        
        save_data(HACKCLUB_REGISTRATIONS_FILE, registrations)
        
        logger.info(f"Hack Club registration deleted: {registration_to_delete['name']} (ID: {registration_id})")
        
        return jsonify({
            'success': True,
            'message': f'Registration for "{registration_to_delete["name"]}" deleted',
            'deleted_registration': registration_to_delete
        })
        
    except Exception as e:
        logger.error(f"Error deleting Hack Club registration {registration_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete registration'}), 500

@app.route('/api/hackclub-registrations/<int:registration_id>/status', methods=['PUT'])
@admin_required
def update_hackclub_registration_status(registration_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['registered', 'contacted', 'confirmed', 'declined']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        registrations = load_data(HACKCLUB_REGISTRATIONS_FILE)
        
        registration = None
        for r in registrations:
            if r.get('id') == registration_id:
                registration = r
                break
        
        if registration is None:
            return jsonify({'success': False, 'error': 'Registration not found'}), 404
        
        old_status = registration.get('status', 'registered')
        registration['status'] = new_status
        registration['status_updated'] = datetime.now().isoformat()
        
        save_data(HACKCLUB_REGISTRATIONS_FILE, registrations)
        
        logger.info(f"Hack Club registration status updated: {registration['name']} (ID: {registration_id}) - {old_status} -> {new_status}")
        
        return jsonify({
            'success': True,
            'message': f'Registration status updated to {new_status}',
            'registration': registration
        })
        
    except Exception as e:
        logger.error(f"Error updating registration status {registration_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to update registration status'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Deáktéri Hack Club API is running',
        'timestamp': datetime.now().isoformat()
    })
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'success': True})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    if not os.path.exists(SPONSORS_FILE):
        save_data(SPONSORS_FILE, [])
    
    if not os.path.exists(DONATORS_FILE):
        save_data(DONATORS_FILE, [])
        
    if not os.path.exists(INVOICE_SUBMISSIONS_FILE):
        save_data(INVOICE_SUBMISSIONS_FILE, [])
    
    if not os.path.exists(HACKCLUB_REGISTRATIONS_FILE):
        save_data(HACKCLUB_REGISTRATIONS_FILE, [])
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Deáktéri Hack Club API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
