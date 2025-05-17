import heapq

def dijkstra(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    heap = []

    # (total_cost, current_node, path_so_far)
    heapq.heappush(heap, (0, start, [start])) 
    visited = set()
    cost_so_far = {start: 0}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while heap:
        cost, (x, y), path = heapq.heappop(heap)

        if (x, y) == end:
            return path

        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if 0 <= nx < rows and 0 <= ny < cols:
                new_cost = cost + grid[nx][ny]
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))

    return None

if __name__ == '__main__':
    grid = [
        [0,0,0,0,9],
        [0,0,0,9,9],
        [0,1,1,9,0],
        [0,0,0,9,0]
    ]
    start = (0,0)
    end = (3,4)
    pts = dijkstra(grid, start, end)
    for r in grid:
        for c in r:
            print(c,end='')
        print()
    print('-----------')
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            if (r,c) in pts:
                print('x',end='')
            else:
                print(col,end='')
        print()