from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import TradesModel, AccountBalance, ProcessedProfit, StrategyModel, Profile, mt5login
from django.db.models import Sum, Count, Q, Max, Avg, F, Case, When, Value, CharField, Min, ExpressionWrapper, DurationField
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.utils import timezone
from django.shortcuts import redirect
from django.http import JsonResponse
import json
import math
import numpy as np
# import MetaTrader5 as mt5
import requests
from django.apps import apps
from djmoney.money import Money
from django.core.exceptions import ObjectDoesNotExist  
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta
import numpy as np
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import SignUpForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, LoginForm, NewSignUpForm

from django.core.exceptions import ValidationError
from io import StringIO
from django.db.models.functions import TruncDate, ExtractWeekDay
from django.db import IntegrityError
from django.db import transaction
from django.contrib.auth.hashers import check_password


import logging

logger = logging.getLogger(__name__)
# Create your views here.

def get_order_type_name(order_type):
    order_type_mapping = {
        0: "Buy",
        1: "Sell",
        2: "Buy Limit",
        3: "Sell Limit",
        4: "Buy Stop",
        5: "Sell Stop",
        6: "Buy Stop Limit",
        7: "Sell Stop Limit"
    }
    return order_type_mapping.get(order_type, "Unknown")





PATH = "forexJournal"
PERCENT = 100
ACCOUNT_BALANCE = apps.get_model("forexJournal", "AccountBalance")
# DEFAULT_BALANCE =     # ACCOUNT_BALANCE._meta.get_field("balance").default

def convertXLSXFILE(file_path):
    xls = pd.ExcelFile(file_path)


    df = pd.read_excel(xls, sheet_name=0)

    data = df.values.tolist()

    start_pos = None
    end_pos = None

    for row in data:
        if "Positions" in str(row):
            start_pos = data.index(row)
        if "Orders" in str(row):
            end_pos = data.index(row)
            break

    extracted_data = ""
    if start_pos is not None and end_pos is not None:
        extracted_data = data[start_pos + 1:end_pos]

    # Create DataFrame from extracted data
    extracted_df = pd.DataFrame(extracted_data)

    # Return DataFrame
    return extracted_df


    

def extract_positons(csv_data):
    lines = csv_data.splitlines()

    # Find the position of "Positions" and "Orders"
    start_pos = None
    end_pos = None

    for i, line in enumerate(lines):
        if "Positions" in line:
            start_pos = i
        if "Orders" in line:
            end_pos = i
            break

    # Extract everything under "Positions" and stop at "Orders"
    positions_data = lines[start_pos + 1:end_pos]

    # Join the extracted lines to form the result
    positions_text = "\n".join(positions_data)

    print(positions_text)


def calculateWinRate(profitableTrades, number_of_trades):
    if number_of_trades == 0:
        return "N/A"
    return round((profitableTrades / number_of_trades) * PERCENT, 2)


def calculateProfitFactor(profitable_value, losing_value):
    if losing_value != 0:
        return round(profitable_value / abs(losing_value), 2)
    return "N/A"


def tradeExpectancy(win_rate, average_profit, average_loss):
    if win_rate == "N/A" or average_profit == "N/A" or average_loss == "N/A":
        return 0
    win_rate_decimal = win_rate / 100
    return (win_rate_decimal * average_profit) - ((1 - win_rate_decimal) * average_loss)

def calculateRealisedRR(open_price, close_price, stop_loss):
    stop_loss_value = Decimal(stop_loss) if stop_loss else Decimal("0")
    risk = abs(open_price - stop_loss_value)
    reward = abs(close_price - open_price)
    
    return round(reward / risk if risk != 0 else Decimal("0"), 2)
    
    
    

# def get_pip_value_by_containment(symbol):
    
#     pip_values = {
#         # Forex Pairs (Currency pip values)
#         "EURUSD": 0.0001,
#         "GBPUSD": 0.0001,
#         "USDJPY": 0.01,
#         "XAUUSD": 0.01,  # Gold
#         "USDCAD": 0.0001,
#         "AUDUSD": 0.0001,
#         "CADJPY": 0.01,
        
#         # Commodities
#         "XAGUSD": 0.001,  # Silver
#         "WTI": 0.01,      # Crude Oil
#         "BRENT": 0.01,    # Brent Oil
        
#         # Indices
#         "US30": 1.0,       # Dow Jones
#         "SPX500": 0.1,     # S&P 500
#         "NAS100": 0.1,     # NASDAQ
        
#         # Stocks (Point value assumed as 1 for most equities)
#         "AAPL": 1.0,
#         "MSFT": 1.0,
#         "TSLA": 1.0,
#     }
#     """
#     Retrieve the pip value by checking if the pip_values key matches the symbol.

#     :param symbol: str, instrument symbol (e.g., "GBPUSD.pro" or "US30m")
#     :return: float, pip value
#     """
#     normalized_symbol = symbol.upper()  # Ensure case-insensitive matching

#     # Iterate through pip_values keys to find a match
#     for key in pip_values:
#         if all(char in normalized_symbol for char in key):  # Check character containment
#             return pip_values[key]
    
#     # If no match is found, raise an error
#     raise ValueError(f"No pip value found for symbol: {symbol}")


# def calculateTakeProfitValue(symbol, entry_price, stop_loss, take_profit, lot_size):
    
    
#     if not mt5.initialize():
#         print("Failed to initialize MT5")
#         quit()

#     # Ensure the symbol is available in MT5
#     if not mt5.symbol_select(symbol, True):
#         print(f"Failed to select symbol {symbol}")
#         mt5.shutdown()
#         quit()

#     # Get the symbol information
#     symbol_info = mt5.symbol_info(symbol)
#     print(f"This is symbol info: {symbol_info}")

#     if symbol_info is None:
#         print(f"Symbol information for {symbol} not found")
#         mt5.shutdown()
#         quit()

#     # Calculate the distance in points
#     sl_points = float(abs(entry_price - stop_loss)) / symbol_info.point
#     tp_points = float(abs(take_profit - entry_price)) / symbol_info.point
    
#     print(f"This is sl_points {sl_points}")
#     print(f"This is tp_points {tp_points}")
#     print(f"This is trade_tick_value {symbol_info.trade_tick_value}")
#     print(f"this is symbol infp point {symbol_info.point}")
    

