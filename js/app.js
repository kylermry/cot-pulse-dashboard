/**
 * COT Pulse - Main Application
 * Vanilla JavaScript Dashboard for CFTC COT Data
 */

(function() {
    'use strict';

    // ========================================================================
    // APPLICATION STATE
    // ========================================================================

    const state = {
        // Theme
        isDarkMode: true,

        // Selected asset
        selectedSymbol: 'ES',
        selectedName: 'E-Mini S&P 500',
        selectedCategory: 'Equities',

        // Report type
        reportType: 'legacy',

        // Chart settings
        chartType: 'line',
        chartView: 'position', // 'position' or 'percentile'
        zoomYears: 0, // 0 = ALL, 1 = 1Y, 2 = 2Y, 3 = 3Y, 5 = 5Y

        // Series visibility
        showTrader1: true,
        showTrader2: true,
        showTrader3: true,
        showTrader4: true,

        // Percentile settings
        percentileLookback: 156, // 3 years default (52 weeks * 3)
        percentileTrader: 'trader1', // Which trader to show percentile for
        percentileHistory: [],
        percentileData: null,

        // Gauge trader index (1-4)
        gaugeTraderIndex: 1,

        // Expanded categories
        expandedCategories: new Set(),

        // Watchlist
        watchlist: [
            { symbol: 'ES', name: 'E-Mini S&P 500', category: 'Equities' },
            { symbol: 'GC', name: 'Gold', category: 'Metals' },
            { symbol: 'CL', name: 'Crude Oil WTI', category: 'Energy' }
        ],

        // Data
        latestReport: null,
        chartData: [],

        // Loading states
        isLoading: false,

        // Modals
        searchModalOpen: false
    };

    // ========================================================================
    // DOM ELEMENTS
    // ========================================================================

    const elements = {};

    function cacheElements() {
        // Header
        elements.themeToggle = document.getElementById('theme-toggle');
        elements.searchTrigger = document.getElementById('search-trigger');
        elements.watchlistCountNav = document.getElementById('watchlist-count');

        // Sidebar
        elements.selectedAssetName = document.getElementById('selected-asset-name');
        elements.selectedAssetSymbol = document.getElementById('selected-asset-symbol');
        elements.selectedAssetCategory = document.getElementById('selected-asset-category');
        elements.assetCategories = document.getElementById('asset-categories');
        elements.watchlistItems = document.getElementById('watchlist-items');
        elements.watchlistBadge = document.getElementById('watchlist-badge');

        // Dashboard header
        elements.headerAssetName = document.getElementById('header-asset-name');
        elements.headerAssetSymbol = document.getElementById('header-asset-symbol');
        elements.reportDate = document.getElementById('report-date');
        elements.watchlistToggle = document.getElementById('watchlist-toggle');

        // Gauge
        elements.gaugeTraderPills = document.getElementById('gauge-trader-pills');
        elements.gaugeLongArc = document.getElementById('gauge-long-arc');
        elements.gaugeShortArc = document.getElementById('gauge-short-arc');
        elements.gaugeLabel = document.getElementById('gauge-label');
        elements.gaugeValue = document.getElementById('gauge-value');
        elements.gaugeLongValue = document.getElementById('gauge-long-value');
        elements.gaugeLongPct = document.getElementById('gauge-long-pct');
        elements.gaugeShortValue = document.getElementById('gauge-short-value');
        elements.gaugeShortPct = document.getElementById('gauge-short-pct');

        // Trader summary
        elements.traderSummary = document.getElementById('trader-summary');

        // Chart
        elements.mainChart = document.getElementById('main-chart');
        elements.chartLoading = document.getElementById('chart-loading');
        elements.legendToggles = document.getElementById('legend-toggles');
        elements.legendTrader1 = document.getElementById('legend-trader1');
        elements.legendTrader2 = document.getElementById('legend-trader2');
        elements.legendTrader3 = document.getElementById('legend-trader3');
        elements.legendTrader4 = document.getElementById('legend-trader4');

        // Metrics grid
        elements.metricsGrid = document.getElementById('metrics-grid');

        // Modals
        elements.searchModal = document.getElementById('search-modal');
        elements.searchInput = document.getElementById('search-input');
        elements.searchResults = document.getElementById('search-results');

        // Percentile trader pills
        elements.percentileTraderPills = document.getElementById('percentile-trader-pills');
        elements.pctlTrader1 = document.getElementById('pctl-trader1');
        elements.pctlTrader2 = document.getElementById('pctl-trader2');
        elements.pctlTrader3 = document.getElementById('pctl-trader3');
        elements.pctlTrader4 = document.getElementById('pctl-trader4');
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    function init() {
        cacheElements();
        initializeIcons();
        setupEventListeners();
        renderCategories();
        renderWatchlist();
        loadAssetData();
    }

    function initializeIcons() {
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    // ========================================================================
    // EVENT LISTENERS
    // ========================================================================

    function setupEventListeners() {
        // Theme toggle
        elements.themeToggle.addEventListener('click', toggleTheme);

        // Search
        elements.searchTrigger.addEventListener('click', openSearchModal);
        elements.searchModal.addEventListener('click', (e) => {
            if (e.target === elements.searchModal) closeSearchModal();
        });
        elements.searchInput.addEventListener('input', handleSearch);

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboard);

        // Report type buttons
        document.querySelectorAll('.report-btn').forEach(btn => {
            btn.addEventListener('click', () => setReportType(btn.dataset.report));
        });

        // Nav items
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.addEventListener('click', () => setActiveNav(btn.dataset.nav));
        });

        // View toggle (position/percentile)
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => setChartView(btn.dataset.view));
        });

        // Chart type toggle
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', () => setChartType(btn.dataset.type));
        });

        // Zoom controls
        document.querySelectorAll('.zoom-btn').forEach(btn => {
            btn.addEventListener('click', () => setZoom(parseInt(btn.dataset.zoom)));
        });

        // Legend toggles
        elements.legendToggles.addEventListener('click', (e) => {
            const btn = e.target.closest('.legend-btn');
            if (btn) toggleSeries(btn.dataset.series);
        });

        // Watchlist toggle
        elements.watchlistToggle.addEventListener('click', toggleWatchlist);

        // Percentile trader pills
        elements.percentileTraderPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.trader-pill');
            if (pill && !pill.classList.contains('hidden')) {
                setPercentileTrader(pill.dataset.trader);
            }
        });
    }

    function handleKeyboard(e) {
        // Ctrl+K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openSearchModal();
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            closeSearchModal();
        }
    }

    // ========================================================================
    // THEME
    // ========================================================================

    function toggleTheme() {
        state.isDarkMode = !state.isDarkMode;
        document.body.classList.toggle('light-theme', !state.isDarkMode);
        document.body.classList.toggle('dark-theme', state.isDarkMode);
        renderChart(); // Re-render chart with new theme
    }

    // ========================================================================
    // NAVIGATION
    // ========================================================================

    function setActiveNav(nav) {
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.nav === nav);
        });
    }

    // ========================================================================
    // SEARCH
    // ========================================================================

    function openSearchModal() {
        state.searchModalOpen = true;
        elements.searchModal.classList.add('visible');
        elements.searchInput.value = '';
        elements.searchInput.focus();
        renderSearchResults('');
    }

    function closeSearchModal() {
        state.searchModalOpen = false;
        elements.searchModal.classList.remove('visible');
    }

    function handleSearch(e) {
        renderSearchResults(e.target.value);
    }

    function renderSearchResults(query) {
        const assets = COTAPI.getAllAssets();
        const filtered = query
            ? assets.filter(a =>
                a.symbol.toLowerCase().includes(query.toLowerCase()) ||
                a.name.toLowerCase().includes(query.toLowerCase())
            )
            : assets;

        if (filtered.length === 0) {
            elements.searchResults.innerHTML = `
                <div class="search-empty">No assets found matching "${query}"</div>
            `;
            return;
        }

        elements.searchResults.innerHTML = filtered.slice(0, 20).map(asset => `
            <div class="search-result" data-symbol="${asset.symbol}" data-category="${asset.category}">
                <span class="result-symbol">${asset.symbol}</span>
                <span class="result-name">${asset.name}</span>
                <span class="result-category">${asset.category}</span>
            </div>
        `).join('');

        // Add click handlers
        elements.searchResults.querySelectorAll('.search-result').forEach(el => {
            el.addEventListener('click', () => {
                const symbol = el.dataset.symbol;
                const category = el.dataset.category;
                const asset = assets.find(a => a.symbol === symbol);
                if (asset) {
                    selectAsset(symbol, asset.name, category);
                    closeSearchModal();
                }
            });
        });
    }

    // ========================================================================
    // ASSET SELECTION
    // ========================================================================

    function selectAsset(symbol, name, category) {
        state.selectedSymbol = symbol;
        state.selectedName = name;
        state.selectedCategory = category;

        // Update UI
        updateAssetDisplay();
        loadAssetData();
    }

    function updateAssetDisplay() {
        // Sidebar
        elements.selectedAssetName.textContent = state.selectedName;
        elements.selectedAssetSymbol.textContent = state.selectedSymbol;
        elements.selectedAssetCategory.textContent = state.selectedCategory;

        // Dashboard header
        elements.headerAssetName.textContent = state.selectedName;
        elements.headerAssetSymbol.textContent = state.selectedSymbol;

        // Update watchlist toggle state
        const isInWatchlist = state.watchlist.some(w => w.symbol === state.selectedSymbol);
        elements.watchlistToggle.classList.toggle('active', isInWatchlist);

        // Update category chip selection
        document.querySelectorAll('.asset-chip').forEach(chip => {
            chip.classList.toggle('selected', chip.dataset.symbol === state.selectedSymbol);
        });

        // Reinitialize icons
        initializeIcons();
    }

    // ========================================================================
    // DATA LOADING
    // ========================================================================

    async function loadAssetData() {
        state.isLoading = true;
        showLoading(true);

        try {
            // Fetch latest report and historical data in parallel
            const [latestReport, chartData] = await Promise.all([
                COTAPI.fetchLatestReport(state.selectedSymbol, state.reportType),
                COTAPI.fetchHistoricalData(state.selectedSymbol, state.reportType)
            ]);

            state.latestReport = latestReport;
            state.chartData = chartData;

            // Calculate percentile data
            calculatePercentileData();

            // Update all UI components
            updateQuickStats();
            updateGaugePills();
            updateGauge();
            updateTraderSummary();
            updateMetricCards();
            renderChart();
        } catch (error) {
            console.error('Error loading asset data:', error);
        } finally {
            state.isLoading = false;
            showLoading(false);
        }
    }

    function showLoading(show) {
        elements.chartLoading.classList.toggle('visible', show);
    }

    // ========================================================================
    // REPORT TYPE
    // ========================================================================

    function setReportType(reportType) {
        state.reportType = reportType;

        // Update UI
        document.querySelectorAll('.report-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.report === reportType);
        });

        // Update labels
        updateTraderLabels();

        // Show/hide trader4 legend button
        const hasTrader4 = reportType !== 'legacy';
        document.querySelector('.legend-btn[data-series="trader4"]').classList.toggle('hidden', !hasTrader4);

        // Reload data
        loadAssetData();
    }

    function updateTraderLabels() {
        const mapping = COTAPI.getFieldMapping(state.reportType);

        // Legend labels
        elements.legendTrader1.textContent = mapping.trader1_name;
        elements.legendTrader2.textContent = mapping.trader2_name;
        elements.legendTrader3.textContent = mapping.trader3_name;
        if (mapping.trader4_name) {
            elements.legendTrader4.textContent = mapping.trader4_name;
        }

        // Update gauge pills
        updateGaugePills();
    }

    // ========================================================================
    // QUICK STATS
    // ========================================================================

    function updateQuickStats() {
        if (!state.latestReport) return;

        // Report date
        elements.reportDate.textContent = state.latestReport.reportDate;
    }

    // ========================================================================
    // GAUGE
    // ========================================================================

    function updateGaugePills() {
        const mapping = COTAPI.getFieldMapping(state.reportType);
        const hasTrader4 = state.reportType !== 'legacy';

        const shortLabels = {
            legacy: ['NC', 'COMM', 'NR'],
            disaggregated: ['PM', 'SWAP', 'MM', 'OTH'],
            tff: ['DLR', 'AM', 'LEV', 'OTH']
        };

        const labels = shortLabels[state.reportType];

        let pillsHTML = labels.slice(0, hasTrader4 ? 4 : 3).map((label, i) => `
            <button class="trader-pill ${state.gaugeTraderIndex === i + 1 ? 'active' : ''}" data-trader="${i + 1}">${label}</button>
        `).join('');

        elements.gaugeTraderPills.innerHTML = pillsHTML;

        // Add click handlers
        elements.gaugeTraderPills.querySelectorAll('.trader-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                state.gaugeTraderIndex = parseInt(pill.dataset.trader);
                updateGaugePills();
                updateGauge();
            });
        });
    }

    function updateGauge() {
        if (!state.latestReport) return;

        const report = state.latestReport;

        // Use the dynamic traders array from the report
        const traders = report.traders || [];
        const traderIndex = state.gaugeTraderIndex - 1; // Convert to 0-based index

        // Get the selected trader's data
        const trader = traders[traderIndex] || traders[0] || { long: 0, short: 0, net: 0 };

        const longVal = trader.long || 0;
        const shortVal = trader.short || 0;
        const netVal = trader.net || 0;

        const total = longVal + shortVal;
        const longPct = total > 0 ? (longVal / total * 100) : 50;
        const shortPct = total > 0 ? (shortVal / total * 100) : 50;

        // Update gauge arcs (SVG path manipulation)
        // The arc goes from 20,100 to 180,100 with center at 100,100 and radius 80
        // We need to calculate the split point based on percentages
        const arcAngle = (longPct / 100) * Math.PI; // 0 to PI (half circle)
        const splitX = 100 - 80 * Math.cos(arcAngle);
        const splitY = 100 - 80 * Math.sin(arcAngle);

        // Long arc: from left (20,100) to split point
        elements.gaugeLongArc.setAttribute('d', `M 20 100 A 80 80 0 0 1 ${splitX.toFixed(1)} ${splitY.toFixed(1)}`);

        // Short arc: from split point to right (180,100)
        elements.gaugeShortArc.setAttribute('d', `M ${splitX.toFixed(1)} ${splitY.toFixed(1)} A 80 80 0 0 1 180 100`);

        // Update center text
        elements.gaugeLabel.textContent = netVal >= 0 ? 'Net Long' : 'Net Short';
        elements.gaugeValue.textContent = formatNumber(netVal);

        // Update legend
        elements.gaugeLongValue.textContent = formatCompact(longVal);
        elements.gaugeLongPct.textContent = longPct.toFixed(1) + '%';
        elements.gaugeShortValue.textContent = formatCompact(shortVal);
        elements.gaugeShortPct.textContent = shortPct.toFixed(1) + '%';
    }

    // ========================================================================
    // TRADER SUMMARY CARDS
    // ========================================================================

    function updateTraderSummary() {
        if (!state.chartData.length) return;

        const mapping = COTAPI.getFieldMapping(state.reportType);
        const hasTrader4 = state.reportType !== 'legacy';

        const latest = state.chartData[state.chartData.length - 1];
        const prev = state.chartData.length > 1 ? state.chartData[state.chartData.length - 2] : null;

        const traders = [
            { label: mapping.trader1_name, key: mapping.trader1_label },
            { label: mapping.trader2_name, key: mapping.trader2_label },
            { label: mapping.trader3_name, key: mapping.trader3_label }
        ];

        if (hasTrader4) {
            traders.push({ label: mapping.trader4_name, key: mapping.trader4_label });
        }

        elements.traderSummary.innerHTML = traders.map(trader => {
            const value = latest[trader.key] || 0;
            const prevValue = prev ? prev[trader.key] || 0 : 0;
            const change = prevValue !== 0 ? ((value - prevValue) / Math.abs(prevValue) * 100) : 0;
            const isPositive = value >= 0;
            const changePositive = change >= 0;

            return `
                <div class="trader-card">
                    <div class="trader-card-header">
                        <span class="trader-card-title">${trader.label}</span>
                        <span class="trader-card-badge ${changePositive ? 'positive' : 'negative'}">
                            ${changePositive ? '+' : ''}${change.toFixed(1)}%
                        </span>
                    </div>
                    <div class="trader-card-value ${isPositive ? 'positive' : 'negative'}">
                        ${formatNumber(value)}
                    </div>
                    <div class="trader-card-desc">Net Position</div>
                </div>
            `;
        }).join('');

        // Update grid columns based on number of traders
        elements.traderSummary.style.gridTemplateColumns = `repeat(${traders.length}, 1fr)`;
    }

    // ========================================================================
    // CHART
    // ========================================================================

    function setChartView(view) {
        state.chartView = view;
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        // Show/hide appropriate controls
        const isPercentile = view === 'percentile';
        elements.percentileTraderPills.classList.toggle('hidden', !isPercentile);
        elements.legendToggles.classList.toggle('hidden', isPercentile);

        // Recalculate percentile if switching to percentile view
        if (isPercentile) {
            // Default to trader1 (blue line) when switching to percentile
            state.percentileTrader = 'trader1';
            updatePercentileTraderPills();
            calculatePercentileData();
        }

        renderChart();
        updateMetricCards(); // Update metrics to show percentile data
    }

    function setPercentileTrader(trader) {
        state.percentileTrader = trader;
        updatePercentileTraderPills();
        calculatePercentileData();
        renderChart();
        updateMetricCards();
    }

    function updatePercentileTraderPills() {
        const mapping = COTAPI.getFieldMapping(state.reportType);
        const hasTrader4 = state.reportType !== 'legacy';

        // Update labels
        elements.pctlTrader1.textContent = mapping.trader1_name;
        elements.pctlTrader2.textContent = mapping.trader2_name;
        elements.pctlTrader3.textContent = mapping.trader3_name;
        if (elements.pctlTrader4) {
            elements.pctlTrader4.textContent = mapping.trader4_name || '';
        }

        // Show/hide trader4 pill
        const trader4Pill = elements.percentileTraderPills.querySelector('[data-trader="trader4"]');
        if (trader4Pill) {
            trader4Pill.classList.toggle('hidden', !hasTrader4);
        }

        // Update active state
        elements.percentileTraderPills.querySelectorAll('.trader-pill').forEach(pill => {
            pill.classList.toggle('active', pill.dataset.trader === state.percentileTrader);
        });
    }

    // ========================================================================
    // PERCENTILE CALCULATIONS
    // ========================================================================

    function calculatePercentileData() {
        if (!state.chartData || state.chartData.length === 0) {
            state.percentileHistory = [];
            state.percentileData = null;
            return;
        }

        const mapping = COTAPI.getFieldMapping(state.reportType);

        // Reverse data so newest is first (API returns oldest first)
        const reversedData = [...state.chartData].reverse();

        // Calculate percentile for each trader type
        state.percentileData = {
            trader1: COTAPI.calculatePercentileRank(reversedData, mapping.trader1_label, state.percentileLookback),
            trader2: COTAPI.calculatePercentileRank(reversedData, mapping.trader2_label, state.percentileLookback),
            trader3: COTAPI.calculatePercentileRank(reversedData, mapping.trader3_label, state.percentileLookback)
        };

        if (state.reportType !== 'legacy' && mapping.trader4_label) {
            state.percentileData.trader4 = COTAPI.calculatePercentileRank(reversedData, mapping.trader4_label, state.percentileLookback);
        }

        // Get the selected trader's label for percentile history
        const traderNum = state.percentileTrader.replace('trader', '');
        const traderLabel = mapping[`trader${traderNum}_label`] || mapping.trader1_label;

        // Generate percentile history for the selected trader
        state.percentileHistory = COTAPI.generatePercentileHistory(
            reversedData,
            traderLabel,
            state.percentileLookback,
            Math.min(104, reversedData.length) // 2 years of history points
        );

        // Validate data quality
        const validation = COTAPI.validateDataQuality(state.chartData, state.selectedSymbol);
        if (validation.warnings.length > 0) {
            console.warn('Data quality warnings:', validation.warnings);
        }
    }

    function setChartType(type) {
        state.chartType = type;
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });
        renderChart();
    }

    function setZoom(years) {
        state.zoomYears = years;
        document.querySelectorAll('.zoom-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.zoom) === years);
        });
        renderChart();
    }

    /**
     * Filter data by years from present
     * @param {Array} data - Array of data points with 'date' property
     * @param {number} years - Number of years to show (0 = all)
     * @returns {Array} Filtered data
     */
    function filterDataByYears(data, years) {
        if (!data || !data.length || years === 0) {
            return data;
        }

        const now = new Date();
        const cutoffDate = new Date(now.getFullYear() - years, now.getMonth(), now.getDate());
        const cutoffStr = cutoffDate.toISOString().split('T')[0];

        return data.filter(d => d.date >= cutoffStr);
    }

    function toggleSeries(series) {
        const btn = document.querySelector(`.legend-btn[data-series="${series}"]`);
        const stateKey = `showTrader${series.replace('trader', '')}`;

        state[stateKey] = !state[stateKey];
        btn.classList.toggle('active', state[stateKey]);

        renderChart();
    }

    function renderChart() {
        if (!state.chartData.length) {
            Plotly.purge(elements.mainChart);
            return;
        }

        // Route to appropriate chart renderer
        if (state.chartView === 'percentile') {
            renderPercentileChart();
        } else {
            renderPositionChart();
        }
    }

    function renderPositionChart() {
        const mapping = COTAPI.getFieldMapping(state.reportType);
        const hasTrader4 = state.reportType !== 'legacy';

        // Apply year-based zoom filter
        const data = filterDataByYears(state.chartData, state.zoomYears);

        const dates = data.map(d => d.date);

        // Colors
        const colors = {
            trader1: '#60A5FA',
            trader2: '#F87171',
            trader3: '#34D399',
            trader4: '#A78BFA'
        };

        const traces = [];

        // Trader 1
        if (state.showTrader1) {
            const values = data.map(d => d[mapping.trader1_label] || 0);
            traces.push(createTrace(dates, values, mapping.trader1_name, colors.trader1));
        }

        // Trader 2
        if (state.showTrader2) {
            const values = data.map(d => d[mapping.trader2_label] || 0);
            traces.push(createTrace(dates, values, mapping.trader2_name, colors.trader2));
        }

        // Trader 3
        if (state.showTrader3) {
            const values = data.map(d => d[mapping.trader3_label] || 0);
            traces.push(createTrace(dates, values, mapping.trader3_name, colors.trader3));
        }

        // Trader 4 (if applicable)
        if (hasTrader4 && state.showTrader4 && mapping.trader4_label) {
            const values = data.map(d => d[mapping.trader4_label] || 0);
            traces.push(createTrace(dates, values, mapping.trader4_name, colors.trader4));
        }

        // Layout
        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                family: 'Inter, system-ui, sans-serif',
                size: 11,
                color: state.isDarkMode ? '#9AA3B2' : '#475569'
            },
            margin: { l: 60, r: 30, t: 20, b: 60 },
            xaxis: {
                gridcolor: state.isDarkMode ? 'rgba(255,255,255,0.025)' : 'rgba(0,0,0,0.04)',
                showgrid: true,
                tickformat: data.length > 200 ? '%Y' : "%b '%y",
                tickangle: 0,
                showline: false
            },
            yaxis: {
                gridcolor: state.isDarkMode ? 'rgba(255,255,255,0.025)' : 'rgba(0,0,0,0.04)',
                showgrid: true,
                tickformat: ',.0f',
                zeroline: true,
                zerolinecolor: state.isDarkMode ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.1)',
                zerolinewidth: 2,
                showline: false
            },
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.02,
                xanchor: 'left',
                x: 0,
                bgcolor: 'rgba(0,0,0,0)'
            },
            hovermode: 'x unified',
            barmode: 'group',
            bargap: 0.15,
            hoverlabel: {
                bgcolor: state.isDarkMode ? '#0F1420' : '#ffffff',
                font_size: 11,
                bordercolor: state.isDarkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.1)'
            }
        };

        const config = {
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot(elements.mainChart, traces, layout, config);
    }

    function renderPercentileChart() {
        if (!state.percentileHistory || state.percentileHistory.length === 0) {
            calculatePercentileData();
            if (!state.percentileHistory || state.percentileHistory.length === 0) {
                Plotly.purge(elements.mainChart);
                return;
            }
        }

        // Apply year-based zoom filter to percentile history
        const data = filterDataByYears(state.percentileHistory, state.zoomYears);

        const dates = data.map(d => d.date);
        const percentiles = data.map(d => d.percentile);

        // Get color based on selected trader
        const traderColors = {
            trader1: '#60A5FA', // Blue
            trader2: '#F87171', // Red
            trader3: '#34D399', // Green
            trader4: '#A78BFA'  // Purple
        };
        const lineColor = traderColors[state.percentileTrader] || '#60A5FA';
        const fillColor = lineColor.replace(')', ', 0.15)').replace('rgb', 'rgba').replace('#', '');

        // Convert hex to rgba for fill
        const hexToRgba = (hex, alpha) => {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        };

        const mapping = COTAPI.getFieldMapping(state.reportType);
        const traderNum = state.percentileTrader.replace('trader', '');
        const traderName = mapping[`trader${traderNum}_name`] || 'Trader';

        const traces = [];

        // Main percentile line
        traces.push({
            x: dates,
            y: percentiles,
            name: `${traderName} Percentile`,
            type: 'scatter',
            mode: 'lines',
            line: { color: lineColor, width: 2.5 },
            fill: 'tozeroy',
            fillcolor: hexToRgba(lineColor, 0.15)
        });

        // Add current value marker
        if (percentiles.length > 0) {
            const currentPct = percentiles[percentiles.length - 1];
            const currentDate = dates[dates.length - 1];

            traces.push({
                x: [currentDate],
                y: [currentPct],
                name: 'Current',
                type: 'scatter',
                mode: 'markers+text',
                marker: {
                    size: 12,
                    color: lineColor,
                    line: { width: 2, color: 'white' }
                },
                text: [`${currentPct.toFixed(0)}%`],
                textposition: 'top center',
                textfont: { size: 12, color: lineColor }
            });
        }

        // Layout with reference zones
        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                family: 'Inter, system-ui, sans-serif',
                size: 11,
                color: state.isDarkMode ? '#9AA3B2' : '#475569'
            },
            margin: { l: 50, r: 30, t: 20, b: 50 },
            xaxis: {
                gridcolor: state.isDarkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
                showgrid: true,
                tickformat: "%b '%y",
                tickangle: 0,
                showline: false
            },
            yaxis: {
                gridcolor: state.isDarkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
                showgrid: true,
                range: [0, 100],
                dtick: 25,
                ticksuffix: '%',
                showline: false
            },
            shapes: [
                // Bullish extreme zone (90-100)
                {
                    type: 'rect',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 90, y1: 100,
                    fillcolor: 'rgba(16, 185, 129, 0.1)',
                    line: { width: 0 }
                },
                // Bullish zone (75-90)
                {
                    type: 'rect',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 75, y1: 90,
                    fillcolor: 'rgba(16, 185, 129, 0.05)',
                    line: { width: 0 }
                },
                // Bearish zone (10-25)
                {
                    type: 'rect',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 10, y1: 25,
                    fillcolor: 'rgba(239, 68, 68, 0.05)',
                    line: { width: 0 }
                },
                // Bearish extreme zone (0-10)
                {
                    type: 'rect',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 0, y1: 10,
                    fillcolor: 'rgba(239, 68, 68, 0.1)',
                    line: { width: 0 }
                },
                // 75% line
                {
                    type: 'line',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 75, y1: 75,
                    line: { color: '#22c55e', width: 1, dash: 'dash' }
                },
                // 50% line
                {
                    type: 'line',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 50, y1: 50,
                    line: { color: 'rgba(255,255,255,0.3)', width: 1, dash: 'dash' }
                },
                // 25% line
                {
                    type: 'line',
                    xref: 'paper',
                    yref: 'y',
                    x0: 0, x1: 1,
                    y0: 25, y1: 25,
                    line: { color: '#ef4444', width: 1, dash: 'dash' }
                }
            ],
            annotations: [
                {
                    x: 1,
                    y: 95,
                    xref: 'paper',
                    yref: 'y',
                    text: 'Bullish Extreme',
                    showarrow: false,
                    font: { size: 10, color: '#10b981' },
                    xanchor: 'right'
                },
                {
                    x: 1,
                    y: 5,
                    xref: 'paper',
                    yref: 'y',
                    text: 'Bearish Extreme',
                    showarrow: false,
                    font: { size: 10, color: '#ef4444' },
                    xanchor: 'right'
                }
            ],
            showlegend: false,
            hovermode: 'x unified',
            hoverlabel: {
                bgcolor: state.isDarkMode ? '#1a1f3a' : '#ffffff',
                font_size: 12,
                bordercolor: state.isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
            }
        };

        const config = {
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot(elements.mainChart, traces, layout, config);
    }

    function createTrace(dates, values, name, color) {
        if (state.chartType === 'bar') {
            return {
                x: dates,
                y: values,
                name: name,
                type: 'bar',
                marker: {
                    color: color,
                    line: { color: color, width: 1 }
                },
                opacity: 0.9
            };
        } else {
            return {
                x: dates,
                y: values,
                name: name,
                type: 'scatter',
                mode: 'lines',
                line: { color: color, width: 2.5 }
            };
        }
    }

    // ========================================================================
    // METRIC CARDS
    // ========================================================================

    function updateMetricCards() {
        if (!state.latestReport) return;

        const report = state.latestReport;
        const mapping = COTAPI.getFieldMapping(state.reportType);

        let metrics;

        if (state.chartView === 'percentile' && state.percentileData) {
            // Show percentile metrics
            const pct1 = state.percentileData.trader1;
            const pct2 = state.percentileData.trader2;
            const pct3 = state.percentileData.trader3;

            metrics = [
                {
                    title: `${mapping.trader1_name} Pctl`,
                    value: pct1 ? `${pct1.percentile.toFixed(0)}%` : '--',
                    percentile: pct1?.percentile || 50,
                    interpretation: pct1?.interpretation || '',
                    icon: 'percent'
                },
                {
                    title: `${mapping.trader2_name} Pctl`,
                    value: pct2 ? `${pct2.percentile.toFixed(0)}%` : '--',
                    percentile: pct2?.percentile || 50,
                    interpretation: pct2?.interpretation || '',
                    icon: 'percent'
                },
                {
                    title: `${mapping.trader3_name} Pctl`,
                    value: pct3 ? `${pct3.percentile.toFixed(0)}%` : '--',
                    percentile: pct3?.percentile || 50,
                    interpretation: pct3?.interpretation || '',
                    icon: 'percent'
                },
                {
                    title: 'Lookback Period',
                    value: `${Math.round(state.percentileLookback / 52)}Y`,
                    percentile: null,
                    interpretation: `${state.percentileLookback} weeks`,
                    icon: 'calendar'
                }
            ];

            elements.metricsGrid.innerHTML = metrics.map(metric => {
                const pctColor = metric.percentile !== null ? COTAPI.getPercentileColor(metric.percentile) : '#3b82f6';
                return `
                    <div class="metric-card">
                        <div class="metric-card-header">
                            <span class="metric-card-title">${metric.title}</span>
                            <div class="metric-card-icon" style="background: ${pctColor}20; color: ${pctColor}">
                                <i data-lucide="${metric.icon}"></i>
                            </div>
                        </div>
                        <div class="metric-card-value" style="color: ${pctColor}">${metric.value}</div>
                        <div class="metric-card-change" style="color: var(--text-muted); font-size: 11px;">
                            ${metric.interpretation}
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            // Show position metrics
            metrics = [
                {
                    title: 'Open Interest',
                    value: formatCompact(report.openInterest),
                    change: report.oiChange,
                    icon: 'activity'
                },
                {
                    title: 'NC Long',
                    value: formatCompact(report.nonCommercialLong),
                    change: null,
                    icon: 'trending-up'
                },
                {
                    title: 'NC Short',
                    value: formatCompact(report.nonCommercialShort),
                    change: null,
                    icon: 'trending-down'
                },
                {
                    title: 'Comm Net',
                    value: formatNumber(report.commercialNet),
                    change: report.commercialChange,
                    icon: 'building'
                }
            ];

            elements.metricsGrid.innerHTML = metrics.map(metric => `
                <div class="metric-card">
                    <div class="metric-card-header">
                        <span class="metric-card-title">${metric.title}</span>
                        <div class="metric-card-icon">
                            <i data-lucide="${metric.icon}"></i>
                        </div>
                    </div>
                    <div class="metric-card-value">${metric.value}</div>
                    ${metric.change !== null ? `
                        <div class="metric-card-change ${metric.change >= 0 ? 'positive' : 'negative'}">
                            <i data-lucide="${metric.change >= 0 ? 'arrow-up' : 'arrow-down'}"></i>
                            ${formatChange(metric.change)}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }

        initializeIcons();
    }

    // ========================================================================
    // CATEGORIES
    // ========================================================================

    function renderCategories() {
        const categories = Object.entries(COTAPI.ASSET_CATEGORIES);

        elements.assetCategories.innerHTML = categories.map(([category, assets]) => {
            const info = COTAPI.CATEGORY_INFO[category];
            const isExpanded = state.expandedCategories.has(category);

            return `
                <div class="category-section ${isExpanded ? 'expanded' : ''}" data-category="${category}">
                    <div class="category-header">
                        <div class="category-accent" style="background: ${info.color}"></div>
                        <i data-lucide="${info.icon}" style="color: ${info.color}"></i>
                        <span class="category-name">${category}</span>
                        <span class="category-count">(${assets.length})</span>
                        <i data-lucide="chevron-down" class="chevron"></i>
                    </div>
                    <div class="category-assets">
                        ${assets.map(asset => `
                            <div class="asset-chip ${asset.symbol === state.selectedSymbol ? 'selected' : ''}"
                                 data-symbol="${asset.symbol}"
                                 data-category="${category}"
                                 style="--category-color: ${info.color}">
                                <span class="asset-name">${asset.name}</span>
                                <span class="asset-symbol">${asset.symbol}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');

        // Add event listeners
        elements.assetCategories.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', () => {
                const section = header.closest('.category-section');
                const category = section.dataset.category;

                if (state.expandedCategories.has(category)) {
                    state.expandedCategories.delete(category);
                } else {
                    state.expandedCategories.add(category);
                }

                section.classList.toggle('expanded');
            });
        });

        elements.assetCategories.querySelectorAll('.asset-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                e.stopPropagation();
                const symbol = chip.dataset.symbol;
                const category = chip.dataset.category;
                const asset = COTAPI.getAllAssets().find(a => a.symbol === symbol);
                if (asset) {
                    selectAsset(symbol, asset.name, category);
                }
            });
        });

        initializeIcons();
    }

    // ========================================================================
    // WATCHLIST
    // ========================================================================

    function renderWatchlist() {
        elements.watchlistItems.innerHTML = state.watchlist.map(item => {
            const categoryColor = COTAPI.CATEGORY_INFO[item.category]?.color || '#3b82f6';
            return `
                <div class="watchlist-item" data-symbol="${item.symbol}">
                    <span class="item-symbol">${item.symbol}</span>
                    <span class="item-name">${item.name}</span>
                    <span class="signal-dot" style="background: ${categoryColor}; box-shadow: 0 0 6px ${categoryColor}"></span>
                    <button class="remove-btn" data-symbol="${item.symbol}">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            `;
        }).join('');

        // Update badges
        elements.watchlistBadge.textContent = state.watchlist.length;
        elements.watchlistCountNav.textContent = state.watchlist.length;

        // Add event listeners
        elements.watchlistItems.querySelectorAll('.watchlist-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.closest('.remove-btn')) return;
                const symbol = item.dataset.symbol;
                const watchlistItem = state.watchlist.find(w => w.symbol === symbol);
                if (watchlistItem) {
                    selectAsset(symbol, watchlistItem.name, watchlistItem.category);
                }
            });
        });

        elements.watchlistItems.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const symbol = btn.dataset.symbol;
                removeFromWatchlist(symbol);
            });
        });

        initializeIcons();
    }

    function toggleWatchlist() {
        const isInWatchlist = state.watchlist.some(w => w.symbol === state.selectedSymbol);

        if (isInWatchlist) {
            removeFromWatchlist(state.selectedSymbol);
        } else {
            addToWatchlist();
        }
    }

    function addToWatchlist() {
        if (!state.watchlist.some(w => w.symbol === state.selectedSymbol)) {
            state.watchlist.push({
                symbol: state.selectedSymbol,
                name: state.selectedName,
                category: state.selectedCategory
            });
            renderWatchlist();
            elements.watchlistToggle.classList.add('active');
        }
    }

    function removeFromWatchlist(symbol) {
        state.watchlist = state.watchlist.filter(w => w.symbol !== symbol);
        renderWatchlist();

        if (symbol === state.selectedSymbol) {
            elements.watchlistToggle.classList.remove('active');
        }
    }

    // ========================================================================
    // UTILITY FUNCTIONS
    // ========================================================================

    function formatNumber(num) {
        if (num === undefined || num === null) return '--';
        const sign = num >= 0 ? '+' : '';
        return sign + num.toLocaleString();
    }

    function formatCompact(num) {
        if (num === undefined || num === null) return '--';
        if (Math.abs(num) >= 1000000) {
            return (num / 1000000).toFixed(2) + 'M';
        } else if (Math.abs(num) >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }

    function formatChange(num) {
        if (num === undefined || num === null) return '--';
        const sign = num >= 0 ? '+' : '';
        return sign + num.toLocaleString();
    }

    // ========================================================================
    // INITIALIZE
    // ========================================================================

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
