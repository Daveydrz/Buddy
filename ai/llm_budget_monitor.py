"""
LLM Budget Monitor - Monitor and control LLM usage and costs
Created: 2025-01-17
Purpose: Track token usage, API costs, and implement budget controls for LLM operations
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class BudgetAlert(Enum):
    NONE = "none"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"

@dataclass
class TokenUsage:
    """Track token usage for a single request"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    timestamp: str = ""
    model: str = ""
    cost_estimate: float = 0.0
    request_type: str = "chat"
    user: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens

@dataclass
class BudgetLimits:
    """Budget limits configuration"""
    daily_cost_limit: float = 10.0
    monthly_cost_limit: float = 100.0
    daily_token_limit: int = 100000
    monthly_token_limit: int = 2000000
    per_request_token_limit: int = 4000
    warning_threshold: float = 0.8  # 80% of limit
    critical_threshold: float = 0.95  # 95% of limit

class LLMBudgetMonitor:
    """Monitor and control LLM usage and costs"""
    
    def __init__(self, config_file: str = "llm_budget_config.json", usage_file: str = "llm_usage_log.json"):
        self.config_file = config_file
        self.usage_file = usage_file
        self.budget_limits = BudgetLimits()
        self.usage_log: List[TokenUsage] = []
        
        # Token costs per model (approximate USD per 1K tokens)
        self.token_costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "llama-70b": {"input": 0.0008, "output": 0.0008},
            "mixtral-8x7b": {"input": 0.0007, "output": 0.0007},
            "default": {"input": 0.002, "output": 0.004}
        }
        
        self.load_config()
        self.load_usage_log()
        
        print(f"[LLMBudgetMonitor] 💰 Initialized with daily limit: ${self.budget_limits.daily_cost_limit}")
        
    def load_config(self):
        """Load budget configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                # Update budget limits from config
                for key, value in config_data.get('budget_limits', {}).items():
                    if hasattr(self.budget_limits, key):
                        setattr(self.budget_limits, key, value)
                        
                # Update token costs if provided
                self.token_costs.update(config_data.get('token_costs', {}))
                
                print(f"[LLMBudgetMonitor] ✅ Loaded config from {self.config_file}")
            else:
                self.save_config()
                print(f"[LLMBudgetMonitor] 📄 Created default config at {self.config_file}")
                
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error loading config: {e}")
            
    def save_config(self):
        """Save current configuration"""
        try:
            config_data = {
                "budget_limits": asdict(self.budget_limits),
                "token_costs": self.token_costs,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error saving config: {e}")
            
    def load_usage_log(self):
        """Load usage history"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    usage_data = json.load(f)
                    
                self.usage_log = [
                    TokenUsage(**entry) for entry in usage_data
                    if isinstance(entry, dict)
                ]
                
                # Clean old entries (keep last 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                self.usage_log = [
                    usage for usage in self.usage_log
                    if datetime.fromisoformat(usage.timestamp) > cutoff_date
                ]
                
                print(f"[LLMBudgetMonitor] 📊 Loaded {len(self.usage_log)} usage entries")
            else:
                print(f"[LLMBudgetMonitor] 📄 No existing usage log found")
                
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error loading usage log: {e}")
            self.usage_log = []
            
    def save_usage_log(self):
        """Save usage history"""
        try:
            usage_data = [asdict(usage) for usage in self.usage_log]
            
            with open(self.usage_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
                
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error saving usage log: {e}")
            
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for token usage"""
        try:
            model_costs = self.token_costs.get(model, self.token_costs["default"])
            
            input_cost = (input_tokens / 1000) * model_costs["input"]
            output_cost = (output_tokens / 1000) * model_costs["output"]
            
            return input_cost + output_cost
            
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error calculating cost: {e}")
            return 0.0
            
    def check_pre_request_limits(self, estimated_tokens: int, model: str, user: str) -> Tuple[bool, BudgetAlert, str]:
        """
        Check if a request would exceed budget limits before making it
        
        Returns:
            (allowed, alert_level, message)
        """
        try:
            # Check per-request token limit
            if estimated_tokens > self.budget_limits.per_request_token_limit:
                return False, BudgetAlert.EXCEEDED, f"Request exceeds per-request token limit ({estimated_tokens} > {self.budget_limits.per_request_token_limit})"
            
            # Get current usage
            daily_usage = self.get_daily_usage()
            monthly_usage = self.get_monthly_usage()
            
            # Estimate cost for this request
            estimated_cost = self.calculate_cost(estimated_tokens // 2, estimated_tokens // 2, model)
            
            # Check daily limits
            projected_daily_cost = daily_usage["total_cost"] + estimated_cost
            projected_daily_tokens = daily_usage["total_tokens"] + estimated_tokens
            
            if projected_daily_cost > self.budget_limits.daily_cost_limit:
                return False, BudgetAlert.EXCEEDED, f"Request would exceed daily cost limit (${projected_daily_cost:.4f} > ${self.budget_limits.daily_cost_limit})"
                
            if projected_daily_tokens > self.budget_limits.daily_token_limit:
                return False, BudgetAlert.EXCEEDED, f"Request would exceed daily token limit ({projected_daily_tokens} > {self.budget_limits.daily_token_limit})"
            
            # Check monthly limits
            projected_monthly_cost = monthly_usage["total_cost"] + estimated_cost
            projected_monthly_tokens = monthly_usage["total_tokens"] + estimated_tokens
            
            if projected_monthly_cost > self.budget_limits.monthly_cost_limit:
                return False, BudgetAlert.EXCEEDED, f"Request would exceed monthly cost limit (${projected_monthly_cost:.4f} > ${self.budget_limits.monthly_cost_limit})"
                
            if projected_monthly_tokens > self.budget_limits.monthly_token_limit:
                return False, BudgetAlert.EXCEEDED, f"Request would exceed monthly token limit ({projected_monthly_tokens} > {self.budget_limits.monthly_token_limit})"
            
            # Check warning thresholds
            daily_cost_ratio = projected_daily_cost / self.budget_limits.daily_cost_limit
            monthly_cost_ratio = projected_monthly_cost / self.budget_limits.monthly_cost_limit
            
            if daily_cost_ratio > self.budget_limits.critical_threshold or monthly_cost_ratio > self.budget_limits.critical_threshold:
                return True, BudgetAlert.CRITICAL, f"Approaching budget limits (daily: {daily_cost_ratio:.1%}, monthly: {monthly_cost_ratio:.1%})"
                
            if daily_cost_ratio > self.budget_limits.warning_threshold or monthly_cost_ratio > self.budget_limits.warning_threshold:
                return True, BudgetAlert.WARNING, f"Budget warning (daily: {daily_cost_ratio:.1%}, monthly: {monthly_cost_ratio:.1%})"
            
            return True, BudgetAlert.NONE, "Request within budget limits"
            
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error checking pre-request limits: {e}")
            return True, BudgetAlert.NONE, "Error checking limits - allowing request"
            
    def log_usage(self, input_tokens: int, output_tokens: int, model: str, user: str, request_type: str = "chat") -> TokenUsage:
        """Log token usage for a completed request"""
        try:
            cost = self.calculate_cost(input_tokens, output_tokens, model)
            
            usage = TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                cost_estimate=cost,
                request_type=request_type,
                user=user
            )
            
            self.usage_log.append(usage)
            
            # Save every 10 entries or if cost is significant
            if len(self.usage_log) % 10 == 0 or cost > 0.01:
                self.save_usage_log()
            
            print(f"[LLMBudgetMonitor] 📊 Logged usage: {usage.total_tokens} tokens, ${cost:.4f} for {user}")
            
            return usage
            
        except Exception as e:
            print(f"[LLMBudgetMonitor] ❌ Error logging usage: {e}")
            return TokenUsage()
            
    def get_daily_usage(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get usage statistics for a specific day"""
        if date is None:
            date = datetime.now()
            
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        daily_entries = [
            usage for usage in self.usage_log
            if start_of_day <= datetime.fromisoformat(usage.timestamp) < end_of_day
        ]
        
        total_tokens = sum(usage.total_tokens for usage in daily_entries)
        total_cost = sum(usage.cost_estimate for usage in daily_entries)
        request_count = len(daily_entries)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "request_count": request_count,
            "entries": daily_entries
        }
        
    def get_monthly_usage(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        """Get usage statistics for a specific month"""
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
            
        # Get first and last day of month
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1)
        else:
            end_of_month = datetime(year, month + 1, 1)
            
        monthly_entries = [
            usage for usage in self.usage_log
            if start_of_month <= datetime.fromisoformat(usage.timestamp) < end_of_month
        ]
        
        total_tokens = sum(usage.total_tokens for usage in monthly_entries)
        total_cost = sum(usage.cost_estimate for usage in monthly_entries)
        request_count = len(monthly_entries)
        
        return {
            "year": year,
            "month": month,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "request_count": request_count,
            "entries": monthly_entries
        }
        
    def get_usage_by_user(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics grouped by user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_entries = [
            usage for usage in self.usage_log
            if datetime.fromisoformat(usage.timestamp) > cutoff_date
        ]
        
        user_stats = {}
        for usage in recent_entries:
            user = usage.user or "unknown"
            if user not in user_stats:
                user_stats[user] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "request_count": 0,
                    "models_used": set()
                }
                
            user_stats[user]["total_tokens"] += usage.total_tokens
            user_stats[user]["total_cost"] += usage.cost_estimate
            user_stats[user]["request_count"] += 1
            user_stats[user]["models_used"].add(usage.model)
            
        # Convert sets to lists for JSON serialization
        for user in user_stats:
            user_stats[user]["models_used"] = list(user_stats[user]["models_used"])
            
        return user_stats
        
    def get_current_budget_status(self) -> Dict[str, Any]:
        """Get comprehensive budget status"""
        daily_usage = self.get_daily_usage()
        monthly_usage = self.get_monthly_usage()
        
        # Calculate usage ratios
        daily_cost_ratio = daily_usage["total_cost"] / self.budget_limits.daily_cost_limit
        monthly_cost_ratio = monthly_usage["total_cost"] / self.budget_limits.monthly_cost_limit
        daily_token_ratio = daily_usage["total_tokens"] / self.budget_limits.daily_token_limit
        monthly_token_ratio = monthly_usage["total_tokens"] / self.budget_limits.monthly_token_limit
        
        # Determine alert level
        max_ratio = max(daily_cost_ratio, monthly_cost_ratio, daily_token_ratio, monthly_token_ratio)
        
        if max_ratio >= 1.0:
            alert_level = BudgetAlert.EXCEEDED
        elif max_ratio >= self.budget_limits.critical_threshold:
            alert_level = BudgetAlert.CRITICAL
        elif max_ratio >= self.budget_limits.warning_threshold:
            alert_level = BudgetAlert.WARNING
        else:
            alert_level = BudgetAlert.NONE
            
        return {
            "alert_level": alert_level.value,
            "daily": {
                "cost": daily_usage["total_cost"],
                "cost_limit": self.budget_limits.daily_cost_limit,
                "cost_ratio": daily_cost_ratio,
                "tokens": daily_usage["total_tokens"],
                "token_limit": self.budget_limits.daily_token_limit,
                "token_ratio": daily_token_ratio,
                "requests": daily_usage["request_count"]
            },
            "monthly": {
                "cost": monthly_usage["total_cost"],
                "cost_limit": self.budget_limits.monthly_cost_limit,
                "cost_ratio": monthly_cost_ratio,
                "tokens": monthly_usage["total_tokens"],
                "token_limit": self.budget_limits.monthly_token_limit,
                "token_ratio": monthly_token_ratio,
                "requests": monthly_usage["request_count"]
            },
            "max_usage_ratio": max_ratio
        }
        
    def set_budget_limits(self, **limits):
        """Update budget limits"""
        for key, value in limits.items():
            if hasattr(self.budget_limits, key):
                setattr(self.budget_limits, key, value)
                print(f"[LLMBudgetMonitor] ⚙️ Updated {key} to {value}")
        
        self.save_config()
        
    def reset_usage(self, confirm: bool = False):
        """Reset usage log (use with caution)"""
        if confirm:
            self.usage_log = []
            self.save_usage_log()
            print("[LLMBudgetMonitor] 🗑️ Usage log reset")
        else:
            print("[LLMBudgetMonitor] ⚠️ Usage reset requires confirmation")