#     # Calculate the dollar value for SL and TP
#     sl_dollar_value = sl_points * symbol_info.trade_tick_value * float(lot_size)
#     tp_dollar_value = tp_points * symbol_info.trade_tick_value * float(lot_size)


#     # Shutdown the MT5 connection
#     mt5.shutdown()
#     return {"stop_loss_value": sl_dollar_value, "take_profit_value": tp_dollar_value}


@csrf_exempt
def set_Initial_balance(request):
    
    logged_in_user = request.user
    if request.method == "POST":
        user_account = get_object_or_404(AccountBalance, user=logged_in_user)
        if "deposit" in request.POST:
            amount = request.POST.get("Deposit", 0)
            user_account.deposit(Decimal(amount))
            print(request.POST)
            return redirect("first-page")
        elif "withdraw" in request.POST:
            amount2 = request.POST.get("Withdraw", 0)
            user_account.withdraw(Decimal(amount2))
            print(request.POST)
            return redirect("first-page")
    return JsonResponse({"success": False, "error": "Invalid Request"})

def auth_view(request):
    signup_form = NewSignUpForm()
    login_form = LoginForm()

    if request.method == 'POST':
          # Sign-up form submitted
        if 'signup' in request.POST:  # Sign-up form submitted
            signup_form_with_data = NewSignUpForm(data=request.POST)
            # signup_form = NewSignUpForm(request.POST)
            if signup_form_with_data.is_valid():
                user = signup_form_with_data.save()  
                login(request, user)  
                return redirect('first-page')  
            else:
                print("Signup form invalid:", signup_form_with_data.errors)
                return render(request, f"{PATH}/login2.html", {"signup_form": signup_form_with_data})
        elif 'login' in request.POST:  
            login_form_with_data = LoginForm(request, data=request.POST)
            if login_form_with_data.is_valid():
                user = authenticate(
                    username=login_form_with_data.cleaned_data['username'],
                    password=login_form_with_data.cleaned_data['password']
                )
                if user is not None:
                    login(request, user)
                    return redirect('first-page')  # Redirect to the dashboard after login
                else:
                    print("We don't know you")
            else:
                print("Login form errors:", login_form_with_data.errors)
                return render(request, f'{PATH}/login2.html', {'login_form': login_form_with_data})
                
    context = {
        'signup_form': signup_form, 
        'login_form': login_form
    }
    
    print(context)

    return render(request, f'{PATH}/login2.html', context)




