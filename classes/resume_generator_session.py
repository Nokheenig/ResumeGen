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
    idRootInstNumPattern = re.compile(r"(?P<idRoot>\w+)(_(?P<idInstNum>\d+))*")

    def __repr__(self):
        return f"[LatexDocumentBlock-{self.id}]"

    def __init__(self, id: str = "", title: str = "", header: str = "", body: str = "", footer: str = "", parent: LatexDocumentBlock | None = None, index: int = -1): #, root: LatexDocumentBlock | None = None):
        with open("resume_gen.log", "w", encoding="utf-8") as f:
            f.write("pouet")
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

        # self.id = "root" if not id and not parent else id if id and not parent else parent.getNewChildId(parent=self, idRoot=self.idRoot) if parent else ""
        self.id = "" 
        if not id and not parent:
            self.id = "root"
        elif id and not parent:
            self.id = id
        elif parent: 
            self.id = parent.getNewChildId(parent=self, idRoot=self.idRoot)
        # self.id = id if not parent else parent.getNewChildId() 
        
        self.title = title
        self.index = index
        self.header = header if header else ""
        self.body = body if body else ""
        self.footer = footer if footer else ""
        

        # blocks = [
        #     LatexDocumentBlock("imports"),
        #     LatexDocumentBlock("definitions"),
        #     LatexDocumentBlock("document")
        # ]
        # self.blocks = {}
        # for block in blocks:
        #     self.attachBlock(block)

    
    def Build(self) -> str:
        with open("resume_gen.log", "a", encoding="utf-8") as f:
                f.write(f"Build-Start -- self id: {self.id}\n")
                f.write(f"            -- self children ({len(self.children)}): {self.children}\n")
        # buildOutput = ""
        # if self.header: output += self.header + "\n"
        # body = self.BuildBody()
        # if body: output += body + "\n"
        # if self.footer: output += self.footer # + "\n"
        # return output
        buildElements = [
            self.header,
            self.BuildBody(),
            self.footer
        ]
        idx = len(buildElements)-1
        while idx >=0:
            if buildElements[idx] == "": buildElements.pop(idx)
            idx -=1
        return "\n".join(buildElements)

    def BuildBody(self) -> str:
        # childrenContentsList = [block.Build() for id, block in self.children.items()]
        childrenContentsList = []
        for id, block in self.children.items():
            print("block id: ", block.id)
            with open("resume_gen.log", "a", encoding="utf-8") as f:
                f.write(f"self id: {self.id}\n")
                f.write(f"block id: {block.id}\n")
            childrenContentsList.append(block.Build())

        
        # buildElements = [
        #     self.header,
        #     self.BuildBody(),
        #     self.footer
        # ]
        idx = len(childrenContentsList)-1
        while idx >=0:
            if childrenContentsList[idx] == "": childrenContentsList.pop(idx)
            idx -=1
        # return "\n".join(buildElements)

            
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

        # if self.body and childrenContentsJoined: body += self.body + "\n"
        # if childrenContentsJoined: body += childrenContentsJoined
        # return body
    
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
        if newId not in parent.children.keys(): return newId
        reservedIndexes = [ ] #int(self.idRootInstNumPattern.match(childId).group("idInstNum")) for childId in self.children]
        for childId in parent.children:
            m = parent.idRootInstNumPattern.match(childId)
            if m: reservedIndexes.append(int(m.group("idInstNum")))
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
    section_aside = "aside"
    section_skills = "skills"
    section_experience = "experience"
    section_education = "education"
    
