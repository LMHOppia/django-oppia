import fnmatch
import os
import time
import json

from django.core.management.base import BaseCommand

from activitylog.views import process_activitylog
from helpers.messages import MessagesDelegate


class Command(BaseCommand):
    help = 'Script to fix the activitylog quiz ids, puts the fixed files ' + \
           'into  a new folder "fixed" under the provided source directory'
    
    QUIZ_ID_MAPPING = {
        0: 0,
        }
        
    QUESTION_ID_MAPPING = {
        0: 0,
        }
    
    def add_arguments(self, parser):

        parser.add_argument(
            'source', type=str,
            help='Source folder that contains the activity log JSON files to process',
        )
    
    def get_files(self, path):
        if not os.path.exists(path):
            print('Error: File "{}" does not exist'.format(path))
            return False

        if not os.path.isdir(path):
            print('Error: "{}" is not a directory'.format(path))
            return False

        if not os.access(path, os.R_OK):
            print('Error: You don\'t have read permission to access "{}"'.format(path))
            return False

        jsonfiles = [f for f in os.listdir(path) if
                     os.path.isfile(os.path.join(path, f)) and fnmatch.fnmatch(f, '*.json')]

        if len(jsonfiles) == 0:
            print('Source folder does not contain any JSON file')


        return jsonfiles
       
    def handle(self, *args, **options):
        sourcedir = options['source']
        jsonfiles = self.get_files(sourcedir)

        if not jsonfiles:
            exit(-1)
            
        start_time = time.time()
        for jsonfile in jsonfiles:
            filename = os.path.join(sourcedir, jsonfile)
            print ('Processing {}:'.format(filename))
            with open(filename, 'r') as file:
                file_data = file.read()
            
            json_data = json.loads(file_data)  
            for user in json_data['users']:
                for quizresponse in user['quizresponses']:
                    if quizresponse['quiz_id'] in self.QUIZ_ID_MAPPING:
                        quizresponse['quiz_id'] = self.QUIZ_ID_MAPPING[quizresponse['quiz_id']]
                        for response in quizresponse['responses']:
                            if response['question_id'] in self.QUESTION_ID_MAPPING:
                                response['question_id'] = self.QUESTION_ID_MAPPING[response['question_id']]

            fixed_filename = jsonfile.replace(".json", "-fixed.json")
            out_file = open(os.path.join(sourcedir, "fixed", fixed_filename), "w")

            json.dump(json_data, out_file, indent = 3)

            out_file.close()        
        
        print("Process finished. Time taken: %s seconds" % (time.time() - start_time))
        