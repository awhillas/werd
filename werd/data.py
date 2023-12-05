"""
Visitor Design pattern

Since the filesytem is a tree structure, we can use the visitor design pattern
to traverse the tree and perform operations on each dir/file/node.

We'll use a common class to represent all filesystem nodes given a root path
and then have different visitor classes to perform different operations to produce
different outputs.
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class Node:
    def accept(self, visitor: "Visitor"):
        pass


class Visitor:
    def visit(self, node: Node):
        pass


class FileSystemNode(Node):
    def __init__(self, path: Path):
        self.path = path

    def is_folder(self):
        return self.path.is_dir()

    def is_a(self, type_of: str):
        return type_of in self.path.parts

    def accept(self, visitor):
        kids = []

        for child in self.path.iterdir():
            childNode = FileSystemNode(child)
            if childNode.is_folder():
                kids.append(childNode.accept(visitor))
            else:
                kids.append(visitor.visit(childNode))

        return visitor.visit(self, kids)


class PageTreeNode(Node):
    def accept(self, visitor):
        visitor.visit(self, self.subpages)
        for page in self.subpages:
            page.accept(visitor)


class Page(BaseModel, PageTreeNode):
    href: str
    lang: str
    title: str


class ContentPage(Page):
    content: str
    content_file: Path


class BlogPost(ContentPage):
    date: datetime


class IndexPage(Page):
    subpages: list[Page]


if __name__ == "__main__":

    class Test(Visitor):
        def visit(self, node: FileSystemNode, kids: list = []):
            print(node.path, len(kids))

    root = Path("tests/content")
    node = Node(root)
    node.accept(Test())
