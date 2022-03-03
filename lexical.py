import sys
from collections import Counter
import re

keywords = ['program', 'declare', 'if', 'else', 'while', 'switchcase', 'forcase', 'incase', 'case', 'default', 'not',
            'and', 'or', 'function', 'procedure', 'call', 'return', 'in', 'inout', 'input', 'print']

family = [
    'keywords', 'addOperator', 'mulOperator', 'relOperator', 'delimiter', 'group', 'comment'
]

alphanumeric = "[a-zA-Z_][a-zA-Z0-9_]*"
number = "^[0-9]+$"
addOperator = ["+", "-"]
mulOperator = ["*", "/"]
relOperator = ["=", "<", ">"]
delimiter = [";", ",", ":", "."]
group = ["[", "]", "(", ")", "{", "}"]
comment = ["#"]

values = [keywords, addOperator, mulOperator, relOperator, delimiter, group, comment]

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
                return Token(self.getChar(), i, self.line)

        if self.current.isnumeric():
            tmp = []
            while (self.current != " " and self.current != "\n" and self.current not in delimiter):
                getChar = self.getChar()
                if (getChar.isnumeric()):
                    tmp.append(getChar)
                else:
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
        #    print(word)

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
            print("Den evales program:(")
            self.endFound = True
            return False

        if self.current.recognized_string in keywords:
            if self.current.recognized_string == "program":
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
        if self.offset - 1 < len(self.stream):
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
            self.getToken()
            if self.current.recognized_string == "}":
                return True

        return False

    def declarations(self):
        while self.current.recognized_string == "declare":
            delimiters = []
            idFound = False
            self.getToken()

            while self.current.family == "id":
                idFound = True
                self.getToken()
                if self.current.family == "delimiter":
                    delimiters.append(self.current.recognized_string)
                    self.getToken()
                else:
                    print("den evales delimiter anamesa sta id")

            if not idFound:
                if self.current.family == "delimiter":
                    delimiters.append(self.current.recognized_string)
                    self.getToken()

            for i in delimiters[0:-1]:
                if i != ",":
                    print("error, comma not found between ids")
                    break
            if len(delimiters) > 0 and (delimiters[-1] != ";"):
                print("error, declaration failure")
            if len(delimiters) == 0:
                print("delimiters not found on declaration")


    def program(self):
        self.getToken()
        if self.current.family == "id":
            self.getToken()
            self.block()
            self.getToken()
            if self.current.recognized_string == ".":
                if self.endFound:
                    print("EOF")

def main(argv):
    form = argv

    if form is not None:
        lex = Lexer(form)
        token = lex.nextToken()
        while token is not None:
            lex.tokenList.append(token)
          #  print(token)
            token = lex.nextToken()

        # Syntax
        syntax = Syntax(lex.tokenList)
        token = syntax.getToken()
        sntx = syntax.checkSyntax()
        while sntx is not False:
            print(token, "       |       " ,sntx)
            token = syntax.getToken()
            sntx = syntax.checkSyntax()
        print(token, "       |       ", sntx)
    else:
        print('Invalid parameters.')
        sys.exit(1)


if __name__ == "__main__":
    f = open(sys.argv[1:][0], "r")

    main(f.read())
