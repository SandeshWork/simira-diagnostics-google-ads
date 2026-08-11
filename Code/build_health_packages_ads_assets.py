"""Rebuilds the 3 RSAs (speed/trust/value angles, per anatomy-of-a-good-ad.md) and
adds campaign-level sitelinks/callouts/structured snippets (per ad-assets-best-practices.md)
for the Health Packages Navi Mumbai campaign."""

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
FINAL_URL = (
    "https://www.simiradiagnostics.com/packages"
    "?utm_source=google&utm_medium=search&utm_campaign=new_health_packages_navi_mum"
)

PINNED_HEADLINES = [
    "Health Checkup Packages",
    "Health Packages Near Me",
    "Full Body Checkup Packages",
]

RSAS = {
    "Speed": {
        "unpinned": [
            "Same-Day Report Delivery", "Reports Within 24 Hrs", "Quick Appointment Slots",
            "Certified Diagnostic Lab", "Expert Lab Technicians", "Same-Day Service",
            "Book Online Today", "Call to Book Now", "Doorstep Sample Pickup",
            "No Hidden Charges", "Comprehensive Health Checkups", "Serving All Navi Mumbai",
        ],
        "descriptions": [
            "Book health checkup packages across Navi Mumbai. Same-day reports, certified lab.",
            "Certified diagnostic lab with expert technicians. Transparent, upfront pricing.",
            "Home sample collection available. Skip the queue, get tested at home.",
            "Call now or book online for a quick appointment slot.",
        ],
    },
    "Trust": {
        "unpinned": [
            "Certified Diagnostic Lab", "Expert Lab Technicians", "Trusted Diagnostic Care",
            "Home Sample Collection", "Comprehensive Health Checkups", "Multiple Test Packages",
            "Same-Day Reports", "No Hidden Charges", "Transparent Pricing",
            "Call to Book Now", "Book Your Checkup Today", "Serving All Navi Mumbai",
        ],
        "descriptions": [
            "Trusted diagnostic care across Navi Mumbai. Certified lab, experienced technicians.",
            "Accurate results from a certified lab. No hidden charges, transparent pricing.",
            "Comprehensive health packages for the whole family, all in one visit.",
            "Book your health checkup today, online or by phone.",
        ],
    },
    "Value": {
        "unpinned": [
            "Affordable Health Packages", "Family Health Packages", "Multiple Packages Available",
            "No Hidden Charges", "Transparent Pricing", "Certified Diagnostic Lab",
            "Home Sample Collection", "Same-Day Reports", "Quick Appointment Slots",
            "Book Online Today", "Call to Book Now", "Doorstep Sample Pickup",
        ],
        "descriptions": [
            "Affordable health checkup packages across Navi Mumbai. Multiple packages to choose from.",
            "Certified lab, transparent pricing, no hidden charges.",
            "Home sample collection included, so you skip the trip to the lab.",
            "Book online today or call now to reserve your slot.",
        ],
    },
}

SITELINKS = [
    ("Blood Tests", "Accurate lab results fast", "Home sample collection",
     "https://www.simiradiagnostics.com/blood-test"),
    ("Sonography", "Expert sonography scans", "Book your slot today",
     "https://www.simiradiagnostics.com/sonography"),
    ("Fever Packages", "Quick fever test panels", "Same day report delivery",
     "https://www.simiradiagnostics.com/fever-packages"),
    ("Full Body Exam", "Comprehensive health screening", "For the whole family",
     "https://www.simiradiagnostics.com/fullbody-checkup"),
    ("Gynaecology", "Womens health checkups", "Confidential expert care",
     "https://www.simiradiagnostics.com/gynaecology"),
    ("Home Visit", "Free sample pickup", "Tests done at your home",
     "https://www.simiradiagnostics.com/home-visit"),
    ("X-Ray", "Digital X-ray reports", "Fast turnaround time",
     "https://www.simiradiagnostics.com/x-ray"),
]

CALLOUTS = [
    "Doorstep Sample Pickup", "Same-Day Reports", "Certified Diagnostic Lab",
    "Across Navi Mumbai", "Book Online Instantly", "Family Health Packages",
    "Affordable Packages", "Trusted Diagnostic Care", "Quick Appointment Slots",
    "Expert Lab Technicians",
]

STRUCTURED_SNIPPETS = [
    ("Services", ["Blood Tests", "Sonography", "X-Ray", "Full Body Checkup",
                  "Fever Packages", "Gynaecology"]),
    ("Types", ["Home Visit", "Lab Tests", "Imaging", "Health Packages"]),
]


