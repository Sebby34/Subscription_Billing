from app.models import Invoice 
from app.extensions import ma 


class InvoiceSchema(ma.SQLAlchemyAutoSchema): 
    class Meta: 
        model = Invoice 
        include_fk = True
        load_instance = True

invoice_schema = InvoiceSchema() 
invoices_schema = InvoiceSchema(many = True)