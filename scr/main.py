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
       
        self.update()

        self.main_loop()

    def update(self):
        clean()        

        for file in os.listdir():
            print(file)

    def main_loop(self):
        while True:
            if self.kb.kbhit():
                c = self.kb.getch()
                c_ord = ord(c)

                if c == "q":
                    clean()
                    break

        self.kb.set_normal_term()

if __name__ == "__main__":
    explorer = Explorer() 
