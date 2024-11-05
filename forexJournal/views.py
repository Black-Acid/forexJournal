from django.shortcuts import render, get_object_or_404
import pandas as pd
from .models import TradesModel, AccountBalance, ProcessedProfit, StrategyModel, Profile, mt5login
from django.db.models import Sum, Count, Q, Max, Avg, F, Case, When, Value, CharField
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.utils import timezone
from django.shortcuts import redirect
from django.http import JsonResponse
import json
import requests
from django.apps import apps
from djmoney.money import Money
from django.core.exceptions import ObjectDoesNotExist
import MetaTrader5 as mt5   
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta
import numpy as np
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import SignUpForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm 



import logging

logger = logging.getLogger(__name__)
# Create your views here.


def connect_to_mt5():
    mt5_login = 191127350
    mt5_password =  "AceBlacK431@"
    mt5_server =  "Exness-MT5Trial"
    if not mt5.initialize():
        logger.error("Failed to initialize MT5")
        return False
    account_number = mt5_login  # Replace with your account number
    password = mt5_password  # Replace with your MT5 password
    server = mt5_server
    if not mt5.login(account_number, password=password, server=server):
        logger.error(f"Failed to login to MT5 with account {account_number}")
        mt5.shutdown()
        return False
    return True


PATH = "forexJournal"
PERCENT = 100
ACCOUNT_BALANCE = apps.get_model("forexJournal", "AccountBalance")
DEFAULT_BALANCE = ACCOUNT_BALANCE._meta.get_field("balance").default


def calculateWinRate(profitableTrades, number_of_trades):
    return round((profitableTrades / number_of_trades) * PERCENT, 2)


def calculateProfitFactor(profitable_value, losing_value):
    if losing_value != 0:
        return round(profitable_value / abs(losing_value), 2)
    return "N/A"


def tradeExpectancy(win_rate, average_profit, average_loss):
    win_rate_decimal = win_rate / 100
    return (win_rate_decimal * average_profit) - ((1 - win_rate_decimal) * average_loss)

def calculateRealisedRR(open_price, close_price, stop_loss):
    stop_loss_value = Decimal(stop_loss) if stop_loss else Decimal("0")
    risk = abs(open_price - stop_loss_value)
    reward = abs(close_price - open_price)
    
    return round(reward / risk if risk != 0 else Decimal("0"), 2)
    
    
def calculateTakeProfitValue(symbol, entry_price, stop_loss, take_profit, lot_size):
    # Initialize the MT5 connection
    if not mt5.initialize():
        print("Failed to initialize MT5")
        quit()

    # Ensure the symbol is available in MT5
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        mt5.shutdown()
        quit()

    # Get the symbol information
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f"Symbol information for {symbol} not found")
        mt5.shutdown()
        quit()

    # Calculate the distance in points
    sl_points = float(abs(entry_price - stop_loss)) / symbol_info.point
    tp_points = float(abs(take_profit - entry_price)) / symbol_info.point
    

    # Calculate the dollar value for SL and TP
    sl_dollar_value = sl_points * symbol_info.trade_tick_value * float(lot_size)
    tp_dollar_value = tp_points * symbol_info.trade_tick_value * float(lot_size)


    # Shutdown the MT5 connection
    mt5.shutdown()
    return {"stop_loss_value": sl_dollar_value, "take_profit_value": tp_dollar_value}


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm  # Use the custom form you created
    template_name = 'forexJournal/login.html'  # Replace with your actual template file name
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        # Fetch user's MT5 credentials
        try:
            user_credentials = mt5login.objects.get(user=user)
        except mt5login.DoesNotExist:
            print("User does not have MT5 credentials.")
            return self.form_invalid(form)

        # Initialize MT5
        if not mt5.initialize():
            print("MT5 initialization failed")
            return self.form_invalid(form)

        # Attempt to log in to MT5
        authorized = mt5.login(
            login=user_credentials.login,
            password=user_credentials.password,
            server=user_credentials.server
        )
        
        if not authorized:
            print(f"Failed to authorize with login: {user_credentials.login}, error: {mt5.last_error()}")
            mt5.shutdown()
            return self.form_invalid(form)

        # Fetch and save trades after successful login
        self.fetch_and_save_trades(user, user_credentials)

        return super().form_valid(form)

    def fetch_and_save_trades(self, user, user_credentials):
        # Define a very early date as the default from_date
        from_date = datetime(2022, 1, 1)  # Adjust as necessary
        to_date = datetime.now()  # Current date and time

        # Convert datetime to timestamp (seconds since epoch)
        
        # Fetch historical orders
        orders = mt5.history_orders_get(from_date, to_date)
        deals = mt5.history_deals_get(from_date, to_date)
        
        if orders is None:
            print(f"Failed to get orders, error: {mt5.last_error()}")
            return
        
        print(orders)
        print(deals)
        # for order in orders:
        #     position_id = order.position_id
            
            # if not TradesModel.objects.filter(ticket=position_id).exists():
            #     if position_id == 0:
            #         continue
            #     else:
            #         processing = TradesModel(
            #             user=user,
            #             ticket=order.position_id,
            #             opening_time=3
            #         )


    
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            # Create and save MT5Login
            mt5_login = mt5login(
                user=user,
                login=form.cleaned_data['mt5_login'],
                password=form.cleaned_data['mt5_password'],
                server=form.cleaned_data['mt5_server'],
            )
            mt5_login.save()

            login(request, user)  # Automatically log in the new user
            return redirect('first-page')  # Redirect to the first page after signup
    else:
        form = SignUpForm()
    return render(request, 'forexJournal/signup.html', {'form': form})

