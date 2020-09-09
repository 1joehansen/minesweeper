import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import pyscreenshot as ImageGrab
import pyautogui as mouse
import numpy as np


def clickCell(x, y):
    print(f"Clicked {x}, {y}")
    # mouse.moveTo(338 - 20 + 40 * x, 310 - 20 + 40 * y)
    # mouse.leftClick()

    x = str(int(x))
    y = str(int(y))
    cell = x + "_" + y

    element = driver.find_element_by_id(cell)
    element.click()


def flagCell(x, y):
    print(f"Flagged {x}, {y}")
    # mouse.moveTo(338 - 20 + 40 * x, 310 - 20 + 40 * y)
    # mouse.rightClick()

    x = str(int(x))
    y = str(int(y))
    cell = x + "_" + y

    element = driver.find_element_by_id(cell)
    actionChains.context_click(element).perform()


def captureField():
    print("Capturing field...")
    # im = ImageGrab.grab(bbox=(338, 310, 338 + 40 * 30, 310 + 40 * 16))
    # im.show()
    # im_array = np.array(im)

    field = np.zeros([16, 30])

    for i in range(16):
        for j in range(30):
            cell = str(i) + "_" + str(j)
            element = driver.find_element_by_id(cell)
            cellStatus = element.get_attribute("class")

            if cellStatus == "square blank":
                # print(f"{i} , {j} : blank")
                field[i-1, j-1] = -10
            elif cellStatus == "square open0":
                # print(f"{i} , {j} : empty")
                field[i-1, j-1] = 0
            else:
                # print(f"{i} , {j} : {cellStatus[-1]}")
                field[i-1, j-1] = int(cellStatus[-1])

    # for i in range(30):
    #     for j in range(16):
    #         # print(j, i, " | ", im_array[j * 40 + 20, i * 40 + 20])
    #
    #         if (im_array[j * 40 + 20, i * 40 + 20] == [189, 189, 189]).all():
    #             if (im_array[j * 40 + 2, i * 40 + 20] == [255, 255, 255]).all():
    #                 field[j, i] = -10
    #             else:
    #                 field[j, i] = 0
    #         elif (im_array[j * 40 + 20, i * 40 + 20] == [0, 0, 255]).all():
    #             field[j, i] = 1
    #         elif (im_array[j * 40 + 20, i * 40 + 20] == [2, 124, 2]).all():
    #             field[j, i] = 2
    #         elif (im_array[j * 40 + 20, i * 40 + 20] == [255, 0, 0]).all():
    #             field[j, i] = 3
    #         elif (im_array[j * 40 + 20, i * 40 + 20] == [255, 255, 255]).all():
    #             field[j, i] = 4

    return field

def rule_one(field):
    """Rule One is the simplest of Minesweeper rules.
       Put simply, if the number on the cell in question
       is equivalent to the number of empty cells it
       touches, all adjacent, clickable, empty cells are mines"""

    numbered_cells = np.argwhere(field > 0)

    added_flags = np.empty((0, 2))

    for index in numbered_cells:
        empty_cells_count = 0
        associated_empty_cells = np.empty((0,2))

        if field[index[0] - 1, index[1] + 1] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [1, -1]))
        if field[index[0] - 0, index[1] + 1] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [1, 0]))
        if field[index[0] + 1, index[1] + 1] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [1, 1]))
        if field[index[0] - 1, index[1] + 0] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [0, -1]))
        if field[index[0] + 1, index[1] + 0] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [0, 1]))
        if field[index[0] - 1, index[1] - 1] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [-1, -1]))
        if field[index[0] + 0, index[1] - 1] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [-1, 0]))
        if field[index[0] + 1, index[1] - 1] == -10:
            empty_cells_count += 1
            associated_empty_cells = np.vstack((associated_empty_cells, [-1, 1]))

        # print(field[index[0], index[1]])

        if empty_cells_count == field[index[0], index[1]]:
            for i in range(len(associated_empty_cells)):

                # print("Rule 1 Index:", "Y:", index[0] + 1, " X:", index[1] + 1)
                # print("    Relative: Y:", associated_empty_cells[i, 1], "   X:", associated_empty_cells[i, 0])

                absolute_cell = np.array([index[1] + 1 + associated_empty_cells[i, 0], index[0] + 1 + associated_empty_cells[i, 1]])

                # print("    Absolute: ", absolute_cell[0], absolute_cell[1])

                if absolute_cell.tolist() not in added_flags.tolist():
                    flagCell(absolute_cell[1], absolute_cell[0])
                    added_flags = np.vstack((added_flags, absolute_cell))
                    field[int(absolute_cell[0] - 1), int(absolute_cell[1] - 1)] = -1
                    # print("")

    return field


