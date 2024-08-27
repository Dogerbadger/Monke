# This is functions for the BTD6 automatic script. Look at main to see the usage
# These are meant to be simple functions, and the logic will mostly be present in main.py,
# when using the functions
# Written 27/12 2022, Kristian

from MonkeyFiles import Tower, PositionDictForAllStagesAndStrategies, DebugException, StageCompleteException, DefeatException
import pyautogui as auto
import time
import keyboard
import os
from PIL import Image
import pytesseract

auto.FAILSAFE = False
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

cwd = os.getcwd()


#TODO: Gjer slk at loading screen er så lenge skjerm er svart, eller 10 sek, eller noko. Funkar dårleg slik den er no



# position dict under the class
class CurrentGame:

    def __init__(self, stage, mode):
        self.stage = stage
        self.mode = mode
        self.difficulty = CurrentGame.getDifficulty(self)
        self.strategy = CurrentGame.getStrategy(self)
        self.hero = CurrentGame.getHero(self)
        self.positions = PositionDictForAllStagesAndStrategies[self.stage][self.strategy]
        self.reties = 0

    def __str__(self):
        return f'Current game is using: {self.strategy} on {self.mode} for {self.stage}'

    def runCurrentGame(self):
        self.enterStage()
        self.startGame()

    #getters
    def getDifficulty(self):
        modeDifficultyDict = {
            'easy': 'easy',
            'medium': 'medium',
            'hard': 'hard',
            'primary only': 'easy',
            'deflation': 'easy',
            'military only': 'medium',
            'reverse': 'medium',
            'apopalypse': 'medium',
            'magic monkeys only': 'hard',
            'double hp moab': 'hard',
            'half cash': 'hard',
            'alternate bloons rounds': 'hard',
            'impoppable': 'hard',
            'chimps': 'hard',
        }
        newMode = modeDifficultyDict[self.mode]
        return newMode

    def getStrategy(self):
        modeStrategyDict = {
            'easy':'jungledruid',
            'medium': 'jungledruid',
            'hard': 'jungledruid',
            'primary only': 'primaryonly',
            'deflation': 'deflationcash',
            'military only': 'militaryonly',
            'reverse': 'jungledruid',
            'apopalypse': 'ninjaadora',
            'magic monkeys only': 'ninjaadora',
            'double hp moab': 'jungledruid',
            'half cash': 'deflationcash',
            'alternate bloons rounds': 'ninjaadora',
            'impoppable': 'jungledruid',
            'chimps': 'jungledruid',
        }
        return modeStrategyDict[self.mode]

    def getHero(self):
        strategyHeroDict ={
            'testing':'psi',
            'jungledruid':'obyn',
            'primaryonly':'obyn',
            'deflationcash':'sauda',
            'militaryonly':'sauda',
            'ninjaadora':'adora',
        }
        return strategyHeroDict[self.strategy]

    def enterStage(self):
        time.sleep(1)
        clickMapSelection()
        time.sleep(0.2)
        self.clickOnStage()
        time.sleep(0.2)
        self.changeHero()
        self.clickOnGameMode()
        time.sleep(1)
        return

    def clickOnStage(self):
        stageName = self.stage
        difficulty = ''

        stageNameDict = {
            # Easy
            'monkey meadow': (1, 1), 'tree stump': (1, 2), 'town center': (1, 3),
            'middle of the road': (1, 4), 'one two tree': (1, 5), 'scrapyard': (1, 6),
            'the cabin': (2, 1), 'resort': (2, 2), 'skates': (2, 3),
            'lotus island': (2, 4), 'candy falls': (2, 5), 'winter park': (2, 6),
            'carved': (3, 1), 'park path': (3, 2), 'alpine run': (3, 3),
            'frozen over': (3, 4), 'in the loop': (3, 5), 'cubism': (3, 6),
            'four circles': (4, 1), 'hedge': (4, 2), 'end of the road': (4, 3),
            'logs': (4, 4), 'begEmpty5': (4, 5), 'begEmpty6': (4, 6),
            # Medium
            'polyphemus': (5, 1), 'covered garden': (5, 2), 'quarry': (5, 3),
            'quiet street': (5, 4), 'bloonarius prime': (5, 5), 'balance': (5, 6),
            'encrypted': (6, 1), 'bazaar': (6, 2), 'adoras temple': (6, 3),
            'spring spring': (6, 4), 'kartsndarts': (6, 5), 'moon landing': (6, 6),
            'haunted': (7, 1), 'downstream': (7, 2), 'firing range': (7, 3),
            'cracked': (7, 4), 'steambed': (7, 5), 'chutes': (7, 6),
            'rake': (8, 1), 'spice islands': (8, 2), 'medEmpty3': (8, 3),
            'medEmpty4': (8, 4), 'medEmpty5': (8, 5), 'medEmpty6': (8, 6),
            # Advanced
            'erosion': (9, 1), 'midnight mansion': (9, 2), 'sunken colums': (9, 3),
            'x factor': (9, 4), 'mesa': (9, 5), 'geared': (9, 6),
            'spillway': (10, 1), 'cargo': (10, 2), 'pat\'s pond': (10, 3),
            'peninsula': (10, 4), 'high finance': (10, 5), 'another brick': (10, 6),
            'off the coast': (11, 1), 'cornfield': (11, 2), 'underground': (11, 3),
            'advEmpty4': (11, 4), 'advEmpty5': (11, 5), 'advEmpty6': (11, 6),
            # Expert
            'dark dungeons': (12, 1), 'sanctuary': (12, 2), 'ravine': (12, 3),
            'flooded valley': (12, 4), 'infernal': (12, 5), 'bloody puddles': (12, 6),
            'workshop': (13, 1), 'quad': (13, 2), 'dark castle': (13, 3),
            'muddy puddles': (13, 4), '#ouch': (13, 5), 'expEmpty6': (13, 6),
        }

        targetDict = {
            '1': (550, 309),
            '2': (1111, 327),
            '3': (1670, 320),
            '4': (550, 730),
            '5': (1111, 730),
            '6': (1670, 730)
        }

        target = stageNameDict[stageName]
        #target = self.convertFromStageNameToIndex()
        if target[0] == 12 or target[0] == 13:
            clickEasyMap()
        else:
            clickExpertMap()

        page = target[0]
        index = str(target[1])
        if page in range(1, 5):
            for i in range(page):
                clickEasyMap()
            auto.moveTo(targetDict.get(index))
            time.sleep(0.5)
            auto.click()
            difficulty = 'easy'

        elif page in range(5, 9):
            for i in range(page - 5 + 1):
                clickMediumMap()
            auto.moveTo(targetDict.get(index))
            time.sleep(0.2)
            auto.click()
            difficulty = 'medium'

        elif page in range(9, 12):
            for i in range(page - 9 + 1):
                clickAdvancedMap()
            auto.moveTo(targetDict.get(index))
            time.sleep(0.2)
            auto.click()
            difficulty = 'advanced'

        elif page in range(12, 14):
            for i in range(page - 12 + 1):
                clickExpertMap()
            auto.moveTo(targetDict.get(index))
            time.sleep(0.2)
            auto.click()
            difficulty = 'expert'
        #print(f'Clicked on {stageName}, which is a(n) {difficulty} map.')

    #def convertFromStageNameToIndex(self):

    def clickOnGameMode(self):
        difficulty = self.difficulty
        mode = self.mode
        easyDict = {
            'enter': (687, 515),
            'easy': (691, 746),
            'primary only': (1113, 571),
            'deflation': (1537, 574)
        }
        mediumDict = {
            'enter': (1115, 520),
            'medium': (693, 749),
            'military only': (1110, 573),
            'reverse': (1113, 940),
            'apopalypse': (1532, 572),
        }
        hardDict = {
            'enter': (1549, 528),
            'hard': (691, 751),
            'magic monkeys only': (1114, 567),
            'double hp moab': (1533, 559),
            'half cash': (1959, 565),
            'alternate bloons rounds': (1112, 955),
            'impoppable': (1539, 948),
            'chimps': (1960, 943),
        }

        time.sleep(0.2)
        if difficulty == 'easy':
            auto.click(easyDict.get('enter'))
            time.sleep(0.2)
            auto.click(easyDict.get(mode))
            time.sleep(0.2)
            if mode == 'deflation':
                waitForLoadingScreen()
                keyboard.send('esc')

        elif difficulty == 'medium':
            auto.click(mediumDict.get('enter'))
            time.sleep(0.2)
            auto.click(mediumDict.get(mode))
            time.sleep(0.2)
            if mode == 'apopalypse':
                waitForLoadingScreen()
                keyboard.send('esc')
                time.sleep(1)
                keyboard.send('space')

        elif difficulty == 'hard':
            auto.click(hardDict.get('enter'))
            time.sleep(0.2)
            auto.click(hardDict.get(mode))
            time.sleep(0.2)
            if mode == 'impoppable':
                self.difficulty = 'impoppable'
                waitForLoadingScreen()
                keyboard.send('esc')
            if mode == 'chimps' or mode == 'half cash':
                waitForLoadingScreen()
                keyboard.send('esc')
        print(f'Clicked on gamemode {self.difficulty}, {mode}!')

    def changeHero(self):
        heroPositionDict = {
            'quincy': (121, 269), 'qwendolin': (326, 274),
            'striker jones': (519, 271), 'obyn': (128, 527),
            'geraldo': (327, 534), 'captin churchill': (519, 524),
            'benjamin': (125, 780), 'ezili': (333, 783),
            'pat fusty': (520, 775), 'adora': (125, 1026),
            'admiral brickell': (330, 1022), 'etienne': (531, 1034),
            'sauda': (127, 1279), 'psi': (328, 1277)
        }

        pressHeroButton()
        time.sleep(0.3)
        auto.click(heroPositionDict[self.hero])
        time.sleep(0.2)
        auto.click((1316, 782))
        time.sleep(0.1)
        keyboard.send('esc')

    def waitForWinScreen(self):
        print('Waiting for win screen!')
        winImage = Image.open(os.path.join(cwd, 'Pictures', 'Search images', 'victoryShot.png'))
        auto.moveTo((10, 100))

        while True:
            auto.click()
            self.useAbilities()
            if auto.locateOnScreen(winImage, confidence=0.7, region=(660, 80, 1000, 370), grayscale=True):
                print('Found the victory image!')
                break
        self.winReturnHome()

    def winReturnHome(self):
        if self.mode == 'apopalypse':
            # UI home 2button: (958, 1092)
            auto.click((1116, 1168))
            time.sleep(1)
            auto.click((958, 1092))
            waitForLoadingScreen()
        else:
            # UI home 3button: (833, 1046)
            auto.click((1116, 1168))
            time.sleep(1)
            auto.click((833, 1046))
            waitForLoadingScreen()

        if not CurrentGame.isOnMainMenu():
            CurrentGame.clearEventFromMenu()

    def defeatReturnHome(self):
        if self.mode == 'apopalypse' or self.mode == 'chimps':
            # UI home 3button: (833, 1046)
            auto.click((833, 1046))
            waitForLoadingScreen()
        # UI home 4button: (685, 1039)
        auto.click((685, 1039))
        waitForLoadingScreen()

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
        if currentStage not in notAbility1List and currentStage != 9001:
            keyboard.send(ability1)
        time.sleep(0.05)
        if currentStage not in notAbility2List and currentStage != 9001:
            keyboard.send(ability2)
            time.sleep(0.05)
            keyboard.send(ability3)
        time.sleep(0.05)
        return

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

            # Print the result
            # print('Frå text:', text)
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

            # print(level)
            return level
        # return value if reading is wrong
        return 9001

    @staticmethod
    def isOnMainMenu():
        menuImage = Image.open(os.path.join(cwd, 'Pictures', 'Search images', 'mainMenu.png'))
        if auto.locateOnScreen(menuImage, confidence=0.5, region=(1400, 1100, 700, 300), grayscale=True):
            print('On main menu!')
            return True
        print('Not on main menu...')
        return False

    @staticmethod
    def clearEventFromMenu():
        coordList = [(1108, 875), (932, 690), (1113, 875), (1317, 692), (1263, 687), (1111, 1284)]
        eventloop_check = 0
        while not CurrentGame.isOnMainMenu():
            for coord in coordList:
                auto.click(coord)
                time.sleep(0.5)
            keyboard.send('esc')
            eventloop_check += 1
            print(f'Event loop nr. {eventloop_check}')
            time.sleep(1)

    @staticmethod
    def findEasyBonusMap():
        event_pixel_colour_list = [(255, 184, 175)]
        findBonusCount = 0
        while True and findBonusCount < 8:
            findBonusCount += 1
            clickEasyMap()
            for x, y in [(795, 370), (1345, 370), (1894, 370), (795, 780), (1345, 780), (1894, 780)]:
                rgb = auto.pixel(x, y)
                #TODO: Gjer slik at dette funkar igjen. abs funkar ikkje. auto.pixelMatching(x,y,(tup)) funka
                if (205, 170, 120) == 0:
                    print('Brown border')
                    continue
                elif abs(rgb-(30, 40, 50)) < 10:
                    #print('Black border')
                    continue
                elif abs(rgb-(255, 200, 0)) < 10:
                    #print('Gold border')
                    continue
                else:
                    #print('Bonus event or unknown block')
                    if rgb[0] != 255:
                        continue
                    pos_tuple = (x, y)
                    return getBonusStageName(pos_tuple).strip()
            time.sleep(0.1)
        return None

    # Strategy methods
    def startGame(self):
        functions_map = {
            'jungledruid': self.druidJungleWrath,
            'primaryonly': self.primaryOnlyandObyn,
            'deflationcash': self.deflationandCash,
            'militaryonly': self.militaryOnlyandSauda,
            'ninjaadora': self.ninjaAdora
        }

        Tower.difficulty = self.difficulty
        Tower.hero = self.hero
        Tower.mode = self.mode
        # Run the mapped function with no input
        functions_map[self.strategy]()

    # Dart, Sauda, ace, alchemist, ace, village
    def deflationandCash(self):
        print('deflationCash is started')

        stageCoords = self.positions
        d = convertMonkeyToHotkey('dart monkey')
        al = convertMonkeyToHotkey('alchemist')
        a = convertMonkeyToHotkey('monkey ace')
        v = convertMonkeyToHotkey('monkey village')

        dart = Tower(stageCoords[0], d)
        hero = Tower(stageCoords[1], 'u')
        ace1 = Tower(stageCoords[2], a)
        alchemist = Tower(stageCoords[3], al)
        ace2 = Tower(stageCoords[4], a)
        village = Tower(stageCoords[5], v)

        try:
            dart.placeTower()
            if self.mode != 'deflation':
                keyboard.send('space')
                time.sleep(0.2)
                keyboard.send('space')
            hero.placeTower()
            ace1.placeTower()
            ace1.upgradeTower('003')
            alchemist.placeTower()
            alchemist.upgradeTower('300')
            if self.mode == 'deflation':
                keyboard.send('space')
                time.sleep(0.2)
                keyboard.send('space')
            ace2.placeTower()
            ace2.upgradeTower('003')
            village.placeTower()
            village.upgradeTower('020')
            ace1.upgradeTower('203')
            ace2.upgradeTower('203')
            alchemist.upgradeTower('401')
            village.upgradeTower('220')
            if self.mode == 'deflation':
                raise StageCompleteException
            dart.upgradeTower('402')
            dart.upgradeTower('502')
            raise StageCompleteException
        except StageCompleteException:
            self.waitForWinScreen()
            print('Done!\n')
        except DebugException:
            print('error in deflationchash')
            self.startGame()
        except DefeatException:
            self.defeatReturnHome()
            raise RetryStageException
        finally:
            print(str(self))
        return

    # Ninja, Adora, alchemist, wizardx2
    def ninjaAdora(self):
        print('ninjaAdora is started!')

        stageCoords = self.positions
        n = convertMonkeyToHotkey('ninja monkey')
        al = convertMonkeyToHotkey('alchemist')
        w = convertMonkeyToHotkey('wizard monkey')

        ninja = Tower(stageCoords[0], n)
        hero = Tower(stageCoords[1], 'u')
        alchemist = Tower(stageCoords[2], al)
        wizard1 = Tower(stageCoords[3], w)
        wizard2 = Tower(stageCoords[4], w)

        try:
            ninja.placeTower()
            keyboard.send('space')
            time.sleep(0.2)
            keyboard.send('space')
            ninja.upgradeTower('101')
            ninja.upgradeTower('201')
            hero.placeTower()
            alchemist.placeTower()
            alchemist.upgradeTower('200')
            ninja.upgradeTower('401')
            alchemist.upgradeTower('420')
            ninja.upgradeTower('402')
            wizard1.placeTower()
            wizard1.upgradeTower('202')
            wizard2.placeTower()
            wizard1.upgradeTower('402')
            wizard2.upgradeTower('202')
            wizard2.upgradeTower('402')
            if self.difficulty == 'medium':
                raise StageCompleteException
            wizard1.upgradeTower('502')
            raise StageCompleteException
        except DebugException:
            print('error in ninjaAdora')
            self.startGame()
        except StageCompleteException:
            self.waitForWinScreen()
            print('Done!\n')
        except DefeatException:
            self.defeatReturnHome()
            raise RetryStageException
        finally:
            print(str(self))
        return

    # Druid, Obyn, druid, village, druidx5
    def druidJungleWrath(self):
        print('druidJungleWrath is started')

        stageCoords = self.positions
        d = convertMonkeyToHotkey('druid')
        v = convertMonkeyToHotkey('monkey village')

        druid1 = Tower(stageCoords[0], d)
        hero = Tower(stageCoords[1], 'u')
        druid2 = Tower(stageCoords[2], d)
        village = Tower(stageCoords[3], v)
        druid3 = Tower(stageCoords[4], d)
        druid4 = Tower(stageCoords[5], d)
        druid5 = Tower(stageCoords[6], d)
        druid6 = Tower(stageCoords[7], d)
        druid7 = Tower(stageCoords[8], d)

        try:
            druid1.placeTower()
            keyboard.send('space')
            time.sleep(0.2)
            keyboard.send('space')
            druid1.upgradeTower('010')
            hero.placeTower()
            druid1.upgradeTower('030')
            druid1.upgradeTower('130')
            druid2.placeTower()
            druid2.upgradeTower('013')
            village.placeTower()
            village.upgradeTower('020')
            druid3.placeTower()
            druid3.upgradeTower('013')
            druid4.placeTower()
            druid5.placeTower()
            druid6.placeTower()
            druid7.placeTower()
            village.upgradeTower('220')
            druid1.upgradeTower('230')
            if self.difficulty == 'easy':
                raise StageCompleteException
            druid2.upgradeTower('014')
            druid3.upgradeTower('014')
            druid4.upgradeTower('014')
            druid5.upgradeTower('014')
            druid6.upgradeTower('014')
            druid7.upgradeTower('014')
            druid1.upgradeTower('240')
            if self.difficulty =='medium':
                raise StageCompleteException
            druid1.upgradeTower('250')
            village.upgradeTower('230')
            if self.mode == 'chimps' or self.mode == 'impoppable':
                druid2.upgradeTower('015')
            raise StageCompleteException

        except DebugException:
            print('An error occured from jungledruid')
            self.startGame()
        except StageCompleteException:
            self.waitForWinScreen()
            print('Done!\n')
        except DefeatException:
            self.defeatReturnHome()
            raise RetryStageException
        finally:
            print(str(self))
        return

    # Obyn, dart, boomer, bomb
    def primaryOnlyandObyn(self):
        print('primaryOnlyandSauda is started')

        stageCoords = self.positions
        d = convertMonkeyToHotkey('dart monkey')
        b = convertMonkeyToHotkey('bomb shooter')
        bb = convertMonkeyToHotkey('boomerang monkey')

        hero = Tower(stageCoords[0], 'u')
        dart = Tower(stageCoords[1], d)
        boomer = Tower(stageCoords[2], bb)
        bomb = Tower(stageCoords[3], b)

        try:
            hero.placeTower()
            keyboard.send('space')
            time.sleep(0.2)
            keyboard.send('space')
            dart.placeTower()
            dart.upgradeTower('003')
            dart.upgradeTower('024')
            boomer.placeTower()
            boomer.upgradeTower('230')
            bomb.placeTower()
            bomb.changeTargeting('strong')
            bomb.upgradeTower('230')
            raise StageCompleteException
        except DebugException:
            print('error in primaryObyn')
            self.startGame()
        except DefeatException:
            self.defeatReturnHome()
            raise RetryStageException
        except StageCompleteException:
            self.waitForWinScreen()
            print('Done!\n')
        finally:
            print(str(self))
        return

    # Sauda, ace, sniper, ace
    def militaryOnlyandSauda(self):
        print('militaryOnlyandSauda is started')

        stageCoords = self.positions
        a = convertMonkeyToHotkey('monkey ace')
        s = convertMonkeyToHotkey('sniper monkey')

        hero = Tower(stageCoords[0], 'u')
        ace1 = Tower(stageCoords[1], a)
        sniper = Tower(stageCoords[2], s)
        ace2 = Tower(stageCoords[3], a)

        try:
            hero.placeTower()
            keyboard.send('space')
            time.sleep(0.2)
            keyboard.send('space')
            ace1.placeTower()
            ace1.upgradeTower('003')
            ace1.upgradeTower('023')
            sniper.placeTower()
            sniper.changeTargeting('strong')
            sniper.upgradeTower('130')
            sniper.upgradeTower('230')
            ace2.placeTower()
            ace2.upgradeTower('024')
            sniper.upgradeTower('240')
            raise StageCompleteException

        except DebugException:
            print('error in militarySauda')
            self.startGame()
        except DefeatException:
            self.defeatReturnHome()
            raise RetryStageException
        except StageCompleteException:
            self.waitForWinScreen()
            print('Done!\n')
        finally:
            print(str(self))
        return

    # functions for utility
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
        'm': 'dartling gunner',  'i':'beast handler',
        'dart monkey': 'q',
        'boomerang monkey': 'w', 'bomb shooter': 'e',
        'tack shooter': 'r', 'ice monkey': 't',
        'glue gunner': 'y',
        'wizard monkey': 'a', 'super monkey': 's',
        'ninja monkey': 'd', 'alchemist': 'f',
        'druid': 'g', 'banana farm': 'h',
        'spike factory': 'j', 'monkey village': 'k',
        'engineer monkey': 'l', 'sniper monkey': 'z',
        'monkey sub': 'x', 'monkey buccaneer': 'c',
        'monkey ace': 'v', 'heli pilot': 'b',
        'mortar monkey': 'n', 'dartling gunner': 'm',
        'quincy': 'u', 'qwendolin': 'u',
        'striker jones': 'u', 'obyn': 'u',
        'geraldo': 'u', 'captin churchill': 'u',
        'benjamin': 'u', 'ezili': 'u',
        'pat fusty': 'u', 'adora': 'u',
        'admiral brickell': 'u', 'etienne': 'u',
        'sauda': 'u', 'psi': 'u',  'beast handler':'i',
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
        'm': 'dartling gunner', 'i':'beast handler',
        'dart monkey': 'q',
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
        'beast handler':'i',
    }

    if len(hotKey) == 1:
        hotKey = monkeyLibrary[hotKey]
    return hotKey

