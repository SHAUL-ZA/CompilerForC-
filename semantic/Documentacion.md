# Proyecto 3: Analizador Semántico
### _Shaul Zayat Askenazi | A01783240_

## Construcción y Uso de la Tabla de Símbolos


La **tabla de símbolos** es una estructura fundamental en el análisis semántico de un compilador. Su función principal es almacenar información sobre los identificadores (variables, funciones, arreglos, parámetros, etc.) que aparecen en el código fuente, permitiendo así verificar reglas semánticas como declaraciones, tipos, ámbitos y usos correctos.

---

### ¿Cómo se construye la tabla de símbolos?

La tabla de símbolos se construye durante un recorrido preorden del árbol de sintaxis abstracta (AST):

1. **Inicialización**:  
   Se crea una tabla global que representa el ámbito global del programa.

2. **Recorrido del AST**:  
   - Al encontrar una declaración de función, se agrega a la tabla global y se crea una nueva tabla para el ámbito local de esa función.
   - Al encontrar una declaración de variable o arreglo, se agrega a la tabla del ámbito actual.
   - Los parámetros de funciones se agregan a la tabla local de la función.

3. **Jerarquía de ámbitos**:  
   Cada tabla puede tener una referencia a su tabla padre, permitiendo búsquedas recursivas para soportar ámbitos anidados.

---

### ¿Qué información se guarda en la tabla de símbolos?

Cada entrada de la tabla de símbolos es un diccionario con información relevante sobre el identificador. Los campos principales son:

- **nombre**: El nombre del identificador (variable, función, arreglo, parámetro).
- **tipo**: El tipo de dato (por ejemplo, `int`, `void`).
- **forma**: El tipo de símbolo (`var` para variable, `arr` para arreglo, `func` para función).
- **tamano**:  
  - Para arreglos, indica el tamaño.  
  - Para funciones, puede almacenar la lista de tipos de parámetros como un string (por ejemplo, `"int|int|void"`).
- **valor**: (opcional) El valor actual de la variable, si ha sido asignado.
- **tiene_return** y **return_con_valor**: (solo para funciones) Flags para verificar si la función tiene un `return` y si ese `return` tiene valor.
- **pos**: (opcional) La posición en el código fuente donde se declaró el identificador, útil para reportar errores precisos.

---

### ¿Qué funciones tiene la clase `TablaSimbolos`?

- **agregar(nombre, tipo, forma, tamano, linea)**  
  Agrega un nuevo símbolo a la tabla. Si el nombre ya existe en el ámbito actual, reporta un error. Inicializa los campos especiales para funciones.

- **buscar(nombre)**  
  Busca un símbolo en la tabla actual. Si no lo encuentra, busca recursivamente en la tabla padre (soporte para ámbitos anidados).

- **actualizar(nombre, valor)**  
  Actualiza el valor de una variable ya declarada. Si no existe en el ámbito actual, busca en los ámbitos superiores.

- **__str__()**  
  Devuelve una representación en texto de la tabla de símbolos, útil para depuración.

---

### ¿Por qué se guarda esa información?

- **nombre**: Para identificar el símbolo y evitar duplicados en el mismo ámbito.
- **tipo**: Para verificar compatibilidad de tipos en asignaciones, operaciones y llamadas a funciones.
- **forma**: Para distinguir entre variables, arreglos y funciones, ya que tienen reglas semánticas distintas.
- **tamano**:  
  - Para arreglos, permite validar accesos y rangos.  
  - Para funciones, permite validar el número y tipo de argumentos en llamadas.
- **valor**: Permite detectar el uso de variables no inicializadas y realizar inferencia de tipos.
- **tiene_return / return_con_valor**: Permite verificar que las funciones cumplen con las reglas de retorno según su tipo.


---

### Ejemplo de uso

Cuando el compilador encuentra una declaración como:
```c
int suma(int a, int b) { ... }
```
Se agrega a la tabla global:
- nombre: `"suma"`
- tipo: `"int"`
- forma: `"func"`
- tamano: `"int|int"` (tipos de parámetros)
- tiene_return: `False` (no se imprime)
- return_con_valor: `False` (no se imprime)

