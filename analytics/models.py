from django.db import models


class SchoolDetails(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    school_ID=models.CharField(max_length=90,null=False,default=None)
    school_name=models.CharField(max_length=255,null=True,default=None)
    school_state=models.CharField(max_length=55,null=True,default=None)
    school_county=models.CharField(max_length=120,null=True,default=None)
    state_abv=models.CharField(max_length=6,null=False,default=None)
    zipcode=models.IntegerField(null=False,default=None)
    survey_taken=models.BooleanField(null=True,default=None)
    gradeLevel_WithPreschool=models.CharField(max_length=120,null=True,default=None)
    locale_number=models.IntegerField(null=True,default=None)
    locale=models.CharField(max_length=32,null=True,default=None)
    student_enrollment_range=models.CharField(max_length=56,null=True,default=None)
    student_free_reduced_lunch=models.CharField(max_length=56,null=True,default=None)
    student_nonwhite_population=models.CharField(max_length=56,null=True,default=None)
    implementation_level=models.CharField(max_length=120,null=True,default=None)
    unified_sports_component=models.BooleanField(null=True,default=None)
    youth_leadership_component=models.BooleanField(null=True,default=None)
    whole_school_component=models.BooleanField(null=True,default=None)
    survey_taken_year=models.IntegerField(null=False,default=None)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
