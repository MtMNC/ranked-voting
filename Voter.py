class Voter():
    """
    A Voter is identified by their name.
    They can vote for (assign rankings to) contest entries.
    """


    # how many distinct Entries each Voter can vote for
    # (in other words, the number of distinct rankings the user can assign)
    ALLOWED_VOTE_COUNT = 3


    def __init__(self, name):
        self.name = name
        # Store votes in a list (indexed by ranking) to easily construct the iterator later on.
        # For readability, self._votes[i] contains those Entries that the Voter has assigned
        # ranking i.
        # Note that arrays are indexed from 0, but rankings are indexed from 1.
        # So, we make the array one element bigger than it needs to be and pretend the array is
        # indexed from 1, ignoring index 0.
        self._votes_by_ranking = [[] for _ in range(Voter.ALLOWED_VOTE_COUNT + 1)]
        # Also store votes in a dictionary (keyed by entry) to easily find Entry's ranks later on.
        self._votes_by_entry = {}
        # the round when the Voter was last allocated to a new Entry
        self.round_when_last_moved = 0


    def rank(self, entry, ranking):
        """
        Vote for (assign the given ranking to) the given Entry.
        Note multiple rankings cannot be assigned to the same Entry. When this happens, only that
        Entry's top ranking is used.
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

        # skip over Entries that have left the race already until we're either out of entries,
        # or we encounter one that is still in the race
        while not ((next_favorite_entry is None) or next_favorite_entry.still_in_race):
            next_favorite_entry = next(self._valid_votes, None)

        return next_favorite_entry
