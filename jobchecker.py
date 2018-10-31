import sentry_sdk, sqlite3, requests
from sentry_sdk import capture_message
from lxml import html
from selenium import webdriver
from collections import namedtuple
'''
sentry_sdk.init(
    dsn="https://1b70f6cd397c4d5a8da2dba23481906f@sentry.io/1311619"
)
'''
class LazyJobChecker():
    '''
    The success rate of applying to jobs is much higher if you apply to them as soon as they are out.
    I'm don't want to check all of these companies on the regular, so this is a much better way.
    '''
    def __init__(self, companyList):
        self.companyList = companyList
        self.conn = sqlite3.connect('companies.db')
        self.cursor = self.conn.cursor()
        self.pastDict = {}
        self.addItems = {}
        self.removeItems = {}

    def getOld(self):
        #gets all exisiting jobs, adds them to a dict
        sql_statement = '''SELECT company, job FROM jobs'''
        self.cursor.execute(sql_statement)
        openings = self.cursor.fetchall()
        for opening in openings:
            if self.pastDict.get(opening[0]):
                self.pastDict[opening[0]].append(opening[1])
            else:
                self.pastDict[opening[0]] = [opening[1]]

    def changeEntries(self):
        if len(self.removeItems) != 0:
            delete_statement = '''DELETE FROM jobs WHERE (company = ? and job = ?)'''
            for company in list(self.removeItems.keys()):
                for job in self.removeItems[company]:
                    self.cursor.execute(delete_statement, (company, job))
        if len(self.addItems) != 0:
            add_statement = '''INSERT INTO jobs (company, job) VALUES (?, ?)'''
            for company in list(self.addItems.keys()):
                for job in self.addItems[company]:
                    self.cursor.execute(add_statement, (company, job))
        self.conn.commit()
        
    def updateCompanies(self, updateItems):
        for item in updateItems:
            toAdd = [x for x in self.checkDict[item] if x not in self.pastDict[item]]
            toRemove = [x for x in self.pastDict[item] if x not in self.checkDict[item]]
            self.addItems[item] = toAdd
            self.removeItems[item] = toRemove
        self.changeEntries()

    def findDiffs(self):
        #python surpisingly doesn't have a great way to manage differences between dicitionaries
        addItems = set(self.checkDict.keys()) - set(self.pastDict.keys())
        self.addItems = {companyName: self.checkDict[companyName] for companyName in addItems}
        removeItems = set(self.pastDict.keys()) - set(self.checkDict.keys())
        self.removeItems = {companyName: self.pastDict[companyName] for companyName in removeItems}
        updateItems =  set(self.pastDict.keys()) & (set(self.checkDict.keys()))
        self.updateCompanies(updateItems)

    def requester(self, company):
        htmlTree = html.fromstring(self.browser.page_source)
        self.openings = htmlTree.xpath(company.xpath)

    def databaseEdit(self):
        self.getOld()
        if len(self.pastDict) == 0:
            self.addItems = self.checkDict
            self.changeEntries()
        else:
            self.findDiffs()
            self.notify()

    def headEqual(self, name, url, size=None):
        r = requests.head(url)
        try:
            newSize = r.headers['Content-Length']
        except KeyError:
            print(f'{name} need to learn about the content-length header')
            return False
        if newSize == 0:
            return False
        if newSize == size:
            return True
        #true upsert is added in newest version fo sqlite 3, not on all systems    
        insertTable = ''' INSERT OR IGNORE INTO career_pages (company, size) VALUES (?, ?)'''
        self.cursor.execute(insertTable, (name, newSize))
        updateTable = '''UPDATE career_pages SET size = ? WHERE company = ?'''
        self.cursor.execute(updateTable, (newSize, name))
        return False

    def findUpdated(self):
        #checks to see if company is in db, if it is does a head request first to see if 'Content-Length' has changed
        new = []
        all_companies = '''SELECT size FROM career_pages WHERE company = ?'''
        for company in self.companyList:
            self.cursor.execute(all_companies, (company.name,))
            size = self.cursor.fetchone()
            if size:
                if not self.headEqual(company.name, company.jobUrl, size):
                    new.append(company)
            else:
                self.headEqual(company.name, company.jobUrl)
                new.append(company)
        self.companyList = new

    def checker(self):        
        self.findUpdated()
        if len(self.companyList) > 0:
            self.checkDict = {company.name: [] for company in self.companyList}
            self.browser = webdriver.Firefox()
            for company in self.companyList:
                self.browser.get(company.jobUrl)
                self.requester(company)
                if len(self.openings) == 0:
                    capture_message(f'Theres some problem from the {company.name} careers page')
                else:
                    self.openings = [opening.strip() for opening in self.openings if 'engineer' in opening.lower()]
                    self.checkDict[company.name].extend(self.openings)
            self.databaseEdit()
    
    def notify(self):
        if self.addItems:
            message = ''
            for k, v in list(self.addItems.items()):
                if len(v) > 0:
                    message += f'{k} has new openings for these jobs: {v}\n'
            if message:
                print(message)
    
    def testXPath(self):
        self.browser = webdriver.Firefox()
        for company in self.companyList:
            self.browser.get(company.jobUrl)
            self.requester(company)
            if len(self.openings) == 0:
                print(f'Theres some problem from the {company.name} careers page')
            else:
                results = [opening.strip() for opening in self.openings if 'engineer' in opening.lower()]
                print(results)



def create_db():
    conn = sqlite3.connect('companies.db')
    cursor = conn.cursor()
    create_jobs = '''CREATE TABLE jobs (
        ID INTEGER PRIMARY KEY NOT NULL, company TEXT NOT NULL, job TEXT NOT NULL
    )'''
    cursor.execute(create_jobs)
    create_career_pages = '''CREATE TABLE career_pages (
        ID INTEGER PRIMARY KEY NOT NULL, company TEXT UNIQUE NOT NULL, size INTEGER NOT NULL
    )'''
    cursor.execute(create_career_pages)

#create_db()

Company = namedtuple('Company', ['name', 'jobUrl', 'xpath'])

companyList = []

with open ('companies.txt', 'r') as f:
    for line in f:
        new = line.split(' ')
        if len(new) != 3:
            #raise some exception cause you messed up the txt doc
            pass
        new_company = Company(new[0], new[1], new[2])
        companyList.append(new_company)

#test_companies = ['airbnb', 'test']
#companyList = [company for company in companyList if company.name in test_companies]

test = LazyJobChecker(companyList)
test.checker()

#test.testXPath()