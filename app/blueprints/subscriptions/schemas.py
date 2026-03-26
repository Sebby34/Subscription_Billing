from app.models import Subscription 
from app.extensions import ma 


class SubscriptionSchema(ma.SQLAlchemyAutoSchema): 
    class Meta: 
        model = Subscription
        include_fk = True 
        load_instance = True

subscription_schema = SubscriptionSchema() 
subscriptions_schema = SubscriptionSchema(many = True)
