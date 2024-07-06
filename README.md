# MSC Computing - Practicum Project 

This repository contains the work that I did for my practicum project during my time at Dublin City University. The use of open-source software in large projects has been growing in the last number of years. Attackers exploit known vulnerabilities in open-source software and this measuring the risk of using these projects is essential. In large projects there can be a number of dependencies which depend on other projects and thus developers can be unaware of the risks that they are exposing themselves to - such as unmaintained projects. This project is a tool for the analysis of the risk of using open-source software. This project aims to investigate the dependency tree of a project and analyse the risk for each of the sub-dependencies giving the user a visual way to explore the risk level of their dependencies.  

## Code - Analysis.py 💻

The idea of the analysis is to analyse and pinpoint the dependencies that are exposing a project to risk. We extract the dependencies from a dependency tree provided by a Maven project. The analysis was split up into the two different objects of analysis that are commonly used to examine risk prediction in open-source projects. Both project activity and the number of vulnerabilities per month are indicators of how risky a project is according to the literature we reviewed. The aim we have is to combine these to give a more comprehensive view of the risk in using a particular open-source project. The idea behind this is that a dependency with some vulnerabilities may be less risky if it is well maintained and a dependency that is not maintained may be less risky if there are never any vulnerabilities associated with it. 

### Setup

The setup involves populating the dependency links using the input in the text file provided. This is used to analyse the GitHub repo information - for either counting commits or counting number of days to resolve issues. The second piece of setup involves taking the configuration file as provided/edited by the user and placing it into the configuration object. 

### Finding and Graphing the Dependencies (of a Maven Project)

The first part of the analysis involves finding the dependencies of a project using the output from the maven dependency tree. We assign each dependency a node in the graph and add edges according to its depth in the dependency tree. The node is coloured based on its analysed and predicted risk (according to the levels set by the user). 

### Risk Prediction Using Project Activity

This part of the analysis aims to predict how well the project is maintained and thus how quick the response time will be to any issues or vulnerabilities reported by users or developers. We measure both the time-to-fix issues and the number of commits per month. The user has the option of exploring risk through commits/issues or both. We use AutoARIMA for this anr return the final predicted value. 

### Risk Prediction Using Vulnerability Database Data

This part of the analysis aims to predict how many vulnerabilities will be reported monthly for the project. This will give an indicator as to how risk-prone the project is. We extract keywords from dependencies and use these to find associated CVEs using the NVD API. We then count the monthly vulnerabilities and aim to predict these. 

## Graphs Generated 📈

- Graph of different dependencies colour coded with their associated risk using NetworkX
- Project Activity Prediction Graphs for each dependency
- Vulnerability CVE Data Predictions for each dependency

## Docs 📁

- Practicum Proposal Form
- Literature Review
- Final Report ( In Progress )
- Practicum Presentation ( Started )

## Data 📑

- dependencies1-4.txt are the test dependency trees files
- config.JSON is the configuration file
- github_urls.txt contains the libraries in the dependency trees and their corresponding github urls
- requirements.txt contains all the requirements to install to run this project

## Project Instructions❗

The idea is that this project and its corresponding data - config.JSON, github_urls.txt and the Analysis.py files can be placed in a folder with a maven project. The user can enable the configuration options as they see fit - to analyse issues/commits, number of days/commits they see as appropriate and number of vulnerabilities before they consider the dependency to be risky. Then the user can run the program which will gather the dependencies and analyse their GitHub activity and NVD vulnerabilities to see which of their dependencies are risky (in their decided levels). 

### Windows Instructions

1. Install python3 and pip3
2. Clone this repository
```bash
  git clone https://github.com/rnibhriain/practicum-code.git
```
4. Edit the configurations to your liking (including adding a github token)
5. Place the folder in a maven project
6. Install the requirements using command (in the Data folder):
```bash
  pip install -r requirements.txt
```
6. Run the analysis file using:
```bash
  py Analysis.py
```
7. Explore the resulting graphs!

## Technology Used

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
