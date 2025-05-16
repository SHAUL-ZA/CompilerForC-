"""
Programación de un analizador léxico (lexer) para un lenguaje C-

Shaul Zayat Askenazi - A01783240
"""

import re
from globalTypes import *  # Importamos los tipos de token y palabras reservadas

# Variables globales requeridas
programa = ''
posicion = 0
progLong = 0
lineaActual = 1

def globales(prog, pos, long):
    global programa, posicion, progLong
    programa = prog
    posicion = pos
    progLong = long

# Lista de expresiones regulares para reconocer tokens
regex_tokens = [
    (r'^\d+', TokenType.NUM),                      # Números
    (r'^\+', TokenType.PLUS),                      # '+'
    (r'^-', TokenType.MINUS),                      # '-'   
    (r'^\*', TokenType.TIMES),                     # '*'
    (r'^/', TokenType.DIVIDE),                     # '/'
    (r'^<=', TokenType.LTE),                       # '<='
    (r'^<', TokenType.LT),                         # '<'
    (r'^>=', TokenType.GTE),                       # '>='
    (r'^>', TokenType.GT),                         # '>'
    (r'^==', TokenType.EQ),                        # '=='
    (r'^!=', TokenType.NEQ),                       # '!='
    (r'^=', TokenType.ASSIGN),                     # '='
    (r'^;', TokenType.SEMI),                       # ';'
    (r'^,', TokenType.COMMA),                      # ','
    (r'^\(', TokenType.LPAREN),                    # '('
    (r'^\)', TokenType.RPAREN),                    # ')'
    (r'^{', TokenType.LBRACE),                     # '{'
    (r'^}', TokenType.RBRACE),                     # '}'
    (r'^\[', TokenType.LBRACKET),                  # '['
    (r'^\]', TokenType.RBRACKET),                  # ']'
    (r'^\s+', None),  # Espacios en blanco (no devuelve token)
    (r'^/\*[\s\S]*?\*/', TokenType.COMMENT),  # Comentarios de varias líneas
]

