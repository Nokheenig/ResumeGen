import os
import json
from definitions import ROOT_DIR
from datetime import datetime, timedelta
import time
from enum import Enum
import re
import math
from utils import deep_merge_dict, deep_extend_dict
import copy
from pathlib import Path
from __future__ import annotations
from classes.resume_generator_session import LatexResumeBuilder

# import logging as logDal
# logDal.basicConfig(filename=os.path.join(ROOT_DIR,"logs","resumeGenerator.log"), encoding='utf-8', filemode='w', format='%(asctime)s-%(levelname)s:%(message)s', level=logDal.DEBUG)

import argparse
import hashlib

parser = argparse.ArgumentParser(description="A resume generator script that takes some options to control the script output.")

# parser.add_argument("-o", "--output", help="Specify the output file")
parser.add_argument("-p", "--profiles", help="Specify the resume profiles to generate: webDev, mobileDev, dataScientist, dataEngineer, devOps, ...",
    nargs="+",  # allows multiple values
    required=False
                    )
parser.add_argument("-n", "--no-filtering", help="Override the filtering of resume data and generate with the maximum of data available.",
    required=False
                    )
# parser.add_argument("-h", "--help", action="help", help="Show help message and exit")
parser.add_argument("-f", "--files", help="Specify the desired resumes (source data files, optionally with profiles) to generate.",
    nargs="+",  # allows multiple values
    required=True
                    )
parser.add_argument("-o", "--outputdir") # , action='store_true'

args = parser.parse_args()

OUTPUT_DIR = Path(os.path.join(ROOT_DIR,"tex"))
if args.outputdir:
    OUTPUT_DIR = Path(args.outputdir)
# if args.output:
#     print("Arguments Passed with -o Option:-", args.output)
# if args.profiles:
#     print("Arguments Passed with -o Option:-", args.output)
# else:
#     pass

class ResumeGenerator:
    class Resume:
        def __init__(self, resumeData: dict, profile: str, outputFile: str):
            self.resumeData = resumeData
            self.profile = profile
            self.outputFile = outputFile
            self.builder = LatexResumeBuilder()
            self.documentRoot = self.builder.document
            
            pass
        def __repr__(self):
            return self.buildResume()
        
        def buildResume(self) -> str:
            return self.__repr__()
        
        def initialize(self):
            self.init_base_document()
            self.init_build_header()
            self.init_build_aside()
            self.init_build_skills()
            self.init_build_experience()
            self.init_build_education()
            

        def init_base_document(self):
            self.documentRoot.header = r"%!TEX TS-program = xelatex"
            imports = self.documentRoot.getBlock(id=self.const.section_imports)
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

            definitions = self.documentRoot.getBlock(id=self.const.section_definitions)
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
            self.document = self.documentRoot.getBlock(id=self.const.section_document)
            if self.document:
                self.document.header = r"\begin{document}"
                self.document.footer = r"\end{document}"

        def init_build_header(self):
            header = self.document.createChild(id=self.const.section_header)
            basics = self.resumeData["basics"]
            fname = basics["firstname"]
            lname = basics["lastname"]
            summary = basics["summary"]
            # catchPhrase = basics["catchPhrase"]

            if header and fname and lname and summary:

                header.body = rf"""\header{fname}{lname}
      {summary}
      {{}}"""
            
            quote = self.document.createChild(id=self.const.section_quote)
            if quote:
                    quote.header = r"""\vspace*{-4.5mm}
\noindent\parbox{\linewidth}{
\vspace*{8.5mm}
\centering"""
                    quote.body = "French Engineer (CTI-accredited), now working as a software developer with a strong engineering mindset. Always eager to learn and improve, I am looking for new challenges!"
                    quote.footer = "}"
            pass

        def init_build_aside(self):
            aside = self.document.createChild(id=self.const.section_aside)
            if aside:
                aside.header = r"""\begin{aside}
\vspace{30mm}"""
                aside.footer = r"""\end{aside}"""   
            pass

            aside_infos = aside and aside.createChild(id=self.const.section_aside_infos)
            if aside_infos:
                aside_infos.header = r"""\section{Infos}"""
                block = aside_infos.createChild()
                block.body = r"""%33 yo\\
Full driving licence\\"""
                block.footer = r"""\vspace{3.5mm}"""

                block = aside_infos.createChild()
                block.body = r"""Legally authorized to work in Canada.\\"""
                block.footer = r"""\vspace{2.5mm}"""
            
            aside_contact = aside and aside.createChild(id=self.const.section_aside_contact)
            if aside_contact:
                block = aside_contact.createChild() 
                block.body = r"""\href{mailto:y.chamillard.pro@gmail.com}{\small y.chamillard.pro@gmail.com}\\"""
                block.footer = r"""\vspace{2.5mm}"""
                
                block = aside_contact.createChild() 
                block.body = r"""\href{https://www.linkedin.com/in/yoannchamillard/?locale=en_US}{LinkedIn\hspace{1.5mm}\includegraphics[scale=0.075]{hlink.png}}\\"""
                block.footer = r"""\vspace{2.5mm}"""

            aside_links = aside and aside.createChild(id=self.const.section_aside_links)
            if aside_links:
                block = aside_links.createChild()
                block.body = r"""\href{https://github.com/Nokheenig?tab=stars}{GitHub\hspace{1.5mm}\includegraphics[scale=0.075]{hlink.png}}\\"""
                block.footer = r"""\vspace{2.5mm}"""
                
                block = aside_links.createChild()
                block.body = r"""\includegraphics[width=1.5cm,height=3cm,keepaspectratio]{qr/resume_CAN_softDev.png}\\"""
                block.footer = r"""\vspace{2.5mm}"""

            aside_languages = aside and aside.createChild(id=self.const.section_aside_languages)
            if aside_languages:
                aside_languages.footer = r"""\vspace{2.5mm}%"""

                block = aside_languages.createChild() 
                block.body = r"""\makebox[4.3cm][l]{\textbf{French} (native)}\\"""

                block = aside_languages.createChild() 
                block.body = r"""\makebox[4.3cm][l]{\textbf{English} (C1,Bulats)}\\"""

                block = aside_languages.createChild() 
                block.body = r"""\makebox[4.3cm][l]{\textbf{German} (B1)}\\"""

                block = aside_languages.createChild() 
                block.body = r"""\makebox[4.3cm][l]{\textbf{Korean} (A1-2)}\\"""

            aside_strengths = aside and aside.createChild(id=self.const.section_aside_strengths)
            if aside_strengths:
                pass

            aside_strengths_list = aside_strengths and aside_strengths.createChild(id=f"{aside_strengths.id}_list")
            if aside_strengths_list:
                aside_strengths_list.header = r"""\begin{itemize}"""
                aside_strengths_list.footer = r"""\end{itemize}"""

                block = aside_strengths_list.createChild()
                block.body = r"""\item Teamwork"""

                block = aside_strengths_list.createChild()
                block.body = r"""\item Curiosity/Creativity"""

                block = aside_strengths_list.createChild()
                block.body = r"""\item Initiative"""

                block = aside_strengths_list.createChild()
                block.body = r"""\item Organization"""

                block = aside_strengths_list.createChild()
                block.body = r"""\item Adaptability"""

            aside_mechanical_skills = aside and aside.createChild(id=self.const.section_aside_mechanicalskills)
            if aside_mechanical_skills:
                aside_mechanical_skills.header = r"""\section{Mechanical Skills}
\begin{itemize}"""
                aside_mechanical_skills.footer = r"""\end{itemize}"""

                block = aside_mechanical_skills.createChild()
                block.header = r"""\item CAD"""
                block.body = r""" \\ \hspace*{0.2em}\small\textit{Catia, Creo, TopSolid}"""

                block = aside_mechanical_skills.createChild()
                block.header = r"""\item CAM"""
                block.body = r""" \\ \hspace*{0.2em}\small\textit{TopSolid}"""

                block = aside_mechanical_skills.createChild()
                block.header = r"""\item PDM"""
                block.body = r""" \\ \hspace*{0.2em}\small\textit{NewPDM, Windchill, TopSolid}"""

                block = aside_mechanical_skills.createChild()
                block.header = r"""\item FEM / CAE"""
                block.body = r""" \\ \hspace*{0.2em}\small\textit{Ansys, Abaqus, Hyperworks}"""

                block = aside_mechanical_skills.createChild()
                block.header = r"""\item 3D Printing"""
                block.body = r""""""

            aside_hobbies = aside and aside.createChild(id=self.const.section_aside_hobbies)
            if aside_hobbies:
                aside_hobbies.header = r"""\section{Hobbies}
\begin{itemize}"""
                aside_hobbies.footer = r"""\end{itemize}"""

                block = aside_hobbies.createChild()
                block.header = r"""\item Hiking"""

                block = aside_hobbies.createChild()
                block.header = r"""\item Music / Concerts"""

                block = aside_hobbies.createChild()
                block.header = r"""\item Cycling, Motorcycling"""

                block = aside_hobbies.createChild()
                block.header = r"""\item Photography"""

                block = aside_hobbies.createChild()
                block.header = r"""\item Traveling"""

            aside_dateid = aside and aside.createChild(id=self.const.section_aside_dateid)
            if aside_dateid:
                aside_dateid.header = r"""\vspace{2.5mm}%\begin{flushleft}
\small \emph{Auto-generated in \LaTeX}\\"""
                aside_dateid.body = r"""\small \emph{Date: 02/05/2026} \hspace*{8mm}\\
\small \emph{Id: 084fe0}"""

        def init_build_skills(self):
            skills = self.document.createChild(id=self.const.section_skills)
            if skills:
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
\vspace*{-2.0mm}"""

            skills_item = skills and skills.createChild(id=self.const.section_skills_backend)
            if skills_item:
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

        def init_build_experience(self):
            experience = self.document.createChild(id=self.const.section_experience)
            if experience:
                experience.header = r"""\section{Work Experience}
