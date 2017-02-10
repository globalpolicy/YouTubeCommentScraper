import requests

APIKEY="{API KEY}"
VIDEOID="{VIDEO ID}"
SAVEFILE="{SAVE FILE LOCATION}"

OUTPUT=""
nextPageToken=""
totalcommentthreads=0
totalreplies=0
grandtotalcomments=0
FirstIteration=1



while FirstIteration == 1 or nextPageToken != "":
    file = open(SAVEFILE, "ab")
    FirstIteration = 0
    parameters = {"part": "id,snippet", "videoId": VIDEOID, "maxResults": "100", "pageToken": nextPageToken,
                  "key": APIKEY}
    r = requests.get("https://www.googleapis.com/youtube/v3/commentThreads", params=parameters)
    commentthreads = r.json()
    if "nextPageToken" in commentthreads:
        nextPageToken = commentthreads['nextPageToken']
    else:
        nextPageToken = ""
    for item in commentthreads['items']:
        OUTPUT=""
        totalcommentthreads += 1
        toplevelcomment = item['snippet']['topLevelComment']
        commenter = toplevelcomment['snippet']['authorDisplayName']
        comment = toplevelcomment['snippet']['textDisplay']
        totalreplycount = item['snippet']['totalReplyCount']
        commentid = item['id']
        OUTPUT += "{\n" + commenter + ":\n" + comment + "\n"
        if totalreplycount > 0:
            parameters = {"part": "id,snippet", "parentId": commentid, "maxResults": "100",
                          "key": APIKEY}
            r = requests.get("https://www.googleapis.com/youtube/v3/comments", params=parameters)
            replyitems = r.json()
            for replyitem in reversed(replyitems['items']):  #reversed coz for replies, we don't want the latest topmost
                totalreplies += 1
                replier = replyitem['snippet']['authorDisplayName']
                reply = replyitem['snippet']['textDisplay']
                OUTPUT += "{\n" + replier + ":\n" + reply + "\n}\n"
        OUTPUT += "}\n\n"
        file.write(OUTPUT.encode())
    file.close()  #appends to file and closes on a page-wise basis


grandtotalcomments=totalreplies+totalcommentthreads
file = open(SAVEFILE, "ab")
file.write(("\n\n"+"COMMENT THREADS : "+str(totalcommentthreads)+"\nREPLIES : "+str(totalreplies)+"\nTOTAL : "+str(grandtotalcomments)).encode())
file.close()