# Global budget monitor instance
budget_monitor = LLMBudgetMonitor()

def check_llm_budget_before_request(estimated_tokens: int, model: str, user: str) -> Tuple[bool, str]:
    """
    Check if LLM request is within budget limits
    
    Returns:
        (allowed, status_message)
    """
    # For local LLM, budget is unlimited
    return True, "✅ Local LLM - Unlimited budget"

def log_llm_usage(input_tokens: int, output_tokens: int, model: str, user: str, request_type: str = "chat"):
    """Log LLM usage after request completion"""
    return budget_monitor.log_usage(input_tokens, output_tokens, model, user, request_type)

def get_budget_status() -> Dict[str, Any]:
    """Get current budget status"""
    return budget_monitor.get_current_budget_status()

def estimate_tokens_from_text(text: str) -> int:
    """
    Rough estimation of tokens from text
    Delegates to dedicated token_budget module for better accuracy
    """
    try:
        # Use dedicated token budget module for better accuracy
        from ai.token_budget import estimate_tokens_from_text as dedicated_estimate
        return dedicated_estimate(text)
        
    except ImportError:
        # Fallback to original simple estimation
        return max(1, len(text) // 4)
    except Exception as e:
        print(f"[LLMBudgetMonitor] ❌ Error using dedicated token estimator: {e}")
        return max(1, len(text) // 4)

if __name__ == "__main__":
    # Test the budget monitor
    print("Testing LLM Budget Monitor")
    
    # Test pre-request check
    allowed, message = check_llm_budget_before_request(1000, "gpt-3.5-turbo", "test_user")
    print(f"Request allowed: {allowed}, Message: {message}")
    
    # Test usage logging
    usage = log_llm_usage(500, 300, "gpt-3.5-turbo", "test_user")
    print(f"Logged usage: {usage.total_tokens} tokens, ${usage.cost_estimate:.4f}")
    
    # Test budget status
    status = get_budget_status()
    print(f"Budget status: {status['alert_level']}")
    print(f"Daily cost: ${status['daily']['cost']:.4f} / ${status['daily']['cost_limit']}")