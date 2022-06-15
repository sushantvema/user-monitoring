# User Credibility Score Algorithm for Public Editor

## Installation:

1. Clone this repository
2. Install the pipenv package if you haven't already
3. `pipenv install --dev` to install all development packages for this project as outlined in the Pipfile
   `pipenv install ` to install all main dependendances for this project as outlined in the pipfile.
4. `pipenv shell` to initialize the virtual environment

## Running the Program:

The User Credibility Score algorithm takes in Datahunt, Inter Annotator Agreement (IAA), Schema, and optionally Gold Standard files for a set of one or more annotation modules, and outputs a .csv of UCS scores and a set of visualizations [TBD] to a results directory. The entire pipeline is in the form of a python executable and leverages a MySQL RDS accessed via pysmysql for long term data tracking and processing. Running the program requires creating a specific file system directory setup that is explained below. This system is intended to be run as a batch processor for one or more annotation modules at a time.

1. `cd ucs-update-algorithm`
2. In order to calculate User Credibility Scores for annotation module data, you must create the following directories. Please refer to the set of directories starting with dekai- as an example of this setup.

- `name-datahunt` for all the datahunt files
- `name-iaa` for all the IAA files
- `name-schema` for all the schema files
- OPTIONAL: `name-goldstandard` for all the Gold Standard files
- `name-results` where the calculated UCS scores will go along with any generated visualizations

3. Notes: For each annotation module you're planning on grading, you MUST have a datahunt, iaa, and schema file all placed in the appropriate directory. In the case that you're using gold standard data to grade annotation modules, ALL the modules have to have gold standard files.
4. Once you have the data directories set up, you can run the script with `python3 main.py name-datahunt name-iaa name-schema name-goldstandard name-results` where `name` is just an arbitrary but uniform label for all the data directories in this batch.
5. The process takes between 5-10 minutes to run. A progress tracker is displayed in the command line.

##

## OLD: ACTION ITEMS FOR April 3rd 2022 User Monitoring PRESENTATION

## Are we on track to present our work by Sunday? YES

To access the notebook we're using for our analysis, go to /ucs-update-algorithm/pipeline.ipynb. Refer to the following sections of the README as a rough timeline for deliverables this weekend. Move completed tasks to the Completed Tasks section. Message Sushant or add a suggestion if necessary.

### Production Tasks:

- make sure everyone pulls. git checkout master, git pull, delete your name branch if you have one, then recreate the branch
- [high] create functionality to update values in any table in the database:
- [high] whitelist all the users in Covid_Source_Users.xlsx
  - at the end of the day we want to keep all of the users in this spreadsheet and associate their uiid’s with their nicknames
  - end up having a table containing nickname, uuid, and ucs score, in descending order
- [medium] figure out way to automate schema reading and loading
  - Function that IAA uses to automate reading and loading schema files: https://github.com/Goodly/pe-consensus-scoring/blob/master/consensus_and_scoring/dataV3.py#L634
  - Some dependency of that? https://github.com/Goodly/pe-consensus-scoring/blob/master/consensus_and_scoring/config/typing_dict.txt
- [medium] handler functions to clear / reset the database tables:
  - 1 function to empty all of the 3 tables in the database
  - [low] 1 function to DELETE everything in the database
  - [low] 1 function to initialize all the tables in the database
- [low] after every run of the pipeline on demo-related tasks, save the csv locally. then continually merge the results of new pipeline runs. then output a single csv file with ucs scores for all n tasks for the demo
- [low] figure out way to pull gold standard data when applicable
- [low] data validation capabilities for insert_into_table() and all of its cases
- [low] change AWS information guide to remove part about whitelisting devices
  - we changed inbound rules to AnyIPv4 so anyone can connect to our instance if they have the credentials

### Demonstration Tasks:

- run the pipeline one time starting with Covid_SourceRelevancev1-2022-04-01T0047-DataHunt.csv.gz [quoted source annotation module]
- eventually run the pipeline and save results for each of the different annotation modules
- sort all the ucs scores in descending order
- save all of the csv's and send them to Nick by sunday afternoon

### Completed Tasks [in order of recency]:

- [high] created functionality to delete all the tables in the database + re-initialize the database
- [high] created functionality to clear specific tables in the database
- [high] create functionality to download tables from aws instance as csv's when necessary
- [low] debug the display helper function in the handler functions cell:
  - we want to be able to print the contents of any table onto the jupyter notebook
- [high] un-hardcode all the cases in insert_into_table():
  - insert into ucs:
    - iterate over rows in df (dataframe containing uuid’s and scores) and add them to the the ucs table
  - insert into task_scores:
    - iterate over rows in df (calculated_task_scores) and add them to the task_scores table
  - insert into datahunt_tracker:
    - add datahunt id (quiz_task_uuid) as well as num_rows_processed
- [high] ask Nick to create csv’s for the people in each task instead of xlsx going forward
- [high] functions to extract csv's from the repo and preprocess to make it usable by Jay's algorithm. uncompress all files from .gz to .csv when we load them in from evidence_eric
- [high] push the data hunts, iaa files, and schema files for all of the annotation modules to evidence_eric
