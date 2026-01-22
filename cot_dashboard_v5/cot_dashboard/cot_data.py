"""
COT Data Fetcher for Dashboard
Fetches real CFTC Commitment of Traders data
"""

import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os


# CFTC API Configuration
API_ENDPOINT = "publicreporting.cftc.gov"
API_KEY = "Z1eALyOoL0nekg4wimFpmGIm5"

# Dataset IDs for different report types
DATASET_IDS = {
    "legacy": "6dca-aqww",          # Legacy Futures Only
    "disaggregated": "72hh-3qpy",   # Disaggregated Futures Only
    "tff": "gpe5-46if",             # Traders in Financial Futures
}

# Legacy dataset ID for backwards compatibility
DATASET_ID = "6dca-aqww"  # Legacy Futures Only

# Field mappings for each report type
# Maps trader category to (long_field, short_field) in the API
REPORT_FIELD_MAPPINGS = {
    "legacy": {
        "trader1": ("noncomm_positions_long_all", "noncomm_positions_short_all"),      # Non-Commercial
        "trader2": ("comm_positions_long_all", "comm_positions_short_all"),            # Commercial
        "trader3": ("nonrept_positions_long_all", "nonrept_positions_short_all"),      # Non-Reportable
        "trader1_label": "non_commercial",
        "trader2_label": "commercial",
        "trader3_label": "non_reportable",
    },
    "disaggregated": {
        "trader1": ("prod_merc_positions_long", "prod_merc_positions_short"),          # Producer/Merchant (no _all suffix)
        "trader2": ("swap_positions_long_all", "swap__positions_short_all"),           # Swap Dealer (NOTE: double underscore on short!)
        "trader3": ("m_money_positions_long_all", "m_money_positions_short_all"),      # Managed Money
        "trader4": ("other_rept_positions_long", "other_rept_positions_short"),        # Other Reportable (no _all suffix)
        "trader1_label": "producer_merchant",
        "trader2_label": "swap_dealer",
        "trader3_label": "managed_money",
        "trader4_label": "other_reportable",
    },
    "tff": {
        "trader1": ("dealer_positions_long_all", "dealer_positions_short_all"),        # Dealer/Intermediary
        "trader2": ("asset_mgr_positions_long", "asset_mgr_positions_short"),          # Asset Manager (no _all suffix)
        "trader3": ("lev_money_positions_long", "lev_money_positions_short"),          # Leveraged Funds (no _all suffix)
        "trader4": ("other_rept_positions_long", "other_rept_positions_short"),        # Other Reportable (no _all suffix)
        "trader1_label": "dealer",
        "trader2_label": "asset_manager",
        "trader3_label": "leveraged_funds",
        "trader4_label": "other_reportable",
    },
}


# ============================================================================
# SYMBOL TO CFTC CONTRACT NAME MAPPINGS
# ============================================================================
#
# CRITICAL: The CFTC frequently renames contracts over time. If you only use
# the current contract name, you will ONLY get data from when that name started
# being used (often 2022), NOT the full historical data!
#
# SOLUTION: Each symbol must include ALL historical contract names to get
# complete data. The fetch_historical_data() function queries ALL names in the
# list and combines the results chronologically.
#
# HOW TO FIND CONTRACT NAMES:
# 1. Query the CFTC API for distinct market_and_exchange_names containing keywords
# 2. Check the date ranges for each contract name variant
# 3. Add ALL variants to the mapping list
#
# Example query to find Natural Gas contract names:
#   client.get("6dca-aqww", select="DISTINCT market_and_exchange_names",
#              where="market_and_exchange_names LIKE '%NATURAL GAS%'")
#
# KNOWN CFTC RENAME EVENT: February 2022
# Many contracts were renamed in Feb 2022. Examples:
#   - "NATURAL GAS" -> "NAT GAS NYME"
#   - "GASOLINE BLENDSTOCK (RBOB)" -> "GASOLINE RBOB"
#   - "JAPANESE YEN" -> "JPN YEN"
#   - "BRITISH POUND STERLING" -> "BRITISH POUND"
#   - etc.
#
# If data is truncated at 2022, CHECK THE CONTRACT NAME MAPPING FIRST!
# ============================================================================

