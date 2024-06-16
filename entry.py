from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle, prompt

import curses


class ChoiceScreen:

    def __init__(self):
        self.choice = ""
        self._choices = ['discuss', 'quit', 'remind', 'next', 'next step']

    def run(self):
        self.choice = curses.wrapper(self._userChoice)

    def _drawScreen(self,stdscr,choices,current_row):
        stdscr.clear()
        stdscr.addstr("Please choose an option:\n\n")
        for i, choice in enumerate(choices):
            x = 4
            y = 2 + i
            if i == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, f"> {choice}", curses.A_REVERSE)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, f"  {choice}")
        stdscr.refresh()

    def _userChoice(self,stdscr):
        stdscr.clear()

        current_row = 0

        self._drawScreen(choices=self._choices,current_row=current_row,stdscr=stdscr)

        while True:
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1

            elif key == curses.KEY_DOWN and current_row < len(self._choices) - 1:
                current_row += 1
          
            elif key == curses.KEY_ENTER or key in [10, 13]:
                stdscr.refresh()
                stdscr.getch()
                
                return self._choices[current_row]
            
         
            self._drawScreen(choices=self._choices,current_row=current_row,stdscr=stdscr)


class MainTaskCompleter(Completer):

    tasks = [
        "next",
        "more",
        "discuss",
        "help",
        "quit",
    ]

    task_meta = {
        "next": HTML("Go to the next step."),
        "more": HTML("Explain the task with more details."),
        "discuss": HTML("Discuss with <b>PentestGPT</b>."),
        "help": HTML("Show the help page."),
        "quit": HTML("End the current session."),
    }

    task_details = """
Below are the available tasks:
TODO"""
    def __init__(self,_task = [],_meta = []) -> None:
        super().__init__()
        if _task != [] and _meta != [] and len(_task) == len(_meta):
            self.task_list = _task
            dic = {}
            for i in range(len(_task)):
                dic[_task[i]] = HTML(_meta[i])
            self.meta = dic
        else:
            self.task_list = self.tasks
            self.meta = self.task_meta

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for task in self.task_list:
            if task.startswith(word):
                yield Completion(
                    task,
                    start_position=-len(word),
                    display=task,
                    display_meta=self.meta.get(task),
                )




def mainTaskEntry(text="> ",_task = [],_meta = []):
    """
    Entry point for the task prompt. Auto-complete
    """
    task_completer = MainTaskCompleter(_task,_meta)
    while True:
        result = prompt(text, completer=task_completer)
        if result not in task_completer.task_list:
            print("Tâche invalide. Veuillez réessayer.")
        else:
            return result

if __name__ == "__main__":
     mainTaskEntry()