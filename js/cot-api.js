/**
 * COT Data API Module
 * Fetches real CFTC Commitment of Traders data from Socrata API
 */

const COTAPI = (function() {
    'use strict';

    // CFTC API Configuration
    const API_ENDPOINT = 'https://publicreporting.cftc.gov/resource';
    const API_KEY = 'Z1eALyOoL0nekg4wimFpmGIm5';

    // Dataset IDs for different report types
    const DATASET_IDS = {
        legacy: '6dca-aqww',
        disaggregated: '72hh-3qpy',
        tff: 'gpe5-46if'
    };

    // Field mappings for each report type
    const REPORT_FIELD_MAPPINGS = {
        legacy: {
            trader1: ['noncomm_positions_long_all', 'noncomm_positions_short_all'],
            trader2: ['comm_positions_long_all', 'comm_positions_short_all'],
            trader3: ['nonrept_positions_long_all', 'nonrept_positions_short_all'],
            trader1_label: 'non_commercial',
            trader2_label: 'commercial',
            trader3_label: 'non_reportable',
            trader1_name: 'Non-Commercial',
            trader2_name: 'Commercial',
            trader3_name: 'Non-Reportable'
        },
        disaggregated: {
            trader1: ['prod_merc_positions_long', 'prod_merc_positions_short'],
            trader2: ['swap_positions_long_all', 'swap__positions_short_all'],
            trader3: ['m_money_positions_long_all', 'm_money_positions_short_all'],
            trader4: ['other_rept_positions_long', 'other_rept_positions_short'],
            trader1_label: 'producer_merchant',
            trader2_label: 'swap_dealer',
            trader3_label: 'managed_money',
            trader4_label: 'other_reportable',
            trader1_name: 'Producer/Merchant',
            trader2_name: 'Swap Dealer',
            trader3_name: 'Managed Money',
            trader4_name: 'Other Reportable'
        },
        tff: {
            trader1: ['dealer_positions_long_all', 'dealer_positions_short_all'],
            trader2: ['asset_mgr_positions_long', 'asset_mgr_positions_short'],
            trader3: ['lev_money_positions_long', 'lev_money_positions_short'],
            trader4: ['other_rept_positions_long', 'other_rept_positions_short'],
            trader1_label: 'dealer',
            trader2_label: 'asset_manager',
            trader3_label: 'leveraged_funds',
            trader4_label: 'other_reportable',
            trader1_name: 'Dealer',
            trader2_name: 'Asset Manager',
            trader3_name: 'Leveraged Funds',
            trader4_name: 'Other Reportable'
        }
    };

    // Symbol to CFTC Contract Name Mapping (Legacy)
    const SYMBOL_TO_CONTRACT = {
        // Energy
        CL: [
            'CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE',
            'WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE'
        ],
        NG: [
            'NATURAL GAS - NEW YORK MERCANTILE EXCHANGE',
            'NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE'
        ],
        RB: [
            'GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE',
            'GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE'
        ],
        HO: [
            'NO. 2 HEATING OIL, N.Y. HARBOR - NEW YORK MERCANTILE EXCHANGE',
            '#2 HEATING OIL- NY HARBOR-ULSD - NEW YORK MERCANTILE EXCHANGE',
            'NY HARBOR ULSD - NEW YORK MERCANTILE EXCHANGE'
        ],
        BZ: [
            'BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE',
            'BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE'
        ],

        // Metals
        GC: ['GOLD - COMMODITY EXCHANGE INC.'],
        SI: ['SILVER - COMMODITY EXCHANGE INC.'],
        HG: ['COPPER-GRADE #1 - COMMODITY EXCHANGE INC.'],
        PL: ['PLATINUM - NEW YORK MERCANTILE EXCHANGE'],
        PA: ['PALLADIUM - NEW YORK MERCANTILE EXCHANGE'],

        // Grains
        ZC: ['CORN - CHICAGO BOARD OF TRADE'],
        ZS: ['SOYBEANS - CHICAGO BOARD OF TRADE'],
        ZW: ['WHEAT-SRW - CHICAGO BOARD OF TRADE'],
        ZM: ['SOYBEAN MEAL - CHICAGO BOARD OF TRADE'],
        ZL: ['SOYBEAN OIL - CHICAGO BOARD OF TRADE'],
        ZO: ['OATS - CHICAGO BOARD OF TRADE'],
        KE: ['WHEAT-HRW - CHICAGO BOARD OF TRADE'],
        ZR: ['ROUGH RICE - CHICAGO BOARD OF TRADE'],

        // Softs
        CT: ['COTTON NO. 2 - ICE FUTURES U.S.'],
        KC: ['COFFEE C - ICE FUTURES U.S.'],
        SB: ['SUGAR NO. 11 - ICE FUTURES U.S.'],
        CC: ['COCOA - ICE FUTURES U.S.'],
        OJ: ['FRZN CONCENTRATED ORANGE JUICE - ICE FUTURES U.S.'],

        // Livestock
        LE: ['LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE'],
        HE: ['LEAN HOGS - CHICAGO MERCANTILE EXCHANGE'],
        GF: ['FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE'],

        // Equities
        ES: [
            'E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE',
            'E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE'
        ],
        NQ: [
            'NASDAQ-100 STOCK INDEX (MINI) - CHICAGO MERCANTILE EXCHANGE',
            'NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE',
            'NASDAQ-100 (MINI) - CHICAGO MERCANTILE EXCHANGE'
        ],
        YM: [
            'DJIA x $5 - CHICAGO BOARD OF TRADE',
            'DOW JONES INDUSTRIAL AVG- x $5 - CHICAGO BOARD OF TRADE',
            'DJIA Consolidated - CHICAGO BOARD OF TRADE'
        ],
        RTY: [
            'RUSSELL 2000 MINI - CHICAGO MERCANTILE EXCHANGE',
            'RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE'
        ],
        VX: ['VIX FUTURES - CBOE FUTURES EXCHANGE'],
        NKD: ['NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE'],

        // Currencies
        '6E': ['EURO FX - CHICAGO MERCANTILE EXCHANGE'],
        '6J': [
            'JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE',
            'JPN YEN - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6B': [
            'BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE',
            'BRITISH POUND - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6A': [
            'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE',
            'AUD DOLLAR - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6C': [
            'CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE',
            'CAD DOLLAR - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6S': [
            'SWISS FRANC - CHICAGO MERCANTILE EXCHANGE',
            'CHF FRANC - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6N': [
            'NEW ZEALAND DOLLAR - CHICAGO MERCANTILE EXCHANGE',
            'NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6M': [
            'MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE',
            'MXN PESO - CHICAGO MERCANTILE EXCHANGE'
        ],
        DX: [
            'U.S. DOLLAR INDEX - ICE FUTURES U.S.',
            'USD INDEX - ICE FUTURES U.S.'
        ],
        BTC: ['BITCOIN - CHICAGO MERCANTILE EXCHANGE'],

        // Treasuries
        ZB: ['U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE'],
        ZN: ['10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'],
        ZF: ['5-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'],
        ZT: ['2-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'],
        UB: ['ULTRA U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE'],
        TN: ['ULTRA 10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE']
    };

    // TFF Contract Name Mapping
    const SYMBOL_TO_CONTRACT_TFF = {
        ES: [
            'E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE',
            'E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE'
        ],
        NQ: [
            'NASDAQ-100 STOCK INDEX (MINI) - CHICAGO MERCANTILE EXCHANGE',
            'NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE'
        ],
        YM: [
            'DJIA x $5 - CHICAGO BOARD OF TRADE',
            'DOW JONES INDUSTRIAL AVG- x $5 - CHICAGO BOARD OF TRADE'
        ],
        RTY: [
            'RUSSELL 2000 MINI - CHICAGO MERCANTILE EXCHANGE',
            'RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE'
        ],
        VX: ['VIX FUTURES - CBOE FUTURES EXCHANGE'],
        NKD: ['NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE'],
        '6E': ['EURO FX - CHICAGO MERCANTILE EXCHANGE'],
        '6J': [
            'JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE',
            'JPN YEN - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6B': [
            'BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE',
            'BRITISH POUND - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6A': [
            'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE',
            'AUD DOLLAR - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6C': [
            'CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE',
            'CAD DOLLAR - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6S': [
            'SWISS FRANC - CHICAGO MERCANTILE EXCHANGE',
            'CHF FRANC - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6N': [
            'NEW ZEALAND DOLLAR - CHICAGO MERCANTILE EXCHANGE',
            'NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE'
        ],
        '6M': [
            'MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE',
            'MXN PESO - CHICAGO MERCANTILE EXCHANGE'
        ],
        DX: [
            'U.S. DOLLAR INDEX - ICE FUTURES U.S.',
            'USD INDEX - ICE FUTURES U.S.'
        ],
        BTC: ['BITCOIN - CHICAGO MERCANTILE EXCHANGE'],
        ZB: [
            'UST BOND - CHICAGO BOARD OF TRADE',
            'U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE'
        ],
        ZN: [
            '10 YR UST NOTE - CHICAGO BOARD OF TRADE',
            '10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'
        ],
        ZF: [
            '5 YR UST NOTE - CHICAGO BOARD OF TRADE',
            '5-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'
        ],
        ZT: [
            '2 YR UST NOTE - CHICAGO BOARD OF TRADE',
            '2-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'
        ],
        UB: [
            'ULTRA UST BOND - CHICAGO BOARD OF TRADE',
            'ULTRA U.S. TREASURY BONDS - CHICAGO BOARD OF TRADE'
        ],
        TN: [
            'ULTRA 10 YR UST NOTE - CHICAGO BOARD OF TRADE',
            'ULTRA 10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE'
        ]
    };

    // Disaggregated Contract Name Mapping
    const SYMBOL_TO_CONTRACT_DISAGG = {
        CL: [
            'CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE',
            'WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE'
        ],
        NG: [
            'NATURAL GAS - NEW YORK MERCANTILE EXCHANGE',
            'NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE'
        ],
        RB: [
            'GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE',
            'GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE'
        ],
        HO: [
            'NO. 2 HEATING OIL, N.Y. HARBOR - NEW YORK MERCANTILE EXCHANGE',
            '#2 HEATING OIL- NY HARBOR-ULSD - NEW YORK MERCANTILE EXCHANGE',
            'NY HARBOR ULSD - NEW YORK MERCANTILE EXCHANGE'
        ],
        BZ: [
            'BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE',
            'BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE'
        ],
        GC: ['GOLD - COMMODITY EXCHANGE INC.'],
        SI: ['SILVER - COMMODITY EXCHANGE INC.'],
        HG: [
            'COPPER-GRADE #1 - COMMODITY EXCHANGE INC.',
            'COPPER- #1 - COMMODITY EXCHANGE INC.'
        ],
        PL: ['PLATINUM - NEW YORK MERCANTILE EXCHANGE'],
        PA: ['PALLADIUM - NEW YORK MERCANTILE EXCHANGE'],
        ZC: ['CORN - CHICAGO BOARD OF TRADE'],
        ZS: ['SOYBEANS - CHICAGO BOARD OF TRADE'],
        ZW: [
            'WHEAT-SRW - CHICAGO BOARD OF TRADE',
            'WHEAT - CHICAGO BOARD OF TRADE'
        ],
        ZM: ['SOYBEAN MEAL - CHICAGO BOARD OF TRADE'],
        ZL: ['SOYBEAN OIL - CHICAGO BOARD OF TRADE'],
        ZO: ['OATS - CHICAGO BOARD OF TRADE'],
        KE: [
            'WHEAT-HRW - CHICAGO BOARD OF TRADE',
            'WHEAT-HRW - KANSAS CITY BOARD OF TRADE'
        ],
        ZR: ['ROUGH RICE - CHICAGO BOARD OF TRADE'],
        CT: ['COTTON NO. 2 - ICE FUTURES U.S.'],
        KC: ['COFFEE C - ICE FUTURES U.S.'],
        SB: ['SUGAR NO. 11 - ICE FUTURES U.S.'],
        CC: ['COCOA - ICE FUTURES U.S.'],
        OJ: ['FRZN CONCENTRATED ORANGE JUICE - ICE FUTURES U.S.'],
        LE: ['LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE'],
        HE: ['LEAN HOGS - CHICAGO MERCANTILE EXCHANGE'],
        GF: ['FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE']
    };

    // Asset Categories
    const ASSET_CATEGORIES = {
        Equities: [
            { symbol: 'ES', name: 'E-Mini S&P 500' },
            { symbol: 'NQ', name: 'E-Mini Nasdaq 100' },
            { symbol: 'YM', name: 'E-Mini Dow Jones' },
            { symbol: 'RTY', name: 'E-Mini Russell 2000' },
            { symbol: 'VX', name: 'VIX Futures' },
            { symbol: 'NKD', name: 'Nikkei 225' }
        ],
        Energy: [
            { symbol: 'CL', name: 'Crude Oil WTI' },
            { symbol: 'BZ', name: 'Brent Crude Oil' },
            { symbol: 'NG', name: 'Natural Gas' },
            { symbol: 'RB', name: 'RBOB Gasoline' },
            { symbol: 'HO', name: 'Heating Oil' }
        ],
        Metals: [
            { symbol: 'GC', name: 'Gold' },
            { symbol: 'SI', name: 'Silver' },
            { symbol: 'HG', name: 'Copper' },
            { symbol: 'PL', name: 'Platinum' },
            { symbol: 'PA', name: 'Palladium' }
        ],
        Grains: [
            { symbol: 'ZC', name: 'Corn' },
            { symbol: 'ZS', name: 'Soybeans' },
            { symbol: 'ZW', name: 'Wheat (SRW)' },
            { symbol: 'KE', name: 'Wheat (HRW)' },
            { symbol: 'ZM', name: 'Soybean Meal' },
            { symbol: 'ZL', name: 'Soybean Oil' },
            { symbol: 'ZO', name: 'Oats' },
            { symbol: 'ZR', name: 'Rough Rice' }
        ],
        Softs: [
            { symbol: 'CT', name: 'Cotton' },
            { symbol: 'KC', name: 'Coffee' },
            { symbol: 'SB', name: 'Sugar' },
            { symbol: 'CC', name: 'Cocoa' },
            { symbol: 'OJ', name: 'Orange Juice' }
        ],
        Livestock: [
            { symbol: 'LE', name: 'Live Cattle' },
            { symbol: 'HE', name: 'Lean Hogs' },
            { symbol: 'GF', name: 'Feeder Cattle' }
        ],
        Currencies: [
            { symbol: '6E', name: 'Euro FX' },
            { symbol: '6J', name: 'Japanese Yen' },
            { symbol: '6B', name: 'British Pound' },
            { symbol: '6A', name: 'Australian Dollar' },
            { symbol: '6C', name: 'Canadian Dollar' },
            { symbol: '6S', name: 'Swiss Franc' },
            { symbol: '6N', name: 'New Zealand Dollar' },
            { symbol: '6M', name: 'Mexican Peso' },
            { symbol: 'DX', name: 'US Dollar Index' },
            { symbol: 'BTC', name: 'Bitcoin' }
        ],
        Treasuries: [
            { symbol: 'ZB', name: '30-Year T-Bond' },
            { symbol: 'ZN', name: '10-Year T-Note' },
            { symbol: 'ZF', name: '5-Year T-Note' },
            { symbol: 'ZT', name: '2-Year T-Note' },
            { symbol: 'UB', name: 'Ultra T-Bond' },
            { symbol: 'TN', name: 'Ultra 10-Year' }
        ]
    };

    // Category display info
    const CATEGORY_INFO = {
        Equities: { icon: 'trending-up', color: '#3b82f6' },
        Energy: { icon: 'zap', color: '#f97316' },
        Metals: { icon: 'circle', color: '#eab308' },
        Grains: { icon: 'leaf', color: '#84cc16' },
        Softs: { icon: 'package', color: '#a855f7' },
        Livestock: { icon: 'box', color: '#ec4899' },
        Currencies: { icon: 'dollar-sign', color: '#06b6d4' },
        Treasuries: { icon: 'building', color: '#64748b' }
    };

    // Cache for API responses
    const cache = new Map();
    const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

    /**
     * Get contract names for a symbol based on report type
     */
    function getContractNames(symbol, reportType) {
        if (reportType === 'tff') {
            return SYMBOL_TO_CONTRACT_TFF[symbol] || [];
        } else if (reportType === 'disaggregated') {
            return SYMBOL_TO_CONTRACT_DISAGG[symbol] || [];
        }
        return SYMBOL_TO_CONTRACT[symbol] || [];
    }

    /**
     * Make API request
     */
    async function apiRequest(datasetId, params) {
        const url = new URL(`${API_ENDPOINT}/${datasetId}.json`);
        url.searchParams.append('$$app_token', API_KEY);

        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });

        const response = await fetch(url.toString());

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return response.json();
    }

    /**
     * Fetch latest COT report for a symbol
     */
    async function fetchLatestReport(symbol, reportType = 'legacy') {
        const cacheKey = `latest_${symbol}_${reportType}`;
        const cached = cache.get(cacheKey);

        if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
            return cached.data;
        }

        const contractNames = getContractNames(symbol, reportType);
        if (!contractNames.length) {
            return getEmptyReport(reportType);
        }

        const datasetId = DATASET_IDS[reportType] || DATASET_IDS.legacy;

        try {
            const allResults = [];

            for (const contractName of contractNames) {
                const results = await apiRequest(datasetId, {
                    $limit: 1,
                    $where: `market_and_exchange_names = '${contractName}'`,
                    $order: 'report_date_as_yyyy_mm_dd DESC'
                });

                if (results && results.length) {
                    allResults.push(...results);
                }
            }

            if (!allResults.length) {
                return getEmptyReport(reportType);
            }

            // Get the most recent report
            const mostRecent = allResults.reduce((latest, current) => {
                const latestDate = latest.report_date_as_yyyy_mm_dd || '';
                const currentDate = current.report_date_as_yyyy_mm_dd || '';
                return currentDate > latestDate ? current : latest;
            });

            const report = processLatestReport(mostRecent, reportType);

            cache.set(cacheKey, { data: report, timestamp: Date.now() });

            return report;
        } catch (error) {
            console.error(`Error fetching ${symbol}:`, error);
            return getEmptyReport(reportType);
        }
    }

    /**
     * Fetch historical COT data for charts
     */
    async function fetchHistoricalData(symbol, reportType = 'legacy') {
        const cacheKey = `historical_${symbol}_${reportType}`;
        const cached = cache.get(cacheKey);

        if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
            return cached.data;
        }

        const contractNames = getContractNames(symbol, reportType);
        if (!contractNames.length) {
            console.log(`No contract names found for ${symbol} (${reportType})`);
            return [];
        }

        const datasetId = DATASET_IDS[reportType] || DATASET_IDS.legacy;
        const fieldMapping = REPORT_FIELD_MAPPINGS[reportType] || REPORT_FIELD_MAPPINGS.legacy;

        try {
            const allRecords = [];

            for (const contractName of contractNames) {
                let offset = 0;
                const batchSize = 50000;

                while (true) {
                    const results = await apiRequest(datasetId, {
                        $limit: batchSize,
                        $offset: offset,
                        $where: `market_and_exchange_names = '${contractName}'`,
                        $order: 'report_date_as_yyyy_mm_dd ASC'
                    });

                    if (!results || !results.length) break;

                    allRecords.push(...results);

                    if (results.length < batchSize) break;
                    offset += batchSize;
                }
            }

            if (!allRecords.length) {
                return [];
            }

            // Process into chart format
            const chartData = processHistoricalData(allRecords, fieldMapping);

            cache.set(cacheKey, { data: chartData, timestamp: Date.now() });

            return chartData;
        } catch (error) {
            console.error(`Error fetching historical data for ${symbol}:`, error);
            return [];
        }
    }

    /**
     * Process raw API data into chart format
     */
    function processHistoricalData(records, fieldMapping) {
        // Create a map to handle duplicates
        const dateMap = new Map();

        records.forEach(record => {
            const date = record.report_date_as_yyyy_mm_dd;
            if (!date) return;

            const safeNum = (val) => parseInt(val) || 0;

            const [t1Long, t1Short] = fieldMapping.trader1;
            const [t2Long, t2Short] = fieldMapping.trader2;
            const [t3Long, t3Short] = fieldMapping.trader3;

            const dataPoint = {
                date,
                [fieldMapping.trader1_label]: safeNum(record[t1Long]) - safeNum(record[t1Short]),
                [fieldMapping.trader2_label]: safeNum(record[t2Long]) - safeNum(record[t2Short]),
                [fieldMapping.trader3_label]: safeNum(record[t3Long]) - safeNum(record[t3Short])
            };

            if (fieldMapping.trader4) {
                const [t4Long, t4Short] = fieldMapping.trader4;
                dataPoint[fieldMapping.trader4_label] = safeNum(record[t4Long]) - safeNum(record[t4Short]);
            }

            // Keep the most recent record for each date
            if (!dateMap.has(date) || record.report_date_as_yyyy_mm_dd > dateMap.get(date).report_date_as_yyyy_mm_dd) {
                dateMap.set(date, dataPoint);
            }
        });

        // Sort by date and return
        return Array.from(dateMap.values()).sort((a, b) => a.date.localeCompare(b.date));
    }

    /**
     * Process latest report data
     */
    function processLatestReport(data, reportType = 'legacy') {
        const safeInt = (val) => parseInt(val) || 0;
        const fieldMapping = REPORT_FIELD_MAPPINGS[reportType] || REPORT_FIELD_MAPPINGS.legacy;

        // Get trader field names from mapping
        const [t1LongField, t1ShortField] = fieldMapping.trader1;
        const [t2LongField, t2ShortField] = fieldMapping.trader2;
        const [t3LongField, t3ShortField] = fieldMapping.trader3;

        // Extract values for each trader
        const t1Long = safeInt(data[t1LongField]);
        const t1Short = safeInt(data[t1ShortField]);
        const t2Long = safeInt(data[t2LongField]);
        const t2Short = safeInt(data[t2ShortField]);
        const t3Long = safeInt(data[t3LongField]);
        const t3Short = safeInt(data[t3ShortField]);

        const t1Net = t1Long - t1Short;
        const t2Net = t2Long - t2Short;
        const t3Net = t3Long - t3Short;

        const oi = safeInt(data.open_interest_all);

        // Calculate total positions
        let totalPositions = t1Long + t1Short + t2Long + t2Short + t3Long + t3Short;

        // Handle trader4 for disaggregated and TFF reports
        let t4Long = 0, t4Short = 0, t4Net = 0;
        if (fieldMapping.trader4) {
            const [t4LongField, t4ShortField] = fieldMapping.trader4;
            t4Long = safeInt(data[t4LongField]);
            t4Short = safeInt(data[t4ShortField]);
            t4Net = t4Long - t4Short;
            totalPositions += t4Long + t4Short;
        }

        // Calculate percentages
        const t1Pct = totalPositions > 0 ? ((t1Long + t1Short) / totalPositions * 100).toFixed(1) : 0;
        const t2Pct = totalPositions > 0 ? ((t2Long + t2Short) / totalPositions * 100).toFixed(1) : 0;
        const t3Pct = totalPositions > 0 ? ((t3Long + t3Short) / totalPositions * 100).toFixed(1) : 0;
        const t4Pct = totalPositions > 0 ? ((t4Long + t4Short) / totalPositions * 100).toFixed(1) : 0;

        let formattedDate = data.report_date_as_yyyy_mm_dd || 'No Date';
        try {
            const dateObj = new Date(formattedDate);
            formattedDate = dateObj.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        } catch (e) {
            // Keep original if parsing fails
        }

        // Build traders array with dynamic data
        const traders = [
            {
                name: fieldMapping.trader1_name,
                label: fieldMapping.trader1_label,
                long: t1Long,
                short: t1Short,
                net: t1Net,
                pct: parseFloat(t1Pct)
            },
            {
                name: fieldMapping.trader2_name,
                label: fieldMapping.trader2_label,
                long: t2Long,
                short: t2Short,
                net: t2Net,
                pct: parseFloat(t2Pct)
            },
            {
                name: fieldMapping.trader3_name,
                label: fieldMapping.trader3_label,
                long: t3Long,
                short: t3Short,
                net: t3Net,
                pct: parseFloat(t3Pct)
            }
        ];

        if (fieldMapping.trader4) {
            traders.push({
                name: fieldMapping.trader4_name,
                label: fieldMapping.trader4_label,
                long: t4Long,
                short: t4Short,
                net: t4Net,
                pct: parseFloat(t4Pct)
            });
        }

        return {
            reportDate: formattedDate,
            reportType: reportType,
            openInterest: oi,
            oiChange: safeInt(data.change_in_open_interest_all),
            traders: traders,

            // Keep legacy fields for backwards compatibility
            nonCommercialLong: t1Long,
            nonCommercialShort: t1Short,
            nonCommercialNet: t1Net,
            nonCommercialPct: parseFloat(t1Pct),

            commercialLong: t2Long,
            commercialShort: t2Short,
            commercialNet: t2Net,
            commercialPct: parseFloat(t2Pct),

            nonReportableLong: t3Long,
            nonReportableShort: t3Short,
            nonReportableNet: t3Net,
            nonReportablePct: parseFloat(t3Pct)
        };
    }

    /**
     * Get empty report structure
     */
    function getEmptyReport(reportType = 'legacy') {
        const fieldMapping = REPORT_FIELD_MAPPINGS[reportType] || REPORT_FIELD_MAPPINGS.legacy;

        const traders = [
            { name: fieldMapping.trader1_name, label: fieldMapping.trader1_label, long: 0, short: 0, net: 0, pct: 0 },
            { name: fieldMapping.trader2_name, label: fieldMapping.trader2_label, long: 0, short: 0, net: 0, pct: 0 },
            { name: fieldMapping.trader3_name, label: fieldMapping.trader3_label, long: 0, short: 0, net: 0, pct: 0 }
        ];

        if (fieldMapping.trader4) {
            traders.push({ name: fieldMapping.trader4_name, label: fieldMapping.trader4_label, long: 0, short: 0, net: 0, pct: 0 });
        }

        return {
            reportDate: 'No Data',
            reportType: reportType,
            openInterest: 0,
            oiChange: 0,
            traders: traders,
            nonCommercialLong: 0,
            nonCommercialShort: 0,
            nonCommercialNet: 0,
            nonCommercialChange: 0,
            nonCommercialPct: 0,
            commercialLong: 0,
            commercialShort: 0,
            commercialNet: 0,
            commercialChange: 0,
            commercialPct: 0,
            nonReportableLong: 0,
            nonReportableShort: 0,
            nonReportableNet: 0,
            nonReportableChange: 0,
            nonReportablePct: 0
        };
    }

    /**
     * Get all assets as flat list
     */
    function getAllAssets() {
        const assets = [];
        Object.entries(ASSET_CATEGORIES).forEach(([category, categoryAssets]) => {
            categoryAssets.forEach(asset => {
                assets.push({ ...asset, category });
            });
        });
        return assets;
    }

    /**
     * Get field mapping for report type
     */
    function getFieldMapping(reportType) {
        return REPORT_FIELD_MAPPINGS[reportType] || REPORT_FIELD_MAPPINGS.legacy;
    }

    // ========================================================================
    // PERCENTILE CALCULATIONS
    // ========================================================================

    /**
     * Calculate percentile rank of a value within an array
     * Percentile = (Number of values below current / Total values) * 100
     */
    function percentileOfScore(arr, value) {
        if (!arr || arr.length === 0) return 50;
        const below = arr.filter(v => v < value).length;
        return (below / arr.length) * 100;
    }

    /**
     * Calculate percentile rank for current value vs historical data
     */
    function calculatePercentileRank(data, column, lookbackWeeks = 156) {
        if (!data || data.length < 10) {
            return {
                currentValue: 0,
                percentile: 50,
                minValue: 0,
                maxValue: 0,
                medianValue: 0,
                dataPoints: 0,
                interpretation: 'Insufficient data'
            };
        }

        // Get lookback window (data should already be sorted newest first from API)
        const lookbackData = data.slice(0, Math.min(lookbackWeeks, data.length));
        const values = lookbackData.map(d => d[column] || 0).filter(v => !isNaN(v));

        if (values.length < 10) {
            return {
                currentValue: 0,
                percentile: 50,
                minValue: 0,
                maxValue: 0,
                medianValue: 0,
                dataPoints: values.length,
                interpretation: 'Insufficient data'
            };
        }

        const currentValue = values[0]; // Most recent
        const percentile = percentileOfScore(values, currentValue);

        // Calculate statistics
        const sortedValues = [...values].sort((a, b) => a - b);
        const minValue = sortedValues[0];
        const maxValue = sortedValues[sortedValues.length - 1];
        const midIdx = Math.floor(sortedValues.length / 2);
        const medianValue = sortedValues.length % 2 === 0
            ? (sortedValues[midIdx - 1] + sortedValues[midIdx]) / 2
            : sortedValues[midIdx];

        // Generate interpretation
        let interpretation;
        if (percentile >= 90) {
            interpretation = 'Extremely bullish positioning (90th+ percentile)';
        } else if (percentile >= 75) {
            interpretation = 'Bullish positioning (75th-90th percentile)';
        } else if (percentile >= 25) {
            interpretation = 'Neutral positioning (25th-75th percentile)';
        } else if (percentile >= 10) {
            interpretation = 'Bearish positioning (10th-25th percentile)';
        } else {
            interpretation = 'Extremely bearish positioning (below 10th percentile)';
        }

        return {
            currentValue: Math.round(currentValue),
            percentile: Math.round(percentile * 10) / 10,
            minValue: Math.round(minValue),
            maxValue: Math.round(maxValue),
            medianValue: Math.round(medianValue),
            dataPoints: values.length,
            interpretation
        };
    }

    /**
     * Generate percentile history for charting
     * Shows how the percentile has changed over time
     * Goes back as far as possible in the data
     */
    function generatePercentileHistory(data, column, lookbackWeeks = 156) {
        if (!data || data.length < 10) {
            return [];
        }

        const percentileHistory = [];

        // Calculate percentile for every point that has enough lookback data
        // Start from the oldest point that has at least lookbackWeeks of history
        const maxHistoryPoints = data.length - lookbackWeeks;

        for (let i = 0; i < data.length; i++) {
            // Get window: from position i back lookbackWeeks (or as much as available)
            const windowEnd = i + lookbackWeeks;
            const windowData = data.slice(i, Math.min(windowEnd, data.length));
            const values = windowData.map(d => d[column] || 0).filter(v => !isNaN(v));

            // Need at least 10 data points for meaningful percentile
            if (values.length < 10) continue;

            const currentValue = values[0];
            const percentile = percentileOfScore(values, currentValue);

            percentileHistory.push({
                date: data[i].date,
                percentile: Math.round(percentile * 10) / 10,
                value: Math.round(currentValue)
            });
        }

        // Reverse so oldest is first (for charting)
        return percentileHistory.reverse();
    }

    /**
     * Get percentile color based on value
     */
    function getPercentileColor(percentile) {
        if (percentile >= 75) return '#22c55e'; // Green - bullish
        if (percentile >= 25) return '#eab308'; // Yellow - neutral
        return '#ef4444'; // Red - bearish
    }

    /**
     * Validate data quality and return warnings
     */
    function validateDataQuality(data, contractName) {
        const warnings = [];

        if (!data || data.length === 0) {
            return {
                contract: contractName,
                recordCount: 0,
                dateRange: 'No data',
                warnings: ['No data found for this contract'],
                isValid: false
            };
        }

        const dates = data.map(d => new Date(d.date)).filter(d => !isNaN(d));
        if (dates.length === 0) {
            return {
                contract: contractName,
                recordCount: data.length,
                dateRange: 'Unknown',
                warnings: ['Could not parse dates'],
                isValid: false
            };
        }

        const minDate = new Date(Math.min(...dates));
        const maxDate = new Date(Math.max(...dates));

        // Check if data is stale (more than 2 weeks old)
        const daysStale = Math.floor((Date.now() - maxDate) / (1000 * 60 * 60 * 24));
        if (daysStale > 14) {
            warnings.push(`Data may be stale: last update was ${daysStale} days ago`);
        }

        // Check if we have enough history
        const yearsOfData = (maxDate - minDate) / (1000 * 60 * 60 * 24 * 365);
        if (yearsOfData < 1) {
            warnings.push(`Limited history: only ${yearsOfData.toFixed(1)} years of data available`);
        }

        return {
            contract: contractName,
            recordCount: data.length,
            dateRange: `${minDate.toISOString().split('T')[0]} to ${maxDate.toISOString().split('T')[0]}`,
            warnings,
            isValid: warnings.length === 0
        };
    }

    // Public API
    return {
        fetchLatestReport,
        fetchHistoricalData,
        getContractNames,
        getAllAssets,
        getFieldMapping,
        calculatePercentileRank,
        generatePercentileHistory,
        getPercentileColor,
        validateDataQuality,
        ASSET_CATEGORIES,
        CATEGORY_INFO,
        REPORT_FIELD_MAPPINGS
    };
})();

// Export for use in app.js
window.COTAPI = COTAPI;