def custom_logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def forex(requests):
    print(requests.user)
    trades_instance = TradesModel.objects.all()
    account_balance, created = AccountBalance.objects.get_or_create(id=1)
    processed_profit, created = ProcessedProfit.objects.get_or_create(id=1)
    number_of_trades = TradesModel.objects.count()
    profitable_trades = TradesModel.objects.filter(profit_usd__gt=0).count()
    losing_trades = TradesModel.objects.filter(profit_usd__lt=0).count()
    total_profitable_value = TradesModel.objects.filter(profit_usd__gt=0).aggregate(Sum("profit_usd"))["profit_usd__sum"]
    rounded_total_profitable_value = round(total_profitable_value, 2)
    
    total_losing_value = TradesModel.objects.filter(profit_usd__lt=0).aggregate(Sum("profit_usd"))["profit_usd__sum"] or Decimal(0)
    rounded_losing = total_losing_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    
    if trades_instance:
        for value in trades_instance.iterator():
            symbol = value.symbol
            entry_price = value.opening_price
            take_profit_price = value.take_profit or 0
            stop_loss_value = value.stop_loss or 0
            size = value.lot_size
            value.stop_loss_value = calculateTakeProfitValue(symbol, entry_price, stop_loss_value, take_profit_price, size)["stop_loss_value"]
            value.profit_target = calculateTakeProfitValue(symbol, entry_price, stop_loss_value, take_profit_price, size)["take_profit_value"]
            value.save(update_fields=["stop_loss_value", "profit_target"])
            value.refresh_from_db()
                      
        
    
        
    winRate = (profitable_trades / number_of_trades) * PERCENT
    
    average_profit = float(rounded_total_profitable_value / profitable_trades)
    
    acc_bal = AccountBalance.objects.latest("last_update")
    current_balance = acc_bal.balance
    

    percentageIncrease = ((float(current_balance) - DEFAULT_BALANCE) / DEFAULT_BALANCE) * PERCENT
    
    if TradesModel.objects.exists():
        for trade in trades_instance:
            
            try:
                # Ensure all values are valid Decimals or default to 0 if not available
                open_price = Decimal(trade.opening_price) if trade.opening_price else Decimal('0')
                stop_loss = Decimal(trade.stop_loss) if trade.stop_loss else Decimal('0')
                take_profit = Decimal(trade.take_profit) if trade.take_profit else Decimal(1)
                
                # Calculate risk and reward
                risk = abs(open_price - stop_loss)
                reward = abs(take_profit - open_price)
                
                # Calculate the R multiple, ensuring no division by zero
                trade.planned_R_Multiple = reward / risk if risk != 0 else Decimal('0')
                trade.save()

            except (InvalidOperation, TypeError, ValueError) as e:
                # Log details of the trade causing the issue for debugging
                print(f"Error calculating RR for trade {trade.id}: {e}")
                print(f"Values - open_price: {trade.opening_price}, stop_loss: {trade.stop_loss}, take_profit: {trade.take_profit}")
                        
    
    
    
    
    
    def averageLoss():
        if losing_trades != 0:
            return abs(rounded_losing / losing_trades)
        return 0
    
    def Profitfactor():
        if rounded_losing != 0:
            return rounded_total_profitable_value / abs(rounded_losing)
        return 0
    
    average_loss = float(averageLoss())

    
    trade_expectancy = tradeExpectancy(winRate, average_profit, average_loss)
    factor = Profitfactor()
    format_factor = "{:.2f}".format(factor)
    
    average_win_loss = "{:.2f}".format(average_profit / average_loss)
    
    
    
    context = {}

    context["balance"] = account_balance.balance
    context["profit"] = Money(account_balance.profits, "USD")
    context["total_trades"] = number_of_trades
    context["profitable_trades"] = profitable_trades
    context["losing_trades"] = losing_trades
    context["profitable_value"] = rounded_total_profitable_value
    context["losing_value"] = rounded_losing
    context["win_rate"] = round(winRate, 2)
    context["expectancy"] = Money(round(trade_expectancy, 2), "USD")
    context["profit_factor"] = float(format_factor)
    context["average_win_ratio"] = average_win_loss
    context["percentageIncrease"] = round(percentageIncrease, 2)
    
    if requests.method == "POST":
        csv_file = requests.FILES.get("csv_file")
        data = pd.read_csv(csv_file)
        
        for index, row in data.iterrows():
            if not TradesModel.objects.filter(ticket=row['ticket']).exists():
                TradesModel.objects.create(
                    ticket=row['ticket'],
                    opening_time=row['opening_time_utc'],
                    closing_time=row['closing_time_utc'],
                    order_type=row['type'],
                    lot_size=row['lots'],
                    original_position_size=row['original_position_size'],
                    symbol=row['symbol'],
                    opening_price=row['opening_price'],
                    closing_price=row['closing_price'],
                    stop_loss=row['stop_loss'],
                    take_profit=row['take_profit'],
                    commission_usd=row['commission_usd'],
                    swap_usd=row['swap_usd'],
                    profit_usd=row['profit_usd'],
                    equity_usd=row['equity_usd'],
                    margin_level=row['margin_level'],
                    close_reason=row['close_reason'],
                ).save()
                

                
        amount = TradesModel.objects.aggregate(Sum("profit_usd"))
        total_amount_value = Decimal(amount["profit_usd__sum"] or 0.0)
        
        new_profit = total_amount_value - processed_profit.last_processed_profit
        account_balance.balance += new_profit # Update balance
        account_balance.profits += new_profit
        account_balance.last_update = timezone.now()  # Record the update timestamp
        account_balance.save()

                # Save the new processed profit
        processed_profit.last_processed_profit = total_amount_value
        processed_profit.save()
        
        return redirect("first-page")

        
    
    return render(requests, "forexJournal/forex.html", context)


