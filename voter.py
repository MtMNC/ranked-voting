import math

class Voter():
    """
    A Voter is identified by their name.
    They can vote for (assign rankings to) contest entries.
    """


    def __init__(self, name, num_distinct_rankings):
        self.name = name

        # self._all_votes_by_ranking[r] contains a list of all Entries that the
        # Voter has assigned ranking r.
        # Note that arrays are indexed from 0, but rankings are indexed from 1.
        # So, we make the array one element bigger than it needs to be and pretend the array is
        # indexed from 1, ignoring index 0.
        # Also, note that some of these rankings might be invalid. (See the docstring of rank
        # for more information.)
        self._all_votes_by_ranking = [[] for _ in range(num_distinct_rankings + 1)]
        # self._all_votes_by_entry[e] contains a list of all the rankings that the
        # Voter has assigned to Entry e.
        # Note that some of these rankings might be invalid. (See the docstring of rank
        # for more information.)
        self._all_votes_by_entry = {}

        # self._all_votes_by_ranking[r] contains the single Entry that the Voter has assigned the
        # valid ranking r, and None if no such Entry exists.
        self._valid_votes_by_ranking = [None for _ in range(num_distinct_rankings + 1)]
        # self._valid_votes_by_entry[e] contains the single valid ranking that the Voter has
        # assigned to entry e.
        self._valid_votes_by_entry = {}

        # the round when the Voter was last allocated to a new Entry
        self.round_when_last_moved = 0


    def rank(self, entry, ranking):
        """
        Vote for (assign the given ranking to) the given Entry.
        Note that not all rankings are valid.
        If the same Entry is given multiple rankings, then only the smallest (highest priority)
        ranking is valid. Similarly, if the same ranking is given to multiple Entries, then all of
        those Entries' rankings are invalid.
        """

        # only apply this ranking if it hasn't been used before and is an improvement for the
        # current Entry
        should_apply_ranking = True

        # a ranking shouldn't be used twice, so if it has been used before,
        # it shouldn't be applied to the new Entry, and it should be removed from the other Entry
        if self._all_votes_by_ranking[ranking]:
            should_apply_ranking = False

            other_entry = self._valid_votes_by_ranking[ranking]
            if other_entry is not None:
                del self._valid_votes_by_entry[other_entry]
                self._valid_votes_by_ranking[ranking] = None

        # if the entry has been ranked already, use the better of the two rankings
        if entry in self._valid_votes_by_entry:
            other_ranking = self._valid_votes_by_entry[entry]
            if ranking < other_ranking:
                self._valid_votes_by_ranking[other_ranking] = None
            else:  # the ranking isn't an improvement for the Entry
                should_apply_ranking = False

        self._all_votes_by_ranking[ranking].append(entry)
        if entry not in self._all_votes_by_entry:
            self._all_votes_by_entry[entry] = []
        self._all_votes_by_entry[entry].append(ranking)

        if should_apply_ranking:
            self._valid_votes_by_entry[entry] = ranking
            self._valid_votes_by_ranking[ranking] = entry


    def get_entry_with_ranking(self, ranking):
        """
        Return the Entry with the given rank, or None if no such Entry exists.
        """

        return self._all_votes_by_ranking.get(ranking)


    def get_ranking_of_entry(self, entry):
        """
        Return the valid ranking of the given Entry, or math.inf if no such ranking exists.
        """

        return self._valid_votes_by_entry.get(entry, math.inf)


    def __iter__(self):
        """
        Iterator over the Entries still in the running that the Voter gave valid votes to,
        sorted from the Voter's favorite to least favorite.

        If multiple entries share the same rank, then those entries are skipped.
        """

        # only iterate over those ranks that were assigned to exactly 1 entry
        self._valid_votes = iter(
            entry for entry in self._valid_votes_by_ranking if entry is not None
        )
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