import requests
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Asset, PortfolioAsset, Portfolio
from .forms import AddToPortfolioForm, ProfileUpdateForm, UserRegisterForm, PortfolioForm
from .utils import calculate_optimal_weights_portfolio, calculate_portfolio_details, fetch_stock_symbols, fetch_asset_details

# Create your views here.

@login_required
def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())

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
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm()
    return render(request, 'portfolio/portfolio_form.html', {'form': form})

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
    return render(request, 'portfolio/portfolio_form.html', {'form': form, 'portfolio': portfolio})

# To view portfolios
@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})

# To view portfolios details
@login_required
def portfolio_details(request, pk):
    portfolio = Portfolio.objects.get(pk=pk, user=request.user)
    # Attach PortfolioAsset instances to each portfolio
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio)
    combined_assets = {}
    for asset in portfolio_assets:
        if asset.asset_ticker in combined_assets:
            combined_assets[asset.asset_ticker] += asset.quantity
        else:
            combined_assets[asset.asset_ticker] = asset.quantity

        portfolio.portfolio_details = calculate_portfolio_details(combined_assets)
    
    return render(request, 'portfolio/portfolio_details.html', {'portfolio': portfolio})

@login_required
def asset_list(request, country='USA'):
    stocks = Asset.objects.filter(country=country, type="Common Stock")
    page = request.GET.get('page', 1)
    paginator = Paginator(stocks, 100)  # Show 100 stocks per page

    try:
        stocks = paginator.page(page)
    except PageNotAnInteger:
        stocks = paginator.page(1)
    except EmptyPage:
        stocks = paginator.page(paginator.num_pages)

    context = {
        'stocks': stocks,
        'country': country
    }
    return render(request, 'asset/asset_list.html', context)

def asset_detail_view(request, symbol):
    asset_details = fetch_asset_details(symbol)  # Fetch detailed info like price, volume, etc.
    if request.method == "POST":
        form = AddToPortfolioForm(request.POST)
        if form.is_valid():
            portfolio_asset = form.save(commit=False)
            portfolio_asset.asset_ticker = symbol
            portfolio_asset.save()
            # Redirect to a success page or the asset detail page
            return redirect('portfolio_list')
    else:
        form = AddToPortfolioForm()
        # Filter portfolios to those owned by the user
        form.fields['portfolio'].queryset = Portfolio.objects.filter(user=request.user)
    return render(request, 'asset/asset_detail.html', {'asset': asset_details, 'symbol': symbol, 'form': form})
    # asset = Asset.objects.get(symbol=symbol)

def portfolio_suggest_weightage(request, portfolio_id):
    # portfolio = Portfolio.objects.get(id=portfolio_id) # ORIGINAL WAY TO GET Portfolio
    # Get the portfolio or return a 404 response if not found
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio)
    asset_list = [asset.asset_ticker for asset in portfolio_assets]
    unique_assets = list(set(asset_list))
    unique_assets.sort()
    weights = calculate_optimal_weights_portfolio(unique_assets)
    zipped_asset_weights = zip(unique_assets, weights)
    context = {
        'portfolio': portfolio,
        'zipped_weights': zipped_asset_weights,
    }
    return render(request, 'portfolio/portfolio_weights.html', context)

def search_stocks(request):
    search_text = request.GET.get('search_text', '')
    print(search_text)
    if search_text:
        print("I am Executed")
        # Call Alpha Vantage API
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "SYMBOL_SEARCH",
                "keywords": search_text,
                "apikey": settings.ALPHA_VANTAGE_API_KEY,
                "entitlement": "delayed"
            }
        )
        if response.status_code == 200:
            search_results = response.json()['bestMatches']
            # Process and return the relevant part of the response
            return JsonResponse(search_results, safe=False)
    return JsonResponse([], safe=False)