import os
import base64
import requests  # <--- Zorg dat deze import bovenaan staat!
from flask import Flask, render_template_string, request
import hvac

app = Flask(__name__)

# Configuratie ophalen
VAULT_URL = os.getenv('VAULT_ADDR')
VAULT_TOKEN = os.getenv('VAULT_TOKEN')
client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)

HTML_PAGE = """
<!doctype html>
<html style="font-family: sans-serif; padding: 2rem;">
<head><title>Vault Weather App</title></head>
<body>
    <h1>Deel 5: Key & Secrets Management</h1>
    
    <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2>Deel 5.A: Het weer in Antwerpen</h2>
        <form action="/get-info" method="post">
            <button type="submit">Haal weer op</button>
        </form>
        {% if api_result %}
            <p><strong>Resultaat:</strong> {{ api_result | safe }}</p>
        {% endif %}
    </div>

    <div style="background: #e8f5e9; padding: 20px; border-radius: 8px;">
        <h2>Deel 5.B: Encryption Service</h2>
        <form action="/encrypt" method="post">
            <input type="text" name="plaintext" placeholder="Tekst..." required>
            <button type="submit">Encrypt</button>
        </form>
        {% if encrypted_text %}
            <p><strong>Ciphertext:</strong><br><code>{{ encrypted_text }}</code></p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/get-info', methods=['POST'])
def get_info():
    try:
        # 1. Haal de API key uit Vault
        secret_resp = client.secrets.kv.v2.read_secret_version(mount_point='secret', path='weather_api')
        real_api_key = secret_resp['data']['data']['apikey']

        # 2. HIER IS DE WIJZIGING: Gebruik de key direct!
        # We checken NIET meer op "12345...", we gebruiken hem gewoon.
        city = "Antwerp"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={real_api_key}&units=metric"
        
        r = requests.get(url)
        
        if r.status_code == 200:
            data = r.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return render_template_string(HTML_PAGE, api_result=f"✅ Het is {temp}°C in {city} met {desc}.")
        elif r.status_code == 401:
            return render_template_string(HTML_PAGE, api_result=f"❌ Fout 401: Key '{real_api_key}' is nog niet actief of ongeldig.")
        else:
            return render_template_string(HTML_PAGE, api_result=f"❌ API Fout: {r.status_code}")

    except Exception as e:
        return render_template_string(HTML_PAGE, api_result=f"Systeem Fout: {str(e)}")

@app.route('/encrypt', methods=['POST'])
def encrypt_text():
    try:
        plaintext = request.form['plaintext']
        plaintext_b64 = base64.b64encode(plaintext.encode()).decode('utf-8')
        response = client.secrets.transit.encrypt_data(name='container-key', plaintext=plaintext_b64)
        return render_template_string(HTML_PAGE, encrypted_text=response['data']['ciphertext'])
    except Exception as e:
        return render_template_string(HTML_PAGE, encrypted_text=f"Fout: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