Y en la tabla local de la función:
- nombre: `"a"`, tipo: `"int"`, forma: `"var"`
- nombre: `"b"`, tipo: `"int"`, forma: `"var"`

---

### En síntesis

La tabla de símbolos es esencial para:
- Detectar declaraciones duplicadas.
- Verificar tipos y usos correctos de identificadores.
- Soportar ámbitos y visibilidad.
- Reportar errores semánticos precisos.

Su construcción y uso sistemático permiten que el compilador garantice la validez semántica del programa fuente antes de la generación de código o interpretación.


## Chequeo de Tipos en el Analizador Semántico


El **chequeo de tipos** es el proceso mediante el cual el analizador semántico verifica que las operaciones y asignaciones en el programa sean válidas según los tipos de datos definidos. Esto previene errores como sumar un entero con un arreglo, asignar un valor de tipo incorrecto a una variable, o llamar a una función con argumentos de tipos incompatibles, etc.

---

### ¿Cómo se realiza el chequeo de tipos en este analizador?

#### 1. Recorrido del AST

El chequeo de tipos se realiza durante un **recorrido postorden** del árbol de sintaxis abstracta (AST). Para cada nodo relevante, se verifica que los tipos de sus hijos y de los símbolos involucrados sean compatibles con la operación.

---

#### 2. Chequeo en asignaciones

Cuando se encuentra un nodo de tipo `"assign"`:
- Se obtiene el nombre de la variable (lado izquierdo) y el tipo del valor asignado (lado derecho).
- Se busca la variable en la tabla de símbolos.
- Se verifica:
  - Que la variable exista y sea de tipo `"var"`.
  - Que el tipo de la variable coincida con el tipo del valor asignado.
- Si todo es correcto, se actualiza el valor de la variable.

**Ejemplo de error detectado:**  
Asignar un valor de tipo `void` a una variable de tipo `int`.

---

#### 3. Chequeo en operaciones aritméticas

Para nodos de tipo `"addop"` o `"mulop"`:
- Se evalúan recursivamente los tipos de los operandos izquierdo y derecho.
- Se verifica que ambos sean de tipo `"int"`.
- Si alguno no es entero, se reporta un error semántico.

**Ejemplo de error detectado:**  
Sumar un entero con una variable no inicializada.

---

#### 4. Chequeo en acceso a arreglos

Para nodos de tipo `"array-access"`:
- Se verifica que el índice sea de tipo `"int"` (ya sea un número o una variable de tipo entero).
- Se verifica que el índice esté dentro del rango permitido por el tamaño del arreglo.
- Se verifica que el identificador del arreglo exista y sea de tipo `"arr"`.

**Ejemplo de error detectado:**  
Acceder a un arreglo con un índice de tipo `void` o fuera de rango.

---

#### 5. Chequeo en llamadas a funciones

Para nodos de tipo `"call"`:
- Se busca la función en la tabla de símbolos.
- Se obtiene la lista de tipos de parámetros declarados.
- Se evalúan los tipos de los argumentos pasados en la llamada.
- Se verifica:
  - Que el número de argumentos coincida con el número de parámetros.
  - Que los tipos de los argumentos coincidan con los tipos de los parámetros.
- Si todo es correcto, se devuelve el tipo de retorno de la función.

**Ejemplo de error detectado:**  
Llamar a una función con un número incorrecto de argumentos o con tipos incompatibles.

---

#### 6. Chequeo en identificadores y variables

Para nodos de tipo `"id"`:
- Se busca el identificador en la tabla de símbolos.
- Se verifica que esté declarado y, si es una variable, que esté inicializada antes de usarse.

**Ejemplo de error detectado:**  
Uso de una variable no declarada o no inicializada.

---

#### 7. Chequeo en sentencias de retorno

Para nodos de tipo `"return-stmt"`:
- Se verifica que las funciones de tipo `int` tengan un `return` con valor.
- Se verifica que las funciones de tipo `void` no tengan un `return` con valor (pueden no tener `return`).

---




### En síntesis

