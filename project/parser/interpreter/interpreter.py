import sys

from antlr4 import ParserRuleContext

from project.parser.interpreter.automations import *
from project.parser.interpreter.pat import *
from project.parser.languageParser import languageParser
from project.parser.languageVisitor import languageVisitor
from project.task_6 import cfg_from_file


class InterpreterVisitor(languageVisitor):
    def __init__(self):
        self.local_set = [{}]
        self.output = ""

    def add_to_scope(self, local_stacks: dict):
        self.local_set.append(local_stacks)

    def pop_from_scope(self):
        if len(self.local_set) <= 1:
            raise RuntimeError("Forbidden to pop from global scope")
        self.local_set.pop()

    def set_var(self, variable: str, value):
        self.local_set[-1][variable] = value

    def find_var(self, var: str):
        for local_stack in reversed(self.local_set):
            if var in local_stack:
                return local_stack[var]
        raise RuntimeError(f"Cannot find variable {var}")

    @staticmethod
    def get_string(ctx: ParserRuleContext):
        string = ""
        for token in ctx.getChildren():
            string += str(token)
        return string

    def visitProg(self, ctx: languageParser.ProgContext):
        return self.visitChildren(ctx)

    def visitDecl(self, ctx: languageParser.DeclContext):
        var = self.get_string(ctx.var())
        value = self.visit(ctx.expr())
        self.set_var(var, value)

    def visitPrint(self, ctx: languageParser.PrintContext):
        value = self.visit(ctx.expr())
        sys.stdout.write(str(value) + "\n")

    def visitPatparens(self, ctx: languageParser.PatparensContext):
        return self.visit(ctx.var())

    def visitExprparens(self, ctx: languageParser.ExprparensContext):
        return self.visit(ctx.expr())

    def visitNot(self, ctx: languageParser.NotContext):
        result = self.visit(ctx.expr())
        if not isinstance(result, bool):
            raise RuntimeError(f"Expected boolean, but found: {type(result)}")
        return not result

    def visitBool(self, ctx: languageParser.BoolContext):
        return str(ctx.getChild(0)) == "true"

    def visitString(self, ctx: languageParser.StringContext):
        return ctx.STRING().getText()[1:-1]

    def visitValint(self, ctx: languageParser.ValintContext):
        return int(self.get_string(ctx))

    def visitSet(self, ctx: languageParser.SetContext):
        return Set(set(self.visit(child) for child in ctx.val()))

    def visitVar(self, ctx: languageParser.VarContext):
        return self.find_var(self.get_string(ctx))

    def visitRegexp(self, ctx: languageParser.RegexpContext):
        return Automation.from_str(self.get_string(ctx)[7:-2])

    def visitLcfg(self, ctx: languageParser.LcfgContext):
        return ContextFreeGrammar.from_str(self.get_string(ctx)[5:-2])

    def visitPair(self, ctx: languageParser.PairContext):
        fst = self.visit(ctx.expr(0))
        snd = self.visit(ctx.expr(1))
        return Pair(fst, snd)

    def visitTriple(self, ctx: languageParser.TripleContext):
        fst = self.visit(ctx.expr(0))
        snd = self.visit(ctx.expr(1))
        thd = self.visit(ctx.expr(2))
        return Triple(fst, snd, thd)

    def visitIn(self, ctx: languageParser.InContext):
        value = self.visit(ctx.expr(0))
        set_expr = self.visit(ctx.expr(1))
        if not isinstance(set_expr, Set):
            raise RuntimeError(f"Expected set, but found: {type(set_expr)}")
        return value in set_expr

    def visitLoad_graph(self, ctx: languageParser.Load_graphContext):
        name = self.get_string(ctx)[12:-2]
        return Automation.load(name)

    def visitPath(self, ctx: languageParser.PathContext):
        return self.get_string(ctx)

    def visitLoad_from_file(self, ctx: languageParser.Load_from_fileContext):
        name = self.visit(ctx.path())
        return cfg_from_file(name)

    def visitPatname(self, ctx: languageParser.PatnameContext):
        return PatVar(self.get_string(ctx))

    def visitPatpair(self, ctx: languageParser.PatpairContext):
        fst = self.visit(ctx.pattern(0))
        snd = self.visit(ctx.pattern(1))
        return PatPair(fst, snd)

    def visitPattriple(self, ctx: languageParser.PattripleContext):
        fst = self.visit(ctx.pattern(0))
        snd = self.visit(ctx.pattern(1))
        thd = self.visit(ctx.pattern(2))
        return PatTriple(fst, snd, thd)

    def visitLambda(self, ctx: languageParser.LambdaContext):
        pat = self.visit(ctx.pattern())

        def lam():
            v = self.visit(ctx.expr())
            return v

        return pat, lam

    def visitMap(self, ctx: languageParser.MapContext):
        pat, lam = self.visit(ctx.lambda_())
        elems: Set = self.visit(ctx.expr())
        if not isinstance(elems, Set):
            raise RuntimeError(f"Expected set, but found: {type(elems)}")
        res = set()
        for elem in elems.elements:
            self.add_to_scope(match(pat, elem))
            res.add(lam())
            self.pop_from_scope()
        return Set(res)

    def visitFilter(self, ctx: languageParser.FilterContext):
        pat, lam = self.visit(ctx.lambda_())
        elems: Set = self.visit(ctx.expr())
        if not isinstance(elems, Set):
            raise RuntimeError(f"Expected set, but found: {type(elems)}")
        res = set()
        for elem in elems.elements:
            self.add_to_scope(match(pat, elem))
            lam_res = lam()
            if not isinstance(lam_res, bool):
                raise RuntimeError(f"Expected boolean, but found: {type(lam_res)}")
            if lam_res:
                res.add(elem)
            self.pop_from_scope()
        return Set(res)

    def visitSet_start(self, ctx: languageParser.Set_startContext):
        automation: Automation = self.visit(ctx.graph())
        arg2 = self.visit(ctx.nodes())
        return automation.set_start(arg2)

    def visitSet_final(self, ctx: languageParser.Set_finalContext):
        automation: Automation = self.visit(ctx.graph())
        arg2 = self.visit(ctx.nodes())
        return automation.set_final(arg2)

    def visitAdd_start(self, ctx: languageParser.Add_startContext):
        automation: Automation = self.visit(ctx.graph())
        arg2 = self.visit(ctx.nodes())
        return automation.add_start(arg2)

    def visitAdd_final(self, ctx: languageParser.Add_finalContext):
        automation: Automation = self.visit(ctx.graph())
        arg2 = self.visit(ctx.nodes())
        return automation.add_final(arg2)

    def visitGet_start(self, ctx: languageParser.Get_startContext):
        automation: Automation = self.visit(ctx.graph())
        return automation.get_start()

    def visitGet_final(self, ctx: languageParser.Get_finalContext):
        automation: Automation = self.visit(ctx.graph())
        return automation.get_final()

    def visitGet_reachable(self, ctx: languageParser.Get_reachableContext):
        automation: Automation = self.visit(ctx.graph())
        return automation.get_reachable()

    def visitGet_edges(self, ctx: languageParser.Get_edgesContext):
        automation: Automation = self.visit(ctx.graph())
        return automation.get_edges()

    def visitGet_nodes(self, ctx: languageParser.Get_nodesContext):
        automation: Automation = self.visit(ctx.graph())
        return automation.get_nodes()

    def visitGet_labels(self, ctx: languageParser.Get_labelsContext):
        automation: Automation = self.visit(ctx.graph())
        return automation.get_labels()

    def visitConcat(self, ctx: languageParser.ConcatContext):
        automation1: Automation = self.visit(ctx.expr(0))
        automation2: Automation = self.visit(ctx.expr(1))
        return automation1.concat(automation2)

    def visitUnion(self, ctx: languageParser.UnionContext):
        automation1: Automation = self.visit(ctx.expr(0))
        automation2: Automation = self.visit(ctx.expr(1))
        return automation1.union(automation2)

    def visitIntersection(self, ctx: languageParser.IntersectionContext):
        automation1: Automation = self.visit(ctx.expr(0))
        automation2: Automation = self.visit(ctx.expr(1))
        return automation1.intersect(automation2)

    def visitStar(self, ctx: languageParser.StarContext):
        automation: Automation = self.visit(ctx.expr())
        return automation.kleene()
