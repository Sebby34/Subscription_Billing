from app.models import User
from app.extensions import ma 


# User Schemas 
class UserSchema(ma.SQLAlchemyAutoSchema): 
    class Meta: 
        model = User 

user_schema = UserSchema() 
users_schema = UserSchema(many = True)
login_schema = UserSchema(exclude = ["name", "role"])