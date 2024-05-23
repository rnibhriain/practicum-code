import requests
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pmdarima.arima import *
from pmdarima import preprocessing
from scipy import stats
from scipy.stats import skew
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import *
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import networkx as nx
import subprocess
from pyvis.network import Network

###############################################################################
# SECTION 1: Algorithm to Find Dependencies                                    #
###############################################################################
dependencies = []
G = nx.Graph()
currentNode = str()
length = int()
currentNodes = dict()

riskScores = dict()

# using Maven dependency tree data (for now) extract and create a dependency graph
def findDependencies ():
    # plan for this is to use maven dependency trees
    # - so create a new maven project with some dependencies

    # this command gets the dependencies from a maven project
    # subprocess.run( [ "mvn", "dependency:tree", ">", "dependencies.txt" ], shell=True )

    f = open( "../Data/dependencies2.txt", "r" )

    global currentNode
    global length

    G.add_node( "PROJECT", color="black",  shape='square' )

    for i in f: 
        if "\\-" in i or "+-" in i: 
            
            library = extractLibrary( i )
            #hasLink = library in links
            print( library )
            dependencies.append( library )

            lib = i.strip( "[INFO] /")
            lib = lib.strip( "| ")
            lib = lib.strip( "\\- ")
            lib = lib.strip( "+- ")
            
            array = lib.split( ":" )

            lib = ""

            for i in range( len( array ) - 1 ):
                if i > 1: 
                    lib += "-" + array[ i ]
                elif i == 1:
                    lib += array[ i ]
                
            score = 0

            if lib in riskScores:
                score = riskScores[ lib ]

            else:
                score = predictRisk( lib, library )
                riskScores[ lib ] = score

            if score >= 0 and score < 2.5:
                G.add_node( lib, color='green' )
            elif score >= 2.5 and score < 5:
                G.add_node( lib, color='yellow' )
            elif score >= 5 and score < 7.5:
                G.add_node( lib, color='orange' )
            elif score >= 7.5 and score <= 10:
                G.add_node( lib, color='red' )
            else:
                G.add_node( lib, color='grey' )

            if length == 7:
                currentNodes.clear()
                G.add_edge( "PROJECT", lib )
                currentNodes[ length ] = lib
            else:
                if currentNodes.get( length ) == None:
                    currentNodes[ length ] = lib
                    G.add_edge( currentNodes.get( length - 3 ), lib, color='black' )
                else: 
                    G.add_edge( currentNodes.get( length - 3 ), lib, color='black' )
            

    net = Network( '1000px', '1000px' )
    net.from_nx( G )
    net.show( 'net.html', notebook=False )

    f.close()

    return 0

# still undecided as to best method for this - in terms of finding keywords
def extractLibrary ( dependency ):
    
    global length
    
    current = dependency.split( "\\" )
    if "\\-" in dependency:
        current = dependency.split( "\\-" )
    else:
        current = dependency.split( "+-" )

    length = len( current[ 0 ] )

    current = current[ 1 ].split( ":" )[ 1 ]

    return current
###############################################################################

gitScores = dict()
VulScores = dict()

def predictRisk ( lib, library ):
    
    # gitScore = projectPrediction( library )
    # vulScore = vulPrediction( lib )

    #return vulScore / gitScore
    return 0

###############################################################################
# SECTION 2: Vulnerability Prediction by Project Metrics                                 #
###############################################################################
links = dict()

# This function takes a text file of maven dependencies to their user/repo github links
def populateDependencyLinks ():
    f = open( "../Data/github_urls.txt", "r" )

    for i in f:
        data = i.split( "," )
        print( data )
        links[ data[ 0 ] ] = data[ 1 ]

    f.close()

gitURLScores = dict()

def projectPrediction ( repoUrl ):
    issues = []

    if repoUrl in gitURLScores:
        return gitURLScores[ repoUrl ]
    
    # Find Time to Close Issues
    url = "https://api.github.com/repos/{repoUrl}/issues?state=closed&per_page=100&page=1"

    token = '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'
    headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
    res = requests.get(url, headers=headers)

    current = res.links['last']['url'].split("=")
    length = int(current[3])

    i = 1
    while ( i < length ):
        url = f"https://api.github.com/repos/{repoUrl}/issues?state=closed&per_page=100&page={i}"
        token = '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'
        headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
        res = requests.get(url, headers=headers)

        if (res.status_code == 200):
                    issues.append(res)
        
        closedIssuesResolving( issues )
        
        i += 1

    issues_over_time()

    return 0

