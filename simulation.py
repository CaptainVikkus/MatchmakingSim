import socket
import json
import random

users = [
    "Elli",         #0
    "Isabel",       #1
    "Jake",         #2
    "Orus",         #3
    "Pam",          #4
    "Porridge",     #5
    "Rudi",         #6
    "Sam",          #7
    "Titus",        #8
    "XxAssassinxX"  #9
    ]

def calcExpected(player1, player2):
    return 1/ (1 + 10^((player2 - player1)/400))

def calcELO(win: bool, player1, player2, player3):
    score = 0
    kfactor = 100
    if (win):
        score = (1 + ((calcExpected(player1, player2) + calcExpected(player1, player3))/400)) * kfactor
    else:
        score = (0 + ((calcExpected(player1, player2) + calcExpected(player1, player3))/400)) * kfactor
    return score

def updateELO(userID, elo):
    url = "https://k1zg78a86f.execute-api.us-east-2.amazonaws.com/default/returnELOfromID/?" + userID + "&" + elo
    response = requests.getURL(url)
    return json.loads(response.content)


def buildFight(sock):
    fight = {"Users" : []}
    #build random fighter list between 3 and 10
    fighters = random.sample(users, random.int(3, 10))
    for fighter in fighters:
        fight["Users"].append(fighter)
    #buildmsg and send to matchmake
    msg = json.dumps(fight)
    sock.send(bytes(msg, 'utf8'))


def fight(player1, player2, player3):
    pnum1 = random.randint(0, 100)
    pnum2 = random.randint(0, 100)
    pnum3 = random.randint(0, 100)

    if (pnum1 > pnum2 & pnum1 > pnum3):
        player1["ELO"] = calcELO(True, int(player1["ELO"]), int(player2["ELO"]), int(player3["ELO"]))
        player2["ELO"] = calcELO(False, int(player2["ELO"]), int(player1["ELO"]), int(player3["ELO"]))
        player3["ELO"] = calcELO(False, int(player3["ELO"]), int(player1["ELO"]), int(player2["ELO"]))
        return player1["UserID"]
    elif (pnum2 > pnum1 & pnum2 > pnum3):
        player1["ELO"] = calcELO(False, int(player1["ELO"]), int(player2["ELO"]), int(player3["ELO"]))
        player2["ELO"] = calcELO(True, int(player2["ELO"]), int(player1["ELO"]), int(player3["ELO"]))
        player3["ELO"] = calcELO(False, int(player3["ELO"]), int(player1["ELO"]), int(player2["ELO"]))
        return player2["UserID"]
    elif (pnum3 > pnum1 & pnum3 > pnum2):
        player1["ELO"] = calcELO(False, int(player1["ELO"]), int(player2["ELO"]), int(player3["ELO"]))
        player2["ELO"] = calcELO(False, int(player2["ELO"]), int(player1["ELO"]), int(player3["ELO"]))
        player3["ELO"] = calcELO(True, int(player3["ELO"]), int(player1["ELO"]), int(player2["ELO"]))
        return player3["UserID"]
    else:
        return "None"


def main():
    numFights = int(input("How Many Fights? : "))

    ##connection
    addr = "3.22.224.12"
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((addr, port))

    iFight = 1
    while (numFights > 0):
        print("Game" + iFight)
        #send players to lobby
        buildFight(s)
        #get match info
        data, ip = s.recvfrom(1024)
        jdata = json.loads(data)
        if (jdata["GameID"] != -1): #valid game check
            print("GameID:" + jdata["GameID"])
            player1 = jdata["Players"]
            player2 = jdata["Players"]
            player3 = jdata["Players"]
            print("Connected Players: ")
            print(" - " + player1)
            print(" - " + player2)
            print(" - " + player3)
            ##fight
            print("Winner" + fight(player1,player2,player3))
            print("Rating Results: ")
            print(" - " + player1)
            print(" - " + player2)
            print(" - " + player3)
            #sendELO for fighters
            updateELO(player1["UserID"], player1["ELO"])
            updateELO(player2["UserID"], player2["ELO"])
            updateELO(player3["UserID"], player3["ELO"])
            #increment fight
            numFights -= 1
            iFight += 1
        else:
            print("Invalid game, trying again")
    #finished
    print("Fights Concluded")


if __name__ == '__main__':
    main()