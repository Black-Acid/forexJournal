from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # path("signup/", views.signup, name="signup"),
    path('login/', views.auth_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path("", views.forex, name="first-page"),
    path("reports", views.reports, name="reports"),
    path("forex.html", views.forex, name="forex"),
    path("journal", views.journal, name="journal"),
    path("playBook", views.playBook, name="playBook"),
    path("All-trades", views.allTrades, name="All_trades"),
    path("daily-journal", views.dailyJournal, name="daily-journal"),
    path("get-data", views.get_data, name="get-data"),
    path("journal/<int:trade_id>", views.trade_details, name="trade-details"),
    path("strategy-reports/<int:strategy_id>", views.strategy_reports, name="strategy-reports"),
    path("sync-mt5", views.sync_MT5, name="sync"),
    path("backtesting", views.backtestingPage, name="backtest"),
    path('fetch-historical-data/', views.fetch_historical_data, name='fetch_historical_data'),
]
