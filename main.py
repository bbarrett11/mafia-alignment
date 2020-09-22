import re,copy
from alignment import MafiaGame
from Formal import Formal
from Vote import Vote
from util import fixName
from colorama import Fore, Back, Style 

def parseGameFromFile(game, file):
    while True:
        input_line = file.readline().strip().split(" ")
        print(input_line)
        ret = 0
        if(input_line[0] == "end"):
            return 0

        # Submit votes to game
        if(input_line[0] == "vote"):
            on = fixName(input_line[1])
            yes_votes = [fixName(x) for x in file.readline().strip().split(" ")]
            if(re.match("all ",yes_votes[0])):
                yes_votes = [x for x in game.alive if x not in yes_votes]
            if(re.match("none",yes_votes[0])):
                yes_votes = []
            ret = game.recordVote(Vote(on=on.lower(),voters=yes_votes,alive=game.alive,day=game.vote_weight))

        # Submit confirmed info    
        elif(input_line[0] == "died"):
            playerName = fixName(input_line[1])
            ret = game.playerDied(playerName)
            if(len(input_line) > 2):
                if re.match("t.*",input_line[2]):
                    game.confirmTown(playerName)
                elif re.match("m.*",input_line[2]):
                    game.confirmMafia(playerName)

        elif(input_line[0] == "town"):
            ret = game.confirmTown(fixName(input_line[1]))
        elif(re.match("maf*",input_line[0])):
            ret = game.confirmMafia(fixName(input_line[1]))
        elif(input_line[0] == "formal"):
            if(len(input_line) < 3):
                print(f"Not enough names in formal declaration")
                return 1

            ret = game.recordFormal(Formal(on=fixName(input_line[1]),first=fixName(input_line[2]),second=None if len(input_line) < 4 else fixName(input_line[3])))

        # Set day/night cycle    
        elif(re.match("[dn]\d+",input_line[0])):
            ret = game.setDay(input_line[0])
                
        # Game is over.
        elif(re.match("reveal",input_line[0])):
            for i in range(1,len(input_line)):
                pass # Reveal mafia team
        print(ret)
        if ret == 1:
            return 1
    return 0


def mafiaUI(game_num=0):
    with open(f"games/game{game_num}.txt") as file:
        # Game setup: Numplayers NumMafia
        #             Player1
        #             Player2 ...
        first_line = file.readline().split(" ")
        num_players = int(first_line[0])
        num_mafia = int(first_line[1])
        players = [fixName(x) for x in file.readline().strip().split(" ")]
        
        if(len(players) != num_players):
            print("Incorrect starting number of players, please fix and reload")
            exit(1)
        
        print(players)
        game = MafiaGame(players=players,mafia=num_mafia)
        
        # load state of game from file
        parse_failure = False if parseGameFromFile(game, file) == 0 else True
        # End loading loop
        
        world = copy.deepcopy(game)
        if ( not parse_failure):
            world.calcAlignment()
        else:
            print("Please fix the issue in:",file.name)

    # Interactive shell to plan worlds
    while True:
        command = input("# ")
        cmd = command.strip().split(" ")
        # info on individual players
        if(re.match("i.*",cmd[0]) and len(cmd) > 1):
            world.getInfo(fixName(cmd[1]))
        # reset world calculation
        elif(re.match("res.*",cmd[0])):
            world = copy.deepcopy(game)
            world.calcAlignment()
        # Reload game from file
        elif(re.match("rel.*",cmd[0])):
            break
        # Closeness
        elif(re.match("c.*",cmd[0])):
            if(len(cmd)>1):
                world.getPartners(fixName(cmd[1]))
            else:
                world.getPartners()
        elif(re.match("exit",cmd[0])):
            exit(0)
            
        # Info on different worlds (confirm ppl either way)
        if(re.match("w.*",cmd[0])):
            world = copy.deepcopy(world)
            town_time = False
            maf_time = False
            temp_town = []
            temp_maf = []
            for word in cmd:
                if(re.match("-t.*",word)):
                    town_time = True
                    maf_time = False
                elif(re.match("-m.*",word)):
                    town_time = False
                    maf_time = True
                if(town_time and fixName(word) in game.players):
                    temp_town.append(fixName(word))
                    world.confirmTown(fixName(word))
                elif(maf_time and fixName(word) in game.players):
                    temp_maf.append(fixName(word))
                    world.confirmMafia(fixName(word))
            world.calcAlignment()
            
# For running UI
if __name__ == "__main__":
    game_num = int(input("Game: "))
    while True:
        mafiaUI(game_num)