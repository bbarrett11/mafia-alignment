from alignment import MafiaGame
from Vote import Vote
from Formal import Formal
from util import fixName

class Harness:
    
    def testNames(self,name):
        name = fixName(name)
        return len(name) == 4
    
    def testVoteScore(self):
        players = [fixName(x) for x in ['p1','p2','p3','p4','p5']]
        game = MafiaGame(players=players,mafia=1)
        game.recordVote(Vote(on=players[0],voters=['p2  ','p3  '],alive=players,day=1))
        if(len(game.votes) == 0):
            return False
        
        vote = game.votes[0]
        
        print(game.getVoteGoodness(vote,'p1  '))
        print(game.getVoteGoodness(vote,'p2  '))
        print(game.getVoteGoodness(vote,'p4  '))
        print(game.players)
        
        return True
        
    def runTests(self):
        
        if(not self.testNames("hi") or not self.testNames("toobig")):
            print("testNames failed")
        
        if(not self.testVoteScore()):
            print("Vote score failed")


if __name__ == "__main__":
    #game_num = int(input("Game: "))
    Harness().runTests()