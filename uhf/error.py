

class UhfException(Exception): #classe de exessões
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg