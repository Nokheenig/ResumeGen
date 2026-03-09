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
        # with open("resume_gen.log", "w", encoding="utf-8") as f:
        #     f.write("pouet")
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
            if id:
                self.id = parent.getNewChildId(parent=parent, idRoot=id)
            else:
                self.id = parent.getNewChildId(parent=parent, idRoot=parent.idRoot)
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
    
    def getBlock(self, id, recursive=True) -> LatexDocumentBlock | None:
        if not recursive:
            block = self.children[id] if id in self.children else None #LatexDocumentBlock(blockId)
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
    
    def createChild(self, id: str = "", title: str = "", header: str = "", body: str = "", footer: str = "", index: int = -1) -> LatexDocumentBlock:
        parent = self
        idRoot, reqIdInstNum = LatexDocumentBlock.getIdRootAndInstNum(id=id)
        id = LatexDocumentBlock.getNewChildId(parent=parent, idRoot=idRoot, reqIdInstNum=reqIdInstNum)
        block = LatexDocumentBlock(id=id, title=title, header=header, body=body, footer=footer, parent=parent, index=index)
        self.attachBlock(block=block)
        return block

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
        reservedIndexes = [ 0 ] #int(self.idRootInstNumPattern.match(childId).group("idInstNum")) for childId in self.children]
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

    def createBlock(self, id: str = "", title: str = "", header: str = "", body: str = "", footer: str = "", parent: LatexDocumentBlock | None = None, index: int = -1) -> LatexDocumentBlock:
        block = LatexDocumentBlock(id=id, title=title, header=header, body=body, footer=footer, parent=parent, index=index)
        # self.blocks[id] = block
        if parent:
            parent.attachBlock(block=block)
        return block

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


        # blocks = {
        #     # self.const.section_header: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_header),
        #     # self.const.section_aside: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_aside),
        #     # self.const.section_skills: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_skills),
        #     # self.const.section_experience: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_experience),
        #     self.const.section_education: LatexDocumentBlock.createBlock(parent=self.document, id=self.const.section_education),
        # }
        # self.blocks = {**self.blocks, **blocks}

        # # blocks[0].header = "Ingénieur et Concepteur Développeur d'Application guidé par un sens du détail et de la performance, à la recherche de nouveaux défis!"

        # for block in blocks.keys():
        #     self.blocks[self.const.section_document].attachBlock(block=blocks[block])

        root = self.document
        root.header = r"%!TEX TS-program = xelatex"

        imports = root.getBlock(id=self.const.section_imports)
        if imports:
            imports.header = r"""\documentclass[]{friggeri-cv}
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
\usepackage[document]{ragged2e}"""

        definitions = root.getBlock(id=self.const.section_definitions)
        if definitions:
            definitions.header = r"""\usetikzlibrary{mindmap,shadows}
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
}"""
        document = root.getBlock(id=self.const.section_document)
        if document:
            document.header = r"\begin{document}"
            document.footer = r"\end{document}"

        header = document and document.createChild(id=self.const.section_header)
        if header:
            # header = self.createBlock(id=self.const.section_header, parent=self.blocks[self.const.section_document])
            header.body = r"""\header{Yoann}{Chamillard}
      {~~~~~~Software Developer}
      {}"""

        # Duplicate
        aside = document and document.createChild(id=self.const.section_aside)
        if aside:
            # aside = self.createBlock(id=self.const.section_aside, parent=self.blocks[self.const.section_document])
            aside.header = r"""\begin{aside}
\vspace{21mm}"""
            aside.footer = r"""\end{aside}"""

        quote = document and document.createChild(id=self.const.section_quote)
        if quote:
            # quote = self.createBlock(id=self.const.section_quote, parent=self.blocks[self.const.section_document])
            quote.header = r"""\vspace*{-2.0mm}
\noindent\parbox{\linewidth}{
\centering"""
            quote.body = "Engineer by training (France, CTI-accredited), now working as a software developer with a strong engineering mindset. Always eager to learn and improve, I am now looking for new challenges!"
            quote.footer = "}"

        # duplicate
        skills = document and document.createChild(id=self.const.section_skills)
        if skills:
            # skills = self.createBlock(id=self.const.section_skills, parent=self.blocks[self.const.section_document])
            skills.header = r"""\vspace*{0.8mm}
\section{IT-Skills}
\vspace*{-0.45cm}
\setlength{\columnsep}{-0.3cm}
\begin{flushleft}
\begin{multicols}{3}
\begin{itemize}
    \setlength{\itemsep}{5pt}
    \setlength{\parskip}{0pt}
    \setlength{\parsep}{0pt}"""
            skills.footer = r"""\end{itemize}
\end{multicols}
%\end{itemize}
\end{flushleft} \normalsize
\vspace*{-0.65cm}"""

        # duplicate
        experience = document and document.createChild(id=self.const.section_experience)
        if experience:
            # experience = self.createBlock(id=self.const.section_experience, parent=self.blocks[self.const.section_document])
            experience.header = r"""\section{Work Experience}
\vspace*{-0.25cm}"""

        education = document and document.createChild(id=self.const.section_education)
        if education:
            education.header = r"""\vspace*{-0.5cm}
\vspace*{0.45cm}
\section{Education - Certifications}
\vspace*{-0.25cm}
\vspace{0.5mm}"""

        aside_infos = aside and aside.createChild(id=self.const.section_aside_infos)
        if aside_infos:
            # aside_infos = self.createBlock(id=self.const.section_aside_infos, parent=self.blocks[self.const.section_aside])
            aside_infos.header = r"""\section{Infos}"""
            # aside_infos.body = r"""\\section{Infos}"""
            block = aside_infos.createChild()
            block.body = r"""%33 yo\\
Full driving licence\\"""
            block.footer = r"""\vspace{3.5mm}"""

            block = aside_infos.createChild()
            block.body = r"""Legally authorized to work in Canada.\\"""
            block.footer = r"""\vspace{2.5mm}"""
        
        aside_contact = aside and aside.createChild(id=self.const.section_aside_contact)
        if aside_contact:
            # aside_contact = self.createBlock(id=self.const.section_aside_contact, parent=self.blocks[self.const.section_aside])
        
            block = aside_contact.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_contact])
            block.body = r"""\href{mailto:y.chamillard.pro@gmail.com}{\small y.chamillard.pro@gmail.com}\\"""
            block.footer = r"""\vspace{2.5mm}"""
            
            block = aside_contact.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_contact])
            block.body = r"""\href{https://www.linkedin.com/in/yoannchamillard/?locale=en_US}{LinkedIn\hspace{1.5mm}\includegraphics[scale=0.075]{hlink.png}}\\"""
            block.footer = r"""\vspace{2.5mm}"""

        aside_links = aside and aside.createChild(id=self.const.section_aside_links)
        if aside_links:
            # aside_links = self.createBlock(id=self.const.section_aside_links, parent=self.blocks[self.const.section_aside])
        
            block = aside_links.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_links])
            block.body = r"""\href{https://github.com/Nokheenig?tab=stars}{GitHub\hspace{1.5mm}\includegraphics[scale=0.075]{hlink.png}}\\"""
            block.footer = r"""\vspace{2.5mm}"""
            
            block = aside_links.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_links])
            block.body = r"""\includegraphics[width=1.5cm,height=3cm,keepaspectratio]{qr/resume_CAN_softDev.png}\\"""
            block.footer = r"""\vspace{2.5mm}"""

        aside_languages = aside and aside.createChild(id=self.const.section_aside_languages)
        if aside_languages:
            # aside_languages = self.createBlock(id=self.const.section_aside_languages, parent=self.blocks[self.const.section_aside])
            aside_languages.footer = r"""\vspace{2.5mm}%"""

            block = aside_languages.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_languages])
            block.body = r"""\makebox[4.3cm][l]{\textbf{French} (native)}\\"""

            block = aside_languages.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_languages])
            block.body = r"""\makebox[4.3cm][l]{\textbf{English} (C1,Bulats)}\\"""

            block = aside_languages.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_languages])
            block.body = r"""\makebox[4.3cm][l]{\textbf{German} (B1)}\\"""

            block = aside_languages.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_languages])
            block.body = r"""\makebox[4.3cm][l]{\textbf{Korean} (A1-2)}\\"""

        aside_strengths = aside and aside.createChild(id=self.const.section_aside_strengths)
        if aside_strengths:
            # aside_strengths = self.createBlock(id="strengths", parent=self.blocks[self.const.section_aside])
            pass

        aside_strengths_list = aside_strengths and aside_strengths.createChild(id=f"{aside_strengths.id}_list")
        if aside_strengths_list:
            # aside_strengths_list = self.createBlock(id="strengths_list", parent=self.blocks["strengths"])
            aside_strengths_list.header = r"""\begin{itemize}"""
            aside_strengths_list.footer = r"""\end{itemize}"""

            block = aside_strengths_list.createChild() # self.createBlock(parent=self.blocks["strengths_list"])
            block.body = r"""\item Teamwork"""

            block = aside_strengths_list.createChild() # self.createBlock(parent=self.blocks["strengths_list"])
            block.body = r"""\item Curiosity/Creativity"""

            block = aside_strengths_list.createChild() # self.createBlock(parent=self.blocks["strengths_list"])
            block.body = r"""\item Initiative"""

            block = aside_strengths_list.createChild() # self.createBlock(parent=self.blocks["strengths_list"])
            block.body = r"""\item Organization"""

            block = aside_strengths_list.createChild() # self.createBlock(parent=self.blocks["strengths_list"])
            block.body = r"""\item Adaptability"""

        aside_mechanical_skills = aside and aside.createChild(id=self.const.section_aside_mechanicalskills)
        if aside_mechanical_skills:
            # aside_mechanical_skills = self.createBlock(id=self.const.section_aside_mechanicalskills, parent=self.blocks[self.const.section_aside])
            aside_mechanical_skills.header = r"""\section{Mechanical Skills}
\begin{itemize}"""
            aside_mechanical_skills.footer = r"""\end{itemize}"""

            block = aside_mechanical_skills.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item CAD"""
            block.body = r""" \\ \hspace*{0.2em}\small\textit{Catia, Creo, TopSolid}"""

            block = aside_mechanical_skills.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item CAM"""
            block.body = r""" \\ \hspace*{0.2em}\small\textit{TopSolid}"""

            block = aside_mechanical_skills.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item PDM"""
            block.body = r""" \\ \hspace*{0.2em}\small\textit{NewPDM, Windchill, TopSolid}"""

            block = aside_mechanical_skills.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item FEM / CAE"""
            block.body = r""" \\ \hspace*{0.2em}\small\textit{Ansys, Abaqus, Hyperworks}"""

            block = aside_mechanical_skills.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item 3D Printing"""
            block.body = r""""""

        aside_hobbies = aside and aside.createChild(id=self.const.section_aside_hobbies)
        if aside_hobbies:
            # aside_hobbies = self.createBlock(id=self.const.section_aside_hobbies, parent=self.blocks[self.const.section_aside])
            aside_hobbies.header = r"""\section{Hobbies}
