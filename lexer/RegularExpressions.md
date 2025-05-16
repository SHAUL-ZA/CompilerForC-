| Expresión Regular         | TokenType         | Descripción                                               |
|---------------------------|-------------------|-----------------------------------------------------------|
| `^\d+`                    | NUM               | Números enteros (uno o más dígitos).                     |
| `^\+`                     | PLUS              | Operador suma `+`.                                       |
| `^-`                      | MINUS             | Operador resta `-`.                                      |
| `^\*`                     | TIMES             | Operador multiplicación `*`.                             |
| `^/`                      | DIVIDE            | Operador división `/`.                                   |
| `^<=`                     | LTE               | Menor o igual `<=`.                                      |
| `^<`                      | LT                | Menor que `<`.                                           |
| `^>=`                     | GTE               | Mayor o igual `>=`.                                      |
| `^>`                      | GT                | Mayor que `>`.                                           |
| `^==`                     | EQ                | Igualdad `==`.                                           |
| `^!=`                     | NEQ               | Diferente `!=`.                                          |
| `^=`                      | ASSIGN            | Asignación `=`.                                          |
| `^;`                      | SEMI              | Punto y coma `;`.                                        |
| `^,`                      | COMMA             | Coma `,`.                                                |
| `^\(`                    | LPAREN            | Paréntesis izquierdo `(`.                                |
| `^\)`                    | RPAREN            | Paréntesis derecho `)`.                                  |
| `^{`                      | LBRACE            | Llave izquierda `{`.                                     |
| `^}`                      | RBRACE            | Llave derecha `}`.                                       |
| `^\[`                    | LBRACKET          | Corchete izquierdo `[`.                                  |
| `^\]`                    | RBRACKET          | Corchete derecho `]`.                                    |
| `^\s+`                   | (ignorado)        | Espacios en blanco o saltos de línea (no generan token). |
| `^/\*[\s\S]*?\*/`         | COMMENT           | Comentarios multilínea `/* ... */`.                      |
