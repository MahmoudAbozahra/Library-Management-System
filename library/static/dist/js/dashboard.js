(function () {
    "use strict";

    const body = document.body;
    const sidebar = document.getElementById("app-sidebar");
    const menuToggle = document.querySelector("[data-sidebar-toggle]");

    function setSidebarOpen(isOpen) {
        body.classList.toggle("sidebar-open", isOpen);
        if (menuToggle) {
            menuToggle.setAttribute("aria-expanded", String(isOpen));
            menuToggle.setAttribute("aria-label", isOpen ? "إغلاق قائمة التنقل" : "فتح قائمة التنقل");
            if (!isOpen) menuToggle.focus();
        }
        if (isOpen && sidebar) {
            const firstLink = sidebar.querySelector("a, button, summary");
            if (firstLink) firstLink.focus();
        }
    }

    if (menuToggle) menuToggle.addEventListener("click", function () {
        setSidebarOpen(!body.classList.contains("sidebar-open"));
    });

    document.querySelectorAll("[data-sidebar-close]").forEach(function (control) {
        control.addEventListener("click", function () { setSidebarOpen(false); });
    });

    if (sidebar) {
        sidebar.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.matchMedia("(max-width: 767px)").matches) setSidebarOpen(false);
            });
        });
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && body.classList.contains("sidebar-open")) setSidebarOpen(false);
    });

    const bookCards = Array.from(document.querySelectorAll("[data-book-card]"));
    const filteredEmpty = document.querySelector("[data-filtered-empty]");
    const filters = { category: "all", status: "all" };

    function applyBookFilters() {
        let visibleCount = 0;
        bookCards.forEach(function (card) {
            const categoryMatches = filters.category === "all" || card.dataset.category === filters.category;
            const statusMatches = filters.status === "all" || card.dataset.status === filters.status;
            const isVisible = categoryMatches && statusMatches;
            card.hidden = !isVisible;
            if (isVisible) visibleCount += 1;
        });
        if (filteredEmpty) filteredEmpty.hidden = bookCards.length === 0 || visibleCount > 0;
    }

    document.querySelectorAll("[data-category-filter]").forEach(function (button) {
        button.addEventListener("click", function () {
            filters.category = button.dataset.categoryFilter;
            document.querySelectorAll("[data-category-filter]").forEach(function (option) {
                const selected = option === button;
                option.classList.toggle("is-selected", selected);
                option.setAttribute("aria-pressed", String(selected));
            });
            applyBookFilters();
        });
    });

    document.querySelectorAll("[data-status-filter]").forEach(function (button) {
        button.addEventListener("click", function () {
            filters.status = button.dataset.statusFilter;
            document.querySelectorAll("[data-status-filter]").forEach(function (option) {
                const selected = option === button;
                option.classList.toggle("is-selected", selected);
                option.setAttribute("aria-pressed", String(selected));
            });
            applyBookFilters();
        });
    });

    document.querySelectorAll("[data-open-dialog]").forEach(function (button) {
        button.addEventListener("click", function () {
            const dialog = document.getElementById(button.dataset.openDialog);
            if (dialog && typeof dialog.showModal === "function") dialog.showModal();
        });
    });

    document.querySelectorAll("[data-close-dialog]").forEach(function (button) {
        button.addEventListener("click", function () {
            const dialog = button.closest("dialog");
            if (dialog) dialog.close();
        });
    });

    document.querySelectorAll("dialog[data-auto-open='true']").forEach(function (dialog) {
        if (typeof dialog.showModal === "function") dialog.showModal();
    });

    document.querySelectorAll("[data-auto-dismiss]").forEach(function (alert) {
        window.setTimeout(function () {
            alert.classList.add("is-dismissing");
            window.setTimeout(function () { alert.remove(); }, 220);
        }, 4500);
    });

    document.querySelectorAll(".alert-close").forEach(function (button) {
        button.addEventListener("click", function () {
            const alert = button.closest("[data-auto-dismiss]");
            if (alert) alert.remove();
        });
    });

    const salesCanvas = document.getElementById("sales-chart");
    const statusCanvas = document.getElementById("status-chart");
    if (!salesCanvas && !statusCanvas) return;
    if (typeof Chart === "undefined") return;

    const saleItems = Array.from(document.querySelectorAll("[data-sales-item]"));
    const soldTotal = saleItems.reduce(function (total, item) {
        return total + (Number(item.dataset.saleAmount) || 0);
    }, 0);
    const rentalTotal = saleItems.reduce(function (total, item) {
        return total + (Number(item.dataset.rentalAmount) || 0);
    }, 0);

    if (salesCanvas) {
        new Chart(salesCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: ["مبيعات الكتب", "إيرادات الإعارة"],
                datasets: [{
                    data: [soldTotal, rentalTotal],
                    backgroundColor: ["#2563eb", "#14b8a6"],
                    borderRadius: 6,
                    maxBarThickness: 62
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: { display: false, rtl: true, textDirection: "rtl" },
                tooltips: {
                    rtl: true,
                    callbacks: { label: function (item, data) { return "$" + data.datasets[item.datasetIndex].data[item.index]; } }
                },
                scales: {
                    xAxes: [{ gridLines: { display: false }, ticks: { fontColor: "#64748b" } }],
                    yAxes: [{ gridLines: { color: "#edf2f7" }, ticks: { beginAtZero: true, fontColor: "#64748b", callback: function (value) { return "$" + value; } } }]
                }
            }
        });
    }

    if (statusCanvas) {
        new Chart(statusCanvas.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: ["متاح", "مباع", "مُعار"],
                datasets: [{
                    data: [Number(statusCanvas.dataset.available), Number(statusCanvas.dataset.sold), Number(statusCanvas.dataset.rental)],
                    backgroundColor: ["#2563eb", "#fb7185", "#f59e0b"],
                    borderColor: "#ffffff",
                    borderWidth: 4,
                    hoverOffset: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutoutPercentage: 62,
                legend: { position: "bottom", rtl: true, textDirection: "rtl", labels: { usePointStyle: true, padding: 18, fontColor: "#475569" } },
                tooltips: { rtl: true, textDirection: "rtl" }
            }
        });
    }
}());
