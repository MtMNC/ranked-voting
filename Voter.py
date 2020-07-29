class Voter():
    """
    A Voter is identified by their username.
    They can vote for (assign rankings to) contest entries.
    """

    # how many distinct entries each Voter can vote for
    # (in other words, the number of distinct rankings the user can assign)
    ALLOWED_VOTE_COUNT = 3


    def __init__(self, username):
        self.username = username
        # For readability, self._votes[i] contains those entries that the Voter has assigned
        # ranking i.
        # Note that arrays are indexed from 0, but rankings are indexed from 1.
        # So, we make the array one element bigger than it needs to be and pretend the array is
        # indexed from 1, ignoring index 0.
        self._votes = [[] for _ in range(Voter.ALLOWED_VOTE_COUNT + 1)]


    def add_vote(self, entry, ranking):
        """
        Vote for (assign the given ranking to) the given entry.
        Note duplicate votes can occur (multiple entries can be given the same ranking).
        """

        self._votes[int(ranking)].append(entry)


    def get_all_votes(self):
        """
        Return a list representing all of the Voter's votes.
        Index i contains those entries that the Voter has assigned ranking i.
        Note that index 0 is empty, since no entries are assigned ranking 0.
        """

        return self._votes


    def __repr__(self):
        return "[Voter: username=" + self.username + ", votes=" + str(self.get_all_votes()) + "]"


    def get_duplicate_votes(self):
        """
        Return a dictionary representing all of the user's duplicate votes (when the Voter assigned
        the same ranking to multiple entries).
        Each key is a ranking that the user assigned duplicates of, and each value is a list of
        entries that received that key's ranking.
        Returns None if the user has no duplicate votes.
        """

        duplicate_votes = {}

        for ranking, entries in enumerate(self._votes):
            if len(entries) > 1:
                duplicate_votes[ranking] = entries

        return duplicate_votes
