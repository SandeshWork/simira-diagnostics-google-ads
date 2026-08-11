"""Uploads a business logo image and attaches it to the Health Packages campaign.

Per ad-assets-best-practices.md specs:
  - Square (1:1): 1200x1200 recommended, 128x128 minimum -> field_type LOGO
  - Horizontal (4:1): 1200x300 recommended, 512x128 minimum -> field_type LANDSCAPE_LOGO
  - PNG (transparent bg preferred) or JPG, 5120 KB max

Usage:
  python upload_logo.py <path_to_square_logo> [path_to_landscape_logo]
"""

import sys
from dotenv import load_dotenv
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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
customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
CAMPAIGN_ID = "24121466394"

MAX_BYTES = 5120 * 1024  # 5120 KB


def upload_image(path, asset_name):
    if not os.path.exists(path):
        print(f" [FAIL] File not found: {path}")
        return None
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        print(f" [FAIL] {path} is {size/1024:.0f}KB, exceeds 5120KB max")
        return None
    with open(path, "rb") as f:
        data = f.read()

    asset_service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    op.create.name = asset_name
    op.create.image_asset.data = data
    try:
        resp = asset_service.mutate_assets(customer_id=customer_id, operations=[op])
        resource_name = resp.results[0].resource_name
        print(f" [OK] Uploaded {path} -> {resource_name}")
        return resource_name
    except GoogleAdsException as ex:
        print(f" [FAIL] Upload failed for {path}")
        for error in ex.failure.errors:
            print(f"     {error.message}")
        return None


def attach(asset_resource, field_type_name):
    campaign_asset_service = client.get_service("CampaignAssetService")
    op = client.get_type("CampaignAssetOperation")
    op.create.campaign = f"customers/{customer_id}/campaigns/{CAMPAIGN_ID}"
    op.create.asset = asset_resource
    op.create.field_type = getattr(client.enums.AssetFieldTypeEnum, field_type_name)
    try:
        resp = campaign_asset_service.mutate_campaign_assets(customer_id=customer_id, operations=[op])
        print(f" [OK] Attached as {field_type_name}: {resp.results[0].resource_name}")
    except GoogleAdsException as ex:
        print(f" [FAIL] Attach failed ({field_type_name})")
        for error in ex.failure.errors:
            print(f"     {error.message}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_logo.py <square_logo_path> [landscape_logo_path]")
        sys.exit(1)

    square_path = sys.argv[1]
    square_asset = upload_image(square_path, "Simira Diagnostics Logo (Square)")
    if square_asset:
        attach(square_asset, "LOGO")

    if len(sys.argv) > 2:
        landscape_path = sys.argv[2]
        landscape_asset = upload_image(landscape_path, "Simira Diagnostics Logo (Landscape)")
        if landscape_asset:
            attach(landscape_asset, "LANDSCAPE_LOGO")


if __name__ == "__main__":
    main()
