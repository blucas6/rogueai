import heapq
from logger import Logger

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

def debugGrid(grid, pts):
    for row in grid:
        Logger().log(row)
    Logger().log('-------------------')
    for r,row in enumerate(grid):
        line = '['
        for c,col in enumerate(row):
            if (r,c) in pts:
                line += 'X'
            else:
                line += str(col)
            if not c == len(row)-1:
                line += ', '
        line += ']'
        Logger().log(line)
    Logger().log('==========')

MULT = [
            [1,  0,  0, -1, -1,  0,  0,  1],
            [0,  1, -1,  0,  0, -1,  1,  0],
            [0,  1,  1,  0,  0, -1, -1,  0],
            [1,  0,  0,  1, -1,  0,  0, -1]
        ]

def RecursiveShadow(grid: list, pos: list, radius: int, blockingLayer: int=1,
                    debug=False):
    '''
    Returns a list of points that are viewable from the current position
    All points are viewable, including the blockingLayer value
    '''
    pts = set()
    pts.add((pos[0],pos[1]))
    for oct in range(8):
        castLight(grid, pos[1], pos[0], 1, 1.0, 0.0, radius,
                  MULT[0][oct], MULT[1][oct], MULT[2][oct], MULT[3][oct], pts,
                  blockingLayer)
    if debug:
        debugGrid(grid, pts)
    return pts

def castLight(grid, cx, cy, row, start, end, radius, xx, xy, yx, yy, pts,
              blockingLayer):
    if start < end:
        return
    radius_squared = radius*radius
    for j in range(row, radius+1):
        dx, dy = -j-1, -j
        blocked = False
        while dx <= 0:
            dx += 1
            X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
            l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
            if not (0 <= X < len(grid[0]) and 0 <= Y < len(grid)):
                continue
            if start < r_slope:
                continue
            elif end > l_slope:
                break
            else:
                if dx*dx + dy*dy < radius_squared:
                    pts.add((Y,X))
                if blocked:
                    if notValid(grid, X, Y, blockingLayer):
                        new_start = r_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if notValid(grid, X, Y, blockingLayer) and j < radius:
                        blocked = True
                        castLight(grid, cx, cy, j+1, start, l_slope, radius,
                                  xx, xy, yx, yy, pts, blockingLayer)
                        new_start = r_slope
        if blocked:
            break

def notValid(grid, x, y, blockingLayer):
    return (x < 0 or y < 0 or x >= len(grid[0]) or y >= len(grid)
            or grid[y][x] > blockingLayer)

def testDijkstras():
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

def testRecursiveShadow():
    grid = [
        [0,0,0,0,9,0],
        [0,2,9,9,9,0],
        [0,2,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,9,9,0,0],
        [0,0,0,9,0,0]
    ]
    start = (2,2)
    pts = RecursiveShadow(grid, start, 3, 1)
    print(pts)
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            if (r,c) == start:
                print('@', end='')
            else:
                print(col,end='')
        print()
    print('-----------')
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            # if (r,c) == start:
            #     print('@', end='')
            if (r,c) in pts:
                print('x',end='')
            else:
                print(col,end='')
        print()

if __name__ == '__main__':
    testRecursiveShadow()