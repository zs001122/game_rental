"""
Flask应用主文件
"""
from flask import Flask, render_template
from flask_cors import CORS
from backend.config import Config
from backend.models import db

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # 加载配置
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from backend.routes.auth import auth_bp
    from backend.routes.account import account_bp
    from backend.routes.order import order_bp
    from backend.routes.user import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(account_bp, url_prefix='/api/accounts')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # 前端路由
    @app.route('/')
    def index():
        """首页"""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """登录页面"""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """注册页面"""
        return render_template('register.html')
    
    @app.route('/rental')
    def rental_page():
        """租赁页面"""
        return render_template('rental.html')
    
    @app.route('/publish')
    def publish_page():
        """发布账号页面"""
        return render_template('publish.html')
    
    @app.route('/profile')
    def profile_page():
        """个人中心页面"""
        return render_template('profile.html')
    
    @app.route('/activity')
    def activity_page():
        """出币活动页面"""
        return render_template('activity.html')
    
    @app.route('/news')
    def news_page():
        """经济学日报页面"""
        return render_template('news.html')
    
    @app.route('/admin')
    def admin_page():
        """管理员后台页面"""
        return render_template('admin.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)
