from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader

from pat.models import Portfolio


def details(request, id):
    # p = Portfolio.objects.get(id=id)
    template = loader.get_template("portfolio/detail.html")
    context = context = {
        # "portfolio": p,
        # "slices_labels": p.labels,
        # "slices_absolute": p.absolute,
        # "slices_relative": p.relative,
    }
    return HttpResponse(template.render(context, request))


def portfolio(request):
    pp_items = Portfolio.objects.iterator()

    return render(
        request,
        "portfolio/list.html",
        {
            # "pp_items": pp_items,
        },
    )
