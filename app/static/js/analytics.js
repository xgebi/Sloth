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
        .attr("width", width)
        .attr("height", height)
        .selectAll("text")
        .data(mostVisited)
        .enter()
        .append("text")
        .attr("font-size", 16)
        .text((d) => d.pathname)
        .attr("x", (d, i, arr) => {
            return padding;
        })
        .attr("y", (d, i) => {
            return (i * paddedBarHeight) + (1.5 * padding);
        })
}

function drawBrowserStats() {

}