# searchAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
This file contains all of the agents that can be selected to control Pacman.  To
select an agent, use the '-p' option when running pacman.py.  Arguments can be
passed to your agent using '-a'.  For example, to load a SearchAgent that uses
depth first search (dfs), run the following command:

> python pacman.py -p SearchAgent -a fn=depthFirstSearch

Commands to invoke other search strategies can be found in the project
description.

Please only change the parts of the file you are asked to.  Look for the lines
that say

"*** YOUR CODE HERE ***"

The parts you fill in start about 3/4 of the way down.  Follow the project
description for details.

Good luck and happy searching!
"""

from game import Directions
from game import Agent
from game import Actions
from itertools import permutations
import util
import time
import random
import search

class GoWestAgent(Agent):
    "An agent that goes West until it can't."

    def getAction(self, state):
        "The agent receives a GameState (defined in pacman.py)."
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
# This portion is written for you, but will only work #
#       after you fill in parts of search.py          #
#######################################################

class SearchAgent(Agent):
    """
    This very general search agent finds a path using a supplied search
    algorithm for a supplied search problem, then returns actions to follow that
    path.

    As a default, this agent runs DFS on a PositionSearchProblem to find
    location (1,1)

    Options for fn include:
      depthFirstSearch or dfs
      breadthFirstSearch or bfs


    Note: You should NOT change any code in SearchAgent
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems

        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError, fn + ' is not a search function in search.py.'
        func = getattr(search, fn)
        if 'heuristic' not in func.func_code.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError, heuristic + ' is not a function in searchAgents.py or search.py.'
            print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError, prob + ' is not a search problem type in SearchAgents.py.'
        self.searchType = globals()[prob]
        print('[SearchAgent] using problem type ' + prob)

    def registerInitialState(self, state):
        """
        This is the first time that the agent sees the layout of the game
        board. Here, we choose a path to the goal. In this phase, the agent
        should compute the path to the goal and store it in a local variable.
        All of the work is done in this method!

        state: a GameState object (pacman.py)
        """
        if self.searchFunction == None: raise Exception, "No search function provided for SearchAgent"
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

    def getAction(self, state):
        """
        Returns the next action in the path chosen earlier (in
        registerInitialState).  Return Directions.STOP if there is no further
        action to take.

        state: a GameState object (pacman.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point on the pacman board.

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print 'Warning: this does not look like a regular search maze'

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # Bookkeeping for display purposes
        self._expanded += 1 # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class StayEastSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the West side of the board.

    The cost function for stepping into a position (x,y) is 1/2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (1, 1), None, False)

class StayWestSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the East side of the board.

    The cost function for stepping into a position (x,y) is 2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    "The Manhattan distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    "The Euclidean distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """

    def __init__(self, startingGameState):
        """
        Stores the walls, pacman's starting position and corners.
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print 'Warning: no food in corner ' + str(corner)
        self._expanded = 0 # DO NOT CHANGE; Number of search nodes expanded
        # Please add any code here which you would like to use
        # in initializing the problem

    def getStartState(self):
        """
        Returns the start state (in your state space, not the full Pacman state
        space)
        """
        return (
            self.startingPosition,
            self.corners,
        )

    def isGoalState(self, state):
        """
        Returns whether this search state is a goal state of the problem.
        """
        return not state[1]

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
            For a given state, this should return a list of triples, (successor,
            action, stepCost), where 'successor' is a successor to the current
            state, 'action' is the action required to get there, and 'stepCost'
            is the incremental cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            position, cornersLeft = state
            x, y = position
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if self.walls[nextx][nexty]:
                continue

            successors.append((
                (
                    (nextx, nexty),
                    tuple(corner for corner in cornersLeft if (nextx, nexty) != corner)
                ),
                action,
                1,
            ))

        self._expanded += 1 # DO NOT CHANGE
        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999.  This is implemented for you.
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state, problem):
    """
    A heuristic for the CornersProblem that you defined.

      state:   The current search state
               (a data structure you chose in your search problem)

      problem: The CornersProblem instance for this layout.

    This function should always return a number that is a lower bound on the
    shortest path from the state to a goal of the problem; i.e.  it should be
    admissible (as well as consistent).
    """
    # See also:
    #   nearestCornersManhattanHeuristic
    #   farthestCornersManhattanHeuristic
    #   probedIntersectionsManhattanHeuristic
    return allCornersManhattanHeuristic(state, problem)

def nearestCornersManhattanHeuristic(state, problem):
    """Gets the Manhattan distance for the nearest corner. This is definitely
    admissable, but I don't think it's consistent."""
    position, cornersLeft = state
    return (
        0 if not cornersLeft
        else min((util.manhattanDistance(position, corner) for corner in cornersLeft))
    )

def farthestCornersManhattanHeuristic(state, problem):
    """Gets the Manhattan distance for the farthest corner. This is definitely
    admissable, and as far as I can tell also consistent."""
    position, cornersLeft = state
    return (
        0 if not cornersLeft
        else max((util.manhattanDistance(position, corner) for corner in cornersLeft))
    )

INFINITY = float("inf")
PROBE_DEPTH = 5
ACTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

def probedIntersectionsManhattanHeuristic(state, problem):
    """Looks for the nearest intersections and gets the minimum sum of the
    Manhattan distance from the current position to each one and the Manhattan
    distance from them to their nearest corner. This works based on the idea
    that at the very least, to reach a nearest corner, you must get out of the
    hallway. It has only slight improvements on nearestCornersManhattanHeuristic
    but is probably more expensive in the long run if you also consider the
    computation necessary for the heuristic itself. This is definitely
    admissable and consistent."""
    (x, y), cornersLeft = state
    if not cornersLeft or (x, y) in cornersLeft:
        return 0
    
    nearestIntersections = [
        getNearestIntersection(action, x + action[0], y + action[1], problem.walls, cornersLeft, 1)
        for action in ACTIONS
        if not problem.walls[x + action[0]][y + action[1]]
    ]

    return min((
        intersection[1] +
        nearestCornersManhattanHeuristic((intersection[0], cornersLeft), problem)
        for intersection in nearestIntersections
    ))

def getNearestIntersection(lastAction, x, y, walls, cornersLeft, depth):
    if depth >= PROBE_DEPTH or (x, y) in cornersLeft:
        return ((x, y), depth)

    neighbors = [
        (action, x + action[0], y + action[1], walls, cornersLeft, depth + 1)
        for action in ACTIONS
        if not walls[x + action[0]][y + action[1]] and action != (-lastAction[0], -lastAction[1])
    ]
    if len(neighbors) == 0:
        return ((x, y), INFINITY)
    elif len(neighbors) == 1:
        return getNearestIntersection(*neighbors[0])
    else:
        return ((x, y), depth)

def allCornersManhattanHeuristic(state, problem):
    """Rather than computing the Manhattan distance to the nearest corner, this
    computes the minimum Manhattan distance to from the current position to each
    corner left in succession for all permutations of corner-visiting orders.

    Even in the worst case when there are 4 corners left to visit, this is both
    fast and performant, only requiring you to calculate to compute 4! * 4 = 96
    Manhattan distances for each heuristic. This is super performant though,
    cutting the number of node visits in half vs. its single corner cousin on
    the mediumCorners problem (760 vs 1480)."""

    position, cornersLeft = state
    if not cornersLeft:
        return 0

    return min((
        util.manhattanDistance(position, perm[0]) +
            sum((util.manhattanDistance(perm[ii - 1], perm[ii])
                 for ii in xrange(1, len(perm))))
        for perm in permutations(cornersLeft)
    ))

class AStarCornersAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    A search problem associated with finding the a path that collects all of the
    food (dots) in a Pacman game.

    A search state in this problem is a tuple ( pacmanPosition, foodGrid ) where
      pacmanPosition: a tuple (x,y) of integers specifying Pacman's position
      foodGrid:       a Grid (see game.py) of either True or False, specifying remaining food
    """
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0 # DO NOT CHANGE
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost of 1."
        successors = []
        self._expanded += 1 # DO NOT CHANGE
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

