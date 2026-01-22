"""
COT PULSE - Institutional Positioning Intelligence
Bloomberg-lite, Stripe-clean, GS-calm design philosophy
"""

import reflex as rx
from typing import List, Dict
import plotly.graph_objects as go
from .cot_data import get_fetcher

# ============================================================================
# INSTITUTIONAL DESIGN SYSTEM
# ============================================================================
# Core principles:
# - Fewer visible containers
# - Fewer accent colors
# - Larger typography contrast
# - Interpretation > decoration
# - Spacing communicates hierarchy, not borders
# ============================================================================

# Typography CSS variables (to be applied globally)
# Premium fonts: Jost for UI/headings (geometric, modern), JetBrains Mono for numeric data
FONT_STACK = {
    "ui": '"Jost", system-ui, -apple-system, sans-serif',
    "heading": '"Jost", system-ui, -apple-system, sans-serif',
    "numeric": '"JetBrains Mono", "IBM Plex Mono", monospace',
}

class DarkTheme:
    """Institutional-grade dark theme - strict color system."""

    # ========================================
    # BASE BACKGROUNDS
    # ========================================
    bg_primary = "#0B0F17"      # Deepest background
    bg_secondary = "#0F1420"    # Card/section background
    bg_tertiary = "#131A2A"     # Elevated elements

    # Legacy aliases for compatibility
    bg_gradient_start = "#0B0F17"
    bg_gradient_mid = "#0F1420"
    bg_gradient_end = "#0B0F17"

    # ========================================
    # CARD STYLING - Prefer spacing over boxes
    # ========================================
    card_bg = "rgba(255, 255, 255, 0.015)"       # Very subtle
    card_bg_hover = "rgba(255, 255, 255, 0.03)"  # Soft hover
    card_border = "rgba(255, 255, 255, 0.04)"    # Nearly invisible
    card_border_hover = "rgba(255, 255, 255, 0.08)"

    # ========================================
    # TEXT COLORS - High contrast hierarchy
    # ========================================
    text_primary = "#E6E9F0"    # Primary content
    text_secondary = "#9AA3B2"  # Supporting text
    text_muted = "#6B7280"      # Labels, captions

    # ========================================
    # ACCENT COLORS - Use sparingly!
    # ========================================
    # Primary accent ONLY for: active asset, selected filter, primary metric
    accent_blue = "#5FA8FF"     # Selection only
    accent_purple = "#8b5cf6"   # Keep but rarely use
    accent_gradient = "linear-gradient(90deg, #5FA8FF, #5FA8FF)"

    # ========================================
    # STATUS COLORS - Muted, professional
    # ========================================
    # Muted green - not neon
    green = "#4CAF91"           # Positive/Long
    green_light = "#5BC9A6"
    green_bg = "rgba(76, 175, 145, 0.08)"
    green_border = "rgba(76, 175, 145, 0.15)"

    # Muted red - not alarming
    red = "#D06C6C"             # Negative/Short
    red_bg = "rgba(208, 108, 108, 0.08)"
    red_border = "rgba(208, 108, 108, 0.15)"

    purple = "#a371f7"
    purple_bg = "rgba(163, 113, 247, 0.08)"
    purple_border = "rgba(163, 113, 247, 0.15)"

    # ========================================
    # CHART COLORS
    # ========================================
    chart_long = "#4CAF91"      # Muted green
    chart_short = "#D06C6C"     # Muted red
    chart_net = "#5FA8FF"       # Accent blue
    chart_nc = "#5FA8FF"

    # ========================================
    # GRID - Barely visible
    # ========================================
    grid_color = "rgba(255, 255, 255, 0.025)"


class LightTheme:
    """Light mode theme."""
    bg_primary = "#f8fafc"
    bg_secondary = "#ffffff"
    bg_gradient_start = "#f8fafc"
    bg_gradient_mid = "#ffffff"
    bg_gradient_end = "#f8fafc"

    card_bg = "rgba(255, 255, 255, 0.8)"
    card_bg_hover = "rgba(255, 255, 255, 0.9)"
    card_border = "rgba(0, 0, 0, 0.1)"
    card_border_hover = "rgba(0, 0, 0, 0.2)"

    text_primary = "#1e293b"
    text_secondary = "#475569"
    text_muted = "#94a3b8"

    accent_blue = "#3b82f6"
    accent_purple = "#7c3aed"
    accent_gradient = "linear-gradient(90deg, #3b82f6, #7c3aed)"

    green = "#059669"
    green_light = "#10b981"
    green_bg = "rgba(5, 150, 105, 0.1)"
    green_border = "rgba(5, 150, 105, 0.3)"

    red = "#dc2626"
    red_bg = "rgba(220, 38, 38, 0.1)"
    red_border = "rgba(220, 38, 38, 0.3)"

    purple = "#7c3aed"
    purple_bg = "rgba(124, 58, 237, 0.1)"
    purple_border = "rgba(124, 58, 237, 0.3)"

    chart_long = "#10b981"
    chart_short = "#dc2626"
    chart_net = "#7c3aed"
    chart_nc = "#3b82f6"

    grid_color = "rgba(0, 0, 0, 0.05)"


# ============================================================================
# DATA
# ============================================================================

ASSET_CATEGORIES: Dict[str, List[Dict[str, str]]] = {
    "Energy": [
        {"symbol": "CL", "name": "Crude Oil WTI"},
        {"symbol": "BZ", "name": "Brent Crude Oil"},
        {"symbol": "NG", "name": "Natural Gas"},
        {"symbol": "RB", "name": "RBOB Gasoline"},
        {"symbol": "HO", "name": "Heating Oil"},
    ],
    "Metals": [
        {"symbol": "GC", "name": "Gold"},
        {"symbol": "SI", "name": "Silver"},
        {"symbol": "HG", "name": "Copper"},
        {"symbol": "PL", "name": "Platinum"},
        {"symbol": "PA", "name": "Palladium"},
    ],
    "Grains": [
        {"symbol": "ZC", "name": "Corn"},
        {"symbol": "ZS", "name": "Soybeans"},
        {"symbol": "ZW", "name": "Wheat (SRW)"},
        {"symbol": "KE", "name": "Wheat (HRW)"},
        {"symbol": "ZM", "name": "Soybean Meal"},
        {"symbol": "ZL", "name": "Soybean Oil"},
        {"symbol": "ZO", "name": "Oats"},
        {"symbol": "ZR", "name": "Rough Rice"},
    ],
    "Softs": [
        {"symbol": "CT", "name": "Cotton"},
        {"symbol": "KC", "name": "Coffee"},
        {"symbol": "SB", "name": "Sugar"},
        {"symbol": "CC", "name": "Cocoa"},
        {"symbol": "OJ", "name": "Orange Juice"},
    ],
    "Livestock": [
        {"symbol": "LE", "name": "Live Cattle"},
        {"symbol": "HE", "name": "Lean Hogs"},
        {"symbol": "GF", "name": "Feeder Cattle"},
    ],
    "Equities": [
        {"symbol": "ES", "name": "E-Mini S&P 500"},
        {"symbol": "NQ", "name": "E-Mini Nasdaq 100"},
        {"symbol": "YM", "name": "E-Mini Dow Jones"},
        {"symbol": "RTY", "name": "E-Mini Russell 2000"},
        {"symbol": "VX", "name": "VIX Futures"},
        {"symbol": "NKD", "name": "Nikkei 225"},
    ],
    "Currencies": [
        {"symbol": "6E", "name": "Euro FX"},
        {"symbol": "6J", "name": "Japanese Yen"},
        {"symbol": "6B", "name": "British Pound"},
        {"symbol": "6A", "name": "Australian Dollar"},
        {"symbol": "6C", "name": "Canadian Dollar"},
        {"symbol": "6S", "name": "Swiss Franc"},
        {"symbol": "6N", "name": "New Zealand Dollar"},
        {"symbol": "6M", "name": "Mexican Peso"},
        {"symbol": "DX", "name": "US Dollar Index"},
        {"symbol": "BTC", "name": "Bitcoin"},
    ],
    "Treasuries": [
        {"symbol": "ZB", "name": "30-Year T-Bond"},
        {"symbol": "ZN", "name": "10-Year T-Note"},
        {"symbol": "ZF", "name": "5-Year T-Note"},
        {"symbol": "ZT", "name": "2-Year T-Note"},
        {"symbol": "UB", "name": "Ultra T-Bond"},
        {"symbol": "TN", "name": "Ultra 10-Year"},
    ],
}

# Flattened list for search dropdown
ALL_ASSETS: List[Dict[str, str]] = []
for category, assets in ASSET_CATEGORIES.items():
    for asset in assets:
        ALL_ASSETS.append({**asset, "category": category})

# Popular/featured assets for quick access (global)
POPULAR_ASSETS = ["ES", "GC", "CL", "6E", "NQ", "ZN", "ZC", "NG"]

# Popular assets per category
POPULAR_BY_CATEGORY: Dict[str, List[str]] = {
    "Equities": ["ES", "NQ", "YM", "RTY"],
    "Energy": ["CL", "NG", "RB", "HO"],
    "Metals": ["GC", "SI", "HG", "PL"],
    "Grains": ["ZC", "ZS", "ZW", "ZM"],
    "Softs": ["CT", "KC", "SB", "CC"],
    "Livestock": ["LE", "HE", "GF"],
    "Currencies": ["6E", "6J", "6B", "DX"],
    "Treasuries": ["ZB", "ZN", "ZF", "ZT"],
}

# Category display info (icon and color) - using valid Lucide icons
CATEGORY_INFO: Dict[str, Dict[str, str]] = {
    "Equities": {"icon": "trending-up", "color": "#3b82f6"},
    "Energy": {"icon": "zap", "color": "#f97316"},
    "Metals": {"icon": "circle", "color": "#eab308"},
    "Grains": {"icon": "leaf", "color": "#84cc16"},
    "Softs": {"icon": "package", "color": "#a855f7"},
    "Livestock": {"icon": "box", "color": "#ec4899"},
    "Currencies": {"icon": "dollar-sign", "color": "#06b6d4"},
    "Treasuries": {"icon": "building", "color": "#64748b"},
}


def fetch_cot_data(symbol: str) -> Dict:
    """Fetch real COT data from CFTC API."""
    fetcher = get_fetcher()
    return fetcher.fetch_latest_report(symbol)


def fetch_chart_data(symbol: str, report_type: str = "legacy") -> List[Dict]:
    """Fetch real historical COT data for charts - ALL available data.

    Args:
        symbol: The market symbol (e.g., 'CL' for Crude Oil)
        report_type: One of 'legacy', 'disaggregated', or 'tff'
    """
    fetcher = get_fetcher()
    return fetcher.fetch_historical_data(symbol, report_type=report_type)


# ============================================================================
# STATE
# ============================================================================