class LatexDocumentBuilder:
    const = LatexDocumentConstants()
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

        self.document = LatexDocumentBlock(id=self.const.document_root)
        self.blocks = {
            self.const.document_root: self.document,
            self.const.section_imports: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_imports),
            self.const.section_definitions: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_definitions),
            self.const.section_document: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_document),
        }

        for block in self.blocks.keys():
            if block != self.document.id: self.document.attachBlock(block=self.blocks[block])


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
    const = LatexResumeConstants()

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
        blocks = {
            self.const.section_header: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_header),
            self.const.section_aside: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_aside),
            self.const.section_skills: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_skills),
            self.const.section_experience: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_experience),
            self.const.section_education: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_education),
        }
        self.blocks = {**self.blocks, **blocks}

        # blocks[0].header = "Ingénieur et Concepteur Développeur d'Application guidé par un sens du détail et de la performance, à la recherche de nouveaux défis!"

        for block in blocks.keys():
            self.blocks[self.const.section_document].attachBlock(block=blocks[block])

        self.blocks[self.const.document_root].header = r"%!TEX TS-program = xelatex"
        self.blocks[self.const.section_imports].header = r"""\documentclass[]{friggeri-cv}
\usepackage{afterpage}
\usepackage{hyperref}
\usepackage{color}
\usepackage{xcolor}
\usepackage{smartdiagram}
\usepackage{fontspec}
%\usepackage{fontawesome}
\usepackage{metalogo}
\usepackage{dtklogos}
\usepackage[utf8]{inputenc}
\usepackage{tikz}
\usepackage{multicol}
\usepackage{setspace}
\usepackage[document]{ragged2e}
"""
        self.blocks[self.const.section_definitions].header = r"""\usetikzlibrary{mindmap,shadows}
\hypersetup{
    pdftitle={},
    pdfauthor={},
    pdfsubject={},
    pdfkeywords={},
    colorlinks=false,           % no lik border color
    allbordercolors=white       % white border color for all
}
\smartdiagramset{
    bubble center node font = \footnotesize,
    bubble node font = \footnotesize,
    % specifies the minimum size of the bubble center node
    bubble center node size = 0.5cm,
    %  specifies the minimum size of the bubbles
    bubble node size = 0.5cm,
    % specifies which is the distance among the bubble center node and the other bubbles
    distance center/other bubbles = 0.3cm,
    % sets the distance from the text to the border of the bubble center node
    distance text center bubble = 0.5cm,
    % set center bubble color
    bubble center node color = pblue,
    % define the list of colors usable in the diagram
    set color list = {lightgray, materialcyan, orange, green, materialorange, materialteal, materialamber, materialindigo, materialgreen, materiallime},
    % sets the opacity at which the bubbles are shown
    bubble fill opacity = 0.6,
    % sets the opacity at which the bubble text is shown
    bubble text opacity = 0.5,
}

\addbibresource{bibliography.bib}
\RequirePackage{xcolor}
\definecolor{pblue}{HTML}{0395DE}

%\titlespacing*{\section}
%{0pt}{12pt plus 4pt minus 2pt}{0pt plus 2pt minus 2pt}
%\titlespacing*{\subsection}
%{0pt}{12pt plus 4pt minus 2pt}{0pt plus 2pt minus 2pt}
%\titlespacing*{\subsubsection}
%{0pt}{12pt plus 4pt minus 2pt}{0pt plus 2pt minus 2pt}

\title{Yoann Chamillard -- Resume}
\author{Yoann Chamillard}
\date{05/2/2026}

\hypersetup{
  pdftitle={Yoann Chamillard -- Resume},
  pdfauthor={Yoann Chamillard},
  pdfsubject={Software Developer - Resume},
  pdfkeywords={profile:softDev; resume; developer; software; engineer; C\# .Net; Python; Javascript; Node.js; Java; Kotlin; Android; Rest API; Git  GitLab; Docker; Jenkins; Selenium; Cron; Html-Css; MySQL; PostgreSQL; MongoDB; SQLite; Firebase; Bash; Jira; Regex; createdAt:2026-02-05 14:54:58.769054 ; id:084fe0},
  pdfcreator={LuaLaTeX},
  pdfproducer={LuaLaTeX}
}
"""
        self.blocks[self.const.section_document].header = r"\begin{document}"
        self.blocks[self.const.section_document].footer = r"\end{document}"



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

if __name__ == "__main__":
    resume = LatexResumeBuilder()

    resumeContents = resume.Build()

    with open("resume.tex", "w", encoding="utf-8") as f:
        f.write(resumeContents)

    # with open("file.txt", "r", encoding="utf-8") as f:
    #     print(f.read())