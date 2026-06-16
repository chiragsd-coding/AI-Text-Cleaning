"""
Example usage of AI Text Cleaning API
Run this to see all features in action
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


class TextCleaningClient:
    """Simple client for AI Text Cleaning API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token = None
        self.api_key = None
        self.user_id = None

    def register(self, email: str, password: str, full_name: str) -> dict:
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
            },
        )
        return response.json()

    def login(self, email: str, password: str) -> dict:
        """Login and get JWT token."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
        )
        data = response.json()
        self.token = data.get("access_token")
        return data

    def get_headers(self) -> dict:
        """Get authorization headers."""
        if self.api_key:
            return {"X-API-Key": self.api_key}
        elif self.token:
            return {"Authorization": f"Bearer {self.token}"}
        else:
            raise ValueError("Not authenticated. Register or login first.")

    def clean_text(
        self,
        text: str,
        operations: Optional[list] = None,
        target_style: str = "formal",
    ) -> dict:
        """Clean text with specified operations."""
        response = requests.post(
            f"{self.base_url}/clean/text",
            headers=self.get_headers(),
            json={
                "text": text,
                "operations": operations,
                "target_style": target_style,
            },
        )
        return response.json()

    def autocorrect(self, text: str) -> dict:
        """Autocorrect text with smart operation selection."""
        response = requests.post(
            f"{self.base_url}/clean/autocorrect",
            headers=self.get_headers(),
            json={"text": text},
        )
        return response.json()

    def batch_clean(
        self,
        texts: list,
        operations: Optional[list] = None,
    ) -> dict:
        """Clean multiple texts in batch."""
        response = requests.post(
            f"{self.base_url}/clean/batch",
            headers=self.get_headers(),
            json={
                "texts": texts,
                "operations": operations,
            },
        )
        return response.json()

    def get_subscription(self) -> dict:
        """Get current subscription."""
        response = requests.get(
            f"{self.base_url}/subscriptions/me",
            headers=self.get_headers(),
        )
        return response.json()

    def list_plans(self) -> dict:
        """List all subscription plans."""
        response = requests.get(f"{self.base_url}/subscriptions/plans")
        return response.json()

    def create_api_key(self, name: str) -> dict:
        """Create a new API key."""
        response = requests.post(
            f"{self.base_url}/api-keys",
            headers=self.get_headers(),
            json={"name": name},
        )
        data = response.json()
        self.api_key = data.get("key")
        return data

    def list_api_keys(self) -> dict:
        """List all API keys."""
        response = requests.get(
            f"{self.base_url}/api-keys",
            headers=self.get_headers(),
        )
        return response.json()

    def get_health(self) -> dict:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(title: str, data: dict):
    """Print formatted result."""
    print(f"\n➜ {title}")
    print(json.dumps(data, indent=2))


def main():
    """Run all examples."""
    print("\n🚀 AI Text Cleaning API - Examples\n")

    # Initialize client
    client = TextCleaningClient()

    # Check health
    print_section("1. API Health Check")
    health = client.get_health()
    print_result("Health Status", health)

    # Register
    print_section("2. User Registration")
    register_result = client.register(
        email="test@example.com",
        password="TestPassword123",
        full_name="Test User",
    )
    print_result("Registration", register_result)

    # Login
    print_section("3. User Login")
    login_result = client.login(
        email="test@example.com",
        password="TestPassword123",
    )
    print_result("Login", login_result)
    print(f"\n✓ Token: {client.token[:50]}...")

    # Get subscription
    print_section("4. Check Current Subscription")
    subscription = client.get_subscription()
    print_result("Current Subscription", subscription)

    # List plans
    print_section("5. List Available Plans")
    plans = client.list_plans()
    for plan in plans:
        print(f"\n  {plan['display_name']} (${plan['price_usd']}/mo)")
        print(f"    - Requests/day: {plan['requests_per_day']}")
        print(f"    - Max chars: {plan['max_chars_per_request']}")

    # Clean Text - Grammar
    print_section("6. Clean Text - Grammar Fixing")
    result = client.clean_text(
        "ur text has grammar mistakess",
        operations=["grammar"],
    )
    print_result("Result", result)

    # Clean Text - Remove Extra Spaces
    print_section("7. Clean Text - Remove Extra Spaces")
    result = client.clean_text(
        "text   with    extra    spaces",
        operations=["spaces"],
    )
    print_result("Result", result)

    # Clean Text - Capitalize
    print_section("8. Clean Text - Standardize Capitalization")
    result = client.clean_text(
        "i am a student. do you like coding?",
        operations=["capitalization"],
    )
    print_result("Result", result)

    # Clean Text - Remove Emojis
    print_section("9. Clean Text - Remove Emojis")
    result = client.clean_text(
        "Hello 👋 world 🌍! 😂😂😂",
        operations=["emojis"],
    )
    print_result("Result", result)

    # Clean Text - Remove PII
    print_section("10. Clean Text - Remove PII")
    result = client.clean_text(
        "My email is john@example.com and phone is 555-1234567",
        operations=["pii"],
    )
    print_result("Result", result)

    # Clean Text - Fix OCR
    print_section("11. Clean Text - Fix OCR Errors")
    result = client.clean_text(
        "0ptical Character Rec0gnition is arn technology",
        operations=["ocr"],
    )
    print_result("Result", result)

    # Clean Text - Convert Style
    print_section("12. Clean Text - Style Conversion (Formal)")
    result = client.clean_text(
        "gonna wanna can't won't u ur",
        operations=["style"],
        target_style="formal",
    )
    print_result("Result", result)

    # Autocorrect
    print_section("13. Autocorrect (Smart Operation Selection)")
    result = client.autocorrect(
        "ur text has   grammar mistakess!!! 😂🎉 contact me at john@example.com"
    )
    print_result("Result", result)

    # Batch Processing
    print_section("14. Batch Processing (Multiple Texts)")
    result = client.batch_clean(
        texts=[
            "text 1 with errors!!!",
            "text 2 needs   cleaning",
            "text 3 😂😂😂",
        ],
        operations=["grammar", "spaces", "emojis"],
    )
    print_result("Batch Result", result)

    # Create API Key
    print_section("15. Create API Key")
    api_key_result = client.create_api_key("Example API Key")
    print_result("API Key Created", api_key_result)

    # List API Keys
    print_section("16. List API Keys")
    api_keys = client.list_api_keys()
    print_result("API Keys", api_keys)

    # Use API Key for requests
    print_section("17. Clean Text Using API Key (No JWT)")
    # Switch to API key auth
    old_token = client.token
    client.token = None
    result = client.clean_text(
        "text with api key auth",
        operations=["spaces"],
    )
    print_result("Result (Using API Key)", result)
    client.token = old_token  # Switch back to JWT

    # Complex example
    print_section("18. Complex Real-World Example")
    messy_text = """
    ur resume is so gr8!!! 😂😂
    
    exp: senior developer w/ 5+ yrs xp
    contact: john.doe@company.com or 555-1234567
    
    skillz: python, javascript, aws, etc...
    
    can't wait 2 hear from u!!! thru next week pls
    """

    result = client.clean_text(
        messy_text,
        operations=[
            "grammar",
            "spaces",
            "capitalization",
            "emojis",
            "pii",
            "style",
        ],
        target_style="formal",
    )
    print_result("Resume Cleaning Result", result)

    print_section("✓ Examples Complete!")
    print(
        """
All examples completed successfully! 🎉

Next steps:
1. Read the full API documentation: API_DOCUMENTATION.md
2. Start integrating the API into your application
3. Upgrade your subscription plan for higher limits
4. Set up webhooks for payment notifications

For support, email: support@aitextcleaning.com
    """
    )


if __name__ == "__main__":
    main()
