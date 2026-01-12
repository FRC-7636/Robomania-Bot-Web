source ./.venv/bin/activate
git pull
pip install --upgrade pip
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
rm -R /var/www/rwb/statics/CACHE
python3 manage.py compress
# Set proper permissions (by Gemini)
sudo find /var/www/rwb/statics/ -type d -exec chmod 755 {} \;
sudo find /var/www/rwb/statics/ -type f -exec chmod 644 {} \;
sudo systemctl restart rwb