
# This is functions for the BTD6 automatic script. Look at main to see the usage
# These are meant to be simple functions, and the logic will mostly be present in main.py,
# when using the functions
# Written 27/12 2022, Kristian

import pyautogui as auto
import time
import datetime
import keyboard
import os
from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity
from pynput.mouse import Listener
import pytesseract

auto.FAILSAFE = False
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

cwd = os.getcwd()

class Tower:
    difficulty = ''
    mode = ''
    hero = ''
    stage_level = 1

    def __init__(self, position, hotkey):
        self.position = position
        self.hotkey = hotkey
        self.buyPrice = Tower.getBuyPrice(self)
        self.upgradePath = '000'

    def __str__(self):
        return f'Tower: P:{self.position}, H:{self.hotkey}, B:{self.getBuyPrice()}, D:{self.difficulty}'

    # Upgrade tower methods
    @staticmethod
    def getUpgrades():
        upgrades = None
        time.sleep(0.2)
        threshold = 0.99  # percent value
        for screenshot in [auto.screenshot(region=(8, 555, 57, 590)), auto.screenshot(region=(1408, 555, 57, 590))]:
            screenshot.save('screenshot.png')

            # Iterate through all images in the "upgrade level" folder
            folder = os.path.join(cwd, 'Pictures', 'upgrade levels')
            for image_filename in os.listdir(folder):
                # Open the target image file
                image = Image.open(os.path.join(folder, image_filename))

                # Turn the images to grayscale. Works best in grayscale
                screenshot_gray = screenshot.convert('L')

                # Convert the images to NumPy arrays
                screenshot_array = np.array(screenshot_gray)
                image_array = np.array(image)

                # Calculate the SSIM between the images
                ssim = structural_similarity(screenshot_array, image_array)

                if ssim > threshold:
                    upgrades = str(image_filename[-7:-4])
                    return upgrades

        if upgrades is None:
            print('Entering towerdebug from upgrades')
            towerDebug()

    def upgradeTower(self, upgradeTo):
        auto.click(self.position)
        upgradeFrom = Tower.getUpgrades()
        if self.upgradePath > upgradeTo:
            print('Exiting early')
            keyboard.send('esc')
            time.sleep(0.1)
            return

        upgradeTo = str(upgradeTo)
        upgradeHotkeys = [',', '.', 'slash']
        for i in range(3):
            while upgradeFrom[i] < upgradeTo[i]:
                keyboard.send(upgradeHotkeys[i])
                time.sleep(0.05)
                upgradeFrom = Tower.getUpgrades()
                self.useAbilities()
        time.sleep(0.1)
        # Make the map clean again
        keyboard.send('esc')
        time.sleep(0.1)
        self.upgradePath = upgradeTo

    # Place tower methods
    @staticmethod
    def getMoney():
        # Ser ok ut. Køddar på talet 4, og 41. Tolkar som H, A, L, bl.a.
        # Ikkje eit problem for mitt bruk
        time.sleep(0.1)
        screenshot = auto.screenshot(region=(440, 80, 175, 55))
        screenshot.save('SMoney.png')
        image = Image.open(os.path.join(cwd, 'SMoney.png')).convert('L')

        # Threshold the image to separate the digits from the background
        threshold = 254
        image = image.point(lambda x: 0 if x > threshold else 255)
        image.save('SMoney_black.png')
        # Extract the text from the image using pytesseract
        text = pytesseract.image_to_string(image, config='--psm 7')

        moneyCount = []
        for n in text:
            try:
                digit = int(n)
                moneyCount.append(n)
            except ValueError:
                continue

        try:
            money = int(''.join(moneyCount))
        except ValueError:
            money = 0
        return money

    def placeTower(self):
        # Loops untill enough money enough times. Can be wrong readings sometimes
        trueCount = 0
        succesiveFalseReadings = 0
        while True:
            myMoney = Tower.getMoney()
            if self.buyPrice < myMoney:
                trueCount += 1
                time.sleep(0.05)
                if trueCount > 2:
                    break
            else:
                trueCount = 0

            # If the money reading is false many times, debug
            if myMoney == 0:
                succesiveFalseReadings += 1
                if succesiveFalseReadings > 8:
                    print('Entering towerdebug from getmoney')
                    towerDebug()
            else:
                succesiveFalseReadings = 0
            self.useAbilities()

        # Place the monkey on the coords
        auto.moveTo(self.position)
        time.sleep(0.1)
        keyboard.send(self.hotkey)
        time.sleep(0.1)
        auto.click(self.position)
        time.sleep(0.1)
        # Move to monkey menu, such that the unplaced monkey disappear
        auto.moveTo((2080, 684))
        time.sleep(0.2)


    # Utility-functions
    def setStageLevel(self, reading):
        if reading != 9001:
            Tower.stage_level = reading

    def useAbilities(self):
        ability1 = '1'
        ability2 = '2'
        ability3 = '3'
        if self.hero == 'adora':
            ability2 = ability3
        if self.hero == 'benjamin':
            ability1 = '9'

        # Blacklist ability use before crucial stages
        notAbility1List = [21, 22, 23, 31, 32, 38, 39]
        notAbility2List = [74, 75]
        currentStage = self.getStageLevel()
        self.setStageLevel(currentStage)
        if currentStage not in notAbility1List and currentStage != 9001:
            keyboard.send(ability1)
        time.sleep(0.05)
        if currentStage not in notAbility2List and currentStage != 9001:
            keyboard.send(ability2)
            time.sleep(0.05)
            keyboard.send(ability3)
        time.sleep(0.05)
        return

    #TODO: Fiks ting med lagring av bileter. Må sjå fint ut! Søk på alle img.save() greier!
    @staticmethod
    def getStageLevel():
        for screenshot in [auto.screenshot(region=(1075, 85, 225, 65)), auto.screenshot(region=(1585, 85, 225, 65))]:
            screenshot.save('StageLevel.png')
            image = Image.open(os.path.join(cwd, 'StageLevel.png')).convert('L')

            # Threshold the image to separate the digits from the background
            threshold = 254
            image = image.point(lambda x: 0 if x > threshold else 255)
            image.save('StageLevel_black.png')
            # Extract the text from the image using pytesseract
            text = pytesseract.image_to_string(image, config='--psm 7')

            levelCount = []
            for s in text:
                if s == '/':
                    break
                try:
                    digit = int(s)
                    levelCount.append(s)
                except ValueError:
                    continue

            try:
                level = int(''.join(levelCount))
            except ValueError:
                continue

            return level
        # return value if reading is wrong
        return 9001

    def getBuyPrice(self):
        difficulty = self.difficulty

        # Set the monkey cost to percent value of medium cost
        diffModifier = 1.08
        if difficulty == 'easy':
            diffModifier = 0.85
        if difficulty == 'medium':
            diffModifier = 1.0
        if difficulty == 'hard':
            diffModifier = 1.08
        if difficulty == 'impoppable':
            diffModifier = 1.2

        monkeyBaseCostDict = {
            'dart monkey': '200', 'glue gunner': '225',
            'boomerang monkey': '275', 'bomb shooter': '525',
            'tack shooter': '280', 'ice monkey': '500',
            'wizard monkey': '375', 'super monkey': '2500',
            'ninja monkey': '500', 'alchemist': '550',
            'druid': '400', 'banana farm': '1125',
            'spike factory': '850', 'monkey village': '1175',
            'engineer monkey': '400', 'sniper monkey': '350',
            'monkey sub': '325', 'monkey buccaneer': '500',
            'monkey ace': '800', 'heli pilot': '1600',
            'mortar monkey': '750', 'dartling gunner': '850',
            'quincy': '540', 'qwendolin': '900',
            'striker jones': '750', 'obyn': '650',
            'geraldo': '700', 'captin churchill': '2000',
            'benjamin': '1200', 'ezili': '600',
            'pat fusty': '800', 'adora': '1000',
            'admiral brickell': '750', 'etienne': '850',
            'sauda': '600', 'psi': '1000'
        }
        monkey = convertHotkeyToMonkey(self.hotkey)
        if monkey == 'hero':
            monkey = self.hero
            if self.mode != 'chimps':
                return int(monkeyBaseCostDict[monkey])*diffModifier*0.9
        return int(monkeyBaseCostDict[monkey]) * diffModifier

    def changeTargeting(self, target='strong'):
        auto.click(self.position)
        time.sleep(0.2)
        if target == 'last':
            for i in range(1):
                keyboard.send('tab')
                time.sleep(0.2)
            keyboard.send('esc')
            time.sleep(0.2)
            return
        elif target == 'close':
            for i in range(2):
                keyboard.send('tab')
                time.sleep(0.2)
            keyboard.send('esc')
            time.sleep(0.2)
            return
        elif target == 'strong':
            for i in range(3):
                keyboard.send('tab')
                time.sleep(0.2)
            keyboard.send('esc')
            time.sleep(0.2)
            return

    def sellTower(self):
        auto.click(self.position)
        time.sleep(0.1)
        keyboard.send('backspace')
        time.sleep(0.1)

