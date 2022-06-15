# Command Line Processing
from genericpath import exists
from importlib.resources import path
from sys import argv
import os
import UMutils
import UMViz
import pandas as pd

script, datahunt, iaa, schema, results, goldstandard = argv

relative_dir = os.path.abspath(os.getcwd()) + "/"
datahunt_dir = os.path.join(relative_dir, datahunt)
iaa_dir = os.path.join(relative_dir, iaa)
schema_dir = os.path.join(relative_dir, schema)
results_dir = os.path.join(relative_dir, results)
goldstandard_dir = os.path.join(relative_dir, goldstandard)

import errors
import sys

try:
    if not (
        os.path.exists(datahunt_dir)
        and os.path.exists(iaa)
        and os.path.exists(schema_dir)
        and os.path.exists(results_dir)
    ):
        raise errors.InvalidDataDirectoryError
except errors.InvalidDataDirectoryError:
    print("One of the inputted data directories does not exist.")
    sys.exit()

import pymysql
import time

# For jupyter notebooks
# Install pymysql in the current Jupyter kernel
# import tqdm
# !pip install --yes ipywidgets
# !jupyter nbextension enable --py widgetsnbextension
# !jupyter labextension install @jupyter-widgets/jupyterlab-manager
# from tqdm.notebook import tqdm, trange

# Configuration Settings
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ.get("ENDPOINT")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
database_name = os.environ.get("DB_NAME")

# LambdaHandler API to interact with MySQL database
import LambdaHandlers

api = LambdaHandlers.LambdaHandler(
    host=endpoint, user=username, passwd=password, db=database_name
)

# FIXME: Clear all tables
api.remake_all_tables()

# Pull in all the data for this iteration of scoring
module_filemap = UMutils.get_module_files_mapping(
    datahunt=datahunt_dir, iaa=iaa_dir, schema=schema_dir, goldstandard=None
)

(
    ArgumentFinal,
    EvidenceFinal,
    LanguageFinal,
    ProbabilityFinal,
    ReasoningFinal,
    SourceFinal,
) = UMutils.get_matched_iaa_schema(module_filemap)

# Scoring
print("Scoring Progress:")
UMutils.progress_bar(0, len(module_filemap.keys()))
for i, (module_name, m) in enumerate(module_filemap.items()):
    if (
        module_filemap[module_name]["Datahunt"] is not None
        and module_filemap[module_name]["IAA"] is not None
        and module_filemap[module_name]["Schema"] is not None
    ):
        scored_questions, question_schema = UMutils.get_module_template(
            module_name, module_filemap
        )
        iaa = module_filemap[module_name]["IAA"]
        schema = module_filemap[module_name]["Schema"]
        iaa_file = UMutils.merge_iaa_schema(iaa=iaa, schema=schema)
        if module_filemap[module_name]["GoldStandard"] is None:
            adj_file = None
        else:
            adj_file = pd.read_csv(module_filemap[module_name]["GoldStandard"])
        dh_file = pd.read_csv(module_filemap[module_name]["Datahunt"])

        UMutils.score_task(
            iaa_file=iaa_file,
            adj_file=adj_file,
            dh_file=dh_file,
            question_schema=question_schema,
            scored_questions=scored_questions,
            client=api,
        )
    UMutils.progress_bar(i + 1, len(module_filemap.keys()))

# Update how much of the Datahunts we've processed

# Add results to results directory
api.post_results(data_dir=results_dir, name="ucs_global")

# FOR PROF DEKAI ONLY - Whitelist participating users and calculate scores
participants = UMutils.load_participants_list(results_dir + "/dekai-users.csv")
demo_users_ucs = UMutils.get_whitelisted_users(participants, client=api)
UMutils.post_whitelisted_ucs(data_dir=results_dir, ucs=demo_users_ucs)
# Create and save visualizations
UMViz.ucs_histogram(data_dir=results_dir, data=demo_users_ucs)

# Reset command line color
import colorama

print(colorama.Fore.RESET)
