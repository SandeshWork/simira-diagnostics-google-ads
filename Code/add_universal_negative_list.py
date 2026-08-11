"""Adds the Section A universal negative keyword list (150 terms, universal-negative-keywords.md)
to the account as a Shared Negative Keyword List, then attaches it to the Health Packages campaign.
All terms use BROAD match (none of the source terms are quoted/bracketed)."""

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

LIST_NAME = "Universal Service Business Negatives v1"

A1_JOB_SEEKERS = [
    "jobs", "job", "hiring", "recruit", "recruiting", "recruitment", "recruiter",
    "career", "careers", "employment", "employer", "employee", "salary", "salaries",
    "wage", "wages", "hourly pay", "resume", "cv", "intern", "interns", "internship",
    "internships", "apprentice", "apprentices", "apprenticeship", "apprenticeships",
    "volunteer", "vacancy", "vacancies", "position open", "hiring near me",
    "work from home", "indeed", "glassdoor", "ziprecruiter",
]

A2_DIY = [
    "diy", "do it yourself", "how to", "howto", "how do", "how do you", "tutorial",
    "tutorials", "guide", "guides", "step by step", "instructions", "youtube",
    "video", "videos", "template", "templates", "example", "examples", "how to fix",
    "how to repair", "how to install", "how to remove", "how to clean",
    "how to replace", "how to build", "homemade", "yourself",
]

A3_EDUCATION = [
    "school", "schools", "schooling", "college", "university", "class", "classes",
    "course", "courses", "training", "trainee", "trained", "certification",
    "certificate", "certified", "license cost", "licensing", "license requirement",
    "license requirements", "become a", "how to become", "exam",
]

A4_FREE_DISCOUNT = [
    "free", "freebie", "giveaway", "giveaways", "sample", "samples", "trial",
    "discount", "discounted", "voucher", "coupon", "coupons", "promo code",
    "clearance", "secondhand",
]

A5_INFORMATIONAL = [
    "what is", "what is a", "what does", "what are", "meaning", "definition",
    "wikipedia", "wiki", "reddit", "quora", "forum", "forums", "blog", "review",
    "reviews", "ratings",
]

A6_CUSTOMER_SUPPORT = [
    "complaint", "complaints", "refund", "refunds", "return policy", "cancel",
    "cancellation", "warranty claim", "problem", "problems", "not working",
    "broken", "contact", "phone number", "customer service", "help", "login",
    "sign in",
]

A7_RESTRICTED = [
    "porn", "adult", "nude", "sex", "gambling", "casino", "weed", "marijuana",
    "cbd", "crypto", "bitcoin", "nft", "mlm", "ponzi",
]

ALL_TERMS = (
    A1_JOB_SEEKERS + A2_DIY + A3_EDUCATION + A4_FREE_DISCOUNT + A5_INFORMATIONAL
    + A6_CUSTOMER_SUPPORT + A7_RESTRICTED
)
# dedupe, preserve order (source list has "vacancy" listed twice)
seen = set()
ALL_TERMS = [t for t in ALL_TERMS if not (t in seen or seen.add(t))]


def match_type_for(term):
    if term.startswith('"') and term.endswith('"'):
        return client.enums.KeywordMatchTypeEnum.PHRASE, term.strip('"')
    if term.startswith("[") and term.endswith("]"):
        return client.enums.KeywordMatchTypeEnum.EXACT, term.strip("[]")
    return client.enums.KeywordMatchTypeEnum.BROAD, term


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
    print(f" Terms to add: {len(ALL_TERMS)} (150 source lines, 1 duplicate 'vacancy' collapsed)\n")

    ga_service = client.get_service("GoogleAdsService")
    shared_set_service = client.get_service("SharedSetService")
    shared_criterion_service = client.get_service("SharedCriterionService")
    campaign_shared_set_service = client.get_service("CampaignSharedSetService")

    def get_or_create_shared_set():
        query = (
            "SELECT shared_set.resource_name FROM shared_set "
            f"WHERE shared_set.name = '{LIST_NAME}' AND shared_set.status != 'REMOVED'"
        )
        existing = list(ga_service.search(customer_id=customer_id, query=query))
        if existing:
            return existing[0].shared_set.resource_name
        op = client.get_type("SharedSetOperation")
        op.create.name = LIST_NAME
        op.create.type_ = client.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS
        resp = shared_set_service.mutate_shared_sets(customer_id=customer_id, operations=[op])
        return resp.results[0].resource_name

    shared_set_resource = run(f'Shared negative keyword list: "{LIST_NAME}"', get_or_create_shared_set)
    if not shared_set_resource:
        sys.exit(1)

    def add_criteria():
        ops = []
        for term in ALL_TERMS:
            match_type, text = match_type_for(term)
            op = client.get_type("SharedCriterionOperation")
            op.create.shared_set = shared_set_resource
            op.create.keyword.text = text
            op.create.keyword.match_type = match_type
            ops.append(op)
        resp = shared_criterion_service.mutate_shared_criteria(customer_id=customer_id, operations=ops)
        return len(resp.results)

    run(f"Added {len(ALL_TERMS)} negative keywords to the list", add_criteria)

    def attach_to_campaign():
        query = (
            "SELECT campaign_shared_set.resource_name FROM campaign_shared_set "
            f"WHERE campaign_shared_set.campaign = 'customers/{customer_id}/campaigns/{CAMPAIGN_ID}' "
            f"AND campaign_shared_set.shared_set = '{shared_set_resource}'"
        )
        existing = list(ga_service.search(customer_id=customer_id, query=query))
        if existing:
            return existing[0].campaign_shared_set.resource_name
        op = client.get_type("CampaignSharedSetOperation")
        op.create.campaign = f"customers/{customer_id}/campaigns/{CAMPAIGN_ID}"
        op.create.shared_set = shared_set_resource
        resp = campaign_shared_set_service.mutate_campaign_shared_sets(customer_id=customer_id, operations=[op])
        return resp.results[0].resource_name

    run("Attached list to New_Health_Packages_Navi_Mum", attach_to_campaign)


if __name__ == "__main__":
    main()
