"""
Programa que implementa un Analizador Semántico para el lenguaje C- con sus reglas de inferencia.
Autor: Shaul Zayat Askenazi - A01783240
"""

from Parser import * 

# ----------------------------
# Clase para representar la tabla de símbolos. Apoyado de Copilot para el diseño de la clase.
# ----------------------------
class TablaSimbolos:
    def __init__(self, nombre, padre=None):
        self.nombre = nombre
        self.padre = padre
        self.simbolos = {}

    # ----------------------------
    # Función para agregar un símbolo a la tabla
    # ----------------------------
    def agregar(self, nombre, tipo, forma, tamano, linea):

        if nombre in self.simbolos:
            print(f"\033[31mError semántico en línea {linea}: '{nombre}' ya está declarado en este scope.\033[0m")
        else:
            self.simbolos[nombre] = {
                "tipo": tipo,
                "forma": forma,
                "tamano": tamano
            }
            # Solo para funciones, agrega campos de return
            if forma == "func":
                self.simbolos[nombre]["tiene_return"] = False
                self.simbolos[nombre]["return_con_valor"] = False

    # ----------------------------
    # Función para buscar un símbolo en la tabla
    # ----------------------------
    def buscar(self, nombre):
        if nombre in self.simbolos:
            return self.simbolos[nombre]
        elif self.padre:
            return self.padre.buscar(nombre)
        else:
            return None

    # ----------------------------
    # Función para actualizar el valor de un símbolo
    # ----------------------------
    def actualizar(self, nombre, valor):
        if nombre in self.simbolos:
            self.simbolos[nombre]["valor"] = valor
        elif self.padre:
            self.padre.actualizar(nombre, valor)
        else:
            print(f"\033[31mError semántico: Variable '{nombre}' no declarada.\033[0m")

    # ----------------------------
    # Función para imprimir la tabla de símbolos
    # ----------------------------
    def __str__(self):
        simbolos_str = "\n".join(
            f"{nombre} | {info['tipo']} | {info['forma']} | {info['tamano']}"
            for nombre, info in self.simbolos.items()
        )
        return f"Tabla de símbolos ({self.nombre}):\n{simbolos_str}"
    


