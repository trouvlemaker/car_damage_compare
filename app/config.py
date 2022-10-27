import os
from omegaconf import OmegaConf


application_path = os.path.dirname(os.path.abspath(__file__))
config_path = f"{application_path}/configs"
config_name = 'app_config.yaml'
config_abs_path = f"{config_path}/{config_name}"
cfg = OmegaConf.load(config_abs_path)
print(f'configuration file loaded {application_path}')