# Symbol to CFTC Contract Name Mapping
# Using exact contract names from Legacy Futures Only report (dataset 6dca-aqww)
# Multiple names listed for contracts that changed names over time (will be combined chronologically)
SYMBOL_TO_CONTRACT = {
    # ========================================
    # ENERGY
    # IMPORTANT: All energy contracts were renamed in Feb 2022!
    # ========================================
    "CL": [
        "CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE",    # Historical (pre-2022)
        "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE",              # Current (2022+)
    ],
    "NG": [
        "NATURAL GAS - NEW YORK MERCANTILE EXCHANGE",               # Historical (1990-2022)
        "NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE",              # Current (2022+)
    ],
    "RB": [
        "GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE",  # Historical (2006-2022)
        "GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE",               # Current (2022+)
    ],
    "HO": [
        "NO. 2 HEATING OIL, N.Y. HARBOR - NEW YORK MERCANTILE EXCHANGE",  # Historical (1986-2013)
        "#2 HEATING OIL- NY HARBOR-ULSD - NEW YORK MERCANTILE EXCHANGE",  # Transition (2017-2022)
        "NY HARBOR ULSD - NEW YORK MERCANTILE EXCHANGE",                   # Current (2022+)
    ],
    "BZ": [
        "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE",  # Historical (2011-2022)
        "BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE",            # Current (2022+)
    ],

    # ========================================
    # METALS
    # ========================================
    "GC": ["GOLD - COMMODITY EXCHANGE INC."],
    "SI": ["SILVER - COMMODITY EXCHANGE INC."],
    "HG": ["COPPER-GRADE #1 - COMMODITY EXCHANGE INC."],
    "PL": ["PLATINUM - NEW YORK MERCANTILE EXCHANGE"],
    "PA": ["PALLADIUM - NEW YORK MERCANTILE EXCHANGE"],

    # ========================================
    # AGRICULTURE - Grains
    # ========================================
    "ZC": ["CORN - CHICAGO BOARD OF TRADE"],
    "ZS": ["SOYBEANS - CHICAGO BOARD OF TRADE"],
    "ZW": ["WHEAT-SRW - CHICAGO BOARD OF TRADE"],
    "ZM": ["SOYBEAN MEAL - CHICAGO BOARD OF TRADE"],
    "ZL": ["SOYBEAN OIL - CHICAGO BOARD OF TRADE"],
    "ZO": ["OATS - CHICAGO BOARD OF TRADE"],
    "KE": ["WHEAT-HRW - CHICAGO BOARD OF TRADE"],
    "ZR": ["ROUGH RICE - CHICAGO BOARD OF TRADE"],

    # ========================================
    # AGRICULTURE - Softs
    # ========================================
    "CT": ["COTTON NO. 2 - ICE FUTURES U.S."],
    "KC": ["COFFEE C - ICE FUTURES U.S."],
    "SB": ["SUGAR NO. 11 - ICE FUTURES U.S."],
    "CC": ["COCOA - ICE FUTURES U.S."],
    "OJ": ["FRZN CONCENTRATED ORANGE JUICE - ICE FUTURES U.S."],

    # ========================================
    # AGRICULTURE - Livestock
    # ========================================
    "LE": ["LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE"],
    "HE": ["LEAN HOGS - CHICAGO MERCANTILE EXCHANGE"],
    "GF": ["FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE"],

    # ========================================
    # EQUITIES - Index Futures
    # ========================================
    "ES": ["E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE"],
    "NQ": ["NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE"],
    "YM": ["DOW JONES INDUSTRIAL AVG- x $5 - CHICAGO BOARD OF TRADE"],
    "RTY": ["RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE"],
    "VX": ["VIX FUTURES - CBOE FUTURES EXCHANGE"],
    "SP": ["S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE"],  # Full-size S&P
    "NKD": ["NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE"],

    # ========================================
    # CURRENCIES
    # Note: CFTC renamed several contracts around Feb 2022
    # Both old and new names are included to get full historical + current data
    # ========================================
    "6E": ["EURO FX - CHICAGO MERCANTILE EXCHANGE"],
    "6J": [
        "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",      # Historical (pre-2022)
        "JPN YEN - CHICAGO MERCANTILE EXCHANGE",           # Current (2022+)
    ],
    "6B": [
        "BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE",  # Historical (pre-2022)
        "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",           # Current (2022+)
    ],
    "6A": [
        "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",  # Historical (pre-2022)
        "AUD DOLLAR - CHICAGO MERCANTILE EXCHANGE",         # Current (2022+)
    ],
    "6C": [
        "CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",    # Historical (pre-2022)
        "CAD DOLLAR - CHICAGO MERCANTILE EXCHANGE",         # Current (2022+)
    ],
    "6S": [
        "SWISS FRANC - CHICAGO MERCANTILE EXCHANGE",        # Historical (pre-2022)
        "CHF FRANC - CHICAGO MERCANTILE EXCHANGE",          # Current (2022+)
    ],
    "6N": [
        "NEW ZEALAND DOLLAR - CHICAGO MERCANTILE EXCHANGE",  # Historical (pre-2022)
        "NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE",           # Current (2022+)
    ],
    "6M": [
        "MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE",        # Historical (pre-2022)
        "MXN PESO - CHICAGO MERCANTILE EXCHANGE",            # Current (2022+)
    ],
    "DX": [
        "U.S. DOLLAR INDEX - ICE FUTURES U.S.",              # Historical (pre-2022)
        "USD INDEX - ICE FUTURES U.S.",                      # Current (2022+)
    ],
    "BTC": ["BITCOIN - CHICAGO MERCANTILE EXCHANGE"],

    # ========================================
    # TREASURIES / INTEREST RATES
    # ========================================
    "ZB": ["U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE"],
    "ZN": ["10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"],
    "ZF": ["5-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"],
    "ZT": ["2-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"],
    "UB": ["ULTRA U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE"],
    "TN": ["ULTRA 10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"],
    "ED": ["EURODOLLAR - CHICAGO MERCANTILE EXCHANGE"],
    "SR3": ["3-MONTH SOFR - CHICAGO MERCANTILE EXCHANGE"],
}

