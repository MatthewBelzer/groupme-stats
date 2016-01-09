from __future__ import print_function

import requests
import pickle
import csv
from enchant.checker import SpellChecker

TOKEN ="qwertyuiopasdfghjklzxcvbnm" #replace this with your API token (get from GroupMe Website)
GROUP_ID = "123456789" #replace this with your group ID

def get_messages(group, token):
	"""Gets all messages from a group since it was created. Requires that the token
	belongs to an account that is currently a member of the group. Paged 100 messages
	per request, so might take a while for groups with 1000+ messages."""

	GROUP_URI = 'https://api.groupme.com/v3/groups/' + str(group)
	messages = []
	message_id = get_latest_message(group)['id']

	while True:
		request_string = GROUP_URI + '/messages?token=' + token + '&before_id=' + str(message_id) + '&limit=' + '100'
		r = requests.get(request_string)
		try:
			messages += r.json()['response']['messages']
			message_id = messages[-1]['id']
		except ValueError:
			break
		print(len(messages))

	return messages

def get_latest_message(group, token):
	"""Gets the most recent message from a group. Token must be valid for the group."""

	GROUP_URI = 'https://api.groupme.com/v3/groups/' + str(group)
	r = requests.get(GROUP_URI + '/messages?token=' + token + '&limit=1')
	return r.json()['response']['messages'][0]

def save_messages(messages):
	"""Save messages so they don't have to be requested from GroupMe servers every time."""
	with open('messages.pkl', 'w') as save_file:
		pickle.dump(messages, save_file)

def load_messages():
	"""Load saved messages"""
	with open('messages.pkl', 'r') as save_file:
		return pickle.load(save_file)

def print_messages(messages):
	for m in reversed(messages):
		print(m['name'] + ':', end=' '*(26-len(m['name'])))
		print('(', len(m['favorited_by']), ')\t', sep='', end='')
		if len(m['attachments']) > 0:
			print('<image>')
		else:
			print(m['text'])

def latest_user_names(messages):
	"""GroupMe users can change their alias as many times as they want. this
	method returns a mapping of user_id to most recent alias. Useful for creating up-to-date
	statistics for groups with a lot of members who change their names frequently."""

	usermap = {}
	for m in messages:
		uid = m['user_id']
		if uid not in usermap or usermap[uid][1] > int(m['created_at']):
			usermap[uid] = (m['name'].encode('utf-8'), int(m['created_at']))
	return {uid: usermap[uid][0] for uid in usermap}

def user_stats(messages, usermap):
	"""Keys: (posts, likes_recieved, likes_given, wordcount, images, misspellings, kicked)"""
	stats = {}
	checker = SpellChecker('en_US')
	for user_id in usermap:
		stats[usermap[user_id]] = {
			'posts': [],
			'likes_recieved': 0,
			'likes_given': 0,
			'wordcount': 0,
			'images': 0,
			'misspellings': [],
			'kicked': 0,
			'been_kicked': 0 }
	current_names = {} # map user id to alias at the time of each message
	for m in reversed(messages):
		current_names[m['sender_id']] = m['name']
		if m['user_id'] == 'system':
			if m['text'] is not None:
				if ' changed name to ' in m['text']:
					s = m['text'].split(' changed name to ')
					for uid in current_names:
						if current_names[uid] == s[0]:
							current_names[uid] = s[1]
				elif ' removed ' in m['text']:
					s = m['text'][:-16].split(' removed ')
					remover = 0
					removed = 0
					for uid in current_names:
						if current_names[uid] == s[0]: remover = uid
						if current_names[uid] == s[1]: removed = uid
					if remover != 0 and removed != 0:
						stats[usermap[remover]]['kicked'] += 1
						stats[usermap[removed]]['been_kicked'] += 1
		name = usermap[m['sender_id']]
		stats[name]['posts'].append(m)
		stats[name]['likes_recieved'] += len(m['favorited_by'])
		for liker in m['favorited_by']:
			try:
				likername = usermap[liker]
				stats[likername]['likes_given'] += 1
			except KeyError:
				pass
		stats[name]['images'] += 1 if len(m['attachments']) > 0 else 0
		if m['text'] is not None:
			stats[name]['wordcount'] += len(m['text'].split(' '))
			checker.set_text(m['text'])
			stats[name]['misspellings'] += [error.word for error in list(checker)]
		
	del stats['GroupMe']
	del stats['GroupMe Calendar']
	del stats['Annie Hughey']
	del stats['Nicole Vergara']
	return stats

