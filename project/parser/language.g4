grammar language;

prog: EOL* stmt* EOF;

stmt: 'val' var '=' expr ';'
    | 'print' expr ';'
    ;

expr: '(' expr ')'
    | var
    | val
    | map
    | filter
    | intersection
    | concat
    | union
    | star
    | '('expr ',' expr ')'
    | '('expr ',' expr ',' expr ')'
    | expr 'in' expr
    | 'not' expr
    ;

INT: [0]|([-]?([1-9][0-9]*));

var: ID;

ID: [a-zA-Z]( [a-zA-Z0-9_] )*;

String: '"' ~[\n]* '"' ;

bool: 'true' | 'false';

path: String ;

val: String
    | INT
    | bool
    | set
    | graph
    | set
    | nodes
    | edges
    | labels
    | CFG
    | REGEX
    ;

set: '{' val (',' val)* '}';

graph: var
    | 'set_start' '(' nodes ',' graph ')'
    | 'set_final' '(' nodes ',' graph ')'
    | 'add_start' '(' nodes ',' graph ')'
    | 'add_final' '(' nodes ',' graph ')'
    | 'load_graph' '(' String ')'
    | 'load_from_file' '(' path ')';

labels: set
    | 'get_labels' '(' graph ')';

edges: set
    | 'get_edges' '(' graph ')';

nodes: set
    | 'get_nodes' '(' graph ')'
    | 'get_start' '(' graph ')'
    | 'get_final' '(' graph ')'
    | 'get_reachable' '(' graph ')';

map: 'map' '(' lambda ',' expr ')';
filter: 'filter' '(' lambda ',' expr ')';

pattern: var
    | '(' pattern ')'
    | '(' pattern ',' pattern ')'
    | '(' pattern ',' pattern ',' pattern ')'
    ;

lambda:
    | '{' pattern '->' expr '}'
    ;

intersection: 'intersect' '(' expr ',' expr ')';

concat: 'concat' '(' expr ',' expr ')';

union: 'union' '(' expr ',' expr ')';

star: 'star' '(' expr ')';

CFG: 'CFG' '('  String  ')';
REGEX: 'REGEX' '(' String ')';
EOL: '\r'? '\n';
WS: ([ \t\r] | '/*' ~[\r\n]* '*/')+ -> skip;
