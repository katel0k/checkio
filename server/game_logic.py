# regarding color: true <=> white checker, false - opposite

def sign(x):
    return -1 if x < 0 else 1

class GameCell:
    is_empty = True # if cell is empty, everything else is junk data
    color = True
    is_queen = False
    # it exists only because I'm lazy
    def __init__(self, char):
        self.is_empty = char == '0'
        self.color = char == 'w' or char == 'W'
        self.is_queen = char == 'W' or char == 'B'
    
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, 
    #         sort_keys=True, indent=4)

class Game:
    order_color = True
    field = list(map(lambda s:
        [GameCell(x) for x in s],
            ['0b0b0b0b', 'b0b0b0b0', '0b0b0b0b', '00000000',
            '00000000', 'w0w0w0w0', '0w0w0w0w', 'w0w0w0w0'])) # i'm just lazy:)
    move_history = []

class GameMove:
    field_from = None
    field_to = None
    is_possible = False
    queens = False
    eats = False
    changes_order = False
    player_color = False
    def __init__(self, field_from, field_to, player_color):
        self.field_from = field_from
        self.field_to = field_to
        self.player_color = player_color

class GameEngine:
    def handle_move(self, game, move: GameMove):
        result = self.check_and_enhance_move(game, move)
        if result:
            self.make_move(game, move)
            game.move_history.append(move)
        return result

    def make_move(self, game, move):
        y0, x0 = move.field_from
        y, x = move.field_to
        game.field[y][x] = game.field[y0][x0]
        game.field[y0][x0] = GameCell('0')
        if move.queens:
            game.field[y][x].is_queen = True
        if move.eats:
            game.field[move.eats[0]][move.eats[1]] = GameCell('0')
        if move.changes_order:
            game.order_color = not game.order_color

    def _get_diagonal_info(self, move):
        arr = []
        from_ind = 0
        to_ind = 0
        y0, x0 = move.field_from
        y, x = move.field_to
        if sign(y - y0) == sign(x - x0):
            for c in range(-8, 8):
                if 0 <= y0 + c < 8 and 0 <= x0 + c < 8:
                    arr.append((y0 + c, x0 + c))
                if c == 0: from_ind = len(arr) - 1
                if y0 + c == y and x0 + c == x:
                    to_ind = len(arr) - 1
        else:
            for c in range(-8, 8):
                if 0 <= y0 + c < 8 and 0 <= x0 - c < 8:
                    arr.append((y0 + c, x0 - c))
                if c == 0: from_ind = len(arr) - 1
                if y0 + c == y and x0 - c == x:
                    to_ind = len(arr) - 1

        return arr, from_ind, to_ind

    def _check_diagonal_for_eating(self, diagonal, game):
        def _check(diag):
            prev = None
            candidate = False

            for y, x in diag:
                if game.field[y][x].is_empty:
                    if candidate:
                        return True
                    candidate = False
                    if prev is None:
                        continue
                    if not prev.is_queen:
                        prev = None
                        continue
                
                if game.field[y][x].color != game.order_color:
                    if prev is None:
                        candidate = False
                        continue
                    candidate = True
                    
                if game.field[y][x].color == game.order_color:
                    prve = game.field[y][x]
                    candidate = False
            return False

        return _check(diagonal) or _check(diagonal[::-1])
    
    def _check_eating(self, game, y, x):
        # I sincerely apologize to anyone, who tries to read this code
        # It just checks if there are any checkers to be eaten, and it is very ugly
        # I think it is clear that I am familiar with industry standarts such as DRY or some codestyle standarts about function sizes
        if game.field[y][x].is_queen:
            diagonal, from_ind, _ = self._get_diagonal_info(GameMove((y, x), (y + 1, x + 1)))
            eats = False
            for ty, tx in diagonal[from_ind + 1:]:
                cell = game.field[ty][tx]
                if eats:
                    if cell.is_empty: return True
                    else: break
                if cell.is_empty: continue
                if cell.color != game.order_color:
                    eats = True
                if cell.color == game.order_color:
                    break
            for ty, tx in diagonal[from_ind + 1::-1]:
                cell = game.field[ty][tx]
                if eats:
                    if cell.is_empty: return True
                    else: break
                if cell.is_empty: continue
                if cell.color != game.order_color:
                    eats = True
                if cell.color == game.order_color:
                    break
            diagonal, from_ind, _ = self._get_diagonal_info(GameMove((y, x), (y + 1, x - 1)))

            for ty, tx in diagonal[from_ind + 1:]:
                cell = game.field[ty][tx]
                if eats:
                    if cell.is_empty: return True
                    else: break
                if cell.is_empty: continue
                if cell.color != game.order_color:
                    eats = True
                if cell.color == game.order_color:
                    break
            for ty, tx in diagonal[from_ind + 1:]:
                cell = game.field[ty][tx]
                if eats:
                    if cell.is_empty: return True
                    else: break
                if cell.is_empty: continue
                if cell.color != game.order_color:
                    eats = True
                if cell.color == game.order_color:
                    break
        else:
            if (0 <= y + 1 < 8 and 0 <= x + 1 < 8 and 
                    not game.field[y + 1][x + 1].is_empty and game.field[y + 1][x + 1].color != cell.color):
                if 0 <= y + 2 < 8 and 0 <= x + 2 < 8 and game.field[y + 2][x + 2].is_empty: return True
            if (0 <= y + 1 < 8 and 0 <= x - 1 < 8 and 
                    not game.field[y + 1][x - 1].is_empty and game.field[y + 1][x - 1].color != cell.color):
                if 0 <= y + 2 < 8 and 0 <= x - 2 < 8 and game.field[y + 2][x - 2].is_empty: return True
            if (0 <= y - 1 < 8 and 0 <= x + 1 < 8 and 
                    not game.field[y - 1][x + 1].is_empty and game.field[y - 1][x + 1].color != cell.color):
                if 0 <= y - 2 < 8 and 0 <= x + 2 < 8 and game.field[y - 2][x + 2].is_empty: return True
            if (0 <= y - 1 < 8 and 0 <= x - 1 < 8 and 
                    not game.field[y - 1][x - 1].is_empty and game.field[y - 1][x - 1].color != cell.color):
                if 0 <= y - 2 < 8 and 0 <= x - 2 < 8 and game.field[y - 2][x - 2].is_empty: return True
        return False

    def check_and_enhance_move(self, game: Game, move: GameMove):
        move.is_possible = False

        y0, x0 = move.field_from
        y, x = move.field_to

        if game.field[y0][x0].is_empty: return False # there is a checker to be moved
        if move.player_color != game.order_color: return False # player moved is correct color
        if game.field[y0][x0].color != game.order_color: return False # checker is correct color
        if abs(y - y0) != abs(x - x0): return False # same diagonal 
        if not game.field[y][x].is_empty: return False # new field is empty

        diagonal, from_ind, to_ind = self._get_diagonal_info(move)
        cell0 = game.field[y0][x0] # just a shortcut
        direction = 1 if to_ind > from_ind else -1 # just a shortcut

        if abs(to_ind - from_ind) == 1: # single cell move
            move.eats = False
        elif cell0.is_queen: # rules for queens are slightly different
            for ty, tx in diagonal[from_ind + 1:to_ind:direction]:
                cell = game.field[ty][tx]
                if cell.is_empty: continue
                if cell.color != game.order_color:
                    if move.eats:
                        move.eats = False
                        return False
                    else:
                        move.eats = True
        else:
            if abs(to_ind - from_ind) > 2: return False
            # only remaining option is difference being equal to 2
            ty, tx = diagonal[from_ind + direction]
            cell = game.field[ty][tx]
            if not cell.is_empty and cell.color != game.order_color:
                move.eats = diagonal[from_ind + direction]
                move.is_possible = True
                if y == 0 and cell.color or y == 7 and not cell.color:
                    move.queens = True
                return move

        if move.eats:
            move.is_possible = True
            if y == 0 and cell.color or y == 7 and not cell.color:
                move.queens = True

            move.changes_order = not self._check_eating(game, y, x)
            return move

        # yes it is full of costyly, and so?
        for i in range(0, 8, 2):
            if self._check_diagonal_for_eating(self._get_diagonal_info(GameMove((i, 0), (i+1,1), False))[0], game): return False
            if self._check_diagonal_for_eating(self._get_diagonal_info(GameMove((0, i), (i+1,1), False))[0], game): return False
            if self._check_diagonal_for_eating(self._get_diagonal_info(GameMove((i, 0), (i-1,1), False))[0], game): return False
            if self._check_diagonal_for_eating(self._get_diagonal_info(GameMove((0, i), (i-1,1), False))[0], game): return False

        move.is_possible = True
        if y == 0 and cell.color or y == 7 and not cell.color:
            move.queens = True
        move.changes_order = True
        return move

        # didn't add another param to the move object, "changes_order"