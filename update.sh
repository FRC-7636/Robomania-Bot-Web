source ./.venv/bin/activate
git pull
pip install --upgrade pip
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
rm -R web_static/CACHE
python3 manage.py compress
sudo systemctl restart roboweb