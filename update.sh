source ./.venv/bin/activate
git pull
pip install --upgrade pip
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
killall uwsgi