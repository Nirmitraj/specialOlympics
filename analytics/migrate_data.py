import csv
import pandas as pd
import sys

import os
import django
from django.conf import settings
from django.db.models import Count

# from django.core.management.base import BaseCommand

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'specialolympics.settings')
django.setup()

from analytics.models import SchoolDetails

class Command():
    def clean_school_name(self,data):
        #school name #countyname # UD_locale
        if data == -99 or type(data)==int:
            return None
        elif data == '#N/A':
            return None
        else:
            return data

    def number_bool(self,data,val = None):
        if data =='#NULL!':
            return None
        elif data == '#N/A':
            return None
        elif data == '':
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
        print("data", data)
        if data == '#NULL!':
            return None
        elif data == '#N/A':
            return None
        elif data == 'n/a':
            return None
        elif data == '':
            return None
        else: 
            print("else data", data)
            return data

    def clean_str_zip_null(self,data):
        #sportcompnent #youthleadership #wholeschool
        #localeNum #enrollment #free lunch #non white #implementation level
        if data == '#NULL!':
            return -99
        elif data == '#N/A':
            return -99
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
        elif data == '#N/A':
            return None
        elif data == 'Emerging': 
            return '1'
        elif data == 'Developing': 
            return '2'
        elif data == 'Full-implementation':
            return '3'
        # elif data == 1:
        #     return '1'
        # elif data == 2:
        #     return '2'
        # elif data == 3:
        #     return '3'
        else:
            return data
    
    def clean_str_grade_level_null(self,data):
        if data == '#NULL!':
            return None
        elif data == '':
            return -99
        elif data == 'NA':
            return None
        elif data == '#N/A':
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
        


                # elementary_school_playbook=self.clean_str_null(row['G13_1']),#13
                # middle_level_playbook=self.clean_str_null(row['G13_4']),#13
                # high_school_playbook=self.clean_str_null(row['G13_5']),#13
                # special_olympics_state_playbook=self.clean_str_null(row['G13_4']),#13
                # special_olympics_fitness_guide_for_schools=self.clean_str_null(row['G13_2']),#13
                # unified_physical_education_resource=self.clean_str_null(row['G13_7']),#13
                # special_olympics_young_athletes_activity_guide=self.clean_str_null(row['G13_8']),#13
                # inclusive_youth_leadership_training_faciliatator_guide=self.clean_str_null(row['G13_10']),#13

    def clean_SONA_playbook_null(self, data):
        if data is None:
            return None
        elif str(data) == 'NA':
            return None
        elif str(data) == '#N/A':
            return None
        elif str(data) == '-99':
            return '0'
        elif str(data) == '0':
            return '0'
        else: 
            return '1'
    
    def calculate_free_reduced_lunch(self, free_lunch, reduced_lunch):
        try:
            free_lunch = float(free_lunch) if free_lunch is not None else 0
            reduced_lunch = float(reduced_lunch) if reduced_lunch is not None else 0
            return str(free_lunch + reduced_lunch) if free_lunch or reduced_lunch else None
        except ValueError:
            return None
    
    def calculate_student_nonwhite_population(self, *args):
        nonwhite_population = 0
        print("Non white", args)
        for population in args:
            if population is not None and population != '':

                nonwhite_population += float(population)
        if nonwhite_population == 0:
            return None
        else:
            return nonwhite_population
    
    def clean_up_duplicates():
        duplicates = SchoolDetails.objects.values('school_ID', 'survey_taken_year').annotate(count=Count('auto_increment_id')).filter(count__gt=1)
        
        for duplicate in duplicates:
            records = SchoolDetails.objects.filter(school_ID=duplicate['school_ID'], survey_taken_year=duplicate['survey_taken_year'])
            records_to_delete = records[1:]  # Keep the first record and delete the rest
            for record in records_to_delete:
                record.delete()
    if __name__ == "__main__":
        clean_up_duplicates()

    def handle(self, *args, **kwargs):
        datafile = os.path.join(settings.BASE_DIR,'excel_data/Copy_Y15_Dataset_for_Dashboard_Team_Master.csv') 
        # self.clean_up_duplicates()

        with open(datafile, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile) #islice(csvfile, None, 51))
            for row in reader:
                # print(row)
                # print(row['auto_increment_id'])

                # row['NCESID']
                # free_lunch = self.clean_str_null(row['UD_FreeLunch'])
                # reduced_lunch = self.clean_str_null(row['UD_ReducedLunch'])
                # student_free_reduced_lunch = self.calculate_free_reduced_lunch(free_lunch, reduced_lunch)
                # Convert to float and add, if both are not None
                # state_abv = row.get('state_abv')  # Ensure you have this key in your data
                # print(row['Y9_NumComponents'])
                # if not state_abv:
                #     print(f"Skipping row with NCESID because state_abv is null.")
                #     continue
                SchoolDetails.objects.update_or_create(
                school_ID=row['NCESID'],#all

                # survey_taken_year=2023,
                # The above code snippet is defining a dictionary named `defaults` with key-value
                # pairs representing fields to update. The commented-out lines suggest that there are
                # additional fields that can be updated. The keys in the dictionary represent the
                # field names, and the values are function calls to clean and extract data from
                # specific columns in a row. The `clean_str_null` and `clean_str_zip_null` functions
                # are likely used to handle null values and clean up string data before updating the
                # fields.
                defaults={  # the fields to update
                    
                # #     'unified_sports_component':self.number_bool(row['Y11_InclusiveSportsComponent']),#1235
                # #     'youth_leadership_component':self.number_bool(row['Y11_YouthLeadershipComponent']),#1235
                # #     'whole_school_component':self.number_bool(row['Y11_WholeSchoolComponent']),#1235
                         'num_components': self.clean_str_null(row['Y15_NumComponents']),
                        #   'school_state': row['UD_StateProgram'],#all
                        'school_county': self.clean_str_null(row['UD_CountyName']),#all
                        'state_abv': row['UD_StateABV'],#all  
                        'zipcode': self.clean_str_zip_null(row['UD_ZIP']),


# UD_StateABV
                # #     # add more fields here...
                },
                school_name=self.clean_school_name(row['UD_SchoolName']),#all
                # school_state=row['UD_StateProgram'],#all
                locale_number=self.clean_str_null(row['UD_LocaleNum']),#all
                # gradeLevel_WithPreschool=self.clean_str_grade_level_null(row['UD_GradeLevel']),#12
                implementation_level= self.clean_str_implementation_level_null(row['Y9_ImplementationLevel']),#12345
                #locale=self.clean_school_name(row['UD_Locale']),#all
                #school_county=row['UD_CountyName'],#all
                #state_abv=row['UD_StateABV'],#all  
                # student_enrollment_range=self.clean_str_null(row['UD_Students']),#1
                
                # student_free_reduced_lunch = student_free_reduced_lunch,
                # student_nonwhite_population = self.calculate_student_nonwhite_population(
                #             self.clean_str_null(row['UD_AmericanIndianAlaskaNativeStudentsPublicSchool201819']),
                #             self.clean_str_null(row['UD_AsianorAsianPacificIslanderStudentsPublicSchool201819']),
                #             self.clean_str_null(row['UD_HispanicStudentsPublicSchool201819']),
                #             self.clean_str_null(row['UD_BlackStudentsPublicSchool201819']),
                #             self.clean_str_null(row['UD_HawaiianNat.PacificIsl.StudentsPublicSchool201819']),
                #             self.clean_str_null(row['UD_TwoorMoreRacesStudentsPublicSchool201819'])
                #         ),#12

                # survey_taken=self.number_bool(row['Y15_data']),#all
                # unified_sports_component= self.number_bool(row['Y15_InclusiveSportsComponent']),#1235
                # youth_leadership_component= self.number_bool(row['Y15_YouthLeadershipComponent']),#1235
                # whole_school_component= self.number_bool(row['Y15_WholeSchoolComponent']),#1235
                # zipcode=self.clean_str_zip_null(row['UD_ZIP']),#all
                survey_taken_year=2023,

                # sports_sports_teams =self.clean_str_null(row['Y15_b1.a_dichot']),#13
                # sports_unified_PE=self.clean_str_null(row['Y15_b1.b_dichot']),#13
                # sports_unified_fitness= None, #self.clean_str_null(row['Y15_C1_3_dichot']),#13
                # sports_unified_esports= None,#self.clean_str_null(row['Y15_C1_4_dichot']),#1
                # sports_young_athletes=self.clean_str_null(row['Y9_b1.m_dichot']),#13
                # sports_unified_developmental_sports= None, #self.clean_str_null(row['Y15_C1_6_dichot']),#13


                # leadership_unified_inclusive_club=self.clean_str_null(row['Y9_b1.c_dichot']),#13
                # leadership_youth_training=None, #self.clean_str_null(row['Y15_D1_2_dichot']),#13
                # leadership_athletes_volunteer=self.clean_str_null(row['Y9_b1.l_dichot']),#13
                # leadership_youth_summit=self.clean_str_null(row['Y9_b1.e_dichot']),#13
                # leadership_activation_committe=self.clean_str_null(row['Y9_b1.e_dichot']),#13

                # engagement_spread_word_campaign=self.clean_str_null(row['Y9_b1.f_dichot']),#123
                # engagement_fansinstands=self.clean_str_null(row['Y9_b1.g_dichot']),#123
                # engagement_sports_day=self.clean_str_null(row['Y9_b1.h_dichot']),#123
                # engagement_fundraisingevent=self.clean_str_null(row['Y9_b1.i_dichot']),#123
                # engagement_SO_play=self.clean_str_null(row['Y9_b1.k_dichot']),#123
                # engagement_fitness_challenge=None, #self.clean_str_null(row['Y15_E_6_dichot']),#123

                # special_education_teachers=self.clean_SONA_playbook_null(row['Y9_f3_1']),#123
                # general_education_teachers=self.clean_SONA_playbook_null(row['Y9_f3_2']),#123
                # physical_education_teachers=self.clean_SONA_playbook_null(row['Y9_f3_3']),#123
                # adapted_pe_teachers=self.clean_SONA_playbook_null(row['Y9_f3_4']),#123
                # athletic_director=None, #self.clean_SONA_playbook_null(row['Y15_F3_5']),#123
                # students_with_idd=self.clean_SONA_playbook_null(row['Y9_f3_5']),#123
                # students_without_idd=self.clean_SONA_playbook_null(row['Y9_f3_6']),#123
                # school_administrators=self.clean_SONA_playbook_null(row['Y9_f3_7']),#123
                # parents_of_students_with_idd=self.clean_SONA_playbook_null(row['Y9_f3_8']),#1
                # parents_of_students_without_idd= None, #self.clean_SONA_playbook_null(row['Y15_F3_10']),#1
                # school_psychologist= None, #self.clean_SONA_playbook_null(row['Y15_F3_11']),#123
                # special_olympics_state_program_staff=self.clean_SONA_playbook_null(row['Y9_f3_9']),#123

                # elementary_school_playbook= None, #self.clean_SONA_playbook_null(row['G13_1']),#13
                # middle_level_playbook= None, #self.clean_SONA_playbook_null(row['G13_4']),#13
                # high_school_playbook=self.clean_SONA_playbook_null(row['Y9_f10.a']),#13
                # special_olympics_state_playbook= None, #self.clean_SONA_playbook_null(row['G13_4']),#13
                # special_olympics_fitness_guide_for_schools= None, #self.clean_SONA_playbook_null(row['G13_2']),#13
                # unified_physical_education_resource= None, #self.clean_SONA_playbook_null(row['G13_7']),#13
                # special_olympics_young_athletes_activity_guide= None, #self.clean_SONA_playbook_null(row['G13_8']),#13
                # inclusive_youth_leadership_training_faciliatator_guide= None, #self.clean_SONA_playbook_null(row['G13_10']),#13
                # planning_and_hosting_a_youth_leadership_experience=None,#self.clean_str_null(row['Y12_E9_10_1']),#13
                # unified_classoom_lessons_and_activities= None, #self.clean_str_null(row['G13_11']),#13
                # generation_unified_youtube_channel_or_videos= None, #self.clean_str_null(row['G13_12']),#13
                # inclusion_tiles_game_or_facilitator_guide= None, #self.clean_str_null(row['G13_13']),#13

                # students_with_intellectual_disability=  None, #self.clean_str_null(row['Y15_L18_1_Recode']),#1
                # students_without_intellectual_disability= None, #self.clean_str_null(row['Y15_L18_2_Recode']),#1
                # the_school_as_a_whole= None, #self.clean_str_null(row['Y15_L19_Recode']),#13

                # increase_in_understanding_language_of_disability=None, #self.clean_str_null(row['Y15_L5_1_Recode']),#1
                # increasing_confidence_of_students_with_idd=self.clean_str_null(row['Y9_h1.d']),#1
                # opportunities_for_students_idd_to_work_together=self.clean_str_null(row['Y9_h1.c_recode']),#1
                # creating_a_more_socially_inclusive_school_environment=self.clean_str_null(row['Y9_h2.a_recode']),#1
                # raising_awareness_about_students_with_idd=self.clean_str_null(row['Y9_h1.e_recode']),#1
                # increasing_participation_of_students_with_idd=self.clean_str_null(row['Y9_h1.a_recode']),#1
                # reducing_bullying_teasing=self.clean_str_null(row['Y9_h2.b_recode']),#1
                # increasing_confidence_of_students_without_idd= None, #self.clean_str_null(row['Y15_L8_1_Recode']),#1
                # increasing_participation_of_students_without_idd=self.clean_str_null(row['Y9_h1.b']),#1
                # increasing_attendance_of_students_with_idd=self.clean_str_null(row['Y9_h2.c_recode']),#1
                # reducing_disciplinary_referrals_for_students_with_idd= None, #self.clean_str_null(row['Y15_L12_1_Recode']),#1
                # increasing_attendance_of_students_without_idd=None, #self.clean_str_null(row['Y15_L11_1_Recode']),#1
                # reducing_disciplinary_referrals_for_students_without_idd= None #self.clean_str_null(row['Y15_L13_1_Recode'])#1
                )

    def test_values(self):

        datafile = os.path.join(settings.BASE_DIR,'excel_data/All_the_data_till_Y14.csv') 

        with open(datafile, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile) #islice(csvfile, None, 51))
            for row in reader:
                print(row['NCESID'])

                
                # print(row['NCESID'])


    def test_values_pandas(self):

        datafile = os.path.join(settings.BASE_DIR,'excel_data/All_the_data_till_Y14.csv') 
        reader=pd.read_excel(datafile)
        print(reader.shape)
        for i in range(reader.shape[0]):
            print(reader['NCESID'][i])
        #print(row['NCESID'])
                
call =  Command()
call.handle()
#call.test_values()

