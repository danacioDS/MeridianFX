import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo')
TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_KEY', 'demo')

# Model paths
MODEL_PATH = os.getenv('MODEL_PATH', 'models/xgboost_model.pkl')
DATA_PATH = os.getenv('DATA_PATH', 'data/historical/')

# Trading parameters
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.2'))
MIN_EDGE_RATIO = float(os.getenv('MIN_EDGE_RATIO', '1.5'))
MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '0.6'))

# Data fetching
DEFAULT_PERIOD = os.getenv('DEFAULT_PERIOD', '1y')
DEFAULT_INTERVAL = os.getenv('DEFAULT_INTERVAL', '1d')
