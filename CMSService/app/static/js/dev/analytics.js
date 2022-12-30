const d3 = require('d3/dist/d3');

document.addEventListener('DOMContentLoaded', () => {
    drawPageViewsChart();
    drawMostVisitedChart();
    drawBrowserStats();
});

function drawPageViewsChart() {
    const rows = []
    for (const [key, value] of Object.entries(pageViews)) {
      rows.push({
          day: new Date(key),
          visits: parseInt(value)
      })
    }

    const height = 300,
        width = 600,
        padding = 40;
    const pageViewsHolderSvg = d3.select("#page-views-holder").append("svg");

    pageViewsHolderSvg
        .attr("width", width) // todo rework later
        .attr("height", height)

    const formatTime = d3.timeFormat("%A");

    const yScale = d3
        .scaleLinear()
        .domain([
            0,
            d3.max(rows, (row) => row.visits)
        ])
        .range([height - padding, padding]);

    const xScale = d3
        .scaleTime()
        .domain([
            d3.max(rows, (d) => d.day),
            d3.min(rows, (d) => d.day)
        ])
        .range([width - padding, padding])
        .nice() ;
    const xAxis = d3.axisBottom()
        .scale(xScale)
        .ticks(7)
        .tickFormat(formatTime);

    //Define Y axis
    const yAxis = d3.axisLeft()
        .scale(yScale)
        .ticks(d3.max(rows, (row) => row.visits) < 10 ? d3.max(rows, (row) => row.visits) : 10);

    const line = d3.line()
        .x(function (d) {
            return xScale(d.day);
        })
        .y(function (d) {
            return yScale(d.visits);
        });

    pageViewsHolderSvg
        .append("path")
        .datum(rows)
        .attr("class", "line")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", "teal")
        .attr("transform", "translate(-5, 0)");

    //Create axes
    pageViewsHolderSvg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis);

    pageViewsHolderSvg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + padding + ",0)")
        .call(yAxis);

}

function drawMostVisitedChart() {
    const paddedBarHeight = 44,
        barHeight = 20,
        padding = 20,
        height = (mostVisited.length * paddedBarHeight) + (2*padding),
        width = 600;
    const mostVisitedHolderSvg = d3.select("#most-visited-holder").append("svg");

    const scale = d3
        .scaleLinear()
        .domain([
            0,
            d3.max(mostVisited, (row) => row.count * barHeight)
        ])
        .range([padding, width - padding]);

    mostVisitedHolderSvg
        .attr("width", width)
        .attr("height", height)
        .selectAll("rect")
        .data(mostVisited)
        .enter()
        .append("rect")
        .attr("x", padding)
        .attr("y", (d, i) => {
            return (i * paddedBarHeight) + (2 * padding);
        })
        .attr("height", 15)
        .attr("width", (d) => {
            return scale(d.count * barHeight);
        })
        .attr("fill", "teal");

    mostVisitedHolderSvg
        .selectAll("text")
        .data(mostVisited)
        .enter()
        .append("text")
        .attr("font-size", 16)
        .text((d) => d.pathname)
        .attr("x", () => {
            return padding;
        })
        .attr("y", (d, i) => {
            return (i * paddedBarHeight) + (1.5 * padding);
        });

    document.querySelectorAll("button.most-visited").forEach((button) => {
        button.addEventListener("click", (event) => {
            const period = event.target.dataset["period"];
            fetch(`/api/dashboard/analytics/pages/${period}`, {
                method: 'GET',
                headers: {
                    'authorization': document.cookie
                        .split(';')
                        .find(row => row.trim().startsWith('sloth_session'))
                        .split('=')[1],
                }
            }).then(response => {
                if (response.ok) {
                    return response.json()
                }
                throw `${response.status}: ${response.statusText}`
            }).then(data => {
                // not ideal, good enough for now
                mostVisitedHolderSvg
                    .selectAll("rect")
                    .remove();

                mostVisitedHolderSvg
                    .selectAll("text")
                    .remove();

                const scale = d3
                    .scaleLinear()
                    .domain([
                        0,
                        d3.max(data, (row) => row.count * barHeight)
                    ])
                    .range([padding, width - padding]);

                mostVisitedHolderSvg
                    .attr("height", (data.length * paddedBarHeight) + (2*padding))
                    .selectAll("rect")
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("x", padding)
                    .attr("y", (d, i) => {
                        return (i * paddedBarHeight) + (2 * padding);
                    })
                    .attr("height", 15)
                    .transition(d3.transition().duration(750))
                    .attr("width", (d) => {
                        return scale(d.count * barHeight);
                    })
                    .attr("fill", "teal");

                mostVisitedHolderSvg
                    .selectAll("text")
                    .data(data)
                    .enter()
                    .append("text")
                    .attr("font-size", 16)
                    .text((d) => {
                        console.log(d);
                        return d.pathname;
                    })
                    .attr("x", () => {
                        return padding;
                    })
                    .attr("y", (d, i) => {
                        return (i * paddedBarHeight) + (1.5 * padding);
                    });
            }).catch((error) => {
                console.error('Error:', error);
            })
        })
    });
}

