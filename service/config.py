def upload_config(data):
    config = {}
    for row in data:
        if row[0] == '#':
            continue
        if '=' not in row:
            continue                
        row = row.replace('\n', '')        
        config_key, config_value = row.split('=')
        config[config_key] = config_value
    return config


with open('.env', 'r') as env:
    data = env.readlines()


config = upload_config(data)
