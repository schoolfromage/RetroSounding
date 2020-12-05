document.addEventListener("DOMContentLoaded", () => {
	if (document.querySelectorAll('tbody>tr').length < 20) { np.style = "display:none" }
	if (pp.value == '0') { pp.style = "display:none" }
	timeline();
})
const timeline = () => {
	sortedDates = results.map(a => a[1]).sort()
	oldest = sortedDates[0]
	recent = sortedDates[results.length-1]
	unique = [...new Set(sortedDates)]
}