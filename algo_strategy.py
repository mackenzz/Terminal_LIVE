import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replacement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.attack_parity = True
        self.attack_count = 2
    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # This is a good place to do initial setup
        self.scored_on_locations = []

    # Returns a score, where a higher score indicates more enemy units close by the path
    def get_cost_of_path(self, game_state, start_location):
        path = game_state.find_path_to_edge(start_location, game_state.game_map.TOP_LEFT)
        if path is None:
            return None

        score = 0
        THRESHOLD = 5

        for coord in path:
            for x in range(0, 28):
                for y in range(14, 28):
                    if game_state.game_map.in_arena_bounds([x,y]) and game_state.contains_stationary_unit([x,y]) and game_state.game_map.distance_between_locations(coord, [x,y]) < THRESHOLD:
                        score += 1
        return score

    def get_cost_of_path_2(self, game_state, start_location):
        path = game_state.find_path_to_edge(start_location, game_state.game_map.TOP_RIGHT)
        if path is None:
            return None

        score = 0
        THRESHOLD = 5

        for coord in path:
            for x in range(0, 28):
                for y in range(14, 28):
                    if game_state.game_map.in_arena_bounds([x,y]) and game_state.contains_stationary_unit([x,y]) and game_state.game_map.distance_between_locations(coord, [x,y]) < THRESHOLD:
                        score += 1
        return score

    def get_cost_of_path_op_left(self, game_state, start_location):
        path = game_state.find_path_to_edge(start_location, game_state.game_map.BOTTOM_LEFT)
        if path is None:
            return None, None

        score = 0
        THRESHOLD = 5

        for coord in path:
            for x in range(0, 28):
                for y in range(0, 14):
                    if game_state.game_map.in_arena_bounds([x,y]) and game_state.contains_stationary_unit([x,y]) and game_state.game_map.distance_between_locations(coord, [x,y]) < THRESHOLD:
                        score += 1

        return score, path[-1]

    def get_cost_of_path_op_right(self, game_state, start_location):
        path = game_state.find_path_to_edge(start_location, game_state.game_map.BOTTOM_RIGHT)
        if path is None:
            return None, None

        score = 0
        THRESHOLD = 5

        for coord in path:
            for x in range(0, 28):
                for y in range(0, 14):
                    if game_state.game_map.in_arena_bounds([x,y]) and game_state.contains_stationary_unit([x,y]) and game_state.game_map.distance_between_locations(coord, [x,y]) < THRESHOLD:
                        score += 1

        return score, path[-1]

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        Then build additional defenses.
        """
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)
        self.build_defences(game_state)

        """
        Finally deploy our information units to attack.
        """
        self.deploy_attackers(game_state)

    def build_defences(self, game_state):
        wall_pieces = [
                # Initial destructors (high priority)
                (DESTRUCTOR, (3, 11), (0, 1)), # type, position, priority (lower is better)
                (DESTRUCTOR, (9, 11), (0, 1)),
                (DESTRUCTOR, (14, 11), (0, 1)),
                (DESTRUCTOR, (19, 11), (0, 1)),
                (DESTRUCTOR, (24, 11), (0, 1)),

                # Edge guards (highest priority)
                (DESTRUCTOR, (0, 13), (0, 0)),
                (FILTER, (1, 12), (0, 0)),
                (FILTER, (27, 13), (0, 0)),
                (FILTER, (22, 12), (0, 0)),
                (FILTER, (23, 13), (0, 0)),
                (DESTRUCTOR, (23, 12), (0, 0)),

                # Initial side filters (high priority)
                (FILTER, (2, 11), (0, 2)),
                (FILTER, (8, 11), (0, 2)),
                (FILTER, (13, 11), (0, 2)),
                (FILTER, (15, 11), (0, 2)),
                (FILTER, (20, 11), (0, 2)),
                (FILTER, (21, 11), (0, 2)),
                (FILTER, (25, 11), (0, 2)),
                (FILTER, (26, 12), (0, 2)),
                (DESTRUCTOR, (27, 13), (0, 2)),
                (FILTER, (24, 12), (2, 0)),
                (FILTER, (25, 13), (2, 0)),
                (FILTER, (24, 13), (2, 0)),
                (FILTER, (4, 13), (2, 0)),

                # Secondary edge destructors
                (DESTRUCTOR, (5, 11), (1, 0)),
                (DESTRUCTOR, (22, 11), (1, 0)),

                # Secondary edge guards
                (FILTER, (23, 11), (1, 1)),
                (FILTER, (26, 12), (2, 0)),

                # Middle filters
                (FILTER, (7, 11), (1, 2)),
                (FILTER, (10, 11), (1, 2)),
                (DESTRUCTOR, (11, 11), (1, 2)),
                (FILTER, (12, 11), (1, 2)),
                (FILTER, (13, 11), (1, 2)),
                (FILTER, (15, 11), (1, 2)),
                (DESTRUCTOR, (16, 11), (1, 2)),
                (FILTER, (17, 11), (1, 2)),
                (FILTER, (18, 11), (1, 2)),
                (DESTRUCTOR, (17, 10), (1, 2)),
                (DESTRUCTOR, (18, 10), (1, 2)),
                (DESTRUCTOR, (19, 10), (1, 2)),
                (DESTRUCTOR, (20, 10), (1, 2)),

                # Encryptors
                (ENCRYPTOR, (8, 9), (1, 1)),
                (ENCRYPTOR, (5, 9), (2, 1)),
                (ENCRYPTOR, (6, 9), (2, 2)),
                (ENCRYPTOR, (7, 9), (2, 3)),
                (ENCRYPTOR, (3, 12), (3, 0)),

                # Left hole
                (DESTRUCTOR, (6, 11), (2, 0)),
                (DESTRUCTOR, (4, 9), (2, 1)),
                (DESTRUCTOR, (2, 12), (2, 1)),
                (DESTRUCTOR, (3, 10), (2, 1)),
                (DESTRUCTOR, (1, 13), (2, 0)),
                (DESTRUCTOR, (25, 12), (2, 0)),
                (DESTRUCTOR, (26, 13), (2, 0)),
                (FILTER, (2, 13), (2, 0)),
                (FILTER, (3, 13), (2, 0)),
                (FILTER, (4, 13), (2, 0)),
                (FILTER, (5, 13), (2, 2)),
                (FILTER, (6, 13), (2, 2)),
                (DESTRUCTOR, (7, 13), (2, 3)),
                (FILTER, (8, 13), (2, 3)),
                (FILTER, (9, 13), (2, 3)),
                (DESTRUCTOR, (10, 13), (2, 3)),
                (FILTER, (11, 13), (2, 3)),
                (FILTER, (12, 13), (2, 3)),
                (FILTER, (13, 13), (2, 3)),
                (FILTER, (14, 13), (2, 3)),
                (FILTER, (15, 13), (2, 3)),
                (DESTRUCTOR, (16, 13), (2, 3)),
                (FILTER, (17, 13), (2, 3)),
                (FILTER, (18, 13), (2, 3)),
                (FILTER, (19, 13), (2, 3)),
                (DESTRUCTOR, (20, 13), (2, 3)),
                (DESTRUCTOR, (9, 8), (2, 3)),
                (DESTRUCTOR, (10, 7), (2, 3)),
                (DESTRUCTOR, (11, 6), (2, 3)),
                (DESTRUCTOR, (12, 5), (2, 3)),
        ]
        wall_pieces.sort(key = lambda x: x[2])

        for (_type, location, _) in wall_pieces:
            if game_state.get_resource(game_state.CORES) < game_state.type_cost(_type):
                break

            if game_state.can_spawn(_type, location):
                game_state.attempt_spawn(_type, location)

    def deploy_attackers(self, game_state):
        if (game_state.get_resource(game_state.BITS) < 9):
            return

        locs = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        loc_costs = []
        locs2 = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
        loc_costs2 = []

        locs_left = game_state.game_map.get_edge_locations(game_state.game_map.TOP_LEFT)
        loc_costs_left = []

        locs_right = game_state.game_map.get_edge_locations(game_state.game_map.TOP_RIGHT)
        loc_costs_right = []

        for loc in locs:
            cost = self.get_cost_of_path(game_state, loc)
            if cost != None:
                loc_costs.append([loc, cost])

        for loc in locs2:
            cost = self.get_cost_of_path_2(game_state, loc)
            if cost != None:
                loc_costs2.append([loc, cost])

        for loc in locs_left:
            cost, coord = self.get_cost_of_path_op_right(game_state, loc)
            if cost != None:
                loc_costs_left.append([coord, cost])

        for loc in locs_right:
            cost, coord = self.get_cost_of_path_op_left(game_state, loc)
            if cost != None:
                loc_costs_right.append([coord, cost])

        loc_costs_all = loc_costs_right + loc_costs_left
        loc_costs = loc_costs + loc_costs2
        # if self.attack_parity:
        if not self.attack_parity:
            # To simplify we will just check sending them from back left and right
            #ping_spawn_location_options = [[13, 0], [14, 0]]
            #best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
            #game_state.attempt_spawn(PING, best_location, 1000)
            
            loc = min(loc_costs, key=lambda x: x[1])[0]
            while game_state.can_spawn(PING, loc):
                game_state.attempt_spawn(PING, loc)
        else:
            # if game_state.can_spawn(SCRAMBLER, [24, 10], 2):
            #     game_state.attempt_spawn(SCRAMBLER, [24, 10], 2)
            loc = max(loc_costs, key=lambda x: x[1])[0]
            while game_state.can_spawn(EMP, loc):
                game_state.attempt_spawn(EMP, loc)

        self.attack_parity = not self.attack_parity

        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        """
        Remove locations that are blocked by our own firewalls since we can't 
        deploy units there.
        """
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        """
        While we have remaining bits to spend lets send out scramblers randomly.
        """
        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(PING) and len(deploy_locations) > 0:
           
            """
            Choose a random deploy location.
            """
            # deploy_index = random.randint(0, len(deploy_locations) - 1)
            # deploy_location = deploy_locations[deploy_index]
            Em_deploy_location = min(loc_costs_all, key=lambda x: x[1])[0]

            all_loc = []
            for location in deploy_locations:
                dis = game_state.game_map.distance_between_locations(location, Em_deploy_location)
                all_loc.append([location, dis])
            deploy_location = min(all_loc, key=lambda x: x[1])[0]
            while game_state.can_spawn(PING, deploy_location):
                game_state.attempt_spawn(PING, deploy_location)
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """
    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]]
            while game_state.can_spawn(DESTRUCTOR, build_location):
                game_state.attempt_spawn(DESTRUCTOR, build_location)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]    
    
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location) and not location in [[17,3], [19,5], [18, 4]]:
                filtered.append(location)
        return filtered

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()