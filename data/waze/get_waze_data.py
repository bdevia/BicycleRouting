import requests
import json

url = "https://waze.p.rapidapi.com/alerts-and-jams"

headers = {
    "X-RapidAPI-Key": "32b9b76b22msh6b1bba18f0da9bfp1eee55jsn16b11b103e05",
    "X-RapidAPI-Host": "waze.p.rapidapi.com"
}

# Specify the coordinates for the bottom left and top right corners
bottom_left = "-33.467708, -70.699994" 
top_right = "-33.416428, -70.617425"


querystring = {
        "bottom_left": bottom_left,
        "top_right": top_right,
        "max_alerts": "20",
        "max_jams": "20"
    }
response = requests.get(url, headers=headers, params=querystring)
# Save the JSON response to a file
with open("waze_data.json", "w") as json_file:
    json.dump(response.json()["data"], json_file)

print(response.status_code)