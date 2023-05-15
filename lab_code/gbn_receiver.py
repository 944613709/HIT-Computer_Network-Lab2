import random
import select

from lab_code.main import Host


class GBN_Receiver:

    def __init__(self, receiver_socket,local_address=Host.host_address_1, remote_address=Host.host_address_2,recv_path = '../client_file/save_file.txt'):
        self.send_base = 0  # 最小的被发送的分组序号
        self.next_seq = 0  # 当前未被利用的序号
        self.time_count = 0  # 记录当前传输时间
        self.time_out = 5  # 设置超时时间
        self.local_address = local_address  # 设置本地socket地址
        self.remote_address = remote_address  # 设置远程socket地址
        self.socket = receiver_socket
        self.data_buf_size = 9182  # 作为接收端接收数据缓存
        self.exp_seq = 0  # 当前期望收到该序号的数据
        self.recv_path = recv_path  # 接收数据时，保存数据的地址
        #   先查看是否存在该要写入的文件,如果不存在则新建
        # 如果存在，将最终保存文件内容提前清空，方便之后写入新内容
        self.write_data_to_file('', mode='w')

        self.ack_loss = 0  # 返回的ack丢包率

    # 保存来自发送方的合适的数据
    def write_data_to_file(self, data, mode='a'):
        with open(self.recv_path, mode, encoding='utf-8') as f:
            f.write(data)  # 模拟将数据交付到上层

    # 主要执行函数，不断接收服务器发送的数据，若为期待序号的数据，则保存到本地，否则直接丢弃；并返回相应的ACK报文
    def recv_run(self):
        while True:
            readable = select.select([self.socket], [], [], 1)[0]  # 非阻塞接收
            if len(readable) > 0:  # 接收到数据
                rcv_data_init, client_address = self.socket.recvfrom(self.data_buf_size)
                rcv_data = rcv_data_init.decode()
                # print("data:"+rcv_data)
                rcv_seq = rcv_data.split()[0]  # 按照格式规约获取数据序号
                rcv_data = rcv_data.replace(rcv_seq + ' ', '')  # 按照格式规约获取数据
                if rcv_seq == '0' and rcv_data == '0':  # 接收到结束包
                    print('接收方:传输数据结束')
                    break
                if int(rcv_seq) == self.exp_seq:  # 接收到按序数据包
                    print('接收方:收到期望序号数据:' + str(rcv_seq))
                    self.write_data_to_file(rcv_data)  # 保存服务器端发送的数据到本地文件中
                    self.exp_seq = self.exp_seq + 1  # 期望数据的序号更新
                else:
                    print('接收方:收到非期望数据，期望:' + str(self.exp_seq) + '实际:' + str(rcv_seq))
                if random.random() >= self.ack_loss:  # 随机丢包发送ACK
                    print("发送ACK:"+str(self.exp_seq))
                    self.socket.sendto(Host.make_ack(self.exp_seq - 1, 0), self.remote_address)
                else:
                    print("发送ACK:" + str(self.exp_seq))
                    print("-------ACK："+str(self.exp_seq)+"丢失")
