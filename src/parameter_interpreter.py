#   
#   Paramter Interpreter
#   
#   v 1.1.0 by Mika Schächinger 01.07.2023
#           No splitting between brackets           
#           multi_arguments
#
#           v1.0.3 Removed debug print
#       
#   

import sys


def split_string_at_indexes(string, indexes):
    substrings = []
    previous_index = 0

    for index in indexes:
        substrings.append(string[previous_index:index])
        previous_index = index + 1

    substrings.append(string[previous_index:])

    return substrings

def indexExists(list, index):
    try:
        list[index]
        return True
    except IndexError:
        return False

def toFloat(input):  
    try:
        inputFloat = float(input)
        return inputFloat
    except ValueError:
        return None

def toInt(input) -> bool:
    try:
        value = toFloat(input)
        if value is None:
            return None
        inputInt = int(value)
        return inputInt
    except ValueError:
        return None


class ParameterException(Exception):
    pass

class Parameter:
    args = []
    __value = None
    __flag = False
    needsValue = False
    __name = None
    helpText = ""
    __expectType = None
    multi_arguments: bool=False

    #
    #   multi_arguments: only, when needsValue=True and args=None
    #                    single arguments will be add together to one
    #


    def __init__(self, name: str, args=None, needsValue=False, startVal=None, helpText: str = None, expectType=None, multi_arguments: bool=False):
        if (args is not None) and (type(args) is not list):
            raise ValueError(f'args {type(args)} was not of type "list"')
        if type(needsValue) is not bool:
            raise ValueError(f'needsValue {type(needsValue)} was not of type "bool"')

        self.__name = name
        if args is not None:
            self.args = args
            self.needsValue = needsValue
        else:
            self.needsValue = True
        self.__expectType = expectType
        if (expectType is not None) and (startVal is not None):
            if type(startVal) != expectType:
                raise ValueError(f'startValue was type {type(startVal)}, but expected was {expectType} because of argument "expectType"')
        self.__value = startVal
        if helpText is not None:
            self.helpText = helpText

        self.multi_arguments = multi_arguments



    def setValue(self, value):
        orginal_value = value
        if self.__expectType is not None:
            if type(value) != self.__expectType:
                if self.__expectType == float:
                    value = toFloat(value)
                elif self.__expectType == int:
                    value = toInt(value)

                if value is None:
                    raise ParameterException(f'The value was of type {type(orginal_value)}, but {self.__expectType} was expected. Casting input "{orginal_value}" to {self.__expectType} was not successfull.')

        self.__value = value

    def getValue(self):
        return self.__value

    def setFlag(self):
        self.__flag = True

    def getFlag(self):
        return self.__flag

    def getName(self):
        return self.__name


