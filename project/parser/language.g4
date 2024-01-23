grammar language;

prog: EOL* (stmt EOL*)* EOF;

stmt: 'val' var '=' expr ';' #decl
    | 'print' expr ';' #print
    ;

expr: var #exprvar
    | val #exprval
    | map #exprmap
    | filter #exprfilter
    | intersection #exprintersection
    | concat #exprconcat
    | union #exprunion
    | star #exprstar
    | expr 'in' expr #in
    | 'not' expr #not
    |'(' expr ')' #exprparens
    ;

INT: [0]|([-]?([1-9][0-9]*));

var: ID;

ID: [a-zA-Z]( [a-zA-Z0-9_] )*;

STRING: '"' ~[\n;]* '"';

bool: 'true' | 'false';

path: STRING ;

val: STRING #string
    | INT #valint
    | bool #valbool
    | set #valset
    | graph #valgraph
    | set #valset
    | nodes #valnodes
    | edges #valedges
    | labels #vallabels
    | 'cfg' '('  STRING  ')' #lcfg
    | 'regex' '(' STRING ')' #regexp
    | '('expr ',' expr ')' #pair
    | '('expr ',' expr ',' expr ')' #triple
    ;

set: '{' val (',' val)* '}';

graph: var #graphname
    | 'set_start' '(' nodes ',' graph ')' #set_start
    | 'set_final' '(' nodes ',' graph ')' #set_final
    | 'add_start' '(' nodes ',' graph ')' #add_start
    | 'add_final' '(' nodes ',' graph ')' #add_final
    | 'load_graph' '(' STRING ')' #load_graph
    | 'load_from_file' '(' path ')' #load_from_file
    ;

labels: set #labelsset
    | 'get_labels' '(' graph ')' #get_labels
    ;

edges: set #edgesset
    | 'get_edges' '(' graph ')' #get_edges
    ;

nodes: set #nodeset
    | 'get_nodes' '(' graph ')' #get_nodes
    | 'get_start' '(' graph ')' #get_start
    | 'get_final' '(' graph ')' #get_final
    | 'get_reachable' '(' graph ')' #get_reachable
    ;

map: 'map' '(' lambda ',' expr ')';
filter: 'filter' '(' lambda ',' expr ')';

pattern: '(' pattern ')' #patparens
    | '(' pattern ',' pattern ')' #patpair
    | '(' pattern ',' pattern ',' pattern ')' #pattriple
    | ID #patname
    ;

lambda:
    | '[' pattern '->' expr ']'
    ;

intersection: 'intersect' '(' expr ',' expr ')';

concat: 'concat' '(' expr ',' expr ')';

union: 'union' '(' expr ',' expr ')';

star: 'star' '(' expr ')';

EOL: '\r'? '\n';
WS: ([ \t\r] | '/*' ~[\r\n]* '*/')+ -> skip;