# ----------------------------
# Función para generar la tabla de símbolos
# ----------------------------
def tabla(tree, imprime=True):
    tablas = [] # Lista para almacenar las tablas de símbolos
    stack = [] # Stack para manejar el contexto de las tablas

    # Recorrido preorden para construir la tabla de símbolos
    def recorrer_preorden(nodo, tabla_actual):
        if nodo.tipo == "programa": # Nodo raíz
            tabla_global = TablaSimbolos("global") # Crear tabla global
            tablas.append(tabla_global)
            stack.append(tabla_global)
            for hijo in nodo.hijos: # Recorrer los hijos del nodo raíz
                recorrer_preorden(hijo, tabla_global)
            stack.pop() # uso del stack para manejar el contexto
        elif nodo.tipo == "fun-decl":
            nombre_funcion = nodo.hijos[1].valor
            tipo_funcion = nodo.hijos[0].valor

            # Procesar argumentos de la función
            argumentos = []
            if len(nodo.hijos) > 2 and nodo.hijos[2].tipo == "parametros": # Verificar si hay parámetros
                if len(nodo.hijos[2].hijos) == 1 and nodo.hijos[2].hijos[0].hijos[0].valor == "void": 
                    # Caso especial: void main(void)
                    argumentos.append("void")
                else:
                    for param in nodo.hijos[2].hijos: 
                        if len(param.hijos) >= 1:  # Validar que el nodo param tiene al menos un hijo
                            tipo_param = param.hijos[0].valor  # Obtener el valor del nodo <tipo>
                            argumentos.append(tipo_param)
                        else:
                            print(f"\033[31mError semántico: Argumento inválido en la declaración de la función '{nombre_funcion}'.\033[0m")
            else:
                argumentos.append("void")  # Si no hay parámetros, se considera void

            # Crear representación de los argumentos
            args_str = "|".join(argumentos)

            # Agregar la función a la tabla actual
            tabla_actual.agregar(nombre_funcion, tipo_funcion, "func", args_str, 0)

            # Crear una nueva tabla de símbolos para la función
            tabla_funcion = TablaSimbolos(nombre_funcion, tabla_actual)
            tablas.append(tabla_funcion)
            stack.append(tabla_funcion) # Agregar la tabla de la función al stack

            # Agregar los argumentos a la tabla de la función
            if nodo.hijos[2].tipo == "parametros" and not (len(nodo.hijos[2].hijos) == 1 and nodo.hijos[2].hijos[0].hijos[0].valor == "void"):
                for param in nodo.hijos[2].hijos:
                    if len(param.hijos) >= 1:
                        tipo_param = param.hijos[0].valor  # Obtener el tipo del parámetro
                        nombre_param = param.valor  # Obtener el nombre del parámetro
                        tabla_funcion.agregar(nombre_param, tipo_param, "var", None, 0)

            # Recorrer el cuerpo de la función
            for hijo in nodo.hijos[3:]:
                recorrer_preorden(hijo, tabla_funcion)
            stack.pop()

        # Declaraciones de variables
        elif nodo.tipo == "var-decl":
            nombre_variable = nodo.valor
            tipo_variable = nodo.hijos[0].valor
            if len(nodo.hijos) > 1:  # Es un arreglo dado que tiene un tamaño
                tamano = int(nodo.hijos[1].valor)
                tabla_actual.agregar(nombre_variable, tipo_variable, "arr", tamano, 0)
            else:  # Es una variable normal
                tabla_actual.agregar(nombre_variable, tipo_variable, "var", None, 0)

        elif nodo.tipo == "array-decl":  # Manejo de declaraciones de arreglos
            nombre_arreglo = nodo.valor
            tipo_arreglo = nodo.hijos[0].valor
            tamano_arreglo = int(nodo.hijos[1].valor) if len(nodo.hijos) > 1 else None # Obtener el tamaño del arreglo
            if tamano_arreglo is None:
                print(f"\033[31mError semántico: El arreglo '{nombre_arreglo}' debe tener un tamaño especificado.\033[0m")
            else:
                tabla_actual.agregar(nombre_arreglo, tipo_arreglo, "arr", tamano_arreglo, 0)
        else:
            for hijo in nodo.hijos:
                recorrer_preorden(hijo, tabla_actual)

    recorrer_preorden(tree, None) # Recorrer el árbol sintáctico y construir la tabla de símbolos

    # Imprimir las tablas de símbolos si se solicita
    if imprime:
        for tabla in tablas:
            print(tabla)

    # Verificar que exista la función 'main' en la tabla global
    tabla_global = next((tabla for tabla in tablas if tabla.nombre == "global"), None)
    if tabla_global:
        simbolo_main = tabla_global.buscar("main")
        if not simbolo_main or simbolo_main["forma"] != "func":
            print("\033[31mError semántico: El programa no tiene una función principal 'main'.\033[0m")
    else:
        print("\033[31mError semántico: No se encontró la tabla de símbolos global.\033[0m")

    return tablas


