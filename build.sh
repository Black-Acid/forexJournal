set -o errexit

pip install -r requirements.txt
git 

python manage.py collectstatic --noinput

python manage.py migrate