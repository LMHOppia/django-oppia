# Helper script to extract the quiz and question ids from json quiz contents
# Specifically to help do the mapping for: https://github.com/LMHOppia/django-oppia/blob/release-0-12-22/activitylog/management/commands/fix_incorrect_cebs_covid_logs_2021_11.py
import json

input_original = ''
input_new = ''

json_original = json.loads(input_original)
json_new = json.loads(input_new)

print("\nQuiz ID mapping")
print("%d: %d,  # %s" % (json_original['id'], json_new['id'], json_original['title']['en']))

print("\nQuestion ID mapping")
print("# %s" % json_original['title']['en'])
for question in json_original['questions']:
    original_id = question['id']
    original_title = question['question']['title']['en']
    new_id = 0
    for new_q in json_new['questions']:
        if new_q['question']['title']['en'] == original_title:
            new_id = new_q['id']
    print("%d: %d,  # %s" % (original_id, new_id, original_title))
    
    
    