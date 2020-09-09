import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np


class Minesweeper:

    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.actionChains = ActionChains(self.driver)
        self.driver.get('http://minesweeperonline.com/#200')
        self.driver.maximize_window()
        self.relative_coords = np.array( [[-1, -1]
                                         ,[-1,  0]
                                         ,[-1,  1]
                                         ,[ 0, -1]
                                         ,[ 0,  1]
                                         ,[ 1, -1]
                                         ,[ 1,  0]
                                         ,[ 1,  1]])


    def clickCell(self, x, y):
        print(f"Clicked {x}, {y}")

        cell = str(int(x+1)) + "_" + str(int(y+1))

        element = self.driver.find_element_by_id(cell)
        element.click()

    def flagCell(self, x, y):
        print(f"Flagged {x}, {y}")

        cell = str(int(x+1)) + "_" + str(int(y+1))

        element = self.driver.find_element_by_id(cell)
        self.actionChains.context_click(element).perform()

    def captureField(self):
        print("Capturing field...")
        t1 = time.time()
        field = np.zeros([16, 30])

        for i in range(16):
            for j in range(30):
                cell = str(i) + "_" + str(j)
                element = self.driver.find_element_by_id(cell)
                cell_status = element.get_attribute("class")

                if cell_status == "square blank":
                    # print(f"{i} , {j} : blank")
                    field[i - 1, j - 1] = -10
                elif cell_status == "square open0":
                    # print(f"{i} , {j} : empty")
                    field[i - 1, j - 1] = 0
                else:
                    field[i - 1, j - 1] = int(cell_status[-1])

        print(f"Captured field in {round(time.time() - t1,2)} seconds")

        return field

    def id_numbered_cells(self, field):
        return np.argwhere(field > 0)

    def id_blank_cells(self, field):
        return np.argwhere(field == -10)

    def adjacent_values(self, field, coordinate):

        adjacent_values = np.empty((0, 1))

        for coord in self.relative_coords:
            abs_cell = np.array([coord[0] + coordinate[0], coord[1] + coordinate[1]])
            adjacent_values = np.append(adjacent_values, field[abs_cell[0], abs_cell[1]])

        return adjacent_values


    def execute_rule_one(self, field):

        #todo: why dont edge 2s get recognized

        print("Flagging known cells...")

        did_i_flag_a_cell = False

        numbered_cells = self.id_numbered_cells(field)

        for cell in numbered_cells:
            adjacents = self.adjacent_values(field, cell)

            if np.count_nonzero(adjacents == -10) == field[cell[0], cell[1]]:
                pre_cells_to_flag = np.where(adjacents == -10)

                for rel_cell in self.relative_coords[pre_cells_to_flag]:
                    if field[cell[0] + rel_cell[0], cell[1] + rel_cell[1]] != -1:
                        self.flagCell(cell[0] + rel_cell[0], cell[1] + rel_cell[1])
                        field[cell[0] + rel_cell[0], cell[1] + rel_cell[1]] = -1
                        did_i_flag_a_cell = True

        return field, did_i_flag_a_cell

    def click_known_safe_cells(self, field):
        print("Clicking known safe cells...")

        did_i_click_a_cell = False

        numbered_cells = self.id_numbered_cells(field)

        for cell in numbered_cells:
            adjacents = self.adjacent_values(field, cell)

            if np.count_nonzero(adjacents == -1) == field[cell[0], cell[1]]:
                pre_cells_to_click = np.where(adjacents == -10)
                for rel_cell in self.relative_coords[pre_cells_to_click]:
                    if field[cell[0] + rel_cell[0], cell[1] + rel_cell[1]] == -10:
                        self.clickCell(cell[0] + rel_cell[0], cell[1] + rel_cell[1])
                        did_i_click_a_cell = True

        return did_i_click_a_cell


    def guess(self, field):
        print("Guessing...")

        blank_cells = self.id_blank_cells(field)

        random_cell = np.random.randint(0,len(blank_cells))

        print("random cell", blank_cells[random_cell])


        # todo: add smarter guessing...
        # numbered_cells = self.id_numbered_cells(field)
        #
        # for cell in numbered_cells:
        #     if field[cell[0], cell[1]] == 1:
        #         adjacents = self.adjacent_values(field, cell)
        #     else:
        #         continue



    def is_game_alive(self):
        print("Checking game alive status...")

        element = self.driver.find_element_by_id("face")
        face_status = element.get_attribute("class")

        if face_status == "facedead":
            print("Game died")
            return False
        elif face_status == "facesmile":
            print("Game is alive!")
            return True
        elif face_status == "faceooh":
            time.sleep(0.25)
            if face_status == "facedead":
                print("Game died")
                return False
            elif face_status == "facesmile":
                print("Game is alive!")
                return True



if __name__ == "__main__":

    game = Minesweeper()

    game.clickCell(0, 0)

    game_alive = True
    while game_alive:

        field = game.captureField()

        field, did_i_flag_a_cell = game.execute_rule_one(field)

        did_i_click_a_cell = True
        while did_i_click_a_cell:
            did_i_click_a_cell = game.click_known_safe_cells(field)

        game.guess(field)

        game_alive = game.is_game_alive()


    input("Game died")