# ----------------------------
# Función para realizar el análisis semántico
# ----------------------------
def semantica(tree, imprime=True):
    print("\033[32mIniciando análisis semántico\033[0m") # Mensaje de inicio en verde en consola
    tablas = tabla(tree, imprime) 
    contexto_funcion = [] # Lista para almacenar el contexto de la función actual
    def recorrer_posorden(nodo):
        
        # Verificar si el nodo es una declaración de función
        if nodo.tipo == "fun-decl":
            nombre_funcion = nodo.hijos[1].valor
            contexto_funcion.append(nombre_funcion)
            for hijo in nodo.hijos: # Recorrer los hijos del nodo
                recorrer_posorden(hijo)
            contexto_funcion.pop() # Regresar al contexto anterior
            return
        
        # Verificar si el nodo es un retorno
        elif nodo.tipo == "return-stmt":
            if contexto_funcion:
                nombre_funcion = contexto_funcion[-1] # Obtener el nombre de la función actual
                # Busca la función en la tabla global
                tabla_global = next((t for t in tablas if t.nombre == "global"), None)
                if tabla_global:
                    simbolo_func = tabla_global.buscar(nombre_funcion) 
                    if simbolo_func and simbolo_func["forma"] == "func":
                        simbolo_func["tiene_return"] = True # Indicar que la función tiene un return
                        if nodo.hijos:
                            simbolo_func["return_con_valor"] = True # Indicar que el return tiene un valor
            for hijo in nodo.hijos:
                recorrer_posorden(hijo)
            return

        # Verificar si el nodo es una asignación
        if nodo.tipo == "assign":
            # Procesar el lado izquierdo (variable) y derecho (valor asignado)
            izquierda = nodo.hijos[0].valor  # Nombre de la variable
            derecha = recorrer_posorden(nodo.hijos[1])  # Tipo del valor asignado

            # Buscar la variable en las tablas y actualizar su valor
            for tabla in reversed(tablas):
                simbolo = tabla.buscar(izquierda)
                if simbolo:
                    if simbolo["forma"] != "var": # Verificar si es una variable
                        print(f"\033[31mError semántico: '{izquierda}' no es una variable.\033[0m")
                        return "error"
                    if simbolo["tipo"] != derecha and derecha != "error": # Verificar si el tipo de la variable coincide con el tipo del valor asignado
                        print(f"\033[31mError semántico: Asignación incompatible entre {simbolo['tipo']} y {derecha}.\033[0m")
                        return "error"
                    # Actualizar el valor de la variable en la tabla de símbolos
                    if derecha == "int" and nodo.hijos[1].tipo == "num":
                        tabla.actualizar(izquierda, int(nodo.hijos[1].valor))
                    else:
                        tabla.actualizar(izquierda, nodo.hijos[1].valor)
                    return simbolo["tipo"]
            print(f"\033[31mError semántico: Variable '{izquierda}' no declarada.\033[0m")
            return "error"

        # Verificar si el nodo es acceso a un arreglo
        elif nodo.tipo == "array-access":
            nombre_arreglo = nodo.valor  # Nombre del arreglo
            indice = nodo.hijos[0]  # Nodo del índice al que se intenta acceder

            # Verificar si el índice es un número o un identificador
            if indice.tipo == "num":
                valor_indice = int(indice.valor)  # Convertir el índice a entero
            elif indice.tipo == "id":
                # Buscar el identificador en las tablas
                for tabla in reversed(tablas):
                    simbolo = tabla.buscar(indice.valor)
                    if simbolo:
                        if simbolo["tipo"] != "int": # Verificar que el tipo del índice sea 'int' ya sea un número o un identificador
                            print(f"\033[31mError semántico: El índice del arreglo '{nombre_arreglo}' debe ser de tipo 'int'.\033[0m")
                            return "error"
                        if simbolo.get("valor") is None:
                            print(f"\033[31mError semántico: El índice '{indice.valor}' no tiene un valor asignado.\033[0m")
                            return "error"
                        # Validar que el valor sea un número antes de convertirlo
                        if isinstance(simbolo["valor"], int):
                            valor_indice = simbolo["valor"]
                        else:
                            print(f"\033[31mError semántico: El índice '{indice.valor}' no contiene un valor numérico válido.\033[0m")
                            return "error"
                        break
                else:
                    print(f"\033[31mError semántico: Identificador '{indice.valor}' no declarado.\033[0m")
                    return "error"
            else:
                print(f"\033[31mError semántico: El índice del arreglo '{nombre_arreglo}' debe ser un número o un identificador de tipo 'int'.\033[0m")
                return "error"

            # Buscar el arreglo en las tablas
            for tabla in reversed(tablas):
                simbolo = tabla.buscar(nombre_arreglo)
                if simbolo:
                    if simbolo["forma"] != "arr": # Verificar si es un arreglo
                        print(f"\033[31mError semántico: '{nombre_arreglo}' no es un arreglo.\033[0m")
                        return "error"
                    tamano = simbolo["tamano"]
                    # Verificar que el índice esté dentro del rango
                    if valor_indice >= tamano+1:
                        print(f"\033[31mError semántico: Índice fuera de rango en el arreglo '{nombre_arreglo}'. Tamaño: {tamano}, Índice: {valor_indice}.\033[0m")
                        return "error"
                    return simbolo["tipo"]
            print(f"\033[31mError semántico: Arreglo '{nombre_arreglo}' no declarado.\033[0m")
            return "error"

        # Verificar si el nodo es una operación aritmética
        elif nodo.tipo == "addop" or nodo.tipo == "mulop":
            izquierda = recorrer_posorden(nodo.hijos[0]) 
            derecha = recorrer_posorden(nodo.hijos[1])
            if izquierda != "int" or derecha != "int": # Verificar que ambos operandos sean enteros
                print(f"\033[31mError semántico: Operación aritmética requiere tipos 'int'.\033[0m")
            return "int"

        # Verificar si el nodo es un identificador
        elif nodo.tipo == "id":
            for tabla in reversed(tablas):
                simbolo = tabla.buscar(nodo.valor)
                if simbolo:
                    # Verificar si es una función
                    if simbolo["forma"] == "func":
                        return simbolo["tipo"]
                    # Verificar si es un parámetro de la función actual
                    if simbolo["forma"] == "var" and simbolo.get("tamano") is None:
                        return simbolo["tipo"]
                    # Verificar si es una variable no inicializada
                    if simbolo.get("valor") is None:
                        print(f"\033[31mError semántico: Variable '{nodo.valor}' no inicializada.\033[0m")
                        return "error"
                    return simbolo["tipo"]
            # Verificar si es una función predefinida
            if nodo.valor in ["input", "output"]:
                return "void"  # Considerar que estas funciones tienen tipo 'void'
            print(f"\033[31mError semántico: Identificador '{nodo.valor}' no declarado.\033[0m")
            return "error"

        # Verificar si el nodo es un número
        elif nodo.tipo == "num":
            return "int"

        # Verificar si el nodo es una llamada a función
        elif nodo.tipo == "call":
            nombre_funcion = nodo.valor
            # Verificar si es una función predefinida
            if nombre_funcion in ["input", "output"]: # Devolver el tipo de la función predefinida del lenguaje
                return "void"  # Considerar que estas funciones tienen tipo 'void'

            # Buscar la función en las tablas
            for tabla in reversed(tablas):
                simbolo = tabla.buscar(nombre_funcion)
                if simbolo:
                    if simbolo["forma"] != "func":
                        print(f"\033[31mError semántico: '{nombre_funcion}' no es una función.\033[0m")
                        return "error"

                    # Obtener los parámetros declarados
                    parametros_declarados = simbolo["tamano"].split("|") if simbolo["tamano"] else []

                    # Localizar el nodo <arg-list> y procesar sus hijos
                    argumentos_llamada = []
                    for hijo in nodo.hijos:
                        if hijo.tipo == "arg-list":
                            for arg in hijo.hijos:  # Procesar los hijos del nodo <arg-list>
                                argumentos_llamada.append(recorrer_posorden(arg))

                    # Verificar que el número de argumentos coincida
                    if len(argumentos_llamada) != len(parametros_declarados):
                        print(f"\033[31mError semántico: Llamada a función '{nombre_funcion}' con un número incorrecto de argumentos. Esperados: {len(parametros_declarados)}, dados: {len(argumentos_llamada)}.\033[0m")
                        return "error"

                    # Verificar que los tipos de los argumentos coincidan
                    for i, (arg, param) in enumerate(zip(argumentos_llamada, parametros_declarados)):
                        if arg != param:
                            print(f"\033[31mError semántico: Tipo incorrecto en el argumento {i + 1} de la función '{nombre_funcion}'. Esperado: {param}, dado: {arg}.\033[0m")
                            return "error"

                    return simbolo["tipo"]

            # Si no se encuentra la función, generar un error
            print(f"\033[31mError semántico: Llamada a función '{nombre_funcion}' no declarada.\033[0m")
            return "error"

        
        else: # Recorrer los hijos del nodo
            for hijo in nodo.hijos:
                recorrer_posorden(hijo) # Recursión para procesar los hijos

    # Iniciar el recorrido postorden del árbol sintáctico
    recorrer_posorden(tree)
    
    # Verificar que todas las funciones de tipo 'int' tengan un return con valor
    tabla_global = next((t for t in tablas if t.nombre == "global"), None)
    if tabla_global:
        for nombre, simbolo in tabla_global.simbolos.items():
            if simbolo["forma"] == "func":
                if simbolo["tipo"] == "int": # Verificar si la función es de tipo 'int'
                    if not simbolo["tiene_return"] or not simbolo["return_con_valor"]: # Verificar si tiene un return con valor
                        print(f"\033[31mError semántico: La función '{nombre}' de tipo 'int' debe tener un 'return' con valor.\033[0m")
                elif simbolo["tipo"] == "void": # Verificar si la función es de tipo 'void'
                    if simbolo["return_con_valor"]: # Verificar si tiene un return con valor
                        print(f"\033[31mError semántico: La función '{nombre}' de tipo 'void' no puede retornar un valor.\033[0m")



# ----------------------------
# Función para manejar errores semánticos
# ----------------------------
def errorSemantico(mensaje):
    global programa, posicion, progLong
    from lexer import programa, posicion, progLong
    # Usa la posición pasada o la global si no se pasa
    if pos is None:
        pos = min(posicion, len(programa) - 1) if len(programa) > 0 else 0
    else:
        pos = min(pos, len(programa) - 1) if len(programa) > 0 else 0
    linea_actual = 1
    columna_actual = 1
    for i in range(pos):
        if programa[i] == '\n':
            linea_actual += 1
            columna_actual = 1
        else:
            columna_actual += 1
    lineas = programa.splitlines()
    linea_codigo = lineas[linea_actual - 1] if linea_actual - 1 < len(lineas) else ""
    print(f"\033[31mError semántico en línea {linea_actual}: {mensaje}\033[0m")
    print(f"{linea_codigo}")
