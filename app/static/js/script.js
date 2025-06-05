/**
 * script.js
 * Combined and integrated scripts for HRM dashboard functionality.
 * Dependencies (include in HTML before this script):
 * - jQuery
 * - Bootstrap 5
 * - DataTables
 * - Chart.js
 */

// Data from backend templating (replace with actual data or inject via backend)


// DataTable initialization
$(document).ready(function () {
    // Only initialize if the table exists
    if ($('#employeeTable').length && !$.fn.DataTable.isDataTable('#employeeTable')) {

        const table = $('#employeeTable').DataTable({
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            responsive: true,
            initComplete: function () {
                // Initialize filters
                $('#departmentFilter, #statusFilter, #genderFilter').on('change', function () {
                    table.column(10).search('^' + this.value + '$', true, false).draw();
                });

                $('#searchInput').on('keyup', function () {
                    table.search(this.value).draw();
                });

                                $('#resetFilters').click(function () {
                                    $('.form-select').val('');
                                    $('#searchInput').val('');
                                    table.search('').columns().search('').draw();
                                });
                // Add this CSS dynamically for the reset button style
                const style = document.createElement('style');
                style.innerHTML = `
                    #resetFilters {
                        background-color: #fff;
                        color: #000;
                        border: 1px solid #007bff;
                        transition: background 0.2s, color 0.2s;
                    }
                    #resetFilters:hover {
                        background-color: #007bff;
                        color: #fff;
                    }
                `;
                document.head.appendChild(style);
            }
        });
    }
});

// Chart.js - Attendance Line Chart
document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('attendanceChart');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        // Only destroy if it's a Chart instance
        if (window.attendanceChart && typeof window.attendanceChart.destroy === 'function') {
            window.attendanceChart.destroy();
        }
        window.attendanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
            labels: attendanceLabels,
            datasets: [
                {
                label: 'Check-ins',
                data: checkinCounts,
                borderColor: '#3FB618',
                backgroundColor: '#3FB618',
                borderWidth: 0
                },
                {
                label: 'Check-outs',
                data: checkoutCounts,
                borderColor: 'rgb(255, 0, 0)',
                backgroundColor: 'rgb(255, 0, 0)',
                borderWidth: 2
                }
            ]
            },
            options: {
            scales: {
                y: {
                beginAtZero: true,
                title: { display: true, text: 'Number of Employees' },
                ticks: {
                    stepSize: 1
                }
                },
                x: {
                title: { display: true, text: 'Date' }
                }
            }
            }
        });
    }

    // Department Pie Chart
    const deptCanvas = document.getElementById('departmentChart');
    if (deptCanvas) {
        const departmentCtx = deptCanvas.getContext('2d');
        if (window.departmentChart && typeof window.departmentChart.destroy === 'function') {
            window.departmentChart.destroy();
        }
        window.departmentChart = new Chart(departmentCtx, {
            type: 'pie',
            data: {
                labels: departmentLabels,
                datasets: [{
                    data: departmentCounts,
                    backgroundColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgb(0, 153, 255)',
                        'rgb(255, 183, 0)',
                        'rgb(0, 255, 255)',
                        'rgb(106, 37, 242)',
                        'rgb(255, 128, 0)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgb(0, 153, 255)',
                        'rgb(255, 183, 0)',
                        'rgb(0, 255, 255)',
                        'rgb(106, 37, 242)',
                        'rgb(255, 128, 0)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Employee Distribution by Department' }
                }
            }
        });
    }
});

// Navigation Control: Dashboard/Departments toggle
document.addEventListener('DOMContentLoaded', function () {
    const deptLink = document.getElementById('deptLink');
    const dashboardContent = document.getElementById('dashboardContent');
    const departmentsSection = document.getElementById('departmentsSection');

    if (deptLink && dashboardContent && departmentsSection) {
        deptLink.addEventListener('click', function (e) {
            e.preventDefault();
            dashboardContent.style.display = 'none';
            departmentsSection.style.display = 'block';
            if (!window.departmentChart && typeof initializeDepartmentChart === 'function') {
                initializeDepartmentChart();
            }
        });

        document.addEventListener('click', function (e) {
            if (e.target.classList && e.target.classList.contains('back-to-dashboard')) {
                dashboardContent.style.display = 'block';
                departmentsSection.style.display = 'none';
            }
        });
    }
});