def clickEasyMap():
    auto.click((633, 1256))
def clickMediumMap():
    auto.click((954, 1263))
def clickAdvancedMap():
    auto.click((1274, 1263))
def clickExpertMap():
    auto.click((1608, 1260))
def clickMapSelection():
    auto.click((955, 1215))
def pressHeroButton():
    auto.click((128, 1280))

def getBonusIconCoord():
    bonusImage = Image.open(os.path.join(cwd, 'Pictures', 'Search images', 'bonusRewardGray.png'))
    for bonusCoords in [
            auto.locateCenterOnScreen(bonusImage, confidence=0.7, grayscale=True, region=(699, 290, 160, 570)),
            auto.locateCenterOnScreen(bonusImage, confidence=0.7, grayscale=True, region=(1248, 290, 160, 570)),
            auto.locateCenterOnScreen(bonusImage, confidence=0.7, grayscale=True, region=(1798, 290, 160, 570))]:
        if bonusCoords is not None:
            return bonusCoords
    return None

def getBonusStageName(bonusCenter):
    # offset x = 444
    # offset y = 240
    screenregion = (bonusCenter[0] - 444, bonusCenter[1] - 240, 480, 70)
    screenshot_gray = auto.screenshot(region=screenregion).convert('L')
    screenshot_black = screenshot_gray.point(lambda x: 255 if x < 254 else 0)
    screenshot_black.save('stageNameFromBonus.png')
    text = pytesseract.image_to_string(screenshot_black, config='--psm 7')
    return text.lower()

def waitForLoadingScreen():
    #350, 100 er på peng. Godt utganspunkt
    time_break = 0
    while auto.pixel(350, 100) == (0, 0, 0):
        time.sleep(0.3)
        time_break += 0.3
        print('Waiting, seeing black')
        if time_break > 20:
            raise LongLoadingException
    print('Saw something else!')
    time.sleep(1)
    return

class RetryStageException(Exception):
    """Retry the stage, please"""
    pass

class LongLoadingException(Exception):
    """The loading screen over 20 seconds"""
    pass


