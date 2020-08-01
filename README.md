# Single Transferable Vote in Discourse

## Introduction

These scripts help users run [single transferable vote](https://en.wikipedia.org/wiki/Single_transferable_vote) (STV) voting in a [Discourse forum](https://www.discourse.org) using Discourse's standard poll system. They were written for the Helryx contest on the [TTV Message Boards](https://board.ttvchannel.com/), but they can be generalized quite easily by finding and replacing URLs in the scripts. This readme does not assume you are familiar with TTV's voting process.

Because this implementation of STV uses the [Droop quota](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Droop_quota) to determine its winner, it is an extension of [instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting) (IRV). In contests with one winner, this STV implementation behaves identically to IRV. Unlike IRV, STV can also handle contests with multiple winners.

## Implementation details
There are many variants of STV. Here are the details of this specific implementation.
* Winners are identified when their vote count meets or exceeds the [Droop quota](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Droop_quota).
* Surplus votes are selected randomly. For example, if an entry has 160 votes and only needed 120 to win, then 40 of the entry's voters are selected at random. Those 40 voters discard their old vote and, if they have a next choice, they vote for it.
* If multiple winners have surplus votes, then those votes are reallocated one winner at a time in random order (rather than all during one round).
* If multiple entries are in last place during an elimination round, then those entries are eliminated one a time in random order (rather than all during one round).
* Voters can only vote for entries that were still in the race (that had neither won nor been eliminated) as of the start of the current round.
* If a voter assigned the same ranking to multiple entries, than that ranking is skipped over. For example, if a voter gave rank 1 to entry A, rank 2 to entries B and C, and rank 3 to entry D, then the voter's preferences are entry A followed by entry D.

## Instructions
### Setting up polls

Set up one poll for each entry in the contest. Voters rank each entry by voting for one option in each poll. For example, if the users can select their 10 favorite entries, each poll should have radio buttons labeled 1 through 10 (and possibly a "no ranking" option). Voters should select option 1 in their favorite entry's poll, option 2 in their next favorite entry's poll, etc.


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

When prompted, enter the id of the post that contains the contest's polls. (You can find the post id with your browser's developer tools. Identify the `<article>` tag containing the post; that tag's `data-post-id` attribute is the post id.)

The script will download the voting data and save it in a CSV file. Each row represents a user, and each column represents a contest entry. Each cell contains the ranking that the row's user assigned to the column's contest entry.

All of the following steps pull voting data from this spreadsheet, not from the Discourse API. You can edit this spreadsheet to add, remove, or edit votes. Of course, with great power comes great responsibility.

#### (Optional) Identifying duplicate votes

Sometimes voters may assign the same ranking to multiple contest entries. You may wish to identify these entries before running simulations. For instance, you may want to let voters know that they cast duplicate votes so they can let you know which rankings they actually meant to use.

Once you have a voting data spreadsheet (made by `create-voter-spreadsheet.py`), you can find duplicate votes. Run `python create-duplicate-votes-document.py`. When prompted, enter the path to the voting data spreadsheet and the desired path of the output text document. The script will produce a document where each line has the following format:

`username: {1: [entry_1, entry_3], 3: [entry_4, entry_7, entry_8]}`

In this case, the voter called `username` assigned ranking 1 to `entry_1` and `entry_3`, and they assigned ranking 3 to `entry_4`, `entry_7`, and `entry_8`.

#### Identifying winners

Once you have a voting data spreadsheet (made by `create-voter-spreadsheet.py`), you can find the contest's results.

Run `python find-contest-winners.py`. When prompted, enter the path to the voting data spreadsheet. Next enter the prefix for the spreadsheet. (After each round, the script will write the current standings into `{PREFIX}{ROUND_NUMBER}.csv`.) Finally, enter the number of desired winners.

The script will simulate the contest. After each round, it will print out a description of the round and a bar chart of the contest's current standings. It will also print out the voting breakdowns of each round into `{PREFIX}{ROUND_NUMBER}.csv`. Each column in the spreadsheet represents an entry. Each cell represents a voter for that column's entry and lists the voter's name, the ranking they gave the entry, and the round when they voted for the entry. When the contest ends, the script prints the winners to the console.
