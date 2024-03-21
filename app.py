from flask import Flask, render_template, request, redirect, url_for, send_from_directory
#这是我们使用的框架“Flask" 如果你们看到编译器错误需要首先安装环境
from flask_talisman import Talisman
import pymongo
from bson import ObjectId
#这是flask框架添加route的方式和我们作业的add_route类似，例如这里的'/'对应了我们作业的'/' 也是root path
#这会response html文件.

mongo_client=pymongo.MongoClient("mongodb://mongo:27017/postDB")
db=mongo_client['postDB']
post_collection=db['posts']
app = Flask(__name__)


talisman = Talisman(app)
@app.route('/')
def index():
    posts=post_collection.find({}, {'title': 1})
    return render_template('index.html',posts=posts)

@app.route('/static/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)

@app.route('/makepost')
def makepost():
    return render_template('makepost.html')

@app.route('/post/<post_id>')
def view_post(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    return render_template('post.html', post=post)

@app.route('/submitpost', methods=['POST'])
def submit_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post_collection.insert_one({'title': title, 'content': content}).inserted_id
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    #ikun,启动！
