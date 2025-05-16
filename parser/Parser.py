"""
Programa que implementa un parser descendente recursivo para el lenguaje C- con sus reglas de gramática.
Autor: Shaul Zayat Askenazi - A01783240
"""

from lexer import *
from globalTypes import *

# ----------------------------

# ----------------------------
# Árbol de sintaxis abstracta (AST)
# Apoyado de copilot para la creación de nodos
# ----------------------------
class Nodo:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo        
        self.valor = valor
        self.hijos = []

    def agregarHijo(self, nodo):
        if nodo:
            self.hijos.append(nodo)

# ----------------------------
# Parser descendente recursivo para C-
# ----------------------------
def parser(imprime=True):
    global tokenActual, programa, posicion, progLong
    print("\033[32mIniciando análisis sintáctico\033[0m") # Mensaje de inicio en verde en consola
    globalValLexer(programa, posicion, progLong)  # Sincronizar con el lexer
    tokenActual = getToken(imprime=True)  # Obtener el primer token
    raiz = program()
    if imprime:
        imprimirAST(raiz)
    return raiz

# ----------------------------
# Hacer match con el token actual
# ----------------------------
def match(esperado):
    global tokenActual
    print(f"match: esperando {esperado}, actual {tokenActual}")
    if tokenActual[0] == esperado:
        tokenActual = getToken()
    else:
        errorSintactico(f"Se esperaba {esperado.name} pero se recibió {tokenActual[0].name}")


# ----------------------------
# Manejo de errores sintácticos
# Apoyado de copilot para los casos de lineas
# ----------------------------
def errorSintactico(mensaje):
    global programa, posicion, tokenActual
    from lexer import posicion  # Importar la posición actual directamente del lexer

    # Variables para rastrear la posición
    linea_actual = 1
    columna_actual = 1
    inicio_error = posicion - len(tokenActual[1]) if len(tokenActual) > 1 else posicion

    # Recorrer el programa hasta la posición inicial del error
    for i in range(inicio_error):
        if programa[i] == '\n':  # Si encontramos un salto de línea
            linea_actual += 1
            columna_actual = 1  # Reiniciar la columna al inicio de la nueva línea
        else:
            columna_actual += 1

    # Verificar si el error ocurre después de un salto de línea
    if inicio_error > 0 and programa[inicio_error - 1] == '\n':
        linea_actual -= 1  # Retroceder a la línea anterior
        # Obtener la columna de la última posición de la línea anterior
        columna_actual = len(programa.splitlines()[linea_actual - 1]) + 1

    # Obtener la línea completa del programa donde ocurrió el error
    lineas = programa.splitlines()
    linea_codigo = lineas[linea_actual - 1] if linea_actual - 1 < len(lineas) else ""

    # Imprimir el mensaje de error en rojo
    print(f"\033[31mError de sintaxis en línea {linea_actual}: {mensaje}\033[0m")
    print(f"{linea_codigo}")
    print(" " * (columna_actual - 2) + "^")  # Marcar la posición del error con un acento circunflejo

    # Recuperación del error (botón de pánico)
    panicMode()
    
# ----------------------------
# Modo de pánico para recuperación de errores
# ----------------------------
def panicMode():
    global tokenActual
    # Avanzar hasta encontrar un token de sincronización
    while tokenActual[0] not in [TokenType.SEMI, TokenType.RBRACE, TokenType.ENDFILE]:
        tokenActual = getToken()
    # Consumir el token de sincronización si no es ENDFILE
    if tokenActual[0] != TokenType.ENDFILE:
        tokenActual = getToken()

# ----------------------------
# Funcion de programa
# ----------------------------
def program():
    global tokenActual, posicion
    print("Iniciando análisis del programa")
    nodo = Nodo("programa")
    while posicion < progLong and tokenActual[0] != TokenType.ENDFILE:
        print(f"program: procesando token {tokenActual}")
        nodo.agregarHijo(declaracion())
        posicion += 1
    return nodo

