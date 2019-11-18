class Buffer:
    def __init__(self, size = 10):
        self.size = size
        self.v = [i for i in range(size)]


if __name__ == "__main__":
    buffer = Buffer()
    print(buffer.v)
