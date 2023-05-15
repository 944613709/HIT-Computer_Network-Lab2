import random
import select
import socket

from lab_code.main import Host


# 能够实现本地和远程相互发送
class SR_TWO:

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
        self.rcv_base = 0  # 最小的需要接收的数据的分组序号
        self.rcv_data = {}  # 缓存失序的接收数据
        self.rcv_window_size = 4  # 接受窗口尺寸

        self.time_counts = {}  # 存储窗口中每个发出序号的时间
        self.ack_seqs = {}  # 储存发送窗口中接受每个序号的ack情况

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
                self.time_counts[self.next_pkt_seq] = 0  # 设置计时器
                self.ack_seqs[self.next_pkt_seq] = False  # 设置为未接受确认包
                print(self.hostname + ':成功发送pkt' + str(self.next_pkt_seq))
                # 本次seq完成后next_seq加1
                self.next_pkt_seq = self.next_pkt_seq + 1
            else:  # 随机产生丢包行为
                # 小概率丢包
                self.time_counts[self.next_pkt_seq] = 0  # 设置计时器
                self.ack_seqs[self.next_pkt_seq] = False  # 设置为未接受确认包
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

            #SR是按照每次给未收到ACK的那个分组+1计时器
            time_counts_temp = self.time_counts
            for seq in list(time_counts_temp.keys()):  # 每个未接收的分组的时长都加1
                if not self.ack_seqs[seq]:  # 若未收到ACK
                    self.time_counts[seq] += 1  # 则计次+1
                    if self.time_counts[seq] > self.time_out:  # 触发超时操作
                        self.handle_time_out(seq)  # 超时处理
            try:
                rcv_data_init, client_address = self.local_socket.recvfrom(self.recv_data_buf_size)
                rcv_data = rcv_data_init.decode()
                rcv_seq = rcv_data.split()[0]  # 按照格式规约获取数据序号
                rcv_flag = rcv_data.split()[1]  # 拿到flag,0->pkt,1->ack
                rcv_data = rcv_data.replace(rcv_seq + ' ', '')  # 按照格式规约获取数据
                if (rcv_flag == '0'):
                    #如果是接收方收到pkt
                    # 收到结束信号
                    if rcv_seq == '0' and rcv_data == '0':  # 收到传输数据结束的标志
                        print(self.hostname + ':接收pkt,传输ACK结束')
                        self.flag_recv_pkt_end = True
                        continue
                    # 正常收到了一则数据
                    print(self.hostname +':收到pkt' + rcv_seq)
                    # 序号在[rcv_base - N, rcv_base + N - 1]内的分组被正确收到。在此情况下，必须产生ACK, 即使该分组是接收方以前已确认过的分组。
                    # 为防止之前发送的ack丢失
                    if self.rcv_base - self.rcv_window_size <= int(rcv_seq) < self.rcv_base + self.rcv_window_size:
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
                            self.local_socket.sendto(Host.make_ack_two(int(rcv_seq), 0), self.remote_address)
                            print(self.hostname +':发送ACK' + rcv_seq)
                        else:
                            # 小概率ACK丢包
                            print(self.hostname +':发送ACK' + rcv_seq)
                            print(self.hostname +'----ACK:' + str(rcv_seq) + ' 发生丢包')
                        # 针对接收方如果是拿到pkt
                        # 拿到pkt，就发回ack
                        # if rcv_seq == '0' and rcv_data == '0':  # 接收到结束包
                        #     print(self.hostname + ':接收pkt,传输ACK结束')
                        #     self.flag_recv_pkt_end = True
                        #     continue
                        # if int(rcv_seq) == self.exp_seq:  # 接收到按序数据包
                        #     print(self.hostname + ':收到期望pkt序号数据:' + str(rcv_seq))
                        #     self.write_data_to_file(rcv_data)  # 保存服务器端发送的数据到本地文件中
                        #     self.exp_seq = self.exp_seq + 1  # 期望数据的序号更新
                        # else:
                        #     print(self.hostname + ':收到非期望pkt数据，期望:' + str(self.exp_seq) + '实际:' + str(rcv_seq))
                        # if random.random() >= self.ack_loss:  # 随机丢包发送ack数据
                        #     print(self.hostname + "发送ack:" + str(self.exp_seq - 1))
                        #     self.local_socket.sendto(Host.make_ack_two(self.exp_seq - 1, 0), self.remote_address)

                elif (rcv_flag == '1'):
                    # 这个是对于发送方
                    # 如果拿到的是ack
                    # 接收客户端发来的ACK数据
                    # 此时的rcv_data是ack
                    print(self.hostname + '收到对面发送方给的ACK序号:' + rcv_seq)
                    # 收到ACK之后更新起始序号，并且计时器清零
                    #将刚刚收到的ack加入缓存,标记已加入缓存
                    self.ack_seqs[int(rcv_seq)] = True
                    if(self.send_base == int(rcv_seq)): # 如果可以滑动了
                        self.slide_send_window() #向右滑动窗口
                    # 如果我拿完了ack
                    flag_recv_ack_end = True
                    for i in range(0,len(self.pkt_data_withoutSeq)):
                        ack_seq_flag = self.ack_seqs.get(i,False)
                        if ack_seq_flag == False: #只要有一个没有拿到
                            flag_recv_ack_end =False#则还没有收完ack
                    # 否则收完了ack
                    self.flag_recv_pkt_end = flag_recv_ack_end
                    #对于发送方，send_base滑倒len(self.pkt_data_withoutSeq)就是结束了
                    if self.send_base == len(self.pkt_data_withoutSeq):  # 判断数据是否传输结束
                        # 在客户端自己编程时候约定rcv_seq == '0' and rcv_data == '0'为结束信号
                        self.local_socket.sendto(Host.make_pkt_two(0, 0), self.remote_address)  # 向客户端发送结束报文
                        print(str(self.hostname) + ':发送完毕')
                        self.flag_recv_ack_end = True
            except socket.timeout:
                continue

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
                print(self.hostname + ':发送pkt完毕')
                return

    # # local没有收到按时ack，所以local重发pkt
    # # 超时处理函数：计时器置0
    # def handle_time_out(self):
    #     print(str(self.hostname) + '未按时收到ack超时，开始重传pkt')
    #     self.time_count = 0  # 超时计次重启
    #     for i in range(self.send_base, self.next_pkt_seq):  # 发送空中的所有分组
    #         self.local_socket.sendto(Host.make_pkt_two(i, self.pkt_data_withoutSeq[i]), self.remote_address)
    #         print('数据已重发:' + str(i))

    # 超时处理函数：计时器置0，设为未接受ACK，同时发送该序列号数据
    def handle_time_out(self, time_out_seq):
        print('超时重传:' + str(time_out_seq))
        self.time_counts[time_out_seq] = 0  # 重新定时
        if random.random() > self.pkt_loss:  # 随机发送数据包
            self.local_socket.sendto(Host.make_pkt_two(time_out_seq, self.pkt_data_withoutSeq[time_out_seq]),
                               self.remote_address)
        else:
            print(self.hostname +'---超时重传的:' + str(time_out_seq) + "发生丢包-----")

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

    # server用的，发送窗口
    # 被滑走的发送党员，在这删除计时器
    # 滑动窗口，用于接收到最小的ack后调用
    def slide_send_window(self):
        # 检测发送窗口的ack缓存 ack_seqs
        while self.ack_seqs.get(self.send_base):  # 一直滑动到未接收到ACK的分组序号处
            del self.ack_seqs[self.send_base]  # 从dict数据结构中删除此关键字
            del self.time_counts[self.send_base]  # 从dict数据结构中删除此关键字
            self.send_base = self.send_base + 1  # 滑动窗口
            print(self.hostname +':发送窗口滑动到' + str(self.send_base))


    # client用的，接收窗口
    # 滑动接收窗口:滑动rcv_base，向上层交付数据，并清除已交付数据的缓存
    # 按序数据的到来:滑动窗口并交付数据(清除对应的缓冲区)，然后滑动窗口直接跨过应该滑走的的
    def slide_rcv_window(self):
        # 检查client接收窗口的pkt缓存rcv_data
        while self.rcv_data.get(self.rcv_base) is not None:  # 循环直到出现未接受的数据包
            self.write_data_to_file(self.rcv_data.get(self.rcv_base))  # 写入文件
            del self.rcv_data[self.rcv_base]  # 清除该缓存
            self.rcv_base = self.rcv_base + 1  # 滑动窗口最左侧向前滑动+1
            print(self.hostname +':接收窗口最左侧滑动到' + str(self.rcv_base))