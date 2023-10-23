#   
#   ConsoleProgram Functions
#   
#   v 1.0.0 by Mika Schächinger 01.12.2022
#   
#   
#   


import sys


class Console:
    error_flag = False
    debug_flag = False
    keepOpen_flag = False

    def errorPrint(self, text: str):
        self.error_flag = True
        print(f'[ERROR] {text}')

    def debugPrint(self, text: str):
        if self.debug_flag:
            print(f'[DEBUG] {text}')

    def closeProgram(self):
        if self.keepOpen_flag or self.error_flag:
            input('Press Enter to continue...')
        sys.exit()