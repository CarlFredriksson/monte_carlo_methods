import numpy as np
from enum import Enum

# TODO: Maybe change to the real version of blackjack
# Book version has draws that give 0, in real blackjack the dealer win on draws.
# In real blackjack, player win immediately on 21?
# Dealer doesn't automatically stop on 17 when player has more than 17?

class Action(Enum):
    HIT = 1
    STICK = 2

class State:
    def __init__(self, player_sum, usable_ace, dealer_showing):
        self.player_sum = player_sum
        self.usable_ace = usable_ace
        self.dealer_showing = dealer_showing
    
    def print(self):
        print("player_sum: {}, usable_ace: {}, dealer_showing: {}".format(
            self.player_sum, self.usable_ace, self.dealer_showing))

class Environment:
    def __init__(self):
        self.state = State(0, False, self.draw_card())
        while self.state.player_sum <= 11:
            self.take_action(Action.HIT)

    def draw_card(self):
        cards = np.arange(10) + 1
        probabilities = np.append(np.ones(9)/13, 4/13)
        return np.random.choice(cards, p=probabilities)

    def take_action(self, action):
        if action == Action.HIT:
            # Get new card
            card = self.draw_card()
            print("Player draws:", card)
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
        
        while self.state.dealer_showing < 17:
            # Dealer get new card
            card = self.draw_card()
            print("Dealer draws:", card)
            if card == 1: # Ace worth 1 or 11
                if self.state.dealer_showing <= 10:
                    self.state.dealer_showing += 11
                    dealer_usable_ace = True
                else:
                    self.state.dealer_showing += 1
            else:
                self.state.dealer_showing += card

            # Check if dealer busted or needs to use an ace as 1
            if self.state.dealer_showing > 21:
                if dealer_usable_ace:
                    self.state.dealer_showing -= 10
                    dealer_usable_ace = False
                else: # Dealer busted
                    return 1
        
        # Round is over
        if self.state.dealer_showing > self.state.player_sum:
            return -1
        elif self.state.dealer_showing < self.state.player_sum:
            return 1
        return 0

#class Agent:

