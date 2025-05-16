# Lenguaje C- en EBNF

### 1. `program = declaration-list `
El programa comienza con una lista de declaraciones.

### 2. `declaration-list = { declaration } `
Una o más declaraciones consecutivas.

### 3. `declaration = var-declaration | fun-declaration `
Una declaración puede ser de variable o de función.

### 4. `var-declaration = type-specifier ID ( ";" | "[" NUM "]" ";" ) `
Declara una variable escalar o un arreglo.

### 5. `type-specifier = "int" | "void" `
Solo se permiten los tipos básicos `int` y `void`.

### 6. `fun-declaration = type-specifier ID "(" params ")" compound-stmt `
Define una función con tipo, nombre, parámetros y cuerpo.

### 7. `params = param-list | "void" `
Una función puede tener parámetros o no tener ninguno.

### 8. `param-list = param { "," param } `
Lista de parámetros separados por comas.

### 9. `param = type-specifier ID [ "[]" ] `
Parámetro escalar o arreglo (pasado por referencia).

### 10. `compound-stmt = "{" local-declarations statement-list "}" `
Bloque de código con declaraciones locales y sentencias.

### 11. `local-declarations = { var-declaration } `
Cero o más declaraciones de variables locales.

### 12. `statement-list = { statement } `
Cero o más sentencias en un bloque.

### 13. `statement = expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt `
Tipos de sentencias que puede tener el lenguaje.

### 14. `expression-stmt = expression ";" | ";" `
Sentencia de expresión o una línea vacía.

### 15. `selection-stmt = "if" "(" expression ")" statement | "if" "(" expression ")" statement "else" statement `
Sentencia condicional `if` con o sin `else`.

### 16. `iteration-stmt = "while" "(" expression ")" statement `
Bucle `while` clásico.

### 17. `return-stmt = "return" [ expression ] ";" `
Sentencia de retorno con o sin valor.

### 18. `expression = var "=" expression | simple-expression `
Asignación o expresión sin asignar.

### 19. `var = ID [ "[" expression "]" ] `
Variable escalar o acceso a arreglo.

### 20. `simple-expression = additive-expression [ relop additive-expression ] `
Expresión con o sin comparación.

### 21. `relop = "<=" | "<" | ">" | ">=" | "==" | "!=" `
Operadores relacionales.

### 22. `additive-expression = term { addop term } `
Expresiones con sumas o restas.

### 23. `addop = "+" | "-" `
Operadores de suma y resta.

### 24. `term = factor { mulop factor } `
Multiplicación y división entre factores.

### 25. `mulop = "*" | "/" `
Operadores multiplicativos.

### 26. `factor = "(" expression ")" | var | call | NUM `
Valores básicos o expresiones entre paréntesis.

### 27. `call = ID "(" args ")" `
Llamada a función.

### 28. `args = arg-list | empty `
Argumentos de la función, pueden estar vacíos.

### 29. `arg-list = expression { "," expression } `
Lista de expresiones como argumentos.

---