# ============================================================================
# TFF (Traders in Financial Futures) CONTRACT NAME MAPPING
# ============================================================================
# IMPORTANT: TFF uses DIFFERENT contract names than Legacy! Don't copy from Legacy.
# TFF covers: equities, currencies, treasuries (NO commodities/energy/agriculture)
#
# Same rules apply: include ALL historical names to get full data history.
# See the main comment block above SYMBOL_TO_CONTRACT for troubleshooting tips.
# ============================================================================
SYMBOL_TO_CONTRACT_TFF = {
    # ========================================
    # EQUITY INDICES
    # ========================================
    "ES": [
        "E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE",  # Current
        "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",               # Historical
    ],
    "NQ": [
        "NASDAQ-100 STOCK INDEX (MINI) - CHICAGO MERCANTILE EXCHANGE",  # Current
        "NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE",                     # Historical
    ],
    "YM": [
        "DJIA x $5 - CHICAGO BOARD OF TRADE",                           # Current
        "DOW JONES INDUSTRIAL AVG- x $5 - CHICAGO BOARD OF TRADE",      # Historical
    ],
    "RTY": [
        "RUSSELL 2000 MINI - CHICAGO MERCANTILE EXCHANGE",              # Current
        "RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE",                 # Historical
    ],
    "VX": ["VIX FUTURES - CBOE FUTURES EXCHANGE"],
    "NKD": ["NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE"],
    "SP": ["S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE"],        # Full-size S&P

    # ========================================
    # CURRENCIES
    # Note: CFTC renamed several contracts around Feb 2022
    # Both old and new names are included to get full historical + current data
    # ========================================
    "6E": ["EURO FX - CHICAGO MERCANTILE EXCHANGE"],
    "6J": [
        "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",      # Historical (pre-2022)
        "JPN YEN - CHICAGO MERCANTILE EXCHANGE",           # Current (2022+)
    ],
    "6B": [
        "BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE",  # Historical (pre-2022)
        "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",           # Current (2022+)
    ],
    "6A": [
        "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",  # Historical (pre-2022)
        "AUD DOLLAR - CHICAGO MERCANTILE EXCHANGE",         # Current (2022+)
    ],
    "6C": [
        "CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",    # Historical (pre-2022)
        "CAD DOLLAR - CHICAGO MERCANTILE EXCHANGE",         # Current (2022+)
    ],
    "6S": [
        "SWISS FRANC - CHICAGO MERCANTILE EXCHANGE",        # Historical (pre-2022)
        "CHF FRANC - CHICAGO MERCANTILE EXCHANGE",          # Current (2022+)
    ],
    "6N": [
        "NEW ZEALAND DOLLAR - CHICAGO MERCANTILE EXCHANGE",  # Historical (pre-2022)
        "NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE",           # Current (2022+)
    ],
    "6M": [
        "MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE",        # Historical (pre-2022)
        "MXN PESO - CHICAGO MERCANTILE EXCHANGE",            # Current (2022+)
    ],
    "DX": [
        "U.S. DOLLAR INDEX - ICE FUTURES U.S.",              # Historical (pre-2022)
        "USD INDEX - ICE FUTURES U.S.",                      # Current (2022+)
    ],
    "BTC": ["BITCOIN - CHICAGO MERCANTILE EXCHANGE"],

    # ========================================
    # TREASURIES / INTEREST RATES
    # ========================================
    "ZB": [
        "UST BOND - CHICAGO BOARD OF TRADE",                          # Current TFF name
        "U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE",               # Historical
    ],
    "ZN": [
        "10 YR UST NOTE - CHICAGO BOARD OF TRADE",                    # Current TFF name
        "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE",       # Historical
    ],
    "ZF": [
        "5 YR UST NOTE - CHICAGO BOARD OF TRADE",                     # Current TFF name
        "5-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE",        # Historical
    ],
    "ZT": [
        "2 YR UST NOTE - CHICAGO BOARD OF TRADE",                     # Current TFF name
        "2-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE",        # Historical
    ],
    "UB": [
        "ULTRA UST BOND - CHICAGO BOARD OF TRADE",                    # Current TFF name
        "ULTRA U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE",         # Historical
    ],
    "TN": [
        "ULTRA 10 YR UST NOTE - CHICAGO BOARD OF TRADE",              # Current TFF name
        "ULTRA 10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE", # Historical
    ],
    "ED": ["EURODOLLAR - CHICAGO MERCANTILE EXCHANGE"],
    "SR3": [
        "3M SOFR - CHICAGO MERCANTILE EXCHANGE",                      # Current TFF name
        "3-MONTH SOFR - CHICAGO MERCANTILE EXCHANGE",                 # Historical
    ],
}

