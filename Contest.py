from Entry import Entry
from Voter import Voter
import csv

class Contest():
    """
    A Contest contains Voters who have assigned rankings (numbers) to various Entries.
    It also has a desired number of finalists.
    """


    def __init__(self, num_finalists = 1, verbose=True):
        self.num_finalists = num_finalists
        self.verbose = verbose
        self.voters = []
        self.entries = []


    def populate_from_spreadsheet(self, spreadsheet_file_name):
        """
        Grab voter data from the given spreadsheet
        (prepared by create_spreadsheet_from_voter_dictionary in create-voter-spreadsheet.py)
        and populate the Contest with the relevant Voters and Entries.
        """

        if self.verbose:
            print("Populating contest with voter data from " + spreadsheet_file_name + "...",
                end="", flush=True)

        with open(spreadsheet_file_name, "r") as spreadsheet:
            reader = csv.reader(spreadsheet, delimiter=",")

            header = next(reader)
            entry_names = header[1:]

            if self.num_finalists >= len(entry_names):
                raise ValueError("A Contest must have fewer finalists then entries. " \
                    + "This Contest seeks to produce " + str(self.num_finalists) + " finalists " \
                    + "but has only " + str(len(entry_names)) + " entries.")

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
