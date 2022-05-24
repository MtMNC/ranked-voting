# Ranked Voting in Google Forms and Discourse

## Introduction

These scripts run ranked voting contests on data from Google Forms or [Discourse](https://www.discourse.org).

They were originally written to run instant-runoff voting for BIONICLE canon contests on the [TTV Message Boards](https://board.ttvchannel.com/). Those boards run on Discourse, and TTV ran the contests using Discourse's standard poll system. The scripts grabbed voting data using the Discourse API and ran [instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting) to determine the winner.

After community feedback, TTV switched voting systems to [Tideman's alternative method](https://en.wikipedia.org/wiki/Tideman_alternative_method). Due to external factors, TTV cancelled their canon contests before using the new voting system. The YouTube channel [DuckBricks](https://www.youtube.com/c/DuckBricks) then began new, non-canon BIONICLE contests where users vote through Google Forms.

In the current use case, the scripts take in voting data that has been pre-downloaded from Google Forms. They process this data into a usable form and run Tideman's alternative method to determine a winner. By running different scripts, users can easily download data from Discourse instead of Google Forms or run instant-runoff voting instead of Tideman's alternative method.

## Voting systems

Ranked choice elections can be run in many ways. These scripts help run contests using variants of the [single transferable vote](https://en.wikipedia.org/wiki/Single_transferable_vote) (STV) or [Tideman's alternative method](https://en.wikipedia.org/wiki/Tideman_alternative_method).

### [Tideman's alternative method](https://en.wikipedia.org/wiki/Tideman_alternative_method)
If this implementation seeks to identify $w$ winners of a contest, then it will identify the winners as the members of the unique dominating set of size $w$. (If a candidate is inside the dominating set, then it would beat any candidate outside the set in a 1v1 match.) Therefore this method is a [Condorcet method](https://en.wikipedia.org/wiki/Condorcet_method).

If a dominating set of size $w$ does not exist, then the method finds the unique smallest dominating set of size $>w$ and attempts to eliminate the last-place candidates through a round of [instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting). If this process still results in more than $w$ winners, then a new dominating set is found on the remaining candidates, and the process repeats. The method terminates when either $w$ entries remain or no more entries can be eliminated.

Variants of Tideman's alternative method differ in how they handle ties for last place during an instant-runoff round. This implementation sorts the last-place entries by their [Borda counts](https://en.wikipedia.org/wiki/Borda_count). It first eliminates all candidates with the lowest Borda count, followed by all candidates with the second-lowest Borda count, etc. If, at any point, removing all candidates with the same Borda count would result in fewer than $w$ winners, then they are not eliminated, a new dominating set is found on the remaining candidates, and the process repeats.

### [Single transferable vote](https://en.wikipedia.org/wiki/Single_transferable_vote)
Because this implementation of STV uses the [Droop quota](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Droop_quota) to determine its winner, it is an extension of [instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting) (IRV). In contests with one winner, this STV implementation behaves identically to IRV. Unlike IRV, STV can also handle contests with multiple winners.

There are many variants of STV. Here are the details of this specific implementation.
* Winners are identified when their vote count meets or exceeds the [Droop quota](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Droop_quota).
* Surplus votes are selected randomly. For example, if an entry has 160 votes and only needed 120 to win, then 40 of the entry's voters are selected at random. Those 40 voters discard their old vote and, if they have a next choice, they vote for it.
* If multiple winners have surplus votes, then those votes are reallocated one winner at a time in random order (rather than all during one round).
* If multiple entries are in last place during an elimination round, then those entries are eliminated one a time in random order (rather than all during one round).
* Voters can only vote for entries that were still in the race (that had neither won nor been eliminated) as of the start of the current round.
* If a voter assigned multiple rankings to the same entry, then only the top ranking counts.

## Instructions

### Collecting votes

These scripts support contests run in Google Forms and in [Discourse](https://www.discourse.org). Consult the appropriate instructions below.

#### Google Forms

##### Creating polls

Set up one form for each contest. Each question in the form should correspond to a single ranking in the contest. Voters rank each entry by voting for one option in each question. The questions should be ordered from most to least favorite.

For example, if the contest has 10 entries and voters can vote for their favorite 3, then set up 3 questions representing rankings 1-3. Each question should have 10 radio buttons or a dropdown with 10 options, one for each entry. Voters should select their favorite entry in the ranking 1 question, then their second favorite entry in the ranking 2 question, and finally their third favorite entry in the ranking 3 question.

##### Downloading voting data

Download the form's output as a CSV file using Google Sheets. Then, reformat that data by running `python create_voter_spreadsheet_google_forms.py`.

When prompted, enter the path to the input CSV file.

The script will download the topic's voting data and save it in `raw_vote_data_form_{INPUT_FILE_NAME_WITHOUT_EXTENSION}.csv`. Each row represents a user, and each column represents a contest entry. Each cell contains the ranking that the row's user assigned to the column's contest entry.

You can edit this spreadsheet to add, remove, or edit votes. Of course, with great power comes great responsibility.

#### Discourse

##### Creating polls

Set up one poll for each ranking in the contest. Each poll should contain options for every entry. Voters rank each entry by voting for one option in each poll. Note that the poll for ranking i should have its name attribute set to `poll_i`. (The polls should have those names by default if they are ordered so the ranking 1 poll comes first.)

For example, if the contest has 10 entries and voters can vote for their favorite 3, then set up 3 polls representing rankings 1-3. Each poll should have 10 radio buttons, one for each entry. Voters should select their favorite entry in the ranking 1 poll, their second favorite entry in the ranking 2 poll, and their third favorite entry in the ranking 3 poll.

##### Getting an API key

`create_voter_spreadsheet_discourse.py` fetches data from the Discourse API, which requires appropriate credentials. Get an API key through the Discourse admin panel. Save it in a file called `api_credentials.txt` located in the same folder as `create_voter_spreadsheet_discourse.py`. The file should contain the API key, then a space, then the key's corresponding username, as shown below.

```
key username
```

If you already have a voting data spreadsheet, then you do not need API credentials.

##### Downloading voting data

Once you have saved your API token, you can download voting data by running `python create_voter_spreadsheet_discourse.py`.

When prompted, enter the id of the poll topic. (The topic id is the number in the topic's URL.) All of the polls should be in the topic's first post.

The script will download the topic's voting data and save it in `raw_vote_data_topic_{TOPIC_ID}.csv`. Each row represents a user, and each column represents a contest entry. Each cell contains the ranking that the row's user assigned to the column's contest entry.

All of the following steps pull voting data from this spreadsheet, not from the Discourse API. You can edit this spreadsheet to add, remove, or edit votes. Of course, with great power comes great responsibility.

Note that `python create_voter_spreadsheet_discourse.py` assumes you want to pull data from the TTV Message Boards. The script can be generalized quite easily by finding and replacing its relevant URLs.

### Identifying winners

Once you have a voting data spreadsheet (made by `create_voter_spreadsheet_discourse.py` or `create_voter_spreadsheet_google_forms.py`), you can find the contest's results.

Depending on which voting system you want to use, either run `python find_contest_winners_tideman.py` or `python find_contest_winners_stv.py`. When prompted, enter the path to the voting data spreadsheet. Next, enter a spreadsheet prefix. (The script will use this prefix when naming any CSV files it writes.) Finally, enter the number of desired winners.

The script will simulate the contest. During each round, it will print out a description of the round to the console, and it will also write CSV files containing detailed voting breakdowns for that round.