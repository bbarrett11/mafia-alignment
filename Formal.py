class Formal:
    def __init__(self,on=None,first=None,second=None):
        self.on = on
        self.first = first
        self.second = second
    
    def describe(self,player=None):
        if player == self.on:
            return f"Formaled by {self.first} second {self.second}"
        if player == self.first:
            return f"Formaled {self.on} with {self.second}"
        if player == self.second:
            return f"Seconded {self.first}'s formal on {self.on}"
