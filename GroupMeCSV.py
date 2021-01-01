from __future__ import print_function
from datetime import datetime
import requests
import pickle
import csv
import numpy as np
import codecs
from enchant.checker import SpellChecker

TOKEN ="7mAhRALCs9H9QCAIYpuSOboBZSwGkbpC8bAszN8A" #replace this with your API token (get from GroupMe Website)
GROUP_ID = "63120231" #replace this with your group ID

def get_messages(group, token):
	"""Gets all messages from a group since it was created. Requires that the token
	belongs to an account that is currently a member of the group. Paged 100 messages
	per request, so might take a while for groups with 1000+ messages."""

	GROUP_URI = 'https://api.groupme.com/v3/groups/' + str(group)
	messages = []
	message_id = get_latest_message(group,token)['id']

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
	with open('messages.pkl', 'wb') as save_file:
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
			'been_kicked': 0,
			'message_time': [],
			'message_length': []}
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
						#print("current_names", current_names,"uid",uid,"s",s)
						#print("current_names[uid] ",current_names[uid])
						if current_names[uid] == s[0]: remover = uid
						if len(current_names) != len(s): removed = uid
						elif current_names[uid] == s[1]: removed = uid
					if remover != 0 and removed != 0:
						stats[usermap[remover]]['kicked'] += 1
						stats[usermap[removed]]['been_kicked'] += 1
		name = usermap[m['sender_id']]
		stats[name]['posts'].append(m)
		MsgTime = datetime.utcfromtimestamp(m['created_at']).strftime('%Y-%m-%d %H:%M:%S')
		stats[name]['message_time'].append(MsgTime.encode('utf-8'))
		stats[name]['likes_recieved'] += len(m['favorited_by'])
		stats[name]["sender"] = m['sender_type']
		if m['text'] != None:
			stats[name]['message_length'].append(len(m['text']))
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
	
	#Deletes non users from analysis otherwise it gives errors for message times
	Deletion = []
	for u in stats:
		if stats[u]['posts'][0]['sender_type'] != "user":
			Deletion = np.append(Deletion, u)

	for j in Deletion:
		try: 
			del stats[j]
		except:
			print("failed")
	return stats

	

def print_stats(userstats, num_listed):
	"""Prints stats to console and also compiles them to a csv file."""

	total_posts = sum([len(userstats[u]['posts']) for u in userstats])
	posts = list(reversed([(len(userstats[u]['posts']), u) for u in userstats]))
	likes_recieved = list(reversed([(userstats[u]['likes_recieved'], u) for u in userstats]))
	likes_given = list(reversed([(userstats[u]['likes_given'], u) for u in userstats]))
	average_likes = list(reversed([(float(userstats[u]['likes_recieved']) / len(userstats[u]['posts']), u) for u in userstats]))
	misspellings = list(reversed([(float(len(userstats[u]['misspellings'])) / len(userstats[u]['posts']), u) for u in userstats]))
	misspelled_count = {u: {} for u in userstats} #map users to a dict that maps words to times misspelled
	#Times of messages array
	times = list(reversed([(userstats[u]['message_time']) for u in userstats]))
	messageLengths =list(reversed([(userstats[u]['message_length']) for u in userstats]))
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
	kicked = list(reversed([(userstats[u]['kicked'], u) for u in userstats]))
	been_kicked = list(reversed([(userstats[u]['been_kicked'], u) for u in userstats]))

	images = list(reversed([(userstats[u]['images'], u) for u in userstats]))


	#function for writing the time array to the csv file
	#for each name
	def writeTime(i, maxArrayLength, writing, timeArray_i):
		length = len(timeArray_i)
		for j in range(0, maxArrayLength):
				if j < length:
					writing = np.append(writing, timeArray_i[j])
				else:
					writing = np.append(writing, "nothingTime")
		writing = np.append(writing, "Time Break")
		return writing

	def writeLength(i, maxArrayLength, writing, lengthArray_i):
		length = len(lengthArray_i)
		for j in range(0, maxArrayLength):
				if j < length:
					writing = np.append(writing, lengthArray_i[j])
				else:
					writing = np.append(writing, "nothingLength")
		writing = np.append(writing, "Length Break")
		return writing


	with open('stats.csv', 'w+', errors = 'strict', encoding="utf-8") as csvfile:
		writer = csv.writer(csvfile, 
					  delimiter=',', 
					  lineterminator = '\n')
		header = ['Name','Posts','Likes Recieved', 'Likes Given', 'Likes Received to Likes Given', 'Average Likes', 
				   'Misspelled Words Per Post','Images and Gifs',
				   'Times Kicked from the Group', 'Times Kicked Others']
		maxTime = 0
		for i in range(0, len(times)):
			size =  np.size(times[i])
			if size > maxTime:
				maxTime = size
		n = 1
		while n <= maxTime:
			header = np.append(header, n)
			n +=1
		header = np.append(header, "Message Time-Length Break")

		maxLength = 0
		for i in range(0, len(messageLengths)):
			size =  np.size(messageLengths[i])
			if size > maxLength:
				maxLength = size
		n = 1
		while n <= maxLength:
			header = np.append(header, n)
			n +=1
		header = np.append(header, "Message Length Break")



		writer.writerow(header)

		for i in range(num_listed):
			timesArr = times[i]
			lengthArr = messageLengths[i]
			length = len(times[i])
			user_name =  posts[i][1]
			user_name = user_name.decode('ascii', 'ignore')
			writing = []
			if likes_given[i][0] != 0:
				writing = [user_name, posts[i][0], likes_recieved[i][0], likes_given[i][0], str(likes_recieved[i][0]/likes_given[i][0])[:4], 
						str(average_likes[i][0])[:4], str(misspellings[i][0])[:4], images[i][0], been_kicked[i][0], kicked[i][0]]
				writing = writeTime(i, maxTime, writing, timesArr)
				writing = writeLength(i, maxLength, writing, lengthArr)
				writer.writerow(writing)

			else:
				writing = [user_name, posts[i][0], likes_recieved[i][0], likes_given[i][0], 'No likes given likes', 
						str(average_likes[i][0])[:4], str(misspellings[i][0])[:4], images[i][0], been_kicked[i][0], kicked[i][0], times[i]]
				writing = writeTime(i, maxTime, writing, lengthArr)
				writing = writeLength(i, maxLength, writing, lengthArr)
				writer.writerow(writing)


if __name__ == '__main__':
	# comment the following lines after first run
	messages = get_messages(GROUP_ID, TOKEN)
	save_messages(messages)

	# uncomment after first run to use saved messages
	#messages = load_messages()

	
	usermap = latest_user_names(messages)
	userstats = user_stats(messages, usermap)
	print_stats(userstats, len(userstats)) #May need to be altered depending on deleted userstats
