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
            getProposer = re.search(r'/.*I\[[0-9]{2}-[0-9]{2}\|([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})] Received proposal\s*module=consensus proposal="Proposal{([0-9]{1,})\/0.*/', str(entry))

            # get the proposer of that round
            temp = re.search(r'/.*I\[[0-9]{2}-[0-9]{2}\|([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})] enterPropose: (Not our turn to propose)?(Our turn to propose)?\ *module=consensus height=([0-9]{1,}) round=[0-9]{1,} proposer=([0-9A-F]{40}).*/', str(entry))

            # check Absent validator
            matchAbsent = re.search(r'/.*I\[([0-9]{2}-[0-9]{2})\|([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})\] Absent validator ([0-9A-F]{40}) at height ([0-9]{1,}), ([0-9]{1,}) signed, threshold ([0-9]{1,}).*/' , str(entry))

            # check timeout_commit of proposer of that round
            getCommitTimeout = re.search(r'/.*I\[[0-9]{2}-[0-9]{2}\|[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}\] Timed out\s*module=consensus dur=([0-9]{1,}.[0-9]{1,})s height=([0-9]{1,}) round=[0-9]{1,} step=RoundStepNewHeight.*/', str(entry))

            msg = entry["MESSAGE"]

            if (getProposer):
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

            elif (matchAbsent):
                valaddr = matchAbsent.group(3)
                h = matchAbsent.group(4)
                if (h == height):
                    print("Absent validator: " + valaddr)
                else:
                    print("It should not appear this line...")

            elif (getCommitTimeout):
                timeout = getCommitTimeout.group(1)
                h = getCommitTimeout.group(2)
                if (height == h):
                    print("Timeout reached: " + timeout)
                else:
                    print("Time not out")


except KeyboardInterrupt:
    print("Thanks for using")

