import colorama
from colorama import Back, Fore, Style

from kbhit import KBHit

import os
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
                print(Back.WHITE + file + Style.RESET_ALL)
                continue
            
            print(file)

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
                        self.selected_index = max(self.selected_index + 1, len(self.files))
                        self.update()
                    case "k":
                        self.selected_index = min(self.selected_index -1, 0)
                        self.update()

                if c == "q":
                    clean()
                    break

        self.kb.set_normal_term()

if __name__ == "__main__":
    explorer = Explorer() 