class State(rx.State):
    """Application state."""

    is_dark_mode: bool = True

    active_category: str = "Equities"
    selected_symbol: str = "ES"
    selected_name: str = "E-Mini S&P 500"

    # Search dropdown state
    search_query: str = ""
    search_dropdown_open: bool = False
    recent_assets: List[str] = ["ES", "GC", "CL"]  # Track recent selections

    # Hover states for dropdowns
    hover_commodities: bool = False
    hover_equities: bool = False
    hover_currencies: bool = False

    # Chart controls
    selected_trader: str = "all"
    selected_metric: str = "net_position"
    chart_type: str = "line"
    zoom_level: int = 100

    # Sparkline data for metric cards (4-week trend)
    oi_sparkline: List[int] = []
    long_sparkline: List[int] = []
    short_sparkline: List[int] = []

    # Login state
    login_email: str = ""
    login_password: str = ""
    show_password: bool = False
    remember_me: bool = False
    login_error: str = ""

    # Premium / Subscription state
    is_premium_user: bool = False
    subscription_tier: str = "free"  # "free" | "premium" | "pro"

    # Percentile Rank feature state
    show_percentile_modal: bool = False
    show_upgrade_modal: bool = False
    percentile_trader_type: str = "Non-Commercial"
    percentile_data: List[Dict] = []
    percentile_lookback: str = "1y"  # Default 1 year lookback
    percentile_history: List[Dict] = []  # Historical percentile data for chart
    current_percentile: float = 50.0  # Current percentile rank
    percentile_interpretation: str = ""  # Text interpretation of percentile

    # Premium feature upgrade state
    upgrade_feature_name: str = ""  # Which feature triggered the upgrade modal (zscore, velocity)

    # Premium feature states
    show_zscore: bool = False
    show_velocity: bool = False
    top_bullish: List[Dict] = []
    bottom_bearish: List[Dict] = []

    # Loading states
    is_refreshing: bool = False
    last_updated: str = ""

    # Chart series visibility for interactive legend
    show_nc_series: bool = True
    show_comm_series: bool = True
    show_nr_series: bool = True
    show_trader4_series: bool = True  # For disaggregated/TFF 4th trader

    # Expandable categories state
    expanded_categories: List[str] = []  # All collapsed by default for cleaner UX

    # Gauge toggle state (True = show long view, False = short view)
    show_gauge_long_view: bool = True

    # Watchlist/Portfolio state
    watchlist: List[Dict] = [
        {"symbol": "ES", "name": "E-Mini S&P 500", "category": "Equities"},
        {"symbol": "GC", "name": "Gold", "category": "Metals"},
        {"symbol": "CL", "name": "Crude Oil", "category": "Energy"},
    ]  # Default watchlist items

    # Navigation state
    active_nav: str = "dashboard"
    show_search_modal: bool = False

    # Report Type state (Legacy, Disaggregated, TFF)
    report_type: str = "legacy"  # 'legacy', 'disaggregated', 'tff'

    # Chart display state
    show_percent_oi: bool = False  # Toggle for % of Open Interest view
    chart_time_period: str = "3Y"  # "1Y", "2Y", "3Y", "ALL"

    def toggle_category(self, category: str):
        """Toggle expand/collapse state of a category."""
        if category in self.expanded_categories:
            self.expanded_categories = [c for c in self.expanded_categories if c != category]
        else:
            self.expanded_categories = self.expanded_categories + [category]

    def is_category_expanded(self, category: str) -> bool:
        """Check if category is expanded."""
        return category in self.expanded_categories

    def toggle_gauge_view(self):
        """Toggle between net long and net short gauge view."""
        print(f"[Gauge Toggle] Before: show_gauge_long_view = {self.show_gauge_long_view}")
        self.show_gauge_long_view = not self.show_gauge_long_view
        print(f"[Gauge Toggle] After: show_gauge_long_view = {self.show_gauge_long_view}")

    # Watchlist methods
    def add_to_watchlist(self):
        """Add current asset to watchlist."""
        # Check if already in watchlist
        symbols_in_watchlist = [item["symbol"] for item in self.watchlist]
        if self.selected_symbol not in symbols_in_watchlist:
            # Find the asset info
            for asset in ALL_ASSETS:
                if asset["symbol"] == self.selected_symbol:
                    self.watchlist = self.watchlist + [{
                        "symbol": asset["symbol"],
                        "name": asset["name"],
                        "category": asset["category"],
                    }]
                    print(f"[Watchlist] Added {self.selected_symbol} to watchlist")
                    break

    def remove_from_watchlist(self, symbol: str):
        """Remove asset from watchlist."""
        self.watchlist = [item for item in self.watchlist if item["symbol"] != symbol]
        print(f"[Watchlist] Removed {symbol} from watchlist")

    def toggle_watchlist(self):
        """Toggle current asset in/out of watchlist."""
        symbols_in_watchlist = [item["symbol"] for item in self.watchlist]
        if self.selected_symbol in symbols_in_watchlist:
            self.remove_from_watchlist(self.selected_symbol)
        else:
            self.add_to_watchlist()

    @rx.var
    def is_in_watchlist(self) -> bool:
        """Check if current asset is in watchlist."""
        symbols_in_watchlist = [item["symbol"] for item in self.watchlist]
        return self.selected_symbol in symbols_in_watchlist

    @rx.var
    def watchlist_count(self) -> int:
        """Get number of items in watchlist."""
        return len(self.watchlist)

    def set_active_nav(self, nav: str):
        """Set active navigation item."""
        self.active_nav = nav

    def open_search_modal(self):
        """Open global search modal."""
        self.show_search_modal = True

    def close_search_modal(self):
        """Close global search modal."""
        self.show_search_modal = False
        self.search_query = ""

    def select_from_search(self, symbol: str):
        """Select an asset from the search modal."""
        # Find the asset info
        asset = next((a for a in ALL_ASSETS if a["symbol"] == symbol), None)
        if asset:
            self.select_asset(asset["category"], asset["symbol"], asset["name"])
        self.close_search_modal()

    # Report Type methods
    def set_report_type(self, report_type: str):
        """Change report type and reset trader to show all."""
        print(f"[REPORT TYPE] set_report_type called with: {report_type}")
        self.report_type = report_type
        # Reset trader to "all" so all series are shown
        self.selected_trader = "all"
        # Reload data with new report type
        self._update_cot_data()
        # Also update percentile data for the new report type
        print(f"[REPORT TYPE] Recalculating percentile data for report type: {report_type}")
        self._calculate_current_percentile_history()
        print(f"[REPORT TYPE] Done - percentile_history has {len(self.percentile_history)} points")

    def toggle_percent_oi(self):
        """Toggle between absolute values and % of Open Interest."""
        self.show_percent_oi = not self.show_percent_oi

    def set_chart_time_period(self, period: str):
        """Set chart time period (1Y, 2Y, 3Y, ALL)."""
        self.chart_time_period = period

    @rx.var
    def current_report_name(self) -> str:
        """Get display name of current report type."""
        names = {
            "legacy": "Legacy COT",
            "disaggregated": "Disaggregated",
            "tff": "TFF Report",
        }
        return names.get(self.report_type, "Legacy COT")

    @rx.var
    def current_report_icon(self) -> str:
        """Get icon for current report type."""
        icons = {
            "legacy": "clipboard-list",
            "disaggregated": "bar-chart-2",
            "tff": "trending-up",
        }
        return icons.get(self.report_type, "clipboard-list")

    @rx.var
    def current_traders(self) -> List[Dict]:
        """Get trader types available for current report."""
        traders = {
            "legacy": [
                {"key": "non_commercial", "label": "Non-Commercial", "icon": "briefcase", "desc": "Large Speculators"},
                {"key": "commercial", "label": "Commercial", "icon": "building", "desc": "Hedgers"},
                {"key": "non_reportable", "label": "Non-Reportable", "icon": "users", "desc": "Small Specs"},
            ],
            "disaggregated": [
                {"key": "producer", "label": "Producer/Merchant", "icon": "factory", "desc": "Physical Hedgers"},
                {"key": "swap_dealer", "label": "Swap Dealer", "icon": "landmark", "desc": "Banks/OTC"},
                {"key": "managed_money", "label": "Managed Money", "icon": "wallet", "desc": "CTAs/Hedge Funds"},
                {"key": "other_reportable", "label": "Other Reportable", "icon": "bar-chart", "desc": "Other Large"},
            ],
            "tff": [
                {"key": "dealer", "label": "Dealer", "icon": "landmark", "desc": "Sell-Side Banks"},
                {"key": "asset_manager", "label": "Asset Manager", "icon": "building-2", "desc": "Institutional"},
                {"key": "leveraged_funds", "label": "Leveraged Funds", "icon": "wallet", "desc": "Hedge Funds/CTAs"},
                {"key": "other_reportable", "label": "Other Reportable", "icon": "bar-chart", "desc": "Other Large"},
            ],
        }
        return traders.get(self.report_type, traders["legacy"])

    @rx.var
    def current_categories(self) -> List[str]:
        """Get asset categories available for current report type."""
        categories = {
            "legacy": ["Equities", "Energy", "Metals", "Grains", "Softs", "Livestock", "Currencies", "Treasuries"],
            "disaggregated": ["Energy", "Metals", "Grains", "Softs", "Livestock"],
            "tff": ["Equities", "Currencies", "Treasuries"],
        }
        return categories.get(self.report_type, categories["legacy"])

    @rx.var
    def chart_y_axis_label(self) -> str:
        """Get Y-axis label based on % OI toggle."""
        return "% of Open Interest" if self.show_percent_oi else "Net Contracts"

    def toggle_password_visibility(self):
        self.show_password = not self.show_password

    def toggle_remember_me(self):
        self.remember_me = not self.remember_me

    def set_login_email(self, email: str):
        self.login_email = email
        self.login_error = ""

    def set_login_password(self, password: str):
        self.login_password = password
        self.login_error = ""

    def handle_login(self):
        """Handle login form submission."""
        if not self.login_email:
            self.login_error = "Please enter your email"
            return
        if "@" not in self.login_email:
            self.login_error = "Please enter a valid email"
            return
        if not self.login_password:
            self.login_error = "Please enter your password"
            return
        if len(self.login_password) < 6:
            self.login_error = "Password must be at least 6 characters"
            return
        # Simulate successful login
        self.login_error = ""
        return rx.redirect("/")

    def handle_google_login(self):
        """Handle Google OAuth login."""
        print("Google OAuth initiated")
        return rx.redirect("/")

    def handle_apple_login(self):
        """Handle Apple OAuth login."""
        print("Apple OAuth initiated")
        return rx.redirect("/")

    # Percentile Rank feature methods
    def open_percentile_modal(self):
        """Open percentile modal directly - available to all users."""
        self._load_percentile_data()
        self._calculate_current_percentile_history()
        self.show_percentile_modal = True

    def set_percentile_lookback(self, lookback: str):
        """Change lookback period and reload percentile data."""
        print(f"[LOOKBACK] set_percentile_lookback called with: {lookback}")
        self.percentile_lookback = lookback
        # Always recalculate - since these buttons only appear in percentile view anyway
        print(f"[LOOKBACK] Recalculating percentile data for lookback: {lookback}")
        self._load_percentile_data()
        self._calculate_current_percentile_history()
        print(f"[LOOKBACK] Done - percentile_history has {len(self.percentile_history)} points")

    # Premium feature methods - Z-Score and Velocity
    show_zscore_panel: bool = False
    show_velocity_panel: bool = False
    zscore_data: Dict = {
        "z_score": 0.0,
        "interpretation": "Loading...",
        "color": "#94a3b8",
        "mean": 0,
        "std": 0,
        "current": 0,
        "trader_type": "Non-Commercial",
        "data_points": 0,
    }
    velocity_data: Dict = {
        "velocity": 0,
        "acceleration": 0,
        "trend": "Loading...",
        "signal": "Neutral",
        "color": "#94a3b8",
        "velocity_series": [],
        "trader_type": "Non-Commercial",
    }

    # View mode for chart: "individual" shows all 3 lines, "net" shows single net position
    chart_view_mode: str = "individual"
    # Chart data view: "position" shows net position, "percentile" shows percentile rank
    chart_data_view: str = "position"
    indicator_trader_type: str = "Non-Commercial"  # Which trader to analyze for Z-Score/Velocity

    def set_chart_view_mode(self, mode: str):
        """Toggle between individual lines and net position view."""
        self.chart_view_mode = mode
        self._recalculate_indicators()

    def set_chart_data_view(self, view: str):
        """Set chart data view: 'position' for net position, 'percentile' for percentile rank."""
        self.chart_data_view = view
        # Recalculate percentile history when switching to percentile view
        if view == "percentile":
            self._calculate_current_percentile_history()

    def set_indicator_trader_type(self, trader_type: str):
        """Set which trader type to analyze for Z-Score and Velocity."""
        self.indicator_trader_type = trader_type
        self._recalculate_indicators()

    def _recalculate_indicators(self):
        """Recalculate both Z-Score and Velocity if panels are open."""
        if self.show_zscore_panel:
            self._calculate_zscore()
        if self.show_velocity_panel:
            self._calculate_velocity()

    def toggle_zscore(self):
        """Toggle Z-Score panel visibility and load data."""
        self.show_zscore_panel = not self.show_zscore_panel
        if self.show_zscore_panel:
            self._calculate_zscore()

    def toggle_velocity(self):
        """Toggle Velocity panel visibility and load data."""
        self.show_velocity_panel = not self.show_velocity_panel
        if self.show_velocity_panel:
            self._calculate_velocity()

    def _get_trader_data_key(self) -> str:
        """Get the chart_data key for the selected trader type."""
        if self.indicator_trader_type == "Non-Commercial":
            return "non_commercial"
        elif self.indicator_trader_type == "Commercial":
            return "commercial"
        else:
            return "non_reportable"

    def _calculate_zscore(self):
        """Calculate Z-Score for selected trader type's net position."""
        import statistics

        # Get the correct data key based on selected trader type
        data_key = self._get_trader_data_key()

        # Get historical net positions from chart data
        historical_positions = []
        for point in self.chart_data:
            net_value = point.get(data_key, 0)
            historical_positions.append(net_value)

        # Apply zoom level to use same time period as chart
        if self.zoom_level < 100 and len(historical_positions) > 0:
            total_points = len(historical_positions)
            start_idx = int(total_points * (1 - self.zoom_level / 100))
            historical_positions = historical_positions[start_idx:]

        print(f"[Z-Score Debug] Trader: {self.indicator_trader_type}, Key: {data_key}")
        print(f"[Z-Score Debug] Data points: {len(historical_positions)}")

        if len(historical_positions) >= 2:
            current = historical_positions[-1]
            mean = statistics.mean(historical_positions)
            std = statistics.stdev(historical_positions)

            print(f"[Z-Score Debug] Current: {current}, Mean: {mean}, Std: {std}")

            if std > 0:
                z_score = (current - mean) / std
            else:
                z_score = 0.0

            # Interpretation - institutional language
            if z_score > 2:
                interpretation = "Bullish Extreme Positioning"
                color = "#3fb950"
            elif z_score > 1:
                interpretation = "Long Skew"
                color = "#56d364"
            elif z_score > -1:
                interpretation = "Neutral Positioning"
                color = "#8b949e"
            elif z_score > -2:
                interpretation = "Short Skew"
                color = "#f85149"
            else:
                interpretation = "Bearish Extreme Positioning"
                color = "#f85149"

            self.zscore_data = {
                "z_score": round(z_score, 2),
                "interpretation": interpretation,
                "color": color,
                "mean": int(round(mean, 0)),
                "std": int(round(std, 0)),
                "current": int(round(current, 0)),
                "trader_type": self.indicator_trader_type,
                "data_points": len(historical_positions),
            }
            print(f"[Z-Score Debug] Result: {self.zscore_data}")
        else:
            self.zscore_data = {
                "z_score": 0.0,
                "interpretation": "Insufficient Data",
                "color": "#94a3b8",
                "mean": 0,
                "std": 0,
                "current": 0,
                "trader_type": self.indicator_trader_type,
                "data_points": len(historical_positions),
            }
            print(f"[Z-Score Debug] Insufficient data: {len(historical_positions)} points")

    def _calculate_velocity(self):
        """Calculate positioning velocity for selected trader type."""
        # Get the correct data key based on selected trader type
        data_key = self._get_trader_data_key()

        # Get historical net positions
        historical_positions = []
        for point in self.chart_data:
            net_value = point.get(data_key, 0)
            historical_positions.append(net_value)

        # Apply zoom level to use same time period as chart
        if self.zoom_level < 100 and len(historical_positions) > 0:
            total_points = len(historical_positions)
            start_idx = int(total_points * (1 - self.zoom_level / 100))
            historical_positions = historical_positions[start_idx:]

        print(f"[Velocity Debug] Trader: {self.indicator_trader_type}, Data points: {len(historical_positions)}")

        if len(historical_positions) >= 3:
            # Calculate velocity (week-over-week change)
            velocities = []
            for i in range(1, len(historical_positions)):
                velocities.append(historical_positions[i] - historical_positions[i-1])

            # Calculate acceleration (change in velocity)
            accelerations = []
            for i in range(1, len(velocities)):
                accelerations.append(velocities[i] - velocities[i-1])

            current_velocity = velocities[-1] if velocities else 0
            current_acceleration = accelerations[-1] if accelerations else 0

            print(f"[Velocity Debug] Velocity: {current_velocity}, Acceleration: {current_acceleration}")

            # Determine trend - institutional language
            if current_velocity > 0:
                if current_acceleration > 0:
                    trend = "Accelerating Buildup"
                    signal = "Aggressive Accumulation"
                    color = "#3fb950"
                elif current_acceleration < 0:
                    trend = "Decelerating Buildup"
                    signal = "Slowing Accumulation"
                    color = "#56d364"
                else:
                    trend = "Steady Buildup"
                    signal = "Consistent Accumulation"
                    color = "#56d364"
            elif current_velocity < 0:
                if current_acceleration < 0:
                    trend = "Accelerating Selloff"
                    signal = "Aggressive Distribution"
                    color = "#f85149"
                elif current_acceleration > 0:
                    trend = "Decelerating Selloff"
                    signal = "Potential Inflection"
                    color = "#f85149"
                else:
                    trend = "Steady Selloff"
                    signal = "Consistent Distribution"
                    color = "#f85149"
            else:
                trend = "Stable"
                signal = "Neutral Flow"
                color = "#8b949e"

            self.velocity_data = {
                "velocity": int(round(current_velocity, 0)),
                "acceleration": int(round(current_acceleration, 0)),
                "trend": trend,
                "signal": signal,
                "color": color,
                "velocity_series": velocities[-10:],
                "trader_type": self.indicator_trader_type,
            }
        else:
            self.velocity_data = {
                "velocity": 0,
                "acceleration": 0,
                "trend": "Insufficient Data",
                "signal": "Neutral",
                "color": "#94a3b8",
                "velocity_series": [],
                "trader_type": self.indicator_trader_type,
            }

    def _load_percentile_data(self):
        """Load extreme positioning data for all assets with lookback period."""
        # Convert lookback to months for calculations
        lookback_months_map = {
            "6m": 6,
            "8m": 8,
            "1y": 12,
            "2y": 24,
            "3y": 36,
        }
        lookback_months = lookback_months_map.get(self.percentile_lookback, 12)

        # Calculate percentile ranks for all assets
        all_results = []
        for asset in ALL_ASSETS:
            try:
                data = fetch_cot_data(asset["symbol"])
                # Calculate net position based on selected trader type
                if self.percentile_trader_type == "Non-Commercial":
                    net = data.get("non_commercial_net", 0)
                elif self.percentile_trader_type == "Commercial":
                    net = data.get("commercial_net", 0)
                else:  # Non-Reportable
                    net = data.get("non_reportable_net", 0)

                oi = data.get("open_interest", 1)
                net_pct = (net / oi) * 100 if oi > 0 else 0

                # Percentile calculation adjusted by lookback period
                # Shorter lookbacks tend to show more extreme percentiles
                # Longer lookbacks normalize positions against more history
                lookback_factor = 12 / lookback_months  # Normalizing factor
                percentile = 50 + (net_pct * 2 * lookback_factor)
                percentile = max(0, min(100, percentile))

                all_results.append({
                    "symbol": asset["symbol"],
                    "asset_name": asset["name"],
                    "category": asset["category"],
                    "net_position": net,
                    "net_pct": round(net_pct, 2),
                    "percentile": round(percentile, 1),
                    "lookback": self.percentile_lookback,
                })
            except Exception:
                continue

        # Sort by percentile
        sorted_results = sorted(all_results, key=lambda x: x["percentile"], reverse=True)

        # Get top 5% and bottom 5%
        count = max(1, len(sorted_results) // 20)
        self.top_bullish = sorted_results[:count + 2]  # Top performers
        self.bottom_bearish = sorted_results[-(count + 2):]  # Bottom performers
        self.percentile_data = sorted_results

    def set_percentile_trader_type(self, trader_type: str):
        """Change trader type and reload percentile data."""
        print(f"[TRADER TYPE] set_percentile_trader_type called with: {trader_type}")
        print(f"[TRADER TYPE] chart_data_view = {self.chart_data_view}, show_modal = {self.show_percentile_modal}")
        self.percentile_trader_type = trader_type
        # Always recalculate - since these buttons only appear in percentile view anyway
        # This ensures the chart updates regardless of the exact condition state
        print(f"[TRADER TYPE] Recalculating percentile data for trader type: {trader_type}")
        self._load_percentile_data()
        self._calculate_current_percentile_history()
        print(f"[TRADER TYPE] Done - percentile_history has {len(self.percentile_history)} points")

    def _calculate_current_percentile_history(self):
        """Calculate historical percentile ranks for the current asset's chart."""
        print(f"[Percentile Debug] Starting calculation for symbol: {self.selected_symbol}")
        print(f"[Percentile Debug] chart_data length: {len(self.chart_data) if self.chart_data else 0}")
        # Debug: show first data point to verify which asset's data we have
        if self.chart_data and len(self.chart_data) > 0:
            print(f"[Percentile Debug] First data point date: {self.chart_data[0].get('date', 'N/A')}")
            print(f"[Percentile Debug] Last data point date: {self.chart_data[-1].get('date', 'N/A')}")

        if not self.chart_data:
            print("[Percentile Debug] No chart_data available!")
            self.percentile_history = []
            self.current_percentile = 50.0
            self.percentile_interpretation = "No data available"
            return

        # Get the trader data key based on selected type AND report type
        # Different report types have different field names
        if self.report_type == "legacy":
            trader_key_map = {
                "Non-Commercial": "non_commercial",
                "Commercial": "commercial",
                "Non-Reportable": "non_reportable",
            }
        elif self.report_type == "disaggregated":
            trader_key_map = {
                "Non-Commercial": "managed_money",  # Closest equivalent
                "Commercial": "producer_merchant",
                "Non-Reportable": "other_reportable",
            }
        else:  # tff
            trader_key_map = {
                "Non-Commercial": "leveraged_funds",  # Closest equivalent
                "Commercial": "dealer",
                "Non-Reportable": "other_reportable",
            }

        # Use report-type-aware default (first trader type for each report)
        default_keys = {
            "legacy": "non_commercial",
            "disaggregated": "managed_money",
            "tff": "leveraged_funds",
        }
        default_key = default_keys.get(self.report_type, "non_commercial")
        trader_key = trader_key_map.get(self.percentile_trader_type, default_key)

        print(f"[Percentile Debug] Report type: {self.report_type}, trader_type: {self.percentile_trader_type}, trader_key: {trader_key}")

        # Debug: show available keys in chart data
        if self.chart_data:
            print(f"[Percentile Debug] Chart data keys: {list(self.chart_data[0].keys())}")

        # Get all position values
        positions = [d.get(trader_key, 0) for d in self.chart_data]
        dates = [d.get("date", "") for d in self.chart_data]

        print(f"[Percentile Debug] Positions length: {len(positions)}")
        print(f"[Percentile Debug] Sample positions (first 5): {positions[:5] if positions else []}")
        print(f"[Percentile Debug] Sample positions (last 3): {positions[-3:] if len(positions) >= 3 else positions}")

        # Convert lookback to weeks
        lookback_months_map = {"6m": 6, "8m": 8, "1y": 12, "2y": 24, "3y": 36}
        lookback_months = lookback_months_map.get(self.percentile_lookback, 12)
        lookback_weeks = lookback_months * 4  # Approximate weeks

        # Calculate rolling percentile for each point
        percentile_history = []
        for i, (date, pos) in enumerate(zip(dates, positions)):
            # Use data up to this point for percentile calculation (excluding current)
            start_idx = max(0, i - lookback_weeks)
            # Use window EXCLUDING current point to compare against
            historical_window = positions[start_idx:i] if i > start_idx else []

            if len(historical_window) >= 4:  # Need minimum data
                # Proper percentile rank formula:
                # Count how many historical values are BELOW the current value
                values_below = sum(1 for v in historical_window if v < pos)

                # Calculate percentile: what % of historical values are below current
                percentile = (values_below / len(historical_window)) * 100.0

                # Clamp to 0-100 range
                percentile = max(0.0, min(100.0, percentile))
            else:
                percentile = 50.0

            percentile_history.append({
                "date": date,
                "percentile": round(percentile, 1),
                "position": pos,
            })

        self.percentile_history = percentile_history

        print(f"[Percentile Debug] Calculated {len(percentile_history)} history points")
        if percentile_history:
            pct_values = [h["percentile"] for h in percentile_history]
            print(f"[Percentile Debug] Range: {min(pct_values):.1f}% to {max(pct_values):.1f}%")
            print(f"[Percentile Debug] Sample: {percentile_history[-3:] if len(percentile_history) >= 3 else percentile_history}")

        # Set current percentile (last value)
        if percentile_history:
            self.current_percentile = percentile_history[-1]["percentile"]
        else:
            self.current_percentile = 50.0

        print(f"[Percentile Debug] Current percentile: {self.current_percentile}")

        # Generate interpretation
        pct = self.current_percentile
        trader_name = "Speculators" if self.percentile_trader_type == "Non-Commercial" else (
            "Hedgers" if self.percentile_trader_type == "Commercial" else "Small Traders"
        )

        if pct >= 90:
            self.percentile_interpretation = f"🔥 EXTREME BULLISH: {trader_name} positioning in the top {100-pct:.0f}% of the past {self.percentile_lookback}. Historically very bullish sentiment."
        elif pct >= 75:
            self.percentile_interpretation = f"📈 BULLISH: {trader_name} are positioned more long than {pct:.0f}% of the past {self.percentile_lookback}."
        elif pct >= 50:
            self.percentile_interpretation = f"⚖️ NEUTRAL-BULLISH: {trader_name} positioning is above average at the {pct:.0f}th percentile."
        elif pct >= 25:
            self.percentile_interpretation = f"📉 BEARISH: {trader_name} positioning is below average at the {pct:.0f}th percentile."
        elif pct >= 10:
            self.percentile_interpretation = f"⚠️ VERY BEARISH: {trader_name} are positioned more short than {100-pct:.0f}% of the past {self.percentile_lookback}."
        else:
            self.percentile_interpretation = f"🔻 EXTREME BEARISH: {trader_name} positioning in the bottom {pct:.0f}% of the past {self.percentile_lookback}. Historically very bearish."

    def close_percentile_modal(self):
        """Close the percentile rank modal."""
        self.show_percentile_modal = False

    def close_upgrade_modal(self):
        """Close the upgrade modal."""
        self.show_upgrade_modal = False

    def handle_upgrade_click(self):
        """Handle upgrade button click - redirect to pricing."""
        self.show_upgrade_modal = False
        return rx.redirect("/pricing")

    # COT Data
    report_date: str = "Loading..."
    open_interest: int = 2847234
    oi_change: int = 45234

    non_commercial_long: int = 487234
    non_commercial_short: int = 324156
    non_commercial_net: int = 163078
    non_commercial_change: int = 12453
    non_commercial_pct: float = 28.5

    commercial_long: int = 612000
    commercial_short: int = 758000
    commercial_net: int = -146000
    commercial_change: int = -8234
    commercial_pct: float = 48.2

    non_reportable_long: int = 148000
    non_reportable_short: int = 165078
    non_reportable_net: int = -17078
    non_reportable_change: int = 2341
    non_reportable_pct: float = 11.0

    chart_data: List[Dict] = []

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode

    def set_hover_commodities(self, hover: bool):
        self.hover_commodities = hover

    def set_hover_equities(self, hover: bool):
        self.hover_equities = hover

    def set_hover_currencies(self, hover: bool):
        self.hover_currencies = hover

    def set_search_query(self, query: str):
        self.search_query = query
        self.search_dropdown_open = len(query) > 0

    def open_search_dropdown(self):
        self.search_dropdown_open = True

    def close_search_dropdown(self):
        self.search_dropdown_open = False
        self.search_query = ""

    def set_active_category(self, category: str):
        """Set the active asset category for the dropdown."""
        self.active_category = category
        self.search_query = ""

    def select_asset(self, category: str, symbol: str, name: str):
        """Select an asset and update all chart data including percentile history."""
        print(f"[ASSET SELECT] select_asset called: {symbol} - {name}")
        self.active_category = category
        self.selected_symbol = symbol
        self.selected_name = name
        self._update_cot_data()
        # Also update percentile data for the new asset
        print(f"[ASSET SELECT] Recalculating percentile data for: {symbol}")
        self._calculate_current_percentile_history()
        print(f"[ASSET SELECT] Done - percentile_history has {len(self.percentile_history)} points")
        self.hover_commodities = False
        self.hover_equities = False
        self.hover_currencies = False
        # Track recent selections
        if symbol in self.recent_assets:
            self.recent_assets.remove(symbol)
        self.recent_assets.insert(0, symbol)
        if len(self.recent_assets) > 5:
            self.recent_assets = self.recent_assets[:5]
        # Close search dropdown
        self.search_dropdown_open = False
        self.search_query = ""

    @rx.var
    def filtered_assets(self) -> List[Dict[str, str]]:
        """Filter assets based on search query."""
        if not self.search_query:
            return ALL_ASSETS
        query = self.search_query.lower()
        return [
            a for a in ALL_ASSETS
            if query in a["symbol"].lower() or query in a["name"].lower()
        ]

    def select_trader(self, trader: str):
        self.selected_trader = trader

    def select_metric(self, metric: str):
        self.selected_metric = metric

    def set_chart_type(self, chart_type: str):
        self.chart_type = chart_type

    def zoom_in(self):
        if self.zoom_level > 25:
            self.zoom_level -= 25

    def zoom_out(self):
        if self.zoom_level < 100:
            self.zoom_level += 25

    def reset_zoom(self):
        self.zoom_level = 100

    def set_zoom_1y(self):
        self.zoom_level = 25

    def set_zoom_2y(self):
        self.zoom_level = 50

    def set_zoom_3y(self):
        self.zoom_level = 75

    def set_zoom_all(self):
        self.zoom_level = 100

    def _update_cot_data(self):
        print(f"[Data Update] Loading data for symbol: {self.selected_symbol}, report_type: {self.report_type}")
        try:
            data = fetch_cot_data(self.selected_symbol)
            print(f"[Data Update] Got COT data: report_date={data.get('report_date', 'N/A')}")
            self.report_date = data["report_date"]
            self.open_interest = data["open_interest"]
            self.oi_change = data["oi_change"]

            self.non_commercial_long = data["non_commercial_long"]
            self.non_commercial_short = data["non_commercial_short"]
            self.non_commercial_net = data["non_commercial_net"]
            self.non_commercial_change = data["non_commercial_change"]
            self.non_commercial_pct = data["non_commercial_pct"]

            self.commercial_long = data["commercial_long"]
            self.commercial_short = data["commercial_short"]
            self.commercial_net = data["commercial_net"]
            self.commercial_change = data["commercial_change"]
            self.commercial_pct = data["commercial_pct"]

            self.non_reportable_long = data["non_reportable_long"]
            self.non_reportable_short = data["non_reportable_short"]
            self.non_reportable_net = data["non_reportable_net"]
            self.non_reportable_change = data["non_reportable_change"]
            self.non_reportable_pct = data["non_reportable_pct"]

            # Fetch chart data with the correct report type
            chart_data = fetch_chart_data(self.selected_symbol, report_type=self.report_type)
            print(f"[Data Update] Got chart_data: {len(chart_data) if chart_data else 0} points for {self.report_type}")
            self.chart_data = chart_data
        except Exception as e:
            print(f"[Data Update] ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Display formatters
    @rx.var
    def nc_net_display(self) -> str:
        return f"{self.non_commercial_net:+,}"

    @rx.var
    def nc_change_display(self) -> str:
        return f"{self.non_commercial_change:+,}"

    @rx.var
    def nc_change_positive(self) -> bool:
        return self.non_commercial_change > 0

    @rx.var
    def comm_net_display(self) -> str:
        return f"{self.commercial_net:+,}"

    @rx.var
    def comm_change_display(self) -> str:
        return f"{self.commercial_change:+,}"

    @rx.var
    def comm_change_positive(self) -> bool:
        return self.commercial_change > 0

    @rx.var
    def nr_net_display(self) -> str:
        return f"{self.non_reportable_net:+,}"

    @rx.var
    def nr_change_display(self) -> str:
        return f"{self.non_reportable_change:+,}"

    @rx.var
    def nr_change_positive(self) -> bool:
        return self.non_reportable_change > 0

    @rx.var
    def report_date_formatted(self) -> str:
        """Format date as 'Jan 13, 2026' instead of ISO format."""
        if not self.report_date or self.report_date == "Loading...":
            return "Loading..."
        try:
            # Parse ISO date format (e.g., "2026-01-13T00:00:00.000")
            from datetime import datetime
            date_str = self.report_date.split("T")[0]  # Get just the date part
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%b %d, %Y")  # e.g., "Jan 13, 2026"
        except Exception:
            return self.report_date

    @rx.var
    def long_short_ratio(self) -> str:
        """Calculate Long/Short ratio for the primary trader."""
        total = self.gauge_long_value + self.gauge_short_value
        if total == 0 or self.gauge_short_value == 0:
            return "N/A"
        ratio = self.gauge_long_value / self.gauge_short_value
        return f"{ratio:.1f}:1"

    @rx.var
    def report_type_display(self) -> str:
        """Human-readable report type name."""
        if self.report_type == "legacy":
            return "Legacy Report"
        elif self.report_type == "disaggregated":
            return "Disaggregated"
        elif self.report_type == "tff":
            return "Traders in Financial Futures"
        return self.report_type.title()

    # =========================================================================
    # DYNAMIC TRADER POSITIONS - extracted from chart_data based on report_type
    # These provide the latest values for each trader category
    # =========================================================================

    @rx.var
    def trader1_net(self) -> int:
        """Latest net position for trader1 (Non-Commercial / Producer/Merchant / Dealer)."""
        if not self.chart_data:
            return 0
        latest = self.chart_data[-1]
        if self.report_type == "legacy":
            return latest.get("non_commercial", 0)
        elif self.report_type == "disaggregated":
            return latest.get("producer_merchant", 0)
        else:  # tff
            return latest.get("dealer", 0)

    @rx.var
    def trader2_net(self) -> int:
        """Latest net position for trader2 (Commercial / Swap Dealer / Asset Manager)."""
        if not self.chart_data:
            return 0
        latest = self.chart_data[-1]
        if self.report_type == "legacy":
            return latest.get("commercial", 0)
        elif self.report_type == "disaggregated":
            return latest.get("swap_dealer", 0)
        else:  # tff
            return latest.get("asset_manager", 0)

    @rx.var
    def trader3_net(self) -> int:
        """Latest net position for trader3 (Non-Reportable / Managed Money / Leveraged Funds)."""
        if not self.chart_data:
            return 0
        latest = self.chart_data[-1]
        if self.report_type == "legacy":
            return latest.get("non_reportable", 0)
        elif self.report_type == "disaggregated":
            return latest.get("managed_money", 0)
        else:  # tff
            return latest.get("leveraged_funds", 0)

    @rx.var
    def trader4_net(self) -> int:
        """Latest net position for trader4 (Other Reportable - disaggregated/TFF only)."""
        if not self.chart_data:
            return 0
        if self.report_type == "legacy":
            return 0  # Legacy doesn't have a 4th trader
        latest = self.chart_data[-1]
        return latest.get("other_reportable", 0)

    @rx.var
    def trader1_label(self) -> str:
        """Label for trader1."""
        if self.report_type == "legacy":
            return "Non-Commercial"
        elif self.report_type == "disaggregated":
            return "Producer/Merchant"
        else:
            return "Dealer"

    @rx.var
    def trader2_label(self) -> str:
        """Label for trader2."""
        if self.report_type == "legacy":
            return "Commercial"
        elif self.report_type == "disaggregated":
            return "Swap Dealer"
        else:
            return "Asset Manager"

    @rx.var
    def trader3_label(self) -> str:
        """Label for trader3."""
        if self.report_type == "legacy":
            return "Non-Reportable"
        elif self.report_type == "disaggregated":
            return "Managed Money"
        else:
            return "Leveraged Funds"

    @rx.var
    def trader4_label(self) -> str:
        """Label for trader4."""
        if self.report_type == "legacy":
            return ""
        else:
            return "Other Reportable"

    @rx.var
    def has_trader4(self) -> bool:
        """Whether the current report type has a 4th trader category."""
        return self.report_type != "legacy"

    # Short labels for gauge pills
    @rx.var
    def trader1_short(self) -> str:
        """Short label for trader1 (for gauge pills)."""
        if self.report_type == "legacy":
            return "NC"
        elif self.report_type == "disaggregated":
            return "PM"
        else:
            return "DLR"

    @rx.var
    def trader2_short(self) -> str:
        """Short label for trader2 (for gauge pills)."""
        if self.report_type == "legacy":
            return "COMM"
        elif self.report_type == "disaggregated":
            return "SWAP"
        else:
            return "AM"

    @rx.var
    def trader3_short(self) -> str:
        """Short label for trader3 (for gauge pills)."""
        if self.report_type == "legacy":
            return "NR"
        elif self.report_type == "disaggregated":
            return "MM"
        else:
            return "LEV"

    @rx.var
    def trader4_short(self) -> str:
        """Short label for trader4 (for gauge pills)."""
        return "OTH"

    @rx.var
    def trader1_net_display(self) -> str:
        """Formatted display of trader1 net position."""
        return f"{self.trader1_net:+,}"

    @rx.var
    def trader2_net_display(self) -> str:
        """Formatted display of trader2 net position."""
        return f"{self.trader2_net:+,}"

    @rx.var
    def trader3_net_display(self) -> str:
        """Formatted display of trader3 net position."""
        return f"{self.trader3_net:+,}"

    @rx.var
    def trader4_net_display(self) -> str:
        """Formatted display of trader4 net position."""
        return f"{self.trader4_net:+,}"

    @rx.var
    def trader1_positive(self) -> bool:
        """Whether trader1 net position is positive."""
        return self.trader1_net > 0

    @rx.var
    def trader2_positive(self) -> bool:
        """Whether trader2 net position is positive."""
        return self.trader2_net > 0

    @rx.var
    def trader3_positive(self) -> bool:
        """Whether trader3 net position is positive."""
        return self.trader3_net > 0

    @rx.var
    def trader4_positive(self) -> bool:
        """Whether trader4 net position is positive."""
        return self.trader4_net > 0

    # =========================================================================
    # TRADER % CHANGE (week-over-week) - for metric card bubbles
    # =========================================================================

    def _get_prev_trader_value(self, trader_key: str) -> int:
        """Helper to get previous week's value for a trader."""
        if not self.chart_data or len(self.chart_data) < 2:
            return 0
        prev = self.chart_data[-2]
        return prev.get(trader_key, 0)

    @rx.var
    def trader1_prev(self) -> int:
        """Previous week's net position for trader1."""
        if not self.chart_data or len(self.chart_data) < 2:
            return 0
        prev = self.chart_data[-2]
        if self.report_type == "legacy":
            return prev.get("non_commercial", 0)
        elif self.report_type == "disaggregated":
            return prev.get("producer_merchant", 0)
        else:  # tff
            return prev.get("dealer", 0)

    @rx.var
    def trader2_prev(self) -> int:
        """Previous week's net position for trader2."""
        if not self.chart_data or len(self.chart_data) < 2:
            return 0
        prev = self.chart_data[-2]
        if self.report_type == "legacy":
            return prev.get("commercial", 0)
        elif self.report_type == "disaggregated":
            return prev.get("swap_dealer", 0)
        else:  # tff
            return prev.get("asset_manager", 0)

    @rx.var
    def trader3_prev(self) -> int:
        """Previous week's net position for trader3."""
        if not self.chart_data or len(self.chart_data) < 2:
            return 0
        prev = self.chart_data[-2]
        if self.report_type == "legacy":
            return prev.get("non_reportable", 0)
        elif self.report_type == "disaggregated":
            return prev.get("managed_money", 0)
        else:  # tff
            return prev.get("leveraged_funds", 0)

    @rx.var
    def trader4_prev(self) -> int:
        """Previous week's net position for trader4."""
        if not self.chart_data or len(self.chart_data) < 2:
            return 0
        if self.report_type == "legacy":
            return 0
        prev = self.chart_data[-2]
        return prev.get("other_reportable", 0)

    @rx.var
    def trader1_change_pct(self) -> float:
        """Percent change from previous week for trader1."""
        if self.trader1_prev == 0:
            return 0.0
        return round(((self.trader1_net - self.trader1_prev) / abs(self.trader1_prev)) * 100, 1)

    @rx.var
    def trader2_change_pct(self) -> float:
        """Percent change from previous week for trader2."""
        if self.trader2_prev == 0:
            return 0.0
        return round(((self.trader2_net - self.trader2_prev) / abs(self.trader2_prev)) * 100, 1)

    @rx.var
    def trader3_change_pct(self) -> float:
        """Percent change from previous week for trader3."""
        if self.trader3_prev == 0:
            return 0.0
        return round(((self.trader3_net - self.trader3_prev) / abs(self.trader3_prev)) * 100, 1)

    @rx.var
    def trader4_change_pct(self) -> float:
        """Percent change from previous week for trader4."""
        if self.trader4_prev == 0:
            return 0.0
        return round(((self.trader4_net - self.trader4_prev) / abs(self.trader4_prev)) * 100, 1)

    @rx.var
    def trader1_change_positive(self) -> bool:
        """Whether trader1 change is positive."""
        return self.trader1_net > self.trader1_prev

    @rx.var
    def trader2_change_positive(self) -> bool:
        """Whether trader2 change is positive."""
        return self.trader2_net > self.trader2_prev

    @rx.var
    def trader3_change_positive(self) -> bool:
        """Whether trader3 change is positive."""
        return self.trader3_net > self.trader3_prev

    @rx.var
    def trader4_change_positive(self) -> bool:
        """Whether trader4 change is positive."""
        return self.trader4_net > self.trader4_prev

    @rx.var
    def nc_long_pct(self) -> float:
        total = self.non_commercial_long + self.non_commercial_short
        if total == 0:
            return 50.0
        return round((self.non_commercial_long / total) * 100, 1)

    @rx.var
    def comm_long_pct(self) -> float:
        total = self.commercial_long + self.commercial_short
        if total == 0:
            return 50.0
        return round((self.commercial_long / total) * 100, 1)

    @rx.var
    def nr_long_pct(self) -> float:
        total = self.non_reportable_long + self.non_reportable_short
        if total == 0:
            return 50.0
        return round((self.non_reportable_long / total) * 100, 1)

    @rx.var
    def net_sentiment_pct(self) -> float:
        """Overall net sentiment as percentage."""
        total_long = self.non_commercial_long + self.commercial_long + self.non_reportable_long
        total_short = self.non_commercial_short + self.commercial_short + self.non_reportable_short
        total = total_long + total_short
        if total == 0:
            return 50.0
        return round((total_long / total) * 100, 1)

    @rx.var
    def is_bullish(self) -> bool:
        return self.net_sentiment_pct > 50

    @rx.var
    def zoom_display(self) -> str:
        if self.zoom_level == 100:
            return "ALL"
        elif self.zoom_level == 75:
            return "3Y"
        elif self.zoom_level == 50:
            return "2Y"
        else:
            return "1Y"

    @rx.var
    def oi_display(self) -> str:
        if self.open_interest >= 1000000:
            return f"{self.open_interest / 1000000:.2f}M"
        elif self.open_interest >= 1000:
            return f"{self.open_interest / 1000:.1f}K"
        return str(self.open_interest)

    @rx.var
    def oi_change_display(self) -> str:
        return f"{self.oi_change:+,}"

    @rx.var
    def oi_change_positive(self) -> bool:
        return self.oi_change > 0

    @rx.var
    def oi_change_pct(self) -> float:
        if self.open_interest == 0:
            return 0.0
        return round((self.oi_change / self.open_interest) * 100, 1)

    # Gauge trader type selector (1, 2, 3, or 4 for trader1, trader2, trader3, trader4)
    gauge_trader_index: int = 1

    def set_gauge_trader_index(self, index: int):
        """Set which trader type to show in the gauge (1-4)."""
        self.gauge_trader_index = index

    # Keep legacy method for backwards compatibility during transition
    def set_gauge_trader_type(self, trader_type: str):
        """Legacy method - maps old names to new indices."""
        if trader_type in ["Non-Commercial", "Producer/Merchant", "Dealer"]:
            self.gauge_trader_index = 1
        elif trader_type in ["Commercial", "Swap Dealer", "Asset Manager"]:
            self.gauge_trader_index = 2
        elif trader_type in ["Non-Reportable", "Managed Money", "Leveraged Funds"]:
            self.gauge_trader_index = 3
        else:
            self.gauge_trader_index = 4

    @rx.var
    def gauge_trader_type(self) -> str:
        """Compute the trader type name based on index and report type."""
        if self.gauge_trader_index == 1:
            return self.trader1_label
        elif self.gauge_trader_index == 2:
            return self.trader2_label
        elif self.gauge_trader_index == 3:
            return self.trader3_label
        else:
            return self.trader4_label

    @rx.var
    def gauge_net_value(self) -> int:
        """Net position for selected gauge trader based on index."""
        if self.gauge_trader_index == 1:
            return self.trader1_net
        elif self.gauge_trader_index == 2:
            return self.trader2_net
        elif self.gauge_trader_index == 3:
            return self.trader3_net
        else:
            return self.trader4_net

    @rx.var
    def gauge_long_value(self) -> int:
        """Long positions for selected gauge trader type (legacy - uses non-commercial data)."""
        # For gauge display, we use legacy data which has long/short breakdown
        if self.gauge_trader_index == 1:
            return self.non_commercial_long
        elif self.gauge_trader_index == 2:
            return self.commercial_long
        return self.non_reportable_long

    @rx.var
    def gauge_short_value(self) -> int:
        """Short positions for selected gauge trader type (legacy - uses non-commercial data)."""
        # For gauge display, we use legacy data which has long/short breakdown
        if self.gauge_trader_index == 1:
            return self.non_commercial_short
        elif self.gauge_trader_index == 2:
            return self.commercial_short
        return self.non_reportable_short

    @rx.var
    def total_long_display(self) -> str:
        """Display long positions for selected trader type."""
        total = self.gauge_long_value
        if total >= 1000000:
            return f"{total / 1000000:.2f}M"
        elif total >= 1000:
            return f"{total / 1000:.1f}K"
        return str(total)

    @rx.var
    def total_short_display(self) -> str:
        """Display short positions for selected trader type."""
        total = self.gauge_short_value
        if total >= 1000000:
            return f"{total / 1000000:.2f}M"
        elif total >= 1000:
            return f"{total / 1000:.1f}K"
        return str(total)

    @rx.var
    def net_position_pct(self) -> float:
        """Net position as percentage of open interest for selected trader type."""
        net_value = self.gauge_net_value
        if self.open_interest == 0:
            return 0.0
        return round((abs(net_value) / self.open_interest) * 100, 1)

    @rx.var
    def is_net_long(self) -> bool:
        """Check if selected trader type is net long."""
        return self.gauge_net_value > 0

    @rx.var
    def net_position_label(self) -> str:
        """Label for net position (Net Long or Net Short)."""
        return "Net Long" if self.is_net_long else "Net Short"

    @rx.var
    def gauge_trader_label(self) -> str:
        """Human readable label for the selected gauge trader type."""
        # Return the full label for the selected trader
        return self.gauge_trader_type

    @rx.var
    def total_long_value(self) -> int:
        """Total long positions for selected trader type."""
        return self.gauge_long_value

    @rx.var
    def total_short_value(self) -> int:
        """Total short positions for selected trader type."""
        return self.gauge_short_value

    @rx.var
    def long_pct(self) -> float:
        """Long positions as percentage of total (long + short). Adds up to 100% with short_pct."""
        total = self.gauge_long_value + self.gauge_short_value
        if total == 0:
            return 50.0
        return round((self.gauge_long_value / total) * 100, 1)

    @rx.var
    def short_pct(self) -> float:
        """Short positions as percentage of total (long + short). Adds up to 100% with long_pct."""
        total = self.gauge_long_value + self.gauge_short_value
        if total == 0:
            return 50.0
        return round((self.gauge_short_value / total) * 100, 1)

    @rx.var
    def long_pct_display(self) -> str:
        """Display long percentage."""
        return f"{self.long_pct}%"

    @rx.var
    def short_pct_display(self) -> str:
        """Display short percentage."""
        return f"{self.short_pct}%"

    @rx.var
    def percentile_badge_text(self) -> str:
        """Percentile badge text for positioning context."""
        pct = self.current_percentile
        if pct >= 90:
            return f"{int(pct)}th pct long"
        elif pct >= 70:
            return f"{int(pct)}th pct long"
        elif pct >= 30:
            return f"{int(pct)}th pct"
        elif pct >= 10:
            return f"{int(pct)}th pct short"
        else:
            return f"{int(pct)}th pct short"

    @rx.var
    def percentile_badge_color(self) -> str:
        """Color for percentile badge based on value."""
        pct = self.current_percentile
        if pct >= 70:
            return "#10B981"  # Green - bullish
        elif pct >= 30:
            return "#6B7280"  # Gray - neutral
        else:
            return "#EF4444"  # Red - bearish

    def init_data(self):
        """Initialize data on page load."""
        print("=" * 60)
        print("[INIT_DATA] *** PAGE LOADED - init_data called! ***")
        print("=" * 60)
        self._update_cot_data()
        # Also initialize percentile data
        self._calculate_current_percentile_history()

    def refresh_data(self):
        """Refresh data with loading state."""
        self.is_refreshing = True
        yield
        self._update_cot_data()
        self.is_refreshing = False
        # Update timestamp
        from datetime import datetime
        self.last_updated = datetime.now().strftime("%I:%M %p")

    def toggle_nc_series(self):
        """Toggle Non-Commercial series visibility."""
        self.show_nc_series = not self.show_nc_series

    def toggle_comm_series(self):
        """Toggle Commercial series visibility."""
        self.show_comm_series = not self.show_comm_series

    def toggle_nr_series(self):
        """Toggle Non-Reportable series visibility."""
        self.show_nr_series = not self.show_nr_series

    def toggle_trader4_series(self):
        """Toggle Trader4 (Other Reportable) series visibility."""
        self.show_trader4_series = not self.show_trader4_series

    @rx.var
    def plotly_fig(self) -> go.Figure:
        """Generate Plotly figure with the new style - supports all report types."""
        print(f"[Main Chart Debug] plotly_fig called, chart_data length: {len(self.chart_data) if self.chart_data else 0}, report_type: {self.report_type}")
        if not self.chart_data:
            print("[Main Chart Debug] No chart_data, returning empty figure")
            fig = go.Figure()
            return fig

        # Debug: show the keys available in the first data point
        if self.chart_data:
            print(f"[Main Chart Debug] First data point keys: {list(self.chart_data[0].keys())}")
            print(f"[Main Chart Debug] First data point: {self.chart_data[0]}")

        dates = [d["date"] for d in self.chart_data]

        # Get data fields based on report type
        if self.report_type == "legacy":
            # Legacy: non_commercial, commercial, non_reportable
            trader1_data = [d.get("non_commercial", 0) for d in self.chart_data]
            trader2_data = [d.get("commercial", 0) for d in self.chart_data]
            trader3_data = [d.get("non_reportable", 0) for d in self.chart_data]
            trader4_data = None
            trader1_name = "Non-Commercial"
            trader2_name = "Commercial"
            trader3_name = "Non-Reportable"
            trader4_name = None
            trader1_key = "non_commercial"
            trader2_key = "commercial"
            trader3_key = "non_reportable"
            trader4_key = None
        elif self.report_type == "disaggregated":
            # Disaggregated: producer_merchant, swap_dealer, managed_money, other_reportable
            trader1_data = [d.get("producer_merchant", 0) for d in self.chart_data]
            trader2_data = [d.get("swap_dealer", 0) for d in self.chart_data]
            trader3_data = [d.get("managed_money", 0) for d in self.chart_data]
            trader4_data = [d.get("other_reportable", 0) for d in self.chart_data]
            trader1_name = "Producer/Merchant"
            trader2_name = "Swap Dealer"
            trader3_name = "Managed Money"
            trader4_name = "Other Reportable"
            trader1_key = "producer"
            trader2_key = "swap_dealer"
            trader3_key = "managed_money"
            trader4_key = "other"
        else:  # TFF
            # TFF: dealer, asset_manager, leveraged_funds, other_reportable
            trader1_data = [d.get("dealer", 0) for d in self.chart_data]
            trader2_data = [d.get("asset_manager", 0) for d in self.chart_data]
            trader3_data = [d.get("leveraged_funds", 0) for d in self.chart_data]
            trader4_data = [d.get("other_reportable", 0) for d in self.chart_data]
            trader1_name = "Dealer"
            trader2_name = "Asset Manager"
            trader3_name = "Leveraged Funds"
            trader4_name = "Other Reportable"
            trader1_key = "dealer"
            trader2_key = "asset_manager"
            trader3_key = "leveraged"
            trader4_key = "other"

        print(f"[Main Chart Debug] Data loaded - dates: {len(dates)}, trader1: {len(trader1_data)}")

        # Apply zoom
        total_points = len(dates)
        if self.zoom_level < 100:
            start_idx = int(total_points * (1 - self.zoom_level / 100))
            dates = dates[start_idx:]
            trader1_data = trader1_data[start_idx:]
            trader2_data = trader2_data[start_idx:]
            trader3_data = trader3_data[start_idx:]
            if trader4_data:
                trader4_data = trader4_data[start_idx:]

        fig = go.Figure()

        # Chart colors - Brighter, more differentiated palette for bars
        color1 = "#60A5FA"   # Bright blue (was #5FA8FF)
        color2 = "#F87171"   # Bright red (was #D06C6C)
        color3 = "#34D399"   # Bright green (was #4CAF91)
        color4 = "#A78BFA"   # Bright purple (was #9AA3B2 gray)

        # Determine which series to show based on selected_trader and visibility toggles
        show_trader1 = self.show_nc_series and self.selected_trader in ["all", trader1_key]
        show_trader2 = self.show_comm_series and self.selected_trader in ["all", trader2_key]
        show_trader3 = self.show_nr_series and self.selected_trader in ["all", trader3_key]
        show_trader4 = trader4_key and self.show_trader4_series and self.selected_trader in ["all", trader4_key]

        if show_trader1:
            if self.chart_type == "bar":
                fig.add_trace(go.Bar(
                    x=dates,
                    y=trader1_data,
                    name=trader1_name,
                    marker_color=color1,
                    marker_line=dict(color=color1, width=1),
                    opacity=0.9,
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=trader1_data,
                    mode="lines",
                    name=trader1_name,
                    line=dict(color=color1, width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(96, 165, 250, 0.15)",
                ))

        if show_trader2:
            if self.chart_type == "bar":
                fig.add_trace(go.Bar(
                    x=dates,
                    y=trader2_data,
                    name=trader2_name,
                    marker_color=color2,
                    marker_line=dict(color=color2, width=1),
                    opacity=0.9,
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=trader2_data,
                    mode="lines",
                    name=trader2_name,
                    line=dict(color=color2, width=2.5),
                ))

        if show_trader3:
            if self.chart_type == "bar":
                fig.add_trace(go.Bar(
                    x=dates,
                    y=trader3_data,
                    name=trader3_name,
                    marker_color=color3,
                    marker_line=dict(color=color3, width=1),
                    opacity=0.9,
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=trader3_data,
                    mode="lines",
                    name=trader3_name,
                    line=dict(color=color3, width=2.5),
                ))

        if show_trader4 and trader4_data:
            if self.chart_type == "bar":
                fig.add_trace(go.Bar(
                    x=dates,
                    y=trader4_data,
                    name=trader4_name,
                    marker_color=color4,
                    marker_line=dict(color=color4, width=1),
                    opacity=0.9,
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=trader4_data,
                    mode="lines",
                    name=trader4_name,
                    line=dict(color=color4, width=2.5),
                ))

        # Add zero reference line - THICKER for institutional look
        fig.add_hline(
            y=0,
            line_dash="solid",
            line_color="rgba(255, 255, 255, 0.15)",
            line_width=2,  # Thicker zero line
        )

        # Layout - Institutional professional style
        bg_color = "rgba(11, 15, 23, 0)" if self.is_dark_mode else "#ffffff"
        text_color = "#9AA3B2" if self.is_dark_mode else "#475569"
        grid_color = "rgba(255,255,255,0.025)" if self.is_dark_mode else "rgba(0,0,0,0.04)"  # Barely visible

        num_points = len(dates)
        if num_points > 200:
            dtick_val = "M12"
        elif num_points > 50:
            dtick_val = "M6"
        else:
            dtick_val = "M3"

        fig.update_layout(
            template="plotly_dark" if self.is_dark_mode else "plotly_white",
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color, family="Inter, system-ui, sans-serif", size=11),
            margin=dict(l=60, r=30, t=20, b=60),
            xaxis=dict(
                gridcolor=grid_color,
                showgrid=True,
                gridwidth=1,  # Thin grid lines
                tickformat="%Y" if num_points > 200 else "%b '%y",
                dtick=dtick_val,
                tickangle=0,
                tickfont=dict(size=10, color=text_color, family="Inter, system-ui, sans-serif"),
                showline=False,
            ),
            yaxis=dict(
                gridcolor=grid_color,
                showgrid=True,
                gridwidth=1,  # Thin grid lines
                tickformat=",.0f",
                zeroline=True,
                zerolinecolor="rgba(255,255,255,0.12)" if self.is_dark_mode else "rgba(0,0,0,0.1)",
                zerolinewidth=2,  # Thicker zero line
                tickfont=dict(size=10, color=text_color, family="IBM Plex Mono, monospace"),
                showline=False,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=11, color=text_color, family="Inter, system-ui, sans-serif"),
                bgcolor="rgba(0,0,0,0)",
            ),
            hovermode="x unified",
            barmode="group",
            bargap=0.15,
            hoverlabel=dict(
                bgcolor="#0F1420" if self.is_dark_mode else "#ffffff",
                font_size=11,
                font_family="Inter, system-ui, sans-serif",
                bordercolor="rgba(255,255,255,0.06)" if self.is_dark_mode else "rgba(0,0,0,0.1)",
            ),
        )

        return fig

    @rx.var
    def percentile_chart_fig(self) -> go.Figure:
        """Generate Plotly figure for percentile rank history."""
        print(f"[Chart Debug] percentile_chart_fig called, history length: {len(self.percentile_history) if self.percentile_history else 0}")
        fig = go.Figure()

        if not self.percentile_history:
            print("[Chart Debug] No percentile_history data, returning empty figure")
            return fig

        dates = [d["date"] for d in self.percentile_history]
        percentiles = [d["percentile"] for d in self.percentile_history]

        # Add reference zones (horizontal fills)
        # Extreme bullish zone (>90)
        fig.add_hrect(
            y0=90, y1=100,
            fillcolor="rgba(16, 185, 129, 0.1)",
            line_width=0,
            annotation_text="Bullish Extreme",
            annotation_position="top right",
            annotation_font_color="#10b981",
            annotation_font_size=10,
        )

        # Bullish zone (75-90)
        fig.add_hrect(
            y0=75, y1=90,
            fillcolor="rgba(16, 185, 129, 0.05)",
            line_width=0,
        )

        # Bearish zone (10-25)
        fig.add_hrect(
            y0=10, y1=25,
            fillcolor="rgba(239, 68, 68, 0.05)",
            line_width=0,
        )

        # Extreme bearish zone (<10)
        fig.add_hrect(
            y0=0, y1=10,
            fillcolor="rgba(239, 68, 68, 0.1)",
            line_width=0,
            annotation_text="Bearish Extreme",
            annotation_position="bottom right",
            annotation_font_color="#ef4444",
            annotation_font_size=10,
        )

        # Add neutral line at 50
        fig.add_hline(
            y=50,
            line_dash="dash",
            line_color="rgba(255, 255, 255, 0.3)",
            line_width=1,
        )

        # Percentile line with gradient fill
        fig.add_trace(go.Scatter(
            x=dates,
            y=percentiles,
            mode="lines",
            name="Percentile Rank",
            line=dict(color="#8b5cf6", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.15)",
        ))

        # Add current value marker
        if percentiles:
            current_pct = percentiles[-1]
            current_date = dates[-1]
            marker_color = "#10b981" if current_pct >= 50 else "#ef4444"

            fig.add_trace(go.Scatter(
                x=[current_date],
                y=[current_pct],
                mode="markers+text",
                name="Current",
                marker=dict(
                    size=12,
                    color=marker_color,
                    line=dict(width=2, color="white"),
                ),
                text=[f"{current_pct:.0f}%"],
                textposition="top center",
                textfont=dict(size=12, color=marker_color),
            ))

        # Layout
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(10, 14, 39, 0)",
            plot_bgcolor="rgba(10, 14, 39, 0)",
            font=dict(color="#94a3b8", family="Inter, sans-serif", size=12),
            margin=dict(l=50, r=30, t=20, b=50),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.05)",
                showgrid=True,
                gridwidth=1,
                tickformat="%b '%y",
                tickfont=dict(size=11, color="#94a3b8"),
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.05)",
                showgrid=True,
                gridwidth=1,
                tickfont=dict(size=11, color="#94a3b8"),
                range=[0, 100],
                dtick=25,
                ticksuffix="%",
            ),
            showlegend=False,
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#1a1f3a",
                font_size=12,
                font_family="Inter, sans-serif",
                bordercolor="rgba(255,255,255,0.1)",
            ),
        )

        return fig


