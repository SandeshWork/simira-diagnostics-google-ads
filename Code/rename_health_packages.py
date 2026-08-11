"""One-off: renames the live Health Packages campaign/ad group to the new
convention and adds UTM params to the ad final URLs."""

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
customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

CAMPAIGN_ID = "24121466394"
NEW_CAMPAIGN_NAME = "New_Health_Packages_Navi_Mum"
NEW_AD_GROUP_NAME = "Health Packages Near Me"
NEW_FINAL_URL = (
    "https://www.simiradiagnostics.com/packages"
    f"?utm_source=google&utm_medium=search&utm_campaign={NEW_CAMPAIGN_NAME.lower()}"
)

ga_service = client.get_service("GoogleAdsService")

# 1. Rename campaign
campaign_service = client.get_service("CampaignService")
op = client.get_type("CampaignOperation")
op.update.resource_name = f"customers/{customer_id}/campaigns/{CAMPAIGN_ID}"
op.update.name = NEW_CAMPAIGN_NAME
op.update_mask.paths.append("name")
campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
print(f" [OK] Campaign renamed to: {NEW_CAMPAIGN_NAME}")

# 2. Rename ad group
q = f"""
    SELECT ad_group.resource_name FROM ad_group
    WHERE ad_group.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
"""
ad_group_resource = list(ga_service.search(customer_id=customer_id, query=q))[0].ad_group.resource_name

ad_group_service = client.get_service("AdGroupService")
op = client.get_type("AdGroupOperation")
op.update.resource_name = ad_group_resource
op.update.name = NEW_AD_GROUP_NAME
op.update_mask.paths.append("name")
ad_group_service.mutate_ad_groups(customer_id=customer_id, operations=[op])
print(f" [OK] Ad group renamed to: {NEW_AD_GROUP_NAME}")

# 3. Update final URLs (with UTMs) on each ad
q = f"""
    SELECT ad_group_ad.ad.resource_name FROM ad_group_ad
    WHERE ad_group.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
"""
ad_resources = [row.ad_group_ad.ad.resource_name for row in ga_service.search(customer_id=customer_id, query=q)]

ad_service = client.get_service("AdService")
ops = []
for ad_resource in ad_resources:
    op = client.get_type("AdOperation")
    op.update.resource_name = ad_resource
    op.update.final_urls.append(NEW_FINAL_URL)
    op.update_mask.paths.append("final_urls")
    ops.append(op)
ad_service.mutate_ads(customer_id=customer_id, operations=ops)
print(f" [OK] {len(ops)} ad final URLs updated with UTM params")
print(f"      {NEW_FINAL_URL}")