function drawBrowserStats() {
    const refinedBrowserDataMap = {};
    for (const item of browserData) {
        if (!refinedBrowserDataMap[item.browser]) {
            refinedBrowserDataMap[item.browser] = {
                browser: item.browser,
                count: item.count,
                versions: [item['browser_version']]
            };
        } else {
            refinedBrowserDataMap[item.browser].count += item.count;
            refinedBrowserDataMap[item.browser].versions.push(item['browser_version']);
        }
    }
    const refinedBrowserData = Object.values(refinedBrowserDataMap)

    // draw chart
    const paddedBarHeight = 44,
        barHeight = 20,
        height = 300,
        width = 600,
        padding = 40;
    const browserHolderSvg = d3
        .select("#browsers-holder")
        .append("svg")
        .attr("width", width) // todo rework later
        .attr("height", height);

    const scale = d3
        .scaleLinear()
        .domain([
            0,
            d3.max(refinedBrowserData, (item) => item.count * barHeight)
        ])
        .range([padding, width - padding]);

    browserHolderSvg
        .selectAll("rect")
        .data(refinedBrowserData)
        .enter()
        .append("rect")
        .attr("x", () => padding + 100)
        .attr("y", (d, i) => {
            return (i * paddedBarHeight);
        })
        .attr("height", paddedBarHeight - 4)
        .attr("width", (d) => {
            return scale(d.count * barHeight);
        })
        .attr("fill", "teal");

    browserHolderSvg
        .selectAll("text")
        .data(refinedBrowserData)
        .enter()
        .append("text")
        .attr("font-size", 16)
        .text((d) => d.browser)
        .attr("x", () => {
            return padding;
        })
        .attr("y", (d, i) => {
            return (i * paddedBarHeight) + (paddedBarHeight / 2);
        });
    // populate table
    const tbody = document.querySelector("#browser-stats tbody");
    for (const item of refinedBrowserData) {
        item.versions.sort().reverse();
        const firstTr = document.createElement("tr");
        const browserNameTd = document.createElement("td");
        browserNameTd.setAttribute("rowspan", item.versions?.length);
        browserNameTd.textContent = item.browser;
        firstTr.appendChild(browserNameTd);
        for (let i = 0; i < item.versions?.length; i++) {
            const browserVersionTd = document.createElement("td");
            browserVersionTd.textContent = item.versions[i];
            if (i === 0) {
                firstTr.appendChild(browserVersionTd);
                tbody.appendChild(firstTr);
            } else {
                const tr = document.createElement("tr");
                tr.append(browserVersionTd)
                tbody.appendChild(tr);
            }
        }
    }
}