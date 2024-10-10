import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Backgammon')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
BEIGE = (245, 245, 220)
RED = (220, 20, 60)
GREEN = (34, 139, 34)

# Global variables
selected_checker = None
moves_left = []
current_player = 'W'
points = []
bar = {'W': [], 'B': []}
borne_off = {'W': [], 'B': []}

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
BEIGE = (245, 245, 220)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)

# Function definitions...

def init_checkers():
    global points, bar, borne_off
    points = [[] for _ in range(24)]
    bar = {'W': [], 'B': []}
    borne_off = {'W': [], 'B': []}

    # Standard Backgammon setup
    # For Player 'W' (White)
    points[23] = ['W'] * 2       # Point 24
    points[12] = ['W'] * 5       # Point 13
    points[7] = ['W'] * 3        # Point 8
    points[5] = ['W'] * 5        # Point 6

    # For Player 'B' (Black)
    points[0] = ['B'] * 2        # Point 1
    points[11] = ['B'] * 5       # Point 12
    points[16] = ['B'] * 3       # Point 17
    points[18] = ['B'] * 5       # Point 19

def roll_dice():
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    if die1 == die2:
        return [die1] * 4
    else:
        return [die1, die2]

def draw_board(available_moves=None):
    if available_moves is None:
        available_moves = []
    point_width = (700 - 20) / 12
    offset_x = 60
    font = pygame.font.SysFont(None, 24)

    # Draw the board background
    pygame.draw.rect(WINDOW, BROWN, (50, 50, 700, 500))

    # Draw the dividing bar (the bar)
    pygame.draw.rect(WINDOW, BLACK, (395, 50, 10, 500))

    # Draw triangles (points)
    triangle_colors = [WHITE, BLACK]
    for i in range(12):
        color = triangle_colors[i % 2]

        # Top triangles
        points_top = [
            (offset_x + i * point_width, 50),
            (offset_x + (i + 1) * point_width, 50),
            (offset_x + i * point_width + point_width / 2, 250)
        ]
        pygame.draw.polygon(WINDOW, color, points_top)

        # Bottom triangles
        points_bottom = [
            (offset_x + i * point_width, 550),
            (offset_x + (i + 1) * point_width, 550),
            (offset_x + i * point_width + point_width / 2, 350)
        ]
        pygame.draw.polygon(WINDOW, color, points_bottom)

    # Highlight available moves
    for end in available_moves:
        if end == 'bear_off':
            # Handle bearing off highlight (optional)
            continue
        if end < 0 or end >= 24:
            continue
        if end < 12:
            # Bottom points
            col = 11 - end
            x = offset_x + col * point_width + point_width / 2
            y = HEIGHT - 50 - 20  # Slightly above the point
        else:
            # Top points
            col = end - 12
            x = offset_x + col * point_width + point_width / 2
            y = 50 + 20  # Slightly below the point
        # Draw a circle to highlight
        pygame.draw.circle(WINDOW, GREEN, (int(x), int(y)), 15, 3)

    # Optionally, add point numbers for debugging
    for i in range(24):
        if i < 12:
            col = 11 - i
            x = offset_x + col * point_width + point_width / 2
            y = HEIGHT - 30
        else:
            col = i - 12
            x = offset_x + col * point_width + point_width / 2
            y = 30
        point_number = str(i + 1)
        img = font.render(point_number, True, RED)
        WINDOW.blit(img, (x - 10, y))
        

def draw_checkers(points):
    global selected_checker
    checker_radius = 20
    point_width = (700 - 20) / 12
    offset_x = 60
    mid_y = HEIGHT // 2

    for i in range(24):
        if i < 12:
            # Bottom points (1 to 12)
            col = 11 - i
            x = offset_x + col * point_width + point_width / 2
            y_start = HEIGHT - 50 - checker_radius
            direction = -1
        else:
            # Top points (13 to 24)
            col = i - 12
            x = offset_x + col * point_width + point_width / 2
            y_start = 50 + checker_radius
            direction = 1

        for j, checker in enumerate(points[i]):
            y = y_start + direction * (checker_radius * 2 + 5) * j
            color = WHITE if checker == 'W' else BLACK

            # Highlight the selected checker
            if selected_checker == i and j == len(points[i]) - 1:
                # Draw a yellow checker to indicate selection
                pygame.draw.circle(WINDOW, YELLOW, (int(x), int(y)), checker_radius)
            else:
                pygame.draw.circle(WINDOW, color, (int(x), int(y)), checker_radius)

            pygame.draw.circle(WINDOW, RED, (int(x), int(y)), checker_radius, 2)  # Outline

