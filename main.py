import os
import PokeStructures as pstructs
import PokeCalcs as pcalcs
import pokeAPIfetch
import math

#These are my globals. Pretty bad practice I would imagine
myteamlist = {}
#enemyteamlist = {}
level = 50

#make sure not to have a trailing \
filesdirectory = r"D:\misc\PycharmProjects\pythonProject"
#

#TODO
# Dynamic filepaths
# Fix the fixable rounding issues. I think damage calcs should use // instead of / for division?
# cleanup
# comments
# Should I reshuffle functions around?
# freeattack mode

# ver2 incorporate sprites?
# ver3 interactive?

def get_type_multiplier(attacking_type, defending_type):
    return pstructs.type_resistances[attacking_type].get(defending_type, 1.0)

def parsefunction():
    file = open(os.path.join(filesdirectory, "team.txt"), 'r')

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
            myteamlist[monname]= tempmon

        if (not line.startswith("-")):
            if " Nature" in line:
                tempmon["nature"] = line[:line.find(" Nature")]

        #Read in the EVs line, and store it for the current mon
        if(line.startswith('EVs')):
            tempmon["evs"]=line[5:-3]

    #This is for lastmon
    myteamlist[monname]= tempmon

    file.close()

def addteamstats(teamlist,filepath):
    file = open(filepath, 'r')

    #Use the firstline to determine whether the newmons match the previous run
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
        file = open(filepath, 'w')
        pokeAPIfetch.fetchteam(file,teamlist)
        file.close()

#This builds the enemy team disctionary from the showdown string
def buildenemydict(enemystring):

    #enemystring will look like this:
    ##Lunala / Groudon / Tapu Fini / Tsareena / Incineroar / Stakataka

    #enemyteamlist
    enarray = enemystring.split(" / ")
    for index in range(0,len(enarray)):
        monname = enarray[index].lower().replace(" ", "-")
        subdict = {"name":monname}
        enemyteamlist[monname] = subdict

