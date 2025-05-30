from flask import Flask, request, jsonify, redirect, render_template_string
import requests
import json
import time
import uuid
import hashlib
from datetime import datetime

app = Flask(__name__)

# Configuration mock
DEVELOPMENT_MODE = True
mock_payments = {}
mock_tokens = {}

class MockOrangeAPI:
    @staticmethod
    def get_token():
        """Simuler l'obtention d'un token"""
        token = f"mock_token_{uuid.uuid4().hex[:16]}"
        mock_tokens[token] = time.time()
        return {"access_token": token, "expires_in": 3600}
    
    @staticmethod
    def create_payment(data):
        """Simuler la création d'un paiement"""
        pay_token = f"mock_pay_{uuid.uuid4().hex[:10]}"
        
        mock_payments[pay_token] = {
            'order_id': data['order_id'],
            'amount': data['amount'],
            'currency': data['currency'],
            'status': 'PENDING',
            'created_at': time.time(),
            'notif_url': data.get('notif_url'),
            'return_url': data.get('return_url'),
            'cancel_url': data.get('cancel_url')
        }
        
        return {
            'pay_token': pay_token,
            'payment_url': f"{request.url_root}mock-payment/{pay_token}",
            'status': 'SUCCESS'
        }

@app.route('/')
def home():
    return """
    <h1>🧡 Orange Money Middleware - Mode DEV</h1>
    <p>✅ Service en cours d'exécution</p>
    <p><a href="/test-payment" style="background: #ff7900; color: white; padding: 10px; text-decoration: none; border-radius: 5px;">🧪 Tester un paiement</a></p>
    <p><small>Mode: Développement avec Mock API</small></p>
    """

