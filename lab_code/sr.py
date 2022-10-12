import random
import select
import socket

from lab_code.main import Host


class SR:

    def __init__(self, local_address=Host.host_address_1, remote_address=Host.host_address_2, window_size=4 ,read_path = '../server_file/read_file.txt',recv_path = '../client_file/save_file.txt'):
        self.send_window_size =  window_size  # 窗口尺寸默认是4
        self.send_base = 0  # 最小的被发送的分组序号
        self.next_seq = 0  # 当前未被利用的序号
        self.time_out = 5  # 设置超时时间
        self.local_address = local_address  # 设置本地socket地址
        self.remote_address = remote_address  # 设置远程socket地址
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.local_address)  # 绑定套接字的本地IP地址和端口号
        self.data = []  # 缓存发送数据
        self.read_path = read_path # 需要发送的源文件数据
        self.ack_buf_size = 10
        self.get_data_from_file()

        self.rcv_window_size = 4  # 接受窗口尺寸
        self.data_buf_size = 1678  # 作为客户端接收数据缓存
        self.recv_path = recv_path  # 接收数据时，保存数据的地址
        self.write_data_to_file('', mode='w')

        self.pkt_loss = 0.1  # 发送数据丢包率
        self.ack_loss = 0  # 返回的ack丢包率

        self.time_counts = {}  # 存储窗口中每个发出序号的时间
        self.ack_seqs = {}  # 储存发送窗口中接受每个序号的ack情况

        self.rcv_base = 0  # 最小的需要接收的数据的分组序号
        self.rcv_data = {}  # 缓存失序的接收数据

    # 若仍剩余窗口空间，则构造数据报发送；否则拒绝发送数据
    def send_data(self):
        if self.next_seq == len(self.data):  # 判断是否还有缓存数据可以发送
            print('服务器:发送完毕，等待确认')
            return
        # 先检查发送窗口空间
        if self.next_seq < self.send_base + self.send_window_size:  # 窗口中仍有可用空间
            # 需要发送pkt

            # 大概率发送pkt不丢包
            if random.random() > self.pkt_loss:
                self.socket.sendto(Host.make_pkt(self.next_seq, self.data[self.next_seq]),
                                   self.remote_address)
                self.time_counts[self.next_seq] = 0  # 设置计时器
                self.ack_seqs[self.next_seq] = False  # 设置为未接受确认包
                print('服务器:发送数据' + str(self.next_seq))
                self.next_seq += 1
            else:# 小概率发送pkt丢包
                self.time_counts[self.next_seq] = 0  # 设置计时器
                self.ack_seqs[self.next_seq] = False  # 设置为未接受确认包
                print('服务器:发送数据' + str(self.next_seq))
                print("---数据:"+str(self.next_seq)+"发生丢包-------")
                self.next_seq += 1
        else:  # 窗口中无可用空间
            print('服务器:窗口已满，暂不发送数据')

    # 超时处理函数：计时器置0，设为未接受ACK，同时发送该序列号数据
    def handle_time_out(self, time_out_seq):
        print('超时重传:' + str(time_out_seq))
        self.time_counts[time_out_seq] = 0  # 重新定时
        if random.random() > self.pkt_loss:  # 随机发送数据包
            self.socket.sendto(Host.make_pkt(time_out_seq, self.data[time_out_seq]),
                               self.remote_address)
        else:
            print('---超时重传的:' + str(time_out_seq)+"发生丢包-----")

    # 从文件中读取数据，并存储到data属性里
    def get_data_from_file(self):
        f = open(self.read_path, 'r', encoding='utf-8')
        while True:
            send_data = f.read(1024)  # 一次读取1024个字节（如果有这么多）
            if len(send_data) <= 0:
                break
            self.data.append(send_data)  # 将读取到的数据保存到data数据结构中

    # server用的，发送窗口
    # 滑动窗口，用于接收到最小的ack后调用
    def slide_send_window(self):
        # 检测发送窗口的ack缓存 ack_seqs
        while self.ack_seqs.get(self.send_base):  # 一直滑动到未接收到ACK的分组序号处
            del self.ack_seqs[self.send_base]  # 从dict数据结构中删除此关键字
            del self.time_counts[self.send_base]  # 从dict数据结构中删除此关键字
            self.send_base = self.send_base + 1  # 滑动窗口
            print('服务器:窗口滑动到' + str(self.send_base))

    def send_run(self):
        while True:
            self.send_data()  # 服务器向客户端发送数据

            # 准备接受客户端发回的ACK
            readable = select.select([self.socket], [], [], 1)[0]  # 非阻塞方法
            if len(readable) > 0:  # 接收ACK数据
                # rcv_ack收到的ack序号
                rcv_ack = self.socket.recvfrom(self.ack_buf_size)[0].decode().split()[0]
                # 如果收到的ack序号是在范围内的
                if self.send_base <= int(rcv_ack) < self.next_seq:  # 收到ack，则标记为已确认且超时计数为0
                    print('服务器:收到有用ACK' + rcv_ack)
                    # 标记rcv_ack序号对应的数据ACK已经被服务器接受
                    self.ack_seqs[int(rcv_ack)] = True  # 设为已接受
                    if self.send_base == int(rcv_ack):  # 收到的ack为最小的窗口序号
                        self.slide_send_window()  # 则滑动窗口
                else:
                    print('服务器:收到无用ACK' + rcv_ack)

            #   对没有接收到ACK的计时器，计数+1
            for seq in self.time_counts.keys():  # 每个未接收的分组的时长都加1
                if not self.ack_seqs[seq]:  # 若未收到ACK
                    self.time_counts[seq] += 1  # 则计次+1
                    if self.time_counts[seq] > self.time_out:  # 触发超时操作
                        self.handle_time_out(seq)  # 超时处理
            if self.send_base == len(self.data):  # 数据传输结束
                self.socket.sendto(Host.make_pkt(0, 0), self.remote_address)  # 发送传输结束包
                print('服务器:数据传输结束')
                break

    # 保存来自服务器的合适的数据
    def write_data_to_file(self, data, mode='a'):
        with open(self.recv_path, mode, encoding='utf-8') as f:
            f.write(data)

    # 主要执行函数，不断接收服务器发送的数据，若失序则保存到缓存；若按序则滑动窗口；否则丢弃
    def recv_run(self):
        while True:
            readable = select.select([self.socket], [], [], 1)[0]  # 非阻塞接受
            if len(readable) > 0:
                rcv_data = self.socket.recvfrom(self.data_buf_size)[0].decode()
                rcv_seq = rcv_data.split()[0]  # 提取数据包序号
                rcv_data = rcv_data.replace(rcv_seq + ' ', '')  # 提取数据包数据
                # 最终rcv_seq代表序号
                # rcv_data代表纯数据

                # 收到结束信号
                if rcv_seq == '0' and rcv_data == '0':  # 收到传输数据结束的标志
                    print('客户端:传输数据结束')
                    break

                # 正常收到了一则数据
                print('客户端:收到数据' + rcv_seq)
                if self.rcv_base - self.rcv_window_size <= int(
                        rcv_seq) < self.rcv_base + self.rcv_window_size:

                    # 1.如果接收到的数据可以在缓存中被接受
                    if self.rcv_base <= int(rcv_seq) < self.rcv_base + self.rcv_window_size:  # 窗口内

                        # 缓存失序的接收数据
                        # rcv_data是dict，映射rcv_seq---->data(对应)
                        self.rcv_data[int(rcv_seq)] = rcv_data  # 失序的数据到来:缓存+发送ack

                        # 如果刚好是滑动窗口最左侧base，则进行滑动
                        if int(rcv_seq) == self.rcv_base:  # 按序数据的到来:滑动窗口并交付数据(清除对应的缓冲区)
                            self.slide_rcv_window()

                    # 2.发送ACK遇上的情况
                    # 大概率正常发送ACK不丢包
                    if random.random() >= self.ack_loss:
                        self.socket.sendto(Host.make_pkt(int(rcv_seq), 0), self.remote_address)
                        print('客户端:发送ACK' + rcv_seq)
                    else:
                        # 小概率ACK丢包
                        print('客户端:发送ACK' + rcv_seq)
                        print('----ACK:' + str(rcv_seq) + ' 发生丢包')

    # client用的，接收窗口
    # 滑动接收窗口:滑动rcv_base，向上层交付数据，并清除已交付数据的缓存
    # 按序数据的到来:滑动窗口并交付数据(清除对应的缓冲区)，然后滑动窗口直接跨过应该滑走的的
    def slide_rcv_window(self):
        # 检查client接收窗口的pkt缓存rcv_data
        while self.rcv_data.get(self.rcv_base) is not None:  # 循环直到出现未接受的数据包
            self.write_data_to_file(self.rcv_data.get(self.rcv_base))  # 写入文件
            del self.rcv_data[self.rcv_base]  # 清除该缓存
            self.rcv_base = self.rcv_base + 1  # 滑动窗口最左侧向前滑动+1
            print('客户端:滑动窗口最左侧滑动到' + str(self.rcv_base))
