# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 07:59:35 2020

@author: janusz
"""


"""
Need bugfix:
    class and origins counters update inside Champion recordtypes.
    add shuffle champions

"""
import itertools
import logging
import os
import time
from operator import itemgetter
from pathlib import Path

import cv2 as cv
import easyocr
import mouseinfo
import numpy as np
import pandas as pd
import pyautogui
from recordtype import recordtype
from win32gui import GetForegroundWindow, GetWindowText

import dss
from windowcapture import WindowCapture

# import pydirectinput
logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)

LOAD_IMAGE = 0
IMAGE_DEBUG_MODE = 1
VARIABLE_PRINT_MODE = 0
IMAGE_DEBUG_MODE = 1
IMAGE_DEBUG_MODE_FULLSCREEN = 1


CROPPING_X_CHAMPIONS = 450
CROPPING_Y_CHAMPIONS = 1000
CROPPING_WIDTH_CHAMPIONS = 1000
CROPPING_HEIGHT_CHAMPIONS = 30

CROPPING_X_ROUND = 760
CROPPING_X_ROUND_FIRST = 820
CROPPING_Y_ROUND = 30
CROPPING_WIDTH_ROUND = 60
CROPPING_HEIGHT_ROUND = 40

CROPPING_X_GOLD = 820
CROPPING_Y_GOLD = 850
CROPPING_WIDTH_GOLD = 100
CROPPING_HEIGHT_GOLD = 40

screenshot = cv.imread("examples/windowed_pyauto_ss.jpg", cv.IMREAD_UNCHANGED)


def start_tft_match(templates_list, delay=3):
    """
    Clicking buttons to start TFT match.

    Parameters
    ----------
    templates_list : TYPE
        DESCRIPTION.
    delay : Delay after click on button. The default is 3.

    Returns
    -------
    None.

    """
    dss.activate_window("client")
    for i, templ in enumerate(templates_list):
        if i < len(templates_list) - 1:
            point = client_match_template(templ)
            if point is not None:
                # to avoid click
                pyautogui.click(point)
                pyautogui.moveTo(900, 400)
                # to avoid mouse on templates position
                time.sleep(delay)
        else:
            while GetWindowText(GetForegroundWindow()) == "League of Legends":
                # if match will be accepted this loop will break
                # bcs active window would change
                # if match will be declined by someone then bot will try to accept again
                point = client_match_template(templ)
                if point is not None:
                    pyautogui.click(point)
                    pyautogui.moveTo(900, 400)
                    # to avoid mouse on templates position
                else:
                    time.sleep(0.3)
                    # little bit pause for pc


def client_match_template(template_img_location, conf=0.8, region_=(0, 0, 1920, 1080)):
    """
    Using pyautogui.locateCenterOnScreen() to check where are buttons to click.

    Parameters
    ----------
    template_img_location : template img path
    conf : confidence The default is 0.8.

    Returns
    -------
    point : XY coords at the center of template found on screen.

    """
    logging.debug(
        "Funtion client_match_template() with %s passed called", template_img_location
    )
    point = pyautogui.locateCenterOnScreen(
        template_img_location, confidence=conf, region=region_
    )
    logging.info("Center of template found on screenshot(return): %s", point)
    logging.debug("Funtion client_match_template() end")
    return point


def click_button_in_game(mode="xp"):
    logging.debug("Function click_button_in_game called with passed: %s", mode)
    if mode == "xp":
        template_button = "examples/bot/game/buy_xp_button.jpg"
        regio = (300, 850, 530, 1080)
    elif mode == "refresh":
        template_button = "examples/bot/game/refresh_button.jpg"
        regio = (300, 850, 530, 1080)
    elif mode == "exit":
        template_button = "examples/bot/game/exit_now_button.jpg"
        regio = (680, 440, 960, 600)

    EXIT_FLAG = False
    dss.activate_window("game")
    point = client_match_template(template_button, conf=0.95, region_=regio)
    logging.info("point is: %s", point)
    if point is not None:
        logging.info("point is not None, clicking: %s", point)
        # to avoid mouse on buttons or cards
        pyautogui.moveTo(300, 300)
        pyautogui.moveTo(point)
        pyautogui.mouseDown()
        # time.sleep(0.1)
        pyautogui.mouseUp()
        # to avoid mouse on buttons
        pyautogui.moveTo(300, 300)
        if point == (838, 543):
            EXIT_FLAG = True
            logging.info("Clicked exit button return: %s", EXIT_FLAG)

    elif point is None:
        logging.info("Button isnt available, couldnt find button or not enough gold.")
    logging.debug("Function click_button_in_game end.")
    return EXIT_FLAG


def unique_file(basename, ext):
    actualname = "%s.%s" % (basename, ext)
    c = itertools.count()
    while os.path.exists(actualname):
        actualname = "%s%d.%s" % (basename, next(c), ext)
    return actualname


def make_cropped_ss(
    LOAD_IMAGE_=LOAD_IMAGE,
    cropping_x=CROPPING_X_CHAMPIONS,
    cropping_y=CROPPING_Y_CHAMPIONS,
    cropping_width=CROPPING_WIDTH_CHAMPIONS,
    cropping_height=CROPPING_HEIGHT_CHAMPIONS,
    IMAGE_DEBUG_MODE_=IMAGE_DEBUG_MODE,
    IMAGE_DEBUG_MODE_FULLSCREEN_=IMAGE_DEBUG_MODE_FULLSCREEN,
):
    """


    Parameters
    ----------
    LOAD_IMAGE_ : If want to open without game then change to 1.
        The default is 0.
    window : Window to be captured, set to None if want to open without game.
        The default is wincap.

        Defaults to cropp screenshot from first to fifth(1-5) champion card name.
    cropping_x :  The default is 450.
    cropping_y :  The default is 1000.
    cropping_width :  The default is 1000.
    cropping_height :  The default is 30.

    Returns
    -------
    crop_img : Cropped screenshot.

    """
    logging.debug("Function make_cropped_ss() called")

    if LOAD_IMAGE_:
        screenshot = cv.imread("examples/windowed_pyauto_ss.jpg", cv.IMREAD_UNCHANGED)
    else:
        dss.activate_window(mode="game", delay=0.2)
        screenshot = pyautogui.screenshot()
        screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)

    crop_img = screenshot[
        cropping_y : cropping_y + cropping_height,
        cropping_x : cropping_x + cropping_width,
    ]

    if IMAGE_DEBUG_MODE_:
        if not IMAGE_DEBUG_MODE_FULLSCREEN_:
            cv.imshow("make_cropped_ss() screenshot", screenshot)
            cv.imshow("make_cropped_ss() crop_img", crop_img)
        else:
            dss.imshow_fullscreen(
                window_name="make_cropped_ss() screenshot", image=screenshot
            )
            cv.imshow("make_cropped_ss() crop_img", crop_img)

    logging.debug("Function make_cropped_ss() end")
    return crop_img, screenshot


def make_ss(
    IMAGE_DEBUG_MODE_=IMAGE_DEBUG_MODE,
    IMAGE_DEBUG_MODE_FULLSCREEN_=IMAGE_DEBUG_MODE_FULLSCREEN,
):
    """


    Parameters
    ----------
    IMAGE_DEBUG_MODE_ : 0 or 1, calls cv.imshow().
        The default is IMAGE_DEBUG_MODE.
    IMAGE_DEBUG_MODE_FULLSCREEN_ : 0 or 1, calls dss.imshow_fullscreen().
        The default is IMAGE_DEBUG_MODE_FULLSCREEN.

    Returns
    -------
    screenshot : screenshot of game.

    """
    logging.debug("Function make_ss() called")
    dss.activate_window(mode="game", delay=0.2)
    screenshot = pyautogui.screenshot()
    screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)
    if IMAGE_DEBUG_MODE_:
        if not IMAGE_DEBUG_MODE_FULLSCREEN_:
            cv.imshow("make_ss() screenshot", screenshot)
        else:
            dss.imshow_fullscreen(window_name="make_ss() screenshot", image=screenshot)
    logging.debug("Function make_ss() end")
    return screenshot


def crop_ss(
    screenshot_=screenshot,
    cropping_x=CROPPING_X_CHAMPIONS,
    cropping_y=CROPPING_Y_CHAMPIONS,
    cropping_width=CROPPING_WIDTH_CHAMPIONS,
    cropping_height=CROPPING_HEIGHT_CHAMPIONS,
    IMAGE_DEBUG_MODE_=IMAGE_DEBUG_MODE,
    IMAGE_DEBUG_MODE_FULLSCREEN_=IMAGE_DEBUG_MODE_FULLSCREEN,
):
    logging.debug("Function crop_ss() called")

    crop_img = screenshot_[
        cropping_y : cropping_y + cropping_height,
        cropping_x : cropping_x + cropping_width,
    ]
    if IMAGE_DEBUG_MODE_:
        if not IMAGE_DEBUG_MODE_FULLSCREEN_:
            cv.imshow("crop_ss() screenshot", screenshot_)
            cv.imshow("crop_ss() crop_img", crop_img)
        else:
            dss.imshow_fullscreen(window_name="crop_ss() screenshot", image=screenshot_)
            cv.imshow("crop_ss() crop_img", crop_img)

    logging.debug("Function crop_ss() end")
    return crop_img


def make_cropped_ss_and_get_champions_to_buy(reader_=None):
    crop_img = make_cropped_ss(
        LOAD_IMAGE_=LOAD_IMAGE,
        cropping_x=CROPPING_X_CHAMPIONS,
        cropping_y=CROPPING_Y_CHAMPIONS,
        cropping_width=CROPPING_WIDTH_CHAMPIONS,
        cropping_height=CROPPING_HEIGHT_CHAMPIONS,
    )[0]
    OCRResult = dss.ocr_on_cropped_img(
        cropped_ss_with_champion_card_names=crop_img, reader_=reader_
    )
    print(OCRResult)


def make_cropped_ss_and_get_gold(reader_=None):
    crop_img = make_cropped_ss(
        LOAD_IMAGE_=LOAD_IMAGE,
        cropping_x=CROPPING_X_GOLD,
        cropping_y=CROPPING_Y_GOLD,
        cropping_width=CROPPING_WIDTH_GOLD,
        cropping_height=CROPPING_HEIGHT_GOLD,
    )[0]
    OCRResult = dss.ocr_on_cropped_img(
        cropped_ss_with_champion_card_names=crop_img, reader_=reader_
    )
    try:
        print(OCRResult[0][1])
        goldAmount = OCRResult[0][1]
    except (IndexError):
        print("Couldnt find the gold")
        goldAmount = 500
    return goldAmount


def make_cropped_ss_and_get_round(reader_=None, crop_x=CROPPING_X_ROUND):
    crop_img = make_cropped_ss(
        LOAD_IMAGE_=LOAD_IMAGE,
        cropping_x=crop_x,
        cropping_y=CROPPING_Y_ROUND,
        cropping_width=CROPPING_WIDTH_ROUND,
        cropping_height=CROPPING_HEIGHT_ROUND,
    )[0]

    cv.imshow("make_cropped_ss_and_get_round", crop_img)
    OCRResult = dss.ocr_on_cropped_img(
        cropped_ss_with_champion_card_names=crop_img, reader_=reader_
    )
    try:
        print(OCRResult[0][1])
        currentRound = OCRResult[0][1]
        return currentRound.replace("-", "")  ######### delete -
    except (IndexError):
        print("Couldnt find round")
        return None


def filling_list_with_counter_for_namedtuple(field_to_check, input_list):
    """


    Parameters
    ----------
    field_to_check : {4:"origin_prim", 5:"origin_sec", 6:"class_prim",
                           7:"class_sec"}
    input_list : List with 4,5,6,7 field == field_to_check. The default is champion_info.

    Returns
    -------
    list_of_counters : List of GUI counters

    """
    logging.debug("Function filling_list_with_counter_for_namedtuple() called")
    field_to_check_2_string = {
        4: "origin_prim",
        5: "origin_sec",
        6: "class_prim",
        7: "class_sec",
    }
    field_to_check_2_check_list = {
        4: origin_list,
        5: origin_list,
        6: class_list,
        7: class_list,
    }
    field_to_check_2_check_list_string = {
        4: "origin_list",
        5: "origin_list",
        6: "class_list",
        7: "class_list",
    }
    field_to_check_2_counters_list = {
        4: origin_counters,
        5: origin_counters,
        6: class_counters,
        7: class_counters,
    }
    list_of_counters = [None] * len(df.champion)
    for i, champ in enumerate(df.champion):
        if input_list[i][field_to_check] == "None":
            logging.info("Champion name: %s, champion index = %d", champ, i)
            logging.info(
                "Field with index %d == 'NONE' filling None as %sCounter",
                field_to_check,
                field_to_check_2_string[field_to_check],
            )
            list_of_counters[i] = None
        else:
            logging.info("%s IS NOT 'NONE'", field_to_check_2_string[field_to_check])
            for j, class_or_origin in enumerate(
                field_to_check_2_check_list[field_to_check]
            ):
                if input_list[i][field_to_check] == class_or_origin:
                    logging.info("Champion name: %s, champion index = %d", champ, i)
                    logging.info(
                        "Found match in champion %s and %s for : %s",
                        field_to_check_2_string[field_to_check],
                        field_to_check_2_check_list_string[field_to_check],
                        class_or_origin,
                    )
                    logging.info(
                        "Filling %s counter: %s",
                        field_to_check_2_string[field_to_check],
                        field_to_check_2_counters_list[field_to_check][j],
                    )
                    list_of_counters[i] = field_to_check_2_counters_list[
                        field_to_check
                    ][j]
    logging.debug("Function filling_list_with_counter_for_namedtuple() end")
    return list_of_counters


def append_counters_to_input_list(input_list):
    """


    Parameters
    ----------
    input_list : Appending counters to list with fields like {4:"origin_prim",
    5:"origin_sec", 6:"class_prim", 7:"class_sec"}.

    Returns
    -------
    None.

    """

    logging.debug("Function filling_list_with_counter_for_namedtuple() called")

    counters_to_append = [4, 5, 6, 7]
    for j in counters_to_append:
        list_of_counters_to_append = filling_list_with_counter_for_namedtuple(
            j, input_list
        )
        for i, champ in enumerate(input_list):
            champ.append(list_of_counters_to_append[i])

    logging.debug("Function filling_list_with_counter_for_namedtuple() end")


def update_origins():
    """Checks nonzero counters for champions in pool and updates origins by
    setting origin counters."""
    logging.debug("Function update_origins() called")

    origin_counters_value_list = [0] * len(origin_list)
    for i, origin_ in enumerate(origin_list):  # looping over counters for every origin
        logging.info("Current origin: %s", origin_)
        for (
            champ
        ) in (
            champions_list
        ):  # for loop to assign how much champions are nonzero in origin
            if champ.ChampCounter >= 1:
                logging.info("Current champ with counter >=1: %s", champ.name)
                if origin_ in (champ.origin_prim, champ.origin_sec):
                    logging.info(
                        "Current champ with counter >=1 match origin Prim or Sec \
                                 : %s or %s",
                        champ.origin_prim,
                        champ.origin_sec,
                    )
                    origin_counters_value_list[i] = origin_counters_value_list[i] + 1
        logging.info(
            "Number of nonzero champions in this origin: %s",
            origin_counters_value_list[i],
        )
        origin_counters[i] = origin_counters_value_list[i]

    logging.debug("Function update_origins() end")


def update_classes():
    """Checks nonzero counters for champions in pool and updates classes by
    setting class counters."""
    logging.debug("Function update_classes() called")

    class_counters_value_list = [0] * len(class_list)
    for i, class_ in enumerate(class_list):  # looping over counters for every class
        logging.info("Current class: %s", class_)
        for (
            champ
        ) in (
            champions_list
        ):  # for loop to assign how much champions are nonzero in class
            if champ.ChampCounter >= 1:
                logging.info("Current champ with counter >=1: %s", champ.name)
                if class_ in (champ.class_prim, champ.class_sec):
                    logging.info(
                        "Current champ with counter >=1 match class Prim or Sec \
                                 : %s or %s",
                        champ.class_prim,
                        champ.class_sec,
                    )
                    class_counters_value_list[i] = class_counters_value_list[i] + 1
        logging.info(
            "Number of nonzero champions in this class = %s",
            class_counters_value_list[i],
        )
        class_counters[i] = class_counters_value_list[i]

    logging.debug("Function update_classes() end")


def update_classes_and_origins():
    """Checks nonzero counters for champions in pool and updates classes and origins."""
    logging.debug("Function update_classes_and_origins() called")

    update_origins()
    update_classes()

    logging.debug("Function update_classes_and_origins() end")


def additional_points_from_origin_combo(champion_position):
    """Part of sum points, bonus from origin for specific champion.
    In: champion_position its just position of champion in list by primal
    champions to buy list.
    Out: Bonus points from origin."""
    logging.debug("Function additional_points_from_origin_combo() called")

    logging.info(
        "Calculating origin points for champ named: %s",
        champions_list[champion_position].name,
    )
    bonus_points_from_origin = 0.2
    total_count = champions_list[champion_position].OriginPrimCounter
    logging.info("Origin primary counter = %d", total_count)
    if champions_list[champion_position].origin_sec != "None":
        total_count = champions_list[champion_position].OriginSecCounter + total_count
        logging.info("Origin primary + secondary counter = %f", total_count)

    origin_bonus = total_count * bonus_points_from_origin
    logging.info("Bonus(return) = %f", origin_bonus)
    logging.debug("Function additional_points_from_origin_combo() end")
    return origin_bonus


def additional_points_from_class_combo(champion_position):
    """Part of sum points, bonus from class for specific champion.
    In: champion_position its just position of champion in list by primal
    champions to buy list.
    Out: Bonus points from class."""
    logging.debug("Function additional_points_from_class_combo() called")

    logging.info(
        "Calculating class points for champ named: %s ",
        champions_list[champion_position].name,
    )
    bonus_points_from_class = 0.2
    total_count = champions_list[champion_position].ClassPrimCounter
    if champions_list[champion_position].class_sec != "None":
        total_count = champions_list[champion_position].ClassSecCounter + total_count
        logging.info("Class primary + secondary counter = %f", total_count)

    class_bonus = total_count * bonus_points_from_class
    logging.info("Bonus(return) = %f", class_bonus)
    logging.debug("Function additional_points_from_class_combo() end")
    return class_bonus


def additional_points_from_champions_in_pool(champion_position):
    """Part of sum points, bonus from champion in pool.
    In: champion_position its just position of champion in list by primal
    champions to buy list.
    Out: Bonus points from champions that are already in pool."""
    logging.debug("Function additional_points_from_champions_in_pool() called")

    champion_pool_bonus = (champions_list[champion_position].ChampCounter - 1) * 0.2
    logging.info(
        "champion_pool_bonus = %f for champ named: %s ",
        champion_pool_bonus,
        champions_list[champion_position].name,
    )

    logging.debug("Function additional_points_from_champions_in_pool() end")
    return champion_pool_bonus


def update_champions_to_buy_from_ocr_detection(
    champions_list_for_ocr__,
    sort_detected_champions_to_buy_by_position,
    **kwargs,
):
    """
    Add 1 to every champion to buy counter detected in ocr_result.
    champion to buy counters GLOBAL STATE CHANGE !!!!!!!!!!!!!!!!!!!!

    Returns
    -------
    None.

    """
    logging.debug("Function update_champions_to_buy_from_ocr_detection() called")

    list_of_champs_to_buy_this_turn = sort_detected_champions_to_buy_by_position(
        **kwargs,
    )
    champs_to_buy_indexes = []
    for champ_to_buy in list_of_champs_to_buy_this_turn:
        for i, champ in enumerate(champions_list_for_ocr__):
            if champ_to_buy == champ:
                logging.info(
                    "IF inside for loop in update_champions_to_buy_from_ocr_detection()"
                )
                logging.info("Index in champions_list_for_ocr that is detected: %d", i)
                logging.info("Champ name in this index: %s", champ)
                champs_to_buy_indexes.append(i)
                break
    logging.info("Champions to buy indexes: %s", champs_to_buy_indexes)
    logging.debug("Function update_champions_to_buy_from_ocr_detection() end")
    return list_of_champs_to_buy_this_turn, champs_to_buy_indexes


def show_points_for_nonzero_counters(row_offset=2, show_mode=1):
    """It shows up champions POINTS to buy that counters are nonzero, as a text.
    Doesnt disappear currently, should be fixed.
    In: row_offset by default = 0 for buttons row placement."""
    logging.debug("Function show_points_for_nonzero_counters() called")
    position_on_screen = [0, 1, 2, 3, 4]
    points_for_champion_to_buy = [0] * 5
    champion_position_in_list_ordered_by_origin = update_champions_to_buy_from_ocr_detection(
        champions_list_for_ocr__=champions_list_for_ocr,
        sort_detected_champions_to_buy_by_position=dss.sort_detected_champions_to_buy_by_position,
        ocr_results_sorted=dss.ocr_on_cropped_img(
            cropped_ss_with_champion_card_names=make_cropped_ss()[0],
            reader_=reader,
        ),
        champions_list_for_ocr_=champions_list_for_ocr,
    )[
        1
    ]
    for i in range(0, len(champion_position_in_list_ordered_by_origin), 1):
        points_for_champion_to_buy[i] = (
            df.points[champion_position_in_list_ordered_by_origin[i]]
            + additional_points_from_origin_combo(
                champion_position_in_list_ordered_by_origin[i]
            )
            + additional_points_from_class_combo(
                champion_position_in_list_ordered_by_origin[i]
            )
            + additional_points_from_champions_in_pool(
                champion_position_in_list_ordered_by_origin[i]
            )
        )
        points_for_champion_to_buy[i] = round(points_for_champion_to_buy[i], 3)
    logging.info(
        "Points and champion_position_in_list_ordered_by_origin: %s",
        list(
            zip(
                points_for_champion_to_buy,
                champion_position_in_list_ordered_by_origin,
            )
        ),
    )

    human_readable_champions = []
    logging.info("Should be empty list: %s", human_readable_champions)
    for champ_index in champion_position_in_list_ordered_by_origin:
        human_readable_champions.append(champions_list[champ_index].name)
    logging.info(
        "Should be filled with nonzero champions to buy: %s", human_readable_champions
    )

    logging.info(
        "Champions availbable to buy with calculated points and position on screen list readable: %s",
        list(
            zip(
                points_for_champion_to_buy, human_readable_champions, position_on_screen
            )
        ),
    )

    logging.debug("Function show_points_for_nonzero_counters() end")
    return list(
        zip(
            points_for_champion_to_buy,
            champion_position_in_list_ordered_by_origin,
            position_on_screen,
        )
    )


def create_list_sorted_champions_to_buy_points_then_indexes_then_position_on_screen(
    points_for_nonzero_to_buy_zip,
):
    sorted_items = sorted(points_for_nonzero_to_buy_zip, reverse=True)
    return sorted_items


def update_champion_counter(index_tuple):
    index = index_tuple[1]
    logging.info("Bought champion: %s", champions_list[index].name)
    logging.info("Counter before: %s", champions_list[index].ChampCounter)
    champions_list[index].ChampCounter = champions_list[index].ChampCounter + 1
    logging.info("Counter after +1: %s", champions_list[index].ChampCounter)


def buy_best_available_champions_by_points_threshold(
    threshold=1.8,
    mousePathDelay=0.05,
):
    dss.activate_window(mode="game")
    points_zip = (
        create_list_sorted_champions_to_buy_points_then_indexes_then_position_on_screen(
            show_points_for_nonzero_counters()
        )
    )
    howMuchChampions = sum(i[0] >= threshold for i in points_zip)
    logging.info(
        "Threshold = %s, number of champions with points above: %s",
        threshold,
        howMuchChampions,
    )
    for i in range(0, howMuchChampions, 1):
        pyautogui.moveTo(
            x=championToBuyPositionOnGame[points_zip[i][2]][0],
            y=championToBuyPositionOnGame[points_zip[i][2]][1],
            duration=mousePathDelay,
        )
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.mouseUp()
        # to avoid mouse on buttons
        pyautogui.moveTo(300, 300)
        update_champion_counter(points_zip[i])

        ss_to_save = make_cropped_ss()[1]
        cv.imwrite(
            unique_file((current_bot_images_directory / "ssIlony"), "jpg"), ss_to_save
        )


def boost_up_points_for_class(clas='"Brawler"'):
    quer = "class_prim == {}".format(clas)
    for indexi in df.query(quer).index:
        print(indexi)
        df.at[indexi, "points"] = 5.0


def check_round_change(roundCurr):
    roundLocal = make_cropped_ss_and_get_round(reader_=reader)
    if roundLocal == None:  ########### different round placement on screen first rounds
        roundLocal = make_cropped_ss_and_get_round(
            reader_=reader, crop_x=CROPPING_X_ROUND_FIRST
        )
        try:
            if "#" in roundLocal:
                print("# in roundLocal something went wrong from check round change")
                roundLocal = None
        except (TypeError):
            roundLocal = None
    if roundLocal:
        try:
            roundCapturedNow = int(roundLocal)
        except (TypeError, ValueError):
            roundLocal = None
        if roundCurr == roundCapturedNow:
            print("roundSaved, roundCapturedNow:", roundCurr, roundCapturedNow)
            print("Round is the same! From check_round_change()")
            return roundCurr, 0
        else:
            print("roundSaved, roundCapturedNow:", roundCurr, roundCapturedNow)
            print("Round changed")
            return roundCapturedNow, 1
    else:
        return None, 2


# list of window names
WindowCapture.list_window_names()


# game things
play_button_first = "examples/bot/play_button_first.jpg"
tft_mode_button = "examples/bot/tft_mode_button.jpg"
confrimation_game_mode_button = "examples/bot/confrimation_game_mode_button.jpg"
find_match_button = "examples/bot/find_match_button.jpg"
accept_match_button = "examples/bot/accept_match_button.jpg"

play_again_button = "examples/bot/play_again_button.jpg"

# play again is first to find next match after finished one
templates_to_start_match_list = [
    play_again_button,
    play_button_first,
    tft_mode_button,
    confrimation_game_mode_button,
    find_match_button,
    accept_match_button,
]

start_tft_match(templates_to_start_match_list)

# wait for client to start
time.sleep(10)
wincap = WindowCapture("League of Legends (TM) Client")

buy_xp_button = "examples/bot/game/buy_xp_button.jpg"
refresh_button = "examples/bot/game/refresh_button.jpg"
exit_now_button = "examples/bot/game/exit_now_button.jpg"


# for i in range(0,5):
#     click_button_in_game(mode="xp")


# create directories to save images if doesnt exist
CWD = Path().cwd()
parent_directory = CWD / "gathered_images"
parent_directory.mkdir(parents=True, exist_ok=True)

print("Main directory for screens in this game")
bot_directory_name = "bot1"  # input()
print("Your input for bot directory is: ", bot_directory_name)


current_bot_images_directory = Path.joinpath(parent_directory, bot_directory_name)

current_bot_images_directory.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("champions_data_scaled.csv")

df.drop("Unnamed: 0", axis=1, inplace=True)
df.points = df["points"].round(3)

# order as in GUI
df.sort_values(by=["origin_prim", "champion"], inplace=True)
df.reset_index(drop=True, inplace=True)


if VARIABLE_PRINT_MODE:
    print("champions_list_for_ocr = [", end=" ")
    for champ in df.champion:
        print("'" + champ + "'", end=", ")
    print("]")


champions_list_for_ocr = [
    "Aatrox",
    "Elise",
    "Kalista",
    "Pyke",
    "Sivir",
    "Twisted Fate",
    "Vladimir",
    "Zilean",
    "Samira",
    "Jax",
    "Kayle",
    "Lee Sin",
    "Nasus",
    "Wukong",
    "Aurelion Sol",
    "Brand",
    "Braum",
    "Olaf",
    "Shyvana",
    "Swain",
    "Tristana",
    "Lulu",
    "Maokai",
    "Nunu & Willump",
    "Ornn",
    "Rakan",
    "Veigar",
    "Xayah",
    "Fiora",
    "Irelia",
    "Janna",
    "Morgana",
    "Talon",
    "Yasuo",
    "Yone",
    "Cho Gath",
    "Nautilus",
    "Neeko",
    "Annie",
    "Darius",
    "Sejuani",
    "Tahm Kench",
    "Akali",
    "Kennen",
    "Shen",
    "Zed",
    "Diana",
    "Kindred",
    "Teemo",
    "Yuumi",
    "Sett",
    "Azir",
    "Garen",
    "Jarvan IV",
    "Katarina",
    "Nidalee",
    "Tryndamere",
    "Vi",
]


reader = easyocr.Reader(["en"])


###################################################################################
############################## POINTS END ######################################
####################################################################################


###################################################################################
############################## POINTS START ######################################
####################################################################################
df.champion = df.champion.str.replace(" ", "")


origin_list = list(set(df.origin_prim)) + list(set(df.origin_sec))
origin_list = list(set(origin_list))
origin_list.remove("None")
origin_list.sort()

if VARIABLE_PRINT_MODE:
    for origin in origin_list:
        print(
            origin.lower()
            + "_champs = list(df.query("
            + "'origin_prim == "
            + '"'
            + "%s" % origin
            + '"'
            + "').champion)"
        )

if VARIABLE_PRINT_MODE:
    print("origin_champs_from_df_list = [", end=" ")
    for origin in origin_list:
        print(origin.lower() + "_champs", end=", ")
    print("]")

cultist_champs = list(df.query('origin_prim == "Cultist"').champion)
daredevil_champs = list(df.query('origin_prim == "Daredevil"').champion)
divine_champs = list(df.query('origin_prim == "Divine"').champion)
dragonsoul_champs = list(df.query('origin_prim == "Dragonsoul"').champion)
elderwood_champs = list(df.query('origin_prim == "Elderwood"').champion)
enlightened_champs = list(df.query('origin_prim == "Enlightened"').champion)
exile_champs = list(df.query('origin_prim == "Exile"').champion)
fabled_champs = list(df.query('origin_prim == "Fabled"').champion)
fortune_champs = list(df.query('origin_prim == "Fortune"').champion)
ninja_champs = list(df.query('origin_prim == "Ninja"').champion)
spirit_champs = list(df.query('origin_prim == "Spirit"').champion)
the_boss_champs = list(df.query('origin_prim == "The Boss"').champion)
warlord_champs = list(df.query('origin_prim == "Warlord"').champion)

origin_champs_from_df_list = [
    cultist_champs,
    daredevil_champs,
    divine_champs,
    dragonsoul_champs,
    elderwood_champs,
    enlightened_champs,
    exile_champs,
    fabled_champs,
    fortune_champs,
    ninja_champs,
    spirit_champs,
    the_boss_champs,
    warlord_champs,
]


class_list = list(set(df.class_prim)) + list(set(df.class_sec))
class_list = list(set(class_list))
class_list.remove("None")
class_list.sort()


if VARIABLE_PRINT_MODE:
    for champ in df.champion:
        print("Counter" + champ + " = 0")


# champions counters
CounterAatrox = 0
CounterElise = 0
CounterKalista = 0
CounterPyke = 0
CounterSivir = 0
CounterTwistedFate = 0
CounterVladimir = 0
CounterZilean = 0
CounterSamira = 0
CounterJax = 0
CounterKayle = 0
CounterLeeSin = 0
CounterNasus = 0
CounterWukong = 0
CounterAurelionSol = 0
CounterBrand = 0
CounterBraum = 0
CounterOlaf = 0
CounterShyvana = 0
CounterSwain = 0
CounterTristana = 0
CounterLulu = 0
CounterMaokai = 0
CounterNunu = 0
CounterOrnn = 0
CounterRakan = 0
CounterVeigar = 0
CounterXayah = 0
CounterFiora = 0
CounterIrelia = 0
CounterJanna = 0
CounterMorgana = 0
CounterTalon = 0
CounterYasuo = 0
CounterYone = 0
CounterChogath = 0
CounterNautilus = 0
CounterNeeko = 0
CounterAnnie = 0
CounterDarius = 0
CounterSejuani = 0
CounterTahmKench = 0
CounterAkali = 0
CounterKennen = 0
CounterShen = 0
CounterZed = 0
CounterDiana = 0
CounterKindred = 0
CounterTeemo = 0
CounterYuumi = 0
CounterSett = 0
CounterAzir = 0
CounterGaren = 0
CounterJarvanIV = 0
CounterKatarina = 0
CounterNidalee = 0
CounterTryndamere = 0
CounterVi = 0

if VARIABLE_PRINT_MODE:
    print("origin_champs_counters = [")
    for champ in df.champion:
        print("Counter" + champ, end=", ")
    print("]")
    print()

origin_champs_counters = [
    CounterAatrox,
    CounterElise,
    CounterKalista,
    CounterPyke,
    CounterSivir,
    CounterTwistedFate,
    CounterVladimir,
    CounterZilean,
    CounterSamira,
    CounterJax,
    CounterKayle,
    CounterLeeSin,
    CounterNasus,
    CounterWukong,
    CounterAurelionSol,
    CounterBrand,
    CounterBraum,
    CounterOlaf,
    CounterShyvana,
    CounterSwain,
    CounterTristana,
    CounterLulu,
    CounterMaokai,
    CounterNunu,
    CounterOrnn,
    CounterRakan,
    CounterVeigar,
    CounterXayah,
    CounterFiora,
    CounterIrelia,
    CounterJanna,
    CounterMorgana,
    CounterTalon,
    CounterYasuo,
    CounterYone,
    CounterChogath,
    CounterNautilus,
    CounterNeeko,
    CounterAnnie,
    CounterDarius,
    CounterSejuani,
    CounterTahmKench,
    CounterAkali,
    CounterKennen,
    CounterShen,
    CounterZed,
    CounterDiana,
    CounterKindred,
    CounterTeemo,
    CounterYuumi,
    CounterSett,
    CounterAzir,
    CounterGaren,
    CounterJarvanIV,
    CounterKatarina,
    CounterNidalee,
    CounterTryndamere,
    CounterVi,
]

# counters for origins

if VARIABLE_PRINT_MODE:
    for origin in origin_list:
        print("Counter" + origin + " = 0")


CounterCultist = 0
CounterDaredevil = 0
CounterDivine = 0
CounterDragonsoul = 0
CounterElderwood = 0
CounterEnlightened = 0
CounterExile = 0
CounterFabled = 0
CounterFortune = 0
CounterNinja = 0
CounterSpirit = 0
CounterTheBoss = 0
CounterWarlord = 0


if VARIABLE_PRINT_MODE:
    print("origin_counters = [")
    for origin in origin_list:
        print("Counter" + origin, end=", ")
    print("]")


origin_counters = [
    CounterCultist,
    CounterDaredevil,
    CounterDivine,
    CounterDragonsoul,
    CounterElderwood,
    CounterEnlightened,
    CounterExile,
    CounterFabled,
    CounterFortune,
    CounterNinja,
    CounterSpirit,
    CounterTheBoss,
    CounterWarlord,
]

# counters for classes


if VARIABLE_PRINT_MODE:
    for clas in class_list:
        print("Counter" + clas + " = 0")


CounterAdept = 0
CounterAssassin = 0
CounterBlacksmith = 0
CounterBrawler = 0
CounterDuelist = 0
CounterEmperor = 0
CounterExecutioner = 0
CounterKeeper = 0
CounterMage = 0
CounterMystic = 0
CounterSharpshooter = 0
CounterSlayer = 0
CounterSyphoner = 0
CounterVanguard = 0


if VARIABLE_PRINT_MODE:
    print("class_counters = [")
    for clas in class_list:
        print("Counter" + clas, end=", ")
    print("]")

class_counters = [
    CounterAdept,
    CounterAssassin,
    CounterBlacksmith,
    CounterBrawler,
    CounterDuelist,
    CounterEmperor,
    CounterExecutioner,
    CounterKeeper,
    CounterMage,
    CounterMystic,
    CounterSharpshooter,
    CounterSlayer,
    CounterSyphoner,
    CounterVanguard,
]

# Champion namedtuple things


champion_info = []
logging.debug("Filling champion_info in purpose of creating namedtuple")
for i, champ in enumerate(df.champion):
    champion_info.append(
        [
            champ,
            champions_list_for_ocr[i],
            i,
            origin_champs_counters[i],
            df.origin_prim[i],
            df.origin_sec[i],
            df.class_prim[i],
            df.class_sec[i],
        ]
    )
logging.debug("First filling champion_info has ended.")


append_counters_to_input_list(champion_info)

Champion = recordtype(
    "Champion",
    [
        "name",
        "name_ocr",
        "index_ocr",
        "ChampCounter",
        "origin_prim",
        "origin_sec",
        "class_prim",
        "class_sec",
        "OriginPrimCounter",
        "OriginSecCounter",
        "ClassPrimCounter",
        "ClassSecCounter",
    ],
)

if VARIABLE_PRINT_MODE:
    for i, champ in enumerate(champion_info):
        print(champ[0] + " = Champion(*champion_info[%d])" % i)

Aatrox = Champion(*champion_info[0])
Elise = Champion(*champion_info[1])
Kalista = Champion(*champion_info[2])
Pyke = Champion(*champion_info[3])
Sivir = Champion(*champion_info[4])
TwistedFate = Champion(*champion_info[5])
Vladimir = Champion(*champion_info[6])
Zilean = Champion(*champion_info[7])
Samira = Champion(*champion_info[8])
Jax = Champion(*champion_info[9])
Kayle = Champion(*champion_info[10])
LeeSin = Champion(*champion_info[11])
Nasus = Champion(*champion_info[12])
Wukong = Champion(*champion_info[13])
AurelionSol = Champion(*champion_info[14])
Brand = Champion(*champion_info[15])
Braum = Champion(*champion_info[16])
Olaf = Champion(*champion_info[17])
Shyvana = Champion(*champion_info[18])
Swain = Champion(*champion_info[19])
Tristana = Champion(*champion_info[20])
Lulu = Champion(*champion_info[21])
Maokai = Champion(*champion_info[22])
Nunu = Champion(*champion_info[23])
Ornn = Champion(*champion_info[24])
Rakan = Champion(*champion_info[25])
Veigar = Champion(*champion_info[26])
Xayah = Champion(*champion_info[27])
Fiora = Champion(*champion_info[28])
Irelia = Champion(*champion_info[29])
Janna = Champion(*champion_info[30])
Morgana = Champion(*champion_info[31])
Talon = Champion(*champion_info[32])
Yasuo = Champion(*champion_info[33])
Yone = Champion(*champion_info[34])
Chogath = Champion(*champion_info[35])
Nautilus = Champion(*champion_info[36])
Neeko = Champion(*champion_info[37])
Annie = Champion(*champion_info[38])
Darius = Champion(*champion_info[39])
Sejuani = Champion(*champion_info[40])
TahmKench = Champion(*champion_info[41])
Akali = Champion(*champion_info[42])
Kennen = Champion(*champion_info[43])
Shen = Champion(*champion_info[44])
Zed = Champion(*champion_info[45])
Diana = Champion(*champion_info[46])
Kindred = Champion(*champion_info[47])
Teemo = Champion(*champion_info[48])
Yuumi = Champion(*champion_info[49])
Sett = Champion(*champion_info[50])
Azir = Champion(*champion_info[51])
Garen = Champion(*champion_info[52])
JarvanIV = Champion(*champion_info[53])
Katarina = Champion(*champion_info[54])
Nidalee = Champion(*champion_info[55])
Tryndamere = Champion(*champion_info[56])
Vi = Champion(*champion_info[57])


if VARIABLE_PRINT_MODE:
    print("champions_list = [")
    for champ in champion_info:
        print(champ[0], end=", ")
    print("]")
    print()


champions_list = [
    Aatrox,
    Elise,
    Kalista,
    Pyke,
    Sivir,
    TwistedFate,
    Vladimir,
    Zilean,
    Samira,
    Jax,
    Kayle,
    LeeSin,
    Nasus,
    Wukong,
    AurelionSol,
    Brand,
    Braum,
    Olaf,
    Shyvana,
    Swain,
    Tristana,
    Lulu,
    Maokai,
    Nunu,
    Ornn,
    Rakan,
    Veigar,
    Xayah,
    Fiora,
    Irelia,
    Janna,
    Morgana,
    Talon,
    Yasuo,
    Yone,
    Chogath,
    Nautilus,
    Neeko,
    Annie,
    Darius,
    Sejuani,
    TahmKench,
    Akali,
    Kennen,
    Shen,
    Zed,
    Diana,
    Kindred,
    Teemo,
    Yuumi,
    Sett,
    Azir,
    Garen,
    JarvanIV,
    Katarina,
    Nidalee,
    Tryndamere,
    Vi,
]


championToBuyPositionOnGame = [
    (600, 975),
    (794, 975),
    (984, 975),
    (1173, 975),
    (1363, 975),
]


boost_up_points_for_class(clas='"Sharpshooter"')


ROUNDSTOBUYREFRESH = [22, 25, 31, 32, 35, 41, 42, 45, 51, 52, 55, 61, 62, 65]

ROUNDSTOBUYXP = [26, 36, 46, 56, 66]

SHUFFLEROUNDS = [23, 25, 26, 32, 33, 36, 37, 42, 43, 47, 51, 52, 53, 55, 61, 65]

# update current champions to buy with ocr
roundNow = None
while True:
    try:

        EXIT_FLAG_ = click_button_in_game("exit")
        if EXIT_FLAG_ is True:
            # time to close
            time.sleep(10)
            if not (
                "League of Legends (TM) Client" in WindowCapture.list_window_names()
            ):
                time.sleep(10)
                logging.info("Exit from game succesfull")
                break

        checkingRound = check_round_change(roundNow)
        if checkingRound[1]:
            roundNow = checkingRound[0]
            print(
                "Changed round or there is no round on the screen!!!!!!!!!!!!!!!!!!!!!!! From while loop"
            )

            try:
                capturedRound = make_cropped_ss_and_get_round(reader_=reader)
                buy_best_available_champions_by_points_threshold()
                if roundNow in ROUNDSTOBUYXP:
                    for i in range(0, 15, 1):
                        click_button_in_game("xp")
                        time.sleep(0.1)

                if roundNow in ROUNDSTOBUYREFRESH:
                    for i in range(0, int(capturedRound[0]) + 1, 1):
                        click_button_in_game("refresh")
                        time.sleep(0.1)
                        buy_best_available_champions_by_points_threshold()

                # if roundNow in SHUFFLEROUNDS:
                #     shuffle_champs()

            except (TypeError):
                print(
                    "None type in ocr_on_cropped_img(make_cropped_ss(wincap)[0]) should be end of the game, bcs no window"
                )
                # break

    except (IndexError):
        logging.info("Caught IndexError, it means less than 5 champion cards on screen")
        pass

pyautogui.PAUSE = 0.02
pyautogui.FAILSAFE = False


###################################################################################
############################## POINTS END ######################################
####################################################################################


#############################################################################
################ CHECK HEX OCCUPANCY WITH template matching ##################]
################################################################################
# test cases
# jpgwithunits = "examples/playgroundwithunits2.jpg"
# jpgwithunits = "examples/playground.jpg"
# jpgwithunits = "examples/playgroundwithunits.jpg"


# # img = make_cropped_ss_and_get_champions_to_buy()

# img = cv.imread("playground.jpg", cv.IMREAD_UNCHANGED)
# # img=cv.imread("playgroundwithunits.jpg", cv.IMREAD_UNCHANGED)
# playgroundHexes = [
#     [584, 410],
#     [677, 413],
#     [798, 405],
#     [915, 400],
#     [1020, 415],
#     [1128, 409],
#     [1227, 402],
#     [622, 466],
#     [731, 468],
#     [855, 476],
#     [954, 484],
#     [1077, 480],
#     [1189, 477],
#     [1306, 474],
#     [535, 515],
#     [670, 515],
#     [783, 515],
#     [902, 515],
#     [1018, 515],
#     [1142, 515],
#     [1248, 515],
#     [599, 618],
#     [720, 627],
#     [847, 626],
#     [974, 625],
#     [1100, 627],
#     [1207, 627],
#     [1327, 630],
# ]


# benchHexes = [
#     [454, 720],
#     [567, 720],
#     [671, 720],
#     [789, 720],
#     [900, 720],
#     [1011, 720],
#     [1120, 720],
#     [1233, 720],
#     [1328, 720],
# ]

# hexToTemplateMatchWidth = 50
# hextoTemlpateMatchHeight = 50

# playgroundHexesWithOffsetToCropp = []

# for hexi in playgroundHexes:
#     playgroundHexesWithOffsetToCropp.append([hexi[0] - 25, hexi[1] - 25])


# benchHexesWithOffsetToCropp = []

# for hexi in benchHexes:
#     benchHexesWithOffsetToCropp.append([hexi[0] - 25, hexi[1] - 25])


# # for i,hexi in enumerate(playgroundHexesWithOffsetToCropp):
# #     saveName = "C:\\Users\\janusz\\Documents\\TFT-DSS\\hexJPG\\playground\\playgroundHex" + "{}".format(i) + ".jpg"
# #     make_cropped_ss_and_get_champions_to_buy(croppingY=hexi[1], croppingX=hexi[0], croppingHeight=hextoTemlpateMatchHeight,croppingWidth=hexToTemplateMatchWidth,saveMode=1,savingName=saveName)


# # for i,hexi in enumerate(benchHexesWithOffsetToCropp):
# #     saveName = "C:\\Users\\janusz\\Documents\\TFT-DSS\\hexJPG\\bench\\benchHex" + "{}".format(i) + ".jpg"
# #     make_cropped_ss_and_get_champions_to_buy(croppingY=hexi[1], croppingX=hexi[0], croppingHeight=hextoTemlpateMatchHeight,croppingWidth=hexToTemplateMatchWidth,saveMode=1,savingName=saveName)


# HEXES_WITHOUT_CHAMPIONS_JPG_LIST = [
#     "hexJPG\\playground\\playgroundHex0.jpg",
#     "hexJPG\\playground\\playgroundHex1.jpg",
#     "hexJPG\\playground\\playgroundHex2.jpg",
#     "hexJPG\\playground\\playgroundHex3.jpg",
#     "hexJPG\\playground\\playgroundHex4.jpg",
#     "hexJPG\\playground\\playgroundHex5.jpg",
#     "hexJPG\\playground\\playgroundHex6.jpg",
#     "hexJPG\\playground\\playgroundHex7.jpg",
#     "hexJPG\\playground\\playgroundHex8.jpg",
#     "hexJPG\\playground\\playgroundHex9.jpg",
#     "hexJPG\\playground\\playgroundHex10.jpg",
#     "hexJPG\\playground\\playgroundHex11.jpg",
#     "hexJPG\\playground\\playgroundHex12.jpg",
#     "hexJPG\\playground\\playgroundHex13.jpg",
#     "hexJPG\\playground\\playgroundHex14.jpg",
#     "hexJPG\\playground\\playgroundHex15.jpg",
#     "hexJPG\\playground\\playgroundHex16.jpg",
#     "hexJPG\\playground\\playgroundHex17.jpg",
#     "hexJPG\\playground\\playgroundHex18.jpg",
#     "hexJPG\\playground\\playgroundHex19.jpg",
#     "hexJPG\\playground\\playgroundHex20.jpg",
#     "hexJPG\\playground\\playgroundHex21.jpg",
#     "hexJPG\\playground\\playgroundHex22.jpg",
#     "hexJPG\\playground\\playgroundHex23.jpg",
#     "hexJPG\\playground\\playgroundHex24.jpg",
#     "hexJPG\\playground\\playgroundHex25.jpg",
#     "hexJPG\\playground\\playgroundHex26.jpg",
#     "hexJPG\\playground\\playgroundHex27.jpg",
# ]


# BENCH_WITHOUT_CHAMPIONS_JPG_LIST = [
#     "hexJPG\\bench\\benchHex0.jpg",
#     "hexJPG\\bench\\benchHex1.jpg",
#     "hexJPG\\bench\\benchHex2.jpg",
#     "hexJPG\\bench\\benchHex3.jpg",
#     "hexJPG\\bench\\benchHex4.jpg",
#     "hexJPG\\bench\\benchHex5.jpg",
#     "hexJPG\\bench\\benchHex6.jpg",
#     "hexJPG\\bench\\benchHex7.jpg",
#     "hexJPG\\bench\\benchHex8.jpg",
# ]

# # u = cv.imread("C:\\Users\\janusz\\pictures\\tft\\testingimages\\graBack\\name00000000.jpg",cv.IMREAD_UNCHANGED)
# # cv.imshow("okno", u)


# # for i,hexi in enumerate(playgroundHexes):
# #     print("playgroudHex{}Occupancy = 0".format(i))
# playgroudHex0Occupancy = 0
# playgroudHex1Occupancy = 0
# playgroudHex2Occupancy = 0
# playgroudHex3Occupancy = 0
# playgroudHex4Occupancy = 0
# playgroudHex5Occupancy = 0
# playgroudHex6Occupancy = 0
# playgroudHex7Occupancy = 0
# playgroudHex8Occupancy = 0
# playgroudHex9Occupancy = 0
# playgroudHex10Occupancy = 0
# playgroudHex11Occupancy = 0
# playgroudHex12Occupancy = 0
# playgroudHex13Occupancy = 0
# playgroudHex14Occupancy = 0
# playgroudHex15Occupancy = 0
# playgroudHex16Occupancy = 0
# playgroudHex17Occupancy = 0
# playgroudHex18Occupancy = 0
# playgroudHex19Occupancy = 0
# playgroudHex20Occupancy = 0
# playgroudHex21Occupancy = 0
# playgroudHex22Occupancy = 0
# playgroudHex23Occupancy = 0
# playgroudHex24Occupancy = 0
# playgroudHex25Occupancy = 0
# playgroudHex26Occupancy = 0
# playgroudHex27Occupancy = 0


# # for i,hexi in enumerate(playgroundHexes):
# #     print("playgroudHex{}Occupancy, ".format(i), end="")

# playgroundHexesOccupancyList = [
#     playgroudHex0Occupancy,
#     playgroudHex1Occupancy,
#     playgroudHex2Occupancy,
#     playgroudHex3Occupancy,
#     playgroudHex4Occupancy,
#     playgroudHex5Occupancy,
#     playgroudHex6Occupancy,
#     playgroudHex7Occupancy,
#     playgroudHex8Occupancy,
#     playgroudHex9Occupancy,
#     playgroudHex10Occupancy,
#     playgroudHex11Occupancy,
#     playgroudHex12Occupancy,
#     playgroudHex13Occupancy,
#     playgroudHex14Occupancy,
#     playgroudHex15Occupancy,
#     playgroudHex16Occupancy,
#     playgroudHex17Occupancy,
#     playgroudHex18Occupancy,
#     playgroudHex19Occupancy,
#     playgroudHex20Occupancy,
#     playgroudHex21Occupancy,
#     playgroudHex22Occupancy,
#     playgroudHex23Occupancy,
#     playgroudHex24Occupancy,
#     playgroudHex25Occupancy,
#     playgroudHex26Occupancy,
#     playgroudHex27Occupancy,
# ]

# # for i,hexi in enumerate(benchHexes):
# #     print("benchHex{}Occupancy = 0".format(i))


# benchHex0Occupancy = 0
# benchHex1Occupancy = 0
# benchHex2Occupancy = 0
# benchHex3Occupancy = 0
# benchHex4Occupancy = 0
# benchHex5Occupancy = 0
# benchHex6Occupancy = 0
# benchHex7Occupancy = 0
# benchHex8Occupancy = 0

# # for i,hexi in enumerate(benchHexes):
# #     print("benchHex{}Occupancy, ".format(i), end="")


# benchHexesOccupancyList = [
#     benchHex0Occupancy,
#     benchHex1Occupancy,
#     benchHex2Occupancy,
#     benchHex3Occupancy,
#     benchHex4Occupancy,
#     benchHex5Occupancy,
#     benchHex6Occupancy,
#     benchHex7Occupancy,
#     benchHex8Occupancy,
# ]


# def check_hexes_list_occupancy(
#     hexesToCheckListJPG=HEXES_WITHOUT_CHAMPIONS_JPG_LIST,
#     hexesLocationWithOffset=playgroundHexesWithOffsetToCropp,
#     occupancyList=playgroundHexesOccupancyList,
# ):
#     img_main = make_cropped_ss()
#     for i, jpg in enumerate(hexesToCheckListJPG):
#         img_rgb = make_cropped_ss(
#             croppingY=hexesLocationWithOffset[i][1],
#             croppingX=hexesLocationWithOffset[i][0],
#             croppingHeight=hextoTemlpateMatchHeight,
#             croppingWidth=hexToTemplateMatchWidth,
#             saveMode=0,
#             savingName="saveName",
#         )
#         img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
#         template = cv.imread(jpg, 0)
#         w, h = template.shape[::-1]
#         res = cv.matchTemplate(img_gray, template, cv.TM_CCORR_NORMED)
#         threshold = 0.95
#         loc = np.where(res >= threshold)
#         if loc[0].size > 0:
#             print("not occupied  hex number {}".format(i))
#             occupancyList[i] = 0
#         else:
#             print("Hex is occupied {}".format(i))
#             occupancyList[i] = 1

#         for pt in zip(*loc[::-1]):
#             cv.rectangle(
#                 img_main,
#                 tuple(hexesLocationWithOffset[i]),
#                 (hexesLocationWithOffset[i][0] + w, hexesLocationWithOffset[i][1] + h),
#                 (0, 0, 255),
#                 2,
#             )
#     cv.imshow("ss5", img_main)


# # check_hexes_list_occupancy(BENCH_WITHOUT_CHAMPIONS_JPG_LIST,benchHexesWithOffsetToCropp,benchHexesOccupancyList)


# ##############################################################################
# ########################## template matching END #############################
# ##############################################################################


# ##############################################################################
# ############################# Simulating user actions ########################
# ##############################################################################


# def move_champion_from_x_to_y(startingPoint, metaPoint):
#     activate_window(mode="game")
#     # time.sleep(0.02)
#     pyautogui.moveTo(x=startingPoint[0], y=startingPoint[1], duration=0.01)
#     pyautogui.click()
#     pyautogui.moveTo(x=metaPoint[0], y=metaPoint[1], duration=0.01)
#     pyautogui.mouseDown()
#     # time.sleep(0.02)
#     pyautogui.mouseUp()


# def move_champion_from_x_to_y_without_game_activation(startingPoint, metaPoint):

#     pyautogui.moveTo(x=startingPoint[0], y=startingPoint[1], duration=0.01)
#     pyautogui.click()
#     pyautogui.moveTo(x=metaPoint[0], y=metaPoint[1], duration=0.01)
#     pyautogui.mouseDown()
#     # time.sleep(0.02)
#     pyautogui.mouseUp()


# # move_champion_from_x_to_y(benchHexes[2],playgroundHexes[9])

# # move_champion_from_x_to_y(benchHexes[3],playgroundHexes[10])


# # move_champion_from_x_to_y(playgroundHexes[21],playgroundHexes[23])


# def shuffle_champions_on_first_and_third_row_of_hexes_and_subsitute_bench():
#     occupiedHexesLocation = []

#     check_hexes_list_occupancy(
#         BENCH_WITHOUT_CHAMPIONS_JPG_LIST,
#         benchHexesWithOffsetToCropp,
#         benchHexesOccupancyList,
#     )
#     check_hexes_list_occupancy()
#     i = 0
#     while i < (len(playgroundHexesOccupancyList) - 7):
#         if playgroundHexesOccupancyList[i]:
#             print("i is {}".format(i))
#             occupiedHexesLocation.append(playgroundHexes[i])
#             print(
#                 "Added {} {} to occupiedHexesLocation list in shuffle_champions_on_first_and_third_row_of_hexes function".format(
#                     playgroundHexes[i], i
#                 )
#             )
#         if i == 6:
#             i = i + 7  ### to avoid checking second row of playground hexes
#             print("changed i: {}".format(i))
#         i = i + 1

#     for i in range(0, len(benchHexesOccupancyList), 1):
#         if benchHexesOccupancyList[i]:
#             occupiedHexesLocation.append(benchHexes[i])
#             print(
#                 "Added {} {} to occupiedHexesLocation list in shuffle_champions_on_first_and_third_row_of_hexes function".format(
#                     benchHexes[i], i
#                 )
#             )

#     print("occupiedHexesLocation before shuffle {}".format(occupiedHexesLocation))
#     np.random.shuffle(occupiedHexesLocation)

#     print("occupiedHexesLocation after shuffle {}".format(occupiedHexesLocation))

#     print("There will be {} shufling".format(len(occupiedHexesLocation) // 2))

#     activate_window(mode="game")
#     if len(occupiedHexesLocation) % 2 == 0:
#         for i in range(0, len(occupiedHexesLocation), 2):
#             move_champion_from_x_to_y_without_game_activation(
#                 occupiedHexesLocation[i], occupiedHexesLocation[i + 1]
#             )

#     if len(occupiedHexesLocation) % 2 == 1:
#         for i in range(0, len(occupiedHexesLocation) - 1, 2):
#             move_champion_from_x_to_y_without_game_activation(
#                 occupiedHexesLocation[i], occupiedHexesLocation[i + 1]
#             )


# def move_champions_from_X_row_to_Y_row(fromRow=2, toRow=1):
#     if fromRow == 1:
#         hexes = [0, 1, 2, 3, 4, 5, 6]  # list(range(0+7*(fromRow-1),7*fromRow))
#     elif fromRow == 2:
#         hexes = [7, 8, 9, 10, 11, 12, 13]
#     elif fromRow == 3:
#         hexes = [14, 15, 16, 17, 18, 19, 20]
#     elif fromRow == 4:
#         hexes = [21, 22, 23, 24, 25, 26, 27]
#     seed = np.random.randint(0, 10000)
#     np.random.seed(seed)
#     np.random.shuffle(hexes)
#     for i, hexi in enumerate(hexes):
#         move_champion_from_x_to_y(
#             startingPoint=playgroundHexes[hexi],
#             metaPoint=playgroundHexes[i + (toRow - 1) * 7],
#         )


# # play_or_party_button_in_client_pos = [440,200]

# # confirm_button_in_client_pos = [850,850]

# # find_match_button_in_client_pos = [850,840]

# # accept_button_in_client_pos = [960,720]


# # activate_window(mode="game")
# # pyautogui.click(play_or_party_button_in_client_pos)
# # time.sleep(5)


# # pyautogui.click(confirm_button_in_client_pos)
# # time.sleep(5)


# # pyautogui.click(find_match_button_in_client_pos)
# # time.sleep(2)

# # u=1
# # while GetWindowText(GetForegroundWindow()) == 'League of Legends':
# #     pyautogui.click(accept_button_in_client_pos)
# #     time.sleep(1)
# #     u=0


# # time.sleep(30)


# gameBuyXPButtonXY = [305, 865]
# gameBuyXPButtonHW = [60, 185]
# # make_cropped_ss(loadImage=0, window=wincap, croppingY=gameBuyXPButtonXY[1], croppingX=gameBuyXPButtonXY[0], croppingHeight=gameBuyXPButtonHW[0], croppingWidth=gameBuyXPButtonHW[1], saveMode=0, savingName="TemplateMatchingGame\\buyXPButton.jpg")


# gameRefreshButtonXY = [305, 935]
# gameRefreshButtonHW = [60, 185]
# # make_cropped_ss(loadImage=0, window=wincap, croppingY=gameRefreshButtonXY[1], croppingX=gameRefreshButtonXY[0], croppingHeight=gameRefreshButtonHW[0], croppingWidth=gameRefreshButtonHW[1], saveMode=0, savingName="TemplateMatchingGame\\refreshButton.jpg")


# gameBuyXPButtonJPG = "TemplateMatchingGame\\buyXPButton.jpg"
# gameRefreshButtonJPG = "TemplateMatchingGame\\refreshButton.jpg"

# gameExitNowButtonXY = [750, 487]
# gameExitNowButtonHW = [50, 150]

# gameExitNowButtonJPG = "TemplateMatchingGame\\exitNowGameButton.jpg"
# # match_template_with_screen(hexesToCheckListJPG=gameBuyXPButtonJPG, hexesLocationWithOffset = gameBuyXPButtonXY, HW = gameBuyXPButtonHW, threshold=0.95)

# # match_template_with_screen(hexesToCheckListJPG=gameRefreshButtonJPG, hexesLocationWithOffset = gameRefreshButtonXY, HW = gameRefreshButtonHW, threshold=0.95)

# # match_template_with_screen(hexesToCheckListJPG=gameExitNowButtonJPG, hexesLocationWithOffset = gameExitNowButtonXY, HW = gameBuyXPButtonHW, threshold=0.90)


# def match_template_with_screen(
#     hexesToCheckListJPG=gameBuyXPButtonJPG,
#     hexesLocationWithOffset=gameBuyXPButtonXY,
#     HW=gameBuyXPButtonHW,
#     threshold=0.95,
# ):
#     img_main = make_cropped_ss()
#     try:
#         if img_main.all() != None:  ### return 0 if ss not found
#             img_rgb = make_cropped_ss(
#                 loadImage=1,
#                 window=wincap,
#                 croppingY=hexesLocationWithOffset[1],
#                 croppingX=hexesLocationWithOffset[0],
#                 croppingHeight=HW[0],
#                 croppingWidth=HW[1],
#                 saveMode=0,
#                 savingName="TemplateMatchingClient\\acceptGameButton.jpg",
#                 imageToLoad=img_main,
#             )
#             img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
#             template = cv.imread(hexesToCheckListJPG, 0)
#             w, h = template.shape[::-1]
#             res = cv.matchTemplate(img_gray, template, cv.TM_CCORR_NORMED)
#             loc = np.where(res >= threshold)

#         print(loc[0].size)

#         for pt in zip(*loc[::-1]):
#             cv.rectangle(
#                 img_main,
#                 tuple(hexesLocationWithOffset),
#                 (
#                     hexesLocationWithOffset[0] + HW[1],
#                     hexesLocationWithOffset[1] + HW[0],
#                 ),
#                 (0, 0, 255),
#                 2,
#             )
#         cv.imshow("ss5", img_main)
#         return loc[0].size  # << if this >0 then template has been found
#     except (AttributeError):
#         print(
#             "Couldnt do image because there is no screenshot! from match template with screen"
#         )


# def shuffle_champs():
#     pyautogui.moveTo(x=300, y=300, duration=0.5)  # to avoid blocking screen
#     shuffle_champions_on_first_and_third_row_of_hexes_and_subsitute_bench()
#     move_champions_from_X_row_to_Y_row(fromRow=2, toRow=1)
#     move_champions_from_X_row_to_Y_row(fromRow=4, toRow=3)


# def check_round_change(roundCurr):
#     roundLocal = make_cropped_ss_and_get_round()
#     if roundLocal == None:  ########### different round placement on screen
#         roundLocal = make_cropped_ss_and_get_round(croppingX=820, croppingWidth=60)
#         try:
#             if "#" in roundLocal:
#                 print("# in roundLocal something went wrong from check round change")
#                 roundLocal = None
#         except (TypeError):
#             roundLocal = None
#     if roundLocal:
#         try:
#             roundCapturedNow = int(roundLocal)
#         except (TypeError):
#             roundLocal = None
#         if roundCurr == roundCapturedNow:
#             print("roundSaved, roundCapturedNow:", roundCurr, roundCapturedNow)
#             print("Round is the same! From check_round_change()")
#             return roundCurr, 0
#         else:
#             print("roundSaved, roundCapturedNow:", roundCurr, roundCapturedNow)
#             print("Round changed")
#             return roundCapturedNow, 1
#     else:
#         return None, 2

# def boost_up_points_for_class(clas='"Brawler"'):
#     quer = "class_prim == {}".format(clas)
#     for indexi in df.query(quer).index:
#         print(indexi)
#         df.at[indexi, "points"] = 5.0

# boost_up_points_for_class(clas='"Brawler"')


# Screenshotwindow = pyautogui.getWindowsWithTitle("League of Legends (TM) Client")[0]

# #  high lvl
# # ROUNDSTOBUYREFRESH = [23,33,45,51,52,55,61,62,65]

# # ROUNDSTOBUYXP = [42,46,56,66]

# # SHUFFLEROUNDS = [23,25,26,32,33,36,37,42,43,47,51,52,53,55,61,65]


# # VANGUARD
# ROUNDSTOBUYREFRESH = [22, 25, 31, 32, 35, 41, 42, 45, 51, 52, 55, 61, 62, 65]

# ROUNDSTOBUYXP = [26, 36, 46, 56, 66]

# SHUFFLEROUNDS = [23, 25, 26, 32, 33, 36, 37, 42, 43, 47, 51, 52, 53, 55, 61, 65]

# # update current champions to buy with ocr
# ROUNDCOUNTER = 0
# TRYCOUNTER = 0
# roundNow = None
# localCapturedRound = "00"
# THRESHOLDFORPOINTSTOBUYCHAMPION = 2.0
# while True:
#     try:
#         # TRYCOUNTER = TRYCOUNTER + 1
#         # if (TRYCOUNTER % 20) == 0:
#         #     pyautogui.moveTo(x=961, y=626, duration=0.15) # continue
#         #     pyautogui.mouseDown()
#         #     time.sleep(0.1)
#         #     pyautogui.mouseUp()

#         if match_template_with_screen(
#             hexesToCheckListJPG=gameExitNowButtonJPG,
#             hexesLocationWithOffset=gameExitNowButtonXY,
#             HW=gameExitNowButtonHW,
#             threshold=0.95,
#         ):
#             print("Found exit game button!!!!!")

#             pyautogui.moveTo(x=834, y=545, duration=0.15)  # exit now
#             pyautogui.mouseDown()
#             time.sleep(0.1)
#             pyautogui.mouseUp()

#         checkingRound = check_round_change(roundNow)
#         if checkingRound[1]:
#             roundNow = checkingRound[0]
#             print(
#                 "Changed round or there is no round on the screen!!!!!!!!!!!!!!!!!!!!!!! From while loop"
#             )

#         # try:
#             championsToBuyIndexes = (
#                 from_OCR_champions_to_buy_list_to_counter_index_list()
#             )
#             pointsForChampionsInGameToBuy = show_points_for_champions_to_buy()
#             print(pointsForChampionsInGameToBuy)
#             capturedRound = make_cropped_ss_and_get_round()
#             buy_champ_if_has_more_points_than_threshold()
#             if roundNow in ROUNDSTOBUYXP:
#                 while (
#                     click_button_in_game("xp")
#                 ):  ### buy XP till bot has gold to do it
#                     print("Buying XP")

#             if roundNow in ROUNDSTOBUYREFRESH:
#                 for i in range(0, int(capturedRound[0]) + 1, 1):
#                     click_button_in_game("refresh")
#                     time.sleep(0.1)
#                     buy_champ_if_has_more_points_than_threshold()

#             if roundNow in SHUFFLEROUNDS:
#                 shuffle_champs()

#             # except (TypeError):
#             #     print("end of the game")
#                 # break

#     except (IndexError):
#         logging.info("Caught IndexError, it means less than 5 champion cards on screen")
#         pass


# # first hex on substitues bench
# # 479,727
# ######################### buy 2 champions with most points


# # points list sorted by apperance on screen


# # pyautogui.getWindowsWithTitle("Spyder (Python 3.8)")[0].minimize()

# # pyautogui.getWindowsWithTitle("Discord")[0].restore()

# # time.sleep(2)

# # pyautogui.getWindowsWithTitle("TFTDSS")[0].maximize()

# # TFTDSSwindow = pyautogui.getWindowsWithTitle("wind")[0]
# # TFTDSSwindow.minimize()
# # time.sleep(1)
# # TFTDSSwindow.restore()
# # TFTDSSwindow.activate()

# # try:
# #     pyautogui.getWindowsWithTitle("TFTDSS")[0].minimize()
# #     time.sleep(1)
# #     pyautogui.getWindowsWithTitle("TFTDSS")[0].restore()
# # except:
# #     pyautogui.getWindowsWithTitle("TFTDSS")[0].minimize()
# #     time.sleep(1)
# #     pyautogui.getWindowsWithTitle("TFTDSS")[0].activate()

# # pyautogui.getWindowsWithTitle("TFTDSS")[0].restore()

# # time.sleep(1)

# # pyautogui.click(x=850, y=450) ### first iteration with gui


# # pyautogui.click(x=1010, y=450) ### after first iteration with gui

# # 862,347 last champion on gui
# # 699,347
# # 535,346
# # 376,346
# # 211,346 first champion on gui


# # championToBuyPositionOnGUI = [ (210,345), (375,345), (535, 346), (700, 345), (860,345)]

# # championToBuyPositionOnGame = [ (600,975), (794,975), (984,975), (1173,975), (1363,975) ]

# # time.sleep(2)

# # try:
# #     TFTDSSwindow.restore()
# #     TFTDSSwindow.activate()
# # except:
# #     TFTDSSwindow.restore()


# # gameWindow = pyautogui.getWindowsWithTitle("wind")[0]

# # # for i in range(2,5,1):
# #     time.sleep(1)
# #     TFTDSSwindow.activate()
# #     pyautogui.click(x=championToBuyPositionOnGUI[i][0], y=championToBuyPositionOnGUI[i][1])
# #     time.sleep(1)
# #     gameWindow.activate()
# #     pyautogui.click(x=championToBuyPositionOnGame[i][0], y=championToBuyPositionOnGame[i][1])


# # def click_on_champion_to_buy_on_GUI_then_click_on_champion_in_game(positionOnGUI=0,positionInGame=0,GUIwindow=TFTDSSwindow,inGameWindow=gameWindow):
# #     time.sleep(1)
# #     GUIwindow.activate()
# #     pyautogui.click(x=championToBuyPositionOnGUI[positionOnGUI][0], y=championToBuyPositionOnGUI[positionOnGUI][1])
# #     time.sleep(1)
# #     inGameWindow.activate()
# #     pyautogui.click(x=championToBuyPositionOnGame[positionInGame][0], y=championToBuyPositionOnGame[positionInGame][1])

# # 600,975 ## first champion to buy in game
# # 794,975
# # 984,975
# # 1173,975
# # 1363,975 ## last champion to buy in game
