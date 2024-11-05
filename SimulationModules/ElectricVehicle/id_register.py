# TODO This needs to be a singelton somehow
class ID_register:

    counter = 0

    def __init__(self):
        self.id = 0


    def get_id(self) -> int:  
        #logger.info(self.__class__.__dict__)
        ID_register.counter=ID_register.counter+1  
        self.id = ID_register.counter

        return self.id

    def reset():

        ID_register.counter=0