# ----------------------------
# Declaración de funciones y variables
# ----------------------------
def declaracion():
    print(f"declaracion: token actual {tokenActual}")
    if tokenActual[0] in [TokenType.INT, TokenType.VOID]:
        tipo = tipo_espec()  # Procesa el tipo (int o void)
        if tokenActual[0] == TokenType.ID:
            id_name = tokenActual[1]
            match(TokenType.ID)  # Procesa el identificador
            if tokenActual[0] == TokenType.LPAREN:
                print(f"Declaración de función: {id_name}")
                match(TokenType.LPAREN)
                params_node = parametros()
                match(TokenType.RPAREN)
                cuerpo_node = compuesto()
                fun_node = Nodo("fun-decl", None)  # Nodo de la función
                fun_node.agregarHijo(tipo)  # Agregar el tipo como hijo
                fun_node.agregarHijo(Nodo("id", id_name))  # Agregar el identificador como hijo
                fun_node.agregarHijo(params_node)  # Agregar los parámetros como hijo
                fun_node.agregarHijo(cuerpo_node)  # Agregar el cuerpo como hijo
                return fun_node
            # Declaración de variable
            elif tokenActual[0] == TokenType.SEMI:
                print(f"Declaración de variable: {id_name}")
                match(TokenType.SEMI)
                var_node = Nodo("var-decl", id_name)
                var_node.agregarHijo(tipo)
                return var_node
            else:
                errorSintactico("Se esperaba '(' o ';' o 'NUM' dentro de un arreglo")
        else:
            errorSintactico("Se esperaba identificador")
    else:
        errorSintactico("Se esperaba 'int' o 'void'")
    return Nodo("error")

# ----------------------------
# Funcion auxiliar de tipo
# ----------------------------
def tipo_espec():
    if tokenActual[0] == TokenType.INT:
        match(TokenType.INT)
        return Nodo("tipo", "int")
    elif tokenActual[0] == TokenType.VOID:
        match(TokenType.VOID)
        return Nodo("tipo", "void")
    # Revisar logica para id
    else:
        errorSintactico("Tipo inválido")
        return Nodo("tipo", "error")

# ----------------------------
# Funcion para parámetros
# ----------------------------
def parametros():
    nodo = Nodo("parametros")
    if tokenActual[0] == TokenType.VOID:
        match(TokenType.VOID)
        if tokenActual[0] != TokenType.RPAREN:
            errorSintactico("'void' no debe ir seguido de parámetros")
        return nodo
    elif tokenActual[0] == TokenType.RPAREN:
        return nodo  # No hay parámetros
    else:
        nodo.agregarHijo(param())
        while tokenActual[0] == TokenType.COMMA:
            match(TokenType.COMMA)
            nodo.agregarHijo(param())
        return nodo

# ----------------------------
# Función para parámetros individuales
# ----------------------------
def param(): 
    global tokenActual
    tipo = tipo_espec()
    if tokenActual[0] == TokenType.ID or tokenActual[0] == TokenType.INT: 
        nombre = tokenActual[1]
        match(TokenType.ID)
        if tokenActual[0] == TokenType.LBRACKET:  # Verificar si hay "["
            match(TokenType.LBRACKET)
            if tokenActual[0] == TokenType.RBRACKET:  # Verificar si hay "]"
                match(TokenType.RBRACKET)
                return Nodo("param", f"{nombre}[]")  # Nodo para un arreglo
            else:
                errorSintactico("Se esperaba ']' después de '['")
        return Nodo("param", nombre)  # Nodo para un parámetro normal
    else:
        errorSintactico("Se esperaba identificador en parámetro")
        return Nodo("param", "error")

# ----------------------------
# Función para el cuerpo de la función
# ----------------------------
def compuesto():
    match(TokenType.LBRACE)
    nodo = Nodo("compound-stmt")
    while tokenActual[0] != TokenType.RBRACE and tokenActual[0] != TokenType.ENDFILE:
        if tokenActual[0] in [TokenType.INT, TokenType.VOID]:
            nodo.agregarHijo(declaracion())  # Procesar declaraciones locales
        else:
            nodo.agregarHijo(statement())  # Procesar sentencias
    if tokenActual[0] == TokenType.RBRACE:
        match(TokenType.RBRACE)
    else:
        errorSintactico("Se esperaba '}' para cerrar el bloque")
    return nodo


