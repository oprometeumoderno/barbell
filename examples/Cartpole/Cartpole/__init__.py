import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)


register(
    id='pendulum1-v0',
    entry_point='Cartpole.envs:Pendulum1'
)