# ============================================================================
# DISAGGREGATED REPORT CONTRACT NAME MAPPING
# ============================================================================
# IMPORTANT: Disaggregated uses DIFFERENT contract names than Legacy!
# Disaggregated covers: energy, metals, agriculture (NO financials)
#
# Same rules apply: include ALL historical names to get full data history.
# See the main comment block above SYMBOL_TO_CONTRACT for troubleshooting tips.
#
# If data is truncated at 2022, the contract was likely renamed. Query the API
# to find all historical names and add them to the list.
# ============================================================================
SYMBOL_TO_CONTRACT_DISAGG = {
    # ========================================
    # ENERGY
    # IMPORTANT: All energy contracts were renamed in Feb 2022!
    # ========================================
    "CL": [
        "CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE",    # Historical (pre-2022)
        "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE",              # Current (2022+)
    ],
    "NG": [
        "NATURAL GAS - NEW YORK MERCANTILE EXCHANGE",               # Historical (1990-2022)
        "NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE",              # Current (2022+)
    ],
    "RB": [
        "GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE",  # Historical (2006-2022)
        "GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE",               # Current (2022+)
    ],
    "HO": [
        "NO. 2 HEATING OIL, N.Y. HARBOR - NEW YORK MERCANTILE EXCHANGE",  # Historical (1986-2013)
        "#2 HEATING OIL- NY HARBOR-ULSD - NEW YORK MERCANTILE EXCHANGE",  # Transition (2017-2022)
        "NY HARBOR ULSD - NEW YORK MERCANTILE EXCHANGE",                   # Current (2022+)
    ],
    "BZ": [
        "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE",  # Historical (2011-2022)
        "BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE",            # Current (2022+)
    ],

    # ========================================
    # METALS
    # ========================================
    "GC": ["GOLD - COMMODITY EXCHANGE INC."],
    "SI": ["SILVER - COMMODITY EXCHANGE INC."],
    "HG": [
        "COPPER-GRADE #1 - COMMODITY EXCHANGE INC.",    # Historical (Legacy name)
        "COPPER- #1 - COMMODITY EXCHANGE INC.",          # Current Disagg name
    ],
    "PL": ["PLATINUM - NEW YORK MERCANTILE EXCHANGE"],
    "PA": ["PALLADIUM - NEW YORK MERCANTILE EXCHANGE"],

    # ========================================
    # AGRICULTURE - Grains
    # ========================================
    "ZC": ["CORN - CHICAGO BOARD OF TRADE"],
    "ZS": ["SOYBEANS - CHICAGO BOARD OF TRADE"],
    "ZW": [
        "WHEAT-SRW - CHICAGO BOARD OF TRADE",           # Current
        "WHEAT - CHICAGO BOARD OF TRADE",               # Historical
    ],
    "ZM": ["SOYBEAN MEAL - CHICAGO BOARD OF TRADE"],
    "ZL": ["SOYBEAN OIL - CHICAGO BOARD OF TRADE"],
    "ZO": ["OATS - CHICAGO BOARD OF TRADE"],
    "KE": [
        "WHEAT-HRW - CHICAGO BOARD OF TRADE",           # Current
        "WHEAT-HRW - KANSAS CITY BOARD OF TRADE",       # Historical
    ],
    "ZR": ["ROUGH RICE - CHICAGO BOARD OF TRADE"],

    # ========================================
    # AGRICULTURE - Softs
    # ========================================
    "CT": ["COTTON NO. 2 - ICE FUTURES U.S."],
    "KC": ["COFFEE C - ICE FUTURES U.S."],
    "SB": ["SUGAR NO. 11 - ICE FUTURES U.S."],
    "CC": ["COCOA - ICE FUTURES U.S."],
    "OJ": ["FRZN CONCENTRATED ORANGE JUICE - ICE FUTURES U.S."],

    # ========================================
    # AGRICULTURE - Livestock
    # ========================================
    "LE": ["LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE"],
    "HE": ["LEAN HOGS - CHICAGO MERCANTILE EXCHANGE"],
    "GF": ["FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE"],
}


