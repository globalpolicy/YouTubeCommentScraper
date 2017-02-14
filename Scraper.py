import requests
import sqlite3


apikey= "{API KEY}"
videoid= "{VIDEO ID}"
SAVETEXTFILE= "{SAVE TEXTFILE LOCATION}"
SAVECOMMENTDB= "{SAVE DATABASE LOCATION}"

def save_to_sqlite_db(savecommentdb, videoid, apikey):

    with sqlite3.connect(savecommentdb) as conn: #opens an existing DB or creates one if not present
        conn.execute('''CREATE TABLE IF NOT EXISTS "CommentThreads" ( `Id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, `Username` TEXT NOT NULL,
        `Comment` TEXT, `PostedTime` TEXT NOT NULL, `Likes` INTEGER NOT NULL, `ReplyCount` INTEGER NOT NULL DEFAULT 0,
        `CommentId` TEXT NOT NULL )''')
        conn.commit()
        conn.execute('''CREATE TABLE IF NOT EXISTS "CommentReplies" ( `Id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, `ParentId` TEXT NOT NULL,
        `Username` TEXT NOT NULL, `Reply` TEXT, `ReplyTime` TEXT NOT NULL, `Likes` INTEGER NOT NULL )''')
        conn.commit()

        nextPageToken=""
        FirstIteration=1

        while FirstIteration == 1 or nextPageToken != "":
            with sqlite3.connect(savecommentdb) as conn:
                FirstIteration = 0
                parameters = {"part": "id,snippet", "videoId": videoid, "maxResults": "100", "pageToken": nextPageToken,
                              "key": apikey}
                r = requests.get("https://www.googleapis.com/youtube/v3/commentThreads", params=parameters)
                commentthreads = r.json()
                if "nextPageToken" in commentthreads:
                    nextPageToken = commentthreads['nextPageToken']
                else:
                    nextPageToken = ""
                for item in commentthreads['items']:
                    toplevelcomment = item['snippet']['topLevelComment']
                    commenter = toplevelcomment['snippet']['authorDisplayName']
                    comment = toplevelcomment['snippet']['textDisplay']
                    likecount=toplevelcomment['snippet']['likeCount']
                    totalreplycount = item['snippet']['totalReplyCount']
                    posttime=toplevelcomment['snippet']['updatedAt']
                    commentid = item['id']
                    conn.execute('''INSERT INTO CommentThreads (Username,Comment,PostedTime,Likes,ReplyCount,CommentId) VALUES (?,?,?,?,?,?)''',
                                 [commenter,comment,posttime,likecount,totalreplycount,commentid])
                    conn.commit()
                    if totalreplycount > 0:
                        parameters = {"part": "id,snippet", "parentId": commentid, "maxResults": "100",
                                      "key": apikey}
                        r = requests.get("https://www.googleapis.com/youtube/v3/comments", params=parameters)
                        replyitems = r.json()
                        for replyitem in reversed(replyitems['items']):  #reversed coz for replies, we don't want the latest topmost
                            replier = replyitem['snippet']['authorDisplayName']
                            reply = replyitem['snippet']['textDisplay']
                            replylikes=replyitem['snippet']['likeCount']
                            replytime=replyitem['snippet']['updatedAt']
                            conn.execute('''INSERT INTO CommentReplies (ParentId,Username,Reply,ReplyTime,Likes) VALUES (?,?,?,?,?)''',
                                         [commentid,replier,reply,replytime,replylikes])
                            conn.commit()
def save_to_txt(savetextfile, videoid, apikey):
    OUTPUT=""
    nextPageToken=""
    totalcommentthreads=0
    totalreplies=0
    grandtotalcomments=0
    FirstIteration=1
    while FirstIteration == 1 or nextPageToken != "":
        file = open(savetextfile, "ab")
        FirstIteration = 0
        parameters = {"part": "id,snippet", "videoId": videoid, "maxResults": "100", "pageToken": nextPageToken,
                      "key": apikey}
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
                              "key": apikey}
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
    file = open(savetextfile, "ab")
    file.write(("\n\n"+"COMMENT THREADS : "+str(totalcommentthreads)+"\nREPLIES : "+str(totalreplies)+"\nTOTAL : "+str(grandtotalcomments)).encode())
    file.close()

save_to_sqlite_db(SAVECOMMENTDB,videoid,apikey)
