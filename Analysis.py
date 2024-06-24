import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pmdarima.arima import *
from pmdarima.arima import auto_arima
from scipy.stats import skew
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import *
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import networkx as nx
import subprocess
from pyvis.network import Network
import json
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

##############################################################################
# CONFIG OBJECT And SetUp                                                    #
##############################################################################

# Object to store current configuration jobs
class config:

    def __init__( self, num_vuls, 
                 num_days_to_fix, 
                 num_commits, 
                  issues_or_commits,
                   token,
                    nvd_key ):
        self.num_vuls = num_vuls
        self.num_days_to_fix = num_days_to_fix
        self.num_commits = num_commits
        self.issues_or_commits = issues_or_commits
        self.token = token
        self.nvd_key = nvd_key

# Setup the configuration object using configuration JSON
def configuration ():
    
    f = open( "Data/config.JSON" )
    data = json.load( f )

    global currentConfig
    
    currentConfig = config( data[ 'num_vuls' ], 
                           data[ 'num_days_to_fix' ], 
                            data[ 'num_commits' ], 
                            data[ 'issues_or_commits' ],
                            data[ 'token' ],
                             data[ 'nvd_key' ] )
    
    if int( data[ 'num_commits' ] ) == 0:
        print( "Error: num_commits cannot be 0" )
        quit()

    f.close()

###############################################################################

###############################################################################
# SECTION 1: Algorithm to Find Dependencies                                   #
###############################################################################
G = nx.Graph()
length = int()
currentNodes = dict()
currentConfig = None
riskScores = dict()

# using Maven dependency tree data extract and create a dependency graph
def findDependencies ():

    # this command gets the dependencies from a maven project
    # subprocess.run( [ "mvn", "dependency:tree", ">", "dependencies.txt" ], shell=True )

    f = open( "Data/dependencies4.txt", "r" )

    # add central node for the project
    G.add_node( "PROJECT", color = "black",  shape = 'square' )

    for i in f: 
        if "\\-" in i or "+-" in i: 
            
            library = extractLibrary( i )

            # remove any unnecessary characters before analysis
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

            # If the dependency has already been analysed then use that score
            if lib in riskScores:
                score = riskScores[ lib ]
            else:
                score = predictRisk( lib, library )
                riskScores[ lib ] = score

            # picking colour for the current nodes - based on the risk
            if score < 0:
                G.add_node( lib, color ='grey' )
            elif score >= 0 and score < 2.5:
                G.add_node( lib, color ='green' )
            elif score >= 2.5 and score < 5:
                G.add_node( lib, color ='yellow' )
            elif score >= 5 and score < 7.5:
                G.add_node( lib, color ='orange' )
            elif score >= 7.5:
                G.add_node( lib, color ='red' )
            else:
                G.add_node( lib, color ='grey' )
 
            # this is one of the immediate nodes to the project itself
            if length == 7:
                currentNodes.clear()
                G.add_edge( "PROJECT", lib )
                currentNodes[ length ] = lib

            # else find the distance from the project
            else:
                if currentNodes.get( length ) == None:
                    currentNodes[ length ] = lib
                    G.add_edge( currentNodes.get( length - 3 ), lib, color ='black' )
                else: 
                    G.add_edge( currentNodes.get( length - 3 ), lib, color ='black' )
            

    # Set up the dependency tree diagram
    net = Network( '1000px', '2000px', heading = 'Dependency Tree of Risks' )
    net.from_nx( G )

    net.show( 'net.html', notebook = False )

    h = open( 'net.html', 'w' )

    # Fix double heading issue
    html_str = net.html.replace( '<center>\n<h1>Dependency Tree of Risks</h1>\n</center>', '' )
    
    # Add a key in for risk score diagram
    html_str = html_str.replace( '<body>', '<body>\n<center>\n<label"><b>Key:</b></label>\n<div style="width: 150px; height: 320px; border: 0.5px solid black">\n<p style="display: inline-block;">Severe Risk<div style="width: 10px; height: 10px; background-color: red;"></div></p>\n<p>High Risk<div style="width: 10px; height: 10px; background-color: orange;"></div></p>\n<p>Medium Risk<div style="width: 10px; height: 10px; background-color: yellow;"></div></p>\n<p>Low Risk<div style="width: 10px; height: 10px; background-color: green;"></div></p>\n<p>Not Enough Data<div style="width: 10px; height: 10px; background-color: gray;"></div></p>\n</div>\n</center>\n' )

    h.write( html_str )

    h.close()

    f.close()

    return 0