\vspace*{-0.25cm}"""

            exp_item = experience and experience.createChild()
            if exp_item:
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
        
        def init_build_education(self):
            education = self.document.createChild(id=self.const.section_education)
            if education:
                education.header = r"""\vspace*{-0.5cm}
    \vspace*{0.45cm}
    \section{Education - Certifications}
    \vspace*{-0.25cm}
    \vspace{0.5mm}"""
                
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
        
    def __init__(self, args) -> None:
        with open(os.path.join(ROOT_DIR,"res",f"doc_header.tex")) as f:
            self.docHeader = f.read()

        self.args = args
        self.today = datetime.now()
        self.targetDay = self.today
        self.year = str(self.targetDay.year)
        self.month = str(self.targetDay.month)
        self.day = "0" + str(self.targetDay.day) if len(str(self.targetDay.day)) < 2 else str(self.targetDay.day) #on ajoute 0 devant le jour s'il est compris entre 1 et 9
        self.currentProfile = None
        # self.sessionProfiles = self.getSessionProfileList
        self.isResumeFilter = True # #TODO when starting a new resume, set back to true unless current resume profile is unfiltered -> profile repalced with default and isFiltered set to false
        self.currentProfiles = None

        self.validatedInputFilesPathList = self.getValidatedInputFiles()
        self.isDetailedResume = self.args.no_filtering is not None and self.args.no_filtering
        self.currentFile = None
        self.currentFileName = None
        self.currentFileDir = None
        self.currentResumeData = None
        self.currentResumeProfiles = None
        self.currentResume = None
        # print("cancelling job...")
        # exit()
    
    # def isResumeDataFiltered(self) -> bool:
    #     return "-unfiltered" in self.currentProfile
        
    def getSessionProfileList(self) -> list[str]:
        profiles = ["default"]
        if self.args.profiles:
            profiles =  [ profile for profile in self.args.profiles if profile in self.rawDataDictionariesProfileFullList] #TODO : change from list comprehension to add notification when a profile has been discarded for not existing in base data

        if "all" in profiles: 
            return self.rawDataDictionariesProfileFullList
        else:
            return profiles

    def generateResumes(self):
        # Load all unfiltered data files from leaf to root (no parent data source)
        self.rawDataDictionariesByFile = self.getRawDataDictionariesByFile()

        # get a list of all profiles in loaded data files
        self.rawDataDictionariesProfileFullList = self.getRawDataProfileFullList()

        # get resume generating session profiles list
        self.sessionProfileList = self.getSessionProfileList()

        # 
        self.unconsolidatedResumeDataByFileByProfile = self.getUnconsolidatedResumeDataByFileByProfile()

        self.consolidatedResumeDataByFileByProfile = self.getConsolidatedResumeDataByFileByProfile()

        self.resumesByFileByProfile = self.getResumesByFileByProfile()

        self.writeResumes()
        pass
    
    def writeResumes(self, inResumes: dict[str,dict[str,ResumeGenerator.Resume]]):
        for file, resumeByProfile in inResumes.items():
            for profile, resume in resumeByProfile.items():
                self.writeResume(resume)

    def writeResume(self, inResume: ResumeGenerator.Resume):
        with open(inResume.outputFile, "w", encoding='utf-8') as f:
            f.write(inResume.buildResume())

            

    def getResumesByFileByProfile(self) -> dict[str,dict[str,ResumeGenerator.Resume]]:
        output = {}
        for file, fileDataByProfile in enumerate(self.consolidatedResumeDataByFileByProfile):
            output[file] = {}
            for profile, data in enumerate(fileDataByProfile):
                extIndex = f"{file}".rfind(".")
                filename = f"{file}"[:extIndex]
                extension = f"{file}"[extIndex+1:]
                profileTag = f"_{profile}" if profile not in ["default"] else ""
                filename = f"{filename}{profileTag}.tex"
                outputFile = OUTPUT_DIR / filename
                resume = self.Resume(resumeData=data, profile=profile, outputFile=outputFile)
                output[file][profile] = resume
        return output

    def getConsolidatedResumeDataByFileByProfile(self) -> dict:
        output = {}
        # resumeHasParentData = lambda  
        for file in self.validatedInputFilesPathList:
            output[file] = {}
            for profile in self.sessionProfileList:
                resumeDataStack = []
                fileData = self.unconsolidatedResumeDataByFileByProfile[file][profile]

                while fileData is not None:
                    resumeDataStack.add(fileData)
                    fileData = self.getResumeParentData(fileData)

                # resume base data is base of the stack
                resumeData = resumeDataStack.pop(0)

                # while elements left on the stack, extend base resume data
                while len(resumeDataStack)>0:
                    resumeData = deep_extend_dict(base=resumeData, extension=resumeDataStack.pop(0))

                # add resulting dictionary to output dict under current file key
                output[file][profile] = resumeData
        return output
    
    def getRawDataProfileFullList(self) -> set[str]:
        profileList = set()
        for file, fileData in enumerate(self.rawDataDictionariesByFile):
            fileProfiles = self.getResumeProfiles(fileData)
            for profile in fileProfiles: profileList.add(profile)
        profileList.add("default")

        return profileList

    def getUnconsolidatedResumeDataByFileByProfile(self) -> dict:
        outData = {}
        for file, fileData in enumerate(self.rawDataDictionariesByFile):
            fileProfiles = self.getResumeProfiles(fileData)
            filteredProfiles = [profile for profile in fileProfiles if profile in self.sessionProfileList]
            for profile in filteredProfiles:
                if file not in outData: outData[file] = {}
                data = copy.deepcopy(fileData)
                data = self.deepFilterProfileDict(inRawDict=data, inProfile=profile, isFilter="unfiltered" in profile)
                # key = f"{file}_{profile}"
                outData[file][profile] = data
        return outData
            
    # def getProfileFilteredDict(self, inRawDict: dict, inProfile: str) -> dict:
    #     return self.deepFilterProfileDict(inDict=inRawDict, inProfile=inProfile, isFilter="unfiltered" in inProfile)

    def deepFilterProfileDict(self, inDict: dict, inProfile: str, isFilter = True) -> dict:
        """
        Filter input dictionary with inProfile
        """
        for key, val in enumerate(inDict):
            # if key->value is dictionary recursively call function to filter deeper dictionary
            if isinstance(val, dict): self.deepFilterProfileDict(inDict=val, inProfile=inProfile, isFilter=isFilter)
            # if key is list of dict: loop on items to filter and keep or remove them based on profile
            if isinstance(val, list[dict]):
                for itemIdx in range(len(val), -1, -1):
                    item = val[itemIdx]
                    if "profile" in item:
                        profile = item["profile"]
                        pin = "in" in profile
                        pex = "except" in profile
                        isDisplayed = True
                        if pin and inProfile not in pin and isFilter: isDisplayed = False
                        if pex and inProfile in pex and isFilter: isDisplayed = False
                        if not isDisplayed:
                            val.pop(itemIdx)
                            continue
                        if pin: profile.pop("in", None)
                        if pex: profile.pop("except", None)
                        if inProfile in profile:
                            overrides = profile[inProfile]
                            item.pop("profile", None)
                            for overFieldKey, overFieldData in enumerate(overrides):
                                if overFieldKey in item and isinstance(overFieldData, dict) and isinstance(item[overFieldKey], dict):
                                    deep_merge_dict(base=item, override=overFieldData)
                                else:
                                    item[overFieldKey] = overFieldData
                        if "profile" in item: item.pop("profile", None)
            else:
                pass
        
        if "profile" in inDict:
            profile = inDict["profile"]
            if inProfile in profile:
                overrides = profile[inProfile]
                inDict.pop("profile", None)
                for overFieldKey, overFieldData in enumerate(overrides):
                    if overFieldKey in inDict and isinstance(overFieldData, dict) and isinstance(inDict[overFieldKey], dict):
                        deep_merge_dict(base=inDict, override=overFieldData)
                    else:
                        inDict[overFieldKey] = overFieldData
            if "profile" in inDict: inDict.pop("profile", None)

            pass
        return inDict

    def getResumeProfiles(self, inDict: dict) -> list[str]:
        if "file" in inDict and "profiles" in inDict["file"] and isinstance(inDict["file"]["profiles"], list[str]):
            fileProfiles = inDict["file"]["profiles"]
            if "default" not in fileProfiles: fileProfiles.append("default")
            return fileProfiles
        else:
            return ["default"]

        

    def getResumeParentData(self, inDict: dict, inProfile: str) -> dict|None:
        if not self.resumeHasParentData(inDict):
            return None
        parentFile = inDict["file"]["parent"]
        return self.unconsolidatedResumeDataByFileByProfile[parentFile][inProfile] # TODO must harden, what if key doesn t exist ?

    def resumeHasParentData(self, inDict: dict) -> bool:
        return "file" in inDict and "parent" in inDict["file"] and inDict["file"]["parent"]

    def getRawDataDictionariesByFile(self) -> dict[str,dict]:
        output = {}
        for file in self.validatedInputFilesPathList:
            fileBranchLoaded = False
            currentFile = file
            while not fileBranchLoaded:
                if currentFile in output:
                    fileBranchLoaded = True
                    continue
                else:
                    with open(file, "r", encoding='utf-8') as f:
                        fileContents = json.loads(f.read())
                        output[currentFile] = fileContents
                        if "file" in fileContents and "parent" in fileContents["file"]:
                            parentFile = fileContents["file"]["parent"]
                            if parentFile:
                                currentFile = parentFile
                                continue
                            else:
                                fileBranchLoaded = True
                                continue
                        else:
                            fileBranchLoaded = True
                            continue
            # if fileBranchLoaded:
        return output

    def getValidatedInputFiles(self) -> list[tuple[str, list[str]]]:
        if self.args.files is None or len(self.args.files) < 1:
            print(f"No target json resume in input !\nAdd -f and specify the target resumes to generate tex resumes\nCancelling job...")
            exit()
        # print(f"files args list: {self.args.files}")
        # Check files are resume json
        inputFiles = []
        discardedFiles = []
        jsonResumeValidator = re.compile("resume_[A-Z0-9_-]+\\.json")

        for file in self.args.files:
            filename = file[file.rfind("/")+1:]
            # print("filename: ", filename)
            if jsonResumeValidator.match(filename):
                inputFiles.append(file)
            else:
                discardedFiles.append(file)

        if len(discardedFiles) > 0:
            print(f"{len(discardedFiles)} input target resumes aren't valid input json resume files!" ,discardedFiles)
        
        return inputFiles

    def getCurrentProfiles(self) -> str|None:
        if self.args.profiles:
            invalidProfiles = [profile for profile in self.args.profiles if profile not in ["webDev", "mobileDev", "devOps", "softDev"]]
            if invalidProfiles:
                # logDal.error(f"Invalid profiles: {', '.join(invalidProfiles)}")
                print(f"Invalid profiles: {', '.join(invalidProfiles)}")
                return ["unknown"]
            return self.args.profiles
        else:
            return [None]

    def createResumes(self):
        outputFilesDirPath = os.path.join(ROOT_DIR,"tex")
        if not os.path.isdir(outputFilesDirPath):
                os.mkdir(outputFilesDirPath)

        if(self.currentProfile == "unknown"):
            errMsg = f"Profile {self.args.profiles} not found"
            # logDal.error(errMsg)
            print(errMsg)
            return
        
        # self.createdAt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # self.createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %z", time.localtime()) 
        # for filename in ["resume_FR", "resume_FR_detailed", "resume_CAN", "resume_CAN_detailed", "resume_CAN-QC", "resume_CAN-QC_detailed", "resume_AS_detailed"]:
        profileThreshold = 5
        profileGenerated = 0
        while len(self.validatedInputFilesPathList) > 0:
            # if profileGenerated >= profileThreshold:
            #     print(f"Profile generation threshold reached: {profileThreshold} profiles generated.")
            #     logDal.info(f"Profile generation threshold reached: {profileThreshold} profiles generated.")
            #     break
            # profileGenerated += 1
            self.currentFile = self.validatedInputFilesPathList.pop(0)
            self.currentFileName = self.currentFile[self.currentFile.rfind("/")+1:self.currentFile.rfind(".json")] 
            self.currentFileDir = os.path.dirname(self.currentFile)
            print(f"Processing file: {self.currentFileName}.json")
            # logDal.info(f"Processing file: {self.currentFileName}.json")
            skipFile = False
            sourceFilesDataStack = []
            with open(self.currentFile, "r", encoding='utf-8') as f:
                sourceFilesDataStack.append(json.loads(f.read()))
            sourceFileHasParent = 'parent' in sourceFilesDataStack[0]['file'] and sourceFilesDataStack[0]['file']['parent'] is not None
            while sourceFileHasParent:
                parentFilePath = sourceFilesDataStack[0]['file']['parent']
                print(f"Fetching parent file data: {parentFilePath}")
                # logDal.info(f"Fetching parent file data: {parentFilePath}")
                if not os.path.exists(parentFilePath):
                    # prepend current file dir to parent file path
                    parentFilePath = os.path.join(self.currentFileDir, parentFilePath)
                if not os.path.exists(parentFilePath):
                    errMsg = f"Parent file {parentFilePath} not found, aborting resume generation for {self.currentFileName}.json"
                    # logDal.error(errMsg)
                    print(errMsg)
                    skipFile = True
                    break
                with open(parentFilePath, "r", encoding='utf-8') as f:
                    sourceFilesDataStack.insert(0, json.loads(f.read()))
                sourceFileHasParent = 'parent' in sourceFilesDataStack[0]['file'] and sourceFilesDataStack[0]['file']['parent'] is not None
            if skipFile:
                print(f"Skipping file {self.currentFileName}.json due to missing parent file.")
                # logDal.info(f"Skipping file {self.currentFileName}.json due to missing parent file.")
                continue

            self.currentResumeData = {}
            self.currentResumeProfiles = None
            for sourceFileData in sourceFilesDataStack:
                if 'file' in sourceFileData and 'profiles' in sourceFileData['file']:
                    if self.currentResumeProfiles is None:
                        self.currentResumeProfiles = list(set(sourceFileData['file']['profiles']))
                    else:
                        self.currentResumeProfiles = list(set(self.currentResumeProfiles) | set(sourceFileData['file']['profiles']))
                # if self.currentProfile is not None and self.currentProfile not in self.sessionProfiles:
                #     print(f"Skipping profile {self.currentProfile} for file {self.currentFileName} as it is not in the session profiles.")
                #     logDal.info(f"Skipping profile {self.currentProfile} for file {self.currentFileName} as it is not in the session profiles.")
                #     continue
                # print(f"Current profile: {self.currentProfile}")
                # logDal.info(f"Current profile: {self.currentProfile}")
                self.currentResumeData = deep_merge_dict(base=self.currentResumeData, override=sourceFileData)

            if self.currentResumeProfiles is None:
                self.currentResumeProfiles = ["default"]
            else:
                self.currentResumeProfiles = list(set(self.currentResumeProfiles))
                if self.sessionProfiles[0] != "all":
                    # Filter current resume profiles to only include those in session profiles
                    self.currentResumeProfiles = [profile for profile in self.currentResumeProfiles if profile in self.sessionProfiles]
                    # for profile in self.currentResumeProfiles:
                    #     if profile not in self.sessionProfiles:
                    #         print(f"Profile {profile} not in session profiles, removing it from current resume profiles.")
                    #         logDal.info(f"Profile {profile} not in session profiles, removing it from current resume profiles.")
                    #         self.currentResumeProfiles.remove(profile)
            
            print(f"Generating resume for profiles: {self.currentResumeProfiles}")
            # logDal.info(f"Generating resume for profiles: {self.currentResumeProfiles}")
            
            while len(self.currentResumeProfiles) > 0:
                self.currentProfile = self.currentResumeProfiles.pop(0)
                if self.currentProfile is None or self.currentProfile == "default":
                    print(f"INFO: Generating resume for default profile.")
                    # logDal.info(f"INFO: Generating resume for default profile.")
                else:
                    print(f"INFO: Generating resume for profile: {self.currentProfile}")
                    # logDal.info(f"INFO: Generating resume for profile: {self.currentProfile}")
                
                #self.generateResume(outputFilesDirPath=outputFilesDirPath)
                filename = self.currentFileName

                if self.currentProfile is not None and self.currentProfile != "default":
                    filename += f"_{self.currentProfile}"

                if self.isDetailedResume:
                    filename += "_detailed"
                
                self.currentOutputFileName = filename
                
                self.countryCode = self.currentFileName.split("_")[1].split("-")[0]
                # self.dataRedirectCountryCode = None
                # dataRedirectCountryCodes = {
                #     "US": ["CAN", "AS", "UK"],
                #     "FR": ["CAN-QC"],
                # }
                # for k, v in dataRedirectCountryCodes.items():
                #     if self.countryCode in v:
                #         self.dataRedirectCountryCode = k
                #         break
                # self.loadResumeData(targetCountryCode=self.dataRedirectCountryCode if self.dataRedirectCountryCode else self.countryCode)
                outFileContent = self.buildResume(targetCountryCode=self.countryCode, detailed=self.isDetailedResume)
                
                outputFilePath = os.path.join(outputFilesDirPath,f"{self.currentOutputFileName}.tex")
                self.writeResumeToFile(outputFilePath=outputFilePath, resumeContent=outFileContent)

                print(f"INFO: Resume generated for {self.currentProfile} in {outputFilePath}")

    def writeResumeToFile(self, outputFilePath: str, resumeContent: str) -> None:
        """
        Writes the generated resume content to a file.
        :param outputFilePath: The path to the output file.
        :param resumeContent: The content of the resume to write.
        """
        with open(outputFilePath, "w", encoding='utf-8') as f:
            f.write(resumeContent)

    def loadResumeData(self, targetCountryCode: str) -> None:
        resumeDataPath = os.path.join(ROOT_DIR,"res",f"resume_{targetCountryCode}.json")
        with open(resumeDataPath, "r", encoding='utf-8') as f:
            self.currentResumeData = json.loads(f.read())

    def buildResume(self, targetCountryCode: str = "FR", detailed: bool = False) -> str:
        
        self.createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %z")
        self.createdOn = self.getCreatedOn()
        self.resumeId = self.getResumeId()

        metadata = self.buildMetadata()
        header = self.buildHeader()
        aside = self.buildAside(targetCountryCode=targetCountryCode)
        catchPhrase = self.buildCatchPhrase()
        skills = self.buildSkills()
        experience = self.buildExperience(detailed=detailed)
        education = self.buildEducation()
        hobbies = self.buildHobbies()

        

        resume = f"""
{self.docHeader}
{metadata}
\\begin{{document}}
{header}
{aside}
{catchPhrase}
{skills}
{experience}
{education}
"""
        if detailed: resume += f"""{hobbies}\n"""
        resume += f"""\\end{{document}}""" 
        return resume
    
    def getCreatedOn(self) -> str:
        if self.countryCode in ["FR", "CAN-QC"]:
            return datetime.now().strftime("%d/%m/%Y")
        else:
            return datetime.now().strftime("%m/%d/%Y")

    def getResumeId(self) -> str:
        resumeId = "default"
        if self.currentProfile is not None:
            resumeId = self.currentProfile
        resumeId += f"_{self.createdAt}"
        resumeId = hashlib.shake_256(resumeId.encode()).hexdigest(3)
        return resumeId

    def buildMetadata(self) -> str:
        name = self.currentResumeData["basics"]["name"]
        # print("self.dataRedirectCountryCode: ", self.dataRedirectCountryCode)
        # docType = "Curriculum Vitae" if self.dataRedirectCountryCode == "FR" else "Resume"
        # print("self.countryCode: ", self.countryCode)
        docType = "Curriculum Vitae" if self.countryCode == "FR" else "Resume"
        summary = self.currentResumeData["basics"]["summary"].replace("~", "").replace("/", "").replace("(", "").replace(")", "")
        keywords = [
            f"profile:{self.currentProfile}" if self.currentProfile else "profile:default",
            "resume", "developer", "software", "engineer", "C\\# (.Net)", "Python", 
            "Javascript", "Node.js", "Java", "Kotlin", "Android", "Rest API", 
            "Git / GitLab", "Docker", "Jenkins", "Selenium", "Cron", "Html-Css", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase", "Bash", "Jira", "Regex",
            f"createdAt:{self.createdAt}", f"id:{self.resumeId}"
        ]
        formattedKeywords = "; ".join(keywords).replace("/", "").replace("(", "").replace(")", "")
        metadata = f"""