\begin{itemize}"""
            aside_hobbies.footer = r"""\end{itemize}"""

            block = aside_hobbies.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item Hiking"""

            block = aside_hobbies.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item Music / Concerts"""

            block = aside_hobbies.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item Cycling, Motorcycling"""

            block = aside_hobbies.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item Photography"""

            block = aside_hobbies.createChild() # self.createBlock(parent=self.blocks[self.const.section_aside_mechanicalskills])
            block.header = r"""\item Traveling"""

        aside_dateid = aside and aside.createChild(id=self.const.section_aside_dateid)
        if aside_dateid:
            # aside_dateid = self.createBlock(id=self.const.section_aside_dateid, parent=self.blocks[self.const.section_aside])
            aside_dateid.header = r"""\vspace{2.5mm}%\begin{flushleft}
\small \emph{Auto-generated in \LaTeX}\\"""
            aside_dateid.body = r"""\small \emph{Date: 02/05/2026} \hspace*{8mm}\\
\small \emph{Id: 084fe0}"""

        skills_item = skills and skills.createChild(id=self.const.section_skills_backend)
        if skills_item:
            # skills_item = self.createBlock(id=self.const.section_skills_backend, parent=self.blocks[self.const.section_skills])
            skills_item.header = r"""\item \large Back-end / Server \
