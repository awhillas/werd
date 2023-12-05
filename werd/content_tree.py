from abc import ABC, abstractmethod
from pathlib import Path

NOT_IMPLEMENTED = "You should implement this."


class Visitor(ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """

    @abstractmethod
    def visit_file(self, file: "FileNode") -> None:
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_directory(self, directory: "DirectoryNode") -> None:
        raise NotImplementedError(NOT_IMPLEMENTED)


class Node(ABC):
    def __init__(self, path: Path) -> None:
        self.path = path

    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError(NOT_IMPLEMENTED)


class FileNode(Node):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_file(self)


class DirectoryNode(Node):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.children = []

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_directory(self)


class ContentTree:
    """
    A tree of content Nodes.
    """

    def __init__(self, config: dict, root: Path):
        """Recurse through the content directory and build a tree of content Nodes."""
        self.root = root
        self.tree = self.build_tree(config, root)

    def build_tree(self, config: dict, root: Path):
        """Recursively build a tree of content Nodes."""
        tree = DirectoryNode(root)

        for child in root.iterdir():
            if child.is_dir():
                tree.children.append(self.build_tree(config, child))
            else:
                tree.children.append(FileNode(child))

        return tree

    def accept(self, visitor: Visitor) -> None:
        """
        Pass each node in the tree to the visitor.
        """
        self.tree.accept(visitor)


class PrintTreeVisitor(Visitor):
    """
    A concrete visitor that prints the content tree.
    """

    def __init__(self, relative_to: Path = Path(".")) -> None:
        self.relative_to = relative_to

    def visit_file(self, file: FileNode) -> None:
        f = file.path.relative_to(self.relative_to)
        print((len(f.parts) - 1) * "\t" + f"{f.name}")

    def visit_directory(self, directory: DirectoryNode) -> None:
        d = directory.path.relative_to(self.relative_to)
        print("\t".join([p for p in d.parts if p != "."]))
        for child in directory.children:
            child.accept(self)


if __name__ == "__main__":
    path = Path("tests/content")
    ct = ContentTree(config={}, root=path)
    ptv = PrintTreeVisitor(path)
    ct.accept(ptv)
