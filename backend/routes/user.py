"""
用户管理路由
"""
from flask import Blueprint, request, jsonify, session
from backend.models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户个人信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({'success': True, 'user': user.to_dict()}), 200

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """更新用户个人信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新允许的字段
    if 'email' in data:
        # 检查邮箱是否已被使用
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'success': False, 'message': '邮箱已被使用'}), 400
        user.email = data['email']
    
    if 'phone' in data:
        # 检查手机号是否已被使用
        existing = User.query.filter_by(phone=data['phone']).first()
        if existing and existing.id != user_id:
            return jsonify({'success': False, 'message': '手机号已被使用'}), 400
        user.phone = data['phone']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@user_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'success': False, 'message': '旧密码和新密码不能为空'}), 400
    
    # 验证旧密码
    if not user.check_password(data['old_password']):
        return jsonify({'success': False, 'message': '旧密码错误'}), 400
    
    # 设置新密码
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'密码修改失败: {str(e)}'}), 500

@user_bp.route('/recharge', methods=['POST'])
def recharge():
    """充值"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 验证金额
    amount = data.get('amount')
    if not amount or amount <= 0:
        return jsonify({'success': False, 'message': '充值金额必须大于0'}), 400
    
    try:
        user.balance += amount
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': f'充值成功，当前余额: {float(user.balance)}',
            'balance': float(user.balance)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'充值失败: {str(e)}'}), 500

@user_bp.route('/withdraw', methods=['POST'])
def withdraw():
    """提现"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 验证金额
    amount = data.get('amount')
    if not amount or amount <= 0:
        return jsonify({'success': False, 'message': '提现金额必须大于0'}), 400
    
    # 检查余额
    if float(user.balance) < amount:
        return jsonify({'success': False, 'message': '余额不足'}), 400
    
    try:
        user.balance -= amount
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': f'提现申请已提交，当前余额: {float(user.balance)}',
            'balance': float(user.balance)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'提现失败: {str(e)}'}), 500

@user_bp.route('/balance', methods=['GET'])
def get_balance():
    """获取余额"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({'success': True, 'balance': float(user.balance)}), 200

@user_bp.route('/lottery-chance', methods=['POST'])
def use_lottery_chance():
    """使用免費抽奖次数"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    # 检查是否有免費次数
    if user.lottery_chances < 1:
        return jsonify({'success': False, 'message': '你不拥有免費抽奖次数'}), 400
    
    try:
        user.lottery_chances -= 1
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': '已使用4次免費抽奖次数',
            'lottery_chances': user.lottery_chances
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500
