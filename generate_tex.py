import os
import json
from definitions import ROOT_DIR
from datetime import datetime, timedelta
import time
from enum import Enum
import re
import math

import logging as logDal
logDal.basicConfig(filename=os.path.join(ROOT_DIR,"logs","resumeGenerator.log"), encoding='utf-8', filemode='w', format='%(asctime)s-%(levelname)s:%(message)s', level=logDal.DEBUG)

import argparse
import hashlib

parser = argparse.ArgumentParser(description="A resume generator script that takes some options to control the script output.")

# parser.add_argument("-o", "--output", help="Specify the output file")
parser.add_argument("-p", "--profile", help="Specify the resume profile: webDev, mobileDev, dataScientist, dataEngineer, devOps, ...")
# parser.add_argument("-h", "--help", action="help", help="Show help message and exit")

args = parser.parse_args()

# if args.output:
#     print("Arguments Passed with -o Option:-", args.output)
# if args.profile:
#     print("Arguments Passed with -o Option:-", args.output)
# else:
#     pass

class ResumeGenerator:
    def __init__(self, args) -> None:
        with open(os.path.join(ROOT_DIR,"res",f"doc_header.tex")) as f:
            self.docHeader = f.read()

        self.args = args
        self.today = datetime.now()
        self.targetDay = self.today
        self.year = str(self.targetDay.year)
        self.month = str(self.targetDay.month)
        self.day = "0" + str(self.targetDay.day) if len(str(self.targetDay.day)) < 2 else str(self.targetDay.day) #on ajoute 0 devant le jour s'il est compris entre 1 et 9
        self.currentProfile = self.getCurrentProfile()
    
    def getCurrentProfile(self) -> str|None:
        if self.args.profile:
            if self.args.profile in ["webDev", "mobileDev", "softDev", "devOps"]:
                return self.args.profile
            else:
                logDal.error(f"Profile {self.args.profile} not found")
                return "unknown"
        else:
            return None

    def createResumes(self):
        outputFilesDirPath = os.path.join(ROOT_DIR,"tex")
        if(self.currentProfile == "unknown"):
            errMsg = f"Profile {self.args.profile} not found"
            logDal.error(errMsg)
            print(errMsg)
            return
        
        # self.createdAt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # self.createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %z", time.localtime()) 
        # for filename in ["resume_FR", "resume_FR_detailed", "resume_CAN", "resume_CAN_detailed", "resume_CAN-QC", "resume_CAN-QC_detailed", "resume_AS_detailed"]:
        for filename in ["resume_FR", "resume_CAN", "resume_CAN-QC", "resume_AS"]:
            detailed = "detailed" in filename
            if self.currentProfile is not None:
                if not detailed:
                    filename += f"_{self.currentProfile}"
                else:
                    filename = filename.replace("_detailed", f"_{self.currentProfile}_detailed")
            outputFilePath = os.path.join(outputFilesDirPath,f"{filename}.tex")
            self.countryCode = filename.split("_")[1]
            self.dataRedirectCountryCode = None
            dataRedirectCountryCodes = {
                "US": ["CAN", "AS", "UK"],
                "FR": ["CAN-QC"],
            }
            for k, v in dataRedirectCountryCodes.items():
                if self.countryCode in v:
                    self.dataRedirectCountryCode = k
                    break
            self.loadResumeData(targetCountryCode=self.dataRedirectCountryCode if self.dataRedirectCountryCode else self.countryCode)
            outFileContent = self.buildResume(targetCountryCode=self.countryCode, detailed=detailed)
            # print(outFileContent)
            with open(outputFilePath, "w", encoding='utf-8') as f:
                f.write(outFileContent)

    def loadResumeData(self, targetCountryCode: str) -> None:
        resumeDataPath = os.path.join(ROOT_DIR,"res",f"resume_{targetCountryCode}.json")
        with open(resumeDataPath, "r", encoding='utf-8') as f:
            self.resumeData = json.loads(f.read())

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
        name = self.resumeData["basics"]["name"]
        print("self.dataRedirectCountryCode: ", self.dataRedirectCountryCode)
        docType = "Curriculum Vitae" if self.dataRedirectCountryCode == "FR" else "Resume"
        summary = self.resumeData["basics"]["summary"].replace("~", "").replace("/", "").replace("(", "").replace(")", "")
        keywords = [
            f"profile:{self.currentProfile}" if self.currentProfile else "profile:default",
            "resume", "developer", "software", "engineer", "C\# (.Net)", "Python", 
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
        name = self.resumeData["basics"]["name"].split(" ")
        assert len(name) > 1
        summary = self.resumeData["basics"]["summary"]
        if(self.currentProfile in self.resumeData["basics"]["profile"]):
            summary = self.resumeData["basics"]["profile"][self.currentProfile]["summary"]
        header = f"""
\\header{{{name[0]}}}{{{name[-1]}}}
      {{{summary}}}
      {{}}
"""
        return header
    
    def buildAsideInfos(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["infos"]["name"]
        sectionContent = self.resumeData["document"]["aside"]["sections"]["infos"]["content"]
        infos = f"""{sectionContent}"""
        return infos

    def buildAsideAddress(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["address"]["name"]
        location = self.resumeData["basics"]["location"]["Paris,France"]
        address = location["address"]
        postalCode = location["postalCode"]
        city = location["city"]
        countryCode = location["countryCode"]
        country = location["country"]
        region = location["region"]
        mobility = self.resumeData["document"]["aside"]["sections"]["address"]["mobility"]
        address = f"""{city}, {country}\\\\"""
        if mobility: address += f"\n\\vspace{{1.5mm}}\n{mobility}"

        return address
        

    def buildAsideContact(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["contact"]["name"]
        phone = self.resumeData["basics"]["phone"]
        mail = self.resumeData["basics"]["email"]
        contact = f"""{phone}\\\\
\\href{{mailto:{mail}}}{{\\small {mail}}}\\\\"""
        return contact

    def buildAsideOnlineProfiles(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["onlineProfiles"]["name"]
        
        profiles = f""
        profilesData = self.resumeData["basics"]["profiles"]
        for idx_profile, profile in enumerate(profilesData):
            network = profile["network"]
            url = profile["url"]
            line = f"" if idx_profile == 0 else f"\n"
            line += f"\\href{{{url}}}{{{network}\\hspace{{1.5mm}}\\includegraphics[scale=0.075]{{hlink.png}}}}\\\\"
            profiles += line
        return profiles

    def buildAsideLanguages(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["languages"]["name"]

        languages = f""
        languagesData = self.resumeData["languages"]
        for idx_language, language in enumerate(languagesData):
            lang = language["language"]
            level = language["fluency"]
            test = language["test"]
            line = f"" if idx_language == 0 else f"\n"
            line += f"\\makebox[4.3cm][l]{{\\textbf{{{lang}}} {test}}}\\\\"
            languages += line
        return languages

    def buildAsideSoftSkills(self, targetCountryCode: str) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["softSkills"]["name"]
        softSkills = f""
        if targetCountryCode in ["FR","CAN-QC"]:
            softSkills += f"\\includegraphics[scale=0.40]{{profileMap_FR.png}}"
        else:
            softSkills += f"\\includegraphics[scale=0.40]{{profileMap_EN.png}}"
        
        return softSkills

    def buildAsideOtherSections(self) -> str:
        #sectionName = self.resumeData["aside"]["sections"]["infos"]["name"]
        sections = ""
        sectionsData = self.resumeData["document"]["aside"]["otherSections"]
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
{address}\n\\vspace{{2.5mm}}
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
        if(self.currentProfile in self.resumeData["basics"]["profile"]):
            catchPhrase = self.resumeData["basics"]["profile"][self.currentProfile]["catchPhrase"]
        else:
            catchPhrase = self.resumeData["basics"]["catchPhrase"]
        
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
        skillsData = self.resumeData['skills']
        skillsCurrentProfileData = self.getCurrentProfileSkillsData(skillsData)
        skillsSortedData = self.sortSkillSectionsInEqualColumns(skillsCurrentProfileData)
        print("currentProfile: ", self.currentProfile)
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

        skills = f"""\\section{{{self.resumeData['document']['sections']['itSkills']['name']}}}
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
                    print(f"Removing skillSection {skillSection['name']}, reason: profileParams['except'] {profileParams['except']}")
                    skillSectionsIndexesToRemove.append(idx_skillSection)
                if profileParams['in'] is not None and self.currentProfile not in profileParams['in']:
                    print(f"Removing skillSection {skillSection['name']}, reason: profileParams['in'] {profileParams['in']}")
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
        print(f"skillSections: {skillSections}")
        for sectionIdx, skillSection in enumerate(skillSections):
            # skillColumns[currentColumn].append(skillSection)
            # currentColumn += step
            # if currentColumn > columnsCount -1 or currentColumn < 0:
            #     step *= -1
            #     currentColumn += step

            print(f"skillSection {sectionIdx}/{len(skillSections)} {skillSection['name']} length: {skillSection['length']}")
            print(f"Storing section in column {currentColumn}")
            skillColumns[currentColumn].append(skillSection)
            skillColumnsComposition[currentColumn].append(skillSection['name'])
            
            print(f"New skillColumnsComposition: {skillColumnsComposition}")
            skillsColumnsLengths[currentColumn] += skillSection['length']
            print(f"New skillColumnsLengths: {skillsColumnsLengths}")

            minColumnLength = min(skillsColumnsLengths)
            minColumnIndex = skillsColumnsLengths.index(minColumnLength)
            currentColumn = minColumnIndex
            print(f"New currentColumn: {currentColumn}")

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
        experienceData = self.resumeData['work']

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

        experience = f"""\\section{{{self.resumeData['document']['sections']['workExperience']['name']}}}
\\vspace*{{-0.25cm}}
{experiences}
\\vspace*{{-0.5cm}}"""
        return experience
    
    def buildEducation(self) -> str:
        educationData = self.resumeData['education']
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
\\section{{{self.resumeData['document']['sections']['education']['name']}}}
\\vspace*{{-0.25cm}}
{educations}"""
        return education
    

    def buildHobbies(self) -> str:
        hobbiesDataRaw = self.resumeData['interestsRaw']
        if(hobbiesDataRaw is not None):
            hobbies = f"""\\section{{{self.resumeData['document']['sections']['hobbies']['name']}}}
{hobbiesDataRaw}"""
            return "" #hobbies
        else:
            hobbiesData = self.resumeData['interests']
            return ""#hobbies

class ResumeLocation(Enum):
    PARIS = "Paris,France"
    LYON = "Lyon,France"

if __name__ == "__main__" :
    gen = ResumeGenerator(args).createResumes()
    # gen.createResumes()
