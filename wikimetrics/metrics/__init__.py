from metric import *
from timeseries_metric import *
from dummy import *
from namespace_edits import *
from revert_rate import *
from bytes_added import *
from pages_created import *
from pages_edited import *
from threshold import *
from survival import *
from newly_registered import *
from rolling_active_editor import *
from rolling_new_active_editor import *
from rolling_surviving_new_active_editor import *

# ignore flake8 because of F403 violation
# flake8: noqa

from inspect import getmembers, isclass
from sys import modules
metric_classes = {
    m[0]: m[1]
    for m in getmembers(modules[__name__], isclass)
    if issubclass(m[1], Metric)
}
