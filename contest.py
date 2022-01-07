from entry import Entry
from voter import Voter
import csv
import heapq
import itertools

class Contest():
    """
    A Contest contains Voters who have assigned rankings (numbers) to various Entries.
    It also has a desired number of winners.
    """


    # how wide in characters the vote bars printed by _print_chart_to_console should be
    # if the bar represents 100%
    NUM_CHARS_IN_FULL_VOTE_BAR = 100
    # how wide in characters the text in _print_round_name should be
    NUM_CHARS_IN_ROUND = 100
    # title of the spreadsheet column containing Voters who didn't cast any valid votes
    INVALID_VOTER_COLUMN_NAME = "voters who didn't cast any valid votes"
    # title of the spreadsheet column containing Voters whose preferred entries can't receive votes
    ELIMINATED_VOTER_COLUMN_NAME = "voters whose valid preferences have all won or been eliminated"

    # title of the spreadsheet column containing the Voters in a 1v1 match
    ALL_1V1_MATCH_VOTES_SPREADSHEET_VOTER_COLUMN_NAME = "voter"


    def __init__(self, verbose=True):
        self.verbose = verbose
        self.voters = []
        self.entries = []


    def _print_round_name(self):
        print("#" * Contest.NUM_CHARS_IN_ROUND)
        print(f" ROUND {self._round_number} ".center(Contest.NUM_CHARS_IN_ROUND, "#"))
        print("#" * Contest.NUM_CHARS_IN_ROUND)


    def populate_from_spreadsheet(self, input_file_name):
        """
        Grab voter data from the given spreadsheet
        (prepared by create_spreadsheet_from_voter_dictionary in create-voter-spreadsheet.py)
        and populate the Contest with the relevant Voters and Entries.
        """

        if self.verbose:
            print(f"Populating contest with voter data from {input_file_name}...",
                end="", flush=True)

        with open(input_file_name, "r", newline="") as spreadsheet:
            reader = csv.reader(spreadsheet, delimiter=",")

            header = next(reader)
            entry_names = header[1:]
            # If there n Entries, each voter can assign at most n distinct rankings.
            # (Really the number of Entries may be more than the number of distinct rankings.
            # For example, a poll could ask users to vote for the top 3 Entries out of 10.
            # It's fine to overestimate the number of distinct rankings though. It'll just lead to
            # some wasted space in each Voter, which doesn't really matter.)
            num_distinct_rankings = len(entry_names)

            # construct Entries
            for entry_name in entry_names:
                # self.entries[i] contains the entry from column i+1
                # (not column i because the leftmost column contains user info, not entry info)
                self.entries.append(Entry(entry_name))

            print()
            # construct Voters and record their votes
            for row in reader:
                voter_name = row[0]
                # voter_rankings[i] contains the voter's ranking for entry self.entries[i]
                voter_rankings = row[1:]

                voter = Voter(voter_name, num_distinct_rankings)

                for i, ranking in enumerate(voter_rankings):
                    if ranking:
                        print(f'{voter_name}: assign ranking {ranking} to {self.entries[i].name}')
                        # the ranks are stored in user_rankings as a list of strings, so cast them
                        # to ints for use as indexes
                        voter.rank(self.entries[i], int(ranking))

                self.voters.append(voter)

        if self.verbose:
            print(" done.")


    # def _write_current_round_to_spreadsheet(self, output_file_name_prefix):
    #     """
    #     Write out the contest's current status to a spreadsheet at the path
    #     {output_file_name_prefix}-round{round_number}.csv

    #     The first column contains the names of those Voters who did not provide any valid votes.
    #     The second column contains the names of those Voters who provided valid votes, but only for
    #     entries that were eliminated already.
    #     Each of the remaining columns represents an Entry that's still in the running.
    #     Each cell in those columns represents a Voter who voted for that column's Entry.
    #     Those cells contain the Voter name, the rank they gave the Entry, and the round during
    #     which they voted for the Entry
    #     """

    #     input_file_name = output_file_name_prefix + str(self._round_number) + ".csv"

    #     if self.verbose:
    #         print(f"Writing round {self._round_number} vote data to {input_file_name}...",
    #             end="", flush=True)

    #     with open(input_file_name, "w", newline="") as spreadsheet:
    #         writer = csv.writer(spreadsheet, delimiter=",")

    #         header = [
    #             Contest.INVALID_VOTER_COLUMN_NAME,
    #             Contest.ELIMINATED_VOTER_COLUMN_NAME,
    #             *[entry.name for entry in self.entries]
    #         ]
    #         writer.writerow(header)

    #         # construct a list for each entry column
    #         entry_columns = []
    #         for entry in self.entries:
    #             # each column is filled with data on the user that voted for that Entry
    #             # and which rank the user gave that Entry
    #             entry_column = []
    #             for voter in entry.voters:
    #                 voter_info_string = (
    #                     f"{voter.name}: round {voter.round_when_last_moved}, "
    #                     f"rank {voter.get_ranking_of_entry(entry)}"
    #                 )
    #                 entry_column.append(voter_info_string)

    #             entry_columns.append(entry_column)

    #         # rearrange the body of the spreadsheet into a list of rows (so each list passed in as
    #         # an argument becomes a column in the final body)
    #         body = itertools.zip_longest(
    #             [voter.name for voter in self._voters_with_no_valid_votes],
    #             [
    #                 f"{voter.name}: round {voter.round_when_last_moved}"
    #                 for voter in self._voters_with_no_remaining_valid_votes
    #             ],
    #             *entry_columns,
    #             fillvalue=""
    #         )
    #         for row in body:
    #             writer.writerow(row)

    #     if self.verbose:
    #         print(" done.")


    # def _print_chart_to_console(self):
    #     """
    #     Output a chart of the current votes to the console.
    #     """

    #     longest_entry_name_length = max(len(entry.name) for entry in self.entries)

    #     print()
    #     for entry in self.entries:
    #         # once entry has won or lost, we never actually removed its Voters (there's no need to)
    #         # so len(entry.voters) won't actually reflect entry's true number of Voters
    #         if entry.has_won:
    #             status_indicator = "WON"
    #         elif entry.has_lost:
    #             status_indicator = "LOST"
    #         else:
    #             status_indicator = ""

    #         vote_fraction = len(entry.voters) / self._num_valid_voters

    #         # bar in chart showing vote count
    #         num_chars_in_vote_bar = round(Contest.NUM_CHARS_IN_FULL_VOTE_BAR * vote_fraction)
    #         vote_bar = "\u25A0" * num_chars_in_vote_bar

    #         # text showing percentage of voters voting for this entry
    #         percentage_text = f"{round(100 * vote_fraction, 1)}%"

    #         # text showing fraction of voters voting for this entry
    #         fraction_text = f"{len(entry.voters)}/{self._num_valid_voters}"

    #         # text showing how much the count changed this round
    #         change_text_sign = "+" if entry.num_voters_gained_in_current_round >= 0 else ""
    #         change_text = f"{change_text_sign}{entry.num_voters_gained_in_current_round} this round"

    #         entry_output = status_indicator.ljust(6)
    #         entry_output += entry.name.ljust(longest_entry_name_length + 2)
    #         entry_output += f"{vote_bar} {percentage_text} ({fraction_text}; {change_text})"
    #         print(entry_output)

    #     print()

    #     # print info about unused voters
    #     print(f"{Contest.INVALID_VOTER_COLUMN_NAME}: {len(self._voters_with_no_valid_votes)}")
    #     print(
    #         f"{Contest.ELIMINATED_VOTER_COLUMN_NAME}: "
    #         f"{len(self._voters_with_no_remaining_valid_votes)}"
    #         f" (+{self._num_voters_exhausted_in_current_round}) this round"
    #     )


    # def _allocate_voters(self, voters_to_allocate):
    #     """
    #     Allocate the given Voters to their first-choice entry.
    #     If they don't have a first choice, add them to self._voters_with_no_valid_votes.
    #     """

    #     for voter in voters_to_allocate:
    #         # prepare voter to iterate through their valid votes
    #         iter(voter)

    #         favorite_entry = next(voter)
    #         if favorite_entry is None:
    #             # the voter cast no valid votes
    #             self._voters_with_no_valid_votes.append(voter)
    #         else:
    #             favorite_entry.voters.append(voter)
    #             favorite_entry.num_voters_gained_in_current_round += 1

    #         voter.round_when_last_moved = self._round_number


    # def _reallocate_voters(self, current_entry, voters_to_reallocate):
    #     """
    #     Reallocate the given Voters to their next-choice entry.
    #     If they don't have a next choice, add them to self._voters_with_no_remaining_valid_votes.
    #     """

    #     for voter in voters_to_reallocate:
    #         next_favorite_entry = next(voter)
    #         if next_favorite_entry is None:
    #             # the voter cast no valid votes
    #             self._voters_with_no_remaining_valid_votes.append(voter)
    #             self._num_voters_exhausted_in_current_round += 1
    #         else:
    #             next_favorite_entry.voters.append(voter)
    #             next_favorite_entry.num_voters_gained_in_current_round += 1

    #         voter.round_when_last_moved = self._round_number

    #     # for bookkeeping purposes, remove all the Voters from the old Entry
    #     # NOTE not the most efficient but doesn't really need to be
    #     current_entry.voters = [
    #         voter for voter in current_entry.voters
    #         if voter not in voters_to_reallocate
    #     ]

    #     current_entry.num_voters_gained_in_current_round -= len(voters_to_reallocate)


    # def _run_first_round(self):
    #     """
    #     Run the first round of the contest. In this round, everybody votes for their first choice.
    #     """

    #     if self.verbose:
    #         self._print_round_name()

    #     # entries have not yet gained any votes this round
    #     for entry in self.entries:
    #         entry.num_voters_gained_in_current_round = 0
    #     self._num_voters_exhausted_in_current_round = 0

    #     self._allocate_voters(self.voters)

    #     # all Entries are still in the race; even if an Entry got no votes, we say it is still in,
    #     # and we'll just remove it in a later round
    #     for entry in self.entries:
    #         self._entries_still_in_race.append(entry)

    #     if self.verbose:
    #         print("* all voters voted for their top choice")


    # def _run_winner_declaration_round(self, undeclared_winners):
    #     """
    #     Run a "winner declaration" round of the contest. In this round, all Entries tied for the
    #     most votes that haven't won yet are marked as winners.
    #     """

    #     if self.verbose:
    #         self._print_round_name()

    #     # entries have not yet gained any votes this round
    #     for entry in self.entries:
    #         entry.num_voters_gained_in_current_round = 0
    #     self._num_voters_exhausted_in_current_round = 0

    #     for winner in undeclared_winners:
    #         self._entries_still_in_race.remove(winner)
    #         self._winners.append(winner)
    #         winner.has_won = True
    #         if self.verbose:
    #             print(
    #                 f"* {winner.name} won"
    #                 f" (earned {len(winner.voters)} votes, needed {self._min_num_voters_to_win})"
    #             )


    # def _run_winner_reallocation_round(self, declared_winners_still_with_surplus):
    #     """
    #     Run a "winner reallocation" round of the contest. In this round, one of the winning Entries
    #     that hasn't reallocated its Voters is selected at random and reallocates its Voters.
    #     """

    #     if self.verbose:
    #         self._print_round_name()

    #     # entries have not yet gained any votes this round
    #     for entry in self.entries:
    #         entry.num_voters_gained_in_current_round = 0
    #     self._num_voters_exhausted_in_current_round = 0

    #     winner = random.choice(declared_winners_still_with_surplus)
    #     num_surplus_voters = len(winner.voters) - self._min_num_voters_to_win
    #     surplus_voters = random.sample(winner.voters, k=num_surplus_voters)

    #     self._reallocate_voters(winner, surplus_voters)

    #     if self.verbose:
    #         print(
    #             f"* only {len(self._winners)}/{self._num_winners} winners have been found,"
    #             f" so winner {winner.name} reallocated its {num_surplus_voters} surplus votes"
    #         )


    # def _run_elimination_round(self):
    #     """
    #     Run an elimination round of the Contest. In this round, a least popular Entry is removed
    #     from the race, and its Voters vote for their next choice.
    #     """

    #     if self.verbose:
    #         self._print_round_name()

    #     # entries have not yet gained any votes this round
    #     for entry in self.entries:
    #         entry.num_voters_gained_in_current_round = 0
    #     self._num_voters_exhausted_in_current_round = 0

    #     # pick a loser at random out of all the bottom vote-getters
    #     num_voters_for_bottom_entry_still_in_race = min(
    #         len(entry.voters) for entry in self._entries_still_in_race
    #     )
    #     bottom_entries_still_in_race = [
    #         entry for entry in self._entries_still_in_race
    #         if len(entry.voters) == num_voters_for_bottom_entry_still_in_race
    #     ]
    #     loser = random.choice(bottom_entries_still_in_race)

    #     if self.verbose:
    #         print(
    #             f"* {loser.name} was eliminated"
    #             f" as it had the fewest votes ({num_voters_for_bottom_entry_still_in_race})"
    #         )

    #     self._entries_still_in_race.remove(loser)
    #     loser.has_lost = True
    #     self._reallocate_voters(loser, loser.voters)

    #     if self.verbose:
    #         print(
    #             f"* {loser.name} reallocated its"
    #             f" {num_voters_for_bottom_entry_still_in_race} votes"
    #         )


    def _write_all_1v1_match_votes_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out the contest's current status to a spreadsheet at the path
        {output_file_name_prefix}-round{round_number}-1v1-matches.csv

        Each row corresponds to a Voter and each column corresponds to a 1v1 matchup.
        Each cell indicates which Entry in the given matchup the given Voter prefers, along with
        the rankings that the Voter assigned each of the two Entries.
        """

        output_file_name = f"{output_file_name_prefix}-all-1v1-match-votes.csv"

        if self.verbose:
            print(f"Writing all 1v1 match vote data to {output_file_name}...", end="", flush=True)

        with open(output_file_name, "w", newline="") as spreadsheet:
            match_names_to_entries = {}
            for i, entry1 in enumerate(self.entries):
                for entry2 in self.entries[i+1:]:
                    match_names_to_entries[f'{entry1.name} vs. {entry2.name}'] = (entry1, entry2)

            header = [
                self.ALL_1V1_MATCH_VOTES_SPREADSHEET_VOTER_COLUMN_NAME,
                *[match_name for match_name in match_names_to_entries]
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
                        match_text = f'{entry1.name} (rankings: {entry1_ranking} vs. {entry2_ranking})'
                    elif entry2_ranking < entry1_ranking:
                        match_text = f'{entry2.name} (rankings: {entry1_ranking} vs. {entry2_ranking})'
                    else:
                        match_text = 'N/A'

                    row[match_name] = match_text

                rows.append(row)

            writer.writerows(rows)

        if self.verbose:
            print(" done.")


    def _write_remaining_1v1_match_summary_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out a summary of the Contest's remaining 1v1 matches to a spreadsheet at the path
        {output_file_name_prefix}-round{round_number}-1v1-matches.csv

        Rows and columns correspond to an Entry still in the race.
        Each cell represents a match between the row's and column's Entries. It contains a 1
        if the row's Entry would win the match.

        Finally, the rightmost column tallies up the wins of each row's Entry.
        """

        raise NotImplementedError


    def _write_instant_runoff_round_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out the contest's current status to a spreadsheet at the path
        {output_file_name_prefix}-round{round_number}-instant-runoff.csv

        The first column contains the names of those Voters who did not provide any valid votes.
        The second column contains the names of those Voters who provided valid votes, but only for
        Entries that were eliminated already.
        Each of the remaining columns represents an Entry that's still in the running.
        Each cell in those columns represents a Voter who voted for that column's Entry.
        Those cells contain the Voter name, the ranking they gave the Entry, and the Borda count
        they gave the Entry.
        """

        input_file_name = f"{output_file_name_prefix}-round{self._round_number}-instant-runoff.csv"

        if self.verbose:
            print(f"Writing round {self._round_number} vote data to {input_file_name}...",
                end="", flush=True)

        with open(input_file_name, "w", newline="") as spreadsheet:
            writer = csv.writer(spreadsheet, delimiter=",")

            entries_header = [
                f'{entry.name} ({len(entry.voters)} votes, Borda count {entry.borda_count})'
                for entry in self.entries
            ]

            header = [
                Contest.INVALID_VOTER_COLUMN_NAME,
                Contest.ELIMINATED_VOTER_COLUMN_NAME,
                *entries_header
            ]
            writer.writerow(header)

            # construct a list for each entry column
            entry_columns = []
            for entry in self.entries:
                # each column is filled with data on the user that voted for that Entry
                # and which rank the user gave that Entry
                entry_column = []
                for voter in entry.voters:
                    voter_info_string = (
                        f"{voter.name}: round {voter.round_when_last_moved}, "
                        f"rank {voter.get_ranking_of_entry(entry)}, "
                        f"Borda count {voter.get_borda_count_of_entry(entry)}"
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


    def _run_all_1v1_matches(self):
        """
        Simulate 1v1 matches between every Entry and store the results in the Entries.
        Specifically, e.remaining_defeatable_1v1_match_opponents contains all the Entries remaining
        in the Contest that Entry e would defeat in a 1v1 match.
        """

        for entry1, entry2 in zip(self.entries, self.entries):
            if entry1 == entry2:
                continue

            for voter in self.voters:
                entry1_ranking = voter.get_ranking_of_entry(entry1)
                entry2_ranking = voter.get_ranking_of_entry(entry2)

                if entry1_ranking < entry2_ranking:
                    entry1.remaining_defeatable_1v1_match_opponents.add(entry2)
                elif entry2_ranking < entry1_ranking:
                    entry2.remaining_defeatable_1v1_match_opponents.add(entry1)


    def _eliminate_entry(self, entry):
        """
        Eliminate the given Entry from the Contest.
        """


    def _eliminate_entries_outside_dominating_set(self):
        """
        Of the remaining Entries, find the smallest dominating set of size at least
        self._num_winners. Eliminate all Entries not in this set from the Contest.
        """

        raise NotImplementedError


    def _get_instant_runoff_last_place_entries(self):
        """
        Simulate a round of instant-runoff voting in which each non-exhausted Voter supports their
        favorite remaining Entry. Return the last-place Entries and their Borda counts in a
        min heap containing tuples of the form
        (borda_count, [all_last_place_entries_with_borda_count]).
        """

        raise NotImplementedError


    def get_winners(self, num_winners, output_file_name_prefix):
        """
        Run the Contest using the Tideman alternative method. The simulation terminates once either:

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
                "A Contest must have fewer winners then entries."
                f" This Contest seeks to produce {num_winners} winners"
                f" but has only {len(self.entries)} entries."
            )

        self._num_winners = num_winners

        # users who cast no valid votes
        self._voters_with_no_valid_votes = []
        # users who cast valid votes, but only for Entries that have been eliminated already
        self._voters_with_no_remaining_valid_votes = []
        # the amount of Voters who have had all of their Entries eliminated during this round
        self._num_voters_exhausted_in_current_round = 0
        self._entries_still_in_race = set(self.entries)
        self._round_number = 0

        # False once we encounter a scenario where eliminating more Entries would result in the
        # Contest not producing enough winners.
        can_eliminate_entries = self._entries_still_in_race > self._num_winners

        self._run_all_1v1_matches()
        self._write_all_1v1_match_votes_to_spreadsheet(output_file_name_prefix)

        while can_eliminate_entries:
            self._round_number += 1
            self._entries_eliminated_this_round = set()

            self._write_remaining_1v1_match_summary_to_spreadsheet(output_file_name_prefix)
            self._eliminate_entries_outside_dominating_set()

            if len(self._entries_still_in_race) == self._num_winners:
                can_eliminate_entries = False
            else:
                # Otherwise we try to eliminate at least one candidate: the loser(s) in an
                # instant-runoff round where every Voter backs their favorite remaining choice.
                # We eliminate them in order from least-to-greatest Borda score until doing
                # so would prevent the contest from having enough winners.
                # (Most of the time, there will only be one Entry to eliminate, and doing so will
                # not prevent the contest from having enough winners.)
                borda_counts_and_last_place_entries = self._get_instant_runoff_last_place_entries()
                self._write_instant_runoff_round_to_spreadsheet(output_file_name_prefix)

                while can_eliminate_entries and borda_counts_and_last_place_entries:
                    _, last_place_entries_with_borda_count = heapq.heappop(borda_counts_and_last_place_entries)
                    if len(self._entries_still_in_race) - len(last_place_entries_with_borda_count) < self._num_winners:
                        can_eliminate_entries = False
                    else:
                        for entry in last_place_entries_with_borda_count:
                            self._eliminate_entry(entry)

        # at this point, winners have been found if possible
        if len(self._entries_still_in_race) > self._num_winners:
            print(
                f"* {len(self._winners)}/{self._num_winners} winners have been found;"
                f" due to a tie, eliminating more would result in fewer than {self._num_winners}"
                f" winners"
            )
        else:
            print(
                f"* all {len(self._winners)}/{self._num_winners} winners have been found,"
                f" so the contest is over"
            )

        print(f"WINNERS: {[winner.name for winner in self._entries_still_in_race]}")

        return list(self._entries_still_in_race)



    # def get_winners(self, num_winners, output_file_name_prefix):
    #     """
    #     Run the contest using multi-winner instant-runoff voting using the Droop quota and
    #     random surplus allocation.
    #     For every round of voting, output a spreadsheet whose columns are entries, with the rows
    #     populated by users who voted for those entries.
    #     The contest terminates once self._num_winners winners have won.
    #     Return the Entry objects representing the winners.
    #     """

    #     if num_winners >= len(self.entries):
    #         raise ValueError(
    #             "A Contest must have fewer winners then entries."
    #             f" This Contest seeks to produce {num_winners} winners"
    #             f" but has only {len(self.entries)} entries."
    #         )

    #     self._num_winners = num_winners

    #     # users who cast no valid votes
    #     self._voters_with_no_valid_votes = []
    #     # users who cast valid votes, but only for Entries that have been eliminated already
    #     self._voters_with_no_remaining_valid_votes = []
    #     # the amount of voters who have had all of their entries eliminated during this round
    #     self._num_voters_exhausted_in_current_round = 0
    #     self._entries_still_in_race = []
    #     self._winners = []
    #     self._round_number = 1


    #     self._run_1v1_matches()

    #     # round 1: everyone votes for their top pick
    #     self._run_first_round()

    #     # Use the "Droop Quota" as the minimum vote threshold.
    #     # Say there are v Voters and w winners. An Entry wins once it has so many votes that it's
    #     # impossible for w other Entries to perform as well as the winner.
    #     # If an Entry gets exactly v/(w+1) votes, then it is still possible for w other Entries to
    #     # also get exactly v/(w+1) votes, in which case there would be a (w+1)-way tie.
    #     # If an Entry gets more than v/(w+1) votes, so at least (v/(w+1)) + 1 votes, then there's
    #     # no way for w other Entries to perform equally well, as that would imply at least
    #     # (w+1) * ((v/(w+1)) + 1) = v + w + 1 votes were cast, and that's more than v votes.
    #     self._num_valid_voters = len(self.voters) - len(self._voters_with_no_valid_votes)
    #     self._min_num_voters_to_win = math.floor(self._num_valid_voters / (self._num_winners + 1)) + 1

    #     self._write_current_round_to_spreadsheet(output_file_name_prefix)
    #     if self.verbose:
    #         self._print_chart_to_console()

    #     while len(self._winners) < self._num_winners:
    #         self._round_number += 1

    #         undeclared_winners = [
    #             entry for entry in self._entries_still_in_race
    #             if len(entry.voters) >= self._min_num_voters_to_win and not entry.has_won
    #         ]

    #         declared_winners_still_with_surplus = [
    #             winner for winner in self._winners
    #             if len(winner.voters) > self._min_num_voters_to_win
    #         ]

    #         if undeclared_winners:
    #             # declare all new winners
    #             self._run_winner_declaration_round(undeclared_winners)
    #         elif declared_winners_still_with_surplus:
    #             # There are no new winners, but some existing winners' Voters have not been
    #             # redistributed yet. Move one of those winner's surplus votes.
    #             # Conducting the reallocations after marking all winners reduces the amount of
    #             # wasted votes. If, say, entry 1 and entry 2 both won in the same round, then the
    #             # surplus votes of entry 1 will not move to entry 2 (since entry 2 was removed from
    #             # the race already).
    #             self._run_winner_reallocation_round(declared_winners_still_with_surplus)
    #         else:
    #             # there are no winners in the race, and all winners votes have been reallocated;
    #             # remove one of the last-place entries from the race
    #             self._run_elimination_round()

    #         self._write_current_round_to_spreadsheet(output_file_name_prefix)
    #         if self.verbose:
    #             self._print_chart_to_console()

    #         # special case: if we still have to crown, say, 10 winners and there are only
    #         # 10 Entries left, then those 10 Entries are the winners
    #         # (situations like this can happen if lots of Voters have exhausted their ballots)
    #         if len(self._entries_still_in_race) + len(self._winners) == self._num_winners:
    #             if self.verbose:
    #                 print(
    #                     f"* because there are {len(self._entries_still_in_race)} entries left"
    #                     f" in the race and there are still {self._num_winners - len(self._winners)}"
    #                     " winners left to find,\nthe remaining entries are crowned as winners"
    #                 )

    #             for entry_still_in_race in self._entries_still_in_race:
    #                 self._winners.append(entry_still_in_race)
    #                 entry_still_in_race.has_won = True
    #             break

    #     if self.verbose:
    #         print()
    #         print(
    #             f"* all {len(self._winners)}/{self._num_winners} winners have been found,"
    #             f" so the contest is over"
    #         )
    #         print(f"WINNERS: {[winner.name for winner in self._winners]}")
    #     return self._winners