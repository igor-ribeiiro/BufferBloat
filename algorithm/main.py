import threading
from time import sleep


class Buffer:
    def __init__(self, size = 10):
        self.size = size
        self.v = [-1 for i in range(size)]
        self.begin_queue = 0
        self.size_queue = 0
    
    def push(self, value):
        if self.is_full():
            print("Queue is FULL in push operation, not doing it")
            return
        self.v[(self.begin_queue + self.size_queue) % self.size] = value
        self.size_queue += 1

    def top(self):
        return self.v[self.begin_queue]

    def pop(self):
        if self.is_empty():
            print("Queue is EMPTY in pop operation, not doing it")
            return -1
        self.size_queue -= 1
        value = self.v[self.begin_queue]
        self.v[self.begin_queue] = -1
        self.begin_queue = (self.begin_queue + 1) % self.size
        return value

    def is_full(self):
        return self.size_queue == self.size

    def is_empty(self):
        return self.size_queue == 0

    def print(self):
        for i in range(self.size_queue):
            print("%d " % self.v[(self.begin_queue + i) % self.size], end = '')
        print("")


class PacketFlow:
    def __init__(self, buffer_size = int(10), sleep_time = 5e-3):
        self.buffer = Buffer(size=buffer_size)
        self.current_packet = 0
        self.buffer_lock = threading.Lock()
        self.transfer_time = sleep_time  # in seconds. This is the sleep time

    def add_packet_to_buffer(self):
        while(True):
            if not self.buffer.is_full():
                sleep(self.transfer_time)
                self.buffer.push(self.current_packet)
                # print("Packet = %d was added to buffer" % self.current_packet)
                self.current_packet += 1
            else:
                pass
                # print("Buffer is full, not adding packet = %d" % self.current_packet)

    def remove_packet_from_buffer(self):
        while True:
            if not self.buffer.is_empty():
                sleep(self.transfer_time*2)
                self.buffer.pop()
                # packet = self.buffer.pop()
                # print("Packet = %d was removed from buffer" % packet)
            else:
                pass
                # print("Buffer is empty, not removing packet")

    def print_buffer_info(self):
        while True:
            sleep(1)
            print("Queue size = ", self.buffer.size_queue)

    def print_queue(self):
        self.buffer.print()


if __name__ == "__main__":
    packet_flow = PacketFlow()

    adding_packets_thread = threading.Thread(target=packet_flow.add_packet_to_buffer)
    adding_packets_thread.start()

    removing_packets_thread = threading.Thread(target=packet_flow.remove_packet_from_buffer)
    removing_packets_thread.start()

    printing_buffer_thread = threading.Thread(target=packet_flow.print_buffer_info)
    printing_buffer_thread.start()



    adding_packets_thread.join()
    removing_packets_thread.join()
    printing_buffer_thread.join()
