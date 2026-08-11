"""Looks up Google Ads geoTargetConstant resource names for a list of place names."""

from dotenv import load_dotenv
import os
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

config = {
    "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
    "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
    "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
    "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
    "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config)
gtc_service = client.get_service("GeoTargetConstantService")

PLACE_NAMES = [
    "400706",
    "CBD Belapur, Maharashtra, India",
    "Kalamboli, Maharashtra, India",
    "Kharghar, Maharashtra, India",
    "Navi Mumbai, Maharashtra, India",
    "Panvel, Maharashtra, India",
    "Seawoods, Maharashtra, India",
    "Taloja, Maharashtra, India",
]

request = client.get_type("SuggestGeoTargetConstantsRequest")
request.locale = "en"
request.country_code = "IN"
request.location_names.names.extend(PLACE_NAMES)

response = gtc_service.suggest_geo_target_constants(request=request)

for suggestion in response.geo_target_constant_suggestions:
    gtc = suggestion.geo_target_constant
    print(
        f"  {gtc.resource_name} | {gtc.name} | type={gtc.target_type} | "
        f"country={gtc.country_code} | canonical='{suggestion.geo_target_constant.canonical_name if False else suggestion.locale}' "
    )
    print(f"     reach={suggestion.reach if suggestion.reach else 'n/a'} | search_term='{suggestion.search_term}'")
