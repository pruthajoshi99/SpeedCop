import json
import math
import pytz
import requests
from datetime import datetime, timedelta
from django.contrib import messages
from django.core import serializers
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch
import os
from .models import City, State
from django.conf import settings


# Create your views here.
def login_view(request):
    return render(request, 'login.html')


def dashboard_view(request):
    if 'token' in request.COOKIES:
        render_data = dict()
        req = requests.get('http://' + request.get_host() + '/api/violations-data',
                           headers={'Authorization': 'Token ' + request.COOKIES['token']})
        if request.method == 'POST':
            req = requests.post('http://' + request.get_host() + '/api/violations-data',
                                headers={'Authorization': 'Token ' + request.COOKIES['token']}, data=request.POST)
            render_data['form_data'] = json.dumps(request.POST)
            print(render_data['form_data'])
        data = req.json()
        for violation in data['violations']:
            violation['timestamp'] = datetime.strptime(violation['timestamp'], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                f"%d %b '%y at %I:%M %p")
        render_data['context'] = data
        if 'pdf' in request.POST:
            # Pass filter date
            date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
            if 'timestamp' in request.POST:
                if request.POST['timestamp']:
                    date = request.POST['timestamp']
                    print("post", date)
                else:
                    date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
                    print("asfdsafa", type(date))
            print("data['violations']=>", data['violations'])
            doc = write_pdf_view(request, data['violations'], date)

            response = HttpResponse(doc, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Violations.pdf"'
            return response
        render_data['States'] = State.objects.all()
        return render(request, 'dashboard.html', render_data)
    else:
        messages.error(request, 'You have been logged out. You will have to login!')
        return redirect('frontend:login')


def change_password_view(request):
    if 'token' in request.COOKIES:
        if request.method == 'POST':
            req = requests.put('http://' + request.get_host() + '/api/change-password',
                               headers={'Authorization': 'Token ' + request.COOKIES['token']},
                               data={'old_password': request.POST['old_password'],
                                     'new_password': request.POST['new_password']})
            if req.status_code == 200:
                messages.success(request, 'Password changed successfully!')
                return redirect('frontend:dashboard')
            else:
                messages.error(request, 'Incorrect password provided')
                return redirect('frontend:change-password')
        return render(request, 'change-password.html')
    else:
        messages.error(request, 'You have been logged out. You will have to login!')
        return redirect('frontend:login')


def forgot_password_view(request):
    if request.method == 'POST':
        messages.error(request, 'Reset password link has been sent to your email id')


def load_cities(request):
    state = request.GET.get('State')
    cities = City.objects.filter(State=state).order_by('name')
    # return HttpResponse(json.dumps({'cities': cities}))


def get_ordinal(n):
    global math
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


def write_pdf_view(request, violations_data, date):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    table_entries = []
    row_array = []

    col_widths = [4 * cm, 3 * cm, 1.5 * cm, 1.5 * cm, 2.5 * cm, 3.5 * cm, 1.5 * cm]

    def myFirstPage(canvas, doc):
        global inch, cm, timezone, get_ordinal
        title = "Violations List"
        width, height = A4

        canvas.setTitle('Violations List')

        # 291 245
        image_path = os.path.join(settings.BASE_DIR, 'frontend/static/img/logo-square.jpg')
        canvas.drawImage(image_path, 1.5 * cm, height - (2.4 * cm), width=50., height=50.5, mask=None)

        image_path = os.path.join(settings.BASE_DIR, 'frontend/static/img/login-page-text.jpg')
        canvas.drawImage(image_path, 1.25 * cm, height - (2.87 * cm), width=60, height=13.21585903083, mask=None)
        # 454 100

        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(7.4 * cm, height - inch, title)

        canvas.setFont("Helvetica", 12)
        date1 = date.strftime(f"%d %b %Y")
        canvas.drawString(16.5 * cm, height - inch, date1)

        # canvas.drawString(16.5 * cm, height - inch, f'F.Y. 2090')

        canvas.line(1 * cm, height - (2.9 * cm), width - 1 * cm, height - (2.9 * cm))

        canvas.line(1 * cm, 1.5 * cm, width - 1 * cm, 1.5 * cm)

        timestamp = datetime.now(pytz.timezone('Asia/Kolkata'))
        day = get_ordinal(int(timestamp.strftime('%d')))
        time = timestamp.strftime(f"{day} %B, %Y at %I:%M %p")

        canvas.setFont("Times-Roman", 11)
        canvas.drawString(cm, cm, f'Report generated electronically on {time}')

    row_array.append(Paragraph("<para align=center>Name</para>", styles['Normal']))
    row_array.append(Paragraph("<para align=center>Vehicle Number</para>", styles['Normal']))
    row_array.append(Paragraph("<para align=center>Speed</para>", styles['Normal']))
    row_array.append(Paragraph("<para align=center>Speed Limit</para>", styles['Normal']))
    row_array.append(Paragraph("<para align=center>Timestamp</para>", styles['Normal']))
    row_array.append(Paragraph("<para align=center>Area</para>", styles['Normal']))
    row_array.append(Paragraph("<para align=center>Paid</para>", styles['Normal']))
    table_entries.append(row_array)

    for data in violations_data:
        entry = []
        for key, value in data.items():
            # if str(date) == str(datetime.strptime(data['timestamp'], "%d %b '%y at %I:%M %p").date()):
            if key in ['_id', 'lat', 'lng', 'difference', 'Notified', 'City']:
                continue
            if key == 'timestamp':
                value = value[14:]
            entry.append(value)
        if entry:
            table_entries.append(entry)

    # Draw things on the PDF. Here's where the PDF generation happens.
    table = Table(table_entries, col_widths)
    # elements.append(Paragraph("<para align=center>Violations List</para>", styles['Heading1']))
    table.setStyle(
        TableStyle([
            ('LINEABOVE', (0, 0), (-1, 1), 2, colors.black),
            # ('LINEBEFORE', (0, 0), (0, -1), 2, colors.black),
            # ('LINEAFTER', (0, 0), (-1, -1), 2, colors.black),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEABOVE', (0, 1), (-1, -1), 0.25, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER')]
        )
    )
    # Close the PDF object cleanly, and we're done.
    elements.append(Spacer(1, 1 * cm))
    elements.append(table)
    doc.build(elements, onFirstPage=myFirstPage)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    pdf_buffer.seek(0)
    return FileResponse(pdf_buffer, as_attachment=True, filename='hello.pdf')


def accidents(request):
    if 'token' in request.COOKIES:
        req = requests.post('http://' + request.get_host() + '/api/accidents',
                            headers={'Authorization': 'Token ' + request.COOKIES['token']}, data=request.POST)
        data = req.json()
        print(data['latlngs'])
        if request.method == 'POST':
            data['form_data'] = json.dumps(request.POST)
            return render(request, 'accidents.html',
                          {'context': data['accidents'], 'areas': data['areas'], 'form_data': data['form_data'],
                           'latlngs': data['latlngs']})

        city = City.objects.all()
        return render(request, 'accidents.html',
                      {'context': data['accidents'], 'areas': data['areas'], 'latlngs': data['latlngs']})
    else:
        messages.error(request, 'You have been logged out. You will have to login!')
        return redirect('frontend:login')


def violations(request):
    if 'token' in request.COOKIES:
        req = requests.post('http://' + request.get_host() + '/api/violations',
                            headers={'Authorization': 'Token ' + request.COOKIES['token']}, data=request.POST)
        data = req.json()
        if request.method == 'POST':
            data['form_data'] = json.dumps(request.POST)
            return render(request, 'violations.html',
                          {'context': data['violations'], 'areas': data['areas'], 'form_data': data['form_data'],
                           'latlngs': data['latlngs']})

        return render(request, 'violations.html',
                      {'context': data['violations'], 'areas': data['areas'], 'latlngs': data['latlngs']})
    else:
        messages.error(request, 'You have been logged out. You will have to login!')
        return redirect('frontend:login')


def CityList(request):
    state_code = request.GET['state-code']
    state = State.objects.get(code=state_code)
    cities = City.objects.all().filter(state=state)
    json_data = serializers.serialize('json', cities)
    return HttpResponse(json_data, content_type='application/json')