def validate():
    errors = []
    for name, rsa in RSAS.items():
        all_headlines = PINNED_HEADLINES + rsa["unpinned"]
        if len(all_headlines) != 15:
            errors.append(f"RSA {name}: {len(all_headlines)} headlines, need 15")
        for h in all_headlines:
            if len(h) > 30:
                errors.append(f"RSA {name} headline too long ({len(h)}): {h}")
        if len(rsa["descriptions"]) != 4:
            errors.append(f"RSA {name}: {len(rsa['descriptions'])} descriptions, need 4")
        for d in rsa["descriptions"]:
            if len(d) > 90:
                errors.append(f"RSA {name} description too long ({len(d)}): {d}")
    for title, d1, d2, url in SITELINKS:
        if len(title) > 25:
            errors.append(f"Sitelink title too long: {title}")
        if len(d1) > 35 or len(d2) > 35:
            errors.append(f"Sitelink desc too long: {title}")
    for c in CALLOUTS:
        if len(c) > 25:
            errors.append(f"Callout too long ({len(c)}): {c}")
    for header, values in STRUCTURED_SNIPPETS:
        for v in values:
            if len(v) > 25:
                errors.append(f"Snippet value too long: {v}")
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(" [OK] All asset text within character limits\n")


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
    validate()

    ga_service = client.get_service("GoogleAdsService")
    ad_group_ad_service = client.get_service("AdGroupAdService")
    asset_service = client.get_service("AssetService")
    campaign_asset_service = client.get_service("CampaignAssetService")

    q = f"""
        SELECT ad_group.resource_name, ad_group_ad.resource_name
        FROM ad_group_ad
        WHERE ad_group.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}'
    """
    rows = list(ga_service.search(customer_id=customer_id, query=q))
    ad_group_resource = rows[0].ad_group.resource_name
    old_ad_group_ad_resources = [r.ad_group_ad.resource_name for r in rows]

    def remove_old_rsas():
        ops = []
        for r in old_ad_group_ad_resources:
            op = client.get_type("AdGroupAdOperation")
            op.remove = r
            ops.append(op)
        ad_group_ad_service.mutate_ad_group_ads(customer_id=customer_id, operations=ops)
        return len(ops)

    run(f"Removed {len(old_ad_group_ad_resources)} old generic RSAs", remove_old_rsas)

    def create_rsa(angle, headlines, descriptions):
        op = client.get_type("AdGroupAdOperation")
        ad_group_ad = op.create
        ad_group_ad.ad_group = ad_group_resource
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad = ad_group_ad.ad
        ad.final_urls.append(FINAL_URL)
        for text in PINNED_HEADLINES:
            asset = client.get_type("AdTextAsset")
            asset.text = text
            asset.pinned_field = client.enums.ServedAssetFieldTypeEnum.HEADLINE_1
            ad.responsive_search_ad.headlines.append(asset)
        for text in headlines:
            asset = client.get_type("AdTextAsset")
            asset.text = text
            ad.responsive_search_ad.headlines.append(asset)
        for text in descriptions:
            asset = client.get_type("AdTextAsset")
            asset.text = text
            ad.responsive_search_ad.descriptions.append(asset)
        resp = ad_group_ad_service.mutate_ad_group_ads(customer_id=customer_id, operations=[op])
        return resp.results[0].resource_name

    for angle, rsa in RSAS.items():
        run(f"RSA ({angle} angle)", lambda angle=angle, rsa=rsa: create_rsa(angle, rsa["unpinned"], rsa["descriptions"]))

    # Sitelinks
    def create_sitelinks():
        ops = []
        for title, d1, d2, url in SITELINKS:
            op = client.get_type("AssetOperation")
            op.create.sitelink_asset.link_text = title
            op.create.sitelink_asset.description1 = d1
            op.create.sitelink_asset.description2 = d2
            op.create.final_urls.append(url)
            ops.append(op)
        resp = asset_service.mutate_assets(customer_id=customer_id, operations=ops)
        return [r.resource_name for r in resp.results]

    sitelink_assets = run(f"Created {len(SITELINKS)} sitelink assets", create_sitelinks)

    # Callouts
    def create_callouts():
        ops = []
        for text in CALLOUTS:
            op = client.get_type("AssetOperation")
            op.create.callout_asset.callout_text = text
            ops.append(op)
        resp = asset_service.mutate_assets(customer_id=customer_id, operations=ops)
        return [r.resource_name for r in resp.results]

    callout_assets = run(f"Created {len(CALLOUTS)} callout assets", create_callouts)

    # Structured snippets
    def create_snippets():
        ops = []
        for header, values in STRUCTURED_SNIPPETS:
            op = client.get_type("AssetOperation")
            op.create.structured_snippet_asset.header = header
            op.create.structured_snippet_asset.values.extend(values)
            ops.append(op)
        resp = asset_service.mutate_assets(customer_id=customer_id, operations=ops)
        return [r.resource_name for r in resp.results]

    snippet_assets = run(f"Created {len(STRUCTURED_SNIPPETS)} structured snippet assets", create_snippets)

    # Attach all at campaign level
    def attach_campaign_assets(asset_resources, field_type):
        ops = []
        for asset_resource in asset_resources:
            op = client.get_type("CampaignAssetOperation")
            op.create.campaign = f"customers/{customer_id}/campaigns/{CAMPAIGN_ID}"
            op.create.asset = asset_resource
            op.create.field_type = field_type
            ops.append(op)
        campaign_asset_service.mutate_campaign_assets(customer_id=customer_id, operations=ops)
        return len(ops)

    if sitelink_assets:
        run("Attached sitelinks to campaign", lambda: attach_campaign_assets(
            sitelink_assets, client.enums.AssetFieldTypeEnum.SITELINK))
    if callout_assets:
        run("Attached callouts to campaign", lambda: attach_campaign_assets(
            callout_assets, client.enums.AssetFieldTypeEnum.CALLOUT))
    if snippet_assets:
        run("Attached structured snippets to campaign", lambda: attach_campaign_assets(
            snippet_assets, client.enums.AssetFieldTypeEnum.STRUCTURED_SNIPPET))

    print("\n Business name / logo assets skipped — not attachable via CampaignAsset for")
    print(" standard Search campaigns (they come from Advertiser Identity / Business Profile")
    print(" linkage in the Google Ads UI, and logo needs an actual 1200x1200 image file).")


if __name__ == "__main__":
    main()
