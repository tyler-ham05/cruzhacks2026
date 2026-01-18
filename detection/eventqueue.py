from collections import deque

class EventQueue:
    def __init__(self):
        self.q = deque()
        self.offset = 0

    def push(self, x):
        # x is the starting value
        self.q.append(x - self.offset)

    def step(self):
        self.offset -= 1
        return self.cleanup()

    def cleanup(self):
        # remove expired
        if self.q and self.q[0] + self.offset <= 0:
            self.q.popleft()
            return True
