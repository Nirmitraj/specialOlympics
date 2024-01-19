import csv
import pandas as pd
import os
from django.conf import settings
# from django.core.management.base import BaseCommand
from analytics.models import SchoolDetails

class Command():
    def clean_school_name(self,data):
        #school name #countyname # UD_locale
        if data == -99 or type(data)==int:
            return None
        else:
            return data

    def number_bool(self,data,val = None):
        if data =='#NULL!':
            return None
        elif float(data) == 1 :
            return True
        elif float(data) == 0:
            return False
        else:
            return None
    
    def clean_str_null(self,data):
        #sportcompnent #youthleadership #wholeschool
        #localeNum #enrollment #free lunch #non white #implementation level
        if data == '#NULL!':
            return None
        else: return data

    def clean_str_zip_null(self,data):
        #sportcompnent #youthleadership #wholeschool
        #localeNum #enrollment #free lunch #non white #implementation level
        if data == '#NULL!':
            return None
        elif data == '':
            return -99
        else: return data
    
    def clean_str_implementation_level_null(self,data):
        #sportcompnent #youthleadership #wholeschool
        #localeNum #enrollment #free lunch #non white #implementation level
        if data == '#NULL!':
            return None
        elif data == '':
            return -99
        elif data == 'NA':
            return None
        elif data == 'Emerging': 
            return '1'
        elif data == 'Developing': 
            return '2'
        elif data == 'Full-implementation':
            return '3'
        else:
            return None
    
    def clean_str_grade_level_null(self,data):
        if data == '#NULL!':
            return None
        elif data == '':
            return -99
        elif data == 'NA':
            return None
        elif data == 'Elementary': 
            return '1.00'
        elif data == 'High': 
            return '2.00'
        elif data == 'Middle':
            return '3.00'
        elif data == 'Preschool':
             return '4.00'
        else:
            return None
    

    def handle(self, *args, **kwargs):
        datafile = os.path.join(settings.BASE_DIR,'excel_data/Y15_Dataset.csv') 

        with open(datafile, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile) #islice(csvfile, None, 51))
            for row in reader:
                print(row)
                SchoolDetails.objects.get_or_create(
                school_ID=row['NCESID'],#all
                school_name=self.clean_school_name(row['UD_SchoolName']),#all
                school_state=row['UD_StateProgram'],#all
                locale_number=self.clean_str_null(row['UD_LocaleNum']),#all
                gradeLevel_WithPreschool=self.clean_str_grade_level_null(row['Y15_GradeLevel']),#12
                implementation_level=self.clean_str_implementation_level_null(row['Y15_ImplementationLevel']),#12345
                locale=self.clean_school_name(row['UD_Locale']),#all
                school_county=row['UD_CountyName'],#all
                state_abv=row['UD_StateABV'],#all  
                student_enrollment_range=None,#self.clean_str_null(row['Y14_Enrollment_CAT']),#1
                student_free_reduced_lunch=None,#self.clean_str_null(row['Y14_FreeReducedLunch_CAT']),#1
                student_nonwhite_population=None,#self.clean_str_null(row['Y13_NONWHITE_CAT2']),#12
                survey_taken=self.number_bool(row['Y15_data']),#all
                unified_sports_component=self.number_bool(row['Y15_UnifiedSportsComponent']),#1235
                youth_leadership_component=self.number_bool(row['Y15_YouthLeadershipComponent']),#1235
                whole_school_component=self.number_bool(row['Y15_WholeSchoolComponent']),#1235
                zipcode=self.clean_str_zip_null(row['UD_ZIP']),#all
                survey_taken_year=2023,
                sports_sports_teams =self.clean_str_null(row['Y15_C1_1_dichot']),#13
                sports_unified_PE=self.clean_str_null(row['Y15_C1_2_dichot']),#13
                sports_unified_fitness=self.clean_str_null(row['Y15_C1_3_dichot']),#13
                sports_unified_esports=self.clean_str_null(row['Y15_C1_4_dichot']),#1
                sports_young_athletes=self.clean_str_null(row['Y15_C1_5_dichot']),#13
                sports_unified_developmental_sports=self.clean_str_null(row['Y15_C1_6_dichot']),#13
                leadership_unified_inclusive_club=self.clean_str_null(row['Y15_D1_1_dichot']),#13
                leadership_youth_training=self.clean_str_null(row['Y15_D1_2_dichot']),#13
                leadership_athletes_volunteer=self.clean_str_null(row['Y15_D1_3_dichot']),#13
                leadership_youth_summit=self.clean_str_null(row['Y15_D1_4_dichot']),#13
                leadership_activation_committe=self.clean_str_null(row['Y15_D1_5_dichot']),#13
                engagement_spread_word_campaign=self.clean_str_null(row['Y15_E_1_dichot']),#123
                engagement_fansinstands=self.clean_str_null(row['Y15_E_2_dichot']),#123
                engagement_sports_day=self.clean_str_null(row['Y15_E_3_dichot']),#123
                engagement_fundraisingevent=self.clean_str_null(row['Y15_E_4_dichot']),#123
                engagement_SO_play=self.clean_str_null(row['Y15_E_5_dichot']),#123
                engagement_fitness_challenge=self.clean_str_null(row['Y15_E_6_dichot']),#123
                special_education_teachers=self.clean_str_null(row['Y15_F3_1']),#123
                general_education_teachers=self.clean_str_null(row['Y15_F3_2']),#123
                physical_education_teachers=self.clean_str_null(row['Y15_F3_3']),#123
                adapted_pe_teachers=self.clean_str_null(row['Y15_F3_4']),#123
                athletic_director=self.clean_str_null(row['Y15_F3_5']),#123
                students_with_idd=self.clean_str_null(row['Y15_F3_6']),#123
                students_without_idd=self.clean_str_null(row['Y15_F3_7']),#123
                school_administrators=self.clean_str_null(row['Y15_F3_8']),#123
                parents_of_students_with_idd=self.clean_str_null(row['Y15_F3_9']),#1
                parents_of_students_without_idd=self.clean_str_null(row['Y15_F3_10']),#1
                school_psychologist=self.clean_str_null(row['Y15_F3_11']),#123
                special_olympics_state_program_staff=self.clean_str_null(row['Y15_F3_12']),#123
                elementary_school_playbook=self.clean_str_null(row['G13_1']),#13
                middle_level_playbook=self.clean_str_null(row['G13_4']),#13
                high_school_playbook=self.clean_str_null(row['G13_5']),#13
                special_olympics_state_playbook=self.clean_str_null(row['G13_4']),#13
                special_olympics_fitness_guide_for_schools=self.clean_str_null(row['G13_2']),#13
                unified_physical_education_resource=self.clean_str_null(row['G13_7']),#13
                special_olympics_young_athletes_activity_guide=self.clean_str_null(row['G13_8']),#13
                inclusive_youth_leadership_training_faciliatator_guide=self.clean_str_null(row['G13_10']),#13
                planning_and_hosting_a_youth_leadership_experience=None,#self.clean_str_null(row['Y12_E9_10_1']),#13
                unified_classoom_lessons_and_activities=self.clean_str_null(row['G13_11']),#13
                generation_unified_youtube_channel_or_videos=self.clean_str_null(row['G13_12']),#13
                inclusion_tiles_game_or_facilitator_guide=self.clean_str_null(row['G13_13']),#13
                students_with_intellectual_disability=self.clean_str_null(row['Y15_L18_1_Recode']),#1
                students_without_intellectual_disability=self.clean_str_null(row['Y15_L18_2_Recode']),#1
                the_school_as_a_whole=self.clean_str_null(row['Y15_L19_Recode']),#13
                increase_in_understanding_language_of_disability=self.clean_str_null(row['Y15_L5_1_Recode']),#1
                increasing_confidence_of_students_with_idd=self.clean_str_null(row['Y15_L7_1_Recode']),#1
                opportunities_for_students_idd_to_work_together=self.clean_str_null(row['Y15_L4_1_Recode']),#1
                creating_a_more_socially_inclusive_school_environment=self.clean_str_null(row['Y15_L17_1_Recode']),#1
                raising_awareness_about_students_with_idd=self.clean_str_null(row['Y15_L9_1_Recode']),#1
                increasing_participation_of_students_with_idd=self.clean_str_null(row['Y15_L5_1_Recode']),#1
                reducing_bullying_teasing=self.clean_str_null(row['Y15_L14_1_Recode']),#1
                increasing_confidence_of_students_without_idd=self.clean_str_null(row['Y15_L8_1_Recode']),#1
                increasing_participation_of_students_without_idd=self.clean_str_null(row['Y15_L6_1_Recode']),#1
                increasing_attendance_of_students_with_idd=self.clean_str_null(row['Y15_L10_1_Recode']),#1
                reducing_disciplinary_referrals_for_students_with_idd=self.clean_str_null(row['Y15_L12_1_Recode']),#1
                increasing_attendance_of_students_without_idd=self.clean_str_null(row['Y15_L11_1_Recode']),#1
                reducing_disciplinary_referrals_for_students_without_idd=self.clean_str_null(row['Y15_L13_1_Recode'])#1
                )

    def test_values(self):

        datafile = os.path.join(settings.BASE_DIR,'excel_data/Y15_Dataset.csv') 

        with open(datafile, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile) #islice(csvfile, None, 51))
            for row in reader:
                print(row['NCESID'])

                
                # print(row['NCESID'])


    def test_values_pandas(self):

        datafile = os.path.join(settings.BASE_DIR,'excel_data/Y15_Dataset.csv') 
        reader=pd.read_excel(datafile)
        print(reader.shape)
        for i in range(reader.shape[0]):
            print(reader['NCESID'][i])
        #print(row['NCESID'])
                
call =  Command()
call.handle()
#call.test_values()

