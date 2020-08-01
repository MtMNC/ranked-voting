(this is out of date)

# Introduction

These scripts help users run [instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting) in a [Discourse forum](https://www.discourse.org) using Discourse's standard poll system.

They were written for the Helryx contest on the [TTV Message Boards](https://board.ttvchannel.com/), but they can be generalized quite easily by finding and replacing URLs in the scripts. This readme does not assume you are familiar with TTV's voting process.


# Setting up polls

Set up one poll for each entry in the contest. Voters rank each entry by voting for one option in each poll. For example, if the users can select their 10 favorite entries, each poll should have radio buttons labeled 1 through 10 (and possibly a "no ranking" option). Voters should select option 1 in their favorite entry's poll, option 2 in their next favorite entry's poll, etc.


# Simulating instant-runoff voting

Once the polls close, the scripts can help simulate instant-runoff voting.

## Getting an API key

`create-voter-spreadsheet.py` fetches data from the Discourse API, which requires appropriate credentials. Get an API key through the Discourse admin panel. Save it in a file called `api-credentials.txt` located in the same folder as `create-voter-spreadsheet.py`. The file should contain the API key, then a space, then the key's corresponding username, as shown below.

```key username```

If you already have a voting data spreadsheet, then you do not need API credentials.

## Downloading voting data

Once you have saved your API token, you can download voting data by running `python create-voter-spreadsheet.py`.

When prompted, enter the id of the post that contains the contest's polls. (You can find the post id with your browser's developer tools. Identify the `<article>` tag containing the post; that tag's `data-post-id` attribute is the post id.)

The script will download the voting data and save it in a CSV file. Each row represents a user, and each column represents a contest entry. Each cell contains the ranking that the row's user assigned to the column's contest entry.

All of the following steps pull vote data from this spreadsheet, not from the Discourse API. You can edit this spreadsheet to add, remove, or edit votes. Of course, with great power comes great responsibility.

## Identifying duplicate votes

Sometimes voters may assign the same ranking to multiple contest entries. You may wish to identify these entries before running simulations. For instance, you may want to let voters know that they cast duplicate votes so they can let you know which rankings they actually meant to use.

To identify duplicate votes, run `python create-duplicate-votes-document.py`. When prompted, enter the path to the vote data spreadsheet (produced by `create-voter-spreadsheet.py`) and the desired path of the output text document. The script will produce a document where each line has the following format:

`username: {1: [entry_1, entry_3], 3: [entry_4, entry_7, entry_8]}`

In this case, the voter called `username` assigned ranking 1 to `entry_1` and `entry_3`, and they assigned ranking 3 to `entry_4`, `entry_7`, and `entry_8`.
