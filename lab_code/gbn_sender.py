import random
import select
import socket

from lab_code.main import Host


class GBN_Sender:

    def __init__(self,sender_socket, local_address=Host.host_address_1, remote_address=Host.host_address_2, send_window_size=4,
                 read_path='../server_file/read_file.txt'):
        self.window_size = send_window_size  # 窗口尺寸默认为4
        self.send_base = 0  # 最小的被发送的分组序号
        self.next_seq = 0  # 当前未被利用的序号
        self.time_count = 0  # 记录当前传输时间
        self.time_out = 5  # 设置超时时间
        self.local_address = local_address  # 设置本地socket地址
        self.remote_address = remote_address  # 设置远程socket地址
        self.socket = sender_socket
        self.pkt_data_withoutSeq = []  # 缓存pkt的data部分分组，
        self.read_path = read_path  # 需要发送的源文件数据
        #recvfrom（）允许接收到ack的缓存大小
        self.ack_buf_size = 20
        self.pkt_data_size = 1024
        #读取发送方要发送的文件，转为byte和pkt分组
        self.get_data_from_file()
        self.exp_seq = 0  # 当前期望收到该序号的数据
        self.pkt_loss = 0.1  # 发送数据丢包率

    # 向remote_address发送数据
    # 若仍剩余窗口空间，则构造数据报发送；否则拒绝发送数据
    def send_pkt(self):
        # next_seq为下一个待发送的序号
        # next_seq从0开始
        if self.next_seq == len(self.pkt_data_withoutSeq):  # data数据已全部被发送过
            print('发送方:发送完毕，等待确认')
            return

        # self.next_seq  < self.window_size+self.send_base
        if self.next_seq - self.send_base < self.window_size:  # 窗口中仍有可用空间
            # random.random()返回一个0到1的数字\
            # pkt_loss = 0.1

            # 大概率不丢包
            if random.random() > self.pkt_loss:
                # 发送格式‘pkt_num pkt_data_withoutSeq’ 比如'13 中国美国'
                self.socket.sendto(Host.make_pkt(self.next_seq, self.pkt_data_withoutSeq[self.next_seq]),
                                   self.remote_address)
                print('发送方:成功发送数据' + str(self.next_seq))
                # 本次seq完成后next_seq加1
                self.next_seq = self.next_seq + 1
            else:  # 随机产生丢包行为
                # 小概率丢包
                print('发送方:成功发送数据' + str(self.next_seq))
                print('----但是数据:' + str(self.next_seq) + ' 发生丢包----')
                # 本次seq完成后next_seq加1
                self.next_seq = self.next_seq + 1
        else:  # 窗口中无可用空间
            print('发送方：窗口已满，暂不发送数据')

    # 超时处理函数：计时器置0
    def handle_time_out(self):
        print('超时，开始重传')
        self.time_count = 0  # 超时计次重启
        for i in range(self.send_base, self.next_seq):  # 发送空中的所有分组
            if random.random() > self.pkt_loss:  # 概率性重传
                self.socket.sendto(Host.make_pkt(i, self.pkt_data_withoutSeq[i]), self.remote_address)
            print('数据已重发:' + str(i))

    # 读取数据划分pkt
    # 从文本中读取数据用于模拟上层协议数据的到来
    def get_data_from_file(self):
        f = open(self.read_path, 'r', encoding='utf-8')
        while True:
            send_data = f.read(self.pkt_data_size)  # 一次读取1024个字节（如果有这么多）
            if len(send_data) <= 0:
                break
            self.pkt_data_withoutSeq.append(send_data)  # 将读取到的数据保存到data数据结构中
        print('PKT总数是:' + str(len(self.pkt_data_withoutSeq)))

    # 线程执行函数，不断发送数据并接收ACK报文做相应的处理
    def send_run(self):
        while True:

            # local_address向remote_address发送数据
            self.send_pkt()  # 构造出数据段并且发送数据逻辑
            # IO多路复用类似listen
            readable = select.select([self.socket], [], [], 1)[0]

            #################
            # r_list, w_list, e_list = select.select(inputs, [], inputs, 1)
            # select中第1个参数表示对read关注，中发生变化的句柄放入r_list。
            # select中第2个参数表示[]
            # 中的值原封不动的传递给w_list。
            # select中第3个参数表示inputs中发生错误的句柄放入e_list。
            #####################
            # readble代表接收到通知可以recvfrom
            # 服务器等待接受ACK
            if len(readable) > 0:
                # 接收客户端发来的ACK数据
                rcv_ack_seq = self.socket.recvfrom(self.ack_buf_size)[0].decode().split()[0]
                print('收到客户端ACK:' + rcv_ack_seq)
                # 收到ACK之后更新起始序号，并且计时器清零
                self.send_base = int(rcv_ack_seq) + 1  # 滑动窗口的起始序号
            else:  # 未收到ACK包
                self.time_count += 1  # 超时计次+1
                if self.time_count > self.time_out:  # 触发超时重传操作
                    self.handle_time_out()
            if self.send_base == len(self.pkt_data_withoutSeq):  # 判断数据是否传输结束
                # 在客户端自己编程时候约定rcv_seq == '0' and rcv_data == '0'为结束信号
                self.socket.sendto(Host.make_pkt(0, 0), self.remote_address)  # 向客户端发送结束报文
                print('发送方:发送完毕')
                break
