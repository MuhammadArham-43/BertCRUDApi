import os



def _get_env_var(key):
    if key in os.environ:
        return os.environ[key]
    raise ValueError(f"Environment variable {key} not set")


def get_db_url():
    return _get_env_var("DB_URL")

def get_bert_ckpt_path():
    return _get_env_var("BERT_CKPT_PATH")