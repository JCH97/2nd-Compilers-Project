from .pycompiler import Grammar, Item
from .automata import State
from .utils import ContainerSet


class GrammarHelp:
    @staticmethod
    def compute_local_first(firsts, alpha):
        first_alpha = ContainerSet()
        try:
            alpha_is_epsilon = alpha.IsEpsilon
        except:
            alpha_is_epsilon = False
        
        if alpha_is_epsilon:
            first_alpha.set_epsilon()
        else:
            for symbol in alpha:
                first_symbol = firsts[symbol]
                first_alpha.update(first_symbol)
                if not first_symbol.contains_epsilon:
                    break
            else:
                first_alpha.set_epsilon()

        return first_alpha

    @staticmethod
    def compute_firsts(G: Grammar):
        firsts = {}
        change = True

        for terminal in G.terminals:
            firsts[terminal] = ContainerSet(terminal)

        for nonterminal in G.nonTerminals:
            firsts[nonterminal] = ContainerSet()

        while change:
            change = False

            for production in G.Productions:
                X = production.Left
                alpha = production.Right

                first_X = firsts[X]

                try:
                    first_alpha = firsts[alpha]
                except:
                    first_alpha = firsts[alpha] = ContainerSet()

                local_first = GrammarHelp.compute_local_first(firsts, alpha)
                change |= first_alpha.hard_update(local_first)
                change |= first_X.hard_update(local_first)
        return firsts

    @staticmethod
    def compute_follows(G: Grammar, firsts):
        follows = {}
        change = True

        local_firsts = {}

        for nonterminal in G.nonTerminals:
            follows[nonterminal] = ContainerSet()
        follows[G.startSymbol] = ContainerSet(G.EOF)

        while change:
            change = False

            for production in G.Productions:
                X = production.Left
                alpha = production.Right

                follow_X = follows[X]

                for i, symbol in enumerate(alpha):
                    if symbol.IsNonTerminal:
                        follow_symbol = follows[symbol]
                        beta = alpha[i + 1:]
                        try:
                            first_beta = local_firsts[beta]
                        except KeyError:
                            first_beta = local_firsts[beta] = GrammarHelp.compute_local_first(
                                firsts, beta)
                        change |= follow_symbol.update(first_beta)
                        if first_beta.contains_epsilon or len(beta) == 0:
                            change |= follow_symbol.update(follow_X)

        return follows

    @staticmethod
    def _register(table, state, symbol, value):
        if state not in table:
            table[state] = dict()

        row = table[state]

        if symbol not in row:
            row[symbol] = []

        cell = row[symbol]

        if value not in cell:
            cell.append(value)

        return len(cell) == 1


class Action(tuple):
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __str__(self):
        try:
            action, tag = self
            return f"{'S' if action == Action.SHIFT else 'OK' if action == Action.OK else ''}{tag}"
        except:
            return str(tuple(self))

    __repr__ = __str__


class ShiftReduceParser:
    def __init__(self, G, verbose = False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output, operations = [], []

        while True:
            state = stack[-1]
            # se cambio aqui y para en caso de error poder devolver el token y asi poder tomar la linea y la columna del error.
            lookahead = w[cursor].token_type
            if self.verbose:
                print(stack, w[cursor:])

            try:
                action, tag = self.action[state][lookahead][0]
                if action == Action.SHIFT:
                    stack.append(tag)
                    cursor += 1
                    operations.append(action)
                elif action == Action.REDUCE:
                    for _ in range(len(tag.Right)):
                        stack.pop()
                    stack.append(self.goto[stack[-1]][tag.Left][0])
                    output.append(tag)
                    operations.append(action)
                elif action == Action.OK:
                    # output.reverse()
                    return output, operations
                else:
                    assert False, 'Must be something wrong!'
            except KeyError:
                #print('Parsing Error:', stack, w[cursor:])
                # cambio para retornar el Token donde dio error y con ello tomar la linea y la columna del error
                # esto deberia retornar el parse y las operaciones, pero en lugar del parser retornamos el token donde hubo error
                return w[cursor], None


class LR1Parser(ShiftReduceParser):
    @staticmethod
    def expand(item, firsts):
        next_symbol = item.NextSymbol
        if next_symbol is None or not next_symbol.IsNonTerminal:
            return []

        lookaheads = ContainerSet()
        for preview in item.Preview():
            lookaheads.hard_update(
                GrammarHelp.compute_local_first(firsts, preview))

        assert not lookaheads.contains_epsilon
        return [Item(prod, 0, lookaheads) for prod in next_symbol.productions]

    @staticmethod
    def compress(items):
        centers = {}

        for item in items:
            center = item.Center()
            try:
                lookaheads = centers[center]
            except KeyError:
                centers[center] = lookaheads = set()
            lookaheads.update(item.lookaheads)

        return {Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items()}

    @staticmethod
    def closure_lr1(items, firsts):
        closure = ContainerSet(*items)

        changed = True
        while changed:
            changed = False

            new_items = ContainerSet()
            for item in closure:
                new_items.extend(LR1Parser.expand(item, firsts))

            changed = closure.update(new_items)

        return LR1Parser.compress(closure)

    @staticmethod
    def goto_lr1(items, symbol, firsts=None, just_kernel=False):
        assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
        items = frozenset(item.NextItem()
                          for item in items if item.NextSymbol == symbol)
        return items if just_kernel else LR1Parser.closure_lr1(items, firsts)

    def build_LR1_automaton(self):
        G = self.augmentedG = self.G.AugmentedGrammar(True)

        firsts = GrammarHelp.compute_firsts(G)
        firsts[G.EOF] = ContainerSet(G.EOF)

        start_production = G.startSymbol.productions[0]
        start_item = Item(start_production, 0, lookaheads=(G.EOF,))
        start = frozenset([start_item])

        closure = LR1Parser.closure_lr1(start, firsts)
        automaton = State(frozenset(closure), True)

        pending = [start]
        visited = {start: automaton}

        while pending:
            current = pending.pop()
            current_state = visited[current]

            for symbol in G.terminals + G.nonTerminals:
                # (Get/Build `next_state`)
                kernels = LR1Parser.goto_lr1(
                    current_state.state, symbol, just_kernel=True)

                if not kernels:
                    continue

                try:
                    next_state = visited[kernels]
                except KeyError:
                    pending.append(kernels)
                    visited[pending[-1]] = next_state = State(
                        frozenset(LR1Parser.goto_lr1(current_state.state, symbol, firsts)), True)

                current_state.add_transition(symbol.Name, next_state)

        self.automaton = automaton

    def _build_parsing_table(self):
        self.is_lr1 = True
        self.build_LR1_automaton()

        for i, node in enumerate(self.automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i
            node.tag = f'I{i}'

        for node in self.automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == self.augmentedG.startSymbol:
                        self.is_lr1 &= GrammarHelp._register(self.action, idx, self.augmentedG.EOF,
                                                              Action((Action.OK, '')))
                    else:
                        for lookahead in item.lookaheads:
                            self.is_lr1 &= GrammarHelp._register(self.action, idx, lookahead,
                                                                  Action((Action.REDUCE, prod)))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self.is_lr1 &= GrammarHelp._register(self.action, idx, next_symbol,
                                                              Action((Action.SHIFT, node[next_symbol.Name][0].idx)))
                    else:
                        self.is_lr1 &= GrammarHelp._register(self.goto, idx, next_symbol,
                                                              node[next_symbol.Name][0].idx)
                pass
