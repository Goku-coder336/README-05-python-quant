"""The Triad Verdict: a multi-agent debate framework for futures trading research."""
from .config import AgentConfig, AssetSpec, RiskConfig, TriadConfig
from .backtest import TriadBacktester

__all__ = ["AgentConfig", "AssetSpec", "RiskConfig", "TriadConfig", "TriadBacktester"]
