import pygame
import sys
import random
import copy

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
game_state_history = []

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
            y = HEIGHT - 50 - 30  # Slightly above the point
        else:
            # Top points
            col = end - 12
            x = offset_x + col * point_width + point_width / 2
            y = 50 + 30  # Slightly below the point
        # Draw a circle to highlight
        pygame.draw.circle(WINDOW, GREEN, (int(x), int(y)), 15, 3)

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
    global selected_checker, current_player
    checker_radius = 20
    point_width = (700 - 20) / 12
    offset_x = 60
    mid_y = HEIGHT // 2

    # Draw checkers on the board
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
                pygame.draw.circle(WINDOW, YELLOW, (int(x), int(y)), checker_radius)
            else:
                pygame.draw.circle(WINDOW, color, (int(x), int(y)), checker_radius)

            pygame.draw.circle(WINDOW, RED, (int(x), int(y)), checker_radius, 2)  # Outline

    # Draw checkers on the bar
    bar_x = 400  # X-coordinate for the bar
    bar_y_w = mid_y - 30  # Y-coordinate for White's checkers on the bar
    bar_y_b = mid_y + 30  # Y-coordinate for Black's checkers on the bar

    # Draw White's checkers on the bar
    for j in range(len(bar['W'])):
        y = bar_y_w - j * (checker_radius * 2 + 5)
        pygame.draw.circle(WINDOW, WHITE, (bar_x, y), checker_radius)
        pygame.draw.circle(WINDOW, RED, (bar_x, y), checker_radius, 2)
        if selected_checker == 'bar' and current_player == 'W' and j == 0:
            # Highlight only the topmost checker
            pygame.draw.circle(WINDOW, YELLOW, (bar_x, y), checker_radius + 4, 4)

    # Draw Black's checkers on the bar
    for j in range(len(bar['B'])):
        y = bar_y_b + j * (checker_radius * 2 + 5)
        pygame.draw.circle(WINDOW, BLACK, (bar_x, y), checker_radius)
        pygame.draw.circle(WINDOW, RED, (bar_x, y), checker_radius, 2)
        if selected_checker == 'bar' and current_player == 'B' and j == 0:
            # Highlight only the topmost checker
            pygame.draw.circle(WINDOW, YELLOW, (bar_x, y), checker_radius + 4, 4)

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
    bar_x = 400
    checker_radius = 20
    # Expand the clickable area for the bar to match the size of the checkers
    if (bar_x - checker_radius <= x <= bar_x + checker_radius):
        # For White's checkers on the bar
        bar_y_w = HEIGHT // 2 - 30
        num_w = len(bar['W'])
        for j in range(num_w):
            y_pos = bar_y_w - j * (checker_radius * 2 + 5)
            if (y_pos - checker_radius <= y <= y_pos + checker_radius):
                return 'bar'
        # For Black's checkers on the bar
        bar_y_b = HEIGHT // 2 + 30
        num_b = len(bar['B'])
        for j in range(num_b):
            y_pos = bar_y_b + j * (checker_radius * 2 + 5)
            if (y_pos - checker_radius <= y <= y_pos + checker_radius):
                return 'bar'
    return None

def is_legal_move(player, start, end, points, bar):
    global moves_left

    if start is None or end is None:
        return False

    # Determine the direction
    direction = -1 if player == 'W' else 1

    if bar[player]:
        if start != 'bar':
            return False  # Must enter checkers from the bar first
        # Entry point for bar checkers
        entry_point = end
        destination = points[entry_point]
        if destination and destination[-1] != player and len(destination) >= 2:
            return False  # Entry point is blocked
        move_distance = (24 - end) if player == 'W' else (end + 1)
        return move_distance in moves_left

    if start == 'bar':
        return False  # Can't move from bar if no checkers there

    move_distance = (end - start) * direction

    if can_bear_off(player, points):
        # Check for bearing off
        home_board = range(18, 24) if player == 'W' else range(0, 6)
        if start in home_board:
            if (player == 'W' and end == 24) or (player == 'B' and end == -1):
                # Exact roll to bear off from the farthest point
                if move_distance in moves_left:
                    return True
                else:
                    # No exact roll, check if there are no checkers behind
                    farthest_point = max([i for i in home_board if points[i] and points[i][-1] == player], default=None)
                    if farthest_point == start:
                        # Allow bearing off with higher die
                        if any(d >= move_distance for d in moves_left):
                            return True
            elif move_distance in moves_left:
                # Move within home board
                # Check if the destination point is blocked
                destination = points[end]
                if destination and destination[-1] != player and len(destination) >= 2:
                    return False  # Point is blocked
                return True
            return False

    # Normal movement rules
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

    # Handle checkers on the bar
    if bar[player]:
        if selected_checker != 'bar':
            return available_moves  # Must move checkers from the bar first
        for move in set(moves_left):
            entry_point = 24 - move if player == 'W' else move - 1
            if is_legal_move(player, selected_checker, entry_point, points, bar):
                available_moves.append(entry_point)
    else:
        # Normal movement
        direction = -1 if player == 'W' else 1
        for move in set(moves_left):
            end = selected_checker + direction * move
            if 0 <= end < 24 and is_legal_move(player, selected_checker, end, points, bar):
                available_moves.append(end)
            elif can_bear_off(player, points):
                # Check if bearing off
                if (player == 'W' and end == 24) or (player == 'B' and end == -1):
                    if is_legal_move(player, selected_checker, end, points, bar):
                        available_moves.append(end)

    return available_moves

