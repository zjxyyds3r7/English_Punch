import pymysql
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def get_today():
    return str(datetime.datetime.now().strftime('%Y-%m-%d'))


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.yticks(fontsize=26)
plt.xticks(fontsize=26)

class mess_sql:
    def __init__(self):
        # self.word_max = 500
        try:
            self.connect = pymysql.connect(host='localhost',
                                           user='root',
                                           password='password1',
                                           db='english punch',
                                           charset='gbk')  # 服务器名,账户,密码，数据库名称
        except:
            self.connect = pymysql.connect(host='localhost',
                                           user='root',
                                           password='password2',
                                           db='english punch',
                                           charset='gbk')  # 服务器名,账户,密码，数据库名称
        self.cur = self.connect.cursor()

    def open_sql(self):
        pass

    def close_sql(self):
        pass

    def add(self, name, ip, vid):
        self.open_sql()
        try:
            self.connect.ping(reconnect=True)
            find_name_in_table = "select class from all_name where name='{0}'".format(name)
            # print("find_name_in_table:", find_name_in_table)
            self.cur.execute(find_name_in_table)
            classres = self.cur.fetchall()
            if len(classres) == 0:
                s = '{0} 不在班级总名单中哦 检查一下是不是字打错了'.format(name)
                print(s)
                self.add_visit(ip, s)
                return s

            today = "select date from update_table where date > '{0}' and name ='{1}'".format(
                get_today(), name)
            self.cur.execute(today)
            res = self.cur.fetchall()

            if len(res) != 0:
                s = '今天 {0} 已经打卡了哦 打卡时间为 {1}'.format(name, res[0][0])
                print(s)
                self.add_visit(ip, s)
                return s

            ip_err = "select name from update_table where date > '{0}' and vid='{1}'".format(
                get_today(), vid
            )
            self.cur.execute(ip_err)
            res = self.cur.fetchall()
            # TODO 防止重复ip
            res = []
            if len(res) != 0:
                s = "今天本设备已经为 {0} 打卡啦 不能重复打卡".format(res[0][0])
                print(s)
                self.add_visit(ip, s)
                return s

            add_text = "insert into update_table values ('{0}','{1}','{2}','{3}','{4}');"\
                .format(name, classres[0][0],
                        datetime.datetime.now(),
                        ip, vid)

            self.cur.execute(add_text)
            self.connect.commit()
            s = '{0}打卡成功 打卡时间为:{1}'.format(name, datetime.datetime.now().strftime('%H:%M:%S'))
            print(s)
            return s
        except Exception as e:
            print(e)
            self.add_visit(ip, str(e))
            return 'E'

    def new_statistics(self):
        import matplotlib.pyplot as plt  
        plt.switch_backend('agg') 
        try:
            self.open_sql()
            self.connect.ping(reconnect=True)
            search_class = 'SELECT class FROM all_name GROUP BY class;'
            self.cur.execute(search_class)
            classes = self.cur.fetchall()
            res_list = []
            for c in classes:
                c = c[0]
                all_name = "select name from all_name where class={0}".format(c)
                self.cur.execute(all_name)
                res = self.cur.fetchall()
                res = [i[0] for i in res]  # list(res)

                tijiao = "select name from update_table where date > '{0}' and class={1}".format(get_today(), c)
                self.cur.execute(tijiao)
                tijiao_list = self.cur.fetchall()
                # tijiao_list = list(tijiao_list)
                tijiao_list = [i[0] for i in tijiao_list]
                # print(tijiao_list)
                yitijiao = len(tijiao_list)
                weitijiao = len(res) - yitijiao
                weitijiao_list = ",".join([i for i in res if i not in tijiao_list])
                yitijiao_list = ",".join([i for i in tijiao_list])
                plt.figure()
                plt.cla()
                plt.title('提交对比', fontsize=26)
                plt.pie([weitijiao, yitijiao], labels=['未提交', '已提交'], autopct='%3.1f%%')
                pie_path = 'static/pie{0}.png'.format(c)
                plt.savefig(pie_path)
                # plt.show()
                bar_path = self.lately(c)
                plt.close('all')
                m = {'class': c,
                     'no_s_p': weitijiao,
                     'no_s_p_list': weitijiao_list,
                     's_p': yitijiao,
                     's_p_list': yitijiao_list,
                     'pie': pie_path,
                     'bar': bar_path
                     }
                res_list.append(m)
            return res_list
        except Exception as e:
            print(e)
            self.add_visit('0.0.0.1', str(e))
            return []

    def lately(self, c):
        try:
            plt.figure(dpi=300, figsize=(10, 10))
            time_list = []
            peo_list = []
            delta = datetime.timedelta(days=-1)
            endtime = datetime.datetime.now() - delta
            for i in range(5):

                starttime = endtime + delta
                # print(str(starttime.strftime('%Y-%m-%d')))
                sql = "select name from update_table where date>'{0}' and date<'{1}' and class={2}".format(starttime.strftime('%Y-%m-%d'),
                                                                                             endtime.strftime('%Y-%m-%d'), c)
                # print('sql line', sql)
                self.connect.ping(reconnect=True)
                self.cur.execute(sql)
                res = self.cur.fetchall()
                # if len(res) == 0:
                #     endtime = starttime
                #     continue
                time_list.append(str(starttime.strftime('%m-%d')))
                peo_list.append(len(res))

                endtime = starttime

            plt.cla()
            plt.legend(fontsize=32)
            plt.title('最近打卡情况对比',fontsize=20)
            x = [i + 1 for i in range(len(time_list))]
            color = ['peru', 'orchid', 'deepskyblue']
            plt.yticks(fontsize=26)
            plt.xticks(fontsize=26)

            plt.xlabel('时间', fontsize=26)
            plt.ylabel('人数', fontsize=26)
            list.reverse(time_list)
            list.reverse(peo_list)
            # time_list = time_list * 2
            # peo_list = peo_list * 2

            plt.xticks(x, time_list)  # 绘制x刻度标签
            b = plt.bar(x, peo_list, color=color, width=0.3)
            plt.bar_label(b, label_type='edge', fontsize=26)
            save_path = 'static/bar{0}.png'.format(c)
            try:
                plt.savefig(save_path)
            except:
                plt.savefig('bar.png')
            return save_path
        except Exception as e:
            print(e)
            self.add_visit('0.0.0.2', str(e))
            return ''

    def ip_to_name(self, ip):
        try:
            self.open_sql()
            sql = "select name from update_table where ip='{0}'".format(ip)
            self.connect.ping(reconnect=True)
            self.cur.execute(sql)
            res = self.cur.fetchall()
            res = [i[0] for i in res]  # list(res)
            res = list(set(res))
            # print(res)
            print('返回的记忆用户名' + ','.join(res))
            self.add_visit(ip, '返回的记忆用户名' + ','.join(res))
            self.close_sql()
            return ','.join(res)
        except Exception as e:
            print(e)
            self.add_visit('0.0.0.3', str(e))
            return ''

    def today_date_have(self):
        try:
            self.open_sql()
            sql = "select name from update_table where date > '{0}'".format(get_today())
            self.connect.ping(reconnect=True)
            self.cur.execute(sql)
            res = self.cur.fetchall()
            self.close_sql()
            return len(res) != 0
        except Exception as e:
            print(e)
            self.add_visit('0.0.0.3', str(e))
            return True

    def add_visit(self, ip, thing):
        try:
            self.open_sql()
            sql = "insert into visit values ('{0}','{1}','{2}');".format(datetime.datetime.now(),ip,thing)
            self.connect.ping(reconnect=True)
            self.cur.execute(sql)
            self.connect.commit()
            self.close_sql()
        except Exception as e:
            print(e)
            # self.add_visit('0.0.0.4', str(e))

    def add_phrase(self, d):
        try:
            self.open_sql()
            question = d.get("result").get("question")
            answer = d.get("result").get("answer")
            source = d.get("result").get("source")
            study = d.get("result").get("study")
            sp = d.get("result").get("abbr")
            quanpin = d.get("result").get("pinyin")
            sql = "insert into phrase values ('{0}','{1}','{2}','{3}','{4}','{5}');".format(
                question, answer, source, study, sp, quanpin
            )
            self.connect.ping(reconnect=True)
            self.cur.execute(sql)
            self.connect.commit()
            self.close_sql()
        except Exception as e:
            print(e)
            self.add_visit('0.0.0.5', str(e))
