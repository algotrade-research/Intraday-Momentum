import optuna
from optuna.samplers import RandomSampler

from src.metrics.metric import Metric
from src.data.service import DataService
from src.backtesting.backtesting import Backtesting

