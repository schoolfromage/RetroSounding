document.addEventListener("DOMContentLoaded", () => {
	if (document.querySelectorAll('tbody>tr').length < 20) { np.style = "display:none" }
	if (pp.value == '0') { pp.style = "display:none" }
	timeline();
})
const timeline = () => {
	sortedDates = results.map(a => a[1]).sort()
	oldest = Number(sortedDates[0])
	youngest = Number(sortedDates[results.length-1])
	unique = [...new Set(sortedDates)]

	const myCanvas=document.getElementById('timeLine');
	const canvasDrawer = myCanvas.getContext('2d');
	canvasDrawer.lineCap='round'
	canvasDrawer.font = '40px Ariel'
	canvasDrawer.strokeStyle='#fff';
	canvasDrawer.fileStyle='#fff';
	canvasDrawer.lineWidth=2;
	
	var w = myCanvas.width; // I'd suggest using myCanvas.clientHeight and clientWidth
	var h = myCanvas.height; // it gives you the real height and width of the object as seen in devtools when hovering over it
	var range = youngest-oldest+2;//add 2 years for the top and bottom bracket
	var spacing = (h-40)/range;
	
	drawBase(oldest,youngest)
	results.forEach(drawGames)
	
	function drawBase(min, max) {
		var gap = 1;//the distance between years marked
		while ((range/gap) > 10){//<- put the max number of ticks here
		gap++;
		}
		//draw the big tabs and center tab
		
			canvasDrawer.beginPath();
			canvasDrawer.moveTo(w/2,0);
			canvasDrawer.lineTo(w/2+10,20);
			canvasDrawer.lineTo(w/2-10,20);
			canvasDrawer.closePath();
		canvasDrawer.stroke()
		canvasDrawer.beginPath();
			canvasDrawer.moveTo(w/2,h);
			canvasDrawer.lineTo(w/2+10,h-20);
			canvasDrawer.lineTo(w/2-10,h-20);
			canvasDrawer.closePath();
		canvasDrawer.stroke()
		canvasDrawer.moveTo(w/2,20);
		canvasDrawer.lineTo(w/2,h-20);
		canvasDrawer.stroke();
		//draw the middle tabs
		for (var i = 0; i <= youngest-oldest; i+=gap){
		 canvasDrawer.moveTo(w/5*2,spacing*(i+1)+20);
		 canvasDrawer.lineTo(w/5*3,spacing*(i+1)+20);
		 canvasDrawer.strokeText((oldest+(i)),w/3*2+10,spacing*(i+1)+20);
		}
		canvasDrawer.stroke();//stroke is basicaly the commit function
	}
	//0-name 1-date 2-pub 3-GID 4-console 5-image
	function drawGames(item, index){
		console.log(item)
		// var place =Number(item[1])-oldest;
		// picture = new Image()
		// if (item.length==6){
			// picture.src = item[5]
		// }else{
			// picture.src = '.\frontend\static\images\missing_image.jpg'
		// }
		// canvasDrawer.drawImage(picture,5,spacing*place+10, 50,50)
	}
}