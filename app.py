from flask import Flask, render_template, request, Response, send_from_directory
#这是我们使用的框架“Flask" 如果你们看到编译器错误需要首先安装环境



#这是flask框架添加route的方式和我们作业的add_route类似，例如这里的'/'对应了我们作业的'/' 也是root path
#这会response html文件.


app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    #ikun,启动！
