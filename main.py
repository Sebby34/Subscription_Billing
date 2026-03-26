from dotenv import load_dotenv 
from app import create_app 
from app.models import db 


load_dotenv()

app = create_app("DevelopmentConfig")

with app.app_context(): 
    db.create_all()

app.run()





