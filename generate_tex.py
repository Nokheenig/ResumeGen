from __future__ import annotations
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
from resumeMultilangGenerator.classes.latex_resume import LatexResumeBuilder, LatexDocumentBlock

# import logging as logDal
# logDal.basicConfig(filename=os.path.join(ROOT_DIR,"logs","resumeGenerator.log"), encoding='utf-8', filemode='w', format='%(asctime)s-%(levelname)s:%(message)s', level=logDal.DEBUG)

import argparse
import hashlib

class ResumeGenerator:
    class Resume:
        const = LatexResumeBuilder.const
        def __init__(self, resumeData: dict, profile: str, outputFile: Path):
            self.resumeData = resumeData
            self.data = resumeData["data"]
            self.document_data = resumeData["document"]
            self.translations = self.document_data["translations"]
            self.createdOn = datetime.now().strftime("%d/%m/%Y") 
            self.profile = profile
            self.outputFile = outputFile
            self.builder = LatexResumeBuilder()
            self.documentRoot = self.builder.document
            self.resumeId = self.getResumeId()
            self.selfRefQr = False

            
            pass
        def __repr__(self):
            return self.buildResume()
        
        def buildResume(self) -> str:
            return self.documentRoot.Build()
        
        def initialize(self):
            self.init_vars()
            self.init_base_document()
            self.init_build_header()
            self.init_build_aside()
            self.init_build_skills()
            self.init_build_experience()
            self.init_build_education()
            

        def init_vars(self):
            formats = self.document_data["formats"] if "formats" in self.document_data else {}
            self.format_date = formats["date"] if "date" in formats else "%m/%d/%Y"
            self.format_date_short = formats["date-short"] if "date-short" in formats else "%m/%y"
            pass

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
            basics = self.data["basics"]
            fname = basics["firstname"]
            lname = basics["lastname"]
            intro = basics["intro"]
            title = intro["title"]

            if header and fname and lname and title:
                header.body = rf"""\header{{{fname}}}{{{lname}}}
      {{{title}}}
      {{}}"""
            
            quote = self.document.createChild(id=self.const.section_quote)
            if quote:
                    # basics = self.data["basics"]
                    catchPhrase = intro["catchPhrase"]

                    quote.header = r"""\vspace*{-4.5mm}
\noindent\parbox{\linewidth}{
\vspace*{8.5mm}
\centering"""
                    quote.body = catchPhrase
                    quote.footer = "}"
            pass

        def init_build_aside(self):
            aside = self.document.createChild(id=self.const.section_aside)
            if aside:
                aside.header = r"""\begin{aside}
\vspace{30mm}"""
                aside.footer = r"""\end{aside}"""   
            
            self.init_build_aside_infos(aside)

            self.init_build_aside_contacts(aside)

            self.init_build_aside_links(aside)

            self.init_build_aside_languages(aside)

            self.init_build_aside_strengths(aside)

            self.init_build_aside_mechanical_skills(aside)

            self.init_build_aside_hobbies(aside)

            self.init_build_aside_dateid(aside)
            

        def init_build_aside_infos(self, inAsideBlock: LatexDocumentBlock):
            headers_trans = self.translations["headers"] if "headers" in self.translations else {}
            section_title = headers_trans["infos"] if "infos" in headers_trans else ""
            
            aside_infos = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_infos)

            if not aside_infos: return

            aside_infos.header = rf"""\section{{{section_title}}}\\"""
            basics = self.data["basics"]
            licence = basics["licence"]
            mobility = basics["mobility"]
            side_highlight = basics["side-highlight"]
            if licence:
                block = aside_infos.createChild()
                block.body = rf"""{licence}\\"""
                block.footer = r"""\vspace{3.5mm}"""
            if side_highlight:
                block = aside_infos.createChild()
                block.body = rf"""{side_highlight}\\"""
                block.footer = r"""\vspace{2.5mm}"""
            if mobility:
                block = aside_infos.createChild()
                block.body = rf"""{mobility}\\"""
                block.footer = r"""\vspace{2.5mm}"""

        def init_build_aside_contacts(self, inAsideBlock: LatexDocumentBlock):
            aside_contact = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_contact)
            if aside_contact:
                contacts = self.data["contacts"]
                email = contacts["email"]
                phone = contacts["phone"]
                online_profiles = contacts["online"]

                if phone and len(phone)>0:
                    block = aside_contact.createChild() 
                    block.body = rf"""{phone[0]}\\"""
                    block.footer = r"""\vspace{2.5mm}"""

                if email and len(email)>0:
                    block = aside_contact.createChild() 
                    block.body = rf"""\href{{mailto:{email}}}{{{email}}}\\"""
                    block.footer = r"""\vspace{2.5mm}"""
                

        def init_build_aside_links(self, inAsideBlock: LatexDocumentBlock):
            aside_links = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_links)
            if not aside_links: return
            
            aside_links.footer = r"""\vspace{1.0mm}"""

            contacts = self.data["contacts"]
            online_profiles = contacts["online"]

            if online_profiles and len(online_profiles)>0:
                for online_profile in online_profiles:
                    profile_name = online_profile["name"]
                    profile_type = online_profile["type"]
                    profile_alias = online_profile["alias"]
                    profile_url = online_profile["url"]
                    
                    block = aside_links.createChild() 
                    block.body = rf"""\href{{{profile_url}}}{{{profile_name}\hspace{{1.5mm}}\includegraphics[scale=0.075]{{hlink.png}}}}\\"""
                    block.footer = r"""\vspace{0.75mm}"""
            
            # Add QR code with the link to the resume in github pages
            if(self.selfRefQr):
                filename = f"{self.outputFile.stem}.png"
                filepath = QR_DIR / filename
                block = aside_links.createChild()
                block.body = rf"""\includegraphics[width=1.5cm,height=3cm,keepaspectratio]{{{filepath}}}"""
                block.footer = r"""\vspace{1.5mm}"""

        def init_build_aside_languages(self, inAsideBlock: LatexDocumentBlock):
            languages = self.data["languages"]
            if languages and len(languages)>0:
                aside_languages = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_languages)
                if aside_languages:
                    aside_languages.footer = r"""\vspace{2.5mm}%"""

                    for lang in languages:
                        language = lang["language"]
                        fluency = lang["fluency"]
                        test = lang["test"]

                        block = aside_languages.createChild() 
                        block.body = rf"""\makebox[4.3cm][l]{{\textbf{{{language}}} ({test})}}\\"""


        def init_build_aside_strengths(self, inAsideBlock: LatexDocumentBlock):
            soft_skills = self.data["skills"]["soft-skills"]
            strengths = soft_skills["strengths"] if "strengths" in soft_skills else []

            headers_trans = self.translations["headers"] if "headers" in self.translations else {}
            section_title = headers_trans["strengths"] if "strengths" in headers_trans else ""


            if strengths and len(strengths)>0:
                aside_strengths = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_strengths)
                if not aside_strengths: return

                aside_strengths.header = rf"""\section{{{section_title}}}"""

                aside_strengths_list = aside_strengths and aside_strengths.createChild(id=f"{aside_strengths.id}_list")
                if aside_strengths_list:
                    aside_strengths_list.header = r"""\begin{itemize}"""
                    aside_strengths_list.footer = r"""\end{itemize}"""

                    for strength in strengths:
                        strength_name = strength["name"]
                        strength_details = strength["details"]

                        block = aside_strengths_list.createChild()
                        block.body = rf"""\item {strength_name}"""


        def init_build_aside_mechanical_skills(self, inAsideBlock: LatexDocumentBlock):
            hard_skills = self.data["skills"]["hard-skills"]
            mechanical_skills = hard_skills["mechanical-skills"] if "mechanical-skills" in hard_skills else []
            headers_trans = self.translations["headers"]if "headers" in self.translations else {}

            title = headers_trans["mechanical-skills"] if "mechanical-skills" in headers_trans else ""

            if mechanical_skills and len(mechanical_skills)> 0:
                aside_mechanical_skills = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_mechanicalskills)
                if aside_mechanical_skills:
                    aside_mechanical_skills.header = rf"""\section{{{title}}}
    \begin{{itemize}}"""
                    aside_mechanical_skills.footer = r"""\end{itemize}"""

                    for skill in mechanical_skills:
                        name = skill["name"]
                        details = skill["details"]
                        if not name: continue

                        block = aside_mechanical_skills.createChild()
                        block.header = rf"""\item {name}"""
                        block.body = rf""" \\ \hspace*{{0.2em}}\small\textit{{{details}}}""" if details else ""


        def init_build_aside_hobbies(self, inAsideBlock: LatexDocumentBlock):
            interests = self.data["interests"] if "interests" in self.data else {}
            groups = interests["groups"] if "groups" in interests else []
            headers_trans = self.translations["headers"]if "headers" in self.translations else {}
            title = headers_trans["hobbies"] if "hobbies" in headers_trans else ""

            if not groups or len(groups) == 0: return

            aside_hobbies = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_hobbies)
            if not aside_hobbies: return

            aside_hobbies.header = rf"""\section{{{title}}}
\begin{{itemize}}"""
            aside_hobbies.footer = r"""\end{itemize}"""

            for hobby in groups:
                hobby_name = hobby["name"] if "name" in hobby else ""
                block = aside_hobbies.createChild()
                block.header = rf"""\item {hobby_name}"""

        def init_build_aside_dateid(self, inAsideBlock: LatexDocumentBlock):
            document_formats = self.document_data["formats"] if "formats" in self.document_data else {}
            date_format = document_formats["date"] if "date" in document_formats else "%d/%m/%Y"
            createdOn = datetime.now().strftime(date_format) # "%d/%m/%Y"
            resumeId = self.resumeId

            aside_dateid = inAsideBlock and inAsideBlock.createChild(id=self.const.section_aside_dateid)
            if not aside_dateid: return

            aside_dateid.header = rf"""\vspace{{2.5mm}}%\begin{{flushleft}}
\small \emph{{Auto-generated in \LaTeX}}\\"""
            aside_dateid.body = rf"""\small \emph{{Date: {createdOn}}} \hspace*{{8mm}}\\
\small \emph{{Id: {resumeId}}}"""

        def init_build_skills(self):
            skills_data = self.data["skills"] if "skills" in self.data else {}
            hard_skills = skills_data["hard-skills"] if "hard-skills" in skills_data else {}
            it_skills = hard_skills["it-skills"] if "it-skills" in hard_skills else {}
            groups = it_skills["groups"] if "groups" in it_skills else []
            columns = it_skills["columns"] if "columns" in it_skills else 2

            if not groups or len(groups) == 0: return

            skills = self.document.createChild(id=self.const.section_skills)
            if not skills: return

            headers_trans = self.translations["headers"] if "headers" in self.translations else {}
            section_title = headers_trans["skills-it"] if "skills-it" in headers_trans else ""

            skills.header = rf"""\vspace*{{0.8mm}}
\section{{{section_title}}}
\vspace*{{-0.45cm}}
\setlength{{\columnsep}}{{-0.3cm}}
\begin{{flushleft}}
\begin{{multicols}}{{{columns}}}
\begin{{itemize}}
\setlength{{\itemsep}}{{5pt}}
\setlength{{\parskip}}{{0pt}}
\setlength{{\parsep}}{{0pt}}"""
            skills.footer = r"""\end{itemize}
\end{multicols}
%\end{itemize}
\end{flushleft} \normalsize
\vspace*{-2.0mm}"""
            groupOrder = {"columns": {
                0: []
            }}

            for skill_section in groups:
                section_name = skill_section["name"] if "name" in skill_section else ""
                section_items = skill_section["items"] if "items" in skill_section else []
                section_column = skill_section["column"] if "column" in skill_section else 0
                section_position = skill_section["position"] if "position" in skill_section else 0

                if not section_name or not section_items or len(section_items) == 0: continue

                skills_group = skills and skills.createChild(id=section_name)
                if not skills_group: continue

                if section_column not in groupOrder["columns"]: 
                    groupOrder["columns"][section_column]=[]

                groupOrder["columns"][section_column].append([section_position, skills_group])

                skills_group.header = rf"""\item \large {section_name} \
\normalsize
\begin{{flushleft}}"""
                skills_group.footer = r"""\end{flushleft}   """

                for item in section_items:
                    item_name = item["name"] if "name" in item else ""
                    item_level = item["level"] if "level" in item else None
                    item_details = item["details"] if "details" in item else None

                    if not item_name or not item_level: continue

                    skills_group_item = skills_group.createChild(id=item_name)
                    skills_group_item.body = rf"""\includegraphics[scale=0.40]{{{item_level}stars.png}}\hspace{{1.5mm}}\textbf{{{item_name}}}"""
                    if item_details: skills_group_item.body += rf"""{item_details}\vspace{{2mm}}"""

            
            for col in groupOrder["columns"].values():
                col.sort(key=lambda group_pos_block: group_pos_block[0])

            new_children = { }
            column_count = len(groupOrder["columns"])
            for column_index in range(column_count):
                column_elements_list = groupOrder["columns"][column_index]

                for el in column_elements_list:
                    element: LatexDocumentBlock = el[1]
                    new_children[element.id] = element

                if column_index != column_count - 1:
                    col_break = skills.createChild(id=f"column_break_{column_index}")
                    col_break.body = r"\columnbreak"
                    new_children[col_break.id] = col_break

            skills.children = new_children

        def init_build_experience(self):
            experience_items = self.data["experience"] if "experience" in self.data else []

            headers_trans = self.translations["headers"]if "headers" in self.translations else {}
            title = headers_trans["experience"] if "experience" in headers_trans else ""

            if not experience_items or len(experience_items) == 0 or not title: return
            
            experience = self.document.createChild(id=self.const.section_experience)
            if not experience: return
            
            experience.header = rf"""\section{{{title}}}
\vspace*{{-0.25cm}}"""

            for exp in experience_items:
                date_from = exp["date-from"] if "date-from" in exp else ""
                if date_from:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d')
                    date_from = date_from.strftime(self.format_date_short)
                
                date_to = exp["date-to"] if "date-to" in exp else ""
                if not date_to:
                    date_to = datetime.now().strftime("%Y-%m-%d") 
                if date_to:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d')
                    date_to = date_to.strftime(self.format_date_short)
                
                company = exp["company"] if "company" in exp else ""
                position = exp["position"] if "position" in exp else ""
                summary = exp["summary"] if "summary" in exp else ""

                location = exp["location"] if "location" in exp else {}
                city = location["city"] if "city" in location else ""
                country = location["country"] if "country" in location else ""
                countryCode = location["countryCode"] if "countryCode" in location else ""
                zipCode = location["zipCode"] if "zipCode" in location else ""

                if not date_from or not company or not position or not summary or not city or not countryCode: continue

                exp_item = experience.createChild()
                if not exp_item: continue

                exp_item.body = rf"""\begin{{entrylist}}
    \entry
    {{{date_from} - {date_to}}}
    {{{position}}}
    {{{company}, \textit{{{city}, {countryCode}}}}}
    {{{summary}}}
\end{{entrylist}}"""
                
                context_mission = exp["context-mission"] if "context-mission" in exp else ""
                goals = exp["goals"] if "goals" in exp else []
                achievements = exp["achievements"] if "achievements" in exp else []
                results = exp["results"] if "results" in exp else []
                tech_env = exp["tech-env"] if "tech-env" in exp else []
                detailed = context_mission or goals or achievements or results or tech_env

                if not detailed: continue

                exp_item_details = exp_item.createChild()
                # TODO Continue from here
                
                if achievements and len(achievements)>0:
                    list_block = exp_item_details.createChild()
                    list_block.header = r"""\vspace{-15pt}
    \vspace{0.5mm}
    \begin{itemize}
        \setlength{\itemsep}{1pt}
        \setlength{\parskip}{0pt}
        \setlength{\parsep}{0pt}"""
                    list_block.footer = r"""\end{itemize}"""

                    for achievement in achievements:
                        block = list_block.createChild()
                        self.init_build_experience_process_achievement(achievement=achievement, block=block)
                        # block.body = rf"\item {achievement}"

        def init_build_experience_process_achievement(self, achievement: str, block: LatexDocumentBlock) -> tuple[str,list]:
            # item_desc, subitems = self.init_build_experience_process_achievement_preprocess(achievement)
            block.body = rf"\item {achievement}"
            pass

        # def init_build_experience_process_achievement_preprocess(self, achievement: str) -> tuple[str,list]:
        #     if achievement.find("|") == -1: return (achievement, None)
        #     splitmark_found = True
        #     level = 1
        #     item_mark = "|" * level + "-"
        #     subitems = achievement.split(item_mark)
        #     while splitmark_found:
        #         level += 1
        #         item_mark = "|" * level + "-"
        #         for item in subitems:
        #             # if isinstance(item, str): continue
        #             if item.find(item_mark) == -1: continue
        #             subit = item.split(item_mark)




        #     re.compile(r"")
        #     pass

        # def split_str(self, inString: str, inSplitLevel: int) -> tuple[str,list]|list[tuple[str,list]]:
        #     split_string = "|" * inSplitLevel + "-"
        #     prefix = ""
        #     if inString.find(split_string) == -1: return (inString, [])

        #     esc_split_string = split_string.replace("|", r"\\|")
        #     pattern = re.compile(r"(?P<er>^.*?)")



        #     subStrings = inString.split(split_string)
        #     if len(subStrings) == 1: return (inString, [])
        #     result = []
        #     for it in subStrings:

        #     pass

        
        def init_build_education(self):
            education_items = self.data["education"] if "education" in self.data else []

            headers_trans = self.translations["headers"]if "headers" in self.translations else {}
            title = headers_trans["education"] if "education" in headers_trans else ""

            education = self.document.createChild(id=self.const.section_education)
            if not education or len(education_items) == 0: return
            
            education.header = r"""\vspace*{-0.5cm}
    \vspace*{0.45cm}
    \section{Education - Certifications}
    \vspace*{-0.25cm}
    \vspace{0.5mm}"""

            for education_entry in education_items:
                institution = education_entry["institution"] if "institution" in education_entry else ""
                area = education_entry["area"] if "area" in education_entry else ""
                subarea = education_entry["subarea"] if "subarea" in education_entry else ""
                
                date_from = education_entry["date-from"] if "date-from" in education_entry else ""
                if date_from:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d')
                    date_from = date_from.strftime(self.format_date_short)
                
                date_to = education_entry["date-to"] if "date-to" in education_entry else ""
                if not date_to:
                    date_to = datetime.now().strftime("%Y-%m-%d") 
                if date_to:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d')
                    date_to = date_to.strftime(self.format_date_short)

                location = education_entry["location"] if "location" in education_entry else {}
                city = location["city"] if "city" in location else ""
                country = location["country"] if "country" in location else ""
                countryCode = location["countryCode"] if "countryCode" in location else ""
                zipCode = location["zipCode"] if "zipCode" in location else ""
                detailsBlock = education_entry["detailsBlock"] if "detailsBlock" in education_entry else ""

                if not date_from or not area or not institution or not city or not countryCode: continue

                education_item = education.createChild()
                education_item.body = rf"""\begin{{entrylist}}
    \entry
    {{{date_from} - {date_to}}}
    {{{area}}}
    {{{institution}, \textit{{{city}, {countryCode}}}}}
    {{{subarea}}}
\end{{entrylist}}
\vspace{{0.5mm}}"""

        def getResumeId(self) -> str:
            resumeId = "default"
            if self.profile is not None:
                resumeId = self.profile
            resumeId += f"_{self.createdOn}"
            resumeId = hashlib.shake_256(resumeId.encode()).hexdigest(3)
            return resumeId
        
    def __init__(self, args) -> None:
        self.args = args

        self.validatedInputFilesPathList = self.getValidatedInputFiles()
        self.options = []
        if self.args.nofiltering is not None and self.args.nofiltering:
            self.isDetailedResume = True
            self.options.append("detailed")

        if self.args.selfrefqr is not None and self.args.selfrefqr:
            self.options.append("selfRefQr")


    def generateResumes(self):
        # Load all unfiltered data files from leaf to root (no parent data source)
        self.rawDataDictionariesByFile = self.getRawDataDictionariesByFile()

        # get a list of all profiles in loaded data files
        self.availableProfilesByResume = self.getAvailableProfilesByResume()

        # get resume generating session profiles list
        self.sessionProfileListByResume = self.getSessionProfileListByResume()

        unconsolidatedResumeDataByFileByProfile = self.getResumeDataStackByFileByProfile()

        resumeDataByFileByProfile = self.getResumeDataByFileByProfile(unconsolidatedResumeDataByFileByProfile)

        resumeByFileByProfile = self.getResumeByFileByProfile(resumeDataByFileByProfile)

        self.writeResumes(resumeByFileByProfile)
    
    def writeResumes(self, inResumeByFileByProfile: dict[Path,dict[str,ResumeGenerator.Resume]]):
        for file, resumeByProfile in inResumeByFileByProfile.items():
            for profile, resume in resumeByProfile.items():
                self.writeResume(resume)

    def writeResume(self, inResume: ResumeGenerator.Resume):
        with open(inResume.outputFile, "w", encoding='utf-8') as f:
            f.write(inResume.buildResume())

    def getResumeByFileByProfile(self, inResumeDataByFileByProfile: dict[Path,dict[str,dict]] ) -> dict[Path,dict[str,ResumeGenerator.Resume]]:
        output: dict[Path,dict[str,ResumeGenerator.Resume]] = {}
        for file, resumeDataByProfile in inResumeDataByFileByProfile.items():
            output[file] = {}
            for profile, resumeData in resumeDataByProfile.items():
                filename = file.stem
                extension = file.suffix
                profileTag = f"_{profile}" if profile not in ["default"] else ""

                filename = f"{filename}{profileTag}.tex"
                outputFile = OUTPUT_DIR / filename

                resume = self.Resume(resumeData=resumeData, profile=profile, outputFile=outputFile)
                resume.selfRefQr = "selfRefQr" in self.options
                resume.initialize()
                output[file][profile] = resume
        return output

    def getResumeDataByFileByProfile(self, inResumeDataStackByFileByProfile: dict[Path,dict[str,list[dict]]]) -> dict[Path,dict[str,dict]]:
        output: dict[Path,dict[str,dict]] = {}
        
        for file, resumeDataStackByProfile in inResumeDataStackByFileByProfile.items():
            output[file] = {}
            for profile, resumeDataStack in resumeDataStackByProfile.items():
                resumeData = {}
                for dataShard in resumeDataStack:
                    resumeData = deep_extend_dict(base=resumeData, extension=dataShard)

                output[file][profile] = resumeData
        return output
    
    def getAvailableProfilesByResume(self) -> dict[Path,set[str]]:
        output: dict[Path,set[str]] = {}
        for file in self.validatedInputFilesPathList:
            output[file] = set()
            output[file].add("default")

            fileBranchLoaded = False
            currentFile = file
            loopIdx = 0
            while not fileBranchLoaded:
                loopIdx +=1
                if loopIdx %100 == 0:
                    print(f"getAvailableProfilesByResume >> while loop idx: '{loopIdx}'")
                fileContents = self.rawDataDictionariesByFile[currentFile]
                fileSectionData = fileContents["file"] if "file" in fileContents else {}
                parentFileName = fileSectionData["parent"] if "parent" in fileSectionData else ""
                fileProfiles = fileSectionData["profiles"] if "profiles" in fileSectionData else []
                if fileProfiles:
                    for profile in fileProfiles:
                        output[file].add(profile)

                if parentFileName:
                    parentPath = Path(os.path.join(currentFile.parent, parentFileName))
                    currentFile = parentPath
                else:
                    fileBranchLoaded = True

        return output

    def getResumeDataStackByFileByProfile(self) -> dict[Path,dict[str,list[dict]]]:
        outData: dict[Path,dict[str,list[dict]]] = {}

        for file in self.validatedInputFilesPathList:
            if file not in outData: 
                outData[file] = {}
            for profile in self.sessionProfileListByResume[file]:

                outResumeProfileDataStack = []

                fileBranchLoaded = False
                currentFile = file
                loopIdx = 0
                while not fileBranchLoaded:
                    loopIdx +=1
                    if loopIdx %100 == 0:
                        print(f"getResumeDataStackByFileByProfile >> while loop idx: '{loopIdx}'")
                    rawData = copy.deepcopy(self.rawDataDictionariesByFile[currentFile])
                    profileFilteredData = self.deepFilterProfileDict(inDict=rawData, inProfile=profile, isFilter="unfiltered" in profile)
                    outResumeProfileDataStack.append(profileFilteredData)

                    fileSectionData = profileFilteredData["file"] if "file" in profileFilteredData else {}
                    parentFileName = fileSectionData["parent"] if "parent" in fileSectionData else ""

                    if parentFileName:
                        parentPath = Path(os.path.join(currentFile.parent, parentFileName))
                        currentFile = parentPath
                    else:
                        fileBranchLoaded = True
                
                outData[file][profile] = outResumeProfileDataStack
            
        return outData
                    
    def deepFilterProfileDict(self, inDict: dict, inProfile: str, isFilter = True) -> dict:
        """
        Filter input dictionary with inProfile
        """

        # Apply overrides before proceeding to dive into the dictionary
        if "$overrides" in inDict:
            inDict = self.getProfileOverridenDictionary(inDict=inDict, inProfile=inProfile)
            if not inDict:
                # inDict = {}
                return {}

        inDictKeysToRemove = []
        for key, val in inDict.items():
            if key == "$overrides": continue # not look for overrides inside an override

            # if key->value is dictionary recursively call function to filter deeper dictionary
            if isinstance(val, dict): 
                item: dict = val
                item = self.deepFilterProfileDict(inDict=item, inProfile=inProfile, isFilter=isFilter)
                
                if not item:
                    inDictKeysToRemove.append(key)
                else:
                    inDict[key] = item

                continue

            # if key is list of dict: loop on items to filter and keep or remove them based on profile
            if isinstance(val, list) and val and isinstance(val[0], dict):
                inListIndexesToRemove = []
                for itemIdx in range(len(val)-1, -1, -1):
                    item: dict = val[itemIdx]
                    item = self.deepFilterProfileDict(inDict=item, inProfile=inProfile, isFilter=isFilter)

                    if not item:
                        inListIndexesToRemove.append(itemIdx)
                    else:
                        val[itemIdx] = item

                for idxToRemove in inListIndexesToRemove:
                    val.pop(idxToRemove)
                
                if len(val) == 0: # Mark to remove filtered list which don't contain any element anymore from
                    inDictKeysToRemove.append(key)

                continue
        
        for key in inDictKeysToRemove:
            inDict.pop(key)

        return inDict

    def getProfileOverridenDictionary(self, inDict: dict, inProfile: str) -> dict:
        overrides = inDict["$overrides"][0]
        if not self.isDictionaryProfileOverriden(inOverridesDict=overrides, inProfile=inProfile):
            return inDict
        inDict.pop("$overrides")
        return deep_merge_dict(base=inDict, override=overrides["data"]) #TODO see later to allow additional overrides profiles

    def isDictionaryProfileOverriden(self, inOverridesDict: dict, inProfile: str) -> bool:
        withConditions = inOverridesDict["with"]
        exceptConditions = inOverridesDict["except"]
        optionPattern = re.compile(r"option:(?P<option>\w+)")
        profilePattern = re.compile(r"profile:(?P<profile>[a-zA-Z0-9-*_]+)") # TODO fix later for _-*

        isWithConditionsTriggered = False
        if len(withConditions) == 0: 
            isWithConditionsTriggered = True
        for condition in withConditions:
            if condition == "*" or isWithConditionsTriggered:
                isWithConditionsTriggered = True
                break
            m = optionPattern.search(condition)
            if m:
                option = m.group("option")
                if option in self.options:
                    isWithConditionsTriggered = True
                    break
            m = profilePattern.search(condition)
            if m:
                profile = m.group("profile")
                if not "*" in profile:
                    if profile == inProfile:
                        isWithConditionsTriggered = True
                        break
                    else:
                        continue
                profile = profile.replace("*", r"[a-zA-Z0-9_-]*?")
                pattern = re.compile(profile)
                profileLikePatternMatch = pattern.search(inProfile)
                if profileLikePatternMatch:
                    isWithConditionsTriggered = True
                    break
                else:
                    continue

        isExceptConditionsTriggered = False
        if len(exceptConditions) == 0:
            isExceptConditionsTriggered = False
        for condition in exceptConditions:
            if condition == "*" or isExceptConditionsTriggered:
                isExceptConditionsTriggered = True
                break
            m = optionPattern.search(condition)
            if m:
                option = m.group("option")
                if option in self.options:
                    isExceptConditionsTriggered = True
                    break
            m = profilePattern.search(condition)
            if m:
                profile = m.group("profile")
                if not "*" in profile:
                    if profile == inProfile:
                        isExceptConditionsTriggered = True
                        break
                    else:
                        continue
                profile = profile.replace("*", r"[a-zA-Z0-9_-]*?")
                pattern = re.compile(profile)
                profileLikePatternMatch = pattern.search(inProfile)
                if profileLikePatternMatch:
                    isExceptConditionsTriggered = True
                    break
                else:
                    continue

        return isWithConditionsTriggered and not isExceptConditionsTriggered

    def getResumeParentData(self, inDict: dict, inProfile: str) -> dict|None:
        if not self.resumeHasParentData(inDict):
            return None
        parentFile = inDict["file"]["parent"]
        return self.unconsolidatedResumeDataByFileByProfile[parentFile][inProfile] # TODO must harden, what if key doesn t exist ?

    def resumeHasParentData(self, inDict: dict) -> bool:
        return "file" in inDict and "parent" in inDict["file"] and inDict["file"]["parent"]

    def getSessionProfileListByResume(self) -> dict[Path,list[str]]:
        output: dict[Path,list[str]] = {}
        for file in self.availableProfilesByResume:
            argsProfilesList = self.args.profiles
            requestedResumesProfiles = argsProfilesList if argsProfilesList else ["default"]
            fileAvailableProfiles = self.availableProfilesByResume[file]
            fileSessionProfiles = fileAvailableProfiles if "all" in requestedResumesProfiles else [profile for profile in fileAvailableProfiles if profile in requestedResumesProfiles]
            output[file] = fileSessionProfiles

        return output

    def getRawDataDictionariesByFile(self) -> dict[Path,dict]:
        output: dict[Path,dict] = {}
        for file in self.validatedInputFilesPathList:
            fileBranchLoaded = False
            currentFile: Path = file
            loopIdx = 0
            while not fileBranchLoaded:
                loopIdx +=1
                if loopIdx %100 == 0:
                    print(f"getRawDataDictionariesByFile >> while loop idx: '{loopIdx}'")
                if currentFile in output:
                    # parents and deeper parents have already been loaded
                    fileBranchLoaded = True
                    continue
                else:
                    with open(currentFile, "r", encoding='utf-8') as f:
                        fileContents = json.loads(f.read())
                        output[currentFile] = fileContents
                        if "file" in fileContents and "parent" in fileContents["file"]:
                            parentFileName = fileContents["file"]["parent"]
                            if parentFileName:
                                parentPath = Path(os.path.join(currentFile.parent, parentFileName))
                                currentFile = parentPath
                                # continue
                            else:
                                fileBranchLoaded = True
                                continue
                        else:
                            fileBranchLoaded = True
                            continue
        
        return output

    def getValidatedInputFiles(self) -> list[Path]:
        if self.args.files is None or len(self.args.files) < 1:
            print(f"No target json resume in input !\nAdd -f and specify the target resumes to generate tex resumes\nCancelling job...")
            exit()

        # Check files are resume json
        inputFiles: list[Path] = []
        discardedFiles = []
        jsonResumeValidator = re.compile("resume_[A-Z0-9_-]+\\.json")

        for file in self.args.files:
            filepath = Path(os.path.join(ROOT_DIR, file))
            filename = filepath.name
            
            if jsonResumeValidator.match(filename):
                inputFiles.append(filepath)
            else:
                discardedFiles.append(filepath)

        if len(discardedFiles) > 0:
            print(f"{len(discardedFiles)} input target resumes aren't valid input json resume files!" ,discardedFiles)
        
        return inputFiles