def foodHeuristic(state, problem):
    """
    Your heuristic for the FoodSearchProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come
    up with an admissible heuristic; almost all admissible heuristics will be
    consistent as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the
    other hand, inadmissible or inconsistent heuristics may find optimal
    solutions, so be careful.

    The state is a tuple ( pacmanPosition, foodGrid ) where foodGrid is a Grid
    (see game.py) of either True or False. You can call foodGrid.asList() to get
    a list of food coordinates instead.

    If you want access to info like walls, capsules, etc., you can query the
    problem.  For example, problem.walls gives you a Grid of where the walls
    are.

    If you want to *store* information to be reused in other calls to the
    heuristic, there is a dictionary called problem.heuristicInfo that you can
    use. For example, if you only want to count the walls once and store that
    value, try: problem.heuristicInfo['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access
    problem.heuristicInfo['wallCount']
    """
    # return 0  # 60-cost path, 16,688 expansions in 1.8s
    # return allFoodManhattanHeuristic(state, problem)  # Takes too long
    # return allNFoodManhattanHeuristic(state, problem, 2)  # 12,531 expansions in 1.5s
    # return allNFoodManhattanHeuristic(state, problem, 3)  # 16,688 expansions in 1.9s
    # return farthestNFoodsManhattanHeuristic(state, problem, 1)  # 9,551 expansions in 1.8s
    # return farthestNFoodsManhattanHeuristic(state, problem, 2)  # 8,560 expansions in 1.6s
    # return farthestNFoodsManhattanHeuristic(state, problem, 3)  # 8,153 expansions in 1.7s
    # return farthestNFoodsManhattanHeuristic(state, problem, 4)  # 7,921 expansions in 2.2s
    # return farthestNFoodsManhattanHeuristic(state, problem, 5)  # 7,666 expansions in 5.9s
    # return farthestNFoodsManhattanHeuristic(state, problem, 6)  # 7,427 expansions in 30s
    # return farthestNFoodsManhattanHeuristic(state, problem, 8)  # Takes too long
    # return farthestNFoodsMazeManhattanHeuristic(state, problem, 1)  # 10,768 expansions in 73s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 2)  # 8,560 expansions in 2.0s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 3)  # 8,153 expansions in 2.5s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 4)  # 7,920 expansions in 3.8s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 5)  # 7,666 expansions in 8.1s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 6)  # 7,427 expansions in 20.6s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 7)  # 7,175 expansions in 52.0s
    # return farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, 8)  # 6,984 expansions in 137.1s
    return farthestFoodMazeHeuristic(state, problem)  # 4,137 expansions in 28.1s

