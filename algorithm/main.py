import threading
import os
import random
import matplotlib.pyplot as plt
from time import sleep
from math import fabs


class Queue:
    def __init__(self, size=10):
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
        print("[", end = '')
        for i in range(self.size_queue):
            if i == self.size_queue-1:
                print("%d" % self.v[(self.begin_queue + i) % self.size], end='')
            else:
                print("%d, " % self.v[(self.begin_queue + i) % self.size], end='')
        print("]")


class Buffer:
    def __init__(self, buffer_size=int(100), transfer_time=50e-3, codel=False):
        self.buffer = Queue(size=buffer_size)
        self.current_packet = 0
        self.buffer_lock = threading.Lock()
        self.transfer_time = transfer_time  # in seconds. This is the sleep time
        self.buffer_size = buffer_size
        self.running = True
        self.error_ammout = 0.02  # 2 percent error
        self.average_times = []
        self.tracking_time = 0.01
        self.codel = codel
        self.last_delay_time = 0
        self.last_delay_time_before_bufferbloat = 0
        self.TARGET = self.buffer_size * self.transfer_time / 10
        self.DROP_STATE = False
        self.INTERVAL = 100 * self.transfer_time

        self.adding_packets_thread = threading.Thread(target=self.keep_adding_packet_to_buffer)
        self.adding_packets_thread.start()
        if not codel:
            self.removing_packets_thread = threading.Thread(target=self.remove_packet_from_buffer)
            self.removing_packets_thread.start()
        else:
            self.removing_packets_thread = threading.Thread(target=self.remove_packet_from_buffer_with_codel)
            self.removing_packets_thread.start()
        self.keep_track_of_times_thread = threading.Thread(target=self.keep_track_of_averages_times)
        self.keep_track_of_times_thread.start()

    def end(self):
        self.running = False
        self.adding_packets_thread.join()
        self.removing_packets_thread.join()
        self.keep_track_of_times_thread.join()

    def add_packet_to_buffer(self, packet=None):
        if not self.buffer.is_full():
            if packet is None:
                self.buffer.push(self.current_packet)
                # print("Packet = %d was added to buffer" % self.current_packet)
                self.current_packet += 1
            else:
                self.buffer.push(packet)

    def generate_random_transfer_time(self):
        return self.transfer_time + self.transfer_time * self.error_ammout * random.uniform(-0.5, 0.5)

    def keep_adding_packet_to_buffer(self):
        while self.running:
            if not self.buffer.is_full():
                sleep(self.generate_random_transfer_time())
                self.add_packet_to_buffer()

    def remove_packet_from_buffer(self):
        while self.running:
            if not self.buffer.is_empty():
                sleep(self.generate_random_transfer_time())
                self.buffer.pop()

    def remove_packet_from_buffer_with_codel(self):
        time = 0
        while self.running:
            if not self.buffer.is_empty():
                time += self.generate_random_transfer_time()

                current_delay_time = self.calculate_average_time()

                if self.DROP_STATE and fabs(current_delay_time - self.last_delay_time_before_bufferbloat) < self.TARGET:
                    print("Saiu no DROP STATE")
                    self.DROP_STATE = False

                if current_delay_time - self.last_delay_time > self.TARGET:
                    print("Entrou no DROP STATE")
                    self.DROP_STATE = True
                    print("last_delay_time_before_bufferbloat", self.last_delay_time_before_bufferbloat)
                    self.last_delay_time_before_bufferbloat = self.last_delay_time

                if self.DROP_STATE:
                    if time > self.INTERVAL:
                        time = 0
                        self.buffer.pop()
                        self.INTERVAL *= 1 + 2.7 / self.buffer_size
                else:
                    sleep(self.generate_random_transfer_time())
                    self.buffer.pop()

                self.last_delay_time = current_delay_time

    def calculate_average_time(self):
        total_time = 0
        size = self.buffer.size_queue
        for _ in range(size):
            total_time += self.generate_random_transfer_time()

        return total_time

    def print_buffer_info(self, name):
        print(name + ":")
        print("Buffer size = ", self.buffer.size_queue)
        print("Average time for a packet to deliver = %.3fs" % self.calculate_average_time())
        
        print("")

    def keep_printing_buffer_info(self):
        while self.running:
            sleep(1)
            self.print_buffer_info()

    def print_queue(self):
        print("Buffer = ", end='')
        self.buffer.print()

    def keep_track_of_averages_times(self):
        while self.running:
            sleep(self.tracking_time)
            self.average_times.append(self.calculate_average_time())


def print_keyboard_commands_info():
    print("Press p to print info about the buffer")
    print("Press b to simulate a buffer bloat")
    print("Press e or q to exit")
    print("")


def plot_average_times(buffer, name=None):
    average_times = buffer.average_times

    xs = []
    ys = []
    for i in range(len(average_times)):
        xs.append((i+1) * buffer.tracking_time)
        ys.append(average_times[i])

    plt.plot(xs, ys)
    plt.suptitle('Total delay in buffer with ' + name)
    plt.xlabel('Time (s)')
    plt.ylabel('Average time for a packet to be delivered (s)')
    plt.show()


if __name__ == "__main__":
    normal_buffer = Buffer()
    codel_buffer = Buffer(codel=True)

    os.system("clear")
    print_keyboard_commands_info()
    print("")
    print("")
    print("")

    while True:
        command = input("Command: ")
        if command == 'e' or command == 'E' or command == 'q' or command == "Q":
            normal_buffer.end()
            codel_buffer.end()
            break
    
        os.system("clear")
        print_keyboard_commands_info()

        if command == "p" or command == "P":
            normal_buffer.print_buffer_info("no bufferbloat algorithm")
            codel_buffer.print_buffer_info("CoDel")
        elif command == "b" or command == "B":
            for i in range(normal_buffer.buffer_size):
                normal_buffer.add_packet_to_buffer(5)
                codel_buffer.add_packet_to_buffer(5)
            print("Bufferbloat!")
            print("")
            print("")
        else:
            print("")
            print("")
            print("")

    plot_average_times(normal_buffer, "no bufferbloat algorithm")
    plot_average_times(codel_buffer, "CoDel")
