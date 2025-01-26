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
        
        self.working_dir = os.getcwd()
        self.selected_index = 0
        self.selected_file = None
        self.is_dir_selected = False
        self.files = []

        self.update()

        self.main_loop()

    def update(self):
        clean() 

        self.files = os.listdir(self.working_dir)

        for i, file in enumerate(self.files):
            if i == self.selected_index:
                abs_file = os.path.join(self.working_dir, file)

                self.selected_file = abs_file 
                self.is_dir_selected = os.path.isdir(abs_file)

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

    def open_selected(self):
        if self.is_dir_selected:
            self.working_dir = self.selected_file
            self.selected_index = 0
        else:
            try:
                os.system("vim " + self.selected_file)
            except:
                os.system("notepad " + self.selected_file)
        
        self.update()

    def dir_up(self):
        self.working_dir = os.path.dirname(self.working_dir)

        self.selected_index = 0
        self.update()
    
    def main_loop(self):
        while True:
            if self.kb.kbhit():
                c = self.kb.getch()
                c_ord = ord(c)
                #print(c, c_ord)

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
                    case " ":
                        self.open_selected()
                    case "-":
                        self.dir_up()

                if c == "q":
                    clean()
                    break

        self.kb.set_normal_term()

if __name__ == "__main__":
    explorer = Explorer() 
