from __future__ import annotations
from datetime import datetime #, timedelta
import re

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
    idRootInstNumPattern = re.compile(r"(?P<idRoot>\w+)(_(?P<idInstNum>\d+))*")

    def __repr__(self):
        return f"[LatexDocumentBlock-{self.id}]"

    def __init__(self, id: str = "", title: str = "", header: str | LatexDocumentBlock = "", body: str = "", footer: str | LatexDocumentBlock = "", parent: LatexDocumentBlock | None = None, index: int = -1):
        self.root = parent.root if parent else self
        self.parent = parent
        self.children = dict[str,LatexDocumentBlock]()
        self.idRoot = id
        self.idInstNum = -1
        m = self.idRootInstNumPattern.match(id)
        if m:
            self.idRoot = m.group("idRoot")
            print("m: ", m)
            print("self.idRoot: ", self.idRoot)
            if "idInstNum" in m.groups():
                self.idInstNum = int(m.group("idInstNum"))

        self.id = "" 
        if not id and not parent:
            self.id = "root"
        elif id and not parent:
            self.id = id
        elif parent: 
            if id:
                self.id = parent.getNewChildId(parent=parent, idRoot=id)
            else:
                self.id = parent.getNewChildId(parent=parent, idRoot=parent.idRoot)
        
        self.title = title
        self.index = index
        self.header = header if header else ""
        self.body = body if body else ""
        self.footer = footer if footer else ""
    
    def Build(self) -> str:
        with open("resume_gen.log", "a", encoding="utf-8") as f:
                f.write(f"Build-Start -- self id: {self.id}\n")
                f.write(f"            -- self children ({len(self.children)}): {self.children}\n")

        header = self.header.Build() if isinstance(self.header, LatexDocumentBlock) else self.header
        footer = self.footer.Build() if isinstance(self.footer, LatexDocumentBlock) else self.footer

        buildElements = [
            header,
            self.BuildBody(),
            footer
        ]
        idx = len(buildElements)-1
        while idx >=0:
            if buildElements[idx] == "": buildElements.pop(idx)
            idx -=1
        return "\n".join(buildElements)

    def BuildBody(self) -> str:
        childrenContentsList = []
        for id, block in self.children.items():
            print("block id: ", block.id)
            with open("resume_gen.log", "a", encoding="utf-8") as f:
                f.write(f"self id: {self.id}\n")
                f.write(f"block id: {block.id}\n")
            childrenContentsList.append(block.Build())

        idx = len(childrenContentsList)-1
        while idx >=0:
            if childrenContentsList[idx] == "": childrenContentsList.pop(idx)
            idx -=1
            
        childrenContentsJoined = "\n".join(childrenContentsList)
        body = ""

        buildElements = [
            self.body,
            childrenContentsJoined
        ]
        idx = len(buildElements)-1
        while idx >=0:
            if buildElements[idx] == "": buildElements.pop(idx)
            idx -=1
        return "\n".join(buildElements)
    
    def getBlock(self, id, recursive=True) -> LatexDocumentBlock | None:
        if not recursive:
            block = self.children[id] if id in self.children else None
            return block
        
        if id in self.children: return self.children[id]
        for child in self.children.values():
            block = child.getBlock(id=id, recursive=True)
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
    
    def createChild(self, id: str = "", title: str = "", header: str | LatexDocumentBlock = "", body: str = "", footer: str | LatexDocumentBlock = "", index: int = -1) -> LatexDocumentBlock:
        parent = self
        idRoot, reqIdInstNum = LatexDocumentBlock.getIdRootAndInstNum(id=id)
        id = LatexDocumentBlock.getNewChildId(parent=parent, idRoot=idRoot, reqIdInstNum=reqIdInstNum)
        block = LatexDocumentBlock(id=id, title=title, header=header, body=body, footer=footer, parent=parent, index=index)
        self.attachBlock(block=block)
        return block

    @staticmethod
    def createBlock(parent: LatexDocumentBlock, id: str = "", title: str = "", header: str | LatexDocumentBlock = "", body: str = "", footer: str | LatexDocumentBlock = "", index: int = -1) -> LatexDocumentBlock: 

        idRoot, reqIdInstNum = LatexDocumentBlock.getIdRootAndInstNum(id=id)
        id = LatexDocumentBlock.getNewChildId(parent=parent, idRoot=idRoot, reqIdInstNum=reqIdInstNum)
        block = LatexDocumentBlock(id=id, title=title, header=header, body=body, footer=footer, parent=parent, index=index)

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
        if not idRoot: return LatexDocumentBlock.getNewChildId(parent=parent, idRoot=f"{parent.idRoot}_{len(parent.children)+1}")
        newId = idRoot if reqIdInstNum == -1 else f"{idRoot}_{reqIdInstNum}"
        if newId not in parent.children.keys(): return newId
        reservedIndexes = [ 0 ] 
        for childId in parent.children:
            m = parent.idRootInstNumPattern.match(childId)
            if m and m.group("idRoot") == idRoot: 
                if "idInstNum" in m.groups():
                    reservedIndex = int(m.group("idInstNum"))
                    reservedIndexes.append(reservedIndex)
        newIdInstNum = max(reservedIndexes)+1
        newId = f"{idRoot}_{newIdInstNum}"
        return newId

class LatexDocumentConstants:
    document_root = "root"
    section_imports = "imports"
    section_definitions = "definitions"
    section_document = "document"

class LatexResumeConstants(LatexDocumentConstants):
    section_header = "header"
    section_quote = "quote"
    section_aside = "aside"
    section_aside_infos = "aside_infos"
    section_aside_contact = "aside_contact"
    section_aside_links = "aside_links"
    section_aside_languages = "aside_languages"
    section_aside_strengths = "aside_strengths"
    section_aside_hobbies = "aside_hobbies"
    section_aside_dateid = "aside_dateid"
    section_skills = "skills"
    section_experience = "experience"
    section_education = "education"
    section_aside_mechanicalskills = "aside_mechanicalskills"
    section_skills_backend = "skills_backend"
    section_skills_devopscicd = "skills_devopscicd"
    section_skills_web = "skills_web"
    section_skills_authentication = "skills_authentication"
    section_skills_databases = "skills_databases"
    section_skills_others = "skills_others"
    
class LatexDocumentBuilder:
    const = LatexDocumentConstants()
    def __repr__(self):
        return self.Build()

    def __init__(self):
        self.document = LatexDocumentBlock(id=self.const.document_root)
        self.blocks = {
            self.const.document_root: self.document,
            self.const.section_imports: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_imports),
            self.const.section_definitions: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_definitions),
            self.const.section_document: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_document),
        }

        for block in self.blocks.keys():
            if block != self.document.id: self.document.attachBlock(block=self.blocks[block])

    def createBlock(self, id: str = "", title: str = "", header: str | LatexDocumentBlock = "", body: str = "", footer: str | LatexDocumentBlock = "", parent: LatexDocumentBlock | None = None, index: int = -1) -> LatexDocumentBlock:
        block = LatexDocumentBlock(id=id, title=title, header=header, body=body, footer=footer, parent=parent, index=index)

        if parent:
            parent.attachBlock(block=block)
        return block

    def Build(self):
        return self.document.Build()
    
class LatexResumeBuilder(LatexDocumentBuilder):
    const = LatexResumeConstants()

    def __init__(self):
        super().__init__()