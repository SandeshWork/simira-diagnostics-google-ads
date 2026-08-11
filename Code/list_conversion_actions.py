"""Lists conversion actions in the account: ID, name, category, status, primary-for-goal."""

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
ga_service = client.get_service("GoogleAdsService")

customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
query = """
    SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.category,
        conversion_action.status,
        conversion_action.primary_for_goal,
        conversion_action.type
    FROM conversion_action
    ORDER BY conversion_action.id
"""

response = ga_service.search(customer_id=customer_id, query=query)
print(f"\nConversion actions for customer {customer_id}:\n")
for row in response:
    ca = row.conversion_action
    print(
        f"  ID {ca.id} | {ca.name} | category={ca.category.name} | "
        f"status={ca.status.name} | type={ca.type_.name} | primary_for_goal={ca.primary_for_goal}"
    )
