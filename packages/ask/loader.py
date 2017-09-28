from packages.ask.Query import *
from packages.ask.Weather import *

def load():
    return [Query(),  WeatherForecast(), WeatherNow()]
