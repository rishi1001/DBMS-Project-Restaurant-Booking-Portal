# . venv/bin/activate
export FLASK_APP=app
export FLASK_ENV=development
kill -9 $(lsof -i:5045)
flask run -p 5045