import requests
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from datetime import datetime
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# .enc file
load_dotenv()

# for the localhost (http://)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# flask credentials
app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('SECRET_KEY')

# discord credentials
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
DISCORD_API_BASE_URL = 'https://discord.com/api'
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# google credentials
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
GOOGLE_AUTH_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

# ensure that user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_user' not in session and 'google_user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/discord')
def discord_login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify")

@app.route('/callback')
def discord_callback():
    code = request.args.get('code')
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(f"{DISCORD_API_BASE_URL}/oauth2/token", data=data, headers=headers)
    response.raise_for_status()
    tokens = response.json()

    # get user info
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}"
    }
    response = requests.get(f"{DISCORD_API_BASE_URL}/users/@me", headers=headers)
    response.raise_for_status()
    user = response.json()

    session['discord_user'] = user
    return redirect(url_for('dashboard'))

@app.route('/login/google')
def google_login():
    google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=GOOGLE_REDIRECT_URI, scope=['openid', 'email', 'profile'])
    authorization_url, state = google.authorization_url(GOOGLE_AUTH_BASE_URL, access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/google/callback')
def google_callback():
    if 'oauth_state' not in session:
        return redirect(url_for('login'))
    google = OAuth2Session(GOOGLE_CLIENT_ID, state=session['oauth_state'], redirect_uri=GOOGLE_REDIRECT_URI)
    google.fetch_token(GOOGLE_TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url)

    # fetch the user info
    response = google.get(GOOGLE_USERINFO_URL)
    user_info = response.json()
    user_email = user_info.get('email')
    user_avatar = user_info.get('picture')

    session['google_user'] = {'email': user_email, 'avatar_url': user_avatar}
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = session.get('discord_user') or session.get('google_user')
    return render_template('index.html', user=user)

@app.route('/logout')
@login_required
def logout():
    session.pop('discord_user', None)
    session.pop('google_user', None)
    return redirect(url_for('index'))

@app.route('/uploaded_files', methods=['GET'])
@login_required
def get_uploaded_files():
    files_with_id = [
        {**file, 'id': idx} for idx, file in enumerate(uploaded_files)
    ]
    return jsonify(files_with_id)

# global variable for uploaded files
uploaded_files = []

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    webhook_url = 'https://discord.com/api/webhooks/1225077084485845132/ZuylmrCsQgasy6-95E3Y-j7vH2WnAyAptBMORih94ERLWlvTHCbqZV7RrYL4WslInz_3'

    if 'file' not in request.files:
        return jsonify(error='ფაილი არ ატვირთულა'), 400

    file = request.files['file']
    file_bytes = file.read()
    MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB limit

    if file and len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return jsonify(error='ფაილის ზომა მიუღებელია'), 400

    if not webhook_url:
        return jsonify(error='ვერ ვუკავშირდები დისქროდს'), 400

    if not file_bytes:
        return jsonify(error='აირჩიეთ სხვა ფაილი'), 400

    # user info
    uploader_ip = request.remote_addr
    file_name = file.filename
    file_size = len(file_bytes)
    user = session.get('discord_user') or session.get('google_user')
    uploader_name = user.get('username', user.get('email', 'Unknown'))

    # get the avatar based on the provider (dc or google)
    if 'discord_user' in session:
        avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}"
    elif 'google_user' in session:
        avatar_url = user.get('picture')
    else:
        avatar_url = ''

    # format file size
    if file_size >= 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"
    else:
        size_str = f"{file_size / 1024:.2f} KB"

    # create the embed
    embed = {
        "title": ":inbox_tray: NEW FILE UPLOADED :inbox_tray:",
        "thumbnail": {
            "url": avatar_url
        },
        "color": 65295,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {
                "name": "Uploaded by",
                "value": f"`{uploader_name}`",
                "inline": True
            },
            {
                "name": "IP address",
                "value": f"`{uploader_ip}`",
                "inline": True
            },
            {
                "name": "File Name",
                "value": f"`{file_name}`",
                "inline": False
            },
            {
                "name": "File Size",
                "value": f"`{size_str}`",
                "inline": False
            }
        ]
    }

    # add the user thing to the embed if logged in with dc
    if 'discord_user' in session:
        embed['fields'].append({
            "name": "Discord User",
            "value": f"<@{user['id']}>",
            "inline": True
        })

    try:
        # send embed
        embed_response = requests.post(webhook_url, json={"embeds": [embed]})
        embed_response.raise_for_status()

        # send file
        file_response = requests.post(webhook_url, files={'file': (file.filename, file_bytes)})
        file_response.raise_for_status()

        # file details
        uploaded_files.append({
            "file_name": file_name,
            "file_size": file_size,
            "upload_time": datetime.utcnow().isoformat(),
            "channel_id": DISCORD_CHANNEL_ID,
            "attachment_id": file_response.json()['attachments'][0]['id']
        })

        return jsonify(success='ფაილი წარმატებით აიტვირთა')

    except requests.exceptions.RequestException as e:
        return jsonify(error=f'ფაილის ატვირთვისას დაფიქსირდა პრობლემა. {str(e)}'), 500

def generate_download_link(channel_id, attachment_id, attachment_name):
    return f"https://cdn.discordapp.com/attachments/{channel_id}/{attachment_id}/{attachment_name}"

# handle file downloads
@app.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    if file_id < 0 or file_id >= len(uploaded_files):
        return jsonify(error='ფაილი ვერ მოიძებნა'), 404

    file_info = uploaded_files[file_id]
    download_link = generate_download_link(file_info['channel_id'], file_info['attachment_id'], file_info['file_name'])
    return jsonify(download_link=download_link)

if __name__ == '__main__':
    app.run(debug=True)
