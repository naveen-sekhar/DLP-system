const usbCtx = document.getElementById('usbChart').getContext('2d');
const usbChart = new Chart(usbCtx, {
    type: 'bar',
    data: {
        labels: ['USB1', 'USB2', 'USB3'],
        datasets: [{
            label: 'USB Activity (events)',
            data: [3, 7, 4],
            backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe']
        }]
    }
});

const uploadCtx = document.getElementById('uploadChart').getContext('2d');
const uploadChart = new Chart(uploadCtx, {
    type: 'line',
    data: {
        labels: ['9 AM', '12 PM', '3 PM'],
        datasets: [{
            label: 'Upload Attempts',
            data: [2, 5, 1],
            backgroundColor: 'rgba(255, 206, 86, 0.2)',
            borderColor: '#ffce56',
            borderWidth: 1
        }]
    }
});