# ============================================================================
# THEME HELPER
# ============================================================================

def themed(light_value: str, dark_value: str):
    return rx.cond(State.is_dark_mode, dark_value, light_value)


# ============================================================================
# COMPONENTS - Terminal-style Header (kept from before)
# ============================================================================

def terminal_logo() -> rx.Component:
    """Terminal-style logo."""
    return rx.hstack(
        rx.text(
            "COT",
            font_size="20px",
            font_weight="700",
            color=themed(LightTheme.accent_blue, "#60a5fa"),
            font_family="'Inter', sans-serif",
            letter_spacing="-0.02em",
        ),
        rx.text(
            "PULSE",
            font_size="20px",
            font_weight="400",
            color=themed(LightTheme.text_secondary, "#94a3b8"),
            font_family="'Inter', sans-serif",
        ),
        rx.box(
            width="8px",
            height="8px",
            border_radius="50%",
            background=themed(LightTheme.green, DarkTheme.green),
            box_shadow="0 0 10px rgba(16, 185, 129, 0.5)",
            margin_left="8px",
        ),
        spacing="1",
        align="center",
    )


def header_nav_item(text: str, href: str = "#") -> rx.Component:
    """Navigation item."""
    return rx.link(
        rx.text(
            text,
            font_size="14px",
            font_weight="500",
            color=themed(LightTheme.text_secondary, "#94a3b8"),
        ),
        href=href,
        padding_x="16px",
        padding_y="8px",
        text_decoration="none",
        _hover={
            "color": themed(LightTheme.accent_blue, "#60a5fa"),
        },
    )


def theme_toggle() -> rx.Component:
    """Theme toggle button."""
    return rx.box(
        rx.cond(
            State.is_dark_mode,
            rx.icon("sun", size=18, color="#94a3b8"),
            rx.icon("moon", size=18, color="#475569"),
        ),
        padding="10px",
        border_radius="8px",
        cursor="pointer",
        background=themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.03)"),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
        _hover={
            "background": themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.05)"),
        },
        on_click=State.toggle_theme,
    )


def nav_item(icon: str, label: str, nav_key: str, badge: rx.Var = None) -> rx.Component:
    """Navigation item with optional badge."""
    is_active = State.active_nav == nav_key

    return rx.box(
        rx.hstack(
            rx.icon(icon, size=16),
            rx.text(label, font_size="13px", font_weight="500"),
            rx.cond(
                badge is not None,
                rx.box(
                    rx.text(
                        badge,
                        font_size="10px",
                        font_weight="600",
                        color="white",
                    ),
                    padding_x="6px",
                    padding_y="2px",
                    background="linear-gradient(135deg, #8b5cf6, #a855f7)",
                    border_radius="10px",
                    min_width="18px",
                    text_align="center",
                ),
                rx.fragment(),
            ),
            spacing="2",
            align="center",
        ),
        padding_x="14px",
        padding_y="8px",
        border_radius="8px",
        cursor="pointer",
        color=rx.cond(is_active, "#a78bfa", themed(LightTheme.text_secondary, "#94a3b8")),
        background=rx.cond(is_active, "rgba(139, 92, 246, 0.15)", "transparent"),
        on_click=lambda: State.set_active_nav(nav_key),
        _hover={
            "background": "rgba(255, 255, 255, 0.05)",
            "color": "#e2e8f0",
        },
        transition="all 0.2s ease",
    )


def terminal_header() -> rx.Component:
    """Command Bar - 56px height, flat, calm institutional style."""
    return rx.box(
        rx.hstack(
            # Left side - Nav only (logo removed, using background watermark instead)
            rx.hstack(
                # Main Nav - Desktop only
                rx.hstack(
                    nav_item("layout-dashboard", "Dashboard", "dashboard"),
                    nav_item("briefcase", "Portfolio", "portfolio", State.watchlist_count.to(str)),
                    nav_item("bell", "Alerts", "alerts"),
                    nav_item("book-open", "Education", "education"),
                    spacing="1",
                    display=["none", "none", "none", "flex"],  # Hide on smaller screens
                ),
                spacing="6",
                align="center",
            ),
            rx.spacer(),
            # Right side - Search + Settings + Auth
            rx.hstack(
                # Global Search - Desktop only
                rx.box(
                    rx.hstack(
                        rx.icon("search", size=14, color="#64748b"),
                        rx.text(
                            "Search assets...",
                            font_size="13px",
                            color="#64748b",
                        ),
                        rx.box(
                            rx.text("⌘K", font_size="10px", color="#64748b", font_weight="600"),
                            padding_x="6px",
                            padding_y="2px",
                            background="rgba(255,255,255,0.1)",
                            border_radius="4px",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    padding_x="12px",
                    padding_y="8px",
                    background=themed("rgba(0,0,0,0.05)", "rgba(30, 41, 59, 0.5)"),
                    border="1px solid",
                    border_color=themed("rgba(0,0,0,0.1)", "rgba(255, 255, 255, 0.1)"),
                    border_radius="8px",
                    cursor="pointer",
                    on_click=State.open_search_modal,
                    _hover={
                        "border_color": "rgba(139, 92, 246, 0.3)",
                        "background": themed("rgba(0,0,0,0.08)", "rgba(30, 41, 59, 0.8)"),
                    },
                    display=["none", "none", "flex", "flex"],  # Hide on mobile
                ),
                # Theme toggle
                theme_toggle(),
                # Settings icon
                rx.box(
                    rx.icon("settings", size=18, color=themed(LightTheme.text_secondary, "#94a3b8")),
                    padding="8px",
                    border_radius="8px",
                    cursor="pointer",
                    _hover={"background": "rgba(255,255,255,0.05)"},
                    display=["none", "flex", "flex", "flex"],  # Hide on smallest screens
                ),
                # User Avatar (logged in state)
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.text("K", font_size="12px", font_weight="600", color="white"),
                            width="32px",
                            height="32px",
                            background="linear-gradient(135deg, #8b5cf6, #6366f1)",
                            border_radius="50%",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        rx.icon("chevron-down", size=14, color="#64748b"),
                        spacing="1",
                        align="center",
                    ),
                    cursor="pointer",
                    _hover={"opacity": "0.8"},
                ),
                # Mobile menu icon - larger touch target (44px min)
                rx.box(
                    rx.icon("menu", size=22, color=themed(LightTheme.text_secondary, "#94a3b8")),
                    padding="10px",
                    min_width="44px",
                    min_height="44px",
                    border_radius="8px",
                    cursor="pointer",
                    _hover={"background": "rgba(255,255,255,0.08)"},
                    _active={"background": "rgba(255,255,255,0.12)"},
                    display=["flex", "flex", "none", "none"],  # Show only on mobile
                    align_items="center",
                    justify_content="center",
                ),
                spacing="2",
                align="center",
            ),
            width="100%",
            align="center",
        ),
        padding_x=["16px", "24px", "32px", "32px"],
        padding_y="8px",
        height="80px",
        background=themed(
            "rgba(255,255,255,0.98)",
            "#0F1420"  # bg_secondary - Command Bar background
        ),
        # Use gradient shadow instead of hard border for premium look
        border_bottom="none",
        box_shadow=themed(
            "0 1px 3px rgba(0, 0, 0, 0.08)",
            "0 1px 3px rgba(0, 0, 0, 0.3)"
        ),
        position="sticky",
        top="0",
        z_index="1000",
    )


# ============================================================================
# COMPONENTS - Main Dashboard (Trader Commitment Style)
# ============================================================================

def asset_dropdown_item(symbol: str, name: str, category: str) -> rx.Component:
    """Individual asset item in dropdown list."""
    is_selected = State.selected_symbol == symbol

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    f"{name} ({symbol})",
                    font_size="14px",
                    font_weight="500",
                    color=rx.cond(
                        is_selected,
                        themed(LightTheme.accent_blue, "#60a5fa"),
                        themed(LightTheme.text_primary, "#e2e8f0"),
                    ),
                ),
                rx.text(
                    category,
                    font_size="11px",
                    color=themed(LightTheme.text_muted, "#64748b"),
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.cond(
                is_selected,
                rx.icon("check", size=16, color="#60a5fa"),
                rx.fragment(),
            ),
            width="100%",
            align="center",
        ),
        padding_x="16px",
        padding_y="10px",
        cursor="pointer",
        background=rx.cond(
            is_selected,
            themed("rgba(59,130,246,0.1)", "rgba(96,165,250,0.1)"),
            "transparent",
        ),
        _hover={
            "background": themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
        },
        on_click=lambda: State.select_asset(category, symbol, name),
    )


def category_tab(category: str) -> rx.Component:
    """Asset class tab button."""
    info = CATEGORY_INFO.get(category, {"icon": "folder", "color": "#64748b"})
    is_active = State.active_category == category

    return rx.box(
        rx.hstack(
            rx.icon(
                info["icon"],
                size=14,
                color=rx.cond(is_active, info["color"], themed(LightTheme.text_muted, "#64748b")),
            ),
            rx.text(
                category,
                font_size="12px",
                font_weight=rx.cond(is_active, "600", "500"),
                color=rx.cond(is_active, themed(LightTheme.text_primary, "#e2e8f0"), themed(LightTheme.text_muted, "#64748b")),
            ),
            spacing="1",
            align="center",
        ),
        padding_x="12px",
        padding_y="8px",
        border_radius="8px",
        cursor="pointer",
        background=rx.cond(
            is_active,
            themed(f"rgba(59, 130, 246, 0.1)", f"{info['color']}20"),
            "transparent",
        ),
        border="1px solid",
        border_color=rx.cond(
            is_active,
            info["color"],
            "transparent",
        ),
        _hover={
            "background": rx.cond(
                is_active,
                themed(f"rgba(59, 130, 246, 0.15)", f"{info['color']}30"),
                themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
            ),
        },
        transition="all 0.2s ease",
        on_click=lambda: State.set_active_category(category),
    )


def popular_asset_chip(symbol: str) -> rx.Component:
    """Quick access chip for popular assets."""
    # Find asset details
    asset_info = next((a for a in ALL_ASSETS if a["symbol"] == symbol), None)
    if not asset_info:
        return rx.fragment()

    is_selected = State.selected_symbol == symbol

    return rx.box(
        rx.text(
            symbol,
            font_size="12px",
            font_weight="600",
        ),
        padding_x="12px",
        padding_y="6px",
        border_radius="20px",
        cursor="pointer",
        background=rx.cond(
            is_selected,
            "linear-gradient(90deg, #3b82f6, #8b5cf6)",
            themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
        ),
        color=rx.cond(
            is_selected,
            "white",
            themed(LightTheme.text_secondary, "#94a3b8"),
        ),
        _hover={
            "background": rx.cond(
                is_selected,
                "linear-gradient(90deg, #2563eb, #7c3aed)",
                themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
            ),
        },
        on_click=lambda: State.select_asset(asset_info["category"], symbol, asset_info["name"]),
    )


