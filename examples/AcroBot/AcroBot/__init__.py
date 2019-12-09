import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)


register(
    id='barbellAcrobot-v0',
    entry_point='AcroBot.envs:BarbellAcrobot'
)
