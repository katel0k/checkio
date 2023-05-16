from ...database import GameOutcomes

class GameField(list):
    ''' Класс для удобства, часто используется доступ по tuple (row, column), и он позволяет такой доступ делать
    '''
    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            return self[key[0]][key[1]]
        return super().__getitem__(key)
    
    def __setitem__(self, key, value):
        if isinstance(key, tuple) and len(key) == 2:
            self[key[0]][key[1]] = value
        else:
            super().__setitem__(key, value)

class GameCell:
    '''Класс клетки поля GameField. 
    0 - пустая клетка, маленькие буквы - не дамки, большие - дамки. w - белый, b - черный'''
    def __init__(self, char='0'):
        self.is_empty = char == '0'
        self.is_white = char == 'w' or char == 'W'
        self.is_queen = char == 'W' or char == 'B'
    def __str__(self):
        if self.is_empty: return '0'
        if self.is_queen: return 'W' if self.is_white else 'B'
        return 'w' if self.is_white else 'b'
    def __repr__(self):
        return self.__str__()

class GameMove:
    '''Класс для хранения всех данных о ходе. '''
    def __init__(self, field_from, field_to, is_white_player, **kwargs):
        self.field_from = field_from
        self.field_to = field_to
        self.is_white_player = is_white_player
        self.is_possible = kwargs.get('is_possible', False)
        self.queens = kwargs.get('queens', False)
        self.eats = kwargs.get('eats', False)
        self.changes_order = kwargs.get('changes_order', False)
    def __str__(self):
        return (f'{self.field_from[0]},{self.field_from[1]},{self.field_to[0]},{self.field_to[1]},'
            + f'{int(self.is_white_player)}{int(self.queens)}{int(self.changes_order)},'
            + (f'{self.eats[0]},{self.eats[1]}' if self.eats else '-'))
    # def __str__(self):
    #     # incorrect, redo
    #     return str(self.field_from) + ' ' + str(self.field_to) + ' ' + str(self.is_white_player)
    #     # return 

