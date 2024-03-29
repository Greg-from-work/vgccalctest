import math
import PokeStructures as pstructs

#Pass in a mon dictionary and a stat to calculate
def calcstat(mondict,statname,level,natureoverride="",evoverride=""):

    basestat = int(mondict["base" + statname])

    if evoverride == "max":
        statev=252
    elif mondict.get("evs"):
        templist = mondict["evs"].split(" / ")

        statev = 0
        for val in templist:
            if statname in val:
                statev = int(val[:val.find(" ")])
    else:
        statev = 0

    if natureoverride == "plus":
        naturemult = 1.1
    elif natureoverride == "minus":
        naturemult = 0.9
    elif mondict.get("nature"):

        templist = pstructs.natures[mondict["nature"]]
        if templist[0] == statname:
            naturemult = 1.1
        elif templist[1] == statname:
            naturemult=0.9
        else:
            naturemult = 1.0

    else:
        naturemult=1.0

    if statname == "HP":
        return (math.floor(((((2*basestat)+31)+math.floor(statev/4))*level)/100)+level+10)
    else:
        return ( math.floor((math.floor(((((2 * basestat) + 31) + math.floor(statev / 4)) * level)/100)+5)*naturemult) )


#Get the number of points of damage that a move deals
def damagenum(typeeffect,stab,attackingstat,defendingstat,level,movepower,multval=1):

    init = math.floor( math.floor( math.floor((2 * level) / 5 + 2) * movepower * attackingstat / defendingstat ) / 50 + 2 )

    if stab == 0:
        poststab = init
    else:
        poststab = round(init * 1.5)

    posttypeeffect = round(poststab * typeeffect)

    return round( posttypeeffect*multval)

def percenthp(dmg,mon,level,evoverrideinternal=""):

    return round( (dmg/calcstat(mon,"HP",level,evoverride=evoverrideinternal))*100 ,1)

def get_type_multiplier(attacking_type, defending_type):
    return pstructs.type_resistances[attacking_type].get(defending_type, 1.0)