def reports(requests):
    return render(requests, "forexJournal/reports.html")

def journal(requests):
    context = {}
    trades = TradesModel.objects.all().order_by("-id")
    for trade in trades:
        trade.profit_usd = Money(trade.profit_usd, "USD")
        
    
    context["trades"] = trades
    
    
    return render(requests, "forexJournal/journal.html", context)

def playBook(request):
    
    
    strategies_with_trade_count = StrategyModel.objects.annotate(trade_count=Count('tradesmodel'),
        total_pnl=Sum('tradesmodel__profit_usd'),
        profitable_trade_count=Count('tradesmodel', filter=Q(tradesmodel__profit_usd__gt=0)),
        profitable_trades=Sum("tradesmodel__profit_usd", filter=Q(tradesmodel__profit_usd__gt=0)),
        losing_trades=Sum("tradesmodel__profit_usd", filter=Q(tradesmodel__profit_usd__lt=0)),
    )
    
    
    
    strategies = list(StrategyModel.objects.all().values())
    
    for strategy in strategies:
        # Find the matching strategy from the annotated queryset
        matching_strategy = strategies_with_trade_count.get(id=strategy['id'])
        # Append the trade_count to the strategy dictionary
        strategy['trade_count'] = matching_strategy.trade_count
        strategy['total_pnl'] = Money(matching_strategy.total_pnl or 0, "USD")
        strategy["win_rate"] = round(calculateWinRate(matching_strategy.profitable_trade_count, matching_strategy.trade_count), 2)
        profit_factor = round(float(calculateProfitFactor(matching_strategy.profitable_trades, matching_strategy.losing_trades)), 2)
        strategy["profit_factor"] = f"{profit_factor:.2f}"
        
        
        
        
    context = {
        "strategies": strategies,
        # "number_of_trades": strategies_with_trade_count
    }
    
    
    if request.method == "POST":
        data_recieved = request.POST.dict()
        new_strategy = StrategyModel(
            strategy_name=data_recieved["Strategy-name"],
            description=data_recieved["Description"],
            risk_reward_ratio=data_recieved["risk-reward"],
            timeframe=data_recieved["time-frame"],
            indicators=data_recieved["indicators"],
            rules_follow=data_recieved["Rules-to-follow"],
            risk_management=data_recieved["Risk-management"],
            market_conditions=data_recieved["market_conditions"],
            entry_criteria=data_recieved["Entry-criteria"],
            exit_criteria=data_recieved["Exit-criteria"],
            dollar_value_risk=data_recieved["dollar-value"]
        )
        new_strategy.save()
        print("data saved successfully")
        return redirect("playBook")
    return render(request, f"{PATH}/playBook.html", context)


