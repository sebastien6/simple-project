import os

from micro import app, db

db.create_all()

# Start flask server
app.run(host="0.0.0.0", debug=os.getenv('FLASK_DEBUG'))
