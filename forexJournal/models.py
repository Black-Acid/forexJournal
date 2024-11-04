from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import os
# Create your models here.

class mt5login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mt5_logins")
    login = models.IntegerField()
    password = models.CharField(max_length=50)
    server = models.CharField(max_length=30)
    
    
    def save(self, *args, **kwargs):
        # Encrypt credentials before saving
        fernet = Fernet(os.getenv('FERNET_KEY'))
        if isinstance(self.login, str):
            self.mt5_login = fernet.encrypt(self.mt5_login.encode())
        if isinstance(self.password, str):
            self.mt5_password = fernet.encrypt(self.mt5_password.encode())
        if isinstance(self.mt5_server, str):
            self.mt5_server = fernet.encrypt(self.server.encode())
        
        # Call the parent class's save method
        super().save(*args, **kwargs)

    def decrypt_credentials(self):
        fernet = Fernet(os.getenv('FERNET_KEY'))
        login = fernet.decrypt(self.login).decode()
        password = fernet.decrypt(self.password).decode()
        server = fernet.decrypt(self.server).decode()
        return login, password, server
    
    
    def __str__(self) -> str:
        return f"{self.login} for {self.user.username}"
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} with {self.user.username}"

class StrategyModel(models.Model):
    strategy_name = models.CharField(max_length=100)
    description = models.TextField()
    risk_reward_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    timeframe = models.CharField(max_length=50)
    indicators = models.CharField(max_length=200, blank=True, null=True)
    average_duration = models.DurationField(blank=True, null=True)
    backtesting_perfomance = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    risk_management = models.CharField(max_length=250, null=True, blank=True)
    rules_follow = models.CharField(max_length=500, null=True, blank=True)
    market_conditions = models.CharField(max_length=15, null=True, blank=True)
    entry_criteria = models.CharField(max_length=250, null=True, blank=True)
    exit_criteria = models.CharField(max_length=250, null=True, blank=True)
    dollar_value_risk = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    
    def __str__(self) -> str:
        return f"{self.strategy_name}"



class TradesModel(models.Model):
    ticket = models.IntegerField(null=False, unique=True)
    opening_time = models.DateTimeField()
    closing_time = models.DateTimeField()
    order_type = models.CharField(null=False, blank=False, max_length=10)
    lot_size = models.DecimalField(decimal_places=2, max_digits=4)
    original_position_size = models.DecimalField(decimal_places=2, max_digits=4)
    symbol = models.CharField(max_length=8)
    opening_price = models.DecimalField(decimal_places=6, max_digits=12)
    closing_price = models.DecimalField(decimal_places=6, max_digits=12)
    stop_loss = models.DecimalField(decimal_places=6, max_digits=12)
    take_profit = models.DecimalField(decimal_places=6, max_digits=12)
    commission_usd = models.DecimalField(decimal_places=4, max_digits=5)
    swap_usd = models.DecimalField(decimal_places=3, max_digits=3)
    profit_usd = models.DecimalField(decimal_places=3, max_digits=7)
    equity_usd = models.CharField(max_length=10)
    margin_level = models.CharField(max_length=10)
    close_reason = models.CharField(max_length=10)
    strategy = models.ForeignKey(StrategyModel, on_delete=models.SET_NULL, null=True, blank=True)
    profit_target = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    stop_loss_value = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    tags = models.CharField(max_length=50, null=True, blank=True)
    planned_R_Multiple = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.symbol} {self.order_type} {self.profit_usd}" 
    
    
class AccountBalance(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    profits = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    last_update = models.DateTimeField(auto_now_add=True)  # Tracks the last update

class ProcessedProfit(models.Model):
    last_processed_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    
    
    

    