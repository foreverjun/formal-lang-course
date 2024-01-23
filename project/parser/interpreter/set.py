class Set:
    def __init__(self, elements: set, ty=None):
        if len(elements) > 0:
            if ty is None:
                # check that types of all elements are the same
                self.type = type(next(iter(elements)))
                for e in elements:
                    if type(e) != self.type:
                        raise TypeError("Elements of set must be of the same type")
            else:
                self.type = ty
        else:
            self.type = None
        self.elements = elements

    def __str__(self):
        return "{" + ", ".join(map(str, self.elements)) + "}"

    def __eq__(self, other: "Set"):
        return self.elements == other.elements

    def __hash__(self):
        return hash(self.elements)

    def __len__(self):
        return len(self.elements)

    def __contains__(self, item):
        if not isinstance(item, self.type):
            raise TypeError("Item must be of the same type as the set")
        if self.type is None:
            return False
        return item in self.elements