# extracts library for GitHub project activity prediction
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

# project activity scores
gitURLScores = dict()

# vulnerability data scores
vulScores = dict()

# this function returns the combined score of the project activity and vulnerabilities
def predictRisk ( lib, library ):
    
    vulScore = 0
    gitScore = 0

    # if the dependency does not have a corresponding link
    if library not in links: 
        gitScore = -1

    # if the project has not been analysed already then analyse
    if links[ library ] not in gitURLScores:
        gitURLScores[ links[ library ] ] = gatherData( links[ library ] )
    gitScore = gitURLScores[ links[ library ] ]

    # if the dependency has not been analysed already then analyse
    if lib not in vulScores:
        vulScores[ lib ] = vulPrediction( lib )
    vulScore = vulScores[ lib ]

    # Print the results
    print( "*************** RISK SCORE ANALYSIS FOR: ", lib, "***************" )
    print( "\n" )
    print( "* Project score: ", gitScore )
    print( "\n" )
    print( "* Vulnerability score: ", vulScore )
    print( "\n" )

    # Combine the Scores
    return ( vulScore + gitScore ) / 2

###############################################################################
# SECTION 2: Vulnerability Prediction by Project Metrics                      #
###############################################################################

# links for each of the projects using extracted data from dependencies
links = dict()

# This function takes a text file of maven dependencies to their user/repo github links
def populateDependencyLinks ():
    f = open( "Data/github_urls.txt", "r" )

    for i in f:
        data = i.split( "," )
        data[ 1 ] = data[ 1 ].replace( "\n", "" )
        links[ data[ 0 ] ] = data[ 1 ]

    f.close()

issueNumDaysToFix = []
issuesClosedPerMonth = dict()
issueAvgDaysToFix = dict()
issueCloseDates = []

commitDates = []
commitCounts = dict()

