from __future__ import annotations
from datetime import datetime #, timedelta
import argparse
import re

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
    idRootInstNumPattern = re.compile(r"(?P<idRoot>\w)(_(?P<idInstNum>\d+))*")

    def __repr__(self):
        return self.Build()

    def __init__(self, id: str = "", title: str = "", header: str = "", body: str = "", footer: str = "", parent: LatexDocumentBlock | None = None, index: int = -1): #, root: LatexDocumentBlock | None = None):
        self.root = parent.root if parent else self
        self.parent = parent
        self.idRoot = id
        self.idInstNum = -1
        m = self.idRootInstNumPattern.match(id)
        if m:
            self.idRoot = m.group("idRoot")
            self.idInstNum = int(m.group("idInstNum"))

        self.id = "root" if not id and not parent else id if id and not parent else parent.getNewChildId(parent=self, idRoot=self.idRoot) if parent else ""
        # self.id = id if not parent else parent.getNewChildId() 
        
        self.title = title
        self.index = index
        self.header = header if header else ""
        self.body = body if body else ""
        self.footer = footer if footer else ""
        self.children: dict[str,LatexDocumentBlock] = dict[str,LatexDocumentBlock]()

        # blocks = [
        #     LatexDocumentBlock("imports"),
        #     LatexDocumentBlock("definitions"),
        #     LatexDocumentBlock("document")
        # ]
        # self.blocks = {}
        # for block in blocks:
        #     self.attachBlock(block)

    
    def Build(self) -> str:
        return self.header + "\n" + self.BuildBody() + "\n" + self.footer

    def BuildBody(self) -> str:
        childrenContentsList = [block.Build() for id, block in self.children.items()]
        childrenContentsJoined = "\n".join(childrenContentsList)
        return self.body + "\n" + childrenContentsJoined
    
    def getBlock(self, blockId, recursive=True) -> LatexDocumentBlock | None:
        if not recursive:
            block = self.children[blockId] if blockId in self.children else None #LatexDocumentBlock(blockId)
            return block
        
        if blockId in self.children: return self.children[blockId]
        for child in self.children.values():
            block = child.getBlock(blockId=blockId, recursive=True)
            if block: return block
        return None
    
    def attachBlock(self, block: LatexDocumentBlock, force = False, keepIndex = True) -> bool:
        if not block.id in self.children or force:
            index = self.children[block.id].index if block.id in self.children else -1
            index = index if keepIndex else block.index if block.index != -1 else self.getNewChildIndex()
            block.index = index
            self.children[block.id] = block
        elif not force:
            return False
        return True
    
    @staticmethod
    def createBlock(parent: LatexDocumentBlock, id: str = "", title: str = "", header: str = "", body: str = "", footer: str = "", index: int = -1) -> LatexDocumentBlock: #, parent: LatexDocumentBlock | None = None, index: int = -1, force = False, keepIndex = True) -> LatexDocumentBlock:
        #parent = parent if parent else self
        #if parent.root != self.root: raise Exception("Not allowed to attach a new block to a different document tree!")

        idRoot, reqIdInstNum = LatexDocumentBlock.getIdRootAndInstNum(id=id)
        id = LatexDocumentBlock.getNewChildId(parent=parent, idRoot=idRoot, reqIdInstNum=reqIdInstNum)
        block = LatexDocumentBlock(id=id, title=title, header=header, body=body, footer=footer, parent=parent, index=index)
        # success = self.attachBlock(block=block, force=force, keepIndex=keepIndex)
        # if not success: raise Exception(f"Could not bind new child block. Child block with id '{id}' already exist!")
        return block

    def getNewChildIndex(self):
        return len(self.children) + 1
    
    @staticmethod
    def getIdRootAndInstNum(id: str) -> tuple[str,int]:
        m = LatexDocumentBlock.idRootInstNumPattern.match(id)
        if not m: return ("", -1)
        idRoot = m.group("idRoot")
        idInstNum = int(m.group("idInstNum")) if "idInstNum" in m.groups() else -1
        return (idRoot, idInstNum)
    
    @staticmethod
    def getNewChildId(parent: LatexDocumentBlock, idRoot: str = "", reqIdInstNum: int = -1) -> str:
        if not idRoot: return LatexDocumentBlock.getNewChildId(parent=parent, idRoot=parent.idRoot)
        newId = idRoot if reqIdInstNum == -1 else f"{idRoot}_{reqIdInstNum}"
        if newId not in parent.children: return newId
        reservedIndexes = [ ] #int(self.idRootInstNumPattern.match(childId).group("idInstNum")) for childId in self.children]
        for childId in parent.children:
            m = parent.idRootInstNumPattern.match(childId)
            if m: reservedIndexes.append(int(m.group("idInstNum")))
        newIdInstNum = max(reservedIndexes)+1
        newId = f"{idRoot}_{newIdInstNum}"
        return newId


    
