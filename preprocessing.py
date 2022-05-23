import csv

"""
Helper functions for preprocessing voter data.
"""

def create_voter_spreadsheet(votes, entry_names, output_spreadsheet_file_name, verbose=True):
    """
    Given a votes dictionary of the form

    votes[voter_id][entry_name] = ranking

    and a list containing the entry names,
    construct a spreadsheet at the given path where every row is a user, every column is a contest
    entry, and each cell is the ranking that the row's user assigned to the column's contest entry.
    """

    if verbose:
        print(f"Writing data to {output_spreadsheet_file_name}...", end="", flush=True)

    with open(output_spreadsheet_file_name, "w", newline="") as spreadsheet:
        writer = csv.writer(spreadsheet, delimiter=",")

        writer.writerow(["user"] + entry_names)

        for username in votes.keys():
            user_votes = []
            for entry_name in entry_names:
                if entry_name in votes[username]:
                    # user voted in the poll; add its ranking
                    user_votes.append(votes[username][entry_name])
                else:
                    user_votes.append(None)

            writer.writerow([username] + user_votes)

    if verbose:
        print(" done.")
