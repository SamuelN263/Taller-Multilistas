import csv


class Node:
    def __init__(self, id, name, **extra):
        self.id = id
        self.name = name
        self.next = None
        self.prev = None
        self.sub_list = None         
        for k, v in extra.items():    # atributos adicionales (lat, lon, tipo...)
            setattr(self, k, v)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}, {self.name})"


class Country(Node):
    pass


class Department(Node):
    pass


class Municipality(Node):
    pass


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, node):
        if self.head is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        return node

    def add_child(self, parent: Node, child: Node):
        if parent.sub_list is None:
            parent.sub_list = LinkedList()
        parent.sub_list.append(child)
        return parent.sub_list

    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def search_by_attr(self, attr, value):
        for node in self:
            if getattr(node, attr, None) == value:
                return node
        return None

    def update_value(self, id, **attrs):
        node = self.search_by_attr("id", id)
        if node:
            for k, v in attrs.items():
                setattr(node, k, v)
            return True
        return False

    def delete_value(self, id):
        node = self.search_by_attr("id", id)
        if node is None:
            return False
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        return True

    def print_multilinked_list(self, level=0):
        if self.head is None:
            print("Empty list")
            return
        for node in self:
            print("  " * level + str(node))
            if node.sub_list:
                node.sub_list.print_multilinked_list(level + 1)

    def to_dict(self):
        """Serializa recursivamente la multilista a una lista de dicts (JSON)."""
        out = []
        for node in self:
            d = {"tipo": node.__class__.__name__, "id": node.id, "name": node.name}
            for k in ("lat", "lon", "kind"):
                if hasattr(node, k):
                    d[k] = getattr(node, k)
            if node.sub_list:
                d["children"] = node.sub_list.to_dict()
            out.append(d)
        return out


def _num(s):
    """'-75,581775' -> -75.581775 (la DIVIPOLA usa coma decimal)."""
    s = (s or "").strip().replace(",", ".")
    return float(s) if s else None


def load_divipola(path):
    """Lee el CSV de la DIVIPOLA y devuelve la LinkedList raíz (con Colombia)."""
    root = LinkedList()
    colombia = root.append(Country("CO", "Colombia"))
    deps = {}  # código -> nodo, solo para no buscar linealmente en cada fila
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            cod_dep = row["Código Departamento"].strip()
            if cod_dep not in deps:
                dep = Department(cod_dep, row["Nombre Departamento"].strip().title())
                root.add_child(colombia, dep)
                deps[cod_dep] = dep
            dep = deps[cod_dep]
            mun = Municipality(
                row["Código Municipio"].strip(),
                row["Nombre Municipio"].strip().title(),
                lat=_num(row["Latitud"]),
                lon=_num(row["longitud"]),
                kind=row["Tipo: Municipio / Isla / Área no municipalizada"].strip(),
            )
            root.add_child(dep, mun)
    return root


if __name__ == "__main__":
    ml = load_divipola("data/DIVIPOLA.csv")
    # impresión resumida: todos los departamentos y los 3 primeros municipios
    col = ml.head
    print(col)
    for dep in col.sub_list:
        print("  " + str(dep))
        for i, m in enumerate(dep.sub_list):
            if i == 3:
                print("    ...")
                break
            print("    " + str(m))
