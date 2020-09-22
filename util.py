
def fixName(name):
    name = name.lower()
    if(len(name) > 4):
        return name[:4]
    elif(len(name) < 4):
        spaces = 4-len(name)
        return name+" "*spaces
    else:
         return name