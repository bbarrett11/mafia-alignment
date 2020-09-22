import re,copy, math
from Formal import Formal
from Vote import Vote
from util import fixName

class MafiaGame:
    def __init__(self, players=["No players entered"],votes=[],mafia=3):
        # Connections
        self.vote_together = 1
        self.no_vote_together = 1
        self.vote_on = 0
        self.no_vote_on = 1
        
        # Town score
        self.vote_weight = 1
        #self.no_vote_weight = 1
        #self.no_vote_together_with_town = 1.5
        #self.no_vote_together_with_mafia = 0
        #self.vote_on_town = 0
        #self.vote_on_mafia = 2.5
        #self.no_vote_on_town = 1.25
        #self.no_vote_on_mafia = 0
        
        # Misc vars
        self.num_mafia = mafia
        self.players = players.copy()
        self.alive = players.copy()
        self.confirmed_town = []
        self.confirmed_mafia = []
        self.num_players = len(players)
        self.num_votes = 0 if votes == None else len(votes)
        self.votes = votes
        
        # Closeness of each player in terms of voting
        self.closeness_pairs = []
        
        # Formals
        self.formals = []
        
        # Actions of each player for easy lookup
        self.player_actions = {}
        for player in self.players:
            self.player_actions[player] = {}
        self.mafia_scores = [0]*len(players)
        self.max_mafia_scores = [0]*len(players)
        
        # Set time to n0 intitially
        self.setDay("n0")
        
    def calcAlignment(self):
        self.closeness_pairs = []
        self.max_closeness_pairs = []
        self.mafia_scores = [0]*len(self.players)
        self.max_mafia_scores = [0]*len(self.players)
            
        # Create 2D map, for connections between players
        # +.5 same no votes
        # +1 same votes
        # -1 vote on player
        for player in self.players:
            self.closeness_pairs.append([0]*self.num_players)
            self.max_closeness_pairs.append([0]*self.num_players)
        
        for vote in self.votes:
            # voting/no-voting together
            for player in vote.alive:
                # Voters
                if player in vote.voters:
                    for other_player in vote.alive:
                        if other_player == player:
                            continue
                        elif other_player in vote.voters:
                            self.closeness_pairs[self.players.index(player)][self.players.index(other_player)]+=self.vote_together
                        self.max_closeness_pairs[self.players.index(player)][self.players.index(other_player)]+=self.vote_together
                # No-Voters
                else:
                    for other_player in vote.alive:
                        if other_player == player:
                            continue
                        elif other_player not in vote.voters:
                            self.closeness_pairs[self.players.index(player)][self.players.index(other_player)]+=self.no_vote_together
                        self.max_closeness_pairs[self.players.index(player)][self.players.index(other_player)]+=self.no_vote_together

            
            # voting/no-voting on
            for player in vote.alive:
                if player == vote.on:
                    continue
                if player in vote.voters:
                    self.closeness_pairs[self.players.index(player)][self.players.index(vote.on)] += self.vote_on
                else:
                    self.closeness_pairs[self.players.index(player)][self.players.index(vote.on)] += self.no_vote_on
                # Most aligned action
                self.max_closeness_pairs[self.players.index(player)][self.players.index(vote.on)] += self.no_vote_on
                

            # no-voting together

            # Town scoring based on votes/no-votes
            for player in vote.alive:
                self.mafia_scores[self.players.index(player)]+=self.getVoteGoodness(vote,player)*vote.getWeight()
                self.max_mafia_scores[self.players.index(player)]+=vote.getWeight()

            # Confirmed
            for player in self.players:
                if(player in self.confirmed_town or player in self.confirmed_mafia):
                    self.mafia_scores[self.players.index(player)]=0
        # Printing/Formatting
        print(self.mafia_scores)  
        # Connection grid
        print("     ",end="")
        for player in self.alive:
            print("%s " % (player),end="")
        print("")
        for player in self.alive:
            print("%s "%(player),end="")
            for other_player in self.alive:
                local_max = self.max_closeness_pairs[self.players.index(player)][self.players.index(other_player)]
                closeness = self.closeness_pairs[self.players.index(player)][self.players.index(other_player)] / (1 if local_max == 0 else local_max) 
                print("%4.1f "%(closeness),end="")
            print("")
        # Town score:
        maf_maxes = [1 if x <= 0 else x for x in self.max_mafia_scores]
        print(maf_maxes)
        print("   ",end="")
        for player in self.alive:
            print("%s " % (player),end="")
        print("")
        print("   ",end="")
        for player in self.alive:
            if player in self.confirmed_mafia:
                print("mafi ",end="")
            elif player in self.confirmed_town:
                print("town ",end="")
            else:
                maf_float = self.mafia_scores[self.players.index(player)]/maf_maxes[self.players.index(player)]
                print("%4.1f "%(maf_float),end="")
        print("")
        print("(dead)")
        print("   ",end="")
        for player in self.players:
            if player in self.alive:
                continue
            print("%s " % (player),end="")
        print("")
        print("   ",end="")
        for player in self.players:
            if player in self.alive:
                continue
            if player in self.confirmed_mafia:
                print("mafi ",end="")
            elif player in self.confirmed_town:
                print("town ",end="")
            else:
                maf_float = self.mafia_scores[self.players.index(player)]/maf_maxes[self.players.index(player)]
                print("%4.1f "%(maf_float),end="")
        print("")

        print("There are %d alive"%(len(self.alive)))
        
        print(f"There are at most {self.getCertainNumMafia()} mafia alive")

    def setDay(self, day="n0"):
        self.day = day
        #TODO 2 digit days
        if(re.match("d\d+",day)):
            self.vote_weight=int(day[1:])
        elif(re.match("n\d+",day)):
            pass # nothing special about night
        else:
            print("Invalid date")
            return 1
        for player in self.players:
            self.player_actions[player][self.day] = []
        
    def confirmTown(self,player=None):
        if(player not in self.players):
            print("This player does not exist: %s" % player)
            return 1
        self.confirmed_town.append(player)
        self.player_actions[player][self.day].append("confirmed town")

    def confirmMafia(self, player=None):
        if(player not in self.players):
            print("This player does not exist: %s" % player)
            return 1
        self.confirmed_mafia.append(player)
        self.player_actions[player][self.day].append("confirmed mafia")
    
    def getVoteGoodness(self, vote, player):
        partial_credit = 0
        num_others = len(vote.alive)-1
        # Votee
        # TODO : increase size based on total number of voters
        if vote.on == player:
            for other_player in vote.voters:
                if other_player in self.confirmed_town:
                    partial_credit-=1
                elif other_player in self.confirmed_mafia:
                    partial_credit+=1
                else:
                    partial_credit+=0.5
            together = [item for item in vote.alive if item not in vote.voters] 
            for other_player in together:
                if other_player == player:
                    continue
                if other_player in self.confirmed_town:
                    partial_credit+=1
                elif other_player in self.confirmed_mafia:
                    partial_credit-=1
                else:
                    partial_credit+=0.5
            return partial_credit/(num_others)

        # If votee is confirmed, immediatly return value (correctness of decision)
        if vote.on in self.confirmed_town:
            return 0 if player in vote.voters else 1
        elif vote.on in self.confirmed_mafia:
            return 0 if player not in vote.voters else 1
        
        # If votee is not confirmed, do percentage based on
        # Number of confirmed players with/against the voter
        else:
            if player in vote.voters:
                team = vote.voters
            else:
                team = [item for item in vote.alive if item not in vote.voters]
            for other_player in team:
                if other_player == player:
                    continue
                if other_player in self.confirmed_town:
                    partial_credit+=1
                elif other_player in self.confirmed_mafia:
                    partial_credit+=0
                else:
                    partial_credit+=0.5
            
            other_team = [item for item in vote.alive if item not in team]
            for other_player in other_team:
                if other_player == player:
                    continue
                if other_player in self.confirmed_town:
                    partial_credit+=0
                elif other_player in self.confirmed_mafia:
                    partial_credit+=1
                else:
                    partial_credit+=0.5
        return partial_credit/num_others

    def getCertainNumMafia(self):
        return min(self.num_mafia-len(self.confirmed_mafia),math.ceil(len(self.alive)/2-1))
    
    def getLikelyNumMafia(self):
        return self.num_mafia-len(self.confirmed_mafia)
    
    def playerDied(self,player=None):
        if(player not in self.alive):
            print("That player is not alive already: %s" % player)
            return 1
        self.alive.remove(player)
        self.player_actions[player][self.day].append("died")
        
    def recordVote(self,vote=None):
        if (vote == None):
            return 1
        # Check vote
        for alive in vote.alive:
            if(alive not in self.alive):
                print(f"Alive player {alive} is not actually alive")
                return 1
        for voter in vote.voters:
            if(voter not in self.alive):
                print(f"Voter {voter} is not actually alive")
                return 1
        if(vote.on not in self.alive):
            print(f"Votee {alive} is not alive")
            return 1
        self.votes.append(vote)
        for player in self.alive:
            self.player_actions[player][self.day].append(vote)

    # Record and submit formal.
    # Currently doesn't effect town score
    def recordFormal(self,formal=None):
        if(formal.on not in self.alive or
           formal.first not in self.alive or
           (formal.second != None and formal.second not in self.alive)):
            print("Formal player not alive: ",formal.on, formal.first, formal.second)
            return 1
        self.formals.append(formal)
        self.player_actions[formal.on][self.day].append(formal)
        # Formaler
        if(formal.first != None):
            self.player_actions[formal.first][self.day].append(formal)
        # Seconder
        if(formal.second != None):
            self.player_actions[formal.second][self.day].append(formal)
        
    def getInfo(self, player=None):
        if(player not in self.players):
            print("Player DNE")
            return
        print("Info on %s:" % player)
        for phase in self.player_actions[player].keys():
            print(phase+":")
            for action in self.player_actions[player][phase]:
                if type(action) == str:
                    print("\t%s"%action)
                elif type(action) == Vote:
                    print("\t%s %f"%(action.describe(player),self.getVoteGoodness(action,player)) )
                elif type(action) == Formal:
                    print("\t%s "%(action.describe(player)))
                    
    def getPartners(self, player=None):
        # Get global max to find outliers
        max_close = max([max(x) for x in self.closeness_pairs])
        view_percentile_top = .9
        view_percentile_bot = .1
        player_list = self.alive
        if(player != None):
            player_list = [player]
        singles = []
        for player in player_list:
            i = self.players.index(player)
            player_align = self.closeness_pairs[i]
            local_max = max(player_align)
            for (j,closeness) in enumerate(player_align):
                # Player's relation to themself is useless
                if j== i:
                    continue
                if closeness >= local_max*view_percentile_top:
                    print(f"{self.players[i]} -> {self.players[j]}")
                    
                elif closeness <= local_max*view_percentile_bot:
                    print(f"{self.players[i]} -/> {self.players[j]}")
