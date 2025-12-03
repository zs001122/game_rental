"""
数据库配置文件
"""
import os
import tempfile

class Config:
    """应用配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置 - 使用SQLite
    # 在Vercel中，使用临时目录避免文件系统限制
    if os.environ.get('VERCEL'):
        # Vercel环境：使用内存数据库或临时目录
        DATABASE_PATH = os.path.join(tempfile.gettempdir(), 'game_rental.db')
    else:
        # 本地开发环境
        BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        DATABASE_PATH = os.path.join(BASE_DIR, 'game_rental.db')
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # 会话配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24小时
