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

if __name__ == "__main__":
    buffer = Buffer()
    print(buffer.v)

    for i in range(11):
        buffer.push(i)
        print(buffer.v)

    for i in range(5):
        print(buffer.pop())
        print(buffer.v)
    
    for i in range(10, 16):
        buffer.push(i)
        print(buffer.v)
    