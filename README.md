# MSC Computing - Practicum Project

The use of open-source software in large projects has been growing in the last number of years. Attackers exploit known vulnerabilities in open-source software and this measuring the risk of using these projects is essential. In large projects there can be a number of dependencies which depend on other projects and thus developers can be unaware of the risks that they are exposing themselves to - such as unmaintained projects. This project is an analysis on the risk of using open-source software. This project aims to investigate the dependency tree of a project and analyse the risk for each of the sub-dependencies - the lower risk scores will percolate up to assign the project itself a score. 

## Code 

The idea of the analysis is to analyse and pinpoint the dependencies which are exposing a project to risk. We first use a dependency tree provided by Maven and extract the dependencies. The analysis was split up into the two different objects of analysis that are commonly used to examine risk in open-source projects. The aim we have is to combine these to give a more comprehensive view of the risk in using a particular open-source project.

### Setup
The setup involves populating the dependency links using the input in the text file provided. This is used to analyse the GitHub repo information - for either counting commits or counting number of days to resolve issues. The second piece of setup involves taking the configuration file as provided/edited by the user and placing it into the configuration object. 

### Finding and Graphing the Dependencies (of a Maven Project)

The first part of the analysis involves finding the dependencies of a project using the output from the maven dependency tree. 

### Risk Prediction Using Project Activity

This part of the analysis aims to predict how well the project is maintained and thus how quick the response time will be to any issues or vulnerabilities reported by users or developers.

### Risk Prediction Using Vulnerability Database Data

This part of the analysis aims to predict how many vulnerabilities will be reported monthly for the project. This will give an indicator as to how risk-prone the project is.

## Graphs

- Graph of different dependencies using NX
- Project Activity Prediction Graphs for each dependency
- Vulnerability Database Data Predictions for each dependency

## Docs

- Proposal Form
- Literature Review
- Final Report ( In Progress )
- Final Presentation ( Not Started )

## Data

- dependencies1-4.txt are the test dependency trees files
- config.JSON is the configuration file
- github_urls.txt contains the libraries in the dependency trees and their corresponding github urls

## Project Instructions
The idea is that this project and its corresponding data - config.JSON, github_urls.txt and the Analysis.py files can be placed in a folder with a maven project. The user can enable the configuration options as they see fit - to analyse issues/commits, number of days/commits they see as appropriate and number of vulnerabilities before it is too many. Then the user can run the program which will gather the dependencies and analyse their GitHub projects and NVD vulnerabilities to see which of their dependencies are risky (in their decided levels). 