myteamloaded = 0
while True:
    mode = input('Input the mode:\n')

    if mode == "s":

        enemyteamlist = {}
        enemyteamstring = input('Enemy team string:\n')

        if myteamloaded == 0:
            parsefunction()
            addteamstats(myteamlist, os.path.join(filesdirectory,"myteamcache.txt"))
            myteamloaded = 1

        buildenemydict(enemyteamstring)
        addteamstats(enemyteamlist, os.path.join(filesdirectory,"enemyteamcache.txt"))

        for mon in myteamlist:
            print(f'{mon} speed is {pcalcs.calcstat(myteamlist[mon],"Spe",level)}')

        print("\n",end="")

        for mon in enemyteamlist:
            print(f'{mon} neutral speed is {pcalcs.calcstat(enemyteamlist[mon], "Spe", level)} or {pcalcs.calcstat(enemyteamlist[mon], "Spe", level,evoverride="max",natureoverride="plus")}')

        print("\n",end="")

    if mode == "a":

        enemyteamstring = input('Enemy team string:\n')
        myattacker = input('Which mon is attacking?:\n').replace(" ", "-")
        movename = input('Move name:\n').replace(" ", "-")
        mults = input('Mults:\n')

        if myteamloaded == 0:
            parsefunction()
            addteamstats(myteamlist, os.path.join(filesdirectory,"myteamcache.txt"))
            myteamloaded = 1

        #Rebuild enemy team dict. Probably a more efficient way, though it will avoid API calls if a teamfile is there
        enemyteamlist = {}
        buildenemydict(enemyteamstring)
        addteamstats(enemyteamlist, os.path.join(filesdirectory,"enemyteamcache.txt"))

        movedata = {}
        pokeAPIfetch.movefetch(movename, movedata)

        finalmult = 1
        if mults != "":
            multsplit = mults.split(",")
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

        stab = 0
        if (myteamlist[myattacker]["type1"] == movedata["movetype"]) or (myteamlist[myattacker].get("type2") == movedata["movetype"]):
            stab = 1

        for mon in enemyteamlist:
            typeeffect = 1.0
            typeeffect *= get_type_multiplier(movedata["movetype"], enemyteamlist[mon]["type1"])
            typeeffect *= get_type_multiplier(movedata["movetype"], enemyteamlist[mon].get("type2"))

            if (movedata["movedmgclass"] == "physical"):
                mystat = pcalcs.calcstat(myteamlist[myattacker], "Atk", level)
                enemystatneutral = pcalcs.calcstat(enemyteamlist[mon], "Def", level)
                enemystatmaxevs = pcalcs.calcstat(enemyteamlist[mon], "Def", level, evoverride="max")
                enemystatmaxevsplusnature = pcalcs.calcstat(enemyteamlist[mon], "Def", level, evoverride="max", natureoverride= "plus")

            elif (movedata["movedmgclass"] == "special"):
                mystat = pcalcs.calcstat(myteamlist[myattacker], "SpA", level)
                enemystatneutral = pcalcs.calcstat(enemyteamlist[mon], "SpD", level)
                enemystatmaxevs = pcalcs.calcstat(enemyteamlist[mon], "SpD", level, evoverride="max")
                enemystatmaxevsplusnature = pcalcs.calcstat(enemyteamlist[mon], "SpD", level, evoverride="max", natureoverride= "plus")

            dmgneutral = pcalcs.damagenum(typeeffect, stab,mystat,enemystatneutral,level, movedata["power"], multval=finalmult)
            dmgmaxevs = pcalcs.damagenum(typeeffect, stab,mystat, enemystatmaxevs,level, movedata["power"], multval=finalmult)
            dmgmaxevsplusnature = pcalcs.damagenum(typeeffect, stab, mystat,enemystatmaxevsplusnature,level, movedata["power"], multval=finalmult)

            # perneutral = pcalcs.percenthp(dmgneutral,enemyteamlist[mon],level)
            # permaxhp = pcalcs.percenthp(dmgneutral,enemyteamlist[mon],level,evoverrideinternal="max")
            # permaxdef = pcalcs.percenthp(dmgmaxevs,enemyteamlist[mon],level)
            # permaxdefplusnature = pcalcs.percenthp(dmgmaxevsplusnature,enemyteamlist[mon],level)
            # permaxhpmaxdefplusnature = pcalcs.percenthp(dmgneutral,enemyteamlist[mon],level,evoverrideinternal="max")

            #TODO is the max hp one slightly off, or is that rounding error elsewhere???

            print(f'{mon} takes the following')
            print(f'No investment: {pcalcs.percenthp(math.floor(0.85*dmgneutral),enemyteamlist[mon],level)}-{pcalcs.percenthp(dmgneutral,enemyteamlist[mon],level)}%')
            print(f'Max HP: {pcalcs.percenthp(math.floor(0.85*dmgneutral),enemyteamlist[mon],level,evoverrideinternal="max")}-{pcalcs.percenthp(dmgneutral,enemyteamlist[mon],level,evoverrideinternal="max")}')
            print(f'Max defensive: {pcalcs.percenthp(math.floor(0.85*dmgmaxevs),enemyteamlist[mon],level)}-{pcalcs.percenthp(dmgmaxevs,enemyteamlist[mon],level)}')
            print(f'Max def w/ plus nature: {pcalcs.percenthp(math.floor(0.85*dmgmaxevsplusnature),enemyteamlist[mon],level)}-{pcalcs.percenthp(dmgmaxevsplusnature,enemyteamlist[mon],level)}')
            print(f'Max bulk: {pcalcs.percenthp(math.floor(0.85*dmgmaxevsplusnature),enemyteamlist[mon],level,evoverrideinternal="max")}-{pcalcs.percenthp(dmgmaxevsplusnature,enemyteamlist[mon],level,evoverrideinternal="max")}')
            print("\n")

    if mode == "d" or mode =="d+":
        parsefunction()
        addteamstats(myteamlist,os.path.join(filesdirectory,"myteamcache.txt"))


        enemypokename = input('Enemy Pokemon name:\n').replace(" ","-")
        movename = input('Move name:\n').replace(" ","-")
        mults = input('Mults:\n')

        finalmult = 1
        if mults != "":
            multsplit = mults.split(",")
            allmults = []

            for val in multsplit:
                if "/" in val:
                    tempval = val.split("/")
                    allmults.append(float(int(tempval[0])/int(tempval[1])))
                else:
                    allmults.append(float(val))

            finalmult = 1.0
            for multval in allmults:
                finalmult *= multval



        # monlist,statname,level,natureoverride="",evoverride=""
        enemypoke = pokeAPIfetch.get_singlemon(enemypokename)
        movedata = {}
        pokeAPIfetch.movefetch(movename,movedata)

        stab = 0
        if (enemypoke["type1"] == movedata["movetype"]) or (enemypoke.get("type2")==movedata["movetype"]):
            stab = 1

        for mon in myteamlist:

            typeeffect = 1.0
            typeeffect *= get_type_multiplier(movedata["movetype"], myteamlist[mon]["type1"])
            typeeffect *= get_type_multiplier(movedata["movetype"], myteamlist[mon].get("type2"))

            if (movedata["movedmgclass"] == "physical"):
                if mode == "d":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "Atk", level)
                    enemystatinv = pcalcs.calcstat(enemypoke, "Atk", level ,evoverride="max")
                elif mode =="d+":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "Atk", level, natureoverride="plus")
                    enemystatinv = pcalcs.calcstat(enemypoke, "Atk", level, natureoverride="plus", evoverride="max")
                allystat = pcalcs.calcstat(myteamlist[mon], "Def", level)


            elif (movedata["movedmgclass"] == "special"):
                if mode == "d":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "SpA", level)
                    enemystatinv = pcalcs.calcstat(enemypoke, "SpA", level, evoverride="max")
                if mode == "d+":
                    enemystatuninv = pcalcs.calcstat(enemypoke, "SpA", level, natureoverride="plus")
                    enemystatinv = pcalcs.calcstat(enemypoke, "SpA", level, natureoverride="plus", evoverride="max")

                allystat = pcalcs.calcstat(myteamlist[mon], "SpD", level)

            movedamageuninv = pcalcs.damagenum(typeeffect, stab, enemystatuninv, allystat, level, movedata["power"], multval=finalmult)
            movedamageinv = pcalcs.damagenum(typeeffect, stab, enemystatinv, allystat, level, movedata["power"], multval=finalmult)

            percentdmguninv = pcalcs.percenthp(movedamageuninv,myteamlist[mon],level)
            percentdmguninvlow = pcalcs.percenthp(math.floor(0.85 * movedamageuninv), myteamlist[mon], level)

            percentdmginv = pcalcs.percenthp(movedamageinv,myteamlist[mon],level)
            percentdmginvlow = pcalcs.percenthp(math.floor(0.85 * movedamageinv), myteamlist[mon], level)

            print(f"{mon}: {percentdmguninvlow}-{percentdmguninv}% or {percentdmginvlow}-{percentdmginv}%")

        print("\n")


# example of enemy team building
# buildenemydict("Lunala / Groudon / Tapu Fini / Tsareena / Incineroar / Stakataka")
# addteamstats(enemyteamlist,os.fspath(r"D:\misc\PycharmProjects\scratchspace\entemp.txt"))