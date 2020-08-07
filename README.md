# Single Transferable Vote in Discourse

## Introduction

These scripts help users run [single transferable vote](https://en.wikipedia.org/wiki/Single_transferable_vote) (STV) voting in a [Discourse forum](https://www.discourse.org) using Discourse's standard poll system. They were written for the Helryx contest on the [TTV Message Boards](https://board.ttvchannel.com/), but they can be generalized quite easily by finding and replacing URLs in the scripts. This README does not assume you are familiar with TTV's voting process.

Because this implementation of STV uses the [Droop quota](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Droop_quota) to determine its winner, it is an extension of [instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting) (IRV). In contests with one winner, this STV implementation behaves identically to IRV. Unlike IRV, STV can also handle contests with multiple winners.

## Implementation details
There are many variants of STV. Here are the details of this specific implementation.
* Winners are identified when their vote count meets or exceeds the [Droop quota](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Droop_quota).
* Surplus votes are selected randomly. For example, if an entry has 160 votes and only needed 120 to win, then 40 of the entry's voters are selected at random. Those 40 voters discard their old vote and, if they have a next choice, they vote for it.
* If multiple winners have surplus votes, then those votes are reallocated one winner at a time in random order (rather than all during one round).
* If multiple entries are in last place during an elimination round, then those entries are eliminated one a time in random order (rather than all during one round).
* Voters can only vote for entries that were still in the race (that had neither won nor been eliminated) as of the start of the current round.
* If a voter assigned multiple rankings to the same entry, than only the top ranking counts.

## Instructions

### Creating polls

Set up one poll for each ranking in the contest. Each poll should contain options for every entry. Voters rank each entry by voting for one option in each poll. For example, if the contest has 10 entries and voters can vote for their favorite 3, then set up 3 polls representing rankings 1-3. Each poll should have 10 radio buttons, one for each entry. Voters should select their favorite entry in the ranking 1 poll, their second favorite entry in the ranking 2 poll, and their third favorite entry in the ranking 3 poll. Note that the poll for ranking i should have its name attribute set to `poll_i`. (The polls should have those names by default if they are are ordered so the ranking 1 poll comes first.)

### Determining results

Once the polls close, the scripts can help determine the results.

#### Getting an API key

`create-voter-spreadsheet.py` fetches data from the Discourse API, which requires appropriate credentials. Get an API key through the Discourse admin panel. Save it in a file called `api-credentials.txt` located in the same folder as `create-voter-spreadsheet.py`. The file should contain the API key, then a space, then the key's corresponding username, as shown below.

```
key username
```

If you already have a voting data spreadsheet, then you do not need API credentials.

#### Downloading voting data

Once you have saved your API token, you can download voting data by running `python create-voter-spreadsheet.py`.

When prompted, enter the id of the poll topic. (The topic id is the number in the topic's URL.) All of the polls should be in the topic's first post.

The script will download the topic's voting data and save it in `raw-vote-data-topic-{TOPIC_ID}.csv`. Each row represents a user, and each column represents a contest entry. Each cell contains the ranking that the row's user assigned to the column's contest entry.

All of the following steps pull voting data from this spreadsheet, not from the Discourse API. You can edit this spreadsheet to add, remove, or edit votes. Of course, with great power comes great responsibility.

#### Identifying winners

Once you have a voting data spreadsheet (made by `create-voter-spreadsheet.py`), you can find the contest's results.

Run `python find-contest-winners.py`. When prompted, enter the path to the voting data spreadsheet. Next enter the prefix for the spreadsheet. (After each round, the script will write the current standings into `{PREFIX}{ROUND_NUMBER}.csv`.) Finally, enter the number of desired winners.

The script will simulate the contest. After each round, it will print out a description of the round and a bar chart of the contest's current standings. It will also print out the voting breakdowns of each round into `{PREFIX}{ROUND_NUMBER}.csv`. Each column in the spreadsheet represents an entry. Each cell represents a voter for that column's entry and lists the voter's name, the ranking they gave the entry, and the round when they voted for the entry. When the contest ends, the script prints the winners to the console.
