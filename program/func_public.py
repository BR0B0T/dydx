import numpy as np
import pandas as pd
import time

from constants import RESOLUTION
from pprint import pprint
from func_utils import get_ISO_times

# Get relevant time periods for ISO from and to
ISO_TIMES = get_ISO_times()
pprint(ISO_TIMES)


def construct_market_prices(client):
    pass