\\title{{{name} -- Resume}}
\\author{{{name}}}
\\date{{{self.day}/{self.month}/{self.year}}}

\\hypersetup{{
  pdftitle={{{name} -- Resume}},
  pdfauthor={{{name}}},
  pdfsubject={{{summary} - {docType}}},
  pdfkeywords={{{formattedKeywords}}},
  pdfcreator={{LuaLaTeX}},
  pdfproducer={{LuaLaTeX}}
}}
"""
        return metadata

    def buildHeader(self) -> str:
        name = self.currentResumeData["basics"]["name"].split(" ")
        assert len(name) > 1
        summary = self.currentResumeData["basics"]["summary"]
        if(self.currentProfile in self.currentResumeData["basics"]["profile"]):
            summary = self.currentResumeData["basics"]["profile"][self.currentProfile]["summary"]
        header = f"""
\\header{{{name[0]}}}{{{name[-1]}}}
      {{{summary}}}
      {{}}
"""
        return header
    
    def buildAsideInfos(self) -> str:
        sectionName = self.currentResumeData["document"]["aside"]["sections"]["infos"]["name"]
        sectionContent = self.currentResumeData["document"]["aside"]["sections"]["infos"]["content"]
        infos = f"""{sectionContent}"""
        return infos

    def buildAsideAddress(self) -> str:
        sectionName = self.currentResumeData["document"]["aside"]["sections"]["address"]["name"]
        location = self.currentResumeData["basics"]["location"]["Paris,France"]
        address = location["address"]
        postalCode = location["postalCode"]
        city = location["city"]
        countryCode = location["countryCode"]
        country = location["country"]
        region = location["region"]
        mobility = self.currentResumeData["document"]["aside"]["sections"]["address"]["mobility"]
        address = ""
        if city != "." and country != ".": address = f"""{city}, {country}\\\\"""
        if mobility: address += f"\n\\vspace{{1.5mm}}\n{mobility}"

        return address
        

    def buildAsideContact(self) -> str:
        sectionName = self.currentResumeData["document"]["aside"]["sections"]["contact"]["name"]
        phone = self.currentResumeData["basics"]["phone"]
        mail = self.currentResumeData["basics"]["email"]
        contact = ""
        if phone != ".": contact += f"{phone}\\\\\n"
        if mail != ".": contact += f"\\href{{mailto:{mail}}}{{\\small {mail}}}\\\\\n"
        #contact = f"""{phone}\\\\
