import os
import json
from definitions import ROOT_DIR
from datetime import datetime, timedelta
import time
from enum import Enum
import re

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

        for filename in ["resume_FR.tex", "resume_FR_detailed.tex", "resume_CAN.tex", "resume_CAN_detailed.tex", "resume_CAN-QC.tex", "resume_CAN-QC_detailed.tex", "resume_AS_detailed.tex"]:
            outputFilePath = os.path.join(outputFilesDirPath,filename)
            detailed = "detailed" in filename
            countryCode = filename.split(".")[0].split("_")[1]
            dataRedirectCountryCode = None
            dataRedirectCountryCodes = {
                "US": ["CAN", "AS", "UK"],
                "FR": ["CAN-QC"],
            }
            for k, v in dataRedirectCountryCodes.items():
                if countryCode in v:
                    dataRedirectCountryCode = k
                    break
            self.loadResumeData(targetCountryCode=dataRedirectCountryCode if dataRedirectCountryCode else countryCode)
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
        catchPhrase = self.buildCatchPhrase()
        skills = self.buildSkills()
        experience = self.buildExperience(detailed=detailed)
        education = self.buildEducation()
        hobbies = self.buildHobbies()

        resume = f"""
{self.docHeader}
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
        infos = f"""{sectionContent}"""
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
        address = f"""{city}, France"""
        if mobility: address += f"\\vspace{{1.5mm}}\n{mobility}"

        return address
        

    def buildAsideContact(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["contact"]["name"]
        phone = self.resumeData["basics"]["phone"]
        mail = self.resumeData["basics"]["email"]
        contact = f"""{phone}
\\href{{mailto:{mail}}}{{\\small {mail}}}"""
        return contact

    def buildAsideOnlineProfiles(self) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["onlineProfiles"]["name"]
        
        profiles = f""
        profilesData = self.resumeData["basics"]["profiles"]
        for idx_profile, profile in enumerate(profilesData):
            network = profile["network"]
            url = profile["url"]
            line = f"" if idx_profile == 0 else f"\n"
            line += f"\\href{{{url}}}{{{network}\\hspace{{1.5mm}}\\includegraphics[scale=0.075]{{res/img/hlink.png}}}}"
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
            line += f"\\makebox[4.3cm][l]{{\\textbf{{{lang}}} {test}}}"
            languages += line
        return languages

    def buildAsideSoftSkills(self, targetCountryCode: str) -> str:
        sectionName = self.resumeData["document"]["aside"]["sections"]["softSkills"]["name"]
        softSkills = f""
        if targetCountryCode in ["FR","CAN-QC"]:
            softSkills += f"\\includegraphics[scale=0.40]{{res/img/profileMap_FR.png}}"
        else:
            softSkills += f"\\includegraphics[scale=0.40]{{res/img/profileMap_EN.png}}"
        
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
                        itemStr = f"\n\\includegraphics[scale=0.40]{{res/img/{level}stars.png}}\\hspace{{1.5mm}}\\textbf{{{itemName}}}"
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
        softSkills = self.buildAsideSoftSkills(targetCountryCode=targetCountryCode)
        otherSections = self.buildAsideOtherSections()
        aside = f"\\begin{{aside}}"

        if targetCountryCode not in ["USA","CAN","CAN-QC", "UK"]:
             aside += f"\n\\hspace{{10mm}}\\includegraphics[scale=0.148]{{res/img/Photo_CV.jpg}}"
        else:
            aside += f"\n\\vspace{{21mm}}"

        aside += f"""\\section{{Infos}}
{infos}\\vspace{{2.5mm}}
{address}\\vspace{{2.5mm}}
{contact}\\vspace{{2.5mm}}
{onlineProfile}\\vspace{{2.5mm}}
{languages}\\vspace{{2.5mm}}
{softSkills}\\vspace{{2.5mm}}
{otherSections}\n\\vspace{{2.5mm}}%\\begin{{flushleft}}
	\\emph{{Le {self.day}/{self.month}/{self.year}}} \\hspace*{{8mm}}
	%\\end{{flushleft}}
\\end{{aside}}"""
        return aside
    
    def buildCatchPhrase(self) -> str:
        catchPhrase = self.resumeData["basics"]["catchPhrase"]
        
        catchPhraseOut = f"""
\\vspace{{-3mm}}
\\begin{{minipage}}[t]{{1.00\\linewidth}}
{catchPhrase}
\\end{{minipage}} % no space if you would like to put them side by side
\\vspace{{1mm}}
"""
        return catchPhraseOut

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
                sectionItems += f"\n\\includegraphics[scale=0.40]{{res/img/{itemLevel}stars.png}}\\hspace{{1.5mm}}\\textbf{{{itemName}}}"
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
    
    def buildExperience(self, detailed: bool) -> str:
        experienceData = self.resumeData['work']

        experiences = ""
        for exp in experienceData:
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
            if not detailed:
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
        hobbiesData = self.resumeData['interests'][0]
        raw = hobbiesData['raw']
        hobbies = f"""\\section{{{self.resumeData['document']['sections']['hobbies']['name']}}}
{raw}"""
        return ""#hobbies

class ResumeLocation(Enum):
    PARIS = "Paris,France"
    LYON = "Lyon,France"

if __name__ == "__main__" :
    gen = ResumeGenerator()
    gen.createResumes()
