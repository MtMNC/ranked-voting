class Entry:
    """
    An Entry into a Contest has a name and a group of Voters who voted for it.
    """


    def __init__(self, name):
        self.name = name
        self.voters = []
        # still_in_race is False once the entry has removed from the polls (when it has either
        # gotten enough wins to guarantee a win, or when it has been eliminated since it's in last
        # place)
        self.has_won = False
        self.has_lost = False
        self.num_voters_gained_in_current_round = 0


    @property
    def still_in_race(self):
        return not (self.has_won or self.has_lost)
