// Set dimensions and margins for the chart
const margin = { top: 40, right: 40, bottom: 60, left: 60 };
const width = 700 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

// Append the SVG object to the body of the page
const svg = d3.select("#chart-area")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Create a tooltip div (initially hidden)
const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

// FIX: Load the data from the 'consistency.json' file
d3.json("Consistency.json").then(data => {

    // 1. Data Processing and Median Calculation
    
    // Ensure data is numeric
    data.forEach(d => {
        d.avg_tries = +d.avg_tries;
        d.standard_deviation = +d.standard_deviation;
    });

    // Calculate the overall median values for the quadrant lines
    const avgTriesValues = data.map(d => d.avg_tries).sort(d3.ascending);
    const stdDevValues = data.map(d => d.standard_deviation).sort(d3.ascending);

    // Median calculation using D3.median
    const medianAvgTries = d3.median(avgTriesValues);
    const medianStdDev = d3.median(stdDevValues);

    console.log("Median Avg Tries (X-axis center):", medianAvgTries);
    console.log("Median Std Dev (Y-axis center):", medianStdDev);


    // 2. Define Scales
    
    // X Scale (Average Tries - Performance)
    const xScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.avg_tries) * 1.05]) // Max + 5% padding
        .range([0, width]);

    // Y Scale (Standard Deviation - Volatility/Consistency)
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.standard_deviation) * 1.05]) // Max + 5% padding
        .range([height, 0]); // Note: Y range is reversed for standard charting


    // 3. Draw Axes

    // X-Axis (Bottom)
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    // Y-Axis (Left)
    svg.append("g")
        .call(d3.axisLeft(yScale));

    // X-Axis Label
    svg.append("text")
        .attr("class", "axis-label")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom - 15)
        .style("text-anchor", "middle")
        .text("Average Tries Per Game (Performance ➡️)");

    // Y-Axis Label
    svg.append("text")
        .attr("class", "axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Standard Deviation (Volatility ⬆️)");


    // 4. Draw Quadrant Lines (The Median Lines)

    // Vertical Median Line (X-center)
    svg.append("line")
        .attr("x1", xScale(medianAvgTries))
        .attr("y1", 0)
        .attr("x2", xScale(medianAvgTries))
        .attr("y2", height)
        .style("stroke-dasharray", ("3, 3"))
        .style("stroke", "red")
        .style("stroke-width", 2);

    // Horizontal Median Line (Y-center)
    svg.append("line")
        .attr("x1", 0)
        .attr("y1", yScale(medianStdDev))
        .attr("x2", width)
        .attr("y2", yScale(medianStdDev))
        .style("stroke-dasharray", ("3, 3"))
        .style("stroke", "red")
        .style("stroke-width", 2);

    // 5. Draw the Scatter Plot Points

    svg.selectAll(".team-dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "team-dot")
        .attr("cx", d => xScale(d.avg_tries))
        .attr("cy", d => yScale(d.standard_deviation))
        .attr("r", 5) // Circle size
        .on("mouseover", function(event, d) {
            // Show tooltip on hover
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(`**${d.team_name}**<br>Avg Tries: ${d.avg_tries}<br>Std Dev: ${d.standard_deviation}<br>Games: ${d.games_played}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function(d) {
            // Hide tooltip on mouse out
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

}).catch(error => {
    console.error("Error loading or processing data:", error);
});