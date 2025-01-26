from colorama import Back, Fore, Style

from kbhit import KBHit
from utils import clamp

import os, shutil
import sys
import time

NO_SELECTED_FILE = ValueError("No selected file found")

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

        self.prev_c = None

        self.motion_mult = 1

        self.input_buffer = ""

        self.waiting_for_key = False

        self.update()

        self.main_loop()

    def update(self):
        clean() 

        self.files = os.listdir(self.working_dir)
        self.selected_file = None
        
        for i, file in enumerate(self.files):
            if i == self.selected_index:
                abs_file = os.path.join(self.working_dir, file)

                self.selected_file = abs_file 
                self.is_dir_selected = os.path.isdir(abs_file)

                print(Back.WHITE + file + Style.RESET_ALL)
                continue
            
            print(file)
    
    def move_focus_down(self):
        self.selected_index = clamp(self.selected_index + self.motion_mult, 0, len(self.files) - 1) 
        self.update()

    def move_focus_up(self):
        self.selected_index = clamp(self.selected_index - self.motion_mult, 0, len(self.files) - 1) 
        self.update()

    def delete_selected(self):
        if not self.selected_file:
            raise NO_SELECTED_FILE 

        if self.is_dir_selected:
            shutil.rmtree(self.selected_file)
        else:
            os.remove(self.selected_file)

        self.update()

    def open_selected(self):
        if not self.selected_file:
            raise NO_SELECTED_FILE

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
        for i in range(abs(self.motion_mult)):
            self.working_dir = os.path.dirname(self.working_dir)

        self.selected_index = 0
        self.update()

    def single_input(self, c: str) -> bool:
        match c:
            case " ":
                if not self.selected_file:
                    return False

                self.open_selected()
            case "-":
                self.dir_up()           
            case _:
                return False

        self.motion_mult = 1 
        return True
    
    def operator_input(self, o: str):
        match o:
            case "d":
                if not self.selected_file:
                    return False
                
                self.delete_selected()
            case _:
                self.move_focus_down()

        
        self.motion_mult = 1

    def buffer_input(self) -> bool:
        ib = self.input_buffer

        operators = ("dd")
        motions = ("gg", "j", "k", "G")
        found_buffer = False

        for motion in motions:
            if not ib.endswith(motion):
                continue
            
            found_buffer = True

            match motion:
                case "gg":
                    self.motion_mult = 0 - self.selected_index
                case "G":
                    self.motion_mult = len(self.files) - 1 - self.selected_index
                case "j":
                    pass
                case "k":
                    self.motion_mult *= -1

            operator = ib.removesuffix(motion)

            if len(operator) != 0:
                operator = ib.removesuffix(motion)[-1]

            self.operator_input(operator)

            break

        if not found_buffer:
            for operator in operators:
                if not ib.endswith(operator):
                    continue

                found_buffer = True

                match operator:
                    case "dd":
                        self.delete_selected()

                break

        return found_buffer

    def input(self, c: str): 
        found_single = self.single_input(c)
        
        if found_single:
            self.input_buffer = ""
            return

        self.input_buffer += c

        found_buffer = self.buffer_input()

        if found_buffer:
            self.input_buffer = ""
            return

    def main_loop(self):
        while True:
            if not self.kb.kbhit():
                continue

            c = self.kb.getch()
            c_ord = ord(c)

            if c == "q":
                clean()
                break

            if c.isdigit():
                if not self.prev_c.isdigit():
                    self.motion_mult *= int(c)
                else:
                    self.motion_mult = self.motion_mult * 10 + int(c)
            else:
                self.input(c)
            
            self.prev_c = c
                   
        self.kb.set_normal_term()

if __name__ == "__main__":
    explorer = Explorer() 
