import os
import pandas as pd
import numpy as np
import colorama
from datetime import datetime
import sys


def get_module_files_mapping(datahunt, iaa, schema, goldstandard):
    """
    Returns a dictionary of dictionaries containing the datahunt, iaa, schema,
    and goldstandard (if it exists) files for each of the annotation
    modules present in the given data directories.
    """
    mapping = {
        "Argument": {
            "Datahunt": None,
            "IAA": None,
            "Schema": None,
            "GoldStandard": None,
        },
        "Evidence": {
            "Datahunt": None,
            "IAA": None,
            "Schema": None,
            "GoldStandard": None,
        },
        "Reasoning": {
            "Datahunt": None,
            "IAA": None,
            "Schema": None,
            "GoldStandard": None,
        },
        "Source": {"Datahunt": None, "IAA": None, "Schema": None, "GoldStandard": None},
        "Language": {
            "Datahunt": None,
            "IAA": None,
            "Schema": None,
            "GoldStandard": None,
        },
        "Probability": {
            "Datahunt": None,
            "IAA": None,
            "Schema": None,
            "GoldStandard": None,
        },
    }

    for modulename in mapping.keys():
        for dh in os.listdir(datahunt):
            if modulename in dh:
                dh_path = os.path.join(datahunt, dh)
                mapping[modulename]["Datahunt"] = dh_path
        for iaa_file in os.listdir(iaa):
            if modulename in iaa_file:
                iaa_path = os.path.join(iaa, iaa_file)
                mapping[modulename]["IAA"] = iaa_path
        for schema_file in os.listdir(schema):
            if modulename in schema_file:
                schema_path = os.path.join(schema, schema_file)
                mapping[modulename]["Schema"] = schema_path

    # if os.path.exists(goldstandard):
    #     for gs in os.listdir(goldstandard):
    #         if

    return mapping


def merge_iaa_schema(iaa, schema):
    """
    Returns new IAA file with question number and agreed answer
    """
    if iaa is None or schema is None:
        return
    if not os.path.exists(iaa) or not os.path.exists(schema):
        return
    iaa = pd.read_csv(iaa)
    schema = pd.read_csv(schema)
    temp_schema = schema.loc[:, ["answer_uuid", "answer_label"]]
    temp = iaa.merge(temp_schema, how="left", on="answer_uuid")
    answer = (
        pd.DataFrame(temp["answer_label"].str.split(".", expand=True))
        .iloc[:, 2]
        .str[1:]
    )
    question = (
        pd.DataFrame(temp["answer_label"].str.split(".", expand=True))
        .iloc[:, 1]
        .str[1:]
    )
    temp["question_Number"] = question.astype(int)
    temp["agreed_Answer"] = answer.astype(int)
    return temp


def get_module_template(module_name, module_filemap):
    """
    Returns a list and a dictionary, scored_questions and question_schema.

    scored_questions is a list of integers representing each of the questions
     to be scored in the module.

    question_schema is a dictionary of dictionaries with the question number
    mapping to a dictionary containing two key-value pairs representing the
    question type and the number of answer choices that question has.
    """
    non_scoring_questions = [
        "How difficult was this task for you, on the whole?",
        "How confident are you about your answers, on the whole?",
        "Is there anything about the interface, instructions, or question wording that could be improved to make tasks like this easier?",
    ]
    scored_questions = []
    question_schema = {}

    schema_path = module_filemap.get(module_name).get("Schema")
    schema = pd.read_csv(schema_path)

    dh_grouped = (
        schema.groupby(["question_label", "question_text"]).agg(list).reset_index()
    )

    dh_grouped["question_number"] = (
        dh_grouped["question_label"].str.split(".Q").apply(lambda x: x[1])
    )

    for index, row in dh_grouped.iterrows():
        if (
            row["question_text"] not in non_scoring_questions
            and row["question_type"][0] != "TEXT"
        ):
            scored_questions.append(row["question_number"])
            # FIXME
            if row["question_type"][0] == "RADIO":

                question_type = "select_one_nominal"
            if row["question_type"][0] == "CHECKBOX":
                question_type = "select_all"
            else:
                question_type = "select_all"
                # print(row["question_type"][0])
                # sys.exit()
            dct = {
                "type": question_type,
                "num_choices": len(row["answer_content"]),
            }
            question_schema[row["question_number"]] = dct

    return scored_questions, question_schema


def schema_to_type_and_num(ques, schema_path, config="./evidence_eric/"):
    df = pd.read_csv(schema_path, encoding="utf-8")
    override = pd.read_json(config + "schema_override.txt")
    ques = "T1.Q" + str(ques)
    qrows = df.loc[df["question_label"] == ques]
    q_uuid = qrows["question_uuid"].iloc[0]
    if len(override[override["question_uuid"] == q_uuid]) > 0:
        qrows = override[override["question_uuid"] == q_uuid]
    question_type = qrows["question_type"].iloc[0]
    if question_type == "CHECKBOX":
        question_type = "checklist"
    else:
        question_type = qrows["alpha_distance"].iloc[0]
    answer_count = qrows["answer_count"].iloc[0]
    return question_type, answer_count


