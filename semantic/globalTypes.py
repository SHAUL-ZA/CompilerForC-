from enum import Enum

class TokenType(Enum):
    # Tokens
    ID = 1          # Identificadores
    NUM = 2         # Números enteros
    PLUS = 3        # +
    MINUS = 4       # -
    TIMES = 5       # *
    DIVIDE = 6      # /
    LT = 7          # <
    LTE = 8         # <=
    GT = 9          # >
    GTE = 10        # >=
    EQ = 11         # ==
    NEQ = 12        # !=
    ASSIGN = 13     # =
    SEMI = 14       # ;
    COMMA = 15      # ,
    LPAREN = 16     # (
    RPAREN = 17     # )
    LBRACE = 18     # {
    RBRACE = 19     # }
    LBRACKET = 20   # [
    RBRACKET = 21   # ]
    COMMENT = 22    # /* */

    # Palabras reservadas de C-
    IF = 23        # if
    ELSE = 24       # else
    INT = 25        # int
    RETURN = 26     # return
    VOID = 27       # void
    WHILE = 28      # while

    # Final de archivo y error
    ENDFILE = 29    # EOF
    ERROR = 30      # Error

# Diccionario de palabras reservadas
reservedWords = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "int": TokenType.INT,
    "return": TokenType.RETURN,
    "void": TokenType.VOID,
    "while": TokenType.WHILE
}
