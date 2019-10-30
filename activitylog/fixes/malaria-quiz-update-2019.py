'''

Script to fix quiz and question ids in the downloaded activity log files, so they match the ids stored on the server

ID mapping:

quiz_id
580 (file) => 11 (server)

question_id 
123 (file) => 66 (server)
762 (file) => 67 (server)
855 (file) => 68 (server)
726 (file) => 69 (server)
198 (file) => 70 (server)
904 (file) => 71 (server)
435 (file) => 72 (server)

'''
import json
import os 
import argparse

def run(path): 

    # scan the provided folder
    try:
        files = os.listdir(path)
    except OSError:
        print("Path not found, please check the path is correct.")
        return
    
    # create folder for storing the updated files
    if not os.path.exists(os.path.join(path, 'processed')):
        os.makedirs(os.path.join(path, 'processed'))
    
    
    for file in files:
        # for each json file load this in and update the ids
        if os.path.isfile(os.path.join(path, file)):
            print("Processing: " + file)
            
            with open(os.path.join(path, file), "r") as content:
                json_obj = json.load(content)
            
            # for local testing only - replace the server name
            #json_obj['server'] = 'http://localhost:8000/'
            
            for user in json_obj['users']:
                print("Processing user: " + user['username'])      
                
                # process quizzes
                for quiz_response in user['quizresponses']:
                    if quiz_response["quiz_id"] == 580:
                        quiz_response["quiz_id"]=11
                        
                    for response in quiz_response['responses']:
                        if response["question_id"] == 123:
                            response["question_id"]=66
                        if response["question_id"] == 762:
                            response["question_id"]=67
                        if response["question_id"] == 855:
                            response["question_id"]=68
                        if response["question_id"] == 726:
                            response["question_id"]=69
                        if response["question_id"] == 198:
                            response["question_id"]=70
                        if response["question_id"] == 904:
                            response["question_id"]=71
                        if response["question_id"] == 435:
                            response["question_id"]=72
                        
            # save file to update folder
            with open(os.path.join(path, 'processed', file.replace('.json','-processed.json')), 'w') as f:
                json.dump(json_obj, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Full path to the folder to scan for activity log files")
    args = parser.parse_args()
    run(args.path)  
