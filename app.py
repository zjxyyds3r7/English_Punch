import http.client, urllib, json
import random
from flask import *
from sql_fun import *

app = Flask(__name__)
sql_f = mess_sql()


class info:
    def __init__(self):
        self.c = sql_f.new_statistics()
        sql_f.close_sql()


i = info()


@app.route('/')
def hello_world():  # put application's code here
    showmess = False
    mess = []
    with open('message.txt', 'r', encoding='utf-8') as f:
        first = f.readline().replace('\n','')
        # print(first)
        if first != '0':
            showmess = True
            mess = [i.replace('\n', '') for i in f.readlines()]
    return render_template("main.html",
                           date=get_today(),
                           name=sql_f.ip_to_name(request.remote_addr),
                           showmess=showmess,
                           lines=mess)


@app.route('/add', methods=["POST"])
def add_fun():
    name = str(request.form.get("name"))
    vid = str(request.form.get("vid"))
    print('vid:', vid)
    ans = sql_f.add(name, request.remote_addr, vid)

    sql_f.close_sql()
    if '打卡成功' in ans:
        i.c = sql_f.new_statistics()
        sql_f.close_sql()
    return {'message': ans}


@app.route('/about', methods=['POST'])
def helpfun():
    sql_f.add_visit(request.remote_addr, 'help')
    infol = []
    with open('helplist.txt', 'r', encoding='utf-8') as f:
        infolist = f.readlines()
        index = 0
        m = {}
        for i in infolist:
            index += 1
            if index % 2 == 0:
                m['info'] = i
                infol.append(m)
                m = {}
            else:
                m['time'] = i

    # return render_template('help.html')
    return render_template('help.html', infolist=infol)


@app.route('/heart', methods=['POST'])
def heart_fun():
    name = str(request.form.get("name"))
    a = random.randint(0,9)
    if name == '' or name == ' ':
        name = '专属于你'
    if a > 6:
        sql_f.add_visit(request.remote_addr, name + ':heart')
        print(name + ':heart')
        return render_template('heart.html', name=name)
    else:
        sql_f.add_visit(request.remote_addr, name + ':圣诞树')
        print(name + ':圣诞树')
        return render_template('圣诞树.html', name=name)


@app.route('/s', methods=['POST'])
def s():
    print(request.remote_addr + ':statistics')
    sql_f.add_visit(request.remote_addr, 'statistics')
    h = sql_f.today_date_have()
    if h not in [True, False]:
        h = False
    return render_template('statistics.html',
                           date=get_today(),
                           havedate=h,
                           classes=i.c,
                           time=datetime.datetime.now().strftime('%H:%M:%S'))


def get_p_dic():
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': 'e4f14dc0f0b162bb745cc20833dce4f0'})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/caichengyu/index', params, headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    dict_data = json.loads(data)
    return dict_data


def is_None(s):
    if s == '':
        return '暂无'
    return s


@app.route('/p', methods=['POST', 'GET'])
def p():
    d = get_p_dic()
    print(d)
    print(request.remote_addr + ':猜成语')
    sql_f.add_visit(request.remote_addr, '猜成语')
    sql_f.add_phrase(d)
    return render_template("phrase.html",
                           question=d.get("result").get("question"),
                           answer=d.get("result").get("answer"),
                           source=is_None(d.get("result").get("source")),
                           study=is_None(d.get("result").get("study")),
                           sp=d.get("result").get("abbr"),
                           quanpin=d.get("result").get("pinyin")
                           )


if __name__ == '__main__':
    app.run()