# Clicks two times to get rid of level up, or finds the return to home, when stage is complete
def towerDebug():
    # Debug
    debugImage = auto.screenshot()
    timestamp = datetime.datetime.now().strftime("%d.%m %H %M %S")
    debugPath = os.path.join(cwd, 'Debug Shots', f'upgradeDebug {timestamp}.png')
    imagePath = os.path.join(cwd, 'Pictures', 'Search images')
    debugImage.save(debugPath)

    #TODO: Gjer slik at denne går lengre. Hadde episode der den avslutta på runde 58, men klarte å vinne. Kanskje restarte
    #TODO: for å vere sikker? Eller køyre til defeat? Restart er raskare
    upgradeDebugCount = 0
    while True and upgradeDebugCount < 250:  # 250*3 sekund er 12.5 min. Det gjer nok tid til å tape eller vinne bana
        if auto.locateOnScreen(os.path.join(imagePath, 'levelUpImage.png'),
                               confidence=0.7, region=(900, 660, 420, 100), grayscale=True) is not None:
            auto.click()
            time.sleep(1)
            auto.click()
            time.sleep(3)
            raise DebugException

        if auto.locateOnScreen(os.path.join(imagePath, 'defeatImage.png'),
                               confidence=0.7, region=(720, 320, 740, 210), grayscale=True) is not None:
            print('Defeated! Trying again...')
            raise DefeatException

        if auto.locateOnScreen(os.path.join(imagePath, 'victoryShot.png'),
                               confidence=0.7, region=(660, 80, 1000, 370), grayscale=True):
            print('Found the victory image!')
            raise StageCompleteException
        upgradeDebugCount += 1
        print(f'This is loop {upgradeDebugCount}')
        time.sleep(3)


