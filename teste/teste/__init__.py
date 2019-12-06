import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)


register(
    id='teste1-v0',
    entry_point='teste.envs:Teste1'
)
