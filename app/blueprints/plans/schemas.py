from app.models import Plan 
from app.extensions import ma 


class PlanSchema(ma.SQLAlchemyAutoSchema): 
    class Meta: 
        model = Plan 

plan_schema = PlanSchema() 
plans_schema = PlanSchema(many = True)