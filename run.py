"""
应用启动脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.models import db

if __name__ == '__main__':
    app = create_app()
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表检查完成！")
    
    # 运行应用
    print("=" * 50)
    print("游戏账号租赁平台启动成功！")
    print("访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
