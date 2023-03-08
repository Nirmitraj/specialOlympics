import csv
from datetime import date
from itertools import islice
import pathlib
from django.conf import settings
from django.core.management.base import BaseCommand
from analytics.models import SchoolDetails
import json

class Command(BaseCommand):
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
                SchoolDetails.objects.get_or_create(school_ID=row['NCESID'],
                school_name=self.clean_school_name(row['UD_SchooName']),
                school_state=row['UD_StateProgram'],
                Locale_number=self.clean_str_null(row['UD_LocaleNum']),
                gradeLevel_WithPreschool=self.clean_str_null(row['Y14_GradeLevel_WithPreschool']),
                implementation_level=self.clean_str_null(row['Y14_ImplementationLevel']),
                locale=self.clean_school_name(row['UD_Locale']),
                school_county=row['UD_CountyName'],
                state_abv=row['UD_StateABV'],
                student_enrollment_range=self.clean_str_null(row['Y14_Enrollment_CAT']),
                student_free_reduced_lunch=self.clean_str_null(row['Y14_FreeReducedLunch_CAT']),
                student_nonwhite_population=self.clean_str_null(row['Y14_NONWHITE_CAT2']),
                survey_taken=self.number_bool(row['Y14_data']),
                unified_sports_component=self.number_bool(row['Y14_UnifiedSportsComponent']),
                youth_leadership_component=self.number_bool(row['Y14_YouthLeadershipComponent']),
                whole_school_component=self.number_bool(row['Y14_WholeSchoolComponent']),
                zipcode=row['UD_ZIP'],
                survey_taken_year=2022)

call =  Command(BaseCommand)
call.handle()