#\\href{{mailto:{mail}}}{{\\small {mail}}}\\\\"""
        return contact

    def buildAsideOnlineProfiles(self) -> str:
        sectionName = self.currentResumeData["document"]["aside"]["sections"]["onlineProfiles"]["name"]
        
        profiles = f""
        profilesData = self.currentResumeData["basics"]["profiles"]
        for idx_profile, profile in enumerate(profilesData):
            network = profile["network"]
            url = profile["url"]
            line = f"" if idx_profile == 0 else f"\n"
            line += f"\\href{{{url}}}{{{network}\\hspace{{1.5mm}}\\includegraphics[scale=0.075]{{hlink.png}}}}\\\\"
            profiles += line
        profiles += "\n\\vspace{2.5mm}"
        profiles += f"\n\\includegraphics[width=1.5cm,height=3cm,keepaspectratio]{{qr/{self.currentOutputFileName}.png}}\\\\"

        return profiles

    def buildAsideLanguages(self) -> str:
        sectionName = self.currentResumeData["document"]["aside"]["sections"]["languages"]["name"]

        languages = f""
        languagesData = self.currentResumeData["languages"]
        for idx_language, language in enumerate(languagesData):
            lang = language["language"]
            level = language["fluency"]
            test = language["test"]
            line = f"" if idx_language == 0 else f"\n"
            line += f"\\makebox[4.3cm][l]{{\\textbf{{{lang}}} {test}}}\\\\"
            languages += line
        return languages

    def buildAsideSoftSkills(self, targetCountryCode: str) -> str:
        sectionName = self.currentResumeData["document"]["aside"]["sections"]["softSkills"]["name"]
        softSkills = f""
        if targetCountryCode in ["FR","CAN-QC"]:
            softSkills += f"\\includegraphics[scale=0.40]{{profileMap_FR.png}}"
        else:
            softSkills += f"\\includegraphics[scale=0.40]{{profileMap_EN.png}}"
        
        return softSkills

    def buildAsideOtherSections(self) -> str:
        #sectionName = self.currentResumeData["aside"]["sections"]["infos"]["name"]
        sections = ""
        sectionsData = self.currentResumeData["document"]["aside"]["otherSections"]
        for section in sectionsData:
            sectionName = section["name"]
            profileParams = section['profile']
            if self.currentProfile is not None and (profileParams['in'] is not None or profileParams['except'] is not None):
                if profileParams['except'] is not None and self.currentProfile in profileParams['except']:
                    continue
                if profileParams['in'] is not None and self.currentProfile not in profileParams['in']:
                    continue
            
            sectionStr = f"\n\\section{{{sectionName}}}"
            match section["type"]:
                case "rankedItems":
                    for item in section['items']:
                        itemName = item['name']
                        level = item['level']
                        itemStr = f"\n\\includegraphics[scale=0.40]{{{level}stars.png}}\\hspace{{1.5mm}}\\textbf{{{itemName}}}\\\\"
                        sectionStr += itemStr
                case "listItems":
                    sectionStr += f"\n\\begin{{itemize}}"
                    for item in section['items']:
                        itemName = item['name']
                        itemDetails = item['details']
                        sectionStr += f"\n\\item {itemName}"
                        if itemDetails:
                            # sectionStr += f" {itemDetails}"
                            sectionStr += f"\n \\\\ \\hspace*{{0.2em}}\\small\\textit{{{itemDetails}}}"
                    sectionStr += f"\n\\end{{itemize}}"
                case _:
                    pass
            sections += sectionStr
        return sections

    def buildAside(self, targetCountryCode: str) -> str:
        infos = self.buildAsideInfos()
        address = self.buildAsideAddress()
        contact = self.buildAsideContact()
        onlineProfile = self.buildAsideOnlineProfiles()
        languages = self.buildAsideLanguages()
        # softSkills = self.buildAsideSoftSkills(targetCountryCode=targetCountryCode)
        otherSections = self.buildAsideOtherSections()
        closureComment = self.buildClosureComment(targetCountryCode)

        aside = f"\\begin{{aside}}"

        if targetCountryCode not in ["USA","CAN","CAN-QC", "UK"]:
             aside += f"\n\\hspace{{10mm}}\\includegraphics[scale=0.148]{{Photo_CV.jpg}}"
        else:
            aside += f"\n\\vspace{{21mm}}"

        aside += f"""\n\\section{{Infos}}

{infos}\n\\vspace{{2.5mm}}
%{address}\n\\vspace{{2.5mm}}
{contact}\n\\vspace{{2.5mm}}
{onlineProfile}\n\\vspace{{2.5mm}}
{languages}\n\\vspace{{2.5mm}}%
{otherSections}\n\\vspace{{2.5mm}}%\\begin{{flushleft}}
{closureComment}
	%\\end{{flushleft}}
\\end{{aside}}"""
        return aside
    
    def buildClosureComment(self, targetCountryCode: str) -> str:
        autoGenComment = "Auto-generated in \\LaTeX"
        if targetCountryCode in ["FR","CAN-QC"]:
             autoGenComment = "Auto-généré en \\LaTeX"

        # createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        # resumeId = "default"
        # if self.currentProfile is not None:
        #     resumeId = self.currentProfile
        # resumeId += f"_{createdAt}"
        # resumeId = hashlib.shake_256(resumeId.encode()).hexdigest(3)

        closureComment = f"""\\small \\emph{{{autoGenComment}}}\\\\
\\small \\emph{{Date: {self.createdOn}}} \\hspace*{{8mm}}\\\\
\\small \\emph{{Id: {self.resumeId}}} % resumeId\\\\
%{{\\tiny {self.resumeId}}}\\\\ % resumeId
"""
        return closureComment

    def buildCatchPhrase(self) -> str:
        if(self.currentProfile in self.currentResumeData["basics"]["profile"]):
            catchPhrase = self.currentResumeData["basics"]["profile"][self.currentProfile]["catchPhrase"]
        else:
            catchPhrase = self.currentResumeData["basics"]["catchPhrase"]
        
        #catchPhraseOut = f"""
