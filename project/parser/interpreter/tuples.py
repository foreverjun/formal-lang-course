class Pair:
    def __init__(self, start, end):
        if type(start) != type(end):
            raise TypeError("start and end must be of the same type")
        self.start = start
        self.end = end
        self.type = type(start)

    def to_tuple(self):
        return self.start, self.end

    def __str__(self):
        return f"({self.start}, {self.end})"

    def __eq__(self, second: "Pair"):
        return self.start == second.start and self.end == second.end

    def __hash__(self):
        return hash((self.start, self.end))


class Triple:
    def __init__(self, start, end, label):
        if type(start) != type(end):
            raise TypeError("start and end must be of the same type")
        self.start = start
        self.end = end
        self.label = label
        self.type = type(start)

    def to_tuple(self):
        return self.start, self.end, self.label

    def __str__(self):
        return f"({self.start}, {self.end}, {self.label})"

    def __eq__(self, second: "Triple"):
        return (
            self.start == second.start
            and self.end == second.end
            and self.label == second.label
        )

    def __hash__(self):
        return hash((self.start, self.end, self.label))
