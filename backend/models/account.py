"""
游戏账号模型
"""
from datetime import datetime
from backend.models.user import db

class Account(db.Model):
    """游戏账号表"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 基础信息
    account_number = db.Column(db.String(50), unique=True, nullable=False)  # 编号
    collection_time = db.Column(db.String(50), nullable=True)  # 收号时间
    login_time = db.Column(db.String(50), nullable=True)  # 上号时间
    common_location = db.Column(db.String(100), nullable=True)  # 常用地
    server_region = db.Column(db.String(50), nullable=True)  # 区服
    login_method = db.Column(db.String(100), nullable=True)  # 账密或扫码
    face_verification = db.Column(db.String(50), nullable=True)  # 本人人脸
    rank = db.Column(db.String(50), nullable=True)  # 段位
    
    # 资产信息
    total_assets = db.Column(db.Numeric(10, 2), nullable=True)  # 总资产(m)
    pure_coin_assets = db.Column(db.Numeric(10, 2), nullable=False)  # 纯币资产(m)
    level = db.Column(db.Integer, nullable=True)  # 等级
    stamina_level = db.Column(db.Integer, nullable=True)  # 体力等级
    safe_box_slots = db.Column(db.Integer, nullable=False)  # 保险箱格数(4/6/9)
    aw_bullets = db.Column(db.Integer, nullable=True)  # aw子弹
    
    # 刀皮信息 (多选，使用JSON存储)
    knife_skins = db.Column(db.JSON, nullable=True)  # 持有刀皮：北极星、黑海、赤霄怜悯、影锋、信条
    
    # 价格信息
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 价格
    deposit = db.Column(db.Numeric(10, 2), nullable=False)  # 押金
    
    # 其他信息
    remarks = db.Column(db.Text, nullable=True)  # 备注
    status = db.Column(db.String(20), default='available', nullable=False)  # 状态：available, rented, unavailable
    
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关联关系
    orders = db.relationship('Order', backref='account', lazy='dynamic')
    
    def calculate_order_amount(self):
        """计算订单金额：纯币资产 × 100 ÷ 比例"""
        ratio_map = {9: 38, 6: 40, 4: 42}
        ratio = ratio_map.get(self.safe_box_slots, 40)
        return float(self.pure_coin_assets) * 100 / ratio
    
    def calculate_deposit(self):
        """计算押金：租金的30%"""
        rental_amount = self.calculate_order_amount()
        return round(rental_amount * 0.3, 2)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_number': self.account_number,
            'collection_time': self.collection_time,
            'login_time': self.login_time,
            'common_location': self.common_location,
            'server_region': self.server_region,
            'login_method': self.login_method,
            'face_verification': self.face_verification,
            'rank': self.rank,
            'total_assets': float(self.total_assets) if self.total_assets else None,
            'pure_coin_assets': float(self.pure_coin_assets),
            'level': self.level,
            'stamina_level': self.stamina_level,
            'safe_box_slots': self.safe_box_slots,
            'aw_bullets': self.aw_bullets,
            'knife_skins': self.knife_skins,
            'price': float(self.price),
            'deposit': float(self.deposit),
            'remarks': self.remarks,
            'status': self.status,
            'order_amount': self.calculate_order_amount(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
