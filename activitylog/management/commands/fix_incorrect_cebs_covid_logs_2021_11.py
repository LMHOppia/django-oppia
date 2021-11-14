import fnmatch
import os
import time
import json

from django.core.management.base import BaseCommand

from activitylog.views import process_activitylog
from helpers.messages import MessagesDelegate


class Command(BaseCommand):
    help = 'Script to fix the activitylog quiz ids, puts the fixed files ' + \
           'into  a new folder "fixed" under the provided source directory' + \
           ' - this script is only relevant/useful for the CEBS course in Liberia'
    
    QUIZ_ID_MAPPING = {
        47: 34,  # Pre-Training Knowledge Assessment
        48: 35,  # Pre-Training Survey for Learners
        35: 36,  # Section 1: Prevention of Coronavirus (COVID-19)
        36: 37,  # Section 2: Promoting Hygiene
        49: 38,  # Section 3: Personal Protective Equipment
        38: 39,  # Section 4: Case Detection
        39: 40,  # Section 5: Contact Tracing &amp; Reporting
        40: 41,  # Section 6: Maintaining Essential Health Services During COVID-19
        50: 42,  # Post-Training Knowledge Assessment
        51: 43,  # Post-Training Self-Efficacy Assessment
        }
        
    QUESTION_ID_MAPPING = {
        # Pre-Training Knowledge Assessment
        586: 425,  # True or False: To prevent the spread of COVID-19, wear a mask that covers your nose and mouth when you are around other people"
        587: 426,  # How long should you wash your hands with soap and water?
        588: 427,  # Select all of the things CHAs should do while wearing PPE
        589: 428,  # Select all of the things a CHA should do during COVID-19 patient monitoring"
        590: 429,  # True or False: The community trigger and referral form should be used to report community triggers for COVID-19 as well as other surveillance diseases
        591: 430,  # Who does not need to wear a mask when around other people?
        592: 431,  # If a patient is a COVID-19 trigger and has a danger sign, what should the CHA do?

        # Pre-Training Survey for Learners
        593: 432,  # Age Range:
        594: 433,  # Please state your level of agreement with the following statements: Coronavirus (COVID-19) is an issue in my community
        595: 434,  # Coronavirus (COVID-19) affects my day to day work
        596: 435,  # I think it is important to follow measures to prevent the spread of coronavirus (COVID-19) including social distancing, wearing a mask, and frequent handwashing
        597: 436,  # How often do you use the Community Health Academy App?
        598: 437,  # Select all of the statements about the Community Health Academy App you agree with

        
        # Section 1: Prevention of Coronavirus (COVID-19)
        453: 438,  # Who can get COVID-19?
        454: 439,  # True or False: COVID-19 does not spread easily and never leads to serious sickness
        455: 440,  # What are the most common symptoms of COVID-19?
        456: 441,  # True or False: You can spread COVID-19 even if you do not feel sick
        457: 442,  # COVID-19 is spread in all of the following ways EXCEPT:
        458: 443,  # True or False: To help prevent the spread of COVID-19, wash your hands often with soap and clean water or use hand sanitizer
        459: 444,  # True or False: To prevent getting COVID-19 avoid touching your face
        460: 445,  # True or False: To prevent COVID-19, stay at least 6 feet away from people
        461: 446,  # True or False: To prevent the spread of COVID-19, avoid places with many people
        462: 447,  # True or False: To prevent the spread of COVID-19, drink hot liquid
        463: 448,  # True or False: To prevent the spread of COVID-19, eat garlic
        464: 449,  # True or False: Providing the correct information to community members to increase their knowledge and understanding about the spread of the disease is a responsibility of the CHA.
        465: 450,  # True or False: Women and youth should be included in the development of the community action plan
        466: 451,  # True or False: When talking to the community members about COVID-19 a CHA should ask them about their COVID-19 beliefs.
        467: 452,  # When should a CHA work with community leaders to develop an action plan?
        468: 453,  # True or False: A CHA should tell the community that everything they hear about COVID-19 is true.
        469: 454,  # A CHA should support their community's mental health by doing all of the following EXCEPT:
        470: 455,  # True or False: It is ok to ignore social distancing if you are providing mental health support.
        471: 456,  # True or False: One of the most powerful tools CHAs can use against stigma is to share facts about COVID-19.
        472: 457,  # True or False: A CHA is responsible for helping the community create an action plan for COVID-19 and for helping the community follow the plan once it is made
        473: 458,  # True or False: A community action plan for COVID-19 should only include the roles and responsibilities of community leaders. Guidance on actions that households can take should not be included.

        
        # Section 2: Promoting Hygiene
        474: 459,  # When should CHAs wash their hands?
        475: 460,  # True or False: People should wash their hands before and after they eat
        476: 461,  # True or False: CHA's should work with Community Health Committees to make sure there are handwashing stations
        477: 462,  # True or False: Only sick people need to wash their hands frequently.
        478: 463,  # True or False: Handwashing stations should be located in a public place so everyone in the community can access them

        
        # Section 3: Personal Protective Equipment
        599: 464,  # What is personal protective equipment (PPE)?
        600: 465,  # True or False: People should wash their hands before and after they eat
        601: 466,  # True or False: If you are working as a CHA, you only need to wear a mask if you are less than 6 feet from other people
        602: 467,  # If a CHA is ever within 6 feet of a patient in order to provide RDT, Sayana Press, MUAC, or to take a temperature, what PPE should they wear?
        603: 468,  # What order should you do things when putting on PPE? (1 is first, 4 is last)
        604: 469,  # True or False: Medical face masks that have been worn should be thrown away at the end of each day in a biohazard trash bag.
        605: 470,  # True or False: When taking off PPE the CHA should follow the below listed steps:Remove glovesWash handsRemove face shield/goggles Wash handsRemove maskWash hands
        606: 471,  # True or False: If gloves are needed, CHAs should wear a new set for each patient.

        
        # Section 4: Case Detection
        487: 472,  # True or False: A person who has travelled from an outbreak area with fever is a COVID-19 trigger.
        488: 473,  # True or False: A person who has not travelled from an outbreak area and has fever, cough and shortness of breath is a COVID-19 trigger.
        489: 474,  # True or False: A person who has not travelled to an outbreak area and does not have fever BUT has cough and tiredness is a COVID-19 trigger.
        490: 475,  # True or False: If a CHA does not have a Thermoflash, they should touch the person's forehead to see if it is warm to determine if they have a fever.
        491: 476,  # When using Thermoflash, what is the lowest temperature that can be a fever?
        492: 477,  # What is the best way to use the Thermoflash?
        493: 478,  # As a CHA, when a community trigger for COVID-19 has been identified, who do you notify?
        494: 479,  # When do you report a trigger of COVID-19 in the community?
        495: 480,  # Which of the following would be the best caregiver for a COVID-19 patient isolating at home?
        496: 481,  # [MULTIPLE] Select all of the topics a CHA should discuss with a family of a COVID-19 trigger when creating a home isolation plan:
        497: 482,  # How often should a CHA monitor a suspected case while awaiting the surveillance team to investigate?
        498: 483,  # [MULTIPLE] Select all of the things a CHA should do when there is a suspected COVID-19 case in the community:
        499: 484,  # True or False: The identified caregiver for a trigger should always wear a mask when within 6 feet of the trigger.

        
        # Section 5: Contact Tracing &amp; Reporting
        500: 485,  # CHW CEBS reporting tools include all of the following EXCEPT
        501: 486,  # True or False: The COVID-19 Primary Alert Screening Form should be completed on a weekly basis
        502: 487,  # True or False: The Weekly Alert Notification Form is used to report ALL community triggers (not just COVID-19) on a weekly basis
        503: 488,  # In what order should a CHA complete the following contract tracing steps? (1 is first 5 is last)
        504: 489,  # True or False: A CHA does not need to conduct a daily check of a community trigger contact if they do not show symptoms of COVID-19 for seven days
        505: 490,  # True or False: A contact for COVID-19 is someone who came closer than 6 feet to a person who was sick and tested positive for COVID-19 or a person that meets trigger definition.
        506: 491,  # A CHA should visit a contact for COVID-19 for....
        507: 492,  # True or False: When following up with COVID-19 contacts, the CHA should start with the contacts they have not reached yet
        508: 493,  # True or False: It is not necessary to fill out a new trigger form if a COVID-19 contact develops COVID-19 symptoms because their information has already been listed on the contact listing form.
        509: 494,  # When CHAs discuss contact tracing with the community, they should discuss all of the following EXCEPT

        
        # Section 6: Maintaining Essential Health Services During COVID-19
        510: 495,  # How far apart should a CHA be standing from people when providing counseling?
        511: 496,  # True or False: You can enter the home of a patient if they are not coughing to provide routine services.
        512: 497,  # When should you screen yourself for symptoms of COVID-19?
        513: 498,  # True or False: CHAs should continue to provide routine services for malaria, pneumonia, diarrhea, malnutrition, and family planning during COVID-19
        514: 499,  # True or False: A CHA does not need to wear a mask when providing services if the person does not show symptoms of COVID-19
        515: 500,  # Who should be screened for COVID-19 before providing routine services?
        516: 501,  # True or False: It is safe to use a MUAC strip if there is a COVID-19 trigger in the household as long as the CHA wears proper PPE and cleans the strip before the next patient.
        517: 502,  # What is the best way to check for feet swelling in a baby during this COVID-19 time?
        518: 503,  # If a patient is a COVID-19 trigger, but also has a fever what should a CHA do?
        519: 504,  # To check for chest indrawing during COVID-19:
        520: 505,  # During COVID-19, what is the BEST way to provide medicine to sick children (assuming the CHA has the medicine in-stock)?
        521: 506,  # True or False: A child with fever and cough is a COVID-19 trigger.
        522: 507,  # The treatment for diarrhea without danger sign is:
        523: 508,  # True or False: A child can have both diarrhea and COVID-19
        524: 509,  # True or False: All injectable forms of family planning must stop during COVID-19
        525: 510,  # True or False: If a woman is a trigger or contact of a trigger and she wants to continue using an injectable family planning method, she can use condoms as a backup method until she is no longer in home isolation and can safely be given the injection.
        526: 511,  # True or False: During the follow up visit, everyone in the household should be re-screened for COVID-19.
        527: 512,  # If a patient that is a COVID-19 trigger is not recovering or has a danger sign, the CHA should recommend the patient continue to isolate at home.
        528: 513,  # True or False: If a CHA is within 6 feet of a patient during service delivery they should wear a face shield or goggles in addition to a mask.
        529: 514,  # True or False: You should give COVID-19 triggers and their caregiver a medical mask from your CHA supply if they do not have one
        530: 515,  # True or False: If a sick child is living with a COVID-19 trigger, you can take their temperature with thermoflash as long as the COVID-19 trigger is in the house and you are outside.

        
        # Post-Training Knowledge Assessment
        607: 516,  # True or False: To prevent the spread of COVID-19, wear a mask that covers your nose and mouth when you are around other people
        608: 517,  # How long should you wash your hands with soap and water?
        609: 518,  # [MULTIPLE] Select all of the things CHAs should do while wearing PPE
        610: 519,  # [MULTIPLE] Select all of the things a CHA should do during COVID-19 patient monitoring
        611: 520,  # True or False: The community trigger and referral form should be used to report community triggers for COVID-19 as well as other surveillance diseases
        612: 521,  # Who does not need to wear a mask when around other people?
        613: 522,  # If a patient is a COVID-19 trigger and has a danger sign, what should the CHA do
        
        # Post-Training Self-Efficacy Assessment
        614: 523,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Conduct coronavirus (COVID-19) community awareness and engagement activities
        615: 524,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Communicate coronavirus (COVID-19) infection prevention and control (IPC) measures to community members
        616: 525,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Follow IPC protocols during the coronavirus (COVID-19) pandemic
        617: 526,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Correctly put on and take off PPE based on the situation
        618: 527,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Identify and follow-up trigger, suspected, and confirmed coronavirus (COVID-19) cases as outlined in the training
        619: 528,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Set up isolation place and monitor coronavirus (COVID-19) trigger until supervisor/ clinic staff arrives
        620: 529,  # Following this training, are you able to properly provide the following community-based services for coronavirus (COVID-19)?: Counsel community members on the benefits, risks, and side effects of COVID-19 vaccines.
        621: 530,  # How much new information did you learn in this training?
        622: 531,  # Please indicate your level of agreement with the following statements: Having the videos from the training on my device will help me to do my job
        623: 532,  # Overall, I was satisfied with the quality of this training
        624: 533,  # Which of the following helped you understand the information presented in the training the most?
        625: 534,  # Which of the following will be the most useful in helping you to correctly implement the information covered in the training?
        626: 535,  # Did you experience any of the following challenges with this training?
        627: 536,  # What did you like most about this training?
        628: 537,  # What areas of the training do you think could be improved?
        
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
            json.dump(json_data, out_file, indent = 2)
            out_file.close()        
        
        print("Process finished. Time taken: %s seconds" % (time.time() - start_time))
        