/**
 * Chart Download Module
 * COT Pulse - Export charts as PNG images
 *
 * Supports:
 * - Plotly.js charts (high-quality native export)
 * - HTML sections via html2canvas (gauge, metrics, etc.)
 * - COT Pulse watermark on all exports
 */

(function () {
    'use strict';

    // Config
    const WATERMARK_TEXT = 'COT Pulse | cotpulse.com';
    const EXPORT_WIDTH = 1400;
    const EXPORT_HEIGHT = 700;
    const BG_COLOR = '#0B0F17';
    const BG_COLOR_LIGHT = '#FFFFFF';

    /**
     * Get current asset name for filename
     */
    function getAssetName() {
        const el = document.getElementById('header-asset-name');
        if (el && el.textContent) {
            return el.textContent.trim().replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();
        }
        return 'chart';
    }

    /**
     * Get current date string for filename
     */
    function getDateString() {
        const now = new Date();
        return now.toISOString().slice(0, 10);
    }

    /**
     * Detect if light theme is active
     */
    function isLightTheme() {
        return document.body.classList.contains('light-theme');
    }

    /**
     * Set button state (downloading, success, normal)
     */
    function setButtonState(btn, state) {
        btn.classList.remove('downloading', 'download-success');
        if (state === 'downloading') {
            btn.classList.add('downloading');
        } else if (state === 'success') {
            btn.classList.add('download-success');
            setTimeout(() => btn.classList.remove('download-success'), 1500);
        }
    }

    /**
     * Add watermark to a canvas
     */
    function addWatermark(canvas) {
        const ctx = canvas.getContext('2d');
        const light = isLightTheme();

        // Watermark text
        ctx.save();
        ctx.font = '500 13px Inter, system-ui, sans-serif';
        ctx.fillStyle = light ? 'rgba(0, 0, 0, 0.25)' : 'rgba(255, 255, 255, 0.25)';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'bottom';
        ctx.fillText(WATERMARK_TEXT, canvas.width - 16, canvas.height - 12);

        // Timestamp
        ctx.font = '400 11px Inter, system-ui, sans-serif';
        ctx.fillStyle = light ? 'rgba(0, 0, 0, 0.15)' : 'rgba(255, 255, 255, 0.15)';
        const reportDate = document.getElementById('report-date');
        const dateText = reportDate ? `Report: ${reportDate.textContent}` : getDateString();
        ctx.fillText(dateText, canvas.width - 16, canvas.height - 30);
        ctx.restore();

        return canvas;
    }

    /**
     * Trigger download from canvas
     */
    function downloadCanvas(canvas, name) {
        const link = document.createElement('a');
        link.download = `cotpulse-${name}-${getDateString()}.png`;
        link.href = canvas.toDataURL('image/png');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Download a Plotly chart as high-quality PNG
     */
    window.downloadPlotlyChart = async function (chartId, chartName) {
        const chartDiv = document.getElementById(chartId);
        const btn = event && event.currentTarget;

        if (!chartDiv || !chartDiv.data) {
            console.warn('[Download] Chart not found or no data:', chartId);
            return;
        }

        if (btn) setButtonState(btn, 'downloading');

        try {
            const assetName = getAssetName();
            const filename = `cotpulse-${assetName}-${chartName || 'chart'}-${getDateString()}`;
            const light = isLightTheme();

            // Get chart title
            const titleEl = chartDiv.closest('.chart-section')?.querySelector('h3');
            const assetEl = document.getElementById('header-asset-name');
            const chartTitle = assetEl ? assetEl.textContent : '';
            const subtitle = titleEl ? titleEl.textContent : '';

            // Export via Plotly at high resolution
            const imgData = await Plotly.toImage(chartDiv, {
                format: 'png',
                width: EXPORT_WIDTH,
                height: EXPORT_HEIGHT,
                scale: 2
            });

            // Draw onto canvas so we can add watermark and title
            const img = new Image();
            img.crossOrigin = 'anonymous';

            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
                img.src = imgData;
            });

            const padding = 80;
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height + padding;
            const ctx = canvas.getContext('2d');

            // Background
            ctx.fillStyle = light ? BG_COLOR_LIGHT : BG_COLOR;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Title
            ctx.font = '600 28px Inter, system-ui, sans-serif';
            ctx.fillStyle = light ? '#111827' : '#E6E9F0';
            ctx.textAlign = 'left';
            ctx.fillText(chartTitle, 24, 36);

            // Subtitle
            ctx.font = '400 18px Inter, system-ui, sans-serif';
            ctx.fillStyle = light ? '#6B7280' : '#9AA3B2';
            ctx.fillText(subtitle, 24, 62);

            // Chart image
            ctx.drawImage(img, 0, padding);

            // Watermark
            addWatermark(canvas);

            // Download
            const link = document.createElement('a');
            link.download = filename + '.png';
            link.href = canvas.toDataURL('image/png');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            if (btn) setButtonState(btn, 'success');

        } catch (error) {
            console.error('[Download] Failed to export chart:', error);
            if (btn) setButtonState(btn, '');
        }
    };

    /**
     * Download an HTML section as PNG using html2canvas
     */
    window.downloadSection = async function (sectionId, name) {
        const section = document.getElementById(sectionId);
        const btn = event && event.currentTarget;

        if (!section) {
            console.warn('[Download] Section not found:', sectionId);
            return;
        }

        if (btn) setButtonState(btn, 'downloading');

        try {
            const assetName = getAssetName();
            const filename = `cotpulse-${assetName}-${name || 'section'}-${getDateString()}`;
            const light = isLightTheme();

            const canvas = await html2canvas(section, {
                backgroundColor: light ? BG_COLOR_LIGHT : BG_COLOR,
                scale: 2,
                useCORS: true,
                logging: false,
                removeContainer: true
            });

            // Create final canvas with padding for title and watermark
            const padding = 60;
            const bottomPad = 40;
            const finalCanvas = document.createElement('canvas');
            finalCanvas.width = Math.max(canvas.width, 800);
            finalCanvas.height = canvas.height + padding + bottomPad;
            const ctx = finalCanvas.getContext('2d');

            // Background
            ctx.fillStyle = light ? BG_COLOR_LIGHT : BG_COLOR;
            ctx.fillRect(0, 0, finalCanvas.width, finalCanvas.height);

            // Title
            const assetEl = document.getElementById('header-asset-name');
            const chartTitle = assetEl ? assetEl.textContent : 'COT Pulse';
            ctx.font = '600 24px Inter, system-ui, sans-serif';
            ctx.fillStyle = light ? '#111827' : '#E6E9F0';
            ctx.textAlign = 'left';
            ctx.fillText(chartTitle, 20, 36);

            // Section image
            ctx.drawImage(canvas, 0, padding);

            // Watermark
            addWatermark(finalCanvas);

            // Download
            const link = document.createElement('a');
            link.download = filename + '.png';
            link.href = finalCanvas.toDataURL('image/png');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            if (btn) setButtonState(btn, 'success');

        } catch (error) {
            console.error('[Download] Failed to capture section:', error);
            if (btn) setButtonState(btn, '');
        }
    };

})();