def allTrades(request):
    context = {}
    if request.method == "POST":
        data = json.loads(request.body)
        clicked_date = data.get("date")
        day_of_week = data.get("day")
        
        context["clicked_date"] = clicked_date
        context["day_of_week"] = day_of_week
        
        return JsonResponse({
                'status': 'success',
                'clicked_date': clicked_date,
                'day_of_week': day_of_week
        })
    return render(request, f"{PATH}/alltrades.html", context)

def rules(requests):
    return render(requests, f"{PATH}/rules.html")


def get_data(requests):
    data = list(TradesModel.objects.values())
    return JsonResponse(data, safe=False)



def trade_details(request, trade_id):
    # trade = get_object_or_404(TradesModel, ticket=trade_id)
    strategies = StrategyModel.objects.all().values()
    trade = TradesModel.objects.filter(ticket=trade_id).values().first()

    dollar_values = calculateTakeProfitValue(
        trade["symbol"], 
        trade["opening_price"], 
        trade["stop_loss"], 
        trade["take_profit"], 
        trade["lot_size"]
    )  
    profit_before_change = float(trade["profit_usd"])
    trade["symbol"] = trade["symbol"] #[:-1]
    before_change = trade["opening_time"]
    trade["opening_time"] = trade["opening_time"].strftime('%a, %b %d, %Y')
    trade["profit_usd"] =  Money(round(trade["profit_usd"], 2), "USD")             
    
    return_on_investment = (profit_before_change - float(trade["commission_usd"])) / DEFAULT_BALANCE
    return_on_investment *= PERCENT
    trade["ROI"] = round(return_on_investment, 2)
    trade["commission_usd"] = format(float(trade["commission_usd"]), ".2f")
    duration = trade["closing_time"] - before_change
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    trade["duration_hours"] = int(hours)
    trade["duration_mins"] = int(minutes)
    trade["duration_secs"] = int(seconds)
    trade["strategies"] = strategies
    trade["realisedRR"] = calculateRealisedRR(trade["opening_price"], trade["closing_price"], trade["stop_loss"])
    trade["dollar_value_profit"] = Money(dollar_values["take_profit_value"], "USD")
    trade["dollar_value_loss"] = Money(dollar_values["stop_loss_value"], "USD")
    print(trade)
    
    
    
    # strategy_used = StrategyModel.objects.get(id=trade["strategy_id"])
    try:
        strategy_used = StrategyModel.objects.get(id=trade["strategy_id"])
    except ObjectDoesNotExist:
        strategy_used = None
    
    
    trade["strategy_used"] = strategy_used
    
    
    
    
    
    
    if request.method == "POST":
        trade_update = get_object_or_404(TradesModel, ticket=trade_id)
        if "submit_quill" in request.POST:
            quill_content = request.POST.get("quill_content", "nothing was passed")
            trade_update.notes = quill_content
        elif "other_details" in request.POST:
            data = request.POST.dict()
            if data.get("tag_choices"):
                selected_tag = data.get("tag_choices") 
                trade_update.tags = selected_tag
            if data.get("setup_choices"):
                selected_strategy = data["setup_choices"]
                selected_strategy_name = StrategyModel.objects.get(strategy_name=selected_strategy)
                trade_update.strategy = selected_strategy_name
        trade_update.save()
        return redirect("trade-details", trade_id=trade_id)
    return render(request, f"{PATH}/tradeDetails.html", trade)