@app.route('/test-payment')
def test_payment():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Orange Money</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            input, button { padding: 10px; margin: 5px 0; width: 100%; }
            button { background: #ff7900; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #e56a00; }
        </style>
    </head>
    <body>
        <h2>🧪 Test de paiement Orange Money</h2>
        <form action="/create-payment" method="post">
            <label>💰 Montant (MGA):</label>
            <input type="number" name="amount" value="5000" required>
            
            <label>💱 Devise:</label>
            <input type="text" name="currency" value="MGA" required>
            
            <label>📋 ID Commande:</label>
            <input type="text" name="order_id" value="SO001" required>
            
            <label>📱 Téléphone client:</label>
            <input type="text" name="customer_phone" value="+261340000000">
            
            <button type="submit">🚀 Créer le paiement</button>
        </form>
    </body>
    </html>
    """

@app.route('/create-payment', methods=['POST'])
def create_payment():
    """Endpoint principal pour Odoo"""
    try:
        # Récupérer les données
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        print(f"📥 Demande de paiement reçue: {data}")
        
        # Validation
        required = ['amount', 'currency', 'order_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Champ manquant: {field}'}), 400
        
        # Simuler l'API Orange Money
        mock_api = MockOrangeAPI()
        
        # Obtenir le token
        token_result = mock_api.get_token()
        print(f"🔑 Token obtenu: {token_result['access_token'][:20]}...")
        
        # Créer le paiement
        payment_data = {
            'amount': data['amount'],
            'currency': data['currency'],
            'order_id': data['order_id'],
            'notif_url': f"{request.url_root}payment-notification",
            'return_url': f"{request.url_root}payment-success",
            'cancel_url': f"{request.url_root}payment-cancel"
        }
        
        payment_result = mock_api.create_payment(payment_data)
        print(f"💳 Paiement créé: {payment_result['pay_token']}")
        
        # Réponse
        if request.is_json:
            return jsonify({
                'success': True,
                'payment_url': payment_result['payment_url'],
                'pay_token': payment_result['pay_token']
            })
        else:
            return redirect(payment_result['payment_url'])
            
    except Exception as e:
        error_msg = f"Erreur: {str(e)}"
        print(f"❌ {error_msg}")
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            return f"<h2>❌ Erreur</h2><p>{error_msg}</p>", 500

@app.route('/mock-payment/<pay_token>')
def mock_payment_page(pay_token):
    """Page de paiement Orange Money simulée"""
    if pay_token not in mock_payments:
        return "❌ Paiement non trouvé", 404
    
    payment = mock_payments[pay_token]
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Orange Money - Paiement</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #ff7900, #ff9500); 
                color: white; 
                padding: 20px; 
                margin: 0;
            }}
            .container {{ 
                max-width: 400px; 
                margin: 50px auto; 
                background: white; 
                color: black; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            h2 {{ color: #ff7900; text-align: center; }}
            .amount {{ font-size: 24px; font-weight: bold; color: #ff7900; text-align: center; margin: 20px 0; }}
            button {{ 
                background: #ff7900; 
                color: white; 
                padding: 15px 20px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                margin: 5px; 
                width: calc(50% - 10px);
                font-size: 14px;
                font-weight: bold;
            }}
            button:hover {{ background: #e56a00; }}
            .cancel {{ background: #dc3545; }}
            .cancel:hover {{ background: #c82333; }}
            .info {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧡 Orange Money</h2>
            <div class="info">
                <p><strong>💰 Montant:</strong> {payment['amount']} {payment['currency']}</p>
                <p><strong>📋 Commande:</strong> {payment['order_id']}</p>
                <p><strong>🏪 Marchand:</strong> Odoo E-commerce</p>
            </div>
            
            <div class="amount">{payment['amount']} {payment['currency']}</div>
            
            <p style="text-align: center; color: #666;">Choisissez le résultat du paiement :</p>
            
            <div style="text-align: center;">
                <button onclick="simulatePayment('SUCCESS')">✅ Paiement Réussi</button>
                <button onclick="simulatePayment('FAILED')" class="cancel">❌ Paiement Échoué</button>
            </div>
            
            <div style="text-align: center; margin-top: 15px;">
                <button onclick="simulatePayment('CANCELLED')" class="cancel" style="width: 100%;">🚫 Annuler le paiement</button>
            </div>
            
            <p style="text-align: center; font-size: 12px; color: #999; margin-top: 20px;">
                🧪 Mode Développement - Simulation Orange Money
            </p>
        </div>
        
        <script>
            function simulatePayment(status) {{
                fetch('/process-mock-payment/{pay_token}', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{'status': status}})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.redirect_url) {{
                        window.location.href = data.redirect_url;
                    }}
                }})
                .catch(error => {{
                    console.error('Erreur:', error);
                    alert('Erreur lors du traitement du paiement');
                }});
            }}
        </script>
    </body>
    </html>
    """

@app.route('/process-mock-payment/<pay_token>', methods=['POST'])
def process_mock_payment(pay_token):
    """Traiter le résultat du paiement simulé"""
    if pay_token not in mock_payments:
        return jsonify({'error': 'Paiement non trouvé'}), 404
    
    data = request.get_json()
    status = data.get('status', 'FAILED')
    
    payment = mock_payments[pay_token]
    payment['status'] = status
    payment['processed_at'] = time.time()
    
    if status == 'SUCCESS':
        payment['txnid'] = f"TXN{uuid.uuid4().hex[:8].upper()}"
    
    print(f"💳 Paiement {pay_token} traité: {status}")
    
    # Envoyer la notification (simulée)
    if payment.get('notif_url'):
        notification_data = {
            'order_id': payment['order_id'],
            'status': status,
            'txnid': payment.get('txnid', ''),
            'amount': payment['amount'],
            'currency': payment['currency']
        }
        
        try:
            # Auto-notification vers notre propre endpoint
            requests.post(
                payment['notif_url'], 
                json=notification_data, 
                timeout=5
            )
            print(f"📡 Notification envoyée: {notification_data}")
        except Exception as e:
            print(f"⚠️ Erreur notification: {e}")
    
    # URL de redirection
    if status == 'SUCCESS':
        redirect_url = payment.get('return_url', '/payment-success')
    else:
        redirect_url = payment.get('cancel_url', '/payment-cancel')
    
    return jsonify({'redirect_url': redirect_url})

@app.route('/payment-notification', methods=['POST'])
def payment_notification():
    """Webhook pour les notifications Orange Money"""
    try:
        if request.is_json:
            notification = request.get_json()
        else:
            notification = json.loads(request.get_data().decode('utf-8'))
        
        print(f"📥 NOTIFICATION REÇUE: {notification}")
        
        # ICI : Mettre à jour Odoo (à implémenter)
        order_id = notification.get('order_id')
        status = notification.get('status')
        txnid = notification.get('txnid')
        
        print(f"📋 Commande {order_id} -> {status} (ID: {txnid})")
        
        # TODO: Appeler l'API Odoo pour mettre à jour
        
        return jsonify({'status': 'received', 'message': 'Notification traitée'}), 200
        
    except Exception as e:
        print(f"❌ Erreur notification: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/payment-success')
def payment_success():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paiement Réussi</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: #d4edda; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #155724; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Paiement Réussi !</h1>
            <p>Votre paiement Orange Money a été traité avec succès.</p>
            <p>Vous allez recevoir un SMS de confirmation.</p>
            <button onclick="window.close()" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Fermer</button>
        </div>
    </body>
    </html>
    """

@app.route('/payment-cancel')
def payment_cancel():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paiement Annulé</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: #f8d7da; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❌ Paiement Annulé</h1>
            <p>Votre paiement Orange Money a été annulé ou a échoué.</p>
            <p>Vous pouvez réessayer ou choisir un autre mode de paiement.</p>
            <button onclick="window.close()" style="background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Fermer</button>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'mode': 'development_mock',
        'payments_count': len(mock_payments),
        'tokens_count': len(mock_tokens)
    })

if __name__ == '__main__':
    print("🚀 Démarrage du middleware Orange Money...")
    print("📋 Mode: Développement avec Mock API")
    print("🌐 Interface: http://localhost:5000")
    print("🧪 Test: http://localhost:5000/test-payment")
    app.run(debug=True, host='0.0.0.0', port=5000)
