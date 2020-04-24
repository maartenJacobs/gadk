from gadk import EnvVars, Dict, Expression


def env_vars_to_yaml(env_vars: EnvVars) -> Dict:
    return {
        key: value.to_yaml() if type(value) is Expression else value
        for key, value in env_vars.items()
    }
