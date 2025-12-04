"""
订单模型
"""
from datetime import datetime
from backend.models.user import db

class Order(db.Model):
    """订单表"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 订单编号
    
    # 关联信息
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 租赁方
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 出租方
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)  # 账号
    
    # 金额信息
    rental_amount = db.Column(db.Numeric(10, 2), nullable=False)  # 租金
    deposit_amount = db.Column(db.Numeric(10, 2), nullable=False)  # 押金
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)  # 总金额（租金+押金）
    
    # 订单状态
    status = db.Column(db.String(20), default='pending', nullable=False)  
    # pending: 待支付, renting: 正在租赁(已支付), completed: 已组赁(已完成), cancelled: 已取消
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)  # 支付时间
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 备注
    remarks = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'renter_id': self.renter_id,
            'owner_id': self.owner_id,
            'account_id': self.account_id,
            'rental_amount': float(self.rental_amount),
            'deposit_amount': float(self.deposit_amount),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'paid_at': self.paid_at.strftime('%Y-%m-%d %H:%M:%S') if self.paid_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'remarks': self.remarks
        }