def farthestFoodManhattanHeuristic(state, problem):
    position, foodGrid = state
    foodPositions = foodGrid.asList()
    if not foodPositions:
        return 0

    return max((
        util.manhattanDistance(position, foodPosition)
        for foodPosition in foodPositions
    ))

def allNFoodManhattanHeuristic(state, problem, n):
    position, foodGrid = state
    foodPositions = tuple((
        (x, y)
        for x in xrange(0, foodGrid.width, n)
        for y in xrange(0, foodGrid.height, n)
        if foodGrid[x][y]
    ))
    if not foodPositions:
        return 0

    return min((
        util.manhattanDistance(position, perm[0]) +
            sum((util.manhattanDistance(perm[ii - 1], perm[ii])
                 for ii in xrange(1, len(perm))))
        for perm in permutations(foodPositions)
    ))

def allFoodManhattanHeuristic(state, problem):
    position, foodGrid = state
    foodPositions = foodGrid.asList()
    if not foodPositions:
        return 0

    return min((
        util.manhattanDistance(position, perm[0]) +
            sum((util.manhattanDistance(perm[ii - 1], perm[ii])
                 for ii in xrange(1, len(perm))))
        for perm in permutations(foodPositions)
    ))

def farthestNFoodsManhattanHeuristic(state, problem, n):
    position, foodGrid = state
    foodPositions = sorted(
        foodGrid.asList(),
        key=lambda foodPosition: util.manhattanDistance(position, foodPosition)
    )[-n:]
    if not foodPositions:
        return 0

    return min((
        util.manhattanDistance(position, perm[0]) +
            sum((util.manhattanDistance(perm[ii - 1], perm[ii])
                 for ii in xrange(1, len(perm))))
        for perm in permutations(foodPositions)
    ))

