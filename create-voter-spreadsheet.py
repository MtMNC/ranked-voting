import csv
import math
import requests
import time

# In Discourse, voters.json takes in a poll and returns a list of users who voted for each option in
# that poll. It returns those users in batches of size POLL_API_MAX_USER_LIMIT.
# So, if some poll option received POLL_API_MAX_USER_LIMIT*3 votes, then you would have to query
# voters.json 3 times.
# See https://github.com/discourse/discourse/blob/e0d9232259f6fb0f76bca471c4626178665ca24a/plugins/poll/plugin.rb#L166
NUM_VOTES_PER_API_REQUEST = 50


# how long (in seconds) to wait between API requests (to stay on good terms with the website)
SECONDS_BETWEEN_API_REQUESTS = 3


def get_poll_data_from_post(post_id, api_headers, verbose=True):
    """
    Grab data (poll names, option ids and names, vote counts, etc.) for all of the polls in the
    given post.
    Note this output does not include the actual users who voted in each poll.
    """

    post_url = "https://board.ttvchannel.com/posts/" + post_id + ".json"

    if verbose:
        print("Fetching poll data from " + post_url + "....", end="", flush=True)
    polls = requests.get(post_url, headers=api_headers).json()["polls"]
    if verbose:
        print(" done." )
        print("Found " + str(len(polls)) + " polls in post " + str(post_id) + "." )

    return polls


def create_voter_dictionary(post_id, api_headers, polls, verbose=True):
    """
    Grab the voter data from all of the given poll data (produced by get_poll_data_from_post).
    Return the data as a dictionary where each key is a username and each value is a list of
    that user's votes.
    Each vote is stored as a dict where the key is a poll name and the value is the option that
    the user voted for.
    NOTE: This method assumes each voter vote for at most one option per poll.
    """

    if verbose:
        print("Fetching and processing vote data...")

    votes = {}

    for poll_index, poll in enumerate(polls):

        option_names = {}
        for option in poll["options"]:
            option_names[option["id"]] = option["html"]


        # Grab the users who voted for each option, in batches of size POLL_API_MAX_USER_LIMIT
        # at a time (that's the upper limit batch size enforced by the API).

        # the most votes that any of the poll's options received
        max_num_votes_to_collect = max([option["votes"] for option in poll["options"]])
        # the amount of API requests it takes to gather max_num_votes_to_collect votes in batches of
        # size POLL_API_MAX_USER_LIMIT
        num_api_requests = math.ceil(max_num_votes_to_collect / NUM_VOTES_PER_API_REQUEST)

        if verbose:
            print("\tPoll " + poll["name"] + " (" + str(poll_index + 1) + "/" + str(len(polls)) + ")")

        for i in range(num_api_requests):
            vote_batch_url = "https://board.ttvchannel.com/polls/voters.json" \
                            + "?post_id=" + post_id \
                            + "&poll_name=" + poll["name"] \
                            + "&limit=" + str(NUM_VOTES_PER_API_REQUEST) \
                            + "&page=" + str(i + 1)
            if verbose:
                print("\t\tFetching vote data from " + vote_batch_url + "...", end="", flush=True)

            vote_batch = requests.get(vote_batch_url, headers=api_headers).json()["voters"]

            if verbose:
                print(" processing data...", end="", flush=True)

            for option_id, users in vote_batch.items():
                for user in users:
                    if user["username"] not in votes:
                        votes[user["username"]] = {}

                    votes[user["username"]][poll["name"]] = option_names[option_id]

            if verbose:
                print(" done.")

            time.sleep(SECONDS_BETWEEN_API_REQUESTS)

    if verbose:
        print("Done fetching and processing vote data.")

    return votes


def create_spreadsheet_from_voter_dictionary(polls, votes, spreadsheet_file_name, verbose=True):
    """
    Given poll data from get_poll_data_from_post and a voter dictionary from
    create_spreadsheet_from_voter_dictionary,
    construct a spreadsheet at the given path where every row is a user, every column is a poll
    (contest entry),
    and each cell represents which rank the row's user assigned to in the column's contest entry.
    """

    if verbose:
        print("Writing data to " + spreadsheet_file_name + "...", end="", flush=True)

    with open(spreadsheet_file_name, "w") as spreadsheet:
        writer = csv.writer(spreadsheet, delimiter=",")

        writer.writerow(["user"] + [poll["name"] for poll in polls])

        for username in votes.keys():
            user_votes = []
            for poll in polls:
                if poll["name"] in votes[username]:
                    # user voted in the poll
                    user_votes.append(votes[username][poll["name"]])
                else:
                    user_votes.append(None)

            writer.writerow([username] + user_votes)

    if verbose:
        print(" done.")


def main():
    with open("api-credentials.txt") as token_file:
        api_key, api_username = token_file.read().split()

    api_headers = {"Api-Key": api_key, "Api_Username": api_username}

    post_id = input("Enter the post's id: ")
    spreadsheet_file_name = "raw-vote-data-post-" + post_id + ".csv"
    polls = get_poll_data_from_post(post_id, api_headers)
    votes = create_voter_dictionary(post_id, api_headers, polls)
    create_spreadsheet_from_voter_dictionary(polls, votes, spreadsheet_file_name)


if __name__ == "__main__":
    main()
