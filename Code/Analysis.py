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
    url = "https://api.github.com/repos/apache/spark/issues?per_page=100&page=1"

    token = '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'
    headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
    res = requests.get(url, headers=headers)
    print(f"Status code: {res.status_code}")
    print(res.reason)

    print(res.links['last']['url'])

    current = res.links['last']['url'].split("=")
    print( "the length is: " , current[2])
    length = int(current[2])

    commits = []
    issues = []

    i = 1
    while ( i < length ):
        url = f"https://api.github.com/repos/apache/spark/issues?per_page=100&page={i}"
        token = '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'
        headers = {"Accept": "application/vnd.github.v3+json", 'User-Agent': 'request'
               , 'Authorization': 'token ' + token }
        res = requests.get(url, headers=headers)

        if (res.status_code == 200):
                    issues.append(res)
                    commits.append(res)
        
        issuesResolving( issues )
        # num_Contributors( commits )
        # populateDates ( commits ) 
        
        i += 1

    #commits_over_time()

    return 0

def populateTimes ():
    


    return 0

def issuesResolving ( issues ):
    for x in issues:
        for i in x.json(): 
            date = i['created_at']
            date1 = i['closed_at']

            print( date1 )
                
            date = date.split("T")

            dates.append(date[0])

    return 0

dates = []
counts = []
contributors = []
def populateDates ( commits ) :
    for x in commits:
        for i in x.json(): 
            date = i['commit']['author']['date'].replace("T", " ")
                
            date = date.split("T")

            dates.append(date[0])


def num_Contributors ( commits ) :
    for x in commits:
        for i in x.json(): 
            if i['commit']['author'] not in contributors:
                contributors.append( i['commit']['author'] )


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

    model = ARIMA(df.Count, order=(5,1,0))
    model_fit = model.fit()

    # plot residual errors
    residuals = pd.DataFrame(model_fit.resid)
    residuals.plot(kind='kde')
    print(residuals.describe())
    #pyplot.show()

    #figline = px.line(x=df.Dates, y=residuals)

    fig = go.Figure(data=figline.data)

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

    popDates( commits )
    vuls_over_time()

def popDates ( commits ) :
    print( len(commits))
    for x in commits:
        date = x[ 'published' ]
                
        date = date.split("T")
        date = date[0].split("-")
        date = date[0] + '-' + date[1]
        dates.append(date)

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
    ax1.set_title('1st Order Differencing')
    plot_acf(df.Count.diff().dropna(), ax=ax1)

    ax2 = f.add_subplot(122)

    result = adfuller(df.Count.dropna())
    print('p-value ', result[1])

    result = adfuller(df.Count.diff().dropna())
    print('p-value ', result[1])

    result = adfuller(df.Count.diff().diff().dropna())
    print('p-value ', result[1])


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
    print( "Please enter a package you would like to use from our list of packages" )

    ######################################################
    # come up with set list of packages
    # for now lets focus on apache cus idk
    ######################################################
    projectPrediction()
    #codePrediction()
    #vulPrediction ()

if __name__ == "__main__":
    main()