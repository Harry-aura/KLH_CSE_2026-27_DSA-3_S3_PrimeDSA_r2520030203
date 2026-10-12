/**
 * PrimeDSA - 1024-Bit Miller-Rabin Primality Engine
 * Frontend Client Application Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const elements = {
        // Navigation Tabs
        navTabs: document.querySelectorAll('.nav-tab'),
        tabPanes: document.querySelectorAll('.tab-pane'),

        // Validator Inputs & Controls
        numberInput: document.getElementById('number-input'),
        statBits: document.getElementById('stat-bits'),
        statDigits: document.getElementById('stat-digits'),
        btnCopyInput: document.getElementById('btn-copy-input'),
        btnClearInput: document.getElementById('btn-clear-input'),
        presetsFilter: document.getElementById('presets-filter'),
        presetChipsContainer: document.getElementById('preset-chips'),
        iterationsSlider: document.getElementById('iterations-slider'),
        iterationsVal: document.getElementById('iterations-val'),
        confPreviewError: document.getElementById('conf-preview-error'),
        confPreviewPct: document.getElementById('conf-preview-pct'),
        genBitsSelect: document.getElementById('gen-bits-select'),
        btnGeneratePrime: document.getElementById('btn-generate-prime'),
        chkDeterministic: document.getElementById('chk-deterministic'),
        chkCustomModpow: document.getElementById('chk-custom-modpow'),
        btnCheckPrime: document.getElementById('btn-check-prime'),

        // Results Section
        emptyState: document.getElementById('empty-state'),
        resultsContent: document.getElementById('results-content'),
        resultHero: document.getElementById('result-hero'),
        heroBadgeIcon: document.getElementById('hero-badge-icon'),
        heroStatusTitle: document.getElementById('hero-status-title'),
        heroStatusDesc: document.getElementById('hero-status-desc'),
        metricTime: document.getElementById('metric-time'),
        metricTimeDetail: document.getElementById('metric-time-detail'),
        metricConfidence: document.getElementById('metric-confidence'),
        metricConfidenceSub: document.getElementById('metric-confidence-sub'),
        metricBits: document.getElementById('metric-bits'),
        metricDigits: document.getElementById('metric-digits'),
        metricRounds: document.getElementById('metric-rounds'),
        metricMethod: document.getElementById('metric-method'),
        carmichaelAlert: document.getElementById('carmichael-alert'),
        witnessBox: document.getElementById('witness-box'),
        witnessValue: document.getElementById('witness-value'),
        decompS: document.getElementById('decomp-s'),
        decompD: document.getElementById('decomp-d'),
        traceTableBody: document.getElementById('trace-table-body'),

        // Benchmark Section
        btnRunBenchmark: document.getElementById('btn-run-benchmark'),
        benchmarkTbody: document.getElementById('benchmark-tbody'),
        benchmarkChartCanvas: document.getElementById('benchmarkChart'),

        // Toast Container
        toastContainer: document.getElementById('toast-container'),
        apiStatusChip: document.getElementById('api-status-chip'),
    };

    let cachedPresets = [];
    let benchmarkChartInstance = null;

    // Initialize Application
    initApp();

    async function initApp() {
        setupTabs();
        setupInputHandlers();
        setupSlider();
        setupActions();
        await loadPresets();
        await checkApiHealth();
        // Load default 1024-bit preset
        selectDefaultPreset();
    }

    // --- Tab Navigation ---
    function setupTabs() {
        elements.navTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTabId = tab.dataset.tab;
                elements.navTabs.forEach(t => t.classList.remove('active'));
                elements.tabPanes.forEach(p => p.classList.remove('active'));

                tab.classList.add('active');
                const activePane = document.getElementById(targetTabId);
                if (activePane) {
                    activePane.classList.add('active');
                }

                // If benchmark tab is opened for the first time, load benchmark data
                if (targetTabId === 'benchmark-tab' && !benchmarkChartInstance) {
                    loadBenchmarkData();
                }
            });
        });
    }

    // --- Input Statistics Calculation ---
    function setupInputHandlers() {
        elements.numberInput.addEventListener('input', updateInputMetrics);

        elements.btnCopyInput.addEventListener('click', () => {
            const val = elements.numberInput.value.trim();
            if (!val) {
                showToast('Input is empty', 'error');
                return;
            }
            navigator.clipboard.writeText(val);
            showToast('Copied integer to clipboard!', 'success');
        });

        elements.btnClearInput.addEventListener('click', () => {
            elements.numberInput.value = '';
            updateInputMetrics();
            elements.emptyState.classList.remove('hidden');
            elements.resultsContent.classList.add('hidden');
            document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
        });
    }

    function updateInputMetrics() {
        const raw = elements.numberInput.value.trim().replace(/\s+/g, '').replace(/,/g, '');
        if (!raw) {
            elements.statBits.textContent = '0';
            elements.statDigits.textContent = '0';
            return;
        }

        try {
            const cleaned = raw.startsWith('-') || raw.startsWith('+') ? raw.slice(1) : raw;
            if (/^\d+$/.test(cleaned)) {
                const bn = BigInt(cleaned);
                let bitLength = 0;
                let temp = bn;
                while (temp > 0n) {
                    temp >>= 1n;
                    bitLength++;
                }
                elements.statBits.textContent = bitLength || '1';
                elements.statDigits.textContent = cleaned.length;
                return;
            }
        } catch (e) {
            // fallback for huge strings
        }

        elements.statBits.textContent = Math.round(raw.length * 3.322);
        elements.statDigits.textContent = raw.length;
    }

    // --- Iterations Slider & Confidence Preview ---
    function setupSlider() {
        elements.iterationsSlider.addEventListener('input', () => {
            const k = parseInt(elements.iterationsSlider.value, 10);
            elements.iterationsVal.textContent = `${k} rounds`;

            // Error probability: 4^(-k) = 2^(-2k)
            const exponent = 2 * k;
            elements.confPreviewError.textContent = `≤ 2⁻${toSuperscript(exponent)} ≈ 4⁻${toSuperscript(k)}`;

            // Percentage calculation
            const ninesCount = Math.floor(k * 0.602);
            if (ninesCount <= 2) {
                const pct = (1 - Math.pow(4, -k)) * 100;
                elements.confPreviewPct.textContent = `≥ ${pct.toFixed(4)}%`;
            } else {
                const decimals = Math.min(ninesCount + 2, 20);
                elements.confPreviewPct.textContent = `≥ 99.${'9'.repeat(decimals)}%`;
            }
        });
    }

    function toSuperscript(num) {
        const map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻'
        };
        return String(num).split('').map(c => map[c] || c).join('');
    }

    // --- Presets Loading & Filtering ---
    async function loadPresets() {
        try {
            const res = await fetch('/api/presets');
            if (!res.ok) throw new Error('Failed to fetch presets');
            cachedPresets = await res.json();
            renderPresetChips();
        } catch (err) {
            console.error('Presets load error:', err);
        }

        elements.presetsFilter.addEventListener('change', renderPresetChips);
    }

    function renderPresetChips() {
        const filter = elements.presetsFilter.value;
        elements.presetChipsContainer.innerHTML = '';

        const filtered = cachedPresets.filter(p => filter === 'all' || p.category === filter);
        filtered.forEach(preset => {
            const chip = document.createElement('button');
            chip.className = 'preset-chip';
            chip.dataset.id = preset.id;
            chip.innerHTML = `<span>${preset.name}</span> <small>(${preset.bitLength}-bit)</small>`;
            chip.title = preset.description;

            chip.addEventListener('click', () => {
                document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                elements.numberInput.value = preset.value;
                updateInputMetrics();
                // Trigger check
                runPrimalityCheck();
            });

            elements.presetChipsContainer.appendChild(chip);
        });
    }

    function selectDefaultPreset() {
        const p1024 = cachedPresets.find(p => p.id === 'prime-1024') || cachedPresets[0];
        if (p1024) {
            elements.numberInput.value = p1024.value;
            updateInputMetrics();
            const firstChip = elements.presetChipsContainer.querySelector(`[data-id="${p1024.id}"]`);
            if (firstChip) firstChip.classList.add('active');
        }
    }

    // --- Actions (Validate, Generate, Benchmark) ---
    function setupActions() {
        elements.btnCheckPrime.addEventListener('click', runPrimalityCheck);

        elements.btnGeneratePrime.addEventListener('click', async () => {
            const bits = parseInt(elements.genBitsSelect.value, 10);
            const iterations = parseInt(elements.iterationsSlider.value, 10);

            const origText = elements.btnGeneratePrime.innerHTML;
            elements.btnGeneratePrime.disabled = true;
            elements.btnGeneratePrime.innerHTML = 'Generating...';

            try {
                const res = await fetch(`/api/generate-prime?bits=${bits}&iterations=${iterations}`);
                if (!res.ok) {
                    const errData = await res.json();
                    throw new Error(errData.detail || 'Prime generation failed');
                }

                const data = await res.json();
                elements.numberInput.value = data.number;
                updateInputMetrics();
                displayResults(data.validationResult);
                showToast(`Generated random ${data.bitLength}-bit prime in ${data.generationTimeMs} ms (${data.candidatesTested} candidates tested)`, 'success');
            } catch (err) {
                showToast(`Error: ${err.message}`, 'error');
            } finally {
                elements.btnGeneratePrime.disabled = false;
                elements.btnGeneratePrime.innerHTML = origText;
            }
        });

        elements.btnRunBenchmark.addEventListener('click', () => {
            loadBenchmarkData();
        });
    }

    // --- API Primality Check Execution ---
    async function runPrimalityCheck() {
        const rawInput = elements.numberInput.value.trim().replace(/\s+/g, '').replace(/,/g, '');
        if (!rawInput) {
            showToast('Please enter an integer or choose a preset.', 'error');
            return;
        }

        const iterations = parseInt(elements.iterationsSlider.value, 10);
        const use_custom_modpow = elements.chkCustomModpow.checked;
        const deterministic_for_small = elements.chkDeterministic.checked;

        const origHtml = elements.btnCheckPrime.innerHTML;
        elements.btnCheckPrime.disabled = true;
        elements.btnCheckPrime.innerHTML = `<span class="spinner"></span> <span>Running Miller–Rabin (${iterations} rounds)...</span>`;

        try {
            const response = await fetch('/api/check-prime', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    number: rawInput,
                    iterations: iterations,
                    use_custom_modpow: use_custom_modpow,
                    deterministic_for_small: deterministic_for_small,
                }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Primality check failed');
            }

            const data = await response.json();
            displayResults(data);
        } catch (err) {
            showToast(`Validation error: ${err.message}`, 'error');
        } finally {
            elements.btnCheckPrime.disabled = false;
            elements.btnCheckPrime.innerHTML = origHtml;
        }
    }

    // --- Display Results in UI ---
    function displayResults(data) {
        elements.emptyState.classList.add('hidden');
        elements.resultsContent.classList.remove('hidden');

        // Hero Banner Styling
        if (data.is_prime) {
            elements.resultHero.className = 'result-hero prime';
            elements.heroBadgeIcon.textContent = '✓';
            elements.heroStatusTitle.textContent = data.deterministic ? 'DEFINITE PRIME' : 'PROBABLE PRIME';
            elements.heroStatusDesc.textContent = data.deterministic
                ? `Proven prime via deterministic 64-bit base set with 100% mathematical certainty.`
                : `Passed all ${data.roundsCompleted} Miller–Rabin rounds with zero composite witnesses.`;
        } else {
            elements.resultHero.className = 'result-hero composite';
            elements.heroBadgeIcon.textContent = '✕';
            elements.heroStatusTitle.textContent = 'COMPOSITE NUMBER';
            elements.heroStatusDesc.textContent = `Proven composite! Found non-trivial witness / divisor.`;
        }

        // Metrics Tiles
        // Time display formatting
        if (data.executionTimeMs >= 1.0) {
            elements.metricTime.textContent = `${data.executionTimeMs.toFixed(3)} ms`;
        } else if (data.executionTimeUs >= 1.0) {
            elements.metricTime.textContent = `${data.executionTimeUs.toFixed(2)} µs`;
        } else {
            elements.metricTime.textContent = `${data.executionTimeNs} ns`;
        }
        elements.metricTimeDetail.textContent = `${data.executionTimeNs.toLocaleString()} ns (${data.executionTimeMs.toFixed(4)} ms)`;

        elements.metricConfidence.textContent = data.confidence;
        elements.metricConfidenceSub.textContent = data.confidence_formula || `Error: ${data.error_probability}`;

        elements.metricBits.textContent = `${data.bitLength} bits`;
        elements.metricDigits.textContent = `${data.decimalLength} decimal digits`;

        elements.metricRounds.textContent = `${data.roundsCompleted} Rounds`;
        elements.metricMethod.textContent = data.method;

        // Carmichael Alert
        if (data.carmichael_number) {
            elements.carmichaelAlert.classList.remove('hidden');
        } else {
            elements.carmichaelAlert.classList.add('hidden');
        }

        // Witness Box
        if (!data.is_prime && data.witness) {
            elements.witnessBox.classList.remove('hidden');
            elements.witnessValue.textContent = `Witness Base / Factor: ${data.witness}`;
        } else {
            elements.witnessBox.classList.add('hidden');
        }

        // Decomposition Section
        elements.decompS.textContent = data.s !== null && data.s !== undefined ? `s = ${data.s}` : 'N/A (Pre-check)';
        elements.decompD.textContent = data.d ? `d = ${data.d}` : 'N/A';

        // Trace Table
        elements.traceTableBody.innerHTML = '';
        if (data.traces && data.traces.length > 0) {
            data.traces.forEach(t => {
                const tr = document.createElement('tr');
                const statusClass = t.passed ? 'trace-pass' : 'trace-fail';
                const statusText = t.passed ? 'PASS' : 'FAIL';
                tr.innerHTML = `
                    <td>Round #${t.round_index}</td>
                    <td>${t.base_a}</td>
                    <td class="code-font">${t.initial_x}</td>
                    <td class="${statusClass}">${statusText}</td>
                    <td>${t.reason}</td>
                `;
                elements.traceTableBody.appendChild(tr);
            });
        } else {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="5" style="text-align: center; color: var(--text-dim);">No detailed traces available</td>`;
            elements.traceTableBody.appendChild(tr);
        }
    }

    // --- Benchmark Data & Chart Rendering ---
    async function loadBenchmarkData() {
        const origText = elements.btnRunBenchmark.innerHTML;
        elements.btnRunBenchmark.disabled = true;
        elements.btnRunBenchmark.innerHTML = 'Running Benchmark...';

        try {
            const res = await fetch('/api/benchmark?iterations=40');
            if (!res.ok) throw new Error('Benchmark request failed');
            const data = await res.json();

            renderBenchmarkTable(data.results);
            renderBenchmarkChart(data.results);
            showToast('Benchmark completed successfully!', 'success');
        } catch (err) {
            showToast(`Benchmark error: ${err.message}`, 'error');
        } finally {
            elements.btnRunBenchmark.disabled = false;
            elements.btnRunBenchmark.innerHTML = origText;
        }
    }

    function renderBenchmarkTable(results) {
        elements.benchmarkTbody.innerHTML = '';
        results.forEach(row => {
            const tr = document.createElement('tr');
            const tdFormatted = row.trial_division_completed 
                ? `${row.trial_division_time_ms.toFixed(3)} ms`
                : `<span style="color: #f87171;">> ${row.trial_division_projected_ms.toFixed(0)} ms (Capped)</span>`;

            const speedupFormatted = row.speedup_factor >= 1000
                ? `${row.speedup_factor.toExponential(2)}x`
                : `${row.speedup_factor.toFixed(1)}x`;

            tr.innerHTML = `
                <td><strong>${row.bit_length}-bit</strong></td>
                <td><code class="code-font">${row.sample_prime_preview}</code></td>
                <td><span style="color: #34d399;">${row.miller_rabin_time_ms.toFixed(3)} ms</span></td>
                <td>${tdFormatted}</td>
                <td><span class="speedup-badge">${speedupFormatted} Speedup</span></td>
            `;
            elements.benchmarkTbody.appendChild(tr);
        });
    }

    function renderBenchmarkChart(results) {
        const labels = results.map(r => `${r.bit_length}-bit`);
        const mrData = results.map(r => Math.max(0.001, r.miller_rabin_time_ms));
        const tdData = results.map(r => Math.max(0.001, r.trial_division_projected_ms));

        if (benchmarkChartInstance) {
            benchmarkChartInstance.destroy();
        }

        const ctx = elements.benchmarkChartCanvas.getContext('2d');
        benchmarkChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Miller–Rabin O(k · b³)',
                        data: mrData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#10b981',
                        pointRadius: 5,
                        tension: 0.2,
                        fill: false,
                    },
                    {
                        label: 'Trial Division O(2^(b/2))',
                        data: tdData,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#ef4444',
                        pointRadius: 5,
                        tension: 0.2,
                        fill: false,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        type: 'logarithmic',
                        title: {
                            display: true,
                            text: 'Execution Time (ms, Log Scale)',
                            color: '#9ca3af',
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#9ca3af',
                            callback: function(val) {
                                if (val >= 1000) return `${val / 1000}s`;
                                return `${val}ms`;
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#f3f4f6' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const val = context.parsed.y;
                                return `${context.dataset.label}: ${val >= 1000 ? (val/1000).toFixed(2) + ' s' : val.toFixed(3) + ' ms'}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // --- Health Check ---
    async function checkApiHealth() {
        try {
            const res = await fetch('/api/health');
            if (res.ok) {
                elements.apiStatusChip.innerHTML = `<span class="status-dot"></span><span>API Connected</span>`;
            }
        } catch (e) {
            elements.apiStatusChip.innerHTML = `<span class="status-dot" style="background: #ef4444;"></span><span>API Disconnected</span>`;
        }
    }

    // --- Toast Notifications ---
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${message}</span>`;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }
});
