import flask
#这是我们使用的框架“Flask" 如果你们看到编译器错误需要首先安装环境
from flask_talisman import Talisman
import pymongo
from bson import ObjectId
import bcrypt
import secrets
import hashlib
#这是flask框架添加route的方式和我们作业的add_route类似，例如这里的'/'对应了我们作业的'/' 也是root path
#这会response html文件.

mongo_client=pymongo.MongoClient("mongodb://mongo:27017/postDB")
db=mongo_client['postDB']
post_collection=db['posts']
user_collection=db['users']
app = flask.Flask(__name__)


talisman = Talisman(app)
@app.route('/')
def index():

    auth_token=flask.request.cookies.get('auth_token')
    current_user="Guest"
    user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
    if user:
        current_user=user['username']

    posts=post_collection.find({},{'title': 1})
    return flask.render_template('index.html',posts=posts,current_user=current_user)

@app.route('/static/img/<path:path>')
def img(path):
    return flask.send_from_directory('static/img', path)

@app.route('/makepost')
def makepost():
    return flask.render_template('makepost.html')

@app.route('/post/<post_id>')
def view_post(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    return flask.render_template('post.html', post=post)

@app.route('/submitpost', methods=['POST'])
def submit_post():
    if flask.request.method == 'POST':
        title = flask.request.form['title']
        content = flask.request.form['content']
        post_collection.insert_one({'title': title, 'content': content}).inserted_id
        return flask.redirect(flask.url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    username = flask.request.form['username_reg']
    password = flask.request.form['password_reg']
    con_password = flask.request.form['confirm_password_reg']
    if password != con_password:
        return flask.redirect(flask.url_for('index'))
    if user_collection.find_one({'username': username}):
        return flask.redirect(flask.url_for('index'))
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_collection.insert_one({'username': username, 'password': hashed_password})
    return flask.redirect(flask.url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username_login']
        password = flask.request.form['password_login']

        user = user_collection.find_one({'username': username})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return "Invalid username or password", 401

        token=secrets.token_hex(16)
        auth_token=hashlib.sha256(token.encode()).hexdigest()
        user_collection.update_one({'username': username}, {'$set': {'auth_token': auth_token}})

        response = flask.make_response(flask.redirect(flask.url_for('index')))
        response.set_cookie('auth_token', token, httponly=True)
        return response

@app.route('/logout', methods=['POST'])
def logout():
    auth_token=flask.request.cookies.get('auth_token')
    user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
    if user:
        user_collection.update_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()}, {'$unset': {'auth_token': 1}})
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    #ikun,启动！
