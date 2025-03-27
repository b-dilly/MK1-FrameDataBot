import json
import requests
from bs4 import BeautifulSoup

characterFilePath = "https://raw.githubusercontent.com/b-dilly/MK1-FrameDataBot/refs/heads/main/json/move_list_2025_02_05.json"
kameoFilePath = "https://raw.githubusercontent.com/b-dilly/MK1-FrameDataBot/refs/heads/main/json/move_list_kameo_2024_11_19.json"

# Open and load the JSON file
#FRAME DATA BOT


def HelpMessage():
    return "Cannot find that character's name or input.\nFor a list of all inputs, type in @MK1-FrameDataBot character-name all\n\nFormatting Examples:\nLiuKang must be entered as Liu, Liu Kang, or Liu-Kang\nKameo names must be entered as k.character-name\n\nNotation:\nH-Hold\nK-Kameo Button\nSS-Switch Stance"

def GetFrameData(charName: str, command_to_search: str):   
    
    
    isKameo = False
    
    characterName1 = normalize_name(charName)
    foundCharacterName = get_best_match(characterName1, 2)

    #the real url to use
    if "k." in charName:
        isKameo = True
        foundCharacterName = foundCharacterName.replace("k.","")
        data = requests.get(kameoFilePath)
    else:
        data = requests.get(characterFilePath)
    
    jsonData = json.loads(data.content)[2]["data"]
    if isKameo:
        moveList = [item for item in jsonData if item["kameo_name"] == foundCharacterName]
        json_normalAttacks = [item for item in moveList if item["category"] == "Kameo Moves"]
    else:
        moveList = [item for item in jsonData if item["char_name"] == foundCharacterName]
        json_normalAttacks = [item for item in moveList if item["category"] == "Basic Attacks"]
    

    if len(moveList) > 1:
        json_specialAttacks = [item for item in moveList if item["category"] == "Special Moves"]
        json_finishers = [item for item in moveList if item["category"] == "Finishers"]
        json_kameoMoves = ""
    else:
        json_kameoMoves = ""
        json_specialAttacks = ""
        json_finishers = ""

    for record in json_normalAttacks:
        if isKameo:
            if record['kameo_name'] == '':
                print("NO KAMEO NAME DETECTED")
                return HelpMessage()
        else:
            if record['char_name'] == '':
                print("NO CHARACTER NAME DETECTED")
                return HelpMessage()

    AdjustJsonData(json_normalAttacks)
    AdjustJsonData(json_specialAttacks)
    AdjustJsonData(json_finishers)
    
    
    allData = []
    if command_to_search == 'ALL':
        tempData = ""
        if isKameo:            
            for record in json_normalAttacks:
                if record['subcategory'] != 'Kameo Fatality':
                    tempData+=record['command']+"\n"
            allData.append(tempData)
            tempData = ""
            for record in json_normalAttacks:
                if record['subcategory'] == 'Kameo Fatality':
                    tempData+=record['command']+"\n"
            allData.append(tempData)
            tempData = ""
        else:
            for record in json_normalAttacks:
                tempData+=record['command']+"\n"
            allData.append(tempData)
            tempData = ""
            for record in json_specialAttacks:
                tempData+=record['command']+"\n"
            allData.append(tempData)
            tempData = ""
            for record in json_finishers:
                tempData+=record['command']+"\n"
            allData.append(tempData)
            tempData = ""
            for record in json_kameoMoves:
                tempData+=record['command']+"\n"
        
        for i in range(len(allData)):
            allData[i] = allData[i].replace('^', ',')
            input_list = allData[i].splitlines()
            # Remove duplicates while maintaining the order
            unique_list = []
            for item in input_list:
                if item not in unique_list:
                    unique_list.append(item)
            allData[i] = '\n'.join(unique_list)
        allDataString = "&".join(allData)
        
        return allDataString
        

    #putting all attack data back together with the query
    #this block only returns matches in the "command" field and any weird inputs they're associated with
    command_to_search = normalize_command(command_to_search)
    
    result = [entry for entry in json_normalAttacks if normalize_command(entry['command']) == command_to_search or (normalize_command(entry['parent_command']) == command_to_search and ('H' in entry['command'] or 'BB' in entry['command']))]           
    result += [entry for entry in json_specialAttacks if normalize_command(entry['command']) == command_to_search or (normalize_command(entry['parent_command']) == command_to_search and ('H' in entry['command'] or 'BB' in entry['command']))]
    result += [entry for entry in json_finishers if  normalize_command(entry['command']) == command_to_search or (normalize_command(entry['parent_command']) == command_to_search and ('H' in entry['command'] or 'BB' in entry['command']))]
    result += [entry for entry in json_kameoMoves if  normalize_command(entry['command']) == command_to_search or (normalize_command(entry['parent_command']) == command_to_search and ('H' in entry['command'] or 'BB' in entry['command']))]
    #removes all keys with no values in them
    result = [{key: value for key, value in obj.items() if value} for obj in result]
    
    #removing keys that i'm not interested in knowing. This is mostly to try to stay under the 2000 character limit
    attackData = ""
    keys_to_remove = ['id','subcategory','category','char_name','kameo_name','fblock_advantage', 'fblock_damage', 'hit_damage', 'block_damage', 'parent_command','active']    
    
    for item in result:
        for key in keys_to_remove:
            if key in item:
                del item[key]
        attackData += json.dumps(item, indent=4)

    if len(attackData) < 30:
        return HelpMessage
        
    #optimizing character space and making text more readable
    attackData = format_attack_data(attackData)

    #print(attackData)
    return attackData
