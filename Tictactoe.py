import pygame
import asyncio
import platform
import random
import sqlite3
import pygame_gui
from datetime import datetime
import sys

# Initialize Pygame
pygame.init()

# PlayerStats
P1Stats = None
P2Stats = None
P1Name = ""
P2Name = ""

# Elements
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (200, 200, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
ERROR_COLOR = (255,0,0)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')
screen.fill(BG_COLOR)

# Board
board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
current_player = 'X'
game_over = False
wait_to_reset = False
winner = None
gameMode = '1'
font = pygame.font.Font(None, 50)
scorefont = pygame.font.Font(None, 30)
titlefont = pygame.font.Font(None, 60)

class Coordinate:
    def __init__(self, row, column):
        self.row = row
        self.column = column

class PlayerStats:
    def __init__(self, playerID, playerName, playerWin, playerLoss, playerPlays):
        self.PlayerID = playerID
        self.Name = playerName
        self.Win = playerWin
        self.Loss = playerLoss
        self.Plays = playerPlays

def draw_lines():
    # Horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    # Vertical lines
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_score(TextColor):
    global P1Stats, P2Stats

    # If P2 Name is Empty it is a computer
    P2Name = P2Stats.Name
    if (P2Name == ""): P2Name = "Comp" 

    # Draw Score
    ScoreText = f"P1 ({P1Stats.Name}): {str(P1Stats.Win)} - P2 ({P2Name}): {str(P2Stats.Win)}"
    text_surface = scorefont.render(ScoreText, True, TextColor)
    text_rect = text_surface.get_rect(center=(300,20))
    screen.blit(text_surface, text_rect)


def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, 
                                (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X':
                pygame.draw.line(screen, CROSS_COLOR, 
                                (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), 
                                (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), 
                                CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, 
                                (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), 
                                (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), 
                                CROSS_WIDTH)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] == ''

def is_board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == '':
                return False
    return True

def check_win(player):
    # Check if any player have complete square marked
    # Vertical win
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            draw_vertical_winning_line(col, player)
            return True
    # Horizontal win
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            draw_horizontal_winning_line(row, player)
            return True
    # Diagonal win
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        draw_diagonal_winning_line(player, True)
        return True
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        draw_diagonal_winning_line(player, False)
        return True
    return False

def occupiedCoordinate(coordinate):
    if available_square(coordinate.row,coordinate.column):
        return coordinate
    else:
        return None

def check_potentialwin(player):
    # Check if 2 of the 3 squares already marked then decide which square to go to 
    # This can be used to block enemy move or advanced in own squares
    # Vertical win
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player:
            return occupiedCoordinate(Coordinate(2,col))
        if board[0][col] == player and board[2][col] == player:
            return occupiedCoordinate(Coordinate(1,col))
        if board[1][col] == player and board[2][col] == player:
            return occupiedCoordinate(Coordinate(0,col))
    # Horizontal win
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player:
            return occupiedCoordinate(Coordinate(row,2))
        if board[row][0] == player and board[row][2] == player:
            return occupiedCoordinate(Coordinate(row,1))
        if board[row][1] == player and board[row][2] == player:
            return occupiedCoordinate(Coordinate(row,0))
    # Diagonal win
    if board[0][0] == player and board[1][1] == player:
        return occupiedCoordinate(Coordinate(2,2))
    if board[1][1] == player and board[2][2] == player:
        return occupiedCoordinate(Coordinate(0,0))
    if board[0][0] == player and board[2][2] == player:
        return occupiedCoordinate(Coordinate(1,1))
    if board[0][2] == player and board[1][1] == player:
        return occupiedCoordinate(Coordinate(2,0))
    if board[2][0] == player and board[1][1] == player:
        return occupiedCoordinate(Coordinate(0,2))
    if board[2][0] == player and board[0][2] == player:
        return occupiedCoordinate(Coordinate(1,1))
    
    # return none if no 2 subsequent squares has been marked, so that the calculateMove function will just pick any unmarked square
    return None


def draw_vertical_winning_line(col, player):
    posX = col * SQUARE_SIZE + SQUARE_SIZE // 2
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (posX, 15), (posX, HEIGHT - 15), LINE_WIDTH)

