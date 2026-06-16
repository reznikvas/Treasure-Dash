"""
Treasure Dash

Copyright (C) 2026 Vasilii Reznik

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY.

See the GNU General Public License for more details.
"""

import random
import sys
import pygame


# Size of one tile in pixels
TILE_SIZE = 40
ENEMY_MOVE_INTERVAL_MS = 320
ENEMY_CHASE_WEIGHT = 4
ENEMY_RANDOM_WEIGHT = 1

# Game map:
# # - wall
# . - empty space
# @ - player start position
# $ - treasure
# E - enemy
GAME_MAP = [
    "############################",
    "#@......#..............$...#",
    "#..####.#.#########..####..#",
    "#.......#.....E.....#......#",
    "#.###########..####.#.####.#",
    "#.....$........#....#....#.#",
    "#.######..####.#.#########.#",
    "#..............#.....$.....#",
    "#..#######.#########..###..#",
    "#......E#.............#....#",
    "#.####..#..######..####..$.#",
    "#...............E..........#",
    "############################",
]

MAP_WIDTH = len(GAME_MAP[0])
MAP_HEIGHT = len(GAME_MAP)

SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE + 60

# Colors in RGB format
COLOR_BACKGROUND = (30, 30, 30)
COLOR_FLOOR = (55, 55, 55)
COLOR_FLOOR_DARK = (45, 45, 45)
COLOR_FLOOR_LIGHT = (65, 65, 65)
COLOR_WALL = (145, 65, 45)
COLOR_WALL_DARK = (85, 35, 28)
COLOR_WALL_LIGHT = (190, 95, 65)
COLOR_MORTAR = (60, 45, 40)
COLOR_PLAYER = (50, 200, 80)
COLOR_TREASURE = (240, 200, 40)
COLOR_ENEMY = (210, 60, 60)
COLOR_BLACK = (15, 15, 15)
COLOR_WHITE = (245, 245, 245)
COLOR_CHEST = (145, 90, 35)
COLOR_CHEST_DARK = (90, 55, 25)
COLOR_CHEST_TRIM = (210, 160, 65)
COLOR_TEXT = (240, 240, 240)
COLOR_WIN_TEXT = (255, 220, 80)
COLOR_LOSE_TEXT = (255, 120, 120)


def find_player_start():
    """
    Find the player's start position on the map.

    Return the player's tile coordinates: x, y.
    """
    for y, row in enumerate(GAME_MAP):
        for x, cell in enumerate(row):
            if cell == "@":
                return x, y

    raise ValueError("The map does not contain a player start position '@'")


def find_cells(target_cell):
    """
    Find all map cells matching the target cell.
    """
    cells = set()

    for y, row in enumerate(GAME_MAP):
        for x, cell in enumerate(row):
            if cell == target_cell:
                cells.add((x, y))

    return cells


def can_move_to(x, y):
    """
    Check whether the player can move to tile x, y.
    Walls are not passable.
    """
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return False

    return GAME_MAP[y][x] != "#"


def distance_between(first_position, second_position):
    """
    Return the Manhattan distance between two tile positions.
    """
    first_x, first_y = first_position
    second_x, second_y = second_position

    return abs(first_x - second_x) + abs(first_y - second_y)


def choose_enemy_move(possible_moves, enemy_position, player_position):
    """
    Choose an enemy move with a bias toward the player.
    """
    current_distance = distance_between(enemy_position, player_position)
    weights = []

    for move in possible_moves:
        next_distance = distance_between(move, player_position)
        weight = ENEMY_RANDOM_WEIGHT

        if next_distance < current_distance:
            weight += ENEMY_CHASE_WEIGHT
        elif next_distance == current_distance:
            weight += 1

        weights.append(weight)

    return random.choices(possible_moves, weights=weights, k=1)[0]


def move_enemies(enemies, player_position):
    """
    Move each enemy with a random bias toward the player.
    """
    moved_enemies = set()
    occupied_positions = set(enemies)

    for enemy_x, enemy_y in sorted(enemies):
        occupied_positions.remove((enemy_x, enemy_y))
        possible_moves = [(enemy_x, enemy_y)]

        for next_x, next_y in (
            (enemy_x, enemy_y - 1),
            (enemy_x, enemy_y + 1),
            (enemy_x - 1, enemy_y),
            (enemy_x + 1, enemy_y),
        ):
            if (
                can_move_to(next_x, next_y)
                and (next_x, next_y) not in occupied_positions
            ):
                possible_moves.append((next_x, next_y))

        enemy_position = (enemy_x, enemy_y)
        next_position = choose_enemy_move(
            possible_moves,
            enemy_position,
            player_position,
        )
        moved_enemies.add(next_position)
        occupied_positions.add(next_position)

    return moved_enemies


