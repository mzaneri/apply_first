import sentry_sdk, sqlite3
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
                    self.conn.commit()
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

    def checker(self):        
        if len(self.companyList) > 0:
            self.checkDict = {company.name: [] for company in self.companyList}
            self.browser = webdriver.Chrome('/usr/bin/chromium-browser')
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
            else:
                print('no changes')
    
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