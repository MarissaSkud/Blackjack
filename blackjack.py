#Blackjack © 2019 Marissa Skudlarek

#Sources for blackjack rules: https://bicyclecards.com/how-to-play/blackjack/
#and http://www.vidpoker.com/blackjack/lasvegas/index.htm

#These sources say that different casinos can have different rules for splitting.
#(i.e. if you split and then receive ANOTHER pair upon splitting, can you split
#a second time?) In this implementation of blackjack, only a single split is 
#allowed.

#Another difference is whether the dealer should hit or stand on a soft 17 (Ace + 6).
#This game is implemented to stand on soft 17, as in many Vegas casinos.

from random import shuffle
from time import sleep

#Adding some sleep(1) statements makes this more fun, as a command-line game:
#it builds suspense and tension

SUITS = ["♠", "♥", "♦", "♣"]

RANKS_POINTS = {"A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, 
"9": 9, "10": 10, "J": 10, "Q": 10, "K": 10}

LIMIT = 21

class Card(object):
    '''A card in a deck of cards.'''

    def __init__(self, name, points):
        self.name = name
        self.points = points

    def __repr__(self):
        return self.name


class Deck(list):
    '''A stack of all cards.'''

    def __init__(self):
        '''Create and shuffle a new 52-card deck'''

        for suit in SUITS:
            for rank in RANKS_POINTS:
                new_card = Card(f"{rank}{suit}", RANKS_POINTS[rank])
                self.append(new_card)

        shuffle(self)

    def deal(self):
        '''Deal 1 card from the end of the deck'''

        return self.pop()


class Hand(list):
    '''A small collection of cards belonging to a player.'''

    def __init__(self):
        self.value = 0
        self.blackjack = False

    def add_card(self, card):
        '''Add card to hand and update hand's point value. Treat Aces as value 1 
        instead of 11 if it will prevent hand from going bust.'''

        self.append(card)

        if card.name.startswith("A") and self.value > 10:
            card.points = 1

        self.value += card.points
        return self.value

    def check_blackjack(self):
        '''Determine if hand is a natural blackjack'''

        self.blackjack = ((len(self) == 2) and self.value == LIMIT)

    def reset_ace_value(self):
        '''If hand value >21 and it contains an ace, reset its value from 11 to 1
        to prevent going bust.'''

        if self.value > LIMIT:
            for card in self:
                if card.name.startswith("A") and card.points == 11:
                    card.points = 1
                    self.value -= 10

        return self.value

    def draw_card(self, deck):
        '''Give an additional card to a hand and recalculate hand value'''

        new_card = deck.deal()
        self.add_card(new_card)
        self.reset_ace_value()
        print(f"This hand draws a {new_card}. Its value is now {self.value}.")


class Player(object):
    '''A person playing blackjack.'''

    def __init__(self, name):
        self.name = name
        self.money = 1000
        self.cashout = False

    def __repr__(self):
        return self.name

    def make_bet(self):
        '''Ask player to make a bet for the round'''

        print(f"{self.name}, you have ${self.money} to wager.")
        while True:
            wager = int(input("How much do you wager for this round? "))
            if not validate_wager(wager, self.money):
                continue
            else:
                self.wager = wager
                self.money -= self.wager
                break

    def reveal_initial_hand(self):
        '''Display player's initial 2-card hand and determine if it is blackjack'''

        print(f"{self.name}, your hand is {self.hand}. Its value is {self.hand.value}.")
        self.hand.check_blackjack()
        if self.hand.blackjack:
            print("This is a natural blackjack! You will win unless the dealer also has a natural blackjack.")
        sleep(1)

    def split_hand(self, deck):
        '''Split a pair of cards into 2 new 2-card hands and arrange 2nd wager'''

        split_card = self.hand.pop()
        self.hand.value -= split_card.points

        if split_card.name.startswith("A"):
            split_card.points = 11
        
        self.second_hand = Hand()
        self.second_hand.add_card(split_card)
        self.hand.add_card(deck.deal())
        self.second_hand.add_card(deck.deal())
        self.second_wager = self.wager
        self.money -= self.second_wager
        print(f"Your new hands are {self.hand} and {self.second_hand}.")

    def cash_out(self):
        '''Allow player to exit the game'''

        print(f"{self.name}, you are cashing out with ${self.money}.")

        if self.money > 1000:
            profit = self.money - 1000
            print(f"You won ${profit} this game!")

        self.cashout = True


