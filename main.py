import os
import PokeCalcs as pcalcs
import pokeAPIfetch
import math
import requests.exceptions

#When altering, make sure not to have a trailing \ and also don't remove the preceding r
filesdirectory = r"D:\misc\PycharmProjects\pythonProject"
level = 50

#Stores all data for the user's team
myteamdict = {}

#Parse the user's showdown exported team file
def parse_user_teamfile():
    with open(os.path.join(filesdirectory, "team.txt"), 'r') as file:

        newmon=1 #Work variables
        for line in file.readlines():
            #If at a line with a new Pokemon name
            if(newmon==1):
                tempmon = {}
                temp = line.split()
                monname=temp[0].lower().replace(" ","-")
                newmon=0
                tempmon["name"] = monname

            #Indicate that we're about to read in a new pokemon name on the next loop iteration
            if(len(line)==1):
                newmon = 1
                myteamdict[monname]= tempmon

            if (not line.startswith("-")):
                if " Nature" in line:
                    tempmon["nature"] = line[:line.find(" Nature")]

            if(line.startswith('EVs')):
                tempmon["evs"]=line[5:-3]

        #This is to store the last mon
        myteamdict[monname]= tempmon

#Add stats and typings to an existing dictionary that contains multiple pokemon
def addteamstats(teamlist,filepath):
    with open(filepath, 'r') as file:

        #Use the firstline to determine whether the new mons match the previous run
        line = file.readline()[:-1]
        newmons = set()

        fromlistmons = set(line.split(","))

        for keys in teamlist:
            newmons.add(teamlist[keys]["name"])

        index = 0
        if(newmons == fromlistmons):
            all_lines = file.readlines()
            for templine in all_lines:
                #This split look like:
                #['bellibolt', '109', '64', '91', '103', '83', '45', 'electric', '']
                splitstring = templine[:-1].split(",")

                teamlist[splitstring[0]]["baseHP"]= splitstring[1]
                teamlist[splitstring[0]]["baseAtk"] = splitstring[2]
                teamlist[splitstring[0]]["baseDef"] = splitstring[3]
                teamlist[splitstring[0]]["baseSpA"] = splitstring[4]
                teamlist[splitstring[0]]["baseSpD"] = splitstring[5]
                teamlist[splitstring[0]]["baseSpe"] = splitstring[6]

                teamlist[splitstring[0]]["type1"] = splitstring[7]
                teamlist[splitstring[0]]["type2"] = splitstring[8]

                index += 1

        else:
            # Close the file, since it needs to be rewritten anyways
            file.close()

            with open(filepath, 'w') as file:
                pokeAPIfetch.fetchteam(file,teamlist)

#This builds the enemy team dictionary from the showdown string
def initenemydict(enemystring):

    #enemystring will look like this:
    #Lunala / Groudon / Tapu Fini / Tsareena / Incineroar / Stakataka

    enarray = enemystring.split(" / ")
    for index in range(0,len(enarray)):
        monname = enarray[index].lower().replace(" ", "-")
        subdict = {"name":monname}
        enemyteamdict[monname] = subdict

#Turns optional multiplier string into the end value to multiply by
def handle_mults(multstring):
    finalmult = 1
    if multstring != "":
        multsplit = multstring.split(",")
        allmults = []

        for val in multsplit:
            if "/" in val:
                tempval = val.split("/")
                allmults.append(float(int(tempval[0]) / int(tempval[1])))
            else:
                allmults.append(float(val))

        finalmult = 1.0
        for multval in allmults:
            finalmult *= multval

    return finalmult

setofmodes = ("d","d+","a","s")

#Load in user's team
parse_user_teamfile()
addteamstats(myteamdict, os.path.join(filesdirectory,"myteamcache.txt"))