def custom_logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def forex(request):
    logged_in_user = request.user
    trades_instance = TradesModel.objects.filter(user=logged_in_user)
    acc_bal = AccountBalance.objects.filter(user=logged_in_user)
    account_balance, created = AccountBalance.objects.get_or_create(user=logged_in_user)
    processed_profit, created = ProcessedProfit.objects.get_or_create(user=logged_in_user)
    number_of_trades = trades_instance.count()
    profit = trades_instance.filter(profit_usd__gt=0)
    loss = trades_instance.filter(profit_usd__lt=0)
    profitable_trades = profit.count()
    losing_trades = loss.count()
    total_profitable_value = profit.aggregate(Sum("profit_usd"))["profit_usd__sum"]
    rounded_total_profitable_value = round(total_profitable_value, 2) if total_profitable_value else 0
    
    total_losing_value = loss.aggregate(Sum("profit_usd"))["profit_usd__sum"] or Decimal(0)
    rounded_losing = total_losing_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    
    
    
    # if trades_instance:
    #     for value in trades_instance.iterator():
    #         symbol = value.symbol
    #         entry_price = value.opening_price
    #         take_profit_price = value.take_profit or 0
    #         stop_loss_value = value.stop_loss or 0
    #         size = value.lot_size
    #         value.stop_loss_value = calculateTakeProfitValue(symbol, entry_price, stop_loss_value, take_profit_price, size)["stop_loss_value"]
    #         value.profit_target = calculateTakeProfitValue(symbol, entry_price, stop_loss_value, take_profit_price, size)["take_profit_value"]
    #         value.save(update_fields=["stop_loss_value", "profit_target"])
    #         value.refresh_from_db()
                      
        
    
    winRate = calculateWinRate(profitable_trades, number_of_trades)
    # winRate = (profitable_trades / number_of_trades) * PERCENT
    
    average_profit = float(rounded_total_profitable_value / profitable_trades) if profitable_trades != 0 else 0
    
    
    acc_balance = acc_bal.latest("last_update")
    current_balance = acc_balance.balance

    default_balance = acc_balance.deposited_value()
    print(default_balance)

    percentageIncrease = ((float(current_balance) - float(default_balance)) / float(default_balance)) * PERCENT  if default_balance else 0
    
    if trades_instance.exists():
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
    
    average_win_loss = "{:.2f}".format(average_profit / (average_loss or 1))
    
    def get_trade_data():
        # Query to retrieve trades with opening date and profit
        new_form_trade = (
            trades_instance.values(
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
    
    t_data = get_trade_data()
    # Get the trade with the highest profit
    
    def highestWinProfit():
        highest_profit = trades_instance.order_by("-profit_usd").first()
        
        if highest_profit:
            return {
                "symbol": highest_profit.symbol,
                "profit": highest_profit.profit_usd
            }
        else:
            return {
                "symbol": None,
                "profit": None
            }
    
    highest_win = highestWinProfit()
    # max winning streak and max losing streak
    
    # When refining define this one outside to be used by multiple views
    def consecutiveWins():
        max_consecutive_wins = 0
        current_streak = 0
        new_form = trades_instance.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd > 0:
                current_streak += 1
                max_consecutive_wins = max(current_streak, max_consecutive_wins)
            else:
                current_streak = 0
                
        return max_consecutive_wins
    
    # When refining define this one outside to be used by multiple views
    def consecutiveLoss():
        max_consecutive_loss = 0
        current_streak = 0
        new_form = trades_instance.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd < 0:
                current_streak += 1
                max_consecutive_loss = max(current_streak, max_consecutive_loss)
            else:
                current_streak = 0
        
        return max_consecutive_loss
    
    
    healthy_trades = trades_instance.filter(tags="Healthy trade").count()
    lucky_trades = trades_instance.filter(tags="Lucky trade").count()
    healthy_loss = trades_instance.filter(tags="Healthy loss").count()
    bad_trades = trades_instance.filter(tags="Bad trade").count()
    missed_trades = trades_instance.filter(tags="Missed trade").count()
    untagged_trades = trades_instance.filter(tags__isnull=True).count() | trades_instance.filter(tags="").count()
    
    
    context = {}

    context["balance"] = Money(account_balance.balance, "USD")
    context["profit"] = Money(account_balance.profits, "USD")
    context["total_trades"] = number_of_trades
    context["profitable_trades"] = profitable_trades
    context["losing_trades"] = losing_trades
    context["profitable_value"] = Money(rounded_total_profitable_value, "USD")
    context["losing_value"] = Money(rounded_losing, "USD")
    context["win_rate"] = round(winRate, 2) if winRate != "N/A" else 0.00
    context["expectancy"] = Money(round(trade_expectancy, 2), "USD")
    context["profit_factor"] = float(format_factor)
    context["average_win_ratio"] = average_win_loss
    context["percentageIncrease"] = round(percentageIncrease, 2)
    context["cumulative_data"] = t_data
    context["max_winning_streak"] = consecutiveWins()
    context["max_losing_streak"] = consecutiveLoss()
    context["highest_profit_symbol"] = highest_win["symbol"]
    context["highest_profit_value"] = Money(highest_win["profit"] or 0, "USD") 
    context["healthy_trade"] = healthy_trades
    context["lucky_trade"] = lucky_trades
    context["healthy_loss"] = healthy_loss
    context["bad_trade"] = bad_trades
    context["Missed_trade"] = missed_trades
    context["untagged_trades"] = untagged_trades
    context["user"] = logged_in_user
    
    entered_password = "Asdf35761K"
    stored_hash = "pbkdf2_sha256$870000$ndqxDGErwI83qzW4H0qDvH$vygdgtfN/sypX/Gryr2yjgoVhZAOZS4J2icQayQAnaY="
    
    is_correct = check_password(entered_password, stored_hash)
    print(f"{is_correct}")
    
    def safe_decimal(value, decimal_places=2, default=Decimal("0.00")):
        try:
            if (
                value in (None, '', 'NaN', 'nan') or
                (isinstance(value, float) and math.isnan(value)) or
                (isinstance(value, np.generic) and np.isnan(value))
            ):
                value = default
            return Decimal(str(value)).quantize(Decimal(f"1.{'0'*decimal_places}"))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal(default).quantize(Decimal(f"1.{'0'*decimal_places}"))

        
    def update_balance():
        amount = trades_instance.aggregate(Sum("profit_usd"))
        total_amount_value = Decimal(amount["profit_usd__sum"] or 0.0)
        
        
        
        new_profit = total_amount_value - processed_profit.last_processed_profit
        account_balance.balance += new_profit # Update balance
        account_balance.profits += new_profit
        account_balance.last_update = timezone.now()  # Record the update timestamp
        account_balance.save()
        print("Balance has been updated Successfully")

        # Save the new processed profit
        processed_profit.last_processed_profit = total_amount_value
        processed_profit.save()
    
    
    if request.method == "POST":
        broker_name = request.POST.get("broker")
        csv_file = request.FILES.get("csv_file")
        trades_saved = False

        trades_instance = TradesModel.objects.filter(user=logged_in_user)
        processed_profit, _ = ProcessedProfit.objects.get_or_create(user=logged_in_user)
        account_balance, _ = AccountBalance.objects.get_or_create(user=logged_in_user)

        
        
        try:
            with transaction.atomic():
                if broker_name.lower() == "exness":
                    data = pd.read_csv(csv_file)
                    for _, row in data.iterrows():
                        if not trades_instance.filter(ticket=row['ticket']).exists():
                            trade = TradesModel(
                                user=logged_in_user,
                                ticket=row['ticket'],
                                opening_time=row['opening_time_utc'],
                                closing_time=row['closing_time_utc'],
                                order_type=row['type'],
                                lot_size=safe_decimal(row['lots'], 3),
                                original_position_size=safe_decimal(row['original_position_size'], 3),
                                symbol=row['symbol'],
                                opening_price=safe_decimal(row['opening_price'], 5),
                                closing_price=safe_decimal(row['closing_price'], 5),
                                stop_loss=safe_decimal(row['stop_loss'], 5),
                                take_profit=safe_decimal(row['take_profit'], 5),
                                commission_usd=safe_decimal(row['commission_usd'], 3),  # keep full, DB will enforce
                                swap_usd=safe_decimal(row['swap_usd'], 4),
                                profit_usd=safe_decimal(row['profit_usd'], 3),
                                equity_usd=safe_decimal(row['equity_usd'], 3),
                                margin_level=safe_decimal(row['margin_level']),
                                close_reason=row['close_reason'],
                            )
                            trade.full_clean()
                            trade.save()
                            trades_saved = True

                elif broker_name.lower() == "metatrader 5":
                    converted_data = convertXLSXFILE(csv_file)
                    csv_data = converted_data.to_csv(index=False, header=False)
                    data = pd.read_csv(StringIO(csv_data))

                    for _, row in data.iterrows():
                        sl = row.get("S / L", "0")
                        tp = row.get("T / P", "0")

                        sl = "0" if str(sl).lower() in ["nan", "", "none"] else sl
                        tp = "0" if str(tp).lower() in ["nan", "", "none"] else tp

                        if not trades_instance.filter(ticket=row["Position"]).exists():
                            trade = TradesModel(
                                user=logged_in_user,
                                ticket=row["Position"],
                                opening_time=datetime.strptime(row['Time'], "%Y.%m.%d %H:%M:%S"),
                                closing_time=datetime.strptime(row['Time.1'], "%Y.%m.%d %H:%M:%S"),
                                order_type=row['Type'],
                                lot_size=safe_decimal(row['Volume']),
                                original_position_size=safe_decimal(row['Volume']),
                                symbol=row['Symbol'],
                                opening_price=safe_decimal(row['Price']),
                                closing_price=safe_decimal(row['Price.1']),
                                stop_loss=safe_decimal(sl),
                                take_profit=safe_decimal(tp),
                                commission_usd=safe_decimal(row['Commission']),
                                swap_usd=safe_decimal(row['Swap']),
                                profit_usd=safe_decimal(row['Profit']),
                                equity_usd=Decimal("0.0"),
                                margin_level=Decimal("0.0"),
                                close_reason="nothing",
                            )
                            trade.full_clean()
                            trade.save()
                            trades_saved = True

                elif broker_name.lower() == "ftmo":
                    data = pd.read_csv(csv_file, delimiter=';')
                    for _, row in data.iterrows():
                        if not trades_instance.filter(ticket=row["Ticket"]).exists():
                            trade = TradesModel(
                                user=logged_in_user,
                                ticket=row["Ticket"],
                                opening_time=row['Open'],
                                closing_time=row['Close'],
                                order_type=row['Type'],
                                lot_size=safe_decimal(row['Volume']),
                                original_position_size=safe_decimal(row['Volume']),
                                symbol=row['Symbol'],
                                opening_price=safe_decimal(row['Price']),
                                closing_price=safe_decimal(row['Price.1']),
                                stop_loss=safe_decimal(row['SL']),
                                take_profit=safe_decimal(row['TP']),
                                commission_usd=safe_decimal(row['Commissions']),
                                swap_usd=safe_decimal(row['Swap']),
                                profit_usd=safe_decimal(row['Profit']),
                                equity_usd=Decimal("0.0"),
                                margin_level=Decimal("0.0"),
                                close_reason="nothing",
                            )
                            trade.full_clean()
                            trade.save()
                            trades_saved = True

                if trades_saved:
                    update_balance(trades_instance, processed_profit, account_balance)

        except Exception as e:
            print(f"BROKEN  {e}")
            return HttpResponse(f"Something went wrong while processing your trades. {e}", status=500)

        # try:
        #     with transaction.atomic():
        #         if broker_name.lower() == "exness":
        #             data = pd.read_csv(csv_file)
        #             for _, row in data.iterrows():
        #                 if not trades_instance.filter(ticket=row['ticket']).exists():
        #                     trade = TradesModel(
        #                         user=logged_in_user,
        #                         ticket=row['ticket'],
        #                         opening_time=row['opening_time_utc'],
        #                         closing_time=row['closing_time_utc'],
        #                         order_type=row['type'],
        #                         lot_size=safe_decimal(row['lots']),
        #                         original_position_size=safe_decimal(row['original_position_size']),
        #                         symbol=row['symbol'],
        #                         opening_price=safe_decimal(row['opening_price']),
        #                         closing_price=safe_decimal(row['closing_price']),
        #                         stop_loss=safe_decimal(row['stop_loss']),
        #                         take_profit=safe_decimal(row['take_profit']),
        #                         commission_usd=safe_decimal(row['commission_usd'], Decimal("0.01")),
        #                         swap_usd=safe_decimal(row['swap_usd'], Decimal("0.01")),
        #                         profit_usd=safe_decimal(row['profit_usd'], Decimal("0.01")),
        #                         equity_usd=safe_decimal(row['equity_usd']),
        #                         margin_level=safe_decimal(row['margin_level']),
        #                         close_reason=row['close_reason'],
        #                     )
        #                     trade.full_clean()
        #                     trade.save()
        #                     trades_saved = True
        #                 else:
        #                     print(f"Duplicate detected: {row['ticket']}")

        #         elif broker_name.lower() == "metatrader 5":
        #             converted_data = convertXLSXFILE(csv_file)
        #             csv_data = converted_data.to_csv(index=False, header=False)
        #             csv_buffer = StringIO(csv_data)
        #             data = pd.read_csv(csv_buffer)

        #             for _, row in data.iterrows():
        #                 sl = row.get("S / L", "0")
        #                 tp = row.get("T / P", "0")
        #                 sl = sl if str(sl).lower() != "nan" else "0"
        #                 tp = tp if str(tp).lower() != "nan" else "0"

        #                 if not trades_instance.filter(ticket=row["Position"]).exists():
        #                     trade = TradesModel(
        #                         user=logged_in_user,
        #                         ticket=row["Position"],
        #                         opening_time=datetime.strptime(row['Time'], "%Y.%m.%d %H:%M:%S"),
        #                         closing_time=datetime.strptime(row['Time.1'], "%Y.%m.%d %H:%M:%S"),
        #                         order_type=row['Type'],
        #                         lot_size=safe_decimal(row['Volume']),
        #                         original_position_size=safe_decimal(row['Volume']),
        #                         symbol=row['Symbol'],
        #                         opening_price=safe_decimal(row['Price']).quantize(Decimal('0.000001')),
        #                         closing_price=safe_decimal(row['Price.1']).quantize(Decimal('0.000001')),
        #                         stop_loss=safe_decimal(sl).quantize(Decimal('0.000001')),
        #                         take_profit=safe_decimal(tp).quantize(Decimal('0.000001')),
        #                         commission_usd=safe_decimal(row['Commission'], Decimal("0.01")),
        #                         swap_usd=safe_decimal(row['Swap'], Decimal("0.01")),
        #                         profit_usd=safe_decimal(row['Profit'], Decimal("0.01")),
        #                         equity_usd=Decimal("0.0"),
        #                         margin_level=Decimal("0.0"),
        #                         close_reason="nothing",
        #                     )
        #                     trade.full_clean()
        #                     trade.save()
        #                     trades_saved = True

        #         elif broker_name.lower() == "ftmo":
        #             data = pd.read_csv(csv_file, delimiter=';')
        #             for _, row in data.iterrows():
        #                 if not trades_instance.filter(ticket=row["Ticket"]).exists():
        #                     trade = TradesModel(
        #                         user=logged_in_user,
        #                         ticket=row["Ticket"],
        #                         opening_time=row['Open'],
        #                         closing_time=row['Close'],
        #                         order_type=row['Type'],
        #                         lot_size=safe_decimal(row['Volume']),
        #                         original_position_size=safe_decimal(row['Volume']),
        #                         symbol=row['Symbol'],
        #                         opening_price=safe_decimal(row['Price']).quantize(Decimal('0.000001')),
        #                         closing_price=safe_decimal(row['Price.1']).quantize(Decimal('0.000001')),
        #                         stop_loss=safe_decimal(row['SL']).quantize(Decimal('0.000001')),
        #                         take_profit=safe_decimal(row['TP']).quantize(Decimal('0.000001')),
        #                         commission_usd=safe_decimal(row['Commissions'], Decimal("0.01")),
        #                         swap_usd=safe_decimal(row['Swap'], Decimal("0.01")),
        #                         profit_usd=safe_decimal(row['Profit'], Decimal("0.01")),
        #                         equity_usd=Decimal("0.0"),
        #                         margin_level=Decimal("0.0"),
        #                         close_reason="nothing",
        #                     )
        #                     trade.full_clean()
        #                     trade.save()
        #                     trades_saved = True

        #         if trades_saved:
        #             update_balance(trades_instance, processed_profit, account_balance)

        # except Exception as e:
        #     print(f"Error processing file: {e}")
        #     return HttpResponse("An error occurred while processing your trades.", status=500)

        # return redirect("first-page")
    
    # if request.method == "POST":
    #     # first get the broker from which the csv data is coming from
    #     broker_name = request.POST.get("broker")
    #     csv_file = request.FILES.get("csv_file")
        
    #     if broker_name.lower() == "exness":
    #         data = pd.read_csv(csv_file)
            
    #         for index, row in data.iterrows():
    #             try:
    #                 with transaction.atomic():
    #                     print(f"Processing row: {row}")
    #                     if not trades_instance.filter(ticket=row['ticket']).exists():
    #                         trade = TradesModel(
    #                             user=logged_in_user,
    #                             ticket=row['ticket'],
    #                             opening_time=row['opening_time_utc'],
    #                             closing_time=row['closing_time_utc'],
    #                             order_type=row['type'],
    #                             lot_size=row['lots'],
    #                             original_position_size=row['original_position_size'],
    #                             symbol=row['symbol'],
    #                             opening_price=row['opening_price'],
    #                             closing_price=row['closing_price'],
    #                             stop_loss=row['stop_loss'],
    #                             take_profit=row['take_profit'],
    #                             commission_usd=row['commission_usd'],
    #                             swap_usd=row['swap_usd'],
    #                             profit_usd=row['profit_usd'],
    #                             equity_usd=row['equity_usd'],
    #                             margin_level=row['margin_level'],
    #                             close_reason=row['close_reason'],
    #                         )
    #                         trade.save()
                            
    #                         print(f"Saved trade: {trade}")
    #                     else:
    #                         print(f"Duplicate detected: {row['ticket']}")
    #                     update_balance()
    #             except Exception as e:
    #                 print(f"Error processing ticket {row['ticket']}: {e}")
                    
    #     # this is where it ends
                            
    #     elif broker_name.lower() == "metatrader 5":
    #         print(broker_name.lower())
    #         print("We got to mt5")
    #         converted_data = convertXLSXFILE(csv_file)
    #         csv_data = converted_data.to_csv(index=False, header=False)
    #         csv_buffer = StringIO(csv_data)
    #         data = pd.read_csv(csv_buffer)
    #         print(data.columns)
            
            
    #         def safe_decimal(value):
    #             try:
    #                 # Check for 'NaN' and other invalid values explicitly
    #                 if value in (None, '', 'NaN', 'nan'):
    #                     return Decimal(0)  # Or any valid value your validation expects, not Decimal(0)
    #                 return Decimal(value)
    #             except InvalidOperation:
    #                 return Decimal(0)
            
    #         for index, row in data.iterrows():
    #             sl = ""
    #             tp = ""
    #             if str(row["S / L"]).lower() == "nan":
    #                 sl = "0"
    #             else:
    #                 sl = row["S / L"]
                
    #             if str(row["T / P"]).lower() == "nan":
    #                 tp = "0"
    #             else:
    #                 tp = row["T / P"]
                
                
                
                
                
    #             if not trades_instance.filter(ticket=row["Position"]):
    #                 meta_trades = TradesModel(
    #                     user=logged_in_user,
    #                     ticket=row["Position"],
    #                     opening_time=datetime.strptime(row['Time'], "%Y.%m.%d %H:%M:%S"),
    #                     closing_time=datetime.strptime(row['Time.1'], "%Y.%m.%d %H:%M:%S"),
    #                     order_type=row['Type'],
    #                     lot_size=row['Volume'],
    #                     original_position_size=row['Volume'],
    #                     symbol=row['Symbol'],
    #                     opening_price=Decimal(row['Price']).quantize(Decimal('0.000001')),  # Round to 6 decimal places
    #                     closing_price=Decimal(row['Price.1']).quantize(Decimal('0.000001')),
    #                     stop_loss=Decimal(sl).quantize(Decimal('0.000001')),
    #                     take_profit=Decimal(tp).quantize(Decimal('0.000001')),
    #                     commission_usd=Decimal(row['Commission']).quantize(Decimal('0.01')),  # 2 decimal places
    #                     swap_usd=Decimal(row['Swap']).quantize(Decimal('0.01')),  
    #                     profit_usd=Decimal(row['Profit']).quantize(Decimal('0.01')),
    #                     equity_usd= 0,
    #                     margin_level= 0,
    #                     close_reason= "nothing",
    #                 )
    #                 meta_trades.save()
    #                 try:
    #                     # Validate the instance without saving
    #                     meta_trades.full_clean()  # Will raise ValidationError if something's wrong
    #                     # Proceed with further logic after validation, e.g., saving if needed
    #                 except ValidationError as e:
    #                     # Handle validation errors here
    #                     print(f"Validation error: {e}")
                    
            
            
    #     elif broker_name.lower() == "ftmo":
    #         data = pd.read_csv(csv_file, delimiter=';')
    #         print(data.columns)
    #         for index, row in data.iterrows():
    #             value = Decimal(str(row["Price"]))
                
    #             print(type(value), value)
                
    #             if not trades_instance.filter(ticket=row["Ticket"]):
    #                 trade = TradesModel(
    #                     user=logged_in_user,
    #                     ticket=row["Ticket"],
    #                     opening_time=row['Open'],
    #                     closing_time=row['Close'],
    #                     order_type=row['Type'],
    #                     lot_size=row['Volume'],
    #                     original_position_size=row['Volume'],
    #                     symbol=row['Symbol'],
    #                     opening_price=Decimal(row['Price']).quantize(Decimal('0.000001')),  # Round to 6 decimal places
    #                     closing_price=Decimal(row['Price.1']).quantize(Decimal('0.000001')),
    #                     stop_loss=Decimal(row['SL']).quantize(Decimal('0.000001')),
    #                     take_profit=Decimal(row['TP']).quantize(Decimal('0.000001')),
    #                     commission_usd=Decimal(row['Commissions']).quantize(Decimal('0.01')),  # 2 decimal places
    #                     swap_usd=Decimal(row['Swap']).quantize(Decimal('0.01')),  
    #                     profit_usd=Decimal(row['Profit']).quantize(Decimal('0.01')),
    #                     equity_usd= 0,
    #                     margin_level= 0,
    #                     close_reason= "nothing",
    #                 )
                    
    #                 try:
    #                     trade.save()
    #                     print("Trade saved successfully.")
    #                 except IntegrityError as e:
    #                     print(f"Integrity error: {e}")
    #                 except Exception as e:
    #                     print(f"Error while saving trade: {e}")
                                        
        
        
    #     return redirect("first-page")

        
    return render(request, "forexJournal/forex.html", context)

@login_required
def reports(request):
    logged_in_user = request.user
    trades = TradesModel.objects.filter(user=logged_in_user)
    account_balance = AccountBalance.objects.filter(user=logged_in_user)
    user_bal = account_balance.latest("last_update")
    profits = trades.filter(profit_usd__gt=0)
    losses = trades.filter(profit_usd__lt=0)
    break_even = trades.filter(profit_usd=0).count()
    profitable_trades_sum = profits.aggregate(Sum("profit_usd"))["profit_usd__sum"] or  0
    profitable_trades_max = profits.aggregate(Max("profit_usd"))["profit_usd__max"]
    losing_trades_sum = losses.aggregate(Sum("profit_usd"))["profit_usd__sum"] or 0
    losing_trades_max = losses.aggregate(Min("profit_usd"))["profit_usd__min"]
    profitable_trades = profits.count()
    losing_trades = losses.count()
    winRate = calculateWinRate(profitable_trades, trades.count())
    commissions = trades.aggregate(Sum("commission_usd"))["commission_usd__sum"] or 0
    swap = trades.aggregate(Sum("swap_usd"))["swap_usd__sum"] or  0
    
    total_pnl = trades.aggregate(Sum("profit_usd"))["profit_usd__sum"]
    average_pnl = (total_pnl / trades.count()) if trades.count() else 0
    
    
    trade_duration = trades.annotate(
        duration=ExpressionWrapper(
            F("closing_time") - F("opening_time"),
            output_field=DurationField()
        )
    )
    winning_trade_duration = profits.annotate(
        winning_duration=ExpressionWrapper(
            F("closing_time") - F("opening_time"),
            output_field=DurationField()
        )
    )
    
    losing_trade_duration = losses.annotate(
        losing_duration=ExpressionWrapper(
            F("closing_time") - F("opening_time"),
            output_field=DurationField()
        )
    )
    
    average_duration = trade_duration.aggregate(Avg("duration"))["duration__avg"]
    winning_average_duration = winning_trade_duration.aggregate(Avg("winning_duration"))["winning_duration__avg"]
    losing_average_duration = losing_trade_duration.aggregate(Avg("losing_duration"))["losing_duration__avg"]
    
    
    winning_total_secs = winning_average_duration.total_seconds() if winning_average_duration else 0
    
    w_hours = 0
    w_mins = 0
    w_secs = 0
    
    if winning_average_duration: 
        w_hours, w_remainder = divmod(winning_total_secs, 3600)
        w_mins, w_secs = divmod(w_remainder, 60)
    
    
    losing_total_secs = losing_average_duration.total_seconds() if losing_average_duration else 0
    
    
    l_hours = 0
    l_mins = 0
    l_secs = 0
    
    if losing_total_secs:
        l_hours, l_remainder = divmod(losing_total_secs, 3600)
        l_mins, l_secs = divmod(l_remainder, 60)
    
    total_secs = average_duration.total_seconds() if average_duration else 0
    hours, remainder = divmod(total_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    #One more of the above here
    
    
    def consecutiveWins():
        max_consecutive_wins = 0
        current_streak = 0
        new_form = trades.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd > 0:
                current_streak += 1
                max_consecutive_wins = max(current_streak, max_consecutive_wins)
            else:
                current_streak = 0
                
        return max_consecutive_wins
    
    # When refining define this one outside to be used by multiple views
    def consecutiveLoss():
        max_consecutive_loss = 0
        current_streak = 0
        new_form = trades.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd < 0:
                current_streak += 1
                max_consecutive_loss = max(current_streak, max_consecutive_loss)
            else:
                current_streak = 0
        
        return max_consecutive_loss
    
    # Daily average volume
    daily_volume = trades.annotate(
        date=TruncDate("opening_time")
    ).values("date").annotate(
        total_volume=Sum("lot_size")
    )
    
    total_volume = sum(day["total_volume"] for day in daily_volume)
    total_days = len(daily_volume)
    
    average_daily_volume = (total_volume / total_days) if total_days else "N/A"
    
    
    #trade count by days
    trades_by_weekday = trades.annotate(
        weekday=ExtractWeekDay('opening_time')
    ).values('weekday').annotate(
        trade_count=Count('id')
    )
    
    profits_by_weekday = trades.annotate(
        weekday=ExtractWeekDay('opening_time')  # Extract weekday as a number (1-7)
    ).values('weekday').annotate(
        total_profit=Sum('profit_usd')  # Sum profits for each day
    )

    # Step 2: Map weekday numbers to names (optional)
    weekday_names = {
        1: 'Sunday',
        2: 'Monday',
        3: 'Tuesday',
        4: 'Wednesday',
        5: 'Thursday',
        6: 'Friday',
        7: 'Saturday'
    }

    # Step 3: Replace weekday numbers with names
    result = {
        weekday_names[item['weekday']]: item['trade_count']
        for item in trades_by_weekday
    }
    
    
    result_for_profits = {
        weekday_names[item['weekday']]: item['total_profit']
        for item in profits_by_weekday
    }
    
    
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    corresponding_trade_count = []
    corresponding_trade_profit = []
    
    
    for value in days:
        corresponding_trade_count.append(result.get(f"{value}", 0))
        
    for value in days:
        corresponding_trade_profit.append(round(float(result_for_profits.get(f"{value}", 0)), 2))
    
    
    trade_days_count = trades.annotate(
        trade_days=TruncDate("opening_time")
    ).values("trade_days").distinct().count()
    
    
    daily_profits = trades.annotate(
        trade_date = TruncDate("opening_time")
    ).values("trade_date").annotate(
        total_profit=Sum("profit_usd")
    )
    
    w_days_count = daily_profits.filter(total_profit__gt=0).count()
    l_days_count = daily_profits.filter(total_profit__lt=0).count()
    
    context = {}
    average_winning_trades = (profitable_trades_sum / profitable_trades) if profitable_trades else 0
    average_losing_trades = (losing_trades_sum / losing_trades) if losing_trades else 0
    context["total_pnl"] = Money(user_bal.profits, "USD")
    context["total_trades"] = trades.count()
    context["winning_trades"] = profitable_trades
    context["losing_trades"] = losing_trades
    context["break_even"] = break_even
    context["win_rate"] = winRate
    context["average_winning_trade"] = Money(average_winning_trades or Decimal(0), "USD")
    context["average_losing_trade"] = Money(average_losing_trades or 0, "USD")
    context["commisions"] = Money(commissions or 0, "USD")
    context["swap"] = Money(swap or 0, "USD")
    context["total_fees"] = Money((commissions + swap) or 0, "USD")
    context["largest_profit"] = Money(profitable_trades_max or 0, "USD")
    context["largest_loss"] = Money(losing_trades_max or 0, "USD")
    context["average_hold_hours"] = int(hours)
    context["average_hold_minutes"] = int(minutes)
    context["average_hold_seconds"] = int(seconds)
    context["average_win_hours"] = int(w_hours)
    context["average_win_minutes"] = int(w_mins)
    context["average_win_seconds"] = int(w_secs)
    context["average_loss_hours"] = int(l_hours)
    context["average_loss_minutes"] = int(l_mins)
    context["average_loss_seconds"] = int(l_secs)
    context["max_consecutive_wins"] = consecutiveWins()
    context["max_consecutive_loss"] = consecutiveLoss()
    context["average_daily_volume"] = average_daily_volume
    context["trade_distribution"] = corresponding_trade_count
    context["trade_profit"] = corresponding_trade_profit
    context["average_pnl"] = Money(average_pnl, "USD")
    context["profit_factor"] = calculateProfitFactor(profitable_trades_sum, losing_trades_sum)
    context["total_trading_days"] = trade_days_count
    context["number_of_win_days"] = w_days_count
    context["number_of_loss_days"] = l_days_count
    
    
    return render(request, "forexJournal/reports.html", context)

@login_required
def journal(request):
    logged_in_user = request.user
    context = {}
    trades = TradesModel.objects.filter(user=logged_in_user).order_by("-id")
    for trade in trades:
        trade.profit_usd = Money(trade.profit_usd, "USD")
        
    
    context["trades"] = trades
    
    
    return render(request, "forexJournal/journal.html", context)

@login_required
def playBook(request):
    logged_in_user = request.user
    all_strategies = StrategyModel.objects.filter(user=logged_in_user)
    
    
    strategies_with_trade_count = all_strategies.annotate(trade_count=Count('tradesmodel'),
        total_pnl=Sum('tradesmodel__profit_usd'),
        profitable_trade_count=Count('tradesmodel', filter=Q(tradesmodel__profit_usd__gt=0)),
        profitable_trades=Sum("tradesmodel__profit_usd", filter=Q(tradesmodel__profit_usd__gt=0)),
        losing_trades=Sum("tradesmodel__profit_usd", filter=Q(tradesmodel__profit_usd__lt=0)),
    )
    
    
    
    strategies = list(strategies_with_trade_count.values())
    
    for strategy in strategies:
        # Find the matching strategy from the annotated queryset
        matching_strategy = strategies_with_trade_count.get(id=strategy['id'])
        # Append the trade_count to the strategy dictionary
        strategy['trade_count'] = matching_strategy.trade_count
        strategy['total_pnl'] = Money(matching_strategy.total_pnl or 0, "USD")
        strategy["win_rate"] = round(calculateWinRate(matching_strategy.profitable_trade_count, matching_strategy.trade_count) or 0, 2)
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

@login_required
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

@login_required
def dailyJournal(request):
    logged_in_user = request.user
    trades = TradesModel.objects.filter(user=logged_in_user).order_by("-id")
    trades_dict = trades.values()
    context = {
        "trades": trades_dict
    }
    return render(request, f"{PATH}/dailyJournal.html", context)

def get_journal_note(request, trade_id):
    try:
        logged_in_user = request.user
        note = TradesModel.objects.filter(user=logged_in_user, ticket=trade_id).first()
        return JsonResponse({"journal_content": note.notes})
    except TradesModel.DoesNotExist:
        return JsonResponse({"journal_content": ""})


def save_journal_entry(request):
    logged_in_user = request.user
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            trade_id = data['trade_id']
            journal_content = data['journal_content']
            trade = TradesModel.objects.get(user=logged_in_user, ticket=trade_id)
            trade.notes = journal_content
            trade.save()
            # Update if exists, or create a new entry if not
            # entry, created = JournalEntry.objects.update_or_create(
            #     trade_id=trade_id,
            #     defaults={'content': journal_content}
            # )
            
            return JsonResponse({'success': True, 'message': 'Journal entry saved!'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@login_required
def get_data(request):
    # sends data to the frontend 
    logged_in_user = request.user
    data = list(TradesModel.objects.filter(user=logged_in_user).values())
    return JsonResponse(data, safe=False)


@login_required
def trade_details(request, trade_id):
    logged_in_user = request.user
    account = AccountBalance.objects.filter(user=logged_in_user)
    strategy_object = StrategyModel.objects.filter(user=logged_in_user)
    strategies = strategy_object.values()
    trade = TradesModel.objects.filter(ticket=trade_id, user=logged_in_user).values().first()

    # dollar_values = calculateTakeProfitValue(
    #     trade["symbol"], 
    #     trade["opening_price"], 
    #     trade["stop_loss"], 
    #     trade["take_profit"], 
    #     trade["lot_size"]
    # )  
    
    profit_before_change = float(trade["profit_usd"])
    trade["symbol"] = trade["symbol"] #[:-1]
    before_change = trade["opening_time"]
    trade["opening_time"] = trade["opening_time"].strftime('%a, %b %d, %Y')
    trade["profit_usd"] =  Money(round(trade["profit_usd"], 2), "USD")             
    
    acc_balance = account.latest("last_update")
    default = acc_balance.deposited_value()
    return_on_investment = (profit_before_change - float(trade["commission_usd"])) / float(default)
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
    trade["dollar_value_profit"] = trade["profit_target"] or 0       # Money(dollar_values["take_profit_value"], "USD")
    trade["dollar_value_loss"] = trade["profit_target"] or 0      # Money(dollar_values["stop_loss_value"], "USD")
    print(trade)
    
    
    
    # strategy_used = StrategyModel.objects.get(id=trade["strategy_id"])
    try:
        strategy_used = strategy_object.get(id=trade["strategy_id"])
    except ObjectDoesNotExist:
        strategy_used = None
    
    
    trade["strategy_used"] = strategy_used
    
    
    
    
    
    
    if request.method == "POST":
        trade_update = get_object_or_404(TradesModel, ticket=trade_id, user=logged_in_user)
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
            if data.get("take_profit"):
                entered_profit = data["take_profit"]
                trade_update.profit_target = entered_profit
            if data.get("stop_loss"):
                entered_loss = data["stop_loss"]
                trade_update.stop_loss_value = entered_loss
        trade_update.save()
        return redirect("trade-details", trade_id=trade_id)
    return render(request, f"{PATH}/tradeDetails.html", trade)


@login_required
def strategy_reports(request, strategy_id):
    logged_in_user = request.user
    all_strategies = StrategyModel.objects.filter(user=logged_in_user)
    all_trades = TradesModel.objects.filter(user=logged_in_user)
    strategy = all_strategies.get(id=strategy_id)
    trades = all_trades.filter(strategy=strategy_id)
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
            else:
                current_streak = 0
        return max_consecutive_wins
    
    def consecutiveLoss():
        max_consecutive_loss = 0
        current_streak = 0
        new_form = trades.order_by("opening_time")
        
        for trade in new_form:
            if trade.profit_usd < 0:
                current_streak += 1
                max_consecutive_loss = max(current_streak, max_consecutive_loss)
            else:
                current_streak = 0
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
    
    
@login_required
def sync_MT5(request):
    print("MT5 sync function started", flush=True)
    
    # if request.method == "POST":
    #     mt5_login = request.POST.get("mt5_login")
    #     mt5_password =  request.POST.get("mt5_password")
    #     mt5_server =  request.POST.get("mt5_server")
        
    #     # Initialize MT5 connection
    #     print(f"Initializing MT5 with login: {mt5_login}, server: {mt5_server}", flush=True)
    #     if not mt5.initialize(login=int(mt5_login), password=str(mt5_password), server=mt5_server):
    #         messages.error(request, "Failed to initialize MT5")
    #         print("MT5 initialization failed", flush=True)
    #         return redirect(request.META.get("HTTP_REFERER", "/"))
        
    #     # Authorize login
    #     authorised = mt5.login(login=int(mt5_login), password=mt5_password, server=mt5_server)
    #     if not authorised:
    #         error_code, error_description = mt5.last_error()
    #         messages.error(request, f"MT5 login failed. Error: {error_code} - {error_description}")
    #         print(f"MT5 login failed: {error_code} - {error_description}", flush=True)
    #         return redirect(request.META.get("HTTP_REFERER", "/"))
        
    #     # Get account info
    #     account_info = mt5.account_info()
    #     if account_info is None:
    #         messages.error(request, "Failed to retrieve account info")
    #         print("Failed to retrieve account info", flush=True)
    #         return redirect(request.META.get("HTTP_REFERER", "/"))
        
    #     print(f"Logged into account #{account_info.login}", flush=True)
    #     print(f"Account balance: {account_info.balance}", flush=True)
        
    #     from_date = datetime(2023, 1, 1)  # Replace with the desired start date
    #     to_date = datetime.now()
        
    #     trade_history = mt5.history_deals_get(from_date, to_date)
    #     if trade_history is None:
    #         messages.error(request, "Unable to retrieve trade history")
    #         print("Failed to retrieve trade history", flush=True)
    #     else:
    #         print(f" {trade_history}", flush=True)
        
    #     messages.success(request, "MT5 synced successfully")
    #     print("MT5 sync function completed successfully", flush=True)
        
    #     # Shutdown MT5 connection
    #     mt5.shutdown()
    #     print("MT5 connection closed", flush=True)
        
    #     return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponse('Invalid request', status=400)


@login_required
def backtestingPage(request):
    return render(request, f"{PATH}/backtestingPage.html")


@login_required
def settingsPage(request):
    logged_in_user = request.user
    return render(request, f'{PATH}/settings.html')


@login_required
def fetch_historical_data(request):
    pass
#     # Connect to MT5
#     if not mt5.initialize():
#         print("Failed to connect. Error code:", mt5.last_error())
#         return JsonResponse({'error': 'Failed to connect to MT5'}, status=500)

#     symbol = "GBPUSDm"  # Replace with your symbol
#     timeframe = mt5.TIMEFRAME_H1  # Replace with your timeframe
#     end_time = datetime.now()
#     start_time = end_time - timedelta(days=400)  # Fetch data for the last 30 days

#     # Check if symbol is available
#     if not mt5.symbol_select(symbol, True):
#         logger.error(f"Symbol {symbol} is not available in Market Watch.")
#         mt5.shutdown()
#         return JsonResponse({'error': f'Symbol {symbol} not available in Market Watch'}, status=404)

#     # Fetch rates
#     rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
#     if rates is None or len(rates) == 0:
#         logger.error("No data returned from MT5")
#         mt5.shutdown()
#         return JsonResponse({'error': 'Failed to retrieve data from MT5'}, status=500)

#     # Convert rates to list of dictionaries for JSON response
#     historical_data = [
#         {
#             'time': int(rate['time']),
#             'open': float(Decimal(rate['open']).quantize(Decimal('0.00000'))),
#             'high': float(Decimal(rate['high']).quantize(Decimal('0.00000'))),
#             'low': float(Decimal(rate['low']).quantize(Decimal('0.00000'))),
#             'close': float(Decimal(rate['close']).quantize(Decimal('0.00000')))
#         }
#         for rate in rates
#     ]
    
#     response_data = {
#     'instrument': symbol,
#     'timeframe': '1H',  # Use a human-readable format for the timeframe
#     'data': historical_data
#     }
    
#     # Clean up MT5 session
#     mt5.shutdown()

#     return JsonResponse(response_data, safe=False)