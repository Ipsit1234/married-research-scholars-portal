from django import forms
from django.db.models import Q
from django.db.models import F
from .models import Applicant, Waitlist, OccupiedList, VacatedList
from django.contrib.admin import widgets
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

class DateInput(forms.DateInput):
    input_type = 'date'

class ApplicantForm(forms.ModelForm):
    """Form Definition for Applicant"""
    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True

    class Meta:
        model = Applicant
        fields = '__all__'
        exclude = (
            'marriage_certificate_verified',
            'joint_photograph_with_spouse_verified',
            'coursework_grade_sheet_verified',
            'recommendation_of_guide_for_accomodation_verified',
            'feedback',
            'acadsection_feedback',
            'waitlist_Type1',
            'waitlist_Tulsi',
            'waitlist_MRSB',
            'date_applied',
            'verified_time',
            'occupied_Type1',
            'occupied_Tulsi',
            'occupied_MRSB',
            # 'defer_Type1',
            # 'defer_Tulsi',
            # 'defer_MRSB',
            'acad_details_verification_date',
            'application_received_by_hcu_date',
            'acad_details_verified',
            'scholarship_awarded_upto'
        )
        widgets = {
            # 'date_of_marriage' : DateInput(format=(r"%Y-%m-%d")), #forms.SelectDateWidget,
            'date_of_registration': DateInput(format=("%YYYY-%MM-%DD")),  # forms.SelectDateWidget,
            'date_of_scholarship': DateInput(format=("%YYYY-%MM-%DD")),  # forms.SelectDateWidget,
            'course_work_completed_on': DateInput(format=("%YYYY-%MM-%DD")),  # forms.SelectDateWidget,
        }

class VacatingForm(forms.Form):
    """Form definition for Vacating"""
    vacate = forms.BooleanField(label="Vacate your apartment",required=True)

class MailingListForm(forms.ModelForm):
    class Meta:
        model = Waitlist
        fields = '__all__'
        widget = widgets.FilteredSelectMultiple('Applicant', False, attrs={'rows': '2'})

    applicant = forms.ModelMultipleChoiceField(
        Applicant.objects.filter(acad_details_verified=True, marriage_certificate_verified=True,
                                 joint_photograph_with_spouse_verified=True,
                                 coursework_grade_sheet_verified=True,
                                 recommendation_of_guide_for_accomodation_verified=True),
        widget=widgets.FilteredSelectMultiple('Applicant', False, attrs={'rows': '2'}), required=False)

    def save(self, commit=True):
        buildings = Waitlist.objects.filter(building=self.cleaned_data['building'])
        applicants_before = None
        for building in buildings:
            applicants_before = building.applicant.all()
        applicants_after = self.cleaned_data['applicant']
        if applicants_before:
            if len(applicants_before) > len(applicants_after):
                raise PermissionDenied()
            if applicants_before != None:
                applicants_diff = applicants_after.exclude(id__in=applicants_before)
            else:
                applicants_diff = applicants_after
            print(applicants_before)
            print(applicants_after)
            print(applicants_diff)
            for appli in applicants_diff:
                emailid = appli.email
                message = f"You have cleared the waitlist to occupy {self.cleaned_data['building']}. Send an acceptance mail " \
                          f"along with your contact details to send@email.com"
                subject = "Married Research Scholar Portal"
                # send_mail(
                #     subject=subject,
                #     message=message,
                #     recipient_list=[emailid, ],
                #     from_email=settings.DEFAULT_FROM_MAIL
                # )
        return super(MailingListForm, self).save(commit=commit)