\normalsize
\begin{flushleft}"""
            skills_item.footer = r"""\end{flushleft}   """
            skills_item.body = r"""\includegraphics[scale=0.40]{5stars.png}\hspace{1.5mm}\textbf{C\#}
\includegraphics[scale=0.40]{5stars.png}\hspace{1.5mm}\textbf{Python}\\Flask, Django, FastAPI, SQLAlchemy, PyMongo, PyTest, Numpy, Uvicorn, Pydantic, Requests\\\vspace{2mm}
\includegraphics[scale=0.40]{4stars.png}\hspace{1.5mm}\textbf{Node.js}\\Express.js, Bcrypt\\
\includegraphics[scale=0.40]{3stars.png}\hspace{1.5mm}\textbf{Java}
\includegraphics[scale=0.40]{3stars.png}\hspace{1.5mm}\textbf{\small Nginx,Apache}
\includegraphics[scale=0.40]{4stars.png}\hspace{1.5mm}\textbf{Rest API}\\OpenAPI standard\\"""

        exp_item = experience and experience.createChild()
        if exp_item:
            # exp_item = self.createBlock(parent=self.blocks[self.const.section_experience])
            exp_item.body = r"""\begin{entrylist}
    \entry
    {09/24 - Today.}
    {Software Engineer}
    {TopSolid, \textit{Paris, FR}}
    {Post-processors developement in: C\# (.Net)}
\end{entrylist}"""
            exp_item_details = exp_item.createChild()
            list_block = exp_item_details.createChild()
            list_block.header = r"""\vspace{-15pt}
\vspace{0.5mm}
\begin{itemize}
    \setlength{\itemsep}{1pt}
    \setlength{\parskip}{0pt}
    \setlength{\parsep}{0pt}"""
            list_block.footer = r"""\end{itemize}"""

            block = list_block.createChild()
            block.body = r"\item Develop from scratch CNC machines, 6 axes robots and 2D/3D laser cutting machines post-processors in C\# (.Net), G-code (Fanuc), ... + customization layer in proprietary language for our integrators."

            block = list_block.createChild()
            block.body = r"\item Write documentations and specifications."

            block = list_block.createChild()
            block.body = r"\item Test and fine-tune in production on customer site."

            block = list_block.createChild()
            block.body = r"\item Write scripts and automations."

            block = list_block.createChild()
            block.body = r"\item Install and configure test/machining simulation virtual machines."

            block = list_block.createChild()
            block.body = r"\item Ensure technical support for customers and improve existing post-processors."

        if education:
            education_item = education and education.createChild()
            education_item.body = r"""\begin{entrylist}
    \entry
    {09/22 - 08/23}
    {Bachelor Degree in Software Design \& Development}
    {EPSI, \textit{Lyon, FR}}
    {Minor: Data/AI; \hspace{7mm} 09/23: Government Skill Certification}
\end{entrylist}
\vspace{0.5mm}"""



if __name__ == "__main__":
    resume = LatexResumeBuilder()

    resumeContents = resume.Build()

    with open("resume.tex", "w", encoding="utf-8") as f:
        f.write(resumeContents)

    # with open("file.txt", "r", encoding="utf-8") as f:
    #     print(f.read())