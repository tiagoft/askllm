import pandas as pd
import json
from tqdm import tqdm

def ingest():
    with open("results.json", "r") as f:
        data = json.load(f)
        all_entries = []
        for key in tqdm(data.keys()):
            this_entry = {}
            school = key.split("/")[5]
            filename = key.split("/")[-1]
            this_entry["school"] = school
            this_entry["filename"] = filename
            for qnum in range(1,10):
                question = f"Q{qnum}"
                qdata = data[key].get(question, None)
                if qdata is not None:
                    if qdata['answer'] is not None:
                        this_entry[question] = qdata['answer']
            all_entries.append(this_entry)
                
            
    df = pd.DataFrame(all_entries)
    for qnum in range(1, 10):
        question = f"Q{qnum}"
        if question in df.columns:
            df[question] = df[question].astype(bool)
    return df

def view_results(df: pd.DataFrame):
    questions = [col for col in df.columns if col.startswith("Q")]
    df_filtered = df[df['Q1'] == True]
    df_schools = df_filtered.groupby('school')[questions].mean()
    df_schools['N'] = df_filtered.groupby('school').size()
    return df_schools
    
def main():
    df = ingest()
    print(view_results(df))
    

if __name__ == "__main__":
    main()