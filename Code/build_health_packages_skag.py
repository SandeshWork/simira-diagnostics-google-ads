"""Builds the Health Packages SKAG for Simira Diagnostics (Navi Mumbai).

Creates: budget, campaign (Search, PAUSED), geo + country exclusions, language,
ad schedule, campaign negatives, 1 ad group, 1 phrase-match keyword, 3 RSAs.
Everything is created PAUSED. Run: python build_health_packages_skag.py
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

CAMPAIGN_NAME = "New_Health_Packages_Navi_Mum"
AD_GROUP_NAME = "Health Packages Near Me"
DAILY_BUDGET_MICROS = 3000 * 1_000_000
KEYWORD = "health checkup packages near me"
FINAL_URL = (
    "https://www.simiradiagnostics.com/packages"
    f"?utm_source=google&utm_medium=search&utm_campaign={CAMPAIGN_NAME.lower()}"
)
KEEP_COUNTRY_CODE = "IN"
LANGUAGE_CONSTANT = "languageConstants/1000"  # English

POSITIVE_LOCATION_IDS = [
    9040246,  # Navi Mumbai (city)
    9300528,  # Panvel (neighborhood)
    9263611,  # Kharghar (neighborhood)
    9199162,  # CBD Belapur (neighborhood)
    9208149,  # Kalamboli (neighborhood)
    9208282,  # Taloja (neighborhood)
    9194505,  # Seawoods (neighborhood)
    9300687,  # 400706 (postal code)
]

NEGATIVE_KEYWORDS = [
    "jobs", "salary", "salaries", "career", "careers", "school", "schools",
    "course", "courses", "training", "apprentice", "apprenticeship",
    "certification", "diy", "how to",
]

HEADLINES = [
    ("Health Checkup Packages", True),
    ("Health Packages Near Me", True),
    ("Full Body Checkup Packages", True),
    ("Home Sample Collection", False),
    ("Reports Within 24 Hrs", False),
    ("Book Your Checkup Today", False),
    ("Affordable Health Packages", False),
    ("Certified Pathology Lab", False),
    ("Same Day Report Delivery", False),
    ("Comprehensive Health Checkups", False),
    ("Expert Diagnostic Care", False),
    ("Trusted Diagnostic Center", False),
    ("Call to Book Now", False),
    ("Multiple Packages Available", False),
    ("Serving All Navi Mumbai", False),
]

DESCRIPTIONS = [
    "Book health checkup packages across Navi Mumbai. Accurate results, fast reports.",
    "Home sample collection available. Trusted diagnostic care across Navi Mumbai.",
    "Comprehensive full body checkups for the whole family. Book your slot today.",
    "Quick appointments, certified diagnostics. Call now or book online.",
]

AD_SCHEDULE_DAYS = [
    "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY",
]


def run(label, fn):
    try:
        result = fn()
        print(f" [OK] {label}")
        return result
    except GoogleAdsException as ex:
        print(f" [FAIL] {label}")
        for error in ex.failure.errors:
            print(f"     {error.message}")
        return None


def main():
    campaign_budget_service = client.get_service("CampaignBudgetService")
    campaign_service = client.get_service("CampaignService")
    campaign_criterion_service = client.get_service("CampaignCriterionService")
    ad_group_service = client.get_service("AdGroupService")
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ga_service = client.get_service("GoogleAdsService")

    # 1. Budget (reuse if a prior partial run already created it)
    def create_budget():
        budget_name = f"Budget - {CAMPAIGN_NAME}"
        query = (
            "SELECT campaign_budget.resource_name FROM campaign_budget "
            f"WHERE campaign_budget.name = '{budget_name}' "
            "AND campaign_budget.status != 'REMOVED'"
        )
        existing = list(ga_service.search(customer_id=customer_id, query=query))
        if existing:
            return existing[0].campaign_budget.resource_name
        op = client.get_type("CampaignBudgetOperation")
        b = op.create
        b.name = budget_name
        b.amount_micros = DAILY_BUDGET_MICROS
        b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        b.explicitly_shared = False
        resp = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[op]
        )
        return resp.results[0].resource_name

    budget_resource = run("Budget: Rs 3,000/day", create_budget)
    if not budget_resource:
        sys.exit(1)

    # 2. Campaign
    def create_campaign():
        op = client.get_type("CampaignOperation")
        c = op.create
        c.name = CAMPAIGN_NAME
        c.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        c.status = client.enums.CampaignStatusEnum.PAUSED
        c.campaign_budget = budget_resource
        c.maximize_conversions.target_cpa_micros = 0  # declare oneof: Max Conversions, no target
        c.network_settings.target_google_search = True
        c.network_settings.target_search_network = False
        c.network_settings.target_content_network = False
        c.network_settings.target_partner_search_network = False
        c.geo_target_type_setting.positive_geo_target_type = (
            client.enums.PositiveGeoTargetTypeEnum.PRESENCE
        )
        c.geo_target_type_setting.negative_geo_target_type = (
            client.enums.NegativeGeoTargetTypeEnum.PRESENCE
        )
        c.contains_eu_political_advertising = (
            client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        )
        resp = campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
        return resp.results[0].resource_name

    campaign_resource = run(f"Campaign: {CAMPAIGN_NAME}", create_campaign)
    if not campaign_resource:
        sys.exit(1)

    # 3. Positive locations
    def create_positive_locations():
        ops = []
        for gtc_id in POSITIVE_LOCATION_IDS:
            op = client.get_type("CampaignCriterionOperation")
            op.create.campaign = campaign_resource
            op.create.location.geo_target_constant = f"geoTargetConstants/{gtc_id}"
            ops.append(op)
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=ops
        )
        return len(ops)

    run(f"Geo: {len(POSITIVE_LOCATION_IDS)} locations (Navi Mumbai area)", create_positive_locations)

    # 4. Negative countries (all except India)
    def create_negative_countries():
        query = (
            "SELECT geo_target_constant.resource_name, geo_target_constant.country_code "
            "FROM geo_target_constant WHERE geo_target_constant.target_type = 'Country'"
        )
        rows = ga_service.search(customer_id=customer_id, query=query)
        ops = []
        for row in rows:
            if row.geo_target_constant.country_code != KEEP_COUNTRY_CODE:
                op = client.get_type("CampaignCriterionOperation")
                op.create.campaign = campaign_resource
                op.create.negative = True
                op.create.location.geo_target_constant = row.geo_target_constant.resource_name
                ops.append(op)
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=ops
        )
        return len(ops)

    run("Excluded: every country except India", create_negative_countries)

    # 5. Language (English)
    def create_language():
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = campaign_resource
        op.create.language.language_constant = LANGUAGE_CONSTANT
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[op]
        )

    run("Language: English", create_language)

    # 6. Ad schedule (Mon-Sat 7am-9pm)
    def create_ad_schedule():
        ops = []
        for day in AD_SCHEDULE_DAYS:
            op = client.get_type("CampaignCriterionOperation")
            op.create.campaign = campaign_resource
            op.create.ad_schedule.day_of_week = getattr(client.enums.DayOfWeekEnum, day)
            op.create.ad_schedule.start_hour = 7
            op.create.ad_schedule.start_minute = client.enums.MinuteOfHourEnum.ZERO
            op.create.ad_schedule.end_hour = 21
            op.create.ad_schedule.end_minute = client.enums.MinuteOfHourEnum.ZERO
            ops.append(op)
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=ops
        )

    run("Schedule: Mon-Sat 7am-9pm", create_ad_schedule)

    # 7. Campaign-level negative keywords
    def create_negative_keywords():
        ops = []
        for term in NEGATIVE_KEYWORDS:
            op = client.get_type("CampaignCriterionOperation")
            op.create.campaign = campaign_resource
            op.create.negative = True
            op.create.keyword.text = term
            op.create.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
            ops.append(op)
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=ops
        )

    run(f"Negative keywords: {len(NEGATIVE_KEYWORDS)} added", create_negative_keywords)

    # 8. Ad group
    def create_ad_group():
        op = client.get_type("AdGroupOperation")
        ag = op.create
        ag.name = AD_GROUP_NAME
        ag.campaign = campaign_resource
        ag.status = client.enums.AdGroupStatusEnum.PAUSED
        ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        resp = ad_group_service.mutate_ad_groups(customer_id=customer_id, operations=[op])
        return resp.results[0].resource_name

    ad_group_resource = run(f"Ad group: {AD_GROUP_NAME}", create_ad_group)
    if not ad_group_resource:
        sys.exit(1)

    # 9. Keyword (phrase match)
    def create_keyword():
        op = client.get_type("AdGroupCriterionOperation")
        crit = op.create
        crit.ad_group = ad_group_resource
        crit.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        crit.keyword.text = KEYWORD
        crit.keyword.match_type = client.enums.KeywordMatchTypeEnum.PHRASE
        ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[op]
        )

    run(f'Keyword: "{KEYWORD}" (phrase match)', create_keyword)

    # 10. RSAs (x3, identical asset set, only slot-1 keyword variants pinned)
    def create_rsa(index):
        op = client.get_type("AdGroupAdOperation")
        ad_group_ad = op.create
        ad_group_ad.ad_group = ad_group_resource
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad = ad_group_ad.ad
        ad.final_urls.append(FINAL_URL)
        for text, pinned in HEADLINES:
            asset = client.get_type("AdTextAsset")
            asset.text = text
            if pinned:
                asset.pinned_field = client.enums.ServedAssetFieldTypeEnum.HEADLINE_1
            ad.responsive_search_ad.headlines.append(asset)
        for text in DESCRIPTIONS:
            asset = client.get_type("AdTextAsset")
            asset.text = text
            ad.responsive_search_ad.descriptions.append(asset)
        resp = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[op]
        )
        return resp.results[0].resource_name

    for i in range(1, 4):
        run(f"RSA {i}", lambda i=i: create_rsa(i))

    print(f"\n ALL CREATED · PAUSED · Campaign: {campaign_resource}")
    campaign_id = campaign_resource.split("/")[-1]
    print(f" Review at: https://ads.google.com/aw/campaigns?campaignId={campaign_id}")


if __name__ == "__main__":
    main()
