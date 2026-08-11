"""Prints live state of the Health Packages SKAG: campaign, ad group, keyword, criteria, ads."""

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
ga_service = client.get_service("GoogleAdsService")

CAMPAIGN_ID = "24121466394"

print("--- Campaign ---")
q = f"""
    SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
           campaign_budget.amount_micros, campaign.maximize_conversions.target_cpa_micros
    FROM campaign WHERE campaign.id = {CAMPAIGN_ID}
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    c = row.campaign
    print(f"  {c.name} | status={c.status.name} | type={c.advertising_channel_type.name} "
          f"| budget=Rs{row.campaign_budget.amount_micros/1e6:.0f}/day")

print("\n--- Locations (positive) ---")
q = f"""
    SELECT campaign_criterion.location.geo_target_constant, campaign_criterion.status
    FROM campaign_criterion
    WHERE campaign_criterion.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    AND campaign_criterion.type = 'LOCATION' AND campaign_criterion.negative = FALSE
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    print(f"  {row.campaign_criterion.location.geo_target_constant}")

print("\n--- Negative locations (countries excluded) count ---")
q = f"""
    SELECT campaign_criterion.criterion_id
    FROM campaign_criterion
    WHERE campaign_criterion.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    AND campaign_criterion.type = 'LOCATION' AND campaign_criterion.negative = TRUE
"""
count = sum(1 for _ in ga_service.search(customer_id=customer_id, query=q))
print(f"  {count} countries excluded")

print("\n--- Language ---")
q = f"""
    SELECT campaign_criterion.language.language_constant
    FROM campaign_criterion
    WHERE campaign_criterion.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    AND campaign_criterion.type = 'LANGUAGE'
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    print(f"  {row.campaign_criterion.language.language_constant}")

print("\n--- Ad schedule ---")
q = f"""
    SELECT campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour,
           campaign_criterion.ad_schedule.end_hour
    FROM campaign_criterion
    WHERE campaign_criterion.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    AND campaign_criterion.type = 'AD_SCHEDULE'
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    s = row.campaign_criterion.ad_schedule
    print(f"  {s.day_of_week.name}: {s.start_hour}:00-{s.end_hour}:00")

print("\n--- Negative keywords ---")
q = f"""
    SELECT campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
    FROM campaign_criterion
    WHERE campaign_criterion.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    print(f"  -{row.campaign_criterion.keyword.text} ({row.campaign_criterion.keyword.match_type.name})")

print("\n--- Ad group + keyword ---")
q = f"""
    SELECT ad_group.id, ad_group.name, ad_group.status,
           ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status
    FROM ad_group_criterion
    WHERE ad_group.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    AND ad_group_criterion.type = 'KEYWORD'
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    ag = row.ad_group
    kw = row.ad_group_criterion.keyword
    print(f"  AdGroup: {ag.name} ({ag.status.name}) | Keyword: \"{kw.text}\" {kw.match_type.name} "
          f"({row.ad_group_criterion.status.name})")

print("\n--- Ads ---")
q = f"""
    SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.responsive_search_ad.headlines,
           ad_group_ad.ad.final_urls
    FROM ad_group_ad
    WHERE ad_group_ad.ad_group IN (
        SELECT ad_group.resource_name FROM ad_group WHERE ad_group.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    )
""" if False else f"""
    SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls
    FROM ad_group_ad
    WHERE ad_group.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
"""
for row in ga_service.search(customer_id=customer_id, query=q):
    print(f"  Ad {row.ad_group_ad.ad.id} | status={row.ad_group_ad.status.name} | url={list(row.ad_group_ad.ad.final_urls)}")