def draw_horizontal_winning_line(row, player):
    posY = row * SQUARE_SIZE + SQUARE_SIZE // 2
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (15, posY), (WIDTH - 15, posY), LINE_WIDTH)

def draw_diagonal_winning_line(player, main_diagonal):
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    if main_diagonal:
        pygame.draw.line(screen, color, (15, 15), (WIDTH - 15, HEIGHT - 15), LINE_WIDTH)
    else:
        pygame.draw.line(screen, color, (15, HEIGHT - 15), (WIDTH - 15, 15), LINE_WIDTH)

def draw_game_over():
    global wait_to_reset, winner, P1Stats, P2Stats
    
    draw_score(BG_COLOR) # Erase last score by rewriting the text using BG_Color
    if (wait_to_reset == True):

        # Only execute this line when first time detecting Game Over otherwise it will add scores multiple times
        wait_to_reset = False

        P1Stats.Plays += 1
        P2Stats.Plays += 1
        if (winner == "X"):
            # P1 wins
            P1Stats.Win += 1
            P2Stats.Loss += 1
        elif (winner == "O"):
            # P2 / Computer wins, P1 Lose
            P2Stats.Win += 1
            P1Stats.Loss += 1

        # Save score to Database
        save_score(P1Stats) # Save P1 Stats to Database
        if (P2Stats.Name != ""):
            # Only save P2 Stats to Database if it's not a Computer
            save_score(P2Stats)

    if (winner):
        text = f"{winner} Won!, next turn is {winner}"
    else:
        # Draw, set the text
        text = "It's a Draw! next turn is randomised"
        
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    reset_text = font.render("Press 1 for 1P or 2 for 2P", True, TEXT_COLOR)
    reset_rect = reset_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(reset_text, reset_rect)

    draw_score(TEXT_COLOR) # Write new updated score
        
def get_currentNewPlayerName():
    return "Player-" + datetime.today().strftime('%Y%m%d%H%M')
    

def reset_game(mode):
    global board, current_player, game_over, winner, gameMode, P1Stats, P2Stats
    screen.fill(BG_COLOR)
    draw_lines()
    board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    gameMode = mode

    if (gameMode == '2') and (P2Stats.Name == ""):
        P2Stats.Name = get_currentNewPlayerName()
        P2Stats.PlayerID = -1
    
    if (gameMode == '1'):
        P2Stats.Name = ""
    
    if ((winner == "X") or (winner == "O")):
        # if X win, Set the Score X+1 and X should given the headstart in the next game
        # if O win, Set the Score O+1 and O should given the headstart in the next game
        current_player = winner
    else:
        # if Draw, No Score changed, next player should be randomised
        r = random.randint(0, 2)
        if (r < 1):
            current_player = "X"
        else:
            current_player = "O"

    draw_score(TEXT_COLOR)
    game_over = False
    winner = None

def save_score(PStats):
        query = ""
        connection = sqlite3.connect('tictactoe.db')
        cursor = connection.cursor()
        Winrate = round(((PStats.Win / PStats.Plays)*100), 2) # calculate winning rate

        if (PStats.PlayerID == -1):
            # New Player
            query = f"INSERT INTO score (playername, win, loss, plays, winrate) VALUES ('{PStats.Name}', {PStats.Win}, {PStats.Loss}, {PStats.Plays}, {Winrate})"
        else:
            # Existing Player
            query = f"UPDATE score SET win={PStats.Win}, loss={PStats.Loss}, plays={PStats.Plays}, winrate={Winrate} WHERE playerid={PStats.PlayerID}"
            
        cursor.execute(query)
        connection.commit()
        cursor.close()

        