#     def buildMetadata(self) -> str:
#         name = self.currentResumeData["basics"]["name"]

#         docType = "Curriculum Vitae" if self.countryCode == "FR" else "Resume"
#         summary = self.currentResumeData["basics"]["summary"].replace("~", "").replace("/", "").replace("(", "").replace(")", "")
#         keywords = [
#             f"profile:{self.currentProfile}" if self.currentProfile else "profile:default",
#             "resume", "developer", "software", "engineer", "C\\# (.Net)", "Python", 
#             "Javascript", "Node.js", "Java", "Kotlin", "Android", "Rest API", 
#             "Git / GitLab", "Docker", "Jenkins", "Selenium", "Cron", "Html-Css", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase", "Bash", "Jira", "Regex",
#             f"createdAt:{self.createdAt}", f"id:{self.resumeId}"
#         ]
#         formattedKeywords = "; ".join(keywords).replace("/", "").replace("(", "").replace(")", "")
#         metadata = f"""
# \\title{{{name} -- Resume}}
# \\author{{{name}}}
# \\date{{{self.day}/{self.month}/{self.year}}}

# \\hypersetup{{
#   pdftitle={{{name} -- Resume}},
#   pdfauthor={{{name}}},
#   pdfsubject={{{summary} - {docType}}},
#   pdfkeywords={{{formattedKeywords}}},
#   pdfcreator={{LuaLaTeX}},
#   pdfproducer={{LuaLaTeX}}
# }}
# """
#         return metadata

        

    # def sortSkillSectionsInEqualColumns(self, skillSectionsData: list, columnsCount = 3, sectionColCharWidth = 22, textColCharWidth = 22, skillColCharWidth = 12, skillSmallColCharWidth = 14) -> list:
    #     skillSections = [section for section in skillSectionsData.copy() if section['name'] != "columnBreak"]
    #     skillSectionsTotalLength = 0
    #     for skillSection in skillSections:
    #         skillSectionLength = 0
    #         sectionTitleLength = math.ceil(len(self.getUnescapedString(skillSection['name'])) / sectionColCharWidth)
    #         skillSectionLength += sectionTitleLength

    #         for item in skillSection['items']:
    #             itemName = self.getUnescapedString(item['name'])
    #             small = itemName.startswith("small")
    #             if small:
    #                 itemName = itemName[5:]
    #                 skillNameLength = math.ceil(len(itemName) / skillSmallColCharWidth)
    #             else:
    #                 skillNameLength = math.ceil(len(itemName) / skillColCharWidth)
    #             skillSectionLength += skillNameLength

    #             itemDetails = self.getUnescapedString(item['details'])
    #             if itemDetails:
    #                 itemDetailsLength = math.ceil(len(itemDetails) / textColCharWidth)
    #                 skillSectionLength += itemDetailsLength
            
    #         skillSection['length'] = skillSectionLength
    #         skillSectionsTotalLength += skillSectionLength
        
    #     # Average length of each column
    #     averageLength = skillSectionsTotalLength / columnsCount
    #     skillSections.sort(key=lambda x: x['length'], reverse=True)

    #     # Distribute skill sections into columns
    #     skillColumns = [[] for _ in range(columnsCount)]
    #     skillsColumnsLengths = [0 for _ in range(columnsCount)]
    #     skillColumnsComposition = [[] for _ in range(columnsCount)]
    #     currentColumn = 0
    #     step = 1

    #     for sectionIdx, skillSection in enumerate(skillSections):
    #         skillColumns[currentColumn].append(skillSection)
    #         skillColumnsComposition[currentColumn].append(skillSection['name'])
            
    #         skillsColumnsLengths[currentColumn] += skillSection['length']

    #         minColumnLength = min(skillsColumnsLengths)
    #         minColumnIndex = skillsColumnsLengths.index(minColumnLength)
    #         currentColumn = minColumnIndex

    #     skillColumns.sort(key=lambda x: self.getSkillColumnLength(x), reverse=True)
    #     for i in range(columnsCount -1):
    #         skillColumns[i].append({"name": "columnBreak", "length": 0})

    #     skillSections = []
    #     for i in range(len(skillColumns)):
    #         skillSections = [*skillSections, *skillColumns[i]]

    #     return skillSections

    # def getUnescapedString(self, string: str) -> str:
    #     # Remove LaTeX escape characters
    #     unescapedString = string.replace("\\", "").replace("{", "").replace("}", "")
    #     return unescapedString
    
    # def getSkillColumnLength(self, skillColumn: list) -> int:
    #     skillColumnLength = 0
    #     for skillSection in skillColumn:
    #         skillColumnLength += skillSection['length']
    #     return skillColumnLength






