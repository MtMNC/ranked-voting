import csv
from pathlib import Path

from preprocessing import create_voter_spreadsheet

def get_votes_dictionary_and_entry_names(input_file_name, verbose=True):
    """
    Grab the voter data from the given spreadsheet and return a tuple of the form

    (votes, entry_names).

    where entry_names is a set of the names of all entries that received at least one vote
    and votes is a dictionary containing votes stored in the form

    votes[voter_id][entry_name] = ranking,

    where each voter is identified by a voter_id (row number and timestamp).

    NOTE: This method assumes that the poll for rank i is question i in the spreadsheet
    (indexed from 1).
    """

    if verbose:
        print("Processing vote data...")

    votes = {}
    entry_names = set()

    with open(input_file_name, "r", newline="") as spreadsheet:
        reader = csv.reader(spreadsheet, delimiter=",")

        # leftmost column (column 0) contains timestamp, and all others contain rankings
        num_rankings = len(next(reader)) - 1

        for i, row in enumerate(reader):
            voter_id = f"Voter {i + 1} ({row[0]})"
            votes[voter_id] = {}

            for ranking in range(1, num_rankings + 1):
                entry_name = row[ranking]

                if entry_name:
                    entry_names.add(entry_name)
                    votes[voter_id][entry_name] = ranking

    if verbose:
        print("Done processing vote data.")

    return (votes, list(entry_names))


def main():
    input_spreadsheet_file_name = input("Enter the path to the input spreadsheet: ")
    output_spreadsheet_file_name = f"raw_vote_data_{Path(input_spreadsheet_file_name).stem}.csv"
    votes, entry_names = get_votes_dictionary_and_entry_names(input_spreadsheet_file_name)

    create_voter_spreadsheet(votes, entry_names, output_spreadsheet_file_name)


if __name__ == "__main__":
    main()
