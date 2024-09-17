import json
import requests
from bs4 import BeautifulSoup

#FRAME DATA BOT
def HelpMessage():
    return "Cannot find that character's name or input.\nFor a list of all inputs, type in @MK1-FrameDataBot character-name all\n\nFormatting Examples:\nLiuKang must be entered as Liu, Liu Kang, or Liu-Kang\nKameo names must be entered as k.character-name\n\nNotation:\nH-Hold\nK-Kameo Button\nSS-Switch Stance"

def GetFrameData(charName: str, command_to_search: str):   
    
    #get latest date so all data returned is the latest database entry in kombatakademy
    url = 'https://mk1.kombatakademy.com/move-list/'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    #find the <select> tag by its name
    select_tag = soup.find('select', {'name': 'date'})
    #get the options inside the <select> tag
    selected_option = select_tag.find('option', {'selected': True})
    latestDate = selected_option['value']

    isKameo = False
    
    characterName1 = normalize_name(charName)
    foundCharacterName = get_best_match(characterName1, 2)

    #the real url to use
    if "k." in charName:
        isKameo = True
        foundCharacterName = foundCharacterName.replace("k.","")
        url = f'https://mk1.kombatakademy.com/move-list/?kameo={foundCharacterName}&date={latestDate}'
    else:
        url = f'https://mk1.kombatakademy.com/move-list/?character={foundCharacterName}&date={latestDate}'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)

    #beautiful soup stuff to parse html
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tags = soup.find_all('script')
    
    jsonContent =  script_tags[2].string
    if len(jsonContent) < 500:
        return HelpMessage

    #cleaning up the script code so it can be parsed in json format
    cleaned_text = jsonContent.replace('<script>', '')
    cleaned_text = cleaned_text.replace('let basicAttacks;', '')
    cleaned_text = cleaned_text.replace('let specialMoves;', '')
    cleaned_text = cleaned_text.replace('let finishers;', '')
    cleaned_text = cleaned_text.replace('let kameoMoves;', '')
    cleaned_text = cleaned_text.replace("'", "")
    cleaned_text = cleaned_text.replace("\\n", ". ")
    cleaned_text = cleaned_text.replace("\\u2022 ", '')
    cleaned_text = cleaned_text.replace('</script>', '')
    cleaned_text = cleaned_text.replace('\n\n\tbasicAttacks = ', '')
    cleaned_text = cleaned_text.replace('\n\tspecialMoves = ', '')
    cleaned_text = cleaned_text.replace('\n\tfinishers = ', '')
    cleaned_text = cleaned_text.replace('\n\tkameoMoves = ', '')
    cleaned_text = cleaned_text.lstrip()

    #getting the indexes of the first [ and last ] to finish cleaning up the json string 
    first_open_bracket_index = cleaned_text.find('[')
    last_close_bracket_index = cleaned_text.rfind(']')
    substring = cleaned_text[first_open_bracket_index:last_close_bracket_index+1]
    moveList = substring.split(';')

    json_normalAttacks = json.loads(moveList[0])
    if len(moveList) > 1:
        json_specialAttacks = json.loads(moveList[1])
        json_finishers = json.loads(moveList[2])
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
    keys_to_remove = ['subcategory','category','char_name','kameo_name','fblock_advantage', 'fblock_damage', 'hit_damage', 'block_damage', 'parent_command','active']    
    
    for item in result:
        for key in keys_to_remove:
            if key in item:
                del item[key]
        attackData += json.dumps(item, indent=4)

    if len(attackData) < 30:
        return HelpMessage
        
    #optimizing character space and making text more readable
    attackData = format_attack_data(attackData)

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
        obj['command'] = obj['command'].replace(' ', '')
        obj['command'] = obj['command'].replace('KAMEO', 'K')
        obj['command'] = obj['command'].replace('Hold', 'H')
        obj['command'] = obj['command'].replace(',', '^')
        obj['command'] = obj['command'].replace('THROW', '1+3')
        obj['command'] = obj['command'].split('or')[0]
        obj['command'] = obj['command'].split('Or')[0]
        obj['parent_command'] = obj['parent_command'].replace(' ', '')
        obj['parent_command'] = obj['parent_command'].replace(',', '^')
        obj['parent_command'] = obj['parent_command'].replace('KAMEO', 'K')
        obj['parent_command'] = obj['parent_command'].replace('Hold', 'H')
        obj['parent_command'] = obj['parent_command'].replace('THROW', '1+3')
        obj['parent_command'] = obj['parent_command'].split('or')[0]
        obj['parent_command'] = obj['parent_command'].split('Or')[0]       
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
    characters = ['ashrah', 'baraka', 'conan', 'cyrax', 'ermac', 'general-shao', 'ghost-face', 'geras', 'havik', 'homelander', 'johnny-cage', 'kenshi', 'kitana', 'kung-lao', 'li-mei', 'liu-kang', 'mileena', 'nitara', 'noob-saibot', 'omni-man', 'peacemaker', 'quan-chi', 'raiden', 'rain', 'reiko', 'reptile', 'scorpion', 'sektor', 'shang-tsung', 'sindel', 'smoke', 'sub-zero', 't-1000', 'takeda', 'tanya', 'k.cyrax', 'k.darrius', 'k.ferra', 'k.frost', 'k.goro', 'k.janet-cage', 'k.jax', 'k.kano', 'k.khameleon', 'k.kung-lao', 'k.mavado', 'k.motaro', 'k.sareena', 'k.scorpion', 'k.sektor', 'k.shujinko', 'k.sonya', 'k.stryker', 'k.sub-zero', 'k.tremor']
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
        name = "ghost-face"
    return name
def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    request = lowered.split(" ")
    
    print(len(request))
    #if the response is only @bot character, then it will return the ALL function of the character.
    if len(request) == 2:
        return GetFrameData(normalize_name(request[1]), 'ALL')[:1999]
    #this is where characters separated by a hyphen(zub-zero, liu-kang, etc) get handled. If user inputs liu kang, it's corrected to liu-kang before being put through the function
    if len(request) > 3:
        request[1] = '-'.join(request[1:3])
        del request[2]
    request[2] = ''.join(request[2:]) 


    return GetFrameData(normalize_name(request[1]), request[2].upper())[:1999]


