import requests
import json
import datetime
import requests
import datetime
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
    url = "https://api.github.com/repos/apache/spark/commits?per_page=100&page=1"

    headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'}
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
        url = "https://api.github.com/repos/apache/spark/commits?per_page=100&page={i}"
        time.sleep(2)
        headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'}
        res = requests.get(url, headers=headers)
        print(f"Status code: {res.status_code}")

        commits = []

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

    figline = px.line(df, x="Dates", y="Count")
    figline.update_traces(line=dict(color = 'white'))

    figscatt = px.scatter(df, x='Dates', y='Count', title='Commits Over Time', color = 'Count', size = 'Count' )

    figscatt.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )

    fig = go.Figure(data=figline.data + figscatt.data)

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title = f'Commits Over Time'
    )

    fig.show()

    return df

def display_productive_days ( commits) :
    days = []
    times = []
    for x in commits:
        for i in x.json(): 
            date = i['commit']['author']['date'].replace("T", " ")
            date = date.replace("Z", "")
            temp = pd.Timestamp(date)
            dt = temp.day_name() 

            days.append(dt)
        
            date = date.split(" ")
            temp = pd.Timestamp(date[1])
                
            hour = temp.hour
            times.append(hour)     
    
    count1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    counts = []
    for i in times:
        count1[i] = count1[i] + 1
    
    for i in times:
        counts.append(count1[i])
    df = pd.DataFrame({
        "Days": days,
        "Times": times,
        "Count": counts
    })

    fig = px.scatter(df, x="Days", y="Times", color='Count', size='Count')

    fig.update_xaxes(showgrid=False, categoryorder='array', categoryarray= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    fig.update_yaxes(showgrid=False, tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black',
        title = f'Commits Distribution Per Day'
    )

    fig.show()
###############################################################################

###############################################################################
# Vulnerability Prediction by NVD Data                                        #
###############################################################################
def vulPrediction ():
    response = requests.get( "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=apache maven " )
    print( response.status_code )
    # print_json( response.json()['vulnerabilities'] )

    for i in response.json()['vulnerabilities']:
        find_published_dates( i['cve'] )
    # print_json( response.json()['vulnerabilities'][0]['cve']['published'] )
    # print_json( response.json()['vulnerabilities'][0]['cve']['descriptions'] )

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

###############################################################################
    
 
def main():
    print( "Please enter a package you would like to use from our list of packages" )

    ######################################################
    # come up with set list of packages
    # for now lets focus on apache cus idk
    ######################################################
    
    projectPrediction ()

if __name__ == "__main__":
    main()