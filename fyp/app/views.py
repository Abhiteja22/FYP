import requests
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Stock, Portfolio
from .forms import AssetFormSet, ProfileUpdateForm, UserRegisterForm, PortfolioForm

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
def profile_view(request):
    profile = request.user.profile
    return render(request, 'profile/profile_view.html', {'profile': profile})

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            # Redirect to profile view or add a success message
            return redirect('profile_view')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'profile/profile_update.html', {'form': form})

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
            return redirect('portfolio_list')
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'portfolio/portfolio_form.html', {'form': form})

# To view portfolios
@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})

def get_asset_list_data():
    # This is a placeholder URL. You will need to use the endpoint provided by your financial data API.
    url = f"https://cloud.iexapis.com/stable/ref-data/symbols?token={settings.IEX_CLOUD_API_KEY}"

    # Replace 'YourApiKey' with the actual key, ideally fetched from your environment or Django settings
    headers = {
        "Authorization": f"Bearer {settings.FINANCIAL_DATA_API_KEY}"
    }

    # Make the API request
    response = requests.get(url, headers=headers)

     # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON data into a Python dictionary
        data = response.json()

        # Extract the list of top stocks. The structure depends on the API response format.
        # Here, I'm assuming 'data' is a list of dictionaries with stock info
        top_stocks = data.get('top500', [])
        
        # Format the data as needed for your application
        # For example, if the data needs to be sorted or filtered
        
        return top_stocks
    else:
        # Handle errors or unsuccessful status codes
        # You may want to log the error and return an empty list or raise an exception
        return []

@login_required
def asset_list(request):
    top_assets_data = get_asset_list_data()
    context = {'top_assets': top_assets_data}
    return render(request, 'asset/asset_list.html', context)