class StageCompleteException(Exception):
    """Stage is done! Well done"""
    pass

class DebugException(Exception):
    """Something wrong from debug()"""
    pass

class DefeatException(Exception):
    """Defeated! Try again"""
    pass



#Converts the monkey name to corresponding hotkey, and vice versa.
def convertMonkeyToHotkey(monke):
    monkeyLibrary = {
        'q': 'dart monkey', 'w': 'boomerang monkey',
        'e': 'bomb shooter', 'r': 'tack shooter',
        't': 'ice monkey', 'y': 'glue gunner',
        'a': 'wizard monkey',
        's': 'super monkey', 'd': 'ninja monkey',
        'f': 'alchemist', 'g': 'druid',
        'h': 'banana farm', 'j': 'spike factory',
        'k': 'monkey village', 'l': 'engineer monkey',
        'z': 'sniper monkey', 'x': 'monkey sub',
        'c': 'monkey buccaneer', 'v': 'monkey ace',
        'b': 'heli pilot', 'n': 'mortar monkey',
        'm': 'dartling gunner', 'i': 'beast handler',
        'dart monkey': 'q',
        'boomerang monkey': 'w', 'bomb shooter': 'e',
        'tack shooter': 'r', 'ice monkey': 't',
        'glue gunner': 'y', 'beast handler':'i',
        'wizard monkey': 'a', 'super monkey': 's',
        'ninja monkey': 'd', 'alchemist': 'f',
        'druid': 'g', 'banana farm': 'h',
        'spike factory': 'j', 'monkey village': 'k',
        'engineer monkey': 'l', 'sniper monkey': 'z',
        'monkey sub': 'x', 'monkey buccaneer': 'c',
        'monkey ace': 'v', 'heli pilot': 'b',
        'mortar monkey': 'n', 'dartling gunner': 'm',
        'quincy':'u', 'qwendolin': 'u',
        'striker jones': 'u', 'obyn': 'u',
        'geraldo': 'u', 'captin churchill': 'u',
        'benjamin': 'u', 'ezili': 'u',
        'pat fusty': 'u', 'adora': 'u',
        'admiral brickell': 'u', 'etienne': 'u',
        'sauda': 'u', 'psi': 'u',
    }

    if len(monke) != 1:
        monke = monkeyLibrary[monke]
    return monke
