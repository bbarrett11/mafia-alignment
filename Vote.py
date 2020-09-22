import copy

class Vote:
    DAY_VOTE_RELAVENCE = 0.75
    def __init__(self,on="",voters=[],alive=[],day=0):
        self.voters = voters
        self.alive = copy.copy(alive)
        self.on = on
        self.day = day
    def describe(self, player=None):
        if player == self.on:
            return "Voted on by "+" ".join(self.voters)
        elif player in self.voters:
            return "Voted on " + str(self.on) + " with " + str(self.voters)
        else:
            return "No-Voted "+ str(self.on) + " with " + str([x for x in self.alive if x not in self.voters])
    def getWeight(self):
        return self.day*self.day*self.DAY_VOTE_RELAVENCE
