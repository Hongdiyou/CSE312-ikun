import flask
#这是我们使用的框架“Flask" 如果你们看到编译器错误需要首先安装环境
from flask_talisman import Talisman
import pymongo
from bson import ObjectId
import bcrypt
import secrets
import hashlib
import os
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta

#这是flask框架添加route的方式和我们作业的add_route类似，例如这里的'/'对应了我们作业的'/' 也是root path
#这会response html文件.

csp = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        'cdnjs.cloudflare.com',
        'ajax.googleapis.com',
        '\'unsafe-inline\'' 
    ]
}


mongo_client=pymongo.MongoClient("mongodb://mongo:27017/postDB")
db=mongo_client['postDB']
post_collection=db['posts']
user_collection=db['users']
message_collection=db['message']
auction_collection = db['auction']
app=flask.Flask(__name__)
if not os.path.exists('media'):
    os.makedirs('media')

socketio = SocketIO(app)
talisman = Talisman(app, content_security_policy=csp)
@app.route('/')
def index():

    auth_token=flask.request.cookies.get('auth_token')
    current_user="Guest"
    if auth_token:
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
    post=db.posts.find_one({'_id': ObjectId(post_id)})
    return flask.render_template('post.html', post=post)

@app.route('/submitpost', methods=['POST'])
def submit_post():
    if flask.request.method == 'POST':
        auth_token=flask.request.cookies.get('auth_token')
        current_user="Guest"
        if auth_token:
            user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
            if user:
                current_user=user['username']
        title=flask.request.form['title']
        content=flask.request.form['content']
        

        if 'image' in flask.request.files:
            image=flask.request.files['image']
            if image.filename != '':
                if '/' not in image.filename:
                    filename=secure_filename(image.filename)
                    image.save(os.path.join('media', filename))
                    image_url=flask.url_for('uploaded_file', filename=filename)
                    content += f'<img src="{image_url}" alt="Uploaded Image">'
        post_collection.insert_one({'title': title,'content': content,'user':current_user}).inserted_id
        return flask.redirect(flask.url_for('index'))

@app.route('/media/<filename>')
def uploaded_file(filename):
    return flask.send_from_directory('media', filename)

@app.route('/chatroom')
def chatroom():
    return flask.render_template('chatroom.html')

@socketio.on('message')
def handle_message(data):
    auth_token = flask.request.cookies.get('auth_token')
    username = "Guest"
    if auth_token:
        user = user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
        if user:
            username = user['username']
    message_collection.insert_one({'username': username, 'message': data})
    emit('message', {'username': username, 'message': data}, broadcast=True)

@socketio.on('connect')
def handle_connect():
    messages = message_collection.find()
    for message in messages:
        emit('message', {'username': message['username'], 'message': message['message']})


@app.route('/register', methods=['POST'])
def register():
    username=flask.request.form['username_reg']
    password=flask.request.form['password_reg']
    con_password=flask.request.form['confirm_password_reg']
    if password != con_password:
        return flask.redirect(flask.url_for('index'))
    if user_collection.find_one({'username': username}):
        return flask.redirect(flask.url_for('index'))
    hashed_password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_collection.insert_one({'username': username, 'password': hashed_password})
    return flask.redirect(flask.url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    if flask.request.method == 'POST':
        username=flask.request.form['username_login']
        password=flask.request.form['password_login']

        user=user_collection.find_one({'username': username})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return flask.redirect(flask.url_for('index'))

        token=secrets.token_hex(16)
        auth_token=hashlib.sha256(token.encode()).hexdigest()
        user_collection.update_one({'username': username}, {'$set': {'auth_token': auth_token}})

        response=flask.make_response(flask.redirect(flask.url_for('index')))
        response.set_cookie('auth_token', token, httponly=True, max_age=3600)
        return response

@app.route('/logout', methods=['POST'])
def logout():
    auth_token=flask.request.cookies.get('auth_token')
    if auth_token:
        user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
        if user:
            user_collection.update_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()}, {'$unset': {'auth_token': 1}})
    return flask.redirect(flask.url_for('index'))

@app.route('/comment/<post_id>', methods=['POST'])
def comment_post(post_id):
    auth_token=flask.request.cookies.get('auth_token')
    current_user="Guest"
    if auth_token:
        user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
        if user:
            current_user=user['username']
    content=flask.request.form['content']

    post=post_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        return "Post not found", 404

    post_collection.update_one({'_id': ObjectId(post_id)}, {'$push': {'comments': {'content': content, 'user': current_user}}})
    return flask.redirect(flask.url_for('view_post', post_id=post_id))




@app.route('/additem', methods=['GET', 'POST'])
def add_item():
    if flask.request.method == 'POST':
        auth_token=flask.request.cookies.get('auth_token')
        current_user="Guest"
        if auth_token:
            user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
            if user:
                current_user=user['username']
        if current_user!='Guest':
            end_time = datetime.now() + timedelta(hours=2)
            end_time_str = flask.request.form['end_time']
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            title = flask.request.form['title']
            description = flask.request.form['description']
            if 'image' in flask.request.files:
                image = flask.request.files['image']
                if image.filename != '':
                    if '/' not in image.filename:
                        filename = secure_filename(image.filename)
                        image.save(os.path.join('media', filename))
                        image_url = flask.url_for('uploaded_file', filename=filename)
                        auction_collection.insert_one({'title': title, 'description': description, 'image_url': image_url, 'current_bid': 0,'seller':current_user,'end_time':end_time,'bidder':'No one'})
                        return flask.redirect(flask.url_for('auction'))
            auction_collection.insert_one({'title': title, 'description': description,'current_bid': 0,'seller':current_user,'end_time':end_time,'bidder':'No one'})
        return flask.redirect(flask.url_for('auction'))
    return flask.render_template('additem.html')

@app.route('/auction')
def auction():
    auction_items = auction_collection.find()
    return flask.render_template('auction.html', auction_items=auction_items)

@app.route('/auction/<item_id>', methods=['GET', 'POST'])
def view_auction_item(item_id):

    auction_item = auction_collection.find_one({'title': item_id})
    if auction_item:
        end_time = auction_item.get('end_time')
        remaining_time = end_time - datetime.now()
        return flask.render_template('auction_item.html',item=auction_item,remaining_time_seconds=remaining_time.total_seconds())
    else:
        return flask.redirect(flask.url_for('auction'))

@app.route('/placebid', methods=['POST'])
def place_bid():
    if flask.request.method == 'POST':
        auth_token=flask.request.cookies.get('auth_token')
        current_user="Guest"
        if auth_token:
            user=user_collection.find_one({'auth_token': hashlib.sha256(auth_token.encode()).hexdigest()})
            if user:
                current_user=user['username']
        item_id = flask.request.form.get('item_id')
        bid_amount = float(flask.request.form.get('bid_amount'))
        item = auction_collection.find_one({'_id': ObjectId(item_id)})
        if datetime.now() > item['end_time']:
            return "This auction has ended", 400
        
        if bid_amount > item.get('current_bid', 0):
            if current_user!='Guest':
                if item['seller']==current_user:
                    return "you cannot make bid to your own item", 400
                auction_collection.update_one({'_id': ObjectId(item_id)}, {'$set': {'current_bid': bid_amount}})
                auction_collection.update_one({'_id': ObjectId(item_id)}, {'$set': {'bidder': current_user}})
            return flask.redirect(flask.url_for('auction'))
        else:
            return "Bid amount must be higher than the current bid", 400



if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=8080)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
    #ikun,启动！