class Dealer(object):
    '''The 'house' who the players are trying to beat.'''

    def __init__(self):
        self.name = "Dealer"

    def __repr__(self):
        return self.name

    def reveal_faceup(self):
        '''Display dealer's faceup card'''

        faceup = self.hand[-1]
        print(f"The dealer's faceup card is {faceup}. Their other card is facedown.")
        return faceup


def instantiate_players(player_count, players):
    '''Create the required number of new Player objects and add them to list of players'''

    for i in range (0, player_count):
        name = input(f"What is Player {i+1}'s name? ")
        new_player = Player(name)
        players.append(new_player)


def reset_for_new_round(players, dealer):
    '''Reset all hands to empty and wagers to 0 before new round'''

    for player in players:
        player.hand = Hand()
        player.wager = 0
        player.stand = False
        player.second_hand = None
        player.second_wager = None

    dealer.hand = Hand()


def validate_wager(wager, maximum):
    '''Check to make sure player isn't wagering more money than they have'''

    if wager > maximum:
        print(f"You cannot wager that much. The most you can wager is ${maximum}.")
        return False

    return True


def deal_hands(deck, players, dealer):
    '''Deal 2 cards to each player and to the dealer'''

    for i in range(0, 2):
        for player in players:
            player.hand.add_card(deck.deal())
        dealer.hand.add_card(deck.deal())


def payout_natural_blackjacks(players):
    '''If player has natural blackjack & dealer does not, pay that player right away'''

    for player in players:
        if player.hand.blackjack:   
            winnings = player.wager + int(1.5 * player.wager)
            player.money += winnings
            print(f"{player.name}, you have won 1.5 times your wager of ${player.wager} and now have ${player.money}.")
            print("Play will continue for any remaining players.")


def handle_dealer_blackjack(dealer, players):
    '''If dealer has natural blackjack, compare it to player hands'''

    print(f"The dealer's hand is {dealer.hand} -- a natural blackjack.")
    sleep(1)

    for player in players:
        if player.hand.blackjack:
            print(f"{player.name}, your blackjack ties the dealer's blackjack.")
            player.money += player.wager
            print(f"You win back your wager of ${player.wager} and have ${player.money} again.")
        else:
            player.stand = True
            print(f"{player.name}, the dealer's blackjack beats your hand. Your bet of ${player.wager} is forfeit.")
        sleep(1)

    print("The round is over.")


def double_down(player, hand, deck, wager):
    '''Add money to bet & draw additional card for a double-down'''

    max_wager = min(wager, player.money)

    while True:
        additional_wager = int(input(f"How much more would you like to wager? It can be up to ${max_wager}. "))
        if not validate_wager(additional_wager, max_wager):
            continue
        else:
            wager += additional_wager
            player.money -= additional_wager
            hand.draw_card(deck)
            player.stand = True
            break

    return wager

#I can't figure out why "wager += additional_wager" does not update player.wager when 
#player.wager gets passed in as the "wager" argument. But that's what was happening, and it
#made the winnings total come out wrong. Having the double_down function "return wager"
#and then using that to re-set player.wager / player.second_wager later on 
#is a hacky way of solving this, but at least it's solved.


def payout_hand(player, player_hand, player_wager):
    '''Calculate winnings on a single winning hand'''

    winnings = 2*player_wager
    player.money += winnings
    print(f"{player.name}, your hand {player_hand} has won ${winnings}.")


def payout_after_dealer_bust(players):
    '''For-loop to dispense winnings for all remaining hands if dealer has gone bust'''

    print("The dealer's hand is bust! All remaining players win this round.")

    for player in players:
        if player.stand:
            if player.hand.value <= LIMIT:
               payout_hand(player, player.hand, player.wager)

            if player.second_hand:
                if player.second_hand.value <= LIMIT:
                    payout_hand(player, player.second_hand, player.second_wager)

            print(f"You now have ${player.money}.")
            sleep(1)


