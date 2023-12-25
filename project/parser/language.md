# Язык запросов к графам

## Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool
  | Set_val of Set<val>
  | Graph of graph
  | Nodes of nodes
  | Edges of edges
  | Labels of labels

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_nodes of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход
  | Tuple of expr * expr         // пара
  | Triple of expr * expr * expr  // тройка
  | Regex of regex               // регулярное выражение
  | Cfg of cfg                   // контекстно-свободная грамматика

pattern =
    Var of var
    | pattern * pattern
    | pattern * pattern * pattern

lambda =
    Lambda of pattern * expr
```

Синтаксис языка в виде грамматики

```
prog --> stmt*

stmt --> val <var> = <expr>;
      |  print <expr>;

expr --> (<expr>)
    | <var>
    | <val>
    | <map>
    | <filter>
    | <intersect>
    | <concat>
    | <union>
    | <star>
    | (<expr>, <expr>)
    | (<expr>, <expr>, <expr>)

cfg --> cfg_from_text (<string>)

regex --> regex_from_text (<string>)


lower --> [a-z]
upper --> [A-Z]
digit --> [0-9]
non_zero_digit --> [1-9]
symbol --> [a-zA-Z0-9_\/]
var --> <lower> <symbol>*
string --> <symbol>*
int --> <non_zero_digit> <digit>*
bool --> true
    | false
set --> {<val>*}

val --> "<string>"
    | <int>
    | <bool>
    | <set_val>
    | <graph>
    | <nodes>
    | <edges>
    | <labels>
    | <regex>
    | <cfg>

graph --> load graph (<string>)
    | set_start (<set_val>, <graph>)
    | set_final (<set_val>, <graph>)
    | add_start (<set_val>, <graph>)
    | add_final (<set_val>, <graph>)
    | load_graph (<string>)
    | load_graph_from_file (<path>)


path --> <string>

nodes --> get_nodes (<graph>)
    | get_nodes (<graph>)
    | get_start (<graph>)
    | get_final (<graph>)
    | get_reachable (<graph>)

edges --> get_edges (<graph>)

labels --> get_labels (<graph>)

map --> map (<lambda>, <expr>)

filter --> filter (<lambda>, <expr>)

intersect --> intersect (<expr>, <expr>)

concat --> concat (<expr>, <expr>)

union --> union (<expr>, <expr>)

star --> star (<expr>)

pattern --> <var>
    | (<pattern>, <pattern>)
    | (<pattern>, <pattern>, <pattern>)

lambda --> lambda (<pattern>, <expr>)
```
Выразительные возможности лямбды должны позволять решать такие задачи как получение достижимых вершин, получение вершин из которых достижимы некоторые, получение пар вершин, между которыми существует путь, удовлетворяющий ограничению.

Пример запроса в некотором гипотетическом конкретном синтаксисе.

```
val g1 = load_graph ("wine"); /* загрузить граф wine */
val g2 = load_from_file ("/graphs/graph.dot"); /* загрузить граф из файла */

val grammar = CFG("S -> a S b | a b"); /* создать КС грамматику */

val g2 = set_start ({1,2,3}, set_final ({4,5,6}, g1)); /* Добавить в граф стартовые и финальные состояния */

val s = get_start (g1); /* получить стартовые состояния */

val inter = intersect (g1, g2); /* пересечение графов  */

```

Достижимые вершины для определенного множества стартовых вершин
```
val graph = set_start({1,2,3,4,5,6} ,load_graph("atom"));
val result  = map({(a, f) -> f}, get_reachible(graph));
```

Вершины удовлетворяющее
```
val cfg = CFG("S -> a S b | a b");
val graph = load_from_file ("/graphs/graph.dot");
val result = get_reachible(intersect(cfg, regex));
print(result);
```

вершины с общими номерами
```
val wine = load_graph("wine");
val cheese = load_graph("cheese");
val nodes = filter({l -> l in get_nodes(wine))}, get_nodes(cheese));
print(nodes);
```

## Правила вывода типов

Константы типизируются очевидным образом.

Тип переменной определяется типом выражения, с которым она связана.
```
[b(v)] => t
_________________
[Var (v)](b) => t
```

Загрузить можно только автомат.
```
_________________________
[Load (p)](b) => FA<int>
```

Установка финальных состояний, а так же добавление стартовых и финальных типизируется аналогично типизации установки стартовых, которая приведена ниже.
```
[s](b) => Set<t> ;  [e](b) => FA<t>
___________________________________
[Set_start (s, e)](b) => FA<t>