def get_matched_iaa_schema(module_filemap):
    packed = []
    for module_name in module_filemap.keys():
        iaa = module_filemap[module_name]["IAA"]
        schema = module_filemap[module_name]["Schema"]
        df = merge_iaa_schema(iaa, schema)
        if not df is None:
            packed.append(df)
        else:
            packed.append(None)
    return packed


def ucs_update_score(user_id, client):
    """
    User Credibility Score function that reads values from a csv and a current user's UCS score from
    the database.
    """

    def logistic(x, k, offset):
        return 1 / (1 + np.e ** (-k * (x - offset)))

    cursor = client.connection.cursor()
    task_scores = client.table_to_df("task_scores")
    task_scores = task_scores[task_scores["user_uuid"] == user_id]["task_score"].astype(
        "float"
    )
    last_task_score = task_scores.iloc[-1]

    a = 1000
    num_task_scores = len(task_scores)
    n = min(10, int(np.sqrt(num_task_scores)) + 1)
    ucs = client.table_to_df("ucs")
    if user_id not in ucs["uuid"].values:  # if this is the user's first task
        cur_ucs = 0.5
        var_scores = np.var(task_scores.iloc[-n:])
        c = logistic(var_scores / (np.log(num_task_scores + 1) / (np.log(a))), 10, 0.2)
        new_ucs = cur_ucs * (1 - c) + (c) * last_task_score
        query = "INSERT INTO `ucs` (`uuid`, `score`) VALUES (%s, %s)"
        cursor.execute(query, (user_id, new_ucs))
        client.connection.commit()
    else:
        cur_ucs = ucs[ucs["uuid"] == user_id]["score"].astype("float").iloc[0]
        var_scores = np.var(task_scores.iloc[-n:])
        c = logistic(var_scores / (np.log(num_task_scores + 1) / (np.log(a))), 10, 0.2)
        new_ucs = cur_ucs * (1 - c) + (c) * last_task_score
        query = "UPDATE `ucs` SET `score` = %s WHERE `uuid` = %s"
        cursor.execute(query, (new_ucs, user_id))
        client.connection.commit()
    cursor.close()


def get_answer(question, answer_source, consensus_answers, question_schema):
    """
    Take in the question and the answer_source, either IAA or Adjudicated / Gold Standard, and adds the
    converged consensus answer to the consensus_answer answer key. This will be an single
    int for select_one questions, or a list of ints for select_all questions.
    """
    question_type = question_schema[question]["type"]
    # FIXME Radio should be dynamically classified as nominal or ordinal
    if question_type == "select_one_nominal" or question_type == "select_one_ordinal":
        consensus_answers[question] = answer_source[
            answer_source.question_Number == int(question)
        ].agreed_Answer.iloc[0]
    elif question_type == "select_all":
        consensus_answers[question] = list(
            answer_source[answer_source.question_Number == int(question)].agreed_Answer
        )
    else:
        print(question_type)
        raise ValueError("Invalid question type")

    return consensus_answers


