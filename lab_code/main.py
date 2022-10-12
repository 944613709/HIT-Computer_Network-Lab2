import threading


class Host:
    # 规定发送数据格式：[seq_num data]
    # 规定发送确认格式：[exp_num-1 0]
    # 规定发送结束格式：[0 0]

    # 若无修改则默认为这个
    host_address_1 = ('127.0.0.1', 12341)  # 主机1的默认地址
    host_address_1_backup = ('127.0.0.1', 12342)  # 主机1的备用端口
    host_address_2 = ('127.0.0.1', 12343)  # 主机2的默认地址
    host_address_2_backup = ('127.0.0.1', 12344)  # 主机2的备用端口

    # 静态方法

    # Todo
    # 可改为用yaml作为配置文件
    # 用于配置主机地址
    @staticmethod
    def config(config_path='../file/config_file.txt'):
        import yaml
        f = open("./config/config.yaml")
        config_yaml = yaml.load(f, Loader=yaml.FullLoader)

        # print(config_yaml)
        # print("类型：", type(config_yaml))
        # print(config_yaml['host_address_1'])
        # 读取yaml文件的配置
        host_address_1 = config_yaml['host_address_1']
        host_address_2 = config_yaml['host_address_2']

        # 配置
        Host.host_address_1 = (host_address_1['ip'], host_address_1['port'])
        Host.host_address_1_backup = (host_address_1['ip'], host_address_1['portBackup'])#host1的备用端口
        Host.host_address_2 = (host_address_2['ip'], host_address_2['port'])
        Host.host_address_2_backup = (host_address_2['ip'], host_address_2['portBackup'])#host2的备用端口
        print("server设定为：" + host_address_1['ip'] + "  port:" + str(host_address_1['port']))
        print("client设定为：" + host_address_2['ip'] + "  port:" + str(host_address_2['port']))
        print()

    # 产生一个发送数据包或者确认数据包，数据包格式遵循本文件的规约
    @staticmethod
    def make_pkt(pkt_num, data):
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        # print(str(pkt_num) + ' ' + str(data))
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        return (str(pkt_num) + ' ' + str(data)).encode(encoding='utf-8')


# 通过该方法运行GBN协议
def run_gbn():
    from lab_code.gbn import GBN
    # 初始化执行init函数
    host_1 = GBN(Host.host_address_1, Host.host_address_2)
    host_2 = GBN(Host.host_address_2, Host.host_address_1)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_1.send_run).start()  # 注意这里函数一定不能带括号
    # 运行客户端,由host2发向host1
    threading.Thread(target=host_2.recv_run).start()  # 注意这里函数一定不能带括号


# 通过该方法运行GBN协议的双向传输(半双工)
def run_gbn_two_way_half():
    from lab_code.gbn import GBN
    # 指定读取路径
    #read发送方读取并发送
    read_path1 = '../server_file/read_file.txt'
    read_path2 = '../client_file/readpic.png'
    #save接收方接收并保存
    save_path1 = '../client_file/save_file.txt'
    save_path2 = '../server_file/savepic.png'
    # # host1向host2发数据
    # host_1 = GBN(Host.host_address_1, Host.host_address_2, 4,read_path1,save_path1)
    # host_2 = GBN(Host.host_address_2, Host.host_address_1, 4, read_path1, save_path1)
    # # host1为服务器，host2为客户端
    # # 多线程执行
    # # 运行服务器端,由host1发向host2
    # threading.Thread(target=host_1.send_run).start()  # 注意这里函数一定不能带括号
    # # 运行客户端,由host2发向host1
    # threading.Thread(target=host_2.recv_run).start()  # 注意这里函数一定不能带括号
    #
    # # 与此同时
    # # host2向host1发数据
    # host_2 = GBN(Host.host_address_1_backup, Host.host_address_2, 4, read_path2, save_path2)
    # host_1 = GBN(Host.host_address_2, Host.host_address_1, 4, read_path2, save_path2)
    # # 多线程执行
    # threading.Thread(target=host_2.send_run).start()  # 注意这里函数一定不能带括号
    # threading.Thread(target=host_1.recv_run).start()  # 注意这里函数一定不能带括号
# 通过该方法运行SR协议
def run_sr():
    from lab_code.sr import SR
    host_1 = SR(Host.host_address_1, Host.host_address_2)
    host_2 = SR(Host.host_address_2, Host.host_address_1)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_1.send_run).start()  # 注意这里函数一定不能带括号
    threading.Thread(target=host_2.recv_run).start()  # 注意这里函数一定不能带括号


def run_rdt():
    # 停等协议就是GBN发送窗口大小尺寸为1
    from lab_code.gbn import GBN
    # 初始化执行init函数
    host_1 = GBN(Host.host_address_1, Host.host_address_2, 1)
    host_2 = GBN(Host.host_address_2, Host.host_address_1, 1)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_1.send_run).start()  # 注意这里函数一定不能带括号
    # 运行客户端,由host2发向host1
    threading.Thread(target=host_2.recv_run).start()  # 注意这里函数一定不能带括号


# 可运行代码块，用户输入协议进行选择，并运行相应的协议程序
if __name__ == '__main__':
    Host.config()  # 配置要运行的发送方和接收方信息
    choice = input('请选择要运行的协议:输入‘GBN’表示运行GBN，‘SR’表示运行SR协议,''rdt''表示运行停等协议,''GBN_two_half''表示运行GBN双向(半双工）')
    if choice == 'GBN':
        run_gbn()
    elif choice == 'GBN_two_half':
            run_gbn_two_way_half()
    elif choice == 'SR':
        run_sr()
    elif choice == 'rdt':
        run_rdt()
    else:
        print('输入非法字串，请重新运行程序')