def expandable_asset_chip(symbol: str, name: str, category: str) -> rx.Component:
    """Individual asset chip for expandable categories."""
    is_selected = State.selected_symbol == symbol
    category_color = CATEGORY_INFO.get(category, {}).get("color", "#64748b")

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    name,
                    font_size="13px",
                    font_weight="500",
                    color=rx.cond(is_selected, "#ffffff", themed(LightTheme.text_primary, "#e2e8f0")),
                ),
                rx.text(
                    symbol,
                    font_size="11px",
                    color=rx.cond(is_selected, "rgba(255,255,255,0.8)", themed(LightTheme.text_muted, "#64748b")),
                ),
                spacing="0",
                align="start",
            ),
            spacing="2",
            align="center",
        ),
        padding_x="14px",
        padding_y="10px",
        border_radius="10px",
        cursor="pointer",
        background=rx.cond(
            is_selected,
            f"linear-gradient(135deg, {category_color}, {category_color}dd)",
            themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.03)"),
        ),
        border="1px solid",
        border_color=rx.cond(
            is_selected,
            category_color,
            themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
        ),
        box_shadow=rx.cond(
            is_selected,
            f"0 4px 12px {category_color}40",
            "none",
        ),
        _hover={
            "background": rx.cond(
                is_selected,
                f"linear-gradient(135deg, {category_color}, {category_color}dd)",
                themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.06)"),
            ),
            "border_color": rx.cond(is_selected, category_color, f"{category_color}60"),
            "transform": "translateY(-1px)",
        },
        transition="all 0.2s ease",
        min_width="140px",
        on_click=lambda: State.select_asset(category, symbol, name),
    )


