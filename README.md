# HIT-Computer_Network-Lab2
基 于 UDP 设计并实现对于停等协议，GBN，SR协议的过程与技术。 

# 说明

## 程序内容

- 基于 UDP 设计一个简单的停等协议，实现单向可靠数据传输（服
- 务器到客户的数据传输）。 
- 模拟引入数据包的丢失，验证所设计协议的有效性。
-  改进所设计的停等协议，支持双向数据传输；
- 基于所设计的停等协议，实现一个 C/S 结构的文件传输应用。
- 基于 UDP 设计一个简单的 GBN 协议，实现单向可靠数据传输
- 模拟引入数据包的丢失，验证所设计协议的有效性。
- 改进所设计的 GBN 协议，支持双向数据传输；
- 将所设计的 GBN 协议改进为 SR 协议。

# 程序演示

 **展示结果方式:**  

 展示控制日志：通过日志打印的发送端与接收端打印显示的序号信息可以判   断实验代码运行结果的正确性；  

 验证接收到的文件：通过接收到的数据存入的文本文件与源文件对比可以得   知实验代码运行结果的正确性。  

Client主机中的文件:  作为发送方，读取的文件路径read_file2.txt  作为接受方，保存的文件路径save_file.txt  

Server主机中的文件:  作为发送方，读取的文件路径read_file.txt  作为接受方，保存的文件路径save_file2.txt     

**1.** **单向 GBN 的实验结果** 

  启动程序前，只有server有read文件

  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153229.jpg)![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153238.jpg)  

启动程序后控制台日志：  发送方成功完成发送pkt，接收方成功完成接收ack  期间有模拟丢失pkt和ack，以及超时重传  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153240.jpg)  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153249.jpg)  

启动程序之后文件数据变化：  Client产生save_file  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153259.jpg)  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153264.jpg)           

**2.** **双向GBN的实验结果**  

启动程序前，只有server，client有read文件  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153041.jpg)  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153126.jpg)     

启动程序后控制台日志：  发送方成功完成发送pkt，接收方成功完成接收ack  期间有模拟丢失pkt和ack，以及超时重传  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153509.jpg)    

 启动程序之后文件数据变化：  Client产生save_file  Server产生save_file2  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153530.jpg)  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153613.jpg)  

**3.** **单向停等协议实验结果**  启动程序前，只有server有read文件  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153679.jpg)  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153993.jpg)  

启动程序后控制台日志：  发送方成功完成发送pkt，接收方成功完成接收ack  期间有模拟丢失pkt和ack，以及超时重传  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153197.jpg)  

启动程序之后文件数据变化：  Client产生save_file  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153370.jpg) 

 **4.** **双向停等协议实验结果**  启动程序前，只有server，client有read文件  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image014.jpg)  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image016.jpg)  

启动程序后控制台日志：  发送方成功完成发送pkt，接收方成功完成接收ack  期间有模拟丢失pkt和ack，以及超时重传  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153656.jpg)  

启动程序之后文件数据变化：  Client产生save_file  Server产生save_file2  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image020.jpg)  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image022.jpg)     

**5.** **单向SR实验结果**  启动程序前，只有server有read文件  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image002.jpg)![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image004.jpg)  

启动程序后控制台日志：  发送方成功完成发送pkt，接收方成功完成接收ack  期间有模拟丢失pkt和ack，以及超时重传     ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153840.jpg)  

启动程序之后文件数据变化：  Client产生save_file  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image010.jpg) 

 **6.** **双向SR实验结果**  启动程序前，只有server，client有read文件  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image014.jpg)  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image016.jpg)     

启动程序后控制台日志：  发送方成功完成发送pkt，接收方成功完成接收ack  期间有模拟丢失pkt和ack，以及超时重传  ![img](https://farsblog.oss-cn-beijing.aliyuncs.com/PicGo/202305152153995.jpg)     

启动程序之后文件数据变化：  Client产生save_file  Server产生save_file2  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image020.jpg)  ![img](file:///C:/Users/86189/AppData/Local/Temp/msohtmlclip1/01/clip_image022.jpg)     

# 问题讨论：

**Q1****：如何实现全双工状态下的同时接收数据**

A1：利用同一个端口和socket同时接收ack和pkt，就需要构造合适的数据结构来区分ack和pkt，因此在单向传输的基础上我尝试加入了flag来区分ack和pkt

**Q2****：丢包概率控制问题怎么具体实现**

A2：利用好random（）产生一个[0,1]的数，然后我给定默认loss=0.1丢包率，然后就可以利 用random()
