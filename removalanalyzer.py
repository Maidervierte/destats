import praw
import re
from datetime import datetime
import jsonpickle

reddit = praw.Reddit(
    client_id='*****',
    client_secret ="*****",
    username="*****",
    password="*****",
    user_agent="*****"
)

class RemovedPost:
    def __init__(self, submission, mod,reason, time):
        self.submission =  submission
        self.mod = mod
        self.reason=reason
        self.time=time

    def __str__(self):
        return f'({self.submission},{self.mod},{self.reason})'
    
    def __repr__(self):
        return f'({self.submission},{self.mod},{self.reason})'
    
subreddit = reddit.subreddit("de")

posts = [[] for x in range(0,28)]
removalreasons = [[] for x in range(0,14)]

mod_dict={}
mod_dict_rev={}
mod_dict_i=0;
removal_dict={}
removal_dict_rev={}
removal_dict_i=0;
breaklimit=0
removalreasonslist=["repost", 
                    "falsch gepostet", 
                    "linktitel",
                    "regional",
                    "relevanz",
                    "lq",
                    "selbstwerbung",
                    "umfrage",
                    "politische werbung / petition",
                    "schwurbel","megathread",
                    "corona",
                    "kein grüner kommentar",
                    "grüne kommentare konnten nicht zugeordnet werden"]

for moderator in subreddit.moderator():
    mod_dict[moderator.name]=mod_dict_i
    mod_dict_rev[mod_dict_i]=moderator.name
    mod_dict_i=mod_dict_i+1
    
for x in removalreasonslist:
    removal_dict[x]=removal_dict_i
    removal_dict_rev[removal_dict_i]=x
    removal_dict_i=removal_dict_i+1


for removedlink in subreddit.mod.log(action='removelink',limit=None):
    breakpoint=True
    print(breaklimit)
    removedlinkid=str(removedlink.target_fullname)
    removedlinkid=removedlinkid[3:]
    file1 = open("remids.txt", "r+")  
    for line in file1:
        if (removedlinkid+"\n")==line:
            breakpoint=breakpoint
            breakpoint=False
            break
    if breakpoint:
        file1.write(removedlinkid+"\n")
    file1.close() 
    if breakpoint:
        if removedlink._mod.strip() != "AutoModerator":
            breaklimit=breaklimit+1;
            #print(removedlink._mod)
            posts[mod_dict.get(removedlink._mod)].append(removedlinkid)
        if breaklimit==1000000:
            break
    else:
        break

#print(posts)
    
mod_num=0
post_num=0


for post_list in posts:
    for submission in post_list: 
        post_num=post_num+1
        print(post_num)
        #print(submission)
        submission=reddit.submission(submission)
        submission.comments.replace_more(limit=None)
        reason=False
        if submission.comments.list(): 
            for comment in submission.comments.list():
                if comment.distinguished:
                    reason=True;
                    modcomment=comment.body
                    if re.search('Mehrfacheinreichungen zum selben Thema', modcomment): reason_num=0; break
                    if re.search('Bitte beachte die folgenden Regeln:', modcomment): reason_num=1; break
                    if re.search('Beim Posten von Nachrichten', modcomment): reason_num=2; break               
                    if re.search('Polizei- und Pressemeldungen', modcomment): reason_num=3; break
                    if re.search('Nachrichtenposts sollten auf Deutsch', modcomment): reason_num=4; break
                    if re.search('Qualitätsanspruch', modcomment): reason_num=5; break
                    if re.search('Eigenwerbung für ein bestimmtes Produkt', modcomment): reason_num=6; break
                    if re.search('Nur nicht-kommerzielle Umfragen', modcomment): reason_num=7; break
                    if re.search('Politische Werbung für Personen', modcomment): reason_num=8; break
                    if re.search('soll der Verbreitung von Verschwörungstheorien', modcomment): reason_num=9; break
                    if re.search('Es gibt zu dem von dir geposteten Thema', modcomment): reason_num=10; break
                    if re.search('Aufgrund der außergewöhnlichen Lage', modcomment): reason_num=11; break
                    reason_num=13
                if comment.author: 
                    if comment.author.name=="AutoErMelReWieDE": reason_num=0; reason=True; break
        if reason==False: reason_num=12
        removedpost=RemovedPost(submission=submission.id,mod=mod_dict_rev.get(mod_num),reason=reason_num,time=submission.created_utc)
        removalreasons[reason_num].append(removedpost)
    print("mod_num: "+str(mod_num))
    mod_num=mod_num+1
    
    
now = datetime.now()
dt_string = now.strftime("%Y.%m.%d %Hh%Mm%Ss")

with open(dt_string+" - removalreasons.txt", "w") as f:
    for x in removalreasons:
        for y in x:
             f.write("reddit.com/r/de/"+y.submission+" - "+y.mod+" - "+removal_dict_rev[y.reason]+"\n")
f.closed

with open(dt_string+" - jsonpickle - removalreasons.txt", "w") as f:
    f.write(jsonpickle.encode(removalreasons))
