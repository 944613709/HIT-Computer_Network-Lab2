import random
import select
import socket

from lab_code.main import Host


# 能够实现本地和远程相互发送
class GBN_TWO:

    def __init__(self, hostname,
                 local_socket=Host.host_socket_1,
                 remote_socket=Host.host_socket_2,
                 local_address=Host.host_address_1, remote_address=Host.host_address_2,
                 send_window_size=4,
                 read_path='../server_file/read_file.txt',
                 recv_path='../client_file/save_file.txt', ):
        self.hostname = hostname
        self.send_window_size = send_window_size  # 窗口尺寸默认为4
        self.send_base = 0  # 最小的被发送的分组序号
        self.next_pkt_seq = 0  # 当前未被利用的序号,真要被发送
        self.time_count = 0  # 记录当前传输时间
        self.time_out = 5  # 设置超时时间
        self.local_address = local_address  # 设置本地socket地址
        self.remote_address = remote_address  # 设置远程socket地址
        self.local_socket = local_socket
        self.remote_socket = remote_socket
        self.pkt_data_withoutSeq = []  # 缓存发送数据
        self.read_path = read_path  # 需要发送的源文件数据
        self.ack_buf_size = 10
        self.read_pkt_data_withoutSeq_size = 4096  # 发送方读取文件的缓存，pkt的size
        self.get_data_from_file()

        self.recv_data_buf_size = 9182  # 作为客户端接收数据缓存
        self.exp_seq = 0  # 当前期望收到该序号的数据
        self.recv_path = recv_path  # 接收数据时，保存数据的地址
        #   先查看是否存在该要写入的文件,如果不存在则新建
        # 如果存在，将最终保存文件内容提前清空，方便之后写入新内容
        self.write_data_to_file('', mode='w')

        self.pkt_loss = 0.1  # 发送数据丢包率
        self.ack_loss = 0  # 返回的ack丢包率
        self.flag_recv_ack_end = False  # 代表接收到ack还没有接收完
        self.flag_recv_pkt_end = False  # 代表接收到pkt还没有接收完
    # local->remote 能够发送pkt_two
    def send_pkt(self):
        if self.next_pkt_seq == len(self.pkt_data_withoutSeq):  # 所有的pkt都已经发送过一遍，如果出现丢包，让超时重发handle_time_out()去重发
            return
        if self.next_pkt_seq - self.send_base < self.send_window_size:  # 窗口中仍有可用空间
            # 大概率不丢包
            if random.random() > self.pkt_loss:
                # 发送格式‘pkt_num pkt_data_withoutSeq’ 比如'13 中国美国'
                self.local_socket.sendto(
                    Host.make_pkt_two(self.next_pkt_seq, self.pkt_data_withoutSeq[self.next_pkt_seq]),
                    self.remote_address)
                print(self.hostname + ':成功发送pkt数据' + str(self.next_pkt_seq))
                # 本次seq完成后next_seq加1
                self.next_pkt_seq = self.next_pkt_seq + 1
            else:  # 随机产生丢包行为
                # 小概率丢包
                print(self.hostname + ':成功发送pkt数据' + str(self.next_pkt_seq))
                print(self.hostname + '----但是pkt数据:' + str(self.next_pkt_seq) + ' 发生丢包----')
                # 本次seq完成后next_seq加1
                self.next_pkt_seq = self.next_pkt_seq + 1
        else:  # 窗口中无可用空间
            return

    # 启动接收功能，打开计时器
    # 功能有3个
    # loacl启动计时器
    # local接受remote发来的ack,计时器
    # local接受remote发来的pkt，发回ack
    # local可以发回ack
    def startTiming_and_Recv_ack_and_pkt(self):

        print("启动接收")
        # 原基础是收到pkt
        while True:
            # 结束本函数的条件是接收ack与pkt任务完成
            if (self.flag_recv_ack_end == True) and (self.flag_recv_pkt_end == True):
                print(str(self.hostname) + "接收ack与pkt任务完成")
                return
            try:
                rcv_data_init, client_address = self.local_socket.recvfrom(self.recv_data_buf_size)
                rcv_data = rcv_data_init.decode()
                rcv_seq = rcv_data.split()[0]  # 按照格式规约获取数据序号
                rcv_flag = rcv_data.split()[1]  # 拿到flag,0->pkt,1->ack
                rcv_data = rcv_data.replace(rcv_seq + ' ', '')  # 按照格式规约获取数据
                if (rcv_flag == '0'):  # 如果是拿到pkt
                    # 拿到pkt，就发回ack
                    if rcv_seq == '0' and rcv_data == '0':  # 接收到结束包
                        print(self.hostname + ':接收pkt,传输ACK结束')
                        self.flag_recv_pkt_end = True
                        continue
                    if int(rcv_seq) == self.exp_seq:  # 接收到按序数据包
                        print(self.hostname + ':收到期望pkt序号数据:' + str(rcv_seq))
                        self.write_data_to_file(rcv_data)  # 保存服务器端发送的数据到本地文件中
                        self.exp_seq = self.exp_seq + 1  # 期望数据的序号更新
                    else:
                        print(self.hostname + ':收到非期望pkt数据，期望:' + str(self.exp_seq) + '实际:' + str(rcv_seq))
                    if random.random() >= self.ack_loss:  # 随机丢包发送ack数据
                        print(self.hostname + "发送ack:" + str(self.exp_seq - 1))
                        self.local_socket.sendto(Host.make_ack_two(self.exp_seq - 1, 0), self.remote_address)

                elif (rcv_flag == '1'):
                    # 如果拿到的是ack
                    # 接收客户端发来的ACK数据
                    # 此时的rcv_data是ack
                    print(self.hostname + '收到对面发送方给的ACK序号:' + rcv_seq)
                    # 收到ACK之后更新起始序号，并且计时器清零
                    self.send_base = int(rcv_seq) + 1  # 滑动窗口的起始序号,累计确认
                    self.time_count = 0  # 计时器计次清0
                    # 如果我拿完了ack
                    if self.send_base == len(self.pkt_data_withoutSeq):  # 判断数据是否传输结束
                        # 在客户端自己编程时候约定rcv_seq == '0' and rcv_data == '0'为结束信号
                        self.local_socket.sendto(Host.make_pkt_two(0, 0), self.remote_address)  # 向客户端发送结束报文
                        print(str(self.hostname) + ':发送完毕')
                        self.flag_recv_ack_end = True

            except socket.timeout:  # 未收到ACK包
                self.time_count += 1  # 超时计次+1
                if self.time_count > self.time_out:  # 触发超时重传操作
                    self.handle_time_out()

    # 开始完整发送pkt
    def startSending(self):
        while True:  # 发送数据
            # local_address向remote_address发送数据
            # 发送一次
            self.send_pkt()  # 构造出数据段并且发送数据逻辑
            # 结束这个函数的条件是，查看是否发送pkt结束了
            if self.send_base == len(self.pkt_data_withoutSeq):  # 判断数据是否传输结束
                # 在客户端自己编程时候约定rcv_seq == '0' and rcv_data == '0'为结束信号
                self.local_socket.sendto(Host.make_pkt_two(0, 0), self.remote_address)  # 向客户端发送结束报文
                print(self.hostname + '发送方:发送pkt完毕')
                return

    # local没有收到按时ack，所以local重发pkt
    # 超时处理函数：计时器置0
    def handle_time_out(self):
        print(str(self.hostname) + '未按时收到ack超时，开始重传pkt')
        self.time_count = 0  # 超时计次重启
        for i in range(self.send_base, self.next_pkt_seq):  # 发送空中的所有分组
            self.local_socket.sendto(Host.make_pkt_two(i, self.pkt_data_withoutSeq[i]), self.remote_address)
            print('数据已重发:' + str(i))

    # 从文本中读取数据用于模拟上层协议数据的到来
    def get_data_from_file(self):
        f = open(self.read_path, 'r', encoding='utf-8')
        while True:
            send_data = f.read(self.read_pkt_data_withoutSeq_size)  # 一次读取1024个字节（如果有这么多）
            if len(send_data) <= 0:
                break
            self.pkt_data_withoutSeq.append(send_data)  # 将读取到的数据保存到data数据结构中
        print(str(self.hostname)+"将发送pkt最后一个序号为"+str(len(self.pkt_data_withoutSeq)-1))

    # 保存来自服务器的合适的数据
    def write_data_to_file(self, pkt_data_withoutSeq, mode='a'):
        with open(self.recv_path, mode, encoding='utf-8') as f:
            f.write(pkt_data_withoutSeq)  # 模拟将数据交付到上层
