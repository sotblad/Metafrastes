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

allowedAlphabet = ["+", "-", "*", "/", "<", ">", "=", "<=", ">=", "<>", ":=", ";", ",", ":", "[", "]", "(", ")", "{",
                   "}", ".", "#", "\t", " ", "\n"]


idCount = 1
tempCount = 1
quads = []

class Quad(object):
    def __init__(self, operator, operand1, operand2, target):
        global idCount
        self.idCount = idCount
        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2
        self.target = target
        idCount +=1
        quads.append(self)

    def changeTarget(self, label):
        self.target = label
        
    def getFirst(self):
        return self.operator
        
    def getSecond(self):
        return self.operand1
        
    def getThird(self):
        return self.operand2
        
    def getFourth(self):
        return self.target

    def __str__(self):
        return "{4}: {0}, {1}, {2}, {3}".format(self.operator, self.operand1, self.operand2, self.target, self.idCount)


def genQuad(operator, operand1, operand2, operand3):
    return Quad(operator, operand1, operand2, operand3)

def nextQuad():
    return idCount

def newTemp():
    global tempCount
    temp = "T_" + str(tempCount)
    tempCount += 1
    return temp

def emptyList():
    return []

def makeList(label):
    return [label]

def mergeList(list1, list2):
    newList = list1+list2
    return newList