def expandable_category_header(category: str, is_expanded: rx.Var[bool]) -> rx.Component:
    """Header for expandable category with icon and color accent."""
    info = CATEGORY_INFO.get(category, {"icon": "folder", "color": "#64748b"})
    assets_count = len(ASSET_CATEGORIES.get(category, []))

    return rx.box(
        rx.hstack(
            # Color accent bar
            rx.box(
                width="4px",
                height="24px",
                background=info["color"],
                border_radius="2px",
            ),
            rx.icon(
                info["icon"],
                size=18,
                color=info["color"],
            ),
            rx.text(
                category,
                font_size="14px",
                font_weight="600",
                color=themed(LightTheme.text_primary, "#e2e8f0"),
            ),
            rx.text(
                f"({assets_count})",
                font_size="12px",
                color=themed(LightTheme.text_muted, "#64748b"),
            ),
            rx.spacer(),
            rx.icon(
                rx.cond(is_expanded, "chevron-up", "chevron-down"),
                size=18,
                color=themed(LightTheme.text_muted, "#64748b"),
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="12px 16px",
        cursor="pointer",
        border_radius="10px",
        background=themed("rgba(0,0,0,0.02)", "rgba(255,255,255,0.02)"),
        _hover={
            "background": themed("rgba(0,0,0,0.04)", "rgba(255,255,255,0.04)"),
        },
        transition="all 0.2s ease",
        on_click=lambda: State.toggle_category(category),
    )


def expandable_category_section(category: str) -> rx.Component:
    """Expandable category with assets grid."""
    assets = ASSET_CATEGORIES.get(category, [])
    is_expanded = State.expanded_categories.contains(category)

    return rx.vstack(
        # Category header
        expandable_category_header(category, is_expanded),
        # Assets grid (shown when expanded)
        rx.cond(
            is_expanded,
            rx.box(
                rx.box(
                    *[expandable_asset_chip(a["symbol"], a["name"], category) for a in assets],
                    display="flex",
                    flex_wrap="wrap",
                    gap="8px",
                    padding="12px 16px",
                ),
                overflow="hidden",
            ),
            rx.fragment(),
        ),
        spacing="0",
        width="100%",
    )


def asset_selector_section() -> rx.Component:
    """Asset selector with expandable categories (no search bar)."""
    return rx.box(
        rx.vstack(
            # Selected asset display at top
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "SELECTED ASSET",
                        font_size="10px",
                        text_transform="uppercase",
                        letter_spacing="0.1em",
                        color=themed(LightTheme.text_muted, "#64748b"),
                        font_weight="600",
                    ),
                    rx.hstack(
                        rx.text(
                            State.selected_name,
                            font_size="20px",
                            font_weight="700",
                            color=themed(LightTheme.text_primary, "#e2e8f0"),
                        ),
                        rx.box(
                            rx.text(
                                State.selected_symbol,
                                font_size="12px",
                                font_weight="600",
                                color="#8b5cf6",
                            ),
                            padding_x="10px",
                            padding_y="4px",
                            background="rgba(139,92,246,0.15)",
                            border_radius="6px",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                # Category badge
                rx.box(
                    rx.text(
                        State.active_category,
                        font_size="11px",
                        font_weight="500",
                        color=themed(LightTheme.text_secondary, "#94a3b8"),
                    ),
                    padding_x="12px",
                    padding_y="6px",
                    background=themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
                    border_radius="20px",
                ),
                width="100%",
                align="center",
                padding_bottom="16px",
                border_bottom="1px solid",
                border_color=themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
                margin_bottom="8px",
            ),
            # Expandable categories
            rx.vstack(
                expandable_category_section("Equities"),
                expandable_category_section("Energy"),
                expandable_category_section("Metals"),
                expandable_category_section("Grains"),
                expandable_category_section("Softs"),
                expandable_category_section("Livestock"),
                expandable_category_section("Currencies"),
                expandable_category_section("Treasuries"),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        padding="20px",
        background=themed("rgba(255,255,255,0.8)", "rgba(255,255,255,0.03)"),
        backdrop_filter="blur(10px)",
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
        border_radius="16px",
        width="100%",
        max_height="500px",
        overflow_y="auto",
        class_name="hide-scrollbar",
    )


def watchlist_item(item: Dict) -> rx.Component:
    """Individual watchlist item with signal indicator and delete button."""
    # Determine signal color based on category
    signal_colors = {
        "Equities": "#10b981",  # Green
        "Metals": "#eab308",    # Yellow
        "Energy": "#f97316",    # Orange
        "Currencies": "#06b6d4", # Cyan
    }
    signal_color = signal_colors.get(item.get("category", ""), "#8b5cf6")

    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.text(
                    item["symbol"],
                    font_size="12px",
                    font_weight="700",
                    color="#a78bfa",
                ),
                rx.text(
                    item["name"],
                    font_size="11px",
                    color="#94a3b8",
                    max_width="80px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            # Signal indicator
            rx.box(
                width="8px",
                height="8px",
                background=signal_color,
                border_radius="50%",
                box_shadow=f"0 0 6px {signal_color}",
            ),
            # Delete button - appears on hover via CSS
            rx.box(
                rx.icon("x", size=12, color="#94a3b8"),
                padding="2px",
                border_radius="4px",
                cursor="pointer",
                opacity="0",
                margin_left="6px",
                background="rgba(239, 68, 68, 0.1)",
                _hover={
                    "background": "rgba(239, 68, 68, 0.3)",
                    "color": "#ef4444",
                },
                on_click=lambda: State.remove_from_watchlist(item["symbol"]),
                class_name="watchlist-delete-btn",
            ),
            width="100%",
            align="center",
        ),
        padding_x="10px",
        padding_y="8px",
        background="rgba(0, 0, 0, 0.2)",
        border_radius="8px",
        cursor="pointer",
        on_click=lambda: State.select_asset(item["symbol"]),
        _hover={
            "background": "rgba(139, 92, 246, 0.15)",
        },
        transition="all 0.1s ease",
        class_name="watchlist-item",
    )


def watchlist_sidebar() -> rx.Component:
    """Watchlist/Portfolio section in sidebar."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    rx.icon("star", size=16, color="#eab308"),
                    rx.text(
                        "My Watchlist",
                        font_size="14px",
                        font_weight="600",
                        color=themed(LightTheme.text_primary, "#e2e8f0"),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.box(
                    rx.text(
                        State.watchlist_count.to(str),
                        font_size="11px",
                        font_weight="600",
                        color="#8b5cf6",
                    ),
                    padding_x="8px",
                    padding_y="3px",
                    background="rgba(139,92,246,0.2)",
                    border_radius="10px",
                ),
                width="100%",
                align="center",
            ),
            # Watchlist items
            rx.cond(
                State.watchlist_count > 0,
                rx.vstack(
                    rx.foreach(
                        State.watchlist,
                        watchlist_item,
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.text(
                    "No assets tracked yet",
                    font_size="12px",
                    color="#64748b",
                    font_style="italic",
                ),
            ),
            # View full portfolio link
            rx.hstack(
                rx.text(
                    "View Full Portfolio",
                    font_size="12px",
                    color="#a78bfa",
                ),
                rx.icon("arrow-right", size=14, color="#a78bfa"),
                spacing="1",
                align="center",
                cursor="pointer",
                _hover={"opacity": "0.7"},
                padding_top="8px",
            ),
            spacing="3",
            width="100%",
        ),
        padding="16px",
        background="linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(96, 165, 250, 0.1))",
        border="1px solid rgba(139, 92, 246, 0.2)",
        border_radius="12px",
    )


def report_type_option(key: str, icon: str, name: str, subtitle: str) -> rx.Component:
    """Individual report type option with radio button."""
    is_active = State.report_type == key

    return rx.hstack(
        # Radio circle
        rx.box(
            rx.cond(
                is_active,
                rx.box(
                    width="8px",
                    height="8px",
                    border_radius="50%",
                    background="#8b5cf6",
                ),
                rx.fragment(),
            ),
            width="16px",
            height="16px",
            border_radius="50%",
            border="2px solid",
            border_color=rx.cond(is_active, "#8b5cf6", "#64748b"),
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        # Label
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=14, color=rx.cond(is_active, "#a78bfa", "#94a3b8")),
                rx.text(
                    name,
                    font_size="13px",
                    font_weight="500",
                    color=rx.cond(is_active, "#a78bfa", "#e2e8f0"),
                ),
                spacing="2",
                align="center",
            ),
            rx.text(
                subtitle,
                font_size="11px",
                color="#64748b",
            ),
            spacing="0",
            align="start",
        ),
        width="100%",
        padding="8px 10px",
        border_radius="8px",
        cursor="pointer",
        background=rx.cond(is_active, "rgba(139, 92, 246, 0.15)", "transparent"),
        border="1px solid",
        border_color=rx.cond(is_active, "rgba(139, 92, 246, 0.3)", "transparent"),
        transition="all 0.2s ease",
        _hover={"background": "rgba(255, 255, 255, 0.05)"},
        on_click=lambda: State.set_report_type(key),
    )


def report_type_selector() -> rx.Component:
    """Radio-style report type selector."""
    return rx.vstack(
        report_type_option("legacy", "clipboard-list", "Legacy COT", "All Markets"),
        report_type_option("disaggregated", "bar-chart-2", "Disaggregated", "Commodities"),
        report_type_option("tff", "trending-up", "TFF Report", "Financials"),
        spacing="1",
        width="100%",
    )


def left_sidebar() -> rx.Component:
    """Left sidebar with report types, asset navigation, and watchlist."""
    return rx.box(
        rx.vstack(
            # Report Type Section
            rx.vstack(
                rx.text(
                    "REPORT TYPE",
                    font_size="11px",
                    font_weight="600",
                    color="#64748b",
                    letter_spacing="0.5px",
                ),
                report_type_selector(),
                spacing="2",
                width="100%",
                align="start",
            ),
            # Divider
            rx.divider(
                opacity="0.1",
                margin_y="12px",
            ),
            # Asset Categories Section - Dynamic based on report type
            rx.vstack(
                rx.text(
                    "ASSET CATEGORIES",
                    font_size="11px",
                    font_weight="600",
                    color="#64748b",
                    letter_spacing="0.5px",
                ),
                # Legacy COT: All categories
                rx.cond(
                    State.report_type == "legacy",
                    rx.box(
                        rx.vstack(
                            expandable_category_section("Equities"),
                            expandable_category_section("Energy"),
                            expandable_category_section("Metals"),
                            expandable_category_section("Grains"),
                            expandable_category_section("Softs"),
                            expandable_category_section("Livestock"),
                            expandable_category_section("Currencies"),
                            expandable_category_section("Treasuries"),
                            spacing="1",
                            width="100%",
                        ),
                        width="100%",
                        max_height="calc(100vh - 450px)",
                        overflow_y="auto",
                        class_name="hide-scrollbar",
                    ),
                    # Disaggregated or TFF
                    rx.cond(
                        State.report_type == "disaggregated",
                        # Disaggregated: Commodities only
                        rx.box(
                            rx.vstack(
                                expandable_category_section("Energy"),
                                expandable_category_section("Metals"),
                                expandable_category_section("Grains"),
                                expandable_category_section("Softs"),
                                expandable_category_section("Livestock"),
                                spacing="1",
                                width="100%",
                            ),
                            width="100%",
                            max_height="calc(100vh - 450px)",
                            overflow_y="auto",
                            class_name="hide-scrollbar",
                        ),
                        # TFF: Financials only
                        rx.box(
                            rx.vstack(
                                expandable_category_section("Equities"),
                                expandable_category_section("Currencies"),
                                expandable_category_section("Treasuries"),
                                spacing="1",
                                width="100%",
                            ),
                            width="100%",
                            max_height="calc(100vh - 450px)",
                            overflow_y="auto",
                            class_name="hide-scrollbar",
                        ),
                    ),
                ),
                spacing="2",
                width="100%",
                align="start",
                flex="1",
            ),
            # Watchlist
            rx.box(
                watchlist_sidebar(),
                width="100%",
            ),
            # AdSense Placeholder - Sidebar (300x250 Medium Rectangle)
            rx.box(
                ad_placeholder("228px", "190px", "SIDEBAR AD"),
                width="100%",
                margin_top="auto",
                padding_top="12px",
            ),
            spacing="3",
            height="100%",
            width="100%",
        ),
        width="240px",  # Slightly narrower
        min_width="240px",
        height="calc(100vh - 56px)",  # Subtract header height
        position="sticky",
        top="56px",
        background="transparent",  # No background - reduce visual weight
        border_right="1px solid",
        border_color=themed("rgba(0,0,0,0.04)", "rgba(255,255,255,0.03)"),  # Very subtle border
        padding="1rem 0.75rem",  # Slightly tighter padding
        overflow_y="auto",
        flex_shrink="0",
        display=["none", "none", "flex", "flex"],  # Hide on mobile
    )


def ad_placeholder(width: str, height: str, label: str = "AD") -> rx.Component:
    """Premium preview placeholder - institutional style upsell."""
    # Convert label to premium preview style
    premium_title = rx.cond(
        rx.Var.create(label == "SIDEBAR AD"),
        "Advanced Analytics",
        rx.cond(
            rx.Var.create(label == "CONTENT AD"),
            "Institutional Insight",
            "Premium Feature"
        )
    )

    return rx.box(
        rx.vstack(
            # Lock icon
            rx.box(
                rx.icon("lock", size=16, color="#5FA8FF"),
                padding="8px",
                background="rgba(95, 168, 255, 0.08)",
                border_radius="8px",
            ),
            # Premium feature name
            rx.text(
                premium_title,
                font_size="12px",
                font_weight="500",
                color=themed(LightTheme.text_primary, "#E6E9F0"),
            ),
            # Description
            rx.text(
                "Unlock with Pro",
                font_size="10px",
                font_weight="400",
                color=themed(LightTheme.text_muted, "#6B7280"),
            ),
            # CTA button
            rx.box(
                rx.text(
                    "Learn More",
                    font_size="10px",
                    font_weight="500",
                    color="#5FA8FF",
                ),
                padding_x="12px",
                padding_y="4px",
                border="1px solid rgba(95, 168, 255, 0.3)",
                border_radius="4px",
                cursor="pointer",
                transition="all 0.1s ease",
                _hover={
                    "background": "rgba(95, 168, 255, 0.08)",
                    "border_color": "rgba(95, 168, 255, 0.5)",
                },
            ),
            spacing="2",
            align="center",
            justify="center",
        ),
        width=width,
        height=height,
        background=themed(
            "rgba(255,255,255,0.4)",
            "rgba(255,255,255,0.01)"
        ),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.04)", "rgba(255,255,255,0.03)"),
        border_radius="8px",
        display="flex",
        align_items="center",
        justify_content="center",
    )


def report_type_pill(label: str, trader_key: str, icon_name: str, color: str) -> rx.Component:
    """Enhanced pill-style report type toggle button."""
    is_active = State.selected_trader == trader_key

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=16),
                padding="4px",
                border_radius="6px",
                background=rx.cond(is_active, f"{color}20", "transparent"),
            ),
            rx.text(label, font_size="13px", font_weight="500"),
            spacing="2",
            align="center",
        ),
        padding_x="18px",
        padding_y="10px",
        border_radius="10px",
        cursor="pointer",
        background=rx.cond(
            is_active,
            f"linear-gradient(135deg, {color}20, {color}10)",
            "transparent",
        ),
        border="1px solid",
        border_color=rx.cond(
            is_active,
            f"{color}50",
            themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
        ),
        color=rx.cond(
            is_active,
            color,
            themed(LightTheme.text_secondary, "#94a3b8"),
        ),
        box_shadow=rx.cond(
            is_active,
            f"0 4px 12px {color}25",
            "none",
        ),
        transition="all 0.2s ease",
        _hover={
            "border_color": f"{color}40",
            "background": f"{color}15",
            "color": color,
            "transform": "translateY(-1px)",
        },
        on_click=lambda: State.select_trader(trader_key),
    )


def legacy_trader_tabs() -> rx.Component:
    """Legacy COT trader tabs."""
    return rx.hstack(
        rx.tooltip(
            report_type_pill("Non-Commercial", "non_commercial", "briefcase", "#60a5fa"),
            content="Speculators & hedge funds - typically trend followers",
        ),
        rx.tooltip(
            report_type_pill("Commercial", "commercial", "building-2", "#10b981"),
            content="Hedgers - producers & consumers hedging price risk",
        ),
        rx.tooltip(
            report_type_pill("Non-Reportable", "non_reportable", "users", "#f59e0b"),
            content="Small traders below CFTC reporting thresholds",
        ),
        rx.tooltip(
            report_type_pill("All Traders", "all", "layers", "#8b5cf6"),
            content="Combined view of all trader categories",
        ),
        spacing="2",
        flex_wrap="wrap",
    )


def disaggregated_trader_tabs() -> rx.Component:
    """Disaggregated COT trader tabs for commodities."""
    return rx.hstack(
        rx.tooltip(
            report_type_pill("All Traders", "all", "layers", "#8b5cf6"),
            content="Combined view of all trader categories",
        ),
        rx.tooltip(
            report_type_pill("Producer/Merchant", "producer", "factory", "#60a5fa"),
            content="Producers, merchants, processors - physical commodity hedgers",
        ),
        rx.tooltip(
            report_type_pill("Swap Dealer", "swap_dealer", "repeat", "#10b981"),
            content="Swap dealers hedging OTC swap positions",
        ),
        rx.tooltip(
            report_type_pill("Managed Money", "managed_money", "trending-up", "#f59e0b"),
            content="CTAs, CPOs, and hedge funds - managed futures",
        ),
        rx.tooltip(
            report_type_pill("Other Reportable", "other", "users", "#a855f7"),
            content="Other reportable traders not classified above",
        ),
        spacing="2",
        flex_wrap="wrap",
    )


def tff_trader_tabs() -> rx.Component:
    """TFF (Traders in Financial Futures) trader tabs."""
    return rx.hstack(
        rx.tooltip(
            report_type_pill("All Traders", "all", "layers", "#8b5cf6"),
            content="Combined view of all trader categories",
        ),
        rx.tooltip(
            report_type_pill("Dealer", "dealer", "building", "#60a5fa"),
            content="Sell-side dealers - banks and broker-dealers",
        ),
        rx.tooltip(
            report_type_pill("Asset Manager", "asset_manager", "briefcase", "#10b981"),
            content="Institutional investors - pension funds, insurance, endowments",
        ),
        rx.tooltip(
            report_type_pill("Leveraged Funds", "leveraged", "zap", "#f59e0b"),
            content="Hedge funds and other leveraged money managers",
        ),
        rx.tooltip(
            report_type_pill("Other Reportable", "other", "users", "#a855f7"),
            content="Other reportable financial traders",
        ),
        spacing="2",
        flex_wrap="wrap",
    )


def trader_tabs() -> rx.Component:
    """Pill-style trader type toggle group - dynamically changes based on report type."""
    return rx.box(
        rx.cond(
            State.report_type == "legacy",
            legacy_trader_tabs(),
            rx.cond(
                State.report_type == "disaggregated",
                disaggregated_trader_tabs(),
                tff_trader_tabs(),  # TFF is the remaining option
            ),
        ),
        padding="6px",
        background=themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.02)"),
        border_radius="14px",
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
    )


def circular_gauge() -> rx.Component:
    """Primary Interpretation Block + Horizontal Percentile Bar - institutional style."""
    return rx.box(
        rx.vstack(
            # ========================================
            # PRIMARY INTERPRETATION (Most important element - visual anchor)
            # ========================================
            rx.vstack(
                # Headline - dominant visual anchor (~26px, was 22px, ~18% larger)
                rx.text(
                    rx.cond(
                        State.is_net_long,
                        State.selected_name + " Positioning: Skewed Long",
                        State.selected_name + " Positioning: Skewed Short"
                    ),
                    font_size="26px",
                    font_weight="600",
                    color=themed(LightTheme.text_primary, "#E6E9F0"),
                    text_align="center",
                    line_height="1.25",
                ),
                # Supporting interpretation text
                rx.text(
                    State.gauge_trader_label + rx.cond(
                        State.is_net_long,
                        " are positioned longer than typical historical levels.",
                        " are positioned shorter than typical historical levels."
                    ),
                    font_size="13px",
                    font_weight="400",
                    color=themed(LightTheme.text_secondary, "#9AA3B2"),
                    text_align="center",
                    line_height="1.5",
                    padding_top="10px",
                ),
                spacing="0",
                width="100%",
                margin_top="8px",
                margin_bottom="24px",
            ),

            # ========================================
            # TRADER SELECTOR - Minimal pills
            # ========================================
            rx.hstack(
                # Trader 1 pill
                rx.box(
                    rx.text(State.trader1_short, font_size="11px", font_weight="500"),
                    padding_x="12px",
                    padding_y="6px",
                    background=rx.cond(
                        State.gauge_trader_index == 1,
                        "#5FA8FF",
                        "transparent"
                    ),
                    color=rx.cond(
                        State.gauge_trader_index == 1,
                        "#0B0F17",
                        themed(LightTheme.text_secondary, "#9AA3B2")
                    ),
                    border="1px solid",
                    border_color=rx.cond(
                        State.gauge_trader_index == 1,
                        "transparent",
                        themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.08)")
                    ),
                    border_radius="4px",
                    cursor="pointer",
                    on_click=lambda: State.set_gauge_trader_index(1),
                    _hover={"background": rx.cond(State.gauge_trader_index == 1, "#5FA8FF", "rgba(255,255,255,0.04)")},
                    transition="all 0.1s ease",
                ),
                # Trader 2 pill
                rx.box(
                    rx.text(State.trader2_short, font_size="11px", font_weight="500"),
                    padding_x="12px",
                    padding_y="6px",
                    background=rx.cond(
                        State.gauge_trader_index == 2,
                        "#5FA8FF",
                        "transparent"
                    ),
                    color=rx.cond(
                        State.gauge_trader_index == 2,
                        "#0B0F17",
                        themed(LightTheme.text_secondary, "#9AA3B2")
                    ),
                    border="1px solid",
                    border_color=rx.cond(
                        State.gauge_trader_index == 2,
                        "transparent",
                        themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.08)")
                    ),
                    border_radius="4px",
                    cursor="pointer",
                    on_click=lambda: State.set_gauge_trader_index(2),
                    _hover={"background": rx.cond(State.gauge_trader_index == 2, "#5FA8FF", "rgba(255,255,255,0.04)")},
                    transition="all 0.1s ease",
                ),
                # Trader 3 pill
                rx.box(
                    rx.text(State.trader3_short, font_size="11px", font_weight="500"),
                    padding_x="12px",
                    padding_y="6px",
                    background=rx.cond(
                        State.gauge_trader_index == 3,
                        "#5FA8FF",
                        "transparent"
                    ),
                    color=rx.cond(
                        State.gauge_trader_index == 3,
                        "#0B0F17",
                        themed(LightTheme.text_secondary, "#9AA3B2")
                    ),
                    border="1px solid",
                    border_color=rx.cond(
                        State.gauge_trader_index == 3,
                        "transparent",
                        themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.08)")
                    ),
                    border_radius="4px",
                    cursor="pointer",
                    on_click=lambda: State.set_gauge_trader_index(3),
                    _hover={"background": rx.cond(State.gauge_trader_index == 3, "#5FA8FF", "rgba(255,255,255,0.04)")},
                    transition="all 0.1s ease",
                ),
                # Trader 4 pill (only for disaggregated/TFF)
                rx.cond(
                    State.has_trader4,
                    rx.box(
                        rx.text(State.trader4_short, font_size="11px", font_weight="500"),
                        padding_x="12px",
                        padding_y="6px",
                        background=rx.cond(
                            State.gauge_trader_index == 4,
                            "#5FA8FF",
                            "transparent"
                        ),
                        color=rx.cond(
                            State.gauge_trader_index == 4,
                            "#0B0F17",
                            themed(LightTheme.text_secondary, "#9AA3B2")
                        ),
                        border="1px solid",
                        border_color=rx.cond(
                            State.gauge_trader_index == 4,
                            "transparent",
                            themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.08)")
                        ),
                        border_radius="4px",
                        cursor="pointer",
                        on_click=lambda: State.set_gauge_trader_index(4),
                        _hover={"background": rx.cond(State.gauge_trader_index == 4, "#5FA8FF", "rgba(255,255,255,0.04)")},
                        transition="all 0.1s ease",
                    ),
                    rx.fragment(),
                ),
                spacing="2",
                padding_y="12px",
                justify="center",
            ),

            # ========================================
            # HORIZONTAL PERCENTILE BAR
            # ========================================
            rx.vstack(
                # Labels - institutional terminology
                rx.hstack(
                    rx.text(
                        "BEARISH",
                        font_size="9px",
                        font_weight="500",
                        letter_spacing="0.04em",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                    ),
                    rx.spacer(),
                    rx.text(
                        "BULLISH",
                        font_size="9px",
                        font_weight="500",
                        letter_spacing="0.04em",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                    ),
                    width="100%",
                ),
                # The bar itself - muted gray track with accent indicator
                rx.box(
                    # Background track - muted gray
                    rx.box(
                        width="100%",
                        height="6px",
                        background="rgba(255,255,255,0.04)",
                        border_radius="3px",
                    ),
                    # Position indicator (dot) - uses accent color
                    rx.box(
                        width="12px",
                        height="12px",
                        background=rx.cond(
                            State.is_net_long,
                            "#4CAF91",  # Muted green
                            "#D06C6C",  # Muted red
                        ),
                        border_radius="50%",
                        position="absolute",
                        top="-3px",
                        left=((State.net_position_pct + 100) / 2).to(str) + "%",
                        transform="translateX(-50%)",
                        box_shadow="0 0 0 2px rgba(11, 15, 23, 0.8)",
                        transition="left 0.3s ease",
                    ),
                    # Center line (neutral)
                    rx.box(
                        width="1px",
                        height="10px",
                        background="rgba(255,255,255,0.15)",
                        position="absolute",
                        top="-2px",
                        left="50%",
                        transform="translateX(-50%)",
                    ),
                    position="relative",
                    width="100%",
                    height="6px",
                ),
                # Percentile rank display - rank language primary, decimal secondary
                rx.vstack(
                    # Primary: Rank language (e.g., "Bottom 10% of historical positioning")
                    rx.text(
                        rx.cond(
                            State.net_position_pct < 0,
                            # Negative (short) - use bottom percentile
                            rx.cond(
                                (State.net_position_pct + 100) / 2 <= 10,
                                "Bottom 10% of historical positioning",
                                rx.cond(
                                    (State.net_position_pct + 100) / 2 <= 25,
                                    "Bottom 25% of historical positioning",
                                    rx.cond(
                                        (State.net_position_pct + 100) / 2 <= 40,
                                        "Below median positioning",
                                        "Near median positioning"
                                    )
                                )
                            ),
                            # Positive (long) - use top percentile
                            rx.cond(
                                (State.net_position_pct + 100) / 2 >= 90,
                                "Top 10% of historical positioning",
                                rx.cond(
                                    (State.net_position_pct + 100) / 2 >= 75,
                                    "Top 25% of historical positioning",
                                    rx.cond(
                                        (State.net_position_pct + 100) / 2 >= 60,
                                        "Above median positioning",
                                        "Near median positioning"
                                    )
                                )
                            )
                        ),
                        font_size="12px",
                        font_weight="500",
                        color=themed(LightTheme.text_secondary, "#9AA3B2"),
                        text_align="center",
                    ),
                    # Secondary: Raw percentile value
                    rx.text(
                        "(" + ((State.net_position_pct + 100) / 2).to(int).to(str) + "th percentile)",
                        font_size="10px",
                        font_weight="400",
                        font_family='"JetBrains Mono", monospace',
                        color=themed(LightTheme.text_muted, "#6B7280"),
                        text_align="center",
                    ),
                    spacing="1",
                    padding_top="8px",
                ),
                spacing="2",
                width="100%",
                padding_y="12px",
            ),

            # ========================================
            # SUPPORTING DATA - Long/Short breakdown
            # ========================================
            rx.hstack(
                rx.vstack(
                    rx.text(
                        State.total_long_display,
                        font_size="15px",
                        font_weight="500",
                        font_family='"JetBrains Mono", monospace',
                        color="#4CAF91",
                    ),
                    rx.text(
                        "LONG",
                        font_size="9px",
                        font_weight="500",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                        letter_spacing="0.04em",
                    ),
                    spacing="0",
                    align="center",
                ),
                rx.box(
                    width="1px",
                    height="32px",
                    background=themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.04)"),
                ),
                rx.vstack(
                    rx.text(
                        State.total_short_display,
                        font_size="15px",
                        font_weight="500",
                        font_family='"JetBrains Mono", monospace',
                        color="#D06C6C",
                    ),
                    rx.text(
                        "SHORT",
                        font_size="9px",
                        font_weight="500",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                        letter_spacing="0.04em",
                    ),
                    spacing="0",
                    align="center",
                ),
                spacing="8",
                align="center",
                justify="center",
                width="100%",
                padding_top="8px",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        padding="24px",
        background=themed(
            "rgba(255,255,255,0.8)",
            "rgba(255,255,255,0.015)"  # Very subtle background
        ),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.04)"),  # Nearly invisible
        border_radius="12px",
        min_width="320px",
        transition="all 0.1s ease",
        _hover={
            "border_color": themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.06)"),
        },
    )


def metric_card_clean(
    label: str,
    value: rx.Var[str],
    change: rx.Var,
    change_positive: rx.Var[bool],
    color: str = "#64748B",
    accent_color: str = None,
) -> rx.Component:
    """
    Clean metric card - matches reference design exactly.

    Hierarchy:
    1. Label (small, muted, uppercase) with subtle accent
    2. Value (large, dominant)
    3. WoW change (color-coded)

    Color semantics:
    - Blue (#60A5FA): Non-Commercial (speculators/momentum)
    - Red (#F87171): Commercial (hedgers)
    - Green (#34D399): Non-Reportable (retail)
    - Gray: Open Interest (neutral)
    """
    # Use accent_color for the left border accent, fallback to color
    border_accent = accent_color if accent_color else color

    return rx.box(
        rx.hstack(
            # Left accent bar - reinforces color semantics
            rx.box(
                width="3px",
                height="100%",
                min_height="100px",
                background=border_accent,
                border_radius="2px",
                opacity="0.6",
            ),
            rx.vstack(
                # Label - small, muted, uppercase
                rx.text(
                    label.upper() if isinstance(label, str) else label,
                    font_size="11px",
                    font_weight="500",
                    letter_spacing="0.05em",
                    color=themed(LightTheme.text_muted, "#6B7280"),
                ),
                # Value - large, dominant
                rx.text(
                    value,
                    font_size="28px",
                    font_weight="600",
                    font_family='"JetBrains Mono", monospace',
                    color=color,
                    line_height="1.1",
                    margin_top="8px",
                ),
                # WoW change - color-coded
                rx.hstack(
                    rx.icon(
                        rx.cond(change_positive, "arrow-up", "arrow-down"),
                        size=14,
                        color=rx.cond(change_positive, "#10B981", "#EF4444"),
                    ),
                    rx.text(
                        rx.cond(change_positive, "+", "") + change.to(str) + "%",
                        font_size="14px",
                        font_weight="500",
                        font_family='"JetBrains Mono", monospace',
                        color=rx.cond(change_positive, "#10B981", "#EF4444"),
                    ),
                    rx.text(
                        "WoW",
                        font_size="11px",
                        font_weight="400",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                        margin_left="4px",
                    ),
                    spacing="1",
                    align="center",
                    margin_top="8px",
                ),
                spacing="0",
                align="start",
                width="100%",
            ),
            spacing="4",
            align="stretch",
            width="100%",
        ),
        padding="16px 20px",
        background=themed("rgba(255,255,255,0.8)", "rgba(255,255,255,0.02)"),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.06)"),
        border_radius="12px",
        width="100%",
        min_height="130px",
        box_shadow=themed(
            "0 2px 8px rgba(0, 0, 0, 0.06)",
            "0 2px 8px rgba(0, 0, 0, 0.3)"
        ),
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        cursor="default",
        _hover={
            "border_color": themed("rgba(0,0,0,0.12)", "rgba(255,255,255,0.12)"),
            "box_shadow": themed(
                "0 8px 24px rgba(0,0,0,0.12)",
                "0 8px 24px rgba(0,0,0,0.4)"
            ),
            "transform": "translateY(-4px)",
            "background": themed("rgba(255,255,255,0.95)", "rgba(255,255,255,0.04)"),
        },
    )


def positioning_summary_card() -> rx.Component:
    """
    Positioning Summary Card - LEFT COLUMN anchor.

    The "lead paragraph" of the page - answers "What's the positioning story?"

    Design principles:
    - More authoritative with larger title
    - Subtle left accent bar for visual weight
    - This is the interpretation engine
    """
    return rx.box(
        rx.hstack(
            # Left accent bar - gives visual authority
            rx.box(
                width="4px",
                height="100%",
                min_height="280px",
                background=rx.cond(
                    State.is_net_long,
                    "linear-gradient(180deg, #10B981 0%, #059669 100%)",
                    "linear-gradient(180deg, #EF4444 0%, #DC2626 100%)"
                ),
                border_radius="2px",
            ),
            rx.vstack(
                # Title with positioning direction - LARGER for authority
                rx.text(
                    rx.cond(
                        State.is_net_long,
                        State.selected_name + " Positioning: Skewed Long",
                        State.selected_name + " Positioning: Skewed Short"
                    ),
                    font_size="24px",
                    font_weight="600",
                    color=themed(LightTheme.text_primary, "#E6E9F0"),
                    line_height="1.25",
                ),
                # Short explanation
                rx.text(
                    State.gauge_trader_label + rx.cond(
                        State.is_net_long,
                        " are positioned longer than typical historical levels.",
                        " are positioned shorter than typical historical levels."
                    ),
                    font_size="14px",
                    font_weight="400",
                    color=themed(LightTheme.text_secondary, "#9AA3B2"),
                    line_height="1.5",
                    margin_top="8px",
                ),

                # Participant toggles with semantic colors
                rx.hstack(
                    # Trader 1 pill (Non-Commercial / Blue)
                    rx.box(
                        rx.text(State.trader1_short, font_size="12px", font_weight="500"),
                        padding_x="14px",
                        padding_y="8px",
                        background=rx.cond(
                            State.gauge_trader_index == 1,
                            "#60A5FA",
                            "transparent"
                        ),
                        color=rx.cond(
                            State.gauge_trader_index == 1,
                            "#0B0F17",
                            themed(LightTheme.text_secondary, "#9AA3B2")
                        ),
                        border="1px solid",
                        border_color=rx.cond(
                            State.gauge_trader_index == 1,
                            "transparent",
                            themed("rgba(0,0,0,0.1)", "rgba(96, 165, 250, 0.3)")
                        ),
                        border_radius="6px",
                        cursor="pointer",
                        on_click=lambda: State.set_gauge_trader_index(1),
                        _hover={"background": rx.cond(State.gauge_trader_index == 1, "#60A5FA", "rgba(96, 165, 250, 0.1)")},
                        transition="all 0.1s ease",
                ),
                # Trader 2 pill (Commercial / Red)
                rx.box(
                    rx.text(State.trader2_short, font_size="12px", font_weight="500"),
                    padding_x="14px",
                    padding_y="8px",
                    background=rx.cond(
                        State.gauge_trader_index == 2,
                        "#F87171",
                        "transparent"
                    ),
                    color=rx.cond(
                        State.gauge_trader_index == 2,
                        "#0B0F17",
                        themed(LightTheme.text_secondary, "#9AA3B2")
                    ),
                    border="1px solid",
                    border_color=rx.cond(
                        State.gauge_trader_index == 2,
                        "transparent",
                        themed("rgba(0,0,0,0.1)", "rgba(248, 113, 113, 0.3)")
                    ),
                    border_radius="6px",
                    cursor="pointer",
                    on_click=lambda: State.set_gauge_trader_index(2),
                    _hover={"background": rx.cond(State.gauge_trader_index == 2, "#F87171", "rgba(248, 113, 113, 0.1)")},
                    transition="all 0.1s ease",
                ),
                # Trader 3 pill (Non-Reportable / Green)
                rx.box(
                    rx.text(State.trader3_short, font_size="12px", font_weight="500"),
                    padding_x="14px",
                    padding_y="8px",
                    background=rx.cond(
                        State.gauge_trader_index == 3,
                        "#34D399",
                        "transparent"
                    ),
                    color=rx.cond(
                        State.gauge_trader_index == 3,
                        "#0B0F17",
                        themed(LightTheme.text_secondary, "#9AA3B2")
                    ),
                    border="1px solid",
                    border_color=rx.cond(
                        State.gauge_trader_index == 3,
                        "transparent",
                        themed("rgba(0,0,0,0.1)", "rgba(52, 211, 153, 0.3)")
                    ),
                    border_radius="6px",
                    cursor="pointer",
                    on_click=lambda: State.set_gauge_trader_index(3),
                    _hover={"background": rx.cond(State.gauge_trader_index == 3, "#34D399", "rgba(52, 211, 153, 0.1)")},
                    transition="all 0.1s ease",
                ),
                # Trader 4 pill (Other / Purple - for disaggregated/TFF)
                rx.cond(
                    State.has_trader4,
                    rx.box(
                        rx.text(State.trader4_short, font_size="12px", font_weight="500"),
                        padding_x="14px",
                        padding_y="8px",
                        background=rx.cond(
                            State.gauge_trader_index == 4,
                            "#A78BFA",
                            "transparent"
                        ),
                        color=rx.cond(
                            State.gauge_trader_index == 4,
                            "#0B0F17",
                            themed(LightTheme.text_secondary, "#9AA3B2")
                        ),
                        border="1px solid",
                        border_color=rx.cond(
                            State.gauge_trader_index == 4,
                            "transparent",
                            themed("rgba(0,0,0,0.1)", "rgba(167, 139, 250, 0.3)")
                        ),
                        border_radius="6px",
                        cursor="pointer",
                        on_click=lambda: State.set_gauge_trader_index(4),
                        _hover={"background": rx.cond(State.gauge_trader_index == 4, "#A78BFA", "rgba(167, 139, 250, 0.1)")},
                        transition="all 0.1s ease",
                    ),
                    rx.fragment(),
                ),
                spacing="2",
                margin_top="24px",
                flex_wrap="wrap",
            ),

            # Extreme positioning scale
            rx.vstack(
                # Labels
                rx.hstack(
                    rx.text(
                        "Extreme Short",
                        font_size="10px",
                        font_weight="500",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                    ),
                    rx.spacer(),
                    rx.text(
                        "Extreme Long",
                        font_size="10px",
                        font_weight="500",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                    ),
                    width="100%",
                ),
                # The bar
                rx.box(
                    # Background track
                    rx.box(
                        width="100%",
                        height="8px",
                        background="linear-gradient(90deg, #EF4444 0%, #6B7280 50%, #10B981 100%)",
                        border_radius="4px",
                        opacity="0.3",
                    ),
                    # Position indicator
                    rx.box(
                        width="16px",
                        height="16px",
                        background=rx.cond(
                            State.is_net_long,
                            "#10B981",
                            "#EF4444",
                        ),
                        border_radius="50%",
                        position="absolute",
                        top="-4px",
                        left=((State.net_position_pct + 100) / 2).to(str) + "%",
                        transform="translateX(-50%)",
                        box_shadow="0 2px 8px rgba(0,0,0,0.3)",
                        border="2px solid",
                        border_color=themed("white", "#1a1a2e"),
                        transition="left 0.3s ease",
                    ),
                    # Center marker
                    rx.box(
                        width="2px",
                        height="12px",
                        background="rgba(255,255,255,0.3)",
                        position="absolute",
                        top="-2px",
                        left="50%",
                        transform="translateX(-50%)",
                    ),
                    position="relative",
                    width="100%",
                    height="8px",
                    margin_top="8px",
                ),
                spacing="1",
                width="100%",
                margin_top="24px",
            ),

            # Long vs Short visual bar - percentages add to 100%
            rx.vstack(
                # Visual positioning bar
                rx.hstack(
                    # Long segment
                    rx.box(
                        rx.vstack(
                            rx.text(
                                State.long_pct_display,
                                font_size=["18px", "20px", "22px", "24px"],  # Bigger percentage
                                font_weight="800",
                                font_family='"JetBrains Mono", monospace',
                                color="white",
                                text_shadow="0 1px 2px rgba(0,0,0,0.2)",
                            ),
                            rx.text(
                                State.total_long_display,
                                font_size=["10px", "11px", "12px", "12px"],
                                font_weight="500",
                                color="rgba(255,255,255,0.85)",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        width=State.long_pct.to(str) + "%",
                        min_width="70px",
                        background="linear-gradient(90deg, #059669 0%, #10B981 100%)",
                        padding="12px 14px",
                        border_radius="8px 0 0 8px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        transition="width 0.3s ease",
                        box_shadow="inset 0 1px 0 rgba(255,255,255,0.15)",
                    ),
                    # Short segment
                    rx.box(
                        rx.vstack(
                            rx.text(
                                State.short_pct_display,
                                font_size=["18px", "20px", "22px", "24px"],  # Bigger percentage
                                font_weight="800",
                                font_family='"JetBrains Mono", monospace',
                                color="white",
                                text_shadow="0 1px 2px rgba(0,0,0,0.2)",
                            ),
                            rx.text(
                                State.total_short_display,
                                font_size=["10px", "11px", "12px", "12px"],
                                font_weight="500",
                                color="rgba(255,255,255,0.85)",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        width=State.short_pct.to(str) + "%",
                        min_width="70px",
                        background="linear-gradient(90deg, #DC2626 0%, #EF4444 100%)",
                        padding="12px 14px",
                        border_radius="0 8px 8px 0",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        transition="width 0.3s ease",
                        box_shadow="inset 0 1px 0 rgba(255,255,255,0.15)",
                    ),
                    spacing="0",
                    width="100%",
                ),
                # Labels below bar
                rx.hstack(
                    rx.text(
                        "LONG",
                        font_size="10px",
                        font_weight="600",
                        color="#10B981",
                        letter_spacing="0.05em",
                    ),
                    rx.spacer(),
                    rx.text(
                        "SHORT",
                        font_size="10px",
                        font_weight="600",
                        color="#EF4444",
                        letter_spacing="0.05em",
                    ),
                    width="100%",
                    margin_top="8px",
                ),
                spacing="0",
                width="100%",
                margin_top="24px",
                padding_top="16px",
                border_top="1px solid",
                border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.06)"),
            ),
            spacing="0",
            align="start",
            width="100%",
        ),
        spacing="4",
        align="stretch",
        width="100%",
    ),
    padding="20px 24px",
        background=themed("rgba(255,255,255,0.8)", "rgba(255,255,255,0.025)"),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
        border_radius="12px",
        width="100%",
        height="100%",
        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "border_color": themed("rgba(0,0,0,0.12)", "rgba(255,255,255,0.12)"),
            "box_shadow": themed(
                "0 8px 24px rgba(0,0,0,0.08)",
                "0 8px 24px rgba(0,0,0,0.3)"
            ),
            "transform": "translateY(-2px)",
        },
    )


def quadrant_metrics_grid() -> rx.Component:
    """
    2x2 Quadrant Metrics Grid - RIGHT COLUMN.

    Four clearly separated cards with semantic color accents:
    - Open Interest (gray/neutral) - system-level metric
    - Non-Commercial Net (blue) - speculators/momentum
    - Commercial Net (red) - hedgers
    - Non-Reportable Net (green) - retail flow
    """
    return rx.box(
        # Open Interest - top left (gray/neutral)
        metric_card_clean(
            label="Open Interest",
            value=State.oi_display,
            change=State.oi_change_pct,
            change_positive=State.oi_change_positive,
            color=themed(LightTheme.text_primary, "#E6E9F0"),
            accent_color="#64748B",  # Slate gray
        ),
        # Non-Commercial Net - top right (blue - speculators/momentum)
        metric_card_clean(
            label=State.trader1_label + " Net",
            value=State.trader1_net_display,
            change=State.trader1_change_pct,
            change_positive=State.trader1_change_positive,
            color="#60A5FA",
            accent_color="#60A5FA",  # Blue - speculators
        ),
        # Commercial Net - bottom left (red - hedgers)
        metric_card_clean(
            label=State.trader2_label + " Net",
            value=State.trader2_net_display,
            change=State.trader2_change_pct,
            change_positive=State.trader2_change_positive,
            color="#F87171",
            accent_color="#F87171",  # Red - hedgers
        ),
        # Non-Reportable Net - bottom right (green - retail)
        metric_card_clean(
            label=State.trader3_label + " Net",
            value=State.trader3_net_display,
            change=State.trader3_change_pct,
            change_positive=State.trader3_change_positive,
            color="#34D399",
            accent_color="#34D399",  # Green - retail
        ),
        display="grid",
        style={
            "grid_template_columns": "1fr 1fr",
            "grid_template_rows": "1fr 1fr",
        },
        gap="16px",
        width="100%",
        height="100%",
    )


def insight_card(
    icon_name: str,
    title: str,
    value: rx.Var[str],
    change: rx.Var,
    change_positive: rx.Var[bool],
    accent_color: str,
    participant_type: str,
    interpretation: rx.Var[str] = None,
) -> rx.Component:
    """Legacy insight_card - kept for compatibility but simplified."""
    return metric_card_clean(
        label=title,
        value=value,
        change=change,
        change_positive=change_positive,
        color=accent_color,
    )


def metric_card(
    icon: str,
    title: str,
    value: rx.Var[str],
    change: rx.Var,
    change_positive: rx.Var[bool],
    border_color: str,
    glow_color: str,
) -> rx.Component:
    """Legacy metric card - wrapper for backward compatibility."""
    # Map old params to new insight_card
    # Determine participant type from title/icon
    participant_type = "oi"
    if "Commercial" in str(title) or icon == "🏢":
        participant_type = "commercial"
    elif "Non-Commercial" in str(title) or "Speculator" in str(title) or icon == "📈":
        participant_type = "speculator"
    elif "Non-Reportable" in str(title) or "Retail" in str(title) or icon == "👥":
        participant_type = "retail"

    return insight_card(
        icon_name=icon,
        title=title,
        value=value,
        change=change,
        change_positive=change_positive,
        accent_color=glow_color,
        participant_type=participant_type,
    )


def chart_control_btn(icon_name: str, on_click, is_active) -> rx.Component:
    """Chart control button."""
    return rx.box(
        rx.icon(
            icon_name,
            size=18,
            color=rx.cond(
                is_active if isinstance(is_active, rx.Var) else rx.Var.create(is_active),
                themed(LightTheme.accent_blue, "#60a5fa"),
                themed(LightTheme.text_muted, "#64748b"),
            ),
        ),
        padding="8px",
        border_radius="6px",
        cursor="pointer",
        background=rx.cond(
            is_active if isinstance(is_active, rx.Var) else rx.Var.create(is_active),
            themed("rgba(59,130,246,0.1)", "rgba(96,165,250,0.1)"),
            "transparent",
        ),
        _hover={
            "background": themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
        },
        on_click=on_click,
    )


def zoom_btn(label: str, level: int, on_click_handler) -> rx.Component:
    """Zoom level button with clear active state."""
    is_active = State.zoom_level == level

    return rx.box(
        rx.text(
            label,
            font_size="12px",
            font_weight=rx.cond(is_active, "600", "500"),
            color=rx.cond(
                is_active,
                "#ffffff",
                themed(LightTheme.text_muted, "#94a3b8"),
            ),
        ),
        padding_x="14px",
        padding_y="6px",
        border_radius="6px",
        cursor="pointer",
        background=rx.cond(
            is_active,
            "linear-gradient(135deg, #8b5cf6, #60a5fa)",
            "transparent",
        ),
        box_shadow=rx.cond(
            is_active,
            "0 2px 8px rgba(139, 92, 246, 0.3)",
            "none",
        ),
        transition="all 0.2s ease",
        _hover={
            "background": rx.cond(
                is_active,
                "linear-gradient(135deg, #7c3aed, #3b82f6)",
                themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.08)"),
            ),
        },
        on_click=on_click_handler,
    )


def legend_toggle_btn(label: str, color: str, is_visible: rx.Var[bool], on_click) -> rx.Component:
    """Interactive legend button to toggle chart series visibility."""
    return rx.box(
        rx.hstack(
            rx.box(
                width="10px",
                height="10px",
                border_radius="2px",
                background=rx.cond(is_visible, color, "#475569"),
                transition="all 0.2s ease",
            ),
            rx.text(
                label,
                font_size="12px",
                font_weight="500",
                color=rx.cond(is_visible, "#e2e8f0", "#64748b"),
                transition="all 0.2s ease",
            ),
            spacing="2",
            align="center",
        ),
        padding_x="12px",
        padding_y="6px",
        border_radius="6px",
        cursor="pointer",
        background=rx.cond(is_visible, f"{color}15", "transparent"),
        border="1px solid",
        border_color=rx.cond(is_visible, f"{color}30", "transparent"),
        transition="all 0.2s ease",
        _hover={
            "background": f"{color}20",
        },
        on_click=on_click,
    )


def chart_section() -> rx.Component:
    """Chart section - institutional style, clean data visualization."""
    return rx.box(
        rx.vstack(
            # Contextual insight sentence - one-liner above chart
            rx.text(
                rx.cond(
                    State.chart_data_view == "position",
                    # Position view insight
                    State.gauge_trader_label + " net positioning " + rx.cond(
                        State.is_net_long,
                        "has increased over recent periods, reflecting growing bullish sentiment.",
                        "has declined over recent periods, reflecting growing bearish sentiment."
                    ),
                    # Percentile view insight
                    "Percentile analysis shows where current positioning ranks against historical data."
                ),
                font_size="13px",
                font_weight="400",
                color=themed(LightTheme.text_secondary, "#9AA3B2"),
                line_height="1.5",
                padding_bottom="12px",
            ),
            # Chart header with controls
            rx.hstack(
                rx.hstack(
                    rx.text(
                        rx.cond(
                            State.chart_data_view == "position",
                            "HISTORICAL POSITIONING",
                            "PERCENTILE ANALYSIS",
                        ),
                        font_size="11px",
                        font_weight="500",
                        letter_spacing="0.04em",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                    ),
                    spacing="2",
                    align="center",
                ),
                # Chart data view toggle (Net Position vs Percentile) - Top Right position
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.hstack(
                                rx.text("Net Position", font_size="11px", font_weight="500"),
                                spacing="1",
                                align="center",
                            ),
                            padding_x="12px",
                            padding_y="5px",
                            border_radius="4px 0 0 4px",
                            cursor="pointer",
                            background=rx.cond(
                                State.chart_data_view == "position",
                                "#5FA8FF",
                                themed("rgba(0,0,0,0.02)", "rgba(255,255,255,0.02)"),
                            ),
                            color=rx.cond(
                                State.chart_data_view == "position",
                                "#0B0F17",
                                "#9AA3B2",
                            ),
                            border="1px solid",
                            border_color=rx.cond(
                                State.chart_data_view == "position",
                                "#5FA8FF",
                                themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.06)"),
                            ),
                            border_right="none",
                            transition="all 0.1s ease",
                            _hover={"background": rx.cond(State.chart_data_view == "position", "#5FA8FF", "rgba(255,255,255,0.04)")},
                            on_click=State.set_chart_data_view("position"),
                        ),
                        rx.box(
                            rx.hstack(
                                rx.text("Percentile", font_size="11px", font_weight="500"),
                                spacing="1",
                                align="center",
                            ),
                            padding_x="12px",
                            padding_y="5px",
                            border_radius="0 4px 4px 0",
                            cursor="pointer",
                            background=rx.cond(
                                State.chart_data_view == "percentile",
                                "#5FA8FF",
                                themed("rgba(0,0,0,0.02)", "rgba(255,255,255,0.02)"),
                            ),
                            color=rx.cond(
                                State.chart_data_view == "percentile",
                                "#0B0F17",
                                "#9AA3B2",
                            ),
                            border="1px solid",
                            border_color=rx.cond(
                                State.chart_data_view == "percentile",
                                "#5FA8FF",
                                themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.06)"),
                            ),
                            transition="all 0.1s ease",
                            _hover={"background": rx.cond(State.chart_data_view == "percentile", "#5FA8FF", "rgba(255,255,255,0.04)")},
                            on_click=State.set_chart_data_view("percentile"),
                        ),
                        spacing="0",
                    ),
                    margin_left="16px",
                ),
                rx.spacer(),
                # Chart type and zoom controls (only shown for position view)
                rx.cond(
                    State.chart_data_view == "position",
                    rx.hstack(
                        # % of OI Toggle
                        rx.tooltip(
                            rx.box(
                                rx.hstack(
                                    rx.text(
                                        rx.cond(State.show_percent_oi, "%", "#"),
                                        font_weight="600",
                                        font_size="13px",
                                    ),
                                    rx.text(
                                        rx.cond(State.show_percent_oi, "% of OI", "Contracts"),
                                        font_size="12px",
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                                padding_x="12px",
                                padding_y="6px",
                                border_radius="8px",
                                cursor="pointer",
                                background=rx.cond(
                                    State.show_percent_oi,
                                    "rgba(139, 92, 246, 0.2)",
                                    themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.03)"),
                                ),
                                border="1px solid",
                                border_color=rx.cond(
                                    State.show_percent_oi,
                                    "rgba(139, 92, 246, 0.5)",
                                    themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                                ),
                                color=rx.cond(State.show_percent_oi, "#a78bfa", "#94a3b8"),
                                transition="all 0.2s ease",
                                _hover={"background": "rgba(139, 92, 246, 0.15)"},
                                on_click=State.toggle_percent_oi,
                            ),
                            content="Toggle between absolute contracts and % of Open Interest",
                        ),
                        rx.box(
                            width="1px",
                            height="28px",
                            background=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                            margin_x="8px",
                        ),
                        # Chart type toggles
                        rx.box(
                            rx.hstack(
                                chart_control_btn("bar-chart-3", lambda: State.set_chart_type("bar"), State.chart_type == "bar"),
                                chart_control_btn("line-chart", lambda: State.set_chart_type("line"), State.chart_type == "line"),
                                spacing="1",
                            ),
                            padding="4px",
                            background=themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.03)"),
                            border_radius="8px",
                        ),
                        rx.box(
                            width="1px",
                            height="28px",
                            background=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                            margin_x="8px",
                        ),
                        # Time period selector with better styling
                        rx.box(
                            rx.hstack(
                                zoom_btn("1Y", 25, State.set_zoom_1y),
                                zoom_btn("2Y", 50, State.set_zoom_2y),
                                zoom_btn("3Y", 75, State.set_zoom_3y),
                                zoom_btn("ALL", 100, State.set_zoom_all),
                                spacing="1",
                            ),
                            padding="4px",
                            background=themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.03)"),
                            border_radius="8px",
                        ),
                        spacing="2",
                        align="center",
                        display=["none", "flex", "flex", "flex"],
                    ),
                    rx.fragment(),  # Empty fragment for percentile view (no controls needed)
                ),
                width="100%",
                align="center",
                padding="20px",
                padding_bottom="12px",
                flex_wrap="wrap",
                gap="12px",
            ),
            # Interactive legend row (different for position vs percentile view)
            rx.cond(
                State.chart_data_view == "position",
                # Net Position view: trader series toggles
                rx.hstack(
                    # Legend toggles
                    rx.hstack(
                        legend_toggle_btn(State.trader1_label, "#8b5cf6", State.show_nc_series, State.toggle_nc_series),
                        legend_toggle_btn(State.trader2_label, "#ef4444", State.show_comm_series, State.toggle_comm_series),
                        legend_toggle_btn(State.trader3_label, "#60a5fa", State.show_nr_series, State.toggle_nr_series),
                        # 4th trader toggle (only for disaggregated/TFF)
                        rx.cond(
                            State.has_trader4,
                            legend_toggle_btn(State.trader4_label, "#10b981", State.show_trader4_series, State.toggle_trader4_series),
                            rx.fragment(),
                        ),
                        spacing="2",
                    ),
                    rx.spacer(),
                    # Export button
                    rx.tooltip(
                        rx.box(
                            rx.hstack(
                                rx.icon("download", size=14),
                                rx.text("Export", font_size="12px", display=["none", "block", "block", "block"]),
                                spacing="1",
                                align="center",
                            ),
                            padding_x="10px",
                            padding_y="6px",
                            border_radius="6px",
                            cursor="pointer",
                            color="#94a3b8",
                            transition="all 0.2s ease",
                            _hover={
                                "background": themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
                                "color": "#e2e8f0",
                            },
                        ),
                        content="Export chart data",
                    ),
                    # Premium features: Z-Score and Velocity
                    rx.box(
                        width="1px",
                        height="24px",
                        background=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                        margin_x="8px",
                    ),
                    # Z-Score button (Coming soon)
                    rx.tooltip(
                        rx.box(
                            rx.hstack(
                                rx.icon("trending-up", size=14),
                                rx.text("Z-Score", font_size="12px", display=["none", "block", "block", "block"]),
                                spacing="1",
                                align="center",
                            ),
                            padding_x="10px",
                            padding_y="6px",
                            border_radius="6px",
                            cursor="not-allowed",
                            color="#64748b",
                            background="transparent",
                            border="1px solid",
                            border_color="rgba(255,255,255,0.06)",
                            opacity="0.6",
                            transition="all 0.1s ease",
                        ),
                        content="Coming soon",
                    ),
                    # Velocity button (Coming soon)
                    rx.tooltip(
                        rx.box(
                            rx.hstack(
                                rx.icon("activity", size=14),
                                rx.text("Velocity", font_size="12px", display=["none", "block", "block", "block"]),
                                spacing="1",
                                align="center",
                            ),
                            padding_x="10px",
                            padding_y="6px",
                            border_radius="6px",
                            cursor="not-allowed",
                            color="#64748b",
                            background="transparent",
                            border="1px solid",
                            border_color="rgba(255,255,255,0.06)",
                            opacity="0.6",
                            transition="all 0.1s ease",
                        ),
                        content="Coming soon",
                    ),
                    width="100%",
                    align="center",
                    padding_x="20px",
                    padding_bottom="8px",
                    flex_wrap="wrap",
                ),
                # Percentile view: trader type selector
                rx.hstack(
                    rx.text(
                        "Select Trader Type:",
                        font_size="13px",
                        color=themed(LightTheme.text_secondary, "#94a3b8"),
                        font_weight="500",
                    ),
                    rx.hstack(
                        # Non-Commercial / Managed Money pill
                        rx.box(
                            rx.text(State.trader1_short, font_size="12px", font_weight="600"),
                            padding_x="14px",
                            padding_y="6px",
                            border_radius="6px",
                            cursor="pointer",
                            background=rx.cond(
                                State.percentile_trader_type == "Non-Commercial",
                                "rgba(139, 92, 246, 0.25)",
                                themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                            ),
                            color=rx.cond(
                                State.percentile_trader_type == "Non-Commercial",
                                "#a78bfa",
                                "#64748b",
                            ),
                            border="1px solid",
                            border_color=rx.cond(
                                State.percentile_trader_type == "Non-Commercial",
                                "rgba(139, 92, 246, 0.5)",
                                themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                            ),
                            transition="all 0.2s ease",
                            _hover={"background": "rgba(139, 92, 246, 0.15)"},
                            on_click=State.set_percentile_trader_type("Non-Commercial"),
                        ),
                        # Commercial / Producer pill
                        rx.box(
                            rx.text(State.trader2_short, font_size="12px", font_weight="600"),
                            padding_x="14px",
                            padding_y="6px",
                            border_radius="6px",
                            cursor="pointer",
                            background=rx.cond(
                                State.percentile_trader_type == "Commercial",
                                "rgba(239, 68, 68, 0.25)",
                                themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                            ),
                            color=rx.cond(
                                State.percentile_trader_type == "Commercial",
                                "#f87171",
                                "#64748b",
                            ),
                            border="1px solid",
                            border_color=rx.cond(
                                State.percentile_trader_type == "Commercial",
                                "rgba(239, 68, 68, 0.5)",
                                themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                            ),
                            transition="all 0.2s ease",
                            _hover={"background": "rgba(239, 68, 68, 0.15)"},
                            on_click=State.set_percentile_trader_type("Commercial"),
                        ),
                        # Non-Reportable / Other pill
                        rx.box(
                            rx.text(State.trader3_short, font_size="12px", font_weight="600"),
                            padding_x="14px",
                            padding_y="6px",
                            border_radius="6px",
                            cursor="pointer",
                            background=rx.cond(
                                State.percentile_trader_type == "Non-Reportable",
                                "rgba(96, 165, 250, 0.25)",
                                themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                            ),
                            color=rx.cond(
                                State.percentile_trader_type == "Non-Reportable",
                                "#60a5fa",
                                "#64748b",
                            ),
                            border="1px solid",
                            border_color=rx.cond(
                                State.percentile_trader_type == "Non-Reportable",
                                "rgba(96, 165, 250, 0.5)",
                                themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                            ),
                            transition="all 0.2s ease",
                            _hover={"background": "rgba(96, 165, 250, 0.15)"},
                            on_click=State.set_percentile_trader_type("Non-Reportable"),
                        ),
                        spacing="2",
                    ),
                    # Lookback period selector
                    rx.hstack(
                        rx.text(
                            "Lookback:",
                            font_size="13px",
                            color=themed(LightTheme.text_secondary, "#94a3b8"),
                            font_weight="500",
                        ),
                        rx.hstack(
                            # 6 months
                            rx.box(
                                rx.text("6M", font_size="11px", font_weight="600"),
                                padding_x="10px",
                                padding_y="4px",
                                border_radius="4px",
                                cursor="pointer",
                                background=rx.cond(
                                    State.percentile_lookback == "6m",
                                    "rgba(139, 92, 246, 0.25)",
                                    themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                                ),
                                color=rx.cond(
                                    State.percentile_lookback == "6m",
                                    "#a78bfa",
                                    "#64748b",
                                ),
                                border="1px solid",
                                border_color=rx.cond(
                                    State.percentile_lookback == "6m",
                                    "rgba(139, 92, 246, 0.5)",
                                    themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                                ),
                                transition="all 0.2s ease",
                                _hover={"background": "rgba(139, 92, 246, 0.15)"},
                                on_click=State.set_percentile_lookback("6m"),
                            ),
                            # 1 year
                            rx.box(
                                rx.text("1Y", font_size="11px", font_weight="600"),
                                padding_x="10px",
                                padding_y="4px",
                                border_radius="4px",
                                cursor="pointer",
                                background=rx.cond(
                                    State.percentile_lookback == "1y",
                                    "rgba(139, 92, 246, 0.25)",
                                    themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                                ),
                                color=rx.cond(
                                    State.percentile_lookback == "1y",
                                    "#a78bfa",
                                    "#64748b",
                                ),
                                border="1px solid",
                                border_color=rx.cond(
                                    State.percentile_lookback == "1y",
                                    "rgba(139, 92, 246, 0.5)",
                                    themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                                ),
                                transition="all 0.2s ease",
                                _hover={"background": "rgba(139, 92, 246, 0.15)"},
                                on_click=State.set_percentile_lookback("1y"),
                            ),
                            # 2 years
                            rx.box(
                                rx.text("2Y", font_size="11px", font_weight="600"),
                                padding_x="10px",
                                padding_y="4px",
                                border_radius="4px",
                                cursor="pointer",
                                background=rx.cond(
                                    State.percentile_lookback == "2y",
                                    "rgba(139, 92, 246, 0.25)",
                                    themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                                ),
                                color=rx.cond(
                                    State.percentile_lookback == "2y",
                                    "#a78bfa",
                                    "#64748b",
                                ),
                                border="1px solid",
                                border_color=rx.cond(
                                    State.percentile_lookback == "2y",
                                    "rgba(139, 92, 246, 0.5)",
                                    themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                                ),
                                transition="all 0.2s ease",
                                _hover={"background": "rgba(139, 92, 246, 0.15)"},
                                on_click=State.set_percentile_lookback("2y"),
                            ),
                            # 3 years
                            rx.box(
                                rx.text("3Y", font_size="11px", font_weight="600"),
                                padding_x="10px",
                                padding_y="4px",
                                border_radius="4px",
                                cursor="pointer",
                                background=rx.cond(
                                    State.percentile_lookback == "3y",
                                    "rgba(139, 92, 246, 0.25)",
                                    themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
                                ),
                                color=rx.cond(
                                    State.percentile_lookback == "3y",
                                    "#a78bfa",
                                    "#64748b",
                                ),
                                border="1px solid",
                                border_color=rx.cond(
                                    State.percentile_lookback == "3y",
                                    "rgba(139, 92, 246, 0.5)",
                                    themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                                ),
                                transition="all 0.2s ease",
                                _hover={"background": "rgba(139, 92, 246, 0.15)"},
                                on_click=State.set_percentile_lookback("3y"),
                            ),
                            spacing="1",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    # Percentile legend info
                    rx.hstack(
                        rx.box(width="12px", height="12px", background="#10b981", border_radius="2px"),
                        rx.text("Bullish (>70%)", font_size="11px", color="#64748b"),
                        rx.box(width="12px", height="12px", background="#94a3b8", border_radius="2px", margin_left="12px"),
                        rx.text("Neutral", font_size="11px", color="#64748b"),
                        rx.box(width="12px", height="12px", background="#ef4444", border_radius="2px", margin_left="12px"),
                        rx.text("Bearish (<30%)", font_size="11px", color="#64748b"),
                        spacing="1",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    padding_x="20px",
                    padding_bottom="8px",
                    flex_wrap="wrap",
                    gap="12px",
                ),
            ),
            # Chart - Full width, responsive height (toggles between Net Position and Percentile)
            rx.box(
                rx.cond(
                    State.chart_data_view == "position",
                    # Net Position chart
                    rx.plotly(
                        data=State.plotly_fig,
                        use_resize_handler=True,
                        style={
                            "width": "100%",
                            "height": "100%",
                        },
                    ),
                    # Percentile Rank chart
                    rx.plotly(
                        data=State.percentile_chart_fig,
                        use_resize_handler=True,
                        style={
                            "width": "100%",
                            "height": "100%",
                        },
                    ),
                ),
                width="100%",
                # Responsive height: 300px mobile, 400px tablet, 450px desktop, 500px wide
                height=["300px", "350px", "450px", "500px"],
                min_height="280px",
            ),
            # Z-Score Panel (conditionally shown)
            rx.cond(
                State.show_zscore_panel,
                rx.box(
                    rx.vstack(
                        # Header with trader type selector
                        rx.hstack(
                            rx.hstack(
                                rx.icon("trending-up", size=20, color="#8b5cf6"),
                                rx.text("Z-Score Analysis", font_size="16px", font_weight="600", color="#e2e8f0"),
                                spacing="2",
                                align="center",
                            ),
                            rx.spacer(),
                            # Trader type selector pills
                            rx.hstack(
                                rx.box(
                                    rx.text("NC", font_size="11px", font_weight="600"),
                                    padding_x="10px",
                                    padding_y="4px",
                                    border_radius="6px",
                                    cursor="pointer",
                                    background=rx.cond(
                                        State.indicator_trader_type == "Non-Commercial",
                                        "rgba(139, 92, 246, 0.3)",
                                        "rgba(255,255,255,0.05)"
                                    ),
                                    color=rx.cond(
                                        State.indicator_trader_type == "Non-Commercial",
                                        "#a78bfa",
                                        "#64748b"
                                    ),
                                    border="1px solid",
                                    border_color=rx.cond(
                                        State.indicator_trader_type == "Non-Commercial",
                                        "rgba(139, 92, 246, 0.5)",
                                        "rgba(255,255,255,0.1)"
                                    ),
                                    on_click=lambda: State.set_indicator_trader_type("Non-Commercial"),
                                ),
                                rx.box(
                                    rx.text("COMM", font_size="11px", font_weight="600"),
                                    padding_x="10px",
                                    padding_y="4px",
                                    border_radius="6px",
                                    cursor="pointer",
                                    background=rx.cond(
                                        State.indicator_trader_type == "Commercial",
                                        "rgba(239, 68, 68, 0.3)",
                                        "rgba(255,255,255,0.05)"
                                    ),
                                    color=rx.cond(
                                        State.indicator_trader_type == "Commercial",
                                        "#f87171",
                                        "#64748b"
                                    ),
                                    border="1px solid",
                                    border_color=rx.cond(
                                        State.indicator_trader_type == "Commercial",
                                        "rgba(239, 68, 68, 0.5)",
                                        "rgba(255,255,255,0.1)"
                                    ),
                                    on_click=lambda: State.set_indicator_trader_type("Commercial"),
                                ),
                                rx.box(
                                    rx.text("NR", font_size="11px", font_weight="600"),
                                    padding_x="10px",
                                    padding_y="4px",
                                    border_radius="6px",
                                    cursor="pointer",
                                    background=rx.cond(
                                        State.indicator_trader_type == "Non-Reportable",
                                        "rgba(96, 165, 250, 0.3)",
                                        "rgba(255,255,255,0.05)"
                                    ),
                                    color=rx.cond(
                                        State.indicator_trader_type == "Non-Reportable",
                                        "#60a5fa",
                                        "#64748b"
                                    ),
                                    border="1px solid",
                                    border_color=rx.cond(
                                        State.indicator_trader_type == "Non-Reportable",
                                        "rgba(96, 165, 250, 0.5)",
                                        "rgba(255,255,255,0.1)"
                                    ),
                                    on_click=lambda: State.set_indicator_trader_type("Non-Reportable"),
                                ),
                                spacing="1",
                            ),
                            width="100%",
                            align="center",
                            margin_bottom="16px",
                        ),
                        # Main content
                        rx.hstack(
                            # Z-Score value display - BIGGER
                            rx.vstack(
                                rx.hstack(
                                    rx.text(
                                        State.zscore_data["z_score"],
                                        font_size="48px",
                                        font_weight="700",
                                        color=State.zscore_data["color"],
                                    ),
                                    rx.text("σ", font_size="24px", color="#94a3b8", margin_left="-4px", margin_top="12px"),
                                    align="start",
                                ),
                                rx.box(
                                    rx.text(
                                        State.zscore_data["interpretation"],
                                        font_size="14px",
                                        font_weight="600",
                                        color=State.zscore_data["color"],
                                    ),
                                    padding_x="12px",
                                    padding_y="4px",
                                    background="rgba(148, 163, 184, 0.1)",
                                    border_radius="6px",
                                ),
                                spacing="2",
                                align="center",
                                min_width="160px",
                            ),
                            # Divider
                            rx.box(width="1px", height="100px", background="rgba(255,255,255,0.1)", margin_x="20px"),
                            # Stats with visual scale
                            rx.vstack(
                                rx.text(State.indicator_trader_type + " Net Position", font_size="12px", color="#64748b", margin_bottom="8px"),
                                rx.hstack(
                                    rx.text("Current:", font_size="12px", color="#64748b", width="70px"),
                                    rx.text(State.zscore_data["current"].to(str), font_size="14px", font_weight="600", color="#e2e8f0"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("Mean:", font_size="12px", color="#64748b", width="70px"),
                                    rx.text(State.zscore_data["mean"].to(str), font_size="14px", font_weight="500", color="#94a3b8"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("Std Dev:", font_size="12px", color="#64748b", width="70px"),
                                    rx.text("±" + State.zscore_data["std"].to(str), font_size="14px", font_weight="500", color="#94a3b8"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("Data pts:", font_size="12px", color="#64748b", width="70px"),
                                    rx.text(State.zscore_data["data_points"].to(str) + " weeks", font_size="13px", color="#64748b"),
                                    spacing="2",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            # Divider
                            rx.box(width="1px", height="100px", background="rgba(255,255,255,0.1)", margin_x="20px"),
                            # Visual scale
                            rx.vstack(
                                rx.text("Position on Scale", font_size="12px", font_weight="600", color="#94a3b8", margin_bottom="8px"),
                                # Scale bar
                                rx.box(
                                    rx.hstack(
                                        rx.text("-2σ", font_size="10px", color="#ef4444"),
                                        rx.text("-1σ", font_size="10px", color="#f97316"),
                                        rx.text("0", font_size="10px", color="#94a3b8"),
                                        rx.text("+1σ", font_size="10px", color="#22c55e"),
                                        rx.text("+2σ", font_size="10px", color="#10b981"),
                                        justify="between",
                                        width="100%",
                                    ),
                                    width="200px",
                                ),
                                rx.box(
                                    rx.box(
                                        width="100%",
                                        height="8px",
                                        background="linear-gradient(90deg, #ef4444, #f97316, #94a3b8, #22c55e, #10b981)",
                                        border_radius="4px",
                                    ),
                                    # Marker centered (50%) - simplified
                                    rx.box(
                                        width="4px",
                                        height="16px",
                                        background="white",
                                        border_radius="2px",
                                        position="absolute",
                                        top="-4px",
                                        left="50%",  # Simplified: will update via computed var later
                                        transform="translateX(-50%)",
                                        box_shadow="0 0 8px rgba(255,255,255,0.5)",
                                    ),
                                    position="relative",
                                    width="200px",
                                    margin_top="4px",
                                ),
                                rx.text(
                                    "Current Z-Score: " + State.zscore_data["z_score"].to(str) + "σ",
                                    font_size="11px",
                                    color="#64748b",
                                    font_style="italic",
                                    margin_top="8px",
                                ),
                                spacing="1",
                                align="center",
                            ),
                            spacing="4",
                            align="center",
                            justify="center",
                            width="100%",
                        ),
                        spacing="0",
                        width="100%",
                    ),
                    padding="20px",
                    background="linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(96, 165, 250, 0.05))",
                    border_top="1px solid rgba(139, 92, 246, 0.2)",
                ),
            ),
            # Velocity Panel (conditionally shown)
            rx.cond(
                State.show_velocity_panel,
                rx.box(
                    rx.vstack(
                        # Header with trader type selector (synced with Z-Score)
                        rx.hstack(
                            rx.hstack(
                                rx.icon("activity", size=20, color="#8b5cf6"),
                                rx.text("Positioning Velocity", font_size="16px", font_weight="600", color="#e2e8f0"),
                                rx.text(" (" + State.indicator_trader_type + ")", font_size="13px", color="#64748b"),
                                spacing="2",
                                align="center",
                            ),
                            rx.spacer(),
                            # Same trader pills as Z-Score for consistency
                            rx.hstack(
                                rx.box(
                                    rx.text("NC", font_size="11px", font_weight="600"),
                                    padding_x="10px",
                                    padding_y="4px",
                                    border_radius="6px",
                                    cursor="pointer",
                                    background=rx.cond(
                                        State.indicator_trader_type == "Non-Commercial",
                                        "rgba(139, 92, 246, 0.3)",
                                        "rgba(255,255,255,0.05)"
                                    ),
                                    color=rx.cond(
                                        State.indicator_trader_type == "Non-Commercial",
                                        "#a78bfa",
                                        "#64748b"
                                    ),
                                    border="1px solid",
                                    border_color=rx.cond(
                                        State.indicator_trader_type == "Non-Commercial",
                                        "rgba(139, 92, 246, 0.5)",
                                        "rgba(255,255,255,0.1)"
                                    ),
                                    on_click=lambda: State.set_indicator_trader_type("Non-Commercial"),
                                ),
                                rx.box(
                                    rx.text("COMM", font_size="11px", font_weight="600"),
                                    padding_x="10px",
                                    padding_y="4px",
                                    border_radius="6px",
                                    cursor="pointer",
                                    background=rx.cond(
                                        State.indicator_trader_type == "Commercial",
                                        "rgba(239, 68, 68, 0.3)",
                                        "rgba(255,255,255,0.05)"
                                    ),
                                    color=rx.cond(
                                        State.indicator_trader_type == "Commercial",
                                        "#f87171",
                                        "#64748b"
                                    ),
                                    border="1px solid",
                                    border_color=rx.cond(
                                        State.indicator_trader_type == "Commercial",
                                        "rgba(239, 68, 68, 0.5)",
                                        "rgba(255,255,255,0.1)"
                                    ),
                                    on_click=lambda: State.set_indicator_trader_type("Commercial"),
                                ),
                                rx.box(
                                    rx.text("NR", font_size="11px", font_weight="600"),
                                    padding_x="10px",
                                    padding_y="4px",
                                    border_radius="6px",
                                    cursor="pointer",
                                    background=rx.cond(
                                        State.indicator_trader_type == "Non-Reportable",
                                        "rgba(96, 165, 250, 0.3)",
                                        "rgba(255,255,255,0.05)"
                                    ),
                                    color=rx.cond(
                                        State.indicator_trader_type == "Non-Reportable",
                                        "#60a5fa",
                                        "#64748b"
                                    ),
                                    border="1px solid",
                                    border_color=rx.cond(
                                        State.indicator_trader_type == "Non-Reportable",
                                        "rgba(96, 165, 250, 0.5)",
                                        "rgba(255,255,255,0.1)"
                                    ),
                                    on_click=lambda: State.set_indicator_trader_type("Non-Reportable"),
                                ),
                                spacing="1",
                            ),
                            width="100%",
                            align="center",
                            margin_bottom="16px",
                        ),
                        # Main content
                        rx.hstack(
                            # Velocity value display - BIGGER
                            rx.vstack(
                                rx.text("WoW Change", font_size="11px", color="#64748b"),
                                rx.hstack(
                                    rx.text(
                                        State.velocity_data["velocity"],
                                        font_size="42px",
                                        font_weight="700",
                                        color=State.velocity_data["color"],
                                    ),
                                    rx.text("/wk", font_size="16px", color="#94a3b8", margin_top="16px"),
                                    align="end",
                                ),
                                rx.box(
                                    rx.text(
                                        State.velocity_data["trend"],
                                        font_size="13px",
                                        font_weight="600",
                                        color=State.velocity_data["color"],
                                    ),
                                    padding_x="10px",
                                    padding_y="3px",
                                    background="rgba(255,255,255,0.05)",
                                    border_radius="4px",
                                ),
                                spacing="1",
                                align="center",
                                min_width="140px",
                            ),
                            # Divider
                            rx.box(width="1px", height="100px", background="rgba(255,255,255,0.1)", margin_x="20px"),
                            # Acceleration
                            rx.vstack(
                                rx.text("Acceleration", font_size="11px", color="#64748b"),
                                rx.hstack(
                                    rx.text(
                                        State.velocity_data["acceleration"],
                                        font_size="32px",
                                        font_weight="600",
                                        color=State.velocity_data["color"],
                                    ),
                                    rx.text("/wk²", font_size="12px", color="#94a3b8", margin_top="10px"),
                                    align="end",
                                ),
                                rx.text(
                                    "Rate of change",
                                    font_size="11px",
                                    color="#64748b",
                                ),
                                spacing="1",
                                align="center",
                            ),
                            # Divider
                            rx.box(width="1px", height="100px", background="rgba(255,255,255,0.1)", margin_x="20px"),
                            # Signal badge
                            rx.vstack(
                                rx.text("Momentum Signal", font_size="11px", color="#64748b"),
                                rx.box(
                                    rx.text(
                                        State.velocity_data["signal"],
                                        font_size="16px",
                                        font_weight="700",
                                        color=State.velocity_data["color"],
                                    ),
                                    padding_x="16px",
                                    padding_y="10px",
                                    background="rgba(148, 163, 184, 0.1)",
                                    border_radius="8px",
                                    border="1px solid",
                                    border_color=State.velocity_data["color"],
                                ),
                                spacing="2",
                                align="center",
                            ),
                            # Divider
                            rx.box(width="1px", height="100px", background="rgba(255,255,255,0.1)", margin_x="20px"),
                            # Interpretation guide
                            rx.vstack(
                                rx.text("Momentum Guide", font_size="12px", font_weight="600", color="#94a3b8", margin_bottom="4px"),
                                rx.hstack(
                                    rx.icon("arrow-up-right", size=14, color="#10b981"),
                                    rx.text("+Vel, +Acc = Strong buying", font_size="11px", color="#64748b"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon("arrow-right", size=14, color="#22c55e"),
                                    rx.text("+Vel, -Acc = Buying fading", font_size="11px", color="#64748b"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon("corner-up-right", size=14, color="#f97316"),
                                    rx.text("-Vel, +Acc = Reversal forming", font_size="11px", color="#64748b"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.icon("arrow-down-right", size=14, color="#ef4444"),
                                    rx.text("-Vel, -Acc = Strong selling", font_size="11px", color="#64748b"),
                                    spacing="2",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            spacing="4",
                            align="center",
                            justify="center",
                            width="100%",
                        ),
                        spacing="0",
                        width="100%",
                    ),
                    padding="20px",
                    background="linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(96, 165, 250, 0.05))",
                    border_top="1px solid rgba(139, 92, 246, 0.2)",
                ),
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
        padding="0",
        background=themed("rgba(255,255,255,0.95)", "rgba(255,255,255,0.02)"),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.06)"),
        border_radius="8px",
        overflow="hidden",
        transition="all 0.15s ease",
        _hover={
            "border_color": themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
        },
    )


def add_to_watchlist_button() -> rx.Component:
    """Add/Remove from watchlist button with dashed border."""
    return rx.box(
        rx.hstack(
            rx.cond(
                State.is_in_watchlist,
                rx.icon("star", size=14, color="#eab308"),
                rx.icon("star", size=14, color="#a78bfa"),
            ),
            rx.text(
                rx.cond(State.is_in_watchlist, "In Watchlist", "Add to Watchlist"),
                font_size="11px",
                font_weight="500",
            ),
            spacing="1",
            align="center",
        ),
        padding_x="10px",
        padding_y="5px",
        border_radius="6px",
        cursor="pointer",
        color=rx.cond(State.is_in_watchlist, "#eab308", "#a78bfa"),
        background=rx.cond(
            State.is_in_watchlist,
            "rgba(234, 179, 8, 0.1)",
            "transparent"
        ),
        border="1px",
        border_style=rx.cond(State.is_in_watchlist, "solid", "dashed"),
        border_color=rx.cond(
            State.is_in_watchlist,
            "rgba(234, 179, 8, 0.3)",
            "rgba(139, 92, 246, 0.3)"
        ),
        on_click=State.toggle_watchlist,
        _hover={
            "background": rx.cond(
                State.is_in_watchlist,
                "rgba(234, 179, 8, 0.2)",
                "rgba(139, 92, 246, 0.1)"
            ),
            "border_color": rx.cond(
                State.is_in_watchlist,
                "rgba(234, 179, 8, 0.5)",
                "rgba(139, 92, 246, 0.5)"
            ),
        },
        transition="all 0.2s ease",
    )


def sticky_asset_header() -> rx.Component:
    """Command Bar extension - Asset info with contract identifier and report type pill."""
    return rx.box(
        rx.hstack(
            # Asset name + Contract identifier
            rx.hstack(
                rx.text(
                    State.selected_name,
                    font_size="16px",
                    font_weight="600",
                    color=themed(LightTheme.text_primary, "#E6E9F0"),
                ),
                # Contract/Symbol - muted pill
                rx.box(
                    rx.text(
                        State.selected_symbol,
                        font_size="10px",
                        font_weight="500",
                        color="#5FA8FF",
                        letter_spacing="0.02em",
                    ),
                    padding_x="8px",
                    padding_y="3px",
                    background="rgba(95,168,255,0.1)",
                    border_radius="4px",
                ),
                # Report type pill (muted)
                rx.box(
                    rx.text(
                        State.current_report_name,
                        font_size="10px",
                        font_weight="500",
                        color=themed(LightTheme.text_muted, "#6B7280"),
                        letter_spacing="0.02em",
                    ),
                    padding_x="8px",
                    padding_y="3px",
                    background=themed("rgba(0,0,0,0.04)", "rgba(255,255,255,0.04)"),
                    border_radius="4px",
                ),
                # Add to Watchlist button
                add_to_watchlist_button(),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            # Quick stats - institutional numeric display
            rx.hstack(
                # Open Interest
                rx.hstack(
                    rx.text("OI:", font_size="11px", color=themed(LightTheme.text_muted, "#6B7280")),
                    rx.text(
                        State.oi_display,
                        font_size="11px",
                        font_weight="500",
                        font_family='"JetBrains Mono", monospace',
                        color=themed(LightTheme.text_primary, "#E6E9F0"),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.box(
                    width="1px",
                    height="14px",
                    background=themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
                ),
                # Trader1 Net
                rx.hstack(
                    rx.text(State.trader1_label + ":", font_size="11px", color=themed(LightTheme.text_muted, "#6B7280")),
                    rx.text(
                        State.trader1_net_display,
                        font_size="11px",
                        font_weight="500",
                        font_family='"JetBrains Mono", monospace',
                        color=rx.cond(State.trader1_positive, "#4CAF91", "#D06C6C"),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.box(
                    width="1px",
                    height="14px",
                    background=themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
                ),
                # Positioning indicator
                rx.hstack(
                    rx.cond(
                        State.is_net_long,
                        rx.icon("trending-up", size=12, color="#4CAF91"),
                        rx.icon("trending-down", size=12, color="#D06C6C"),
                    ),
                    rx.text(
                        State.net_position_pct.to(str) + "%",
                        font_size="11px",
                        font_weight="500",
                        font_family='"JetBrains Mono", monospace',
                        color=rx.cond(State.is_net_long, "#4CAF91", "#D06C6C"),
                    ),
                    spacing="1",
                    align="center",
                ),
                spacing="3",
                align="center",
                display=["none", "none", "flex", "flex"],
            ),
            # Last updated timestamp (right side)
            rx.text(
                State.report_date,
                font_size="10px",
                color=themed(LightTheme.text_muted, "#6B7280"),
                display=["none", "none", "block", "block"],
            ),
            width="100%",
            align="center",
            padding_x=["16px", "20px", "24px", "24px"],
            padding_y="10px",
        ),
        position="sticky",
        top="0",
        z_index="100",
        background=themed(
            "rgba(255,255,255,0.95)",
            "rgba(15, 20, 32, 0.95)"  # bg_secondary with transparency
        ),
        backdrop_filter="blur(8px)",
        border_bottom="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.04)"),  # Very subtle
        width="100%",
    )


def dashboard_header_section() -> rx.Component:
    """
    Dashboard Hero Section - Proper institutional header.

    Layout: Title+Meta | Stat Pills | Actions
    """
    return rx.box(
        rx.hstack(
            # LEFT: Title and asset info
            rx.vstack(
                rx.text(
                    "Commitment of Traders",
                    font_size=["20px", "24px", "28px", "28px"],
                    font_weight="700",
                    color=themed(LightTheme.text_primary, "#F9FAFB"),
                    letter_spacing="-0.02em",
                ),
                rx.hstack(
                    rx.text(
                        State.selected_name,
                        font_size="14px",
                        font_weight="600",
                        color="#3B82F6",
                    ),
                    rx.text("•", color=themed(LightTheme.text_muted, "#4B5563"), padding_x="6px"),
                    rx.text(
                        State.report_date_formatted,
                        font_size="13px",
                        font_weight="400",
                        color=themed(LightTheme.text_muted, "#9CA3AF"),
                    ),
                    rx.text("•", color=themed(LightTheme.text_muted, "#4B5563"), padding_x="6px"),
                    rx.text(
                        State.report_type_display,
                        font_size="13px",
                        font_weight="400",
                        color=themed(LightTheme.text_muted, "#9CA3AF"),
                    ),
                    spacing="0",
                    align="center",
                    flex_wrap="wrap",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            # CENTER: Stat Pills (hidden on mobile)
            rx.hstack(
                # Data Fresh pill
                header_stat_pill(
                    icon="circle-check",
                    icon_color="#10B981",
                    label="Data Fresh",
                    value=State.report_date_formatted,
                ),
                # L/S Ratio pill
                header_stat_pill(
                    icon="scale",
                    icon_color="#8B5CF6",
                    label="L/S Ratio",
                    value=State.long_short_ratio,
                ),
                # WoW Change pill
                header_stat_pill(
                    icon="trending-up",
                    icon_color="#60A5FA",
                    label="WoW Change",
                    value=State.oi_change_display,
                ),
                # Open Interest pill
                header_stat_pill(
                    icon="bar-chart-2",
                    icon_color="#10B981",
                    label="Open Interest",
                    value=State.oi_display,
                ),
                spacing="3",
                align="center",
                display=["none", "none", "none", "flex"],  # Only on wide screens
            ),
            # RIGHT: Actions
            rx.hstack(
                # Markets status badge
                rx.box(
                    rx.hstack(
                        rx.box(
                            width="6px",
                            height="6px",
                            border_radius="50%",
                            background="#EF4444",
                            box_shadow="0 0 8px rgba(239, 68, 68, 0.5)",
                            style={"animation": "pulse 2s infinite"},
                        ),
                        rx.text(
                            "Closed",
                            font_size="12px",
                            font_weight="500",
                            color="#EF4444",
                            display=["none", "block", "block", "block"],
                        ),
                        spacing="2",
                        align="center",
                    ),
                    padding_x="10px",
                    padding_y="6px",
                    background="rgba(239, 68, 68, 0.12)",
                    border="1px solid rgba(239, 68, 68, 0.3)",
                    border_radius="6px",
                ),
                # Refresh button
                rx.box(
                    rx.hstack(
                        rx.cond(
                            State.is_refreshing,
                            rx.box(
                                rx.icon("loader", size=14, color="#3B82F6"),
                                style={"animation": "spin 1s linear infinite"},
                            ),
                            rx.icon("refresh-cw", size=14, color=themed(LightTheme.text_muted, "#9CA3AF")),
                        ),
                        rx.text(
                            rx.cond(State.is_refreshing, "Loading...", "Refresh"),
                            font_size="13px",
                            font_weight="500",
                            display=["none", "block", "block", "block"],
                        ),
                        spacing="2",
                        align="center",
                    ),
                    padding_x=["10px", "14px", "14px", "14px"],
                    padding_y="8px",
                    background=themed("rgba(255,255,255,0.8)", "rgba(255,255,255,0.03)"),
                    border="1px solid",
                    border_color=themed("rgba(0,0,0,0.08)", "rgba(255,255,255,0.08)"),
                    border_radius="8px",
                    color=themed(LightTheme.text_primary, "#D1D5DB"),
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _hover={
                        "background": themed("rgba(255,255,255,0.95)", "rgba(255,255,255,0.06)"),
                        "border_color": themed("rgba(0,0,0,0.12)", "rgba(255,255,255,0.12)"),
                    },
                    on_click=State.refresh_data,
                ),
                spacing="3",
                align="center",
            ),
            width="100%",
            align="center",
            gap="16px",
            flex_wrap="wrap",
        ),
        padding="20px 24px",
        background=themed(
            "linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%)",
            "linear-gradient(135deg, #1a1f2e 0%, #141923 100%)"
        ),
        border_bottom="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.08)"),
        width="100%",
    )


def header_stat_pill(
    icon: str,
    icon_color: str,
    label: str,
    value,
    value_color: str = None,
) -> rx.Component:
    """Individual stat pill for the header."""
    text_color = value_color if value_color else themed(LightTheme.text_primary, "#F9FAFB")

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=16, color=icon_color),
                padding="8px",
                background=f"{icon_color}15",
                border_radius="8px",
            ),
            rx.vstack(
                rx.text(
                    label,
                    font_size="10px",
                    font_weight="600",
                    letter_spacing="0.05em",
                    text_transform="uppercase",
                    color=themed(LightTheme.text_muted, "#6B7280"),
                ),
                rx.text(
                    value,
                    font_size="14px",
                    font_weight="700",
                    font_family='"JetBrains Mono", monospace',
                    color=text_color,
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        padding="10px 14px",
        background=themed("rgba(255,255,255,0.6)", "rgba(255,255,255,0.03)"),
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.06)"),
        border_radius="10px",
        min_width="140px",
        transition="all 0.2s ease",
        _hover={
            "background": themed("rgba(255,255,255,0.9)", "rgba(255,255,255,0.05)"),
            "border_color": f"{icon_color}30",
            "transform": "translateY(-2px)",
        },
    )


def search_filter_section() -> rx.Component:
    """Search and filter bar with asset selector."""
    return rx.vstack(
        # Asset selector with searchable dropdown
        asset_selector_section(),
        # Watchlist section
        watchlist_sidebar(),
        spacing="4",
        width="100%",
    )


def quick_stat_item(label: str, value: str, icon_name: str, color: str) -> rx.Component:
    """Individual quick stat item with hover effect."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=14, color=color),
                padding="6px",
                background=f"{color}15",
                border_radius="6px",
            ),
            rx.vstack(
                rx.text(
                    value,
                    font_size="14px",
                    font_weight="600",
                    font_family='"JetBrains Mono", monospace',
                    color=themed(LightTheme.text_primary, "#e2e8f0"),
                ),
                rx.text(
                    label,
                    font_size="11px",
                    font_weight="500",
                    letter_spacing="0.02em",
                    color=themed(LightTheme.text_muted, "#64748b"),
                ),
                spacing="0",
                align="start",
            ),
            spacing="2",
            align="center",
        ),
        padding="8px 12px",
        border_radius="8px",
        border="1px solid transparent",
        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
        cursor="default",
        _hover={
            "background": themed("rgba(0,0,0,0.03)", "rgba(255,255,255,0.05)"),
            "border_color": f"{color}30",
            "transform": "translateY(-2px)",
        },
    )


def quick_stats_bar() -> rx.Component:
    """Quick stats bar with key metrics and data freshness indicator."""
    return rx.box(
        rx.hstack(
            # Data freshness indicator
            rx.hstack(
                rx.box(
                    width="8px",
                    height="8px",
                    border_radius="50%",
                    background="#10b981",
                    box_shadow="0 0 8px rgba(16, 185, 129, 0.5)",
                ),
                rx.vstack(
                    rx.text(
                        "Data Fresh",
                        font_size="12px",
                        font_weight="500",
                        color=themed(LightTheme.text_primary, "#e2e8f0"),
                    ),
                    rx.text(
                        State.report_date,
                        font_size="11px",
                        color=themed(LightTheme.text_muted, "#64748b"),
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="2",
                align="center",
                padding_right="16px",
                border_right="1px solid",
                border_color=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
            ),
            # Quick stats
            quick_stat_item("L/S Ratio", "1.5:1", "scale", "#8b5cf6"),
            quick_stat_item("WoW Change", State.oi_change_display, "activity", "#60a5fa"),
            quick_stat_item("Open Interest", State.oi_display, "bar-chart-2", "#10b981"),
            rx.spacer(),
            # Last updated timestamp
            rx.cond(
                State.last_updated != "",
                rx.hstack(
                    rx.icon("clock", size=12, color="#64748b"),
                    rx.text(
                        "Updated " + State.last_updated,
                        font_size="11px",
                        color="#64748b",
                    ),
                    spacing="1",
                    align="center",
                    padding_right="12px",
                ),
                rx.fragment(),
            ),
            # Market status
            rx.box(
                rx.hstack(
                    rx.icon("clock", size=14, color="#f59e0b"),
                    rx.text(
                        "Markets Closed",
                        font_size="12px",
                        font_weight="500",
                        color="#f59e0b",
                    ),
                    spacing="2",
                    align="center",
                ),
                padding_x="12px",
                padding_y="6px",
                background="rgba(245, 158, 11, 0.1)",
                border="1px solid rgba(245, 158, 11, 0.2)",
                border_radius="20px",
            ),
            spacing="6",
            align="center",
            width="100%",
            flex_wrap="wrap",
        ),
        padding="16px 20px",
        background=themed("rgba(255,255,255,0.6)", "rgba(255,255,255,0.02)"),
        backdrop_filter="blur(10px)",
        border="1px solid",
        border_color=themed("rgba(0,0,0,0.05)", "rgba(255,255,255,0.05)"),
        border_radius="12px",
    )


def footer_section() -> rx.Component:
    """Footer - minimal, institutional."""
    return rx.box(
        rx.vstack(
            # AdSense Placeholder - Footer Leaderboard (728x90)
            rx.box(
                ad_placeholder("728px", "90px", "FOOTER AD"),
                display=["none", "none", "flex", "flex"],
                justify_content="center",
                margin_bottom="16px",
            ),
            # Mobile ad - smaller
            rx.box(
                ad_placeholder("320px", "50px", "MOBILE AD"),
                display=["flex", "flex", "none", "none"],
                justify_content="center",
                margin_bottom="16px",
            ),
            rx.hstack(
                rx.text(
                    "Data: CFTC Commitment of Traders",
                    font_size="11px",
                    color=themed(LightTheme.text_muted, "#6e7681"),
                ),
                rx.text("|", color=themed(LightTheme.text_muted, "#6e7681"), padding_x="8px"),
                rx.text(
                    "Release: Weekly (Tuesday)",
                    font_size="11px",
                    color=themed(LightTheme.text_muted, "#6e7681"),
                ),
                spacing="0",
                align="center",
                flex_wrap="wrap",
                justify="center",
            ),
            rx.text(
                "For informational purposes only. Not financial advice.",
                font_size="10px",
                color=themed(LightTheme.text_muted, "#6e7681"),
                padding_top="4px",
            ),
            spacing="2",
            align="center",
        ),
        padding_y="20px",
        border_top="1px solid",
        border_color=themed("rgba(0,0,0,0.06)", "rgba(255,255,255,0.06)"),
        text_align="center",
        width="100%",
    )


def main_content() -> rx.Component:
    """
    Main dashboard content area - matches reference design exactly.

    Layout (top to bottom):
    1. Header + metadata
    2. Summary strip (Data Fresh, Ratio, Weekly Change, OI)
    3. Two-column layout: Positioning Summary (left) | Quadrant Metrics (right)
    4. Historical positioning chart (full width)
    """
    return rx.box(
        # Sticky asset header - stays at top when scrolling
        sticky_asset_header(),
        rx.vstack(
            # ========================================
            # 1. HEADER + METADATA
            # ========================================
            dashboard_header_section(),

            # ========================================
            # 2. SUMMARY STRIP (horizontal bar)
            # ========================================
            rx.box(
                quick_stats_bar(),
                display=["none", "none", "block", "block"],  # Hide on mobile
                margin_top="20px",
            ),

            # On mobile only: show asset selector (since sidebar is hidden)
            rx.box(
                search_filter_section(),
                display=["block", "block", "none", "none"],  # Only on mobile
                margin_top="16px",
            ),

            # ========================================
            # 3. TWO-COLUMN LAYOUT: Positioning Summary | Quadrant Metrics
            # ========================================
            # Desktop: side-by-side layout
            rx.box(
                rx.hstack(
                    # LEFT COLUMN: Positioning Summary Card (anchoring, taller)
                    rx.box(
                        positioning_summary_card(),
                        flex="1",
                        min_width="320px",
                    ),
                    # RIGHT COLUMN: 2x2 Quadrant Metrics Grid
                    rx.box(
                        quadrant_metrics_grid(),
                        flex="1.2",
                        min_width="400px",
                    ),
                    spacing="6",
                    width="100%",
                    align="stretch",
                ),
                display=["none", "none", "block", "block"],  # Desktop only
                width="100%",
                margin_top="32px",
            ),
            # Mobile: stacked layout
            rx.box(
                rx.vstack(
                    # Positioning Summary Card
                    positioning_summary_card(),
                    # Quadrant Metrics as 2x2 grid
                    rx.box(
                        metric_card_clean(
                            label="Open Interest",
                            value=State.oi_display,
                            change=State.oi_change_pct,
                            change_positive=State.oi_change_positive,
                            color=themed(LightTheme.text_primary, "#E6E9F0"),
                        ),
                        metric_card_clean(
                            label=State.trader1_label + " Net",
                            value=State.trader1_net_display,
                            change=State.trader1_change_pct,
                            change_positive=State.trader1_change_positive,
                            color="#60A5FA",
                        ),
                        metric_card_clean(
                            label=State.trader2_label + " Net",
                            value=State.trader2_net_display,
                            change=State.trader2_change_pct,
                            change_positive=State.trader2_change_positive,
                            color="#F87171",
                        ),
                        metric_card_clean(
                            label=State.trader3_label + " Net",
                            value=State.trader3_net_display,
                            change=State.trader3_change_pct,
                            change_positive=State.trader3_change_positive,
                            color="#34D399",
                        ),
                        display="grid",
                        style={
                            "grid_template_columns": "1fr 1fr",
                        },
                        gap="12px",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                display=["block", "block", "none", "none"],  # Mobile only
                width="100%",
                margin_top="16px",
            ),

            # ========================================
            # 4. HISTORICAL POSITIONING CHART (full width)
            # Strong visual separation from metrics section
            # ========================================
            rx.box(
                # Subtle gradient divider
                rx.box(
                    width="60%",
                    height="1px",
                    background=themed(
                        "linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent)",
                        "linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)"
                    ),
                    margin="0 auto",
                    margin_bottom="32px",
                ),
                chart_section(),
                width="100%",
                margin_top="48px",
                padding_top="24px",
            ),

            # Footer - with breathing room
            rx.box(
                footer_section(),
                margin_top="48px",
            ),

            spacing="0",
            width="100%",
            max_width="1400px",
            margin="0 auto",
        ),
        padding=["16px", "24px", "32px", "40px"],  # Responsive padding
        padding_top=["16px", "20px", "24px", "24px"],
        flex="1",
        min_width="0",
        overflow_y="auto",
        min_height="calc(100vh - 60px)",
    )


# ============================================================================
# PERCENTILE RANK MODALS - Premium Feature
# ============================================================================

def percentile_trader_pill(label: str, trader_type: str) -> rx.Component:
    """Pill button for selecting trader type in percentile modal."""
    is_active = State.percentile_trader_type == trader_type
    return rx.box(
        rx.text(label, font_size="13px", font_weight="500"),
        padding_x="16px",
        padding_y="8px",
        border_radius="20px",
        cursor="pointer",
        background=rx.cond(
            is_active,
            "linear-gradient(135deg, #60a5fa, #8b5cf6)",
            "rgba(255, 255, 255, 0.05)",
        ),
        color=rx.cond(is_active, "white", "#94a3b8"),
        border="1px solid",
        border_color=rx.cond(
            is_active,
            "transparent",
            "rgba(255, 255, 255, 0.1)",
        ),
        transition="all 0.2s ease",
        _hover={
            "background": rx.cond(
                is_active,
                "linear-gradient(135deg, #3b82f6, #7c3aed)",
                "rgba(255, 255, 255, 0.1)",
            ),
        },
        on_click=State.set_percentile_trader_type(trader_type),
    )


def percentile_asset_card_bullish(item: Dict) -> rx.Component:
    """Display bullish asset with percentile score in modal."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    item["asset_name"],
                    font_size="14px",
                    font_weight="600",
                    color="#e2e8f0",
                ),
                rx.hstack(
                    rx.text(
                        item["symbol"],
                        font_size="12px",
                        color="#64748b",
                    ),
                    rx.text("•", font_size="12px", color="#475569"),
                    rx.text(
                        item["category"],
                        font_size="11px",
                        color="#64748b",
                    ),
                    spacing="1",
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text(
                    item["percentile"].to(str) + "%",
                    font_size="20px",
                    font_weight="700",
                    color="#10b981",
                ),
                rx.text(
                    "Percentile",
                    font_size="10px",
                    color="#64748b",
                    text_transform="uppercase",
                ),
                spacing="0",
                align="end",
            ),
            width="100%",
            align="center",
        ),
        padding="16px",
        background="rgba(16, 185, 129, 0.08)",
        border="1px solid",
        border_color="rgba(16, 185, 129, 0.25)",
        border_radius="12px",
        transition="all 0.2s ease",
        _hover={
            "border_color": "#10b981",
            "transform": "translateX(4px)",
        },
    )


def percentile_asset_card_bearish(item: Dict) -> rx.Component:
    """Display bearish asset with percentile score in modal."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    item["asset_name"],
                    font_size="14px",
                    font_weight="600",
                    color="#e2e8f0",
                ),
                rx.hstack(
                    rx.text(
                        item["symbol"],
                        font_size="12px",
                        color="#64748b",
                    ),
                    rx.text("•", font_size="12px", color="#475569"),
                    rx.text(
                        item["category"],
                        font_size="11px",
                        color="#64748b",
                    ),
                    spacing="1",
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text(
                    item["percentile"].to(str) + "%",
                    font_size="20px",
                    font_weight="700",
                    color="#ef4444",
                ),
                rx.text(
                    "Percentile",
                    font_size="10px",
                    color="#64748b",
                    text_transform="uppercase",
                ),
                spacing="0",
                align="end",
            ),
            width="100%",
            align="center",
        ),
        padding="16px",
        background="rgba(239, 68, 68, 0.08)",
        border="1px solid",
        border_color="rgba(239, 68, 68, 0.25)",
        border_radius="12px",
        transition="all 0.2s ease",
        _hover={
            "border_color": "#ef4444",
            "transform": "translateX(4px)",
        },
    )


def percentile_rank_modal() -> rx.Component:
    """Full-screen modal showing percentile rank analysis for premium users."""
    return rx.cond(
        State.show_percentile_modal,
        rx.box(
            # Backdrop
            rx.box(
                position="fixed",
                top="0",
                left="0",
                right="0",
                bottom="0",
                background="rgba(0, 0, 0, 0.8)",
                backdrop_filter="blur(8px)",
                z_index="998",
                on_click=State.close_percentile_modal,
            ),
            # Modal content
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.hstack(
                            rx.icon("bar-chart-horizontal", size=24, color="#8b5cf6"),
                            rx.text(
                                "Percentile Rank Analysis",
                                font_size="24px",
                                font_weight="700",
                                color="#e2e8f0",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        rx.spacer(),
                        rx.box(
                            rx.icon("x", size=20, color="#94a3b8"),
                            padding="8px",
                            border_radius="8px",
                            cursor="pointer",
                            _hover={"background": "rgba(255,255,255,0.1)"},
                            on_click=State.close_percentile_modal,
                        ),
                        width="100%",
                        align="center",
                    ),
                    # Description
                    rx.text(
                        "Discover assets at extreme positioning levels across all trader categories.",
                        font_size="14px",
                        color="#94a3b8",
                        margin_bottom="16px",
                    ),
                    # Controls row: Trader type + Lookback period
                    rx.hstack(
                        # Trader type selector
                        rx.hstack(
                            percentile_trader_pill("Non-Commercial", "Non-Commercial"),
                            percentile_trader_pill("Commercial", "Commercial"),
                            percentile_trader_pill("Non-Reportable", "Non-Reportable"),
                            spacing="2",
                            flex_wrap="wrap",
                        ),
                        rx.spacer(),
                        # Lookback period selector
                        rx.hstack(
                            rx.text("Lookback:", font_size="13px", color="#94a3b8", font_weight="500"),
                            rx.select(
                                ["6m", "8m", "1y", "2y", "3y"],
                                value=State.percentile_lookback,
                                on_change=State.set_percentile_lookback,
                                size="2",
                                variant="soft",
                                style={
                                    "background": "rgba(139, 92, 246, 0.15)",
                                    "border": "1px solid rgba(139, 92, 246, 0.3)",
                                    "color": "#e2e8f0",
                                    "min_width": "80px",
                                },
                            ),
                            spacing="2",
                            align="center",
                        ),
                        width="100%",
                        align="center",
                        justify="between",
                        flex_wrap="wrap",
                        gap="3",
                        margin_bottom="16px",
                    ),
                    # Current Asset Percentile Section
                    rx.box(
                        rx.vstack(
                            # Header with asset name and current percentile
                            rx.hstack(
                                rx.text(
                                    State.selected_name,
                                    font_size="18px",
                                    font_weight="700",
                                    color="#e2e8f0",
                                ),
                                rx.box(
                                    rx.text(
                                        State.selected_symbol,
                                        font_size="11px",
                                        font_weight="600",
                                        color="#8b5cf6",
                                    ),
                                    padding_x="8px",
                                    padding_y="3px",
                                    background="rgba(139,92,246,0.2)",
                                    border_radius="4px",
                                ),
                                rx.spacer(),
                                # Current percentile value
                                rx.hstack(
                                    rx.text("Current:", font_size="13px", color="#94a3b8"),
                                    rx.text(
                                        State.current_percentile.to(str) + "%",
                                        font_size="24px",
                                        font_weight="700",
                                        color=rx.cond(
                                            State.current_percentile >= 50,
                                            "#10b981",
                                            "#ef4444"
                                        ),
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                width="100%",
                                align="center",
                            ),
                            # Interpretation text
                            rx.text(
                                State.percentile_interpretation,
                                font_size="13px",
                                color="#94a3b8",
                                line_height="1.5",
                            ),
                            # Percentile chart
                            rx.plotly(
                                data=State.percentile_chart_fig,
                                use_resize_handler=True,
                                style={
                                    "width": "100%",
                                    "height": "200px",
                                    "min_height": "180px",
                                },
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        padding="16px",
                        background="rgba(139, 92, 246, 0.05)",
                        border="1px solid rgba(139, 92, 246, 0.2)",
                        border_radius="12px",
                        margin_bottom="16px",
                        width="100%",
                    ),
                    # Two columns: Top Bullish | Bottom Bearish
                    rx.box(
                        rx.hstack(
                            # Top 5% Most Bullish
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("trending-up", size=18, color="#10b981"),
                                    rx.text(
                                        "Top 5% Most Bullish",
                                        font_size="16px",
                                        font_weight="600",
                                        color="#10b981",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.foreach(
                                    State.top_bullish,
                                    percentile_asset_card_bullish,
                                ),
                                spacing="3",
                                width="100%",
                                align="stretch",
                            ),
                            # Bottom 5% Most Bearish
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("trending-down", size=18, color="#ef4444"),
                                    rx.text(
                                        "Bottom 5% Most Bearish",
                                        font_size="16px",
                                        font_weight="600",
                                        color="#ef4444",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.foreach(
                                    State.bottom_bearish,
                                    percentile_asset_card_bearish,
                                ),
                                spacing="3",
                                width="100%",
                                align="stretch",
                            ),
                            spacing="6",
                            width="100%",
                            align="start",
                            flex_direction=["column", "column", "row", "row"],
                        ),
                        width="100%",
                        max_height="60vh",
                        overflow_y="auto",
                        padding_right="8px",
                    ),
                    spacing="4",
                    width="100%",
                ),
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                width=["95%", "95%", "900px", "1000px"],
                max_width="1000px",
                max_height="90vh",
                padding=["20px", "24px", "32px", "32px"],
                background="linear-gradient(145deg, #0f1629 0%, #1a1f3a 100%)",
                border="1px solid rgba(96, 165, 250, 0.2)",
                border_radius="20px",
                box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 60px rgba(139, 92, 246, 0.1)",
                z_index="999",
                overflow="hidden",
            ),
            position="fixed",
            top="0",
            left="0",
            right="0",
            bottom="0",
            z_index="997",
        ),
        rx.fragment(),
    )


def upgrade_feature_item(icon: str, text: str) -> rx.Component:
    """Feature item in upgrade modal."""
    return rx.hstack(
        rx.text(icon, font_size="20px"),
        rx.text(text, font_size="14px", color="#e2e8f0"),
        spacing="3",
        align="center",
    )


def upgrade_modal() -> rx.Component:
    """Upgrade modal shown for premium features (Z-Score, Velocity)."""
    return rx.cond(
        State.show_upgrade_modal,
        rx.box(
            # Backdrop
            rx.box(
                position="fixed",
                top="0",
                left="0",
                right="0",
                bottom="0",
                background="rgba(0, 0, 0, 0.85)",
                backdrop_filter="blur(12px)",
                z_index="998",
                on_click=State.close_upgrade_modal,
            ),
            # Modal content
            rx.box(
                rx.vstack(
                    # Lock icon with golden tint for premium
                    rx.center(
                        rx.box(
                            rx.icon("lock", size=36, color="#eab308"),
                            padding="20px",
                            background="linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(245, 158, 11, 0.2))",
                            border_radius="50%",
                            border="2px solid rgba(234, 179, 8, 0.3)",
                        ),
                        margin_bottom="16px",
                    ),
                    # Dynamic Header based on feature
                    rx.cond(
                        State.upgrade_feature_name == "zscore",
                        rx.text(
                            "Unlock Z-Score Analysis",
                            font_size="24px",
                            font_weight="700",
                            color="#e2e8f0",
                            text_align="center",
                        ),
                        rx.cond(
                            State.upgrade_feature_name == "velocity",
                            rx.text(
                                "Unlock Positioning Velocity",
                                font_size="24px",
                                font_weight="700",
                                color="#e2e8f0",
                                text_align="center",
                            ),
                            rx.text(
                                "Unlock Premium Features",
                                font_size="24px",
                                font_weight="700",
                                color="#e2e8f0",
                                text_align="center",
                            ),
                        ),
                    ),
                    # Dynamic Description based on feature
                    rx.cond(
                        State.upgrade_feature_name == "zscore",
                        rx.text(
                            "Identify statistical extremes in positioning with standard deviation bands. See when positions are 2+ standard deviations from the mean.",
                            font_size="14px",
                            color="#94a3b8",
                            text_align="center",
                            line_height="1.6",
                            max_width="400px",
                        ),
                        rx.cond(
                            State.upgrade_feature_name == "velocity",
                            rx.text(
                                "Track the rate of change and acceleration in trader positioning. Detect trend momentum and potential reversals early.",
                                font_size="14px",
                                color="#94a3b8",
                                text_align="center",
                                line_height="1.6",
                                max_width="400px",
                            ),
                            rx.text(
                                "Access advanced quantitative analysis tools for professional trading insights.",
                                font_size="14px",
                                color="#94a3b8",
                                text_align="center",
                                line_height="1.6",
                                max_width="400px",
                            ),
                        ),
                    ),
                    # Dynamic Feature list based on feature
                    rx.cond(
                        State.upgrade_feature_name == "zscore",
                        rx.vstack(
                            upgrade_feature_item("📊", "Rolling Z-Score calculation"),
                            upgrade_feature_item("📈", "Standard deviation bands"),
                            upgrade_feature_item("🎯", "Historical percentile context"),
                            upgrade_feature_item("🔔", "Automatic extreme alerts"),
                            upgrade_feature_item("⚙️", "Customizable lookback periods"),
                            spacing="3",
                            width="100%",
                            padding="20px",
                            background="rgba(255, 255, 255, 0.02)",
                            border_radius="12px",
                            margin_y="16px",
                        ),
                        rx.cond(
                            State.upgrade_feature_name == "velocity",
                            rx.vstack(
                                upgrade_feature_item("🚀", "Position velocity tracking"),
                                upgrade_feature_item("📉", "Acceleration/deceleration detection"),
                                upgrade_feature_item("🔄", "Identify potential reversals"),
                                upgrade_feature_item("📊", "Momentum indicators"),
                                upgrade_feature_item("💹", "Position flow analysis"),
                                spacing="3",
                                width="100%",
                                padding="20px",
                                background="rgba(255, 255, 255, 0.02)",
                                border_radius="12px",
                                margin_y="16px",
                            ),
                            rx.vstack(
                                upgrade_feature_item("📊", "Z-Score Analysis"),
                                upgrade_feature_item("🚀", "Positioning Velocity"),
                                upgrade_feature_item("🎯", "Historical percentile rankings"),
                                upgrade_feature_item("⚡", "Real-time data updates"),
                                upgrade_feature_item("🔔", "Positioning threshold alerts"),
                                spacing="3",
                                width="100%",
                                padding="20px",
                                background="rgba(255, 255, 255, 0.02)",
                                border_radius="12px",
                                margin_y="16px",
                            ),
                        ),
                    ),
                    # Pricing card
                    rx.box(
                        rx.vstack(
                            rx.text(
                                "Premium Plan",
                                font_size="14px",
                                font_weight="500",
                                color="#94a3b8",
                            ),
                            rx.hstack(
                                rx.text(
                                    "$29",
                                    font_size="36px",
                                    font_weight="700",
                                    background="linear-gradient(135deg, #60a5fa, #8b5cf6)",
                                    background_clip="text",
                                    style={"-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"},
                                ),
                                rx.text(
                                    "/month",
                                    font_size="16px",
                                    color="#64748b",
                                    margin_left="4px",
                                ),
                                align="end",
                            ),
                            rx.text(
                                "Includes all premium features",
                                font_size="12px",
                                color="#64748b",
                            ),
                            spacing="1",
                            align="center",
                        ),
                        padding="20px",
                        background="linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(96, 165, 250, 0.1))",
                        border="1px solid rgba(139, 92, 246, 0.3)",
                        border_radius="16px",
                        width="100%",
                    ),
                    # CTA Buttons
                    rx.vstack(
                        rx.box(
                            rx.text(
                                "Upgrade Now",
                                font_size="16px",
                                font_weight="600",
                                color="white",
                            ),
                            width="100%",
                            padding="16px",
                            background="linear-gradient(135deg, #60a5fa 0%, #8b5cf6 100%)",
                            border_radius="12px",
                            text_align="center",
                            cursor="pointer",
                            box_shadow="0 8px 20px rgba(96, 165, 250, 0.3)",
                            transition="all 0.3s ease",
                            _hover={
                                "transform": "translateY(-2px)",
                                "box_shadow": "0 12px 30px rgba(96, 165, 250, 0.4)",
                            },
                            on_click=State.handle_upgrade_click,
                        ),
                        rx.box(
                            rx.text(
                                "Maybe Later",
                                font_size="14px",
                                color="#64748b",
                            ),
                            padding="12px",
                            cursor="pointer",
                            _hover={"color": "#94a3b8"},
                            on_click=State.close_upgrade_modal,
                        ),
                        spacing="2",
                        width="100%",
                        margin_top="8px",
                    ),
                    spacing="3",
                    width="100%",
                    align="center",
                ),
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                width=["90%", "90%", "480px", "480px"],
                max_width="480px",
                padding=["24px", "32px", "40px", "40px"],
                background="linear-gradient(145deg, #0f1629 0%, #1a1f3a 100%)",
                border="1px solid rgba(96, 165, 250, 0.2)",
                border_radius="24px",
                box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 80px rgba(139, 92, 246, 0.15)",
                z_index="999",
            ),
            position="fixed",
            top="0",
            left="0",
            right="0",
            bottom="0",
            z_index="997",
        ),
        rx.fragment(),
    )


def search_modal() -> rx.Component:
    """Global search modal for finding assets quickly."""
    return rx.cond(
        State.show_search_modal,
        rx.box(
            # Backdrop
            rx.box(
                position="fixed",
                top="0",
                left="0",
                right="0",
                bottom="0",
                background="rgba(0, 0, 0, 0.8)",
                backdrop_filter="blur(8px)",
                z_index="998",
                on_click=State.close_search_modal,
            ),
            # Modal content
            rx.box(
                rx.vstack(
                    # Header with search input
                    rx.hstack(
                        rx.icon("search", size=20, color="#64748b"),
                        rx.input(
                            placeholder="Search assets by name or symbol...",
                            value=State.search_query,
                            on_change=State.set_search_query,
                            width="100%",
                            background="transparent",
                            border="none",
                            color=themed(LightTheme.text_primary, "#e2e8f0"),
                            font_size="16px",
                            outline="none",
                            _focus={"outline": "none", "box_shadow": "none"},
                            auto_focus=True,
                        ),
                        rx.box(
                            rx.text("ESC", font_size="10px", color="#64748b", font_weight="600"),
                            padding_x="8px",
                            padding_y="4px",
                            background=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                            border_radius="4px",
                            cursor="pointer",
                            on_click=State.close_search_modal,
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                        padding="16px",
                        border_bottom="1px solid",
                        border_color=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                    ),
                    # Results list
                    rx.box(
                        rx.foreach(
                            State.filtered_assets,
                            lambda asset: rx.box(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(
                                            asset["name"],
                                            font_size="14px",
                                            font_weight="500",
                                            color=themed(LightTheme.text_primary, "#e2e8f0"),
                                        ),
                                        rx.hstack(
                                            rx.text(
                                                asset["symbol"],
                                                font_size="12px",
                                                font_weight="600",
                                                color="#3B82F6",
                                            ),
                                            rx.text(
                                                "•",
                                                color=themed(LightTheme.text_muted, "#64748b"),
                                                padding_x="6px",
                                            ),
                                            rx.text(
                                                asset["category"],
                                                font_size="12px",
                                                color=themed(LightTheme.text_muted, "#64748b"),
                                            ),
                                            spacing="0",
                                            align="center",
                                        ),
                                        spacing="0",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.icon(
                                        "chevron-right",
                                        size=16,
                                        color=themed(LightTheme.text_muted, "#64748b"),
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                                padding="12px 16px",
                                cursor="pointer",
                                _hover={
                                    "background": themed(
                                        "rgba(59, 130, 246, 0.08)",
                                        "rgba(59, 130, 246, 0.15)"
                                    ),
                                },
                                on_click=lambda a=asset: State.select_from_search(a["symbol"]),
                            ),
                        ),
                        max_height="400px",
                        overflow_y="auto",
                        width="100%",
                        class_name="hide-scrollbar",
                    ),
                    # Footer hint
                    rx.hstack(
                        rx.text(
                            f"{State.filtered_assets.length()} assets",
                            font_size="12px",
                            color=themed(LightTheme.text_muted, "#64748b"),
                        ),
                        rx.spacer(),
                        rx.hstack(
                            rx.text("Press", font_size="11px", color="#64748b"),
                            rx.box(
                                rx.text("↵", font_size="10px", color="#64748b"),
                                padding_x="6px",
                                padding_y="2px",
                                background=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                                border_radius="4px",
                            ),
                            rx.text("to select", font_size="11px", color="#64748b"),
                            spacing="1",
                            align="center",
                        ),
                        width="100%",
                        padding="12px 16px",
                        border_top="1px solid",
                        border_color=themed("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)"),
                    ),
                    spacing="0",
                    width="100%",
                ),
                position="fixed",
                top="15%",
                left="50%",
                transform="translateX(-50%)",
                width=["95%", "90%", "600px", "600px"],
                max_width="600px",
                background=themed(
                    "rgba(255, 255, 255, 0.98)",
                    "linear-gradient(145deg, #0f1629 0%, #1a1f3a 100%)"
                ),
                border="1px solid",
                border_color=themed("rgba(0,0,0,0.1)", "rgba(96, 165, 250, 0.2)"),
                border_radius="16px",
                box_shadow=themed(
                    "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                    "0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 80px rgba(59, 130, 246, 0.1)"
                ),
                z_index="999",
                overflow="hidden",
            ),
            position="fixed",
            top="0",
            left="0",
            right="0",
            bottom="0",
            z_index="997",
        ),
        rx.fragment(),
    )


# ============================================================================
# LOGIN PAGE - Stunning design with animated world map background
# ============================================================================

def floating_particle(delay: str, size: str, left: str, color: str) -> rx.Component:
    """Create an animated floating particle."""
    return rx.box(
        width=size,
        height=size,
        border_radius="50%",
        background=f"radial-gradient(circle, {color} 0%, transparent 70%)",
        position="absolute",
        left=left,
        bottom="-50px",
        opacity="0.6",
        filter="blur(1px)",
        style={
            "animation": f"floatUp 20s ease-in-out infinite",
            "animation-delay": delay,
        },
    )


def login_input_field(
    label: str,
    placeholder: str,
    input_type: str,
    value,
    on_change,
    show_toggle: bool = False,
) -> rx.Component:
    """Styled input field for login form."""
    return rx.vstack(
        rx.text(
            label,
            font_size="13px",
            font_weight="500",
            color="#94a3b8",
            margin_bottom="6px",
        ),
        rx.box(
            rx.hstack(
                rx.input(
                    placeholder=placeholder,
                    type=rx.cond(
                        State.show_password,
                        "text",
                        input_type
                    ) if show_toggle else input_type,
                    value=value,
                    on_change=on_change,
                    width="100%",
                    background="transparent",
                    border="none",
                    color="#e2e8f0",
                    font_size="15px",
                    _focus={"outline": "none"},
                    _placeholder={"color": "#64748b"},
                ),
                rx.cond(
                    show_toggle,
                    rx.box(
                        rx.cond(
                            State.show_password,
                            rx.icon("eye-off", size=18, color="#64748b"),
                            rx.icon("eye", size=18, color="#64748b"),
                        ),
                        cursor="pointer",
                        on_click=State.toggle_password_visibility,
                        padding="4px",
                        _hover={"color": "#94a3b8"},
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            width="100%",
            padding="14px 18px",
            background="rgba(30, 41, 59, 0.6)",
            border="1px solid rgba(96, 165, 250, 0.2)",
            border_radius="12px",
            transition="all 0.3s ease",
            _focus_within={
                "border_color": "#60a5fa",
                "box_shadow": "0 0 0 3px rgba(96, 165, 250, 0.1)",
            },
            _hover={
                "border_color": "rgba(96, 165, 250, 0.4)",
            },
        ),
        spacing="0",
        width="100%",
        align="start",
    )


def social_login_button(icon_name: str, provider: str, on_click) -> rx.Component:
    """Social login button (Google/Apple)."""
    return rx.box(
        rx.hstack(
            rx.icon(icon_name, size=20, color="#e2e8f0"),
            rx.text(
                provider,
                font_size="14px",
                font_weight="500",
                color="#e2e8f0",
            ),
            spacing="3",
            align="center",
            justify="center",
        ),
        width="100%",
        padding="14px",
        background="rgba(255, 255, 255, 0.03)",
        border="1px solid rgba(96, 165, 250, 0.2)",
        border_radius="12px",
        cursor="pointer",
        transition="all 0.3s ease",
        _hover={
            "background": "rgba(255, 255, 255, 0.06)",
            "transform": "translateY(-2px)",
            "border_color": "rgba(96, 165, 250, 0.4)",
        },
        on_click=on_click,
    )


def login_page() -> rx.Component:
    """Stunning login page with animated world map background."""
    return rx.box(
        # ===== Background Layers =====
        # World map background
        rx.box(
            position="absolute",
            top="0",
            left="0",
            right="0",
            bottom="0",
            background_image="url('/world_map.png')",
            background_size="cover",
            background_position="center",
            background_repeat="no-repeat",
            opacity="0.35",
            style={
                "animation": "pulseMap 8s ease-in-out infinite",
            },
            z_index="0",
        ),
        # Gradient overlay
        rx.box(
            position="absolute",
            top="0",
            left="0",
            right="0",
            bottom="0",
            background="radial-gradient(ellipse at center, transparent 0%, rgba(10, 14, 39, 0.7) 70%, rgba(10, 14, 39, 0.95) 100%)",
            z_index="1",
        ),
        # Grid lines overlay
        rx.box(
            position="absolute",
            top="0",
            left="0",
            right="0",
            bottom="0",
            opacity="0.03",
            background_image="linear-gradient(rgba(96, 165, 250, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(96, 165, 250, 0.3) 1px, transparent 1px)",
            background_size="50px 50px",
            z_index="2",
        ),
        # Floating particles
        rx.box(
            floating_particle("0s", "120px", "10%", "#10b981"),
            floating_particle("5s", "80px", "25%", "#8b5cf6"),
            floating_particle("10s", "100px", "60%", "#60a5fa"),
            floating_particle("15s", "60px", "80%", "#10b981"),
            floating_particle("8s", "90px", "45%", "#8b5cf6"),
            position="absolute",
            top="0",
            left="0",
            right="0",
            bottom="0",
            overflow="hidden",
            pointer_events="none",
            z_index="3",
        ),
        # ===== Login Card =====
        rx.box(
            rx.vstack(
                # Logo
                rx.box(
                    rx.image(
                        src="/cot_pulse_logo.png",
                        max_width="280px",
                        height="auto",
                        style={
                            "animation": "floatLogo 3s ease-in-out infinite",
                        },
                    ),
                    margin_bottom="8px",
                ),
                # Tagline
                rx.text(
                    "Track Market Sentiment in Real-Time",
                    font_size="14px",
                    color="#64748b",
                    margin_bottom="24px",
                ),
                # Welcome header
                rx.text(
                    "Welcome Back",
                    font_size="28px",
                    font_weight="700",
                    background="linear-gradient(135deg, #60a5fa 0%, #8b5cf6 100%)",
                    background_clip="text",
                    style={"-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"},
                    margin_bottom="8px",
                ),
                # Sign up link
                rx.hstack(
                    rx.text(
                        "Don't have an account?",
                        font_size="14px",
                        color="#64748b",
                    ),
                    rx.link(
                        "Sign up",
                        href="/signup",
                        font_size="14px",
                        font_weight="500",
                        color="#60a5fa",
                        _hover={"color": "#8b5cf6", "text_decoration": "underline"},
                    ),
                    spacing="2",
                    margin_bottom="28px",
                ),
                # Email input
                login_input_field(
                    "Email",
                    "Enter your email",
                    "email",
                    State.login_email,
                    State.set_login_email,
                ),
                rx.box(height="16px"),
                # Password input
                login_input_field(
                    "Password",
                    "Enter your password",
                    "password",
                    State.login_password,
                    State.set_login_password,
                    show_toggle=True,
                ),
                # Error message
                rx.cond(
                    State.login_error != "",
                    rx.text(
                        State.login_error,
                        font_size="13px",
                        color="#ef4444",
                        margin_top="8px",
                    ),
                    rx.fragment(),
                ),
                rx.box(height="12px"),
                # Remember me + Forgot password row
                rx.hstack(
                    rx.hstack(
                        rx.checkbox(
                            checked=State.remember_me,
                            on_change=lambda _: State.toggle_remember_me(),
                            color_scheme="blue",
                        ),
                        rx.text(
                            "Remember me",
                            font_size="13px",
                            color="#94a3b8",
                            cursor="pointer",
                            on_click=State.toggle_remember_me,
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.link(
                        "Forgot password?",
                        href="/forgot-password",
                        font_size="13px",
                        color="#60a5fa",
                        _hover={"color": "#8b5cf6"},
                    ),
                    width="100%",
                    align="center",
                ),
                rx.box(height="24px"),
                # Login button
                rx.box(
                    rx.text(
                        "Sign In",
                        font_size="15px",
                        font_weight="600",
                        color="white",
                    ),
                    width="100%",
                    padding="16px",
                    background="linear-gradient(135deg, #60a5fa 0%, #8b5cf6 100%)",
                    border_radius="12px",
                    text_align="center",
                    cursor="pointer",
                    box_shadow="0 4px 15px rgba(96, 165, 250, 0.35)",
                    transition="all 0.3s ease",
                    _hover={
                        "transform": "translateY(-2px)",
                        "box_shadow": "0 8px 25px rgba(96, 165, 250, 0.45)",
                    },
                    on_click=State.handle_login,
                ),
                rx.box(height="24px"),
                # Divider
                rx.hstack(
                    rx.box(
                        height="1px",
                        flex="1",
                        background="rgba(96, 165, 250, 0.2)",
                    ),
                    rx.text(
                        "Or continue with",
                        font_size="13px",
                        color="#64748b",
                        padding_x="16px",
                    ),
                    rx.box(
                        height="1px",
                        flex="1",
                        background="rgba(96, 165, 250, 0.2)",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.box(height="20px"),
                # Social login buttons
                rx.hstack(
                    social_login_button("chrome", "Google", State.handle_google_login),
                    social_login_button("apple", "Apple", State.handle_apple_login),
                    spacing="3",
                    width="100%",
                ),
                rx.box(height="24px"),
                # Terms and Privacy
                rx.hstack(
                    rx.link(
                        "Terms of Service",
                        href="/terms",
                        font_size="12px",
                        color="#64748b",
                        _hover={"color": "#94a3b8"},
                    ),
                    rx.text("•", color="#4a5568", font_size="12px"),
                    rx.link(
                        "Privacy Policy",
                        href="/privacy",
                        font_size="12px",
                        color="#64748b",
                        _hover={"color": "#94a3b8"},
                    ),
                    spacing="3",
                    justify="center",
                ),
                spacing="0",
                width="100%",
                align="center",
            ),
            width=["90%", "90%", "480px", "480px"],
            max_width="480px",
            padding=["32px", "40px", "48px", "48px"],
            background="rgba(10, 14, 39, 0.85)",
            backdrop_filter="blur(30px)",
            border="1px solid rgba(96, 165, 250, 0.2)",
            border_radius="24px",
            box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(96, 165, 250, 0.1)",
            position="relative",
            z_index="10",
            style={
                "animation": "slideUp 0.6s ease-out",
            },
            _hover={
                "border_color": "rgba(96, 165, 250, 0.35)",
                "box_shadow": "0 25px 60px -12px rgba(0, 0, 0, 0.6), 0 0 50px rgba(96, 165, 250, 0.15)",
            },
        ),
        # Container
        width="100%",
        min_height="100vh",
        background="#0a0e27",
        display="flex",
        align_items="center",
        justify_content="center",
        position="relative",
        overflow="hidden",
        font_family="'Inter', -apple-system, sans-serif",
    )


# ============================================================================
# MAIN PAGE
# ============================================================================

def index() -> rx.Component:
    """Main dashboard page with sidebar layout."""
    return rx.box(
        # Background watermark - COT PULSE logo (full-page, more visible)
        rx.box(
            background_image="url('/pulse (2).png')",
            background_size="contain",
            background_repeat="no-repeat",
            background_position="center",
            position="fixed",
            top="50%",
            left="55%",  # Slightly right of center
            transform="translate(-50%, -50%) rotate(-5deg)",
            width="65vw",  # 65% of viewport width
            height="65vh",  # 65% of viewport height
            max_width="1100px",
            pointer_events="none",
            z_index="0",
            # Remove white background and make logo visible as ghost watermark
            mix_blend_mode="screen",  # Makes white transparent on dark backgrounds
            filter=themed(
                "invert(0) brightness(1) opacity(0.08)",  # Light mode: more visible
                "invert(1) brightness(0.6) opacity(1)"  # Dark mode: brighter white ghost
            ),
            opacity=themed("0.08", "0.06"),  # More visible - 6-8% opacity
        ),
        # Top Header (sticky)
        terminal_header(),
        # Main Layout - Sidebar + Content
        rx.hstack(
            # Left Sidebar (260px)
            left_sidebar(),
            # Main Content (flex: 1)
            main_content(),
            spacing="0",
            align_items="stretch",
            width="100%",
            position="relative",
            z_index="1",  # Above watermark
        ),
        # Modals (positioned fixed, render at top level)
        percentile_rank_modal(),
        upgrade_modal(),
        search_modal(),
        background=rx.cond(
            State.is_dark_mode,
            "#0B0F17",  # Institutional deep background
            "#ffffff",
        ),
        min_height="100vh",
        font_family='"Inter", system-ui, -apple-system, sans-serif',
        on_mount=State.init_data,
        position="relative",
    )


# ============================================================================
# APP
# ============================================================================

app = rx.App(
    stylesheets=[
        # Premium fonts: Jost (geometric, modern UI) + JetBrains Mono (crisp numeric data)
        "https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap",
    ],
    style={
        # Minimal transitions - no bouncing, no flashy animations
        "*": {
            "transition": "background-color 0.1s ease, border-color 0.1s ease, color 0.1s ease",
        },
        # Selection uses accent color sparingly
        "::selection": {
            "background": "#5FA8FF",
            "color": "#ffffff",
        },
        # Typography system - Jost for clean, geometric UI
        "body": {
            "font-family": '"Jost", system-ui, -apple-system, sans-serif',
            "font-weight": "400",
            "-webkit-font-smoothing": "antialiased",
            "-moz-osx-font-smoothing": "grayscale",
        },
        # Hide scrollbar utility class
        ".hide-scrollbar": {
            "scrollbar-width": "none",  # Firefox
            "-ms-overflow-style": "none",  # IE and Edge
        },
        ".hide-scrollbar::-webkit-scrollbar": {
            "display": "none",  # Chrome, Safari, Opera
        },
        # Watchlist item delete button - show on hover
        ".watchlist-item:hover .watchlist-delete-btn": {
            "opacity": "1",
        },
        # Login page animations
        "@keyframes slideUp": {
            "from": {
                "opacity": "0",
                "transform": "translateY(30px)",
            },
            "to": {
                "opacity": "1",
                "transform": "translateY(0)",
            },
        },
        "@keyframes floatLogo": {
            "0%, 100%": {
                "transform": "translateY(0)",
            },
            "50%": {
                "transform": "translateY(-10px)",
            },
        },
        "@keyframes pulseMap": {
            "0%, 100%": {
                "transform": "scale(1)",
                "opacity": "0.35",
            },
            "50%": {
                "transform": "scale(1.02)",
                "opacity": "0.4",
            },
        },
        "@keyframes floatUp": {
            "0%": {
                "transform": "translateY(100vh) rotate(0deg)",
                "opacity": "0",
            },
            "10%": {
                "opacity": "0.6",
            },
            "90%": {
                "opacity": "0.6",
            },
            "100%": {
                "transform": "translateY(-100vh) rotate(360deg)",
                "opacity": "0",
            },
        },
        # Spinner animation for loading states
        "@keyframes spin": {
            "0%": {"transform": "rotate(0deg)"},
            "100%": {"transform": "rotate(360deg)"},
        },
        # Fade in animation for metric cards
        "@keyframes fadeIn": {
            "from": {"opacity": "0", "transform": "translateY(10px)"},
            "to": {"opacity": "1", "transform": "translateY(0)"},
        },
        # Fade-in-up animation for sections
        "@keyframes fadeInUp": {
            "from": {"opacity": "0", "transform": "translateY(20px)"},
            "to": {"opacity": "1", "transform": "translateY(0)"},
        },
        # Utility classes for animations
        ".fade-in": {
            "animation": "fadeIn 0.4s ease-out forwards",
        },
        ".fade-in-up": {
            "animation": "fadeInUp 0.5s ease-out forwards",
        },
        # Staggered delays for cards
        ".delay-1": {"animation-delay": "0.1s", "opacity": "0"},
        ".delay-2": {"animation-delay": "0.2s", "opacity": "0"},
        ".delay-3": {"animation-delay": "0.3s", "opacity": "0"},
        ".delay-4": {"animation-delay": "0.4s", "opacity": "0"},
    },
)

app.add_page(index, route="/", title="COT Pulse | Commitment of Traders Dashboard")
app.add_page(login_page, route="/login", title="Login | COT Pulse")