def get_score(PlayerName, PStats):
    connection = sqlite3.connect('tictactoe.db')
    cursor = connection.cursor()
    selectSQL = f"SELECT * FROM score WHERE playername='{PlayerName}'"
    cursor.execute(selectSQL)
    output = cursor.fetchone()
    
    if (PlayerName == ""): output = None # if PlayerName is empty the PStats
    if (output):
        PStats.PlayerID = output[0] # Get current Player ID
        PStats.Name = output[1] # Get current Player Name
        PStats.Win = output[2] # winning score
        PStats.Loss = output[3] # lossing score
        PStats.Plays = output[4] # how many times have have play
    else:
        PStats.PlayerID = -1
        PStats.Name = PlayerName
        PStats.Win = 0
        PStats.Loss = 0
        PStats.Plays = 0
    
    connection.commit()

    # Close the connection
    connection.close()

    return PStats


def get_leaderboard():
    # Get leaderboard from database sorted by number of plays, winrate  descending
    connection = sqlite3.connect('tictactoe.db')
    cursor = connection.cursor()
    selectSQL = f"SELECT * FROM score ORDER BY plays DESC,winrate DESC"
    cursor.execute(selectSQL)
    output = cursor.fetchall()
    connection.commit()

    # Close the connection
    connection.close()

    return output

def display_leaderboard(Data):
    count = 0
    for x in Data:
        # create the leaderboard text
        HiScore = f"{x[1]} - Win: {x[2]} - Loss: {x[3]} - Win Rate: {x[5]}%"

        # display it on screen
        HiScoreText = scorefont.render(HiScore, True, CIRCLE_COLOR)
        YCoordinate = 300 + (count * 30)
        HiScoreText_rect = HiScoreText .get_rect(center=(300,YCoordinate))
        logscreen.blit(HiScoreText, HiScoreText_rect)
        count += 1

        # Only display 10 highest score
        if (count >= 10):
            break

def setupLogScreen():
    global clock, Player1Name, Player2Name, manager, logscreen

    # Prepare Log Screen
    logscreen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Log Screen")
    logscreen.fill(BG_COLOR)

    # Create UI elements
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))    
    Player1Name = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 90), (400, 30)), manager=manager, object_id='#P1_text_entry')
    Player2Name = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 150), (400, 30)), manager=manager, object_id='#P2_text_entry')
    Start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 200), (200, 30)), text='Start Game', manager=manager, object_id='#start_button')

    # Display Title
    TitleText = titlefont.render("TIC TAC TOE!", True, CROSS_COLOR)
    Text_rect = TitleText.get_rect(center=(300,40))
    logscreen.blit(TitleText, Text_rect)

    # Player 1 Name
    P1Text = scorefont.render("Player 1 Name:", True, CIRCLE_COLOR)
    P1_rect = P1Text.get_rect(center=(300,80))
    logscreen.blit(P1Text, P1_rect)

    # Player 2 Name
    P2Text = scorefont.render("Player 2 Name:", True, CIRCLE_COLOR)
    P2_rect = P2Text.get_rect(center=(300,140))
    logscreen.blit(P2Text, P2_rect)

    # Get and display leaderboard
    Data = get_leaderboard()
    display_leaderboard(Data)

    clock = pygame.time.Clock()
    get_player_name()

def validate_playerName(Name, checkEmpty):
    if (checkEmpty == True):
        if (Name == ""):
            return False
        elif len(Name) >= 30:
            return False
        else:
            return True
    else:
        if len(Name) >= 30:
            return False
        else:
            return True        

def writeText(text,x,y,color, scr):
    text_text = scorefont.render(text, True, color)
    text_rect = text_text.get_rect(center=(x,y))
    scr.blit(text_text, text_rect)

def show_player_name():
    global P1Name, P2Name
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        NameIsOK = True
        # Get Player 1 name
        P1Name = Player1Name.text
        if (validate_playerName(P1Name, True) == False):
            writeText("Please fix P1 name",300, 250, BG_COLOR, logscreen)
            writeText("Please fix P1 name",300, 250, ERROR_COLOR, logscreen)
            NameIsOK = False
            
        # If Player 2 doesnt have a name assume its the computer playing, otherwise get the name
        if (Player2Name.text != ""):
            P2Name = Player2Name.text
            if (validate_playerName(P2Name, False) == False):
                writeText("Please fix P2 name",300, 250, BG_COLOR, logscreen)
                writeText("Please fix P2 name",300, 250, ERROR_COLOR, logscreen)
                NameIsOK = False
        else:
            clock.tick(60)
            pygame.display.update()

        if NameIsOK == True:
            setup()
            while True:
                update_loop()
        else:
            #clock = pygame.time.Clock()
            get_player_name()