class Game:
    def __init__(self, **kwargs):
        '''Создает игру по правилам, заданным в параметрах функции. Правила для модификации:
            CAN_EAT_BACKWARDS = True, # может ли простая шашка есть назад
            TURNS_QUEEN_AFTER_EATING = True, # превращается ли шашка во время боя в дамку
            QUEEN_GOES_FURTHER = True, # ходит ли дамка на несколько полей или только на одно
            CAN_QUEEN_EAT_FURTHER = True, # может ли дамка идти на произвольное поле после боя
            STARTING_POSITION = (стандартная расстановка для русских шашек) # строка, задающая изначальную позицию. 
                Формат клеток в соответствии с форматом Cell. Строки должны быть разделены с помощью \\n
            FIELD_SIZE = 8
        '''
        self.is_white_move = kwargs.get('STARTING_ORDER', True)
        self.field = GameField(map(
                lambda x: list(map(GameCell, list(x))),
                kwargs.get('STARTING_POSITION', 
'''0b0b0b0b
b0b0b0b0
0b0b0b0b
00000000
00000000
w0w0w0w0
0w0w0w0w
w0w0w0w0'''
).split()))
        
        self.CAN_EAT_BACKWARDS = kwargs.get('CAN_EAT_BACKWARDS', True)
        self.TURNS_QUEEN_AFTER_EATING = kwargs.get('TURNS_QUEEN_AFTER_EATING', True)
        self.QUEEN_GOES_FURTHER = kwargs.get('QUEEN_GOES_FURTHER', True)
        self.CAN_QUEEN_EAT_FURTHER = kwargs.get('CAN_QUEEN_EAT_FURTHER', True)
        self.FIELD_SIZE = kwargs.get('FIELD_SIZE', 8)

        self.outcome: GameOutcomes | None = None # исход партии. По умолчанию это False, то есть его еще нет
        self.history = []
        self._prev = None # последняя шашка, сделавшая съедающий ход.

    def _generate_diagonal(self, r, c, is_main=True):
        '''генерирует диагональ, содержающую клетку r,c. Направление диагонали aka главность определяется is_main'''
        res = []
        for k in range(-self.FIELD_SIZE, self.FIELD_SIZE):
            if 0 <= r + k < self.FIELD_SIZE and 0 <= c + (k if is_main else -k) < self.FIELD_SIZE:
                res.append((r + k, c + (k if is_main else -k)))
        return res

    # не используются, если не делать турецкие шашки (в планах есть)
    def _generate_row(self, r): return [(r, i) for i in range(self.FIELD_SIZE)]
    def _generate_col(self, c): return [(i, c) for i in range(self.FIELD_SIZE)]

    def _generate_fields_to_check(self):
        '''захардкоженные поля для проверки. В теории, для других правил, это можно будет поменять'''
        res = []
        for i in range(-self.FIELD_SIZE + 1, self.FIELD_SIZE * 2, 2):
            res.append(self._generate_diagonal(0, i))
            res.append(self._generate_diagonal(0, i, False))
        return res
        
    def _get_array_fights(self, array, dir):
        '''Возвращает dict элементов вида (field_from, field_to): eats, состоящий из всех возможных поедающих ходов на "диагонали" array.
            Диагональю может быть любой массив, состояющий из координат клеток. Поиск ходов производится в одну сторону по этому массиву
            Сторона по увелечению индекса считается как сверху вниз (dir=True)
          dir = True если сверху вниз(важно, если назад бить нельзя)'''
        predator = None
        prey = None
        res = {}
        for cell_coords in array:
            cell = self.field[cell_coords]
            if cell.is_empty:
                if predator is None: continue
                if prey is not None:
                    if not(not self.field[predator].is_queen and not self.CAN_EAT_BACKWARDS
                           and dir == self.field[predator].is_white):
                        res[(predator, cell_coords)] = prey
                    if not(self.field[predator].is_queen and self.CAN_QUEEN_EAT_FURTHER):
                        predator = None
                        prey = None
                elif not self.field[predator].is_queen:
                    predator = None
            elif cell.is_white == self.is_white_move:
                predator = cell_coords
                prey = None
            else:
                if predator is None: continue
                if prey is not None:
                    predator = None
                    prey = None
                else:
                    prey = cell_coords
        return res
    
    def _get_array_noneating_moves(self, array, dir):
        '''Возвращает set элементов вида (field_from, field_to), состоящий из всех возможных ходов по "диагонали" array.
            Диагональю может быть любой массив, состояющий из координат клеток. Поиск ходов производится в одну сторону по этому массиву
            Сторона по увелечению индекса считается как сверху вниз (dir=True)
            '''
        checker_coords = None
        res = set()
        for cell_coords in array:
            cell = self.field[cell_coords]
            if cell.is_empty:
                if checker_coords is None: continue
                if self.field[checker_coords].is_queen or dir != self.field[checker_coords].is_white:
                    res.add((checker_coords, cell_coords))
                if not self.field[checker_coords].is_queen or not self.QUEEN_GOES_FURTHER:
                    checker_coords = None
            elif cell.is_white == self.is_white_move:
                checker_coords = cell_coords
            else:
                checker_coords = None
        return res
    
    def _get_all_fights(self):
        '''Возвращает dict элементов вида (field_from, field_to): eats, состоящий из всех возможных поедающих ходов.'''
        res = {}
        for arr in self._generate_fields_to_check():
            res.update(self._get_array_fights(arr, True))
            res.update(self._get_array_fights(arr[::-1], False))
        return res
    
    def _get_all_noneating_moves(self):
        '''Возвращает set элементов вида (field_from, field_to), состоящий из всех возможных непоедающих ходов'''
        res = set()
        for arr in self._generate_fields_to_check():
            res.update(self._get_array_noneating_moves(arr, True))
            res.update(self._get_array_noneating_moves(arr[::-1], False))
        return res

    def _check_and_enhance_move(self, move):
        '''Проверяет, возможен ли данный ход. Кусочек плохого кода: она также редактирует переменную хода.
        В частности, редактируются поля is_possible, queens, eats, changes_order.
        Возвращает отредактированную переменную, если ход возможен и False иначе'''
        move.is_possible = False
        if self._prev and move.field_from != self._prev: 
            return False # если предыдущий ход был боем и бой не завершился, проверяет, та же ли шашка подвинута
        if self.field[move.field_from].is_empty: return False # есть шашка которую можно подвинуть
        if move.is_white_player != self.is_white_move: return False # правильный цвет игрока
        if self.field[move.field_from].is_white != self.is_white_move: return False # шашка нужного цвета
        if not self.field[move.field_to].is_empty: return False # новое поле для шашки пустое

        fights_array = self._get_all_fights()
        # print(fights_array)
        moves_array = self._get_all_noneating_moves()
        # print(moves_array)

        if len(fights_array) != 0:
            if (move.field_from, move.field_to) not in fights_array:
                return False
            move.eats = fights_array[(move.field_from, move.field_to)]
        elif (move.field_from, move.field_to) not in moves_array:
            return False
        
        cell = self.field[move.field_from]
        move.queens = move.field_to[0] == 0 and cell.is_white or move.field_to[0] == 7 and not cell.is_white
        move.is_possible = True
        move.changes_order = True
        return move
    
    def _check_eating(self):
        all_fights = self._get_all_fights()
        for (field_from, _) in all_fights.keys():
            if field_from == self._prev: return True
        return False
        
    def _make_move(self, move):
        y0, x0 = move.field_from
        y, x = move.field_to
        
        self.field[y][x] = GameCell(str(self.field[y0][x0]))
        self.field[y0][x0] = GameCell('0')
        
        if move.eats:
            self.field[move.eats] = GameCell('0')
            self._prev = move.field_to
            move.changes_order = not self._check_eating()

        if move.queens and (move.changes_order or self.TURNS_QUEEN_AFTER_EATING):
            self.field[y][x].is_queen = True

        if move.changes_order:
            self._prev = None
            self.is_white_move = not self.is_white_move

        if len(self._get_all_noneating_moves()) == 0 and len(self._get_all_fights()) == 0:
            self.outcome = GameOutcomes.WHITE_WON if not self.is_white_move else GameOutcomes.BLACK_WON
        
        self.history.append(move)

    def handle_move(self, move):
        '''Возвращает False если ход невозможен, иначе выполняет ход'''
        res = self._check_and_enhance_move(move)
        if res:
            self._make_move(res)
        return res