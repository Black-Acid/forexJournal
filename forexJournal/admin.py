from django.contrib import admin
from .models import TradesModel, StrategyModel, AccountBalance, ProcessedProfit, mt5login, Profile
# Register your models here.

admin.site.register(TradesModel)
admin.site.register(StrategyModel)
admin.site.register(AccountBalance)
admin.site.register(ProcessedProfit)
admin.site.register(mt5login)
admin.site.register(Profile)
