import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)


register(
    id='henrique-v0',
    entry_point='Henrique.envs:Henrique'
)

register(
    id='henrique_hard-v0',
    entry_point='Henrique.envs:HenriqueHard'
)
