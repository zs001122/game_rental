"""
用户认证路由
"""
from flask import Blueprint, request, jsonify, session
from backend.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data.get('email'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '注册成功', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证密码
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    # 设置会话
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    
    return jsonify({
        'success': True, 
        'message': '登录成功',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'}), 200

@auth_bp.route('/current', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({'success': True, 'user': user.to_dict()}), 200
