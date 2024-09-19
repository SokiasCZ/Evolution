
class Neuron:
    def __init__(self, name, short, computation, nType, nId):
        self.name = name
        self.sign = short
        self.computation = computation
        self.nType = nType
        self.nId = nId
    
    def __str__(self):
        return self.name