# ----------------------------
# Función para procesar sentencias
# ----------------------------
def statement():
    global tokenActual
    # Selection statement
    if tokenActual[0] == TokenType.IF:
        return if_stmt()
    # Iteration statement
    elif tokenActual[0] == TokenType.WHILE:
        return while_stmt()
    # Return statement
    elif tokenActual[0] == TokenType.RETURN:
        return return_stmt()
    # Compound statement
    elif tokenActual[0] == TokenType.LBRACE:
        return compuesto()
    # Expression statement
    else:
        return expression_stmt()

# ----------------------------
# Función para procesar sentencias de expresión
# ----------------------------
def expression_stmt():
    global tokenActual
    if tokenActual[0] == TokenType.SEMI:  # Sentencia vacía
        match(TokenType.SEMI)
        return Nodo("empty-stmt")
    else:
        expr = expression()  # Procesar la expresión
        if tokenActual[0] == TokenType.SEMI:
            match(TokenType.SEMI)  # Consumir el punto y coma
            return expr
        else:
            errorSintactico(f"Se esperaba ';' pero se recibió {tokenActual[0].name}")
            return Nodo("error")

# ----------------------------
# Función para procesar sentencias de selección (if-else)
# ----------------------------
def if_stmt():
    global tokenActual
    match(TokenType.IF)  # Consumir el token `if`
    match(TokenType.LPAREN)  # Consumir el paréntesis de apertura
    cond = expression()  # Procesar la condición como una expresión
    match(TokenType.RPAREN)  # Consumir el paréntesis de cierre
    then_stmt = statement()  # Procesar el cuerpo del `if`
    else_stmt = None
    if tokenActual[0] == TokenType.ELSE:  # Verificar si hay una rama `else`
        match(TokenType.ELSE)
        else_stmt = statement()  # Procesar el cuerpo del `else`
    nodo = Nodo("if-stmt")
    nodo.agregarHijo(cond)  # Agregar la condición como hijo
    nodo.agregarHijo(then_stmt)  # Agregar el cuerpo del `if` como hijo
    if else_stmt:
        nodo.agregarHijo(else_stmt)  # Agregar el cuerpo del `else` como hijo (si existe)
    return nodo

# ----------------------------
# Función para procesar sentencias de iteración (while)
# ----------------------------
def while_stmt():
    global tokenActual
    match(TokenType.WHILE)
    match(TokenType.LPAREN)
    cond = expression()
    match(TokenType.RPAREN)
    body = statement()
    nodo = Nodo("while-stmt")
    nodo.agregarHijo(cond)
    nodo.agregarHijo(body)
    return nodo

# ----------------------------
# Función para procesar sentencias de retorno (return)
# ----------------------------
def return_stmt():
    global tokenActual
    match(TokenType.RETURN)
    if tokenActual[0] != TokenType.SEMI:
        expr = expression()
        nodo = Nodo("return-stmt")
        nodo.agregarHijo(expr)
    else:
        nodo = Nodo("return-stmt")
    match(TokenType.SEMI)
    return nodo

