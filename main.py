
import os
import UMutils
import UMViz
import pandas as pd

# Configuration Settings
#from dotenv import load_dotenv
# LambdaHandler API to interact with MySQL database
import LambdaHandlers

#Args are paths to directories
def generate_cred_scores(datahunt_dir, iaa_dir, schema_dir, results_dir, goldstandard_dir):
    # relative_dir = os.path.abspath(os.getcwd()) + "/"
    # datahunt_dir = os.path.join(relative_dir, datahunt)
    # iaa_dir = os.path.join(relative_dir, iaa)
    # schema_dir = os.path.join(relative_dir, schema)
    # results_dir = os.path.join(relative_dir, results)
    # goldstandard_dir = os.path.join(relative_dir, goldstandard)
    print(os.path.exists(datahunt_dir))
    # try:
    #     if not (
    #         os.path.exists(datahunt_dir)
    #         and os.path.exists(schema_dir)
    #         and os.path.exists(results_dir)
    #     ):
    #         raise errors.InvalidDataDirectoryError
    # except errors.InvalidDataDirectoryError:
    #     print("One of the required data directories does not exist.")
    #     sys.exit()

#    load_dotenv()

    endpoint = os.environ.get("ENDPOINT")
    username = os.environ.get("USERNAME")
    database_name = os.environ.get("DB_NAME")
    #database access info
    password = 'GoodlyLocalPass'
    database_name = 'user_credibility_scores'

    api = LambdaHandlers.LambdaHandler(
        host=endpoint, user=username, passwd=password, db=database_name
    )

    # FIXME: Clear all tables
    api.remake_all_tables()
    # Keep track of how many rows we processed in every datahunt thus far
    datahunt_tracker = pd.DataFrame(columns=["datahunt_id", "num_rows_processed"])
    num_rows_processed = 0
    datahunt_id = None

    # Pull in all the data for this iteration of scoring
    if os.path.exists(goldstandard_dir):
        module_filemap = UMutils.get_module_files_mapping(
            datahunt=datahunt_dir,
            iaa=iaa_dir,
            schema=schema_dir,
            goldstandard=goldstandard_dir,
        )
    else:
        module_filemap = UMutils.get_module_files_mapping(
            datahunt=datahunt_dir, iaa=iaa_dir, schema=schema_dir, goldstandard=None
        )

    if os.path.exists(goldstandard_dir):
        (
        ArgumentFinal,
        EvidenceFinal,
        LanguageFinal,
        ProbabilityFinal,
        ReasoningFinal,
        SourceFinal,
        ) = UMutils.get_matched_goldstandard_schema(module_filemap)
    else:
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
        merged_schema = eval("%sFinal" % (module_name))
        if (
            module_filemap[module_name]["Datahunt"] is not None
            and module_filemap[module_name]["Schema"] is not None
        ):
            scored_questions, question_schema = UMutils.get_module_template(
                module_name, module_filemap
            )
            schema = module_filemap[module_name]["Schema"]
            dh_file = pd.read_csv(module_filemap[module_name]["Datahunt"])
            # If data hunt was partially processed before, ignore the processed rows
            # FIXME: Implement
            UMutils.score_task(
                merged_schema=merged_schema,
                dh_file=dh_file,
                question_schema=question_schema,
                scored_questions=scored_questions,
                client=api,
                with_goldstandard=True
            )
            # Update how much of the Datahunts we've processed
            # datahunt = pd.read_csv(module_filemap[module_name]["Datahunt"])
            # num_rows_processed = datahunt.shape[0]
            # datahunt_id = datahunt["schema_sha256"][0]
            # api.insert_into_table(
            #     "datahunt_tracker",
            #     num_rows_processed=num_rows_processed,
            #     datahunt_id=datahunt_id,
            # )
        UMutils.progress_bar(i + 1, len(module_filemap.keys()))


    # Add results to results directory
    api.post_results(data_dir=results_dir, name="ucs_global")

    # FOR PROF DEKAI ONLY - Whitelist participating users and calculate scores
    participants = UMutils.load_participants_list(results_dir + "/dekai-users.csv")
    demo_users_ucs = UMutils.get_whitelisted_users(participants, client=api)
    UMutils.post_whitelisted_ucs(data_dir=results_dir, ucs=demo_users_ucs)
    # Create and save visualizations
    UMViz.ucs_histogram(data_dir=results_dir, data=demo_users_ucs)

if __name__ == '__main__':

    datahunt = './dekai-datahunt'
    iaa = './dekai-iaa'
    schema = './dekai-schema'
    results = './dekai-results'
    goldstandard = './dekai-goldstandard'

    generate_cred_scores(datahunt, iaa, schema, results, goldstandard)

print("\n")
