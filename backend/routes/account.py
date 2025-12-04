"""
账号管理路由
"""
from flask import Blueprint, request, jsonify, session
from backend.models import db, Account
from sqlalchemy import or_, and_

account_bp = Blueprint('account', __name__)

# 允许的刀皮列表
ALLOWED_KNIFE_SKINS = ['北极星', '黑海', '赤霄怜悯', '影锋', '信条']

@account_bp.route('/', methods=['GET'])
def get_accounts():
    """获取账号列表（支持搜索和筛选）"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 筛选条件
    safe_box_slots = request.args.getlist('safe_box_slots')  # 保险箱格数（可多选）
    min_level = request.args.get('min_level', type=int)  # 最小等级
    max_level = request.args.get('max_level', type=int)  # 最大等级
    min_assets = request.args.get('min_assets', type=float)  # 最小资产
    max_assets = request.args.get('max_assets', type=float)  # 最大资产
    knife_skins = request.args.getlist('knife_skins')  # 刀皮（可多选）
    server_region = request.args.get('server_region')  # 区服
    status = request.args.get('status', 'available')  # 状态
    
    # 构建查询
    query = Account.query.filter_by(status=status)
    
    # 保险箱格数筛选
    if safe_box_slots:
        safe_box_slots = [int(s) for s in safe_box_slots]
        query = query.filter(Account.safe_box_slots.in_(safe_box_slots))
    
    # 等级筛选
    if min_level:
        query = query.filter(Account.level >= min_level)
    if max_level:
        query = query.filter(Account.level <= max_level)
    
    # 资产筛选
    if min_assets:
        query = query.filter(Account.pure_coin_assets >= min_assets)
    if max_assets:
        query = query.filter(Account.pure_coin_assets <= max_assets)
    
    # 区服筛选
    if server_region:
        query = query.filter(Account.server_region.like(f'%{server_region}%'))
    
    # 刀皮筛选（包含任意一个指定的刀皮）
    if knife_skins:
        # 使用JSON查询
        conditions = []
        for skin in knife_skins:
            conditions.append(Account.knife_skins.contains([skin]))
        if conditions:
            query = query.filter(or_(*conditions))
    
    # 分页
    pagination = query.order_by(Account.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'accounts': [account.to_dict() for account in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@account_bp.route('/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """获取单个账号详情"""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({'success': False, 'message': '账号不存在'}), 404
    
    return jsonify({'success': True, 'account': account.to_dict()}), 200

@account_bp.route('/', methods=['POST'])
def create_account():
    """发布账号"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    data = request.get_json()
    
    # 验证必填字段（account_number 由系统生成）
    required_fields = ['pure_coin_assets', 'safe_box_slots', 'price', 'deposit', 'server_region', 'total_assets']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
    
    # 验证总资产 > 纯币资产
    total_assets = float(data.get('total_assets', 0))
    pure_coin = float(data.get('pure_coin_assets', 0))
    
    if total_assets <= pure_coin:
        return jsonify({'success': False, 'message': '总资产必须大于纯币资产'}), 400
    
    # 验证保险箱格数
    if data['safe_box_slots'] not in [4, 6, 9]:
        return jsonify({'success': False, 'message': '保险箱格数只能是4、6或9'}), 400
    
    # 验证刀皮
    knife_skins = data.get('knife_skins', [])
    if knife_skins:
        if not isinstance(knife_skins, list):
            return jsonify({'success': False, 'message': '刀皮必须是数组'}), 400
        for skin in knife_skins:
            if skin not in ALLOWED_KNIFE_SKINS:
                return jsonify({'success': False, 'message': f'不允许的刀皮: {skin}'}), 400
    
    # 生成唯一的账号编号
    import uuid
    from datetime import datetime
    account_number = f'ACC{datetime.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6].upper()}'
    
    # 创建账号
    account = Account(
        user_id=user_id,
        account_number=account_number,
        collection_time=data.get('collection_time'),
        login_time=data.get('login_time'),
        common_location=data.get('common_location'),
        server_region=data.get('server_region'),
        login_method=data.get('login_method'),
        face_verification=data.get('face_verification'),
        rank=data.get('rank'),
        total_assets=data.get('total_assets'),
        pure_coin_assets=data['pure_coin_assets'],
        level=data.get('level'),
        stamina_level=data.get('stamina_level'),
        safe_box_slots=data['safe_box_slots'],
        aw_bullets=data.get('aw_bullets'),
        knife_skins=knife_skins,
        price=data['price'],
        deposit=data['deposit'],
        remarks=data.get('remarks')
    )
    
    try:
        db.session.add(account)
        db.session.commit()
        return jsonify({'success': True, 'message': '发布成功', 'account': account.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'发布失败: {str(e)}'}), 500

@account_bp.route('/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """更新账号信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'success': False, 'message': '账号不存在'}), 404
    
    # 验证权限
    if account.user_id != user_id and not session.get('is_admin'):
        return jsonify({'success': False, 'message': '无权限修改此账号'}), 403
    
    data = request.get_json()
    
    # 更新字段
    if 'safe_box_slots' in data and data['safe_box_slots'] not in [4, 6, 9]:
        return jsonify({'success': False, 'message': '保险箱格数只能是4、6或9'}), 400
    
    if 'knife_skins' in data:
        knife_skins = data['knife_skins']
        if knife_skins and not isinstance(knife_skins, list):
            return jsonify({'success': False, 'message': '刀皮必须是数组'}), 400
        for skin in knife_skins:
            if skin not in ALLOWED_KNIFE_SKINS:
                return jsonify({'success': False, 'message': f'不允许的刀皮: {skin}'}), 400
    
    # 更新允许的字段
    allowed_fields = [
        'collection_time', 'login_time', 'common_location', 'server_region',
        'login_method', 'face_verification', 'rank', 'total_assets',
        'pure_coin_assets', 'level', 'stamina_level', 'safe_box_slots',
        'aw_bullets', 'knife_skins', 'price', 'deposit', 'remarks', 'status'
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(account, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功', 'account': account.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@account_bp.route('/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """删除账号"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'success': False, 'message': '账号不存在'}), 404
    
    # 验证权限
    if account.user_id != user_id and not session.get('is_admin'):
        return jsonify({'success': False, 'message': '无权限删除此账号'}), 403
    
    try:
        db.session.delete(account)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
