from contest import Contest

def main():
    input_file_name = input("Enter the path to the voting data spreadsheet (made by create_voter_spreadsheet.py): ")
    contest = Contest()
    contest.populate_from_spreadsheet(input_file_name)
    output_file_name_prefix = input("Enter the prefix that the output spreadsheets will start with: ")
    num_winners = int(input("Enter the desired number of winners for the contest: "))
    contest.get_winners(num_winners, output_file_name_prefix)


if __name__ == "__main__":
    main()
