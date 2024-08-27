import datetime

import pyautogui as auto
import time
import keyboard
import os
import MonkeyFiles as function
from CurrentGame import CurrentGame, RetryStageException
from PIL import Image
cwd = os.getcwd()
auto.FAILSAFE = False

#============================= Shortcuts/hotkeys ======================================


#============================= Active Code ====================================
print('Running!')



def waitForLoadingScreen():
    #350, 100 er på peng. Godt utganspunkt
    time_break = 0
    while auto.pixel(350, 100) == (0, 0, 0):
        time.sleep(0.3)
        time_break += 0.3
        print('Waiting, seeing black')
        if time_break > 20:
            print('too long')
            break
    print('Saw something else!')
    time.sleep(1)
    return


while not keyboard.is_pressed('+'):


    if keyboard.is_pressed('5'):
        print('5 is pressed')
        for x, y in [(795, 370), (1345, 370), (1894, 370), (795, 780), (1345, 780), (1894, 780)]:
            print(auto.pixel(x, y))
        time.sleep(1)


    if keyboard.is_pressed('6'):
        print('6 is pressed')
        runModeList = [
            'easy',
            'medium'
        ]
        stageList = ['carved', 'skates']
        for stage in stageList:
            for mode in runModeList:
                retry_flag = True
                while retry_flag:
                    try:
                        currentRun = CurrentGame(stage, mode)
                        currentRun.runCurrentGame()
                        #currentRun.startGame()
                        retry_flag = False
                    except RetryStageException:
                        continue

        print('The 6 pressed is done B)')


    if keyboard.is_pressed('7'):
        runModeList = [
                        'easy',
                        'primary only',
                        'deflation',
                        'medium',
                        'military only',
                        'reverse',
                        'apopalypse',
                        'hard',
                        'magic monkeys only',
                        'double hp moab',
                        'half cash',
                        'alternate bloons rounds',
                        'impoppable',
                        'chimps',
                       ]
        stageList = ['carved']

        for stage in stageList:
            for mode in runModeList:
                flag = True
                while flag:
                    try:
                        currentRun = CurrentGame(stage, mode)
                        currentRun.runCurrentGame()
                        flag = False
                    except RetryStageException:
                        continue

        print('The 7 pressed is done B)')

    if keyboard.is_pressed('8'):
        print('8 is pressed')
        myList = []
        while not keyboard.is_pressed('0'):
            if keyboard.is_pressed('9'):
                myList.append(function.getMouseTuple())
                print(myList)
                time.sleep(0.5)
        print(myList)
        time.sleep(1)

    if keyboard.is_pressed('9'):
        print('9 is pressed! Time to add new stages!')
        time.sleep(0.5)
        stageNameList = ['carved']
        for name in stageNameList:
            function.printNewStageInPosDict(name)

    if keyboard.is_pressed('0'):
        print('0 is pressed!')
        waitForLoadingScreen()
