class Entry:
    """
    An Entry into a Contest has a name and a group of Voters who voted for it.
    """


    def __init__(self, name):
        self.name = name
        self.instant_runoff_voters = []
        # still_in_race is False once the entry has removed from the polls (when it has either
        # gotten enough wins to guarantee a win, or when it has been eliminated since it's in last
        # place)
        self.has_won = False
        self.has_lost = False
        self.num_instant_runoff_voters_gained_in_current_round = 0

        # the Entries still in the race that this Entry would beat in a 1v1 match
        self.remaining_beatable_1v1_match_opponents = set()


    @property
    def still_in_race(self):
        return not (self.has_won or self.has_lost)


    @property
    def borda_count(self):
        return sum(voter.get_borda_count_of_entry(self) for voter in self.instant_runoff_voters)
