import threading
import socket

class Host:
    # 规定发送数据格式：[seq_num data]
    # 规定发送确认格式：[exp_num-1 0]
    # 规定发送结束格式：[0 0]

    # 若无修改则默认为这个
    host_address_1 = ('127.0.0.1', 12341)  # 主机1的默认地址
    host_address_2 = ('127.0.0.1', 12343)  # 主机2的默认地址
    host_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 静态方法

    # Todo
    # 可改为用yaml作为配置文件
    # 用于配置主机地址
    @staticmethod
    def config(config_path='../file/config_file.txt'):
        import yaml
        f = open("./config/config.yaml")
        config_yaml = yaml.load(f, Loader=yaml.FullLoader)

        # 读取yaml文件的配置
        host_address_1 = config_yaml['host_address_1']
        host_address_2 = config_yaml['host_address_2']

        # 配置
        Host.host_address_1 = (host_address_1['ip'], host_address_1['port'])
        Host.host_address_1_backup = (host_address_1['ip'], host_address_1['portBackup'])  # host1的备用端口
        Host.host_address_2 = (host_address_2['ip'], host_address_2['port'])
        Host.host_address_2_backup = (host_address_2['ip'], host_address_2['portBackup'])  # host2的备用端口
        print("server设定为：" + host_address_1['ip'] + "  port:" + str(host_address_1['port']))
        print("client设定为：" + host_address_2['ip'] + "  port:" + str(host_address_2['port']))
        # 初始化以UDP为基础的hostsocket
        Host.host_socket_1.bind(Host.host_address_1)
        Host.host_socket_2.bind(Host.host_address_2)  # 绑定套接字的本地IP地址和端口号
        print()

    # 产生一个发送数据包或者确认数据包，数据包格式遵循本文件的规约
    @staticmethod
    def make_pkt(pkt_num, data):
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        # print(str(pkt_num) + ' ' + str(data))
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        return (str(pkt_num) + ' ' + str(data)).encode(encoding='utf-8')


    # 产生一个发送数据包或者确认数据包，数据包格式遵循本文件的规约
    @staticmethod
    def make_ack(pkt_num, data=0):
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        # print(str(pkt_num) + ' ' + str(data))
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        return (str(pkt_num) + ' ' + str(data)).encode(encoding='utf-8')

    # 产生一个发送数据包或者确认数据包，数据包格式遵循本文件的规约
    @staticmethod
    def make_pkt_two(pkt_num, data):
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        # print(str(pkt_num) + ' ' + str(data))
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        return (str(pkt_num) + ' ' + '0' + ' '+str(data)).encode(encoding='utf-8')
        #第二位flag = 0->代表是pkt

    # 用于全双工的
    @staticmethod
    def make_ack_two(pkt_num, data=0):
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        # print(str(pkt_num) + ' ' + str(data))
        # print('"线程:"+str(threading.current_thread().ident)+-------------pkt----------')
        return (str(pkt_num) + ' ' + '1' + ' '+ str(data)).encode(encoding='utf-8')
        # 第二位flag=1代表为ack

# 通过该方法运行GBN协议
def run_gbn():
    from lab_code.gbn_sender import GBN_Sender
    from lab_code.gbn_receiver import GBN_Receiver
    # 指定读取路径
    # read发送方读取并发送
    read_path1 = '../server_file/read_file.txt'
    # save接收方接收并保存
    recv_path1 = '../client_file/save_file.txt'
    # 初始化执行init函数
    host_1_sender = GBN_Sender(Host.host_socket_1,Host.host_address_1, Host.host_address_2,4,read_path1)
    host_2_receiver = GBN_Receiver(Host.host_socket_2,Host.host_address_2, Host.host_address_1,recv_path1)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_1_sender.send_run).start()  # 注意这里函数一定不能带括号
    # 运行客户端,由host2发向host1
    threading.Thread(target=host_2_receiver.recv_run).start()  # 注意这里函数一定不能带括号


# 通过该方法运行GBN协议的双向传输(全双工)
def run_gbn_two_way():
    from lab_code.gbn_two import GBN_TWO
    # 新的_two_host
    host_address_1_two = ('127.0.0.1', 22341)  # 主机1的默认地址
    host_address_2_two = ('127.0.0.1', 22343)  # 主机2的默认地址
    host_socket_1_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_1_two.bind(host_address_1_two)
    host_socket_2_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_2_two.bind(host_address_2_two)
    #这个socket特殊,利用settimeout（）
    host_socket_1_two.settimeout(1)# 1秒，计数器次数加1
    host_socket_2_two.settimeout(1)
    # 指定读取路径
    # read发送方读取并发送
    read_path1 = '../server_file/read_file.txt'
    read_path2 = '../client_file/read_file2.txt'
    # save接收方接收并保存
    recv_path1 = '../client_file/save_file.txt'
    recv_path2 = '../server_file/save_file2.txt'
    host_1_sender_receiver = GBN_TWO("host1",host_socket_1_two,host_socket_2_two,host_address_1_two,host_address_2_two,4,read_path1,recv_path2)
    host_2_sender_receiver = GBN_TWO("Host2",host_socket_2_two,host_socket_1_two,host_address_2_two,host_address_1_two,4,read_path2,recv_path1)
    threading.Thread(target=host_1_sender_receiver.startSending).start()
    threading.Thread(target=host_2_sender_receiver.startSending).start()
    threading.Thread(target=host_1_sender_receiver.startTiming_and_Recv_ack_and_pkt).start()
    threading.Thread(target=host_2_sender_receiver.startTiming_and_Recv_ack_and_pkt).start()


