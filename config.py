import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """공통 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    REFRESH_SECRET_KEY = os.environ.get('REFRESH_SECRET_KEY', 'default-refresh-key')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """개발 환경"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProductionConfig(Config):
    """운영 환경"""
    DEBUG = False
    # 운영 환경에서는 반드시 환경변수에서 실제 DB 주소를 가져옵니다.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REFRESH_SECRET_KEY = os.environ.get('REFRESH_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}