def find_root(marker="Makefile"):
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"Could not find project root (looking for {marker})")

def main(args):
    generator = ResumeGenerator(args=args)
    generator.generateResumes()

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(...)
    # parser.add_argument(...)
    # args = parser.parse_args()

    parser = argparse.ArgumentParser(description="A resume generator script that takes some options to control the script output.")

    parser.add_argument("-p", "--profiles", help="Specify the resume profiles to generate: webDev, mobileDev, dataScientist, dataEngineer, devOps, ...",
        nargs="+",  # allows multiple values
        required=False
                        )
    parser.add_argument("-n", "--nofiltering", help="Override the filtering of resume data and generate with the maximum of data available.", action='store_true')

    parser.add_argument("-q", "--selfrefqr", help="add a qr code in resume to open itself in pdf", action='store_true')
    # parser.add_argument("-h", "--help", action="help", help="Show help message and exit")
    parser.add_argument("-f", "--files", help="Specify the desired resumes (source data files, optionally with profiles) to generate.",
        nargs="+",  # allows multiple values
        required=True
                        )
    parser.add_argument("-o", "--outputdir")

    args = parser.parse_args()

    ROOT_DIR = find_root()

    ARTIFACTS_DIR = ROOT_DIR / "artifacts"
    TEX_DIR = ARTIFACTS_DIR / "tex"
    QR_DIR = ARTIFACTS_DIR / "qr"
    
    OUTPUT_DIR = TEX_DIR
    if args.outputdir:
        OUTPUT_DIR = Path(args.outputdir)

    main(args)

