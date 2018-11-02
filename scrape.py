from jobchecker import LazyJobChecker
from collections import namedtuple

def scrape():
    Company = namedtuple('Company', ['name', 'jobUrl', 'xpath'])

    companyList = []
    with open ('companies.txt', 'r') as f:
        for line in f:
            new = line.split(' ')
            if len(new) != 3:
                #raise some exception cause you messed up the txt doc
                pass
            new_company = Company(new[0], new[1], new[2] + '/text()')
            companyList.append(new_company)

    #test_companies = ['airbnb', 'test']
    #companyList = [company for company in companyList if company.name in test_companies]

    test = LazyJobChecker(companyList)
    test.checker()

    #test.testXPath()

#scrape()