def display_victory(player):
    font = pygame.font.SysFont(None, 72)
    victory_text = f"Player {'White' if player == 'W' else 'Black'} Wins!"
    text_surface = font.render(victory_text, True, GREEN)
    # Fill the screen and display the message
    WINDOW.fill(BEIGE)
    WINDOW.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - text_surface.get_height() // 2))
    pygame.display.update()
    # Pause for a moment
    pygame.time.delay(5000)

def save_game_state():
    state = {
        'points': copy.deepcopy(points),
        'bar': copy.deepcopy(bar),
        'borne_off': copy.deepcopy(borne_off),
        'current_player': current_player,
        'dice': dice[:],
        'moves_left': moves_left[:],
        'selected_checker': selected_checker
    }
    game_state_history.append(state)

def undo_move():
    global points, bar, borne_off, current_player, dice, moves_left, selected_checker

    if len(game_state_history) > 1:
        # Remove the current state
        game_state_history.pop()
        # Get the previous state
        prev_state = game_state_history[-1]

        # Restore the game state
        points = copy.deepcopy(prev_state['points'])
        bar = copy.deepcopy(prev_state['bar'])
        borne_off = copy.deepcopy(prev_state['borne_off'])
        current_player = prev_state['current_player']
        dice = prev_state['dice'][:]
        moves_left = prev_state['moves_left'][:]
        selected_checker = prev_state['selected_checker']
    else:
        print("No moves to undo.")

def main():
    global selected_checker, moves_left, current_player, dice, points, bar, borne_off, game_state_history
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

    # Initialize game state history
    game_state_history = []
    save_game_state()  # Save the initial state

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    undo_move()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Check if Undo button is clicked
                if undo_rect.collidepoint(pos):
                    undo_move()
                else:
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
                            elif selected_checker == 'bar' and point == 'bar':
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
                                    if point != 'bear_off' and points[point] and points[point][-1] != current_player:
                                        hit_checker = points[point].pop()
                                        bar[hit_checker].append(hit_checker)

                                    if (current_player == 'W' and point == 24) or (current_player == 'B' and point == -1):
                                        # Bear off the checker
                                        borne_off[current_player].append(checker)
                                    else:
                                        points[point].append(checker)

                                    # Calculate move distance
                                    if selected_checker == 'bar':
                                        move_distance = (24 - point) if current_player == 'W' else (point + 1)
                                    else:
                                        move_distance = abs(point - selected_checker)
                                    if move_distance == 0:
                                        move_distance = max(moves_left)
                                    moves_left.remove(move_distance)
                                    selected_checker = None

                                    # Save the game state after the move
                                    save_game_state()

                                    # Check for victory
                                    if len(borne_off[current_player]) == 15:
                                        display_victory(current_player)
                                        run = False
                                        break  # Exit the event loop

                                    if not moves_left:
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

        # Draw the Undo button
        button_font = pygame.font.SysFont(None, 30)
        undo_text = button_font.render("Undo (U)", True, BLACK)
        undo_rect = undo_text.get_rect(topleft=(50, HEIGHT - 40))
        pygame.draw.rect(WINDOW, WHITE, undo_rect.inflate(10, 10))
        WINDOW.blit(undo_text, undo_rect)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()