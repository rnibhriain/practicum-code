import requests
import json
import datetime
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time

# Risk Levels
# 0 - Not risky < 7 days
# 1 - Risky > 7 days
def predictRisk ( package ):
    
    # default is 0
    return 0

###############################################################################
# Vulnerability Prediction by Code Metrics                                    #
###############################################################################
def codePrediction ():
    


    return 0
###############################################################################

###############################################################################
# Vulnerability Prediction by Project Metrics                                 #
###############################################################################
def projectPrediction ():
    url = "https://api.github.com/repos/prestodb/presto/commits?per_page=100&page=1"

    token = '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'
    headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
    res = requests.get(url, headers=headers)
    print(f"Status code: {res.status_code}")
    print(res.reason)

    print(res.links['last']['url'])

    current = res.links['last']['url'].split("=")
    print(current[2])
    length = int(current[2])

    commits = []



    i = 1
    while ( i < length ):
        url = f"https://api.github.com/repos/apache/spark/commits?per_page=100&page={i}"
        token = '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'
        headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
        res = requests.get(url, headers=headers)

        if (res.status_code == 200):
                    commits.append(res)

        populateDates ( commits ) 
        
        i += 1

    commits_over_time()

    return 0

dates = []
counts = []
def populateDates ( commits ) :
    for x in commits:
        for i in x.json(): 
            date = i['commit']['author']['date'].replace("T", " ")
            date = date.replace("Z", "")
                
            date = date.split(" ")

            dates.append(date[0])

def commits_over_time () :
    finalDates = []
    currentDate = ''
    i = -1
    for x in dates: 
        if (currentDate == x ):
            
            counts[ i ] += 1
        else:
            finalDates.append(x)
            counts.append( 1 )
            currentDate = x
            i += 1

    print(len(finalDates))
    print(len(counts))

    df = pd.DataFrame({
        "Dates": finalDates,
        "Count": counts
    })

    df = df.drop_duplicates()

    figline = px.line(x=df.Dates, y=df.Count)

    fig = go.Figure(data=figline.data)

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title = f'Commits Over Time'
    )

    fig.show()

    return df
###############################################################################

###############################################################################
# Vulnerability Prediction by NVD Data                                        #
###############################################################################
def vulPrediction ():
    response = requests.get( "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=apache" )
    print( response.status_code )

    commits = []

    for i in response.json()['vulnerabilities']:
        commits.append( i['cve'] )

    populateDates( commits )
    vuls_over_time()

def populateDates ( commits ) :
    for x in commits:
        date = x[ 'published' ].replace("T", " ")
        date = date.replace("Z", "")
                
        date = date.split(" ")

        dates.append(date[0])

def vuls_over_time ():
    finalDates = []
    currentDate = ''
    i = -1
    for x in dates: 
        if (currentDate == x ):
            
            counts[ i ] += 1
        else:
            finalDates.append(x)
            counts.append( 1 )
            currentDate = x
            i += 1

    print(len(finalDates))
    print(len(counts))

    df = pd.DataFrame({
        "Dates": finalDates,
        "Count": counts
    })

    df = df.drop_duplicates()

    figline = px.line(x=df.Dates, y=df.Count)

    fig = go.Figure(data=figline.data)

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title = f'Vulnerabilities Over Time'
    )

    fig.show()

    return df

###############################################################################
    
 
def main():
    print( "Please enter a package you would like to use from our list of packages" )

    ######################################################
    # come up with set list of packages
    # for now lets focus on apache cus idk
    ######################################################
    
    vulPrediction ()

if __name__ == "__main__":
    main()