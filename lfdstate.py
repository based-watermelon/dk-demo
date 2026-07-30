# add isclimbing. is jumping, is onbrudge

import pygame
import math

def closest_ladder_x(mario,ladders):
    closest = ladders[0].centerx - mario.rect.centerx
    for ladder in ladders:
        dist = ladder.centerx - mario.rect.centerx
        if abs(dist) < abs(closest) :
            closest = dist
    return closest
def closest_ladder_y(mario,ladders):
    closest = ladders[0].centery - mario.rect.centery
    for ladder in ladders:
        dist = ladder.centery - mario.rect.centery
        if abs(dist) < abs(closest) :
            closest = dist
    return closest

def closest_barrel_x(mario,all_barrels):
    closest = 9999
    for barrel in all_barrels:
        dist = barrel.rect.centerx - mario.rect.centerx
        if abs(dist) < abs(closest) :
            closest = dist
    return closest

def closest_barrel_y(mario,all_barrels):
    closest = 9999
    for barrel in all_barrels:
        dist = barrel.rect.centery - mario.rect.centery
        if abs(dist) < abs(closest) :
            closest = dist
    return closest

def closest_bridge_dist(mario, bridges):
    closest_dx, closest_dy = None, None
    for bridge in bridges:
        dx = bridge.centerx - mario.rect.centerx
        dy = bridge.centery - mario.rect.centery
        if closest_dx is None or dx**2 + dy**2 < closest_dx**2 + closest_dy**2:
            closest_dx, closest_dy = dx, dy
    return closest_dx, closest_dy

def get_state(mario, all_barrels, ladders, bridges, screen):
    rel_ladder_x = closest_ladder_x(mario, ladders)
    rel_ladder_y = closest_ladder_y(mario, ladders)
    rel_barrel_x = closest_barrel_x(mario, all_barrels)
    rel_barrel_y = closest_barrel_y(mario, all_barrels)
    bridge_dx, bridge_dy = closest_bridge_dist(mario, bridges)



    current_state = {}
    current_state["mario_x"] = mario.rect.x
    current_state["mario_y"] = float(math.floor(mario.rect.y))
    current_state["bridge_dx"] = bridge_dx
    current_state["bridge_dy"] = bridge_dy
    current_state["vel_y"] = float(math.floor(mario.vel_y))
    current_state["ladder_dx"] = rel_ladder_x
    current_state["ladder_dy"] = rel_ladder_y
    current_state["barrel_dx"] = rel_barrel_x
    current_state["barrel_dy"] = rel_barrel_y

    return current_state

