class Entry:
    """
    An Entry into a Contest has a name and a list of Votes cast for it.
    Its current value in the Contest is given by sum of those Votes' values.
    """


    def __init__(self, name):
        self.name = name
        self.votes = []
        self.has_won = False
        self.has_lost = False
        self.value = 0
        self.value_gained_in_current_round = 0


    @property
    def still_in_race(self):
        return not (self.has_won or self.has_lost)