# ----------------------------
# Función para procesar expresiones
# ----------------------------
def expression():
    global tokenActual
    # Procesar una variable o un identificador
    if tokenActual[0] == TokenType.ID:
        id_name = tokenActual[1]
        match(TokenType.ID)
        # Si se recibe un paréntesis, se trata de llamar a factor
        if tokenActual[0] == TokenType.LPAREN:
            return call(id_name)
        if tokenActual[0] == TokenType.LBRACKET:  # Acceso a un arreglo
            match(TokenType.LBRACKET)
            expr = expression()
            match(TokenType.RBRACKET)
            var_node = Nodo("array-access", id_name)
            var_node.agregarHijo(expr)
        else:
            var_node = Nodo("id", id_name)  # Nodo para un identificador

        # Verificar si hay una asignación
        if tokenActual[0] == TokenType.ASSIGN:
            match(TokenType.ASSIGN)
            expr_node = expression()  # Procesar la expresión del lado derecho
            assign_node = Nodo("assign")
            assign_node.agregarHijo(var_node)  # Lado izquierdo de la asignación
            assign_node.agregarHijo(expr_node)  # Lado derecho de la asignación
            return assign_node
            
        elif tokenActual[0] in [TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE, TokenType.EQ, TokenType.NEQ]:
            # Si hay un operador relacional, procesar la expresión
            operador = tokenActual[1]
            match(tokenActual[0])  # Consume el operador
            nodo_relacional = Nodo("relop", operador)
            nodo_relacional.agregarHijo(var_node)  # Agrega la variable como hijo
            nodo_relacional.agregarHijo(additive_expression())  # Procesa la expresión aditiva
            return nodo_relacional
        
        elif tokenActual[0] in [TokenType.PLUS, TokenType.MINUS]:
            # Si hay un operador aritmético, procesar la expresión
            operador = tokenActual[1]
            match(tokenActual[0])
            nodo_aditivo = Nodo("addop", operador) # Nodo para el operador
            nodo_aditivo.agregarHijo(var_node)  # Agrega la variable como hijo
            nodo_aditivo.agregarHijo(term())  # Procesa el siguiente término
            return nodo_aditivo
        elif tokenActual[0] in [TokenType.TIMES, TokenType.DIVIDE]:
            # Si hay un operador multiplicativo, procesar la expresión
            operador = tokenActual[1]
            match(tokenActual[0])
            nodo_multiplicativo = Nodo("mulop", operador) # Nodo para el operador de multiplicación o división
            nodo_multiplicativo.agregarHijo(var_node)
            nodo_multiplicativo.agregarHijo(factor())  # Procesa el siguiente factor
            return nodo_multiplicativo      
        else:
            # Si no hay asignación, delegar a simple_expression
            return simple_expression_with_var(var_node)
    # Procesar un número
    elif tokenActual[0] == TokenType.NUM:
        num_value = tokenActual[1]
        match(TokenType.NUM)
        return Nodo("num", num_value)
    # Procesar una simple-expression
    else:
        return simple_expression()

# ----------------------------
# Función auxiliar para procesar expresiones simples con variables
# ----------------------------
def simple_expression_with_var(var_node):
    global tokenActual
    if tokenActual[0] in [TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE, TokenType.EQ, TokenType.NEQ]:
        operador = tokenActual[1]  # Captura el operador relacional
        match(tokenActual[0])  # Consume el operador
        nodo_relacional = Nodo("relop", operador)
        nodo_relacional.agregarHijo(var_node)  # Agrega la variable como hijo
        nodo_relacional.agregarHijo(additive_expression())  # Procesa la expresión aditiva
        return nodo_relacional
    return var_node  # Si no hay operador relacional, devuelve la variable

# ----------------------------
# Función para procesar declaraciones de variables
# ----------------------------
def var_decl():
    global tokenActual
    tipo = tipo_espec()
    if tokenActual[0] == TokenType.ID:
        id_name = tokenActual[1]
        match(TokenType.ID)
        if tokenActual[0] == TokenType.LBRACKET:
            match(TokenType.LBRACKET)
            if tokenActual[0] == TokenType.NUM:
                num_value = tokenActual[1]
                match(TokenType.NUM)
                match(TokenType.RBRACKET)
                nodo = Nodo("array-decl", id_name)
                nodo.agregarHijo(tipo)
                nodo.agregarHijo(Nodo("num", num_value))
                return nodo
            else:
                errorSintactico("Se esperaba un número después de '['")
        else:
            match(TokenType.SEMI)
            return Nodo("var-decl", id_name)
    else:
        errorSintactico("Se esperaba un identificador")
        return Nodo("error")
    

# ----------------------------
# Función para procesar expresiones simples
# ----------------------------
def simple_expression():
    nodo = additive_expression()  # Procesa la primera expresión aditiva
    if tokenActual[0] in [TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE, TokenType.EQ, TokenType.NEQ]:
        operador = tokenActual[1]  # Captura el operador relacional
        match(tokenActual[0])  # Consume el operador
        nodo_relacional = Nodo("relop", operador)
        nodo_relacional.agregarHijo(nodo)  # Agrega la primera expresión como hijo
        nodo_relacional.agregarHijo(additive_expression())  # Procesa la segunda expresión aditiva
        return nodo_relacional
    return nodo  # Si no hay operador relacional, devuelve la expresión aditiva


