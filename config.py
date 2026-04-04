import os 

class DevelopmentConfig: 
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = True 
    CACHE_TYPE = "SimpleCache"
    SECRET_KEY = os.getenv("SECRET_KEY")

class TestingConfig: 
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory"
    TESTING = True 
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    SECRET_KEY = "testsecret123"

class ProductionConfig: 
    pass 

