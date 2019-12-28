# oppia/views.py
import datetime
import json

import tablib
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

from helpers.forms.dates import DateRangeIntervalForm, \
    DateRangeForm
from oppia.models import Points
from oppia.models import Tracker
from oppia.permissions import can_view_course_detail
from oppia.views.utils import generate_graph_data
from reports.signals import dashboard_accessed
from summary.models import CourseDailyStats


def recent_activity(request, course_id):

    course, response = can_view_course_detail(request, course_id)
    if response is not None:
        raise response

    dashboard_accessed.send(sender=None, request=request, data=course)

    start_date = datetime.datetime.now() - datetime.timedelta(days=31)
    end_date = datetime.datetime.now()
    interval = 'days'

    if request.method == 'POST':
        form = DateRangeIntervalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date + " 00:00:00",
                                                    "%Y-%m-%d %H:%M:%S")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date + " 23:59:59",
                                                  "%Y-%m-%d %H:%M:%S")
            interval = form.cleaned_data.get("interval")
    else:
        data = {}
        data['start_date'] = start_date
        data['end_date'] = end_date
        data['interval'] = interval
        form = DateRangeIntervalForm(initial=data)

    dates = []
    if interval == 'days':
        daily_stats = CourseDailyStats.objects.filter(course=course,
                                                      day__gte=start_date,
                                                      day__lte=end_date) \
                        .values('day', 'type') \
                        .annotate(total=Sum('total'))

        dates = generate_graph_data(daily_stats, False)

    else:
        monthly_stats = CourseDailyStats.objects.filter(course=course,
                                                        day__gte=start_date,
                                                        day__lte=end_date) \
                        .extra({'month': 'month(day)', 'year': 'year(day)'}) \
                        .values('month', 'year', 'type') \
                        .annotate(total=Sum('total')) \
                        .order_by('year', 'month')

        dates = generate_graph_data(monthly_stats, True)

    leaderboard = Points.get_leaderboard(10, course)
    return render(request, 'course/activity.html',
                  {'course': course,
                   'monthly': interval == 'months',
                   'form': form,
                   'data': dates,
                   'leaderboard': leaderboard})


def recent_activity_detail(request, course_id):
    course, response = can_view_course_detail(request, course_id)

    if response is not None:
        return response

    start_date = datetime.datetime.now() - datetime.timedelta(days=31)
    end_date = datetime.datetime.now()
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            trackers = Tracker.objects.filter(course=course,
                                              tracker_date__gte=start_date,
                                              tracker_date__lte=end_date) \
                              .order_by('-tracker_date')
        else:
            trackers = Tracker.objects.filter(course=course) \
                .order_by('-tracker_date')
    else:
        data = {}
        data['start_date'] = start_date
        data['end_date'] = end_date
        form = DateRangeForm(initial=data)
        trackers = Tracker.objects.filter(course=course) \
            .order_by('-tracker_date')

    paginator = Paginator(trackers, 25)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        tracks = paginator.page(page)
        for t in tracks:
            t.data_obj = []
            try:
                data_dict = json.loads(t.data)
                for key, value in data_dict.items():
                    t.data_obj.append([key, value])
            except ValueError:
                pass
            t.data_obj.append(['agent', t.agent])
            t.data_obj.append(['ip', t.ip])
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    return render(request, 'course/activity-detail.html',
                  {'course': course,
                   'form': form,
                   'page': tracks, })


def export_tracker_detail(request, course_id):
    course, response = can_view_course_detail(request, course_id)

    if response is not None:
        return response

    headers = ('Date',
               'UserId',
               'Type',
               'Activity Title',
               'Section Title',
               'Time Taken',
               'IP Address',
               'User Agent',
               'Language')
    data = []
    data = tablib.Dataset(* data, headers=headers)
    trackers = Tracker.objects.filter(course=course).order_by('-tracker_date')
    for t in trackers:
        try:
            data_dict = json.loads(t.data)
            if 'lang' in data_dict:
                lang = data_dict['lang']
            else:
                lang = ""
            data.append((t.tracker_date.strftime('%Y-%m-%d %H:%M:%S'),
                         t.user.id,
                         t.type,
                         t.get_activity_title(),
                         t.get_section_title(),
                         t.time_taken,
                         t.ip,
                         t.agent,
                         lang))
        except ValueError:
            data.append((t.tracker_date.strftime('%Y-%m-%d %H:%M:%S'),
                         t.user.id,
                         t.type,
                         "",
                         "",
                         t.time_taken,
                         t.ip,
                         t.agent,
                         ""))

    response = HttpResponse(
        data.xls,
        content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=export.xls"

    return response