def tile_rect(tile_x, tile_y, margin=0):
    """
    Return a pygame rectangle for a tile with an optional inset margin.
    """
    return pygame.Rect(
        tile_x * TILE_SIZE + margin,
        tile_y * TILE_SIZE + margin,
        TILE_SIZE - margin * 2,
        TILE_SIZE - margin * 2,
    )


def draw_floor(screen, tile_x, tile_y):
    """
    Draw a floor tile with subtle stone shading.
    """
    rect = tile_rect(tile_x, tile_y)
    inner_rect = tile_rect(tile_x, tile_y, 4)

    pygame.draw.rect(screen, COLOR_FLOOR_DARK, rect)
    pygame.draw.rect(screen, COLOR_FLOOR, inner_rect)
    pygame.draw.line(
        screen,
        COLOR_FLOOR_LIGHT,
        inner_rect.topleft,
        inner_rect.topright,
        1,
    )


def draw_wall(screen, tile_x, tile_y):
    """
    Draw a wall tile as a small brick block.
    """
    rect = tile_rect(tile_x, tile_y)

    pygame.draw.rect(screen, COLOR_MORTAR, rect)
    pygame.draw.rect(screen, COLOR_WALL, tile_rect(tile_x, tile_y, 2))

    left = tile_x * TILE_SIZE
    top = tile_y * TILE_SIZE

    pygame.draw.line(
        screen,
        COLOR_WALL_LIGHT,
        (left + 3, top + 3),
        (left + TILE_SIZE - 4, top + 3),
        2,
    )
    pygame.draw.line(
        screen,
        COLOR_WALL_DARK,
        (left + 3, top + TILE_SIZE - 4),
        (left + TILE_SIZE - 4, top + TILE_SIZE - 4),
        2,
    )

    pygame.draw.line(
        screen,
        COLOR_MORTAR,
        (left, top + 13),
        (left + TILE_SIZE, top + 13),
        2,
    )
    pygame.draw.line(
        screen,
        COLOR_MORTAR,
        (left, top + 27),
        (left + TILE_SIZE, top + 27),
        2,
    )
    pygame.draw.line(screen, COLOR_MORTAR, (left + 20, top), (left + 20, top + 13), 2)
    pygame.draw.line(
        screen,
        COLOR_MORTAR,
        (left + 10, top + 13),
        (left + 10, top + 27),
        2,
    )
    pygame.draw.line(
        screen,
        COLOR_MORTAR,
        (left + 30, top + 13),
        (left + 30, top + 27),
        2,
    )
    pygame.draw.line(
        screen,
        COLOR_MORTAR,
        (left + 20, top + 27),
        (left + 20, top + 40),
        2,
    )


def draw_player(screen, tile_x, tile_y):
    """
    Draw the player as a small green character.
    """
    center_x = tile_x * TILE_SIZE + TILE_SIZE // 2
    top_y = tile_y * TILE_SIZE

    head_center = (center_x, top_y + 13)
    body_rect = pygame.Rect(center_x - 10, top_y + 19, 20, 15)

    pygame.draw.circle(screen, COLOR_PLAYER, head_center, 10)
    pygame.draw.rect(screen, COLOR_PLAYER, body_rect, border_radius=5)

    pygame.draw.circle(screen, COLOR_WHITE, (center_x - 4, top_y + 11), 2)
    pygame.draw.circle(screen, COLOR_WHITE, (center_x + 4, top_y + 11), 2)
    pygame.draw.line(
        screen,
        COLOR_PLAYER,
        (center_x - 10, top_y + 24),
        (center_x - 16, top_y + 31),
        4,
    )
    pygame.draw.line(
        screen,
        COLOR_PLAYER,
        (center_x + 10, top_y + 24),
        (center_x + 16, top_y + 31),
        4,
    )
    pygame.draw.line(
        screen,
        COLOR_PLAYER,
        (center_x - 5, top_y + 33),
        (center_x - 10, top_y + 38),
        4,
    )
    pygame.draw.line(
        screen,
        COLOR_PLAYER,
        (center_x + 5, top_y + 33),
        (center_x + 10, top_y + 38),
        4,
    )


def draw_enemy(screen, tile_x, tile_y):
    """
    Draw an enemy as a small red monster.
    """
    body = tile_rect(tile_x, tile_y, 6)
    center_x = tile_x * TILE_SIZE + TILE_SIZE // 2
    top_y = tile_y * TILE_SIZE

    pygame.draw.rect(screen, COLOR_ENEMY, body, border_radius=8)
    pygame.draw.circle(screen, COLOR_ENEMY, (center_x - 9, top_y + 9), 5)
    pygame.draw.circle(screen, COLOR_ENEMY, (center_x + 9, top_y + 9), 5)

    pygame.draw.circle(screen, COLOR_WHITE, (center_x - 6, top_y + 18), 4)
    pygame.draw.circle(screen, COLOR_WHITE, (center_x + 6, top_y + 18), 4)
    pygame.draw.circle(screen, COLOR_BLACK, (center_x - 6, top_y + 18), 2)
    pygame.draw.circle(screen, COLOR_BLACK, (center_x + 6, top_y + 18), 2)

    mouth_y = top_y + 28
    pygame.draw.rect(
        screen,
        COLOR_BLACK,
        (center_x - 11, mouth_y, 22, 5),
        border_radius=2,
    )

    for tooth_x in (center_x - 7, center_x, center_x + 7):
        pygame.draw.polygon(
            screen,
            COLOR_WHITE,
            [
                (tooth_x - 3, mouth_y),
                (tooth_x + 3, mouth_y),
                (tooth_x, mouth_y + 5),
            ],
        )