# 通过该方法运行SR协议
def run_sr_two_way():
    from lab_code.sr_two import SR_TWO
    # 新的_two_host
    host_address_1_two = ('127.0.0.1', 22341)  # 主机1的默认地址
    host_address_2_two = ('127.0.0.1', 22343)  # 主机2的默认地址
    host_socket_1_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_1_two.bind(host_address_1_two)
    host_socket_2_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_2_two.bind(host_address_2_two)
    #这个socket特殊,利用settimeout（）
    host_socket_1_two.settimeout(1)# 1秒，计数器次数加1
    host_socket_2_two.settimeout(1)
    # 指定读取路径
    # read发送方读取并发送
    read_path1 = '../server_file/read_file.txt'
    read_path2 = '../client_file/read_file2.txt'
    # save接收方接收并保存
    recv_path1 = '../client_file/save_file.txt'
    recv_path2 = '../server_file/save_file2.txt'
    host_1_sender_receiver = SR_TWO("host1",host_socket_1_two,host_socket_2_two,host_address_1_two, host_address_2_two,4,read_path1,recv_path2)
    host_2_sender_receiver = SR_TWO("host2",host_socket_2_two,host_socket_1_two,host_address_2_two, host_address_1_two,4,read_path2,recv_path1)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_1_sender_receiver.startSending).start()
    threading.Thread(target=host_2_sender_receiver.startSending).start()
    threading.Thread(target=host_1_sender_receiver.startTiming_and_Recv_ack_and_pkt).start()
    threading.Thread(target=host_2_sender_receiver.startTiming_and_Recv_ack_and_pkt).start()
# 通过该方法运行SR协议
def run_sr():
    from lab_code.sr import SR
    host_address_3 = ('127.0.0.1', 32341)  # 主机1的默认地址
    host_address_4 = ('127.0.0.1', 42343)  # 主机2的默认地址
    host_3 = SR(host_address_3, host_address_4)
    host_4 = SR(host_address_4, host_address_3)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_3.send_run).start()  # 注意这里函数一定不能带括号
    threading.Thread(target=host_4.recv_run).start()  # 注意这里函数一定不能带括号

def run_rdt():
    # 停等协议就是GBN发送窗口大小尺寸为1
    from lab_code.gbn_sender import GBN_Sender
    from lab_code.gbn_receiver import GBN_Receiver
    # 指定读取路径
    # read发送方读取并发送
    read_path1 = '../server_file/read_file.txt'
    # save接收方接收并保存
    recv_path1 = '../client_file/save_file.txt'
    # 初始化执行init函数
    host_1_sender = GBN_Sender(Host.host_socket_1,Host.host_address_1, Host.host_address_2,1,read_path1)
    host_2_receiver = GBN_Receiver(Host.host_socket_2,Host.host_address_2, Host.host_address_1,recv_path1)
    # host1为服务器，host2为客户端
    # 多线程执行
    # 运行服务器端,由host1发向host2
    threading.Thread(target=host_1_sender.send_run).start()  # 注意这里函数一定不能带括号
    # 运行客户端,由host2发向host1
    threading.Thread(target=host_2_receiver.recv_run).start()  # 注意这里函数一定不能带括号

def run_rdt_two_way():
    from lab_code.gbn_two import GBN_TWO
    # 新的_two_host
    host_address_1_two = ('127.0.0.1', 22341)  # 主机1的默认地址
    host_address_2_two = ('127.0.0.1', 22343)  # 主机2的默认地址
    host_socket_1_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_1_two.bind(host_address_1_two)
    host_socket_2_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket_2_two.bind(host_address_2_two)
    #这个socket特殊,利用settimeout（）
    host_socket_1_two.settimeout(1)# 1秒，计数器次数加1
    host_socket_2_two.settimeout(1)
    # 指定读取路径
    # read发送方读取并发送
    read_path1 = '../server_file/read_file.txt'
    read_path2 = '../client_file/read_file2.txt'
    # save接收方接收并保存
    recv_path1 = '../client_file/save_file.txt'
    recv_path2 = '../server_file/save_file2.txt'
    host_1_sender_receiver = GBN_TWO("host1",host_socket_1_two,host_socket_2_two,host_address_1_two,host_address_2_two,1,read_path1,recv_path1)
    host_2_sender_receiver = GBN_TWO("Host2",host_socket_2_two,host_socket_1_two,host_address_2_two,host_address_1_two,1,read_path2,recv_path2)
    threading.Thread(target=host_1_sender_receiver.startSending).start()
    threading.Thread(target=host_2_sender_receiver.startSending).start()
    threading.Thread(target=host_1_sender_receiver.startTiming_and_Recv_ack_and_pkt).start()
    threading.Thread(target=host_2_sender_receiver.startTiming_and_Recv_ack_and_pkt).start()

# 可运行代码块，用户输入协议进行选择，并运行相应的协议程序
if __name__ == '__main__':
    Host.config()  # 配置要运行的发送方和接收方信息
    choice = input('请选择要运行的协议:输入‘GBN’表示运行GBN，‘SR’表示运行SR协议,''rdt''表示运行停等协议,''GBN_two_way''表示运行GBN双向(全双工），''rdt_two_way''表示停等协议的双向（全双工）,"sr_two_way"'
                   '表示SR协议的双向（全双工')
    if choice == 'GBN':
        run_gbn()
    elif choice == 'GBN_two_way':
        run_gbn_two_way()
    elif choice == 'SR':
        run_sr()
    elif choice == 'rdt':
        run_rdt()
    elif choice == 'rdt_two_way':
        run_rdt_two_way()
    elif choice == 'sr_two_way':
        run_sr_two_way()
    else:
        print('输入非法字串，请重新运行程序')
