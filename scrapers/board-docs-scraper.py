import requests
from bs4 import BeautifulSoup
import pickle
import re
import datetime
import os.path
import json

def main():

	agency = "east_side_uhsd"
	agency_code = "esuhsd"

	agenda_list = loadExistingAgendaList(agency)
	agenda_list = getAgendasList(agency, agency_code, agenda_list)
	writeAgendaListToDisk(agency, agenda_list)


'''
loadExistingAgendaList
==================
Check if there is a saved list of agendas for this agency.
Return the list if it exists, otherwise return an empty list.
'''
def loadExistingAgendaList(agency):

	agenda_list = list()
	agenda_list_filepath = "../docs/" + agency + "/agenda_list.json"
	if os.path.exists(agenda_list_filepath):
		with open(agenda_list_filepath) as data_file:
			agenda_list = json.load(data_file)

	return agenda_list


	

'''
getAgendasList
==============
Given an agency and the BoardDocs code for that agency,
return a list of meeting agendas posted on BoardDocs.
'''
def getAgendasList(agency, agency_code, agenda_list):

	# get list of meetings
	r = requests.get('http://www.boarddocs.com/ca/' + agency_code + '/Board.nsf/LT-GetMeetings')
	meetings_soup = BeautifulSoup(r.content, "lxml")

	# # write to disk to avoid hammering the server
	# pickle.dump(meetings_soup, open( "../docs/" + agency + "/data/test_meetings_html.p", "wb" ))
	# meetings_soup = pickle.load(open("../docs/" + agency + "/data/test_meetings_html.p", "rb" ))

	# extract links to agendas
	agenda_links = meetings_soup.find_all("a", class_="meeting")
	for link in agenda_links:

		meeting_title_raw = link.find_all("div")[-1].string
		meeting_title = cleanMeetingTitle(meeting_title_raw, agency)

		# # extract the meeting date
		meeting_date_string = link.find(string=re.compile(r'\w{3}\s\d+\,\s\d{4}'))
		meeting_date_string = re.sub(r'\(\w{3}\)', '', meeting_date_string).strip() # clean string
		meeting_date = datetime.datetime.strptime(meeting_date_string, "%b %d, %Y").date().strftime('%m-%d-%Y')

		# # extract the meeting id
		boarddocs_id = link['id']

		if boarddocs_id not in [agenda["boarddocs_id"] for agenda in agenda_list]:

			print("New agenda found: %s, %s" % (meeting_title, meeting_date))

			agenda_list.append({"agency": agency, "meeting_title": meeting_title, "meeting_title_raw": meeting_title_raw, "meeting_date": meeting_date, "boarddocs_id": boarddocs_id, "parsed": False})

	return agenda_list

'''
cleanMeetingTitle
=================
Remove unwanted boilerplate that some agencies attach to their agenda titles.
'''
def cleanMeetingTitle(raw_title, agency):

	if agency == "east_side_uhsd":
		meeting_title = raw_title.split("-", 1)[0].strip()
	else:
		meeting_title = raw_title

	return meeting_title

	
'''
writeAgendaListToDisk
=====================
Given an agency and JSON-formatted agenda list,
write out the list to disk.
'''
def writeAgendaListToDisk(agency, agenda_list):

	agenda_list_filepath = "../docs/" + agency + "/agenda_list.json"
	with open(agenda_list_filepath, 'wb') as outfile:
		json.dump(agenda_list, outfile, sort_keys = True, indent = 4, ensure_ascii=False)












if __name__ == '__main__':
	main()