def compare_hand(player, player_hand, dealer_hand, player_wager):
    '''Compare a single hand to the dealer's final hand'''

    if dealer_hand.value > player_hand.value:
        print(f"{player.name}, the dealer's hand beats your hand {player_hand}.")
        print(f"Your bet is forfeit. You now have ${player.money}.")

    elif dealer_hand.value == player_hand.value:
        print(f"{player.name}, your hand {player_hand} has tied the dealer.")
        player.money += player_wager
        print(f"We are returning your ${player_wager} bet to you. You have ${player.money} again.")

    else:
        payout_hand(player, player_hand, player_wager)
        print(f"You now have ${player.money}.")


def compare_multiple_hands(players, dealer):
    '''For-loop to compare all remaining hands to dealer's final hand'''

    for player in players:
        if player.stand:
            if player.hand.value <= LIMIT:
                compare_hand(player, player.hand, dealer.hand, player.wager)

            if player.second_hand:
                if player.second_hand.value <= LIMIT:
                    compare_hand(player, player.second_hand, dealer.hand, player.second_wager) 

            sleep(1)


def resolve_dealer_hand(deck, dealer, players):
    '''Reveal dealer's hand, draw additional cards if its value is less than 17,
    then compare it to hands of remaining players'''

    print(f"The dealer's hand is {dealer.hand}. Its value is {dealer.hand.value}.")
    sleep(1)

    while dealer.hand.value < 17:
        dealer.hand.draw_card(deck)
        sleep(1)

    if dealer.hand.value > LIMIT:
        payout_after_dealer_bust(players)

    else:
        #This will get called only if 17 <= dealer.hand.value <= 21
        compare_multiple_hands(players, dealer)


def remove_bankrupt_players(players):
    '''Take player(s) out of the game if they have no money at the end of a round.'''

    for player in players:
        if player.money == 0:
            print(f"{player.name}, you have lost all your money and will need to leave the game.")

    players[:] = [player for player in players if not player.money == 0]

    #Doing this as a list comprehension with list slice to avert the bug that occurred
    #if 2 or more players went bankrupt in the same round.


def ask_to_continue(players):
    '''Ask if each player wants to play another round; remove players who quit'''

    for player in players:
        while True:
            again = input(f"{player.name}, do you want to play again? Y/N ")
            if again.upper() == "Y":
                break
            elif again.upper() == "N":
                player.cash_out()
                break
            else:
                print("Input not valid, try again")
                continue

    players[:] = [player for player in players if not player.cashout]


