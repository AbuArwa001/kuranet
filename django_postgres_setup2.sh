#!/bin/bash
# Django + PostgreSQL Auto-Setup Script for Ubuntu Servers (using system Gunicorn)
# Improved version with permission fixes
# Usage: sudo bash django_postgres_setup.sh
set -e  # Exit on error

# Verify root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

# Configuration - customize these variables
DB_NAME="kuranet_db"
DB_USER="kuranet_user"
DB_PASS="securepassword123"  # Change to a strong password
GITHUB_REPO="https://github.com/AbuArwa001/kuranet.git"
SERVER_IP=$(hostname -I | awk '{print $1}')
HOME_DIR="/home/ubuntu"
PROJECT_DIR="$HOME_DIR/kuranet"
SOCKET_FILE="$PROJECT_DIR/kuranet.sock"

echo "Starting Django + PostgreSQL setup on $SERVER_IP..."

# Update system and install dependencies
echo "Updating system and installing dependencies..."
apt-get update -y
apt-get upgrade -y 
apt-get install -y python3.10-venv python3-pip python3-dev libpq-dev postgresql postgresql-contrib git gunicorn

# Set up PostgreSQL
echo "Configuring PostgreSQL..."
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    systemctl start postgresql
fi

sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Clone GitHub repository
echo "Cloning GitHub repository..."
cd $HOME_DIR
if [ ! -d "$PROJECT_DIR" ]; then
    git clone $GITHUB_REPO
fi
chown -R ubuntu:ubuntu $PROJECT_DIR
cd $PROJECT_DIR

# Set up virtual environment
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    pip install gunicorn==21.2.0
else
    pip install django djangorestframework psycopg2-binary gunicorn==21.2.0
fi

# Configure Django settings
echo "Configuring Django database settings..."
sed -i "s/'NAME':.*/'NAME': '$DB_NAME',/" kuranet/settings.py
sed -i "s/'USER':.*/'USER': '$DB_USER',/" kuranet/settings.py
sed -i "s/'PASSWORD':.*/'PASSWORD': '$DB_PASS',/" kuranet/settings.py
sed -i "s/'HOST':.*/'HOST': 'localhost'/" kuranet/settings.py

# Add allowed hosts
sed -i "/ALLOWED_HOSTS/s/\[\]/['$SERVER_IP', 'localhost', '127.0.0.1']/" kuranet/settings.py

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Set up Gunicorn with proper permissions
echo "Configuring Gunicorn with proper permissions..."
# Ensure www-data is in ubuntu group
usermod -a -G ubuntu www-data

# Create directory for socket file with correct permissions
mkdir -p $(dirname $SOCKET_FILE)
chown ubuntu:www-data $(dirname $SOCKET_FILE)
chmod 775 $(dirname $SOCKET_FILE)

cat <<EOT > /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin:/usr/bin"
Environment="DJANGO_SETTINGS_MODULE=kuranet.settings"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --timeout 120 \
          --bind unix:$SOCKET_FILE \
          kuranet.wsgi:application

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl start gunicorn
systemctl enable gunicorn

# Set socket file permissions (will be created by Gunicorn)
echo "Waiting for socket file creation..."
for i in {1..10}; do
    if [ -S $SOCKET_FILE ]; then
        chown ubuntu:www-data $SOCKET_FILE
        chmod 660 $SOCKET_FILE
        break
    fi
    sleep 1
done

# Configure Nginx with proper permissions
echo "Configuring Nginx..."
cat <<EOT > /etc/nginx/sites-available/kuranet
server {
    listen 80;
    server_name $SERVER_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$SOCKET_FILE;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOT

ln -sf /etc/nginx/sites-available/kuranet /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
systemctl restart nginx

# Configure firewall
echo "Configuring firewall..."
ufw allow 'Nginx Full'

python manage.py collectstatic --noinput

echo ""
echo "============================================"
echo "Setup complete!"
echo "Django project: $PROJECT_DIR"
echo "Virtual environment: $PROJECT_DIR/.venv"
echo "PostgreSQL database: $DB_NAME"
echo "PostgreSQL user: $DB_USER"
echo "Access your site at: http://$SERVER_IP"
echo "Socket file: $SOCKET_FILE"
echo "============================================"