f.closed

with open(dt_string+" - jsonpickle - posts.txt", "w") as f:
    f.write(jsonpickle.encode(posts))
f.closed

                        
print(removalreasons)


posts2 = [[[] for x in range(0,14)] for x in range(0,28)]
modlist = [[] for x in range(0,14)]

for y in range(0,28):
    modlist = [[] for x in range(0,14)]
    for submission in posts[y]: 
        for x in range (0,14):
            for submission2 in removalreasons[x]:
                if submission==submission2.submission and mod_dict_rev.get(y)==submission2.mod:
                    modlist[x].append(submission2)
    posts2[y]=modlist


count = 0
for listElem in posts2:
    for listElem2 in listElem:
        count += len(listElem2) 
removed_count=count
    
printstring="Die Verteilung der Entfernungsgründe der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,14):
    count = 0
    for listElem in posts2:
        count += len(listElem[x]) 
    printstring=printstring+str(count)+" "+(removal_dict_rev.get(x))+"\n"
print(printstring)

with open(dt_string+" - stats nach reason.txt", "w") as f:
    f.write(printstring)
f.closed

printstring="Die Verteilung der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,28):
    count = 0
    for listElem in posts2[x]:
        count += len(listElem) 
    if count>0:
        printstring=printstring+str(count)+" "+(mod_dict_rev.get(x))+"\n"
        for y in range(0,14):
            if len(posts2[x][y])>0:
                printstring=printstring+"     "+str(len(posts2[x][y]))+" "+(removal_dict_rev.get(y))+"\n"
        
print(printstring)

with open(dt_string+" - stats nach mods.txt", "w") as f:
    f.write(printstring)
f.closed

print(posts2)
printstring="\n"
printstring=printstring+"Posts ohne Kommentar:\n"

for x in posts2:
    for rem_post in x[12]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod
        
printstring=printstring+"\n\nPosts mit Kommentaren, die nicht zugeordnet werden konnten:\n"

for x in posts2:
    for rem_post in x[13]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod
        
with open(dt_string+" - unidentifiziert.txt", "w") as f:
    f.write(printstring)
f.closed

with open(dt_string+" - jsonpickle - posts2.txt", "w") as f:
    f.write(jsonpickle.encode(posts2))
f.closed

print(printstring)posts2 = [[[] for x in range(0,14)] for x in range(0,28)]
modlist = [[] for x in range(0,14)]

for y in range(0,28):
    modlist = [[] for x in range(0,14)]
    for submission in posts[y]: 
        for x in range (0,14):
            for submission2 in removalreasons[x]:
                if submission==submission2.submission and mod_dict_rev.get(y)==submission2.mod:
                    modlist[x].append(submission2)
    posts2[y]=modlist


count = 0
for listElem in posts2:
    for listElem2 in listElem:
        count += len(listElem2) 
removed_count=count
    
printstring="Die Verteilung der Entfernungsgründe der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,14):
    count = 0
    for listElem in posts2:
        count += len(listElem[x]) 
    printstring=printstring+str(count)+" "+(removal_dict_rev.get(x))+"\n"
print(printstring)

with open(dt_string+" - stats nach reason.txt", "w") as f:
    f.write(printstring)
f.closed

printstring="Die Verteilung der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,28):
    count = 0
    for listElem in posts2[x]:
        count += len(listElem) 
    if count>0:
        printstring=printstring+str(count)+" "+(mod_dict_rev.get(x))+"\n"
        for y in range(0,14):
            if len(posts2[x][y])>0:
                printstring=printstring+"     "+str(len(posts2[x][y]))+" "+(removal_dict_rev.get(y))+"\n"
        
print(printstring)

with open(dt_string+" - stats nach mods.txt", "w") as f:
    f.write(printstring)
f.closed

print(posts2)
printstring="\n"
printstring=printstring+"Posts ohne Kommentar:\n"

for x in posts2:
    for rem_post in x[12]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod
        
printstring=printstring+"\n\nPosts mit Kommentaren, die nicht zugeordnet werden konnten:\n"

for x in posts2:
    for rem_post in x[13]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod
        
with open(dt_string+" - unidentifiziert.txt", "w") as f:
    f.write(printstring)
f.closed

with open(dt_string+" - jsonpickle - posts2.txt", "w") as f:
    f.write(jsonpickle.encode(posts2))
f.closed

print(printstring)

file1 = open("gesamt posts2.txt", "r+")  
posts3=""
for line in file1:
    posts3=posts3+line
file1.close()

file1 = open("gesamt removalreasons.txt", "r+")  
removalreasons2=""
for line in file1:
    removalreasons2=removalreasons2+line
file1.close()

file1 = open("gesamt posts.txt", "r+")  
posts5=""
for line in file1:
    posts5=posts5+line
file1.close()


posts4=jsonpickle.decode(posts3)
posts6=jsonpickle.decode(posts5)
removalreasons3=jsonpickle.decode(removalreasons2)