def print_stats(userstats, num_listed):
	"""Prints stats to console and also compiles them to a csv file."""

	total_posts = sum([len(userstats[u]['posts']) for u in userstats])
	posts = list(reversed(sorted([(len(userstats[u]['posts']), u) for u in userstats])))
	likes_recieved = list(reversed(sorted([(userstats[u]['likes_recieved'], u) for u in userstats])))
	likes_given = list(reversed(sorted([(userstats[u]['likes_given'], u) for u in userstats])))
	average_likes = list(reversed(sorted([(float(userstats[u]['likes_recieved']) / len(userstats[u]['posts']), u) for u in userstats])))
	misspellings = list(reversed(sorted([(float(len(userstats[u]['misspellings'])) / len(userstats[u]['posts']), u) for u in userstats])))
	misspelled_count = {u: {} for u in userstats} #map users to a dict that maps words to times misspelled
	for u in userstats:
		all_misspellings = userstats[u]['misspellings']
		for word in all_misspellings:
			if word not in misspelled_count[u]:
				misspelled_count[u][word] = 1
			else:
				misspelled_count[u][word] += 1
	commonly_misspelled = {u: [] for u in userstats} #map users to a list of touples: (times misspelled, word)
	for user in misspelled_count:
		for word in misspelled_count[user]:
			commonly_misspelled[user].append((misspelled_count[user][word], word))
		commonly_misspelled[user] = list(reversed(sorted(commonly_misspelled[user])))
	kicked = list(reversed(sorted([(userstats[u]['kicked'], u) for u in userstats])))
	been_kicked = list(reversed(sorted([(userstats[u]['been_kicked'], u) for u in userstats])))

	images = list(reversed(sorted([(userstats[u]['images'], u) for u in userstats])))


	print('\nTotal Posts:', total_posts)
	print()

	print('Most Posts:')
	for post, name in posts[:num_listed]:
		print('\t', name, '-', post)
	print()

	print('Fewest Posts:')
	for post, name in list(reversed(posts))[:num_listed]:
		print('\t', name, '-', post)
	print()

	print('Most Likes Recieved:')
	for likes, name in likes_recieved[:num_listed]:
		print('\t', name, '-', likes)
	print()

	print('Fewest Likes Recieved:')
	for likes, name in list(reversed(likes_recieved))[:num_listed]:
		print('\t', name, '-', likes)
	print()

	print ('Average Likes Per Post:')
	for likes, name in average_likes[:num_listed]:
		print('\t', name, '-', str(likes)[:num_listed])
	print()

	with open('stats.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(['Total Posts', total_posts])

		writer.writerow([])
		writer.writerow(['Most Posts', '', '', 'Fewest Posts'])
		for i in range(num_listed):
			writer.writerow([posts[i][1], posts[i][0], '', posts[-i-1][1], posts[-i-1][0]])

		writer.writerow([])
		writer.writerow(['Most Likes', '', '', 'Fewest Likes'])
		for i in range(num_listed):
			writer.writerow([likes_recieved[i][1], likes_recieved[i][0], '', likes_recieved[-i-1][1], likes_recieved[-i-1][0]])

		writer.writerow([])
		writer.writerow(['Most Average Likes', '', '', 'Fewest Average Likes'])
		for i in range(num_listed):
			writer.writerow([average_likes[i][1], str(average_likes[i][0])[:4], '', average_likes[-i-1][1], str(average_likes[-i-1][0])[:4]])

		writer.writerow([])
		writer.writerow(['Misspelled Words Per Post', '', '', 'Most Common Misspellings'])
		for i in range(num_listed):
			m = ', '.join([cm[1] for cm in commonly_misspelled[misspellings[i][1]]][:7])
			writer.writerow([misspellings[i][1], str(misspellings[i][0])[:4], '', m])

		writer.writerow([])
		writer.writerow(['Images/Gifs'])
		for i in range(num_listed):
			writer.writerow([images[i][1], images[i][0]])

		writer.writerow([])
		writer.writerow(['Times Kicked From Group', '', '', 'People Kicked'])
		for i in range(num_listed):
			print(been_kicked)
			writer.writerow([been_kicked[i][1], been_kicked[i][0], '', kicked[i][1], kicked[i][0]])


if __name__ == '__main__':
	# comment the following lines after first run
	messages = get_messages(GROUP_ID, TOKEN)
	save_messages(messages)

	# uncomment after first run to use saved messages
	#messages = load_messages()

	usermap = latest_user_names(messages)
	userstats = user_stats(messages, usermap)
	print_stats(userstats, 6)