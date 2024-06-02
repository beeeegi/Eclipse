# Eclipse
Eclipse is a web application that allows users to securely log in using either their Discord or Google accounts and upload files. Uploaded files are sent to a Discord channel using a webhook, and users can view and download their uploaded files through the web interface.

## Developer notes
I am not primarily a GUI developer, so the graphical user interface in this project sucks. The application has been tested locally, and its behavior on a live web server is unknown. Due to recent changes in Discord's CDN authentication mechanism, attachment URLs now include three new parameters: ex, is, and hm. These changes are intended to improve security but will affect how attachment URLs are managed in this application. So I can't really make a downloadable files with this project, the script is written BEFORE the changes were applied to the cdn links so it may not work.

## Setup and Installation
`1.` Clone the repository
```bash
git clone https://github.com/beeeegi/Eclipse
```

`2.` Install requirements
```bash
cd eclipse
pip install -r requirements.txt
```

`3.` Create a `.env` File
Put it in the root directory and paste this in the file:
```env
SECRET_KEY=your_secret_key

DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:5000/callback
DISCORD_CHANNEL_ID=your_discord_channel_id

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/google/callback
```

`4.` Run the application with:
```bash
python3 app.py
```
You can access the app with this link: `http://localhost:5000`

## Usage
### Authentication
You have two options here: Google or Discord
### File Upload
After logging in, you will be presented with an option to upload a file or view the library.
In the library section, you have option to download the file again or view file's name, size and the upload date.

## Screenshots
![image](https://github.com/beeeegi/Eclipse/assets/102294103/0080687d-ec8d-4405-b421-8cb8a3f49df6)
![image](https://github.com/beeeegi/Eclipse/assets/102294103/480a0d8e-3b5f-45ad-b890-6f5c2a04b93a)


