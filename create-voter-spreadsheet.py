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


def get_poll_data_from_topic(topic_id, api_headers, verbose=True):
    """
    Grab data (poll names, option ids and names, vote counts, etc.) for all of the polls in the
    first post of the given topic. Return the JSON represening the first post.

    Note this output does not include the actual users who voted in each poll.
    """

    topic_url = "https://board.ttvchannel.com/t/" + topic_id + ".json"

    if verbose:
        print("Fetching poll data from " + topic_url + "....", end="", flush=True)

    topic = requests.get(topic_url, headers=api_headers).json()

    first_post = topic["post_stream"]["posts"][0]

    if verbose:
        print(" done." )
        print("Found " + str(len(first_post["polls"])) + " polls in the first post of topic " \
        + str(topic_id) + " (" + topic["title"] + ")." )

    return first_post


def create_voter_dictionary(post, api_headers, verbose=True):
    """
    Grab the voter data from all of the given poll data (produced by get_poll_data_from_post).
    Return the data as a dictionary of user votes keyed by username.
    Each vote is a dictionary of rankings (numbers) keyed by entry name.
    So, the output follows this format:
    output[username][entry_name] = ranking

    NOTE: This method assumes that each poll corresponds to a particular ranking and that entries
    are listed in the same order across all polls.
    """

    if verbose:
        print("Fetching and processing vote data...")

    votes = {}

    for poll_index, poll in enumerate(post["polls"]):

        # In the i-th poll (indexed from 1), users vote for which entry should get ranking i.
        # For instance, in the 3st poll users assign ranking 3 to an entry (users pick their
        # 3rd-favorite entry).
        ranking = poll_index + 1

        # In each poll, users select one entry. Each option in the poll corresponds to a particular
        # entry.
        # entry_names_keyed_by_id contains the names of the contest entries, each keyed by the id of
        # their option in this particular poll.
        entry_names_keyed_by_id = {}
        for option in poll["options"]:
            entry_names_keyed_by_id[option["id"]] = option["html"]

        # Grab the users who voted for each option, in batches of size POLL_API_MAX_USER_LIMIT
        # at a time (that's the upper limit batch size enforced by the API).

        # the most votes that any of the poll's options received
        max_num_votes_to_collect = max([option["votes"] for option in poll["options"]])
        # the amount of API requests it takes to gather max_num_votes_to_collect votes in batches of
        # size POLL_API_MAX_USER_LIMIT
        num_api_requests = math.ceil(max_num_votes_to_collect / NUM_VOTES_PER_API_REQUEST)

        if verbose:
            print("\tPoll " + poll["name"] \
                + " (" + str(poll_index + 1) + "/" + str(len(post["polls"])) + ")")

        for i in range(num_api_requests):
            vote_batch_url = "https://board.ttvchannel.com/polls/voters.json" \
                            + "?post_id=" + str(post["id"]) \
                            + "&poll_name=" + poll["name"] \
                            + "&limit=" + str(NUM_VOTES_PER_API_REQUEST) \
                            + "&page=" + str(i + 1)

            if verbose:
                print("\t\tFetching vote data from " + vote_batch_url + "...", end="", flush=True)

            vote_batch = requests.get(vote_batch_url, headers=api_headers).json()["voters"]

            if verbose:
                print(" processing data...", end="", flush=True)

            for option_id, users in vote_batch.items():
                entry_name = entry_names_keyed_by_id[option_id]

                for user in users:
                    username = user["username"]
                    if username not in votes:
                        votes[username] = {}

                    votes[username][entry_name] = ranking

            if verbose:
                print(" done.")

            time.sleep(SECONDS_BETWEEN_API_REQUESTS)

    if verbose:
        print("Done fetching and processing vote data.")

    return votes


def create_spreadsheet_from_voter_dictionary(post, votes, spreadsheet_file_name, verbose=True):
    """
    Given poll data from get_poll_data_from_post and a voter dictionary from
    create_spreadsheet_from_voter_dictionary,
    construct a spreadsheet at the given path where every row is a user, every column is a contest
    entry, and each cell is the ranking that the row's user assigned to the column's contest entry.
    """

    if verbose:
        print("Writing data to " + spreadsheet_file_name + "...", end="", flush=True)

    entry_names = [option["html"] for option in post["polls"][0]["options"]]

    with open(spreadsheet_file_name, "w", newline="") as spreadsheet:
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


def main():
    with open("api-credentials.txt") as token_file:
        api_key, api_username = token_file.read().split()

    api_headers = {"Api-Key": api_key, "Api_Username": api_username}

    topic_id = input("Enter the topic's id: ")
    spreadsheet_file_name = "raw-vote-data-topic-" + topic_id + ".csv"
    post = get_poll_data_from_topic(topic_id, api_headers)
    votes = create_voter_dictionary(post, api_headers)
    create_spreadsheet_from_voter_dictionary(post, votes, spreadsheet_file_name)


if __name__ == "__main__":
    main()
