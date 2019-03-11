import json
import random
import os
import shutil
from tkinter import *
import subprocess

server_item = "[{{var1}}]\ntype = {{var2}}\nlocal_ip = {{var3}}\nlocal_port = {{var4}}\ncustom_domains = {{var5}}\n"
process_list = []


def random_string():
    # 产生随机的字符串
    seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    name = []
    for i in range(8):
        name.append(random.choice(seed))
    name = ''.join(name)
    return name


def get_server():
    # 从 server.json 获取服务器列表信息
    checkout_server_info_flag = 0
    server_info = open("server.json", "r+")
    server_info_content = server_info.read()
    server_list = json.loads(server_info_content)
    for item in server_list:
        if item['username'] == '':
            checkout_server_info_flag = 1
            item['username'] = random_string()
    if checkout_server_info_flag == 1:
        server_info.seek(0)
        server_info.truncate()
        server_info.write(json.dumps(server_list))
    server_info.close()
    return server_list


def get_mine():
    # 从 mine.json 获取本地应用列表信息
    checkout_mine_info_flag = 0
    mine_info = open("mine.json", "r+")
    mine_info_content = mine_info.read()
    mine_list = json.loads(mine_info_content)
    for item in mine_list:
        if item['sub_domain'] == '':
            checkout_mine_info_flag = 1
            item['sub_domain'] = random_string()
    if checkout_mine_info_flag == 1:
        print("test")
        mine_info.seek(0)
        mine_info.truncate()
        mine_info.write(json.dumps(mine_list))
    mine_info.close()
    return mine_list


def start_client(path):
    # 启动各个子文件夹下的 frpc 程序
    p_1 = path + "frpc"
    p_2 = path + "frpc.ini"
    print('Server ' + path + ' Go!\n')
    r = subprocess.Popen([p_1, '-c', p_2])
    print('PID: ' + str(r.pid) + "\n")
    process_list.append(r)
    # 将子进程添加到 process_list 以管理


def stop_client():
    # 终止所有 process_list 里的子进程
    for proc in process_list:
        proc.kill()
        print("进程终止")


def create_client(server, mine_list, temp):
    # 根据两个json文件里的信息，生成子文件夹
    # 并将ini配置文件 和 frpc 放入子文件夹
    path = server['domain'] + "/"
    if not os.path.exists(path):
        os.mkdir(path, 0o755)
    frpc_ini = open(path + "frpc.ini", "w+")
    data = temp
    data = data.replace('{{var1}}', server['domain'])
    data = data.replace('{{var2}}', server['port'])
    data = data.replace('{{var3}}', server['token'])
    data = data.replace('{{var4}}', server['username'])
    var5 = ''
    for one in mine_list:
        string = server_item
        print(one['sub_domain'] + '.' + server['domain'] + "\n")
        string = string.replace('{{var1}}', one['sub_domain'])
        string = string.replace("{{var2}}", one['type'])
        string = string.replace("{{var3}}", one['ip'])
        string = string.replace("{{var4}}", one['port'])
        string = string.replace("{{var5}}", one['sub_domain'] + '.' + server['domain'])
        var5 += string
    data = data.replace('{{var5}}', var5)
    shutil.copy("frpc", path)
    # 取出对应的 frpc 启动程序拷贝到子文件夹（临时写法）
    frpc_ini.write(data)
    frpc_ini.close()
    start_client(path)


def main():
    conf_template = open("frpc_template.txt", "r")
    conf_template_content = (conf_template.read())
    conf_template.close()
    s_list = get_server()
    m_list = get_mine()
    for i in s_list:
        create_client(i, m_list, conf_template_content)
    stop_client()


class App:
    # 图形界面部分
    def __init__(self, root_el):
        label_data_1 = ["服务器IP", "端口", "服务器密码", "用户名"]
        label_data_2 = ["本机IP", "端口", "类型", "子域名"]
        label_data = [StringVar(), StringVar(), StringVar(), StringVar()]
        form_data = [StringVar(), StringVar(), StringVar(), StringVar()]
        for i in range(4):
            label_data[i].set(label_data_1[i])

        def get_list_clicked():
            the_flag = 0
            the_index = -1
            if list_1.curselection():
                the_flag = 1
                the_index = list_1.curselection()[0]
            elif list_2.curselection():
                the_flag = 2
                the_index = list_2.curselection()[0]
            return {
                'x': the_index,
                'y': the_flag
            }

        def instant_data():
            apple = get_list_clicked()
            the_flag = apple['x']
            the_index = apple['y']
            if list_1.curselection():
                the_flag = 1
                the_index = list_1.curselection()[0]
            elif list_2.curselection():
                the_flag = 2
                the_index = list_2.curselection()[0]
            if the_flag == 1:
                for index in range(4):
                    label_data[index].set(label_data_1[index])
                form_data[0].set(li_1[the_index]['domain'])
                form_data[1].set(li_1[the_index]['port'])
                form_data[2].set(li_1[the_index]['token'])
                form_data[3].set(li_1[the_index]['username'])
            elif the_flag == 2:
                for index in range(4):
                    label_data[index].set(label_data_2[index])
                form_data[0].set(li_2[the_index]['ip'])
                form_data[1].set(li_2[the_index]['port'])
                form_data[2].set(li_2[the_index]['type'])
                form_data[3].set(li_2[the_index]['sub_domain'])

        root_el.title("FRP客户端")
        root_el.geometry('500x500')
        # 使用Frame增加一层容器
        fm1 = Frame(root_el)

        li_1 = get_server()
        list_1 = Listbox(fm1, width=15, height=10)
        for item in li_1:
            list_1.insert('end', item['domain'])

        li_2 = get_mine()
        list_2 = Listbox(fm1, width=15, height=10)
        for item in li_2:
            list_2.insert(-1, item['sub_domain'])

        list_1.pack(side=TOP, pady=10, fill=X)
        fm1_1 = Frame(fm1)
        Button(fm1_1, text='Add').pack(side=LEFT, anchor=W)
        Button(fm1_1, text='view', command=instant_data).pack(side=LEFT, anchor=W)
        fm1_1.pack(side=TOP, padx=10, pady=10, fill=BOTH)

        list_2.pack(side=TOP, pady=10, fill=X)
        fm1.pack(side=LEFT, padx=10, pady=10, fill=BOTH)

        fm2 = Frame(root_el)
        Label(fm2, textvariable=label_data[0]).grid(row=0)
        Label(fm2, textvariable=label_data[1]).grid(row=1)
        Label(fm2, textvariable=label_data[2]).grid(row=2)
        Label(fm2, textvariable=label_data[3]).grid(row=3)

        e_data_1 = Entry(fm2, textvariable=form_data[0])
        e_data_1.grid(row=0, column=1, padx=10, pady=5)
        e_data_2 = Entry(fm2, textvariable=form_data[1])
        e_data_2.grid(row=1, column=1, padx=10, pady=5)
        e_data_3 = Entry(fm2, textvariable=form_data[2])
        e_data_3.grid(row=2, column=1, padx=10, pady=5)
        e_data_4 = Entry(fm2, textvariable=form_data[3])
        e_data_4.grid(row=3, column=1, padx=10, pady=5)
        Button(fm2, text="保存", width=10, command=None).grid(row=4, column=1, sticky=W, padx=10, pady=5)
        fm2.pack(side=LEFT, padx=10, expand=YES)

# 启动图形界面，暂时注释掉
# root = Tk()
# app = App(root)
# root.mainloop()

# 启动函数 main
main()