for x in range(0,28):
    for y in range(0,14):
            posts4[x][y]=posts4[x][y]+posts2[x][y]
            
count = 0
for listElem in posts4:
    for listElem2 in listElem:
        count += len(listElem2) 
removed_count=count

with open("gesamt posts2.txt", "w") as f:
    f.write(jsonpickle.encode(posts4))
f.closed

for x in range(0,28):
    posts6[x]=posts6[x]+posts[x]

with open("gesamt posts.txt", "w") as f:
    f.write(jsonpickle.encode(posts6))
f.closed

for y in range(0,14):
    removalreasons3=removalreasons3+removalreasons
    
with open("gesamt removalreasons.txt", "w") as f:
    f.write(jsonpickle.encode(removalreasons3))
f.closed

print(posts4)

printstring="Die Verteilung der Entfernungsgründe der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,14):
    count = 0
    for listElem in posts4:
        count += len(listElem[x]) 
    printstring=printstring+str(count)+" "+(removal_dict_rev.get(x))+"\n"
print(printstring)

with open("gesamt stats reason.txt", "w") as f:
    f.write(printstring)
f.closed

printstring="Die Verteilung der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,28):
    count = 0
    for listElem in posts4[x]:
        count += len(listElem) 
    if count>0:
        printstring=printstring+str(count)+" "+(mod_dict_rev.get(x))+"\n"
        for y in range(0,14):
            if len(posts4[x][y])>0:
                printstring=printstring+"     "+str(len(posts4[x][y]))+" "+(removal_dict_rev.get(y))+"\n"
        
print(printstring)

with open("gesamt stats mods.txt", "w") as f:
    f.write(printstring)
f.closed

printstring=""
for x in posts4:
    for rem_post in x[12]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod+"\n"
        
with open("gesamt kein grüner comment.txt", "w") as f:
    f.write(printstring)
f.closed

printstring=""
        
for x in posts4:
    for rem_post in x[13]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod+"\n"
        
with open("gesamt comment nicht zugeordnet.txt", "w") as f:
    f.write(printstring)
f.closedfile1 = open("gesamt posts2.txt", "r+")  
posts3=""
for line in file1:
    posts3=posts3+line
file1.close()

file1 = open("gesamt removalreasons.txt", "r+")  
removalreasons2=""
for line in file1:
    removalreasons2=removalreasons2+line
file1.close()

file1 = open("gesamt posts.txt", "r+")  
posts5=""
for line in file1:
    posts5=posts5+line
file1.close()


posts4=jsonpickle.decode(posts3)
posts6=jsonpickle.decode(posts5)
removalreasons3=jsonpickle.decode(removalreasons2)



for x in range(0,28):
    for y in range(0,14):
            posts4[x][y]=posts4[x][y]+posts2[x][y]
            
count = 0
for listElem in posts4:
    for listElem2 in listElem:
        count += len(listElem2) 
removed_count=count

with open("gesamt posts2.txt", "w") as f:
    f.write(jsonpickle.encode(posts4))
f.closed

for x in range(0,28):
    posts6[x]=posts6[x]+posts[x]

with open("gesamt posts.txt", "w") as f:
    f.write(jsonpickle.encode(posts6))
f.closed

for y in range(0,14):
    removalreasons3=removalreasons3+removalreasons
    
with open("gesamt removalreasons.txt", "w") as f:
    f.write(jsonpickle.encode(removalreasons3))
f.closed

print(posts4)

printstring="Die Verteilung der Entfernungsgründe der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,14):
    count = 0
    for listElem in posts4:
        count += len(listElem[x]) 
    printstring=printstring+str(count)+" "+(removal_dict_rev.get(x))+"\n"
print(printstring)

with open("gesamt stats reason.txt", "w") as f:
    f.write(printstring)
f.closed

printstring="Die Verteilung der letzten "+str(removed_count)+" von Menschen entfernten Einreichungen:\n"
for x in range(0,28):
    count = 0
    for listElem in posts4[x]:
        count += len(listElem) 
    if count>0:
        printstring=printstring+str(count)+" "+(mod_dict_rev.get(x))+"\n"
        for y in range(0,14):
            if len(posts4[x][y])>0:
                printstring=printstring+"     "+str(len(posts4[x][y]))+" "+(removal_dict_rev.get(y))+"\n"
        
print(printstring)

with open("gesamt stats mods.txt", "w") as f:
    f.write(printstring)
f.closed

printstring=""
for x in posts4:
    for rem_post in x[12]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod+"\n"
        
with open("gesamt kein grüner comment.txt", "w") as f:
    f.write(printstring)
f.closed

printstring=""
        
for x in posts4:
    for rem_post in x[13]:
        printstring=printstring+"reddit.com/r/de/comments/"+rem_post.submission+", "+rem_post.mod+"\n"
        
with open("gesamt comment nicht zugeordnet.txt", "w") as f:
    f.write(printstring)
f.closed
