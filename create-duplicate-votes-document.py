from Contest import Contest
from Voter import Voter

import csv

def create_duplicate_votes_document(contest, document_file_name, verbose=True):
    """
    Take a Contest populated with Voters and Entries.
    Output all of the duplicate voters (voters who assigned multiple entries the same rank),
    along with their duplicate votes, to the given text file.
    Each line of the text file follows this format:
    username: {rank1: [entries, assigned, that, rank], rank2: [entries, assigned, that, rank], etc.}
    """

    if verbose:
        print("Writing duplicate vote data to " + document_file_name + "...", end="", flush=True)

    with open(document_file_name, "w") as document:
        for voter in contest.voters:
            duplicate_votes = voter.get_duplicate_votes()

            if duplicate_votes:
                print(voter.name + ": " + str(duplicate_votes), file=document)

    if verbose:
        print(" done.")


def get_voters_from_spreadsheet(spreadsheet_file_name, verbose=True):
    """
    Grab voter data from the given spreadsheet
    (prepared by create_spreadsheet_from_voter_dictionary in create-voter-spreadsheet.py)
    and return it in a dictionary.
    Each dictionary key is a username, and its value is a Voter representing that user that has
    been populated with all of that user's votes.
    """

    if verbose:
        print("Reading voter data from " + spreadsheet_file_name + "...", end="", flush=True)

    with open(spreadsheet_file_name, "r") as spreadsheet:
        reader = csv.reader(spreadsheet, delimiter=",")

        header = next(reader)
        entry_names = header[1:]

        # key is username, value is Voter populated with that user's votes
        voters = {}
        for row in reader:
            username = row[0]
            user_rankings = row[1:]

            voter = Voter(username)

            for i, user_rank in enumerate(user_rankings):
                if user_rank:
                    # the ranks are stored in user_rankings as a list of strings, so cast them to
                    # ints for use as indexes
                    voter.rank(entry_names[i], int(user_rank))

            voters[username] = voter

    if verbose:
        print(" done.")

    return voters


def main():
    spreadsheet_file_name = input("Enter the path to the voting data spreadsheet: ")
    document_file_name = input("Enter the desired path to the duplicate votes document: ")

    contest = Contest()
    contest.populate_from_spreadsheet(spreadsheet_file_name)

    # voters = get_voters_from_spreadsheet(spreadsheet_file_name)
    create_duplicate_votes_document(contest, document_file_name)


if __name__ == "__main__":
    main()
