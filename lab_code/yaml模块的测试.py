import yaml
f = open("./config/config.yaml")
config_yaml = yaml.load(f,Loader=yaml.FullLoader)
print(config_yaml)
