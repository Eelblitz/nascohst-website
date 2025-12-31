from django.shortcuts import render, get_object_or_404
from .models import School, Programme


def programme_detail(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    return render(request, 'academics/programme_detail.html', {
        'programme': programme
    })



def school_list(request):
    schools = School.objects.all()
    return render(request, 'academics/school_list.html', {
        'schools': schools
    })


def school_detail(request, pk):
    school = get_object_or_404(School, pk=pk)

    programmes_pd = Programme.objects.filter(school=school, level='PD')
    programmes_nd = Programme.objects.filter(school=school, level='ND')
    programmes_hnd = Programme.objects.filter(school=school, level='HND')

    return render(request, 'academics/school_detail.html', {
        'school': school,
        'programmes_pd': programmes_pd,
        'programmes_nd': programmes_nd,
        'programmes_hnd': programmes_hnd,
    })