def draw_treasure(screen, tile_x, tile_y):
    """
    Draw treasure as a small chest with a golden lid and lock.
    """
    left = tile_x * TILE_SIZE
    top = tile_y * TILE_SIZE

    lid_rect = pygame.Rect(left + 7, top + 10, 26, 11)
    body_rect = pygame.Rect(left + 6, top + 19, 28, 15)
    lock_rect = pygame.Rect(left + 17, top + 21, 6, 8)

    pygame.draw.rect(screen, COLOR_CHEST_TRIM, lid_rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_CHEST, body_rect, border_radius=3)
    pygame.draw.line(
        screen,
        COLOR_CHEST_DARK,
        (left + 6, top + 20),
        (left + 34, top + 20),
        2,
    )
    pygame.draw.line(
        screen,
        COLOR_CHEST_DARK,
        (left + 13, top + 20),
        (left + 13, top + 34),
        2,
    )
    pygame.draw.line(
        screen,
        COLOR_CHEST_DARK,
        (left + 27, top + 20),
        (left + 27, top + 34),
        2,
    )
    pygame.draw.rect(screen, COLOR_TREASURE, lock_rect, border_radius=2)
    pygame.draw.rect(screen, COLOR_CHEST_DARK, body_rect, 2, border_radius=3)


def draw_game(
    screen,
    font,
    player_x,
    player_y,
    enemies,
    treasures,
    total_treasures,
    game_state,
):
    """
    Draw the full game scene in the window.
    """
    screen.fill(COLOR_BACKGROUND)

    for y, row in enumerate(GAME_MAP):
        for x, cell in enumerate(row):
            rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            )

            if cell == "#":
                draw_wall(screen, x, y)
            else:
                draw_floor(screen, x, y)

            # Draw the grid around tiles
            pygame.draw.rect(screen, COLOR_BACKGROUND, rect, 1)

            if (x, y) in treasures:
                draw_treasure(screen, x, y)

            if (x, y) in enemies:
                draw_enemy(screen, x, y)

    draw_player(screen, player_x, player_y)

    # Text at the bottom
    collected_treasures = total_treasures - len(treasures)

    if game_state == "won":
        text = font.render(
            "Victory! You collected every treasure. Press ESC to exit.",
            True,
            COLOR_WIN_TEXT,
        )
    elif game_state == "lost":
        text = font.render(
            "Game over! You hit an enemy. Press ESC to exit.",
            True,
            COLOR_LOSE_TEXT,
        )
    else:
        text = font.render(
            (
                f"Treasures: {collected_treasures}/{total_treasures}   "
                "Controls: WASD or arrows. ESC - exit."
            ),
            True,
            COLOR_TEXT,
        )

    screen.blit(text, (20, MAP_HEIGHT * TILE_SIZE + 20))


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Treasure Dash")

    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    player_x, player_y = find_player_start()
    enemies = find_cells("E")
    treasures = find_cells("$")
    total_treasures = len(treasures)
    game_state = "playing"
    last_enemy_move_time = pygame.time.get_ticks()

    running = True

    while running:
        # Limit the game to 60 frames per second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    continue

                if game_state != "playing":
                    continue

                new_x = player_x
                new_y = player_y

                if event.key in (pygame.K_w, pygame.K_UP):
                    new_y -= 1
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    new_y += 1
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    new_x -= 1
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    new_x += 1

                if can_move_to(new_x, new_y):
                    player_x = new_x
                    player_y = new_y

                player_position = (player_x, player_y)

                if player_position in enemies:
                    game_state = "lost"
                elif player_position in treasures:
                    treasures.remove(player_position)

                    if not treasures:
                        game_state = "won"

        current_time = pygame.time.get_ticks()

        if (
            game_state == "playing"
            and current_time - last_enemy_move_time >= ENEMY_MOVE_INTERVAL_MS
        ):
            enemies = move_enemies(enemies, (player_x, player_y))
            last_enemy_move_time = current_time

            if (player_x, player_y) in enemies:
                game_state = "lost"

        draw_game(
            screen,
            font,
            player_x,
            player_y,
            enemies,
            treasures,
            total_treasures,
            game_state,
        )

        # Update the image in the window
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
