from django.http import HttpResponse
from django.template import loader
from .models import Stock

# Create your views here.

def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())

def app(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())

def stocks(request):
    myStocks = Stock.objects.all().values()
    template = loader.get_template('all_stocks.html')
    context = {
        'myStocks': myStocks,
    }
    return HttpResponse(template.render(context, request))

def details(request, id):
    myStock = Stock.objects.get(id=id)
    template = loader.get_template('details.html')
    context = {
        'myStock': myStock,
    }
    return HttpResponse(template.render(context, request))