El chequeo de tipos garantiza que el programa sea **semánticamente correcto** antes de su ejecución o compilación final. Previene errores de ejecución, asegura la coherencia de los datos y ayuda a detectar errores lógicos en el código fuente.

- El chequeo de tipos se realiza recorriendo el AST y consultando la tabla de símbolos.
- Se verifica la compatibilidad de tipos en asignaciones, operaciones, accesos a arreglos, llamadas a funciones y retornos.
- Los errores de tipo se reportan con mensajes claros, indicando la causa y el contexto del error.

<br><br><br>

# Reglas de Inferencia

### Suma de Enteros

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 + e_2 : \text{Int}}
$$

**Descripción**:  
Si se puede inferir que `e₁` es de tipo `Int` y que `e₂` también es de tipo `Int`, entonces se concluye que la expresión `e₁ + e₂` es de tipo `Int`.

**Contexto de uso**:  
Esta regla se permite verificar que las operaciones aritméticas se realizan entre operandos compatibles.

**Ejemplo**:

```plaintext
Entrada: 3 + 5  
Inferencia: ⊢ 3 : Int, ⊢ 5 : Int ⊢ 3 + 5 : Int  
Resultado: Int
```

---

### Resta de Enteros

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 - e_2 : \text{Int}}
$$

**Descripción**:  
Si `e₁` y `e₂` son expresiones del tipo `Int`, entonces la expresión `e₁ - e₂` se infiere como de tipo `Int`.

**Ejemplo**:

```plaintext
Entrada: 10 - 7  
Inferencia: ⊢ 10 : Int, ⊢ 7 : Int ⊢ 10 - 7 : Int  
Resultado: Int
```

---

### Multiplicación de Enteros

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 * e_2 : \text{Int}}
$$

**Descripción**:  
Dada la inferencia de que `e₁` y `e₂` son de tipo `Int`, se deduce que `e₁ * e₂` también es de tipo `Int`.

**Ejemplo**:

```plaintext
Entrada: 4 * 6
Inferencia: ⊢ 4 : Int, ⊢ 6 : Int ⊢ 4 * 6 : Int
Resultado: Int
```

---

### División de Enteros

$$
\frac{\;\vdash e_1 : \text{Int} ,\vdash e_2 : \text{Int} \quad \;}{\vdash e_1 / e_2 : \text{Int}}
$$

**Descripción**:  
Si `e₁` y `e₂` son de tipo `Int` y `e₂` no es cero, entonces la división `e₁ / e₂` es una operación válida y su tipo es `Int`.

**Ejemplo**:

```plaintext
Entrada: 12 / 3  
Inferencia: ⊢ 12 : Int, ⊢ 3 : Int ⊢ 12 / 3 : Int  
Resultado: Int
```

---


### Reglas de Inferencia Semántica — Operadores Relacionales

### Menor que `<`

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 < e_2 : \text{Int}}
$$

**Ejemplo**:

```plaintext
Entrada: 3 < 7
Inferencia: ⊢ 3 : Int, ⊢ 7 : Int ⊢ 3 < 7 : int
Resultado: int 
```

---

### Menor o igual que `<=`

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 \leq e_2 : \text{Int}}
$$

**Ejemplo**:

```plaintext
Entrada: 5 <= 5
Inferencia: ⊢ 5 : Int, ⊢ 5 : Int ⊢ 5 <= 5 : int
Resultado: int
```

---

### Mayor que `>`

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 > e_2 : \text{Int}}
$$

**Ejemplo**:

```plaintext
Entrada: 10 > 2
Inferencia: ⊢ 10 : Int, ⊢ 2 : Int ⊢ 10 > 2 : int
Resultado: int 
```

---

### Mayor o igual que `>=`

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 \geq e_2 : \text{Int}}
$$

**Ejemplo**:

```plaintext
Entrada: 8 >= 3
Inferencia: ⊢ 8 : Int, ⊢ 3 : Int ⊢ 8 >= 3 : int
Resultado: int 
```

---

### Distinto de `!=`

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 != e_2 : \text{Int}}
$$

**Ejemplo**:

```plaintext
Entrada: 4 != 9
Inferencia: ⊢ 4 : Int, ⊢ 9 : Int ⊢ 4 != 9 : int
Resultado: int 
```