# Función principal
def getToken(imprime=True):
    global programa, posicion, progLong, lineaActual
    estado = 0
    tokenString = ''

    while posicion < progLong:
        c = programa[posicion]

        # Estados del DFA   
        if estado == 0:
            # Estado 0: espera una letra, número o espacio
            if c.isspace():
                # Si es espacio, seguimos en estado 0
                if c == '\n':
                    lineaActual += 1
                posicion += 1
            elif c.isalpha():  # Si encontramos una letra
                estado = 1  # Pasamos al estado 1
                tokenString += c
                posicion += 1
            elif c.isdigit():  # Si encontramos un número
                estado = 2  # Pasamos al estado 2
                tokenString += c
                posicion += 1
            elif c == '+':  # Si encontramos '+'
                estado = 3  # Estado 3 para '+'
                tokenString += c
                posicion += 1
            elif c == '-':  # Si encontramos '-'
                estado = 4  # Estado 4 para '-'
                tokenString += c
                posicion += 1
            elif c == '*':  # Si encontramos '*'
                estado = 5  # Estado 5 para '*'
                tokenString += c
                posicion += 1

            elif c == '/':  # Si encontramos '/'
                # Miramos el siguiente carácter
                if posicion + 1 < progLong and programa[posicion + 1] == '*':
                    # Si el siguiente carácter es '*', iniciamos un comentario multilinea
                    estado = 19  # Estado para comentarios multilinea
                    tokenString += '/*'
                    posicion += 2  # Avanzamos dos posiciones (el '/' y el '*')
                else:
                    # Si no es '*', puede ser un error o un operador '/'
                    estado = 6  # Estado para '/'
                    tokenString += c
                    posicion += 1                                                 

            elif c == '<':  # Si encontramos '<'
                # Miramos el siguiente carácter
                if posicion + 1 < progLong and programa[posicion + 1] == '=':
                    # Si el siguiente carácter es '=', formamos el token '<='
                    estado = 22
                    tokenString += '<='
                    posicion += 2  # Avanzamos dos posiciones (el '<' y el '=')
                else:
                    # Si no es '=', formamos el token '<'
                    estado = 7
                    tokenString += '<'
                    posicion += 1 # Avanzamos una posición para continuar el análisis

            
            elif c == '>':  # Si encontramos '>'
                # Miramos el siguiente carácter
                if posicion + 1 < progLong and programa[posicion + 1] == '=':
                    # Si el siguiente carácter es '=', formamos el token '>='
                    estado = 23
                    tokenString += '>='
                    posicion += 2
                else:
                    # Si no es '=', formamos el token '>'
                    estado = 8
                    tokenString += '>'
                    posicion += 1


            elif c == '=' :  # Si encontramos '='
                # Miramos el siguiente carácter
                if posicion + 1 < progLong and programa[posicion + 1] == '=':
                    # Si el siguiente carácter es '=', formamos el token '=='
                    estado = 24
                    tokenString += '=='
                    posicion += 2  # Avanzamos dos posiciones (el '=' y el '=')
                else:
                    # Si no es '=', formamos el token '='
                    estado = 9
                    tokenString += '='
                    posicion += 1  # Avanzamos una posición para continuar el análisis

            elif c == '!':  # Si encontramos '!'
                # Miramos el siguiente carácter
                if posicion + 1 < progLong and programa[posicion + 1] == '=':
                    # Si el siguiente carácter es '=', formamos el token '!='
                    estado = 25  # Estado para '!='
                    tokenString += '!='
                    posicion += 2  # Avanzamos dos posiciones (el '!' y el '=')
                else:
                    # Si no es '=', es un error
                    token = TokenType.ERROR
                    tokenString = '!'  # El token erróneo es solo '!'
                    mensajeError(lineaActual, tokenString)
                    tokenString = ''  # Reiniciamos el tokenString para evitar procesar partes válidas
                    posicion += 1  # Avanzamos una posición para continuar el análisis


            elif c == ';':  # Si encontramos ';'
                estado = 11  # Estado 11 para ';'
                tokenString += c
                posicion += 1

            elif c == ',':  # Si encontramos ','
                estado = 12  # Estado 12 para ','
                tokenString += c
                posicion += 1
            
            elif c == '(':  # Si encontramos '('
                estado = 13  # Estado 13 para '('
                tokenString += c
                posicion += 1

            elif c == ')':  # Si encontramos ')'
                estado = 14  # Estado 14 para ')'
                tokenString += c
                posicion += 1
            
            elif c == '[':  # Si encontramos '['
                estado = 15  # Estado 15 para '['
                tokenString += c
                posicion += 1

            elif c == ']':  # Si encontramos ']'
                estado = 16  # Estado 16 para ']'
                tokenString += c
                posicion += 1

            elif c == '{':  # Si encontramos '{'
                estado = 17  # Estado 17 para '{'
                tokenString += c
                posicion += 1

            elif c == '}':  # Si encontramos '}'
                estado = 18  # Estado 18 para '}'
                tokenString += c
                posicion += 1
    
                
            # No coincide ningun estado de aceptación, intentamos con expresiones regulares o mandamos error
            else:
                # Si no coincide con ningún estado válido, intentamos hacer match con expresiones regulares
                for regex, token_type in regex_tokens:
                    match = re.match(regex, programa[posicion:])
                    if match:
                        lexema = match.group(0)
                        posicion += len(lexema)
                        if token_type is not None:
                            if imprime:
                                print(token_type, " = ", lexema)
                            return token_type, lexema
                        else:
                            break  # Si es solo un espacio o comentario, pasamos al siguiente
                
                # Se tiene que buscar todo el lexema para reportar el error
                tokenString += c  # Incluimos el carácter no válido en el token
                posicion += 1
                # Consumimos el resto del token inválido hasta un delimitador válido o espacio 
                while posicion < progLong and not esDelimitadorValido(programa[posicion]):
                    tokenString += programa[posicion]
                    posicion += 1
                token = TokenType.ERROR
                mensajeError(lineaActual, tokenString)  # Reportamos el error
                tokenString = ''  # Reiniciamos el tokenString para evitar procesar partes válidas
                return token, tokenString  # Salimos sin procesar más        
                

        elif estado == 1: # Apoyado de Copilot
            # Estado 1: procesar identificadores (IDs)
            if c.isalpha():  # Solo aceptamos letras
                # Si es una letra, seguimos construyendo el identificador
                tokenString += c
                posicion += 1
            elif esDelimitadorValido(c) or c.isspace():
                # Si encontramos un delimitador válido o un espacio, terminamos el lexema
                token = reservedWords.get(tokenString, TokenType.ID)  # Verifica si es una palabra reservada
                if imprime:
                    print(tokenString, " = ", token)
                return token, tokenString
            else:
                # Si encontramos un carácter no válido, consumimos todo el lexema como un error
                while posicion < progLong and not esDelimitadorValido(programa[posicion]) and not programa[posicion].isspace():
                    tokenString += programa[posicion]
                    posicion += 1
                token = TokenType.ERROR
                mensajeError(lineaActual, tokenString)  # Reportamos el error
                tokenString = ''  # Reiniciamos el tokenString para evitar procesar partes válidas
                return token, tokenString

        elif estado == 2:
            # Estado 2: espera un número y puede seguir recibiendo más números
            if c.isdigit():
                # Si encontramos un dígito, seguimos recibiendo números
                tokenString += c
                posicion += 1
            else:
                if (c.isalpha() or c == '.'):
                    # Si encontramos una letra, es un error
                    tokenString += c  # Incluimos el carácter no válido en el token
                    posicion += 1
                    while posicion < progLong and programa[posicion].isalnum():
                        # Consumimos el resto del token inválido
                        tokenString += programa[posicion]
                        posicion += 1
                    token = TokenType.ERROR
                    mensajeError(lineaActual, tokenString)  # Reportamos el error
                    return token, tokenString  # Salimos sin procesar más
                else:
                    # Si encontramos cualquier otro carácter, terminamos el lexema
                    token = TokenType.NUM
                    if imprime:
                        print(tokenString, " = ", token)
                    return token, tokenString

        elif estado == 3:
            # Estado 3: '+', es un estado de aceptación
            token = TokenType.PLUS
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString

        elif estado == 4:
            # Estado 4: '-', es un estado de aceptación
            token = TokenType.MINUS
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString

        elif estado == 5:
            # Estado 5: '*', es un estado de aceptación
            token = TokenType.TIMES
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 6:
            # Estado 6: '/', es un estado de aceptación
            token = TokenType.DIVIDE
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString

        elif estado == 7:
            # Estado 7: '<', es un estado de aceptación
            token = TokenType.LT
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 8:
            # Estado 8: '>', es un estado de aceptación
            token = TokenType.GT
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 9:
            # Estado 9: '=', es un estado de aceptación
            token = TokenType.ASSIGN
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString

        elif estado == 11:
            # Estado 11: ';', es un estado de aceptación
            token = TokenType.SEMI
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 12:
            # Estado 12: ',', es un estado de aceptación
            token = TokenType.COMMA
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 13:
            # Estado 13: '(', es un estado de aceptación
            token = TokenType.LPAREN
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 14:
            # Estado 14: ')', es un estado de aceptación
            token = TokenType.RPAREN
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 15:
            # Estado 15: '[', es un estado de aceptación
            token = TokenType.LBRACKET
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 16:
            # Estado 16: ']', es un estado de aceptación
            token = TokenType.RBRACKET
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 17:
            # Estado 17: '{', es un estado de aceptación
            token = TokenType.LBRACE
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 18:
            # Estado 18: '}', es un estado de aceptación
            token = TokenType.RBRACE
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 19:
            # Estado 19: '/*', (iniciando comentario multilinea)
            while posicion < progLong and not (programa[posicion] == '*' and programa[posicion + 1] == '/'):
                tokenString += programa[posicion]
                posicion += 1
            if posicion < progLong:
                tokenString += '*/'
                posicion += 2  # Avanzamos dos posiciones (el '*' y el '/')
                token = TokenType.COMMENT # Estado de aceptación para el comentario multilinea #21 DFA
                if imprime:
                    print(tokenString, " = ", token)
                return token, tokenString
            else:
                # Si no encontramos el cierre del comentario le mandamos error
                token = TokenType.ERROR
                tokenString = '/*'  # El token erróneo es solo '/*'
                mensajeError(lineaActual, tokenString)
                posicion += 1  # Avanzamos una posición para continuar el análisis
        
        elif estado == 22:
            # Estado 22: '<=', es un estado de aceptación
            token = TokenType.LTE
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 23:
            # Estado 23: '>=', es un estado de aceptación
            token = TokenType.GTE
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 24:
            # Estado 24: '==', es un estado de aceptación
            token = TokenType.EQ
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString
        
        elif estado == 25:
            # Estado 25: '!=', es un estado de aceptación
            token = TokenType.NEQ
            if imprime:
                print(tokenString, " = ", token)
            return token, tokenString    

    if estado == 19:
        # Si estamos en estado de comentario y no hemos encontrado el cierre, lo procesamos
        token = TokenType.COMMENT
        if imprime:
            print(tokenString, " = ", token)
        return token, tokenString
    # Al final del archivo: si no hemos llegado al final, lo procesamos también
    if posicion >= progLong:
        token = TokenType.ENDFILE
        tokenString = ''
        if imprime:
            print(tokenString, " = ", token)
        return token, tokenString
    else: # Si hay algún carácter que no se ha reconocido (en caso de error)
        # Si encontramos un carácter no válido al inicio de un token
        if not c.isalnum() and not c.isspace():
            tokenString += c  # Incluimos el carácter no válido en el token
            posicion += 1
            # Consumimos el resto del token inválido (hasta un delimitador válido o espacio)
            while posicion < progLong and not esDelimitadorValido(programa[posicion]):
                tokenString += programa[posicion]
                posicion += 1
            token = TokenType.ERROR
            mensajeError(lineaActual, tokenString)  # Reportamos el error
            tokenString = ''  # Reiniciamos el tokenString para evitar procesar partes válidas
            return token, tokenString
        else:
            # Si no es un carácter válido pero tampoco es un delimitador, avanzamos
            posicion += 1