class OccupiedListForm(forms.ModelForm):
    class Meta:
        model = OccupiedList
        fields = '__all__'
        widget = widgets.FilteredSelectMultiple('Applicant', False, attrs={'rows': '2'})

    applicant = forms.ModelMultipleChoiceField(
        queryset=Applicant.objects.filter(acad_details_verified=True, marriage_certificate_verified=True,
                                                         joint_photograph_with_spouse_verified=True,
                                                         coursework_grade_sheet_verified=True,
                                                         recommendation_of_guide_for_accomodation_verified=True, waitlist__id__isnull=False,
                                          occupied_MRSB=False, occupied_Tulsi=False, occupied_Type1=False),
        widget=widgets.FilteredSelectMultiple('Applicant', False, attrs={'rows': '2'}),
        required=False)


    def save(self, commit=True):
        instance = super(OccupiedListForm, self).save(commit=False)
        buildings = OccupiedList.objects.filter(building=self.cleaned_data['building'])
        applicants_before = None
        for building in buildings:
            applicants_before = building.applicant.all()
        applicants_after = self.cleaned_data['applicant']
        if applicants_before:
            if len(applicants_before) > len(applicants_after):
                raise PermissionDenied()
            if applicants_before != None:
                applicants_after.exclude(id__in=applicants_before)
            else:
                pass
            for appli in applicants_after:
                emailid = appli.email
                message = f"Your acceptance mail for the building {self.cleaned_data['building']} has been received. You can contact HCU for further details"
                subject = "Married Research Scholar Portal"
                # send_mail(
                #     subject=subject,
                #     message=message,
                #     recipient_list=[emailid,],
                #     from_email=settings.DEFAULT_FROM_MAIL
                # )
            qs = Applicant.objects.all().filter(acad_details_verified=True, marriage_certificate_verified=True,
                                                joint_photograph_with_spouse_verified=True,
                                                coursework_grade_sheet_verified=True,
                                                recommendation_of_guide_for_accomodation_verified=True).order_by(
                'date_applied')
            for student in applicants_after:
                if self.cleaned_data['building'] == 'Type-1':
                    student.occupied_Type1 = True
                    qs_excluded = qs.exclude(
                        id=student.id)  # exclude the current applicant and all those who are already occupying
                    qs_excluded.exclude(
                        waitlist_Type1__lte=student.waitlist_Type1)  # list of students having higher waitlist than current applicant
                    qs_excluded.update(waitlist_Type1=F('waitlist_Type1') - 1)
                    student.waitlist_Type1 = 0
                elif self.cleaned_data['building'] == 'Tulsi':
                    student.occupied_Tulsi = True
                    qs_excluded = qs.exclude(
                        id=student.id)  # exclude the current applicant and all those who are already occupying
                    qs_excluded.exclude(
                        waitlist_Tulsi__lte=student.waitlist_Tulsi)  # list of students having higher waitlist than current applicant
                    qs_excluded.update(waitlist_Tulsi=F('waitlist_Tulsi') - 1)
                    student.waitlist_Tulsi = 0
                elif self.cleaned_data['building'] == 'Manas':
                    student.occupied_MRSB = True
                    qs_excluded = qs.exclude(
                        id=student.id)  # exclude the current applicant and all those who are already occupying
                    qs_excluded.exclude(
                        waitlist_MRSB__lte=student.waitlist_MRSB)  # list of students having higher waitlist than current applicant
                    qs_excluded.update(waitlist_MRSB=F('waitlist_MRSB') - 1)
                    student.waitlist_MRSB = 0
                student.save(flag=True)
        return super(OccupiedListForm, self).save(commit=commit)


class VacatedListForm(forms.ModelForm):
    class Meta:
        model = VacatedList
        fields = '__all__'
        widget = widgets.FilteredSelectMultiple('Applicant', False, attrs={'rows': '2'})

    # applicant = forms.ModelMultipleChoiceField(Applicant.objects.filter(Q(occupied_Type1=True) | Q(occupied_Tulsi=True) | Q(occupied_MRSB=True)), widget = widgets.FilteredSelectMultiple('Applicant', False, attrs={'rows': '2'}), required=False)

    def save(self, commit=True):
        buildings = VacatedList.objects.filter(building=self.cleaned_data['building'])
        applicants_before = None
        for building in buildings:
            applicants_before = building.applicant.all()
        applicants_after = self.cleaned_data['applicant']
        if len(applicants_before) > len(applicants_after):
            raise PermissionDenied()
        if applicants_before != None:
            applicants_diff = applicants_after.exclude(id__in=applicants_before)
        else:
            applicants_diff = applicants_after
        for appli in applicants_diff:
            emailid = appli.email
            message = f"You have successfully vacated {self.cleaned_data['building']}. Deposit the keys at HCU office."
            subject = "Married Research Scholar Portal"
            # send_mail(
            #     subject=subject,
            #     message=message,
            #     recipient_list=[emailid, ],
            #     from_email=settings.DEFAULT_FROM_MAIL
            # )
        return super(VacatedListForm, self).save(commit=commit)