def click_known_safes(field):
    numbered_cells = np.argwhere(field > 0)

    added_flags = np.empty((0, 2))

    for index in numbered_cells:
        flagged_cells_count = 0
        associated_flagged_cells = np.empty((0, 2))

        if field[index[0] - 1, index[1] + 1] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [1, -1]))
        if field[index[0] - 0, index[1] + 1] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [1, 0]))
        if field[index[0] + 1, index[1] + 1] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [1, 1]))
        if field[index[0] - 1, index[1] + 0] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [0, -1]))
        if field[index[0] + 1, index[1] + 0] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [0, 1]))
        if field[index[0] - 1, index[1] - 1] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [-1, -1]))
        if field[index[0] + 0, index[1] - 1] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [-1, 0]))
        if field[index[0] + 1, index[1] - 1] == -1:
            flagged_cells_count += 1
            associated_empty_cells = np.vstack((associated_flagged_cells, [-1, 1]))


        if flagged_cells_count == field[index[0], index[1]]:

            # -1 1
            if field[index[0] - 1, index[1] + 1] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + -1, index[0] + 1 + 1])
                clickCell(absolute_cell[0], absolute_cell[1])
            # 0 1
            if field[index[0] - 0, index[1] + 1] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + 0, index[0] + 1 + 1])
                clickCell(absolute_cell[0], absolute_cell[1])
            # 1 1
            if field[index[0] + 1, index[1] + 1] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + 1, index[0] + 1 + 1])
                clickCell(absolute_cell[0], absolute_cell[1])
            # -1 0
            if field[index[0] - 1, index[1] + 0] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + -1, index[0] + 1 + 0])
                clickCell(absolute_cell[0], absolute_cell[1])
            # 1 0
            if field[index[0] + 1, index[1] + 0] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + 1, index[0] + 1 + 0])
                clickCell(absolute_cell[0], absolute_cell[1])
            # -1 -1
            if field[index[0] - 1, index[1] - 1] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + -1, index[0] + 1 - 1])
                clickCell(absolute_cell[0], absolute_cell[1])
            # 0 1
            if field[index[0] + 0, index[1] - 1] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + 0, index[0] + 1 + 1])
                clickCell(absolute_cell[0], absolute_cell[1])
            # 1 -1
            if field[index[0] + 1, index[1] - 1] == -10:
                absolute_cell = np.array(
                    [index[1] + 1 + 1, index[0] + 1 - 1])
                clickCell(absolute_cell[0], absolute_cell[1])



if __name__ == "__main__":

    driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver = webdriver.Chrome(executable_path=r'C:\Users\1joeh\Documents\chromedriver.exe')
    actionChains = ActionChains(driver)
    # r"C:\Users\1joeh\.wdm\drivers\chromedriver\win32\84.0.4147.30\chromedriver.exe"
    # driver = webdriver.Chrome()
    driver.get('http://minesweeperonline.com/#200')
    driver.maximize_window()

    # TOP LEFT 318, 185
    # BOTTOM RIGHT 1562, 974
    # CELLS 39x39 px
    # PLAYING FIELD 30 x 16 CELLS
    # CELL TOP LEFT 338, 310

    t1 = time.time()
    clickCell(1, 1)
    t2 = time.time()
    print(f"Cell click time: {t2-t1}")

    t1 = time.time()
    field = captureField()
    t2 = time.time()
    print(f"Capture field time: {t2 - t1}")


    field = rule_one(field)

    click_known_safes(field)

    # field = captureField()



    input("Finsihed?")


    driver.quit()