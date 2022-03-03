import sys
import os
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


def main(argv):
    form = argv

    if form is not None:
        lex = Lexer(form)
        token = lex.nextToken()
        while token is not None:
            print(token)
            token = lex.nextToken()
    else:
        print('Invalid parameters.')
        sys.exit(1)


if __name__ == "__main__":
    f = open(sys.argv[1:][0], "r")

    main(f.read())
