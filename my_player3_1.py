import random
import sys
import math
import copy
import numpy as np

N=5

def readInput(n, path="input.txt"):

    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]

        return piece_type, previous_board, board

def writeOutput(result, path="output.txt"):
    res = ""
    if result is None or result == (-1, -1):
        res='PASS'
    else:
	    res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)

def emptyBoard(board):
    for i in range(N):
        for j in range(N):
            if board[i][j]!=0:
                return False
    return True

def get_no_of_moves(previous_board, board):
    if(emptyBoard(previous_board)):
        if(emptyBoard(board)):
            no_of_moves = 0
        else:
            no_of_moves = 1
    else:
        with open("moves.txt") as fopen:
            no_of_moves = int(fopen.read())
            no_of_moves+=2
    with open("moves.txt","w") as f:
        f.write(str(no_of_moves))
    f.close()  
    return no_of_moves

class MyPlayer():
    def __init__(self, piece_type, previous_board, board):
        self.depth = 4
        self.bf = 20
        self.piece_type = piece_type
        self.opponent_piece_type = 3-piece_type
        self.previous_board = previous_board
        self.current_board = board

    def detect_neighbor(self, i, j, board):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j, board):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        neighbors = self.detect_neighbor(i, j, board)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j, board):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1], board)
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j, board):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        ally_members = self.ally_dfs(i, j, board)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1], board)
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False
    
    def calculate_euler_quad(self, i, j, board, piece_type, q_dict):
        if board[i+1][j+1]!=piece_type:
            q1=0
        else:
            q1=1
        if board[i+1][j]!=piece_type:
            q2=0
        else:
            q2=1
        if board[i][j+1]!=piece_type:
            q3=0
        else:
            q3=1
        if board[i][j]!=piece_type:
            q4=0
        else:
            q4=1
        q_sum = q1+q2+q3+q4
        if q_sum==1:
            q_dict["q1"]+=1
        elif q_sum==3:
            q_dict["q3"]+=1
        elif(q_sum==2 and ((board[i+1][j+1]==piece_type and board[i][j]==piece_type) or (board[i][j+1]==piece_type and board[i+1][j]==piece_type))):
            q_dict["q2"]+=1
        return

    def euler(self, piece_type, board):
        new_board = [[0]*(N+2) for i in range(N+2)]
        for i in range(N):
            for j in range(N):
                new_board[i + 1][j + 1] = board[i][j]
        opp = 3-piece_type
        my_q_dict={"q1":0,"q2":0,"q3":0}
        opp_q_dict={"q1":0,"q2":0,"q3":0}
        for i in range(N):
            for j in range(N):
                self.calculate_euler_quad(i, j, new_board, piece_type, my_q_dict)
                self.calculate_euler_quad(i, j, new_board, opp, opp_q_dict)
        return (my_q_dict["q1"] - my_q_dict["q3"] + 2 * my_q_dict["q2"] - (opp_q_dict["q1"] - opp_q_dict["q3"] + 2 * opp_q_dict["q2"])) / 4

    def piecePos(piece_type, board):
        pos = []
        for i in range(N):
            for j in range(N):
                if board[i][j] == piece_type:
                    pos.append((i,j))
        return pos

    def firstLib(self,piece_type,board):
        pos = piecePos(piece_type, board)
        libs=set()
        for each_pos in pos:
            neighbors = self.detect_neighbor(each_pos[0],each_pos[1],board)
            for neighbor in neighbors:
                if board[neighbor[0]][neighbor[1]]==0:
                    libs.add((neighbor[0],neighbor[1]))
        return len(libs)


    def utility1(self, piece_type, board):
        mycount=0
        oppcount=0
        opp = 3-piece_type
        for i in range(N):
            for j in range(N):
                if board[i][j]==piece_type:
                    mycount+=1
                elif board[i][j]==opp:
                    oppcount+=1
        return mycount-oppcount

    def utility2(self, piece_type, board):
        mycount=set()
        oppcount=set()
        opp = 3-piece_type
        for i in range(N):
            for j in range(N):
                if board[i][j]==0:
                    neighbors = self.detect_neighbor(i,j,board)
                    for neighbor in neighbors:
                        if board[neighbor[0]][neighbor[1]] == piece_type:
                            mycount.add((i, j))
                        elif board[neighbor[0]][neighbor[1]] == opp:
                            oppcount.add((i, j))
        return len(mycount)-len(oppcount)


    def side_count(self, piece_type, board):
        opp = 3-piece_type
        my_count = 0
        for i in range(N):
            if board[0][i] == piece_type or board[N- 1][i] == piece_type:
                my_count += 1
            if(i!=0 and i!=(N-1)):
                if board[i][0] == piece_type or board[i][N - 1] == piece_type:
                    my_count += 1
        return my_count
    
    def zero_count(self, board):
        zero_count = 0
        for i in range(1, N - 1):
            for j in range(1, N - 1):
                if board[i][j] == 0:
                    zero_count += 1
        return zero_count

    def utility(self, piece_type, board):
        utility1 = self.utility1(piece_type, board)
        utility2 = self.utility2(piece_type, board)
        my_side_count = self.side_count(piece_type, board)
        euler_number = self.euler(piece_type, board)
        zero_count = self.zero_count(board)
        komi = 2.5 if self.piece_type==2 else 0
        return  min(max(utility2, -8), 8) + (-4 * euler_number) + (5 * utility1) - (9 * my_side_count * (zero_count / 9))+komi

    def compare_board(self, board1, board2):
        for i in range(N):
            for j in range(N):
                if board1[i][j] != board2[i][j]:
                    return False
        return True
    
    def move_of_opp(self):
        if(self.compare_board(self.previous_board,self.current_board)):
            return None
        for i in range(N):
            for j in range(N):
                if(self.previous_board[i][j]!=self.current_board[i][j] and self.current_board[i][j]!=0):
                    return i,j

    def komi_rule_violate(self, i, j):
        if self.previous_board[i][j] != self.piece_type:
            return False
        new_board = copy.deepcopy(self.current_board)
        new_board[i][j] = self.piece_type
        opp_move_i, opp_move_j = self.move_of_opp()
        neighbors = self.detect_neighbor(i, j, new_board)
        for neighbor in neighbors:
            if neighbor[0] == opp_move_i and neighbor[1] == opp_move_j:
                if not self.libCheck(self.opponent_piece_type,opp_move_i, opp_move_j, new_board):
                    ally_dfs = self.ally_dfs(opp_move_i, opp_move_j, new_board)
                    for ally in ally_dfs:
                        new_board[ally[0]][ally[1]] = 0
        return self.compare_board(new_board, self.previous_board)

    def is_killing_move(self, board, piece_type, i, j):
        opp = 3-piece_type
        neighbors = self.detect_neighbor(i,j,board)
        for neighbor in neighbors:
            if(board[neighbor[0]][neighbor[1]] == opp):
                new_board = copy.deepcopy(board)
                new_board[i][j] = piece_type
                if((not self.libCheck(opp,neighbor[0], neighbor[1], new_board)) and (not self.komi_rule_violate(i,j))):
                    return True
        return False

    def libCheck(self, piece_type, i, j, board):
        marked = set()
        s = [(i, j)]
        while s:
            top = s.pop()
            marked.add(top)
            neighbors = self.detect_neighbor(top[0],top[1],board)
            for neighbor in neighbors:
                if (neighbor[0],neighbor[1]) in marked:
                    continue
                elif board[neighbor[0]][neighbor[1]] == 0:
                    return True
                elif board[neighbor[0]][neighbor[1]] == piece_type and (neighbor[0], neighbor[1]) not in marked:
                    s.append((neighbor[0], neighbor[1]))
        return False
    
    def find_all_moves(self, piece_type, board):
        killing = []
        p2 = []
        p3 = []
        for i in range(N):
            for j in range(N):
                if board[i][j] == 0:
                    if(self.libCheck(piece_type, i, j, board)):
                        if(not self.komi_rule_violate(i,j)):
                            if i == 0 or i == N-1 or j == 0 or j == N-1:
                                p3.append((i, j))
                            else:
                                p2.append((i, j))
                    else:
                        if(self.is_killing_move(board, piece_type, i, j)):
                            killing.append((i,j))
        killing.extend(p2)
        killing.extend(p3)
        killing.append((-1,-1))
        return killing

    def terminalState(self, min_or_max, given_depth, no_of_moves, second_pass_count):
        if(min_or_max == 'max'):
            if(given_depth==self.depth or no_of_moves+given_depth >=24 or second_pass_count):
                return True
            return False
        else:
            if(no_of_moves+given_depth >= 24 or second_pass_count):
                return True


    def get_next_state(self, piece_type, move, board):
        new_board = copy.deepcopy(board)
        opp=3-piece_type
        new_board[move[0]][move[1]] = piece_type
        neighbors = self.detect_neighbor(move[0],move[1],board)
        should_delete = 1
        for neighbor in neighbors:
            if new_board[neighbor[0]][neighbor[1]] == opp:
                if(self.find_liberty(neighbor[0],neighbor[1],new_board)):
                    should_delete = 0
                else:
                    to_delete=self.ally_dfs(neighbor[0],neighbor[1],new_board)
                if should_delete:
                    for piece in to_delete:
                        new_board[piece[0]][piece[1]] = 0
        return new_board

    def minValue(self, piece_type, board, no_of_moves, given_depth, second_pass_count, prev_action, a, b):
        if(self.terminalState('min', given_depth, no_of_moves, second_pass_count)):
            return self.utility(self.piece_type, board)
        if given_depth==self.depth:
            return self.utility(piece_type, board)
        min_action_value = math.inf
        opp = 3-piece_type
        second_pass_count = False
        moves_list = self.find_all_moves(piece_type, board)
        if prev_action == (-1, -1):
            second_pass_count = True
        for move in moves_list[:self.bf]:
            if move == (-1, -1):
                new_board = copy.deepcopy(board)
            else:
                new_board = self.get_next_state(piece_type, move, board)
            max_action_value = self.maxValue(opp,new_board,no_of_moves,given_depth+1,second_pass_count,move,a,b)
            if max_action_value < min_action_value:
                min_action_value = max_action_value
            if min_action_value <= a:
                return min_action_value
            b = min(b, min_action_value)
        return min_action_value

    def maxValue(self, piece_type, board, no_of_moves, given_depth, second_pass_count, prev_action, a, b):
        if(self.terminalState('max', given_depth, no_of_moves, second_pass_count)):
            return self.utility(piece_type, board)
        opp = 3-piece_type
        max_action = None; max_action_value = -math.inf
        second_pass_count = False
        moves_list = self.find_all_moves(piece_type, board)
        if prev_action == (-1, -1):
            second_pass_count = True
        for move in moves_list[:self.bf]:
            if move == (-1, -1):
                new_board = copy.deepcopy(board)
            else:
                new_board = self.get_next_state(piece_type, move, board)
            min_action_value = self.minValue(opp,new_board,no_of_moves,given_depth+1,second_pass_count,move,a,b)
            if max_action_value < min_action_value:
                max_action = move
                max_action_value = min_action_value
            if max_action_value >= b:
                if given_depth == 0:
                    return (max_action_value, max_action)
                else:
                    return max_action_value
            a = max(a, max_action_value)
        if given_depth == 0:
            return (max_action_value, max_action)
        else:
            return max_action_value

    def alphabeta(self, no_of_moves):
        max_action_value, max_action = self.maxValue(self.piece_type, self.current_board, no_of_moves, 0, False, None, -math.inf, math.inf)
        return max_action


    def get_input(self, no_of_moves):
        action = self.alphabeta(no_of_moves)
        return action
        

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    player = MyPlayer(piece_type, previous_board, board)
    no_of_moves = get_no_of_moves(previous_board, board)
    action = player.get_input(no_of_moves)
    writeOutput(action)