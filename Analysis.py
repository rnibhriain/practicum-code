import requests
import json

# Risk Levels
# 0 - Not risky < 7 days
# 1 - Risky > 7 days

def predictRisk ( package ):
    
    # default is 0
    return 0

def print_json ( object ):
    
    text = json.dumps( object, sort_keys = True, indent = 4 )
    print( text )

def main():
    print( "Please enter a package you would like to use from our list of packages" )
    ######################################################
    # come up with set list of packages
    ######################################################
    ##  
    response = requests.get( "https://services.nvd.nist.gov/rest/json/cves/2.0" )
    # print( response.json() )
    print_json( response.json()['description'] )

if __name__ == "__main__":
    main()