// Department Card Click Handler & Modal
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.department-card').forEach(card => {
        card.addEventListener('click', function () {
            // Example: Fetch department details using data attributes or AJAX as needed
            const deptName = this.querySelector('.card-title') ? this.querySelector('.card-title').textContent : '';
            // Optionally, fetch more details using this.dataset.deptId

            // Update modal content
            if (document.getElementById('deptDetailsModal')) {
                document.querySelector('#deptDetailsModal .modal-title').textContent = deptName + ' Details';
                // Example: Fill in more modal fields if available
                // document.getElementById('deptName').textContent = deptName;
                // document.getElementById('deptEmployees').textContent = ...;
                // document.getElementById('deptManager').textContent = ...;
                // document.getElementById('deptBudget').textContent = ...;

                new bootstrap.Modal(document.getElementById('deptDetailsModal')).show();
            }
        });
    });
});

// Employee ID validation on leave form
if (document.getElementById('emp_id')) {
    document.getElementById('emp_id').addEventListener('blur', function () {
        const empId = this.value;
        if (!empId) return;

        fetch(`/validate_leave_id/${empId}`)
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('empIdFeedback');
                if (feedback) {
                    if (data.exists) {
                        feedback.textContent = 'Valid Employee ID';
                        feedback.className = 'valid-feedback d-block';
                    } else {
                        feedback.textContent = 'Invalid Employee ID';
                        feedback.className = 'invalid-feedback d-block';
                    }
                }
            });
    });
}

// Optional: Date range validation for leave form (uncomment if needed)

document.addEventListener('DOMContentLoaded', function () {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    if (startDateInput && endDateInput) {
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        startDateInput.value = today;
        endDateInput.min = today;

        startDateInput.addEventListener('change', function () {
            endDateInput.min = startDateInput.value;
            if (endDateInput.value < startDateInput.value) {
                endDateInput.value = startDateInput.value;
            }
        });
    }
});


// Optional: Live leave count update (uncomment if needed)

// 


// Helper: Initialize department chart (used in navigation toggle)
function initializeDepartmentChart() {
    if (document.getElementById('departmentChart')) {
        const ctx = document.getElementById('departmentChart').getContext('2d');
        window.departmentChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: departmentLabels,
                datasets: [{
                    data: departmentCounts,
                    backgroundColor: [
                        'rgb(232, 19, 65)',
                        'rgb(0, 142, 237)',
                        'rgb(242, 174, 0)',
                        'rgb(2, 255, 255)',
                        'rgb(95, 20, 246)',
                        'rgb(239, 122, 5)'
                    ],
                    borderColor: [
                        'rgb(235, 12, 60)',
                        'rgb(0, 153, 255)',
                        'rgb(255, 184, 5)',
                        'rgb(0, 255, 255)',
                        'rgb(82, 0, 247)',
                        'rgb(255, 128, 0)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Department Distribution' }
                }
            }
        });
    }
}

console.log(attendanceLabels, checkinCounts, checkoutCounts);
document.addEventListener('DOMContentLoaded', function() {
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        startDateInput.value = today;
        endDateInput.min = today;

        startDateInput.addEventListener('change', function() {
            endDateInput.min = startDateInput.value;
            if (endDateInput.value < startDateInput.value) {
                endDateInput.value = startDateInput.value;
            }
        });
    });

    function validateEmpId() {
        const empId = document.getElementById('emp_id').value;
        if (!empId) return;
        fetch(`/validate_leave_id/${empId}`)
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('empIdFeedback');
                if (data.exists) {
                    feedback.textContent = '✅ Valid Employee ID';
                    feedback.className = 'valid-feedback d-block fw-bold';
                } else {
                    feedback.textContent = '❌ Invalid Employee ID';
                    feedback.className = 'invalid-feedback d-block fw-bold';
                }
            });
    }


    // Link active script

