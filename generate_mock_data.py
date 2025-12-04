"""
生成模拟数据脚本
"""
import sys
sys.path.insert(0, '/home/ubuntu/game_rental_platform')

from backend.app import create_app
from backend.models import db, User, Account, Order
from datetime import datetime, timedelta
import random

# 刀皮列表
KNIFE_SKINS = ['北极星', '黑海', '赤霄怜悯', '影锋', '信条']

# 区服列表
SERVER_REGIONS = ['华东一区', '华东二区', '华南一区', '华南二区', '华北一区', '华北二区', '西南一区', '西南二区']

# 段位列表
RANKS = ['青铜', '白银', '黄金', '铂金', '钻石', '大师', '王者']

# 常用地列表
LOCATIONS = ['上海', '北京', '广州', '深圳', '成都', '杭州', '南京', '武汉', '西安', '重庆']

def generate_users(count=20):
    """生成用户数据"""
    users = []
    
    # 创建管理员账户
    admin = User(
        username='admin',
        email='admin@example.com',
        phone='13800000000',
        balance=0.00,
        is_admin=True
    )
    admin.set_password('admin123')
    users.append(admin)
    print(f"创建管理员账户: admin (密码: admin123)")
    
    # 创建普通用户
    for i in range(1, count + 1):
        user = User(
            username=f'user{i:03d}',
            email=f'user{i:03d}@example.com',
            phone=f'138{i:08d}',
            balance=round(random.uniform(100, 10000), 2),
            is_admin=False
        )
        user.set_password('123456')
        users.append(user)
    
    print(f"创建了 {count} 个普通用户 (密码: 123456)")
    return users

def generate_accounts(users, count=50):
    """生成账号数据"""
    accounts = []
    
    # 排除管理员
    non_admin_users = [u for u in users if not u.is_admin]
    
    for i in range(1, count + 1):
        # 随机选择一个用户作为账号所有者
        owner = random.choice(non_admin_users)
        
        # 随机保险箱格数
        safe_box_slots = random.choice([4, 6, 9])
        
        # 随机刀皮（0-5个）
        knife_count = random.randint(0, len(KNIFE_SKINS))
        knife_skins = random.sample(KNIFE_SKINS, knife_count) if knife_count > 0 else []
        
        # 随机资产
        pure_coin_assets = round(random.uniform(10, 500), 2)
        total_assets = round(pure_coin_assets * random.uniform(1.1, 2.0), 2)
        
        # 随机等级
        level = random.randint(20, 100)
        
        # 计算租金（基于纯币资产：纯币资产 × 100 ÷ 比例）
        ratio_map = {9: 38, 6: 40, 4: 42}
        ratio = ratio_map[safe_box_slots]
        rental_price = round(pure_coin_assets * 100 / ratio, 2)
        
        # 押金（与租金相同或略高）
        deposit = round(rental_price * 30, 2)
        
        account = Account(
            user_id=owner.id,
            account_number=f'ACC{datetime.now().year}{i:05d}',
            collection_time=f'{random.randint(1, 12)}月{random.randint(1, 28)}日',
            login_time=f'{random.randint(8, 22)}:00-{random.randint(8, 22)}:00',
            common_location=random.choice(LOCATIONS),
            server_region=random.choice(SERVER_REGIONS),
            login_method=random.choice(['账密登录', '扫码登录', '账密/扫码']),
            face_verification=random.choice(['已认证', '未认证']),
            rank=random.choice(RANKS),
            total_assets=total_assets,
            pure_coin_assets=pure_coin_assets,
            level=level,
            stamina_level=random.randint(1, 50),
            safe_box_slots=safe_box_slots,
            aw_bullets=random.randint(0, 1000),
            knife_skins=knife_skins,
            price=rental_price,
            deposit=deposit,
            remarks=f'这是一个测试账号，编号{i}',
            status='available'
        )
        accounts.append(account)
    
    print(f"创建了 {count} 个游戏账号")
    return accounts

def generate_orders(users, accounts, count=30):
    """生成订单数据"""
    orders = []
    
    # 排除管理员
    non_admin_users = [u for u in users if not u.is_admin]
    
    # 只选择可用的账号
    available_accounts = [a for a in accounts if a.status == 'available']
    
    if len(available_accounts) < count:
        count = len(available_accounts)
    
    selected_accounts = random.sample(available_accounts, count)
    
    for i, account in enumerate(selected_accounts, 1):
        # 随机选择租赁方（不能是账号所有者）
        possible_renters = [u for u in non_admin_users if u.id != account.user_id]
        renter = random.choice(possible_renters)
        
        # 计算金额
        rental_amount = account.calculate_order_amount()
        deposit_amount = float(account.deposit)
        total_amount = rental_amount + deposit_amount
        
        # 随机订单状态
        status = random.choice(['pending', 'renting', 'completed'])
        
        # 创建时间（最近30天内）
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        order = Order(
            order_number=f'ORD{created_at.strftime("%Y%m%d%H%M%S")}{i:04d}',
            renter_id=renter.id,
            owner_id=account.user_id,
            account_id=account.id,
            rental_amount=rental_amount,
            deposit_amount=deposit_amount,
            total_amount=total_amount,
            status=status,
            created_at=created_at
        )
        
        # 根据状态设置时间
        if status in ['renting', 'completed']:
            order.paid_at = created_at + timedelta(minutes=random.randint(1, 60))
            # 更新账号状态
            if status == 'renting':
                account.status = 'rented'
        
        if status == 'completed':
            order.completed_at = order.paid_at + timedelta(days=random.randint(1, 7))
            account.status = 'available'
        
        orders.append(order)
    
    print(f"创建了 {count} 个订单")
    return orders

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建成功！")
        
        # 清空现有数据
        print("\n正在清空现有数据...")
        Order.query.delete()
        Account.query.delete()
        User.query.delete()
        db.session.commit()
        print("现有数据已清空！")
        
        # 生成用户
        print("\n正在生成用户数据...")
        users = generate_users(20)
        db.session.add_all(users)
        db.session.commit()
        
        # 生成账号
        print("\n正在生成账号数据...")
        accounts = generate_accounts(users, 50)
        db.session.add_all(accounts)
        db.session.commit()
        
        # 生成订单
        print("\n正在生成订单数据...")
        orders = generate_orders(users, accounts, 30)
        db.session.add_all(orders)
        db.session.commit()
        
        print("\n" + "="*50)
        print("模拟数据生成完成！")
        print("="*50)
        print(f"用户总数: {User.query.count()}")
        print(f"账号总数: {Account.query.count()}")
        print(f"订单总数: {Order.query.count()}")
        print("\n登录信息：")
        print("管理员账号: admin / admin123")
        print("普通用户账号: user001-user020 / 123456")
        print("="*50)

if __name__ == '__main__':
    main()
