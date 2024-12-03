set -o errexit

pip install -r requirements.txt
pip install MetaTrader5

python manage.py collectstatic --noinput

python manage.py migrate