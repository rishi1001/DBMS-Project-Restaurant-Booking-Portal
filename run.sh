# . venv/bin/activate
export FLASK_APP=app
export FLASK_ENV=development
kill -9 $(lsof -i:5054)
flask run -p 5054