def convertHotkeyToMonkey(hotKey):
    monkeyLibrary = {
        'q': 'dart monkey', 'w': 'boomerang monkey',
        'e': 'bomb shooter', 'r': 'tack shooter',
        't': 'ice monkey', 'y': 'glue gunner',
        'u': 'hero', 'a': 'wizard monkey',
        's': 'super monkey', 'd': 'ninja monkey',
        'f': 'alchemist', 'g': 'druid',
        'h': 'banana farm', 'j': 'spike factory',
        'k': 'monkey village', 'l': 'engineer monkey',
        'z': 'sniper monkey', 'x': 'monkey sub',
        'c': 'monkey buccaneer', 'v': 'monkey ace',
        'b': 'heli pilot', 'n': 'mortar monkey',
        'm': 'dartling gunner', 'dart monkey': 'q',
        'i':'beast handler',
        'boomerang monkey': 'w', 'bomb shooter': 'e',
        'tack shooter': 'r', 'ice monkey': 't',
        'glue gunner': 'y', 'hero': 'u',
        'wizard monkey': 'a', 'super monkey': 's',
        'ninja monkey': 'd', 'alchemist': 'f',
        'druid': 'g', 'banana farm': 'h',
        'spike factory': 'j', 'monkey village': 'k',
        'engineer monkey': 'l', 'sniper monkey': 'z',
        'monkey sub': 'x', 'monkey buccaneer': 'c',
        'monkey ace': 'v', 'heli pilot': 'b',
        'mortar monkey': 'n', 'dartling gunner': 'm',
        'beast handler': 'i'
    }

    if len(hotKey) == 1:
        hotKey = monkeyLibrary[hotKey]
    return hotKey

#Returns the mouse position as a tuple
def getMouseTuple():
    #Turns the mouse coordinates to a tuple
    mousePosTuple = tuple(auto.position())
    return mousePosTuple

def restartMap():
    time.sleep(0.2)
    keyboard.send('esc')
    time.sleep(0.2)
    auto.click((1266, 1083))
    time.sleep(0.2)
    auto.click((1312, 959))
    pass


def printNewStageInPosDict(StageName):
    posDict = {
        'deflationcash': [],
        'ninjaadora': [],
        'jungledruid': [],
        'primaryonly': [],
        'militaryonly': []
    }

    strategy_max_len = [6, 5, 9, 4, 4]

    # Get coord for every key
    for i, key in enumerate(posDict):

        posDict[key] = getPosList(key, strategy_max_len[i])

    #Print in format
    print(f'\'{StageName}\'' + ': {')
    for key, value in posDict.items():
        print(f'      \'{key}\': {value},')
    print('},')


