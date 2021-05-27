class BFS(object):
    def __init__(self, adjlist, distance):
        self.adjlist = adjlist
        self.distance = distance
        self.visited = {}
        for src in adjlist:
            for dst in adjlist[src]:
                self.visited[(src, dst)] = False

    def bfs(self):
        start_node = next(iter(self.adjlist))
        path = ([], 0)
        queue = [start_node]
        while queue:
            src = queue.pop(0)
            index = 0
            for dst in self.adjlist[src]:
                index += 1
                if self.visited[(src, dst)] is False:
                    queue.append(dst)
                    path[0].append((src, dst))
                    path[1] += self.distance[src][index]
                    self.visited[(src, dst)] = True
        return path
