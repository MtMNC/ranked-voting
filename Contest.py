from Entry import Entry
from Voter import Voter
import csv
import itertools
import math
import random

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
    ELIMINATED_VOTER_COLUMN_NAME = "voters who stopped as all their remaining picks left the race"


    def __init__(self, verbose=True):
        self.verbose = verbose
        self.voters = []
        self.entries = []


    def _print_round_name(self):
        print("#" * Contest.NUM_CHARS_IN_ROUND)
        print((" ROUND " + str(self._round_number) + " ").center(Contest.NUM_CHARS_IN_ROUND, "#"))
        print("#" * Contest.NUM_CHARS_IN_ROUND)

    def populate_from_spreadsheet(self, input_file_name):
        """
        Grab voter data from the given spreadsheet
        (prepared by create_spreadsheet_from_voter_dictionary in create-voter-spreadsheet.py)
        and populate the Contest with the relevant Voters and Entries.
        """

        if self.verbose:
            print("Populating contest with voter data from " + input_file_name + "...",
                end="", flush=True)

        with open(input_file_name, "r") as spreadsheet:
            reader = csv.reader(spreadsheet, delimiter=",")

            header = next(reader)
            entry_names = header[1:]

            # construct Entries
            for entry_name in entry_names:
                # self.entries[i] contains the entry from column i+1
                # (not column i because the leftmost column contains user info, not entry info)
                self.entries.append(Entry(entry_name))

            # construct Voters and record their votes
            for row in reader:
                voter_name = row[0]
                # voter_rankings[i] contains the voter's ranking for entry self.entries[i]
                voter_rankings = row[1:]

                voter = Voter(voter_name)

                for i, ranking in enumerate(voter_rankings):
                    if ranking:
                        # the ranks are stored in user_rankings as a list of strings, so cast them
                        # to ints for use as indexes
                        voter.rank(self.entries[i], int(ranking))

                self.voters.append(voter)

        if self.verbose:
            print(" done.")


    def _write_current_round_to_spreadsheet(self, output_file_name_prefix):
        """
        Write out the contest's current status to a spreadsheet at the path
        {output_file_name_prefix}-round{round_number}.csv

        The first column contains the names of those Voters who did not provide any valid votes.
        The second column contains the names of those Voters who provided valid votes, but only for
        entries that were eliminated already.
        Each of the remaining columns represents an Entry that's still in the running.
        Each cell in those columns represents a Voter who voted for that column's Entry.
        Those cells contain the Voter name, the rank they gave the Entry, and the round during
        which they voted for the Entry
        """

        input_file_name = output_file_name_prefix + str(self._round_number) + ".csv"

        if self.verbose:
            print("Writing round " + str(self._round_number) + " vote data to " \
                + input_file_name + "...", end="", flush=True)

        with open(input_file_name, "w") as spreadsheet:
            writer = csv.writer(spreadsheet, delimiter=",")

            header = [Contest.INVALID_VOTER_COLUMN_NAME, Contest.ELIMINATED_VOTER_COLUMN_NAME] + \
                [entry.name for entry in self.entries]
            writer.writerow(header)

            # construct a list for each entry column
            entry_columns = []
            for entry in self.entries:
                # each column is filled with data on the user that voted for that Entry
                # and which rank the user gave that Entry
                entry_column = []
                for voter in entry.voters:
                    voter_info_string = voter.name + ": round " \
                        + str(voter.round_when_last_moved) + ", rank " \
                        + str(voter.get_ranking_of_entry(entry))
                    entry_column.append(voter_info_string)

                entry_columns.append(entry_column)

            # rearrange the body of the spreadsheet into a list of rows (so each list passed in as
            # an argument becomes a column in the final body)
            body = itertools.zip_longest([voter.name for voter in self._voters_with_no_valid_votes],
                [voter.name + ": round " + str(voter.round_when_last_moved)
                for voter in self._voters_with_no_remaining_valid_votes],
                *entry_columns, fillvalue="")
            for row in body:
                writer.writerow(row)

        if self.verbose:
            print(" done.")


    def _print_chart_to_console(self):
        """
        Output a chart of the current votes to the console.
        """

        bar_names = [len(entry.name) for entry in self.entries]
        longest_entry_name_length = max([len(entry.name) for entry in self.entries])

        print()
        for entry in self.entries:
            # once entry has won or lost, we never actually removed its Voters (there's no need to)
            # so len(entry.voters) won't actually reflect entry's true number of Voters
            if entry.has_won:
                status_indicator = "WON"
            elif entry.has_lost:
                status_indicator = "LOST"
            else:
                status_indicator = ""

            vote_fraction = len(entry.voters) / self._num_valid_voters

            # bar in chart showing vote count
            num_chars_in_vote_bar = round(Contest.NUM_CHARS_IN_FULL_VOTE_BAR * vote_fraction)
            vote_bar = "\u25A0" * num_chars_in_vote_bar

            # text showing percentage of voters voting for this entry
            percentage_text = str(round(100 * vote_fraction, 1)) + "%"

            # text showing fraction of voters voting for this entry
            fraction_text = str(len(entry.voters)) + "/" + str(self._num_valid_voters)

            # text showing how much the count changed this round
            if entry.num_voters_gained_in_current_round >= 0:
                change_text_sign = "+"
            else:
                change_text_sign = ""
            change_text = change_text_sign + str(entry.num_voters_gained_in_current_round) \
                + " this round"

            entry_output = status_indicator.ljust(6)
            entry_output += entry.name.ljust(longest_entry_name_length + 2)
            entry_output += vote_bar + " " + percentage_text
            entry_output += " (" + fraction_text
            entry_output += "; " + change_text + ")"
            print(entry_output)

        print()

        # print info about unused voters
        print(Contest.INVALID_VOTER_COLUMN_NAME + ": " \
            + str(len(self._voters_with_no_valid_votes)))
        print(Contest.ELIMINATED_VOTER_COLUMN_NAME + ": " \
            + str(len(self._voters_with_no_remaining_valid_votes)) \
            + " (+" + str(self._num_voters_exhausted_in_current_round) + " this round)")
        print()


    def _allocate_voters(self, voters_to_allocate):
        """
        Allocate the given Voters to their first-choice entry.
        If they don't have a first choice, add them to self._voters_with_no_valid_votes.
        """
        for voter in voters_to_allocate:
            # prepare voter to iterate through their valid votes
            iter(voter)

            favorite_entry = next(voter)
            if favorite_entry is None:
                # the voter cast no valid votes
                self._voters_with_no_valid_votes.append(voter)
            else:
                favorite_entry.voters.append(voter)
                favorite_entry.num_voters_gained_in_current_round += 1

            voter.round_when_last_moved = self._round_number


    def _reallocate_voters(self, current_entry, voters_to_reallocate):
        """
        Reallocate the given Voters to their next-choice entry.
        If they don't have a next choice, add them to self._voters_with_no_remaining_valid_votes.
        """

        for voter in voters_to_reallocate:
            next_favorite_entry = next(voter)
            if next_favorite_entry is None:
                # the voter cast no valid votes
                self._voters_with_no_remaining_valid_votes.append(voter)
                self._num_voters_exhausted_in_current_round += 1
            else:
                next_favorite_entry.voters.append(voter)
                next_favorite_entry.num_voters_gained_in_current_round += 1

            voter.round_when_last_moved = self._round_number

        # for bookkeeping purposes, remove all the Voters from the old Entry
        # NOTE not the most efficient but doesn't really need to be
        current_entry.voters = [voter for voter in current_entry.voters
            if voter not in voters_to_reallocate]

        current_entry.num_voters_gained_in_current_round -= len(voters_to_reallocate)


    def _run_first_round(self):
        """
        Run the first round of the contest. In this round, everybody votes for their first choice.
        """

        if self.verbose:
            self._print_round_name()

        # entries have not yet gained any votes this round
        for entry in self.entries:
            entry.num_voters_gained_in_current_round = 0
        self._num_voters_exhausted_in_current_round = 0

        self._allocate_voters(self.voters)

        # all Entries are still in the race; even if an Entry got no votes, we say it is still in,
        # and we'll just remove it in a later round
        for entry in self.entries:
            self._entries_still_in_race.append(entry)

        if self.verbose:
            print("* all voters voted for their top choice")


    def _run_winner_declaration_round(self, undeclared_winners):
        """
        Run a "winner declaration" round of the contest. In this round, all Entries tied for the
        most votes that haven't won yet are marked as winners.
        """

        if self.verbose:
            self._print_round_name()

        # entries have not yet gained any votes this round
        for entry in self.entries:
            entry.num_voters_gained_in_current_round = 0
        self._num_voters_exhausted_in_current_round = 0

        for winner in undeclared_winners:
            self._entries_still_in_race.remove(winner)
            self._winners.append(winner)
            winner.has_won = True
            if self.verbose:
                print("* " + winner.name + " won (earned " + str(len(winner.voters)) \
                    + " votes, needed " + str(self._min_num_voters_to_win) + ")")


    def _run_winner_reallocation_round(self, declared_winners_still_with_surplus):
        """
        Run a "winner reallocation" round of the contest. In this round, one of the winning Entries
        that hasn't reallocated its Voters is selected at random and reallocates its Voters.
        """

        if self.verbose:
            self._print_round_name()

        # entries have not yet gained any votes this round
        for entry in self.entries:
            entry.num_voters_gained_in_current_round = 0
        self._num_voters_exhausted_in_current_round = 0

        winner = random.choice(declared_winners_still_with_surplus)
        num_surplus_voters = len(winner.voters) - self._min_num_voters_to_win
        surplus_voters = random.sample(winner.voters, k=num_surplus_voters)

        self._reallocate_voters(winner, surplus_voters)


        if self.verbose:
            print("* only " + str(len(self._winners)) + "/" + str(self._num_winners) \
                + " winners have been found, so winner " + winner.name \
                + " reallocated its " + str(num_surplus_voters) + " surplus votes")


    def _run_elimination_round(self):
        """
        Run an elimination round of the Contest. In this round, a least popular Entry is removed
        from the race, and its Voters vote for their next choice.
        """

        if self.verbose:
            self._print_round_name()

        # entries have not yet gained any votes this round
        for entry in self.entries:
            entry.num_voters_gained_in_current_round = 0
        self._num_voters_exhausted_in_current_round = 0

        # pick a loser at random out of all the bottom vote-getters
        num_voters_for_bottom_entry_still_in_race = min([len(entry.voters)
            for entry in self._entries_still_in_race])
        bottom_entries_still_in_race = [entry for entry in self._entries_still_in_race
            if len(entry.voters) == num_voters_for_bottom_entry_still_in_race]
        loser = random.choice(bottom_entries_still_in_race)

        if self.verbose:
            print("* " + loser.name + " was eliminated as it had the fewest votes (" \
                + str(num_voters_for_bottom_entry_still_in_race) + ")")

        self._entries_still_in_race.remove(loser)
        loser.has_lost = True
        self._reallocate_voters(loser, loser.voters)

        if self.verbose:
            print("* " + loser.name + " reallocated its " \
            + str(num_voters_for_bottom_entry_still_in_race) + " votes")


    def get_winners(self, num_winners, output_file_name_prefix):
        """
        Run the contest using multi-winner instant-runoff voting using the Droop quota and
        random surplus allocation.
        For every round of voting, output a spreadsheet whose columns are entries, with the rows
        populated by users who voted for those entries.
        The contest terminates once self._num_winners winners have won.
        Return the Entry objects representing the winners.
        """

        if num_winners >= len(self.entries):
            raise ValueError("A Contest must have fewer winners then entries. " \
                + "This Contest seeks to produce " + str(num_winners) + " winners " \
                + "but has only " + str(len(self.entries)) + " entries.")

        self._num_winners = num_winners

        # users who cast no valid votes
        self._voters_with_no_valid_votes = []
        # users who cast valid votes, but only for Entries that have been eliminated already
        self._voters_with_no_remaining_valid_votes = []
        # the amount of voters who have had all of their entries eliminated during this round
        self._num_voters_exhausted_in_current_round = 0
        self._entries_still_in_race = []
        self._winners = []
        self._round_number = 1

        # round 1: everyone votes for their top pick
        self._run_first_round()

        # Use the "Droop Quota" as the minimum vote threshold.
        # Say there are v Voters and w winners. An Entry wins once it has so many votes that it's
        # impossible for w other Entries to perform as well as the winner.
        # If an Entry gets exactly v/(w+1) votes, then it is still possible for w other Entries to
        # also get exactly v/(w+1) votes, in which case there would be a (w+1)-way tie.
        # If an Entry gets more than v/(w+1) votes, so at least (v/(w+1)) + 1 votes, then there's
        # no way for w other Entries to perform equally well, as that would imply at least
        # (w+1) * ((v/(w+1)) + 1) = v + w + 1 votes were cast, and that's more than v votes.
        self._num_valid_voters = len(self.voters) - len(self._voters_with_no_valid_votes)
        self._min_num_voters_to_win = math.floor(self._num_valid_voters / (self._num_winners + 1)) + 1

        self._write_current_round_to_spreadsheet(output_file_name_prefix)
        if self.verbose:
            self._print_chart_to_console()

        while len(self._winners) < self._num_winners:
            self._round_number += 1

            undeclared_winners = [entry for entry in self._entries_still_in_race
                if len(entry.voters) >= self._min_num_voters_to_win and not entry.has_won]

            declared_winners_still_with_surplus = [winner for winner in self._winners
                if len(winner.voters) > self._min_num_voters_to_win]

            if undeclared_winners:
                # declare all new winners
                self._run_winner_declaration_round(undeclared_winners)
            elif declared_winners_still_with_surplus:
                # There are no new winners, but some existing winners' Voters have not been
                # redistributed yet. Move one of those winner's surplus votes.
                # Conducting the reallocations after marking all winners reduces the amount of
                # wasted votes. If, say, entry 1 and entry 2 both won in the same round, then the
                # surplus votes of entry 1 will not move to entry 2 (since entry 2 was removed from
                # the race already).
                self._run_winner_reallocation_round(declared_winners_still_with_surplus)
            else:
                # there are no winners in the race, and all winners votes have been reallocated;
                # remove one of the last-place entries from the race
                self._run_elimination_round()

            self._write_current_round_to_spreadsheet(output_file_name_prefix)
            if self.verbose:
                self._print_chart_to_console()

            # special case: if we still have to crown, say, 10 winners and there are only
            # 10 Entries left, then those 10 Entries are the winners
            # (situations like this can happen if lots of Voters have exhausted their ballots)
            if len(self._entries_still_in_race) + len(self._winners) == self._num_winners:
                if self.verbose:
                    print("* because there are " + str(len(self._entries_still_in_race)) \
                        + " entries left in the race and there are still " \
                        + str(self._num_winners - len(self._winners)) \
                        + " winners left to find,\nthe remaining entries are crowned as winners")
                for entry_still_in_race in self._entries_still_in_race:
                    self._winners.append(entry_still_in_race)
                    entry_still_in_race.has_won = True
                break

        if self.verbose:
            print()
            print("* all " + str(len(self._winners)) + "/" + str(self._num_winners) \
                + " winners have been found, so the contest is over")
            print("WINNERS: " + str([winner.name for winner in self._winners]))
        return self._winners