def farthestNFoodsMazeManhattanHeuristic(state, problem, n):
    position, foodGrid = state
    foodPositions = sorted(
        foodGrid.asList(),
        key=lambda foodPosition: mazeDistance(position, foodPosition, problem.startingGameState)
    )[-n:]
    if not foodPositions:
        return 0

    return min((
        util.manhattanDistance(position, perm[0]) +
            sum((util.manhattanDistance(perm[ii - 1], perm[ii])
                 for ii in xrange(1, len(perm))))
        for perm in permutations(foodPositions)
    ))

def farthestFoodMazeHeuristic(state, problem):
    position, foodGrid = state
    foodPositions = foodGrid.asList()
    if not foodPositions:
        return 0

    return max((
        mazeDistance(position, foodPosition, problem.startingGameState)
        for foodPosition in foodPositions
    ))

def farthestNFoodsAStarFurthestFoodManhattanHeuristic(state, problem, n):
    position, foodGrid = state
    foodPositions = tuple(sorted(
        foodGrid.asList(),
        key=lambda foodPosition: util.manhattanDistance(position, foodPosition)
    )[-n:])
    if not foodPositions:
        return 0

    reducedProblem = ReducedFoodSearchProblem(position, foodPositions)
    return reducedProblem.getCostOfActions(search.aStarSearch(
        reducedProblem,
        reducedFarthestFoodManhattanHeuristic,
    ))

def reducedFarthestFoodManhattanHeuristic(state, problem):
    if not state[1]:
        return 0

    return min((
        util.manhattanDistance(state[0], foodPosition)
        for foodPosition in state[1]
    ))

class ReducedFoodSearchProblem:
    """
    A search problem associated with finding the a path that collects all of the
    food (dots) in a Pacman game, but with no walls.

    A search state in this problem is a tuple ( pacmanPosition, foodGrid ) where
      pacmanPosition: a tuple (x,y) of integers specifying Pacman's position
      foodPositions: a tuple of (x,y) tuples specifying the food's positions
    """
    def __init__(self, position, foodPositions):
        self.start = (position, foodPositions)

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return not state[1]

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost."
        position, foodPositions = state
        foodPositions = set(foodPositions)
        return tuple((
            ((foodPosition, tuple(foodPositions - set((foodPosition,)))), (position, foodPosition), util.manhattanDistance(position, foodPosition))
            for foodPosition in foodPositions
        ))

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        return sum((util.manhattanDistance(*action) for action in actions))

class ClosestDotSearchAgent(SearchAgent):
    "Search for all food using a sequence of searches"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception, 'findPathToClosestDot returned an illegal move: %s!\n%s' % t
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print 'Path found with cost %d.' % len(self.actions)

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)

        return search.bfs(problem)

def farthestIndividualFoodManhattanHeuristic(state, problem):
    position = state
    foodPositions = problem.food.asList()
    if not foodPositions:
        return 0

    return max((
        util.manhattanDistance(position, foodPosition)
        for foodPosition in foodPositions
    ))

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x, y = state
        return self.food[x][y]

def mazeDistance(point1, point2, gameState):
    """
    Returns the maze distance between any two points, using the search functions
    you have already built. The gameState can be any game state -- Pacman's
    position in that state is ignored.

    Example usage: mazeDistance( (2,4), (5,6), gameState)

    This might be a useful helper function for your ApproximateSearchAgent.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.aStarSearch(prob, heuristic=manhattanHeuristic))
