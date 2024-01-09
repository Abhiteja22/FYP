import requests
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Asset, PortfolioAsset, Portfolio, Profile
from .forms import AddToPortfolioForm, UserRegisterForm, ProfileForm, PortfolioForm
from .utils import calculate_optimal_weights_portfolio, calculate_portfolio_details, get_VaR, get_asset_details, get_expected_market_return, get_linear_regression, get_maximum_drawdown, get_risk_free_rate, get_simple_moving_average, get_sortino_ratio

# Create your views here.

def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render())

@login_required
def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Obtain the existing Profile instance or create a new one if it doesn't exist
            profile, created = Profile.objects.get_or_create(user=user)

            # Update the profile with form data
            profile_form = ProfileForm(request.POST, instance=profile)
            profile = profile_form.save(commit=False)
            
            profile.risk_free_rate = get_risk_free_rate(profile.investment_time_period)
            profile.expected_market_return = get_expected_market_return(profile.market_index, profile.investment_time_period)

            profile.save()
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()
    return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def profile_view(request):
    profile = request.user.profile
    profile.risk_free_rate = get_risk_free_rate(profile.investment_time_period)
    profile.expected_market_return = get_expected_market_return(profile.market_index, profile.investment_time_period)
    profile.save()
    return render(request, 'profile/profile_view.html', {'profile': profile})

@login_required
def profile_update(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.risk_free_rate = get_risk_free_rate(profile.investment_time_period)
            profile.expected_market_return = get_expected_market_return(profile.market_index, profile.investment_time_period)
            profile.save()
            return redirect('profile_view')
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile/profile_update.html', {'form': profile_form})

# TODO: Update portfolio creation page to be able to add assets from the page
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

# TODO: Update portfolio update page
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

# To view list of portfolios
@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})

# To view portfolios details
@login_required
def portfolio_details(request, pk):
    profile = request.user.profile
    portfolio = Portfolio.objects.get(pk=pk, user=request.user)
    # Attach PortfolioAsset instances to each portfolio
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio)
    combined_assets = {}
    for asset in portfolio_assets:
        if asset.asset_ticker in combined_assets:
            combined_assets[asset.asset_ticker] += asset.quantity
        else:
            combined_assets[asset.asset_ticker] = asset.quantity

    portfolio.portfolio_details = calculate_portfolio_details(combined_assets, profile)

    VaR, CVaR = get_VaR(portfolio_assets)
    sortino_ratio = get_sortino_ratio(portfolio_assets)
    maximum_drawdown = get_maximum_drawdown(portfolio_assets)
    print(f"VaR at 95% confidence level: {VaR}")
    print(f"CVaR at 95% confidence level: {CVaR}")
    print(f"Sortino Ratio with Target return 0%: {sortino_ratio}")
    print(f"Maximum Drawdown: {maximum_drawdown * 100:.2f}%")
    
    return render(request, 'portfolio/portfolio_details.html', {'portfolio': portfolio})

@login_required
def asset_list(request, country='USA'):
    stocks = Asset.objects.filter(country=country, type="Stock")
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
    profile = request.user.profile
    asset_details = get_asset_details(symbol, profile)  # Fetch detailed info like price, volume, etc.
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
    profile = request.user.profile
    # portfolio = Portfolio.objects.get(id=portfolio_id) # ORIGINAL WAY TO GET Portfolio
    # Get the portfolio or return a 404 response if not found
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio)
    asset_list = [asset.asset_ticker for asset in portfolio_assets]
    unique_assets = list(set(asset_list))
    unique_assets.sort()
    zipped_asset_weights = calculate_optimal_weights_portfolio(profile, unique_assets)
    context = {
        'portfolio': portfolio,
        'zipped_weights': zipped_asset_weights,
    }
    return render(request, 'portfolio/portfolio_weights.html', context)

def search_stocks(request):
    search_text = request.GET.get('search_text', '')
    if search_text:
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

def show_chart(request, symbol):
    chart = get_simple_moving_average(symbol)
    predicted_prices_chart = get_linear_regression(symbol)
    context = {'chart': chart, 'ARIMA': predicted_prices_chart}
    return render(request, 'asset/asset_dashboard.html', context)