# Muestra errores con posición exacta
def mensajeError(linea, lexema):
    """
    Muestra un mensaje de error con la línea y el lexema que causó el error.

    Args: linea (int): Número de línea.
          lexema (str): Lexema que causó el error.

    Returns: None
    """
    lineaTexto = obtenerLinea(linea)
    col = obtenerColumnaActual()
    print(f"Línea {linea}: Error en la formación de un token:")
    print(lineaTexto)
    print(" " * col + "^")

# Función auxiliar: regresa el texto de la línea actual
def obtenerLinea(linea):
    """
    Regresa el texto de la línea actual.   

    Args: linea (int): Número de línea.

    Returns: str: Texto de la línea actual.
    """
    return programa.split('\n')[linea - 1]

# Función auxiliar: calcula posición en la línea actual
def obtenerColumnaActual():
    """
    Calcula la posición en la línea actual.

    Args: None

    Returns: int: Posición en la línea actual.
    """
    linea_inicio = programa.rfind('\n', 0, posicion)
    return posicion - linea_inicio - 1

# Función auxiliar: verifica si el carácter es un delimitador válido dentro de un posible lexema inválido
def esDelimitadorValido(caracter):
    """
    Verifica si el carácter es un delimitador válido dentro de un posible lexema inválido.

    Args: caracter (str): Carácter a verificar.

    Returns: bool: True si es un delimitador válido, False en caso contrario.
    """
    delimitadores = ['+', '-', '*', '/', '<', '>', '=', '!', ';', ',', '(', ')', '[', ']', '{', '}']
    return caracter.isspace() or caracter in delimitadores