def get_player_name():
    while True:
        UI_REFRESH_RATE = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (event.type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_object_id == '#start_button'):
                show_player_name()
            manager.process_events(event)
        manager.update(UI_REFRESH_RATE)
        manager.draw_ui(logscreen)
        pygame.display.update()
    


def setup():
    global P1Stats, P2Stats, gameMode, P1Name, P2Name

    # Init Player Stats
    P1Stats = PlayerStats(-1,get_currentNewPlayerName(),0,0,0)
    P2Stats = PlayerStats(-1,"",0,0,0)
    P1Stats = get_score(P1Name, P1Stats) # Get P1 Stats when starting the game
    P2Stats = get_score(P2Name, P2Stats) # Get P2 Stats when starting the game

    if (P2Stats.Name == ""): 
        gameMode = '1' # if P2 Name is empty than its a Computer, 1 Player mode
    else:
        gameMode = '2' # if P2 Name is not empty than 2 Player mode
        
    screen.fill(BG_COLOR)
    draw_lines()
    draw_score(TEXT_COLOR)


def calculateMove():
    # Calculate Computer move logic here
    if available_square(1,1):
        # if middle square is empty try get it but ...
        # ... put handicap to make computer move slightly randomised
        r = random.randint(0, 2)
        if (r < 1):
            return Coordinate(1,1)
        
    for row in range(BOARD_COLS):
        for column in range(BOARD_ROWS):
            if available_square(row,column):
                # board is unoccupied then decide strategy
                coordPlayer = check_potentialwin('X') # Move to block enemy move
                coordComputer = check_potentialwin('O') # Move to try to complete the squares

                coord = coordPlayer # Firstly, prioritise in blocking enemy move
                if (coordComputer is not None): # if can complete the block try to switch strategy to complete the squares

                    # But put handicap to make computer move slightly randomised
                    r = random.randint(0, 2)
                    if (r > 1):
                        coord = coordComputer


                if (coord is None):
                    # if check_potentialwin not returning any for both strategy (blocking enemy move, or completing own squares), then just pick dummy unoccupied column
                    return Coordinate(row,column)
                else:
                    return coord


def update_loop():
    global current_player, game_over, wait_to_reset, winner, gameMode
    
    # Draw the figure
    draw_figures()
    
    # Check if game over
    if game_over:
        draw_game_over()

    if (game_over != True) and (gameMode == '1'): # If Gamemode = 1 means 1P then O is Computer
        if (current_player == 'O'): 
            # if gamemode is 1P and O turn, then do move calculation for computer 
            computerMove = calculateMove();  
            if (computerMove is not None):     
                mark_square(computerMove.row, computerMove.column, current_player)
                if check_win(current_player):
                    game_over = True
                    winner = current_player
                    wait_to_reset = True
                elif is_board_full():
                    game_over = True
                    wait_to_reset = True
                else:
                    current_player = 'O' if current_player == 'X' else 'X'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            # Player move, get whatever square player choose and mark it (if it is available)
            mouseX, mouseY = event.pos
            clicked_row = mouseY // SQUARE_SIZE
            clicked_col = mouseX // SQUARE_SIZE
            if available_square(clicked_row, clicked_col):
                mark_square(clicked_row, clicked_col, current_player)
                if check_win(current_player):
                    game_over = True
                    winner = current_player
                    wait_to_reset = True
                elif is_board_full():
                    game_over = True
                    wait_to_reset = True
                else:
                    current_player = 'O' if current_player == 'X' else 'X'

        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            reset_game('1')
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            reset_game('2')

    pygame.display.update()


async def main():
    setupLogScreen()
    #while True:
    #    update_loop()
    #    await asyncio.sleep(1.0 / 60)


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())