def getPosList(strategyname, max_len):
    cordList = []

    if strategyname == 'deflationcash':
        print('Deflation: Dart, Sauda, ace, alchemist, ace, village')
    if strategyname == 'ninjaadora':
        print('Ninjaadora: Ninja, Adora, alchemist, wizardx2')
    if strategyname == 'jungledruid':
        print('JungleDruid: ruid, Obyn, druid, village, druidx5')
    if strategyname == 'primaryonly':
        print('Primary: Obyn, dart, boomer, bomb')
    if strategyname == 'militaryonly':
        print('Military: Sauda, ace, sniper, ace')
    # Wait to get ready (for jungledruid)
    print('Press 0 for mouse, 9 for 9-key')
    mouseBool = False
    while True:
        if keyboard.is_pressed('0'):
            mouseBool = True
            print('MouseClick selection!')
            break
        if keyboard.is_pressed('9'):
            print('9 key selection!')
            break

    if mouseBool:
        try:
            with Listener(on_click=
                          lambda x, y, button, pressed:
                          add_coord(x, y, button, pressed, cordList, max_len)) as listener:
                listener.join()
        except ExitListenerSession:
            print('exited Listener!')
            time.sleep(0.3)
            restartMap()
            return cordList
    else:
        time.sleep(1)
        while len(cordList) < max_len:
            if keyboard.is_pressed('9'):
                cordList.append(getMouseTuple())
                print(cordList)
                time.sleep(0.5)
        restartMap()
        return cordList


def add_coord(x, y, button, pressed, coordlist, max_len):
    if button == button.left and not pressed:
        coordlist.append((x, y))
        print(coordlist)
    if len(coordlist) >= max_len:
        raise ExitListenerSession


class ExitListenerSession(Exception):
    pass


#=====================  PositionDict for all maps and strategies ===============================

#TODO: Oppdater denne, slik at den funkar på alle baner. Ein del har ikkje fulle pos-lister for alle

#TODO: Byt magicbenjamin mot ninjaadora. Det er berre pos 2 som er endra, altså ben til adora. Lett fiks



