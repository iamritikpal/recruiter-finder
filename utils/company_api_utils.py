import requests
import yfinance as yf
import logging
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
from .company_cache import company_cache

logger = logging.getLogger(__name__)

class CompanyDataService:
    """Service to fetch real company data from multiple APIs"""
    
    def __init__(self):
        self.clearbit_logo_base = "https://logo.clearbit.com"
        self.alpha_vantage_key = None  # Can be added later if needed
        self.cache_key = "all_companies"
        
        # Major companies with their stock symbols and domains
        self.major_companies = [
            # Tech Giants
            {"symbol": "AAPL", "domain": "apple.com", "name": "Apple Inc."},
            {"symbol": "MSFT", "domain": "microsoft.com", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "domain": "google.com", "name": "Alphabet Inc. (Google)"},
            {"symbol": "AMZN", "domain": "amazon.com", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "domain": "tesla.com", "name": "Tesla, Inc."},
            {"symbol": "META", "domain": "meta.com", "name": "Meta Platforms, Inc."},
            {"symbol": "NFLX", "domain": "netflix.com", "name": "Netflix, Inc."},
            {"symbol": "NVDA", "domain": "nvidia.com", "name": "NVIDIA Corporation"},
            {"symbol": "ORCL", "domain": "oracle.com", "name": "Oracle Corporation"},
            {"symbol": "CRM", "domain": "salesforce.com", "name": "Salesforce, Inc."},
            {"symbol": "ADBE", "domain": "adobe.com", "name": "Adobe Inc."},
            {"symbol": "UBER", "domain": "uber.com", "name": "Uber Technologies, Inc."},
            {"symbol": "SPOT", "domain": "spotify.com", "name": "Spotify Technology S.A."},
            {"symbol": "ABNB", "domain": "airbnb.com", "name": "Airbnb, Inc."},
            {"symbol": "SQ", "domain": "squareup.com", "name": "Block, Inc. (Square)"},
            {"symbol": "SHOP", "domain": "shopify.com", "name": "Shopify Inc."},
            {"symbol": "ZM", "domain": "zoom.us", "name": "Zoom Video Communications"},
            {"symbol": "PYPL", "domain": "paypal.com", "name": "PayPal Holdings, Inc."},
            {"symbol": "INTC", "domain": "intel.com", "name": "Intel Corporation"},
            {"symbol": "AMD", "domain": "amd.com", "name": "Advanced Micro Devices"},
            {"symbol": "IBM", "domain": "ibm.com", "name": "International Business Machines"},
            {"symbol": "CSCO", "domain": "cisco.com", "name": "Cisco Systems, Inc."},
            {"symbol": "V", "domain": "visa.com", "name": "Visa Inc."},
            {"symbol": "MA", "domain": "mastercard.com", "name": "Mastercard Incorporated"},
            {"symbol": "DIS", "domain": "disney.com", "name": "The Walt Disney Company"},
            
            # Additional Public Tech Companies
            {"symbol": "BABA", "domain": "alibaba.com", "name": "Alibaba Group Holding Limited"},
            {"symbol": "TME", "domain": "tencentmusic.com", "name": "Tencent Music Entertainment Group"},
            {"symbol": "BIDU", "domain": "baidu.com", "name": "Baidu, Inc."},
            {"symbol": "JD", "domain": "jd.com", "name": "JD.com, Inc."},
            {"symbol": "NTES", "domain": "netease.com", "name": "NetEase, Inc."},
            {"symbol": "SE", "domain": "sea.com", "name": "Sea Limited"},
            {"symbol": "GRAB", "domain": "grab.com", "name": "Grab Holdings Limited"},
            {"symbol": "DDOG", "domain": "datadoghq.com", "name": "Datadog, Inc."},
            {"symbol": "SNOW", "domain": "snowflake.com", "name": "Snowflake Inc."},
            {"symbol": "PLTR", "domain": "palantir.com", "name": "Palantir Technologies Inc."},
            {"symbol": "U", "domain": "unity.com", "name": "Unity Software Inc."},
            {"symbol": "RBLX", "domain": "roblox.com", "name": "Roblox Corporation"},
            {"symbol": "DOCU", "domain": "docusign.com", "name": "DocuSign, Inc."},
            {"symbol": "OKTA", "domain": "okta.com", "name": "Okta, Inc."},
            {"symbol": "TWLO", "domain": "twilio.com", "name": "Twilio Inc."},
            {"symbol": "CRWD", "domain": "crowdstrike.com", "name": "CrowdStrike Holdings, Inc."},
            {"symbol": "ZS", "domain": "zscaler.com", "name": "Zscaler, Inc."},
            {"symbol": "TEAM", "domain": "atlassian.com", "name": "Atlassian Corporation"},
            {"symbol": "WDAY", "domain": "workday.com", "name": "Workday, Inc."},
            {"symbol": "VEEV", "domain": "veeva.com", "name": "Veeva Systems Inc."},
            {"symbol": "SPLK", "domain": "splunk.com", "name": "Splunk Inc."},
            {"symbol": "NOW", "domain": "servicenow.com", "name": "ServiceNow, Inc."},
            {"symbol": "FTNT", "domain": "fortinet.com", "name": "Fortinet, Inc."},
            {"symbol": "PANW", "domain": "paloaltonetworks.com", "name": "Palo Alto Networks, Inc."},
            
            # Financial Services
            {"symbol": "JPM", "domain": "jpmorganchase.com", "name": "JPMorgan Chase & Co."},
            {"symbol": "BAC", "domain": "bankofamerica.com", "name": "Bank of America Corporation"},
            {"symbol": "WFC", "domain": "wellsfargo.com", "name": "Wells Fargo & Company"},
            {"symbol": "GS", "domain": "goldmansachs.com", "name": "The Goldman Sachs Group, Inc."},
            {"symbol": "MS", "domain": "morganstanley.com", "name": "Morgan Stanley"},
            {"symbol": "AXP", "domain": "americanexpress.com", "name": "American Express Company"},
            {"symbol": "BLK", "domain": "blackrock.com", "name": "BlackRock, Inc."},
            {"symbol": "SPGI", "domain": "spglobal.com", "name": "S&P Global Inc."},
            {"symbol": "CME", "domain": "cmegroup.com", "name": "CME Group Inc."},
            {"symbol": "ICE", "domain": "theice.com", "name": "Intercontinental Exchange, Inc."},
            
            # E-commerce & Retail
            {"symbol": "WMT", "domain": "walmart.com", "name": "Walmart Inc."},
            {"symbol": "HD", "domain": "homedepot.com", "name": "The Home Depot, Inc."},
            {"symbol": "COST", "domain": "costco.com", "name": "Costco Wholesale Corporation"},
            {"symbol": "TGT", "domain": "target.com", "name": "Target Corporation"},
            {"symbol": "EBAY", "domain": "ebay.com", "name": "eBay Inc."},
            {"symbol": "ETSY", "domain": "etsy.com", "name": "Etsy, Inc."},
            
            # Media & Entertainment
            {"symbol": "CMCSA", "domain": "comcast.com", "name": "Comcast Corporation"},
            {"symbol": "VZ", "domain": "verizon.com", "name": "Verizon Communications Inc."},
            {"symbol": "T", "domain": "att.com", "name": "AT&T Inc."},
            {"symbol": "TMUS", "domain": "t-mobile.com", "name": "T-Mobile US, Inc."},
            {"symbol": "WBD", "domain": "wbd.com", "name": "Warner Bros. Discovery, Inc."},
            {"symbol": "PARA", "domain": "paramount.com", "name": "Paramount Global"},
            {"symbol": "FOXA", "domain": "fox.com", "name": "Fox Corporation"},
            
            # Healthcare & Pharma
            {"symbol": "JNJ", "domain": "jnj.com", "name": "Johnson & Johnson"},
            {"symbol": "PFE", "domain": "pfizer.com", "name": "Pfizer Inc."},
            {"symbol": "ABBV", "domain": "abbvie.com", "name": "AbbVie Inc."},
            {"symbol": "MRK", "domain": "merck.com", "name": "Merck & Co., Inc."},
            {"symbol": "TMO", "domain": "thermofisher.com", "name": "Thermo Fisher Scientific Inc."},
            {"symbol": "DHR", "domain": "danaher.com", "name": "Danaher Corporation"},
            {"symbol": "BMY", "domain": "bms.com", "name": "Bristol-Myers Squibb Company"},
            {"symbol": "AMGN", "domain": "amgen.com", "name": "Amgen Inc."},
            {"symbol": "GILD", "domain": "gilead.com", "name": "Gilead Sciences, Inc."},
            {"symbol": "VRTX", "domain": "vrtx.com", "name": "Vertex Pharmaceuticals Incorporated"},
            
            # Aerospace & Defense
            {"symbol": "BA", "domain": "boeing.com", "name": "The Boeing Company"},
            {"symbol": "LMT", "domain": "lockheedmartin.com", "name": "Lockheed Martin Corporation"},
            {"symbol": "RTX", "domain": "rtx.com", "name": "RTX Corporation"},
            {"symbol": "NOC", "domain": "northropgrumman.com", "name": "Northrop Grumman Corporation"},
            {"symbol": "GD", "domain": "gd.com", "name": "General Dynamics Corporation"},
            
            # Automotive
            {"symbol": "GM", "domain": "gm.com", "name": "General Motors Company"},
            {"symbol": "F", "domain": "ford.com", "name": "Ford Motor Company"},
            {"symbol": "RIVN", "domain": "rivian.com", "name": "Rivian Automotive, Inc."},
            {"symbol": "LCID", "domain": "lucidmotors.com", "name": "Lucid Group, Inc."},
            {"symbol": "NIO", "domain": "nio.com", "name": "NIO Inc."},
            {"symbol": "XPEV", "domain": "xiaopeng.com", "name": "XPeng Inc."},
            {"symbol": "LI", "domain": "lixiang.com", "name": "Li Auto Inc."},
            
            # Private/Other companies
            {"symbol": None, "domain": "stripe.com", "name": "Stripe, Inc."},
            {"symbol": None, "domain": "slack.com", "name": "Slack Technologies"},
            {"symbol": None, "domain": "gitlab.com", "name": "GitLab Inc."},
            {"symbol": None, "domain": "notion.so", "name": "Notion Labs, Inc."},
            {"symbol": None, "domain": "figma.com", "name": "Figma, Inc."},
            {"symbol": None, "domain": "canva.com", "name": "Canva Pty Ltd"},
            {"symbol": None, "domain": "dropbox.com", "name": "Dropbox, Inc."},
            {"symbol": None, "domain": "reddit.com", "name": "Reddit, Inc."},
            {"symbol": None, "domain": "discord.com", "name": "Discord Inc."},
            {"symbol": None, "domain": "bytedance.com", "name": "ByteDance Ltd."},
            {"symbol": None, "domain": "spacex.com", "name": "Space Exploration Technologies Corp."},
            {"symbol": None, "domain": "openai.com", "name": "OpenAI"},
            {"symbol": None, "domain": "anthropic.com", "name": "Anthropic"},
            {"symbol": None, "domain": "databricks.com", "name": "Databricks, Inc."},
            {"symbol": None, "domain": "instacart.com", "name": "Instacart"},
            {"symbol": None, "domain": "doordash.com", "name": "DoorDash, Inc."},
            {"symbol": None, "domain": "chime.com", "name": "Chime Financial, Inc."},
            {"symbol": None, "domain": "robinhood.com", "name": "Robinhood Markets, Inc."},
            {"symbol": None, "domain": "coinbase.com", "name": "Coinbase Global, Inc."},
            {"symbol": None, "domain": "binance.com", "name": "Binance"},
            {"symbol": None, "domain": "kraken.com", "name": "Kraken"},
            {"symbol": None, "domain": "epic.com", "name": "Epic Systems Corporation"},
            {"symbol": None, "domain": "cargill.com", "name": "Cargill, Incorporated"},
            {"symbol": None, "domain": "kochind.com", "name": "Koch Industries, Inc."},
            {"symbol": None, "domain": "mars.com", "name": "Mars, Incorporated"},
            {"symbol": None, "domain": "ikea.com", "name": "IKEA"},
            {"symbol": None, "domain": "aldi.com", "name": "ALDI"},
            {"symbol": None, "domain": "bmw.com", "name": "BMW Group"},
            {"symbol": None, "domain": "mercedes-benz.com", "name": "Mercedes-Benz Group AG"},
            {"symbol": None, "domain": "volkswagen.com", "name": "Volkswagen Group"},
            {"symbol": None, "domain": "toyota.com", "name": "Toyota Motor Corporation"},
            {"symbol": None, "domain": "honda.com", "name": "Honda Motor Co., Ltd."},
            {"symbol": None, "domain": "nissan.com", "name": "Nissan Motor Corporation"},
            {"symbol": None, "domain": "samsung.com", "name": "Samsung Electronics Co., Ltd."},
            {"symbol": None, "domain": "sony.com", "name": "Sony Group Corporation"},
            {"symbol": None, "domain": "nintendo.com", "name": "Nintendo Co., Ltd."},
            {"symbol": None, "domain": "huawei.com", "name": "Huawei Technologies Co., Ltd."},
            {"symbol": None, "domain": "xiaomi.com", "name": "Xiaomi Corporation"},
            {"symbol": None, "domain": "oppo.com", "name": "OPPO"},
            {"symbol": None, "domain": "vivo.com", "name": "Vivo Communication Technology Co. Ltd."},
            {"symbol": None, "domain": "realme.com", "name": "Realme"},
            {"symbol": None, "domain": "oneplus.com", "name": "OnePlus Technology Co., Ltd."},
        ]
        
        # Industry categories mapping
        self.industry_mapping = {
            # Tech Giants
            "apple.com": {"category": "Technology", "industry": "Consumer Electronics", "tags": ["iPhone", "Mac", "iPad", "Services", "Wearables", "Design"]},
            "microsoft.com": {"category": "Technology", "industry": "Computer Software", "tags": ["Cloud Computing", "Office Software", "Gaming", "AI", "Enterprise Software"]},
            "google.com": {"category": "Technology", "industry": "Internet & Technology", "tags": ["Search", "Cloud Computing", "AI", "Advertising", "Mobile", "Hardware"]},
            "amazon.com": {"category": "E-commerce", "industry": "E-commerce & Cloud", "tags": ["E-commerce", "AWS", "Prime", "Logistics", "AI", "Alexa"]},
            "tesla.com": {"category": "Automotive", "industry": "Electric Vehicles", "tags": ["Electric Vehicles", "Autonomous Driving", "Energy Storage", "Solar", "AI"]},
            "meta.com": {"category": "Social Media", "industry": "Social Media", "tags": ["Social Media", "VR/AR", "Metaverse", "Advertising", "AI", "Communication"]},
            "netflix.com": {"category": "Entertainment", "industry": "Streaming Entertainment", "tags": ["Streaming", "Original Content", "Entertainment", "Global", "AI Recommendations"]},
            "nvidia.com": {"category": "Technology", "industry": "Semiconductors", "tags": ["GPU", "AI Computing", "Gaming", "Data Centers", "Autonomous Vehicles"]},
            "oracle.com": {"category": "Technology", "industry": "Enterprise Software", "tags": ["Database", "Cloud Computing", "Enterprise Software", "Java", "Analytics"]},
            "salesforce.com": {"category": "Cloud Computing", "industry": "Cloud Software", "tags": ["CRM", "Cloud Computing", "Sales Automation", "Marketing", "Customer Service"]},
            "adobe.com": {"category": "Software", "industry": "Creative Software", "tags": ["Creative Software", "Design Tools", "Digital Marketing", "PDF", "Photography"]},
            "uber.com": {"category": "Transportation", "industry": "Ride-sharing", "tags": ["Ride-sharing", "Food Delivery", "Logistics", "Autonomous Vehicles", "Mobility"]},
            "spotify.com": {"category": "Music", "industry": "Audio Streaming", "tags": ["Music Streaming", "Podcasts", "Audio", "AI Recommendations", "Discovery"]},
            "airbnb.com": {"category": "Travel", "industry": "Travel & Hospitality", "tags": ["Vacation Rentals", "Travel", "Experiences", "Hospitality", "Marketplace"]},
            "squareup.com": {"category": "Fintech", "industry": "Financial Technology", "tags": ["Payment Processing", "Point of Sale", "Small Business", "Cash App"]},
            "shopify.com": {"category": "E-commerce", "industry": "E-commerce Platform", "tags": ["E-commerce Platform", "Online Stores", "Payments", "Merchant Services"]},
            "zoom.us": {"category": "Communication", "industry": "Video Communications", "tags": ["Video Conferencing", "Remote Work", "Communication", "Cloud", "Collaboration"]},
            "paypal.com": {"category": "Fintech", "industry": "Digital Payments", "tags": ["Digital Payments", "Online Payments", "Venmo", "Cryptocurrency", "Financial Services"]},
            "intel.com": {"category": "Technology", "industry": "Semiconductors", "tags": ["Processors", "Semiconductors", "Computing", "Data Centers", "AI"]},
            "amd.com": {"category": "Technology", "industry": "Semiconductors", "tags": ["Processors", "Graphics Cards", "Gaming", "Data Centers", "Computing"]},
            "ibm.com": {"category": "Technology", "industry": "Technology Services", "tags": ["Cloud Computing", "AI", "Watson", "Enterprise Services", "Consulting"]},
            "cisco.com": {"category": "Technology", "industry": "Networking", "tags": ["Networking", "Security", "Collaboration", "Cloud", "IoT"]},
            "visa.com": {"category": "Fintech", "industry": "Payment Networks", "tags": ["Payment Processing", "Credit Cards", "Digital Payments", "Financial Networks"]},
            "mastercard.com": {"category": "Fintech", "industry": "Payment Networks", "tags": ["Payment Processing", "Credit Cards", "Digital Payments", "Financial Technology"]},
            "disney.com": {"category": "Entertainment", "industry": "Entertainment", "tags": ["Movies", "Theme Parks", "Streaming", "Media", "Family Entertainment"]},
            
            # Additional Tech Companies
            "alibaba.com": {"category": "E-commerce", "industry": "E-commerce & Cloud", "tags": ["E-commerce", "Cloud Computing", "B2B", "Digital Payments", "Logistics"]},
            "tencentmusic.com": {"category": "Music", "industry": "Digital Music", "tags": ["Music Streaming", "Digital Entertainment", "Social Music", "Live Streaming"]},
            "baidu.com": {"category": "Technology", "industry": "Internet Services", "tags": ["Search Engine", "AI", "Autonomous Driving", "Cloud Computing", "Maps"]},
            "jd.com": {"category": "E-commerce", "industry": "E-commerce", "tags": ["E-commerce", "Logistics", "Supply Chain", "Technology", "Retail"]},
            "netease.com": {"category": "Gaming", "industry": "Gaming & Entertainment", "tags": ["Gaming", "Online Games", "Mobile Games", "Entertainment", "Technology"]},
            "sea.com": {"category": "Technology", "industry": "Digital Entertainment", "tags": ["Gaming", "E-commerce", "Digital Payments", "Southeast Asia", "Mobile"]},
            "grab.com": {"category": "Transportation", "industry": "Super App", "tags": ["Ride-hailing", "Food Delivery", "Digital Payments", "Logistics", "Southeast Asia"]},
            "datadoghq.com": {"category": "Technology", "industry": "Cloud Monitoring", "tags": ["Cloud Monitoring", "DevOps", "Analytics", "Security", "Infrastructure"]},
            "snowflake.com": {"category": "Technology", "industry": "Data Cloud", "tags": ["Data Warehouse", "Cloud Computing", "Analytics", "Big Data", "Machine Learning"]},
            "palantir.com": {"category": "Technology", "industry": "Data Analytics", "tags": ["Data Analytics", "Big Data", "Government", "Enterprise", "AI"]},
            "unity.com": {"category": "Technology", "industry": "Game Development", "tags": ["Game Engine", "3D Development", "AR/VR", "Real-time 3D", "Gaming"]},
            "roblox.com": {"category": "Gaming", "industry": "Gaming Platform", "tags": ["Gaming Platform", "User-Generated Content", "Virtual Worlds", "Social Gaming", "Metaverse"]},
            "docusign.com": {"category": "Technology", "industry": "Digital Transaction", "tags": ["Digital Signatures", "Document Management", "Workflow", "Legal Tech", "Cloud"]},
            "okta.com": {"category": "Technology", "industry": "Identity Management", "tags": ["Identity Management", "Security", "SSO", "Cloud Security", "Authentication"]},
            "twilio.com": {"category": "Technology", "industry": "Communications Platform", "tags": ["Communications API", "Messaging", "Voice", "Video", "Developer Tools"]},
            "crowdstrike.com": {"category": "Technology", "industry": "Cybersecurity", "tags": ["Cybersecurity", "Endpoint Protection", "Threat Intelligence", "Cloud Security", "AI"]},
            "zscaler.com": {"category": "Technology", "industry": "Cloud Security", "tags": ["Cloud Security", "Zero Trust", "Web Security", "Network Security", "SASE"]},
            "atlassian.com": {"category": "Technology", "industry": "Software Development", "tags": ["Project Management", "Issue Tracking", "Collaboration", "DevOps", "Jira"]},
            "workday.com": {"category": "Technology", "industry": "Enterprise Software", "tags": ["HR Software", "Financial Management", "Cloud ERP", "Analytics", "Workforce Management"]},
            "veeva.com": {"category": "Technology", "industry": "Life Sciences Software", "tags": ["Life Sciences", "CRM", "Clinical Data", "Regulatory", "Pharma"]},
            "splunk.com": {"category": "Technology", "industry": "Data Platform", "tags": ["Data Analytics", "Machine Learning", "Security", "Observability", "Search"]},
            "servicenow.com": {"category": "Technology", "industry": "Digital Workflow", "tags": ["IT Service Management", "Digital Workflows", "Automation", "Cloud", "AI"]},
            "fortinet.com": {"category": "Technology", "industry": "Cybersecurity", "tags": ["Network Security", "Firewalls", "Cybersecurity", "SD-WAN", "Secure Networking"]},
            "paloaltonetworks.com": {"category": "Technology", "industry": "Cybersecurity", "tags": ["Network Security", "Cloud Security", "Threat Prevention", "Firewalls", "Zero Trust"]},
            
            # Financial Services
            "jpmorganchase.com": {"category": "Financial Services", "industry": "Investment Banking", "tags": ["Investment Banking", "Commercial Banking", "Asset Management", "Trading", "Finance"]},
            "bankofamerica.com": {"category": "Financial Services", "industry": "Banking", "tags": ["Banking", "Investment Services", "Credit Cards", "Loans", "Wealth Management"]},
            "wellsfargo.com": {"category": "Financial Services", "industry": "Banking", "tags": ["Banking", "Mortgages", "Investment", "Business Banking", "Financial Services"]},
            "goldmansachs.com": {"category": "Financial Services", "industry": "Investment Banking", "tags": ["Investment Banking", "Securities", "Asset Management", "Trading", "Private Banking"]},
            "morganstanley.com": {"category": "Financial Services", "industry": "Investment Banking", "tags": ["Investment Banking", "Wealth Management", "Trading", "Securities", "Financial Advisory"]},
            "americanexpress.com": {"category": "Financial Services", "industry": "Financial Services", "tags": ["Credit Cards", "Travel Services", "Business Services", "Payment Solutions", "Rewards"]},
            "blackrock.com": {"category": "Financial Services", "industry": "Asset Management", "tags": ["Asset Management", "Investment", "ETFs", "Risk Management", "Financial Technology"]},
            "spglobal.com": {"category": "Financial Services", "industry": "Financial Information", "tags": ["Credit Ratings", "Market Intelligence", "Data Analytics", "Financial Research", "Indices"]},
            "cmegroup.com": {"category": "Financial Services", "industry": "Financial Markets", "tags": ["Derivatives", "Futures", "Options", "Clearing", "Market Data"]},
            "theice.com": {"category": "Financial Services", "industry": "Financial Markets", "tags": ["Trading", "Clearing", "Data Services", "Energy Markets", "Financial Infrastructure"]},
            
            # Retail & E-commerce
            "walmart.com": {"category": "Retail", "industry": "Retail", "tags": ["Retail", "Grocery", "E-commerce", "Supply Chain", "Technology"]},
            "homedepot.com": {"category": "Retail", "industry": "Home Improvement", "tags": ["Home Improvement", "Retail", "Hardware", "Building Materials", "Tools"]},
            "costco.com": {"category": "Retail", "industry": "Wholesale Retail", "tags": ["Wholesale", "Membership", "Retail", "Grocery", "Bulk Shopping"]},
            "target.com": {"category": "Retail", "industry": "Retail", "tags": ["Retail", "Fashion", "Home Goods", "Grocery", "E-commerce"]},
            "ebay.com": {"category": "E-commerce", "industry": "Online Marketplace", "tags": ["Online Marketplace", "Auctions", "E-commerce", "Collectibles", "Electronics"]},
            "etsy.com": {"category": "E-commerce", "industry": "Handmade Marketplace", "tags": ["Handmade", "Crafts", "Vintage", "Marketplace", "Creative"]},
            
            # Media & Telecommunications
            "comcast.com": {"category": "Telecommunications", "industry": "Media & Telecommunications", "tags": ["Cable", "Internet", "Media", "Broadcasting", "Entertainment"]},
            "verizon.com": {"category": "Telecommunications", "industry": "Telecommunications", "tags": ["Wireless", "5G", "Internet", "Cloud", "Business Services"]},
            "att.com": {"category": "Telecommunications", "industry": "Telecommunications", "tags": ["Wireless", "Internet", "Business Solutions", "5G", "Fiber"]},
            "t-mobile.com": {"category": "Telecommunications", "industry": "Wireless", "tags": ["Wireless", "5G", "Mobile", "Prepaid", "Business"]},
            "wbd.com": {"category": "Entertainment", "industry": "Media & Entertainment", "tags": ["Streaming", "Media", "Entertainment", "News", "Sports"]},
            "paramount.com": {"category": "Entertainment", "industry": "Media & Entertainment", "tags": ["Movies", "TV", "Streaming", "Entertainment", "Media"]},
            "fox.com": {"category": "Entertainment", "industry": "Media & Entertainment", "tags": ["Broadcasting", "News", "Sports", "Entertainment", "Media"]},
            
            # Healthcare & Pharmaceuticals
            "jnj.com": {"category": "Healthcare", "industry": "Pharmaceuticals", "tags": ["Pharmaceuticals", "Medical Devices", "Consumer Health", "Healthcare", "Life Sciences"]},
            "pfizer.com": {"category": "Healthcare", "industry": "Pharmaceuticals", "tags": ["Pharmaceuticals", "Vaccines", "Oncology", "Healthcare", "Research"]},
            "abbvie.com": {"category": "Healthcare", "industry": "Pharmaceuticals", "tags": ["Pharmaceuticals", "Immunology", "Oncology", "Neuroscience", "Healthcare"]},
            "merck.com": {"category": "Healthcare", "industry": "Pharmaceuticals", "tags": ["Pharmaceuticals", "Vaccines", "Oncology", "Healthcare", "Animal Health"]},
            "thermofisher.com": {"category": "Healthcare", "industry": "Life Sciences", "tags": ["Life Sciences", "Laboratory Equipment", "Diagnostics", "Research", "Biotechnology"]},
            "danaher.com": {"category": "Healthcare", "industry": "Life Sciences", "tags": ["Life Sciences", "Diagnostics", "Biotechnology", "Medical Technology", "Research"]},
            "bms.com": {"category": "Healthcare", "industry": "Pharmaceuticals", "tags": ["Pharmaceuticals", "Oncology", "Immunology", "Cardiovascular", "Healthcare"]},
            "amgen.com": {"category": "Healthcare", "industry": "Biotechnology", "tags": ["Biotechnology", "Oncology", "Inflammation", "Cardiovascular", "Bone Health"]},
            "gilead.com": {"category": "Healthcare", "industry": "Pharmaceuticals", "tags": ["Pharmaceuticals", "Antiviral", "Oncology", "HIV", "Hepatitis"]},
            "vrtx.com": {"category": "Healthcare", "industry": "Biotechnology", "tags": ["Biotechnology", "Rare Diseases", "Gene Therapy", "Cell Therapy", "Research"]},
            
            # Aerospace & Defense
            "boeing.com": {"category": "Aerospace & Defense", "industry": "Aerospace", "tags": ["Aircraft", "Defense", "Space", "Commercial Aviation", "Military"]},
            "lockheedmartin.com": {"category": "Aerospace & Defense", "industry": "Defense", "tags": ["Defense", "Aerospace", "Missiles", "Space", "Technology"]},
            "rtx.com": {"category": "Aerospace & Defense", "industry": "Aerospace & Defense", "tags": ["Aerospace", "Defense", "Engines", "Systems", "Technology"]},
            "northropgrumman.com": {"category": "Aerospace & Defense", "industry": "Defense", "tags": ["Defense", "Aerospace", "Cybersecurity", "Space", "Autonomous Systems"]},
            "gd.com": {"category": "Aerospace & Defense", "industry": "Defense", "tags": ["Defense", "Aerospace", "Marine Systems", "Land Systems", "Technology"]},
            
            # Automotive
            "gm.com": {"category": "Automotive", "industry": "Automotive", "tags": ["Automotive", "Electric Vehicles", "Autonomous Driving", "Manufacturing", "Mobility"]},
            "ford.com": {"category": "Automotive", "industry": "Automotive", "tags": ["Automotive", "Electric Vehicles", "Trucks", "Manufacturing", "Mobility"]},
            "rivian.com": {"category": "Automotive", "industry": "Electric Vehicles", "tags": ["Electric Vehicles", "Trucks", "Delivery Vans", "Sustainable Transportation", "Adventure"]},
            "lucidmotors.com": {"category": "Automotive", "industry": "Electric Vehicles", "tags": ["Electric Vehicles", "Luxury Cars", "Battery Technology", "Autonomous Driving", "Performance"]},
            "nio.com": {"category": "Automotive", "industry": "Electric Vehicles", "tags": ["Electric Vehicles", "Battery Swapping", "Autonomous Driving", "Smart Cars", "China"]},
            "xiaopeng.com": {"category": "Automotive", "industry": "Electric Vehicles", "tags": ["Electric Vehicles", "Smart Cars", "Autonomous Driving", "Technology", "China"]},
            "lixiang.com": {"category": "Automotive", "industry": "Electric Vehicles", "tags": ["Electric Vehicles", "Extended Range", "Smart Cars", "Family Vehicles", "China"]},
            
            # Private Companies
            "stripe.com": {"category": "Fintech", "industry": "Financial Technology", "tags": ["Payment Processing", "APIs", "E-commerce", "Global Payments", "Developer Tools"]},
            "slack.com": {"category": "Communication", "industry": "Business Communication", "tags": ["Team Communication", "Collaboration", "Workflow", "Integration", "Remote Work"]},
            "gitlab.com": {"category": "Technology", "industry": "DevOps Platform", "tags": ["DevOps", "Version Control", "CI/CD", "Software Development", "Git"]},
            "notion.so": {"category": "Productivity", "industry": "Productivity Software", "tags": ["Note-taking", "Project Management", "Collaboration", "Documentation", "Workspace"]},
            "figma.com": {"category": "Design", "industry": "Design Software", "tags": ["Design Tools", "UI/UX", "Collaboration", "Prototyping", "Vector Graphics"]},
            "canva.com": {"category": "Design", "industry": "Design Platform", "tags": ["Graphic Design", "Templates", "Visual Content", "Marketing", "Social Media"]},
            "dropbox.com": {"category": "Cloud Storage", "industry": "Cloud Storage", "tags": ["File Storage", "Collaboration", "Sync", "Backup", "Productivity"]},
            "reddit.com": {"category": "Social Media", "industry": "Social Media", "tags": ["Social Media", "Communities", "Discussion", "News", "Entertainment"]},
            "discord.com": {"category": "Communication", "industry": "Gaming Communication", "tags": ["Voice Chat", "Gaming", "Communities", "Streaming", "Communication"]},
            "bytedance.com": {"category": "Social Media", "industry": "Social Media", "tags": ["TikTok", "Social Media", "Short Video", "AI", "Global Platform"]},
            "spacex.com": {"category": "Aerospace", "industry": "Space Exploration", "tags": ["Space Exploration", "Rockets", "Satellites", "Mars", "Commercial Space"]},
            "openai.com": {"category": "Technology", "industry": "Artificial Intelligence", "tags": ["Artificial Intelligence", "GPT", "Machine Learning", "Research", "Language Models"]},
            "anthropic.com": {"category": "Technology", "industry": "Artificial Intelligence", "tags": ["AI Safety", "Constitutional AI", "Research", "Language Models", "Claude"]},
            "databricks.com": {"category": "Technology", "industry": "Data & Analytics", "tags": ["Data Analytics", "Machine Learning", "Big Data", "Spark", "Cloud"]},
            "instacart.com": {"category": "E-commerce", "industry": "Grocery Delivery", "tags": ["Grocery Delivery", "On-demand", "Marketplace", "Logistics", "Retail"]},
            "doordash.com": {"category": "Food Delivery", "industry": "Food Delivery", "tags": ["Food Delivery", "Logistics", "On-demand", "Restaurants", "Mobile"]},
            "chime.com": {"category": "Fintech", "industry": "Digital Banking", "tags": ["Digital Banking", "Mobile Banking", "Financial Services", "No Fees", "Savings"]},
            "robinhood.com": {"category": "Fintech", "industry": "Investment Platform", "tags": ["Investment", "Trading", "Stocks", "Cryptocurrency", "Commission-free"]},
            "coinbase.com": {"category": "Fintech", "industry": "Cryptocurrency", "tags": ["Cryptocurrency", "Bitcoin", "Trading", "Digital Assets", "Blockchain"]},
            "binance.com": {"category": "Fintech", "industry": "Cryptocurrency", "tags": ["Cryptocurrency Exchange", "Trading", "Blockchain", "DeFi", "Global"]},
            "kraken.com": {"category": "Fintech", "industry": "Cryptocurrency", "tags": ["Cryptocurrency Exchange", "Bitcoin", "Security", "Professional Trading", "Institutional"]},
            "epic.com": {"category": "Healthcare", "industry": "Healthcare Software", "tags": ["Electronic Health Records", "Healthcare IT", "Medical Software", "Hospital Systems", "Epic"]},
            "cargill.com": {"category": "Agriculture", "industry": "Agriculture & Food", "tags": ["Agriculture", "Food Production", "Commodities", "Animal Nutrition", "Supply Chain"]},
            "kochind.com": {"category": "Conglomerate", "industry": "Diversified Industries", "tags": ["Manufacturing", "Energy", "Chemicals", "Trading", "Technology"]},
            "mars.com": {"category": "Food & Beverage", "industry": "Food & Confectionery", "tags": ["Confectionery", "Pet Care", "Food", "Chocolate", "Global Brands"]},
            "ikea.com": {"category": "Retail", "industry": "Furniture Retail", "tags": ["Furniture", "Home Furnishing", "Design", "Affordable", "Sustainability"]},
            "aldi.com": {"category": "Retail", "industry": "Grocery Retail", "tags": ["Grocery", "Discount Retail", "Private Label", "Efficiency", "Value"]},
            "bmw.com": {"category": "Automotive", "industry": "Luxury Automotive", "tags": ["Luxury Cars", "BMW", "Motorcycles", "Electric Vehicles", "Performance"]},
            "mercedes-benz.com": {"category": "Automotive", "industry": "Luxury Automotive", "tags": ["Luxury Cars", "Mercedes-Benz", "Innovation", "Electric Vehicles", "Premium"]},
            "volkswagen.com": {"category": "Automotive", "industry": "Automotive", "tags": ["Automotive", "Volkswagen", "Electric Vehicles", "Manufacturing", "Global"]},
            "toyota.com": {"category": "Automotive", "industry": "Automotive", "tags": ["Automotive", "Hybrid Vehicles", "Manufacturing", "Reliability", "Global"]},
            "honda.com": {"category": "Automotive", "industry": "Automotive", "tags": ["Automotive", "Motorcycles", "Power Equipment", "Reliability", "Innovation"]},
            "nissan.com": {"category": "Automotive", "industry": "Automotive", "tags": ["Automotive", "Electric Vehicles", "Innovation", "Global", "Technology"]},
            "samsung.com": {"category": "Technology", "industry": "Consumer Electronics", "tags": ["Smartphones", "Electronics", "Semiconductors", "Displays", "Appliances"]},
            "sony.com": {"category": "Technology", "industry": "Consumer Electronics", "tags": ["Electronics", "PlayStation", "Entertainment", "Cameras", "Music"]},
            "nintendo.com": {"category": "Gaming", "industry": "Gaming", "tags": ["Gaming", "Nintendo Switch", "Video Games", "Entertainment", "Hardware"]},
            "huawei.com": {"category": "Technology", "industry": "Telecommunications Equipment", "tags": ["Smartphones", "5G", "Networking", "Cloud", "Enterprise"]},
            "xiaomi.com": {"category": "Technology", "industry": "Consumer Electronics", "tags": ["Smartphones", "IoT", "Consumer Electronics", "Ecosystem", "Innovation"]},
            "oppo.com": {"category": "Technology", "industry": "Smartphones", "tags": ["Smartphones", "Mobile Technology", "Camera Technology", "Design", "Innovation"]},
            "vivo.com": {"category": "Technology", "industry": "Smartphones", "tags": ["Smartphones", "Camera Technology", "Design", "Youth Market", "Innovation"]},
            "realme.com": {"category": "Technology", "industry": "Smartphones", "tags": ["Smartphones", "Youth Brand", "Performance", "Value", "Fast Charging"]},
            "oneplus.com": {"category": "Technology", "industry": "Smartphones", "tags": ["Smartphones", "Flagship Killer", "Performance", "OxygenOS", "Fast Charging"]},
        }
    
    def get_company_logo_url(self, domain: str) -> str:
        """Get company logo URL from Clearbit Logo API"""
        try:
            logo_url = f"{self.clearbit_logo_base}/{domain}"
            # Test if logo exists
            response = requests.head(logo_url, timeout=5)
            if response.status_code == 200:
                return logo_url
            else:
                # Fallback to default or generate initials
                return self._generate_fallback_logo(domain)
        except Exception as e:
            logger.warning(f"Failed to get logo for {domain}: {e}")
            return self._generate_fallback_logo(domain)
    
    def _generate_fallback_logo(self, domain: str) -> str:
        """Generate a fallback logo URL or placeholder"""
        # Use a service like UI Avatars for text-based logos
        company_name = domain.split('.')[0].upper()
        initials = company_name[:2] if len(company_name) >= 2 else company_name
        return f"https://ui-avatars.com/api/?name={initials}&size=128&background=401664&color=ffffff&bold=true"
    
    def get_stock_data(self, symbol: str) -> Dict:
        """Fetch stock data using yfinance"""
        try:
            if not symbol:
                return {}
                
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and market cap
            market_cap = info.get('marketCap', 0)
            current_price = info.get('currentPrice', 0)
            
            # Format market cap
            if market_cap > 1e12:
                market_cap_formatted = f"${market_cap/1e12:.1f}T"
            elif market_cap > 1e9:
                market_cap_formatted = f"${market_cap/1e9:.1f}B"
            elif market_cap > 1e6:
                market_cap_formatted = f"${market_cap/1e6:.1f}M"
            else:
                market_cap_formatted = f"${market_cap:,.0f}"
            
            return {
                'stock_symbol': symbol,
                'current_price': current_price,
                'market_cap': market_cap_formatted,
                'market_cap_raw': market_cap,
                'revenue': info.get('totalRevenue', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'website': info.get('website', ''),
                'business_summary': info.get('businessSummary', ''),
                'city': info.get('city', ''),
                'state': info.get('state', ''),
                'country': info.get('country', ''),
                'ceo': info.get('companyOfficers', [{}])[0].get('name', '') if info.get('companyOfficers') else ''
            }
        except Exception as e:
            logger.warning(f"Failed to get stock data for {symbol}: {e}")
            return {}
    
    def get_company_locations(self, domain: str) -> List[str]:
        """Get company locations based on known data"""
        # Mapping of companies to their known major office locations
        location_mapping = {
            # Tech Giants
            "apple.com": ["USA", "UK", "Germany", "Japan", "China", "Singapore", "Australia", "India", "Ireland", "France"],
            "microsoft.com": ["USA", "India", "UK", "Canada", "Germany", "France", "Australia", "China", "Ireland", "Netherlands"],
            "google.com": ["USA", "India", "UK", "Canada", "Germany", "Singapore", "Australia", "Japan", "Brazil", "France"],
            "amazon.com": ["USA", "India", "UK", "Germany", "Canada", "Japan", "Australia", "Brazil", "France", "Spain"],
            "tesla.com": ["USA", "Germany", "China", "UK", "Canada", "Australia", "Netherlands", "Norway"],
            "meta.com": ["USA", "UK", "India", "Singapore", "Canada", "Germany", "Australia", "Ireland", "Brazil"],
            "netflix.com": ["USA", "UK", "India", "Brazil", "Canada", "Germany", "Japan", "Australia", "France", "Netherlands"],
            "nvidia.com": ["USA", "UK", "Germany", "India", "Japan", "China", "Israel", "Finland"],
            "oracle.com": ["USA", "India", "UK", "Germany", "Australia", "Japan", "Canada", "France", "Brazil"],
            "salesforce.com": ["USA", "India", "UK", "Germany", "Australia", "Japan", "Canada", "France", "Ireland", "Singapore"],
            "adobe.com": ["USA", "India", "UK", "Germany", "Japan", "Australia", "Canada", "Singapore", "France", "Romania"],
            "uber.com": ["USA", "India", "UK", "Brazil", "Canada", "Mexico", "Germany", "France", "Netherlands"],
            "spotify.com": ["Sweden", "USA", "UK", "Germany", "India", "Brazil", "Canada", "Australia", "France", "Netherlands"],
            "airbnb.com": ["USA", "India", "UK", "Germany", "France", "Australia", "Canada", "Singapore", "Ireland", "China"],
            "squareup.com": ["USA", "Canada", "UK", "Australia", "Japan"],
            "shopify.com": ["Canada", "USA", "UK", "Germany", "Australia", "Singapore"],
            "zoom.us": ["USA", "UK", "Germany", "Australia", "Singapore", "India"],
            "paypal.com": ["USA", "UK", "Germany", "Australia", "Singapore", "India", "Ireland"],
            "intel.com": ["USA", "India", "UK", "Germany", "China", "Israel", "Ireland", "Malaysia"],
            "amd.com": ["USA", "Canada", "UK", "Germany", "China", "India", "Singapore"],
            "ibm.com": ["USA", "India", "UK", "Germany", "Canada", "Australia", "Brazil", "China"],
            "cisco.com": ["USA", "India", "UK", "Germany", "Canada", "Australia", "Singapore", "China"],
            "visa.com": ["USA", "UK", "Singapore", "Australia", "Brazil", "India"],
            "mastercard.com": ["USA", "UK", "Ireland", "Singapore", "Australia", "Brazil"],
            "disney.com": ["USA", "UK", "France", "Japan", "China", "India"],
            
            # Additional Tech Companies
            "alibaba.com": ["China", "USA", "UK", "Germany", "Singapore", "India", "Israel"],
            "tencentmusic.com": ["China", "USA", "UK", "Singapore"],
            "baidu.com": ["China", "USA", "Japan", "Brazil"],
            "jd.com": ["China", "USA", "Germany", "UK", "Thailand", "Indonesia"],
            "netease.com": ["China", "USA", "Canada", "Japan"],
            "sea.com": ["Singapore", "Indonesia", "Thailand", "Vietnam", "Malaysia", "Philippines", "Taiwan"],
            "grab.com": ["Singapore", "Indonesia", "Thailand", "Vietnam", "Malaysia", "Philippines", "Myanmar", "Cambodia"],
            "datadoghq.com": ["USA", "France", "UK", "Germany", "Japan", "Australia", "Singapore"],
            "snowflake.com": ["USA", "UK", "Germany", "Australia", "Japan", "Singapore"],
            "palantir.com": ["USA", "UK", "Germany", "Australia", "Japan"],
            "unity.com": ["USA", "UK", "Germany", "Denmark", "Finland", "Canada", "China", "Japan", "Singapore"],
            "roblox.com": ["USA", "UK", "Germany", "China"],
            "docusign.com": ["USA", "UK", "Germany", "Australia", "Brazil", "Canada", "France", "Japan"],
            "okta.com": ["USA", "UK", "Germany", "Australia", "Canada", "Sweden"],
            "twilio.com": ["USA", "UK", "Germany", "Australia", "Singapore", "Ireland", "Estonia"],
            "crowdstrike.com": ["USA", "UK", "Germany", "Australia", "Japan", "India"],
            "zscaler.com": ["USA", "UK", "Germany", "Australia", "Japan", "India", "Israel"],
            "atlassian.com": ["Australia", "USA", "UK", "Germany", "India", "Poland", "Netherlands"],
            "workday.com": ["USA", "UK", "Germany", "Australia", "Canada", "Ireland", "India"],
            "veeva.com": ["USA", "UK", "Germany", "Canada", "Australia", "Japan", "China"],
            "splunk.com": ["USA", "UK", "Germany", "Australia", "Japan", "Singapore"],
            "servicenow.com": ["USA", "UK", "Germany", "Australia", "Netherlands", "India"],
            "fortinet.com": ["USA", "Canada", "UK", "Germany", "France", "Australia", "Japan", "Singapore"],
            "paloaltonetworks.com": ["USA", "UK", "Germany", "Australia", "Japan", "Singapore", "India", "Israel"],
            
            # Financial Services
            "jpmorganchase.com": ["USA", "UK", "Germany", "Japan", "Singapore", "India", "Brazil", "Australia"],
            "bankofamerica.com": ["USA", "UK", "Germany", "Japan", "Singapore", "India", "Brazil"],
            "wellsfargo.com": ["USA", "UK", "India", "Philippines"],
            "goldmansachs.com": ["USA", "UK", "Germany", "Japan", "Singapore", "India", "Australia", "Brazil"],
            "morganstanley.com": ["USA", "UK", "Germany", "Japan", "Singapore", "India", "Australia"],
            "americanexpress.com": ["USA", "UK", "Germany", "Japan", "Singapore", "India", "Australia", "Mexico"],
            "blackrock.com": ["USA", "UK", "Germany", "Japan", "Singapore", "Australia", "Canada", "Brazil"],
            "spglobal.com": ["USA", "UK", "Germany", "Australia", "India", "Singapore", "Japan"],
            "cmegroup.com": ["USA", "UK", "Singapore", "Brazil"],
            "theice.com": ["USA", "UK", "Singapore", "Canada"],
            
            # Retail & E-commerce
            "walmart.com": ["USA", "Mexico", "Canada", "UK", "India", "China", "Brazil", "Argentina"],
            "homedepot.com": ["USA", "Canada", "Mexico"],
            "costco.com": ["USA", "Canada", "Mexico", "Japan", "South Korea", "Australia", "Spain", "France"],
            "target.com": ["USA", "India"],
            "ebay.com": ["USA", "UK", "Germany", "Australia", "Canada", "France", "Italy", "Spain"],
            "etsy.com": ["USA", "UK", "Germany", "Australia", "Canada", "France"],
            
            # Media & Telecommunications
            "comcast.com": ["USA"],
            "verizon.com": ["USA", "India"],
            "att.com": ["USA", "Mexico", "India"],
            "t-mobile.com": ["USA", "Germany", "Netherlands", "Poland", "Czech Republic"],
            "wbd.com": ["USA", "UK", "Germany", "Australia", "India"],
            "paramount.com": ["USA", "UK", "Germany", "Australia", "India"],
            "fox.com": ["USA", "Australia", "UK"],
            
            # Healthcare & Pharmaceuticals
            "jnj.com": ["USA", "Belgium", "Ireland", "Switzerland", "Brazil", "India", "China", "Japan"],
            "pfizer.com": ["USA", "UK", "Germany", "Ireland", "Belgium", "China", "India", "Japan"],
            "abbvie.com": ["USA", "Germany", "Ireland", "UK", "Puerto Rico", "Singapore"],
            "merck.com": ["USA", "Germany", "UK", "Ireland", "China", "India", "Japan"],
            "thermofisher.com": ["USA", "Germany", "UK", "China", "India", "Singapore"],
            "danaher.com": ["USA", "Germany", "UK", "Ireland", "China", "Singapore"],
            "bms.com": ["USA", "Ireland", "Puerto Rico", "France", "Germany", "India"],
            "amgen.com": ["USA", "Netherlands", "Turkey", "Puerto Rico", "Singapore"],
            "gilead.com": ["USA", "Ireland", "Australia", "Germany"],
            "vrtx.com": ["USA", "UK"],
            
            # Aerospace & Defense
            "boeing.com": ["USA", "UK", "Australia", "Canada", "India", "Brazil"],
            "lockheedmartin.com": ["USA", "UK", "Australia", "Canada"],
            "rtx.com": ["USA", "UK", "Germany", "Canada", "Australia", "India"],
            "northropgrumman.com": ["USA", "UK", "Australia"],
            "gd.com": ["USA", "UK", "Germany", "Canada"],
            
            # Automotive
            "gm.com": ["USA", "China", "Brazil", "Mexico", "Canada", "South Korea", "India"],
            "ford.com": ["USA", "Germany", "UK", "Mexico", "Brazil", "India", "China", "Australia"],
            "rivian.com": ["USA", "UK", "Canada"],
            "lucidmotors.com": ["USA", "Saudi Arabia"],
            "nio.com": ["China", "Norway", "Germany", "Denmark", "Netherlands"],
            "xiaopeng.com": ["China", "Norway", "Denmark", "Netherlands"],
            "lixiang.com": ["China"],
            
            # Private/Other Companies
            "stripe.com": ["USA", "UK", "Ireland", "Singapore", "Germany", "Australia", "Canada", "Brazil"],
            "slack.com": ["USA", "UK", "Canada", "Australia", "Germany", "India", "Japan", "Ireland"],
            "gitlab.com": ["USA", "Netherlands", "UK", "Germany", "Australia", "Canada"],
            "notion.so": ["USA", "UK", "Japan", "Korea"],
            "figma.com": ["USA", "UK", "Germany", "Japan"],
            "canva.com": ["Australia", "USA", "UK", "Philippines"],
            "dropbox.com": ["USA", "UK", "Germany", "Australia", "Israel"],
            "reddit.com": ["USA", "UK", "Canada", "Australia", "Germany"],
            "discord.com": ["USA", "UK", "Germany", "Japan"],
            "bytedance.com": ["China", "Singapore", "USA", "UK", "Germany"],
            "spacex.com": ["USA"],
            "openai.com": ["USA", "UK"],
            "anthropic.com": ["USA", "UK"],
            "databricks.com": ["USA", "UK", "Germany", "Australia", "Singapore", "India"],
            "instacart.com": ["USA", "Canada"],
            "doordash.com": ["USA", "Canada", "Australia", "Germany", "Japan"],
            "chime.com": ["USA"],
            "robinhood.com": ["USA", "UK"],
            "coinbase.com": ["USA", "UK", "Germany", "Singapore", "India"],
            "binance.com": ["Malta", "Singapore", "USA", "Japan", "UK"],
            "kraken.com": ["USA", "UK", "Canada", "Australia", "Germany"],
            "epic.com": ["USA", "Denmark", "Netherlands", "UK", "Australia"],
            "cargill.com": ["USA", "Brazil", "Argentina", "Germany", "UK", "India", "China", "Singapore"],
            "kochind.com": ["USA", "Canada", "Germany", "UK", "India"],
            "mars.com": ["USA", "UK", "Germany", "Belgium", "China", "India", "Australia", "Brazil"],
            "ikea.com": ["Sweden", "Netherlands", "Poland", "Germany", "USA", "China", "India", "Russia"],
            "aldi.com": ["Germany", "USA", "UK", "Australia", "Austria", "Poland"],
            "bmw.com": ["Germany", "USA", "UK", "China", "India", "Brazil", "South Africa"],
            "mercedes-benz.com": ["Germany", "USA", "UK", "China", "India", "Brazil", "South Africa"],
            "volkswagen.com": ["Germany", "USA", "China", "Brazil", "Mexico", "India", "Slovakia"],
            "toyota.com": ["Japan", "USA", "UK", "Germany", "China", "India", "Brazil", "Thailand"],
            "honda.com": ["Japan", "USA", "UK", "Germany", "China", "India", "Brazil", "Thailand"],
            "nissan.com": ["Japan", "USA", "UK", "Spain", "China", "India", "Brazil", "Mexico"],
            "samsung.com": ["South Korea", "USA", "UK", "Germany", "China", "India", "Vietnam", "Brazil"],
            "sony.com": ["Japan", "USA", "UK", "Germany", "China", "India", "Brazil"],
            "nintendo.com": ["Japan", "USA", "UK", "Germany", "France"],
            "huawei.com": ["China", "Germany", "UK", "France", "UAE", "Canada", "Russia"],
            "xiaomi.com": ["China", "India", "Germany", "Spain", "France", "UK", "Indonesia"],
            "oppo.com": ["China", "India", "Indonesia", "Thailand", "Vietnam", "Malaysia"],
            "vivo.com": ["China", "India", "Indonesia", "Thailand", "Malaysia", "Bangladesh"],
            "realme.com": ["China", "India", "Indonesia", "Thailand", "Malaysia", "Philippines"],
            "oneplus.com": ["China", "India", "USA", "UK", "Germany", "Finland"],
        }
        
        return location_mapping.get(domain, ["USA"])
    
    def fetch_all_companies(self) -> List[Dict]:
        """Fetch comprehensive data for all companies with caching"""
        
        # Try to get from cache first
        cached_data = company_cache.get(self.cache_key)
        if cached_data:
            logger.info(f"Returning cached company data: {len(cached_data)} companies")
            return cached_data
        
        logger.info("Cache miss - fetching fresh company data from APIs...")
        companies = []
        
        for idx, company_info in enumerate(self.major_companies, 1):
            try:
                domain = company_info["domain"]
                symbol = company_info["symbol"]
                name = company_info["name"]
                
                logger.info(f"Fetching data for {name} ({domain})")
                
                # Get stock data (with error handling)
                stock_data = {}
                if symbol:
                    try:
                        stock_data = self.get_stock_data(symbol)
                    except Exception as e:
                        logger.warning(f"Failed to get stock data for {symbol}: {e}")
                        stock_data = {}
                
                # Get industry info (with fallback)
                industry_info = self.industry_mapping.get(domain, {
                    "category": self._guess_category_from_name(name),
                    "industry": "Technology",
                    "tags": ["Business", "Technology"]
                })
                
                # Get locations
                locations = self.get_company_locations(domain)
                
                # Get logo URL (with error handling)
                logo_url = ""
                try:
                    logo_url = self.get_company_logo_url(domain)
                except Exception as e:
                    logger.warning(f"Failed to get logo for {domain}: {e}")
                    logo_url = self._generate_fallback_logo(domain)
                
                # Build company object with essential data only
                company = {
                    "id": idx,
                    "name": name,
                    "display_name": name,
                    "logo_url": logo_url,
                    "category": industry_info["category"],
                    "industry": industry_info.get("industry", stock_data.get("industry", "")),
                    "description": self._generate_description(name, industry_info, stock_data),
                    "long_description": stock_data.get("businessSummary") or self._generate_description(name, industry_info, stock_data),
                    "locations": locations,
                    "website": f"https://{domain}",
                    "domain": domain,
                    "tags": industry_info.get("tags", ["Business", "Technology"]),
                    
                    # Stock/Financial data (minimal, keeping only stock symbol and market cap)
                    "stock_symbol": symbol,
                    "market_cap": stock_data.get("market_cap", "Private" if not symbol else "N/A"),
                    "current_price": stock_data.get("current_price", 0),
                    
                    # Removing: revenue, employees, headquarters, founded, ceo
                    "sector": stock_data.get("sector", industry_info.get("category", "")),
                }
                
                companies.append(company)
                
            except Exception as e:
                logger.error(f"Error processing company {company_info}: {e}")
                # Still try to add basic company info even if APIs fail
                try:
                    basic_company = {
                        "id": idx,
                        "name": company_info["name"],
                        "display_name": company_info["name"],
                        "logo_url": self._generate_fallback_logo(company_info["domain"]),
                        "category": self._guess_category_from_name(company_info["name"]),
                        "industry": "Technology",
                        "description": f"Leading company in the technology and business sector.",
                        "long_description": f"{company_info['name']} is a major corporation operating globally.",
                        "locations": ["USA"],
                        "website": f"https://{company_info['domain']}",
                        "domain": company_info["domain"],
                        "tags": ["Business", "Technology"],
                        "stock_symbol": company_info["symbol"],
                        "market_cap": "Private" if not company_info["symbol"] else "N/A",
                        "current_price": 0,
                        "revenue": "N/A",
                        "employees": "N/A",
                        "headquarters": "N/A",
                        "founded": "N/A",
                        "ceo": "",
                        "sector": self._guess_category_from_name(company_info["name"]),
                    }
                    companies.append(basic_company)
                except Exception as inner_e:
                    logger.error(f"Failed to create basic company entry for {company_info}: {inner_e}")
                    continue
        
        logger.info(f"Successfully processed {len(companies)} companies")
        
        # Cache the results
        if companies:
            company_cache.set(self.cache_key, companies)
            logger.info(f"Cached {len(companies)} companies")
        
        return companies
    
    def was_last_fetch_from_cache(self) -> bool:
        """Check if the last fetch_all_companies call returned cached data"""
        return company_cache.was_last_get_hit()
    
    def clear_cache(self) -> None:
        """Clear the company data cache"""
        company_cache.clear()
        logger.info("Company data cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return company_cache.get_stats()
    
    def force_refresh(self) -> List[Dict]:
        """Force refresh company data (bypass cache)"""
        logger.info("Forcing refresh of company data...")
        self.clear_cache()
        return self.fetch_all_companies()
    
    def _generate_description(self, name: str, industry_info: Dict, stock_data: Dict) -> str:
        """Generate a company description"""
        if stock_data.get("businessSummary"):
            # Truncate business summary to about 150 characters
            summary = stock_data["businessSummary"]
            if len(summary) > 150:
                summary = summary[:147] + "..."
            return summary
        else:
            # Fallback description based on industry
            category = industry_info.get("category", "Technology")
            return f"Leading {category.lower()} company providing innovative solutions and services."
    
    def _format_revenue(self, revenue: int) -> str:
        """Format revenue in a readable format"""
        if revenue == 0:
            return "Private"
        elif revenue > 1e12:
            return f"${revenue/1e12:.1f}T"
        elif revenue > 1e9:
            return f"${revenue/1e9:.1f}B"
        elif revenue > 1e6:
            return f"${revenue/1e6:.1f}M"
        else:
            return f"${revenue:,.0f}"
    
    def _format_employees(self, employees: int) -> str:
        """Format employee count"""
        if employees == 0:
            return "N/A"
        elif employees > 1000000:
            return f"{employees/1000000:.1f}M+"
        elif employees > 1000:
            return f"{employees/1000:.0f}K+"
        else:
            return f"{employees:,}+"
    
    def _format_headquarters(self, stock_data: Dict) -> str:
        """Format headquarters location"""
        city = stock_data.get("city", "")
        state = stock_data.get("state", "")
        country = stock_data.get("country", "")
        
        if city and state:
            return f"{city}, {state}"
        elif city and country:
            return f"{city}, {country}"
        elif city:
            return city
        else:
            return "N/A"

    def _guess_category_from_name(self, name: str) -> str:
        """Guess company category from name"""
        name_lower = name.lower()
        if any(word in name_lower for word in ["bank", "financial", "capital", "investment", "goldman", "morgan"]):
            return "Financial Services"
        elif any(word in name_lower for word in ["pharma", "pharmaceutical", "health", "medical", "bio", "pfizer", "johnson"]):
            return "Healthcare"
        elif any(word in name_lower for word in ["auto", "motor", "tesla", "ford", "gm", "toyota", "bmw", "mercedes"]):
            return "Automotive"
        elif any(word in name_lower for word in ["retail", "walmart", "target", "costco", "home depot"]):
            return "Retail"
        elif any(word in name_lower for word in ["media", "entertainment", "disney", "netflix", "fox", "paramount"]):
            return "Entertainment"
        elif any(word in name_lower for word in ["telecom", "verizon", "att", "t-mobile", "comcast"]):
            return "Telecommunications"
        elif any(word in name_lower for word in ["aerospace", "defense", "boeing", "lockheed", "northrop"]):
            return "Aerospace & Defense"
        else:
            return "Technology"
    
    def _guess_headquarters(self, domain: str) -> str:
        """Guess headquarters from domain or company info"""
        if any(indicator in domain for indicator in ["baidu", "alibaba", "tencent", "xiaomi", "huawei"]):
            return "China"
        elif any(indicator in domain for indicator in ["toyota", "honda", "nissan", "sony", "nintendo"]):
            return "Japan"
        elif any(indicator in domain for indicator in ["samsung"]):
            return "South Korea"
        elif any(indicator in domain for indicator in ["spotify"]):
            return "Stockholm, Sweden"
        elif any(indicator in domain for indicator in ["sap"]):
            return "Germany"
        else:
            return "USA"

# Create a global instance
company_service = CompanyDataService() 