const ubaCtx = document.getElementById('ubaChart').getContext('2d');
const ubaChart = new Chart(ubaCtx, {
    type: 'bar',
    data: {
        labels: ['User1', 'User2', 'User3'],
        datasets: [{
            label: 'Anomalies Detected',
            data: [0, 3, 1], // Example data
            backgroundColor: '#ff6384'
        }]
    }
});

const uploadBlockCtx = document.getElementById('uploadBlockChart').getContext('2d');
const uploadBlockChart = new Chart(uploadBlockCtx, {
    type: 'line',
    data: {
        labels: ['9 AM', '12 PM', '3 PM'],
        datasets: [{
            label: 'Blocked Upload Attempts',
            data: [0, 2, 5],
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: '#ff6384'
        }]
    }
});
