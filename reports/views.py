from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.decorators import admin_required
from .forms import AttendanceReportForm
from students.models import Student, Attendance, Class
import openpyxl
from datetime import datetime

@login_required
@admin_required
def attendance_report(request):
    report_data = None
    form = AttendanceReportForm(request.POST or None)

    # Handle Excel export on GET request
    if 'export' in request.GET and request.GET['export'] == 'excel':
        get_form = AttendanceReportForm(request.GET)
        if get_form.is_valid():
            class_obj = get_form.cleaned_data['class_obj']
            start_date = get_form.cleaned_data['start_date']
            end_date = get_form.cleaned_data['end_date']
            
            students = Student.objects.filter(current_class=class_obj)
            results = []
            for student in students:
                attendance_records = Attendance.objects.filter(student=student, date__range=[start_date, end_date])
                results.append({
                    'student': student,
                    'present': attendance_records.filter(status='present').count(),
                    'absent': attendance_records.filter(status='absent').count(),
                    'late': attendance_records.filter(status='late').count(),
                    'excused': attendance_records.filter(status='excused').count(),
                })

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=attendance_report_{class_obj.name}_{start_date}_to_{end_date}.xlsx'

            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = 'Attendance Report'

            # Headers
            headers = ['Student Name', 'Admission No.', 'Present', 'Absent', 'Late', 'Excused']
            sheet.append(headers)

            # Data
            for item in results:
                sheet.append([
                    item['student'].user.get_full_name(),
                    item['student'].admission_number,
                    item['present'],
                    item['absent'],
                    item['late'],
                    item['excused'],
                ])
            
            workbook.save(response)
            return response

    if request.method == 'POST' and form.is_valid():
        class_obj = form.cleaned_data['class_obj']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        students = Student.objects.filter(current_class=class_obj)
        results = []
        for student in students:
            attendance_records = Attendance.objects.filter(student=student, date__range=[start_date, end_date])
            present_count = attendance_records.filter(status='present').count()
            total_days = (end_date - start_date).days + 1
            results.append({
                'student': student,
                'present': present_count,
                'absent': attendance_records.filter(status='absent').count(),
                'late': attendance_records.filter(status='late').count(),
                'excused': attendance_records.filter(status='excused').count(),
                'attendance_percentage': (present_count / total_days) * 100 if total_days > 0 else 0
            })
        
        report_data = {
            'class': class_obj,
            'start_date': start_date,
            'end_date': end_date,
            'results': results,
            'class_pk': class_obj.pk, # Pass pk for export link
            'start_date_str': start_date.isoformat(),
            'end_date_str': end_date.isoformat(),
        }

    context = {
        'title': 'Attendance Report',
        'form': form,
        'report_data': report_data
    }
    return render(request, 'reports/attendance_report.html', context)
