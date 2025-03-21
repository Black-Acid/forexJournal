from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import os
from django.conf import settings
# Create your models here.

class mt5login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mt5_logins", default=1)
    login = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    server = models.CharField(max_length=30)
    
    
    def save(self, *args, **kwargs):
        # Encrypt credentials before saving
        fernet = Fernet(os.getenv('FERNET_KEY'))
        if isinstance(self.login, str):
            self.login = fernet.encrypt(self.login.encode())
        if isinstance(self.password, str):
            self.password = fernet.encrypt(self.password.encode())
        if isinstance(self.server, str):
            self.server = fernet.encrypt(self.server.encode())
        
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="strategies", default=1)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades", default=1)
    ticket = models.IntegerField(null=False, unique=True)
    opening_time = models.DateTimeField()
    closing_time = models.DateTimeField()
    order_type = models.CharField(null=False, blank=False, max_length=10)
    lot_size = models.DecimalField(decimal_places=7, max_digits=25)
    original_position_size = models.DecimalField(decimal_places=7, max_digits=25)
    symbol = models.CharField(max_length=20)
    opening_price = models.DecimalField(decimal_places=7, max_digits=25)
    closing_price = models.DecimalField(decimal_places=7, max_digits=25)
    stop_loss = models.DecimalField(decimal_places=7, max_digits=25)
    take_profit = models.DecimalField(decimal_places=7, max_digits=25)
    commission_usd = models.DecimalField(decimal_places=7, max_digits=25)
    swap_usd = models.DecimalField(decimal_places=7, max_digits=25)
    profit_usd = models.DecimalField(decimal_places=7, max_digits=25)
    equity_usd = models.CharField(max_length=10)
    margin_level = models.CharField(max_length=10)
    close_reason = models.CharField(max_length=10)
    strategy = models.ForeignKey(StrategyModel, on_delete=models.SET_NULL, null=True, blank=True)
    profit_target = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    stop_loss_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    tags = models.CharField(max_length=50, null=True, blank=True)
    planned_R_Multiple = models.DecimalField(max_digits=20, decimal_places=7, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.symbol} {self.order_type} {self.profit_usd}" 
    
    
class AccountBalance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account_balance", default=1)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profits = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_default_balance = models.BooleanField(default=True)
    last_update = models.DateTimeField(auto_now_add=True)  # Tracks the last update
    
    
    def deposit(self, amount):
        """Add funds to the account balance."""
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Subtract funds from the account balance, ensuring it doesn't go below zero."""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    
    def deposited_value(self):
        return self.balance - self.profits

class ProcessedProfit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  # Replace '1' with a valid user ID
    last_processed_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    
    
    

    