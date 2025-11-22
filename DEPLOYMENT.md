# Deployment Guide for Algo Trading Backtest App

This guide covers multiple deployment options for your Flask backtesting application.

## Prerequisites

1. Ensure your code is in a Git repository
2. Make sure `requirements.txt` is up to date
3. Test the app locally before deploying

---

## Option 1: Render (Recommended - Free Tier Available)

**Best for:** Quick deployment with free tier

### Steps:

1. **Sign up at [render.com](https://render.com)**

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Or use "Public Git repository" and paste your repo URL

3. **Configure the service:**
   - **Name:** algo-trading-backtest (or your choice)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn backtest_app:app`
   - **Plan:** Free (or paid for better performance)

4. **Add environment variables (if needed):**
   - Go to Environment tab
   - Add any required variables

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy

**Note:** Add `gunicorn` to your `requirements.txt`:
```
gunicorn>=21.2.0
```

---

## Option 2: Railway

**Best for:** Simple deployment with good free tier

### Steps:

1. **Sign up at [railway.app](https://railway.app)**

2. **Create a new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or upload code)

3. **Configure:**
   - Railway auto-detects Python apps
   - It will use your `requirements.txt`
   - Add start command: `gunicorn backtest_app:app --bind 0.0.0.0:$PORT`

4. **Deploy:**
   - Railway automatically deploys on git push
   - Get your URL from the dashboard

---

## Option 3: PythonAnywhere

**Best for:** Python-focused hosting with free tier

### Steps:

1. **Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)**

2. **Upload your code:**
   - Use the Files tab to upload your project
   - Or use Git: `git clone <your-repo-url>`

3. **Create a Web App:**
   - Go to Web tab
   - Click "Add a new web app"
   - Choose Flask and Python 3.10+
   - Set source code directory to your project folder

4. **Configure WSGI file:**
   - Edit the WSGI file to point to your app:
   ```python
   import sys
   path = '/home/yourusername/yourproject'
   if path not in sys.path:
       sys.path.append(path)
   
   from backtest_app import app as application
   ```

5. **Reload the web app**

---

## Option 4: DigitalOcean App Platform

**Best for:** Production apps with scaling

### Steps:

1. **Sign up at [digitalocean.com](https://www.digitalocean.com)**

2. **Create App:**
   - Go to App Platform
   - Connect GitHub repository
   - Select Python as runtime

3. **Configure:**
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn backtest_app:app`
   - Set environment variables if needed

4. **Deploy:**
   - DigitalOcean handles the rest
   - Get your app URL

---

## Option 5: VPS (DigitalOcean Droplet, Linode, etc.)

**Best for:** Full control and customization

### Steps:

1. **Create a VPS:**
   - DigitalOcean Droplet (Ubuntu 22.04)
   - Linode, Vultr, or similar
   - Minimum: 1GB RAM, 1 CPU

2. **SSH into your server:**
   ```bash
   ssh root@your-server-ip
   ```

3. **Install dependencies:**
   ```bash
   apt update
   apt install python3-pip python3-venv nginx git -y
   ```

4. **Clone your repository:**
   ```bash
   cd /var/www
   git clone <your-repo-url> algo-trading
   cd algo-trading
   ```

5. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

6. **Create systemd service:**
   ```bash
   nano /etc/systemd/system/algo-trading.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Algo Trading Backtest App
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/algo-trading
   Environment="PATH=/var/www/algo-trading/venv/bin"
   ExecStart=/var/www/algo-trading/venv/bin/gunicorn --workers 3 --bind unix:algo-trading.sock -m 007 backtest_app:app

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start the service:**
   ```bash
   systemctl start algo-trading
   systemctl enable algo-trading
   ```

8. **Configure Nginx:**
   ```bash
   nano /etc/nginx/sites-available/algo-trading
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/algo-trading/algo-trading.sock;
       }
   }
   ```

9. **Enable site and restart Nginx:**
   ```bash
   ln -s /etc/nginx/sites-available/algo-trading /etc/nginx/sites-enabled
   nginx -t
   systemctl restart nginx
   ```

10. **Set up SSL with Let's Encrypt:**
    ```bash
    apt install certbot python3-certbot-nginx
    certbot --nginx -d your-domain.com
    ```

---

## Required Changes for Production

### 1. Update `backtest_app.py`:

Change the last lines from:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

To:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 2. Add `gunicorn` to `requirements.txt`:
```
gunicorn>=21.2.0
```

### 3. Create `.env` file (if using environment variables):
```
FLASK_ENV=production
PORT=5000
```

---

## Quick Deploy Checklist

- [ ] Code is in Git repository
- [ ] `requirements.txt` is complete
- [ ] `gunicorn` added to requirements
- [ ] Debug mode set to `False` in production
- [ ] Tested locally
- [ ] Environment variables configured
- [ ] Domain name ready (optional)

---

## Troubleshooting

### App won't start:
- Check logs in your hosting platform
- Verify `gunicorn` is installed
- Check port configuration

### Import errors:
- Ensure all dependencies in `requirements.txt`
- Check Python version compatibility

### Timeout errors:
- Increase timeout in gunicorn config
- Optimize backtest calculations

---

## Recommended: Render or Railway

For easiest deployment, I recommend **Render** or **Railway**:
- Free tier available
- Automatic deployments from Git
- Easy to set up
- Good documentation

