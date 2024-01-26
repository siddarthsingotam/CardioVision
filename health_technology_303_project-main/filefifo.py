
class Filefifo:
    def __init__(self, name):
        self.file  = open(name)
        self.value = 0
        
    def put(self, value):
        pass

    def get(self):
        str = self.file.readline()
        if len(str) > 0:
            self.value = int(str)
        else:
            self.value = -1            
        return self.value
    
    def dropped(self):
        return 0
        
                
    def empty(self):        
        return False
