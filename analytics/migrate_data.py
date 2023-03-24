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
                SchoolDetails.objects.get_or_create(school_ID=row['NCESID'],#all
                school_name=self.clean_school_name(row['UD_SchooName']),#all
                school_state=row['UD_StateProgram'],#all
                Locale_number=self.clean_str_null(row['UD_LocaleNum']),#all
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
                survey_taken_year=2022)

call =  Command(BaseCommand)
call.handle()