def get_point_from_pos(pos):
    x, y = pos
    point_width = (700 - 20) / 12
    offset_x = 60

    if offset_x <= x <= 740:
        col = int((x - offset_x) // point_width)
        if y < 300:
            point = col + 12  # Top points are indices 12 to 23
        else:
            point = 11 - col  # Bottom points are indices 11 to 0
        return point
    # Check for bar clicks
    if 395 <= x <= 405:
        return 'bar'
    return None

def is_legal_move(player, start, end, points, bar):
    global moves_left

    if start is None or end is None:
        return False

    # Determine the direction
    direction = -1 if player == 'W' else 1
    move_distance = (end - start) * direction

    if bar[player]:
        if start != 'bar':
            return False  # Must enter from the bar first
        # Entry point for bar checkers
        entry_point = end
        if player == 'W':
            entry_point = 24 - move_distance
        else:
            entry_point = move_distance - 1
        if not (0 <= entry_point < 24):
            return False
        destination = points[entry_point]
        if destination and destination[-1] != player and len(destination) >= 2:
            return False  # Entry point is blocked
        return move_distance in moves_left

    # Check for bearing off
    if (player == 'W' and end < 0) or (player == 'B' and end >= 24):
        if not can_bear_off(player, points):
            return False
        # Additional rules for bearing off can be implemented here
        return move_distance in moves_left

    if move_distance <= 0:
        return False  # Can't move backward

    if move_distance not in moves_left:
        return False  # Move not matching dice roll

    # Check if the destination point is blocked
    destination = points[end]
    if destination and destination[-1] != player and len(destination) >= 2:
        return False  # Point is blocked

    return True

def can_bear_off(player, points):
    home_board = range(18, 24) if player == 'W' else range(0, 6)
    for i in range(24):
        if i not in home_board and points[i]:
            for checker in points[i]:
                if checker == player:
                    return False
    return True

def get_available_moves(player, selected_checker, points, bar, moves_left):
    available_moves = []
    if selected_checker is None:
        return available_moves

    # Check for checkers on the bar
    if bar[player]:
        if selected_checker != 'bar':
            return available_moves  # Can only move checkers from the bar
        possible_ends = []
        for move in moves_left:
            if player == 'W':
                end = 24 - move
            else:
                end = move - 1
            possible_ends.append(end)
    else:
        possible_ends = []
        for move in moves_left:
            direction = -1 if player == 'W' else 1
            end = selected_checker + direction * move
            if 0 <= end < 24:
                possible_ends.append(end)
            else:
                # Check for bearing off
                if can_bear_off(player, points):
                    available_moves.append('bear_off')

    # Filter possible ends based on legality
    for end in possible_ends:
        if is_legal_move(player, selected_checker, end, points, bar):
            available_moves.append(end)

    return available_moves

def main():
    global selected_checker, moves_left, current_player, dice, points, bar
    clock = pygame.time.Clock()
    run = True

    # Initialize game state
    init_checkers()
    current_player = 'W'
    dice = roll_dice()
    moves_left = dice[:]
    selected_checker = None

    # Initialize font
    font = pygame.font.SysFont(None, 36)

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                point = get_point_from_pos(pos)
                if point is not None:
                    if selected_checker is None:
                        # Select a checker
                        if point == 'bar':
                            if bar[current_player]:
                                selected_checker = 'bar'
                        elif points[point] and points[point][-1] == current_player:
                            selected_checker = point
                    else:
                        # Deselect the checker if clicking on it again
                        if selected_checker == point:
                            selected_checker = None
                        else:
                            # Attempt to move the selected checker
                            if is_legal_move(current_player, selected_checker, point, points, bar):
                                # Move the checker
                                if selected_checker == 'bar':
                                    checker = bar[current_player].pop()
                                else:
                                    checker = points[selected_checker].pop()

                                # Hitting a blot
                                if points[point] and points[point][-1] != current_player:
                                    hit_checker = points[point].pop()
                                    bar[hit_checker].append(hit_checker)

                                points[point].append(checker)
                                move_distance = abs(point - selected_checker)
                                moves_left.remove(move_distance)
                                selected_checker = None

                                if not moves_left:
                                    # Switch player turn
                                    current_player = 'B' if current_player == 'W' else 'W'
                                    dice = roll_dice()
                                    moves_left = dice[:]
                            else:
                                # If move is illegal, keep the checker selected
                                pass

        WINDOW.fill(BEIGE)

        # Calculate available moves
        available_moves = get_available_moves(current_player, selected_checker, points, bar, moves_left)

        draw_board(available_moves)
        draw_checkers(points)

        # Display current player's turn
        player_color_text = "Current Player: White" if current_player == 'W' else "Current Player: Black"
        text_color = WHITE if current_player == 'W' else BLACK
        text_surface = font.render(player_color_text, True, text_color)
        WINDOW.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT - 40))

        # Display dice rolls
        dice_text = f"Dice Roll: {', '.join(map(str, moves_left))}"
        dice_surface = font.render(dice_text, True, RED)
        WINDOW.blit(dice_surface, (WIDTH // 2 - dice_surface.get_width() // 2, HEIGHT - 70))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()