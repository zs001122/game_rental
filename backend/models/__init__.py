"""
模型初始化文件
"""
from backend.models.user import db, User
from backend.models.account import Account
from backend.models.order import Order

__all__ = ['db', 'User', 'Account', 'Order']