def backpatch(list, label):
    for i in list:
        for j in quads:
            if j.idCount == i:
                j.target = label

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
        print("Lexical error @ line " + str(lex.line - 1) + " with message: '" + str(message) + "'")
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

        while self.current in comment:
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
                    if (self.current == ":"):
                        checkAssign = True
                    temp = self.getChar()
                    if (checkAssign):
                        if self.current != "=":
                            LexError(self, "Assignment not found")
                            checkAssign = False
                    getChar = self.getChar()
                    concat = str(temp) + str(getChar)
                    if (concat in allComplex):
                        if (concat == ":="):
                            i = "assignment"
                        return Token(concat, i, self.line)
                    else:
                        self.getPreviousChar()
                        return Token(temp, i, self.line)
                if (self.current == "."):
                    self.endFound = True
                    return Token(self.current, i, self.line)
                if (self.current == "}"):
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
        if count == 3 and self.stream[self.offset] != "'":
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

    def block(self, flag):
        if self.current.recognized_string == "{":
            self.getToken()
            self.declarations()
            self.subprograms()
            if(flag == 0):
                genQuad("begin_block", programName, "_", "_")
            self.blockstatements()
            if self.current.recognized_string == "}":
                return True
            else:
                if(self.stream[self.offset-1].recognized_string == "}"):
                    return True
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
        ok = 0
        while self.current.family == "id":
            ok = 1
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

        if (needNextId == True):
            Error(self, "Error, comma delimiter without next id")

        if(ok == 1):
            return True

    def subprograms(self):
        while (self.subprogram()):
            if(self.current.recognized_string not in keywords):
                self.getToken()

    def subprogram(self):
        if self.current.recognized_string in ["function", "procedure"]:
            self.getToken()
            blockName = self.current.recognized_string
            genQuad("begin_block", blockName, "_", "_")
            if self.current.family == "id":
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if(self.formalparlist()):
                        if self.current.recognized_string == ")":
                            self.getToken()
                            if(self.block(1)):
                                genQuad("end_block", blockName, "_", "_")
                                return True
                            else:
                                Error(self, "block not found on subprogram")
                        else:
                            Error(self, "subprogram ending parenthesis error")
                    else:
                        Error(self, "subprogram params not found")
                else:
                    Error(self, "subprogram starting parenthesis error")
            else:
                Error(self, "subprogram ID not found")
        return False

    def formalparlist(self):
        needNextItem = False
        ok = 0
        while self.formalparitem():
            ok = 1
            needNextItem = False
            self.getToken()
            if self.current.recognized_string == ",":
                needNextItem = True
                self.getToken()
            if self.current.recognized_string == ")":
                break

        if (needNextItem == True and self.current.recognized_string != ")"):
            Error(self, "Error, comma delimiter without next item")
            return False
        if(self.current.recognized_string == ")"):
            ok = 1
            
        if(ok == 1):
            return True

    def formalparitem(self):
        if self.current.recognized_string in ["in", "inout"]:
            self.getToken()
            if self.current.family == "id":
                return True
            else:
                Error(self, "error, id not found in formalparitem")
                return False
        else:
            return False
            
    def statements(self):
        stat = self.statement()
        if(stat):
            while(stat):
                if(self.offset + 1 < len(self.stream)):
                    if(self.stream[self.offset+1].recognized_string == ";"):
                        self.getToken()
                if self.current.recognized_string == ";":
                    self.getToken()
                    stat = self.statement()
                else:
                    if(self.current.recognized_string == "}"):
                        if(self.stream[self.offset+1].recognized_string == "}"):
                            self.getToken()
                        #self.getToken()
                        return True
                    Error(self, "statement error")
                    return False
            return True
        else:
            if self.current.recognized_string == "{":
                self.getToken()
                self.blockstatements()
                if(self.stream[self.offset-1].recognized_string == "}"):
                    return True
                if self.current.recognized_string == "}":
                    return True
                else:
                    Error(self, "no closing bracket found")
                    return False
                
        Error(self, "invalid statements format")
        return False

    def statement(self):
        ok = 0
        if self.current.recognized_string in ["if", "while", "switchcase", "forcase", "incase", "call", "return",
                                              "input", "print"] or self.current.family == "id":
            ok = 1
            if self.current.recognized_string == "if":
                if(not self.ifStat()):
                    ok = -1
            elif self.current.recognized_string == "while":
                if(not self.whileStat()):
                    ok = -1
            elif self.current.recognized_string == "switchcase":
                if(not self.switchcaseStat()):
                    ok = -1
            elif self.current.recognized_string == "forcase":
                if(not self.forcaseStat()):
                    ok = -1
            elif self.current.recognized_string == "incase":
                if(not self.incaseStat()):
                    ok = -1
            elif self.current.recognized_string == "call":
                if(not self.callStat()):
                    ok = -1
            elif self.current.recognized_string == "return":
                if(not self.returnStat()):
                    ok = -1
            elif self.current.recognized_string == "input":
                if(not self.inputStat()):
                    ok = -1
            elif self.current.recognized_string == "print":
                if(not self.printStat()):
                    ok = -1
            else:
                if(not self.assignStat()):
                    ok = -1

            if(ok in [0,1]):
                return True
        return False

    def assignStat(self):
        if self.current.family == "id":
            target = self.current.recognized_string
            self.getToken()
            if self.current.recognized_string == ":=":
                self.getToken()
                tmpVar = self.current.recognized_string
           #     genQuad(":=", self.current.recognized_string, "_", target)
                if self.expression():
                    src = tmpVar
                    if(not src.isnumeric()):
                        src = quads[len(quads)-1].getFourth()
                    genQuad(":=", src, "_", target)
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
                            if(self.stream[self.offset+1].recognized_string == "else"):
                                self.getToken()
                            if self.elsepart():
                                return True
                            else:
                                Error(self, "elsepart not found")
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
            genQuad("jump", "_", "_", "_")
            self.getToken()
            if self.statements():
                return True
            else:
                Error(self, "statement not found on elsePart")
            return False
        else:
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
            if(self.current.recognized_string == "case"):
                while self.current.recognized_string == "case":
                    self.getToken()
                    if self.current.recognized_string == "(":
                        self.getToken()
                        if self.condition():
                            if self.current.recognized_string == ")":
                                self.getToken()
                                if self.statements():
                                    if (self.current.recognized_string == "default"):
                                        break
                                    if(self.current.recognized_string == "}"):
                                        self.getToken()
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
            if(self.current.recognized_string == "case"):
                while self.current.recognized_string == "case":
                    self.getToken()
                    if self.current.recognized_string == "(":
                        self.getToken()
                        if self.condition():
                            if self.current.recognized_string == ")":
                                self.getToken()
                                if self.statements():
                                    if (self.current.recognized_string == "default"):
                                        break
                                    if(self.current.recognized_string == "}"):
                                        self.getToken()
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
                    Error(self, "statements not found on default forcase")
            else:
                Error(self, "default not found on forcase")
            return False
        return False

    def incaseStat(self):
        if self.current.recognized_string == "incase":
            self.getToken()
            if(self.current.recognized_string == "case"):
                while self.current.recognized_string == "case":
                    self.getToken()
                    if self.current.recognized_string == "(":
                        self.getToken()
                        if self.condition():
                            if self.current.recognized_string == ")":
                                self.getToken()
                                if self.statements():
                                    if(self.current.recognized_string == "}"):
                                        self.getToken()
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
            else:
                return True

    def returnStat(self):
        if self.current.recognized_string == "return":
            self.getToken()
            if self.current.recognized_string == "(":
                self.getToken()
                returnName = self.current.recognized_string
                if self.expression():
                    if(self.offset + 1 < len(self.stream)):
                        if(self.stream[self.offset+1].recognized_string == ")"):
                            self.getToken()
                    if self.current.recognized_string == ")":
                        genQuad("RET", quads[len(quads)-2].getSecond(), "_", "_")
                     #   genQuad("call", "_", "_", returnName)
                        return True
                    else:
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
                name = self.current.recognized_string
                self.getToken()
                if self.current.recognized_string == "(":
                    self.getToken()
                    if self.actualparlist():
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
                genQuad("out", self.current.recognized_string, "_", "_")
                if self.expression():
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
                genQuad("in", self.current.recognized_string, "_", "_")
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
                tmpVar = self.current.recognized_string
                if self.expression():
                    genQuad("par", quads[len(quads)-1].getFourth(), "CV", "_")
                    return True
                else:
                    Error(self, "error, expression not found in actualparitem")
                    return False
            else:
                self.getToken()
                if self.current.family == "id":
                    genQuad("par", self.current.recognized_string, "REF", "_")
                    self.getToken()
                    return True
                else:
                    Error(self, "error, id not found in actualparitem")
                    return False
        else:
            return False

    def condition(self):
        ok = 1
        if self.boolterm():
            if(self.current.recognized_string == "or"):
                while self.current.recognized_string == "or":
                    self.getToken()
                    if self.boolterm():
                        continue
                    else:
                        ok = -1
                        Error(self, "boolterm not found")
                        break
            if(ok == 1):
                return True
        Error(self, "boolterm not found")
        return False

    def boolterm(self):
        ok = 1
        if self.boolfactor():
            if(self.current.recognized_string == "and"):
                while self.current.recognized_string == "and":
                    self.getToken()
                    if self.boolfactor():
                        continue
                    else:
                        ok = -1
                        Error(self, "boolfactor not found")
                        break
            if(ok == 1):
                return True
        Error(self, "boolfactor not found")
        return False

    def boolfactor(self):
        if self.current.recognized_string == "not":
            self.getToken()
            if self.current.recognized_string == "[":
                self.getToken()
                if self.condition():
                    if self.current.recognized_string == "]":
                        self.getToken()
                        return True
                    else:
                        Error(self, "closing arr not found")
                else:
                    Error(self, "condition not found")
            return False
        elif self.current.recognized_string == "[":
            self.getToken()
            if self.condition():
                if self.current.recognized_string == "]":
                    self.getToken()
                    return True
                else:
                    Error(self, "closing arr not found")
            else:
                Error(self, "condition not found")
            return False
        elif self.expression():
            if(self.stream[self.offset+1].recognized_string in REL_OP):
                self.getToken()
            if self.current.recognized_string in REL_OP:
                tmpRelOp = self.current.recognized_string
                tmpVar = self.stream[self.offset-1].recognized_string
                self.getToken()
                tmp = self.current.recognized_string
                if self.expression():
                    genQuad(tmpRelOp, tmpVar, tmp, "_")
                    genQuad("jump", "_", "_", "_")
                    return True
                else:
                     Error(self, "relop err")
            else:
                Error(self, "relop err")
            return False
        return False



    def expression(self):
        templist = []
        if self.optionalSign():
            temp1 = self.current.recognized_string
            if self.term():
                if(self.stream[self.offset+1].recognized_string in addOperator):
                    self.getToken()
                if self.current.recognized_string in addOperator:
                    while self.current.recognized_string in addOperator:
                        op = self.current.recognized_string
                        self.getToken()
                        temp2 = self.current.recognized_string
                        if len(templist) != 0:
                            temp1 = templist.pop()
                        temp3 = newTemp()
                        templist.append(temp3)
                        genQuad(op, temp1, temp2, temp3)
                        if self.term():
                            continue
                        else:
                            Error(self, "term not found")
                            return False
                    return True
                return True
            else:
                Error(self, "term not found")
        return False

    def term(self):
        if self.factor():
            if(self.current.recognized_string in mulOperator):
                while self.current.recognized_string in mulOperator:
                    self.getToken()
                    if self.factor():
                        continue
                    else:
                        Error(self, "factor not found")
                        return False
                return True
            return True
        Error(self, "factor not found")
        return False

    def factor(self):
        if self.current.recognized_string.isnumeric():
            self.getToken()
            return True
        elif self.current.recognized_string == "(":
            self.getToken()
            if(self.expression()):
                if self.current.recognized_string != ")":
                    self.getToken()
                if self.current.recognized_string == ")":
                    self.getToken()
                    return True
            Error(self, "err somewhere")
            return False
        elif self.current.family == "id":
            self.getToken()
            if self.idtail():
                if(self.stream[self.offset+1].recognized_string == ","):
                    self.getToken()
                return True
            Error(self, "err somewhere")
            return False
        Error(self, "err somewhere")
        return False

    def idtail(self):
        if self.current.recognized_string == "(":
            tmpId = self.stream[self.offset-1].recognized_string
            self.getToken()

            if self.actualparlist():
                if self.current.recognized_string != ")":
                    self.getToken()
                if self.current.recognized_string == ")":
                    genQuad("par", newTemp(), "RET", "_",)
                    genQuad("call", tmpId, "_", "_",)
                    return True
                else:
                    Error(self, "ERR")
            else:
                Error(self, "actualparlist not found")
            Error(self, "closing parenthesis not found")
            return False
        return True

    def optionalSign(self):
        if self.current.recognized_string in addOperator:
            return True
        return True

    def blockstatements(self):
        needNextItem = False
        ok = 0
        while self.statement():
            if(self.current.recognized_string == "}"):
                zs = 0
                if(self.stream[self.offset+1].recognized_string == ";"):
                    self.getToken()
                while(self.current.recognized_string == ";"):
                    self.getToken()
                    zs = 1
                if(zs == 1):
                    continue
                return True
            ok = 1
            needNextItem = False
            if(self.current.recognized_string in keywords):
                return False
            self.getToken()
            if self.current.recognized_string == ";":
                needNextItem = True
                self.getToken()
            if self.current.recognized_string == ")":
                break
        
        while(self.current.recognized_string in [")", ";"]):
            self.getToken()
        if(self.offset + 1 < len(self.stream)):
            if(self.stream[self.offset+1].recognized_string == "case"):
                self.getToken()
                return True
                
        if (needNextItem == True and self.current.recognized_string != "}"):
            Error(self, "Error, comma delimiter without next statement")
            return False
            
        if(ok == 1):
            return True

    programName = ""
    def program(self):
        if self.current.recognized_string == "program":
            self.getToken()
            if self.current.family == "id":
                global programName
                programName = self.current.recognized_string
             #   genQuad("begin_block", programName, "_", "_")
                self.getToken()
                self.block(0)
                self.getToken()
                if self.current.recognized_string == ".":
                    self.getToken()
                    if self.endFound:
                        genQuad("halt", "_", "_", "_")
                        genQuad("end_block", programName, "_", "_")
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
       #     print(token)
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
            for i in quads:
                print(i)

    else:
        print('Invalid parameters.')
        sys.exit(1)


if __name__ == "__main__":
    f = open(sys.argv[1:][0], "r")

    main(f.read())
