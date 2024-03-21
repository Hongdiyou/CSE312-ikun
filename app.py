from flask import Flask, render_template, request, Response
#这是我们使用的框架“Flask" 如果你们看到编译器错误需要首先安装环境
app=Flask(__name__)


#这是flask框架添加route的方式和我们作业的add_route类似，例如这里的'/'对应了我们作业的'/' 也是root path
#这会response html文件.
@app.route('/')
def responsetoroot():
    response= Response("/src/index.html","X-Content-Type-Options: nosniff")
    print(response)
    return response


def __main__():
    app.run()
    #ikun,启动！