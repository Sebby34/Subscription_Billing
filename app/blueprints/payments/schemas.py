from app.models import Payment 
from app.extensions import ma 


class PaymentSchema(ma.SQLAlchemyAutoSchema): 
    class Meta: 
        model = Payment 
        include_fk = True
        load_instance = True

payment_schema = PaymentSchema() 
payments_schema = PaymentSchema(many = True)
