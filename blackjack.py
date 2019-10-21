import numpy as np
from enum import Enum
from copy import copy

# TODO: Maybe change to the real version of blackjack
# Book version has draws that give 0, in real blackjack the dealer win on draws.
# In real blackjack, player win immediately on 21?
# Dealer doesn't automatically stop on 17 when player has more than 17?

class Action(Enum):
    HIT = 0
    STICK = 1

class State:
    def __init__(self, player_sum, usable_ace, dealer_showing):
        self.player_sum = player_sum
        self.usable_ace = usable_ace
        self.dealer_showing = dealer_showing
    
    def to_string(self):
        return "player_sum: {}, usable_ace: {}, dealer_showing: {}".format(
            self.player_sum, self.usable_ace, self.dealer_showing)

class Environment:
    def __init__(self, starting_state):
        self.state = starting_state

    def draw_card(self):
        cards = np.arange(10) + 1
        probabilities = np.append(np.ones(9)/13, 4/13)
        return np.random.choice(cards, p=probabilities)

    def take_action(self, action):
        if action == Action.HIT:
            # Get new card
            card = self.draw_card()
            if card == 1: # Ace worth 1 or 11
                if self.state.player_sum <= 10:
                    self.state.player_sum += 11
                    self.state.usable_ace = True
                else:
                    self.state.player_sum += 1
            else:
                self.state.player_sum += card

            # Check if player busted or needs to use an ace as 1
            if self.state.player_sum > 21:
                if self.state.usable_ace:
                    self.state.player_sum -= 10
                    self.state.usable_ace = False
                else: # Player busted
                    return -1
            return None
        
        # Player sticks, dealer now acts
        dealer_usable_ace = self.state.dealer_showing == 1
        dealer_sum = 11 if dealer_usable_ace else self.state.dealer_showing
        
        while dealer_sum < 17:
            # Dealer get new card
            card = self.draw_card()
            if card == 1: # Ace worth 1 or 11
                if dealer_sum <= 10:
                    dealer_sum += 11
                    dealer_usable_ace = True
                else:
                    dealer_sum += 1
            else:
                dealer_sum += card

            # Check if dealer busted or needs to use an ace as 1
            if dealer_sum > 21:
                if dealer_usable_ace:
                    dealer_sum -= 10
                    dealer_usable_ace = False
                else: # Dealer busted
                    return 1
        
        # Round is over
        if dealer_sum > self.state.player_sum:
            return -1
        elif dealer_sum < self.state.player_sum:
            return 1
        return 0

class Agent:
    # The policy is a deterministic mapping from state to action: 0 = HIT, 1 = STICK
    # Init policy to only stick on 20 and 21
    policy = np.zeros((2, 10, 10))
    policy[:, 8:10, :] = 1
    action_values = np.zeros((2, 10, 10, 2))
    num_visits = np.zeros(np.shape(action_values))

    def run_episode(self, environment, starting_action):
        history = []
        reward = None

        # Generate episode
        #print("Starting state:", environment.state.to_string())
        history.append((copy(environment.state), starting_action))
        reward = environment.take_action(starting_action)
        while reward is None:
            i = 0 if environment.state.usable_ace else 1
            j = environment.state.player_sum - 12
            k = environment.state.dealer_showing - 1
            action = Action(self.policy[i, j, k])
            #print("action:", action)
            history.append((copy(environment.state), action))
            reward = environment.take_action(action)
            #print("state:", environment.state.to_string())
            #print("reward:", reward)

        # Use episode history to update state-values
        #print("History:")
        for state, action in history:
            #print("state: ({}), action: {}, reward: {}".format(state.to_string(), action, reward))
            i = 0 if state.usable_ace else 1
            j = state.player_sum - 12
            k = state.dealer_showing - 1
            l = action.value
            self.num_visits[i, j, k, l] += 1
            self.action_values[i, j, k, l] += (reward - self.action_values[i, j, k, l]) / self.num_visits[i, j, k, l]
            #print("usable_ace=True, action=HIT")
            #print(self.action_values[0,:,:,0])
            #print("usable_ace=False, action=HIT")
            #print(self.action_values[1,:,:,0])
            #print("usable_ace=True, action=STICK")
            #print(self.action_values[0,:,:,1])
            #print("usable_ace=False, action=STICK")
            #print(self.action_values[1,:,:,1])
            self.policy[i, j, k] = 0 if self.action_values[i, j, k, 0] > self.action_values[i, j, k, 1] else 1

if __name__ == "__main__":
    NUM_EPISODES = 500000
    agent = Agent()

    for episode in range(NUM_EPISODES):
        if episode % 1000 == 0:
            print("STARTING EPISODE:", str(episode))
        random_starting_state = State(
            np.random.randint(12, high=22),
            True if np.random.randint(2) == 0 else False,
            np.random.randint(1, high=11)
        )
        environment = Environment(random_starting_state)
        random_starting_action = Action(np.random.randint(2))
        agent.run_episode(environment, random_starting_action)
    np.set_printoptions(precision=1)
    np.set_printoptions(suppress=True)
    print("Num visited for HIT")
    print(agent.num_visits[:,:,:,0])
    print("Num visited for STICK")
    print(agent.num_visits[:,:,:,1])
    print("Action values for HIT")
    print(agent.action_values[:,:,:,0])
    print("Action values for STICK")
    print(agent.action_values[:,:,:,1])
    print("Policy")
    print(agent.policy)

"""
class Agent:
    state_values = np.zeros((2, 10, 10))
    num_visits = np.zeros(np.shape(state_values))

    def run_episode(self, environment):
        history = []
        reward = None

        # Generate episode
        while reward is None:
            action = Action.HIT if environment.state.player_sum <= 19 else Action.STICK
            history.append((copy(environment.state), action))
            reward = environment.take_action(action)

        # Use episode history to update state-values
        for state, action in history:
            i = 0 if state.usable_ace else 1
            j = state.player_sum - 12
            k = state.dealer_showing - 1
            self.num_visits[i, j, k] += 1
            self.state_values[i, j, k] += (reward - self.state_values[i, j, k]) / self.num_visits[i, j, k]

if __name__ == "__main__":
    NUM_EPISODES = 100000
    agent = Agent()

    for episode in range(NUM_EPISODES):
        if episode % 1000 == 0:
            print("STARTING EPISODE:", str(episode))
        environment = Environment()
        agent.run_episode(environment)
    np.set_printoptions(precision=1)
    np.set_printoptions(suppress=True)
    print(agent.state_values)
"""
