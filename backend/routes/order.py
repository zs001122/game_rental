"""
订单管理路由
"""
from flask import Blueprint, request, jsonify, session
from backend.models import db, Order, Account, User
from datetime import datetime
import uuid
from decimal import Decimal

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['GET'])
def get_orders():
    """获取订单列表"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    order_type = request.args.get('type', 'all')  # all, rented, owned
    
    # 构建查询
    if order_type == 'rented':
        # 我租赁的订单
        query = Order.query.filter_by(renter_id=user_id)
    elif order_type == 'owned':
        # 我出租的订单
        query = Order.query.filter_by(owner_id=user_id)
    else:
        # 所有相关订单
        query = Order.query.filter(
            (Order.renter_id == user_id) | (Order.owner_id == user_id)
        )
    
    # 分页
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取订单详情（包含账号信息）
    orders_data = []
    for order in pagination.items:
        order_dict = order.to_dict()
        # 添加账号信息
        account = Account.query.get(order.account_id)
        if account:
            order_dict['account'] = account.to_dict()
        # 添加用户信息
        renter = User.query.get(order.renter_id)
        owner = User.query.get(order.owner_id)
        if renter:
            order_dict['renter'] = {'id': renter.id, 'username': renter.username}
        if owner:
            order_dict['owner'] = {'id': owner.id, 'username': owner.username}
        orders_data.append(order_dict)
    
    return jsonify({
        'success': True,
        'orders': orders_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """获取订单详情"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    # 验证权限
    if order.renter_id != user_id and order.owner_id != user_id and not session.get('is_admin'):
        return jsonify({'success': False, 'message': '无权限查看此订单'}), 403
    
    order_dict = order.to_dict()
    # 添加账号信息
    account = Account.query.get(order.account_id)
    if account:
        order_dict['account'] = account.to_dict()
    
    return jsonify({'success': True, 'order': order_dict}), 200

@order_bp.route('/', methods=['POST'])
def create_order():
    """创建订单"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    data = request.get_json()
    
    # 验证必填字段
    if 'account_id' not in data:
        return jsonify({'success': False, 'message': '缺少账号ID'}), 400
    
    # 获取账号信息
    account = Account.query.get(data['account_id'])
    if not account:
        return jsonify({'success': False, 'message': '账号不存在'}), 404
    
    # 检查账号状态
    if account.status != 'available':
        return jsonify({'success': False, 'message': '账号不可租赁'}), 400
    
    # 不能租赁自己的账号
    if account.user_id == user_id:
        return jsonify({'success': False, 'message': '不能租赁自己的账号'}), 400
    
    # 计算订单金额
    rental_amount = account.calculate_order_amount()
    deposit_amount = float(account.deposit)
    total_amount = rental_amount + deposit_amount
    
    # 检查用户余额
    user = User.query.get(user_id)
    if float(user.balance) < total_amount:
        return jsonify({'success': False, 'message': '余额不足，请先充值'}), 400
    
    # 生成订单编号
    order_number = f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6].upper()}'
    
    # 创建订单
    order = Order(
        order_number=order_number,
        renter_id=user_id,
        owner_id=account.user_id,
        account_id=account.id,
        rental_amount=rental_amount,
        deposit_amount=deposit_amount,
        total_amount=total_amount,
        status='pending'
    )
    
    try:
        db.session.add(order)
        
        # 订单创建时立即标记账号为已租出（待支付）
        account.status = 'rented'
        
        db.session.commit()
        return jsonify({'success': True, 'message': '订单创建成功', 'order': order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'订单创建失败: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    """支付订单"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    # 验证权限
    if order.renter_id != user_id:
        return jsonify({'success': False, 'message': '无权限支付此订单'}), 403
    
    # 检查订单状态
    if order.status != 'pending':
        return jsonify({'success': False, 'message': '订单状态不正确'}), 400
    
    # 检查用户余额
    user = User.query.get(user_id)
    if float(user.balance) < float(order.total_amount):
        return jsonify({'success': False, 'message': '余额不足'}), 400
    
    # 获取账号和出租方
    account = Account.query.get(order.account_id)
    owner = User.query.get(order.owner_id)
    
    # 获取管理员账户
    admin = User.query.filter_by(is_admin=True).first()
    
    try:
        # 扣除租赁方余额
        user.balance -= Decimal(str(order.total_amount))
        
        # 租金给出租方
        owner.balance += Decimal(str(order.rental_amount))
        
        # 定金50%给下单方(租赁方)
        user.balance += Decimal(str(order.deposit_amount)) / 2
        
        # 定金50%给管理员
        if admin:
            admin.balance += Decimal(str(order.deposit_amount)) / 2
        
        # 更新订单状态为'正在租赁'
        order.status = 'renting'
        order.paid_at = datetime.now()
        
        # 账号状态已在订单创建时设置为'rented'，这里不需要再改
        
        db.session.commit()
        return jsonify({'success': True, 'message': '支付成功，订单已进入正在租赁状态', 'order': order.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'支付失败: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/complete', methods=['POST'])
def complete_order(order_id):
    """完成订单（租赁结束）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    # 验证权限（租赁方或出租方都可以完成订单）
    if order.renter_id != user_id and order.owner_id != user_id and not session.get('is_admin'):
        return jsonify({'success': False, 'message': '无权限操作此订单'}), 403
    
    # 检查订单状态 - 只有'renting'状态才能完成
    if order.status != 'renting':
        return jsonify({'success': False, 'message': '订单状态不正确，只有正在租赁的订单才能确认为已组赁'}), 400
    
    # 获取租赁方和账号
    renter = User.query.get(order.renter_id)
    account = Account.query.get(order.account_id)
    
    try:
        # 订单完成时，更新状态并增加租赁方的抽奖次数
        
        # 更新订单状态为'已组赁'
        order.status = 'completed'
        order.completed_at = datetime.now()
        
        # 更新账号状态回到可租赁
        account.status = 'available'
        
        # 增加租赁方的免费抽奖次数
        renter.lottery_chances += 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': '订单已确认为已组赁，资金分配完成，已获得1次免费抽奖机会', 'order': order.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    # 验证权限
    if order.renter_id != user_id and not session.get('is_admin'):
        return jsonify({'success': False, 'message': '无权限取消此订单'}), 403
    
    # 只能取消待支付的订单
    if order.status != 'pending':
        return jsonify({'success': False, 'message': '只能取消待支付的订单'}), 400
    
    try:
        # 获取账号，取消订单时恢复账号为可租赁状态
        account = Account.query.get(order.account_id)
        
        order.status = 'cancelled'
        
        # 恢复账号为可租赁
        if account:
            account.status = 'available'
        
        db.session.commit()
        return jsonify({'success': True, 'message': '订单已取消', 'order': order.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消失败: {str(e)}'}), 500