def format_attack_data(atkData: str):
    atkData = atkData.replace('"', '')
    atkData = atkData.replace(',', '')
    atkData = atkData.replace('^', ',')
    atkData = atkData.replace('}{', '\n---')
    atkData = atkData.replace('{', '')
    atkData = atkData.replace('}', '')
    atkData = atkData.replace('Special Moves', 'Special')
    atkData = atkData.replace('    move_name:', '')
    atkData = atkData.replace('    block_type:', '**Target**\n')
    atkData = atkData.replace('    block_advantage:', '**Block**\n')
    atkData = atkData.replace('    hit_advantage:', '**Hit**\n')
    atkData = atkData.replace('    startup:', '**Startup**\n')
    atkData = atkData.replace('    recovery:', '**Recovery**\n')
    atkData = atkData.replace('    cancel:', '**Cancel**\n')
    atkData = atkData.replace('    command:', '**Input**\n')
    atkData = atkData.replace('    notes:', '**Notes**\n')
    atkData = atkData.replace('    properties:', '**Properties**\n')
    atkData = atkData.replace('    category:', '**Category**\n')
    atkData = atkData.replace('    subcategory:', '**Subcategory**\n')
    atkData = atkData.replace('    fblock_advantage:', '**F-Block-Adv**\n')
    atkData = atkData.replace('    fblock_damage:', '**F-Block-Dmg**\n')
    atkData = atkData.replace('    hit_damage:', '**Hit-Dmg**\n')
    atkData = atkData.replace('    block_damage:', '**Block-Dmg**\n')
    atkData = atkData.replace('    parent_command:', '**Parent-Command**\n')
    atkData = atkData.replace('    active:', '**Active**\n')
    atkData = atkData.replace('Hold ', 'HOLD+')
    atkData = atkData.replace('Overhead', 'O')
    atkData = atkData.replace('High', 'H')
    atkData = atkData.replace('Mid', 'M')
    atkData = atkData.replace('Low', 'L')
    atkData = atkData.replace('Unblockable', 'U')
    atkData = atkData.strip()
    return atkData
