from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poetry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 数据库模型
class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    dynasty = db.Column(db.String(20))
    tags = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 与评论的一对多关系
    comments = db.relationship('Comment', backref='poem', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    poem_id = db.Column(db.Integer, db.ForeignKey('poem.id'), nullable=False)


# 初始化数据库的函数
def init_db():
    with app.app_context():
        db.create_all()
        # 检查是否已有数据
        if not Poem.query.first():
            sample_poems = [
                Poem(
                    title="静夜思",
                    author="李白",
                    dynasty="唐",
                    content="床前明月光，疑是地上霜。\n举头望明月，低头思故乡。",
                    tags="思乡,月亮,唐诗"
                ),
                Poem(
                    title="春晓",
                    author="孟浩然",
                    dynasty="唐",
                    content="春眠不觉晓，处处闻啼鸟。\n夜来风雨声，花落知多少。",
                    tags="春天,唐诗,自然"
                ),
                Poem(
                    title="登鹳雀楼",
                    author="王之涣",
                    dynasty="唐",
                    content="白日依山尽，黄河入海流。\n欲穷千里目，更上一层楼。",
                    tags="山水,励志,唐诗"
                ),
                Poem(
                    title="相思",
                    author="王维",
                    dynasty="唐",
                    content="红豆生南国，春来发几枝。\n愿君多采撷，此物最相思。",
                    tags="相思,爱情,唐诗"
                ),
                Poem(
                    title="江雪",
                    author="柳宗元",
                    dynasty="唐",
                    content="千山鸟飞绝，万径人踪灭。\n孤舟蓑笠翁，独钓寒江雪。",
                    tags="冬天,孤独,唐诗"
                )
            ]
            db.session.bulk_save_objects(sample_poems)
            db.session.commit()
            print("示例数据已添加")


# 路由定义
@app.route('/')
def index():
    poems = Poem.query.order_by(Poem.created_at.desc()).limit(6).all()
    return render_template('index.html', poems=poems)


@app.route('/poem/<int:poem_id>')
def poem_detail(poem_id):
    poem = Poem.query.get_or_404(poem_id)
    return render_template('poem_detail.html', poem=poem)


@app.route('/random')
def random_poem():
    poems = Poem.query.all()
    if poems:
        poem = random.choice(poems)
        return render_template('random_poem.html', poem=poem)
    return redirect(url_for('index'))


@app.route('/game')
def poem_game():
    return render_template('game.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/add_comment/<int:poem_id>', methods=['POST'])
def add_comment(poem_id):
    username = request.form.get('username', '匿名')
    content = request.form.get('content', '')

    if content:
        comment = Comment(username=username, content=content, poem_id=poem_id)
        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('poem_detail', poem_id=poem_id))


# API接口
@app.route('/api/poems')
def api_poems():
    poems = Poem.query.all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'author': p.author,
        'dynasty': p.dynasty,
        'content': p.content
    } for p in poems])


@app.route('/api/random_poem')
def api_random_poem():
    poems = Poem.query.all()
    if poems:
        poem = random.choice(poems)
        return jsonify({
            'id': poem.id,
            'title': poem.title,
            'author': poem.author,
            'dynasty': poem.dynasty,
            'content': poem.content
        })
    return jsonify({'error': 'No poems available'})


# 添加一个初始化数据库的路由（仅开发使用）
@app.route('/init-db')
def init_database():
    init_db()
    return "数据库初始化完成！"


if __name__ == '__main__':
    # 检查数据库文件是否存在，如果不存在则初始化
    if not os.path.exists('poetry.db'):
        init_db()
    app.run(host="::", debug=True)