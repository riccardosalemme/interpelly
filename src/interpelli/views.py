from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Interpello, Province


def home(request):
    provinces = list(Province.objects.all())
    selected_provinces = [
        str(province.pk) for province in provinces
        if str(province.pk) in request.GET.getlist("province")
    ]
    interpelli = Interpello.objects.select_related("province").order_by("-created_at", "-pk")
    if selected_provinces:
        interpelli = interpelli.filter(province_id__in=selected_provinces)
    page = Paginator(interpelli, 50).get_page(request.GET.get("page"))
    return render(request, "interpelli/home.html", {
        "page": page,
        "provinces": provinces,
        "selected_provinces": selected_provinces,
    })
