import argparse
import json
import sys
from configparser import ConfigParser
from urllib import error, parse, request
from pprint import pp

import style

API_URL = 'https://api.openweathermap.org/data/2.5/weather?q='


def change_color(color):
    print(color, end='')


def build_weather_query(city_input, imperial=False):
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{API_URL}{url_encoded}"
        f"&units={units}&appid={api_key}"
    )
    return url


def get_weather_data(query_url):
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Access denied. Check your API key")
        elif http_error.code == 404:
            sys.exit("Can't find weather for this city")
        else:
            sys.exit(f"Somethig went wrong...({http_error.code})")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Could not read from server")


def read_user_cli_args():
    parser = argparse.ArgumentParser(
        description="Get weather and temperature information for a city")
    parser.add_argument("city", nargs="+", type=str, help="Enter city name")
    parser.add_argument("-i", "--imperial", action="store_true",
                        help="Display the temperature in imperial units")
    return parser.parse_args()


def display_weather_info(weather_data, imperial=False):
    city = weather_data["name"]
    weather_id = weather_data["weather"][0]["id"]
    description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]

    change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)
    change_color(color)

    print(f"\t{weather_symbol:^{style.PADDING}}", end=" ")
    print(f"\t{description.capitalize():^{style.PADDING}}", end=" ")
    change_color(style.RESET)

    print(f"({temperature} °{'F' if imperial else 'C'})")


def _select_weather_display_params(weather_id):
    if weather_id in style.THUNDERSTORM:
        display_params = ("💥", style.RED)
    elif weather_id in style.DRIZZLE:
        display_params = ("💧", style.CYAN)
    elif weather_id in style.RAIN:
        display_params = ("💦", style.BLUE)
    elif weather_id in style.SNOW:
        display_params = ("⛄️", style.WHITE)
    elif weather_id in style.ATMOSPHERE:
        display_params = ("🌀", style.BLUE)
    elif weather_id in style.CLEAR:
        display_params = ("🔆", style.YELLOW)
    elif weather_id in style.CLOUDY:
        display_params = ("💨", style.WHITE)
    else:
        display_params = ("🌈", style.RESET)
    return display_params


def _get_api_key():
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)
    # pp(weather_data)

_get_api_key()
