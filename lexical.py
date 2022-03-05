import sys
from collections import Counter
import re

keywords = ['program', 'declare', 'if', 'else', 'while', 'switchcase', 'forcase', 'incase', 'case', 'default', 'not',
            'and', 'or', 'function', 'procedure', 'call', 'return', 'in', 'inout', 'input', 'print']

family = [
    'keywords', 'addOperator', 'mulOperator', 'relOperator', 'delimiter', 'group'
]

alphanumeric = "[a-zA-Z_][a-zA-Z0-9_]*"
number = "^[0-9]+$"
addOperator = ["+", "-"]
mulOperator = ["*", "/"]
relOperator = ["=", "<", ">"]
delimiter = [";", ",", ":", "."]
group = ["[", "]", "(", ")", "{", "}"]
comment = ["#"]
REL_OP = ["=", "<", ">", "<=", ">=", "<>"]

values = [keywords, addOperator, mulOperator, relOperator, delimiter, group]

dict = {}
counter = 0
for i in family:
    dict[i] = values[counter]
    counter += 1
all = [item for sublist in dict.values() for item in sublist]

complexCase = ["<", ">", ":"]

complex = ['groupComplex', 'set']
groupComplex = ["<>", "<=", ">="]
set = [":="]

values = [groupComplex, set]
dictComplex = {}
counter = 0
for i in complex:
    dictComplex[i] = values[counter]
    counter += 1
allComplex = [item for sublist in dictComplex.values() for item in sublist]


class Token(object):
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__(self):
        return '{0}\tfamily:"{1}", line: {2}'.format(self.recognized_string, self.family, self.line_number)

class Error(object):
    def __init__(self, syntax, message):
        syntax.endFound = True
        print("Syntax error @ line " + str(syntax.current.line_number) + " with message: '" + str(message) + "'")


class Lexer(object):
    def __init__(self, stream):
        self.stream = stream
        self.current = None
        self.offset = -1
        self.line = 1
        self.endFound = False
        self.tokenList = []
        self.getChar()

    def nextToken(self):
        if self.current == None or self.endFound:
            return None

        self.checkWhite()

        if self.current in comment:
            self.getChar()
            getChar = self.getChar()
            endCommentFound = False
            while getChar != "\n":
                if getChar in comment:
                    endCommentFound = True
                    self.getChar()
                    break
                getChar = self.getChar()
            self.line += 1
            if not endCommentFound:
                print("ERROR, COMMENT SYNTAX INVALID")

        for i in dict.keys():
            if self.current in dict[i]:
                if (self.current in complexCase):
                    temp = self.getChar()
                    getChar = self.getChar()
                    concat = str(temp) + str(getChar)
                    if (concat in allComplex):
                        return Token(concat, i, self.line)
                    else:
                        self.getPreviousChar()
                        return Token(temp, i, self.line)
                if(self.current == "."):
                    self.endFound = True
                    return Token(self.current, i, self.line)
                if(self.current == "}"):
                    getChar = self.getChar()
                    if getChar == None:
                        self.endFound = True
                        return Token(self.current, i, self.line)
                    else:
                        self.getPreviousChar()
                return Token(self.getChar(), i, self.line)

        if self.current.isnumeric():
            tmp = []
            while (self.current != " " and self.current != "\n" and self.current not in delimiter):
                getChar = self.getChar()

                if getChar.isnumeric():
                    tmp.append(getChar)
                else:
                    self.getPreviousChar()
                    break
            num = ''.join(tmp)
            if (self.checkRegex(number, num)):

                return Token(num, "number", self.line)

        if self.current.isalpha():
            tmp = []
            while (self.current != " " and self.current != "\n"):
                getChar = self.getChar()
                if (getChar not in all):
                    tmp.append(getChar)
                else:
                    self.getPreviousChar()
                    break
            word = ''.join(tmp)

            if (self.checkRegex(alphanumeric, word)):
                found = "id"
                for i in dict.keys():
                    if word in dict[i]:
                        found = i
                return Token(word, found, self.line)

    def checkRegex(self, regex, input):
        pattern = re.compile(regex)
        matches = re.match(pattern, input)

        if matches:
            return True

        return False

    def checkWhite(self):
        while self.current == " " or self.current == '\t':
            self.getChar()

        while self.current == "\n":
            self.line += 1
            self.getChar()
            self.checkWhite()

    def getChar(self):
        if self.offset + 1 >= len(self.stream):
            return None

        result = self.stream[self.offset]
        self.offset += 1
        self.current = self.stream[self.offset]

        return result

    def getPreviousChar(self):
        if self.offset - 1 < 0:
            return None

        result = self.stream[self.offset]
        self.offset -= 1
        self.current = self.stream[self.offset]

        return result