# Gather Data for Both Time to Close Issues and Commits Per Month
def gatherData ( repoUrl ):
    issues = []
    commits = []
    
    issueNumDaysToFix.clear()
    issueAvgDaysToFix.clear()
    issuesClosedPerMonth.clear()
    issueCloseDates.clear()

    commitDates.clear()
    commitCounts.clear()

    if repoUrl in gitURLScores:
        return gitURLScores[ repoUrl ]
    
    # Find Time to Close Issues
    url = f"https://api.github.com/repos/{repoUrl}/issues?state=closed&per_page=100&page=1"

    token = currentConfig.token
    headers = { "Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
    res = requests.get( url, headers = headers )

    if res.status_code == 404:
        return -1
    
    length = 1

    # find necessary pagination/if there is no data
    if ( len( res.json() ) == 0 ):
        return -1
    elif ( len( res.json() ) < 100 ):
        length = 1
    else: 
        current = res.links[ 'last' ][ 'url' ].split( "=" )
        length = int( current[ 3 ] )

    i = 1

    while ( i <= length ):
        url = f"https://api.github.com/repos/{repoUrl}/issues?state=closed&per_page=100&page={i}"
        headers = { "Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
        res = requests.get( url, headers = headers )

        if ( res.status_code == 200 ):
                    issues.append( res )
        
        # find and store issue close dates
        closedIssuesResolving( issues )
        
        i += 1

    # Find Commits for projects
    url = f"https://api.github.com/repos/{repoUrl}/commits?per_page=100&page=1"

    headers = { "Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
    res = requests.get( url, headers = headers )

    if res.status_code == 404:
        return -1
    
    length = 1

    # find necessary pagination/if there is no data
    if ( len( res.json() ) == 0 ):
        return -1
    elif ( len( res.json() ) < 100 ):
        length = 1
    else: 
        current = res.links[ 'last' ][ 'url' ].split( "=" )
        length = int( current[ 2 ] )

    i = 1
    while ( i <= length ):
        url = f"https://api.github.com/repos/{repoUrl}/commits?per_page=100&page={i}"
        headers = { "Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
        res = requests.get( url, headers = headers )

        if ( res.status_code == 200 ):
                    commits.append( res )
        
        # find and store commit dates
        populateDates( commits )
        
        i += 1

    # Return scores according to configuration options (accounts for if there is not enough data for either issues or commits)
    if currentConfig.issues_or_commits == 'both':
        
        issues_prediction = float( projectPrediction( issues_over_time(), repoUrl, 'Issues' )  / int( currentConfig.num_days_to_fix ) ) * 10
        commits_prediction = projectPrediction( commits_over_time(), repoUrl, 'Commits' )
        if commits_prediction == 0:
            commits_prediction = float( int( currentConfig.num_days_to_fix ) / 1 ) * 10
        else:
            commits_prediction = float( int( currentConfig.num_days_to_fix ) / commits_prediction ) * 10 

        if commits_prediction == -1 and issues_prediction == -1:
            return -1
            
        elif commits_prediction == -1:
            return issues_prediction / 2
            
        elif issues_prediction == -1:
            return commits_prediction / 2
        
    elif currentConfig.issues_or_commits == 'issues':
        issues_prediction = projectPrediction( issues_over_time(), repoUrl, 'Issues' )

        if issues_prediction != -1:
            return float( issues_prediction / int( currentConfig.num_days_to_fix ) ) * 10
        
        return issues_prediction
    
    elif currentConfig.issues_or_commits == 'commits':
        commits_prediction = projectPrediction( commits_over_time(), repoUrl, 'Commits' )
        if commits_prediction == 0:
            return float( int( currentConfig.num_days_to_fix ) / 1 ) * 10
        elif commits_prediction != -1:
            return float( int( currentConfig.num_days_to_fix ) / commits_prediction ) * 10
        
        return commits_prediction

    # Error with configuration
    print( "Configuration for project analysis can be: 'both', 'issues' or 'commits'")
    return -1

# Populate monthly dates for commit data gathered
def populateDates ( commits ) :
    for x in commits:
        for i in x.json(): 
            date = i[ 'commit' ][ 'author' ][ 'date' ].replace( "T", " " )
                
            date = date.split( " " ) 

            commitDates.append( date[ 0 ].split( '-' )[ 0 ] + '-' + date[ 0 ].split( '-' )[ 1 ] )

# Place commit data over time in a DataFrame
def commits_over_time () :
    i = 0

    for x in commitDates: 
        if x in commitCounts :
            commitCounts[ x ] += 1
        else:
            commitCounts[ x ] = 1
            i += 1

    df = pd.DataFrame({
        "Dates": commitCounts.keys(),
        "Actual": commitCounts.values()
    })

    df = df.drop_duplicates() 

    df.sort_values( by = 'Dates', ascending = True, inplace = True )

    idx = pd.date_range( df.Dates.min(), datetime.today(), freq = 'MS' )

    df.set_index( df.Dates )

    # Ensure it is monthly data in the index
    for i in idx:
        current  = pd.to_datetime( i )
        current = current.strftime( format = "%Y-%m" )
        if current not in df[ 'Dates' ].unique():
            df = pd.concat( [ pd.DataFrame( [ [ current, 0 ] ], columns = df.columns ), df ], ignore_index = True )

    df.sort_values( by = 'Dates', ascending = True, inplace = True )

    return df

# Use ARIMA to predict gathered data - either issues or commits
def projectPrediction ( df, repo, type ):

    df.index = pd.DatetimeIndex( df.Dates ).to_period( 'M' )

    # ensure that the values are not constant
    if len( df[ 'Actual' ].unique() ) == 1:
        return -1

    # Automatic Prediction
    autoparameters = auto_arima( y = df[ 'Actual' ], seasonal = False )

    # Place predicted values in a dataframe
    df2 = pd.DataFrame({
       "Dates": autoparameters.fittedvalues().axes[ 0 ].strftime( "%Y-%m" ),
       "Prediction": autoparameters.fittedvalues()
    })

    # Concatenate the data 
    df = pd.concat( [ df, df2 ] )

    # Graph predicted vs actual values
    fig = px.line( data_frame= df, x = 'Dates', y = [ 'Actual', 'Prediction' ],  color_discrete_map={
                 "Actual": "#42DB04",
                "Prediction": "#F66491"
             } )
    
    fig.update_traces( line = dict( width = 3 ) )
    
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title = f'{type} Over Time for : {repo}'
    )
    
    fig.show()

    # not enough data
    if len( set( autoparameters.fittedvalues().values ) ) == 1:
        return -1  
    
    df = df.replace( np.nan, 0 )

    # EVALUATION SECTION
    df[ 'forecast_error' ] = df[ 'Actual' ] - df[ 'Prediction' ]

    # Calculate the absolute percentage errors
    df[ 'absolute_percentage_error' ] = ( df[ 'forecast_error' ].abs() / df[ 'Actual' ].replace( 0, 1 ) ) * 100

    # Calculate the MAPE
    mape = df[ 'absolute_percentage_error' ].mean() 

    mae = mean_absolute_error( df[ 'Actual' ], df[ 'Prediction' ] )

    rmse = mean_squared_error( df[ 'Actual' ], df[ 'Prediction' ], squared = False )

    print( "*******************************************************************************" )
    print( "* Evaluation Metrics for ", type, " Prediction for ", repo, ":" )
    print( "\n" )
    print( "* MAPE:", mape )
    print( "\n" )
    print( "* MAE:", mae )
    print( "\n" )
    print( "* RMSE:", rmse )
    print( "*******************************************************************************\n" )

    # if the prediction is below 0 then return 0
    if autoparameters.fittedvalues().values[ len( autoparameters.fittedvalues().values ) - 1 ] < 0:
        return 0

    return autoparameters.fittedvalues().values[ len( autoparameters.fittedvalues().values ) - 1 ]

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
                
            issueCloseDates.append( date1.split( '-' )[ 0 ] + '-' + date1.split( '-' )[ 1 ] )
            issueNumDaysToFix.append( time.days )

# Place issue close data over time in a DataFrame
def issues_over_time () :

    # Average length of time to close issues per month
    for i in range( len( issueCloseDates ) ):
        if ( issueCloseDates[ i ] not in issuesClosedPerMonth ):
            issuesClosedPerMonth[ issueCloseDates[ i ] ] = 1 
            issueAvgDaysToFix[ issueCloseDates[ i ] ] = issueNumDaysToFix[ i ]
        else:
            issueAvgDaysToFix[ issueCloseDates[ i ] ] += issueNumDaysToFix[ i ]
            issuesClosedPerMonth[ issueCloseDates[ i ] ] += 1


    for x in issuesClosedPerMonth.keys():
        issueAvgDaysToFix[ x ] = issueAvgDaysToFix[ x ] / issuesClosedPerMonth[ x ]

    df = pd.DataFrame({
        "Dates": issueAvgDaysToFix.keys(),
        "Actual": issueAvgDaysToFix.values()
    })

    df.sort_values( by = 'Dates', ascending = True, inplace = True )

    idx = pd.date_range( df.Dates.min(), datetime.today(), freq = 'M' )

    df.set_index( df.Dates )

    # Ensure it is monthly data in the index
    for i in idx:
        current  = pd.to_datetime( i )
        current = current.strftime( format = "%Y-%m" )
        if current not in df[ 'Dates' ].unique():
            df = pd.concat( [ pd.DataFrame( [ [ current, 0 ] ], columns = df.columns ), df ], ignore_index = True )

    df.sort_values( by = 'Dates', ascending = True, inplace = True )

    return df

###############################################################################

###############################################################################
# SECTION 3: Vulnerability Prediction by NVD Data                                        #
###############################################################################

# extract keywords for each dependency
def extractKeywords ( dependency ):
    
    array = dependency.split( "-" )

    for i in array:
        if "." in i:
            array.remove( i )
            newSection = i.split( "." )
            if "org" == newSection[ 0 ]: 
                newSection.remove( "org" )
                array = newSection + array
            elif newSection[ 0 ].isdigit():
                array.append( newSection[ 0 ] ) 
            else:
                array = newSection + array 

    current = ""

    for i in array:
        if i.isdigit():
            array.append( array[ 0 ] + i )
            array.remove( i )
        else: 
            current += i + " "

    array.append( current )

    return removeUnncessary( array )

# removing any unncessary keywords
def removeUnncessary ( array ):
    
    if "jar" in array: array.remove( "jar" )
    if "core" in array: array.remove( "core" )
    if "win" in array: array.remove( "win" )
    if "base" in array: array.remove( "base" )
    if "plugins" in array: array.remove( "plugins" )
    if "web" in array: array.remove( "web" )
    if "api" in array: array.remove( "api" )
    if "classic" in array: array.remove( "classic" )
    if "module" in array: array.remove( "module" )
    if "parameter" in array: array.remove( "parameter" )
    if "embed" in array: array.remove( "embed" )
    if "expression" in array: array.remove( "expression" )
    if "byte" in array: array.remove( "byte" )
    if "runtime" in array: array.remove( "runtime" )
    if "java" in array: array.remove( "java" )
    if "test" in array: array.remove( "test" )
    if "smart" in array: array.remove( "smart" )
    if "platform" in array: array.remove( "platform" )
    if "engine" in array: array.remove( "engine" )
    if "agent" in array: array.remove( "agent" )
    if "SNAPSHOT" in array: array.remove( "SNAPSHOT" )
    if "xml" in array: array.remove( "xml" )
    if "legacy" in array: array.remove( "legacy" )
    if "settings" in array: array.remove( "settings" )

    return array

vulnerabilityDates = []

# Predict Number of Vulnerabilities Per Month
def vulPrediction ( dependency ):
    
    vulnerabilityDates.clear()

    keywords = extractKeywords( dependency )
    
    vulnerabilities = []

    # Gather data for each of the keywords
    for x in keywords:
        
        # Search NVD API using the keywords from the dependencies
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={x}&resultsPerPage=2000"

        token = currentConfig.nvd_key
        headers = { 'User-Agent': 'request'
               , 'apiKey': token }
        
        response = requests.get( url, headers = headers )

        if response != None:
            
            if response.status_code == 200:

                for i in response.json()[ 'vulnerabilities' ]:
                    if i[ 'cve' ] not in vulnerabilities:
                        vulnerabilities.append( i[ 'cve' ] )
            else:
                print( response.status_code )

    popDates( vulnerabilities )

    numVuls = vulnerabilityPrediction( vuls_over_time(), dependency )

    if numVuls != -1:
        return float( numVuls / int( currentConfig.num_vuls ) ) * 10

    return numVuls
 
# Predict number of vulnerabilities per month
def vulnerabilityPrediction ( df, dependency ):

    df.index = pd.DatetimeIndex( df.Dates ).to_period( 'M' )

    # ensure that the values are not constant
    if len( df[ 'Actual' ].unique() ) == 1 or len( df ) == 0:
        return -1

    # Automatic prediction
    autoparameters = auto_arima( y = df[ 'Actual' ], seasonal = False )

    # Place the predicted values in a dataframe
    df2 = pd.DataFrame({
       "Dates": autoparameters.fittedvalues().axes[ 0 ].strftime( "%Y-%m" ),
       "Prediction": autoparameters.fittedvalues()
    })

    # Concatenate the data
    df = pd.concat( [ df, df2 ] )

    # Graph predicted vs actual values
    fig = px.line( data_frame= df, x = 'Dates', y = [ 'Actual', 'Prediction' ],  color_discrete_map={
                 "Actual": "#0AFBFF",
                "Prediction": "#FBFF00"
             } )
    
    fig.update_traces( line = dict( width = 3 ) )
    
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title = f'Vulnerabilities Over Time for : {dependency}'
    )
    
    fig.show()

    # not enough data for a prediction
    if len( set( autoparameters.fittedvalues().values ) ) == 1:
        return -1

    df = df.replace( np.nan, 0 )
    
    # EVALUATION SECTION
    df[ 'forecast_error' ] = df[ 'Actual' ] - df[ 'Prediction' ]

    # Calculate the absolute percentage errors
    df[ 'absolute_percentage_error' ] = ( df[ 'forecast_error' ].abs() / df[ 'Actual' ].replace( 0, 1 ) ) * 100

    # Calculate the MAPE
    mape = df[ 'absolute_percentage_error' ].mean() 

    mae = mean_absolute_error( df[ 'Actual' ], df[ 'Prediction' ] )

    rmse = mean_squared_error( df[ 'Actual' ], df[ 'Prediction' ], squared = False )

    print( "**************************************************************************************************" )
    print( "* Evaluation Metrics for Vulnerability Prediction for", dependency, ":" )
    print( "\n" )
    print( "* MAPE:", mape )
    print( "\n" )
    print( "* MAE:", mae )
    print( "\n" )
    print( "* RMSE:", rmse )
    print( "**************************************************************************************************\n" ) 

    # if the prediction is below 0 then return 0
    if autoparameters.fittedvalues().values[ len( autoparameters.fittedvalues().values ) - 1 ] < 0:
        return 0

    return autoparameters.fittedvalues().values[ len( autoparameters.fittedvalues().values ) - 1 ]

# Populate the Dates for gathered vulnerabilities per month
def popDates ( vuls ) :
    for x in vuls:
        date = x[ 'published' ]           
        date = date.split( "T") 
        date = date[ 0 ].split( "-" )
        date = date[ 0 ] + '-' + date[ 1 ]

        vulnerabilityDates.append( date )

# Place number of vulnerabilities over time in a dataframe
def vuls_over_time ():
    
    i = 0

    vulCounts = dict()

    for x in vulnerabilityDates: 
        if x in vulCounts :
            vulCounts[ x ] += 1
        else:
            vulCounts[ x ] = 1
            i += 1

    df = pd.DataFrame({
        "Dates": vulCounts.keys(),
        "Actual": vulCounts.values()
    })

    if len( df ) == 0:
        return df

    df = df.drop_duplicates() 

    df.sort_values( by = 'Dates', ascending = True, inplace = True )

    idx = pd.date_range( df.Dates.min(), datetime.today(), freq = 'MS' )

    df.set_index( df.Dates )

    # Ensure it is monthly data in the index
    for i in idx:
        current  = pd.to_datetime( i )
        current = current.strftime( format = "%Y-%m" )
        if current not in df[ 'Dates' ].unique():
            df = pd.concat( [ pd.DataFrame( [ [ current, 0 ] ], columns = df.columns ), df ], ignore_index = True )

    df.sort_values( by = 'Dates', ascending = True, inplace = True )

    return df

###############################################################################


# Starting the Program
def main():
    
    # SETUP
    populateDependencyLinks()
    configuration()

    # Analysis
    findDependencies()
    

if __name__ == "__main__":
    main()