def AdjustJsonData(json):
    for obj in json:
        obj['move_name'] = "__**"+obj['move_name']+"**__"
        obj['command'] = str(obj['command']).replace(' ', '')
        obj['command'] = str(obj['command']).replace('KAMEO', 'K')
        obj['command'] = str(obj['command']).replace('Hold', 'H')
        obj['command'] = str(obj['command']).replace(',', '^')
        obj['command'] = str(obj['command']).replace('THROW', '1+3')
        obj['command'] = str(obj['command']).split('or')[0]
        obj['command'] = str(obj['command']).split('Or')[0]
        obj['parent_command'] = str(obj['parent_command']).replace(' ', '')
        obj['parent_command'] = str(obj['parent_command']).replace(',', '^')
        obj['parent_command'] = str(obj['parent_command']).replace('KAMEO', 'K')
        obj['parent_command'] = str(obj['parent_command']).replace('Hold', 'H')
        obj['parent_command'] = str(obj['parent_command']).replace('THROW', '1+3')
        obj['parent_command'] = str(obj['parent_command']).split('or')[0]
        obj['parent_command'] = str(obj['parent_command']).split('Or')[0]       
def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
        distances = new_distances

    return distances[-1]
def get_best_match(user_input, mispelling_tolerance):
    characters = ['Ashrah', 'Baraka', 'Conan', 'Cyrax', 'Ermac', 'General Shao', 'Ghostface', 'Geras', 'Havik', 'Homelander', 'Johnny Cage', 'Kenshi', 'Kitana', 'Kung Lao', 'Li Mei', 'Liu Kang', 'Mileena', 'Nitara', 'Noob Saibot', 'Omni Man', 'Peacemaker', 'Quan Chi', 'Raiden', 'Rain', 'Reiko', 'Reptile', 'Scorpion', 'Sektor', 'Shang Tsung', 'Sindel', 'Smoke', 'Sub-Zero', 'T-1000', 'Takeda', 'Tanya', 'k.Cyrax', 'k.Darrius', 'k.Ferra', 'k.Frost', 'k.Goro', 'k.Janet Cage', 'k.Jax', 'k.Kano', 'k.Khameleon', 'k.Kung Lao', 'k.Mavado', 'k.Motaro', 'k.Sareena', 'k.Scorpion', 'k.Sektor', 'k.Shujinko', 'k.Sonya', 'k.Stryker', 'k.Sub-Zero', 'k.Tremor']
    best_match = None
    lowest_distance = float('inf')

    for character in characters:
        distance = levenshtein_distance(user_input.lower(), character.lower())
        if distance < lowest_distance:
            lowest_distance = distance
            best_match = character
    if lowest_distance > mispelling_tolerance:
            return HelpMessage()
    return best_match
def normalize_command(command):
    return command.replace("+", "").replace("^", "").replace(",", "").lower()
def normalize_name(name):
    if name == "liu":
        name = "liu-kang"
    elif name == "k.sub":
        name = "k.sub-zero"
    elif name == "sub":
        name = "sub-zero"
    elif name == "johnny":
        name = "johnny-cage"
    elif name == "k.kung":
        name = "k.kung-lao"
    elif name == "kung":
        name = "kung-lao"
    elif name == "li":
        name = "li-mei"
    elif name == "general":
        name = "general-shao"
    elif name == "shao":
        name = "general-shao"
    elif name == "shang":
        name = "shang-tsung"
    elif name == "omni":
        name = "omni-man"
    elif name == "quan":
        name = "quan-chi"
    elif name == "noob":
        name = "noob-saibot"
    elif name == "t1000":
        name = "t-1000"
    elif name == "ghost":
        name = "ghostface"
    return name
def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    request = lowered.split(" ")
    
    #print(len(request))
    #if the response is only @bot character, then it will return the ALL function of the character.
    if len(request) == 2:
        return GetFrameData(normalize_name(request[1]), 'ALL')[:1999]
    #this is where characters separated by a hyphen(zub-zero, liu-kang, etc) get handled. If user inputs liu kang, it's corrected to liu-kang before being put through the function
    if len(request) > 3:
        request[1] = '-'.join(request[1:3])
        del request[2]
    request[2] = ''.join(request[2:]) 

    print("Here is what we're sending to the bot:")
    
    return GetFrameData(normalize_name(request[1]), request[2].upper())#[:1999]