[s](b) => Set<t> ;  [e](b) => RSM<t>
____________________________________
[Set_start (s, e)](b) => RSM<t>

```

Получение финальных типизируется аналогично получению стартовых, правила для которого приведены ниже.
```
[e](b) => FA<t>
____________________________
[Get_start (e)](b) => Set<t>


[e](b) => RSM<t>
____________________________
[Get_start (e)](b) => Set<t>

```

```
[e](b) => FA<t>
__________________________________
[Get_reachable (e)](b) => Set<t*t>


[e](b) => RSM<t>
__________________________________
[Get_reachable (e)](b) => Set<t*t>

```

```
[e](b) => FA<t>
_______________________________
[Get_nodes (e)](b) => Set<t>


[e](b) => RSM<t>
_______________________________
[Get_nodes (e)](b) => Set<t>


[e](b) => FA<t>
______________________________________
[Get_edges (e)](b) => Set<t*string*t>


[e](b) => RSM<t>
______________________________________
[Get_edges (e)](b) => Set<t*string*t>

[e](b) => FA<t>
__________________________________
[Get_labels (e)](b) => Set<string>


[e](b) => RSM<t>
__________________________________
[Get_labels (e)](b) => Set<string>

```

Правила для ```map``` и ```filter``` традиционные.
```
[f](b) => t1 -> t2 ; [q](b) => Set<t1>
_______________________________________
[Map (f,q)](b) => Set<t2>


[f](b) => t1 -> bool ; [q](b) => Set<t1>
________________________________________
[Filter (f,q)](b) => Set<t1>
```

Пересечение для двух КС не определено.
```
[e1](b) => FA<t1> ;  [e2](b) => FA<t2>
______________________________________
[Intersect (e1, e2)](b) => FA<t1*t2>


[e1](b) => FA<t1> ;  [e2](b) => RSM<t2>
_______________________________________
[Intersect (e1, e2)](b) => RSM<t1*t2>


[e1](b) => RSM<t1> ;  [e2](b) => FA<t2>
_______________________________________
[Intersect (e1, e2)](b) => RSM<t1*t2>

```

Остальные операции над автоматами типизируются согласно формальных свойств классов языков.
```
[e1](b) => FA<t> ;  [e2](b) => FA<t>
_____________________________________
[Concat (e1, e2)](b) => FA<t>


[e1](b) => FA<t> ;  [e2](b) => RSM<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => FA<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => RSM<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>

```

```
[e1](b) => FA<t> ;  [e2](b) => FA<t>
______________________________________
[Union (e1, e2)](b) => FA<t>


[e1](b) => FA<t> ;  [e2](b) => RSM<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => FA<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => RSM<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>

```

```
[e](b) => FA<t>
______________________
[Star (e)](b) => FA<t>


[e](b) => RSM<t>
______________________
[Star (e)](b) => RSM<t>

```

```
[e](b) => string
________________________
[Smb (e)](b) => FA<int>

```


## Динамическая семантика языка запросов

Связывание переопределяет имя.

```
[e](b1) => x,b2
_____________________________________
[Bind (v, e)](b1) => (), (b1(v) <= x)

```

Загрузить можно только автомат и у него все вершины будут стартовыми и финальными.

```
[p](b1) => s,b2 ; read_fa_from_file s => fa
_____________________________________
[Load (p)](b1) => (fa | fa.start = fa.nodes, fa.final = fa.nodes), b1

```

## Задача
Решение задачи оформляется в виде .md файла в репозитории. Как вариант --- сделать описание языка частью readme. В качестве примера описания языка можно использовать, например, [спецификацию F#](https://fsharp.org/specs/language-spec/4.1/FSharpSpec-4.1-latest.pdf) или [спецификацию Java](https://docs.oracle.com/javase/specs/jls/se11/html/index.html).
 - [ ] Расширить абстрактный синтаксис в местах, указанных в его описании (```val```, ```lambda```)
 - [ ] Описать конкретный синтаксис языка запросов в виде грамматики (на основе получившегося абстрактного синтаксиса). При необходимости выделить лексическую спецификацию (описание лексики). Постарайтесь, чтобы, с одной стороны, синтаксис был достаточно уникальным, но с другой, достаточно разумным и на получившемся языке можно было писать без сильной боли.
 - [ ] Привести примеры скриптов на получившемся языке. Не забыть описать, что же эти скрипты делают.
