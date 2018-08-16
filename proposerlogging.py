#!/usr/bin/env python
from __future__ import division
from systemd import journal
import re
from pprint import pprint
# import pymongo
# from pymongo import MongoClient
import json
import os
import subprocess
import requests
import time
from requests_futures.sessions import FuturesSession


# check the current height
# if height changes
    # get the proposer from dump_consense_state,
    # keep track on the log, log down absent validators, calculate the timeout_commit


j = journal.Reader()
j.this_boot()
j.seek_tail()
# Important! - Discard old journal entries
j.get_previous()
j.log_level(journal.LOG_INFO)
j.add_match(_SYSTEMD_UNIT="forboled.service")

#start = time.time()

preHeight = 0

# check the current height when found this line in log
try:
    while True:
        for entry in j:
            # get new height when encounter this line
            checkHeight = re.search(r'/.*I\[[0-9]{2}-[0-9]{2}\|([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})] Received proposal\s*module=consensus proposal="Proposal{([0-9]{1,})\/0.*/', str(entry))

            # get the proposer of that round
            getProposer = re.search(r'/.*I\[[0-9]{2}-[0-9]{2}\|([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})] enterPropose: (Not our turn to propose)?(Our turn to propose)?\ *module=consensus height=([0-9]{1,}) round=[0-9]{1,} proposer=([0-9A-F]{40}).*/', str(entry))

            # check

            msg = entry["MESSAGE"]

            if (checkHeight):
                startTime = checkHeight.group(1)
                height = checkHeight.group(2)
                if (height != preHeight):
                    # get proposer
                    #print("getting proposer")
                    session = FuturesSession()
                    #print(session)
                    response = session.get("https://rpc.forbole.com/dump_consensus_state")
                    #print(response)
                    unijson = response.result().text
                    jsonstr = unijson.encode("ascii", "replace")
                    myjson = json.loads(jsonstr)
                    proposerAddr = myjson['result']['round_state']['validators']['proposer']['address']
                    print('Height: ' + height + ', Proposer: ' + proposerAddr)

                    preheight = height

             elif (getProposer):
                 h = getProposer.group(4)
                 proposer = getProposer.group(5)
except KeyboardInterrupt:
    print("Thanks for using")

