import pygame
import csv

#initial variables
GRID_SIZE = 7
CELL_SIZE = 40
ENV_GRID = 20


def vision_grid(CELL_SIZE,GRID_SIZE,mario,screen,all_barrels,ladders):
    grid_left = mario.rect.centerx - 3.5 * CELL_SIZE
    grid_top = mario.rect.bottom - 5 * CELL_SIZE

    for i in range(GRID_SIZE + 1):
        pygame.draw.line(
            screen,
            "white",
            (grid_left + i * CELL_SIZE, grid_top),
            (grid_left + i * CELL_SIZE, grid_top + GRID_SIZE * CELL_SIZE),
        )

        pygame.draw.line(
            screen,
            "white",
            (grid_left, grid_top + i * CELL_SIZE),
            (grid_left + GRID_SIZE * CELL_SIZE, grid_top + i * CELL_SIZE),
        )

    barrel_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for barrel in all_barrels:

        rel_x = barrel.rect.centerx - grid_left
        rel_y = barrel.rect.centery - grid_top

        col = int(rel_x // CELL_SIZE)
        row = int(rel_y // CELL_SIZE)

        if 0 <= row < 7 and 0 <= col < 7:
            barrel_grid[row][col] = 1
            if barrel_grid[row][col]:
                pygame.draw.rect(
                    screen,
                    "red",
                    (
                        grid_left + col * CELL_SIZE,
                        grid_top + row * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    ),
                )
    ladder_grid = [[0 for i in range(7)] for i in range(7)]
    for ladder in ladders:
        rel_x = ladder.centerx - grid_left
        rel_yc = ladder.centery - grid_top
        rel_yt = ladder.top - grid_top
        rel_yb = ladder.bottom - grid_top

        col = int(rel_x //CELL_SIZE)
        rowc = int(rel_yc//CELL_SIZE)
        rowt = rowc - 1
        rowb = rowc + 1


        if 0<= rowc <7 and 0<= col <7:
            ladder_grid[rowc][col] = 1
            if ladder_grid[rowc][col]:
                pygame.draw.rect(
                    screen,
                    "yellow",
                    (
                        grid_left + col * CELL_SIZE,
                        grid_top +rowc * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                )
                
        if 0<= rowt <7 and 0<= col <7:
                    ladder_grid[rowt][col] = 1
                    if ladder_grid[rowt][col]:
                        pygame.draw.rect(
                            screen,
                            "yellow",
                            (
                                grid_left + col * CELL_SIZE,
                                grid_top +rowt * CELL_SIZE,
                                CELL_SIZE,
                                CELL_SIZE
                            )
                        )

        if 0<= rowb <7 and 0<= col <7:
                    ladder_grid[rowb][col] = 1
                    if ladder_grid[rowb][col]:
                        pygame.draw.rect(
                            screen,
                            "yellow",
                            (
                                grid_left + col * CELL_SIZE,
                                grid_top +rowb * CELL_SIZE,
                                CELL_SIZE,
                                CELL_SIZE
                            )
                        )
    return ladder_grid, barrel_grid

def agent_grid(CELL_SIZE,ENV_GRID,mario,screen):
    grid_left = 0
    grid_top = 0
    for i in range(ENV_GRID+1):
        pygame.draw.line(
                    screen,
                    "green",
                    (grid_left + i * CELL_SIZE, grid_top),
                    (grid_left + i * CELL_SIZE, grid_top + ENV_GRID * CELL_SIZE),
                )
        
        pygame.draw.line(
                    screen,
                    "green",
                    (grid_left, grid_top + i * CELL_SIZE),
                    (grid_left + ENV_GRID * CELL_SIZE, grid_top + i * CELL_SIZE),
                )
    grid = [[0 for _ in range(ENV_GRID)] for _ in range(ENV_GRID)]
    rel_x = mario.rect.centerx - grid_left
    rel_y = mario.rect.centery - grid_top
    
    col = int(rel_x //CELL_SIZE)
    row = int(rel_y//CELL_SIZE)
    
    
    if 0<= row <20 and 0<= col <20:
        grid[row][col] = 1
        if grid[row][col]:
            pygame.draw.rect(
                            screen,
                            "blue",
                            (
                                grid_left + col * CELL_SIZE,
                                grid_top +row * CELL_SIZE,
                                CELL_SIZE,
                                CELL_SIZE
                            )
                        )

    return grid

def get_state(mario, all_barrels, ladders, screen, CELL_SIZE, GRID_SIZE, ENV_GRID):
    barrel_grid , ladder_grid = vision_grid(CELL_SIZE,GRID_SIZE,mario,screen,all_barrels,ladders)
    mario_grid = agent_grid(CELL_SIZE,ENV_GRID,mario,screen)

    state = []
    state.extend(flatten(barrel_grid))
    state.extend(flatten(ladder_grid))
    state.extend(flatten(mario_grid))

    return state

def flatten(grid):
    data = []

    for row in grid:
        data.extend(row)

    return data

def log(state):

    reward = 0 
    dataset.append(state + [action, reward])
     
