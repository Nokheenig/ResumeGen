import os
import json
from definitions import ROOT_DIR
from datetime import datetime, timedelta
import time
from enum import Enum

import logging as logDal
logDal.basicConfig(filename=os.path.join(ROOT_DIR,"logs","resumeGenerator.log"), encoding='utf-8', filemode='w', format='%(asctime)s-%(levelname)s:%(message)s', level=logDal.DEBUG)

class ResumeGenerator:
    def __init__(self) -> None:
        with open(os.path.join(ROOT_DIR,"res",f"doc_header.tex")) as f:
            self.docHeader = f.read()

        self.today = datetime.now()
        self.targetDay = self.today
        self.year = str(self.targetDay.year)
        self.month = str(self.targetDay.month)
        self.day = "0" + str(self.targetDay.day) if len(str(self.targetDay.day)) < 2 else str(self.targetDay.day) #on ajoute 0 devant le jour s'il est compris entre 1 et 9
    
    def createResumes(self):
        outputFilesDirPath = os.path.join(ROOT_DIR,"out")

        for filename in ["resume_FR.tex", "resume_FR_detailed.tex"]:#, "resume_CAN.tex", "resume_CAN_detailed.tex"]:
            outputFilePath = os.path.join(outputFilesDirPath,filename)
            detailed = "detailed" in filename
            countryCode = filename.split(".")[0].split("_")[1]
            self.loadResumeData(targetCountryCode=countryCode)
            outFileContent = self.buildResume(targetCountryCode=countryCode, detailed=detailed)
            print(outFileContent)
            with open(outputFilePath, "w", encoding='utf-8') as f:
                f.write(outFileContent)

    def loadResumeData(self, targetCountryCode: str) -> None:
        resumeDataPath = os.path.join(ROOT_DIR,"res",f"resume_{targetCountryCode}.json")
        with open(resumeDataPath, "r", encoding='utf-8') as f:
            self.resumeData = json.loads(f.read())

    def buildResume(self, targetCountryCode: str = "FR", detailed: bool = False) -> str:
        header = self.buildHeader()
        aside = self.buildAside(targetCountryCode=targetCountryCode)
        skills = self.buildSkills()
        experience = self.buildExperience(detailed=detailed)
        education = self.buildEducation()
        hobbies = self.buildHobbies()

        resume = f"""
{self.docHeader}
\\begin{{document}}
{header}
{aside}
{skills}
{experience}
{education}
{hobbies}
\\end{{document}} 
"""
        return resume
    
    def buildHeader(self) -> str:
        name = self.resumeData["basics"]["name"].split(" ")
        assert len(name) > 1
        summary = self.resumeData["basics"]["summary"]
        header = f"""
\\header{{{name[0]}}}{{{name[-1]}}}
      {{{summary}}}
      {{}}
"""
        return header
    
    def buildAsideInfos(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["infos"]["name"]
        sectionContent = self.resumeData["document"]["aside"]["sections"]["infos"]["content"]
        infos = f"""\\section{{{sectionName}}}
{sectionContent}"""
        return infos

    def buildAsideAddress(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["address"]["name"]
        location = self.resumeData["basics"]["location"]["Paris,France"]
        address = location["address"]
        postalCode = location["postalCode"]
        city = location["city"]
        countryCode = location["countryCode"]
        region = location["region"]
        mobility = self.resumeData["document"]["aside"]["sections"]["address"]["mobility"]
        address = f"""\\section{{{sectionName}}}
{address}
{postalCode} {city},
France"""
        if mobility: address += f"\n{mobility}"

        return address
        

    def buildAsideContact(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["contact"]["name"]
        phone = self.resumeData["basics"]["phone"]
        mail = self.resumeData["basics"]["email"].split("@")
        contact = f"""\\section{{{sectionName}}}
{phone}
\\href{{mailto:{mail[0]}@{mail[1]}}}{{\\textbf{{{mail[0]}@}}\\\\{mail[1]}}}"""
        return contact

    def buildAsideOnlineProfiles(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["onlineProfiles"]["name"]
        
        profiles = f"\\section{{{sectionName}}}"
        profilesData = self.resumeData["basics"]["profiles"]
        for profile in profilesData:
            network = profile["network"]
            url = profile["url"]
            line = f"\n\\href{{{url}}}{{{network}}}"
            profiles += line
        return profiles

    def buildAsideLanguages(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["languages"]["name"]

        languages = f"\\section{{{sectionName}}}"
        languagesData = self.resumeData["languages"]
        for language in languagesData:
            lang = language["language"]
            level = language["fluency"]
            test = language["test"]
            line = f"\n\\makebox[4.3cm][l]{{\\textbf{{{lang}}}\\includegraphics[scale=0.40]{{res/img/{level}stars.png}} {test}}}"
            languages += line
        return languages

    def buildAsideSoftSkills(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["softSkills"]["name"]
        softSkillsLines = ""
        softSkillsData = self.resumeData["document"]["aside"]["sections"]["softSkills"]["content"]
        for idx_skill, skill in enumerate(softSkillsData):
            line = "\n"
            skillParts = skill.split(" ")
            for idx, skillPart in enumerate(skillParts):
                partStr = f""
                if idx > 0: partStr += "\\\\"
                partStr += f"\\textbf{{{skillPart}}}"
                line += partStr
            if idx_skill != len(softSkillsData)-1: line += ","
            softSkillsLines += line
            
        softSkills = f"""\\section{{{sectionName}}}
\\smartdiagram[bubble diagram]{{
{softSkillsLines}
    }}"""
        return softSkills

    def buildAsideOtherSections(self) -> str:
        #sectionName = self.resumeData["aside"]["sections"]["infos"]["name"]
        sections = ""
        sectionsData = self.resumeData["document"]["aside"]["otherSections"]
        for section in sectionsData:
            sectionName = section["name"]
            sectionStr = f"\\section{{{sectionName}}}"
            match section["type"]:
                case "rankedItems":
                    for item in section['items']:
                        itemName = item['name']
                        level = item['level']
                        itemStr = f"\n\\textbf{{{itemName}}}\\includegraphics[scale=0.40]{{res/img/{level}stars.png}}"
                        sectionStr += itemStr
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
        softSkills = self.buildAsideSoftSkills()
        otherSections = self.buildAsideOtherSections()
        aside = f"\\begin{{aside}}"

        if targetCountryCode not in ["USA","CAN"]:
             aside += f"\n\\includegraphics[scale=0.28]{{res/img/Photo_CV.jpg}}"

        aside += f"""\n%\\begin{{flushleft}}
	\\emph{{Le {self.day}/{self.month}/{self.year}}} \\hspace*{{8mm}}
	%\\end{{flushleft}}
{infos}
{address}
{contact}
{onlineProfile}
{languages}
{softSkills}
{otherSections}
\\end{{aside}}"""
        return aside
    
    def buildSkills(self) -> str:
        skillsData = self.resumeData['skills']

        skillSections = ""
        for skillSection in skillsData:
            sectionName = skillSection['name']
            if sectionName == "columnBreak":
                skillSections += f"\n\\columnbreak"
                continue

            sectionItems = ""
            for item in skillSection['items']:
                itemName = item['name']
                itemLevel = item['level']
                itemDetails = item['details']
                sectionItems += f"\n\\textbf{{{itemName}}}\\includegraphics[scale=0.40]{{res/img/{itemLevel}stars.png}}"
                if itemDetails: sectionItems += itemDetails
            sectionStr = f"""
\\item {sectionName} \\
\\begin{{flushright}}
{sectionItems}
\\end{{flushright}}            
"""
            skillSections += sectionStr

        skills = f"""\\section{{{self.resumeData['document']['sections']['itSkills']['name']}}}
        \\vspace*{{-0.45cm}}
        \\setlength{{\\columnsep}}{{-0.3cm}}
        \\begin{{flushright}}
        \\begin{{multicols}}{{3}}
		\\begin{{itemize}}
		
		\\setlength{{\\itemsep}}{{1pt}}
  		\\setlength{{\\parskip}}{{0pt}}
  		\\setlength{{\\parsep}}{{0pt}}
          
        {skillSections}

        \\end{{itemize}}
        \\end{{multicols}}
        %\\end{{itemize}}
        \\end{{flushright}}
        \\vspace*{{-0.65cm}}"""
        return skills
    
    def buildExperience(self, detailed: bool) -> str:
        experienceData = self.resumeData['work']

        experiences = ""
        for exp in experienceData:
            company = exp['company']
            position = exp['position']
            startDate = exp['startDate'].split("-")
            startDate = startDate[1] + "/" + startDate[0][2:]
            endDate = exp['endDate'].split("-")
            endDate = endDate[1] + "/" + endDate[0][2:]
            #TODO: Prevoir le cas ou il n' y a pas de date de fin  
            city = exp['location']['city']
            countryCode = exp['location']['countryCode']
            summary = exp['summary']
            details = exp['details']


            expStr = f"""
\\begin{{entrylist}}
  \\entry
    {{{startDate} - {endDate}}}
    {{{position}}}
    {{{company}, \\textit{{{city}, {countryCode}}}}}
    {{{summary}}}
\\end{{entrylist}}
"""
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


            eduStr = f"""
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
        
        
        education = f"""\\section{{{self.resumeData['document']['sections']['education']['name']}}}
\\vspace*{{-0.25cm}}
{educations}"""
        return education
    

    def buildHobbies(self) -> str:
        hobbiesData = self.resumeData['interests'][0]
        raw = hobbiesData['raw']
        hobbies = f"""\\section{{{self.resumeData['document']['sections']['hobbies']['name']}}}
{raw}"""
        return hobbies

class ResumeLocation(Enum):
    PARIS = "Paris,France"
    LYON = "Lyon,France"

if __name__ == "__main__" :
    gen = ResumeGenerator()
    gen.createResumes()
