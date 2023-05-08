import csv
import pandas as pd
import os
from django.conf import settings
#from django.core.management.base import BaseCommand
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
    

    def handle(self, *args, **kwargs):
        datafile = os.path.join(settings.BASE_DIR,'excel_data/server_upload_file_v1.csv') 

        with open(datafile, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile) #islice(csvfile, None, 51))
            for row in reader:
                print(row)
                SchoolDetails.objects.get_or_create(
                school_ID=row['NCESID'],#all
                school_name=self.clean_school_name(row['UD_SchooName']),#all
                school_state=row['UD_StateProgram'],#all
                locale_number=self.clean_str_null(row['UD_LocaleNum']),#all
                gradeLevel_WithPreschool=self.clean_str_null(row['Y14_GradeLevel_WithPreschool']),#12
                implementation_level=self.clean_str_null(row['Y14_ImplementationLevel']),#12345
                locale=self.clean_school_name(row['UD_Locale']),#all
                school_county=row['UD_CountyName'],#all
                state_abv=row['UD_StateABV'],#all  
                student_enrollment_range=self.clean_str_null(row['Y14_Enrollment_CAT']),#1
                student_free_reduced_lunch=self.clean_str_null(row['Y14_FreeReducedLunch_CAT']),#1
                student_nonwhite_population=self.clean_str_null(row['Y14_NONWHITE_CAT2']),#12
                survey_taken=self.number_bool(row['Y14_data']),#all
                unified_sports_component=self.number_bool(row['Y14_UnifiedSportsComponent']),#123
                youth_leadership_component=self.number_bool(row['Y14_YouthLeadershipComponent']),#123
                whole_school_component=self.number_bool(row['Y14_WholeSchoolComponent']),#123
                zipcode=row['UD_ZIP'],#all
                survey_taken_year=2022,
                sports_sports_teams =self.clean_str_null(row['Y14_C1_1_dichot']),#13
                sports_unified_PE=self.clean_str_null(row['Y14_C1_2_dichot']),#13
                sports_unified_fitness=self.clean_str_null(row['Y14_C1_3_dichot']),#13
                sports_unified_esports=self.clean_str_null(row['Y14_C1_4_dichot']),#1
                sports_young_athletes=self.clean_str_null(row['Y14_C1_5_dichot_AllSchoolLevels']),#13
                sports_unified_developmental_sports=self.clean_str_null(row['Y14_C1_6_dichot_AllSchoolLevels']),#13
                leadership_unified_inclusive_club=self.clean_str_null(row['Y14_D1_1_dichot']),#13
                leadership_youth_training=self.clean_str_null(row['Y14_D1_2_dichot']),#13
                leadership_athletes_volunteer=self.clean_str_null(row['Y14_D1_3_dichot']),#13
                leadership_youth_summit=self.clean_str_null(row['Y14_D1_4_dichot']),#13
                leadership_activation_committe=self.clean_str_null(row['Y14_D1_5_dichot']),#13
                engagement_spread_word_campaign=self.clean_str_null(row['Y14_E1_1_dichot']),#123
                engagement_fansinstands=self.clean_str_null(row['Y14_E1_2_dichot']),#123
                engagement_sports_day=self.clean_str_null(row['Y14_E1_3_dichot']),#123
                engagement_fundraisingevent=self.clean_str_null(row['Y14_E1_4_dichot']),#123
                engagement_SO_play=self.clean_str_null(row['Y14_E1_5_dichot']),#123
                engagement_fitness_challenge=self.clean_str_null(row['Y14_E1_6_dichot']),#123
                special_education_teachers=self.clean_str_null(row['Y14_F11_1']),#123
                general_education_teachers=self.clean_str_null(row['Y14_F11_2']),#123
                physical_education_teachers=self.clean_str_null(row['Y14_F11_3']),#123
                adapted_pe_teachers=self.clean_str_null(row['Y14_F11_4']),#123
                athletic_director=self.clean_str_null(row['Y14_F11_5']),#123
                students_with_idd=self.clean_str_null(row['Y14_F11_6']),#123
                students_without_idd=self.clean_str_null(row['Y14_F11_7']),#123
                school_administrators=self.clean_str_null(row['Y14_F11_8']),#123
                parents_of_students_with_idd=self.clean_str_null(row['Y14_F11_9']),#1
                parents_of_students_without_idd=self.clean_str_null(row['Y14_F11_10']),#1
                school_psychologist=self.clean_str_null(row['Y14_F11_11']),#123
                special_olympics_state_program_staff=self.clean_str_null(row['Y14_F11_12']),#123
                elementary_school_playbook=self.clean_str_null(row['Y14_G13_1']),#13
                middle_level_playbook=self.clean_str_null(row['Y14_G13_2']),#13
                high_school_playbook=self.clean_str_null(row['Y14_G13_3']),#13
                special_olympics_state_playbook=self.clean_str_null(row['Y14_G13_4']),#13
                special_olympics_fitness_guide_for_schools=self.clean_str_null(row['Y14_G13_5']),#13
                unified_physical_education_resource=self.clean_str_null(row['Y14_G13_6']),#13
                special_olympics_young_athletes_activity_guide=self.clean_str_null(row['Y14_G13_7']),#13
                inclusive_youth_leadership_training_faciliatator_guide=self.clean_str_null(row['Y14_G13_8']),#13
                planning_and_hosting_a_youth_leadership_experience=self.clean_str_null(row['Y14_G13_9']),#13
                unified_classoom_lessons_and_activities=self.clean_str_null(row['Y14_G13_10']),#13
                generation_unified_youtube_channel_or_videos=self.clean_str_null(row['Y14_G13_11']),#13
                inclusion_tiles_game_or_facilitator_guide=self.clean_str_null(row['Y14_G13_12']),#13
                students_with_intellectual_disability=self.clean_str_null(row['Y14_M15_1_Recode']),#1
                students_without_intellectual_disability=self.clean_str_null(row['Y14_M16_1_Recode']),#1
                the_school_as_a_whole=self.clean_str_null(row['Y14_M17_1_Recode']),#1
                increase_in_understanding_language_of_disability=self.clean_str_null(row['Y14_M14_1_Recode']),#1
                increasing_confidence_of_students_with_idd=self.clean_str_null(row['Y14_M5_1_Recode']),#1
                opportunities_for_students_idd_to_work_together=self.clean_str_null(row['Y14_M1_1_Recode']),#1
                creating_a_more_socially_inclusive_school_environment=self.clean_str_null(row['Y14_M12_1_Recode']),#1
                raising_awareness_about_students_with_idd=self.clean_str_null(row['Y14_M7_1_Recode']),#1
                increasing_participation_of_students_with_idd=self.clean_str_null(row['Y14_M3_1_Recode']),#1
                reducing_bullying_teasing=self.clean_str_null(row['Y14_M13_1_Recode']),#1
                increasing_confidence_of_students_without_idd=self.clean_str_null(row['Y14_M6_1_Recode']),#1
                increasing_participation_of_students_without_idd=self.clean_str_null(row['Y14_M4_1_Recode']),#1
                increasing_attendance_of_students_with_idd=self.clean_str_null(row['Y14_M8_1_Recode']),#1
                reducing_disciplinary_referrals_for_students_with_idd=self.clean_str_null(row['Y14_M10_1_Recode']),#1
                increasing_attendance_of_students_without_idd=self.clean_str_null(row['Y14_M9_1_Recode']),#1
                reducing_disciplinary_referrals_for_students_without_idd=self.clean_str_null(row['Y14_M11_1_Recode'])#1
                )

    def test_values(self):

        datafile = os.path.join(settings.BASE_DIR,'excel_data/server_upload_file_v1.csv') 

        with open(datafile, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile) #islice(csvfile, None, 51))
            for row in reader:
                print(row['NCESID'])

                
                # print(row['NCESID'])


    def test_values_pandas(self):

        datafile = os.path.join(settings.BASE_DIR,'excel_data/server_upload_file_v1___.xlsx') 
        reader=pd.read_excel(datafile)
        print(reader.shape)
        for i in range(reader.shape[0]):
            print(reader['NCESID'][i])
        #print(row['NCESID'])
                
call =  Command()
call.handle()
#call.test_values()