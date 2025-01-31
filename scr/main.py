from colorama import Back, Fore, Style

from kbhit import KBHit
from utils import clamp

import os, shutil
import sys
import time

NO_SELECTED_FILE = ValueError("No selected file found")

TO_END = 10069993

def move_cursor(direction, steps=1):
    directions = {
        "up": f"\x1b[{steps}A",
        "down": f"\x1b[{steps}B",
        "right": f"\x1b[{steps}C",
        "left": f"\x1b[{steps}D",
    }
    sys.stdout.write(directions[direction])
    sys.stdout.flush()

def move_cursor_to(row: int, col: int):
    sys.stdout.write(f"\x1b[{row};{col}H")
    sys.stdout.flush()

def move_cursor_to_end_of_all_lines():
    sys.stdout.write("\x1b[999B")  # Move cursor to the bottom of the terminal
    sys.stdout.write("\x1b[999C")  # Move cursor to the far right of the last line
    sys.stdout.flush()

def clean():
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")

class Explorer:
    def __init__(self):
        self.kb = KBHit()
        
        self.working_dir = os.getcwd()

        self.selected_index = 0
        self.selected_file = None
        self.is_dir_selected = False

        self.files = []

        self.motion_mult = 1

        self.input_buffer = ""
        self.prev_c = None

        self.is_text_input_enabled = False
        self.is_command_mode = False

        self.current_input = ""

        self.deleted_files = []
        self.created_files = []
        self.renamed_files: list[tuple] = []
        self.created_dirs = []

        self.naming = False
        
        self.update()

        self.main_loop()

    def update(self):
        clean() 

        self.files = os.listdir(self.working_dir)

        for created_file in self.created_files + self.created_dirs:
            if os.path.exists(created_file):
                continue

            if os.path.dirname(created_file) == self.working_dir:
                self.files.append(os.path.basename(created_file))

        for deleted_file in self.deleted_files:
            if not os.path.exists(deleted_file):
                continue
            
            if os.path.dirname(deleted_file) == self.working_dir:
                self.files.remove(os.path.basename(deleted_file))

        for old, new in self.renamed_files:
            if not os.path.exists(old):
                continue

            if os.path.dirname(old) == self.working_dir:
                self.files.remove(os.path.basename(old))
                self.files.append(os.path.basename(new))

        self.selected_file = None
        
        for i, file in enumerate(self.files):
            if i == self.selected_index:
                abs_file = os.path.join(self.working_dir, file)

                self.selected_file = abs_file 
                self.is_dir_selected = os.path.isdir(abs_file)

                print(Back.WHITE + Fore.BLACK + file + Style.RESET_ALL)
                continue
            
            print(file)
        
        if self.is_command_mode:
            print(":", end = "", flush = True)

    def write_changes(self):
        for file in self.deleted_files:
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)

        for file in self.created_files:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    f.write("")

        for dir in self.created_dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)

        for old, new in self.renamed_files:
            os.rename(old, new)

        self.deleted_files = []
        self.created_files = []
        self.renamed_files = []

    def discard_changes(self):
        self.deleted_files = []
        self.created_files = []
        self.renamed_files = []

        self.update()
    
    def move_focus_down(self):
        self.selected_index = clamp(self.selected_index + self.motion_mult, 0, len(self.files) - 1) 
        self.update()

    def move_focus_up(self):
        self.selected_index = clamp(self.selected_index - self.motion_mult, 0, len(self.files) - 1) 
        self.update()

    def delete_selected(self):
        if not self.selected_file:
            raise NO_SELECTED_FILE 

        for i in range(abs(self.motion_mult)):
            self.deleted_files.append(self.selected_file)

            self.update()

    # TODO: make new delete method that can delete from selected to start or to end

    def single_open_selected(self):
        if self.is_dir_selected:
            self.working_dir = self.selected_file
            self.selected_index = 0
        else:
            try:
                os.system("vim " + self.selected_file)
            except:
                os.system("notepad " + self.selected_file)

        self.update()

    def open_selected(self):
        if not self.selected_file:
            raise NO_SELECTED_FILE
        
        times = self.motion_mult
        breaking = False

        if times == TO_END:
            while len(os.listdir()) > 0:
                if not self.is_dir_selected:
                    breaking = True

                self.single_open_selected()
                
                if breaking:
                    break
        else:
            for i in range(abs(times)):
                self.single_open_selected()

    def dir_up(self):
        times = self.motion_mult

        if times == TO_END:
            while self.working_dir != os.path.dirname(self.working_dir):
                self.working_dir = os.path.dirname(self.working_dir)
        else:
            for i in range(abs(times)):
                self.working_dir = os.path.dirname(self.working_dir)

        self.selected_index = 0
        self.update()

    def enable_command_mode(self):
        self.is_command_mode = True
        self.enable_text_input()

        sys.stdout.flush()
        self.update()
        sys.stdout.flush()

    def disable_command_mode(self):
        self.is_command_mode = False
        self.disable_text_input()

        self.update()

    def finish_rename(self):
        new_name = self.current_input

        self.naming = False
        
        self.disable_text_input()

        self.renamed_files.append((self.selected_file, os.path.join(self.working_dir, new_name)))
        
        move_cursor_to_end_of_all_lines()

        self.update()

    def finish_creating(self):
        name = self.current_input

        self.creating = False

        self.disable_text_input()

        if self.creating_dir:
            self.creating_dir = False
            self.created_dirs.append(os.path.join(self.working_dir, name))
        else:
            self.created_files.append(os.path.join(self.working_dir, name))


        self.creating_dir = False

        self.update()

    def single_input(self, c: str) -> bool:
        match c:
            case ":":
                self.enable_command_mode()
            case '\x1b':
                self.disable_command_mode()
            case "\n" | "\r":
                if self.is_command_mode:
                    self.command_input()
                    self.disable_command_mode()

                if self.naming:
                    self.finish_rename()                    
                
                if self.creating:
                    self.finish_creating()
            case _:
                match ord(c):
                    case 27:
                        self.disable_command_mode()
                    case _:
                        return False

        self.motion_mult = 1 
        return True        

    def rename_selected(self):
        if not self.selected_file:
            raise NO_SELECTED_FILE

        move_cursor_to(self.selected_index + 1, 1)
        print(" " * 100, end="", flush=True)
        move_cursor_to(self.selected_index + 1, 1)

        self.naming = True

        self.enable_text_input()

    def create_file(self, isDir:bool = False):
        self.creating = True
        self.creating_dir = isDir

        print("%", end="", flush=True)
        self.enable_text_input()

    def operator_input(self, o: str):
        match o:
            case "-":
                self.dir_up()
            case " ":
                if not self.selected_file:
                    return False
                
                self.open_selected()
            case "d":
                if not self.selected_file:
                    return False
                
                self.delete_selected()
            case "r":
                if not self.selected_file:
                    return False
                
                self.rename_selected()
            case "n":
                self.create_file()
            case "N":
                self.create_file(True)
                
            case _:
                self.move_focus_down()

        
        self.motion_mult = 1

    def buffer_input(self) -> bool:
        ib = self.input_buffer

        operators = ("dd", "--", "  ", "rr", "nn", "NN")
        motions = ("gg", "j", "k", "G", "t")
        found_buffer = False

        for motion in motions:
            if not ib.endswith(motion) or len(ib) < len(motion):
                continue
            
            found_buffer = True

            operator = ib.removesuffix(motion)

            if len(operator) != 0:
                operator = ib.removesuffix(motion)[-1]

            match motion:
                case "gg":
                    self.motion_mult = 0 - self.selected_index
                case "G":
                    self.motion_mult = len(self.files) - 1 - self.selected_index

                    if operator == "d":
                        self.motion_mult += 1
                case "j":
                    pass
                case "k":
                    self.motion_mult *= -1
                case "t":
                    self.motion_mult = TO_END

            self.operator_input(operator)

            break

        if not found_buffer:
            for operator in operators:
                if not ib.endswith(operator) or len(ib) < len(operator):
                    continue

                found_buffer = True

                match operator:
                    case "dd":
                        self.operator_input("d")
                    case "--":
                        self.operator_input("-")
                    case "  ":
                        self.operator_input(" ")
                    case "rr":
                        self.operator_input("r")
                    case "nn":
                        self.operator_input("n")
                    case "NN":
                        self.operator_input("N")

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

    def command_input(self):
        match self.current_input:
            case "w":
                self.write_changes()
            case "d":
                self.discard_changes()

        self.current_input = ""

    def enable_text_input(self):
        self.is_text_input_enabled = True

    def disable_text_input(self):
        self.is_text_input_enabled = False

        self.current_input = ""

    def main_loop(self):
        while True:
            c = self.kb.getch()

            if c:
                c_ord = ord(c)
            else:
                continue

            if c == "q":
                clean()
                break

            if self.is_text_input_enabled:
                if c == "\x08" or c == "\x7f":  # Handle backspace (both \x08 and \x7f are backspace keys)
                    if self.current_input:  # Only delete if there's text in the buffer
                        # Remove the last character from the command buffer
                        self.current_input = self.current_input[:-1]

                        # Move the cursor back and overwrite with space (erase character)
                        sys.stdout.write("\x1b[D \x1b[D")
                        sys.stdout.flush()

                    continue

                if c and c != "\n":
                    print(c, end = "", flush = True)

                if c and c.isalnum():
                    self.current_input += c

                match c:
                    case 67:
                        pass
                        #move_cursor("right")
                    case 68:
                        pass
                        #move_cursor("left")                
                   
                    case "\r" | "\n" | "\x1b":
                        next_char = self.kb.getch()  # Store the next character in a variable
                        
                        if next_char == "[":
                            print("[", end="", flush=True)
                            continue
                        else:
                            self.input(c)  # The original 'c' is passed to input()



                continue
             
            if c.isdigit():
                if not self.prev_c.isdigit():
                    self.motion_mult *= int(c)
                else:
                    self.motion_mult = self.motion_mult * 10 + int(c)
            else:
                try:
                    self.input(c)
                except:
                    pass
            
            self.prev_c = c
                   
        self.kb.set_normal_term()

if __name__ == "__main__":
    explorer = Explorer() 
