from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Stock, Portfolio
from .forms import AssetFormSet, UserRegisterForm, PortfolioForm

# Create your views here.

@login_required
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

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        formset = AssetFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            formset.instance = portfolio
            formset.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm()
        formset = AssetFormSet()
    return render(request, 'portfolio/portfolio_form.html', {'form': form, 'formset': formset})

# TODO
@login_required 
def portfolio_update(request, pk):
    portfolio = Portfolio.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'portfolio/portfolio_form.html', {'form': form})

# To view portfolios
@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})