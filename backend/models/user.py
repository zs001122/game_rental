"""
用户模型
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    balance = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)  # 账户余额
    lottery_chances = db.Column(db.Integer, default=0, nullable=False)  # 免費抽奖次数
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # 是否为管理员
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关联关系
    accounts = db.relationship('Account', backref='owner', lazy='dynamic', foreign_keys='Account.user_id')
    orders_as_renter = db.relationship('Order', backref='renter', lazy='dynamic', foreign_keys='Order.renter_id')
    orders_as_owner = db.relationship('Order', backref='account_owner', lazy='dynamic', foreign_keys='Order.owner_id')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'balance': float(self.balance),
            'lottery_chances': self.lottery_chances,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