#\\vspace{{-3mm}}
#\\begin{{minipage}}[t]{{1.00\\linewidth}}
#{catchPhrase}
#\\end{{minipage}} % no space if you would like to put them side by side
#\\vspace{{1mm}}
#"""
        catchPhraseOut = f"""
\\vspace*{{-2.0mm}}
\\noindent\\parbox{{\\linewidth}}{{
  \\centering
  {catchPhrase}
}}
\\vspace*{{0.8mm}}
"""
        return catchPhraseOut

    def buildSkills(self) -> str:
        skillsData = self.currentResumeData['skills']
        skillsCurrentProfileData = self.getCurrentProfileSkillsData(skillsData)
        skillsSortedData = self.sortSkillSectionsInEqualColumns(skillsCurrentProfileData)
        # print("currentProfile: ", self.currentProfile)
        skillSections = ""
        for skillSection in skillsSortedData: # for skillSection in skillsData:
            sectionName = skillSection['name']
            if sectionName == "columnBreak":
                skillSections += f"\n\\columnbreak"
                continue
            
            # profileParams = skillSection['profile']
            # if self.currentProfile is not None and (profileParams['in'] is not None or profileParams['except'] is not None):
            #     if profileParams['except'] is not None and self.currentProfile in profileParams['except']:
            #         continue
            #     if profileParams['in'] is not None and self.currentProfile not in profileParams['in']:
            #         continue
            sectionItems = ""
            for item in skillSection['items']:
                itemName = item['name']
                itemLevel = item['level']
                itemDetails = item['details']
                sectionItems += f"\n\\includegraphics[scale=0.40]{{{itemLevel}stars.png}}\\hspace{{1.5mm}}\\textbf{{{itemName}}}"
                if itemDetails: sectionItems += itemDetails
            sectionStr = f"""
\\item \\large {sectionName} \\
\\normalsize
\\begin{{flushleft}}
{sectionItems}
\\end{{flushleft}}            
"""
            skillSections += sectionStr

        skills = f"""\\section{{{self.currentResumeData['document']['sections']['itSkills']['name']}}}
        \\vspace*{{-0.45cm}}
        \\setlength{{\\columnsep}}{{-0.3cm}}
        \\begin{{flushleft}}
        \\begin{{multicols}}{{3}}
		\\begin{{itemize}}
		
		\\setlength{{\\itemsep}}{{5pt}}
  		\\setlength{{\\parskip}}{{0pt}}
  		\\setlength{{\\parsep}}{{0pt}}
          
        {skillSections}

        \\end{{itemize}}
        \\end{{multicols}}
        %\\end{{itemize}}
        \\end{{flushleft}} \\normalsize
        \\vspace*{{-0.65cm}}"""
        return skills
    
    def getCurrentProfileSkillsData(self, skillSectionsData: list) -> list:
        skillSections = [section for section in skillSectionsData.copy() if section['name'] != "columnBreak"]
        skillSectionsIndexesToRemove = []
        for idx_skillSection, skillSection in enumerate(skillSections):
            profileParams = skillSection['profile']
            if self.currentProfile is not None and ((profileParams['in'] is not None) or (profileParams['except'] is not None)):
                if profileParams['except'] is not None and self.currentProfile in profileParams['except']:
                    print(f"Removing skillSection {skillSection['name']}: (except) {profileParams['except']}")
                    skillSectionsIndexesToRemove.append(idx_skillSection)
                if profileParams['in'] is not None and self.currentProfile not in profileParams['in']:
                    print(f"Removing skillSection {skillSection['name']}: (in) {profileParams['in']}")
                    skillSectionsIndexesToRemove.append(idx_skillSection)
        skillSectionsIndexesToRemove.sort(reverse=True)

        for idxToRemove in skillSectionsIndexesToRemove:
            skillSections.pop(idxToRemove)
        return skillSections
        

    def sortSkillSectionsInEqualColumns(self, skillSectionsData: list, columnsCount = 3, sectionColCharWidth = 22, textColCharWidth = 22, skillColCharWidth = 12, skillSmallColCharWidth = 14) -> list:
        #skillSections = skillSectionsData.copy().filter(lambda x: x['name'] != "columnBreak")
        skillSections = [section for section in skillSectionsData.copy() if section['name'] != "columnBreak"]
        skillSectionsTotalLength = 0
        for skillSection in skillSections:
            skillSectionLength = 0
            sectionTitleLength = math.ceil(len(self.getUnescapedString(skillSection['name'])) / sectionColCharWidth)
            skillSectionLength += sectionTitleLength

            for item in skillSection['items']:
                itemName = self.getUnescapedString(item['name'])
                small = itemName.startswith("small")
                if small:
                    itemName = itemName[5:]
                    skillNameLength = math.ceil(len(itemName) / skillSmallColCharWidth)
                else:
                    skillNameLength = math.ceil(len(itemName) / skillColCharWidth)
                skillSectionLength += skillNameLength

                itemDetails = self.getUnescapedString(item['details'])
                if itemDetails:
                    itemDetailsLength = math.ceil(len(itemDetails) / textColCharWidth)
                    skillSectionLength += itemDetailsLength
            
            skillSection['length'] = skillSectionLength
            skillSectionsTotalLength += skillSectionLength
        
        # Average length of each column
        averageLength = skillSectionsTotalLength / columnsCount
        skillSections.sort(key=lambda x: x['length'], reverse=True)

        # Distribute skill sections into columns
        skillColumns = [[] for _ in range(columnsCount)]
        skillsColumnsLengths = [0 for _ in range(columnsCount)]
        skillColumnsComposition = [[] for _ in range(columnsCount)]
        currentColumn = 0
        step = 1
        # print(f"skillSections: {skillSections}")
        for sectionIdx, skillSection in enumerate(skillSections):
            # skillColumns[currentColumn].append(skillSection)
            # currentColumn += step
            # if currentColumn > columnsCount -1 or currentColumn < 0:
            #     step *= -1
            #     currentColumn += step

            # print(f"skillSection {sectionIdx}/{len(skillSections)} {skillSection['name']} length: {skillSection['length']}")
            # print(f"Storing section in column {currentColumn}")
            skillColumns[currentColumn].append(skillSection)
            skillColumnsComposition[currentColumn].append(skillSection['name'])
            
            # print(f"New skillColumnsComposition: {skillColumnsComposition}")
            skillsColumnsLengths[currentColumn] += skillSection['length']
            # print(f"New skillColumnsLengths: {skillsColumnsLengths}")

            minColumnLength = min(skillsColumnsLengths)
            minColumnIndex = skillsColumnsLengths.index(minColumnLength)
            currentColumn = minColumnIndex
            # print(f"New currentColumn: {currentColumn}")

        # print(f"skillColumns: {skillColumns}")
        skillColumns.sort(key=lambda x: self.getSkillColumnLength(x), reverse=True)
        for i in range(columnsCount -1):
            skillColumns[i].append({"name": "columnBreak", "length": 0})
        # print(f"skillColumns (after sorting by desc length): {skillColumns}")

        skillSections = []
        for i in range(len(skillColumns)):
            skillSections = [*skillSections, *skillColumns[i]]

        return skillSections

    def getUnescapedString(self, string: str) -> str:
        # Remove LaTeX escape characters
        unescapedString = string.replace("\\", "").replace("{", "").replace("}", "")
        return unescapedString
    
    def getSkillColumnLength(self, skillColumn: list) -> int:
        skillColumnLength = 0
        for skillSection in skillColumn:
            skillColumnLength += skillSection['length']
        return skillColumnLength

    def buildExperience(self, detailed: bool) -> str:
        experienceData = self.currentResumeData['work']

        experiences = ""
        for expIdx, exp in enumerate(experienceData):
            profileParams = exp['profile']
            if self.currentProfile is not None and (profileParams['in'] is not None or profileParams['except'] is not None):
                if profileParams['except'] is not None and self.currentProfile in profileParams['except']:
                    continue
                if profileParams['in'] is not None and self.currentProfile not in profileParams['in']:
                    continue
            company = exp['company']
            position = exp['position']
            startDate = exp['startDate'].split("-")
            startDate = startDate[1] + "/" + startDate[0][2:]
            
            endDateFieldIsDate = len( re.findall(r"([0-9]{4}-(0[1-9]{1}|10|11|12)-([0-2]{1}[0-9]{1}|30|31))", exp['endDate']) ) > 0
            if endDateFieldIsDate:
                endDate = exp['endDate'].split("-")
                endDate = endDate[1] + "/" + endDate[0][2:]
            else:
                #Cas ou il n' y a pas de date de fin     
                endDate = exp['endDate']
            
            city = exp['location']['city']
            countryCode = exp['location']['countryCode']
            summary = exp['summary']

            expStr = f"""
\\begin{{entrylist}}
  \\entry
    {{{startDate} - {endDate}}}
    {{{position}}}
    {{{company}, \\textit{{{city}, {countryCode}}}}}
    {{{summary}}}
\\end{{entrylist}}
"""
            if not expIdx == 0 and not detailed:
                experiences += expStr
                continue
            details = exp['details']
            contextMission = details['context-mission']
            goals = details['goals']
            achievements = details['achievements']
            results = details['results']
            techEnv = details['tech-env']

            detailsStr = f"""\\vspace{{-15pt}}
"""

            achievementsStr = ""
            for idx_achievement, achievement in enumerate(achievements):
                achievementsStr += f"\n\\item {achievement}"
            if achievementsStr:
                achievementsStr = f"""\n\\vspace{{0.5mm}}
\\begin{{itemize}}
\\setlength{{\\itemsep}}{{1pt}}
\\setlength{{\\parskip}}{{0pt}}
\\setlength{{\\parsep}}{{0pt}}
{achievementsStr}
\\end{{itemize}}
"""
                detailsStr += achievementsStr


            expStr += detailsStr
            experiences += expStr

        experience = f"""\\section{{{self.currentResumeData['document']['sections']['workExperience']['name']}}}
\\vspace*{{-0.25cm}}
{experiences}
\\vspace*{{-0.5cm}}"""
        return experience
    
    def buildEducation(self) -> str:
        educationData = self.currentResumeData['education']
        educations = ""
        for edu in educationData:
            profileParams = edu['profile']
            if self.currentProfile is not None and (profileParams['in'] is not None or profileParams['except'] is not None):
                if profileParams['except'] is not None and self.currentProfile in profileParams['except']:
                    continue
                if profileParams['in'] is not None and self.currentProfile not in profileParams['in']:
                    continue
            institution = edu['institution']
            area = edu['area']
            startDate = edu['startDate'].split("-")
            startDate = startDate[1] + "/" + startDate[0][2:]
            endDate = edu['endDate'].split("-")
            endDate = endDate[1] + "/" + endDate[0][2:]
            #TODO: Prevoir le cas ou il n' y a pas de date de fin  
            city = edu['location']['city']
            countryCode = edu['location']['countryCode']
            studyType = edu['studyType']
            courses = edu['courses']
            coursesRaw = edu['coursesRaw']

            if studyType:
                eduStr = f"""\\vspace{{0.5mm}}
    \\begin{{entrylist}}
    \\entry
        {{{startDate} - {endDate}}}
        {{{area}}}
        {{{institution}, \\textit{{{city}, {countryCode}}}}}
        {{{studyType}}}
    \\end{{entrylist}}
    """
            else:
                eduStr = f"""\\vspace{{0.5mm}}
\\begin{{entrylist}}
\\entry
    {{{startDate} - {endDate}}}
    {{{area}}}
    {{{institution}, \\textit{{{city}, {countryCode}}}}}
    {{{studyType}}}
\\end{{entrylist}}
"""
            if coursesRaw:
                eduStr += coursesRaw
            if len(courses) != 0:
                coursesItemsStr = ""
                for item in courses:
                    coursesItemsStr += f"\n\\item {item}"
                coursesStr = f"""\n\\vspace*{{-0.35cm}}
\\begin{{itemize}}
\\setlength{{\\itemsep}}{{1pt}}
\\setlength{{\\parskip}}{{0pt}}
\\setlength{{\\parsep}}{{0pt}}
{coursesItemsStr}
\\end{{itemize}}"""
                eduStr += coursesStr
            educations += eduStr
        
        
        education = f"""\\vspace*{{0.45cm}}
\\section{{{self.currentResumeData['document']['sections']['education']['name']}}}
\\vspace*{{-0.25cm}}
{educations}"""
        return education
    

    def buildHobbies(self) -> str:
        hobbiesDataRaw = self.currentResumeData['interestsRaw']
        if(hobbiesDataRaw is not None):
            hobbies = f"""\\section{{{self.currentResumeData['document']['sections']['hobbies']['name']}}}
{hobbiesDataRaw}"""
            return "" #hobbies
        else:
            hobbiesData = self.currentResumeData['interests']
            return ""#hobbies


class ResumeLocation(Enum):
    PARIS = "Paris,France"
    LYON = "Lyon,France"

if __name__ == "__main__" :
    gen = ResumeGenerator(args).createResumes()