class ParameterInterpreter:
    __parameterList: list[Parameter] = []
    _combine_until_closing_bracked = False

    def __init__(self, combine_until_closing_bracket: bool=False):
        self._combine_until_closing_bracked = combine_until_closing_bracket

    def addParameter(self, param: Parameter):
        if type(param) is not Parameter:
            raise ValueError(f'param {type(param)} was not of type "Parameter"')

        self.__parameterList.append(param)


    def __getFlagParamsList(self):
        # returns a List of Params, which don't need Values
        paramList = []
        for param in self.__parameterList:
            if not param.needsValue:
                paramList.append(param)
        return paramList
    

    def __modifyArgList(self, argList):
        if len(argList) > 0:    # new if case by Mika S.  14.12.2022
            last_arg = argList[-1]
            if ',' in last_arg:
                # new 01.07.2023 Mika S.
                # split at each ',', which is not in brackets
                split_index_list = [] # list contains indexes with ',', where the string should be splitted
                bracket_counter = 0
                for index, character in enumerate(last_arg):
                    if character == '(':
                        bracket_counter += 1
                    elif character == ')':
                        bracket_counter -= 1
                    if character == ',' and bracket_counter == 0:
                        split_index_list.append(index)

                    if bracket_counter < 0:
                        raise ParameterException(f"Error: There were more closing brackets then opening brackets")

                endArgsList = split_string_at_indexes(last_arg, split_index_list)

                #endArgsList = argList[-1].split(',')   # old
                argList = argList[:-1]
                for arg in endArgsList:
                    if arg != '':
                        argList.append(arg) 
             

        insertDict = {}
        replaceArg = False
        highestKey = 0

        for i, arg in enumerate(argList):

            if arg[0] == '%':
                number = arg[1:]
                if number.isdigit():
                    number = int(number)
                    replaceArg = True
                    if number in insertDict:
                        text = f'There was a duplicated placeholder "%{number}"'
                        raise ParameterException(text)
                    insertDict[number] = i
                    if number < 0:
                        text = f'Placholder {i} ({arg}) Number was interpreted as {number}, but must be greather then zero!'
                        raise ParameterException(text)
                    if number > highestKey:
                        highestKey = number
                else:
                    text = f'Argument {i} ({arg}) is a Placeholder, but has no number'
                    raise ParameterException(text)
        
        if not replaceArg:
            return argList  

        if len(insertDict) != highestKey + 1:   # +1 because: highestKey starts with 0, len with 1
            text = f'The highest replace Number was {highestKey} (starting with 0, there must be {highestKey+1}), but only {len(insertDict)} were detected!\n\t\tDetected %Numbers are {insertDict.keys()}'
            raise ParameterException(text)

        if highestKey > (len(argList)-1)*2:  # -1 because one element is the programm Name; *2 because every replacement needs two ars
            text = f'There are {len(argList)-1} arguments and the highest replace number is {highestKey}. Each replace Argument needs a Argument at the End.'
            raise ParameterException(text)

        splitIndex = len(argList)-(highestKey+1)
        insertList = argList[splitIndex:].copy()
        argList = argList[:splitIndex]
        

        try:
            for argIndex, insertIndex in insertDict.items():
                argList[insertIndex] = insertList[argIndex]
        except IndexError:
            text = f'IndexError: argList[insertIndex] = insertList[argIndex]\n\tThere were missing Arguments at the end ({highestKey+1} are required, last {highestKey+1} are: {insertList})'
            raise ParameterException(text)
        return argList


    def combine_until_closing_bracket(self, arg_list: list[str]) ->list[str]:
        bracket_counter = 0
        combine_index: list[tuple[int, int]] = []

        for index in range(len(arg_list)):
            string = arg_list[index]

            if bracket_counter > 0:
                combine_index.append((index-1, index))

            if not '(' in string:
                continue
            

            for character in string:
                if character == '(':
                    bracket_counter += 1
                elif character == ')':
                    bracket_counter -= 1
                
                if bracket_counter < 0:
                    raise ParameterException(f"Error: There were more closing brackets then opening brackets")
        
        combine_index.reverse()
        for index_tuple in combine_index:
            first, second = index_tuple
            arg_list[first] += arg_list[second]
            del arg_list[second]

        return arg_list

        

    def interpretList(self, argList, firstIsProgramName=True):
        argList = argList.copy()
        if firstIsProgramName:
            argList = argList[1:]

        
        if self._combine_until_closing_bracked:
            argList = self.combine_until_closing_bracket(argList)

        # fisrst interpret all Params, which need no Value
        flagParams = self.__getFlagParamsList()
        copyArgList = argList.copy()
        argList = []
        for arg in copyArgList:
            haveAMatch = False
            for param in flagParams:
                if arg in param.args:
                    param.setFlag()
                    haveAMatch = True
            if not haveAMatch:
                argList.append(arg)
        # Then replace %Placeholder with the Last Elements     
        argList = self.__modifyArgList(argList)    
        # interpret the Params, which need a Value
        copyArgList = argList.copy()
        argList = []

        skipNextArg = False
        for i, arg in enumerate(copyArgList):   # sys.argv
            if skipNextArg:
                skipNextArg = False
                continue
            
            haveAMatch = False

            # Check Parameter which needs Args
            for param in self.__parameterList:         # Parameter
                if arg in param.args:
                    haveAMatch = True
                    #argList.remove(arg)
                    param.setFlag()
                    if param.needsValue:
                        if not indexExists(copyArgList, i+1):
                            raise ParameterException(f'Parameter "{arg}" needs a following Value, but the List has Ended')
                        param.setValue(copyArgList[i+1])
                        #print(param.getValue(), type(param.getValue()))    # 24.01.2023
                        #argList.remove(copy_argList[i+1])
                        skipNextArg = True
            # Check 
            if not haveAMatch:
                for param in self.__parameterList:
                    if (param.args == []) and ((param.getValue() is None) or param.multi_arguments): # and (param.needsValue)
                        haveAMatch = True

                        if param.multi_arguments:
                            old_value: list|None = param.getValue()
                            if old_value is None:
                                old_value = []
                                param.setValue(old_value)
                            old_value.append(arg)
                        else:
                            param.setValue(arg)
                        param.setFlag()
                        #argList.remove(arg)
                        break                   # by MS 21.12.2022

            if not haveAMatch:
                argList.append(arg)
        
        if len(argList) > 0:
            if len(argList) > 1:
                t = f'Parameter "{argList}" could not be assigned!'
                raise ParameterException(t)
            else:
                t = f'Parameter "{argList[0]}" could not be assigned!'
                raise ParameterException(t)


    


    def getParameterList(self):
        return self.__parameterList.copy()

        

    def showAllFlagsAndValues(self):
        print('+----------- Parameter Flags and Values ------------------------------')
        print('|')
        for param in self.__parameterList:
            output = f'|\t{param.getName()}:   \tflag={param.getFlag()}\tneedsValue={param.needsValue} '
            if param.needsValue:
                output = output + f'\tvalue="{param.getValue()}"'
            print(output)
        print('|')
        print('+----------- End Parameter Flags and Values --------------------------')
        print()





if __name__ == "__main__":

    version = Parameter('version', args=['-V'])
    port = Parameter('port', needsValue=True, expectType=int)
    input = Parameter('input', args=['-I'], needsValue=True)

    port.setValue("5.2 0")

    #pi = ParameterInterpreter()
    #pi.addParameter(version)
    #pi.addParameter(input)
    #pi.addParameter(port)

    #try:
    #    pi.interpretSysArgv(['-V', '-I', '5', '10', '1'])
    #except ParameterException as e:
    #    print(e)
    #    pi.showAllFlagsAndValues()

    
    #print('Finish')

