import requests
import json
import datetime

# Risk Levels
# 0 - Not risky < 7 days
# 1 - Risky > 7 days

def predictRisk ( package ):
    
    # default is 0
    return 0

class VulDates:
    def __init__( self, id, pub, mod ):
        self.id = id
        self.pub = pub
        self.mod = mod

def find_published_dates ( object ):
    dateobj = VulDates( object[ 'id' ], object[ 'published' ], object[ 'lastModified' ] )
    print( object[ 'id' ] )
    print( datetime.strptime( object[ 'published' ] ) )
    print( object[ 'lastModified' ] )
    return dateobj

def print_json ( object ):
    
    text = json.dumps( object, sort_keys = True, indent = 4 )
    print( text )
    
 
def main():
    print( "Please enter a package you would like to use from our list of packages" )

    ######################################################
    # come up with set list of packages
    # for now lets focus on apache cus idk
    ######################################################
    
    response = requests.get( "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=apache maven " )
    print( response.status_code )
    # print_json( response.json()['vulnerabilities'] )

    for i in response.json()['vulnerabilities']:
        find_published_dates( i['cve'] )
    # print_json( response.json()['vulnerabilities'][0]['cve']['published'] )
    # print_json( response.json()['vulnerabilities'][0]['cve']['descriptions'] )
    

if __name__ == "__main__":
    main()