def play_game():
    '''Function to run the entire blackjack game'''

    print("Welcome to Blackjack!")

    players = []
    dealer = Dealer()

    #Vegas blackjack tables typically have a 7-person maximum so our game will as well.
    #This also helps ensure that a single deck per round will suffice.
    while True:
        player_count = int(input("How many people are playing? "))
        if player_count < 8:
            instantiate_players(player_count, players)
            break
        else:
            print("This blackjack table has a 7-player maximum.")
            continue

    #This while loop runs a single round of Blackjack.
    while players:
        reset_for_new_round(players, dealer)
        game_deck = Deck()

        #Each round uses a freshly shuffled deck. With this and the 7-player limit,
        #it means the deck is unlikely to ever get exhausted.

        for player in players:
            player.make_bet()

        deal_hands(game_deck, players, dealer)

        for player in players:
            player.reveal_initial_hand()

        faceup = dealer.reveal_faceup()

        if faceup.points == 10 or faceup.name.startswith("A"):
        #If-statement was originally written to check if faceup.points == 10 or 11, but
        #this resulted in a bug when dealer's hand contained two Aces (and the 2nd Ace
        #therefore had had its value reset to 1).

            print(f"Therefore, the dealer must check to see if they have a natural blackjack.")
            dealer.hand.check_blackjack()
            sleep(1)

            if dealer.hand.blackjack == True:
                handle_dealer_blackjack(dealer, players)
            else:
                print("The dealer's hand is not a blackjack.")
                payout_natural_blackjacks(players)
        else:
            print("It is impossible for the dealer to have a natural blackjack.")
            payout_natural_blackjacks(players)

        sleep(1)

        #This for-loop allows each of the remaining players to hit, stand, or double down in turn.

        for player in players:
            if player.hand.blackjack == False and player.stand == False:
                while player.hand.value < LIMIT:

                    print(f"{player.name}, your hand is currently worth {player.hand.value}.")

                    #Allows player to split if and only if they were initally dealt a pair, 
                    #and if they have sufficient money to double their bet.
                    if (len(player.hand) == 2 and player.hand[0].name[0] == player.hand[1].name[0] 
                    and player.second_hand == None and player.money >= player.wager):
                        choice = input("Do you want to [H]it, [S]tand, s[P]lit, or [D]ouble Down? ")
                        valid_choices = {"H", "S", "D", "P"}

                        if choice.upper() not in valid_choices:
                            print("Choice not recognized, try again")

                        #Splits pair (if desired) and handles special case of splitting a pair of aces.
                        if choice.upper() == "P":
                            player.split_hand(game_deck)
                            if player.hand[0].name.startswith("A") and player.second_hand[0].name.startswith("A"):
                                print("Because you split a pair of aces, you will get no more cards. Both these hands stand.")
                                player.stand = True
                                break

                    else:
                        choice = input("Do you want to [H]it, [S]tand, or [D]ouble Down? ")
                        valid_choices = {"H", "S", "D"}
                        if choice.upper() not in valid_choices:
                            print("Choice not recognized, try again")

                    if choice.upper() == "H":
                        player.hand.draw_card(game_deck)

                    elif choice.upper() == "S":
                        player.stand = True
                        break

                    elif choice.upper() == "D":
                        wager = double_down(player, player.hand, game_deck, player.wager)
                        player.wager = wager
                        break

                if player.hand.value == LIMIT:
                    player.stand = True

                if player.hand.value > LIMIT:
                    print(f"This hand is bust, your ${player.wager} bet is forfeit.")
                    player.stand = False

                #Allows player to hit, stand or double-down on their second (split) hand,
                #as long as the split was not of a pair of aces.
                if player.second_hand:
                    if not player.second_hand[0].name.startswith("A"):
                        while player.second_hand.value < LIMIT:
                            print(f"{player.name}, your second hand is currently worth {player.second_hand.value}.")

                            choice = input("Do you want to [H]it, [S]tand, or [D]ouble Down? ")
                            valid_choices = {"H", "S", "D"}
                            if choice.upper() not in valid_choices:
                                print("Choice not recognized, try again")

                            if choice.upper() == "H":
                                player.second_hand.draw_card(game_deck)

                            elif choice.upper() == "S":
                                player.stand = True
                                break

                            elif choice.upper() == "D":
                                wager = double_down(player, player.second_hand, game_deck, player.second_wager)
                                player.second_wager = wager
                                break

                        if player.second_hand.value == LIMIT:
                            player.stand = True

                        if player.second_hand.value > LIMIT:
                            print(f"This hand is bust, your ${player.second_wager} bet is forfeit.")
                            if not player.stand == True:
                                player.stand = False

        sleep(1)

        for player in players:
            if player.stand and not dealer.hand.blackjack:
                resolve_dealer_hand(game_deck, dealer, players)
                break

        remove_bankrupt_players(players)

        if not players:
            print("All players have gone bankrupt, the game is over.")
        else:
            ask_to_continue(players)

    print("There are no more players, goodbye!")
        

if __name__ == "__main__":       
    play_game()  

# TO DO (things I would have implemented with additional time):

# 1. If hand is "soft" (contains an ace) it would be nice to make sure the player
# realizes that. Right now, if player has [A, 7] it will say "Your hand's value
# is 18" not "Your hand's value is 18 or 8"

# 2. I realize it's confusing to have both add_card and draw_card methods on the
# Hand class. Could probably take some time to re-factor and clean that up.

# 3. The implementation of splitting/allowing for a second hand is pretty hacky
#and involves basically writing the same code twice (for hand 1 and hand 2).
#There is probably a better way to do this that involves more elegant use of
#functions and looping.