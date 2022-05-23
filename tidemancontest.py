import csv
import heapq
import itertools

from contest import Contest
from entry import Entry
from voter import Voter

class TidemanContest(Contest):
    """
    A Contest contains Voters who have assigned rankings (numbers) to various Entries.
    It also has a desired number of winners.
    """


    # how wide in characters the vote bars printed by _print_instant_runoff_chart should be
    # if the bar represents 100%
    NUM_CHARS_IN_FULL_VOTE_BAR = 100


    # title of the spreadsheet column containing Voters who didn't cast any valid votes;
    # also used when printing instant runoff results to console
    INSTANT_RUNOFF_ROUND_SPREADSHEET_INVALID_VOTER_COLUMN_NAME = "voters who didn't cast any valid votes"
    # title of the spreadsheet column containing Voters whose preferred entries can't receive votes;
    # also used when printing instant runoff results to console
    INSTANT_RUNOFF_ROUND_SPREADSHEET_ELIMINATED_VOTER_COLUMN_NAME = "voters whose valid preferences have all been eliminated"


    # title of the spreadsheet column containing the Voters in a 1v1 match
    ALL_1V1_MATCH_VOTES_SPREADSHEET_VOTER_COLUMN_NAME = "voter"


    # title of the spreadsheet column tallying each Entry's total win count in remaining 1v1 matches
    REMAINING_1V1_MATCH_SUMMARY_SPREADSHEET_NUM_WINS_COLUMN_NAME = "number of wins"


    def _write_all_1v1_match_votes_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out the contest's current status to a spreadsheet at the path
        {output_file_name_prefix}-all-1v1-match-votes.csv

        Each row corresponds to a Voter and each column corresponds to a 1v1 matchup.
        Each cell indicates which Entry in the given matchup the given Voter prefers, along with
        the rankings that the Voter assigned each of the two Entries.
        """

        output_file_name = f"{output_file_name_prefix}-all-1v1-match-votes.csv"

        if self.verbose:
            print()
            print(f"Writing all 1v1 match vote data to {output_file_name}...", end="", flush=True)

        with open(output_file_name, "w", newline="") as spreadsheet:
            match_names_to_entries = {}
            for i, entry1 in enumerate(self.entries):
                for entry2 in self.entries[i+1:]:
                    match_names_to_entries[f"{entry1.name} vs. {entry2.name}"] = (entry1, entry2)

            header = [
                self.ALL_1V1_MATCH_VOTES_SPREADSHEET_VOTER_COLUMN_NAME,
                *[match_name for match_name in match_names_to_entries],
            ]
            writer = csv.DictWriter(spreadsheet, delimiter=",", fieldnames=header)
            writer.writeheader()

            rows = []
            for voter in self.voters:
                row = {
                    self.ALL_1V1_MATCH_VOTES_SPREADSHEET_VOTER_COLUMN_NAME: voter.name
                }
                for match_name, (entry1, entry2) in match_names_to_entries.items():
                    entry1_ranking = voter.get_ranking_of_entry(entry1)
                    entry2_ranking = voter.get_ranking_of_entry(entry2)

                    if entry1_ranking < entry2_ranking:
                        match_text = f"{entry1.name} (rankings: {entry1_ranking} vs. {entry2_ranking})"
                    elif entry2_ranking < entry1_ranking:
                        match_text = f"{entry2.name} (rankings: {entry1_ranking} vs. {entry2_ranking})"
                    else:
                        match_text = "N/A"

                    row[match_name] = match_text

                rows.append(row)

            writer.writerows(rows)

        if self.verbose:
            print(" done.")


    def _write_remaining_1v1_match_summary_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out a summary of the TidemanContest's remaining 1v1 matches to a spreadsheet at the
        path {output_file_name_prefix}-round{self._round_number}-1v1-matches.csv

        Rows and columns correspond to an Entry still in the race.
        Each cell represents a match between the row's and column's Entries. It contains a 1
        if the row's Entry would win the match.

        Finally, the rightmost column tallies up the wins of each row's Entry.
        """

        output_file_name = f"{output_file_name_prefix}-round{self._round_number}-1v1-matches.csv"

        if self.verbose:
            print()
            print(f"Writing current 1v1 match summary to {output_file_name}...", end="", flush=True)

        with open(output_file_name, "w", newline="") as spreadsheet:
            header = [
                "",
                *[entry.name for entry in self.entries],
                self.REMAINING_1V1_MATCH_SUMMARY_SPREADSHEET_NUM_WINS_COLUMN_NAME
            ]
            writer = csv.DictWriter(spreadsheet, delimiter=",", fieldnames=header)
            writer.writeheader()

            rows = []
            for entry in self.entries:
                row = {
                    "": entry.name
                }

                for other_entry in self.entries:
                    if other_entry in entry.remaining_beatable_1v1_match_opponents:
                        row[other_entry.name] = 1

                row[self.REMAINING_1V1_MATCH_SUMMARY_SPREADSHEET_NUM_WINS_COLUMN_NAME] = len(entry.remaining_beatable_1v1_match_opponents)

                rows.append(row)

            writer.writerows(rows)

        if self.verbose:
            print(" done.")


    def _write_instant_runoff_round_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out the results of the last instant-runoff round to a spreadsheet at the path
        {output_file_name_prefix}-round{self._round_number}-instant-runoff.csv

        The first column contains the names of those Voters who did not provide any valid votes.
        The second column contains the names of those Voters who provided valid votes, but only for
        Entries that were eliminated already.
        Each of the remaining columns represents an Entry that's still in the running.
        Each cell in those columns represents a Voter who voted for that column's Entry.
        Those cells contain the Voter name, the ranking they gave the Entry, and the Borda count
        they gave the Entry.
        """

        output_file_name = f"{output_file_name_prefix}-round{self._round_number}-instant-runoff.csv"

        if self.verbose:
            print()
            print(
                f"Writing round {self._round_number} instant runoff data to {output_file_name}...",
                end="",
                flush=True
            )

        with open(output_file_name, "w", newline="") as spreadsheet:
            writer = csv.writer(spreadsheet, delimiter=",")

            entries_header = [
                f"{entry.name} ({len(entry.instant_runoff_voters)} votes, Borda count {entry.borda_count})"
                for entry in self.entries
            ]

            header = [
                TidemanContest.INSTANT_RUNOFF_ROUND_SPREADSHEET_INVALID_VOTER_COLUMN_NAME,
                TidemanContest.INSTANT_RUNOFF_ROUND_SPREADSHEET_ELIMINATED_VOTER_COLUMN_NAME,
                *entries_header
            ]
            writer.writerow(header)

            # construct a list for each entry column
            entry_columns = []
            for entry in self.entries:
                # each column is filled with data on the user that voted for that Entry
                # and which rank the user gave that Entry
                entry_column = []
                for voter in entry.instant_runoff_voters:
                    voter_info_string = (
                        f"{voter.name}: assigned ranking {voter.get_ranking_of_entry(entry)}"
                        f" (Borda count {voter.get_borda_count_of_entry(entry)}),"
                        f" moved in round {voter.round_when_last_moved}"
                    )
                    entry_column.append(voter_info_string)

                entry_columns.append(entry_column)

            # rearrange the body of the spreadsheet into a list of rows (so each list passed in as
            # an argument becomes a column in the final body)
            body = itertools.zip_longest(
                [voter.name for voter in self._voters_with_no_valid_votes],
                [
                    f"{voter.name}: round {voter.round_when_last_moved}"
                    for voter in self._voters_with_no_remaining_valid_votes
                ],
                *entry_columns,
                fillvalue=""
            )
            for row in body:
                writer.writerow(row)

        if self.verbose:
            print(" done.")


    def _print_round_name(self):
        print()
        print("#" * TidemanContest.NUM_CHARS_IN_DIVIDER)
        print(f" ROUND {self._round_number} ".center(TidemanContest.NUM_CHARS_IN_DIVIDER, "#"))
        print("#" * TidemanContest.NUM_CHARS_IN_DIVIDER)


    def _print_1v1_match_summary(self):
        """
        Print each Entry still in the race and its 1v1 win count to the console.
        Note that this method assumes at least one Entry remains in the race.
        """

        print()
        print("Entries still in the race:")
        print()
        sorted_entries = self._get_sorted_entries_still_in_race()
        longest_entry_name_length = max(len(entry.name) for entry in self._entries_still_in_race)
        longest_num_wins_length = len(str(len(sorted_entries[0].remaining_beatable_1v1_match_opponents)))
        for entry in sorted_entries:
            win_text = "win " if len(entry.remaining_beatable_1v1_match_opponents) == 1 else "wins"
            beatable_entries_text = str([e.name for e in entry.remaining_beatable_1v1_match_opponents])[1:-1]

            entry_text = f"\t{entry.name}: ".ljust(longest_entry_name_length + 3)
            entry_text += str(len(entry.remaining_beatable_1v1_match_opponents)).ljust(longest_num_wins_length)
            entry_text += f" 1v1 {win_text}"
            if entry.remaining_beatable_1v1_match_opponents:
                entry_text += f" (beats {beatable_entries_text})"

            print(entry_text)


    def _print_instant_runoff_chart(self):
        """
        Output a chart of the current instant runoff votes to the console.
        """

        longest_entry_name_length = max(len(entry.name) for entry in self.entries)

        print()
        print("Instant runoff results:")
        print()
        for entry in self._entries_still_in_race:

            vote_fraction = len(entry.instant_runoff_voters) / len(self._voters_with_valid_votes)

            # bar in chart showing vote count
            num_chars_in_vote_bar = round(TidemanContest.NUM_CHARS_IN_FULL_VOTE_BAR * vote_fraction)
            vote_bar = "\u25A0" * num_chars_in_vote_bar

            # text showing percentage of Voters voting for this entry
            percentage_text = f"{round(100 * vote_fraction, 1)}%"

            # text showing number of Voters voting for this entry
            vote_text = "vote" if len(entry.instant_runoff_voters) == 1 else "votes"
            vote_count_text = f"{len(entry.instant_runoff_voters)} {vote_text}"

            # text showing how much the number of Voters changed this round
            change_text_sign = "+" if entry.num_instant_runoff_voters_gained_in_current_round >= 0 else ""
            change_text = f"{change_text_sign}{entry.num_instant_runoff_voters_gained_in_current_round} this round"

            # text showing the Borda count
            borda_count_text = f"Borda count {entry.borda_count}"

            entry_output = "\t" + entry.name.ljust(longest_entry_name_length + 2)
            entry_output += f"{vote_bar} {percentage_text}"
            entry_output += f" ({vote_count_text}, {change_text}; {borda_count_text})"
            print(entry_output)

        print()

        # print info about unused voters
        print(
            f"\t{TidemanContest.INSTANT_RUNOFF_ROUND_SPREADSHEET_INVALID_VOTER_COLUMN_NAME}:"
            f" {len(self._voters_with_no_valid_votes)}"
        )
        print(
            f"\t{TidemanContest.INSTANT_RUNOFF_ROUND_SPREADSHEET_ELIMINATED_VOTER_COLUMN_NAME}: "
            f"{len(self._voters_with_no_remaining_valid_votes)}"
            f" (+{self._num_instant_runoff_voters_exhausted_in_current_round} this round)"
        )


    def _run_all_1v1_matches(self):
        """
        Simulate 1v1 matches between every Entry and store the results in the Entries.
        Specifically, e.remaining_beatable_1v1_match_opponents contains all the Entries remaining
        in the TidemanContest that Entry e would defeat in a 1v1 match.
        """

        for i, entry1 in enumerate(self.entries):
            for entry2 in self.entries[i+1:]:
                entry1_num_votes = 0
                entry2_num_votes = 0

                for voter in self.voters:
                    entry1_ranking = voter.get_ranking_of_entry(entry1)
                    entry2_ranking = voter.get_ranking_of_entry(entry2)

                    if entry1_ranking < entry2_ranking:
                        entry1_num_votes += 1
                    elif entry2_ranking < entry1_ranking:
                        entry2_num_votes += 1

                if entry1_num_votes > entry2_num_votes:
                    entry1.remaining_beatable_1v1_match_opponents.add(entry2)
                elif entry2_num_votes > entry1_num_votes:
                    entry2.remaining_beatable_1v1_match_opponents.add(entry1)


    def _prepare_instant_runoff(self):
        """
        Pre-process and store Voter data to prepare for the first round of instant runoff voting.
        """

        # Voters who did and did not cast valid votes
        self._voters_with_valid_votes = []
        self._voters_with_no_valid_votes = []
        for voter in self.voters:
            if voter.cast_valid_vote:
                self._voters_with_valid_votes.append(voter)
                # prepare Voter to iterate through their valid votes in future rounds
                iter(voter)
            else:
                self._voters_with_no_valid_votes.append(voter)

        # Voters who should vote for their favorite remaining Entry in the next round;
        # in the first round, all eligible voters should vote for their favorite remaining Entry
        self._voters_to_reallocate = self._voters_with_valid_votes.copy()
        # Voters who only cast valid votes for Entries that have been eliminated
        self._voters_with_no_remaining_valid_votes = []

        # the amount of Voters who have had all of their Entries eliminated during the current round
        self._num_instant_runoff_voters_exhausted_in_current_round = 0


    def _eliminate_entry(self, entry):
        """
        Eliminate the given Entry from the TidemanContest.
        """

        entry.has_lost = True
        self._entries_still_in_race.remove(entry)

        # remove the Entry from the records of remaining 1v1 matches
        for other_entry in self.entries:
            other_entry.remaining_beatable_1v1_match_opponents.discard(entry)

        # all Voters currently supporting the Entry as their favorite should now support their
        # next-favorite remaining Entry during the next instant-runoff round
        self._voters_to_reallocate += entry.instant_runoff_voters
        entry.instant_runoff_voters = []

        # at the beginning of the next round, self._prev_round_was_productive should be True to
        # indicate that this round had at least one elimination
        self._prev_round_was_productive = True


    def _get_sorted_entries_still_in_race(self):
        """
        Return the Entries still in the race, sorted from highest to lowest 1v1 win count.
        """

        return sorted(
            self._entries_still_in_race,
            key=lambda e: len(e.remaining_beatable_1v1_match_opponents),
            reverse=True
        )


    def _set_is_dominating(self, inside_entries, outside_entries):
        """
        Given two lists of Entries still in the race, one representing a possible dominating set
        and one representing the elements not in the set,
        Return True if the possible dominating set is in fact dominating and False otherwise.

        The set is dominating if it is non-empty and has a special property:
        if you take two Entries, one inside the set and one outside,
        then the one inside the set would win in a 1v1 match.
        """

        if not inside_entries:
            if self.verbose:
                print(
                    f" result {inside_entries} is not dominating"
                    " because dominating sets must contain at least 1 entry."
                )
            return False

        for inside_entry in inside_entries:
            for outside_entry in outside_entries:
                if outside_entry not in inside_entry.remaining_beatable_1v1_match_opponents:
                    if self.verbose:
                        print(
                            f" result {[entry.name for entry in inside_entries]} is not dominating "
                            f"because {inside_entry.name} does not defeat {outside_entry.name}."
                        )
                    return False

        if self.verbose:
            print(f" result {[entry.name for entry in inside_entries]} is dominating.")
        return True


    def _eliminate_entries_outside_dominating_set(self):
        """
        Of the remaining Entries, find the smallest dominating set of size at least
        self._num_winners. Eliminate all Entries not in this set from the TidemanContest.

        A dominating set is a non-empty subset of Entries still in the race with a special property:
        if you take two Entries still in the race, one that's in the set and one that's not,
        then the one in the set would win in a 1v1 match.
        """

        # For every dominating set, there is a threshold T such that every Entry in the set has
        # at least T wins, and every Entry outside the set has fewer than T wins.
        # Therefore, we can construct the dominating set by adding Entries in most-to-least win
        # order until it contains at least self._num_winners Entries and is dominating.
        # (This procedure will terminate because eventually, the set will contain every single Entry
        # still in the race. Then the set will be dominating because it's vacuously true
        # that each Entry outside the set will lose to each Entry in the set.)

        if self.verbose:
            print()
            print(
                f"Because {self._num_winners} winners are desired,"
                f" constructing the smallest dominating set of size >={self._num_winners}"
                f" on the remaining entries."
            )
            print(f"\t* Adding {self._num_winners} entries with the most wins to the set...", end="")

        sorted_entries = self._get_sorted_entries_still_in_race()
        inside_entries = sorted_entries[:self._num_winners]
        outside_entries = sorted_entries[self._num_winners:]

        while not self._set_is_dominating(inside_entries, outside_entries):
            entry = outside_entries.pop(0)
            inside_entries.append(entry)

            if self.verbose:
                win_text = "win" if len(entry.remaining_beatable_1v1_match_opponents) == 1 else "wins"
                print(
                    f"\t* Adding {entry.name} ({len(entry.remaining_beatable_1v1_match_opponents)} {win_text}) to the set...",
                    end=""
                )

        # at this point, inside_entries is a dominating set of at least self._num_winners elements;
        # remove all the other elements

        if self.verbose:
            print(
                f"\t* The dominating set is {[entry.name for entry in inside_entries]}"
                f" with size {len(inside_entries)}."
            )
            print()
            print(f"Eliminating all {len(outside_entries)} entries outside the dominating set.")

        for outside_entry in outside_entries:
            if self.verbose:
                print(f"\t* Eliminating {outside_entry.name}.")

            self._eliminate_entry(outside_entry)


    def _reallocate_voters(self):
        """
        Reallocate the Voters in self._voters_to_reallocate to their next-choice Entry.
        If they don't have a next choice, add them to self._voters_with_no_remaining_valid_votes.
        """

        for voter in self._voters_to_reallocate:
            next_favorite_entry = next(voter)
            if next_favorite_entry is None:
                # the voter cast no more valid votes for Entries that are still in the race
                self._voters_with_no_remaining_valid_votes.append(voter)
                self._num_instant_runoff_voters_exhausted_in_current_round += 1
            else:
                next_favorite_entry.instant_runoff_voters.append(voter)
                next_favorite_entry.num_instant_runoff_voters_gained_in_current_round += 1

            voter.round_when_last_moved = self._round_number

        self._voters_to_reallocate = []


    def _update_borda_counts(self, last_place_entries):
        """
        Set all of the given last place Entries' Borda counts to reflect a simulated Contest in
        which every valid Voter backs their favorite Entry in last_place_entries.
        Set the Borda counts of all other remaining Entries to None.
        """

        for entry in self._entries_still_in_race:
            entry.borda_count = None

        for last_place_entry in last_place_entries:
            last_place_entry.borda_count = 0

        for voter in self._voters_with_valid_votes:
            entry_to_voter_borda_count = voter.get_borda_counts_of_entries(last_place_entries)
            for last_place_entry, borda_count in entry_to_voter_borda_count.items():
                last_place_entry.borda_count += borda_count



    def _get_instant_runoff_last_place_entries(self):
        """
        Simulate a round of instant-runoff voting in which each non-exhausted Voter supports their
        favorite remaining Entry. Return the last-place Entries and their Borda counts in a
        min heap containing tuples of the form
        (borda_count, entries_with_borda_count).
        """

        if self.verbose:
            print()
            print(
                f"Because {len(self._entries_still_in_race)} entries remain"
                f" but only {self._num_winners} winners are desired, identifying"
                " last-place entries through instant-runoff voting."
            )

        # Entries have not yet gained any Voters this round
        for entry in self.entries:
            entry.num_instant_runoff_voters_gained_in_current_round = 0
        self._num_instant_runoff_voters_exhausted_in_current_round = 0

        # move all valid, unassigned Voters to their next favorite Entry if possible
        # (for the first round, this is all valid Voters; for future rounds, this is all valid
        # Voters whose favorite Entry has been eliminated since their last vote)
        self._reallocate_voters()

        num_voters_for_last_place_entries = min(
            len(entry.instant_runoff_voters) for entry in self._entries_still_in_race
        )
        last_place_entries = [
            entry for entry in self._entries_still_in_race
            if len(entry.instant_runoff_voters) == num_voters_for_last_place_entries
        ]

        if self.verbose:
            entry_text = "entry" if len(last_place_entries) == 1 else "entries"
            print(
                f"\t* Identified {len(last_place_entries)} last-place {entry_text}"
                f" ({num_voters_for_last_place_entries} votes):"
                f" {[entry.name for entry in last_place_entries]}."
            )

        self._update_borda_counts(last_place_entries)

        # last_place_entries_by_borda_count[borda_count] contains a list of the last-place entries
        # with the given borda count
        last_place_entries_by_borda_count = {}
        for last_place_entry in last_place_entries:
            if last_place_entry.borda_count not in last_place_entries_by_borda_count:
                last_place_entries_by_borda_count[last_place_entry.borda_count] = []
            last_place_entries_by_borda_count[last_place_entry.borda_count].append(last_place_entry)

        min_heap = []
        for borda_count, entries_with_borda_count in last_place_entries_by_borda_count.items():
            heapq.heappush(min_heap, (borda_count, entries_with_borda_count))

        return min_heap


    def _eliminate_instant_runoff_last_place_entries(self):
        """
        Simulate a round of instant-runoff voting in which each non-exhausted Voter supports their
        favorite remaining Entry. Eliminate the last-place Entries in order from least to greatest
        Borda count until either all have been eliminated or eliminating more would prevent the
        TidemanContest from having enough winners.
        """

        borda_counts_and_last_place_entries = self._get_instant_runoff_last_place_entries()

        if self.verbose:
            self._print_instant_runoff_chart()
            print()
            print("Eliminating last-place entries in order from least-to-greatest Borda count.")

        while borda_counts_and_last_place_entries and \
            len(self._entries_still_in_race) > self._num_winners:
            borda_count, entries_with_borda_count = heapq.heappop(borda_counts_and_last_place_entries)

            if len(self._entries_still_in_race) - len(entries_with_borda_count) < self._num_winners:
                if self.verbose:
                    print(
                        f"\t* Because {[e.name for e in entries_with_borda_count]} have"
                        f" the same Borda count ({borda_count}), eliminating more entries"
                        " would produce"
                        f" {len(self._entries_still_in_race) - len(entries_with_borda_count)} < {self._num_winners}"
                        " winners."
                    )
                break
            else:
                if self.verbose:
                    print(
                        f"\t* Eliminating last-place entries with Borda count {borda_count}:",
                        [e.name for e in entries_with_borda_count]
                    )
                for entry in entries_with_borda_count:
                    self._eliminate_entry(entry)


    def get_winners(self, num_winners, output_file_name_prefix):
        """
        Run the TidemanContest using Tideman's alternative method. The simulation terminates once
        either:

        * num_winners winners have won, or
        * more than num_winners winners have won, but we cannot eliminate any Entries according to
            the contest rules.

        During the simulation, output the following spreadsheets:

        * how the Voters would vote in every possible 1v1 match;
        * for every round, a summary of the 1v1 matches involving the Entries still in the race;
        * for every round, if needed, the results of an IRV round of voting for those Entries that
            survived the round's 1v1 matches.

        Return the Entry objects representing the winners.
        """

        if num_winners >= len(self.entries):
            raise ValueError(
                "A TidemanContest must have fewer winners then entries."
                f" This TidemanContest seeks to produce {num_winners} winners"
                f" but has only {len(self.entries)} entries."
            )

        self._num_winners = num_winners
        self._round_number = 0
        self._entries_still_in_race = self.entries.copy()
        # at the beginning of a round, self._prior_round_was_productive is True if the prior round
        # resulted in at least one elimination and False otherwise. At all other times, the
        # boolean's value is not guaranteed to mean anything.
        self._prev_round_was_productive = True

        # perform prep work before eliminations can take place:
        # determine the outcome of every 1v1 match, and prepare for instant-runoff voting
        self._run_all_1v1_matches()
        self._prepare_instant_runoff()
        self._write_all_1v1_match_votes_to_spreadsheet(output_file_name_prefix)

        # keep running rounds until all the winners are found or until a round accomplishes nothing
        # (which can happen if too many winners were found, but none can be eliminated due to a tie)
        while len(self._entries_still_in_race) > self._num_winners and self._prev_round_was_productive:
            self._round_number += 1
            if self.verbose:
                self._print_round_name()

            self._prev_round_was_productive = False

            if self.verbose:
                self._print_1v1_match_summary()

            self._write_remaining_1v1_match_summary_to_spreadsheet(output_file_name_prefix)
            self._eliminate_entries_outside_dominating_set()

            if len(self._entries_still_in_race) > self._num_winners:
                self._eliminate_instant_runoff_last_place_entries()
                self._write_instant_runoff_round_to_spreadsheet(output_file_name_prefix)

        if self.verbose:
            print()
            print("#" * TidemanContest.NUM_CHARS_IN_DIVIDER)
            print("#" * TidemanContest.NUM_CHARS_IN_DIVIDER)
            print("#" * TidemanContest.NUM_CHARS_IN_DIVIDER)
            print()
            if len(self._entries_still_in_race) > self._num_winners:
                reason_contest_ended = "No entries were eliminated last round"
            else:
                winner_text = "winner has" if self._num_winners == 1 else "winners have"
                reason_contest_ended = f"{self._num_winners} {winner_text} been found"

            print(f"{reason_contest_ended}, so the contest is over.")

        print()
        print(f"WINNERS: {[winner.name for winner in self._entries_still_in_race]}")
        print()
        return self._entries_still_in_race