class Syntax(object):
    def __init__(self, stream):
        self.stream = stream
        self.current = None
        self.offset = -2
        self.endFound = False
        self.getToken()

    def checkSyntax(self):
        if self.offset + 1 == len(self.stream) or self.endFound:
            return False

        if self.offset == 0 and self.current.recognized_string != "program":
            Error(self, "Den evales program:(")
            self.endFound = True
            return False
        self.program()

        return True

    def getToken(self):
        if self.offset + 2 > len(self.stream):
            self.endFound = True
            return None

        self.offset += 1
        result = self.stream[self.offset]
        self.current = self.stream[self.offset]

        return result

    def getPreviousToken(self):
        if self.offset - 1 < 0:
            self.endFound = True
            return None

        self.offset -= 1
        result = self.stream[self.offset]
        self.current = self.stream[self.offset]

        return result

    def block(self):
        if self.current.recognized_string == "{":
            self.getToken()
            self.declarations()
            self.subprograms()
            self.blockstatements()
            if self.current.recognized_string == "}":
                return True
        else:
            Error(self, "Error, block start not found")
        return False

    def declarations(self):
        while self.current.recognized_string == "declare":
            self.getToken()

            self.varlist()
            if self.current.recognized_string != ";":
                Error(self, "Error, end delimiter not found")
            self.getToken()

    def varlist(self):
        needNextId = False
        while self.current.family == "id":
            needNextId = False
            self.getToken()
            if self.current.recognized_string in [",", ";"]:
                if self.current.recognized_string == ",":
                    needNextId = True
                    self.getToken()
            else:
                needNextId = False
                Error(self, "Error, delimiter not found on declaration")
                break

        if(needNextId == True):
            Error(self, "Error, comma delimiter without next id")

        return True

    def subprograms(self):
        while(self.subprogram()):
            pass

    def subprogram(self):
        while self.current.recognized_string in ["function", "procedure"]:
            self.getToken()
            if self.current.family == "id":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    self.formalparlist()
                    if self.current.recognized_string == ")":
                        self.getToken()
                        self.block()
                        return True
        return False

    def formalparlist(self):
        needNextItem = False
        while self.formalparitem():
            needNextItem = False
            self.getToken()
            if self.current.recognized_string == ",":
                needNextItem = True
                self.getToken()

        if (needNextItem == True):
            Error(self, "Error, comma delimiter without next item")

        return True

    def formalparitem(self):
        if self.current.recognized_string in ["in", "inout"]:
            self.getToken()
            if self.current.family != "id":
                Error(self, "error, id not found in formalparitem")
                return False
        else:
            return False

        return True

    def statement(self):
        if self.current.recognized_string in ["if", "while", "switchcase", "forcase", "incase", "call", "return", "input", "print"] or self.current.family == "id":
            if self.current.recognized_string == "if":
                self.ifStat()
            elif self.current.recognized_string == "while":
                self.whileStat()
            elif self.current.recognized_string == "switch":
                self.switchcaseStat()
            elif self.current.recognized_string == "forcase":
                self.forcaseStat()
            elif self.current.recognized_string == "incase":
                self.incaseStat()
            elif self.current.recognized_string == "call":
                self.callStat()
            elif self.current.recognized_string == "return":
                self.returnStat()
            elif self.current.recognized_string == "input":
                self.inputStat()
            elif self.current.recognized_string == "print":
                self.printStat()
            else:
                self.assignStat()

            return True
        return False

    def statements(self):
        if self.statement():
            self.getToken()
            if self.current.recognized_string == ";":
                return True
        elif self.current.recognized_string == "{":
            self.getToken()
            self.blockstatements()
            if self.current.recognized_string == "}":
                return True
        return False

    # def assignStat(self):
    #     if self.current.family == "id":
    #         self.getToken()
    #         if self.current.recognized_string == ":":
    #             self.getToken()
    #             if self.current.recognized_string == "=":
    #                 pass ### TODO
    #             else:
    #                 self.getPreviousToken()
    #         else:
    #             self.getPreviousToken()
    #     else:
    #         self.getPreviousToken()
    #         return False

    def assignStat(self):
        if self.current.family == "id":
            self.getToken()
            if self.current.recognized_string == ":=":
                self.getToken()
                if self.expression():
                    return True
        return False

    def ifStat(self):
        if self.current.recognized_string == "if":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.condition():
                    self.getToken()
                    if self.current.recognized_string == ")":
                        self.getToken()
                        if self.statements():
                            self.getToken()
                            if self.elsepart():
                                return True
        return False

    def elsepart(self):
        if self.current.recognized_string == "else":
            self.getToken()
            if self.statements():
                return True
            return False
        return True

    def whileStat(self):
        if self.current.recognized_string == "while":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.condition():
                    self.getPreviousToken()
                    if self.current.recognized_string == ")":
                        self.getToken()
                        if self.statements():
                            return True
        return False

    def switchcaseStat(self):
        if self.current.recognized_string == "switchcase":
            self.getToken()
            while self.current.recognized_string == "case":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if self.condition():
                        self.getToken()
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if self.statements():
                                continue
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            if self.current.recognized_string == "default":
                self.getToken()
                if self.statements():
                    return True
            return False
        return False

    def forcaseStat(self):
        if self.current.recognized_string == "forcase":
            self.getToken()
            while self.current.recognized_string == "case":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if self.condition():
                        self.getToken()
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if self.statements():
                                continue
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            if self.current.recognized_string == "default":
                self.getToken()
                if self.statements():
                    return True
            return False
        return False

    def incaseStat(self):
        if self.current.recognized_string == "incase":
            self.getToken()
            while self.current.recognized_string == "case":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if self.condition():
                        self.getToken()
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if self.statements():
                                continue
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            return True
        return False



    def returnStat(self):
        if self.current.recognized_string == "return":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.expression():
                    self.getToken()

                    if self.current.recognized_string == ")":
                        return True
        return False

    def callStat(self):
        if self.current.recognized_string == "call":
            self.getToken()
            if self.current.family == "id":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if self.actualparlist():
                        self.getToken()
                        if self.current.recognized_string == ")":
                            return True
        return False

    def printStat(self):
        if self.current.recognized_string == "print":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.expression():
                    self.getToken()
                    if self.current.recognized_string == ")":
                        return True
        return False

    def inputStat(self):
        if self.current.recognized_string == "input":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.current.family == "id":
                    self.getToken()
                    if self.current.recognized_string == ")":
                        return True
        return False

    def actualparlist(self):
        needNextItem = False
        while self.actualparitem():
            needNextItem = False
            self.getToken()
            if self.current.recognized_string == ",":
                needNextItem = True
                self.getToken()

        if (needNextItem == True):
            Error(self, "Error, comma delimiter without next item")

        return True

    def actualparitem(self):
        if self.current.recognized_string in ["in", "inout"]:
            if self.current.recognized_string == "in":
                self.getToken()
                if not self.expression():
                    Error(self, "error, expression not found in actualparitem")
                    return False
            else:
                if self.current.family != "id":
                    Error(self, "error, id not found in actualparitem")
                    return False
        else:
            return False

        return True

    def condition(self):
        if self.boolterm():
          #  self.getToken()
            while self.current.recognized_string == "or":
                self.getToken()
                if self.boolterm():
                    self.getToken()
                    return True
                return False
            return True
        return False

    def boolterm(self):
        if self.boolfactor():
        #    self.getToken()
            while self.current.recognized_string == "and":
                self.getToken()
                if self.boolfactor():
                    self.getToken()
                    return True
                return False
            return True
        return False


    def boolfactor(self):
        if self.current.recognized_string == "not":
            self.getToken()
            if self.current.recognized_string == "[":
                self.getToken()
                self.condition()
                self.getToken()
                if self.current.recognized_string == "]":
                    return True
            return False
        elif self.current.recognized_string == "[":
            self.getToken()
            self.condition()
            self.getToken()
            if self.current.recognized_string == "]":
                return True
            return False
        elif self.expression():
            self.getPreviousToken()
            if self.current.recognized_string in REL_OP:
                self.getToken()
                if self.expression():
                    return True
            return False
        return False


    def expression(self):
        if self.optionalSign():
            if self.term():
                while self.current.recognized_string in addOperator:
                    self.getToken()
                    if self.term():
                      #  self.getToken()
                        return True
                    return False
                return True
        return False

    def term(self):
        if self.factor():
            self.getToken()
            while self.current.recognized_string in mulOperator:
                self.getToken()
                if self.factor():
                    self.getToken()
                    return True
                return False
            return True
        return False

    def factor(self):
        if self.current.recognized_string.isnumeric():
            return True
        elif self.current.recognized_string == "(":
            self.getToken()
            self.expression()
            if self.current.recognized_string == ")":
                return True
            return False
        elif self.current.family == "id":
            self.getToken()
            if self.idtail():
                return True
            return False
        return False



    def idtail(self):
        if self.current.recognized_string == "(":
            self.getToken()
            self.actualparlist()
            if self.current.recognized_string == ")":
                return True
            return False
        return True

    def optionalSign(self):
        if self.current.recognized_string in addOperator:
            return True
        return True

    def blockstatements(self):
        needNextStatement = False
        while self.statement():
            needNextStatement = False
            if(self.current != ";"):
                self.getToken()
            if self.current.recognized_string == ";":
                self.getToken()
                needNextStatement = True

        if(needNextStatement):
            Error(self, "Error, no next statement found after delimiter")

    def program(self):
        if self.current.recognized_string == "program":
            self.getToken()
            if self.current.family == "id":
                self.getToken()
                self.block()
                self.getToken()
                if self.current.recognized_string == ".":
                    self.getToken()
                    if self.endFound:
                        print("PARSED GGEZ")
                else:
                    Error(self, "ERROR, ending character not found")
            else:
                Error(self, "ERROR, id not found after program")
        else:
            Error(self, "ERROR, program not found")

def main(argv):
    form = argv

    if form is not None:
        lex = Lexer(form)
        token = lex.nextToken()
        while token is not None:
            lex.tokenList.append(token)
         #   print(token)
            token = lex.nextToken()

        # Syntax
        syntax = Syntax(lex.tokenList)
        token = syntax.getToken()
        sntx = syntax.checkSyntax()
    else:
        print('Invalid parameters.')
        sys.exit(1)


if __name__ == "__main__":
    f = open(sys.argv[1:][0], "r")

    main(f.read())
