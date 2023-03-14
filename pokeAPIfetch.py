import requests

def get_singlemon(monname):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{monname}')
    jsonobj = response.json()

    singlemon = {"name":monname}

    singlemon["baseHP"] = jsonobj["stats"][0]["base_stat"]
    singlemon["baseAtk"] = jsonobj["stats"][1]["base_stat"]
    singlemon["baseDef"] = jsonobj["stats"][2]["base_stat"]
    singlemon["baseSpA"] = jsonobj["stats"][3]["base_stat"]
    singlemon["baseSpD"] = jsonobj["stats"][4]["base_stat"]
    singlemon["baseSpe"] = jsonobj["stats"][5]["base_stat"]

    typecount = len(jsonobj["types"])
    if typecount == 1:
        singlemon["type1"] = jsonobj["types"][0]["type"]["name"]
        singlemon["type2"] = ""
    else:
        singlemon["type1"] = jsonobj["types"][0]["type"]["name"]
        singlemon["type2"] = jsonobj["types"][1]["type"]["name"]

    return singlemon

def movefetch(move,movedata):
    response = requests.get(f'https://pokeapi.co/api/v2/move/{move}')
    jsonobj = response.json()

    movedata["power"] = jsonobj["power"]
    movedata["movetype"] = jsonobj["type"]["name"]
    movedata["movedmgclass"] = jsonobj["damage_class"]["name"]

#For when a whole team needs to be fetched from PokeAPI
def fetchteam(file,teamlist):
    # Add all of the new properties
    for keys in teamlist:
        # Get extra data (typings etc.) for current mon
        tempmondict = get_singlemon(teamlist[keys]["name"])
        for key in tempmondict:
            # name is a duplicate entry so this is a bootleg way to ignore it
            if key != "name":
                teamlist[keys][key] = tempmondict[key]

    # Generate the first line, which contains just the mon names
    index = 0
    for keys in teamlist:
        file.write(teamlist[keys]["name"])
        if index < 5:
            file.write(",")
        index += 1
    file.write("\n")

    # Generate the remaining 6 lines
    for keys in teamlist:
        file.write(teamlist[keys]["name"] + ",")
        file.write(str(teamlist[keys]["baseHP"]) + "," + str(teamlist[keys]["baseAtk"]) + "," + str(
            teamlist[keys]["baseDef"]) + ",")
        file.write(str(teamlist[keys]["baseSpA"]) + "," + str(teamlist[keys]["baseSpD"]) + "," + str(
            teamlist[keys]["baseSpe"]) + ",")
        file.write(teamlist[keys]["type1"] + "," + teamlist[keys]["type2"])
        file.write("\n")