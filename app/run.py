#!flask/bin/python

# Import app variable from our app package
from app import create_app

app_instance = create_app()
app_instance.run(debug=True)