class COTDataFetcher:
    """Fetches and caches COT data from CFTC API."""

    def __init__(self, cache_dir: str = ".cot_cache"):
        """Initialize the data fetcher with caching."""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.client = Socrata(API_ENDPOINT, API_KEY)

    def _get_cache_path(self, symbol: str) -> str:
        """Get cache file path for a symbol."""
        return os.path.join(self.cache_dir, f"{symbol}.json")

    def _is_cache_valid(self, symbol: str, max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid."""
        cache_path = self._get_cache_path(symbol)
        if not os.path.exists(cache_path):
            return False

        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_time
        return age < timedelta(hours=max_age_hours)

    def _load_from_cache(self, symbol: str) -> Optional[Dict]:
        """Load data from cache."""
        cache_path = self._get_cache_path(symbol)
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def _save_to_cache(self, symbol: str, data: Dict):
        """Save data to cache."""
        cache_path = self._get_cache_path(symbol)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Cache save error: {e}")

    def fetch_latest_report(self, symbol: str) -> Dict:
        """Fetch the most recent COT report for a symbol."""
        # Check cache first
        if self._is_cache_valid(symbol):
            cached = self._load_from_cache(symbol)
            if cached:
                return cached

        # Fetch from API
        contract_names = SYMBOL_TO_CONTRACT.get(symbol, [])
        if not contract_names:
            return self._get_empty_report()

        try:
            # Fetch latest from all contract variations
            all_results = []
            for contract_name in contract_names:
                results = self.client.get(
                    DATASET_ID,
                    limit=1,
                    where=f"market_and_exchange_names = '{contract_name}'",
                    order="report_date_as_yyyy_mm_dd DESC"
                )
                if results:
                    all_results.extend(results)

            if not all_results:
                return self._get_empty_report()

            # Find the single most recent report across all contract names
            # This ensures we use only the current active contract, not aggregate old ones
            most_recent = max(all_results, key=lambda x: x.get("report_date_as_yyyy_mm_dd", ""))

            # Use only the most recent report (no aggregation for latest data)
            report = self._process_latest_report(most_recent)

            # Cache the result
            self._save_to_cache(symbol, report)

            return report

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return self._get_empty_report()

    def fetch_historical_data(self, symbol: str, years: int = 0, report_type: str = "legacy") -> List[Dict]:
        """Fetch historical COT data for charts. years=0 means all available data.

        Args:
            symbol: The market symbol (e.g., 'CL' for Crude Oil)
            years: Number of years of history (0 = all available)
            report_type: One of 'legacy', 'disaggregated', or 'tff'
        """
        print(f"[fetch_historical_data] Fetching for symbol: {symbol}, report_type: {report_type}")

        # Use the appropriate contract name mapping for each report type
        if report_type == "tff":
            contract_names = SYMBOL_TO_CONTRACT_TFF.get(symbol, [])
        elif report_type == "disaggregated":
            contract_names = SYMBOL_TO_CONTRACT_DISAGG.get(symbol, [])
        else:
            contract_names = SYMBOL_TO_CONTRACT.get(symbol, [])

        print(f"[fetch_historical_data] Contract names for {report_type}: {contract_names}")
        if not contract_names:
            print("[fetch_historical_data] No contract names found, returning []")
            return []

        # Get the correct dataset ID for this report type
        dataset_id = DATASET_IDS.get(report_type, DATASET_IDS["legacy"])
        field_mapping = REPORT_FIELD_MAPPINGS.get(report_type, REPORT_FIELD_MAPPINGS["legacy"])
        print(f"[fetch_historical_data] Using dataset: {dataset_id}")

        try:
            # Fetch ALL data from 1986 onwards (when COT data began)
            # Use pagination to get all records
            all_dfs = []
            for contract_name in contract_names:
                offset = 0
                batch_size = 50000

                while True:
                    results = self.client.get(
                        dataset_id,
                        limit=batch_size,
                        offset=offset,
                        where=f"market_and_exchange_names = '{contract_name}'",
                        order="report_date_as_yyyy_mm_dd ASC"
                    )

                    if not results:
                        print(f"[fetch_historical_data] No results for {contract_name}")
                        break

                    print(f"[fetch_historical_data] Got {len(results)} results for {contract_name}")
                    df = pd.DataFrame.from_records(results)
                    all_dfs.append(df)

                    # If we got fewer results than batch_size, we've reached the end
                    if len(results) < batch_size:
                        break

                    offset += batch_size

            if not all_dfs:
                print("[fetch_historical_data] No data frames collected, returning []")
                return []

            print(f"[fetch_historical_data] Combining {len(all_dfs)} dataframes")
            # Combine all dataframes and defragment immediately with .copy()
            df = pd.concat(all_dfs, ignore_index=True).copy()
            print(f"[fetch_historical_data] Combined dataframe has {len(df)} rows")

            # Calculate net positions based on report type
            # Get the field names from mapping
            t1_long, t1_short = field_mapping["trader1"]
            t2_long, t2_short = field_mapping["trader2"]
            t3_long, t3_short = field_mapping["trader3"]

            # Helper to safely get column data (returns 0 if column doesn't exist)
            def safe_col(col_name):
                if col_name in df.columns:
                    return pd.to_numeric(df[col_name], errors='coerce').fillna(0)
                return pd.Series(0, index=df.index)

            # Build all new columns at once to avoid DataFrame fragmentation
            new_cols = {
                'date': pd.to_datetime(df['report_date_as_yyyy_mm_dd']),
                'trader1_net': safe_col(t1_long) - safe_col(t1_short),
                'trader2_net': safe_col(t2_long) - safe_col(t2_short),
                'trader3_net': safe_col(t3_long) - safe_col(t3_short),
            }

            # For disaggregated and TFF, there's a 4th trader category
            if "trader4" in field_mapping:
                t4_long, t4_short = field_mapping["trader4"]
                new_cols['trader4_net'] = safe_col(t4_long) - safe_col(t4_short)
            else:
                new_cols['trader4_net'] = pd.Series(0, index=df.index)

            # Assign all new columns at once using pd.concat to avoid fragmentation
            df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

            # Remove duplicates and sort by date
            df = df.drop_duplicates(subset=['date'], keep='last')
            df = df.sort_values('date')

            # Get the label names
            label1 = field_mapping["trader1_label"]
            label2 = field_mapping["trader2_label"]
            label3 = field_mapping["trader3_label"]
            label4 = field_mapping.get("trader4_label", "other")

            # Process into chart format with dynamic keys based on report type
            chart_data = []
            for idx, row in df.iterrows():
                data_point = {
                    "date": row['date'].strftime("%Y-%m-%d"),
                    "week": len(chart_data),
                    label1: int(row['trader1_net']),
                    label2: int(row['trader2_net']),
                    label3: int(row['trader3_net']),
                }
                # Add 4th trader for disaggregated/TFF
                if "trader4" in field_mapping:
                    data_point[label4] = int(row['trader4_net'])
                chart_data.append(data_point)

            print(f"[fetch_historical_data] Returning {len(chart_data)} chart data points for {report_type}")
            return chart_data

        except Exception as e:
            print(f"Error fetching historical data for {symbol} ({report_type}): {e}")
            import traceback
            traceback.print_exc()
            return []

    def _aggregate_reports(self, reports: List[Dict]) -> Dict:
        """Aggregate multiple contract reports from the same date."""
        if len(reports) == 1:
            return reports[0]

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Initialize aggregated values
        aggregated = {
            "report_date_as_yyyy_mm_dd": reports[0].get("report_date_as_yyyy_mm_dd", ""),
            "noncomm_positions_long_all": 0,
            "noncomm_positions_short_all": 0,
            "comm_positions_long_all": 0,
            "comm_positions_short_all": 0,
            "nonrept_positions_long_all": 0,
            "nonrept_positions_short_all": 0,
            "open_interest_all": 0,
            "change_in_noncomm_long_all": 0,
            "change_in_noncomm_short_all": 0,
            "change_in_comm_long_all": 0,
            "change_in_comm_short_all": 0,
            "change_in_nonrept_long_all": 0,
            "change_in_nonrept_short_all": 0,
            "change_in_open_interest_all": 0,
        }

        # Sum all numeric fields
        for report in reports:
            aggregated["noncomm_positions_long_all"] += safe_float(report.get("noncomm_positions_long_all", 0))
            aggregated["noncomm_positions_short_all"] += safe_float(report.get("noncomm_positions_short_all", 0))
            aggregated["comm_positions_long_all"] += safe_float(report.get("comm_positions_long_all", 0))
            aggregated["comm_positions_short_all"] += safe_float(report.get("comm_positions_short_all", 0))
            aggregated["nonrept_positions_long_all"] += safe_float(report.get("nonrept_positions_long_all", 0))
            aggregated["nonrept_positions_short_all"] += safe_float(report.get("nonrept_positions_short_all", 0))
            aggregated["open_interest_all"] += safe_float(report.get("open_interest_all", 0))
            aggregated["change_in_noncomm_long_all"] += safe_float(report.get("change_in_noncomm_long_all", 0))
            aggregated["change_in_noncomm_short_all"] += safe_float(report.get("change_in_noncomm_short_all", 0))
            aggregated["change_in_comm_long_all"] += safe_float(report.get("change_in_comm_long_all", 0))
            aggregated["change_in_comm_short_all"] += safe_float(report.get("change_in_comm_short_all", 0))
            aggregated["change_in_nonrept_long_all"] += safe_float(report.get("change_in_nonrept_long_all", 0))
            aggregated["change_in_nonrept_short_all"] += safe_float(report.get("change_in_nonrept_short_all", 0))
            aggregated["change_in_open_interest_all"] += safe_float(report.get("change_in_open_interest_all", 0))

        return aggregated

    def _process_latest_report(self, data: Dict) -> Dict:
        """Process raw API data into dashboard format."""
        def safe_int(value, default=0):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

        # Extract positions
        nc_long = safe_int(data.get("noncomm_positions_long_all"))
        nc_short = safe_int(data.get("noncomm_positions_short_all"))
        comm_long = safe_int(data.get("comm_positions_long_all"))
        comm_short = safe_int(data.get("comm_positions_short_all"))
        nr_long = safe_int(data.get("nonrept_positions_long_all"))
        nr_short = safe_int(data.get("nonrept_positions_short_all"))
        oi = safe_int(data.get("open_interest_all"))

        # Calculate net positions
        nc_net = nc_long - nc_short
        comm_net = comm_long - comm_short
        nr_net = nr_long - nr_short

        # Calculate changes (if available)
        nc_change = safe_int(data.get("change_in_noncomm_long_all", 0)) - \
                   safe_int(data.get("change_in_noncomm_short_all", 0))
        comm_change = safe_int(data.get("change_in_comm_long_all", 0)) - \
                     safe_int(data.get("change_in_comm_short_all", 0))
        nr_change = safe_int(data.get("change_in_nonrept_long_all", 0)) - \
                   safe_int(data.get("change_in_nonrept_short_all", 0))

        # Calculate % of OI
        total_positions = (nc_long + nc_short + comm_long + comm_short + nr_long + nr_short)
        nc_pct = round((nc_long + nc_short) / total_positions * 100, 1) if total_positions > 0 else 0
        comm_pct = round((comm_long + comm_short) / total_positions * 100, 1) if total_positions > 0 else 0
        nr_pct = round((nr_long + nr_short) / total_positions * 100, 1) if total_positions > 0 else 0

        # Format report date
        report_date = data.get("report_date_as_yyyy_mm_dd", "")
        try:
            date_obj = datetime.strptime(report_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = report_date

        return {
            "report_date": formatted_date,
            "open_interest": oi,
            "oi_change": safe_int(data.get("change_in_open_interest_all", 0)),

            "non_commercial_long": nc_long,
            "non_commercial_short": nc_short,
            "non_commercial_net": nc_net,
            "non_commercial_change": nc_change,
            "non_commercial_pct": nc_pct,

            "commercial_long": comm_long,
            "commercial_short": comm_short,
            "commercial_net": comm_net,
            "commercial_change": comm_change,
            "commercial_pct": comm_pct,

            "non_reportable_long": nr_long,
            "non_reportable_short": nr_short,
            "non_reportable_net": nr_net,
            "non_reportable_change": nr_change,
            "non_reportable_pct": nr_pct,
        }

    def _get_empty_report(self) -> Dict:
        """Return empty report structure."""
        return {
            "report_date": "No Data Available",
            "open_interest": 0,
            "oi_change": 0,

            "non_commercial_long": 0,
            "non_commercial_short": 0,
            "non_commercial_net": 0,
            "non_commercial_change": 0,
            "non_commercial_pct": 0.0,

            "commercial_long": 0,
            "commercial_short": 0,
            "commercial_net": 0,
            "commercial_change": 0,
            "commercial_pct": 0.0,

            "non_reportable_long": 0,
            "non_reportable_short": 0,
            "non_reportable_net": 0,
            "non_reportable_change": 0,
            "non_reportable_pct": 0.0,
        }


# Global instance
_fetcher = None

def get_fetcher() -> COTDataFetcher:
    """Get or create global fetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = COTDataFetcher()
    return _fetcher


# ============================================================================
# PREMIUM QUANT CALCULATIONS
# ============================================================================

def calculate_rolling_zscore(
    current_position: float,
    historical_positions: List[float],
    window: int = 52  # 52 weeks = 1 year default
) -> Dict:
    """
    Calculate Rolling Z-Score (number of standard deviations from mean).

    Z-Score = (X - μ) / σ
    where:
        X = current position
        μ = mean of historical positions
        σ = standard deviation of historical positions

    Interpretation:
        > +2: Extremely bullish (top 2.5%)
        +1 to +2: Bullish
        -1 to +1: Neutral
        -2 to -1: Bearish
        < -2: Extremely bearish (bottom 2.5%)

    Args:
        current_position: The current net position value
        historical_positions: List of historical net positions
        window: Lookback period in weeks (default 52 = 1 year)

    Returns:
        dict with z_score, interpretation, and context
    """
    import numpy as np

    if not historical_positions or len(historical_positions) < 2:
        return {
            "z_score": 0.0,
            "interpretation": "Insufficient data",
            "percentile": 50.0,
            "is_extreme": False,
            "mean": 0.0,
            "std": 0.0,
        }

    # Get recent window of data
    recent_data = historical_positions[-window:] if len(historical_positions) >= window else historical_positions

    # Calculate mean and std
    mean = float(np.mean(recent_data))
    std = float(np.std(recent_data))

    # Avoid division by zero
    if std == 0:
        return {
            "z_score": 0.0,
            "interpretation": "No variance in data",
            "percentile": 50.0,
            "is_extreme": False,
            "mean": mean,
            "std": 0.0,
        }

    # Calculate z-score
    z_score = (current_position - mean) / std
    z_score = round(z_score, 2)

    # Determine interpretation
    if z_score > 2:
        interpretation = "Extremely Bullish"
    elif z_score > 1:
        interpretation = "Bullish"
    elif z_score > -1:
        interpretation = "Neutral"
    elif z_score > -2:
        interpretation = "Bearish"
    else:
        interpretation = "Extremely Bearish"

    # Convert to percentile (approximate using normal distribution)
    from scipy import stats
    percentile = round(stats.norm.cdf(z_score) * 100, 1)

    return {
        "z_score": z_score,
        "interpretation": interpretation,
        "percentile": percentile,
        "is_extreme": abs(z_score) >= 2,
        "mean": round(mean, 0),
        "std": round(std, 0),
    }


def calculate_positioning_velocity(
    positions: List[float],
    smoothing_window: int = 4
) -> Dict:
    """
    Calculate positioning velocity (1st derivative) and acceleration (2nd derivative).

    Velocity = rate of change in positions
    Acceleration = rate of change in velocity

    Interpretation:
        Positive velocity + Positive acceleration = Strong trend continuation
        Positive velocity + Negative acceleration = Trend losing momentum
        Negative velocity + Positive acceleration = Bearish trend slowing (potential reversal)
        Negative velocity + Negative acceleration = Strong bearish acceleration

    Args:
        positions: List of position values over time
        smoothing_window: Window for smoothing (default 4 weeks)

    Returns:
        dict with velocity, acceleration, trend interpretation
    """
    import numpy as np

    if not positions or len(positions) < 3:
        return {
            "velocity": 0.0,
            "acceleration": 0.0,
            "trend": "Insufficient data",
            "momentum_signal": "Neutral",
            "velocity_series": [],
            "acceleration_series": [],
        }

    # Convert to numpy array
    pos_array = np.array(positions, dtype=float)

    # Smooth the data if enough points
    if len(pos_array) >= smoothing_window:
        from scipy.ndimage import uniform_filter1d
        smoothed = uniform_filter1d(pos_array, size=smoothing_window)
    else:
        smoothed = pos_array

    # Calculate 1st derivative (velocity) - rate of change
    velocity = np.diff(smoothed)

    # Calculate 2nd derivative (acceleration) - rate of change of velocity
    acceleration = np.diff(velocity) if len(velocity) > 1 else np.array([0.0])

    # Get most recent values
    current_velocity = float(velocity[-1]) if len(velocity) > 0 else 0.0
    current_acceleration = float(acceleration[-1]) if len(acceleration) > 0 else 0.0

    # Determine trend interpretation
    if current_velocity > 0:
        if current_acceleration > 0:
            trend = "Accelerating Buildup"
            momentum_signal = "Strong Bullish"
        elif current_acceleration < 0:
            trend = "Decelerating Buildup"
            momentum_signal = "Weakening Bullish"
        else:
            trend = "Steady Buildup"
            momentum_signal = "Bullish"
    elif current_velocity < 0:
        if current_acceleration < 0:
            trend = "Accelerating Selloff"
            momentum_signal = "Strong Bearish"
        elif current_acceleration > 0:
            trend = "Decelerating Selloff"
            momentum_signal = "Potential Reversal"
        else:
            trend = "Steady Selloff"
            momentum_signal = "Bearish"
    else:
        trend = "Stable"
        momentum_signal = "Neutral"

    return {
        "velocity": round(current_velocity, 0),
        "acceleration": round(current_acceleration, 0),
        "trend": trend,
        "momentum_signal": momentum_signal,
        "velocity_series": velocity.tolist()[-20:],  # Last 20 for charting
        "acceleration_series": acceleration.tolist()[-20:],
    }


def calculate_percentile_rank(
    current_value: float,
    historical_values: List[float],
    lookback_months: int = 12
) -> Dict:
    """
    Calculate percentile rank of current value vs historical data.

    Args:
        current_value: Current position value
        historical_values: List of historical values
        lookback_months: How many months to look back

    Returns:
        dict with percentile rank and context
    """
    import numpy as np

    if not historical_values:
        return {
            "percentile": 50.0,
            "rank_label": "Neutral",
            "historical_min": 0,
            "historical_max": 0,
            "historical_median": 0,
        }

    # Get lookback window (approximately 4 weeks per month)
    lookback_weeks = lookback_months * 4
    recent_data = historical_values[-lookback_weeks:] if len(historical_values) >= lookback_weeks else historical_values

    # Calculate percentile
    count_below = sum(1 for x in recent_data if x < current_value)
    percentile = (count_below / len(recent_data)) * 100
    percentile = round(percentile, 1)

    # Determine label
    if percentile >= 90:
        rank_label = "Extremely High"
    elif percentile >= 75:
        rank_label = "High"
    elif percentile >= 50:
        rank_label = "Above Average"
    elif percentile >= 25:
        rank_label = "Below Average"
    elif percentile >= 10:
        rank_label = "Low"
    else:
        rank_label = "Extremely Low"

    return {
        "percentile": percentile,
        "rank_label": rank_label,
        "historical_min": round(float(np.min(recent_data)), 0),
        "historical_max": round(float(np.max(recent_data)), 0),
        "historical_median": round(float(np.median(recent_data)), 0),
    }
