import colorama
from colorama import Back, Fore, Style

from kbhit import KBHit

import os, shutil
import sys
import time

def clean():
    os.system("clear")

class Explorer:
    def __init__(self):
        self.kb = KBHit()
        
        self.selected_index = 0
        self.selected_file = None
        self.is_dir_selected = False
        self.files = []

        self.update()

        self.main_loop()

    def update(self):
        clean() 

        self.files = os.listdir()

        for i, file in enumerate(self.files):
            if i == self.selected_index:
                self.selected_file = file
                print(Back.WHITE + file + Style.RESET_ALL)
                continue
            
            print(file)
    
    def move_focus_down(self):
        self.selected_index = min(self.selected_index + 1, len(self.files) -1)
        self.update()

    def move_focus_up(self):
        self.selected_index = max(self.selected_index - 1, 0)
        self.update()

    def delete_selected(self):
        if self.is_dir_selected:
            shutil.rmtree(self.selected_file)
        else:
            os.remove(self.selected_file)

        self.update()

    def main_loop(self):
        while True:
            if self.kb.kbhit():
                c = self.kb.getch()
                c_ord = ord(c)

                match c:
                    case "q":
                        clean()
                        break
                    case "j":
                        self.move_focus_down()
                    case "k":
                        self.move_focus_up()
                    case "d":
                        self.delete_selected()

                if c == "q":
                    clean()
                    break

        self.kb.set_normal_term()

if __name__ == "__main__":
    explorer = Explorer() 
