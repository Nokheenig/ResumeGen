from __future__ import annotations
from datetime import datetime #, timedelta
import argparse

parse = argparse.ArgumentParser().parse_args()

class ResumeGeneratorSession:
    def __init__(self, args) -> None:
        # Date-time
        self.today = datetime.now()
        self.targetDay = self.today
        self.year = str(self.targetDay.year)
        self.month = str(self.targetDay.month)
        self.day = "0" + str(self.targetDay.day) if len(str(self.targetDay.day)) < 2 else str(self.targetDay.day) #on ajoute 0 devant le jour s'il est compris entre 1 et 9

        self.cliArgs = args



class LatexDocumentBlock:
    def __repr__(self):
        return self.Build()

    def __init__(self, id: str, title: str = "", index: int = -1):
        self.id = id
        self.title = title
        self.index = index
        self.header : str = ""
        self.body: str = ""
        self.footer: str = ""
        self.children: list[LatexDocumentBlock] = []
    
    def Build(self) -> str:
        return self.header + "\n" + self.BuildBody() + "\n" + self.footer

    def BuildBody(self) -> str:
        childrenContentsList = [childBlock.Build() for childBlock in self.children]
        childrenContentsJoined = "\n".join(childrenContentsList)
        return self.body + "\n" + childrenContentsJoined
    
class LatexDocumentBuilder:
    def __repr__(self):
        return self.Build()

    def __init__(self):
        blocks = [
            LatexDocumentBlock("imports"),
            LatexDocumentBlock("definitions"),
            LatexDocumentBlock("document")
        ]
        self.blocks = {}
        for block in blocks:
            self.addBlock(block)
        # self.blocks = {block.id: block for block in blocks}

    def Build(self):
        # return self.imports.Build() + "\n" + self.definitions.Build() + "\n" + self.document.Build()
        return "\n".join(self.blocks)
    
    def getBlock(self, blockId):
        block = self.blocks[blockId] if blockId in self.blocks else LatexDocumentBlock(blockId)
        return block
    
    def addBlock(self, block, force = False, keepIndex = True):
        if not block.id in self.blocks or force:
            index = self.blocks[block.id].index if block.id in self.blocks else -1
            index = index if keepIndex else block.index if block.index != -1 else self.getNextBlockIndex()
            block.index = index
            self.blocks[block.id] = block
    
    def getNextBlockIndex(self):
        return len(self.blocks) + 1
    
class LatexResumeBuilder(LatexDocumentBuilder):
    def __init__(self):
        super().__init__()
        blocks = [
            LatexResumeBlock("header"),
            LatexResumeBlock("aside"),
            LatexResumeBlock("skills"),
            LatexResumeBlock("experience"),
            LatexResumeBlock("education")
        ]
        for block in blocks:
            self.addBlock(block)

class LatexResumeBlock(LatexDocumentBlock):
    # def __init__(self, id: str, title: str = "", index: int = -1):
    #     self.id = id
    #     self.title = title
    #     self.index = index
    #     self.header : str = ""
    #     self.body: str = ""
    #     self.footer: str = ""
    #     self.children: list[LatexDocumentBlock] = []

    def __init__(self, id: str, title: str = "", index: int = -1):
        super().__init__(id, title, index)  

    
    def __repr__(self):
        return self.Build()

    
    def Build(self) -> str:
        return self.header + "\n" + self.BuildBody() + "\n" + self.footer

    def BuildBody(self) -> str:
        childrenContentsList = [childBlock.Build() for childBlock in self.children]
        childrenContentsJoined = "\n".join(childrenContentsList)
        return self.body + "\n" + childrenContentsJoined