#MAIN WORK LOOP
while True:
    mode = input('Input the mode:\n').lower()

    if mode not in setofmodes:
        print("Not a valid mode")
        continue

    #Speed mode
    if mode == "s":

        enemyteamdict = {}
        enemyteamstring = input('Enemy team string:\n')

        try:
            initenemydict(enemyteamstring)
            addteamstats(enemyteamdict, os.path.join(filesdirectory, "enemyteamcache.txt"))
        except requests.exceptions.JSONDecodeError:
            print("Probable typo in enemy team, please try again")
            continue

        for mon in myteamdict:
            print(f'{mon} speed is {pcalcs.calcstat(myteamdict[mon],"Spe",level)}')

        print("\n\n",end="")

        print("Left is no evs neutral nature, right is max invested plus nature")

        for mon in enemyteamdict:
            print(f'{mon} speed is {pcalcs.calcstat(enemyteamdict[mon], "Spe", level)} or {pcalcs.calcstat(enemyteamdict[mon], "Spe", level,evoverride="max",natureoverride="plus")}')

        print("\n",end="")

    #User is attacker mode
    if mode == "a":

        enemyteamstring = input('Enemy team string:\n')
        myattacker = input('Which mon is attacking?:\n').lower().replace(" ", "-")
        movename = input('Move name:\n').lower().replace(" ", "-")
        mults = input('Mults:\n').replace(" ","")

        enemyteamdict = {}
        initenemydict(enemyteamstring)

        try:
            addteamstats(enemyteamdict, os.path.join(filesdirectory,"enemyteamcache.txt"))
            movedata = {}
            pokeAPIfetch.movefetch(movename, movedata)

            stab = 0
            if (myteamdict[myattacker]["type1"] == movedata["movetype"]) or (
                    myteamdict[myattacker].get("type2") == movedata["movetype"]):
                stab = 1

        except requests.exceptions.JSONDecodeError:
            print("Probable typo, please try again")
            continue

        except KeyError:
            print("Probable typo in attacking mon, please try again")
            continue

        #Turn mults string into the final value to multiply by
        finalmult = handle_mults(mults)

        for mon in enemyteamdict:
            typeeffect = 1.0
            typeeffect *= pcalcs.get_type_multiplier(movedata["movetype"], enemyteamdict[mon]["type1"])
            typeeffect *= pcalcs.get_type_multiplier(movedata["movetype"], enemyteamdict[mon].get("type2"))

            if (movedata["movedmgclass"] == "physical"):
                mystat = pcalcs.calcstat(myteamdict[myattacker], "Atk", level)
                enemystatneutral = pcalcs.calcstat(enemyteamdict[mon], "Def", level)
                enemystatmaxevs = pcalcs.calcstat(enemyteamdict[mon], "Def", level, evoverride="max")
                enemystatmaxevsplusnature = pcalcs.calcstat(enemyteamdict[mon], "Def", level, evoverride="max", natureoverride= "plus")

            elif (movedata["movedmgclass"] == "special"):
                mystat = pcalcs.calcstat(myteamdict[myattacker], "SpA", level)
                enemystatneutral = pcalcs.calcstat(enemyteamdict[mon], "SpD", level)
                enemystatmaxevs = pcalcs.calcstat(enemyteamdict[mon], "SpD", level, evoverride="max")
                enemystatmaxevsplusnature = pcalcs.calcstat(enemyteamdict[mon], "SpD", level, evoverride="max", natureoverride= "plus")

            dmgneutral = pcalcs.damagenum(typeeffect, stab,mystat,enemystatneutral,level, movedata["power"], multval=finalmult)
            dmgmaxevs = pcalcs.damagenum(typeeffect, stab,mystat, enemystatmaxevs,level, movedata["power"], multval=finalmult)
            dmgmaxevsplusnature = pcalcs.damagenum(typeeffect, stab, mystat,enemystatmaxevsplusnature,level, movedata["power"], multval=finalmult)

            print(f'{mon} takes the following')
            print(f'No investment: {pcalcs.percenthp(math.floor(0.85*dmgneutral),enemyteamdict[mon],level)}-{pcalcs.percenthp(dmgneutral,enemyteamdict[mon],level)}%')
            print(f'Max HP: {pcalcs.percenthp(math.floor(0.85*dmgneutral),enemyteamdict[mon],level,evoverrideinternal="max")}-{pcalcs.percenthp(dmgneutral,enemyteamdict[mon],level,evoverrideinternal="max")}')
            print(f'Max defensive: {pcalcs.percenthp(math.floor(0.85*dmgmaxevs),enemyteamdict[mon],level)}-{pcalcs.percenthp(dmgmaxevs,enemyteamdict[mon],level)}')
            print(f'Max def w/ plus nature: {pcalcs.percenthp(math.floor(0.85*dmgmaxevsplusnature),enemyteamdict[mon],level)}-{pcalcs.percenthp(dmgmaxevsplusnature,enemyteamdict[mon],level)}')
            print(f'Max bulk: {pcalcs.percenthp(math.floor(0.85*dmgmaxevsplusnature),enemyteamdict[mon],level,evoverrideinternal="max")}-{pcalcs.percenthp(dmgmaxevsplusnature,enemyteamdict[mon],level,evoverrideinternal="max")}')
            print("\n")

    #User is defender mode
    if mode == "d" or mode =="d+":

        enemypokename = input('Enemy Pokemon name:\n').lower().replace(" ","-")
        movename = input('Move name:\n').lower().replace(" ","-")
        mults = input('Mults:\n').replace(" ","")

        try:
            enemypoke = pokeAPIfetch.get_singlemon(enemypokename)
            movedata = {}
            pokeAPIfetch.movefetch(movename,movedata)
        except requests.exceptions.JSONDecodeError:
            print("Likely mispelling, please try again")
            continue

        # Turn mults string into the final value to multiply by
        finalmult = handle_mults(mults)

        stab = 0
        if (enemypoke["type1"] == movedata["movetype"]) or (enemypoke.get("type2")==movedata["movetype"]):
            stab = 1

        print("\nLeft is no enemy evs, right is max evs")

        for mon in myteamdict:

            typeeffect = 1.0
            typeeffect *= pcalcs.get_type_multiplier(movedata["movetype"], myteamdict[mon]["type1"])
            typeeffect *= pcalcs.get_type_multiplier(movedata["movetype"], myteamdict[mon].get("type2"))

            if (movedata["movedmgclass"] == "physical"):
                if mode == "d":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "Atk", level)
                    enemystatinv = pcalcs.calcstat(enemypoke, "Atk", level ,evoverride="max")
                elif mode =="d+":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "Atk", level, natureoverride="plus")
                    enemystatinv = pcalcs.calcstat(enemypoke, "Atk", level, natureoverride="plus", evoverride="max")
                allystat = pcalcs.calcstat(myteamdict[mon], "Def", level)


            elif (movedata["movedmgclass"] == "special"):
                if mode == "d":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "SpA", level)
                    enemystatinv = pcalcs.calcstat(enemypoke, "SpA", level, evoverride="max")
                if mode == "d+":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "SpA", level, natureoverride="plus")
                    enemystatinv = pcalcs.calcstat(enemypoke, "SpA", level, natureoverride="plus", evoverride="max")

                allystat = pcalcs.calcstat(myteamdict[mon], "SpD", level)

            movedamageuninv = pcalcs.damagenum(typeeffect, stab, enemystatuninv, allystat, level, movedata["power"], multval=finalmult)
            movedamageinv = pcalcs.damagenum(typeeffect, stab, enemystatinv, allystat, level, movedata["power"], multval=finalmult)

            #low means a low damage roll
            percentdmguninv = pcalcs.percenthp(movedamageuninv,myteamdict[mon],level)
            percentdmguninvlow = pcalcs.percenthp(math.floor(0.85 * movedamageuninv), myteamdict[mon], level)

            percentdmginv = pcalcs.percenthp(movedamageinv,myteamdict[mon],level)
            percentdmginvlow = pcalcs.percenthp(math.floor(0.85 * movedamageinv), myteamdict[mon], level)

            print(f"{mon}: {percentdmguninvlow}-{percentdmguninv}% or {percentdmginvlow}-{percentdmginv}%")

        print("\n")

    #TODO Implement this mode
    #
    # #Freeattack mode (attack an enemy that is not part of your opponent's team)
    # if mode == "f":
    #     enemymon = input('Enemy enemy mon:\n')
    #     myattacker = input('Which mon is attacking?:\n').lower().replace(" ", "-")
    #     movename = input('Move name:\n').lower().replace(" ", "-")
    #     mults = input('Mults:\n').replace(" ","")
    #
    #     #Turn mults string into the final value to multiply by
    #     finalmult = handle_mults(mults)

