import json

import requests
from django.conf import settings
from django.shortcuts import render
from requests.structures import CaseInsensitiveDict

from .helpers import is_connected
from .models import Scan


def connection_test(request):

    return render(
        request, "partials/internet.html", {"is_connected": is_connected("google.com")}
    )


def button_test_hx(request):
    scans = Scan.objects.all().order_by("-time_scan")

    has_non_uploaded = False

    for scan in scans:
        if scan.scan_id is None:
            has_non_uploaded = True
            break

    return render(
        request,
        "partials/resend_failed_button.html",
        {
            "scans": scans,
            "is_connected": is_connected("google.com"),
            "scan_button_on": True
            if (has_non_uploaded is True and is_connected("google.com"))
            else False,
        },
    )


def scan_home_page(request):

    scans = Scan.objects.all().order_by("-time_scan")

    return render(
        request,
        "scan.html",
        {
            "scans": scans,
            "is_connected": False,
            "scan_button_on": False,
        },
    )


def scan_hx(request):

    sku = request.POST.get("sku")

    scans = Scan.objects.all().order_by("-time_scan")

    if sku != "" and sku[0] != " ":

        new_scan = Scan(sku=sku, location=settings.LOCATION_CODE)
        new_scan.save()

        return render(
            request,
            "partials/hx_table.html",
            {
                "scans": Scan.objects.all().order_by("-time_scan"),
                "scan_button_on": False,
            },
        )

    else:
        return render(
            request,
            "partials/hx_table.html",
            {
                "scans": scans,
                "scan_button_on": False,
            },
        )


def send_scans_hx(request):

    internet_status = 0

    for scan in Scan.objects.filter(time_upload=None):

        if is_connected("google.com"):

            app_key = settings.APP_KEY
            scan_data = {
                "sku": scan.sku,
                "time_scan": scan.time_scan.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                "location": scan.location,
            }
            data_json = json.dumps(scan_data)

            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Content-type"] = "application/json"
            headers["Authorization"] = "Token {}".format(app_key)

            response = requests.post(
                "https://bddwscans.com/endpoint/", data=data_json, headers=headers
            )

            if response.status_code == 200:
                print(response.json())
                scan.scan_id = response.json()["scan_id"]
                scan.time_upload = response.json()["time_upload"]
                scan.save()

            if response.status_code == 403:
                print("API KEY ERROR")

            internet_status = 1

    return render(
        request,
        "partials/hx_table.html",
        {
            "scans": Scan.objects.all().order_by("-time_scan"),
            "internet_status": internet_status,
        },
    )
