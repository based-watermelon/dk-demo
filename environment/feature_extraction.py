import pygame


#initial variables
GRID_SIZE = 7
CELL_SIZE = 40
ENV_GRID = 20


def vision_grid(CELL_SIZE, GRID_SIZE, mario, screen, all_barrels, ladders):
    grid_left = mario.rect.centerx - 3.5 * CELL_SIZE
    grid_top = mario.rect.bottom - 5 * CELL_SIZE

    barrel_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for barrel in all_barrels:
        rel_x = barrel.rect.centerx - grid_left
        rel_y = barrel.rect.centery - grid_top
        col = int(rel_x // CELL_SIZE)
        row = int(rel_y // CELL_SIZE)
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            barrel_grid[row][col] = 1

    ladder_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for ladder in ladders:
        rel_x = ladder.centerx - grid_left
        rel_yc = ladder.centery - grid_top
        col = int(rel_x // CELL_SIZE)
        rowc = int(rel_yc // CELL_SIZE)
        for row in (rowc - 1, rowc, rowc + 1):
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                ladder_grid[row][col] = 1

    return barrel_grid, ladder_grid


def agent_grid(CELL_SIZE, ENV_GRID, mario, screen):
    grid = [[0 for _ in range(ENV_GRID)] for _ in range(ENV_GRID)]
    rel_x = mario.rect.centerx
    rel_y = mario.rect.centery
    col = int(rel_x // CELL_SIZE)
    row = int(rel_y // CELL_SIZE)
    if 0 <= row < ENV_GRID and 0 <= col < ENV_GRID:
        grid[row][col] = 1
    return grid
    
def get_state(mario, all_barrels, ladders, screen, CELL_SIZE, GRID_SIZE, ENV_GRID):
    barrel_grid , ladder_grid = vision_grid(CELL_SIZE,GRID_SIZE,mario,screen,all_barrels,ladders)
    mario_grid = agent_grid(CELL_SIZE,ENV_GRID,mario,screen)

    state = []
    state.extend(flatten(barrel_grid))
    state.extend(flatten(ladder_grid))
    state.extend(flatten(mario_grid))

    return state


def get_princess_features(mario, princess_rect, screen_width, screen_height):
    mario_x = mario.rect.centerx
    mario_y = mario.rect.centery

    princess_x = princess_rect.centerx
    princess_y = princess_rect.centery

    dx = (princess_x - mario_x) / screen_width
    dy = (princess_y - mario_y) / screen_height

    return [dx, dy]

def flatten(grid):
    data = []

    for row in grid:
        data.extend(row)

    return data


