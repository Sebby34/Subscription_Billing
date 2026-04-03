import os 

class DevelopmentConfig: 
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = True 
    CACHE_TYPE = "SimpleCache"
    SECRET_KEY = os.getenv("SECRET_KEY")

class TestingConfig: 
    pass 

class ProductionConfig: 
    pass 