class LatexDocumentBuilder:
    def __repr__(self):
        return self.Build()

    def __init__(self):
        # blocks = [
        #     LatexDocumentBlock("imports"),
        #     LatexDocumentBlock("definitions"),
        #     LatexDocumentBlock("document")
        # ]
        # self.blocks = {}
        # for block in blocks:
        #     self.attachBlock(block)
        # # self.blocks = {block.id: block for block in blocks}
        self.document = LatexDocumentBlock()
        blocks = [
            LatexDocumentBlock.createBlock(parent=self.document, id="imports"),
            LatexDocumentBlock.createBlock(parent=self.document, id="definitions"),
            LatexDocumentBlock.createBlock(parent=self.document, id="document"),
        ]

        for block in blocks:
            self.document.attachBlock(block=block)
        # self.document.createBlock(id="imports")
        # self.document.createBlock(id="definitions")
        # self.document.createBlock(id="document")

    def Build(self):
        # return self.imports.Build() + "\n" + self.definitions.Build() + "\n" + self.document.Build()
        return self.document.Build()
    
    # def getBlock(self, blockId):
    #     block = self.blocks[blockId] if blockId in self.blocks else LatexDocumentBlock(blockId)
    #     return block
    
    # def attachBlock(self, block, force = False, keepIndex = True):
    #     if not block.id in self.blocks or force:
    #         index = self.blocks[block.id].index if block.id in self.blocks else -1
    #         index = index if keepIndex else block.index if block.index != -1 else self.getNextBlockIndex()
    #         block.index = index
    #         self.blocks[block.id] = block
    
    # def getNextBlockIndex(self):
    #     return len(self.blocks) + 1
    
class LatexResumeBuilder(LatexDocumentBuilder):
    def __init__(self):
        super().__init__()
        # blocks = [
        #     LatexResumeBlock("header"),
        #     LatexResumeBlock("aside"),
        #     LatexResumeBlock("skills"),
        #     LatexResumeBlock("experience"),
        #     LatexResumeBlock("education")
        # ]
        # for block in blocks:
        #     self.attachBlock(block)

        # self.document.createBlock("header")
        # self.document.createBlock("aside")
        # self.document.createBlock("skills")
        # self.document.createBlock("experience")
        # self.document.createBlock("education")
        blocks = [
            LatexResumeBlock.createBlock(parent=self.document, id="header"),
            LatexResumeBlock.createBlock(parent=self.document, id="aside"),
            LatexResumeBlock.createBlock(parent=self.document, id="skills"),
            LatexResumeBlock.createBlock(parent=self.document, id="experience"),
            LatexResumeBlock.createBlock(parent=self.document, id="education"),
        ]

        for block in blocks:
            self.document.attachBlock(block=block)


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
        super().__init__(id=id, title=title, index=index)  

    
    def __repr__(self):
        return self.Build()

    
    def Build(self) -> str:
        return self.header + "\n" + self.BuildBody() + "\n" + self.footer

    def BuildBody(self) -> str:
        childrenContentsList = [childBlock.Build() for childBlock in self.children.values()]
        childrenContentsJoined = "\n".join(childrenContentsList)
        return self.body + "\n" + childrenContentsJoined
