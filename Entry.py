class Entry:
    """
    An Entry into a Contest has a name and a group of Voters who voted for it.
    """


    def __init__(self, name):
        self.name = name
        self._voters = []


    def add_voter(self, voter):
        """
        Add the given voter, and their remaining ballot, to the Entry's list of voters.
        """

        self._voters.append(voter)


    def get_num_voters(self):
        return len(self._voters)


    def __iter__(self):
        """
        Iterator over the Entry's Voters.
        """

        return iter(self.voters)
