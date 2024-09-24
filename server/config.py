from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:port/db_name'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'k1@8F3z&@jL2n*Yq$RzP5s8#dU9pM3^91'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'k1@8F3z&@jL2n*Yq$RzP5s8#dU9pM3^91'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    TESTING = True