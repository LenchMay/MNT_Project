from flask import Flask, render_template
from models import db, Post, Comment

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Welcome to Blog Post</h1>'

@app.route('/posts')
def all_posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/post/<int:post_id>/comments')
def show_comments(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('comments.html', post=post)

@app.route('/contacts')
def contacts():
    cnt =   '1. Elena<br>' \
            '2. Nikolay'
    return cnt

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)