---

### Igual a `==`

$$
\frac{\;\vdash e_1 : \text{Int} \quad \vdash e_2 : \text{Int}\;}{\vdash e_1 == e_2 : \text{Int}}
$$

**Ejemplo**:

```plaintext
Entrada: 6 == 6
Inferencia: ⊢ 6 : Int, ⊢ 6 : Int ⊢ 6 == 6 : int
Resultado: int 
```

---


## Regla de Inferencia Semántica — Variables

### Evaluación de una variable en un entorno

$$
\frac{\;\vdash [a : \text{Int}] \quad \vdash O(a) : \text{Int}\;}{\vdash a : \text{Int}}
$$

Esta regla indica que:

> Si en el entorno se ha declarado que la variable `a` tiene tipo `Int`,  
> y además el valor asociado a `a` en el entorno (es decir, `O(a)`) es de tipo `Int`,  
> entonces se puede inferir que `a` es de tipo `Int`.

---

### Ejemplo

Supongamos el siguiente entorno:

```plaintext
Entorno: [a : Int]
Valores actuales: O(a) = 42
```

### Regla de Inferencia Semántica — Acceso a un Elemento de Arreglo

### Acceso por índice a un arreglo de enteros

$$
\frac{\;\vdash [a : \text{Int}[]] \quad \vdash e : \text{Int}\;}{\vdash a[e] : \text{Int}}
$$

Esta regla establece que:

> Si `a` es un arreglo de enteros (`Int[]`) y se accede con un índice `e` de tipo `Int`,  
> entonces el resultado de `a[e]` es un valor de tipo `Int`.

---

### Ejemplo

Supongamos el siguiente entorno:

```plaintext
Entorno: [a : Int[]]
Valores actuales: a = [10, 20, 30], e = 1
```

## Reglas de Inferencia Semántica — Evaluación de Funciones

### Función que retorna un entero (`Int`)

$$
\frac{\;O\vdash [f : \text{Int}] \quad \vdash O(f) : \text{Int}\;}{\vdash f : \text{Int}}
$$

Esta regla indica que:

> Si en el entorno `f` está declarada como una función de retorno `Int`,  
> y el valor actual de `f` también es de tipo `Int`,  
> entonces `f` se puede usar como una expresión de tipo `Int`.

---

#### Ejemplo

```plaintext
Entorno: [f : Int]
Valores actuales: O(f) = 7
```

## Regla de Inferencia Semántica — Función sin Retorno (`void`)

### Evaluación de una función declarada como `void`

$$
\frac{\;\vdash [f : \text{void}] \quad \vdash O(f) : \text{void}\;}{\vdash f : \text{void}}
$$

Esta regla establece que:

> Si una función `f` está declarada en el entorno como de tipo `void`  
> y su valor actual (`O(f)`) también es de tipo `void`,  
> entonces se puede inferir que `f` es de tipo `void`.

---

### Ejemplo

```plaintext
Entorno: [f : void]
Valores actuales: O(f) = void
```

## Reglas de Inferencia Semántica — Llamadas a Funciones

### Función que retorna `Int` con argumento `Int`

$$
\frac{\;O\vdash O(f) : \text{Int}  ,e : \text{Int}\;}{\vdash f(e) : \text{Int}}
$$

Esta regla establece que:

> Si `f` es una función que espera un argumento entero  
> y retorna un entero (`Int`), y si el argumento `e` también es de tipo `Int`,  
> entonces la llamada `f(e)` es válida y su tipo es `Int`.

---

#### Ejemplo

```plaintext
Entorno: O(f) : Int
Argumento: e = 5, tipo: Int
```

## Regla de Inferencia Semántica — Llamada a Función `void`

### Evaluación de una función `void` sin argumentos

$$
\frac{\;O\vdash O(f) : \text{void}\;}{\vdash f() : \text{void}}
$$

Esta regla indica que:

> Si el entorno determina que `f` es una función de tipo `void` (sin valor de retorno),  
> entonces la llamada `f()` es válida y también es de tipo `void`.

---

### Ejemplo

```plaintext
Entorno: O(f) = void
```