# ----------------------------
# Función para procesar expresiones aditivas
# ----------------------------
def additive_expression():
    nodo = term()  # Procesa el primer término
    while tokenActual[0] in [TokenType.PLUS, TokenType.MINUS]:
        operador = tokenActual[1]  # Captura el operador de suma o resta
        match(tokenActual[0])  # Consume el operador
        nodo_aditivo = Nodo("addop", operador)
        nodo_aditivo.agregarHijo(nodo)  # Agrega el término actual como hijo
        nodo_aditivo.agregarHijo(term())  # Procesa el siguiente término
        nodo = nodo_aditivo  # Actualiza el nodo actual
    return nodo

# ----------------------------
# Función para procesar términos
# ----------------------------
def term():
    nodo = factor()  # Procesa el primer factor
    while tokenActual[0] in [TokenType.TIMES, TokenType.DIVIDE]:
        operador = tokenActual[1]  # Captura el operador de multiplicación o división
        match(tokenActual[0])  # Consume el operador
        nodo_multiplicativo = Nodo("mulop", operador)
        nodo_multiplicativo.agregarHijo(nodo)  # Agrega el factor actual como hijo
        nodo_multiplicativo.agregarHijo(factor())  # Procesa el siguiente factor
        nodo = nodo_multiplicativo  # Actualiza el nodo actual
    return nodo


# ----------------------------
# Función para procesar factores
# ----------------------------
def factor():
    if tokenActual[0] == TokenType.LPAREN:
        match(TokenType.LPAREN)
        nodo = expression()  # Procesa la expresión entre paréntesis
        match(TokenType.RPAREN)
        return nodo
    elif tokenActual[0] == TokenType.NUM:
        valor = tokenActual[1]
        match(TokenType.NUM)
        return Nodo("num", valor)  # Nodo para un número
    elif tokenActual[0] == TokenType.ID:
        id_name = tokenActual[1]
        match(TokenType.ID)
        if tokenActual[0] == TokenType.LPAREN:
            return call(id_name)  # Llamada a función
        elif tokenActual[0] == TokenType.LBRACKET:
            return var_decl(id_name)  # Acceso a un arreglo
        else:
            return Nodo("id", id_name)  # Nodo para un identificador
    else:
        errorSintactico("Se esperaba un factor válido")
        return Nodo("error")

# ----------------------------
# Función para procesar llamadas a funciones
# ----------------------------
def call(id_name):
    match(TokenType.LPAREN)
    nodo = Nodo("call", id_name)
    nodo.agregarHijo(args())  # Procesa los argumentos
    match(TokenType.RPAREN)
    return nodo

# ----------------------------
# Función para procesar argumentos de función
# ----------------------------
def args():
    if tokenActual[0] == TokenType.RPAREN:
        return Nodo("args")  # Nodo vacío para argumentos
    else:
        return arg_list()  # Procesa la lista de argumentos

# ----------------------------
# Función para procesar la lista de argumentos
# ----------------------------
def arg_list():
    nodo = Nodo("arg-list")
    nodo.agregarHijo(expression())  # Procesa la primera expresión
    while tokenActual[0] == TokenType.COMMA:
        match(TokenType.COMMA)
        nodo.agregarHijo(expression())  # Procesa las expresiones adicionales
    return nodo

# ----------------------------
# Impresión del AST
# ----------------------------
def imprimirAST(nodo, nivel=0):
    if nodo:
        print("  " * nivel + f"<{nodo.tipo} {nodo.valor if nodo.valor else ''}>")
        for hijo in nodo.hijos:
            imprimirAST(hijo, nivel + 1)

# ----------------------------
# Función para inicializar los valores globales y sincronizar con el lexer
# ----------------------------
def globales(pro, pos, long):
    global programa, posicion, progLong
    programa = pro
    posicion = pos
    progLong = long
    globalValLexer(programa, posicion, progLong)