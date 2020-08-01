class Voter():
    """
    A Voter is identified by their name.
    They can vote for (assign rankings to) contest entries.
    """


    # how many distinct entries each Voter can vote for
    # (in other words, the number of distinct rankings the user can assign)
    ALLOWED_VOTE_COUNT = 3


    def __init__(self, name):
        self.name = name
        # Store votes in a list (indexed by ranking) to easily construct the iterator later on.
        # For readability, self._votes[i] contains those entries that the Voter has assigned
        # ranking i.
        # Note that arrays are indexed from 0, but rankings are indexed from 1.
        # So, we make the array one element bigger than it needs to be and pretend the array is
        # indexed from 1, ignoring index 0.
        self._votes_by_ranking = [[] for _ in range(Voter.ALLOWED_VOTE_COUNT + 1)]
        # Also store votes in a dictionary (keyed by entry) to easily find entry's ranks later on.
        self._votes_by_entry = {}


    def rank(self, entry, ranking):
        """
        Vote for (assign the given ranking to) the given entry.
        Note duplicate votes can occur (multiple entries can be given the same ranking), but
        multiple rankings cannot be assigned to the same entry.
        """

        self._votes_by_ranking[ranking].append(entry)
        self._votes_by_entry[entry] = ranking


    def get_entries_with_ranking(self, ranking):
        """
        Return a list of the Entries with the given rank.
        """

        return self._votes_by_ranking[ranking]


    def get_ranking_of_entry(self, entry):
        """
        Return the ranking of the given Entry.
        """

        return self._votes_by_entry[entry]


    def get_duplicate_votes(self):
        """
        Return a dictionary representing all of the user's duplicate votes (when the Voter assigned
        the same ranking to multiple Entries).
        Each key is a ranking that the user assigned duplicates of, and each value is a list of
        Entry names that received that key's ranking.
        Returns None if the user has no duplicate votes.
        """

        duplicate_votes = {}

        for ranking, entries in enumerate(self._votes_by_ranking):
            if len(entries) > 1:
                duplicate_votes[ranking] = [entry.name for entry in entries]

        return duplicate_votes


    def __iter__(self):
        """
        Iterator over the Entries still in the running that the Voter gave valid votes to,
        sorted from the Voter's favorite to least favorite.

        If multiple entries share the same rank, then those entries are skipped.
        """

        # only iterate over those ranks that were assigned to exactly 1 entry
        self._valid_votes = iter([entries_with_given_ranking[0] for entries_with_given_ranking
            in self._votes_by_ranking if len(entries_with_given_ranking) == 1])
        return self


    def __next__(self):
        """
        Return the Voter's next favorite Entry that's still in the race, or None if none remain.
        """

        next_favorite_entry = next(self._valid_votes, None)

        while not ((next_favorite_entry is None) or (next_favorite_entry.still_in_race)):
            next_favorite_entry = next(self._valid_votes, None)

        return next_favorite_entry