numDays = []

# Find the Time an Issue Has Been Open
def openIssuesResolving ( issues ):
    for x in issues:
        for i in x.json(): 
            date = i[ 'created_at' ]
            date = date.split( "T" )[ 0 ]
            dateobj = datetime.strptime( date, "%Y-%m-%d" )
            date1obj = datetime.today()

            date1 = date1obj.strftime( "%Y-%m-%d" )

            time = date1obj - dateobj
                
            dates.append( date1.split( '-' )[ 0 ] + '-' + date1.split( '-' )[ 1 ] )
            numDays.append( time.days )


# Find the Time It Took to Close an Issue
def closedIssuesResolving ( issues ):
    for x in issues:
        for i in x.json(): 
            date = i[ 'created_at' ]
            date1 = i[ 'closed_at' ]
            date = date.split( "T" )[ 0 ]
            date1 = date1.split( "T" )[ 0 ]
            dateobj = datetime.strptime( date, "%Y-%m-%d" )
            date1obj = datetime.strptime( date1, "%Y-%m-%d" )

            time = date1obj - dateobj
                

            dates.append( date1.split( '-' )[ 0 ] + '-' + date1.split( '-' )[ 1 ] )
            numDays.append( time.days )

nums = dict()
avg = dict()
dates = []

# Display the length of time to close issues/how long they are open
def issues_over_time () :

    # average length of time per month
    for i in range( len( dates ) ):
        if ( dates[ i ] not in nums ):
            nums[ dates[ i ] ] = 1 
            avg[ dates[ i ] ] = numDays[ i ]
        else:
            avg[ dates[ i ] ] += numDays[ i ]
            nums[ dates[ i ] ] += 1

    for x in nums.keys():
        avg[ x ] = avg[ x ] / nums[ x ]

    print( "check : ", avg.keys() )
    print( "check : ", avg.values() )
        

    df = pd.DataFrame({
        "Dates": avg.keys(),
        "Count": avg.values()
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

    fig = go.Figure(data=figline.data)

    fig.show()

    return df

###############################################################################



###############################################################################
# SECTION 3: Vulnerability Prediction by NVD Data                                        #
###############################################################################


# Predict Number of Vulnerabilities Per Month
def vulPrediction ( keywords ):
    
    commits = []
    
    # Search NVD API using the keywords from the dependencies
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=" + keywords
    response = requests.get( url )

    for i in response.json()['vulnerabilities']:
        commits.append( i['cve'] )

    popDates( commits )
    vuls_over_time()

    return 0


# Populate the Dates
def popDates ( commits ) :
    print( len(commits))
    for x in commits:
        date = x[ 'published' ]
                
        date = date.split("T")
        date = date[0].split("-")
        date = date[0] + '-' + date[1]
        dates.append(date)

counts = []

# Display Vulnerabilities Over Time
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

    df = pd.DataFrame({
        "Dates": finalDates,
        "Count": counts
    })

    print(df)
    df = df.drop_duplicates()

    f = plt.figure()
    ax1 = f.add_subplot(121)
    ax1.set_title('Actual Values')
    ax1.plot( df[ 'Dates' ], df[ 'Count' ] )

    ax2 = f.add_subplot(122)

    result = adfuller(df.Count.dropna())
    print('p-value ', result[1])

    result = adfuller(df.Count.diff().dropna())
    print('p-value ', result[1])

    result = adfuller(df.Count.diff().diff().dropna())
    print('p-value ', result[1] )

    # p = 1
    # d = 0
    # q = 1

    arima_model = ARIMA(df.Count, order=(1, 0, 1))
    model = arima_model.fit()
    print(model.summary())
    plot_predict(model, ax = ax2)
    plt.show()

    print(model.get_prediction())

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
    
    # SETUP
    populateDependencyLinks()

    findDependencies()
    

if __name__ == "__main__":
    main()