PositionDictForAllStagesAndStrategies = {
    'stagename': {
        'deflationcash':[],
        'ninjaadora':[],
        'jungledruid':[],
        'primaryonly':[],
        'militaryonly':[]
    },

    'monkey meadow': {
       'deflationcash': [(536, 691), (737, 711), (474, 500), (321, 504), (469, 386), (304, 385)],
       'ninjaadora': [(725, 523), (740, 690), (789, 456), (846, 524), (545, 684)],
       'jungledruid': [(711, 652), (856, 529), (809, 650), (732, 516), (910, 650), (715, 734), (823, 733), (922, 728), (791, 425)],
       'primaryonly': [(724, 690), (550, 673), (716, 526), (536, 517)],
       'militaryonly': [(733, 707), (485, 502), (724, 531), (478, 672)],
    },

    'tree stump': {
      'deflationcash': [(566, 385), (590, 495), (1077, 992), (922, 989), (1072, 886), (1245, 871)],
      'ninjaadora': [(598, 501), (636, 698), (521, 543), (584, 426), (837, 547)],
      'jungledruid': [(949, 935), (972, 1011), (1042, 921), (855, 996), (1065, 1004), (1154, 979), (1127, 891), (880, 870), (1019, 842)],
      'primaryonly': [(633, 710), (569, 377), (598, 497), (507, 538)],
      'militaryonly': [(574, 501), (1008, 898), (891, 512), (1209, 864)],
    },

    'town center': {
      'deflationcash': [(442, 650), (615, 653), (670, 1235), (496, 1234), (666, 1124), (503, 1106)],
      'ninjaadora': [(805, 677), (656, 621), (796, 778), (951, 744), (570, 663)],
      'jungledruid': [(948, 670), (659, 657), (799, 657), (782, 470), (799, 570), (799, 738), (948, 590), (952, 750), (951, 829)],
      'primaryonly': [(630, 660), (394, 674), (507, 655), (313, 718)],
      'militaryonly': [(637, 646), (666, 1117), (234, 472), (229, 635)],
    },

    'middle of the road': {
      'deflationcash': [(533, 691), (712, 704), (1716, 280), (1544, 291), (1710, 178), (1539, 173)],
      'ninjaadora': [(532, 679), (719, 704), (525, 609), (589, 521), (539, 760)],
      'jungledruid': [(524, 679), (532, 597), (522, 764), (664, 586), (615, 682), (707, 680), (613, 761), (709, 761), (612, 840)],
      'primaryonly': [(536, 680), (526, 762), (540, 581), (150, 585)],
      'militaryonly': [(534, 702), (1264, 810), (694, 705), (1258, 659)],
    },

    'one two tree': { #TODO
        'deflationcash': [],
        'ninjaadora': [],
        'jungledruid': [],
        'primaryonly': [],
        'militaryonly': []
    },

    'scrapyard': {
      'deflationcash': [(310, 389), (770, 590), (1250, 316), (1456, 341), (1242, 211), (1486, 242)],
      'ninjaadora': [(771, 590), (768, 841), (747, 350), (627, 471), (732, 1084)],
      'jungledruid': [(438, 252), (301, 221), (448, 330), (320, 413), (302, 313), (544, 347), (532, 268), (494, 187), (309, 140)],
      'primaryonly': [(725, 1084), (766, 847), (774, 742), (458, 1095)],
      'militaryonly': [(773, 837), (368, 1112), (587, 636), (622, 1100)],
    },

    'the cabin': {
      'deflationcash': [(1060, 216), (747, 243), (669, 337), (547, 547), (645, 460), (501, 359)],
      'ninjaadora': [(636, 946), (621, 736), (725, 968), (840, 984), (664, 452)],
      'jungledruid': [(604, 968), (514, 936), (694, 956), (677, 1057), (560, 1044), (462, 1039), (786, 979), (797, 1062), (413, 971)],
      'primaryonly': [(752, 296), (1052, 237), (894, 169), (499, 226)],
      'militaryonly': [(743, 274), (642, 380), (1371, 470), (703, 1020)],
    },

    'resort': {
      'deflationcash': [(983, 315), (1533, 327), (1378, 924), (1228, 930), (1377, 819), (1211, 820)],
      'ninjaadora': [(1533, 774), (1538, 326), (1432, 767), (1534, 851), (1244, 766)],
      'jungledruid': [(1523, 777), (1516, 946), (1431, 747), (1384, 939), (1530, 858), (1437, 838), (1342, 839), (1334, 748), (1251, 824)],
      'primaryonly': [(1532, 330), (1523, 776), (1426, 780), (955, 346)],
      'militaryonly': [(1532, 340), (1443, 929), (1258, 930), (1067, 922)],
    },

    'skates': {
      'deflationcash': [(287, 599), (315, 429), (493, 723), (359, 739), (490, 619), (465, 840)],
      'ninjaadora': [(293, 613), (395, 702), (138, 628), (132, 519), (400, 789)],
      'jungledruid': [(570, 943), (403, 876), (481, 920), (490, 707), (659, 958), (589, 861), (502, 831), (417, 791), (573, 782)],
      'primaryonly': [(593, 956), (284, 599), (318, 437), (124, 508)],
      'militaryonly': [(322, 425), (537, 904), (328, 758), (483, 765)],
    },

    'lotus island': {
        'deflationcash': [(1198, 1061), (1553, 1116), (457, 822), (590, 776), (390, 718), (563, 635)],
        'ninjaadora': [(1526, 1092), (1522, 941), (1588, 1024), (1379, 914), (1295, 979)],
        'jungledruid': [(1241, 977), (1131, 990), (1170, 1115), (1254, 874), (973, 1172), (1067, 1172), (1065, 1090), (1234, 1058), (1329, 957)],
        'primaryonly': [(1228, 1017), (1067, 1144), (1133, 1058), (1542, 1078)],
        'militaryonly': [(1553, 1098), (1154, 712), (960, 490), (1371, 699)]
    },

    'candy falls': {
        'deflationcash': [(386, 978), (273, 1124), (655, 185), (509, 199), (658, 294), (480, 304)],
        'ninjaadora': [(506, 1022), (283, 1116), (418, 987), (333, 942), (627, 996)],
        'jungledruid': [(596, 1014), (411, 974), (509, 961), (611, 863), (488, 879), (498, 1043), (689, 985), (729, 911), (719, 824)],
        'primaryonly': [(494, 1023), (389, 978), (271, 949), (286, 1113)],
        'militaryonly': [(264, 1126), (642, 858), (335, 767), (488, 968)]
    },

    'winter park': {
        'deflationcash': [(825, 395), (466, 383), (817, 1192), (948, 1078), (1007, 1189), (828, 1078)],
        'ninjaadora': [(609, 515), (954, 497), (632, 372), (716, 517), (613, 633)],
        'jungledruid': [(606, 522), (472, 635), (611, 601), (698, 515), (453, 528), (702, 594), (610, 681), (705, 673), (470, 389)],
        'primaryonly': [(622, 549), (827, 397), (717, 519), (666, 383)],
        'militaryonly': [(471, 379), (663, 1030), (758, 1183), (885, 1027)]
    },

    'carved': {
      'deflationcash': [(857, 1087), (1525, 796), (1706, 1267), (1541, 1253), (1702, 1160), (1697, 1043)],
      'ninjaadora': [(1492, 878), (1523, 787), (1454, 959), (1402, 1029), (1081, 1085)],
      'jungledruid': [(754, 1135), (728, 975), (666, 1099), (865, 1076), (655, 913), (586, 1051), (854, 1177), (699, 1290), (836, 877)],
      'primaryonly': [(867, 1065), (655, 1095), (1085, 1095), (505, 962)],
      'militaryonly': [(1526, 775), (960, 664), (728, 681), (108, 637)],
    },

    'park path': { #TODO
        'deflationcash': [],
        # 'ninjaadora':[(1190, 371), (380, 360), (1337, 450), (1171, 474), (983, 461)],
        'jungledruid': [(1146, 412), (993, 463), (1239, 365), (1312, 499), (1151, 514), (1239, 447), (1152, 328), (1059, 333), (967, 311)],
        'primaryonly': [],
        'militaryonly': []
    },

    'alpine run': { #TODO
        'deflationcash':[],
        'ninjaadora':[],
        'jungledruid':[],
        'primaryonly':[],
        'militaryonly':[]
    },

    'frozen over': { #TODO
        'deflationcash': [],
        'ninjaadora': [],
        'jungledruid': [],
        'primaryonly': [],
        'militaryonly': []
    },

    'in the loop': {
        'deflationcash': [(1419, 784), (1321, 944), (620, 708), (769, 695), (625, 820), (800, 793)],
        'ninjaadora': [(1153, 1068), (1312, 946), (1245, 1076), (1209, 954), (1190, 815)],
        'jungledruid': [(1339, 865), (1441, 807), (1261, 811), (1168, 873), (1243, 960), (1332, 944), (1376, 727), (1285, 674), (1178, 682)],
        'primaryonly': [(1249, 960), (1340, 883), (1138, 1068), (1032, 1048)],
        'militaryonly': [(1319, 940), (631, 681), (980, 523), (628, 812)]
    },

    'cubism': {
        'deflationcash': [(531, 679), (720, 786), (1256, 821), (1382, 708), (1442, 810), (1258, 698)],
        'ninjaadora':[(778, 681), (557, 732), (709, 532), (875, 622), (707, 792)],
        'jungledruid': [(769, 687), (845, 730), (812, 617), (889, 660), (1013, 583), (948, 724), (1030, 689), (974, 815), (722, 519)],
        'primaryonly': [(795, 694), (525, 660), (613, 721), (706, 765)],
        'militaryonly': [(708, 791), (1287, 641), (1011, 674), (1292, 754)],
        'testing': [(1570, 245), (1713, 677), (1245, 600), (637, 1039), (631, 359)]
    },

    'four circles': {
        'deflationcash': [(826, 565), (935, 661), (120, 677), (279, 572), (318, 674), (157, 564)],
        'ninjaadora': [(932, 628), (764, 596), (1095, 517), (992, 685), (931, 776)],
        'jungledruid': [(842, 551), (1033, 564), (929, 625), (876, 689), (743, 606), (968, 697), (994, 493), (859, 473), (768, 505)],
        'primaryonly': [(932, 646), (990, 718), (833, 539), (1016, 496)],
        'militaryonly': [(968, 670), (675, 601), (702, 853), (669, 971)],
    },

    'hedge': {
        'deflationcash': [(497, 875), (333, 786), (173, 570), (315, 570), (173, 460), (337, 407)],
        'ninjaadora': [(337, 824), (346, 718), (339, 937), (430, 943), (496, 792)],
        'jungledruid': [(490, 976), (331, 818), (496, 892), (375, 957), (260, 936), (238, 1014), (288, 1086), (390, 1074), (480, 1056)],
        'primaryonly': [(333, 804), (337, 694), (333, 595), (167, 765)],
        'militaryonly': [(336, 777), (218, 480), (686, 1241), (216, 355)]
    },

    'end of the road':{
        'deflationcash':[(851, 617), (209, 601), (591, 615), (454, 616), (592, 719), (428, 757)],
        'ninjaadora':[(860, 609), (617, 646), (837, 529), (947, 601), (587, 514)],
        'jungledruid':[(443, 549), (393, 704), (438, 631), (512, 722), (532, 622), (531, 530), (621, 541), (626, 624), (634, 704)],
        'primaryonly':[(440, 632), (514, 512), (600, 546), (205, 587)],
        'militaryonly':[(207, 600), (530, 655), (739, 805), (535, 778)]
    },

    'logs': { #TODO
        'deflationcash': [],
        'ninjaadora': [],
        'jungledruid': [],
        'primaryonly': [],
        'militaryonly': []
    },

    'steambed':{
        'deflationcash':[],
        #'ninjaadora':[(601, 564), (1325, 242), (502, 395), (723, 523), (804, 572)],
        'jungledruid':[(624, 566), (777, 640), (704, 526), (760, 463), (878, 586), (677, 640), (817, 401), (849, 482), (586, 644)],
        'primaryonly':[],
        'militaryonly':[]
    },

    'cracked': {
        'deflationcash':[],
        #'ninjaadora': [(653, 470), (1260, 312), (624, 326), (629, 561), (745, 594)],
        'jungledruid': [(566, 526), (474, 505), (638, 475), (554, 420), (468, 609), (593, 604), (663, 552), (735, 489), (765, 565)],
        'primaryonly':[],
        'militaryonly':[]
    },

    'balance':{
        'deflationcash':[(1115, 697), (960, 724), (127, 861), (190, 968), (144, 1125), (70, 991)],
        'ninjaadora':[(958, 722), (785, 524), (805, 706), (1119, 697), (969, 502)],
        'jungledruid':[(957, 729), (1121, 696), (969, 495),   (789, 521), (781, 709),  (962, 328), (1136, 520), (708, 902), (1181, 903)],
        'primaryonly':[(1119, 701), (969, 508), (962, 730), (791, 711)],
        'militaryonly':[(962, 727), (191, 264), (956, 114), (140, 421)]
    },

}
