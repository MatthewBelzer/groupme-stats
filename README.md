# groupme-stats
Generate statistics on a GroupMe group.

Requires the ID of the group, as well as a valid access token.

To find your token, go to https://dev.groupme.com/bots and click "Access Token" in the top right.

To get group ID's for all the groups you're in, execute:

   curl https://api.groupme.com/v3/groups?token=youraccesstokenhere

There are two global variables called TOKEN and GROUP_ID in main.py. Replace them with your credentials, and then run the program. The default main function will save your group's messages, print the statistics, and create a csv file. After your first run, please read the comments in the main function to avoid putting undue load on GroupMe's servers. You don't want to be requesting 5000 messages every time you run the program. Message saving with the pickle library has been added to avoid this.

If you have any questions, comments, or suggestions, please feel free to email me at jsp263@cornell.edu.