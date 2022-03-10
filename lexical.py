# Ektelestike me python3
# Dimitrios Giannakopoulos, 4336, cse84336
# Sotirios Panagiotou, 4456, cse84456

# You can run the lexsyn analyzer using this format: python3 lexsyn.py PathOfCimple.ci

import sys
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

allowedAlphabet = ["+", "-", "*", "/", "<", ">", "=", "<=", ">=", "<>", ":=", ";", ",", ":", "[", "]", "(", ")", "{", "}", ".", "#", "\t", " ", "\n"]

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
        sys.exit()

class LexError(object):
    def __init__(self, lex, message):
        lex.errFound = True
        lex.endFound = True
        print("Lexical error @ line " + str(lex.line-1) + " with message: '" + str(message) + "'")
        sys.exit()

class Lexer(object):
    def __init__(self, stream):
        self.stream = stream
        self.current = None
        self.offset = -1
        self.line = 1
        self.errFound = False
        self.endFound = False
        self.tokenList = []
        self.getChar()

    def checkValidation(self, token):
        token = token.recognized_string

        if token.isnumeric():
            self.checkValidInteger(token)
        else:
            self.getValidToken(token)

    def getValidToken(self, token):
        if len(token) > 30:
            LexError(self, "Error, token length is invalid")

    def checkValidInteger(self, token):
        if int(token) > 4294967295:
            LexError(self, "Error, integer length is invalid")

    def nextToken(self):
        if self.current == None or self.endFound:
            return None

        self.checkWhite()

        if self.current in comment:
            self.getChar()
            while self.current in [" ", "\t"]:
                self.getChar()
            endCommentFound = False
            while self.current != "\n":
                if self.current in comment:
                    endCommentFound = True
                    self.getChar()
                    break
                self.getChar()
            self.checkWhite()
            if not endCommentFound:
                LexError(self, "invalid comment")

        for i in dict.keys():
            if self.current in dict[i]:
                if (self.current in complexCase):
                    checkAssign = False
                    if(self.current == ":"):
                        checkAssign = True
                    temp = self.getChar()
                    if(checkAssign):
                        if self.current != "=":
                            LexError(self, "Assignment not found")
                            checkAssign = False
                    getChar = self.getChar()
                    concat = str(temp) + str(getChar)
                    if (concat in allComplex):
                        if(concat == ":="):
                            i = "assignment"
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

                if self.current.isnumeric():
                    tmp.append(self.current)
                    self.getChar()
                else:
                    if self.current.isalpha():
                        LexError(self, "letter after digit found")
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

        count = 0

        if self.stream[self.offset] not in allowedAlphabet:
            count += 1
        if not self.stream[self.offset].isalpha():
            count += 1
        if not self.stream[self.offset].isnumeric():
            count += 1
        if count == 3:
            LexError(self, " token includes illegal alphabet " + str(self.current))

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
            if self.current.recognized_string == ".":
                self.getPreviousToken()
            if self.current.recognized_string == "}":
                return True
            else:
                Error(self, "Error, block end not found")
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
            if self.current.recognized_string == ",":
                needNextId = True
                self.getToken()
            else:
                needNextId = False
                if self.current.recognized_string != ";":
                    Error(self, "Error, delimiter not found on declaration")
                break

        if(needNextId == True):
            Error(self, "Error, comma delimiter without next id")

        return True

    def subprograms(self):
        while(self.subprogram()):
            self.getToken()

    def subprogram(self):
        if self.current.recognized_string in ["function", "procedure"]:
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
                    else:
                        Error(self, "subprogram ending parenthesis error")
                else:
                    Error(self, "subprogram starting parenthesis error")
            else:
                Error(self, "subprogram ID not found")
        return False

    def formalparlist(self):
        needNextItem = False
        while self.formalparitem():
            needNextItem = False
            self.getToken()
            if self.current.recognized_string == ",":
                needNextItem = True
                self.getToken()
            if self.current.recognized_string == ")":
                break

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
            Error(self, "formalparitem not found")
            return False

        return True

    def statement(self):
        if self.current.recognized_string in ["if", "while", "switchcase", "forcase", "incase", "call", "return", "input", "print"] or self.current.family == "id":
            if self.current.recognized_string == "if":
                self.ifStat()
            elif self.current.recognized_string == "while":
                self.whileStat()
            elif self.current.recognized_string == "switchcase":
                self.switchcaseStat()
            elif self.current.recognized_string == "forcase":
                self.forcaseStat()
                self.getPreviousToken()
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
        while self.statement():
            if self.current.recognized_string in keywords:
                return True
            self.getToken()

            if self.current.recognized_string == ";":
                self.getToken()
            return True
        if self.current.recognized_string == "{":
            self.getToken()
            self.blockstatements()
            if self.current.recognized_string == "}":
                return True
            else:
                Error(self, "no closing bracket found")
                return False
        Error(self, "invalid statements format")
        return False

    def assignStat(self):
        if self.current.family == "id":
            self.getToken()
            if self.current.recognized_string == ":=":
                self.getToken()
                if self.expression():
                    return True
                else:
                    Error(self, "expression not found on assignment")
            else:
                Error(self, ":= not found on assignment")
        else:
            Error(self, "id not found on assignment")
        return False

    def ifStat(self):
        if self.current.recognized_string == "if":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.condition():
                    if self.current.recognized_string == ")":
                        self.getToken()
                        if self.statements():
                            if self.elsepart():
                                return True
                        else:
                            Error(self, "statement not found on ifStat")
                    else:
                        Error(self, "ending parenthesis not found on ifStat")
                else:
                    Error(self, "condition not found on ifStat")
            else:
                Error(self, "starting parenthesis not found on ifStat")
        return False

    def elsepart(self):
        if self.current.recognized_string == "else":
            self.getToken()
            if self.statements():
                return True
            else:
                Error(self, "statement not found on elsePart")
            return False
        return True

    def whileStat(self):
        if self.current.recognized_string == "while":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.condition():
                    if self.current.recognized_string == ")":
                        self.getToken()
                        if self.statements():
                            return True
                        else:
                            Error(self, "statements not found on whileStat")
                    else:
                        Error(self, "closing parenthesis not found on whileStat")
                else:
                    Error(self, "condition not found on whileStat")
            else:
                Error(self, "starting parenthesis not found on whileStat")
        else:
            Error(self, "while not found on whileStat")
        return False

    def switchcaseStat(self):
        if self.current.recognized_string == "switchcase":
            self.getToken()
            while self.current.recognized_string == "case":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if self.condition():
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if self.statements():
                                if(self.current.recognized_string == "default"):
                                    break
                                if self.current.recognized_string != "case":
                                    Error(self, "case not found.")
                                continue
                            else:
                                Error(self, "statements not found in case")
                                return False
                        else:
                            Error(self, "closing parenthesis not found in case")
                            return False
                    else:
                        Error(self, "condition not found in case")
                        return False
                else:
                    Error(self, "starting parenthesis not found in case")
                    return False

            if self.current.recognized_string == "default":
                self.getToken()
                if self.statements():
                    return True
                else:
                    Error(self, "statements not found on default switchcase")
            else:
                Error(self, "default not found on switchcase")
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
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if self.statements():
                                self.getToken()
                                if (self.current.recognized_string == "default"):
                                    break
                                if self.current.recognized_string != "case":
                                    Error(self, "case not found.")
                                continue
                            else:
                                Error(self, "statement not found on forcase")
                                return False
                        else:
                            Error(self, "closing parenthesis not found on forcase")
                            return False
                    else:
                        Error(self, "condition not found on forcase")
                        return False
                else:
                    Error(self, "starting parenthesis not found on forcase")
                    return False
            if self.current.recognized_string == "default":
                self.getToken()
                if self.statements():
                    return True
                else:
                    Error(self, "default statement not found on forcase")
            else:
                Error(self, "default not found on forcase")
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
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if self.statements():
                                continue
                            else:
                                Error(self, "statements not found on incase")
                                return False
                        else:
                            Error(self, "closing parenthesis not found on incase")
                            return False
                    else:
                        Error(self, "condition not found on incase")
                        return False
                else:
                    Error(self, "starting parenthesis not found on incase")
                    return False
            return True
        return False



    def returnStat(self):
        if self.current.recognized_string == "return":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.expression():

                    if self.current.recognized_string == ")":
                        return True
                    else:
                        self.getPreviousToken()
                        if(self.current.recognized_string == ")"):
                            return True
                        self.getToken()
                        Error(self, "closing parenthesis not found on returnStat")
                else:
                    Error(self, "expression not found on returnStat")
            else:
                Error(self, "starting parenthesis not found on returnStat")
        else:
            Error(self, "return not found on returnStat")
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
                        else:
                            Error(self, "closing parenthesis not found on callStat")
                    else:
                        Error(self, "actualparlist not found on callStat")
                else:
                    Error(self, "starting parenthesis not found on callStat")
            else:
                Error(self, "id not found on callStat")
        else:
            Error(self, "call not found on callStat")
        return False

    def printStat(self):
        if self.current.recognized_string == "print":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                if self.expression():
                    self.getPreviousToken()
                    if self.current.recognized_string == ")":
                        return True
                    else:
                        Error(self, "closing parenthesis not found on printStat")
                else:
                    Error(self, "expression not found on printStat")
            else:
                Error(self, "starting parenthesis not found on printStat")
        else:
            Error(self, "print not found on printStat")
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
                    else:
                        Error(self, "closing parenthesis not found on inputStat")
                else:
                    Error(self, "id not found on inputStat")
            else:
                Error(self, "starting parenthesis not found on inputStat")
        else:
            Error(self, "input not found on inputStat")
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
        while self.current.recognized_string in ["in", "inout"]:
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
                else:
                    Error(self, "boolterm not found")
                return False
            return True
        Error(self, "boolterm not found")
        return False

    def boolterm(self):
        if self.boolfactor():
            while self.current.recognized_string == "and":
                self.getToken()
                if self.boolfactor():
                    self.getToken()
                    return True
                else:
                    Error(self, "boolfactor not found")
                return False
            return True
        Error(self, "boolfactor not found")
        return False


    def boolfactor(self):
        if self.current.recognized_string == "not":
            self.getToken()
            if self.current.recognized_string == "[":
                self.getToken()
                if not self.condition():
                    Error(self, "condition not found")
                self.getToken()
                if self.current.recognized_string == "]":
                    return True
            return False
        elif self.current.recognized_string == "[":
            self.getToken()
            if not self.condition():
                Error(self, "condition not found")
            self.getToken()
            if self.current.recognized_string == "]":
                return True
            return False
        elif self.expression():
            if self.current.recognized_string not in REL_OP:
                self.getPreviousToken()
            if self.current.recognized_string in REL_OP:
                self.getToken()
                if self.expression():
                    self.getPreviousToken()
                    return True
            return False
        return False


    def expression(self):
        if self.optionalSign():
            if self.term():
                while self.current.recognized_string in addOperator:
                    self.getToken()
                    if self.term():
                        return True
                    else:
                        Error(self, "term not found")
                    return False
                return True
            else:
                Error(self, "term not found")
        return False

    def term(self):
        while self.factor():
            self.getToken()
            while self.current.recognized_string in mulOperator:
                self.getToken()
                if self.factor():
                    self.getToken()
                    return True
                else:
                    Error(self, "factor not found")
                return False
            return True
        Error(self, "factor not found")
        return False

    def factor(self):
        if self.current.recognized_string.isnumeric():
            self.getToken()
            if not self.current.recognized_string == ")":
                self.getPreviousToken()
            return True
        elif self.current.recognized_string == "(":
            self.getToken()
            self.expression()
            self.getToken()
            if self.current.recognized_string == ")":
                return True
            return False
        elif self.current.family == "id":
            self.getToken()
            if self.idtail():
                return True
            return True
        return False

    def idtail(self):
        if self.current.recognized_string == "(":
            self.getToken()

            if not self.actualparlist():
                Error(self, "actualparlist not found")
            self.getToken()
            while self.current.recognized_string != ")":
                self.getPreviousToken()
            if self.current.recognized_string == ")":
                return True
            Error(self, "closing parenthesis not found")
            return False
        return True

    def optionalSign(self):
        if self.current.recognized_string in addOperator:
            return True
        return True

    def blockstatements(self):
        needNextStatement = False
        while self.current.recognized_string == ";":
            self.getToken()
        while self.statement():
            needNextStatement = False
            if(self.current != ";"):
                self.getToken()
            while self.current.recognized_string == ";":
                self.getToken()
                needNextStatement = True

        if(needNextStatement):
            if self.current.recognized_string != "}":
                Error(self, "Error, no next statement found after delimiter")

    def program(self):
        if self.current.recognized_string == "program":
            self.getToken()
            if self.current.family == "id":
                self.getToken()
                self.block()
                self.getToken()
                if self.current.recognized_string == "." and not self.endFound:
                    self.getToken()
                    if self.endFound:
                        print("The cimple program got parsed successfully")
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
        while token is not None and not lex.endFound:
           # print(token)
            lex.checkValidation(token)
            lex.tokenList.append(token)
            token = lex.nextToken()
        if lex.current == ".":
          #  print(token)
            lex.checkValidation(token)
            lex.tokenList.append(token)

        # Syntax
        if not lex.errFound:
            syntax = Syntax(lex.tokenList)
            token = syntax.getToken()
            sntx = syntax.program()
    else:
        print('Invalid parameters.')
        sys.exit(1)


if __name__ == "__main__":
    f = open(sys.argv[1:][0], "r")

    main(f.read())
