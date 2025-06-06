from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.templatetags.static import static as static_tag

from . import views


urlpatterns = [
    # path("signup/", views.signup, name="signup"),
    path('get-journal-note/<int:trade_id>', views.get_journal_note, name='get_journal_entry'),
    path("save-journal", views.save_journal_entry, name="save-journal"),
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
    path("settings", views.settingsPage, name="settings"),
    path("set-balance", views.set_Initial_balance, name="set-balance"),
    path('fetch-historical-data/', views.fetch_historical_data, name='fetch_historical_data'),
    path('favicon.ico', RedirectView.as_view(url=static_tag('forexJournal/images/favicon.ico'))),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
