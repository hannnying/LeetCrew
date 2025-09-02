import pandas as pd
from utils import fetch_all_questions


def main():
    data = fetch_all_questions(3600)
    questions = data["problemsetQuestionList"]
    df = {
        "question_id": [],
        "title": [],
        "topics": [],
        "difficulty": []
    }

    for q in questions:
        df["question_id"].append(q["questionFrontendId"])
        df["title"].append(q["titleSlug"])
        df["topics"].append(list(map(lambda x: x["slug"], q["topicTags"])))
        df["difficulty"].append(q["difficulty"])
    
    pd.DataFrame(df).to_csv("data/questions.csv", index=False)


if __name__=="__main__":
    main()
