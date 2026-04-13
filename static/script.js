let chart;
let selectedSymbol = null;

const stockTableEl = document.getElementById("stockTable");
const chartTitleEl = document.getElementById("chartTitle");
const statusTextEl = document.getElementById("statusText");
const stockCountEl = document.getElementById("stockCount");
const dataSourceEl = document.getElementById("dataSource");
const fundamentalsEl = document.getElementById("fundamentals");
const minPriceEl = document.getElementById("minPrice");
const maxPriceEl = document.getElementById("maxPrice");
const profitFilterEl = document.getElementById("profitFilter");

function setStatus(message) {
    statusTextEl.textContent = message;
}

function formatNumber(value) {
    if (value === null || value === undefined || value === "N/A") {
        return "N/A";
    }

    const num = Number(value);
    if (Number.isNaN(num)) {
        return value;
    }

    return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function formatRoe(roe) {
    if (roe === "N/A" || roe === null || roe === undefined) {
        return "N/A";
    }

    const num = Number(roe);
    if (Number.isNaN(num)) {
        return roe;
    }

    return `${num.toFixed(2)}%`;
}

function rowTemplate(stock) {
    const isPositive = Number(stock.change) >= 0;
    const sign = isPositive ? "+" : "";
    const changeClass = isPositive ? "positive" : "negative";
    const activeClass = selectedSymbol === stock.symbol ? "active" : "";

    return `
        <tr class="${activeClass}" data-symbol="${stock.symbol}">
            <td>${stock.symbol}</td>
            <td>INR ${formatNumber(stock.price)}</td>
            <td class="${changeClass}">${sign}${formatNumber(stock.change)} (${sign}${formatNumber(stock.changePct)}%)</td>
        </tr>
    `;
}

async function loadStocks() {
    try {
        setStatus("Fetching stocks...");

        const min = minPriceEl.value.trim();
        const max = maxPriceEl.value.trim();
        const profit = profitFilterEl.value;

        const params = new URLSearchParams({
            min_price: min,
            max_price: max,
            profit,
        });

        const response = await fetch(`/get_stocks?${params.toString()}`);
        const data = await response.json();

        stockTableEl.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            stockCountEl.textContent = "0";
            setStatus("No stocks found for selected filters.");
            stockTableEl.innerHTML = `
                <tr>
                    <td colspan="3" class="empty">No stocks found</td>
                </tr>
            `;
            return;
        }

        stockCountEl.textContent = String(data.length);
        stockTableEl.innerHTML = data.map(rowTemplate).join("");
        setStatus("Stocks loaded successfully.");

        if (!selectedSymbol || !data.find((item) => item.symbol === selectedSymbol)) {
            selectedSymbol = data[0].symbol;
        }

        highlightSelectedRow();
        const selected = data.find((item) => item.symbol === selectedSymbol) || data[0];
        dataSourceEl.textContent = selected.source || "N/A";
        await loadStock(selected.symbol);
    } catch (error) {
        stockCountEl.textContent = "0";
        setStatus("Error loading stocks. Please try refresh.");
        stockTableEl.innerHTML = `
            <tr>
                <td colspan="3" class="empty">Unable to fetch stock list</td>
            </tr>
        `;
        console.error(error);
    }
}

function highlightSelectedRow() {
    const rows = stockTableEl.querySelectorAll("tr");
    rows.forEach((row) => {
        row.classList.toggle("active", row.dataset.symbol === selectedSymbol);
    });
}

async function loadStock(symbol) {
    selectedSymbol = symbol;
    chartTitleEl.textContent = `${symbol} Intraday`;
    highlightSelectedRow();

    await Promise.all([loadChart(symbol), loadFundamentals(symbol)]);
}

async function loadChart(symbol) {
    try {
        const response = await fetch(`/get_chart/${symbol}`);
        const data = await response.json();

        if (chart) {
            chart.destroy();
        }

        const canvas = document.getElementById("chart");
        const ctx = canvas.getContext("2d");
        const gradient = ctx.createLinearGradient(0, 0, 0, 320);
        gradient.addColorStop(0, "rgba(19, 193, 181, 0.35)");
        gradient.addColorStop(1, "rgba(19, 193, 181, 0)");

        chart = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.time || [],
                datasets: [
                    {
                        label: symbol,
                        data: data.price || [],
                        borderColor: "#14b8a6",
                        backgroundColor: gradient,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: "#d7e6ff",
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: "#a4b7da", maxTicksLimit: 8 },
                        grid: { color: "rgba(148, 163, 184, 0.16)" },
                    },
                    y: {
                        ticks: { color: "#a4b7da" },
                        grid: { color: "rgba(148, 163, 184, 0.16)" },
                    },
                },
            },
        });
    } catch (error) {
        console.error(error);
    }
}

function cardTemplate(title, value) {
    return `
        <article class="metric-card">
            <p class="metric-title">${title}</p>
            <p class="metric-value">${value}</p>
        </article>
    `;
}

async function loadFundamentals(symbol) {
    try {
        const response = await fetch(`/get_fundamentals/${symbol}`);
        const data = await response.json();

        dataSourceEl.textContent = data.source || dataSourceEl.textContent;

        fundamentalsEl.innerHTML = [
            cardTemplate("Last Price", `INR ${formatNumber(data.price)}`),
            cardTemplate("Previous Close", `INR ${formatNumber(data.previousClose)}`),
            cardTemplate("P/E", formatNumber(data.pe)),
            cardTemplate("ROE", formatRoe(data.roe)),
            cardTemplate("Debt/Equity", formatNumber(data.debt)),
            cardTemplate("Market Cap", formatNumber(data.marketCap)),
            cardTemplate("Day High", `INR ${formatNumber(data.high)}`),
            cardTemplate("Day Low", `INR ${formatNumber(data.low)}`),
        ].join("");
    } catch (error) {
        fundamentalsEl.innerHTML = cardTemplate("Error", "Unable to load fundamentals");
        console.error(error);
    }
}

stockTableEl.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-symbol]");
    if (!row) {
        return;
    }
    loadStock(row.dataset.symbol);
});

document.getElementById("applyBtn").addEventListener("click", loadStocks);
document.getElementById("refreshBtn").addEventListener("click", loadStocks);

window.addEventListener("DOMContentLoaded", loadStocks);