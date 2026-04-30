let chartInstance = null;

// ==============================
// 📤 Upload + AI Analysis
// ==============================
async function uploadFile() {
    let file = document.getElementById("fileInput").files[0];

    if (!file) {
        alert("Please select a file!");
        return;
    }

    // 🔄 Loading state
    document.getElementById("fraud").innerText = "Analyzing... ⏳";
    document.getElementById("patterns").innerText = "";
    document.getElementById("suggestions").innerText = "";

    let formData = new FormData();
    formData.append("file", file);

    try {
        let response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        let data = await response.json();

        if (data.result) {
            formatAIOutput(data.result);
        } else {
            document.getElementById("fraud").innerText = "Error: " + data.error;
        }

        // 📊 Create chart
        createChart(file);

    } catch (err) {
        document.getElementById("fraud").innerText = "Error: " + err;
    }
}


// ==============================
// 🤖 Format AI Output
// ==============================
function formatAIOutput(text) {
    try {
        let fraud = text.split("Spending Patterns:")[0];
        let rest = text.split("Spending Patterns:")[1] || "";

        let patterns = rest.split("Suggestions:")[0] || "";
        let suggestions = rest.split("Suggestions:")[1] || "";

        document.getElementById("fraud").innerText = "🚨 " + fraud.trim();
        document.getElementById("patterns").innerText = "📊 " + patterns.trim();
        document.getElementById("suggestions").innerText = "💡 " + suggestions.trim();

    } catch (e) {
        document.getElementById("fraud").innerText = text;
    }
}


// ==============================
// 📊 Create Chart from CSV
// ==============================
function createChart(file) {
    let reader = new FileReader();

    reader.onload = function (e) {
        let rows = e.target.result.split("\n").slice(1);

        let categoryMap = {};

        rows.forEach(row => {
            let cols = row.split(",");

            let category = cols[2];
            let amount = parseFloat(cols[1]);

            if (!category || isNaN(amount)) return;

            if (!categoryMap[category]) {
                categoryMap[category] = 0;
            }

            categoryMap[category] += amount;
        });

        drawChart(categoryMap);
    };

    reader.readAsText(file);
}


// ==============================
// 📈 Draw Chart
// ==============================
function drawChart(data) {
    let ctx = document.getElementById("chart").getContext("2d");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: "Spending by Category",
                data: Object.values(data)
            }]
        }
    });
}


// ==============================
// 📄 Download PDF Report
// ==============================
async function downloadReport() {
    let content =
        document.getElementById("fraud").innerText + "\n\n" +
        document.getElementById("patterns").innerText + "\n\n" +
        document.getElementById("suggestions").innerText;

    try {
        let response = await fetch("/download", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content })
        });

        let blob = await response.blob();
        let link = document.createElement("a");

        link.href = window.URL.createObjectURL(blob);
        link.download = "AI_Report.pdf";
        link.click();

    } catch (err) {
        alert("Download failed: " + err);
    }
}