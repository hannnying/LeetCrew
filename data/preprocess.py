import ast
import os
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def encode_topics(df):
    # Convert string representation of list to actual list if necessary
    df["topics"] = df["topics"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    mlb = MultiLabelBinarizer()
    topic_encoded = mlb.fit_transform(df["topics"])

    # Create a new DataFrame with one column per topic
    topic_df = pd.DataFrame(topic_encoded, columns=mlb.classes_, index=df.index)

    # Concatenate back with original dataframe (optional)
    df = pd.concat([df, topic_df], axis=1)

    return df


if __name__=="__main__":
    path = os.path.join(os.getcwd(), "questions.csv")
    df = pd.read_csv(path)
    encode_topics(df).to_csv(path, index=True)

    print("Encoded question topics")


