import csv

from entry import Entry
from voter import Voter

class Contest:
    """
    A Contest contains Voters who have assigned rankings (numbers) to various Entries.
    It also has a desired number of winners.
    Its get_winners method determines ranked choice voting results and returns the winning Entries.
    """


    # how wide in characters the dividers in _print_round_name should be
    NUM_CHARS_IN_DIVIDER = 100


    def __init__(self, verbose=True):
        self.verbose = verbose
        self.voters = []
        self.entries = []


    def _print_round_name(self):
        print("#" * Contest.NUM_CHARS_IN_DIVIDER)
        print(f" ROUND {self._round_number} ".center(Contest.NUM_CHARS_IN_DIVIDER, "#"))
        print("#" * Contest.NUM_CHARS_IN_DIVIDER)


    def populate_from_spreadsheet(self, input_file_name):
        """
        Grab voter data from the given spreadsheet
        (prepared by create_spreadsheet_from_voter_dictionary in create-voter-spreadsheet.py)
        and populate the STVContest with the relevant Voters and Entries.
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

            # construct Voters and record their votes
            for row in reader:
                voter_name = row[0]
                # voter_rankings[i] contains the voter's ranking for entry self.entries[i]
                voter_rankings = row[1:]

                voter = Voter(voter_name, num_distinct_rankings)

                for i, ranking in enumerate(voter_rankings):
                    if ranking:
                        # the ranks are stored in user_rankings as a list of strings, so cast them
                        # to ints for use as indexes
                        voter.rank(self.entries[i], int(ranking))

                self.voters.append(voter)

        if self.verbose:
            print(" done.")


    def get_winners(self):
        """
        Determine and return the Contest's winners.
        """

        raise NotImplementedError

