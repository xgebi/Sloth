document.addEventListener('DOMContentLoaded', () => {
    drawPageViewsChart();
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
        .range([width - padding, padding]);

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
            console.log("x", d);
            return xScale(d.day);
        })
        .y(function (d) {
            console.log("y", d);
            return yScale(d.visits);
        });


    console.log(JSON.stringify(rows));
    pageViewsHolderSvg
        .append("path")
        .datum(rows)
        .attr("class", "line")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", "teal");

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