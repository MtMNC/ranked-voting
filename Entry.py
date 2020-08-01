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
        self.still_in_race = True

    # def add_voter(self, voter):
    #     """
    #     Add the given Voter, and their remaining ballot, to the Entry's list of Voters.
    #     """
    #
    #     self.voters.append(voter)
    #
    #
    # def get_voters(self):
    #     """
    #     Return the list of this Entry's Voters.
    #     """
    #
    #     return self.voters
    #
    #
    # def get_num_voters(self):
    #     return len(self._voters)
