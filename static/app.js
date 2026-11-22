let currentNetworks = [];
let channelChart = null;
let securityChart = null;
let autoRefreshInterval = null;
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadData();
    setupEventListeners();
    autoRefreshInterval = setInterval(loadData, 15000);
});
function setupEventListeners() {
    document.getElementById('scanBtn').addEventListener('click', scanNetworks);
    document.getElementById('searchInput').addEventListener('input', filterNetworks);
    document.getElementById('sortSelect').addEventListener('change', sortNetworks);
}
function initCharts() {
    const channelCtx = document.getElementById('channelChart').getContext('2d');
    channelChart = new Chart(channelCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Количество сетей',
                data: [],
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    const securityCtx = document.getElementById('securityChart').getContext('2d');
    securityChart = new Chart(securityCtx, {
        type: 'doughnut',
        data: {
            labels: ['Высокая', 'Средне-высокая', 'Средняя', 'Низкая', 'Отсутствует'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(251, 191, 36, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
async function loadData() {
    try {
        updateStatus('scanning', 'Загрузка данных...');
        const currentResponse = await fetch('/api/current');
        const currentData = await currentResponse.json();
        if (currentData.status === 'success') {
            currentNetworks = currentData.data.networks;
            updateNetworksTable(currentNetworks);
            updateStatistics(currentNetworks);
            const analysisResponse = await fetch('/api/analysis');
            const analysisData = await analysisResponse.json();
            if (analysisData.status === 'success') {
                updateRecommendations(analysisData.data.analysis.recommendations);
                updateIssues(analysisData.data.analysis.issues);
                updateSecurityChart(analysisData.data.analysis.security_stats);
                updateBestNetwork(analysisData.data.best_network);
            }
            const channelResponse = await fetch('/api/channel-usage');
            const channelData = await channelResponse.json();
            if (channelData.status === 'success') {
                updateChannelChart(channelData.data.channels, channelData.data.counts);
            }
            updateStatus('ready', 'Данные обновлены');
            updateLastUpdate();
        } else {
            updateStatus('waiting', currentData.message || 'Ожидание данных...');
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        updateStatus('error', 'Ошибка загрузки данных');
    }
}
async function scanNetworks() {
    const btn = document.getElementById('scanBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Сканирование...';
    try {
        updateStatus('scanning', 'Сканирование сетей...');
        const response = await fetch('/api/scan');
        const data = await response.json();
        if (data.status === 'success') {
            await loadData();
        } else {
            updateStatus('error', data.message || 'Ошибка сканирования');
        }
    } catch (error) {
        console.error('Ошибка сканирования:', error);
        updateStatus('error', 'Ошибка сканирования');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Сканировать';
    }
}
function updateStatus(status, text) {
    const dot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    dot.className = 'статус-точка статус-' + status;
    statusText.textContent = text;
}
function updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ru-RU');
    document.getElementById('lastUpdate').textContent = timeString;
}
function updateStatistics(networks) {
    document.getElementById('networkCount').textContent = networks.length;
    const secureNetworks = networks.filter(n =>
        n.security_level && !['none', 'low'].includes(n.security_level.toLowerCase())
    ).length;
    document.getElementById('secureCount').textContent = secureNetworks;
    const avgSignal = networks.length > 0
        ? Math.round(networks.reduce((sum, n) => sum + n.signal_strength, 0) / networks.length)
        : 0;
    document.getElementById('avgSignal').textContent = avgSignal + '%';
}
function updateNetworksTable(networks) {
    const tbody = document.getElementById('networksTableBody');
    if (networks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">Сети не обнаружены</td></tr>';
        return;
    }
    tbody.innerHTML = networks.map(network => `
        <tr class="${network.connected ? 'connected-row' : ''}">
            <td>
                <strong>${escapeHtml(network.ssid)}</strong>
                ${network.connected ? '<span class="badge badge-success">Подключено</span>' : ''}
            </td>
            <td>
                <div class="signal-bar">
                    <div class="signal-fill signal-${getSignalClass(network.signal_strength)}"
                         style="width: ${network.signal_strength}%"></div>
                    <span class="signal-text">${network.signal_strength}%</span>
                </div>
            </td>
            <td><span class="badge badge-channel">${network.channel || 'N/A'}</span></td>
            <td><span class="badge badge-${getSecurityClass(network.security_level)}">${network.security || 'Unknown'}</span></td>
            <td><span class="quality quality-${getQualityClass(network.quality)}">${network.quality}</span></td>
            <td><code>${network.bssid || 'Unknown'}</code></td>
        </tr>
    `).join('');
}
function updateChannelChart(channels, counts) {
    channelChart.data.labels = channels.map(ch => 'Канал ' + ch);
    channelChart.data.datasets[0].data = counts;
    channelChart.update();
}
function updateSecurityChart(stats) {
    const data = [
        stats.high || 0,
        stats['medium-high'] || 0,
        stats.medium || 0,
        stats.low || 0,
        stats.none || 0
    ];
    securityChart.data.datasets[0].data = data;
    securityChart.update();
}
function updateRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p class="no-data">Рекомендации отсутствуют</p>';
        return;
    }
    container.innerHTML = recommendations.slice(0, 5).map(rec => `
        <div class="recommendation-item priority-${rec.priority || 'medium'}">
            <div class="recommendation-header">
                <span class="priority-badge">${getPriorityText(rec.priority)}</span>
                <span class="recommendation-type">${getTypeIcon(rec.type)}</span>
            </div>
            <p>${escapeHtml(rec.message)}</p>
            ${rec.reason ? `<small class="recommendation-reason">${escapeHtml(rec.reason)}</small>` : ''}
        </div>
    `).join('');
}
function updateIssues(issues) {
    const container = document.getElementById('issues');
    document.getElementById('issueCount').textContent = issues.length;
    if (!issues || issues.length === 0) {
        container.innerHTML = '<p class="no-issues">✅ Проблемы не обнаружены</p>';
        return;
    }
    container.innerHTML = issues.map(issue => `
        <div class="issue-item severity-${issue.severity || 'medium'}">
            <div class="issue-header">
                <span class="severity-badge">${getSeverityText(issue.severity)}</span>
            </div>
            <p>${escapeHtml(issue.message)}</p>
        </div>
    `).join('');
}
function updateBestNetwork(bestNetwork) {
    const container = document.getElementById('bestNetwork');
    if (!bestNetwork) {
        container.innerHTML = '<p class="no-data">Нет рекомендуемых сетей</p>';
        return;
    }
    container.innerHTML = `
        <div class="best-network-info">
            <div class="best-network-main">
                <h3>${escapeHtml(bestNetwork.ssid)}</h3>
                <div class="best-network-stats">
                    <div class="stat">
                        <span class="label">Сигнал:</span>
                        <span class="value">${bestNetwork.signal}%</span>
                    </div>
                    <div class="stat">
                        <span class="label">Канал:</span>
                        <span class="value">${bestNetwork.channel}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Безопасность:</span>
                        <span class="value">${bestNetwork.security}</span>
                    </div>
                </div>
            </div>
            <p class="best-network-reason"><em>${escapeHtml(bestNetwork.reason)}</em></p>
        </div>
    `;
}
function filterNetworks() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filteredNetworks = currentNetworks.filter(network =>
        network.ssid.toLowerCase().includes(searchTerm)
    );
    updateNetworksTable(filteredNetworks);
}
function sortNetworks() {
    const sortBy = document.getElementById('sortSelect').value;
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    let sortedNetworks = [...currentNetworks];
    switch (sortBy) {
        case 'signal':
            sortedNetworks.sort((a, b) => b.signal_strength - a.signal_strength);
            break;
        case 'name':
            sortedNetworks.sort((a, b) => a.ssid.localeCompare(b.ssid));
            break;
        case 'channel':
            sortedNetworks.sort((a, b) => (a.channel || 0) - (b.channel || 0));
            break;
        case 'security':
            sortedNetworks.sort((a, b) => {
                const order = { 'high': 4, 'medium-high': 3, 'medium': 2, 'low': 1, 'none': 0 };
                return (order[b.security_level?.toLowerCase()] || 0) - (order[a.security_level?.toLowerCase()] || 0);
            });
            break;
    }
    if (searchTerm) {
        sortedNetworks = sortedNetworks.filter(network =>
            network.ssid.toLowerCase().includes(searchTerm)
        );
    }
    updateNetworksTable(sortedNetworks);
}
function getSignalClass(strength) {
    if (strength >= 80) return 'excellent';
    if (strength >= 60) return 'good';
    if (strength >= 40) return 'fair';
    if (strength >= 20) return 'weak';
    return 'very-weak';
}
function getSecurityClass(level) {
    const l = (level || '').toLowerCase();
    if (l === 'high') return 'success';
    if (l === 'medium-high') return 'info';
    if (l === 'medium') return 'warning';
    if (l === 'low') return 'danger';
    if (l === 'none') return 'danger';
    return 'secondary';
}
function getQualityClass(quality) {
    const q = (quality || '').toLowerCase();
    if (q.includes('excellent')) return 'excellent';
    if (q.includes('good')) return 'good';
    if (q.includes('fair')) return 'fair';
    if (q.includes('weak')) return 'weak';
    return 'unknown';
}
function getPriorityText(priority) {
    const priorities = {
        'critical': '🔴 Критично',
        'high': '🟠 Высокий',
        'medium': '🟡 Средний',
        'low': '🟢 Низкий',
        'info': 'ℹ️ Информация'
    };
    return priorities[priority] || '📌 Обычный';
}
function getSeverityText(severity) {
    const severities = {
        'high': '🔴 Высокая',
        'medium': '🟡 Средняя',
        'low': '🟢 Низкая'
    };
    return severities[severity] || '⚠️ Обычная';
}
function getTypeIcon(type) {
    const icons = {
        'channel_optimization': '📡',
        'channel_selection': '🎯',
        'security': '🔐',
        'signal_improvement': '📶',
        'signal_status': '✅',
        'signal_optimization': '⚡'
    };
    return icons[type] || '💡';
}
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}