def strategy_reports(request, strategy_id):
    strategy = StrategyModel.objects.get(id=strategy_id)
    trades = TradesModel.objects.filter(strategy=strategy_id)
    profitable = trades.filter(profit_usd__gt=0).count()
    total_trades = trades.count()
    
    average_profit = trades.filter(profit_usd__gt=0).aggregate(Avg("profit_usd"))["profit_usd__avg"]
    average_loss = trades.filter(profit_usd__lt=0).aggregate(Avg("profit_usd"))["profit_usd__avg"]
    
    def most_profitable_pair():
        # Assuming profit is a field in your Trade model
        pairs = trades.values('symbol').annotate(total_profit=Sum('profit_usd')).order_by('-total_profit')
        return pairs.first() if pairs.exists() else (None, 0)

    # def most_profitable_day():
    #     # Assuming trade_date is a DateField in your Trade model
    #     days = trades.extra(select={'day': 'DATE(opening_time)'}).values('day').annotate(total_profit=Sum('profit_usd')).order_by('-total_profit')
    #     return days.first() if days.exists() else (None, 0)

    def get_most_profitable_day():
        profit_by_day = (
            trades
            .annotate(day_of_week=Case(
                When(opening_time__week_day=2, then=Value('Monday')),
                When(opening_time__week_day=3, then=Value('Tuesday')),
                When(opening_time__week_day=4, then=Value('Wednesday')),
                When(opening_time__week_day=5, then=Value('Thursday')),
                When(opening_time__week_day=6, then=Value('Friday')),
                When(opening_time__week_day=7, then=Value('Saturday')),
                When(opening_time__week_day=1, then=Value('Sunday')),
                output_field=CharField()
            ))
            .values('day_of_week')
            .annotate(total_profit=Sum('profit_usd'))
        )

        profit_list = list(profit_by_day)

        most_profitable_day = max(profit_list, key=lambda x: x['total_profit'], default=None)

        return most_profitable_day['day_of_week'] if most_profitable_day["day_of_week"] else None

    def get_most_losing_day():
        profit_by_day = (
            trades
            .annotate(day_of_week=Case(
                When(opening_time__week_day=2, then=Value('Monday')),
                When(opening_time__week_day=3, then=Value('Tuesday')),
                When(opening_time__week_day=4, then=Value('Wednesday')),
                When(opening_time__week_day=5, then=Value('Thursday')),
                When(opening_time__week_day=6, then=Value('Friday')),
                When(opening_time__week_day=7, then=Value('Saturday')),
                When(opening_time__week_day=1, then=Value('Sunday')),
                output_field=CharField()
            ))
            .values('day_of_week')
            .annotate(total_profit=Sum('profit_usd'))
        )

        

        most_losing_day = min(profit_by_day, key=lambda x: x['total_profit'], default=None)
        return most_losing_day['day_of_week'] if most_losing_day else None

    def get_trade_data():
        # Query to retrieve trades with opening date and profit
        new_form_trade = (
            trades.values(
                date=F('opening_time__date'),  # Extract the date part only
                pnl=F('profit_usd')
            )
        )

        # Format the trade data into the required structure
        trade_data = [
            {'date': trade['date'].strftime('%Y-%m-%d'), 'pnl': float(trade['pnl'])}
            for trade in new_form_trade
        ]
        
        return trade_data    
    
    
    
    
    def most_traded_pair():
        counter = (
            trades.values("symbol")
            .annotate(pair_count=Count("symbol"))
            .order_by("-pair_count")
        )
        
        if counter.exists():
            most_traded = counter.first()
            return most_traded["symbol"], most_traded["pair_count"]
        else:
            return None, 0
    
    
    def calculate_average_trade_duration_excluding_weekends():
        # Get trades for the strategy
        
        total_duration = timedelta(0)
        count = 0

        # Loop through each trade and calculate weekday duration
        for trade in trades:
            entry_date = trade.opening_time.date()
            exit_date = trade.closing_time.date()
            
            # Calculate business days between entry and exit
            business_days = np.busday_count(entry_date, exit_date)
            
            # Estimate daily duration as trade's total duration divided by business days
            total_trade_duration = (trade.closing_time - trade.opening_time)
            
            # Scale total duration to weekdays
            weekday_duration = total_trade_duration * (business_days / ((exit_date - entry_date).days or 1))
            
            total_duration += weekday_duration
            count += 1

        # Calculate average duration if there are any trades
        avg_duration = total_duration / count if count else timedelta(0)
        
        # Convert to hours, minutes, and seconds
        total_seconds = int(avg_duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format the output string
        return f"{hours}hrs {minutes}min {seconds}secs"
        
    
    
    
    def calculate_total_RR():
        total_rr = Decimal(0)
        
        for trade in trades:
            total_rr += trade.planned_R_Multiple
            
        return total_rr
    
    
    def consecutiveWins():
        max_consecutive_wins = 0
        current_streak = 0
        new_form = trades.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd > 0:
                current_streak += 1
                max_consecutive_wins = max(current_streak, max_consecutive_wins)
        
        return max_consecutive_wins
    
    def consecutiveLoss():
        max_consecutive_loss = 0
        current_streak = 0
        new_form = trades.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd < 0:
                current_streak += 1
                max_consecutive_loss = max(current_streak, max_consecutive_loss)
        
        return max_consecutive_loss
        
    most_profitable_day = get_most_profitable_day()
    most_losing_day = get_most_losing_day()
    data = get_trade_data()

    
    symbol_data = list(set((obj.symbol for obj in trades.iterator())))
    
    symbol_data_values = []
    
    def sum_of_symbol(symbol):
        total = 0
        for values in trades.filter(symbol=symbol).iterator():
            total += values.profit_usd
            
        return total
    
    for symbol in symbol_data:
        value = sum_of_symbol(symbol)
        symbol_data_values.append(float(value))
    
    
    
    
    context = {}
    
    context["name"] = strategy.strategy_name
    context["trades_total"] = total_trades
    context["profitable_trades"] = profitable
    context["losing_trades"] = trades.filter(profit_usd__lt=0).count()
    context["pnl"] = Money(trades.aggregate(total_pnl=Sum('profit_usd'))['total_pnl'] or 0, "USD")
    context["buys"] = trades.filter(order_type="buy").count()
    context["sells"] = trades.filter(order_type="sell").count()
    context["win_rate"] = calculateWinRate(profitable, total_trades)
    context["largest_profit"] = Money(trades.filter(profit_usd__gt=0).aggregate(Max("profit_usd"))["profit_usd__max"], "USD")
    context["largest_loss"] = Money(trades.filter(profit_usd__lt=0).aggregate(Max("profit_usd"))["profit_usd__max"], "USD")
    context["avg_profit"] = Money(average_profit, "USD")
    context["avg_loss"] = Money(average_loss, "USD")
    context["max_con_wins"] = consecutiveWins()
    context["max_con_loss"] = consecutiveLoss()
    context["trade_expectancy"] = Money(tradeExpectancy(context["win_rate"], float(average_profit),  abs(float(average_loss))), "USD")
    context["total_rr"] = calculate_total_RR()
    context["average_duration"] = calculate_average_trade_duration_excluding_weekends()
    context["most_traded"], context["pair_count"] = most_traded_pair()
    context['most_profitable'] = most_profitable_pair()["symbol"]
    context['most_profitable_day'] = most_profitable_day
    context['most_losing_day'] = most_losing_day 
    context["trade_data"] = data                
    context["bar_chart_symbols"] = symbol_data
    context["bar_chart_values"] = symbol_data_values if symbol_data_values else 0
    context["all_trades"] = trades
    context["winning_buys"] = trades.filter(order_type="buy", profit_usd__gt=0).count()
    context["winning_sells"] = trades.filter(order_type="sell", profit_usd__gt=0).count()
   
        
    
    return render(request, f"{PATH}/strategyReports.html", context)
    
    

def sync_MT5(request):
    print("MT5 sync function started", flush=True)
    
    if request.method == "POST":
        mt5_login = request.POST.get("mt5_login")
        mt5_password =  request.POST.get("mt5_password")
        mt5_server =  request.POST.get("mt5_server")
        
        # Initialize MT5 connection
        print(f"Initializing MT5 with login: {mt5_login}, server: {mt5_server}", flush=True)
        if not mt5.initialize(login=int(mt5_login), password=str(mt5_password), server=mt5_server):
            messages.error(request, "Failed to initialize MT5")
            print("MT5 initialization failed", flush=True)
            return redirect(request.META.get("HTTP_REFERER", "/"))
        
        # Authorize login
        authorised = mt5.login(login=int(mt5_login), password=mt5_password, server=mt5_server)
        if not authorised:
            error_code, error_description = mt5.last_error()
            messages.error(request, f"MT5 login failed. Error: {error_code} - {error_description}")
            print(f"MT5 login failed: {error_code} - {error_description}", flush=True)
            return redirect(request.META.get("HTTP_REFERER", "/"))
        
        # Get account info
        account_info = mt5.account_info()
        if account_info is None:
            messages.error(request, "Failed to retrieve account info")
            print("Failed to retrieve account info", flush=True)
            return redirect(request.META.get("HTTP_REFERER", "/"))
        
        print(f"Logged into account #{account_info.login}", flush=True)
        print(f"Account balance: {account_info.balance}", flush=True)
        
        from_date = datetime(2023, 1, 1)  # Replace with the desired start date
        to_date = datetime.now()
        
        trade_history = mt5.history_deals_get(from_date, to_date)
        if trade_history is None:
            messages.error(request, "Unable to retrieve trade history")
            print("Failed to retrieve trade history", flush=True)
        else:
            print(f" {trade_history}", flush=True)
        
        messages.success(request, "MT5 synced successfully")
        print("MT5 sync function completed successfully", flush=True)
        
        # Shutdown MT5 connection
        mt5.shutdown()
        print("MT5 connection closed", flush=True)
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponse('Invalid request', status=400)



def backtestingPage(request):
    return render(request, f"{PATH}/backtestingPage.html")



def fetch_historical_data(request):
    # Connect to MT5
    if not connect_to_mt5():
        print("failed to connect")
        return JsonResponse({'error': 'Failed to connect to MT5'}, status=500)

    symbol = "GBPUSDm"  # Replace with your symbol
    timeframe = mt5.TIMEFRAME_H1  # Replace with your timeframe
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)  # Fetch data for the last 30 days

    # Check if symbol is available
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Symbol {symbol} is not available in Market Watch.")
        mt5.shutdown()
        return JsonResponse({'error': f'Symbol {symbol} not available in Market Watch'}, status=404)

    # Fetch rates
    rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
    if rates is None or len(rates) == 0:
        logger.error("No data returned from MT5")
        mt5.shutdown()
        return JsonResponse({'error': 'Failed to retrieve data from MT5'}, status=500)

    # Convert rates to list of dictionaries for JSON response
    historical_data = [
        {
            'time': int(rate['time']),
            'open': float(Decimal(rate['open']).quantize(Decimal('0.00000'))),
            'high': float(Decimal(rate['high']).quantize(Decimal('0.00000'))),
            'low': float(Decimal(rate['low']).quantize(Decimal('0.00000'))),
            'close': float(Decimal(rate['close']).quantize(Decimal('0.00000')))
        }
        for rate in rates
    ]
    
    # Clean up MT5 session
    mt5.shutdown()

    return JsonResponse(historical_data, safe=False)