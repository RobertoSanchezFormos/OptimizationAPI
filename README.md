# REST API 

## How to execute it (without Docker):
1. In the terminal go to the root path of the project 
2. Install the requirements:
`pip3 install -r requirements.txt`
3. Run the application as follows:
   * PRODUCTION: `python3 app_prod.py`
   * DEVELOPMENT: `python3 app_dev.py`

## How to execute it (with Docker):
1. In the terminal go to the root path of the project 
2. Open the `docker-compose.yml` file and configure the environment according:
   * PRODUCTION: Change in the `environment `section: `ENVIROMENT=prod`
   * DEVELOPMENT: Change in the `environment `section: `ENVIROMENT=dev`
3. Execute `docker-compose -f docker-compose.yml up -d`
 


## How to check if it is running:
Open a web browser in:
* PRODUCTION: http://127.0.0.1/docs
* DEVELOPMENT: http://127.0.0.1:8000/docs

## GLPK package:

The GLPK (GNU Linear Programming Kit) package is intended for solving large-scale linear programming (LP), mixed integer programming (MIP), and other related problems. It is a set of routines written in ANSI C and organized in the form of a callable library. 

This project uses this Linear Programming Kit to solve large-scale problems related to Logistics, the installation 
depends on the Operating System:

- Windows: https://winglpk.sourceforge.net/ 
- Linux: `apt-get install -y -qq glpk-utils`
- Mac:  `brew install glpk`