def score_task(iaa_file, adj_file, dh_file, question_schema, scored_questions, client):
    # adj_file takes priority
    if adj_file is not None:
        file = adj_file
    else:
        file = iaa_file

    # cleaning invalid rows in file
    file = file[file.answer_uuid.str.len() > 3]

    # these are the only relevant columns for scoring for now, notice highlight data is not included here
    cols = ["answer_uuid", "question_Number", "agreed_Answer"]

    # getting rid of some rows where the above columns were the same, this may represent different
    # highlights for the same question and answer?
    file = file[cols].drop_duplicates()

    consensus_answers = {}

    # create a set of questions that the IAA data determined converged to a consensus
    file_consensus_questions = set(file.question_Number)

    # uses get_answer function to fill in the consensus_answers answer key
    for question in scored_questions:
        if int(question) in file_consensus_questions:
            consensus_answers = get_answer(
                question, file, consensus_answers, question_schema
            )
        else:
            consensus_answers[question] = -1

    # narrow down the datahunt to the relevant columns for scoring, getting rid of some rows
    # where the data for the below columns were the same, this may represent different highlights
    # for the same question and answer? not certain.
    dh = dh_file[
        ["contributor_uuid", "question_label", "answer_label"]
    ].drop_duplicates()

    # the question and answer labels in the datahunt are in the form 'T1.QX' and 'T1.QX.AX'
    # the below lines strip down to only question number and answer number
    dh["question_label"] = dh["question_label"].str.split("Q").str[1].astype(int)
    dh["answer_label"] = dh["answer_label"].str.split("A").str[1]

    # we want to groupby contributor_uuid and question_label to get all the answers a user
    # selected for a particular question, to account for select_all questions. Now, the
    # granularity of df_grouped will be one row per contributor answering a question.
    dh_grouped = (
        dh.groupby(["contributor_uuid", "question_label"]).agg(list).reset_index()
    )

    # we only want to score the rows with scored questions (not survey questions like 13 and 14)
    # so we'll filter those out
    filter = dh_grouped.question_label.isin(map(int, scored_questions))
    dh_grouped = dh_grouped[filter]

    def scoring_select_one_nominal(question, answer):
        """
        Takes in a question and the selected answer, returns a score of 0 if the consensus
        answer is different, and 1 if the consensus answer is the same.
        """
        consensus_answer = int(consensus_answers[str(question)])
        return int(consensus_answer == answer)

    def scoring_select_one_ordinal(question, answer):
        """
        Takes in a question and the selected answer, returns a score between 0 and 1 depending
        on how far off the answer is from the consensus answer.
        """
        consensus_answer = int(consensus_answers[question])
        num_choices = question_schema[question]["num_choices"]
        return 1 - (abs(answer - consensus_answer) / num_choices)

    def scoring_select_all(question, answer_list):
        """
        Takes in a question and the selected answer, returns a score between 0 and 1 depending
        on the accuracy ((True Positive + True Negative) / Total) of the answer selections
        compared to the consensus answer selections.
        """
        answer_set = set(answer_list)
        consensus_answer_set = set(consensus_answers[question])
        num_choices = question_schema[question]["num_choices"]

        total_correct = 0
        for answer in range(1, num_choices + 1):
            if (answer in answer_set) and (answer in consensus_answer_set):
                total_correct += 1
            elif (answer not in answer_set) and (answer not in consensus_answer_set):
                total_correct += 1
            else:
                total_correct += 0

        return total_correct / num_choices

    def scoring(row):
        """
        This is a Pandas apply function, to be applied on axis=1 (on each row).
        Makes a call to one of scoring_select_one_nominal, scoring_select_one_ordinal, and
        scoring_select_all depending on the type of question, returns the outputted score.

        An important note is that right now if neither IAA nor Gold Standard have a consensus
        answer for a question, the consensus_answers answer key will contain a -1 for that
        question. I currently assume this question should not have been answered due to it
        being a child-question from an incorrectly answered parent question, so I score it
        """
        question = int(row["question_label"])
        answer_list = [int(i) for i in row["answer_label"]]

        if consensus_answers[str(question)] == -1:
            return 0

        question_type = question_schema[str(question)]["type"]
        if question_type == "select_one_nominal":
            return scoring_select_one_nominal(question, answer_list[0])
        elif question_type == "select_one_ordinal":
            return scoring_select_one_ordinal(question, answer_list[0])
        elif question_type == "select_all":
            return scoring_select_all(question, answer_list)
        else:
            raise ValueError("Invalid question type")

    # using the scoring function defined above, we'll create a new column containing the scores
    # for each contributor answering a question.
    dh_grouped["score"] = dh_grouped.apply(scoring, axis=1)
    # lastly, we want to get the average score for all task responses, this will be their
    # task score. this is done by a simple groupby on contributor_uuid and mean() aggregate function
    calculated_task_scores = (
        dh_grouped[["contributor_uuid", "score"]]
        .groupby("contributor_uuid")
        .mean()
        .reset_index()
    )

    quiz_task_uuid = dh_file["quiz_task_uuid"][0]
    rows_processed = len(dh_file)

    calculated_task_scores["quiz_task_uuid"] = quiz_task_uuid
    calculated_task_scores = calculated_task_scores[
        ["quiz_task_uuid", "contributor_uuid", "score"]
    ]

    client.insert_into_table("task_scores", calculated_task_scores)

    for user_id in calculated_task_scores["contributor_uuid"]:
        ucs_update_score(user_id, client=client)


def load_participants_list(file_name):
    participants = pd.read_csv(file_name).iloc[2:, :]
    participants.columns = [
        "ux_contributor_id",
        "nickname",
        "contributor_uuid",
        "retrieved_task_runs",
        "total_worktime",
    ]
    return participants


def get_whitelisted_users(participants_list, client):
    # FIXME: Some duplicate uuid's in ucs at the end of the day
    ucs = client.table_to_df("ucs").astype({"score": float}).groupby(["uuid"]).mean()
    ucs = pd.merge(
        ucs, participants_list, left_on="uuid", right_on="contributor_uuid", how="right"
    )
    ucs = ucs.sort_values(by="score", ascending=False)
    return ucs


def post_whitelisted_ucs(data_dir, ucs):
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    ucs.to_csv(f"{data_dir}/whitelisted_ucs_{date}.csv")


def progress_bar(progress, total, color=colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = "█" * int(percent) + "-" * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if progress == total:
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")