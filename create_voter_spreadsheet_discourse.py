import math
import requests
import time

from preprocessing import create_voter_spreadsheet

# In Discourse, voters.json takes in a poll and returns a list of users who voted for each option in
# that poll. It returns those users in batches of size NUM_VOTES_PER_API_REQUEST.
# So, if some poll option received NUM_VOTES_PER_API_REQUEST*3 votes, then you would have to query
# voters.json 3 times.
# See https://github.com/discourse/discourse/blob/e0d9232259f6fb0f76bca471c4626178665ca24a/plugins/poll/plugin.rb#L166
NUM_VOTES_PER_API_REQUEST = 50


# how long (in seconds) to wait between API requests (to stay on good terms with the website)
SECONDS_BETWEEN_API_REQUESTS = 3


# The URL from which to request vote info from Discourse
DISCOURSE_VOTES_LOCATION = "https://board.ttvchannel.com/polls/voters.json"


def get_poll_data_from_topic(topic_id, api_headers, verbose=True):
    """
    Grab data (poll names, option ids and names, vote counts, etc.) for all of the polls in the
    first post of the given topic. Return the JSON represening the first post.

    Note this output does not include the actual users who voted in each poll.
    """

    topic_url = "https://board.ttvchannel.com/t/" + topic_id + ".json"

    if verbose:
        print(f"Fetching poll data from {topic_url}....", end="", flush=True)

    topic = requests.get(topic_url, headers=api_headers).json()

    first_post = topic["post_stream"]["posts"][0]

    if verbose:
        print(" done." )
        print(
            f"Found {len(first_post['polls'])} polls"
            f" in the first post of topic {topic_id} ({topic['title']})."
        )

    return first_post


def get_voter_dictionary(post, api_headers, verbose=True):
    """
    Grab the voter data from all of the given poll data (produced by get_poll_data_from_topic).
    Return the data as a dictionary of user votes keyed by username.
    Each vote is a dictionary of rankings (numbers) keyed by entry name.
    So, the voter dictionary follows this format:
    votes[username][entry_name] = ranking

    NOTE: This method assumes that each poll corresponds to a particular ranking and that entries
    are listed in the same order across all polls.

    NOTE: This method assumes that the poll for rank i is titled poll_i.
    """

    if verbose:
        print("Fetching and processing vote data...")

    votes = {}

    for poll_index, poll in enumerate(post["polls"]):

        # In the i-th poll (indexed from 1), users vote for which entry should get ranking i.
        # For instance, in the 3st poll users assign ranking 3 to an entry (users pick their
        # 3rd-favorite entry).
        # This assumes that the poll for ranking i has its name attribute set to poll_i.
        ranking = int(poll["name"][5:])

        # In each poll, users select one entry. Each option in the poll corresponds to a particular
        # entry.
        # entry_names_keyed_by_id contains the names of the contest entries, each keyed by the id of
        # their option in this particular poll.
        entry_names_keyed_by_id = {}
        for option in poll["options"]:
            entry_names_keyed_by_id[option["id"]] = option["html"]

        # Grab the users who voted for each option, in batches of size NUM_VOTES_PER_API_REQUEST
        # at a time (that's the upper limit batch size enforced by the API).

        # the most votes that any of the poll's options received
        max_num_votes_to_collect = max(option["votes"] for option in poll["options"])
        # the amount of API requests it takes to gather max_num_votes_to_collect votes in batches of
        # size NUM_VOTES_PER_API_REQUEST
        num_api_requests = math.ceil(max_num_votes_to_collect / NUM_VOTES_PER_API_REQUEST)

        if verbose:
            print(
                f"\tPoll {poll['name']} (poll {poll_index + 1}/{len(post['polls'])},"
                f" where users vote for ranking {ranking})"
            )

        for i in range(num_api_requests):
            params = {
                "post_id": post["id"],
                "poll_name": poll["name"],
                "limit": NUM_VOTES_PER_API_REQUEST,
                "page": i + 1
            }

            if verbose:
                print(f"\t\tFetching vote data from {DISCOURSE_VOTES_LOCATION}...",
                    end="", flush=True)

            vote_batch = requests.get(DISCOURSE_VOTES_LOCATION,
                headers=api_headers, params=params).json()["voters"]

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


def main():
    with open("api_credentials.txt") as token_file:
        api_key, api_username = token_file.read().split()

    api_headers = {"Api-Key": api_key, "Api_Username": api_username}

    topic_id = input("Enter the topic's id: ")
    output_spreadsheet_file_name = f"raw_vote_data_topic_{topic_id}.csv"
    post = get_poll_data_from_topic(topic_id, api_headers)
    votes = get_voter_dictionary(post, api_headers)
    entry_names = [option["html"] for option in post["polls"][0]["options"]]

    create_voter_spreadsheet(votes, entry_names, output_spreadsheet_file_name)


if __name__ == "__main__":
    main()
