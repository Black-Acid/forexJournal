from django.shortcuts import render, get_object_or_404
import pandas as pd
from .models import TradesModel, AccountBalance, ProcessedProfit, StrategyModel
from django.db.models import Sum, Count, Q
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.shortcuts import redirect
from django.http import JsonResponse
import json
import requests
from django.apps import apps
from djmoney.money import Money
from django.core.exceptions import ObjectDoesNotExist   
# Create your views here.


PATH = "forexJournal"
PERCENT = 100
ACCOUNT_BALANCE = apps.get_model("forexJournal", "AccountBalance")
DEFAULT_BALANCE = ACCOUNT_BALANCE._meta.get_field("balance").default


def calculateWinRate(profitableTrades, number_of_trades):
    return (profitableTrades / number_of_trades) * PERCENT


def calculateProfitFactor(profitable_value, losing_value):
    if losing_value != 0:
        return profitable_value / abs(losing_value)
    return "N/A"


def tradeExpectancy(win_rate, average_profit, average_loss):
    win_rate_decimal = win_rate / 100
    return (win_rate_decimal * average_profit) - ((1 - win_rate_decimal) * average_loss)
    


def forex(requests):
    account_balance, created = AccountBalance.objects.get_or_create(id=1)
    processed_profit, created = ProcessedProfit.objects.get_or_create(id=1)
    number_of_trades = TradesModel.objects.count()
    profitable_trades = TradesModel.objects.filter(profit_usd__gt=0).count()
    losing_trades = TradesModel.objects.filter(profit_usd__lt=0).count()
    total_profitable_value = TradesModel.objects.filter(profit_usd__gt=0).aggregate(Sum("profit_usd"))["profit_usd__sum"]
    rounded_total_profitable_value = round(total_profitable_value, 2)
    
    total_losing_value = TradesModel.objects.filter(profit_usd__lt=0).aggregate(Sum("profit_usd"))["profit_usd__sum"] or Decimal(0)
    rounded_losing = total_losing_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    
    winRate = (profitable_trades / number_of_trades) * PERCENT
    
    average_profit = float(rounded_total_profitable_value / profitable_trades)
    
    acc_bal = AccountBalance.objects.latest("last_update")
    current_balance = acc_bal.balance
    

    percentageIncrease = ((float(current_balance) - DEFAULT_BALANCE) / DEFAULT_BALANCE) * PERCENT
    
    
    
    def averageLoss():
        if losing_trades != 0:
            return abs(rounded_losing / losing_trades)
        return 0
    
    def Profitfactor():
        if rounded_losing != 0:
            return rounded_total_profitable_value / abs(rounded_losing)
        return 0
    
    average_loss = float(averageLoss())
    win_rate_in_decimal = float(winRate / 100)
    
    trade_expectancy = (win_rate_in_decimal * average_profit) - ((1 - win_rate_in_decimal) * average_loss)
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
        strategy["win_rate"] = calculateWinRate(matching_strategy.profitable_trade_count, matching_strategy.trade_count)
        strategy["profit_factor"] = round(calculateProfitFactor(matching_strategy.profitable_trades, matching_strategy.losing_trades), 2)
        
        
        
        
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

    profit_before_change = float(trade["profit_usd"])
    trade["symbol"] = trade["symbol"][:-1]
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
    
    # strategy_used = StrategyModel.objects.get(id=trade["strategy_id"])
    try:
        strategy_used = StrategyModel.objects.get(id=trade["strategy_id"])
    except ObjectDoesNotExist:
        strategy_used = None
    
    
    trade["strategy_used"] = strategy_used
    print(trade)
    
    
    
    
    
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



    