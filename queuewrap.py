import heapq



class QueueWrap:
    def __init__(self, nodes: [(float, (int, int))] = None):
        self.queue = list() if nodes is None else list(nodes)
        self.size = len(self.queue)
        heapq.heapify(self.queue)

    def push(self, priority: float, node: (int, int)):
        self.size += 1
        heapq.heappush(self.queue, (priority, node))

    def pop(self) -> (int, int):
        self.size -= 1
        return heapq.heappop(self.queue)[1]

    def is_empty(self) -> bool:
        return self.size == 0
        # return len(self.queue) == 0
