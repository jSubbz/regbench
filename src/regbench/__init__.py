"""regbench: a perturbation-paired benchmark for embedded systems reasoning."""

from .dataset import regbench_dataset
from .scorer import answer_match
from .task import regbench

__all__ = ["regbench", "regbench_dataset", "answer_match"]
__version__ = "0.1.0"
